"""State machine for persistent task runtime runs."""

from __future__ import annotations

import hashlib
import sys
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path

from event_bus import publish
from models import RuntimeRun, RuntimeRunApproval, RuntimeRunEvidence, db

TRANSITIONS = {
    "queued": {"running", "cancelled"},
    "running": {"awaiting_approval", "cancel_requested", "succeeded", "failed"},
    "awaiting_approval": {"running", "cancelled"},
    "cancel_requested": {"cancelled", "failed"},
    "failed": set(),
    "succeeded": set(),
    "cancelled": set(),
}
TERMINAL = {"succeeded", "failed", "cancelled"}


def create_run(task_id: int, *, requested_profile: str | None = None, resolved_profile: str | None = None, provider: str | None = None, workflow_type: str | None = None) -> RuntimeRun:
    from ecc_catalog import resolve_workflow

    prior = RuntimeRun.query.filter_by(task_id=task_id).order_by(RuntimeRun.attempt.desc()).first()
    workflow = resolve_workflow(workflow_type) if workflow_type else None
    if provider is None and workflow is not None:
        sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "ADWs"))
        from runtime_policy import resolve_runtime
        decision = resolve_runtime(workflow["slug"], str(task_id))
        provider = decision["primary"]
    run = RuntimeRun(
        id=str(uuid.uuid4()), task_id=task_id, attempt=(prior.attempt + 1 if prior else 1),
        requested_profile=requested_profile, resolved_profile=resolved_profile,
        runtime_provider=provider, workflow_slug=workflow["slug"] if workflow else None,
        workflow_hash=workflow["sha256"] if workflow else None, correlation_id=str(uuid.uuid4()),
    )
    db.session.add(run)
    publish("run.queued", f"run:{run.id}", run.correlation_id, {"task_id": task_id, "workflow": run.workflow_slug})
    db.session.commit()
    return run


def request_approval(run: RuntimeRun, action: str) -> RuntimeRunApproval:
    if run.status != "running":
        raise ValueError("Only running runs can await approval")
    approval = RuntimeRunApproval(
        id=str(uuid.uuid4()), run_id=run.id,
        action_hash=hashlib.sha256(action.encode()).hexdigest(),
    )
    transition(run, "awaiting_approval")
    db.session.add(approval)
    db.session.commit()
    return approval


def decide_approval(run: RuntimeRun, approval: RuntimeRunApproval, *, approved: bool, actor: str) -> RuntimeRun:
    if approval.status != "pending":
        raise ValueError("Approval is already decided")
    approval.status = "approved" if approved else "rejected"
    approval.decided_by = actor
    approval.decided_at = datetime.now(timezone.utc)
    transition(run, "running" if approved else "cancelled")
    db.session.commit()
    return run


def add_evidence(run: RuntimeRun, reference: str, mime_type: str | None = None, size_bytes: int | None = None) -> RuntimeRunEvidence:
    if not reference or reference.startswith("/") or ".." in reference:
        raise ValueError("Invalid evidence reference")
    evidence = RuntimeRunEvidence(
        id=str(uuid.uuid4()), run_id=run.id, reference=reference,
        mime_type=mime_type, size_bytes=size_bytes,
        checksum=hashlib.sha256(reference.encode()).hexdigest(),
    )
    db.session.add(evidence)
    db.session.commit()
    return evidence


def compute_metrics() -> dict:
    from collections import Counter, defaultdict

    runs = RuntimeRun.query.all()
    status_counts = Counter(run.status for run in runs)

    queue_durations = []
    run_durations = []
    per_workflow = defaultdict(lambda: {"succeeded": 0, "failed": 0, "cancelled": 0, "total": 0})
    for run in runs:
        if run.started_at and run.queued_at:
            queue_durations.append((run.started_at - run.queued_at).total_seconds())
        if run.completed_at and run.started_at:
            run_durations.append((run.completed_at - run.started_at).total_seconds())
        if run.workflow_slug:
            bucket = per_workflow[run.workflow_slug]
            bucket["total"] += 1
            if run.status in ("succeeded", "failed", "cancelled"):
                bucket[run.status] += 1

    def _avg(values):
        return round(sum(values) / len(values), 3) if values else None

    workflows = {}
    for slug, bucket in per_workflow.items():
        finished = bucket["succeeded"] + bucket["failed"]
        workflows[slug] = {
            **bucket,
            "success_rate": round(bucket["succeeded"] / finished, 4) if finished else None,
        }

    return {
        "status_counts": dict(status_counts),
        "avg_queue_seconds": _avg(queue_durations),
        "avg_run_seconds": _avg(run_durations),
        "workflows": workflows,
    }


def recover_orphaned_runs(lease_seconds: int = 900) -> int:
    cutoff = datetime.now(timezone.utc) - timedelta(seconds=lease_seconds)
    stale = RuntimeRun.query.filter(RuntimeRun.status.in_(("running", "cancel_requested")), RuntimeRun.started_at < cutoff).all()
    for run in stale:
        transition(run, "failed", error="Worker lease expired after restart", exit_code=-1)
    return len(stale)


def transition(run: RuntimeRun, target: str, *, summary: str | None = None, error: str | None = None, exit_code: int | None = None) -> RuntimeRun:
    if target == run.status:
        return run
    if target not in TRANSITIONS.get(run.status, set()):
        raise ValueError(f"Invalid runtime run transition: {run.status} -> {target}")
    run.status = target
    now = datetime.now(timezone.utc)
    if target == "running" and run.started_at is None:
        run.started_at = now
    if target in TERMINAL:
        run.completed_at = now
    if summary is not None:
        run.result_summary = summary[:5000]
    if error is not None:
        run.error = error[:2000]
    if exit_code is not None:
        run.exit_code = exit_code
    publish(f"run.{target}", f"run:{run.id}", run.correlation_id, {"task_id": run.task_id, "attempt": run.attempt})
    db.session.commit()
    return run

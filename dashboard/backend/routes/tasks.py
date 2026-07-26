"""Scheduled task API and durable task execution lifecycle."""

from __future__ import annotations

import os
import signal
import subprocess
import sys
import threading
from datetime import datetime, timedelta, timezone
from pathlib import Path

from flask import Blueprint, current_app, jsonify, request
from flask_login import current_user

from models import RuntimeRunApproval, RuntimeRunEvidence, ScheduledTask, audit, db, has_permission
from secret_redaction import redact_secrets

TASK_TIMEOUT_SECONDS = 15 * 60
_RUNNING_PROCESSES: dict[int, subprocess.Popen] = {}
bp = Blueprint("tasks", __name__)


def _require(resource: str, action: str):
    if not has_permission(current_user.role, resource, action):
        return jsonify({"error": "Forbidden"}), 403
    return None


def _validate_hermes_profile_override(data: dict):
    if "hermes_profile" not in data:
        return None, None
    profile = data["hermes_profile"] or None
    if profile and not has_permission(current_user.role, "tasks", "manage"):
        return None, (jsonify({"error": "Forbidden"}), 403)
    if profile:
        try:
            sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "ADWs"))
            from hermes_profiles import is_valid_slug
            if not is_valid_slug(profile):
                return None, (jsonify({"error": "Invalid Hermes profile"}), 400)
        finally:
            sys.path.pop(0)
    return profile, None


def _validate_task_data(data: dict, *, partial: bool = False):
    required = ("name", "type", "payload", "scheduled_at")
    if not partial:
        missing = [field for field in required if not data.get(field)]
        if missing:
            return None, (jsonify({"error": f"Missing fields: {', '.join(missing)}"}), 400)
    if "name" in data and (not isinstance(data["name"], str) or not data["name"].strip()):
        return None, (jsonify({"error": "name must be a non-empty string"}), 400)
    if "type" in data and data["type"] not in ("skill", "prompt", "script"):
        return None, (jsonify({"error": "type must be skill, prompt, or script"}), 400)
    if "payload" in data and (not isinstance(data["payload"], str) or not data["payload"].strip()):
        return None, (jsonify({"error": "payload must be a non-empty string"}), 400)
    scheduled_at = None
    if "scheduled_at" in data:
        try:
            scheduled_at = datetime.fromisoformat(data["scheduled_at"].replace("Z", "+00:00"))
        except (ValueError, AttributeError):
            return None, (jsonify({"error": "Invalid scheduled_at format (use ISO 8601)"}), 400)
        if scheduled_at.tzinfo is None:
            return None, (jsonify({"error": "scheduled_at must include timezone"}), 400)
    return scheduled_at, None


def claim_task(task_id: int) -> bool:
    claimed = ScheduledTask.query.filter_by(id=task_id, status="pending").update({
        "status": "running", "started_at": datetime.now(timezone.utc), "completed_at": None,
    }, synchronize_session=False)
    db.session.commit()
    return claimed == 1


def claim_due_tasks(now: datetime | None = None) -> list[int]:
    now = now or datetime.now(timezone.utc)
    ids = [row.id for row in ScheduledTask.query.filter(
        ScheduledTask.status == "pending", ScheduledTask.scheduled_at <= now,
    ).all()]
    return [task_id for task_id in ids if claim_task(task_id)]


def recover_stale_tasks(max_age_seconds: int = TASK_TIMEOUT_SECONDS) -> int:
    cutoff = datetime.now(timezone.utc) - timedelta(seconds=max_age_seconds)
    stale = ScheduledTask.query.filter(ScheduledTask.status == "running", ScheduledTask.started_at < cutoff).all()
    for task in stale:
        task.status = "pending"
        task.started_at = None
        task.attempt += 1
        task.error = "Recovered after worker restart"
    db.session.commit()
    return len(stale)


def _resolve_task_runtime(task: ScheduledTask) -> tuple[str, str | None, str | None]:
    adw_dir = str(Path(__file__).resolve().parents[3] / "ADWs")
    sys.path.insert(0, adw_dir)
    try:
        from runner import _get_provider_config
        provider, _ = _get_provider_config()
        profile = None
        if provider == "hermes":
            from hermes_profiles import resolve_profile
            profile, _ = resolve_profile(task.agent or task.type, task.hermes_profile)
        return provider, profile, None
    finally:
        sys.path.pop(0)


def _requirements_met(run_id: str) -> bool:
    return not RuntimeRunApproval.query.filter(
        RuntimeRunApproval.run_id == run_id,
        RuntimeRunApproval.status.in_(("pending", "denied")),
    ).count()


def _kill_process_group(process: subprocess.Popen) -> None:
    if process.poll() is not None:
        return
    try:
        os.killpg(os.getpgid(process.pid), signal.SIGTERM)
        process.wait(timeout=2)
    except subprocess.TimeoutExpired:
        os.killpg(os.getpgid(process.pid), signal.SIGKILL)
    except ProcessLookupError:
        pass


def cancel_task_process(task_id: int) -> bool:
    process = _RUNNING_PROCESSES.get(task_id)
    if not process:
        return False
    _kill_process_group(process)
    return True


@bp.route("/api/tasks")
def list_tasks():
    denied = _require("tasks", "view")
    if denied:
        return denied
    page = request.args.get("page", 1, type=int)
    per_page = min(request.args.get("per_page", 50, type=int), 100)
    pagination = ScheduledTask.query.order_by(ScheduledTask.scheduled_at.desc()).paginate(page=page, per_page=per_page, error_out=False)
    return jsonify({"tasks": [task.to_dict() for task in pagination.items], "total": pagination.total, "pages": pagination.pages, "page": page})


@bp.route("/api/tasks/<int:task_id>")
def get_task(task_id):
    denied = _require("tasks", "view")
    if denied:
        return denied
    return jsonify(ScheduledTask.query.get_or_404(task_id).to_dict())


@bp.route("/api/tasks", methods=["POST"])
def create_task():
    denied = _require("tasks", "execute")
    if denied:
        return denied
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "JSON body required"}), 400
    scheduled_at, error = _validate_task_data(data)
    if error:
        return error
    profile, error = _validate_hermes_profile_override(data)
    if error:
        return error
    ticket_id = data.get("ticket_id")
    if ticket_id is not None:
        from models import Ticket
        if not isinstance(ticket_id, str):
            return jsonify({"error": "ticket_id must be a string"}), 400
        if not Ticket.query.get(ticket_id):
            return jsonify({"error": "ticket_id does not exist"}), 404
    task = ScheduledTask(name=data["name"], description=data.get("description"), type=data["type"], payload=data["payload"], agent=data.get("agent"), hermes_profile=profile, ticket_id=ticket_id, scheduled_at=scheduled_at, status="pending", created_by=current_user.id if current_user.is_authenticated else None)
    db.session.add(task)
    db.session.commit()
    audit(current_user, "create", "tasks", f"Created task #{task.id}: {task.name}")
    return jsonify(task.to_dict()), 201


@bp.route("/api/tasks/<int:task_id>", methods=["PUT"])
def update_task(task_id):
    denied = _require("tasks", "execute")
    if denied:
        return denied
    task = ScheduledTask.query.get_or_404(task_id)
    if task.status != "pending":
        return jsonify({"error": "Only pending tasks can be edited"}), 400
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "JSON body required"}), 400
    scheduled_at, error = _validate_task_data(data, partial=True)
    if error:
        return error
    profile, error = _validate_hermes_profile_override(data)
    if error:
        return error
    for field in ("name", "description", "type", "payload", "agent", "ticket_id"):
        if field in data:
            setattr(task, field, data[field])
    if "hermes_profile" in data:
        task.hermes_profile = profile
    if scheduled_at is not None:
        task.scheduled_at = scheduled_at
    db.session.commit()
    audit(current_user, "update", "tasks", f"Updated task #{task.id}: {task.name}")
    return jsonify(task.to_dict())


@bp.route("/api/tasks/<int:task_id>", methods=["DELETE"])
def cancel_task(task_id):
    denied = _require("tasks", "execute")
    if denied:
        return denied
    task = ScheduledTask.query.get_or_404(task_id)
    if task.status == "running":
        cancel_task_process(task.id)
    elif task.status not in ("pending", "failed"):
        return jsonify({"error": f"Cannot cancel task with status '{task.status}'"}), 400
    task.status = "cancelled"
    task.completed_at = datetime.now(timezone.utc)
    if task.runtime_run_id:
        from runtime_runs import transition
        from models import RuntimeRun
        run = RuntimeRun.query.get(task.runtime_run_id)
        if run and run.status in ("queued", "running", "awaiting_approval", "cancel_requested"):
            transition(run, "cancelled" if run.status != "running" else "cancel_requested")
    db.session.commit()
    audit(current_user, "cancel", "tasks", f"Cancelled task #{task.id}: {task.name}")
    return jsonify(task.to_dict())


def _start_task(task_id: int) -> bool:
    if not claim_task(task_id):
        return False
    app = current_app._get_current_object()
    threading.Thread(target=lambda: _execute_with_context(app, task_id), daemon=True).start()
    return True


def _execute_with_context(app, task_id: int):
    with app.app_context():
        _execute_task(task_id, already_claimed=True)


@bp.route("/api/tasks/<int:task_id>/run", methods=["POST"])
def run_task_now(task_id):
    denied = _require("tasks", "execute")
    if denied:
        return denied
    task = ScheduledTask.query.get_or_404(task_id)
    if task.status == "failed":
        task.status = "pending"
        db.session.commit()
    if task.status != "pending" or not _start_task(task.id):
        return jsonify({"error": f"Cannot run task with status '{task.status}'"}), 400
    audit(current_user, "run", "tasks", f"Manually triggered task #{task.id}: {task.name}")
    return jsonify(ScheduledTask.query.get(task.id).to_dict()), 202


def _execute_task(task_id: int, *, already_claimed: bool = False):
    if not already_claimed and not claim_task(task_id):
        return False
    task = ScheduledTask.query.get(task_id)
    if not task:
        return False
    from runtime_runs import create_run, transition
    run = None
    try:
        provider = profile = fallback = None
        if task.type != "script":
            provider, profile, fallback = _resolve_task_runtime(task)
        run = create_run(task.id, requested_profile=task.hermes_profile, resolved_profile=profile, provider=provider)
        task.provider, task.resolved_profile, task.workflow_policy, task.fallback_reason = provider, profile, run.workflow_slug, fallback
        task.runtime_run_id = run.id
        task.attempt = run.attempt
        db.session.commit()
        transition(run, "running")
        if task.type in ("skill", "prompt"):
            adw_dir = str(Path(__file__).resolve().parents[3] / "ADWs")
            sys.path.insert(0, adw_dir)
            try:
                from runner import run_claude, run_skill
                def track_process(process):
                    _RUNNING_PROCESSES[task.id] = process
                result = run_skill(task.payload, log_name=f"task-{task.id}", timeout=TASK_TIMEOUT_SECONDS, agent=task.agent, profile=profile, on_process=track_process) if task.type == "skill" else run_claude(task.payload, log_name=f"task-{task.id}", timeout=TASK_TIMEOUT_SECONDS, agent=task.agent, profile=profile, on_process=track_process)
            finally:
                sys.path.pop(0)
            task.result_summary = redact_secrets(result.get("stdout"), limit=5000)
            db.session.refresh(task)
            if task.status == "cancelled":
                transition(run, "cancelled")
            elif result.get("success"):
                if not _requirements_met(run.id):
                    raise RuntimeError("Pending or denied approval blocks successful completion")
                task.status = "completed"
                transition(run, "succeeded", summary=task.result_summary, exit_code=result.get("returncode", 0))
            else:
                task.status = "failed"
                task.error = redact_secrets(result.get("stderr") or "Task failed", limit=2000)
                transition(run, "failed", summary=task.result_summary, error=task.error, exit_code=result.get("returncode", -1))
        elif task.type == "script":
            script = (Path(__file__).resolve().parents[3] / "ADWs" / "routines" / task.payload).resolve()
            root = (Path(__file__).resolve().parents[3] / "ADWs" / "routines").resolve()
            if root not in script.parents or not script.is_file():
                raise FileNotFoundError(f"Script not found: {task.payload}")
            process = subprocess.Popen([sys.executable, str(script)], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, start_new_session=True)
            _RUNNING_PROCESSES[task.id] = process
            stdout, stderr = process.communicate(timeout=TASK_TIMEOUT_SECONDS)
            task.result_summary = redact_secrets(stdout, limit=5000)
            db.session.refresh(task)
            if task.status == "cancelled":
                transition(run, "cancelled")
            elif process.returncode == 0:
                task.status = "completed"
                transition(run, "succeeded", summary=task.result_summary, exit_code=0)
            else:
                task.status = "failed"
                task.error = redact_secrets(stderr or "Script failed", limit=2000)
                transition(run, "failed", summary=task.result_summary, error=task.error, exit_code=process.returncode)
    except subprocess.TimeoutExpired:
        process = _RUNNING_PROCESSES.get(task_id)
        if process:
            _kill_process_group(process)
        task.status, task.error = "failed", f"Timeout ({TASK_TIMEOUT_SECONDS}s)"
        if run:
            transition(run, "failed", error=task.error, exit_code=-1)
    except Exception as exc:
        task.status, task.error = "failed", redact_secrets(exc, limit=2000)
        if run and run.status not in ("failed", "succeeded", "cancelled"):
            transition(run, "failed", error=task.error, exit_code=-1)
    finally:
        _RUNNING_PROCESSES.pop(task_id, None)
        if task.status == "cancelled" and run and run.status not in ("cancelled",):
            transition(run, "cancelled")
        task.completed_at = datetime.now(timezone.utc)
        db.session.commit()
    return True

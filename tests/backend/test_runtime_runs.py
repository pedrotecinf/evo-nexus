from __future__ import annotations

import importlib
import sys
from datetime import datetime, timezone
from pathlib import Path

import pytest
from flask import Flask

BACKEND_DIR = Path(__file__).resolve().parents[2] / "dashboard" / "backend"
sys.path.insert(0, str(BACKEND_DIR))


@pytest.fixture
def app():
    import models
    import runtime_runs
    importlib.reload(runtime_runs)
    app = Flask(__name__)
    app.config.update(TESTING=True, SQLALCHEMY_DATABASE_URI="sqlite:///:memory:", SQLALCHEMY_TRACK_MODIFICATIONS=False)
    models.db.init_app(app)
    with app.app_context():
        models.db.create_all()
    return app


def test_state_machine_and_retry(app):
    from models import ScheduledTask
    from runtime_runs import add_evidence, create_run, decide_approval, recover_orphaned_runs, request_approval, transition
    with app.app_context():
        task = ScheduledTask(name="test", description="", type="prompt", payload="ok", scheduled_at=datetime(2026, 1, 1, tzinfo=timezone.utc))
        app.extensions["sqlalchemy"].session.add(task)
        app.extensions["sqlalchemy"].session.commit()
        run = create_run(task.id)
        assert run.status == "queued"
        transition(run, "running")
        transition(run, "failed", error="failure")
        assert run.status == "failed"
        retried = create_run(task.id)
        assert retried.attempt == 2 and retried.status == "queued"
        with pytest.raises(ValueError):
            transition(run, "running")


def test_approval_evidence_and_recovery(app):
    from models import ScheduledTask
    from runtime_runs import add_evidence, create_run, decide_approval, recover_orphaned_runs, request_approval, transition
    with app.app_context():
        task = ScheduledTask(name="test", description="", type="prompt", payload="ok", scheduled_at=datetime.now(timezone.utc))
        app.extensions["sqlalchemy"].session.add(task)
        app.extensions["sqlalchemy"].session.commit()
        run = create_run(task.id)
        transition(run, "running")
        approval = request_approval(run, "send message")
        assert run.status == "awaiting_approval"
        decide_approval(run, approval, approved=True, actor="admin")
        assert run.status == "running"
        evidence = add_evidence(run, "artifacts/output.json", "application/json", 42)
        assert evidence.checksum
        with pytest.raises(ValueError):
            add_evidence(run, "../secret")
        run.started_at = datetime(2000, 1, 1, tzinfo=timezone.utc)
        app.extensions["sqlalchemy"].session.commit()
        assert recover_orphaned_runs() == 1
        assert run.status == "failed"


def test_scheduled_task_links_to_ticket(app):
    from models import ScheduledTask, Ticket
    with app.app_context():
        ticket = Ticket(id="ticket-1", title="Investigate", status="open", priority="medium", created_at="2026-01-01T00:00:00Z", updated_at="2026-01-01T00:00:00Z")
        app.extensions["sqlalchemy"].session.add(ticket)
        app.extensions["sqlalchemy"].session.commit()

        task = ScheduledTask(name="fix", description="", type="prompt", payload="ok", scheduled_at=datetime.now(timezone.utc), ticket_id="ticket-1")
        app.extensions["sqlalchemy"].session.add(task)
        app.extensions["sqlalchemy"].session.commit()

        fetched = ScheduledTask.query.get(task.id)
        assert fetched.ticket_id == "ticket-1"
        assert fetched.to_dict()["ticket_id"] == "ticket-1"


def test_goal_linked_run_preserves_auditable_origin_and_evidence(app):
    from models import Goal, GoalProject, Mission, Ticket
    from runtime_runs import add_evidence, create_run

    with app.app_context():
        mission = Mission(slug="mission", title="Mission", created_at="2026-01-01T00:00:00Z", updated_at="2026-01-01T00:00:00Z")
        app.extensions["sqlalchemy"].session.add(mission)
        app.extensions["sqlalchemy"].session.flush()
        project = GoalProject(slug="project", mission_id=mission.id, title="Project", created_at="2026-01-01T00:00:00Z", updated_at="2026-01-01T00:00:00Z")
        app.extensions["sqlalchemy"].session.add(project)
        app.extensions["sqlalchemy"].session.flush()
        goal = Goal(slug="goal", project_id=project.id, title="Goal", created_at="2026-01-01T00:00:00Z", updated_at="2026-01-01T00:00:00Z")
        ticket = Ticket(id="ticket-1", title="Investigate", status="open", priority="medium", created_at="2026-01-01T00:00:00Z", updated_at="2026-01-01T00:00:00Z", goal_id=goal.id)
        app.extensions["sqlalchemy"].session.add_all([goal, ticket])
        app.extensions["sqlalchemy"].session.commit()

        run = create_run(
            origin_type="heartbeat",
            origin_id="atlas-4h",
            provider="hermes",
            resolved_profile="atlas",
            agent_slug="atlas-project",
            ticket_id=ticket.id,
            goal_id=goal.id,
        )
        evidence = add_evidence(run, "artifacts/heartbeat.json", "application/json", 42)

        payload = run.to_dict()
        assert payload["origin_type"] == "heartbeat"
        assert payload["origin_id"] == "atlas-4h"
        assert payload["runtime_provider"] == "hermes"
        assert payload["agent_slug"] == "atlas-project"
        assert payload["ticket_id"] == ticket.id
        assert payload["goal_id"] == goal.id
        assert evidence.run_id == run.id


def test_compute_metrics_aggregates_by_workflow(app):
    from models import ScheduledTask
    from runtime_runs import compute_metrics, create_run, transition
    with app.app_context():
        task = ScheduledTask(name="test", description="", type="prompt", payload="ok", scheduled_at=datetime.now(timezone.utc))
        app.extensions["sqlalchemy"].session.add(task)
        app.extensions["sqlalchemy"].session.commit()

        run_ok = create_run(task.id)
        transition(run_ok, "running")
        transition(run_ok, "succeeded")

        run_bad = create_run(task.id)
        transition(run_bad, "running")
        transition(run_bad, "failed", error="boom")

        metrics = compute_metrics()
        assert metrics["status_counts"]["succeeded"] == 1
        assert metrics["status_counts"]["failed"] == 1
        assert sum(metrics["status_counts"].values()) == 2

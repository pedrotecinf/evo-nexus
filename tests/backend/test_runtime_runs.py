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
    importlib.reload(models)
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


def test_compute_metrics_aggregates_by_workflow(app):
    from models import ScheduledTask
    from runtime_runs import compute_metrics, create_run, transition
    with app.app_context():
        task = ScheduledTask(name="test", description="", type="prompt", payload="ok", scheduled_at=datetime.now(timezone.utc))
        app.extensions["sqlalchemy"].session.add(task)
        app.extensions["sqlalchemy"].session.commit()

        run_ok = create_run(task.id, workflow_type="review")
        transition(run_ok, "running")
        transition(run_ok, "succeeded")

        run_bad = create_run(task.id, workflow_type="review")
        transition(run_bad, "running")
        transition(run_bad, "failed", error="boom")

        metrics = compute_metrics()
        assert metrics["status_counts"]["succeeded"] == 1
        assert metrics["status_counts"]["failed"] == 1
        workflow_metrics = metrics["workflows"]["orch-review"]
        assert workflow_metrics["succeeded"] == 1
        assert workflow_metrics["failed"] == 1
        assert workflow_metrics["success_rate"] == 0.5

from __future__ import annotations

import importlib
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest
from flask import Flask

BACKEND_DIR = Path(__file__).resolve().parents[2] / "dashboard" / "backend"
ADW_DIR = Path(__file__).resolve().parents[2] / "ADWs"
for path in (str(BACKEND_DIR), str(ADW_DIR)):
    if path not in sys.path:
        sys.path.insert(0, path)


@pytest.fixture
def app():
    import models
    importlib.reload(models)
    app = Flask(__name__)
    app.config.update(TESTING=True, SQLALCHEMY_DATABASE_URI="sqlite:///:memory:", SQLALCHEMY_TRACK_MODIFICATIONS=False)
    models.db.init_app(app)
    with app.app_context():
        models.db.create_all()
    return app


def make_task(app, **overrides):
    from models import ScheduledTask, db

    values = {
        "name": "task",
        "description": "",
        "type": "prompt",
        "payload": "say hi",
        "scheduled_at": datetime.now(timezone.utc) - timedelta(seconds=1),
    }
    values.update(overrides)
    with app.app_context():
        task = ScheduledTask(**values)
        db.session.add(task)
        db.session.commit()
        return task.id


def test_atomic_claim_executes_due_task_once(app):
    import routes.tasks as tasks
    importlib.reload(tasks)

    task_id = make_task(app)
    with app.app_context():
        assert tasks.claim_task(task_id) is True
        assert tasks.claim_task(task_id) is False
        from models import ScheduledTask
        assert ScheduledTask.query.get(task_id).status == "running"


def test_recover_running_task_requeues_or_fails_by_policy(app):
    import routes.tasks as tasks
    importlib.reload(tasks)

    task_id = make_task(app, status="running", started_at=datetime.now(timezone.utc) - timedelta(minutes=20))
    with app.app_context():
        assert tasks.recover_stale_tasks(max_age_seconds=60) == 1
        from models import ScheduledTask
        task = ScheduledTask.query.get(task_id)
        assert task.status == "pending"
        assert task.attempt == 1


def test_hermes_adapter_never_treats_agent_as_skill(monkeypatch):
    import hermes_adapter

    command = {}

    class Result:
        returncode = 0
        stdout = "ok"
        stderr = ""

    def fake_run(args, **kwargs):
        command["args"] = args
        return Result()

    monkeypatch.setattr(hermes_adapter.subprocess, "run", fake_run)
    monkeypatch.setattr(sys, "argv", ["hermes_adapter.py", "--print", "--output-format", "json", "--agent", "clawdia-assistant", "--profile", "operator", "hello"])
    with pytest.raises(SystemExit) as exit_info:
        hermes_adapter.main()
    assert exit_info.value.code == 0
    assert "--skills" not in command["args"]
    assert command["args"][:3] == ["hermes", "-p", "operator"]


def test_update_validation_rejects_invalid_mutable_type(app):
    import routes.tasks as tasks
    importlib.reload(tasks)

    with app.test_request_context(json={"type": "invalid"}):
        _, error = tasks._validate_task_data({"type": "invalid"}, partial=True)
    assert error[1] == 400


def test_skill_prompt_and_script_types_are_valid(app):
    import routes.tasks as tasks
    importlib.reload(tasks)

    for task_type in ("skill", "prompt", "script"):
        with app.test_request_context(json={}):
            _, error = tasks._validate_task_data({"name": "t", "type": task_type, "payload": "x", "scheduled_at": "2026-07-25T10:00:00Z"})
        assert error is None


def test_cancel_signals_running_process_group(monkeypatch):
    import routes.tasks as tasks
    importlib.reload(tasks)

    class Process:
        def poll(self):
            return None

        pid = 123

        def wait(self, timeout):
            return None

    process = Process()
    tasks._RUNNING_PROCESSES[7] = process
    calls = []
    monkeypatch.setattr(tasks.os, "getpgid", lambda pid: 42)
    monkeypatch.setattr(tasks.os, "killpg", lambda pgid, sig: calls.append((pgid, sig)))
    assert tasks.cancel_task_process(7) is True
    assert calls == [(42, tasks.signal.SIGTERM)]


def test_approval_gate_rejects_pending_or_denied(app):
    import routes.tasks as tasks
    importlib.reload(tasks)
    from models import RuntimeRunApproval, db

    with app.app_context():
        db.session.add(RuntimeRunApproval(id="approval", run_id="run", action_hash="x", status="pending"))
        db.session.commit()
        assert tasks._requirements_met("run") is False
        RuntimeRunApproval.query.get("approval").status = "denied"
        db.session.commit()
        assert tasks._requirements_met("run") is False


def test_script_task_does_not_resolve_provider(app, monkeypatch):
    import routes.tasks as tasks
    importlib.reload(tasks)

    task_id = make_task(app, type="script", payload="missing.py")
    monkeypatch.setattr(tasks, "_resolve_task_runtime", lambda task: (_ for _ in ()).throw(AssertionError("provider should not resolve")))
    with app.app_context():
        tasks._execute_task(task_id)
        from models import ScheduledTask
        assert ScheduledTask.query.get(task_id).status == "failed"

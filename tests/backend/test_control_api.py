from __future__ import annotations

import importlib
import os
import sys
from pathlib import Path

import pytest
from flask import Flask

BACKEND_DIR = Path(__file__).resolve().parents[2] / "dashboard" / "backend"
sys.path.insert(0, str(BACKEND_DIR))


@pytest.fixture
def app(monkeypatch):
    monkeypatch.setenv("HERMES_CONTROL_API_TOKEN", "control-test-token")
    monkeypatch.setenv("HERMES_CONTROL_API_SCOPES", "health:read,projects:read,tickets:read,tickets:write,comments:write,evidence:write,goals:read,goals:write,heartbeats:read,heartbeats:write,heartbeats:run,scheduled_tasks:read,scheduled_tasks:write,scheduled_tasks:run")
    import models
    importlib.reload(models)
    import routes.control_api as control_api
    importlib.reload(control_api)
    app = Flask(__name__)
    app.config.update(TESTING=True, SQLALCHEMY_DATABASE_URI="sqlite:///:memory:", SQLALCHEMY_TRACK_MODIFICATIONS=False)
    models.db.init_app(app)
    app.register_blueprint(control_api.bp)
    with app.app_context():
        models.db.create_all()
    yield app


@pytest.fixture
def client(app):
    return app.test_client()


def headers(**extra):
    return {"Authorization": "Bearer control-test-token", **extra}


def test_requires_service_token(client):
    assert client.get("/api/control/v1/health").status_code == 401
    assert client.get("/api/control/v1/health", headers={"Authorization": "Bearer invalid"}).status_code == 401


def test_requires_scope(client, monkeypatch):
    monkeypatch.setenv("HERMES_CONTROL_API_SCOPES", "health:read")
    assert client.post("/api/control/v1/tickets", headers=headers(**{"Idempotency-Key": "a"}), json={"title": "x"}).status_code == 403


def test_create_ticket_is_idempotent(client):
    request_headers = headers(**{"Idempotency-Key": "create-1", "X-Correlation-ID": "corr-1"})
    payload = {"title": "Follow up", "description": "Safe"}
    created = client.post("/api/control/v1/tickets", headers=request_headers, json=payload)
    replayed = client.post("/api/control/v1/tickets", headers=request_headers, json=payload)
    assert created.status_code == 201
    assert replayed.status_code == 201
    assert created.json["data"]["id"] == replayed.json["data"]["id"]
    assert replayed.json["correlation_id"] == "corr-1"
    conflict = client.post("/api/control/v1/tickets", headers=request_headers, json={"title": "Other"})
    assert conflict.status_code == 409


def test_mutations_require_idempotency_key(client):
    created = client.post("/api/control/v1/tickets", headers=headers(**{"Idempotency-Key": "key-required"}), json={"title": "Task"})
    ticket_id = created.json["data"]["id"]
    assert client.patch(f"/api/control/v1/tickets/{ticket_id}", headers=headers(), json={"title": "Changed"}).status_code == 400
    assert client.post(f"/api/control/v1/tickets/{ticket_id}/comments", headers=headers(), json={"body": "Done"}).status_code == 400
    assert client.post(f"/api/control/v1/tickets/{ticket_id}/evidence", headers=headers(), json={"evidence": "run-123"}).status_code == 400


def test_ticket_timeline_checkout_release_and_conflict(client):
    created = client.post("/api/control/v1/tickets", headers=headers(**{"Idempotency-Key": "ticket-lock"}), json={"title": "Task"})
    ticket_id = created.json["data"]["id"]
    assert client.get(f"/api/control/v1/tickets/{ticket_id}/timeline", headers=headers()).status_code == 200

    lock_headers = headers(**{"Idempotency-Key": "lock-1", "X-Correlation-ID": "lock-correlation"})
    locked = client.post(f"/api/control/v1/tickets/{ticket_id}/checkout", headers=lock_headers, json={"agent": "zara-cs"})
    replayed = client.post(f"/api/control/v1/tickets/{ticket_id}/checkout", headers=lock_headers, json={"agent": "zara-cs"})
    assert locked.status_code == replayed.status_code == 200
    assert locked.json["data"]["locked_by"] == "zara-cs"
    assert client.post(f"/api/control/v1/tickets/{ticket_id}/checkout", headers=headers(**{"Idempotency-Key": "lock-2"}), json={"agent": "atlas-project"}).status_code == 409
    assert client.post(f"/api/control/v1/tickets/{ticket_id}/release", headers=headers(**{"Idempotency-Key": "release-wrong"}), json={"agent": "atlas-project"}).status_code == 403
    released = client.post(f"/api/control/v1/tickets/{ticket_id}/release", headers=headers(**{"Idempotency-Key": "release-1"}), json={"agent": "zara-cs"})
    assert released.status_code == 200
    assert released.json["data"]["locked_by"] is None


def test_comments_evidence_and_validation(client):
    created = client.post("/api/control/v1/tickets", headers=headers(**{"Idempotency-Key": "ticket-1"}), json={"title": "Task"})
    ticket_id = created.json["data"]["id"]
    comment_headers = headers(**{"Idempotency-Key": "comment-1"})
    comment = client.post(f"/api/control/v1/tickets/{ticket_id}/comments", headers=comment_headers, json={"body": "Done"})
    replay = client.post(f"/api/control/v1/tickets/{ticket_id}/comments", headers=comment_headers, json={"body": "Done"})
    assert comment.status_code == replay.status_code == 201
    assert comment.json["data"]["id"] == replay.json["data"]["id"]
    invalid = client.post(f"/api/control/v1/tickets/{ticket_id}/evidence", headers=headers(**{"Idempotency-Key": "evidence-invalid"}), json={"evidence": "../../secret"})
    assert invalid.status_code == 400
    evidence = client.post(f"/api/control/v1/tickets/{ticket_id}/evidence", headers=headers(**{"Idempotency-Key": "evidence-1"}), json={"evidence": "run-123"})
    assert evidence.status_code == 201


def test_token_rotation_overlap_window(client, monkeypatch):
    monkeypatch.setenv("HERMES_CONTROL_API_TOKEN", "new-token")
    monkeypatch.setenv("HERMES_CONTROL_API_TOKEN_PREVIOUS", "control-test-token")
    old = client.get("/api/control/v1/health", headers=headers())
    new = client.get("/api/control/v1/health", headers={"Authorization": "Bearer new-token"})
    assert old.status_code == 200
    assert new.status_code == 200
    monkeypatch.delenv("HERMES_CONTROL_API_TOKEN_PREVIOUS", raising=False)
    expired = client.get("/api/control/v1/health", headers=headers())
    assert expired.status_code == 401


def test_control_audit_never_stores_token(client, app):
    client.post("/api/control/v1/tickets", headers=headers(**{"Idempotency-Key": "audit-1"}), json={"title": "Audited"})
    from models import ControlApiAuditLog
    with app.app_context():
        entry = ControlApiAuditLog.query.one()
        assert "control-test-token" not in " ".join((entry.operation, entry.resource, entry.correlation_id))


def test_goals_list_read(client, app):
    from models import Mission, GoalProject, Goal, GoalTask
    with app.app_context():
        now = "2026-07-25T00:00:00.000000Z"
        m = Mission(slug="m1", title="M1", created_at=now, updated_at=now)
        from models import db
        db.session.add(m)
        db.session.commit()
        p = GoalProject(slug="p1", title="P1", mission_id=m.id, created_at=now, updated_at=now)
        db.session.add(p)
        db.session.commit()
        g = Goal(slug="g1", title="G1", project_id=p.id, created_at=now, updated_at=now)
        db.session.add(g)
        db.session.commit()
        t = GoalTask(goal_id=g.id, title="T1", created_at=now, updated_at=now)
        db.session.add(t)
        db.session.commit()

    assert client.get("/api/control/v1/missions", headers=headers()).status_code == 200
    assert client.get("/api/control/v1/projects", headers=headers()).status_code == 200
    resp = client.get("/api/control/v1/goals", headers=headers())
    assert resp.status_code == 200
    assert len(resp.json["data"]) == 1
    assert resp.json["data"][0]["slug"] == "g1"
    resp = client.get("/api/control/v1/goal-tasks", headers=headers())
    assert resp.status_code == 200
    assert len(resp.json["data"]) == 1


def test_goal_update_idempotent(client, app):
    from models import Goal, GoalProject, Mission, db
    with app.app_context():
        now = "2026-07-25T00:00:00.000000Z"
        m = Mission(slug="m2", title="M2", created_at=now, updated_at=now)
        db.session.add(m)
        db.session.commit()
        p = GoalProject(slug="p2", title="P2", mission_id=m.id, created_at=now, updated_at=now)
        db.session.add(p)
        db.session.commit()
        g = Goal(slug="g2", title="G2", project_id=p.id, created_at=now, updated_at=now)
        db.session.add(g)
        db.session.commit()
        goal_id = g.id

    h = headers(**{"Idempotency-Key": "goal-update-1"})
    resp = client.patch(f"/api/control/v1/goals/{goal_id}", headers=h, json={"current_value": 42})
    assert resp.status_code == 200
    assert resp.json["data"]["current_value"] == 42
    replay = client.patch(f"/api/control/v1/goals/{goal_id}", headers=h, json={"current_value": 42})
    assert replay.status_code == 200
    assert replay.json["data"]["current_value"] == 42


def test_heartbeat_list_and_enable_disable(client, app):
    from models import Heartbeat, db
    with app.app_context():
        hb = Heartbeat(id="test-hb", agent="zara-cs", interval_seconds=3600, decision_prompt="Test", enabled=False)
        db.session.add(hb)
        db.session.commit()

    resp = client.get("/api/control/v1/heartbeats", headers=headers())
    assert resp.status_code == 200
    assert any(h["id"] == "test-hb" for h in resp.json["data"])

    resp = client.get("/api/control/v1/heartbeats/test-hb", headers=headers())
    assert resp.status_code == 200
    assert resp.json["data"]["enabled"] is False

    h = headers(**{"Idempotency-Key": "hb-enable-1"})
    resp = client.patch("/api/control/v1/heartbeats/test-hb/enabled", headers=h, json={"enabled": True})
    assert resp.status_code == 200
    assert resp.json["data"]["enabled"] is True


def test_heartbeat_run_requires_scope(client, monkeypatch):
    monkeypatch.setenv("HERMES_CONTROL_API_SCOPES", "heartbeats:read")
    h = headers(**{"Idempotency-Key": "hb-run-no-scope"})
    resp = client.post("/api/control/v1/heartbeats/test-hb/run", headers=h, json={})
    assert resp.status_code == 403


def test_scheduled_task_cancel_and_transitions(client, app):
    from models import ScheduledTask, db
    from datetime import datetime, timezone
    with app.app_context():
        task = ScheduledTask(name="cancel-me", type="prompt", payload="ok", scheduled_at=datetime(2026, 12, 1, tzinfo=timezone.utc))
        db.session.add(task)
        db.session.commit()
        task_id = task.id

    resp = client.get(f"/api/control/v1/scheduled-tasks/{task_id}", headers=headers())
    assert resp.status_code == 200
    assert resp.json["data"]["status"] == "pending"

    h = headers(**{"Idempotency-Key": "cancel-task-1"})
    resp = client.post(f"/api/control/v1/scheduled-tasks/{task_id}/cancel", headers=h, json={})
    assert resp.status_code == 200
    assert resp.json["data"]["status"] == "cancelled"

    h2 = headers(**{"Idempotency-Key": "cancel-task-2"})
    resp = client.post(f"/api/control/v1/scheduled-tasks/{task_id}/cancel", headers=h2, json={})
    assert resp.status_code == 409


def test_scheduled_task_run_now(client, app):
    from models import ScheduledTask, db
    from datetime import datetime, timezone
    with app.app_context():
        task = ScheduledTask(name="run-me", type="prompt", payload="ok", scheduled_at=datetime(2026, 12, 1, tzinfo=timezone.utc), status="failed")
        db.session.add(task)
        db.session.commit()
        task_id = task.id

    h = headers(**{"Idempotency-Key": "run-task-1"})
    resp = client.post(f"/api/control/v1/scheduled-tasks/{task_id}/run", headers=h, json={})
    assert resp.status_code == 202
    assert resp.json["data"]["status"] == "pending"

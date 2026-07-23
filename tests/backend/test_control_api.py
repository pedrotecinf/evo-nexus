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
    monkeypatch.setenv("HERMES_CONTROL_API_SCOPES", "health:read,projects:read,tickets:read,tickets:write,comments:write,evidence:write")
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

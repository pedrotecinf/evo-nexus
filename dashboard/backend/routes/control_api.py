"""Hermes Control API — service-authenticated, scoped internal integration."""

from __future__ import annotations

import hashlib
import json
import os
import secrets
import uuid
from datetime import datetime, timezone
from functools import wraps

from flask import Blueprint, jsonify, request
from sqlalchemy.exc import IntegrityError

from models import (
    ControlApiAuditLog, ControlApiIdempotency, GoalProject, Ticket, TicketActivity,
    TicketComment, TICKET_PRIORITIES, TICKET_STATUSES, db,
)
from event_bus import publish as publish_event

bp = Blueprint("control_api", __name__)
ACTOR = "service:hermes"
MAX_TITLE = 500
MAX_DESCRIPTION = 20_000
MAX_COMMENT = 20_000
MAX_EVIDENCE = 8_000


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")


def _correlation_id() -> str:
    return request.headers.get("X-Correlation-ID", "").strip()[:128] or str(uuid.uuid4())


def _response(data=None, error=None, status=200, correlation_id=None):
    body = {"correlation_id": correlation_id or _correlation_id()}
    if error is not None:
        body["error"] = error
    else:
        body["data"] = data
    return jsonify(body), status


def _scopes() -> set[str]:
    return {scope.strip() for scope in os.environ.get("HERMES_CONTROL_API_SCOPES", "").split(",") if scope.strip()}


def _service_authenticated() -> bool:
    header = request.headers.get("Authorization", "")
    if not header.startswith("Bearer "):
        return False
    presented = header[7:].strip()
    for env_var in ("HERMES_CONTROL_API_TOKEN", "HERMES_CONTROL_API_TOKEN_PREVIOUS"):
        expected = os.environ.get(env_var, "").strip()
        if expected and secrets.compare_digest(presented, expected):
            return True
    return False


def _require(scope: str):
    def decorator(fn):
        @wraps(fn)
        def wrapped(*args, **kwargs):
            correlation_id = _correlation_id()
            if not _service_authenticated():
                return _response(error="unauthorized", status=401, correlation_id=correlation_id)
            if scope not in _scopes():
                return _response(error="forbidden", status=403, correlation_id=correlation_id)
            return fn(*args, correlation_id=correlation_id, **kwargs)

        return wrapped

    return decorator


def _payload() -> tuple[dict | None, tuple | None]:
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return None, _response(error="invalid_json", status=400)
    return data, None


def _string(data: dict, key: str, maximum: int, required: bool = False) -> tuple[str | None, str | None]:
    value = data.get(key)
    if value is None:
        return (None, f"{key}_required") if required else (None, None)
    if not isinstance(value, str):
        return None, f"{key}_must_be_string"
    value = value.strip()
    if required and not value:
        return None, f"{key}_required"
    if len(value) > maximum:
        return None, f"{key}_too_long"
    return value or None, None


def _ticket_data(ticket: Ticket) -> dict:
    return ticket.to_dict()


def _audit(operation: str, resource: str, correlation_id: str, result: str) -> None:
    db.session.add(
        ControlApiAuditLog(
            operation=operation,
            resource=resource,
            outcome=result,
            correlation_id=correlation_id,
            created_at=_now(),
        )
    )
    publish_event(
        "control_api.mutation", resource, correlation_id,
        {"operation": operation, "outcome": result, "provider": "hermes", "agent": ACTOR},
    )


def _request_hash(data: dict) -> str:
    return hashlib.sha256(json.dumps(data, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def _replay(operation: str, key: str, request_hash: str, correlation_id: str):
    existing = ControlApiIdempotency.query.filter_by(operation=operation, key=key).first()
    if existing is None:
        return None
    if not secrets.compare_digest(existing.request_hash, request_hash):
        return _response(error="idempotency_conflict", status=409, correlation_id=correlation_id)
    return _response(json.loads(existing.response_json), status=existing.response_status, correlation_id=correlation_id)


def _record_idempotent(operation: str, key: str, request_hash: str, status: int, response: dict) -> None:
    db.session.add(
        ControlApiIdempotency(
            operation=operation,
            key=key,
            request_hash=request_hash,
            response_status=status,
            response_json=json.dumps(response),
            created_at=_now(),
        )
    )


def _require_idempotency(operation: str, data: dict, correlation_id: str):
    key, error = _idempotency_key()
    if error:
        return None, None, error
    request_hash = _request_hash(data)
    replay = _replay(operation, key, request_hash, correlation_id)
    return key, request_hash, replay


def _idempotency_key() -> tuple[str | None, tuple | None]:
    key = request.headers.get("Idempotency-Key", "").strip()
    if not key:
        return None, _response(error="idempotency_key_required", status=400)
    if len(key) > 255:
        return None, _response(error="idempotency_key_too_long", status=400)
    return key, None


@bp.route("/api/control/v1/health")
@_require("health:read")
def health(correlation_id: str):
    return _response({"dashboard": "ok", "hermes_configured": bool(os.environ.get("HERMES_CONTROL_API_TOKEN"))}, correlation_id=correlation_id)


@bp.route("/api/control/v1/projects/<int:project_id>")
@_require("projects:read")
def get_project(project_id: int, correlation_id: str):
    project = GoalProject.query.get(project_id)
    if project is None:
        return _response(error="not_found", status=404, correlation_id=correlation_id)
    return _response(project.to_dict(include_goals=True), correlation_id=correlation_id)


@bp.route("/api/control/v1/tickets/<string:ticket_id>")
@_require("tickets:read")
def get_ticket(ticket_id: str, correlation_id: str):
    ticket = Ticket.query.get(ticket_id)
    if ticket is None:
        return _response(error="not_found", status=404, correlation_id=correlation_id)
    return _response(_ticket_data(ticket), correlation_id=correlation_id)


@bp.route("/api/control/v1/tickets")
@_require("tickets:read")
def list_tickets(correlation_id: str):
    return _response([_ticket_data(ticket) for ticket in Ticket.query.order_by(Ticket.created_at.asc()).all()], correlation_id=correlation_id)


@bp.route("/api/control/v1/tickets/<string:ticket_id>/timeline")
@_require("tickets:read")
def ticket_timeline(ticket_id: str, correlation_id: str):
    ticket = Ticket.query.get(ticket_id)
    if ticket is None:
        return _response(error="not_found", status=404, correlation_id=correlation_id)
    comments = [{**comment.to_dict(), "_type": "comment"} for comment in ticket.comments.order_by(TicketComment.created_at.asc()).all()]
    activities = [{**activity.to_dict(), "_type": "activity"} for activity in ticket.activity.order_by(TicketActivity.created_at.asc()).all()]
    timeline = sorted(comments + activities, key=lambda item: item["created_at"])
    return _response({"timeline": timeline, "total": len(timeline)}, correlation_id=correlation_id)


@bp.route("/api/control/v1/tickets/<string:ticket_id>/checkout", methods=["POST"])
@_require("tickets:write")
def checkout_ticket(ticket_id: str, correlation_id: str):
    data, error = _payload()
    if error:
        return error
    key, request_hash, replay = _require_idempotency(f"checkout_ticket:{ticket_id}", data, correlation_id)
    if replay:
        return replay
    if key is None:
        return request_hash
    ticket = Ticket.query.get(ticket_id)
    if ticket is None:
        return _response(error="not_found", status=404, correlation_id=correlation_id)
    agent, validation = _string(data, "agent", 100, required=True)
    if validation:
        return _response(error=validation, status=400, correlation_id=correlation_id)
    if ticket.locked_at is not None:
        return _response(error="already_locked", status=409, correlation_id=correlation_id)
    ticket.locked_at = _now()
    ticket.locked_by = agent
    ticket.lock_timeout_seconds = data.get("lock_timeout_seconds", 1800)
    ticket.updated_at = _now()
    db.session.add(TicketActivity(id=str(uuid.uuid4()), ticket_id=ticket.id, actor=ACTOR, action="checkout", payload=json.dumps({"agent": agent} ), created_at=_now()))
    response = _ticket_data(ticket)
    _record_idempotent(f"checkout_ticket:{ticket_id}", key, request_hash, 200, response)
    _audit("checkout_ticket", f"ticket:{ticket.id}", correlation_id, "locked")
    db.session.commit()
    return _response(response, correlation_id=correlation_id)


@bp.route("/api/control/v1/tickets/<string:ticket_id>/release", methods=["POST"])
@_require("tickets:write")
def release_ticket(ticket_id: str, correlation_id: str):
    data, error = _payload()
    if error:
        return error
    key, request_hash, replay = _require_idempotency(f"release_ticket:{ticket_id}", data, correlation_id)
    if replay:
        return replay
    if key is None:
        return request_hash
    ticket = Ticket.query.get(ticket_id)
    if ticket is None:
        return _response(error="not_found", status=404, correlation_id=correlation_id)
    agent, validation = _string(data, "agent", 100, required=True)
    if validation:
        return _response(error=validation, status=400, correlation_id=correlation_id)
    if ticket.locked_by != agent:
        return _response(error="not_locked_by_you", status=403, correlation_id=correlation_id)
    ticket.locked_at = None
    ticket.locked_by = None
    ticket.updated_at = _now()
    db.session.add(TicketActivity(id=str(uuid.uuid4()), ticket_id=ticket.id, actor=ACTOR, action="release", payload=json.dumps({"agent": agent}), created_at=_now()))
    response = _ticket_data(ticket)
    _record_idempotent(f"release_ticket:{ticket_id}", key, request_hash, 200, response)
    _audit("release_ticket", f"ticket:{ticket.id}", correlation_id, "released")
    db.session.commit()
    return _response(response, correlation_id=correlation_id)


@bp.route("/api/control/v1/tickets", methods=["POST"])
@_require("tickets:write")
def create_ticket(correlation_id: str):
    data, error = _payload()
    if error:
        return error
    key, request_hash, replay = _require_idempotency("create_ticket", data, correlation_id)
    if replay:
        return replay
    if key is None:
        return request_hash
    title, validation = _string(data, "title", MAX_TITLE, required=True)
    if validation:
        return _response(error=validation, status=400, correlation_id=correlation_id)
    description, validation = _string(data, "description", MAX_DESCRIPTION)
    if validation:
        return _response(error=validation, status=400, correlation_id=correlation_id)
    priority = data.get("priority", "medium")
    if priority not in TICKET_PRIORITIES:
        return _response(error="invalid_priority", status=400, correlation_id=correlation_id)
    status = data.get("status", "open")
    if status not in TICKET_STATUSES:
        return _response(error="invalid_status", status=400, correlation_id=correlation_id)

    now = _now()
    ticket = Ticket(
        id=str(uuid.uuid4()), title=title, description=description, priority=priority, status=status,
        created_at=now, updated_at=now,
    )
    response = _ticket_data(ticket)
    db.session.add(ticket)
    _record_idempotent("create_ticket", key, request_hash, 201, response)
    _audit("create_ticket", f"ticket:{ticket.id}", correlation_id, "created")
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return _replay("create_ticket", key, request_hash, correlation_id)
    return _response(response, status=201, correlation_id=correlation_id)


@bp.route("/api/control/v1/tickets/<string:ticket_id>", methods=["PATCH"])
@_require("tickets:write")
def update_ticket(ticket_id: str, correlation_id: str):
    data, error = _payload()
    if error:
        return error
    key, request_hash, replay = _require_idempotency(f"update_ticket:{ticket_id}", data, correlation_id)
    if replay:
        return replay
    if key is None:
        return request_hash
    ticket = Ticket.query.get(ticket_id)
    if ticket is None:
        return _response(error="not_found", status=404, correlation_id=correlation_id)
    allowed = {"title", "description", "priority", "status"}
    if not data or set(data) - allowed:
        return _response(error="invalid_fields", status=400, correlation_id=correlation_id)
    if "title" in data:
        title, validation = _string(data, "title", MAX_TITLE, required=True)
        if validation:
            return _response(error=validation, status=400, correlation_id=correlation_id)
        ticket.title = title
    if "description" in data:
        description, validation = _string(data, "description", MAX_DESCRIPTION)
        if validation:
            return _response(error=validation, status=400, correlation_id=correlation_id)
        ticket.description = description
    if "priority" in data:
        if data["priority"] not in TICKET_PRIORITIES:
            return _response(error="invalid_priority", status=400, correlation_id=correlation_id)
        ticket.priority = data["priority"]
    if "status" in data:
        if data["status"] not in TICKET_STATUSES:
            return _response(error="invalid_status", status=400, correlation_id=correlation_id)
        ticket.status = data["status"]
    ticket.updated_at = _now()
    response = _ticket_data(ticket)
    _record_idempotent(f"update_ticket:{ticket_id}", key, request_hash, 200, response)
    _audit("update_ticket", f"ticket:{ticket.id}", correlation_id, "updated")
    db.session.commit()
    return _response(response, correlation_id=correlation_id)


@bp.route("/api/control/v1/tickets/<string:ticket_id>/comments", methods=["POST"])
@_require("comments:write")
def create_comment(ticket_id: str, correlation_id: str):
    data, error = _payload()
    if error:
        return error
    key, request_hash, replay = _require_idempotency(f"create_comment:{ticket_id}", data, correlation_id)
    if replay:
        return replay
    if key is None:
        return request_hash
    ticket = Ticket.query.get(ticket_id)
    if ticket is None:
        return _response(error="not_found", status=404, correlation_id=correlation_id)
    body, validation = _string(data, "body", MAX_COMMENT, required=True)
    if validation:
        return _response(error=validation, status=400, correlation_id=correlation_id)
    comment = TicketComment(id=str(uuid.uuid4()), ticket_id=ticket.id, author=ACTOR, body=body, created_at=_now())
    response = comment.to_dict()
    db.session.add(comment)
    _record_idempotent(f"create_comment:{ticket_id}", key, request_hash, 201, response)
    _audit("create_comment", f"ticket:{ticket.id}", correlation_id, "created")
    db.session.commit()
    return _response(response, status=201, correlation_id=correlation_id)


@bp.route("/api/control/v1/tickets/<string:ticket_id>/evidence", methods=["POST"])
@_require("evidence:write")
def create_evidence(ticket_id: str, correlation_id: str):
    data, error = _payload()
    if error:
        return error
    key, request_hash, replay = _require_idempotency(f"create_evidence:{ticket_id}", data, correlation_id)
    if replay:
        return replay
    if key is None:
        return request_hash
    ticket = Ticket.query.get(ticket_id)
    if ticket is None:
        return _response(error="not_found", status=404, correlation_id=correlation_id)
    evidence, validation = _string(data, "evidence", MAX_EVIDENCE, required=True)
    if validation:
        return _response(error=validation, status=400, correlation_id=correlation_id)
    if ".." in evidence or evidence.startswith("/"):
        return _response(error="invalid_evidence", status=400, correlation_id=correlation_id)
    comment = TicketComment(id=str(uuid.uuid4()), ticket_id=ticket.id, author=ACTOR, body=f"Evidence: {evidence}", created_at=_now())
    response = comment.to_dict()
    db.session.add(comment)
    _record_idempotent(f"create_evidence:{ticket_id}", key, request_hash, 201, response)
    _audit("create_evidence", f"ticket:{ticket.id}", correlation_id, "created")
    db.session.commit()
    return _response(response, status=201, correlation_id=correlation_id)

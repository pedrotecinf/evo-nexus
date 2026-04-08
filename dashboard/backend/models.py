"""SQLAlchemy models for OpenClaude dashboard."""

import json
from datetime import datetime, timezone
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
import bcrypt

db = SQLAlchemy()


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True)
    password_hash = db.Column(db.String(128), nullable=False)
    display_name = db.Column(db.String(120))
    avatar_url = db.Column(db.String(500))
    role = db.Column(db.String(20), nullable=False, default="viewer")
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    last_login = db.Column(db.DateTime)
    created_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)

    def set_password(self, password: str):
        self.password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt(12)).decode()

    def check_password(self, password: str) -> bool:
        return bcrypt.checkpw(password.encode(), self.password_hash.encode())

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "display_name": self.display_name,
            "avatar_url": self.avatar_url,
            "role": self.role,
            "is_active": self.is_active,
            "created_at": self.created_at.strftime("%Y-%m-%dT%H:%M:%S.%fZ") if self.created_at else None,
            "last_login": self.last_login.strftime("%Y-%m-%dT%H:%M:%S.%fZ") if self.last_login else None,
        }


class AuditLog(db.Model):
    __tablename__ = "audit_log"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    username = db.Column(db.String(80))
    action = db.Column(db.String(50), nullable=False)
    resource = db.Column(db.String(100))
    detail = db.Column(db.Text)
    ip_address = db.Column(db.String(45))
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "username": self.username,
            "action": self.action,
            "resource": self.resource,
            "detail": self.detail,
            "ip_address": self.ip_address,
            "created_at": self.created_at.strftime("%Y-%m-%dT%H:%M:%S.%fZ") if self.created_at else None,
        }


# All available resources and their possible actions
ALL_RESOURCES = {
    "chat": ["view", "execute", "manage"],
    "services": ["view", "execute", "manage"],
    "systems": ["view", "execute", "manage"],
    "integrations": ["view", "execute", "manage"],
    "reports": ["view", "manage"],
    "agents": ["view", "manage"],
    "memory": ["view", "manage"],
    "skills": ["view", "manage"],
    "costs": ["view", "manage"],
    "config": ["view", "manage"],
    "users": ["view", "manage"],
    "audit": ["view"],
    "files": ["view", "manage"],
    "templates": ["view"],
    "routines": ["view", "execute"],
    "scheduler": ["view", "execute"],
}

# Default permissions for built-in roles (used when seeding)
BUILTIN_ROLES = {
    "admin": {
        "description": "Full access to all resources",
        "permissions": {r: actions[:] for r, actions in ALL_RESOURCES.items()},
    },
    "operator": {
        "description": "Can view and execute, but not manage users or audit",
        "permissions": {
            "chat": ["view", "execute"],
            "services": ["view", "execute"],
            "systems": ["view", "execute"],
            "integrations": ["view", "execute"],
            "reports": ["view"],
            "agents": ["view"],
            "memory": ["view"],
            "skills": ["view"],
            "costs": ["view"],
            "config": ["view"],
            "files": ["view"],
            "templates": ["view"],
            "routines": ["view", "execute"],
            "scheduler": ["view", "execute"],
        },
    },
    "viewer": {
        "description": "Read-only access to dashboards",
        "permissions": {
            "reports": ["view"],
            "agents": ["view"],
            "memory": ["view"],
            "skills": ["view"],
            "costs": ["view"],
            "config": ["view"],
            "files": ["view"],
            "templates": ["view"],
            "services": ["view"],
            "systems": ["view"],
            "integrations": ["view"],
            "routines": ["view"],
            "scheduler": ["view"],
        },
    },
}


class Role(db.Model):
    __tablename__ = "roles"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.String(200))
    permissions_json = db.Column(db.Text, nullable=False, default="{}")
    is_builtin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    @property
    def permissions(self) -> dict:
        try:
            return json.loads(self.permissions_json)
        except (json.JSONDecodeError, TypeError):
            return {}

    @permissions.setter
    def permissions(self, value: dict):
        self.permissions_json = json.dumps(value)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "permissions": self.permissions,
            "is_builtin": self.is_builtin,
            "created_at": self.created_at.strftime("%Y-%m-%dT%H:%M:%S.%fZ") if self.created_at else None,
        }


def seed_roles():
    """Create built-in roles if they don't exist."""
    for name, config in BUILTIN_ROLES.items():
        existing = Role.query.filter_by(name=name).first()
        if not existing:
            role = Role(
                name=name,
                description=config["description"],
                is_builtin=True,
            )
            role.permissions = config["permissions"]
            db.session.add(role)
    db.session.commit()


def get_role_permissions(role_name: str) -> dict:
    """Get permissions for a role from DB, fallback to builtin defaults."""
    role = Role.query.filter_by(name=role_name).first()
    if role:
        return role.permissions
    # Fallback to builtin
    builtin = BUILTIN_ROLES.get(role_name)
    if builtin:
        return builtin["permissions"]
    return {}


def has_permission(role: str, resource: str, action: str) -> bool:
    perms = get_role_permissions(role)
    return action in perms.get(resource, [])


def audit(user, action: str, resource: str = None, detail: str = None):
    """Log an action to the audit trail."""
    from flask import request
    entry = AuditLog(
        user_id=user.id if user else None,
        username=user.username if user else "system",
        action=action,
        resource=resource,
        detail=detail,
        ip_address=request.remote_addr if request else None,
    )
    db.session.add(entry)
    db.session.commit()


def needs_setup() -> bool:
    """Check if the system needs initial setup (no users exist)."""
    try:
        return User.query.count() == 0
    except Exception:
        return True

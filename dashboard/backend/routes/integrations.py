"""Integrations endpoint — check configured integrations via env vars."""

import os
from flask import Blueprint, jsonify

bp = Blueprint("integrations", __name__)

INTEGRATIONS = [
    {"name": "Omie", "key": "OMIE_APP_KEY", "category": "erp"},
    {"name": "Stripe", "key": "STRIPE_SECRET_KEY", "category": "payments"},
    {"name": "Todoist", "key": "TODOIST_API_TOKEN", "category": "productivity"},
    {"name": "Fathom", "key": "FATHOM_API_KEY", "category": "meetings"},
    {"name": "Discord", "key": "DISCORD_BOT_TOKEN", "category": "community"},
    {"name": "Telegram", "key": "TELEGRAM_BOT_TOKEN", "category": "messaging"},
    {"name": "WhatsApp", "key": "WHATSAPP_API_KEY", "category": "messaging"},
    {"name": "Licensing", "key": "LICENSING_ADMIN_TOKEN", "category": "product"},
    {"name": "YouTube", "key": "SOCIAL_YOUTUBE_", "category": "social", "prefix": True},
    {"name": "Instagram", "key": "SOCIAL_INSTAGRAM_", "category": "social", "prefix": True},
    {"name": "LinkedIn", "key": "SOCIAL_LINKEDIN_", "category": "social", "prefix": True},
]


@bp.route("/api/integrations")
def list_integrations():
    results = []
    for integ in INTEGRATIONS:
        if integ.get("prefix"):
            # Check if any env var starts with the prefix
            configured = any(k.startswith(integ["key"]) for k in os.environ)
        else:
            configured = bool(os.environ.get(integ["key"]))

        results.append({
            "name": integ["name"],
            "category": integ["category"],
            "configured": configured,
            "status": "ok" if configured else "pending",
            "type": integ["category"],
        })

    configured_count = sum(1 for r in results if r["configured"])
    return jsonify({
        "integrations": results,
        "configured_count": configured_count,
        "total_count": len(results),
    })

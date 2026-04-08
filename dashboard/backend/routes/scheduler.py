"""Scheduler endpoint — parse scheduler.py to extract schedule entries."""

import re
from flask import Blueprint, jsonify
from routes._helpers import WORKSPACE, safe_read

bp = Blueprint("scheduler", __name__)


@bp.route("/api/scheduler")
def get_schedule():
    content = safe_read(WORKSPACE / "scheduler.py")
    if not content:
        return jsonify([])

    entries = []

    # Match: schedule.every().day.at("HH:MM").do(run_adw, "Name", "script.py")
    # Or:    schedule.every(30).minutes.do(run_adw, "Name", "script.py")
    # Or:    schedule.every().friday.at("HH:MM").do(run_adw, "Name", "script.py")
    pattern = re.compile(
        r'schedule\.every\(([^)]*)\)\.'
        r'([\w.]+)'
        r'(?:\.at\(["\']([^"\']+)["\']\))?'
        r'\.do\(\s*(\w+)'
        r'(?:\s*,\s*["\']([^"\']*)["\'])?'   # first string arg = name
        r'(?:\s*,\s*["\']([^"\']*)["\'])?'    # second string arg = script
    )

    # Agent mapping from script name
    SCRIPT_AGENTS = {
        "review_todoist": "clawdia", "good_morning": "clawdia", "email_triage": "clawdia",
        "sync_meetings": "clawdia", "end_of_day": "clawdia", "memory_sync": "clawdia",
        "weekly_review": "clawdia", "trends": "clawdia", "dashboard": "clawdia",
        "community_daily": "pulse", "community_weekly": "pulse", "community_monthly": "pulse",
        "faq_sync": "pulse", "financial_pulse": "flux", "financial_weekly": "flux",
        "monthly_close": "flux", "licensing_daily": "atlas", "licensing_weekly": "atlas",
        "licensing_monthly": "atlas", "github_review": "atlas", "linear_review": "atlas",
        "health_checkin": "kai", "strategy_digest": "sage",
        "social_analytics": "pixel", "youtube_report": "pixel", "instagram_report": "pixel",
        "linkedin_report": "pixel",
    }

    for m in pattern.finditer(content):
        interval, freq_chain, time_str, func_name, name_arg, script_arg = m.groups()

        # Determine frequency
        days = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
        day_match = [d for d in days if d in freq_chain.lower()]

        if day_match:
            frequency = "weekly"
            day_label = day_match[0].capitalize()
        elif "minute" in freq_chain:
            frequency = f"every {interval or '1'} min"
            day_label = ""
        elif "hour" in freq_chain:
            frequency = f"every {interval or '1'} hour"
            day_label = ""
        else:
            frequency = "daily"
            day_label = ""

        schedule_str = f"{frequency}"
        if day_label:
            schedule_str = f"{day_label}"
        if time_str:
            schedule_str += f" @ {time_str}"

        # Get real name from first arg, or derive from script
        task_name = name_arg or ""
        script = script_arg or ""

        if not task_name and script:
            task_name = script.replace(".py", "").replace("_", " ").title()

        # Get agent from script name
        script_key = script.replace(".py", "") if script else ""
        agent = SCRIPT_AGENTS.get(script_key, "")

        entries.append({
            "name": task_name,
            "script": script,
            "schedule": schedule_str,
            "frequency": frequency,
            "time": time_str or "",
            "agent": agent,
        })

    return jsonify(entries)

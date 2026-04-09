"""Services endpoint — check running background services."""

import subprocess
from flask import Blueprint, jsonify
from routes._helpers import WORKSPACE

bp = Blueprint("services", __name__)


def _check_process(check_cmd: str) -> dict:
    try:
        result = subprocess.run(check_cmd, shell=True, capture_output=True, text=True, timeout=5)
        running = result.returncode == 0 and result.stdout.strip() != ""
        return {"running": running, "detail": result.stdout.strip()[:200] if running else ""}
    except Exception:
        return {"running": False, "detail": ""}


def _check_scheduler() -> dict:
    """Check if scheduler thread is running inside the dashboard process."""
    import threading
    for t in threading.enumerate():
        if t.name == "scheduler" and t.is_alive():
            return {"running": True, "detail": "Running (embedded in dashboard)"}
    # Fallback: check for standalone scheduler.py process
    result = _check_process("ps aux | grep '[s]cheduler.py' | grep -v grep")
    return result


@bp.route("/api/services")
def list_services():
    services = [
        {
            "id": "scheduler",
            "name": "Scheduler",
            "description": "Automated routines (daily, weekly, monthly) — runs with dashboard",
            "command": "make dashboard-app",
            **_check_scheduler(),
        },
        {
            "id": "telegram",
            "name": "Telegram Bot",
            "description": "Telegram Bot — receives and responds to messages via Claude",
            "command": "make telegram",
            **_check_process("screen -list 2>/dev/null | grep telegram"),
        },
        {
            "id": "dashboard",
            "name": "Dashboard App",
            "description": "This dashboard (React + Flask)",
            "command": "make dashboard-app",
            **_check_process("ps aux | grep '[a]pp.py' | grep dashboard"),
        },
    ]

    return jsonify(services)


WORKSPACE_STR = str(WORKSPACE)

# ── Manual routine execution ─────────────────────────


@bp.route("/api/routines/<routine_id>/run", methods=["POST"])
def run_routine(routine_id):
    """Manually trigger a routine execution."""
    from routes._helpers import get_routine_scripts
    routine_scripts = get_routine_scripts()

    script = routine_scripts.get(routine_id)
    if not script:
        # Try matching by script name
        for name, s in routine_scripts.items():
            if routine_id.replace("-", "_") in s or s.replace(".py", "") == routine_id.replace("-", "_"):
                script = s
                break
    if not script:
        return jsonify({"error": f"Unknown routine: {routine_id}"}), 400

    cmd = f"cd {WORKSPACE_STR} && nohup uv run python ADWs/routines/{script} > /dev/null 2>&1 &"
    try:
        subprocess.Popen(cmd, shell=True)
        return jsonify({"status": "started", "routine": routine_id, "script": script})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


TELEGRAM_LOG = f"{WORKSPACE_STR}/ADWs/logs/telegram.log"
SCHEDULER_LOG = f"{WORKSPACE_STR}/ADWs/logs/scheduler.log"

START_CMDS = {
    "scheduler": f"cd {WORKSPACE_STR} && nohup uv run python -u scheduler.py >> {SCHEDULER_LOG} 2>&1 &",
    "telegram": f"cd {WORKSPACE_STR} && screen -dmS telegram claude --channels plugin:telegram@claude-plugins-official --dangerously-skip-permissions",
}

STOP_CMDS = {
    "scheduler": "pkill -f 'scheduler.py' 2>/dev/null",
    "telegram": "screen -S telegram -X quit 2>/dev/null",
}


@bp.route("/api/services/<service_id>/start", methods=["POST"])
def start_service(service_id):
    cmd = START_CMDS.get(service_id)
    if not cmd:
        return jsonify({"error": f"Unknown service: {service_id}"}), 400
    try:
        subprocess.Popen(cmd, shell=True)
        return jsonify({"status": "started", "id": service_id})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route("/api/services/<service_id>/logs")
def service_logs(service_id):
    """Get recent output from a service."""
    if service_id == "telegram":
        from routes._helpers import safe_read

        # Read from log file
        log_path = WORKSPACE / "ADWs" / "logs" / "telegram.log"
        content = safe_read(log_path)
        if content:
            # Clean ANSI escape codes and control chars
            import re
            clean = re.sub(r'\x1b\[[0-9;]*[a-zA-Z]', '', content)
            clean = re.sub(r'\x1b\][^\x07]*\x07', '', clean)  # OSC sequences
            clean = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f]', '', clean)  # control chars
            lines = [l for l in clean.split('\n') if l.strip()]
            if lines:
                return jsonify({"lines": lines[-200:]})

        # Check if running but no log yet
        try:
            result = subprocess.run("screen -list 2>/dev/null | grep telegram", shell=True, capture_output=True, text=True, timeout=3)
            if result.returncode == 0:
                return jsonify({"lines": [
                    "Telegram bot is running.",
                    "Log file will populate as messages are processed.",
                    "",
                    "If started before this update, restart with Stop → Start",
                    "to enable logging.",
                    "",
                    f"Screen: {result.stdout.strip()}",
                ]})
        except Exception:
            pass

        return jsonify({"lines": ["Telegram bot is not running. Click Start to launch it."]})

    elif service_id == "scheduler":
        from routes._helpers import safe_read

        # Read real scheduler process output
        log_path = WORKSPACE / "ADWs" / "logs" / "scheduler.log"
        content = safe_read(log_path)
        if content:
            import re
            # Clean ANSI escape codes and control chars (Rich output)
            clean = re.sub(r'\x1b\[[0-9;]*[a-zA-Z]', '', content)
            clean = re.sub(r'\x1b\][^\x07]*\x07', '', clean)  # OSC sequences
            clean = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f]', '', clean)  # control chars
            lines = [l for l in clean.split('\n') if l.strip()]
            if lines:
                return jsonify({"lines": lines[-200:]})

        # Check if running but no log yet
        try:
            result = subprocess.run("ps aux | grep '[s]cheduler.py'", shell=True, capture_output=True, text=True, timeout=3)
            if result.returncode == 0 and result.stdout.strip():
                return jsonify({"lines": [
                    "Scheduler is running.",
                    "Log file will populate as routines execute.",
                    "",
                    "If started before this update, restart with Stop → Start",
                    "to enable log capture.",
                ]})
        except Exception:
            pass

        return jsonify({"lines": ["Scheduler is not running. Click Start to launch it."]})

    return jsonify({"error": "Unknown service"}), 400


@bp.route("/api/services/<service_id>/stop", methods=["POST"])
def stop_service(service_id):
    cmd = STOP_CMDS.get(service_id)
    if not cmd:
        return jsonify({"error": f"Unknown service: {service_id}"}), 400
    try:
        subprocess.run(cmd, shell=True, timeout=5)
        return jsonify({"status": "stopped", "id": service_id})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

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


@bp.route("/api/services")
def list_services():
    services = [
        {
            "id": "scheduler",
            "name": "Scheduler",
            "description": "Rotinas automatizadas (diárias, semanais, mensais)",
            "command": "make scheduler",
            **_check_process("ps aux | grep '[s]cheduler.py' | grep -v grep"),
        },
        {
            "id": "telegram",
            "name": "Telegram Bot",
            "description": "Bot Telegram — recebe e responde mensagens via Claude",
            "command": "make telegram",
            **_check_process("screen -list 2>/dev/null | grep telegram"),
        },
        {
            "id": "dashboard",
            "name": "Dashboard App",
            "description": "Este dashboard (React + Flask)",
            "command": "make dashboard-app",
            **_check_process("ps aux | grep '[a]pp.py' | grep dashboard"),
        },
    ]

    # Add Docker containers
    try:
        result = subprocess.run(
            'docker ps --format "{{.Names}}\\t{{.Status}}\\t{{.Ports}}\\t{{.Image}}"',
            shell=True, capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0:
            for line in result.stdout.strip().splitlines():
                parts = line.split('\t')
                if len(parts) >= 4:
                    name, status, ports, image = parts[0], parts[1], parts[2], parts[3]
                    # Extract port mapping
                    port_str = ""
                    if "0.0.0.0:" in ports:
                        import re
                        port_match = re.search(r'0\.0\.0\.0:(\d+)', ports)
                        if port_match:
                            port_str = f":{port_match.group(1)}"

                    services.append({
                        "id": f"docker-{name}",
                        "name": name,
                        "description": f"{image}{port_str}",
                        "command": f"docker start {name}",
                        "running": "Up" in status,
                        "detail": status,
                        "category": "docker",
                    })
    except Exception:
        pass

    return jsonify(services)


WORKSPACE_STR = str(WORKSPACE)

# ── Manual routine execution ─────────────────────────

ROUTINE_SCRIPTS = {
    "morning": "good_morning.py", "sync": "sync_meetings.py", "triage": "email_triage.py",
    "review": "review_todoist.py", "memory": "memory_sync.py", "eod": "end_of_day.py",
    "dashboard": "dashboard.py", "fin-pulse": "financial_pulse.py", "youtube": "youtube_report.py",
    "instagram": "instagram_report.py", "linkedin": "linkedin_report.py", "social": "social_analytics.py",
    "licensing": "licensing_daily.py", "weekly": "weekly_review.py", "health": "health_checkin.py",
    "trends": "trends.py", "linear": "linear_review.py", "community": "community_daily.py",
    "community-week": "community_weekly.py", "community-month": "community_monthly.py",
    "github": "github_review.py", "faq": "faq_sync.py", "strategy": "strategy_digest.py",
    "fin-weekly": "financial_weekly.py", "licensing-weekly": "licensing_weekly.py",
    "fin-close": "monthly_close.py", "licensing-month": "licensing_monthly.py",
}


@bp.route("/api/routines/<routine_id>/run", methods=["POST"])
def run_routine(routine_id):
    """Manually trigger a routine."""
    script = ROUTINE_SCRIPTS.get(routine_id)
    if not script:
        # Try matching by script name
        for name, s in ROUTINE_SCRIPTS.items():
            if routine_id.replace("-", "_") in s or s.replace(".py", "") == routine_id.replace("-", "_"):
                script = s
                break
    if not script:
        return jsonify({"error": f"Unknown routine: {routine_id}"}), 400

    cmd = f"cd {WORKSPACE_STR} && nohup uv run python ADWs/rotinas/{script} > /dev/null 2>&1 &"
    try:
        subprocess.Popen(cmd, shell=True)
        return jsonify({"status": "started", "routine": routine_id, "script": script})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


TELEGRAM_LOG = f"{WORKSPACE_STR}/ADWs/logs/telegram.log"

START_CMDS = {
    "scheduler": f"cd {WORKSPACE_STR} && nohup uv run python scheduler.py > /dev/null 2>&1 &",
    "telegram": f"cd {WORKSPACE_STR} && screen -dmS telegram -L -Logfile {TELEGRAM_LOG} claude --channels plugin:telegram@claude-plugins-official --dangerously-skip-permissions",
}

STOP_CMDS = {
    "scheduler": "pkill -f 'scheduler.py' 2>/dev/null",
    "telegram": "screen -S telegram -X quit 2>/dev/null",
}


@bp.route("/api/services/<service_id>/start", methods=["POST"])
def start_service(service_id):
    # Docker containers
    if service_id.startswith("docker-"):
        container = service_id[7:]
        try:
            subprocess.run(f"docker start {container}", shell=True, timeout=10)
            return jsonify({"status": "started", "id": service_id})
        except Exception as e:
            return jsonify({"error": str(e)}), 500

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
        # Read execution logs from JSONL files (real scheduler activity)
        import json as _json
        from datetime import date, timedelta
        from routes._helpers import safe_read
        logs_dir = WORKSPACE / "ADWs" / "logs"

        lines = []
        if logs_dir.is_dir():
            # Read last 3 days of JSONL logs
            today = date.today()
            for offset in range(3):
                d = today - timedelta(days=offset)
                jsonl_file = logs_dir / f"{d.isoformat()}.jsonl"
                if jsonl_file.is_file():
                    content = safe_read(jsonl_file)
                    if content:
                        for raw_line in content.strip().splitlines():
                            try:
                                entry = _json.loads(raw_line)
                                ts = entry.get("timestamp", "")[:19].replace("T", " ")
                                name = entry.get("run", "?")
                                rc = entry.get("returncode", -1)
                                dur = entry.get("duration_seconds", 0)
                                cost = entry.get("cost_usd", 0)
                                status = "✓" if rc == 0 else "✗"
                                lines.append(f"{ts}  {status}  {name:<25} {dur:>6.1f}s  ${cost:.4f}")
                            except (_json.JSONDecodeError, KeyError):
                                continue

        if lines:
            # Header
            header = f"{'Timestamp':<20}  {'':>1}  {'Routine':<25} {'Duration':>8}  {'Cost':>8}"
            separator = "-" * len(header)
            return jsonify({"lines": [header, separator] + lines[-100:]})

        return jsonify({"lines": ["No scheduler execution logs yet.", "", "Logs appear here after routines run."]})

    # Docker container logs
    if service_id.startswith("docker-"):
        container = service_id[7:]
        try:
            result = subprocess.run(f"docker logs --tail 100 {container}", shell=True, capture_output=True, text=True, timeout=5)
            lines = [l for l in result.stdout.split('\n') if l.strip()]
            if not lines:
                lines = [l for l in result.stderr.split('\n') if l.strip()]
            return jsonify({"lines": lines[-100:]})
        except Exception:
            return jsonify({"lines": [f"Failed to get logs for {container}"]})

    return jsonify({"error": "Unknown service"}), 400


@bp.route("/api/services/<service_id>/stop", methods=["POST"])
def stop_service(service_id):
    # Docker containers
    if service_id.startswith("docker-"):
        container = service_id[7:]
        try:
            subprocess.run(f"docker stop {container}", shell=True, timeout=15)
            return jsonify({"status": "stopped", "id": service_id})
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    cmd = STOP_CMDS.get(service_id)
    if not cmd:
        return jsonify({"error": f"Unknown service: {service_id}"}), 400
    try:
        subprocess.run(cmd, shell=True, timeout=5)
        return jsonify({"status": "stopped", "id": service_id})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

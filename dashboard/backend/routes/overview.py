"""Overview endpoint — summary data for the dashboard home."""

import json
from flask import Blueprint, jsonify
from routes._helpers import WORKSPACE, safe_read

bp = Blueprint("overview", __name__)

REPORT_DIRS = [
    "01 Daily Logs",
    "03 Comunidade/reports",
    "04 Redes Sociais/reports",
    "05 Financeiro/reports",
    "02 Projects/licensing-reports",
    "09 Estrategia/digests",
]


def _recent_reports(limit: int = 10) -> list[dict]:
    """Scan report dirs for recent HTML/MD files."""
    files = []
    for d in REPORT_DIRS:
        dirpath = WORKSPACE / d
        if not dirpath.is_dir():
            continue
        for f in dirpath.rglob("*"):
            if f.is_file() and f.suffix.lower() in (".html", ".md"):
                try:
                    files.append({
                        "name": f.name,
                        "path": str(f.relative_to(WORKSPACE)),
                        "area": d.split("/")[0],
                        "extension": f.suffix,
                        "modified": f.stat().st_mtime,
                    })
                except Exception:
                    continue
    files.sort(key=lambda x: x.get("modified", 0), reverse=True)
    return files[:limit]


def _metrics_summary() -> dict:
    """Load routine metrics summary from ADWs/logs/metrics.json."""
    path = WORKSPACE / "ADWs" / "logs" / "metrics.json"
    content = safe_read(path)
    if content:
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            pass
    return {}


def _integration_count() -> int:
    """Count integrations with configured env vars."""
    import os
    keys = [
        "OMIE_APP_KEY", "STRIPE_SECRET_KEY", "TODOIST_API_TOKEN",
        "FATHOM_API_KEY", "DISCORD_BOT_TOKEN", "TELEGRAM_BOT_TOKEN",
        "WHATSAPP_API_KEY", "LICENSING_ADMIN_TOKEN",
    ]
    return sum(1 for k in keys if os.environ.get(k))


def _build_overview_metrics(raw_metrics: dict, integration_count: int) -> list[dict]:
    """Transform raw metrics.json into overview KPI cards."""
    total_runs = sum(v.get("runs", 0) for v in raw_metrics.values())
    total_cost = sum(v.get("total_cost_usd", 0) for v in raw_metrics.values())
    total_success = sum(v.get("successes", 0) for v in raw_metrics.values())
    success_rate = round((total_success / total_runs * 100), 1) if total_runs > 0 else 0

    agents_count = len(list((WORKSPACE / ".claude" / "agents").glob("*.md"))) if (WORKSPACE / ".claude" / "agents").is_dir() else 0
    skills_count = len([d for d in (WORKSPACE / ".claude" / "skills").iterdir() if d.is_dir()]) if (WORKSPACE / ".claude" / "skills").is_dir() else 0

    return [
        {"label": "Rotinas Executadas", "value": total_runs, "delta": f"{success_rate}% success", "deltaType": "up" if success_rate >= 90 else "neutral"},
        {"label": "Custo Total", "value": f"${total_cost:.2f}", "delta": f"${total_cost / max(total_runs, 1):.2f}/run", "deltaType": "neutral"},
        {"label": "Agentes", "value": agents_count, "delta": f"{skills_count} skills", "deltaType": "neutral"},
        {"label": "Integrações Ativas", "value": integration_count},
    ]


def _build_routines(raw_metrics: dict) -> list[dict]:
    """Transform raw metrics into routines table."""
    routines = []
    for name, v in sorted(raw_metrics.items(), key=lambda x: x[1].get("last_run", ""), reverse=True):
        rate = v.get("success_rate", 0)
        status = "healthy" if rate >= 90 else ("warning" if rate >= 50 else "critical")
        routines.append({
            "name": name,
            "last_run": (v.get("last_run") or "")[:16],
            "status": status,
            "runs": v.get("runs", 0),
        })
    return routines[:10]


@bp.route("/api/overview")
def overview():
    raw_metrics = _metrics_summary()
    ic = _integration_count()
    reports = _recent_reports()

    return jsonify({
        "recent_reports": [{"title": r["name"], "path": r["path"], "date": r["path"].split("/")[-1][:10] if "/" in r["path"] else "", "area": r["area"]} for r in reports],
        "metrics": _build_overview_metrics(raw_metrics, ic),
        "routines": _build_routines(raw_metrics),
        "integration_count": ic,
    })

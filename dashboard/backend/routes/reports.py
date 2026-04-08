"""Reports endpoint — list and serve report files."""

import re
from datetime import datetime
from flask import Blueprint, jsonify, request, Response, abort
from routes._helpers import WORKSPACE, safe_read

bp = Blueprint("reports", __name__)

REPORT_DIRS = {
    "workspace/daily-logs": "daily",
    "workspace/community/reports": "community",
    "workspace/social/reports": "social",
    "workspace/finance/reports": "financial",
    "workspace/projects/reports": "projects",
    "workspace/strategy/digests": "strategy",
}


def _detect_type(name: str) -> str:
    low = name.lower()
    if "weekly" in low or "semanal" in low:
        return "weekly"
    if "monthly" in low or "mensal" in low:
        return "monthly"
    return "daily"


def _extract_date(name: str) -> str | None:
    """Try to extract a date from the filename."""
    m = re.search(r"(\d{4}-\d{2}-\d{2})", name)
    if m:
        return m.group(1)
    m = re.search(r"(\d{4}_\d{2}_\d{2})", name)
    if m:
        return m.group(1).replace("_", "-")
    return None


def _list_reports() -> list[dict]:
    reports = []
    for rel_dir, area in REPORT_DIRS.items():
        dirpath = WORKSPACE / rel_dir
        if not dirpath.is_dir():
            continue
        for f in dirpath.rglob("*"):
            if f.is_file() and f.suffix.lower() in (".html", ".md"):
                reports.append({
                    "path": str(f.relative_to(WORKSPACE)),
                    "name": f.stem,
                    "area": area,
                    "type": _detect_type(f.name),
                    "date": _extract_date(f.name),
                    "extension": f.suffix,
                    "modified": f.stat().st_mtime,
                })
    reports.sort(key=lambda x: x.get("modified", 0), reverse=True)
    return reports


@bp.route("/api/reports")
def list_reports():
    reports = _list_reports()

    # Filter by query params
    area = request.args.get("area")
    rtype = request.args.get("type")
    date = request.args.get("date")

    if area:
        reports = [r for r in reports if r["area"] == area]
    if rtype:
        reports = [r for r in reports if r["type"] == rtype]
    if date:
        reports = [r for r in reports if r.get("date") == date]

    return jsonify(reports)


@bp.route("/api/reports/<path:filepath>")
def get_report(filepath):
    full = WORKSPACE / filepath
    if not full.is_file():
        abort(404, description="Report not found")
    # Security: ensure path is inside workspace
    try:
        full.resolve().relative_to(WORKSPACE.resolve())
    except ValueError:
        abort(403, description="Access denied")

    content = safe_read(full)
    if content is None:
        abort(500, description="Could not read file")

    mime = "text/html" if full.suffix.lower() == ".html" else "text/markdown"
    return Response(content, mimetype=mime)

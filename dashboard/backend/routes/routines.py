"""Routines endpoint — metrics, logs, and ADW scripts."""

import ast
import json
from datetime import date
from flask import Blueprint, jsonify, request
from routes._helpers import WORKSPACE, safe_read

bp = Blueprint("routines", __name__)

METRICS_PATH = WORKSPACE / "ADWs" / "logs" / "metrics.json"
LOGS_DIR = WORKSPACE / "ADWs" / "logs"
ROTINAS_DIR = WORKSPACE / "ADWs" / "rotinas"


@bp.route("/api/routines")
def get_routines():
    content = safe_read(METRICS_PATH)
    if not content:
        return jsonify({"metrics": {}, "totals": {}})
    try:
        data = json.loads(content)
    except json.JSONDecodeError:
        return jsonify({"metrics": {}, "totals": {}})

    # Calculate totals
    totals = {"total_runs": 0, "total_cost": 0.0, "total_tokens": 0}
    if isinstance(data, dict):
        for key, val in data.items():
            if isinstance(val, dict):
                totals["total_runs"] += val.get("runs", 0)
                totals["total_cost"] += val.get("cost", 0.0)
                totals["total_tokens"] += val.get("tokens", 0)

    return jsonify({"metrics": data, "totals": totals})


@bp.route("/api/routines/logs")
def get_routine_logs():
    target = request.args.get("date", date.today().isoformat())
    # Look for JSONL files matching the date
    entries = []
    if LOGS_DIR.is_dir():
        for f in LOGS_DIR.iterdir():
            if f.suffix == ".jsonl" and target in f.name:
                text = safe_read(f)
                if text:
                    for line in text.strip().splitlines():
                        try:
                            entries.append(json.loads(line))
                        except json.JSONDecodeError:
                            continue
        # Also check a generic log file
        generic = LOGS_DIR / f"{target}.jsonl"
        if generic.is_file():
            text = safe_read(generic)
            if text:
                for line in text.strip().splitlines():
                    try:
                        entries.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue
    return jsonify(entries)


@bp.route("/api/routines/adws")
def list_adws():
    if not ROTINAS_DIR.is_dir():
        return jsonify([])
    scripts = []
    for f in sorted(ROTINAS_DIR.iterdir()):
        if f.suffix == ".py" and f.is_file():
            doc = ""
            text = safe_read(f)
            if text:
                try:
                    tree = ast.parse(text)
                    raw = ast.get_docstring(tree)
                    if raw:
                        doc = raw.splitlines()[0]
                except SyntaxError:
                    pass
            scripts.append({"name": f.stem, "file": f.name, "description": doc})
    return jsonify(scripts)

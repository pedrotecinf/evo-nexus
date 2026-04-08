"""Config endpoint — CLAUDE.md, ROTINAS.md, ROADMAP.md, commands, Makefile."""

import re
from flask import Blueprint, jsonify, Response, abort
from routes._helpers import WORKSPACE, safe_read

bp = Blueprint("config", __name__)


@bp.route("/api/config/claude-md")
def get_claude_md():
    content = safe_read(WORKSPACE / "CLAUDE.md")
    if content is None:
        abort(404, description="CLAUDE.md not found")
    return Response(content, mimetype="text/markdown")


@bp.route("/api/config/rotinas")
def get_rotinas():
    content = safe_read(WORKSPACE / "ROTINAS.md")
    if content is None:
        abort(404, description="ROTINAS.md not found")
    return Response(content, mimetype="text/markdown")


@bp.route("/api/config/roadmap")
def get_roadmap():
    content = safe_read(WORKSPACE / "ROADMAP.md")
    if content is None:
        abort(404, description="ROADMAP.md not found")
    return Response(content, mimetype="text/markdown")


@bp.route("/api/config/commands")
def list_commands():
    cmd_dir = WORKSPACE / ".claude" / "commands"
    if not cmd_dir.is_dir():
        return jsonify([])
    commands = []
    for f in sorted(cmd_dir.iterdir()):
        if f.suffix.lower() == ".md" and f.is_file():
            content = safe_read(f) or ""
            commands.append({
                "name": f.stem,
                "file": f.name,
                "content": content,
            })
    return jsonify(commands)


@bp.route("/api/config/makefile")
def parse_makefile():
    content = safe_read(WORKSPACE / "Makefile")
    if content is None:
        abort(404, description="Makefile not found")

    targets = []
    lines = content.splitlines()
    for i, line in enumerate(lines):
        m = re.match(r"^([a-zA-Z_][a-zA-Z0-9_-]*):", line)
        if m:
            name = m.group(1)
            # Look for comment on same line or line above
            desc = ""
            if "##" in line:
                desc = line.split("##", 1)[1].strip()
            elif i > 0 and lines[i - 1].startswith("#"):
                desc = lines[i - 1].lstrip("# ").strip()
            targets.append({"name": name, "description": desc})

    return jsonify(targets)

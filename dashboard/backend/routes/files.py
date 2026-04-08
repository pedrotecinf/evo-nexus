"""Files endpoint — browse workspace files."""

import mimetypes
from flask import Blueprint, jsonify, abort, Response
from routes._helpers import WORKSPACE, safe_read

bp = Blueprint("files", __name__)

TEXT_EXTENSIONS = {".md", ".html", ".json", ".py", ".yaml", ".yml", ".toml",
                   ".txt", ".sh", ".js", ".ts", ".css", ".env", ".cfg", ".ini"}


@bp.route("/api/files/")
@bp.route("/api/files")
def list_root():
    """List top-level dirs and files."""
    items = []
    for f in sorted(WORKSPACE.iterdir()):
        # Skip hidden dirs except .claude
        if f.name.startswith(".") and f.name != ".claude":
            continue
        items.append({
            "name": f.name,
            "is_dir": f.is_dir(),
            "path": f.name,
        })
    return jsonify(items)


@bp.route("/api/files/<path:filepath>")
def browse(filepath):
    full = WORKSPACE / filepath

    # Security check
    try:
        full.resolve().relative_to(WORKSPACE.resolve())
    except ValueError:
        abort(403, description="Access denied")

    if not full.exists():
        abort(404, description="Not found")

    if full.is_dir():
        items = []
        for f in sorted(full.iterdir()):
            if f.name.startswith(".") and f.name != ".claude":
                continue
            items.append({
                "name": f.name,
                "is_dir": f.is_dir(),
                "path": str(f.relative_to(WORKSPACE)),
            })
        return jsonify(items)

    # It's a file — return content
    suffix = full.suffix.lower()
    if suffix in TEXT_EXTENSIONS:
        content = safe_read(full)
        if content is None:
            abort(500, description="Could not read file")
        mime_map = {
            ".md": "text/markdown",
            ".html": "text/html",
            ".json": "application/json",
            ".py": "text/x-python",
            ".yaml": "text/yaml",
            ".yml": "text/yaml",
        }
        mime = mime_map.get(suffix, "text/plain")
        return Response(content, mimetype=mime)

    # Binary or unknown — return info only
    return jsonify({
        "name": full.name,
        "path": filepath,
        "size": full.stat().st_size,
        "type": mimetypes.guess_type(full.name)[0] or "application/octet-stream",
        "binary": True,
    })

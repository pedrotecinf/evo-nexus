"""Templates endpoint — list and serve HTML/MD templates."""

from flask import Blueprint, jsonify, abort, Response
from routes._helpers import WORKSPACE, safe_read, file_info

bp = Blueprint("templates", __name__)

HTML_TEMPLATES_DIR = WORKSPACE / ".claude" / "templates" / "html"
MD_TEMPLATES_DIR = WORKSPACE / ".claude" / "templates"


@bp.route("/api/templates")
def list_templates():
    templates = []

    # HTML templates
    if HTML_TEMPLATES_DIR.is_dir():
        for f in sorted(HTML_TEMPLATES_DIR.iterdir()):
            if f.is_file() and f.suffix.lower() == ".html":
                info = file_info(f, WORKSPACE)
                info["type"] = "html"
                templates.append(info)

    # MD templates (top-level .md in templates dir, excluding subdirs)
    if MD_TEMPLATES_DIR.is_dir():
        for f in sorted(MD_TEMPLATES_DIR.iterdir()):
            if f.is_file() and f.suffix.lower() == ".md":
                info = file_info(f, WORKSPACE)
                info["type"] = "markdown"
                templates.append(info)

    return jsonify(templates)


@bp.route("/api/templates/<name>")
def get_template(name):
    # Try HTML first, then MD
    for d, ext in [(HTML_TEMPLATES_DIR, ".html"), (MD_TEMPLATES_DIR, ".md")]:
        path = d / name
        if path.is_file():
            mime = "text/html" if ext == ".html" else "text/markdown"
            return Response(safe_read(path) or "", mimetype=mime)
        # Try with extension
        path_ext = d / (name + ext)
        if path_ext.is_file():
            mime = "text/html" if ext == ".html" else "text/markdown"
            return Response(safe_read(path_ext) or "", mimetype=mime)

    abort(404, description="Template not found")

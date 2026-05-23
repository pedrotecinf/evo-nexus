"""Proxy HTTP traffic to the local Hermes Agent UI.

Hermes Agent runs a web UI on port 9119. This proxy makes it accessible
through the dashboard on /hermes-ui/*, protected by @login_required.
Port 9119 is never exposed externally — only reachable via this proxy.

Pattern follows terminal_proxy.py exactly.
"""

from __future__ import annotations

import logging
import os

import requests
from flask import Blueprint, Response, request, stream_with_context
from flask_login import login_required

log = logging.getLogger(__name__)

bp = Blueprint("hermes_proxy", __name__)

HERMES_UI_HOST = os.environ.get("HERMES_UI_HOST", "127.0.0.1")
HERMES_UI_PORT = int(os.environ.get("HERMES_UI_PORT", "9119"))
HERMES_UI_BASE = f"http://{HERMES_UI_HOST}:{HERMES_UI_PORT}"

_HOP_BY_HOP = frozenset(
    {
        "connection",
        "keep-alive",
        "proxy-authenticate",
        "proxy-authorization",
        "te",
        "trailers",
        "transfer-encoding",
        "upgrade",
        "host",
        "content-length",
    }
)

# Headers that block iframe embedding — strip from upstream responses
_IFRAME_BLOCK = frozenset(
    {
        "x-frame-options",
        "content-security-policy",
        "content-security-policy-report-only",
    }
)


def _forward_headers(src: dict[str, str]) -> dict[str, str]:
    return {k: v for k, v in src.items() if k.lower() not in _HOP_BY_HOP}


@bp.route(
    "/hermes-ui/<path:subpath>",
    methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
)
@bp.route("/hermes-ui", methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"])
@bp.route("/hermes-ui/", methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"])
@login_required
def proxy_http(subpath: str = ""):
    target = f"{HERMES_UI_BASE}/{subpath}"
    if request.query_string:
        target = f"{target}?{request.query_string.decode('latin-1')}"

    try:
        upstream = requests.request(
            method=request.method,
            url=target,
            headers=_forward_headers(dict(request.headers)),
            data=request.get_data(),
            allow_redirects=False,
            stream=True,
            timeout=30,
        )
    except requests.exceptions.ConnectionError:
        return (
            "Hermes UI is not running. Ensure Hermes Agent is installed "
            "and the UI is started (hermes ui --port 9119).",
            503,
        )
    except requests.exceptions.Timeout:
        return "Hermes UI timed out.", 504

    content_type = upstream.headers.get("content-type", "")
    is_html = "text/html" in content_type

    if is_html:
        # Buffer HTML to rewrite absolute asset paths.
        # Hermes UI serves assets at /assets/*, /favicon.ico, etc.
        # Behind /hermes-ui/ proxy these must become /hermes-ui/assets/* etc.
        body = upstream.content.decode("utf-8", errors="replace")
        body = body.replace('src="/', 'src="/hermes-ui/')
        body = body.replace("src='/", "src='/hermes-ui/")
        body = body.replace('href="/', 'href="/hermes-ui/')
        body = body.replace("href='/", "href='/hermes-ui/")
        body = body.replace('action="/', 'action="/hermes-ui/')
        body = body.replace("action='/", "action='/hermes-ui/")
        response = Response(body, status=upstream.status_code, content_type=content_type)
    else:
        response = Response(
            stream_with_context(upstream.iter_content(chunk_size=8192)),
            status=upstream.status_code,
        )

    for key, value in upstream.headers.items():
        kl = key.lower()
        if kl not in _HOP_BY_HOP and kl not in _IFRAME_BLOCK:
            if is_html and kl == "content-length":
                continue
            response.headers[key] = value
    return response

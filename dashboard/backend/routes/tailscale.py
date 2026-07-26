"""Tailscale VPN integration — connect/disconnect/status via Auth Key."""

import logging
import os
import re
import subprocess
from flask import Blueprint, jsonify, request, abort
from flask_login import login_required

log = logging.getLogger(__name__)
bp = Blueprint("tailscale", __name__)

_TAILSCALE_BINARY = "/usr/bin/tailscale"
_AUTH_KEY_RE = re.compile(r"^tskey-auth-[a-zA-Z0-9_-]+$")


def _tailscale(*args, timeout=15) -> subprocess.CompletedProcess:
    """Run a tailscale command and return the result."""
    cmd = [_TAILSCALE_BINARY] + list(args)
    return subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=timeout,
        env={**os.environ, "TAILSCALE_SOCKET": "/var/run/tailscale/tailscaled.sock"},
    )


def _get_status() -> dict:
    """Return current Tailscale connection status."""
    try:
        result = _tailscale("status", "--json")
        if result.returncode != 0:
            return {"connected": False, "error": result.stderr.strip() or "not running"}
        import json

        data = json.loads(result.stdout)
        # Find the current node (Self)
        self_node = data.get("Self", {})
        return {
            "connected": True,
            "ip": self_node.get("TailscaleIPs", [None])[0],
            "hostname": self_node.get("HostName", ""),
            "tailnet": data.get("MagicDNSSuffix", ""),
            "online": self_node.get("Online", False),
        }
    except subprocess.TimeoutExpired:
        return {"connected": False, "error": "command timeout"}
    except FileNotFoundError:
        return {"connected": False, "error": "tailscale binary not found"}
    except Exception as exc:
        log.warning("tailscale status error: %s", exc)
        return {"connected": False, "error": str(exc)}


@bp.route("/api/tailscale/status")
def tailscale_status():
    """Return current Tailscale connection status. Public (no login needed)."""
    return jsonify(_get_status())


@bp.route("/api/tailscale/connect", methods=["POST"])
@login_required
def tailscale_connect():
    """Connect to Tailscale using an Auth Key.

    Body: {auth_key: str}
    """
    data = request.get_json(silent=True) or {}
    auth_key = (data.get("auth_key") or "").strip()

    if not auth_key:
        abort(400, description="auth_key is required")

    if not _AUTH_KEY_RE.match(auth_key):
        abort(400, description="auth_key must start with 'tskey-auth-'")

    # Check if already connected
    current = _get_status()
    if current.get("connected"):
        return jsonify({"connected": True, "ip": current.get("ip"), "already": True})

    # Attempt connection.
    # Daemon runs with --tun=userspace-networking (no NET_ADMIN available under
    # Dokploy), so --accept-routes is omitted: in userspace mode the node cannot
    # install kernel routes / act as a subnet router. --accept-dns keeps MagicDNS.
    result = _tailscale(
        "up",
        "--authkey=" + auth_key,
        "--accept-dns",
        "--hostname=hermes",
        "--reset",
    )

    if result.returncode != 0:
        log.error("tailscale up failed: %s", result.stderr)
        abort(502, description=f"Tailscale connection failed: {result.stderr.strip()}")

    # Verify connection
    new_status = _get_status()
    if not new_status.get("connected"):
        abort(502, description="Connection command succeeded but Tailscale is not connected")

    return jsonify(
        {
            "connected": True,
            "ip": new_status.get("ip"),
            "hostname": new_status.get("hostname"),
        }
    )


@bp.route("/api/tailscale/disconnect", methods=["POST"])
@login_required
def tailscale_disconnect():
    """Disconnect from Tailscale."""
    current = _get_status()
    if not current.get("connected"):
        return jsonify({"connected": False})

    result = _tailscale("down", "--accept-routes")
    if result.returncode != 0:
        log.error("tailscale down failed: %s", result.stderr)
        abort(502, description=f"Tailscale disconnect failed: {result.stderr.strip()}")

    return jsonify({"connected": False})


@bp.route("/api/tailscale/whoami")
@login_required
def tailscale_whoami():
    """Return Tailscale identity information."""
    try:
        result = _tailscale("whoami", "--json")
        if result.returncode != 0:
            abort(502, description=result.stderr.strip())
        import json

        return jsonify(json.loads(result.stdout))
    except subprocess.TimeoutExpired:
        abort(504, description="command timeout")
    except FileNotFoundError:
        abort(503, description="tailscale binary not found")

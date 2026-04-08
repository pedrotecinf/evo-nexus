"""TikTok OAuth flow — multi-account, requires HTTPS callback."""

from flask import Blueprint, request, redirect, session
import json
import urllib.request
import urllib.error
import urllib.parse
import secrets
from datetime import datetime, timezone

bp = Blueprint("tiktok", __name__)


@bp.route("/connect/tiktok")
def connect():
    from env_manager import read_env
    env = read_env()
    client_key = env.get("TIKTOK_CLIENT_KEY", "")
    if not client_key:
        return _missing("TIKTOK_CLIENT_KEY e TIKTOK_CLIENT_SECRET")

    callback_url = env.get("TIKTOK_CALLBACK_URL", "http://localhost:8765/callback/tiktok")
    state = secrets.token_urlsafe(32)
    session["oauth_state_tiktok"] = state

    params = urllib.parse.urlencode({
        "client_key": client_key,
        "response_type": "code",
        "scope": "user.info.basic,user.info.stats,video.list",
        "redirect_uri": callback_url,
        "state": state,
    })
    return redirect(f"https://www.tiktok.com/v2/auth/authorize/?{params}")


@bp.route("/callback/tiktok")
def callback():
    from env_manager import read_env, save_account, next_index
    env = read_env()

    state = request.args.get("state", "")
    if state != session.get("oauth_state_tiktok"):
        return "Invalid state — CSRF protection", 403

    code = request.args.get("code", "")
    if not code:
        return f"Error: {request.args.get('error', 'no code')}", 400

    callback_url = env.get("TIKTOK_CALLBACK_URL", "http://localhost:8765/callback/tiktok")
    payload = json.dumps({
        "client_key": env.get("TIKTOK_CLIENT_KEY", ""),
        "client_secret": env.get("TIKTOK_CLIENT_SECRET", ""),
        "code": code,
        "grant_type": "authorization_code",
        "redirect_uri": callback_url,
    }).encode()

    req = urllib.request.Request("https://open.tiktokapis.com/v2/oauth/token/",
                                 data=payload, method="POST",
                                 headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req) as resp:
            token_data = json.loads(resp.read())
    except urllib.error.HTTPError as e:
        return f"Token exchange failed: {e.read().decode()}", 500

    idx = next_index("tiktok")
    fields = {
        "ACCESS_TOKEN": token_data.get("access_token", ""),
        "TOKEN_CREATED_AT": datetime.now(timezone.utc).isoformat(),
    }
    if token_data.get("refresh_token"):
        fields["REFRESH_TOKEN"] = token_data["refresh_token"]
    if token_data.get("open_id"):
        fields["OPEN_ID"] = token_data["open_id"]

    save_account("tiktok", idx, "TikTok", fields)
    return redirect("/?saved=TikTok")


def _missing(keys):
    return f"""
    <html><body style="background:#0C111D;color:#F9FAFB;font-family:Inter,sans-serif;display:flex;justify-content:center;align-items:center;height:100vh;">
    <div style="background:#182230;border:1px solid #344054;border-radius:12px;padding:40px;max-width:500px;">
        <h2 style="color:#F04438;">Configuração necessária</h2>
        <p style="color:#D0D5DD;">Configure <code>{keys}</code> no <code>.env</code></p>
        <p style="color:#F79009;font-size:13px;margin-top:12px;">TikTok exige HTTPS callback. Configure <code>TIKTOK_CALLBACK_URL</code> com URL do ngrok.</p>
        <a href="/" style="color:#00FFA7;">Voltar</a>
    </div></body></html>
    """

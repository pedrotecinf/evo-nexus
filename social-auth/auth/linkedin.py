"""LinkedIn OAuth flow — multi-account."""

from flask import Blueprint, request, redirect, session
import json
import urllib.request
import urllib.error
import urllib.parse
import secrets
from datetime import datetime, timezone

bp = Blueprint("linkedin", __name__)


def _callback_url():
    from env_manager import read_env
    env = read_env()
    ngrok = env.get("NGROK_URL", "")
    if ngrok:
        return f"{ngrok.rstrip('/')}/callback/linkedin"
    return "http://localhost:8765/callback/linkedin"


@bp.route("/connect/linkedin")
def connect():
    from env_manager import read_env
    env = read_env()
    client_id = env.get("LINKEDIN_CLIENT_ID", "")
    if not client_id:
        return _missing("LINKEDIN_CLIENT_ID e LINKEDIN_CLIENT_SECRET")

    state = secrets.token_urlsafe(32)
    session["oauth_state_linkedin"] = state

    params = urllib.parse.urlencode({
        "response_type": "code",
        "client_id": client_id,
        "redirect_uri": _callback_url(),
        "state": state,
        "scope": "openid profile email w_member_social",
    })
    return redirect(f"https://www.linkedin.com/oauth/v2/authorization?{params}")


@bp.route("/callback/linkedin")
def callback():
    from env_manager import read_env, save_account, next_index

    env = read_env()
    state = request.args.get("state", "")
    if state != session.get("oauth_state_linkedin"):
        return "Invalid state — CSRF protection", 403

    code = request.args.get("code", "")
    if not code:
        return f"Error: {request.args.get('error_description', 'no code')}", 400

    data = urllib.parse.urlencode({
        "grant_type": "authorization_code",
        "code": code,
        "client_id": env.get("LINKEDIN_CLIENT_ID", ""),
        "client_secret": env.get("LINKEDIN_CLIENT_SECRET", ""),
        "redirect_uri": _callback_url(),
    }).encode()

    req = urllib.request.Request("https://www.linkedin.com/oauth/v2/accessToken", data=data, method="POST",
                                 headers={"Content-Type": "application/x-www-form-urlencoded"})
    try:
        with urllib.request.urlopen(req) as resp:
            token_data = json.loads(resp.read())
    except urllib.error.HTTPError as e:
        return f"Token exchange failed: {e.read().decode()}", 500

    access_token = token_data.get("access_token", "")
    now = datetime.now(timezone.utc).isoformat()

    # Get profile info
    person_urn = ""
    name = "LinkedIn"
    try:
        req = urllib.request.Request("https://api.linkedin.com/v2/userinfo",
                                     headers={"Authorization": f"Bearer {access_token}"})
        with urllib.request.urlopen(req) as resp:
            profile = json.loads(resp.read())
        person_urn = f"urn:li:person:{profile.get('sub', '')}"
        name = profile.get("name", "LinkedIn")
    except Exception:
        pass

    idx = next_index("linkedin")
    save_account("linkedin", idx, name, {
        "ACCESS_TOKEN": access_token,
        "PERSON_URN": person_urn,
        "TOKEN_CREATED_AT": now,
    })

    return redirect(f"/?saved=LinkedIn ({name})")


def _missing(keys):
    return f"""
    <html><body style="background:#0C111D;color:#F9FAFB;font-family:Inter,sans-serif;display:flex;justify-content:center;align-items:center;height:100vh;">
    <div style="background:#182230;border:1px solid #344054;border-radius:12px;padding:40px;max-width:500px;">
        <h2 style="color:#F04438;">Configuração necessária</h2>
        <p style="color:#D0D5DD;">Configure <code>{keys}</code> no <code>.env</code></p>
        <a href="/" style="color:#00FFA7;">Voltar</a>
    </div></body></html>
    """

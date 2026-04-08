"""Twitch auth — Client Credentials + User Token, multi-account."""

from flask import Blueprint, request, redirect, session
import json
import urllib.request
import urllib.error
import urllib.parse
import secrets

bp = Blueprint("twitch", __name__)


@bp.route("/connect/twitch")
def connect():
    from env_manager import read_env
    env = read_env()
    client_id = env.get("TWITCH_CLIENT_ID", "")

    if not client_id:
        return """
        <html><body style="background:#0C111D;color:#F9FAFB;font-family:Inter,sans-serif;display:flex;justify-content:center;align-items:center;height:100vh;">
        <div style="background:#182230;border:1px solid #344054;border-radius:12px;padding:40px;max-width:500px;width:100%;">
            <h2 style="color:#00FFA7;">Twitch — Adicionar Conta</h2>
            <form action="/save/twitch" method="POST">
                <input name="label" type="text" placeholder="Nome da conta (ex: Evolution)" style="width:100%;padding:12px;background:#0C111D;border:1px solid #344054;border-radius:8px;color:#F9FAFB;font-size:14px;margin-bottom:12px;">
                <input name="client_id" type="text" placeholder="Client ID" style="width:100%;padding:12px;background:#0C111D;border:1px solid #344054;border-radius:8px;color:#F9FAFB;font-size:14px;margin-bottom:12px;">
                <input name="client_secret" type="password" placeholder="Client Secret" style="width:100%;padding:12px;background:#0C111D;border:1px solid #344054;border-radius:8px;color:#F9FAFB;font-size:14px;margin-bottom:12px;">
                <input name="broadcaster_id" type="text" placeholder="Broadcaster ID (opcional)" style="width:100%;padding:12px;background:#0C111D;border:1px solid #344054;border-radius:8px;color:#F9FAFB;font-size:14px;margin-bottom:20px;">
                <button type="submit" style="width:100%;padding:12px;background:#00FFA7;color:#0C111D;border:none;border-radius:8px;font-weight:700;cursor:pointer;">Salvar e gerar Token</button>
            </form>
            <a href="/" style="color:#667085;font-size:12px;display:block;text-align:center;margin-top:16px;">Voltar</a>
        </div></body></html>
        """

    # OAuth for User Token (followers)
    state = secrets.token_urlsafe(32)
    session["oauth_state_twitch"] = state

    params = urllib.parse.urlencode({
        "client_id": client_id,
        "redirect_uri": "http://localhost:8765/callback/twitch",
        "response_type": "code",
        "scope": "moderator:read:followers analytics:read:extensions",
        "state": state,
    })
    return redirect(f"https://id.twitch.tv/oauth2/authorize?{params}")


@bp.route("/save/twitch", methods=["POST"])
def save():
    from env_manager import save_account, next_index, set_env

    label = request.form.get("label", "").strip() or "Twitch"
    client_id = request.form.get("client_id", "").strip()
    client_secret = request.form.get("client_secret", "").strip()
    broadcaster_id = request.form.get("broadcaster_id", "").strip()

    # Save global client creds (shared across accounts)
    if client_id:
        set_env("TWITCH_CLIENT_ID", client_id)
    if client_secret:
        set_env("TWITCH_CLIENT_SECRET", client_secret)

    # Auto-generate App Access Token
    access_token = ""
    if client_id and client_secret:
        data = urllib.parse.urlencode({
            "client_id": client_id,
            "client_secret": client_secret,
            "grant_type": "client_credentials",
        }).encode()
        req = urllib.request.Request("https://id.twitch.tv/oauth2/token", data=data, method="POST")
        try:
            with urllib.request.urlopen(req) as resp:
                token_data = json.loads(resp.read())
            access_token = token_data.get("access_token", "")
        except Exception:
            pass

    idx = next_index("twitch")
    fields = {}
    if client_id:
        fields["CLIENT_ID"] = client_id
    if client_secret:
        fields["CLIENT_SECRET"] = client_secret
    if access_token:
        fields["ACCESS_TOKEN"] = access_token
    if broadcaster_id:
        fields["BROADCASTER_ID"] = broadcaster_id

    save_account("twitch", idx, label, fields)
    return redirect("/?saved=Twitch")


@bp.route("/callback/twitch")
def callback():
    from env_manager import read_env, save_account, next_index
    env = read_env()

    state = request.args.get("state", "")
    if state != session.get("oauth_state_twitch"):
        return "Invalid state — CSRF protection", 403

    code = request.args.get("code", "")
    if not code:
        return f"Error: {request.args.get('error', 'no code')}", 400

    data = urllib.parse.urlencode({
        "client_id": env.get("TWITCH_CLIENT_ID", ""),
        "client_secret": env.get("TWITCH_CLIENT_SECRET", ""),
        "code": code,
        "grant_type": "authorization_code",
        "redirect_uri": "http://localhost:8765/callback/twitch",
    }).encode()

    req = urllib.request.Request("https://id.twitch.tv/oauth2/token", data=data, method="POST")
    try:
        with urllib.request.urlopen(req) as resp:
            token_data = json.loads(resp.read())
    except urllib.error.HTTPError as e:
        return f"Token exchange failed: {e.read().decode()}", 500

    idx = next_index("twitch")
    fields = {
        "ACCESS_TOKEN": token_data.get("access_token", ""),
    }
    if token_data.get("refresh_token"):
        fields["REFRESH_TOKEN"] = token_data["refresh_token"]

    save_account("twitch", idx, "Twitch (User)", fields)
    return redirect("/?saved=Twitch")

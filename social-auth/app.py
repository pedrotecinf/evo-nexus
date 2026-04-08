#!/usr/bin/env python3
"""Evolution Social Auth App — Multi-account OAuth for all social platforms."""

import os
import sys
import secrets
import webbrowser
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from flask import Flask, render_template, request, redirect

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)

# Register blueprints
from auth.youtube import bp as youtube_bp
from auth.instagram import bp as instagram_bp
from auth.linkedin import bp as linkedin_bp
from auth.twitter import bp as twitter_bp
from auth.tiktok import bp as tiktok_bp
from auth.twitch import bp as twitch_bp

app.register_blueprint(youtube_bp)
app.register_blueprint(instagram_bp)
app.register_blueprint(linkedin_bp)
app.register_blueprint(twitter_bp)
app.register_blueprint(tiktok_bp)
app.register_blueprint(twitch_bp)


@app.route("/")
def index():
    from env_manager import all_platforms_with_accounts
    platforms = all_platforms_with_accounts()
    saved = request.args.get("saved")
    return render_template("index.html", platforms=platforms, saved=saved)


@app.route("/disconnect/<platform>/<int:index>", methods=["POST"])
def disconnect(platform, index):
    from env_manager import delete_account
    delete_account(platform, index)
    return redirect("/")


if __name__ == "__main__":
    port = int(os.environ.get("SOCIAL_AUTH_PORT", 8765))
    print(f"\n  🔑 Evolution Social Auth")
    print(f"  📍 http://localhost:{port}")
    print(f"  ⛔ Ctrl+C para parar\n")
    webbrowser.open(f"http://localhost:{port}")
    app.run(host="127.0.0.1", port=port, debug=False)

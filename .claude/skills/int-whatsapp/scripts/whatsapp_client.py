#!/usr/bin/env python3
"""WhatsApp Messages API Client — Evolution Foundation."""

import json
import os
import sys
import urllib.request
import urllib.error
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict


def _load_dotenv():
    """Load .env file from project root."""
    env_path = Path(__file__).resolve().parents[4] / ".env"
    if not env_path.exists():
        return
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            key, value = key.strip(), value.strip()
            if key and key not in os.environ:
                os.environ[key] = value


_load_dotenv()

API_KEY = os.environ.get("WHATSAPP_API_KEY", "")
BASE_URL = "https://evolutionfoundation.com.br/api/whatsapp-messages"


def _api_get(params: dict) -> dict:
    """Make a GET request to the WhatsApp Messages API."""
    query = "&".join(f"{k}={v}" for k, v in params.items() if v is not None)
    url = f"{BASE_URL}?{query}" if query else BASE_URL

    req = urllib.request.Request(
        url,
        headers={"x-api-key": API_KEY},
        method="GET"
    )

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        return {"error": f"HTTP {e.code}", "detail": body}
    except Exception as e:
        return {"error": str(e)}


def _fetch_all_pages(params: dict, max_pages: int = 50) -> list:
    """Fetch all pages of results."""
    all_items = []
    params["page"] = 1
    params["limit"] = 100

    for _ in range(max_pages):
        data = _api_get(params)
        if "error" in data:
            return [data]

        items = data.get("items", [])
        all_items.extend(items)

        pagination = data.get("pagination", {})
        if not pagination.get("hasNext", False):
            break
        params["page"] = pagination.get("page", 1) + 1

    return all_items


# ── Commands ─────────────────────────────────────────────


def messages(start_date=None, end_date=None, group_id=None,
             participant=None, message_type=None, page=1, limit=25):
    """Fetch messages with optional filters."""
    params = {
        "startDate": start_date,
        "endDate": end_date,
        "groupId": group_id,
        "participant": participant,
        "messageType": message_type,
        "page": page,
        "limit": limit,
    }
    params = {k: v for k, v in params.items() if v is not None}
    return _api_get(params)


def messages_24h(group_id=None):
    """Fetch messages from the last 24 hours."""
    end = datetime.now(tz=__import__('datetime').timezone.utc).strftime("%Y-%m-%d")
    start = (datetime.now(tz=__import__('datetime').timezone.utc) - timedelta(days=1)).strftime("%Y-%m-%d")
    items = _fetch_all_pages({
        "startDate": start,
        "endDate": end,
        **({"groupId": group_id} if group_id else {}),
    })
    return {"items": items, "total": len(items), "period": f"{start} to {end}"}


def messages_7d(group_id=None):
    """Fetch messages from the last 7 days."""
    end = datetime.now(tz=__import__('datetime').timezone.utc).strftime("%Y-%m-%d")
    start = (datetime.now(tz=__import__('datetime').timezone.utc) - timedelta(days=7)).strftime("%Y-%m-%d")
    items = _fetch_all_pages({
        "startDate": start,
        "endDate": end,
        **({"groupId": group_id} if group_id else {}),
    })
    return {"items": items, "total": len(items), "period": f"{start} to {end}"}


def messages_30d(group_id=None):
    """Fetch messages from the last 30 days."""
    end = datetime.now(tz=__import__('datetime').timezone.utc).strftime("%Y-%m-%d")
    start = (datetime.now(tz=__import__('datetime').timezone.utc) - timedelta(days=30)).strftime("%Y-%m-%d")
    items = _fetch_all_pages({
        "startDate": start,
        "endDate": end,
        **({"groupId": group_id} if group_id else {}),
    })
    return {"items": items, "total": len(items), "period": f"{start} to {end}"}


def groups(start_date=None, end_date=None):
    """List unique groups with message counts."""
    if not start_date:
        start_date = (datetime.now(tz=__import__('datetime').timezone.utc) - timedelta(days=7)).strftime("%Y-%m-%d")
    if not end_date:
        end_date = datetime.now(tz=__import__('datetime').timezone.utc).strftime("%Y-%m-%d")

    items = _fetch_all_pages({"startDate": start_date, "endDate": end_date})

    if isinstance(items, list) and len(items) > 0 and "error" in items[0]:
        return items[0]

    group_map = defaultdict(lambda: {"count": 0, "participants": set(), "instance": ""})
    for msg in items:
        gid = msg.get("remoteJid", "unknown")
        group_map[gid]["count"] += 1
        group_map[gid]["instance"] = msg.get("instance", "")
        p = msg.get("pushName", "")
        if p:
            group_map[gid]["participants"].add(p)

    result = []
    for gid, info in sorted(group_map.items(), key=lambda x: x[1]["count"], reverse=True):
        result.append({
            "groupId": gid,
            "instance": info["instance"],
            "messages": info["count"],
            "unique_participants": len(info["participants"]),
            "participants": sorted(info["participants"]),
        })

    return {"groups": result, "total_groups": len(result), "period": f"{start_date} to {end_date}"}


def stats(start_date=None, end_date=None):
    """Message counts by group and by day."""
    if not start_date:
        start_date = (datetime.now(tz=__import__('datetime').timezone.utc) - timedelta(days=7)).strftime("%Y-%m-%d")
    if not end_date:
        end_date = datetime.now(tz=__import__('datetime').timezone.utc).strftime("%Y-%m-%d")

    items = _fetch_all_pages({"startDate": start_date, "endDate": end_date})

    if isinstance(items, list) and len(items) > 0 and "error" in items[0]:
        return items[0]

    by_day = defaultdict(int)
    by_group = defaultdict(int)
    by_type = defaultdict(int)
    by_participant = defaultdict(int)

    for msg in items:
        created = msg.get("createdAt", "")[:10]
        if created:
            by_day[created] += 1
        by_group[msg.get("remoteJid", "unknown")] += 1
        by_type[msg.get("messageType", "unknown")] += 1
        name = msg.get("pushName", "unknown")
        if name:
            by_participant[name] += 1

    return {
        "period": f"{start_date} to {end_date}",
        "total_messages": len(items),
        "by_day": dict(sorted(by_day.items())),
        "by_group": dict(sorted(by_group.items(), key=lambda x: x[1], reverse=True)),
        "by_type": dict(sorted(by_type.items(), key=lambda x: x[1], reverse=True)),
        "top_participants": dict(sorted(by_participant.items(), key=lambda x: x[1], reverse=True)[:20]),
    }


# ── CLI ──────────────────────────────────────────────────

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: whatsapp_client.py <command> [args]")
        print("\nCommands:")
        print("  messages [--start YYYY-MM-DD] [--end YYYY-MM-DD] [--group ID] [--type TYPE] [--page N] [--limit N]")
        print("  messages_24h [--group ID]")
        print("  messages_7d [--group ID]")
        print("  messages_30d [--group ID]")
        print("  groups [--start YYYY-MM-DD] [--end YYYY-MM-DD]")
        print("  stats [--start YYYY-MM-DD] [--end YYYY-MM-DD]")
        sys.exit(1)

    command = sys.argv[1]
    args = sys.argv[2:]

    def _parse_arg(args, flag, default=None):
        if flag in args:
            idx = args.index(flag)
            if idx + 1 < len(args):
                return args[idx + 1]
        return default

    try:
        if command == "messages":
            result = messages(
                start_date=_parse_arg(args, "--start"),
                end_date=_parse_arg(args, "--end"),
                group_id=_parse_arg(args, "--group"),
                message_type=_parse_arg(args, "--type"),
                participant=_parse_arg(args, "--participant"),
                page=int(_parse_arg(args, "--page", 1)),
                limit=int(_parse_arg(args, "--limit", 25)),
            )
        elif command == "messages_24h":
            result = messages_24h(group_id=_parse_arg(args, "--group"))
        elif command == "messages_7d":
            result = messages_7d(group_id=_parse_arg(args, "--group"))
        elif command == "messages_30d":
            result = messages_30d(group_id=_parse_arg(args, "--group"))
        elif command == "groups":
            result = groups(
                start_date=_parse_arg(args, "--start"),
                end_date=_parse_arg(args, "--end"),
            )
        elif command == "stats":
            result = stats(
                start_date=_parse_arg(args, "--start"),
                end_date=_parse_arg(args, "--end"),
            )
        else:
            print(f"Unknown command: {command}")
            sys.exit(1)

        print(json.dumps(result, indent=2, ensure_ascii=False))
    except Exception as e:
        print(json.dumps({"error": str(e)}, indent=2))
        sys.exit(1)

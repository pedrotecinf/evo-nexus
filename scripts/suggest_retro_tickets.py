#!/usr/bin/env python3
"""suggest_retro_tickets.py — Suggest tickets from existing chat sessions.

Reads session store files and groups by agent + inferred topic (first user message),
then outputs a CSV with suggestions for Davidson to review.

Does NOT auto-create tickets — Davidson imports manually after reviewing the CSV.

Usage:
    python scripts/suggest_retro_tickets.py

Output:
    workspace/development/features/tickets/[C]retro-tickets-suggestions.csv
"""

import csv
import json
import os
import re
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parent.parent
SESSIONS_DIR = WORKSPACE / "ADWs" / "logs" / "chat"
OUTPUT_PATH = WORKSPACE / "workspace" / "development" / "features" / "tickets" / "[C]retro-tickets-suggestions.csv"

# Group sessions within this window (hours) as the same topic
WINDOW_HOURS = 48

# Minimum sessions to form a group worth suggesting
MIN_SESSIONS_PER_GROUP = 1


def _load_sessions(sessions_dir: Path) -> list[dict]:
    """Load all session records from JSONL files in sessions_dir."""
    sessions = []
    if not sessions_dir.exists():
        print(f"[suggest_retro_tickets] sessions dir not found: {sessions_dir}", file=sys.stderr)
        return sessions

    for f in sorted(sessions_dir.glob("*.jsonl")):
        try:
            for line in f.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if not line:
                    continue
                try:
                    rec = json.loads(line)
                    sessions.append(rec)
                except json.JSONDecodeError:
                    pass
        except Exception as exc:
            print(f"[suggest_retro_tickets] WARNING: could not read {f}: {exc}", file=sys.stderr)

    return sessions


def _extract_first_user_message(session: dict) -> str:
    """Try to extract the first user message from a session record."""
    for key in ("messages", "turns", "history"):
        msgs = session.get(key)
        if msgs and isinstance(msgs, list):
            for msg in msgs:
                role = msg.get("role", "") or msg.get("type", "")
                if role in ("user", "human"):
                    content = msg.get("content") or msg.get("text") or ""
                    if isinstance(content, list):
                        # Anthropic message format
                        for block in content:
                            if isinstance(block, dict) and block.get("type") == "text":
                                return str(block.get("text", ""))[:120]
                    return str(content)[:120]
    # Fallback: try top-level "message"
    return str(session.get("message") or session.get("prompt") or "")[:120]


def _normalize_title(raw: str) -> str:
    """Truncate and clean a raw first message to a title."""
    title = raw.strip()
    # Remove special chars
    title = re.sub(r"[\n\r\t]+", " ", title)
    # Truncate
    if len(title) > 80:
        title = title[:77] + "..."
    return title or "(no title)"


def main():
    print(f"[suggest_retro_tickets] scanning {SESSIONS_DIR} ...")
    sessions = _load_sessions(SESSIONS_DIR)
    print(f"[suggest_retro_tickets] loaded {len(sessions)} session records")

    # Group by (agent, date_bucket)
    # Key: (agent, date_bucket_str)
    # date_bucket: ISO date string with WINDOW_HOURS granularity
    groups: dict[tuple, list[dict]] = defaultdict(list)

    for s in sessions:
        agent = (
            s.get("agent") or s.get("agent_slug") or s.get("agent_name") or "unknown"
        )
        # Try to parse timestamp
        ts_raw = s.get("created_at") or s.get("timestamp") or s.get("started_at") or ""
        try:
            dt = datetime.fromisoformat(str(ts_raw).replace("Z", "+00:00"))
            # Bucket by WINDOW_HOURS
            bucket_hour = (dt.hour // WINDOW_HOURS) * WINDOW_HOURS
            bucket = dt.strftime(f"%Y-%m-%d") + f"-{bucket_hour:02d}h"
        except Exception:
            bucket = "unknown-date"

        groups[(agent, bucket)].append(s)

    # Build suggestions
    rows = []
    for (agent, bucket), group_sessions in sorted(groups.items()):
        if len(group_sessions) < MIN_SESSIONS_PER_GROUP:
            continue

        first_session = group_sessions[0]
        first_msg = _extract_first_user_message(first_session)
        suggested_title = _normalize_title(first_msg)

        # Date range
        dates = []
        for s in group_sessions:
            ts_raw = s.get("created_at") or s.get("timestamp") or s.get("started_at") or ""
            try:
                dates.append(datetime.fromisoformat(str(ts_raw).replace("Z", "+00:00")))
            except Exception:
                pass

        first_date = min(dates).strftime("%Y-%m-%d") if dates else "unknown"
        last_date = max(dates).strftime("%Y-%m-%d") if dates else "unknown"

        sample_ids = [
            str(s.get("id") or s.get("session_id") or "")
            for s in group_sessions[:3]
        ]

        rows.append({
            "suggested_title": suggested_title,
            "agent": agent,
            "session_count": len(group_sessions),
            "first_date": first_date,
            "last_date": last_date,
            "sample_session_ids": "|".join(filter(None, sample_ids)),
            "first_message_snippet": first_msg[:120],
        })

    # Sort by agent, then date
    rows.sort(key=lambda r: (r["agent"], r["first_date"]))

    # Write CSV
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "suggested_title", "agent", "session_count",
            "first_date", "last_date", "sample_session_ids", "first_message_snippet",
        ])
        writer.writeheader()
        writer.writerows(rows)

    print(f"[suggest_retro_tickets] wrote {len(rows)} suggestions to {OUTPUT_PATH}")
    print("[suggest_retro_tickets] Review the CSV and import tickets manually — no auto-creation.")


if __name__ == "__main__":
    main()

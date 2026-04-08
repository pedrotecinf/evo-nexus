"""Costs endpoint — aggregated and daily cost breakdowns."""

import json
from datetime import date, timedelta
from flask import Blueprint, jsonify, request
from routes._helpers import WORKSPACE, safe_read

bp = Blueprint("costs", __name__)

METRICS_PATH = WORKSPACE / "ADWs" / "logs" / "metrics.json"
LOGS_DIR = WORKSPACE / "ADWs" / "logs"


@bp.route("/api/costs")
def costs_summary():
    content = safe_read(METRICS_PATH)
    if not content:
        return jsonify({"total_cost": 0, "by_routine": [], "by_agent": [], "today": 0, "week": 0, "month_estimate": 0})

    try:
        data = json.loads(content)
    except json.JSONDecodeError:
        return jsonify({"total_cost": 0, "by_routine": [], "by_agent": [], "today": 0, "week": 0, "month_estimate": 0})

    total = 0.0
    by_routine = []
    agent_costs = {}

    if isinstance(data, dict):
        for name, val in data.items():
            if isinstance(val, dict):
                cost = float(val.get("total_cost_usd", 0) or 0)
                tokens = int(val.get("total_input_tokens", 0) or 0) + int(val.get("total_output_tokens", 0) or 0)
                runs = int(val.get("runs", 0) or 0)
                avg_cost = float(val.get("avg_cost_usd", 0) or 0)
                agent = val.get("agent", "unknown")

                total += cost
                by_routine.append({
                    "name": name,
                    "cost": round(cost, 5),
                    "total_cost": round(cost, 5),
                    "avg_cost": round(avg_cost, 5),
                    "tokens": tokens,
                    "runs": runs,
                    "agent": agent,
                })
                agent_costs[agent] = agent_costs.get(agent, 0.0) + cost

    by_agent = [{"agent": a, "cost": round(c, 4)} for a, c in sorted(agent_costs.items(), key=lambda x: x[1], reverse=True)]

    # Calculate today and week from JSONL logs
    today_cost = 0.0
    week_cost = 0.0
    daily_costs = {}
    today_str = date.today().isoformat()
    week_start = (date.today() - timedelta(days=7)).isoformat()

    if LOGS_DIR.is_dir():
        for f in LOGS_DIR.iterdir():
            if f.suffix != ".jsonl":
                continue
            text = safe_read(f)
            if not text:
                continue
            for line in text.strip().splitlines():
                try:
                    entry = json.loads(line)
                except json.JSONDecodeError:
                    continue
                ts = entry.get("timestamp", "")[:10]
                cost_val = float(entry.get("cost_usd", 0) or 0)
                if ts:
                    daily_costs[ts] = daily_costs.get(ts, 0.0) + cost_val
                if ts == today_str:
                    today_cost += cost_val
                if ts >= week_start:
                    week_cost += cost_val

    daily = [{"date": k, "cost": round(v, 4)} for k, v in sorted(daily_costs.items())]

    return jsonify({
        "total_cost": round(total, 4),
        "today": round(today_cost, 4),
        "week": round(week_cost, 4),
        "month_estimate": round(total, 4),
        "daily": daily,
        "by_routine": by_routine,
        "by_agent": by_agent,
    })


@bp.route("/api/costs/daily")
def costs_daily():
    from_date = request.args.get("from", (date.today() - timedelta(days=7)).isoformat())
    to_date = request.args.get("to", date.today().isoformat())

    daily = {}
    if LOGS_DIR.is_dir():
        for f in sorted(LOGS_DIR.iterdir()):
            if f.suffix != ".jsonl":
                continue
            text = safe_read(f)
            if not text:
                continue
            for line in text.strip().splitlines():
                try:
                    entry = json.loads(line)
                except json.JSONDecodeError:
                    continue
                ts = entry.get("timestamp", "")
                if not ts:
                    continue
                day = ts[:10]
                if from_date <= day <= to_date:
                    cost = float(entry.get("cost_usd", entry.get("cost", 0)) or 0)
                    daily[day] = daily.get(day, 0.0) + cost

    sorted_daily = [{"date": k, "cost": round(v, 4)} for k, v in sorted(daily.items())]
    return jsonify(sorted_daily)

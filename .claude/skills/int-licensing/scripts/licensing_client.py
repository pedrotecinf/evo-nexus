#!/usr/bin/env python3
"""Evolution Licensing API Client."""

import json
import os
import sys
import urllib.request
import urllib.error
from pathlib import Path


def _load_dotenv():
    """Load .env from project root."""
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

TOKEN = os.environ.get("LICENSING_ADMIN_TOKEN", "")
BASE_URL = "https://license.evolutionfoundation.com.br/admin/v1"


def _api_get(path: str, params: dict = None) -> dict:
    """Make a GET request to the Licensing API."""
    query = ""
    if params:
        query = "&".join(f"{k}={v}" for k, v in params.items() if v is not None)
    url = f"{BASE_URL}/{path}"
    if query:
        url += f"?{query}"

    req = urllib.request.Request(
        url,
        headers={"Authorization": f"Bearer {TOKEN}"},
        method="GET"
    )

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        return {"error": f"HTTP {e.code}", "detail": body[:500]}
    except Exception as e:
        return {"error": str(e)}


def _fetch_all(path: str, params: dict = None, max_pages: int = 50) -> list:
    """Fetch all pages of a paginated endpoint."""
    params = params or {}
    params["page"] = 1
    params["limit"] = 100
    all_items = []

    for _ in range(max_pages):
        data = _api_get(path, params)
        if isinstance(data, dict) and "error" in data:
            return [data]
        if isinstance(data, list):
            all_items.extend(data)
            if len(data) < params["limit"]:
                break
            params["page"] += 1
        else:
            # Single object response
            return [data]

    return all_items


# ── Keys ─────────────────────────────────────────────

def keys(status=None, tier=None, page=1, limit=25):
    params = {"page": page, "limit": limit}
    if status:
        params["status"] = status
    if tier:
        params["tier"] = tier
    return _api_get("keys", params)


def keys_all(status=None, tier=None):
    params = {}
    if status:
        params["status"] = status
    if tier:
        params["tier"] = tier
    return _fetch_all("keys", params)


# ── Instances ────────────────────────────────────────

def instances(status=None, tier=None, geo=None, heartbeat_age=None, page=1, limit=25):
    params = {"page": page, "limit": limit}
    if status:
        params["status"] = status
    if tier:
        params["tier"] = tier
    if geo:
        params["geo"] = geo
    if heartbeat_age:
        params["heartbeat_age"] = heartbeat_age
    return _api_get("instances", params)


def instances_all(status=None, tier=None, geo=None):
    params = {}
    if status:
        params["status"] = status
    if tier:
        params["tier"] = tier
    if geo:
        params["geo"] = geo
    return _fetch_all("instances", params)


def instance_detail(instance_id: str):
    return _api_get(f"instances/{instance_id}")


# ── Activation Log ───────────────────────────────────

def activation_log(api_key=None, page=1, limit=50):
    params = {"page": page, "limit": limit}
    if api_key:
        params["api_key"] = api_key
    return _api_get("activation-log", params)


# ── Telemetry ────────────────────────────────────────

def telemetry(period="24h"):
    return _api_get("telemetry/summary", {"period": period})


# ── Commercial Alerts ────────────────────────────────

def alerts(resolved=False, page=1, limit=25):
    return _api_get("commercial-alerts", {
        "resolved": str(resolved).lower(),
        "page": page,
        "limit": limit,
    })


# ── Customers ────────────────────────────────────────

def customers(search=None, country=None, tier=None, page=1, limit=25):
    params = {"page": page, "limit": limit}
    if search:
        params["search"] = search
    if country:
        params["country"] = country
    if tier:
        params["tier"] = tier
    return _api_get("customers", params)


def customer_detail(customer_id: int):
    return _api_get(f"customers/{customer_id}")


# ── Products ─────────────────────────────────────────

def products():
    return _api_get("products")


# ── CLI ──────────────────────────────────────────────

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: licensing_client.py <command> [args]")
        print("\nCommands:")
        print("  keys [--status STATUS] [--tier TIER] [--page N] [--limit N]")
        print("  keys_all [--status STATUS] [--tier TIER]")
        print("  instances [--status STATUS] [--tier TIER] [--geo CC] [--heartbeat AGE] [--page N] [--limit N]")
        print("  instances_all [--status STATUS] [--tier TIER] [--geo CC]")
        print("  instance_detail INSTANCE_ID")
        print("  activation_log [--api_key KEY] [--page N] [--limit N]")
        print("  telemetry [--period 24h|7d|30d]")
        print("  alerts [--resolved true|false]")
        print("  customers [--search TEXT] [--country CC] [--tier TIER] [--page N] [--limit N]")
        print("  customer_detail CUSTOMER_ID")
        print("  products")
        sys.exit(1)

    command = sys.argv[1]
    args = sys.argv[2:]

    def _arg(flag, default=None):
        if flag in args:
            idx = args.index(flag)
            if idx + 1 < len(args):
                return args[idx + 1]
        return default

    try:
        if command == "keys":
            result = keys(status=_arg("--status"), tier=_arg("--tier"),
                         page=int(_arg("--page", 1)), limit=int(_arg("--limit", 25)))
        elif command == "keys_all":
            result = keys_all(status=_arg("--status"), tier=_arg("--tier"))
        elif command == "instances":
            result = instances(status=_arg("--status"), tier=_arg("--tier"),
                             geo=_arg("--geo"), heartbeat_age=_arg("--heartbeat"),
                             page=int(_arg("--page", 1)), limit=int(_arg("--limit", 25)))
        elif command == "instances_all":
            result = instances_all(status=_arg("--status"), tier=_arg("--tier"), geo=_arg("--geo"))
        elif command == "instance_detail":
            result = instance_detail(args[0] if args else "")
        elif command == "activation_log":
            result = activation_log(api_key=_arg("--api_key"),
                                   page=int(_arg("--page", 1)), limit=int(_arg("--limit", 50)))
        elif command == "telemetry":
            result = telemetry(period=_arg("--period", "24h"))
        elif command == "alerts":
            resolved = _arg("--resolved", "false") == "true"
            result = alerts(resolved=resolved)
        elif command == "customers":
            result = customers(search=_arg("--search"), country=_arg("--country"),
                             tier=_arg("--tier"), page=int(_arg("--page", 1)),
                             limit=int(_arg("--limit", 25)))
        elif command == "customer_detail":
            result = customer_detail(int(args[0]) if args else 0)
        elif command == "products":
            result = products()
        else:
            print(f"Unknown command: {command}")
            sys.exit(1)

        print(json.dumps(result, indent=2, ensure_ascii=False))
    except Exception as e:
        print(json.dumps({"error": str(e)}, indent=2))
        sys.exit(1)

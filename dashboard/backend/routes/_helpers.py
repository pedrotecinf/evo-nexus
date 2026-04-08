"""Shared helpers for route modules."""

import re
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parent.parent.parent.parent


def parse_frontmatter(text: str) -> dict:
    """Extract key-value pairs from YAML-style --- frontmatter."""
    m = re.match(r"^---\s*\n(.*?)\n---", text, re.DOTALL)
    if not m:
        return {}
    result = {}
    for line in m.group(1).splitlines():
        if ":" in line:
            key, _, val = line.partition(":")
            result[key.strip()] = val.strip().strip('"').strip("'")
    return result


def safe_read(path: Path, encoding: str = "utf-8") -> str | None:
    """Read file content safely, returning None on error."""
    try:
        return path.read_text(encoding=encoding, errors="replace")
    except Exception:
        return None


def file_info(path: Path, base: Path | None = None) -> dict:
    """Build a basic info dict for a file."""
    info = {
        "name": path.name,
        "path": str(path.relative_to(base)) if base else str(path),
        "extension": path.suffix,
        "size": path.stat().st_size if path.exists() else 0,
    }
    try:
        info["modified"] = path.stat().st_mtime
    except Exception:
        pass
    return info

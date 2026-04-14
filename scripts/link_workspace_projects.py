"""
link_workspace_projects.py — idempotent script to populate projects.workspace_folder_path.

Scans workspace/project/*.md (status files) and workspace/projects/*/ (git repos),
matches them to projects table rows by slug, and fills workspace_folder_path if NULL.

Usage:
    python scripts/link_workspace_projects.py
    uv run python scripts/link_workspace_projects.py
"""

from __future__ import annotations

import re
import sqlite3
import sys
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parent.parent
DB_PATH = WORKSPACE / "dashboard" / "data" / "evonexus.db"


def _slugify(name: str) -> str:
    """Convert folder/file name to slug: lowercase, hyphens."""
    s = name.lower().strip()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    s = s.strip("-")
    return s


def _collect_candidates() -> dict[str, str]:
    """
    Returns a mapping of slug → absolute path for all workspace project candidates.
    Sources:
      - workspace/project/*.md  (status docs, singular)
      - workspace/projects/*/   (git repos, plural)
    """
    candidates: dict[str, str] = {}

    # workspace/project/*.md
    project_singular = WORKSPACE / "workspace" / "project"
    if project_singular.is_dir():
        for md in project_singular.glob("*.md"):
            slug = _slugify(md.stem)
            if slug:
                candidates[slug] = str(md)

    # workspace/projects/*/
    projects_plural = WORKSPACE / "workspace" / "projects"
    if projects_plural.is_dir():
        for subdir in projects_plural.iterdir():
            if subdir.is_dir() and not subdir.name.startswith("."):
                slug = _slugify(subdir.name)
                if slug:
                    # Prefer git repo dirs over .md files (more specific)
                    candidates[slug] = str(subdir)

    return candidates


def main():
    if not DB_PATH.exists():
        print(f"ERROR: database not found at {DB_PATH}")
        sys.exit(1)

    conn = sqlite3.connect(str(DB_PATH))
    cur = conn.cursor()

    # Check table exists
    tables = {row[0] for row in cur.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()}
    if "projects" not in tables:
        print("ERROR: 'projects' table does not exist. Run migration first.")
        conn.close()
        sys.exit(1)

    # Load all projects
    rows = cur.execute("SELECT id, slug, workspace_folder_path FROM projects").fetchall()
    if not rows:
        print("No projects in database. Seed data may not have run yet.")
        conn.close()
        return

    candidates = _collect_candidates()
    print(f"Found {len(candidates)} workspace candidates: {list(candidates.keys())}")

    linked = 0
    skipped_manual = 0
    not_found = []

    for proj_id, slug, existing_path in rows:
        if existing_path is not None:
            # Already set manually — never overwrite
            skipped_manual += 1
            print(f"  SKIP (already set): {slug} → {existing_path}")
            continue

        # Try exact slug match
        path = candidates.get(slug)

        # Fallback: try partial match (e.g. "evo-ai" matches "evo-ai-crm" folder)
        if path is None:
            for cand_slug, cand_path in candidates.items():
                if cand_slug.startswith(slug) or slug.startswith(cand_slug):
                    path = cand_path
                    break

        if path:
            cur.execute(
                "UPDATE projects SET workspace_folder_path = ? WHERE id = ?",
                (path, proj_id),
            )
            linked += 1
            print(f"  LINKED: {slug} → {path}")
        else:
            not_found.append(slug)
            print(f"  NOT FOUND: {slug}")

    conn.commit()
    conn.close()

    print(f"\nSummary: {linked} linked, {skipped_manual} already set (skipped), {len(not_found)} not matched")
    if not_found:
        print(f"Unmatched slugs: {not_found}")


if __name__ == "__main__":
    main()

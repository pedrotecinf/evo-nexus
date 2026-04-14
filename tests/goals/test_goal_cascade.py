"""
tests/goals/test_goal_cascade.py

Goal Cascade (Feature 1.2) — unit + integration tests.

Run:
    cd /path/to/workspace && pytest tests/goals/ -v
"""

import json
import sqlite3
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch

import pytest

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

NOW = "2026-04-14T00:00:00.000000Z"


@pytest.fixture
def db_path(tmp_path):
    """Create an in-memory-like temp SQLite DB with goal cascade schema."""
    p = tmp_path / "test.db"
    conn = sqlite3.connect(str(p))
    conn.row_factory = sqlite3.Row
    conn.executescript("""
        CREATE TABLE missions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            slug TEXT UNIQUE NOT NULL,
            title TEXT NOT NULL,
            description TEXT,
            target_metric TEXT,
            target_value REAL,
            current_value REAL NOT NULL DEFAULT 0,
            due_date TEXT,
            status TEXT NOT NULL DEFAULT 'active',
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );
        CREATE TABLE projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            slug TEXT UNIQUE NOT NULL,
            mission_id INTEGER REFERENCES missions(id) ON DELETE CASCADE,
            title TEXT NOT NULL,
            description TEXT,
            workspace_folder_path TEXT,
            status TEXT NOT NULL DEFAULT 'active',
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );
        CREATE TABLE goals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            slug TEXT UNIQUE NOT NULL,
            project_id INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
            title TEXT NOT NULL,
            description TEXT,
            target_metric TEXT,
            metric_type TEXT NOT NULL DEFAULT 'count',
            target_value REAL NOT NULL DEFAULT 1.0,
            current_value REAL NOT NULL DEFAULT 0.0,
            due_date TEXT,
            status TEXT NOT NULL DEFAULT 'active',
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );
        CREATE TABLE goal_tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            goal_id INTEGER REFERENCES goals(id) ON DELETE SET NULL,
            title TEXT NOT NULL,
            description TEXT,
            priority INTEGER NOT NULL DEFAULT 3,
            assignee_agent TEXT,
            status TEXT NOT NULL DEFAULT 'open',
            locked_at TEXT,
            locked_by TEXT,
            due_date TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );
        CREATE INDEX idx_projects_mission ON projects(mission_id);
        CREATE INDEX idx_goals_project_status ON goals(project_id, status);
        CREATE INDEX idx_goal_tasks_goal_status ON goal_tasks(goal_id, status);
        CREATE VIEW goal_progress_v AS
        SELECT g.id as goal_id, g.slug, g.target_value,
               COUNT(t.id) as total_tasks,
               COUNT(CASE WHEN t.status='done' THEN 1 END) as done_tasks,
               CASE WHEN COUNT(t.id) > 0
                    THEN CAST(COUNT(CASE WHEN t.status='done' THEN 1 END) AS REAL) / COUNT(t.id) * 100.0
                    ELSE 0 END as pct_complete
        FROM goals g LEFT JOIN goal_tasks t ON t.goal_id = g.id
        GROUP BY g.id;
        CREATE TRIGGER trg_task_done_updates_goal
        AFTER UPDATE OF status ON goal_tasks
        WHEN NEW.goal_id IS NOT NULL AND NEW.status = 'done' AND OLD.status != 'done'
        BEGIN
          UPDATE goals SET current_value = current_value + 1, updated_at = datetime('now') WHERE id = NEW.goal_id;
          UPDATE goals SET status = 'achieved' WHERE id = NEW.goal_id AND current_value >= target_value AND status = 'active';
        END;
    """)
    conn.commit()
    return p


@pytest.fixture
def seed_data(db_path):
    """Seed 1 Mission, 1 Project, 1 Goal into test DB. Returns (conn, ids)."""
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO missions (slug, title, target_value, current_value, status, created_at, updated_at) "
        "VALUES ('test-mission', 'Test Mission', 1000000, 0, 'active', ?, ?)", (NOW, NOW)
    )
    mission_id = cur.lastrowid
    cur.execute(
        "INSERT INTO projects (slug, mission_id, title, status, created_at, updated_at) "
        "VALUES ('test-project', ?, 'Test Project', 'active', ?, ?)", (mission_id, NOW, NOW)
    )
    project_id = cur.lastrowid
    cur.execute(
        "INSERT INTO goals (slug, project_id, title, metric_type, target_value, current_value, status, created_at, updated_at) "
        "VALUES ('test-goal', ?, 'Test Goal', 'count', 3, 0, 'active', ?, ?)", (project_id, NOW, NOW)
    )
    goal_id = cur.lastrowid
    conn.commit()
    conn.close()
    return db_path, mission_id, project_id, goal_id


# ---------------------------------------------------------------------------
# Unit tests: schema + view
# ---------------------------------------------------------------------------

def test_schema_tables_exist(db_path):
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    tables = {row[0] for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()}
    conn.close()
    assert "missions" in tables
    assert "projects" in tables
    assert "goals" in tables
    assert "goal_tasks" in tables


def test_view_goal_progress_v_exists(db_path):
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    views = {row[0] for row in conn.execute("SELECT name FROM sqlite_master WHERE type='view'").fetchall()}
    conn.close()
    assert "goal_progress_v" in views


def test_view_pct_compute_correct(seed_data):
    """2 done out of 3 tasks → pct ≈ 66.67."""
    db, _, _, goal_id = seed_data
    conn = sqlite3.connect(str(db))
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    for title, status in [("T1", "done"), ("T2", "done"), ("T3", "open")]:
        cur.execute(
            "INSERT INTO goal_tasks (goal_id, title, status, created_at, updated_at) VALUES (?, ?, ?, ?, ?)",
            (goal_id, title, status, NOW, NOW),
        )
    conn.commit()
    row = conn.execute("SELECT pct_complete, done_tasks, total_tasks FROM goal_progress_v WHERE goal_id=?", (goal_id,)).fetchone()
    conn.close()
    assert row["total_tasks"] == 3
    assert row["done_tasks"] == 2
    assert abs(row["pct_complete"] - 66.666) < 0.1


def test_view_zero_tasks_pct_zero(seed_data):
    db, _, _, goal_id = seed_data
    conn = sqlite3.connect(str(db))
    conn.row_factory = sqlite3.Row
    row = conn.execute("SELECT pct_complete, done_tasks FROM goal_progress_v WHERE goal_id=?", (goal_id,)).fetchone()
    conn.close()
    assert row["pct_complete"] == 0
    assert row["done_tasks"] == 0


# ---------------------------------------------------------------------------
# Unit tests: trigger on task done
# ---------------------------------------------------------------------------

def test_trigger_increments_current_value(seed_data):
    db, _, _, goal_id = seed_data
    conn = sqlite3.connect(str(db))
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    # Insert open task
    cur.execute(
        "INSERT INTO goal_tasks (goal_id, title, status, created_at, updated_at) VALUES (?, 'Task A', 'open', ?, ?)",
        (goal_id, NOW, NOW),
    )
    task_id = cur.lastrowid
    conn.commit()
    # Mark done → trigger should fire
    cur.execute("UPDATE goal_tasks SET status='done' WHERE id=?", (task_id,))
    conn.commit()
    row = conn.execute("SELECT current_value FROM goals WHERE id=?", (goal_id,)).fetchone()
    conn.close()
    assert row["current_value"] == 1.0


def test_trigger_achieves_goal_when_target_met(seed_data):
    db, _, _, goal_id = seed_data
    conn = sqlite3.connect(str(db))
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    # target_value is 3 — insert 3 open tasks and mark all done
    task_ids = []
    for i in range(3):
        cur.execute(
            "INSERT INTO goal_tasks (goal_id, title, status, created_at, updated_at) VALUES (?, ?, 'open', ?, ?)",
            (goal_id, f"Task {i}", NOW, NOW),
        )
        task_ids.append(cur.lastrowid)
    conn.commit()
    for tid in task_ids:
        cur.execute("UPDATE goal_tasks SET status='done' WHERE id=?", (tid,))
        conn.commit()
    row = conn.execute("SELECT current_value, status FROM goals WHERE id=?", (goal_id,)).fetchone()
    conn.close()
    assert row["current_value"] == 3.0
    assert row["status"] == "achieved"


def test_trigger_does_not_regress_achieved_goal(seed_data):
    """Once achieved, additional done tasks don't change status back."""
    db, _, _, goal_id = seed_data
    conn = sqlite3.connect(str(db))
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    # Set goal to already achieved
    cur.execute("UPDATE goals SET status='achieved', current_value=3 WHERE id=?", (goal_id,))
    # Insert another task and mark done
    cur.execute(
        "INSERT INTO goal_tasks (goal_id, title, status, created_at, updated_at) VALUES (?, 'Extra', 'open', ?, ?)",
        (goal_id, NOW, NOW),
    )
    task_id = cur.lastrowid
    conn.commit()
    cur.execute("UPDATE goal_tasks SET status='done' WHERE id=?", (task_id,))
    conn.commit()
    row = conn.execute("SELECT status FROM goals WHERE id=?", (goal_id,)).fetchone()
    conn.close()
    # Status stays achieved — trigger's CASE clause handles this
    assert row["status"] == "achieved"


def test_trigger_not_fired_for_cancelled(seed_data):
    """Marking a task cancelled should NOT increment current_value."""
    db, _, _, goal_id = seed_data
    conn = sqlite3.connect(str(db))
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO goal_tasks (goal_id, title, status, created_at, updated_at) VALUES (?, 'X', 'open', ?, ?)",
        (goal_id, NOW, NOW),
    )
    task_id = cur.lastrowid
    conn.commit()
    cur.execute("UPDATE goal_tasks SET status='cancelled' WHERE id=?", (task_id,))
    conn.commit()
    row = conn.execute("SELECT current_value FROM goals WHERE id=?", (goal_id,)).fetchone()
    conn.close()
    assert row["current_value"] == 0.0


# ---------------------------------------------------------------------------
# Unit tests: cascade FK behaviour
# ---------------------------------------------------------------------------

def test_delete_mission_cascades_to_project_and_goal(seed_data):
    db, mission_id, project_id, goal_id = seed_data
    conn = sqlite3.connect(str(db))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("DELETE FROM missions WHERE id=?", (mission_id,))
    conn.commit()
    projects = conn.execute("SELECT id FROM projects WHERE id=?", (project_id,)).fetchall()
    goals = conn.execute("SELECT id FROM goals WHERE id=?", (goal_id,)).fetchall()
    conn.close()
    assert len(projects) == 0
    assert len(goals) == 0


def test_delete_goal_sets_task_goal_id_null(seed_data):
    db, _, _, goal_id = seed_data
    conn = sqlite3.connect(str(db))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO goal_tasks (goal_id, title, status, created_at, updated_at) VALUES (?, 'Orphan', 'open', ?, ?)",
        (goal_id, NOW, NOW),
    )
    task_id = cur.lastrowid
    conn.commit()
    conn.execute("DELETE FROM goals WHERE id=?", (goal_id,))
    conn.commit()
    row = conn.execute("SELECT goal_id FROM goal_tasks WHERE id=?", (task_id,)).fetchone()
    conn.close()
    assert row["goal_id"] is None  # ON DELETE SET NULL


# ---------------------------------------------------------------------------
# Unit tests: goal_context.py
# ---------------------------------------------------------------------------

def test_goal_context_no_ids_returns_empty():
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "dashboard" / "backend"))
    try:
        from goal_context import build_goal_context
        result = build_goal_context(project_id=None, goal_id=None)
        assert result == ""
    except ImportError:
        pytest.skip("goal_context module not importable in this env")


def test_inject_into_prompt_no_context():
    """If no context, prompt returned unchanged."""
    sys.path = [str(Path(__file__).resolve().parent.parent.parent / "dashboard" / "backend")] + sys.path
    try:
        from goal_context import inject_into_prompt
        original = "Original prompt content"
        result = inject_into_prompt(original)
        assert result == original
    except ImportError:
        pytest.skip("goal_context module not importable in this env")


import sys  # noqa: E402 — needed at module level for skip


# ---------------------------------------------------------------------------
# Integration test: full create → done → recalculate flow
# ---------------------------------------------------------------------------

def test_integration_mission_project_goal_task_flow(db_path):
    """
    Create mission → project → goal (target=2) → 2 tasks.
    Mark both done → verify current_value=2, status='achieved'.
    """
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    # Mission
    cur.execute(
        "INSERT INTO missions (slug, title, target_value, current_value, status, created_at, updated_at) "
        "VALUES ('m1', 'M1', 100, 0, 'active', ?, ?)", (NOW, NOW)
    )
    mid = cur.lastrowid

    # Project
    cur.execute(
        "INSERT INTO projects (slug, mission_id, title, status, created_at, updated_at) "
        "VALUES ('p1', ?, 'P1', 'active', ?, ?)", (mid, NOW, NOW)
    )
    pid = cur.lastrowid

    # Goal with target=2
    cur.execute(
        "INSERT INTO goals (slug, project_id, title, metric_type, target_value, current_value, status, created_at, updated_at) "
        "VALUES ('g1', ?, 'G1', 'count', 2, 0, 'active', ?, ?)", (pid, NOW, NOW)
    )
    gid = cur.lastrowid
    conn.commit()

    # 2 tasks
    for name in ["T1", "T2"]:
        cur.execute(
            "INSERT INTO goal_tasks (goal_id, title, status, created_at, updated_at) VALUES (?, ?, 'open', ?, ?)",
            (gid, name, NOW, NOW),
        )
    conn.commit()
    task_ids = [r[0] for r in cur.execute("SELECT id FROM goal_tasks WHERE goal_id=?", (gid,)).fetchall()]

    # Mark both done
    for tid in task_ids:
        cur.execute("UPDATE goal_tasks SET status='done' WHERE id=?", (tid,))
        conn.commit()

    row = conn.execute("SELECT current_value, status FROM goals WHERE id=?", (gid,)).fetchone()
    conn.close()

    assert row[0] == 2.0
    assert row[1] == "achieved"


def test_integration_recalculate_corrects_drift(db_path):
    """
    If current_value drifts (e.g. after bulk operations bypassing the trigger),
    recalculating from goal_progress_v should correct it.
    """
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    cur.execute(
        "INSERT INTO missions (slug, title, target_value, current_value, status, created_at, updated_at) "
        "VALUES ('m2', 'M2', 100, 0, 'active', ?, ?)", (NOW, NOW)
    )
    mid = cur.lastrowid
    cur.execute(
        "INSERT INTO projects (slug, mission_id, title, status, created_at, updated_at) "
        "VALUES ('p2', ?, 'P2', 'active', ?, ?)", (mid, NOW, NOW)
    )
    pid = cur.lastrowid
    cur.execute(
        "INSERT INTO goals (slug, project_id, title, metric_type, target_value, current_value, status, created_at, updated_at) "
        "VALUES ('g2', ?, 'G2', 'count', 5, 99, 'active', ?, ?)", (pid, NOW, NOW)  # current_value=99 (drift)
    )
    gid = cur.lastrowid

    # Insert 2 done tasks directly (bypass trigger by using INSERT, not UPDATE)
    for name in ["D1", "D2"]:
        cur.execute(
            "INSERT INTO goal_tasks (goal_id, title, status, created_at, updated_at) VALUES (?, ?, 'done', ?, ?)",
            (gid, name, NOW, NOW),
        )
    conn.commit()

    # Recalculate from view
    row_v = conn.execute("SELECT done_tasks FROM goal_progress_v WHERE goal_id=?", (gid,)).fetchone()
    correct_value = float(row_v[0])
    cur.execute("UPDATE goals SET current_value=?, updated_at=datetime('now') WHERE id=?", (correct_value, gid))
    conn.commit()

    row = conn.execute("SELECT current_value FROM goals WHERE id=?", (gid,)).fetchone()
    conn.close()
    assert row[0] == 2.0  # not 99 anymore


# ---------------------------------------------------------------------------
# Unit tests: link_workspace_projects.py idempotency
# ---------------------------------------------------------------------------

def test_link_script_idempotent(db_path, tmp_path, monkeypatch):
    """Running link script twice should not change existing paths."""
    # Setup a minimal workspace
    projects_dir = tmp_path / "workspace" / "projects"
    (projects_dir / "evo-ai").mkdir(parents=True)

    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO missions (slug, title, target_value, current_value, status, created_at, updated_at) "
        "VALUES ('m3', 'M3', 10, 0, 'active', ?, ?)", (NOW, NOW)
    )
    mid = cur.lastrowid
    cur.execute(
        "INSERT INTO projects (slug, mission_id, title, workspace_folder_path, status, created_at, updated_at) "
        "VALUES ('evo-ai', ?, 'Evo AI', NULL, 'active', ?, ?)", (mid, NOW, NOW)
    )
    conn.commit()
    conn.close()

    # Import and run the linker
    import sys
    script_dir = str(Path(__file__).resolve().parent.parent.parent / "scripts")
    if script_dir not in sys.path:
        sys.path.insert(0, script_dir)

    try:
        import link_workspace_projects as lw
    except ImportError:
        pytest.skip("link_workspace_projects not importable")

    # Monkeypatch WORKSPACE and DB_PATH
    monkeypatch.setattr(lw, "WORKSPACE", tmp_path)
    monkeypatch.setattr(lw, "DB_PATH", db_path)

    # First run
    lw.main()

    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    path_after_first = conn.execute("SELECT workspace_folder_path FROM projects WHERE slug='evo-ai'").fetchone()[0]
    conn.close()

    # Second run
    lw.main()

    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    path_after_second = conn.execute("SELECT workspace_folder_path FROM projects WHERE slug='evo-ai'").fetchone()[0]
    conn.close()

    # Path should be set after first run and unchanged by second run
    assert path_after_first is not None
    assert path_after_first == path_after_second

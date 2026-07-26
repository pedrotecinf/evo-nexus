"""Allowlisted ECC workflow catalog."""

from __future__ import annotations

import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] / ".ecc" / "commands"
MAX_WORKFLOW_BYTES = 128 * 1024
TASK_WORKFLOWS = {
    "bug": "orch-fix-defect",
    "feature": "orch-add-feature",
    "refactor": "orch-refine-code",
    "review": "orch-review",
    "security": "orch-review",
    "research": "orch-review",
}


def resolve_workflow(task_type: str, override: str | None = None) -> dict:
    slug = override or TASK_WORKFLOWS.get(task_type)
    if slug not in set(TASK_WORKFLOWS.values()):
        raise ValueError("Workflow is not allowlisted")
    path = (ROOT / f"{slug}.md").resolve()
    if path.parent != ROOT.resolve() or path.is_symlink() or not path.is_file():
        raise ValueError("Workflow source is invalid")
    content = path.read_bytes()
    if len(content) > MAX_WORKFLOW_BYTES:
        raise ValueError("Workflow source exceeds size limit")
    return {"slug": slug, "sha256": hashlib.sha256(content).hexdigest(), "risk": "high" if task_type == "security" else "standard"}

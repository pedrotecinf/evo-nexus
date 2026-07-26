from __future__ import annotations

from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
DEPLOYMENT_FILES = (
    "docker-compose.hub.yml",
    "docker-compose.proxy.yml",
    "evonexus.stack.yml",
)


def _load_compose(path: Path) -> dict:
    rendered = path.read_text().replace("${EVONEXUS_IMAGE_TAG:?set EVONEXUS_IMAGE_TAG to an immutable sha-* tag}", "sha-test")
    return yaml.safe_load(rendered)


def test_production_deployments_require_one_immutable_revision_tag():
    for relative_path in DEPLOYMENT_FILES:
        contents = (ROOT / relative_path).read_text()
        assert ":latest" not in contents
        assert "${EVONEXUS_IMAGE_TAG:?set EVONEXUS_IMAGE_TAG to an immutable sha-* tag}" in contents

        services = _load_compose(ROOT / relative_path)["services"]
        dashboard = services.get("dashboard", services.get("evonexus_dashboard"))
        assert dashboard["image"].endswith(":sha-test")


def test_scheduler_uses_runtime_image_at_the_same_revision_as_dashboard():
    for relative_path in DEPLOYMENT_FILES:
        services = _load_compose(ROOT / relative_path)["services"]
        scheduler = services.get("scheduler", services.get("evonexus_scheduler"))
        assert "evo-nexus-runtime" in scheduler["image"]
        assert "sha-test" in scheduler["image"]


def test_runtime_image_installs_claude_and_hermes():
    dockerfile = (ROOT / "Dockerfile.swarm").read_text()
    assert "@anthropic-ai/claude-code" in dockerfile
    assert "uv tool install hermes-agent" in dockerfile


def test_stack_checks_dashboard_and_scheduler_capabilities():
    stack = (ROOT / "evonexus.stack.yml").read_text()
    assert 'evonexus_dashboard:' in stack
    assert 'command -v claude && command -v hermes && curl -fsS http://localhost:${EVONEXUS_PORT:-8080}/api/version' in stack
    assert 'evonexus_scheduler:' in stack
    assert 'test: ["CMD-SHELL", "command -v claude && command -v hermes"]' in stack


def test_publish_workflow_does_not_publish_latest():
    workflow = (ROOT / ".github/workflows/docker-publish.yml").read_text()
    assert "latest=" not in workflow
    assert "type=sha,prefix=sha-,format=short" in workflow

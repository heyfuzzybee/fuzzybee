"""Integration tests: v0.2 doc structure, package.json, SKILL.md, bin scripts."""
import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def test_package_json_has_npx_fields():
    pkg = json.loads((ROOT / "package.json").read_text())
    assert "name" in pkg
    assert "version" in pkg
    assert "bin" in pkg
    assert "scripts" in pkg
    assert pkg["name"].startswith("@") or pkg["name"] == "fuzzybee"


def test_skill_md_has_required_sections():
    text = (ROOT / "SKILL.md").read_text()
    assert "## When to invoke" in text
    assert "## STOP GATES" in text
    assert "## Workflow" in text
    assert "## CLI" in text
    assert "## Dashboard" in text


def test_all_skill_directories_have_skill_md():
    skills_dir = ROOT / "skills"
    for d in skills_dir.iterdir():
        if d.is_dir():
            assert (d / "SKILL.md").exists(), f"skills/{d.name}/SKILL.md missing"
            assert len((d / "SKILL.md").read_text()) > 50


def test_sections_complete():
    for s in ["contract.md", "workflow.md", "gates.md", "integration.md", "CONTEXT.md"]:
        assert (ROOT / "sections" / s).exists(), f"sections/{s} missing"


def test_references_complete():
    for r in ["flow-skill.md", "skill-integration.md", "secure-code-review-integration.md"]:
        assert (ROOT / "references" / r).exists(), f"references/{r} missing"


def test_bin_scripts_executable():
    bin_dir = ROOT / "bin"
    for b in bin_dir.iterdir():
        if b.is_file() and not b.name.startswith("."):
            assert os.access(b, os.X_OK), f"bin/{b.name} not executable"


def test_pyproject_toml_has_extras():
    text = (ROOT / "pyproject.toml").read_text()
    for extra in ["dev", "lint", "test", "mem0"]:
        assert f'"{extra}"' in text or f"'{extra}'" in text or f"{extra} =" in text


def test_health_script_exists():
    health = ROOT / "bin/fuzzybee-health"
    assert health.exists()
    assert os.access(health, os.X_OK)
    assert health.read_text().startswith("#!/")


def test_stop_gates_documented():
    skill = (ROOT / "SKILL.md").read_text()
    gates = (ROOT / "sections/gates.md").read_text()
    for gate in ["S1", "S2", "S3", "S4"]:
        assert gate in skill or gate in gates

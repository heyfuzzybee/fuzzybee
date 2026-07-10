"""Tests for engine.py — ExecutionEngine."""
from datetime import datetime
from unittest.mock import patch, MagicMock

import pytest

from lib.engine import ExecutionEngine
from lib.decompose import Unit, UnitType
from lib.gate import GateStatus


def test_engine_initializes_with_default_evidence_dir():
    engine = ExecutionEngine()
    assert "docs/status/execution-gates" in str(engine.evidence_dir)
    assert engine.evidence_dir.exists()


def test_check_health_returns_expected_keys():
    engine = ExecutionEngine()
    health = engine.check_health()
    assert "engine" in health
    assert "gap_auditor" in health
    assert "git" in health
    assert "evidence_dir_writable" in health


def test_classify_problem_bug():
    engine = ExecutionEngine()
    assert engine._classify_problem("crash when user submits form with empty email").value == "bug"
    assert engine._classify_problem("add login page to app").value == "feature"
    assert engine._classify_problem("audit memory architecture").value == "audit"


def test_decompose_bug_returns_3_units():
    engine = ExecutionEngine()
    units = engine.decompose("crash on empty submit")
    assert len(units) == 3
    assert all(isinstance(u, Unit) for u in units)
    assert "bats" in units[2].pass_criteria


def test_execute_runs_gate_and_records_evidence():
    engine = ExecutionEngine()
    unit = Unit(
        task_id="test-01",
        subject="Test unit",
        unit_type=UnitType.VERIFY,
        pass_criteria="`echo hello`",
    )
    with patch("lib.gate.subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(returncode=0, stdout="hello\n", stderr="")
        cycle = engine.execute(unit)
    assert len(unit.evidence) == 1
    assert unit.evidence[0].status == GateStatus.PASS


def test_3_strike_escalation_blocks():
    engine = ExecutionEngine()
    unit = Unit(
        task_id="test-01",
        subject="Test unit",
        unit_type=UnitType.VERIFY,
        pass_criteria="`false`",
    )
    unit.gate_failures = 3
    with patch("lib.gate.subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(returncode=1, stdout="", stderr="fail")
        cycle = engine.execute(unit)
    assert cycle["status"] == "BLOCKED"
    assert any("3-strike" in v for v in cycle["sla_violations"])


def test_sla_tool_call_limit_enforced():
    engine = ExecutionEngine()
    unit = Unit(
        task_id="test-01",
        subject="Test unit",
        unit_type=UnitType.VERIFY,
        pass_criteria="`echo hello`",
    )
    unit.tool_calls = 8
    with patch("lib.gate.subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")
        cycle = engine.execute(unit)
    assert cycle["status"] == "BLOCKED"


def test_report_produces_markdown():
    engine = ExecutionEngine()
    unit = Unit(
        task_id="test-01",
        subject="Test unit",
        unit_type=UnitType.VERIFY,
        pass_criteria="`echo hello`",
    )
    cycle = {
        "cycle_number": 1,
        "status": "PASS",
        "sla_violations": [],
        "wall_clock_s": 1.5,
        "tool_calls": 2,
    }
    report = engine.report(unit, cycle)
    assert "# Cycle Report" in report
    assert "Test unit" in report
    assert "PASS" in report


def test_evidence_json_schema():
    engine = ExecutionEngine()
    record = engine.gate_runner.run("schema-test", "`echo test`")
    # Evidence file should be written
    assert record.evidence_file is not None
    import json
    with open(record.evidence_file) as f:
        data = json.load(f)
    assert "gate_name" in data
    assert "status" in data
    assert "timestamp" in data


def test_health_includes_recommendations():
    engine = ExecutionEngine()
    health = engine.check_health()
    assert "recommendations" in health
    assert isinstance(health["recommendations"], list)
    for rec in health["recommendations"]:
        assert "name" in rec
        assert "installed" in rec


def test_execute_handles_empty_pass_criteria():
    engine = ExecutionEngine()
    unit = Unit(
        task_id="test-empty",
        subject="Empty pass criteria",
        unit_type=UnitType.VERIFY,
        pass_criteria="",
    )
    from unittest.mock import patch, MagicMock
    with patch("lib.gate.subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")
        cycle = engine.execute(unit)
    assert cycle["status"] in ("PASS", "FAIL", "BLOCKED", "ERROR")


def test_engine_can_create_report_without_execute():
    engine = ExecutionEngine()
    unit = Unit(
        task_id="pre-report",
        subject="Report without executing",
        unit_type=UnitType.VERIFY,
        pass_criteria="`true`",
    )
    cycle = {
        "cycle_number": 1,
        "status": "SKIPPED",
        "sla_violations": [],
        "wall_clock_s": 0.0,
        "tool_calls": 0,
    }
    report = engine.report(unit, cycle)
    assert "# Cycle Report" in report
    assert "SKIPPED" in report


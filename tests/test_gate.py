"""Tests for gate.py — GateRunner, EvidenceRecord, GateStatus."""
import subprocess
from unittest.mock import patch, MagicMock

import pytest

from lib.gate import EvidenceRecord, GateRunner, GateStatus


def test_gate_runner_parses_exit_code_0_as_pass():
    runner = GateRunner(evidence_dir="/tmp/fuzzybee-test-evidence")
    with patch("lib.gate.subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")
        record = runner.run("test-gate", "echo hello", expected="exit 0")
    assert record.status == GateStatus.PASS


def test_gate_runner_parses_exit_code_nonzero_as_fail():
    runner = GateRunner(evidence_dir="/tmp/fuzzybee-test-evidence")
    with patch("lib.gate.subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(returncode=1, stdout="", stderr="error")
        record = runner.run("test-gate", "false", expected="exit 0")
    assert record.status == GateStatus.FAIL


def test_gate_runner_timeout_kills_subprocess():
    runner = GateRunner(evidence_dir="/tmp/fuzzybee-test-evidence")
    with patch("lib.gate.subprocess.run") as mock_run:
        mock_run.side_effect = subprocess.TimeoutExpired("cmd", 30)
        record = runner.run("test-gate", "sleep 60", timeout=1)
    assert record.status == GateStatus.FAIL
    assert "TIMEOUT" in record.actual


def test_evidence_record_schema_matches_dataclass():
    record = EvidenceRecord(
        gate_name="g1",
        command="echo test",
        expected="exit 0",
        actual="exit 0",
        status=GateStatus.PASS,
    )
    d = record.to_dict()
    assert d["gate_name"] == "g1"
    assert d["status"] == "PASS"
    assert "timestamp" in d


def test_evidence_json_round_trip():
    record = EvidenceRecord(
        gate_name="g1",
        command="echo test",
        expected="exit 0",
        actual="exit 0",
        status=GateStatus.PASS,
    )
    d = record.to_dict()
    restored = EvidenceRecord.from_dict(d)
    assert restored.gate_name == record.gate_name
    assert restored.status == record.status

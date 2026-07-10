"""Tests for telemetry.py — TelemetryLogger."""
import json
import tempfile
import os

from lib.telemetry import TelemetryLogger, TelemetryTier


def test_telemetry_off_does_not_write():
    with tempfile.TemporaryDirectory() as td:
        logger = TelemetryLogger(tier=TelemetryTier.OFF, log_dir=td)
        logger.log("test", 1000)
        path = f"{td}/skill-usage.jsonl"
        assert not os.path.exists(path)


def test_telemetry_anonymous_writes_minimal():
    with tempfile.TemporaryDirectory() as td:
        logger = TelemetryLogger(tier=TelemetryTier.ANONYMOUS, log_dir=td)
        logger.log("fuzzybee", 1500, pass_count=2, fail_count=1)
        with open(f"{td}/skill-usage.jsonl") as f:
            data = json.loads(f.readline())
        assert data["skill"] == "fuzzybee"
        assert "pass_count" in data
        assert "cycle_type" not in data  # community only

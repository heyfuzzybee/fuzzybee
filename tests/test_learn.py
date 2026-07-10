"""Tests for learn.py — InstinctLogger."""
import json
import tempfile
from pathlib import Path

from lib.learn import InstinctLogger


def test_instinct_log_creates_jsonl_line():
    with tempfile.TemporaryDirectory() as td:
        path = Path(td) / "learnings.jsonl"
        logger = InstinctLogger(log_path=str(path))
        logger.log_cycle("bug", "PASS", 4, 45000)
        assert path.exists()
        lines = list(path.open())
        assert len(lines) == 1
        data = json.loads(lines[0])
        assert data["pattern"] == "bug:PASS"


def test_confidence_scoring_decrements_correctly():
    with tempfile.TemporaryDirectory() as td:
        path = Path(td) / "learnings.jsonl"
        logger = InstinctLogger(log_path=str(path))
        # Write old entry
        old = {
            "pattern": "bug:FAIL",
            "confidence": 1.0,
            "timestamp": "2026-06-01T00:00:00",
        }
        with open(path, "w") as f:
            f.write(json.dumps(old) + "\n")
        logger.confidence_decay(days=7)
        with open(path) as f:
            data = json.loads(f.readline())
        assert data["confidence"] < 1.0


def test_learnings_file_created_on_first_write():
    with tempfile.TemporaryDirectory() as td:
        path = Path(td) / "sub" / "learnings.jsonl"
        logger = InstinctLogger(log_path=str(path))
        logger.log_cycle("feature", "PASS", 2, 1000)
        assert path.exists()


def test_injection_sanitization_in_pattern_strings():
    # Patterns with special chars should still be loggable (JSON handles escaping)
    logger = InstinctLogger(log_path="/tmp/fuzzybee-test-inject.jsonl")
    logger.log_cycle("bug<script>", "PASS", 1, 100)
    with open("/tmp/fuzzybee-test-inject.jsonl") as f:
        data = json.loads(f.readline())
    assert data["problem_type"] == "bug<script>"

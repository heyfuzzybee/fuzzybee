"""Tests for session.py — SessionDetector."""
from lib.session import SessionDetector, SessionKind


def test_detect_interactive_default():
    d = SessionDetector()
    kind = d.detect()
    # In test environment, usually interactive (no CI vars set)
    assert kind in (SessionKind.INTERACTIVE, SessionKind.HEADLESS, SessionKind.SPAWNED)


def test_detect_str_returns_string():
    d = SessionDetector()
    s = d.detect_str()
    assert s in ("interactive", "headless", "spawned")

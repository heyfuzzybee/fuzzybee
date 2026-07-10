"""Tests for sla.py — SLAEnforcer."""
from lib.sla import SLAEnforcer


def test_sla_no_violation_within_limits():
    e = SLAEnforcer()
    assert e.check(tool_calls=5, elapsed_s=300, gate_failures=1) is None


def test_sla_tool_call_limit_blocks():
    e = SLAEnforcer()
    v = e.check(tool_calls=8, elapsed_s=100, gate_failures=0)
    assert v is not None
    assert "tool calls" in v


def test_sla_3_strike_escalation():
    e = SLAEnforcer()
    v = e.check(tool_calls=2, elapsed_s=100, gate_failures=3)
    assert v is not None
    assert "3-strike" in v

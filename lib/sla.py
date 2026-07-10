"""SLA enforcement: tool-call limits, wall-clock limits, strike system."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class SLAEnforcer:
    """Enforce execution boundaries per unit."""

    MAX_TOOL_CALLS: int = 8
    MAX_WALL_CLOCK_S: float = 600.0  # 10 min
    MAX_GATE_FAILURES: int = 3  # strike 3 = BLOCKED

    def check(self, tool_calls: int, elapsed_s: float, gate_failures: int) -> Optional[str]:
        """Return violation message or None. Called after each gate.

        Args:
            tool_calls: Number of tool calls made so far.
            elapsed_s: Seconds elapsed since unit start.
            gate_failures: Number of consecutive gate failures.
        """
        if tool_calls >= self.MAX_TOOL_CALLS:
            return f"SLA: {tool_calls} tool calls exceeds {self.MAX_TOOL_CALLS}"
        if elapsed_s >= self.MAX_WALL_CLOCK_S:
            return f"SLA: {elapsed_s:.0f}s exceeds {self.MAX_WALL_CLOCK_S}s"
        if gate_failures >= self.MAX_GATE_FAILURES:
            return f"STOP: 3-strike escalation"
        return None

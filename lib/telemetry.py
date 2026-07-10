"""Telemetry: 3-tier privacy (off / anonymous / community)."""
from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, Optional


class TelemetryTier(Enum):
    OFF = "off"
    ANONYMOUS = "anonymous"
    COMMUNITY = "community"


@dataclass
class TelemetryLogger:
    """Log skill usage analytics with tiered privacy."""

    tier: TelemetryTier = TelemetryTier.OFF
    log_dir: str = "~/.execute/analytics"

    def __post_init__(self):
        self.log_path = Path(self.log_dir).expanduser() / "skill-usage.jsonl"
        self.log_path.parent.mkdir(parents=True, exist_ok=True)

    def log(
        self,
        skill_name: str,
        duration_ms: float,
        pass_count: int = 0,
        fail_count: int = 0,
        cycle_type: Optional[str] = None,
        problem_type: Optional[str] = None,
        gate_outcomes: Optional[list] = None,
    ) -> None:
        """Append telemetry entry based on tier."""
        if self.tier == TelemetryTier.OFF:
            return

        entry: Dict[str, Any] = {
            "skill": skill_name,
            "duration_ms": duration_ms,
            "pass_count": pass_count,
            "fail_count": fail_count,
            "timestamp": datetime.now().isoformat(),
        }

        if self.tier == TelemetryTier.COMMUNITY:
            entry["cycle_type"] = cycle_type
            entry["problem_type"] = problem_type
            entry["gate_outcomes"] = gate_outcomes or []

        with open(self.log_path, "a") as f:
            f.write(json.dumps(entry) + "\n")

    def get_tier(self) -> TelemetryTier:
        return self.tier

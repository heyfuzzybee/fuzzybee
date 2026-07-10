"""Gate system: run pass/fail commands, record evidence."""
from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Optional


class GateStatus(Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    BLOCKED = "BLOCKED"
    SKIPPED = "SKIPPED"
    ERROR = "ERROR"


@dataclass
class EvidenceRecord:
    gate_name: str
    command: str
    expected: str
    actual: str
    status: GateStatus
    timestamp: datetime = field(default_factory=datetime.now)
    evidence_file: Optional[str] = None
    duration_ms: float = 0.0

    def to_dict(self) -> dict:
        d = asdict(self)
        d["status"] = self.status.value
        d["timestamp"] = self.timestamp.isoformat()
        return d

    @classmethod
    def from_dict(cls, data: dict) -> "EvidenceRecord":
        data["status"] = GateStatus(data["status"])
        data["timestamp"] = datetime.fromisoformat(data["timestamp"])
        return cls(**data)


class GateRunner:
    """Run a gate command and produce an EvidenceRecord."""

    DEFAULT_TIMEOUT = 30

    def __init__(self, evidence_dir: str = "docs/status/execution-gates/"):
        self.evidence_dir = Path(evidence_dir).expanduser()
        self.evidence_dir.mkdir(parents=True, exist_ok=True)

    def run(
        self,
        gate_name: str,
        command: str,
        expected: str = "exit 0",
        timeout: Optional[int] = None,
    ) -> EvidenceRecord:
        """Execute a gate command, return EvidenceRecord.

        Args:
            gate_name: Human-readable gate identifier.
            command: Shell command or backtick expression to run.
            expected: Expected outcome (default: exit 0).
            timeout: Seconds before killing subprocess (default 30).
        """
        timeout = timeout or self.DEFAULT_TIMEOUT
        started = datetime.now()

        # Parse command: backtick expression or shell command
        if command.startswith("`") and command.endswith("`"):
            cmd = command[1:-1]
        else:
            cmd = command

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
                shell=True,  # Required for backtick expressions and compound commands
            )
            actual = f"exit {result.returncode}"
            if result.stdout:
                actual += f" | stdout: {result.stdout.strip()[:500]}"
            if result.stderr:
                actual += f" | stderr: {result.stderr.strip()[:500]}"

            # Determine status
            if expected.startswith("exit "):
                expected_code = int(expected.replace("exit ", ""))
                status = GateStatus.PASS if result.returncode == expected_code else GateStatus.FAIL
            elif expected in actual:
                status = GateStatus.PASS
            else:
                status = GateStatus.FAIL

        except subprocess.TimeoutExpired:
            actual = f"TIMEOUT after {timeout}s"
            status = GateStatus.FAIL
        except Exception as exc:
            actual = f"ERROR: {exc}"
            status = GateStatus.ERROR

        duration_ms = (datetime.now() - started).total_seconds() * 1000

        record = EvidenceRecord(
            gate_name=gate_name,
            command=command,
            expected=expected,
            actual=actual,
            status=status,
            duration_ms=duration_ms,
        )

        # Persist evidence to file
        self._write_evidence(record)
        return record

    def _write_evidence(self, record: EvidenceRecord) -> Path:
        """Write evidence record as JSON to evidence_dir."""
        ts = record.timestamp.strftime("%Y%m%d-%H%M%S")
        filename = f"{record.gate_name}-{ts}-{record.status.value}.json"
        path = self.evidence_dir / filename
        with open(path, "w") as f:
            json.dump(record.to_dict(), f, indent=2, default=str)
        record.evidence_file = str(path)
        return path

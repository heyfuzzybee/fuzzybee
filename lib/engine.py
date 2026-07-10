"""Core execution engine: Reason → Act → Verify → gate."""
from __future__ import annotations

import json
import os
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from .decompose import Decomposer, ProblemClassifier, Unit, UnitType
from .gate import EvidenceRecord, GateRunner, GateStatus
from .learn import InstinctLogger
from .memory import JSONLMemoryAdapter, MemoryAdapter
FileMemoryAdapter = JSONLMemoryAdapter  # backwards compat
from .report import ReportGenerator
from .session import SessionDetector
from .sla import SLAEnforcer
from .telemetry import TelemetryLogger, TelemetryTier


class ExecutionEngine:
    """Recursive verify engine: decompose, execute, verify, report."""

    def __init__(
        self,
        evidence_dir: str = "docs/status/execution-gates/",
        memory_adapter: Optional[MemoryAdapter] = None,
    ):
        self.evidence_dir = Path(evidence_dir).expanduser()
        self.evidence_dir.mkdir(parents=True, exist_ok=True)
        self.gate_runner = GateRunner(str(self.evidence_dir))
        self.decomposer = Decomposer()
        self.sla = SLAEnforcer()
        self.report_gen = ReportGenerator()
        self.session = SessionDetector()
        self.telemetry = TelemetryLogger()
        self.learner = InstinctLogger()
        self.memory = memory_adapter or FileMemoryAdapter()
        self._cycle_count = 0

    # ── Health ───────────────────────────────────────────────

    def check_health(self) -> Dict[str, Any]:
        """Verify: gap auditor, 14-skill checker, OMC, git, evidence dir."""
        health = {
            "engine": "healthy",
            "evidence_dir": str(self.evidence_dir),
            "evidence_dir_writable": os.access(self.evidence_dir, os.W_OK),
            "session_kind": self.session.detect_str(),
            "git": self._git_status(),
            "gap_auditor": self._check_script("scripts/memory_gap_auditor_v2.py"),
            "skill_compliance": self._check_script("scripts/check-14-skill-compliance.sh"),
            "omc": self._check_script("scripts/check-omc-compliance.sh"),
        }
        return health

    def _git_status(self) -> Dict[str, Any]:
        try:
            branch = subprocess.run(
                ["git", "branch", "--show-current"],
                capture_output=True, text=True, timeout=5,
            )
            return {
                "available": True,
                "branch": branch.stdout.strip() if branch.returncode == 0 else "unknown",
            }
        except Exception:
            return {"available": False, "branch": "unknown"}

    def _check_script(self, path: str) -> Dict[str, Any]:
        p = Path(path)
        return {
            "exists": p.exists(),
            "path": str(p.resolve()) if p.exists() else path,
        }

    # ── Decomposition ────────────────────────────────────────

    def decompose(self, problem: str, sla_tight: bool = False) -> List[Unit]:
        """Classify problem type, return list of verifiable Unit objects."""
        return self.decomposer.decompose(problem, sla_tight)

    def _classify_problem(self, problem: str):
        """Detect problem type from keywords."""
        return self.decomposer.classifier.classify(problem)

    # ── Execute ────────────────────────────────────────────────

    def execute(self, unit: Unit) -> Dict[str, Any]:
        """Run a unit: Reason → Act → Verify → gate. Enforce SLA."""
        self._cycle_count += 1
        started = datetime.now()
        unit.tool_calls += 1

        # Run the gate
        record = self.gate_runner.run(
            gate_name=unit.task_id,
            command=unit.pass_criteria,
        )
        unit.evidence.append(record)

        if record.status == GateStatus.FAIL:
            unit.gate_failures += 1

        elapsed = (datetime.now() - started).total_seconds()
        unit.wall_clock_s += elapsed

        # SLA check
        violation = self.sla.check(
            tool_calls=unit.tool_calls,
            elapsed_s=unit.wall_clock_s,
            gate_failures=unit.gate_failures,
        )
        sla_violations = [violation] if violation else []

        # Determine final status
        if violation:
            status = GateStatus.BLOCKED
        elif record.status == GateStatus.FAIL:
            status = GateStatus.FAIL
        else:
            status = record.status

        # Build cycle report
        cycle = {
            "cycle_number": self._cycle_count,
            "task_id": unit.task_id,
            "status": status.value,
            "evidence_summary": f"{record.gate_name}: {record.status.value}",
            "next_step": "continue" if status == GateStatus.PASS else "retry or escalate",
            "memory_written": False,
            "wall_clock_s": unit.wall_clock_s,
            "tool_calls": unit.tool_calls,
            "sla_violations": sla_violations,
        }

        # Log learning
        self.learner.log_cycle(
            problem_type="generic",
            status=status.value,
            tool_count=unit.tool_calls,
            duration_ms=int(unit.wall_clock_s * 1000),
        )

        # Persist to memory
        self.memory.write(
            f"cycle-{self._cycle_count}-{unit.task_id}",
            cycle,
        )
        cycle["memory_written"] = True

        return cycle

    # ── Verify ───────────────────────────────────────────────

    def verify(self, unit: Unit) -> GateStatus:
        """Re-run a gate to confirm pass/fail."""
        record = self.gate_runner.run(
            gate_name=f"{unit.task_id}-verify",
            command=unit.pass_criteria,
        )
        unit.evidence.append(record)
        return record.status

    # ── Report ───────────────────────────────────────────────

    def report(self, unit: Unit, cycle: Dict[str, Any]) -> str:
        """Produce structured report with SLA and contract info."""
        evidence_dicts = [ev.to_dict() for ev in unit.evidence]
        return self.report_gen.generate(
            task_id=unit.task_id,
            subject=unit.subject,
            status=cycle["status"],
            evidence=evidence_dicts,
            sla_violations=cycle.get("sla_violations", []),
            wall_clock_s=cycle.get("wall_clock_s", 0.0),
            tool_calls=cycle.get("tool_calls", 0),
            cycle_number=cycle.get("cycle_number", 1),
        )

    # ── Evidence persistence ─────────────────────────────────

    def _write_evidence(self, unit: Unit) -> Path:
        """Write unit evidence as JSON."""
        ts = datetime.now().strftime("%Y%m%d-%H%M%S")
        filename = f"{unit.task_id}-{ts}.json"
        path = self.evidence_dir / filename
        data = {
            "task_id": unit.task_id,
            "subject": unit.subject,
            "evidence": [ev.to_dict() for ev in unit.evidence],
            "timestamp": datetime.now().isoformat(),
        }
        with open(path, "w") as f:
            json.dump(data, f, indent=2, default=str)
        return path

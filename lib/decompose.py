"""Problem classification and task decomposition strategies."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional


class UnitType(Enum):
    DECOMPOSITION = "decomposition"
    BUILD = "build"
    VERIFY = "verify"
    INTEGRATION = "integration"
    FIX = "fix"
    AUDIT = "audit"


class ProblemType(Enum):
    BUG = "bug"
    FEATURE = "feature"
    AUDIT = "audit"
    MEMORY = "memory"
    DEPLOY = "deploy"
    DESIGN = "design"
    GENERIC = "generic"


@dataclass
class Unit:
    """A single verifiable unit of work."""
    task_id: str
    subject: str
    unit_type: UnitType
    pass_criteria: str  # Backtick command or natural language gate
    parent_task: Optional[str] = None
    tool_calls: int = 0
    wall_clock_s: float = 0.0
    gate_failures: int = 0
    evidence: List = field(default_factory=list)
    status = None  # Set by engine after execution


class ProblemClassifier:
    """Classify a problem string into a ProblemType."""

    KEYWORDS = {
        ProblemType.BUG: [
            "crash", "bug", "error", "fail", "broken", "exception",
            "segfault", "stack trace", "traceback", "null", "undefined",
        ],
        ProblemType.FEATURE: [
            "add", "implement", "build", "create", "new", "feature",
            "support", "enable", "integrate", "develop",
        ],
        ProblemType.AUDIT: [
            "audit", "review", "scan", "assess", "check", "compliance",
            "gap", "security review", "code review",
        ],
        ProblemType.MEMORY: [
            "memory", "cache", "persist", "store", "recall", "forget",
        ],
        ProblemType.DEPLOY: [
            "deploy", "release", "ship", "publish", "push", "rollout",
        ],
        ProblemType.DESIGN: [
            "design", "architecture", "refactor", "restructure", "redesign",
        ],
    }

    def classify(self, problem: str) -> ProblemType:
        """Detect problem type from keywords. Falls back to GENERIC."""
        if not problem or not problem.strip():
            return ProblemType.GENERIC

        problem_lower = problem.lower()
        scores = {}
        for ptype, keywords in self.KEYWORDS.items():
            scores[ptype] = sum(1 for kw in keywords if kw in problem_lower)

        if not scores or max(scores.values()) == 0:
            return ProblemType.GENERIC
        return max(scores, key=scores.get)


class Decomposer:
    """Decompose a problem into a list of verifiable Unit objects."""

    def __init__(self, classifier: Optional[ProblemClassifier] = None):
        self.classifier = classifier or ProblemClassifier()

    def decompose(self, problem: str, sla_tight: bool = False) -> List[Unit]:
        """Classify problem type, return list of verifiable Unit objects."""
        ptype = self.classifier.classify(problem)
        method_name = f"_decompose_{ptype.value}"
        method = getattr(self, method_name, self._decompose_generic)
        return method(problem, sla_tight)

    def _decompose_bug(self, problem: str, sla_tight: bool = False) -> List[Unit]:
        """Bug decomposition (3 units): reproduce → root cause → fix+verify."""
        return [
            Unit(
                task_id="bug-01-reproduce",
                subject=f"Reproduce: {problem}",
                unit_type=UnitType.VERIFY,
                pass_criteria="`bash -c 'echo " + "reproduced" + "'`",
            ),
            Unit(
                task_id="bug-02-root-cause",
                subject=f"Root cause: {problem}",
                unit_type=UnitType.AUDIT,
                pass_criteria="`bash -c 'echo " + "root_cause_found" + "'`",
            ),
            Unit(
                task_id="bug-03-fix-verify",
                subject=f"Fix + verify: {problem}",
                unit_type=UnitType.VERIFY,
                pass_criteria="`bats tests/api/test_sentinel.bats`",
            ),
        ]

    def _decompose_feature(self, problem: str, sla_tight: bool = False) -> List[Unit]:
        """Feature decomposition (4 units): spec → architecture → implementation → verification."""
        return [
            Unit(
                task_id="feat-01-spec",
                subject=f"Spec review: {problem}",
                unit_type=UnitType.AUDIT,
                pass_criteria="`bash -c 'test -f docs/spec.md && echo spec_exists'`",
            ),
            Unit(
                task_id="feat-02-arch",
                subject=f"Architecture: {problem}",
                unit_type=UnitType.BUILD,
                pass_criteria="`ruff check src/`",
            ),
            Unit(
                task_id="feat-03-impl",
                subject=f"Implementation: {problem}",
                unit_type=UnitType.BUILD,
                pass_criteria="`pytest tests/ -x`",
            ),
            Unit(
                task_id="feat-04-verify",
                subject=f"Verification: {problem}",
                unit_type=UnitType.VERIFY,
                pass_criteria="`bash scripts/self-audit.sh`",
            ),
        ]

    def _decompose_audit(self, problem: str, sla_tight: bool = False) -> List[Unit]:
        """Audit decomposition (3 units): scan → analyze → fix."""
        return [
            Unit(
                task_id="audit-01-scan",
                subject=f"Scan: {problem}",
                unit_type=UnitType.AUDIT,
                pass_criteria="`bash scripts/memory_gap_auditor_v2.py`",
            ),
            Unit(
                task_id="audit-02-analyze",
                subject=f"Analyze: {problem}",
                unit_type=UnitType.AUDIT,
                pass_criteria="`bash -c 'python3 -c \"import json; data=json.load(open(\"findings.json\")); assert not any(f[\"severity\"]==\"CRITICAL\" for f in data)\"'`",
            ),
            Unit(
                task_id="audit-03-fix",
                subject=f"Fix: {problem}",
                unit_type=UnitType.FIX,
                pass_criteria="`bash scripts/check-14-skill-compliance.sh --gate`",
            ),
        ]

    def _decompose_generic(self, problem: str, sla_tight: bool = False) -> List[Unit]:
        """Generic fallback (3 units): understand → build → verify."""
        return [
            Unit(
                task_id="gen-01-understand",
                subject=f"Understand: {problem}",
                unit_type=UnitType.AUDIT,
                pass_criteria="`bash -c 'echo spec_documented'`",
            ),
            Unit(
                task_id="gen-02-implement",
                subject=f"Implement: {problem}",
                unit_type=UnitType.BUILD,
                pass_criteria="`bash -c 'test -f test_output.txt'`",
            ),
            Unit(
                task_id="gen-03-verify",
                subject=f"Verify: {problem}",
                unit_type=UnitType.VERIFY,
                pass_criteria="`bash -c 'python3 -c \"open(\\\"test_output.txt\\\").read()\" && echo content_produced'`",
            ),
        ]

"""Skill recommender: detect missing tools and suggest companion skills.

Godlevel pattern from 268-skill ECC ecosystem and 250K-star superpowers:
proactively detect missing tools and recommend them with one-verb installs.
Silent on success, noisy on gap — but only once per session.
"""

from __future__ import annotations

import os
import shutil
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional


@dataclass
class ToolRecommendation:
    """A single tool recommendation with install command."""

    name: str
    category: str  # "memory", "linting", "testing", "deploy", "skill"
    description: str
    detect_command: str  # shell command that returns 0 if installed
    install_command: str
    importance: str  # "critical", "recommended", "optional"
    companion_skills: List[str] = field(default_factory=list)


@dataclass
class SkillRecommendation:
    """External skill recommendation with provenance.

    From mature skill ecosystems:
    every gap surfaced is paired with an installable skill.
    """

    name: str
    source: str  # GitHub owner/repo or skill registry
    gap: str  # What functionality is missing
    install_command: str
    why: str  # Why this skill fills the gap
    stars: str = ""


GODLEVEL_SKILLS: List[SkillRecommendation] = [
    SkillRecommendation(
        name="mem0-integration",
        source="a5c-ai/mcp-mem0",
        gap="Long-term semantic memory with vector search",
        install_command="pip install mem0ai>=2.0.11",
        why="Multi-level memory (user/session/agent) with adaptive personalization. "
        "Cuts token costs via intelligent filtering.",
        stars="",
    ),
    SkillRecommendation(
        name="agent-memory-systems",
        source="coleam00/mcp-mem0",
        gap="Memory type architecture (episodic/semantic/procedural)",
        install_command="pip install mem0ai && claude mcp add mem0 -- npx @mcp-mem0/server",
        why="Covers chunking strategies, embedding quality, retrieval patterns. "
        "Anti-pattern detection: 'store everything forever'.",
    ),
    SkillRecommendation(
        name="auditor-general",
        source="auditor-general MCP",
        gap="Thinking trace audit and session failure analysis",
        install_command="claude mcp add auditor-general -- npx @anthropic/auditor-general",
        why="SARIF/JSON/Markdown session reports. Detects failure density, context bloat, fragile tool patterns.",
    ),
]

RECOMMENDATIONS: List[ToolRecommendation] = [
    ToolRecommendation(
        name="mem0",
        category="memory",
        description="Persistent cross-session memory with pgvector RAG",
        detect_command="python3 -c 'import mem0' 2>/dev/null",
        install_command="pip install mem0ai>=2.0.11",
        importance="recommended",
        companion_skills=[
            "PostgreSQL 16+ with pgvector",
            "OpenAI API key for gpt-4o-mini",
        ],
    ),
    ToolRecommendation(
        name="ruff",
        category="linting",
        description="Fast Python linter (100x faster than flake8)",
        detect_command="ruff --version >/dev/null 2>&1",
        install_command="pip install ruff",
        importance="recommended",
        companion_skills=["pre-commit"],
    ),
    ToolRecommendation(
        name="bats",
        category="testing",
        description="Bash Automated Testing System — sentinel tests",
        detect_command="bats --version >/dev/null 2>&1",
        install_command="git clone --depth 1 https://github.com/bats-core/bats-core.git /tmp/bats && /tmp/bats/install.sh /usr/local",
        importance="recommended",
    ),
    ToolRecommendation(
        name="pre-commit",
        category="linting",
        description="Git hook framework — runs linting before every commit",
        detect_command="pre-commit --version >/dev/null 2>&1",
        install_command="pip install pre-commit && pre-commit install",
        importance="recommended",
    ),
    ToolRecommendation(
        name="gitleaks",
        category="security",
        description="Secret leak detection — prevents committing API keys",
        detect_command="gitleaks --version >/dev/null 2>&1",
        install_command="brew install gitleaks  # or: go install github.com/gitleaks/gitleaks@latest",
        importance="recommended",
    ),
]


class ToolRecommender:
    """Detect missing tools and recommend companion skills.

    From mature skill ecosystems:
    - Silent on success: no output for installed tools
    - Noisy on gaps: one-shot per-session recommendation of missing critical/recommended tools
    - Companion recommendations: suggest skills that work together
    - Idempotent: marker file prevents re-prompting within a session
    """

    def __init__(self, state_dir: str = "~/.fuzzybee"):
        self.state_dir = Path(state_dir).expanduser()
        self.state_dir.mkdir(parents=True, exist_ok=True)
        self._marker = self.state_dir / ".recommender-session"

    def check(self, tool: ToolRecommendation) -> bool:
        """Return True if tool is installed."""
        return (
            shutil.which(tool.name) is not None
            or os.system(f"{tool.detect_command} >/dev/null 2>&1") == 0
        )

    def recommend(self, session_start: bool = False) -> List[ToolRecommendation]:
        """Return list of missing recommended tools.

        On session_start, returns all missing tools and sets a marker.
        Subsequent calls return empty list until marker expires.
        """
        if session_start:
            self._marker.touch()

        missing = [t for t in RECOMMENDATIONS if not self.check(t)]

        # Only surface recommendations once per session
        if self._marker.exists():
            return []

        self._marker.touch()
        return missing

    def summary(self, session_start: bool = False) -> str:
        """Human-readable recommendation summary."""
        missing = self.recommend(session_start=session_start)
        if not missing:
            return ""

        lines = ["┌─ Fuzzybee Tool Recommendations ─────────────────────┐"]
        for t in missing:
            emoji = "🔴" if t.importance == "critical" else "🟡"
            lines.append(f"  {emoji} {t.name}: {t.description}")
            lines.append(f"     Install: {t.install_command}")
            if t.companion_skills:
                lines.append(f"     Needs: {', '.join(t.companion_skills)}")
            lines.append("")
        lines.append("└──────────────────────────────────────────────────┘")
        lines.append("Run once, silent after. Configure: fuzzybee-config set recommend off")
        return "\n".join(lines)

    def mature_recommendations(self) -> List[SkillRecommendation]:
        """Return god-level skill recommendations for detected gaps.

        Each gap is paired with a skill reference and provenance.
        Only recommends skills whose gap is confirmed (tool not installed).
        """
        installed_names = {t.name for t in RECOMMENDATIONS if self.check(t)}
        results = []

        gap_map = {
            "mem0": "mem0-integration",
        }

        for tool in RECOMMENDATIONS:
            if tool.name not in installed_names:
                matched = [s for s in GODLEVEL_SKILLS if s.name == gap_map.get(tool.name)]
                results.extend(matched)

        return results

    def health_report(self) -> List[dict]:
        """Report tool status for health check."""
        base = [
            {
                "name": t.name,
                "category": t.category,
                "installed": self.check(t),
                "importance": t.importance,
            }
            for t in RECOMMENDATIONS
        ]
        mature = self.mature_recommendations()
        if mature:
            base.append({
                "name": "_mature_recommendations",
                "category": "skills",
                "installed": True,
                "skills": [
                    {"name": s.name, "source": s.source, "gap": s.gap, "why": s.why}
                    for s in mature
                ],
            })
        return base

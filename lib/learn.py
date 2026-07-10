"""Instinct-based learning: log cycles, decay confidence, cluster patterns.
mem0-backed with JSONL fallback."""
from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional


class InstinctLogger:
    """Log cycle outcomes to mem0 (primary) with JSONL fallback."""

    def __init__(self, log_path: str = "~/.fuzzybee/learnings.jsonl"):
        self.log_path = log_path
        self.path = Path(log_path).expanduser()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._mem0 = None
        self._try_init_mem0()

    def _try_init_mem0(self) -> None:
        try:
            from mem0 import Memory
            self._mem0 = Memory()
        except ImportError:
            self._mem0 = None

    def log_cycle(
        self,
        problem_type: str,
        status: str,
        tool_count: int,
        duration_ms: int,
    ) -> None:
        """Store in mem0 with JSONL fallback."""
        entry = {
            "pattern": f"{problem_type}:{status}",
            "confidence": 1.0,
            "problem_type": problem_type,
            "gate_outcome": status,
            "tool_count": tool_count,
            "duration_ms": duration_ms,
            "timestamp": datetime.now().isoformat(),
        }
        text = json.dumps(entry)
        if self._mem0:
            try:
                self._mem0.add(text, user_id="fuzzybee-agent")
                return
            except Exception:
                pass
        with open(self.path, "a") as f:
            f.write(text + "\n")

    def recall(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Semantic recall from mem0. Empty list on failure."""
        if self._mem0:
            try:
                return self._mem0.search(query, user_id="fuzzybee-agent")[:limit]
            except Exception:
                pass
        if self.path.exists():
            lines = []
            with open(self.path) as f:
                for line in f:
                    if line.strip():
                        lines.append(json.loads(line))
            return lines[-limit:]
        return []

    def confidence_decay(self, days: int = 7) -> None:
        """Decay all JSONL entries by 0.1 per period."""
        if not self.path.exists():
            return
        cutoff = datetime.now() - timedelta(days=days)
        updated = []
        with open(self.path) as f:
            for line in f:
                entry = json.loads(line.strip())
                ts = datetime.fromisoformat(entry["timestamp"])
                weeks_old = (datetime.now() - ts).days // days
                if weeks_old >= 1:
                    entry["confidence"] = max(0.0, entry["confidence"] - 0.1 * weeks_old)
                updated.append(entry)
        with open(self.path, "w") as f:
            for entry in updated:
                f.write(json.dumps(entry) + "\n")

    def cluster_by_pattern(self) -> Dict[str, List[Dict]]:
        """Group learnings by pattern."""
        if not self.path.exists():
            return {}
        clusters: Dict[str, List[Dict]] = {}
        with open(self.path) as f:
            for line in f:
                entry = json.loads(line.strip())
                pattern = entry["pattern"]
                clusters.setdefault(pattern, []).append(entry)
        return clusters

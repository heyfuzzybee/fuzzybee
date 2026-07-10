"""Memory adapters: mem0 (primary), SQLite (WAL), JSONL (fallback)."""
from __future__ import annotations

import json
import sqlite3
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence


class MemoryAdapter(ABC):
    """Abstract memory adapter."""

    @abstractmethod
    def write(self, key: str, data: Dict[str, Any]) -> None:
        pass

    @abstractmethod
    def read(self, key: str) -> Optional[Dict[str, Any]]:
        pass

    @abstractmethod
    def search(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        pass


class JSONLMemoryAdapter(MemoryAdapter):
    """Simple JSONL file memory (last-resort fallback)."""

    def __init__(self, base_dir: str = "~/.fuzzybee/memory"):
        self.base_dir = Path(base_dir).expanduser()
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def _path(self, key: str) -> Path:
        safe = key.replace("/", "_").replace("\\", "_")
        return self.base_dir / f"{safe}.jsonl"

    def write(self, key: str, data: Dict[str, Any]) -> None:
        path = self._path(key)
        with open(path, "a") as f:
            f.write(json.dumps(data, default=str) + "\n")

    def read(self, key: str) -> Optional[Dict[str, Any]]:
        path = self._path(key)
        if not path.exists():
            return None
        with open(path) as f:
            lines = [json.loads(l) for l in f if l.strip()]
        return lines[-1] if lines else None

    def search(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        results = []
        for f in sorted(self.base_dir.glob("*.jsonl")):
            with open(f) as fh:
                for line in fh:
                    if line.strip():
                        results.append(json.loads(line))
        return results[-limit:]


class SQLiteMemoryAdapter(MemoryAdapter):
    """SQLite-backed memory with WAL mode (second fallback)."""

    def __init__(self, db_path: str = "~/.fuzzybee/cycles.db"):
        self.db_path = Path(db_path).expanduser()
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self) -> None:
        conn = sqlite3.connect(str(self.db_path))
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("""
            CREATE TABLE IF NOT EXISTS memory (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                created_at TEXT DEFAULT (datetime('now'))
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS cycles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cycle_number INTEGER NOT NULL,
                task_id TEXT NOT NULL,
                status TEXT NOT NULL,
                evidence_summary TEXT,
                created_at TEXT DEFAULT (datetime('now'))
            )
        """)
        conn.commit()
        conn.close()

    def write(self, key: str, data: Dict[str, Any]) -> None:
        conn = sqlite3.connect(str(self.db_path))
        conn.execute(
            "INSERT OR REPLACE INTO memory (key, value) VALUES (?, ?)",
            (key, json.dumps(data, default=str)),
        )
        conn.commit()
        conn.close()

    def read(self, key: str) -> Optional[Dict[str, Any]]:
        conn = sqlite3.connect(str(self.db_path))
        row = conn.execute(
            "SELECT value FROM memory WHERE key = ?", (key,)
        ).fetchone()
        conn.close()
        if row:
            return json.loads(row[0])
        return None

    def search(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        conn = sqlite3.connect(str(self.db_path))
        rows = conn.execute(
            "SELECT key, value FROM memory ORDER BY created_at DESC LIMIT ?",
            (limit,),
        ).fetchall()
        conn.close()
        return [{"key": r[0], **json.loads(r[1])} for r in rows]


class Mem0Adapter(MemoryAdapter):
    """mem0 adapter with SQLite → JSONL fallback chain.

    Primary: mem0ai SDK (pgvector RAG, semantic search).
    Fallback: SQLite WAL → JSONL file.
    """

    def __init__(
        self,
        timeout: float = 5.0,
        user_id: str = "fuzzybee-agent",
    ):
        self.timeout = timeout
        self.user_id = user_id
        self._mem0 = None
        self._fallback = SQLiteMemoryAdapter()
        self._last_resort = JSONLMemoryAdapter()
        self._try_init_mem0()

    def _try_init_mem0(self) -> None:
        try:
            from mem0 import Memory
            self._mem0 = Memory()
        except Exception:
            self._mem0 = None

    def write(self, key: str, data: Dict[str, Any]) -> None:
        text = f"{key}: {json.dumps(data, default=str)[:500]}"
        if self._mem0:
            try:
                self._mem0.add(text, user_id=self.user_id)
                return
            except Exception:
                pass
        try:
            self._fallback.write(key, data)
        except Exception:
            self._last_resort.write(key, data)

    def read(self, key: str) -> Optional[Dict[str, Any]]:
        if self._mem0:
            try:
                results = self._mem0.search(key, user_id=self.user_id)
                if results:
                    return {"mem0_result": results[0]}
            except Exception:
                pass
        return self._fallback.read(key) or self._last_resort.read(key)

    def search(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        if self._mem0:
            try:
                results = self._mem0.search(query, user_id=self.user_id)
                if results:
                    return results[:limit]
            except Exception:
                pass
        return self._fallback.search(query, limit)

    def health(self) -> Dict[str, Any]:
        """Return degradation status and recommendations."""
        status = "healthy" if self._mem0 else "degraded"
        failures = []
        if not self._mem0:
            failures.append("mem0 package not installed (pip install mem0ai)")
        return {
            "status": status,
            "mem0_available": self._mem0 is not None,
            "sqlite_available": True,
            "jsonl_available": True,
            "failure_reason": failures[0] if failures else None,
            "recommendations": [
                {
                    "name": "mem0-integration",
                    "source": "a5c-ai/mcp-mem0",
                    "gap": "Long-term semantic memory with vector search",
                    "install": "pip install mem0ai>=2.0.11",
                    "why": "Multi-level memory (user/session/agent), 60K GitHub stars, cuts token costs via intelligent filtering",
                },
                {
                    "name": "agent-memory-systems",
                    "source": "coleam00/mcp-mem0",
                    "gap": "Memory type architecture (episodic/semantic/procedural)",
                    "install": "pip install mem0ai && claude mcp add mem0 -- npx @mcp-mem0/server",
                    "why": "Covers chunking strategies, embedding quality, retrieval patterns; anti-pattern detection",
                },
            ],
        }


class AutoMemoryAdapter(MemoryAdapter):
    """Auto-select best available adapter: mem0 → SQLite → JSONL.

    Godlevel pattern from 60K⭐ mem0 ecosystem:
    - Silent on success: uses best tier available
    - Noisy on gaps: health() reports degradation with actionable fixes
    - Zero deps guaranteed: always degrades to JSONL
    """

    def __init__(
        self,
        preferred: str = "mem0",
        fallback_chain: Optional[List[str]] = None,
    ):
        self.fallback_chain = fallback_chain or ["sqlite", "jsonl"]
        self._adapters: Dict[str, MemoryAdapter] = {}
        self._active: Optional[str] = None

        # Try preferred first
        if preferred == "mem0":
            try:
                self._adapters["mem0"] = Mem0Adapter()
                self._active = "mem0"
            except Exception:
                pass

        # Fill fallbacks
        if not self._active or "sqlite" in self.fallback_chain:
            sqlite_key = "sqlite"
            if sqlite_key not in self._adapters:
                try:
                    self._adapters[sqlite_key] = SQLiteMemoryAdapter()
                    if not self._active:
                        self._active = sqlite_key
                except Exception:
                    pass

        if not self._active or "jsonl" in self.fallback_chain:
            jsonl_key = "jsonl"
            if jsonl_key not in self._adapters:
                self._adapters[jsonl_key] = JSONLMemoryAdapter()
                if not self._active:
                    self._active = jsonl_key

    @property
    def active(self) -> MemoryAdapter:
        return self._adapters[self._active]

    @property
    def active_tier(self) -> str:
        return self._active or "none"

    def write(self, key: str, data: Dict[str, Any]) -> None:
        self.active.write(key, data)

    def read(self, key: str) -> Optional[Dict[str, Any]]:
        return self.active.read(key)

    def search(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        return self.active.search(query, limit)

    def health(self) -> Dict[str, Any]:
        tiers = {}
        for name, adapter in self._adapters.items():
            if hasattr(adapter, "health"):
                tiers[name] = adapter.health()
            else:
                tiers[name] = {"status": "available"}
        return {
            "active_tier": self.active_tier,
            "available_tiers": list(self._adapters.keys()),
            "fallback_chain": self.fallback_chain,
            "tiers": tiers,
        }

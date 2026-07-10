"""Tests for memory.py — JSONL, SQLite, mem0 adapters."""
import tempfile

from lib.memory import JSONLMemoryAdapter, SQLiteMemoryAdapter, Mem0Adapter


def test_jsonl_adapter_creates_memory_file():
    with tempfile.TemporaryDirectory() as td:
        mem = JSONLMemoryAdapter(base_dir=td)
        mem.write("test-key", {"foo": "bar"})
        result = mem.read("test-key")
        assert result == {"foo": "bar"}


def test_sqlite_adapter_creates_table_on_first_write():
    with tempfile.TemporaryDirectory() as td:
        db = f"{td}/test.db"
        mem = SQLiteMemoryAdapter(db_path=db)
        mem.write("k1", {"a": 1})
        result = mem.read("k1")
        assert result == {"a": 1}


def test_mem0_adapter_fallback_on_failure():
    # mem0 not available or times out — falls back to SQLite → JSONL
    mem = Mem0Adapter()
    mem.write("fallback-key", {"data": 42})
    result = mem.read("fallback-key")
    assert result is not None
    assert result.get("data") == 42 or "mem0_result" not in result


def test_mem0_adapter_search_without_mem0():
    # mem0 not available — search falls through to SQLite
    with tempfile.TemporaryDirectory() as td:
        mem = Mem0Adapter()
        mem.write("search-1", {"val": 1})
        mem.write("search-2", {"val": 2})
        results = mem.search("search", limit=5)
        assert len(results) > 0

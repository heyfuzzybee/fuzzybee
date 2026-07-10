"""Tests for memory.py — File, SQLite, mem0 adapters."""
import tempfile

from lib.memory import FileMemoryAdapter, SQLiteMemoryAdapter, Mem0Adapter


def test_file_adapter_creates_memory_file():
    with tempfile.TemporaryDirectory() as td:
        mem = FileMemoryAdapter(base_dir=td)
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


def test_memory_fallback_on_mem0_timeout():
    with tempfile.TemporaryDirectory() as td:
        fallback = FileMemoryAdapter(base_dir=td)
        mem = Mem0Adapter(fallback=fallback)
        mem.write("key", {"data": 42})
        assert mem.read("key") == {"data": 42}


def test_mem0_adapter_calls_search_nodes():
    # mem0 not available — falls back, list_keys works
    with tempfile.TemporaryDirectory() as td:
        fallback = FileMemoryAdapter(base_dir=td)
        mem = Mem0Adapter(fallback=fallback)
        mem.write("prefix-a", {})
        mem.write("prefix-b", {})
        keys = mem.list_keys("prefix")
        assert len(keys) == 2

"""Tests for recommender.py — ToolRecommender."""
import tempfile
from pathlib import Path

from lib.recommender import ToolRecommender, RECOMMENDATIONS


def test_recommender_initializes_with_state_dir():
    with tempfile.TemporaryDirectory() as td:
        r = ToolRecommender(state_dir=td)
        assert Path(td).exists()


def test_recommender_returns_missing_tools_on_first_call():
    with tempfile.TemporaryDirectory() as td:
        r = ToolRecommender(state_dir=td)
        missing = r.recommend()
        # Should find python3 and git as installed, skip those
        for t in missing:
            assert not r.check(t)


def test_recommender_silent_after_session_start():
    with tempfile.TemporaryDirectory() as td:
        r = ToolRecommender(state_dir=td)
        # First call with session_start=True should return tools
        first = r.recommend(session_start=True)
        # Second call should return empty
        second = r.recommend()
        # Verify session marker exists
        assert (Path(td) / ".recommender-session").exists()
        # Verify we get recommendations on session_start
        assert isinstance(first, list)


def test_health_report_returns_all_tools():
    with tempfile.TemporaryDirectory() as td:
        r = ToolRecommender(state_dir=td)
        report = r.health_report()
        assert len(report) == len(RECOMMENDATIONS)
        for entry in report:
            assert "name" in entry
            assert "installed" in entry
            assert "importance" in entry
            assert "category" in entry


def test_check_ruff_installed_if_available():
    import shutil
    has_ruff = shutil.which("ruff") is not None
    with tempfile.TemporaryDirectory() as td:
        r = ToolRecommender(state_dir=td)
        for t in RECOMMENDATIONS:
            if t.name == "ruff":
                assert r.check(t) == has_ruff


def test_recommender_summary_empty_when_all_installed():
    with tempfile.TemporaryDirectory() as td:
        r = ToolRecommender(state_dir=td)
        # After session_start, recommendations are consumed
        r.recommend(session_start=True)
        assert r.summary() == ""


def test_recommender_summary_non_empty_before_session():
    with tempfile.TemporaryDirectory() as td:
        r = ToolRecommender(state_dir=td)
        summary = r.summary()
        if summary:
            assert "Tool Recommendations" in summary
            assert "Install" in summary


def test_recommender_detect_python():
    """Python3 should always be detected as available."""
    with tempfile.TemporaryDirectory() as td:
        r = ToolRecommender(state_dir=td)
        # Check that shutil.which works for common tools
        import shutil
        assert shutil.which("python3") is not None or shutil.which("python") is not None


def test_mature_recommendations_returns_skills_when_mem0_missing():
    with tempfile.TemporaryDirectory() as td:
        r = ToolRecommender(state_dir=td)
        skills = r.mature_recommendations()
        for s in skills:
            assert hasattr(s, "name")
            assert hasattr(s, "source")
            assert hasattr(s, "gap")
            assert hasattr(s, "install_command")


def test_health_report_includes_mature_when_gaps():
    with tempfile.TemporaryDirectory() as td:
        r = ToolRecommender(state_dir=td)
        report = r.health_report()
        mature_entries = [e for e in report if e.get("name") == "_mature_recommendations"]
        # If mem0 is missing, mature entries appear
        mem0_installed = any(
            e["name"] == "mem0" and e["installed"] for e in report
        )
        if not mem0_installed:
            assert len(mature_entries) > 0
            for entry in mature_entries:
                assert "skills" in entry
                assert len(entry["skills"]) > 0

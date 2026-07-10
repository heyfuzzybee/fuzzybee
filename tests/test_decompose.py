"""Tests for decompose.py — ProblemClassifier, Decomposer."""
import pytest

from lib.decompose import Decomposer, ProblemClassifier, ProblemType, UnitType


def test_classify_bug_from_keywords():
    c = ProblemClassifier()
    assert c.classify("crash when user submits form") == ProblemType.BUG
    assert c.classify("null pointer exception in login") == ProblemType.BUG


def test_classify_feature_from_keywords():
    c = ProblemClassifier()
    assert c.classify("add login page to app") == ProblemType.FEATURE
    assert c.classify("implement OAuth support") == ProblemType.FEATURE


def test_classify_audit_from_keywords():
    c = ProblemClassifier()
    assert c.classify("audit memory architecture") == ProblemType.AUDIT


def test_decompose_bug_returns_3_units():
    d = Decomposer()
    units = d.decompose("crash on empty submit")
    assert len(units) == 3
    assert all(hasattr(u, "task_id") for u in units)
    assert "bats" in units[2].pass_criteria


def test_decompose_feature_returns_4_units():
    d = Decomposer()
    units = d.decompose("add user dashboard")
    assert len(units) == 4


def test_decompose_bug_no_keyword_falls_back_to_generic():
    d = Decomposer()
    units = d.decompose("xyz123 something unknown")
    assert len(units) == 3  # generic fallback: understand → implement → verify


def test_decompose_empty_string_returns_generic():
    d = Decomposer()
    units = d.decompose("")
    assert len(units) == 3
    assert units[0].unit_type == UnitType.AUDIT

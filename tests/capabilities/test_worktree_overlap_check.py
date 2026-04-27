from __future__ import annotations

import json
from pathlib import Path

import pytest

from orca.core.errors import ErrorKind
from orca.capabilities.worktree_overlap_check import (
    WorktreeOverlapInput,
    WorktreeInfo,
    worktree_overlap_check,
)


def _wt(path: str, *, claimed: list[str], branch: str = "feat", feature_id: str = "f") -> WorktreeInfo:
    return WorktreeInfo(path=path, branch=branch, feature_id=feature_id, claimed_paths=claimed)


def test_no_conflicts_safe_true():
    inp = WorktreeOverlapInput(worktrees=[
        _wt("/a", claimed=["src/foo/"]),
        _wt("/b", claimed=["src/bar/"]),
    ])
    result = worktree_overlap_check(inp)
    assert result.ok
    assert result.value["safe"] is True
    assert result.value["conflicts"] == []
    assert result.value["proposed_overlaps"] == []


def test_exact_path_conflict_detected():
    inp = WorktreeOverlapInput(worktrees=[
        _wt("/a", claimed=["src/foo.py"]),
        _wt("/b", claimed=["src/foo.py"]),
    ])
    result = worktree_overlap_check(inp)
    assert result.ok
    assert result.value["safe"] is False
    assert len(result.value["conflicts"]) == 1
    assert set(result.value["conflicts"][0]["worktrees"]) == {"/a", "/b"}


def test_directory_prefix_conflict_detected():
    inp = WorktreeOverlapInput(worktrees=[
        _wt("/a", claimed=["src/foo/"]),
        _wt("/b", claimed=["src/foo/bar.py"]),
    ])
    result = worktree_overlap_check(inp)
    assert result.ok
    assert result.value["safe"] is False
    assert len(result.value["conflicts"]) == 1


def test_directory_prefix_conflict_reverse_order():
    """Containment must be detected regardless of which side is the prefix."""
    inp = WorktreeOverlapInput(worktrees=[
        _wt("/a", claimed=["src/foo/bar.py"]),
        _wt("/b", claimed=["src/foo/"]),
    ])
    result = worktree_overlap_check(inp)
    assert result.ok
    assert result.value["safe"] is False


def test_proposed_overlap_detected():
    inp = WorktreeOverlapInput(
        worktrees=[_wt("/a", claimed=["src/foo/"])],
        proposed_writes=["src/foo/bar.py"],
    )
    result = worktree_overlap_check(inp)
    assert result.ok
    assert result.value["safe"] is False
    assert len(result.value["proposed_overlaps"]) == 1
    assert result.value["proposed_overlaps"][0]["blocked_by"] == "/a"


def test_proposed_writes_with_no_conflict_safe():
    inp = WorktreeOverlapInput(
        worktrees=[_wt("/a", claimed=["src/foo/"])],
        proposed_writes=["src/bar/baz.py"],
    )
    result = worktree_overlap_check(inp)
    assert result.ok
    assert result.value["safe"] is True


def test_empty_worktrees_safe():
    inp = WorktreeOverlapInput(worktrees=[])
    result = worktree_overlap_check(inp)
    assert result.ok
    assert result.value["safe"] is True


def test_single_worktree_no_self_conflict():
    """A single worktree with two non-overlapping claimed paths is safe."""
    inp = WorktreeOverlapInput(worktrees=[
        _wt("/a", claimed=["src/foo/", "tests/"]),
    ])
    result = worktree_overlap_check(inp)
    assert result.ok
    assert result.value["safe"] is True


def test_invalid_path_in_claimed_returns_input_invalid():
    inp = WorktreeOverlapInput(worktrees=[_wt("/a", claimed=[""])])
    result = worktree_overlap_check(inp)
    assert not result.ok
    assert result.error.kind == ErrorKind.INPUT_INVALID


def test_three_way_conflict_pairwise():
    """When three worktrees claim the same path, we report each pair."""
    inp = WorktreeOverlapInput(worktrees=[
        _wt("/a", claimed=["src/foo.py"]),
        _wt("/b", claimed=["src/foo.py"]),
        _wt("/c", claimed=["src/foo.py"]),
    ])
    result = worktree_overlap_check(inp)
    assert result.ok
    assert result.value["safe"] is False
    # Three pairs: (a,b), (a,c), (b,c)
    assert len(result.value["conflicts"]) == 3


def test_output_validates_against_schema(tmp_path):
    pytest.importorskip("jsonschema")
    import jsonschema

    schema_path = Path(__file__).resolve().parents[2] / "docs" / "capabilities" / "worktree-overlap-check" / "schema" / "output.json"
    schema = json.loads(schema_path.read_text())

    inp = WorktreeOverlapInput(worktrees=[
        _wt("/a", claimed=["src/foo.py"]),
        _wt("/b", claimed=["src/foo.py"]),
    ])
    result = worktree_overlap_check(inp)
    assert result.ok
    jsonschema.validate(result.value, schema)

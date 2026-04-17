"""Tests for 017 Matriarch completion gates."""
from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from speckit_orca import matriarch
from speckit_orca.session import SessionScope, SESSIONS_DIRNAME, start_session


def _run(*args: str, cwd: Path) -> None:
    # Disable hooks so operator's global conventional-commits / gpg-sign
    # config doesn't run inside ephemeral test repos.
    full = ("git", "-c", "core.hooksPath=/dev/null", *args[1:]) if args[0] == "git" else args
    subprocess.run(full, cwd=cwd, check=True, capture_output=True)


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    """A bootstrapped spec-kit project with minimal structure + initial commit."""
    _run("git", "init", "-q", cwd=tmp_path)
    _run("git", "config", "user.email", "t@test", cwd=tmp_path)
    _run("git", "config", "user.name", "Test", cwd=tmp_path)
    _run("git", "config", "commit.gpgsign", "false", cwd=tmp_path)
    (tmp_path / ".specify").mkdir()
    (tmp_path / ".specify" / "orca").mkdir()
    (tmp_path / "specs").mkdir()
    feature_dir = tmp_path / "specs" / "888-test-feature"
    feature_dir.mkdir()
    (feature_dir / "spec.md").write_text("# Test Feature\n")
    (tmp_path / "README.md").write_text("root\n")
    _run("git", "add", "-A", cwd=tmp_path)
    _run("git", "commit", "-q", "-m", "chore: initial", cwd=tmp_path)
    return tmp_path


def _head_sha(repo: Path) -> str:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def _make_commit(repo: Path, msg: str = "work") -> str:
    (repo / f"file-{msg}.txt").write_text(msg)
    _run("git", "add", "-A", cwd=repo)
    _run("git", "commit", "-q", "-m", f"feat: {msg}", cwd=repo)
    return _head_sha(repo)


# ─── register_lane: session conflict gate ────────────────────────────────


def test_register_rejects_when_another_session_holds_lane(repo: Path):
    # Start a session holding the lane
    start_session(
        agent="claude",
        repo_root=repo,
        scope=SessionScope(lane_id="888-test-feature"),
    )
    with pytest.raises(matriarch.MatriarchError) as exc:
        matriarch.register_lane("888-test-feature", repo_root=repo)
    assert "LANE_SCOPE_BUSY" in str(exc.value)


def test_register_succeeds_when_no_conflicting_session(repo: Path):
    record = matriarch.register_lane("888-test-feature", repo_root=repo)
    assert record.lane_id == "888-test-feature"


def test_register_succeeds_when_only_conflict_is_stale(repo: Path):
    import json
    from datetime import datetime, timedelta, timezone

    s = start_session(
        agent="claude",
        repo_root=repo,
        scope=SessionScope(lane_id="888-test-feature"),
    )
    # Age the heartbeat past TTL
    session_file = repo / SESSIONS_DIRNAME / f"{s.session_id}.json"
    data = json.loads(session_file.read_text())
    data["last_heartbeat"] = (
        datetime.now(timezone.utc) - timedelta(seconds=600)
    ).isoformat()
    session_file.write_text(json.dumps(data))

    # Stale session reaped on next access — registration succeeds
    record = matriarch.register_lane("888-test-feature", repo_root=repo)
    assert record.lane_id == "888-test-feature"


# ─── register_lane: worktree escape gate ─────────────────────────────────


def test_register_rejects_worktree_outside_managed_root(repo: Path):
    rogue = repo.parent / "rogue-worktree"
    rogue.mkdir()
    with pytest.raises(matriarch.MatriarchError) as exc:
        matriarch.register_lane(
            "888-test-feature", repo_root=repo, worktree_path=str(rogue)
        )
    assert "LANE_WORKTREE_ESCAPED" in str(exc.value)


def test_register_accepts_worktree_under_managed_root(repo: Path):
    managed = repo / ".specify" / "orca" / "worktrees" / "888-test-feature"
    managed.mkdir(parents=True)
    record = matriarch.register_lane(
        "888-test-feature", repo_root=repo, worktree_path=str(managed)
    )
    assert record.worktree_path is not None


def test_register_accepts_no_worktree_path(repo: Path):
    """An unset worktree_path is treated as 'at repo root' and allowed."""
    record = matriarch.register_lane(
        "888-test-feature", repo_root=repo, worktree_path=None
    )
    assert record.lane_id == "888-test-feature"


# ─── register_lane: captures HEAD SHA ────────────────────────────────────


def test_register_records_head_sha(repo: Path):
    expected = _head_sha(repo)
    record = matriarch.register_lane("888-test-feature", repo_root=repo)
    assert record.registered_at_sha == expected


# ─── mark_lane_complete: all 4 gates ─────────────────────────────────────


def test_complete_rejects_no_commits(repo: Path):
    matriarch.register_lane("888-test-feature", repo_root=repo)
    # No commits made
    with pytest.raises(matriarch.MatriarchError) as exc:
        matriarch.mark_lane_complete("888-test-feature", repo_root=repo)
    assert "LANE_NO_COMMITS" in str(exc.value)


def test_complete_rejects_missing_review_code(repo: Path):
    matriarch.register_lane("888-test-feature", repo_root=repo)
    _make_commit(repo, "implement")
    # No review-code.md yet
    with pytest.raises(matriarch.MatriarchError) as exc:
        matriarch.mark_lane_complete("888-test-feature", repo_root=repo)
    assert "LANE_REVIEW_MISSING" in str(exc.value)


def test_complete_succeeds_with_commit_and_review(repo: Path):
    matriarch.register_lane("888-test-feature", repo_root=repo)
    _make_commit(repo, "implement")
    (repo / "specs" / "888-test-feature" / "review-code.md").write_text(
        "# Review\npass\n"
    )
    final = _head_sha(repo)
    record = matriarch.mark_lane_complete("888-test-feature", repo_root=repo)
    assert record.lifecycle_state == "completed"
    assert record.final_commit_sha == final


def test_complete_rejects_when_already_complete(repo: Path):
    matriarch.register_lane("888-test-feature", repo_root=repo)
    _make_commit(repo, "implement")
    (repo / "specs" / "888-test-feature" / "review-code.md").write_text("ok\n")
    matriarch.mark_lane_complete("888-test-feature", repo_root=repo)
    with pytest.raises(matriarch.MatriarchError) as exc:
        matriarch.mark_lane_complete("888-test-feature", repo_root=repo)
    assert "LANE_ALREADY_COMPLETE" in str(exc.value)


def test_complete_rejects_when_worktree_escaped_post_register(repo: Path, tmp_path: Path):
    """If the worktree got moved out of managed root after registration,
    completion must still refuse."""
    # Register with a managed worktree, then hack the record to escape
    managed = repo / ".specify" / "orca" / "worktrees" / "888-test-feature"
    managed.mkdir(parents=True)
    matriarch.register_lane(
        "888-test-feature", repo_root=repo, worktree_path=str(managed)
    )
    # Manually corrupt the lane record's worktree_path to something outside
    from speckit_orca.matriarch import MatriarchPaths, _load_lane, _commit_lane_record
    paths = MatriarchPaths(repo)
    record = _load_lane(paths, "888-test-feature")
    rogue = repo.parent / "escaped"
    rogue.mkdir()
    record.worktree_path = str(rogue)
    _commit_lane_record(paths, record, expected_revision=record.registry_revision)

    _make_commit(repo, "work")
    (repo / "specs" / "888-test-feature" / "review-code.md").write_text("ok\n")
    with pytest.raises(matriarch.MatriarchError) as exc:
        matriarch.mark_lane_complete("888-test-feature", repo_root=repo)
    assert "LANE_WORKTREE_ESCAPED" in str(exc.value)


# ─── mark_lane_complete: legacy compatibility ────────────────────────────


def test_complete_propagates_completed_state_into_status_derivation(repo: Path):
    """After ``mark_lane_complete`` the derived effective_state must be
    ``completed``, not regress to ``active``/``review_ready``/``registered``.
    Regression for PR #58 (CodeRabbit)."""
    matriarch.register_lane("888-test-feature", repo_root=repo)
    _make_commit(repo, "work")
    (repo / "specs" / "888-test-feature" / "review-code.md").write_text("ok\n")
    matriarch.mark_lane_complete("888-test-feature", repo_root=repo)
    summary = matriarch.summarize_lane("888-test-feature", repo_root=repo)
    assert summary["effective_state"] == "completed"
    overall = matriarch.overall_status(repo_root=repo)
    assert overall["counts"]["completed"] == 1


def test_register_fails_when_head_unresolvable(tmp_path: Path):
    """Regression for PR #58 (CodeRabbit/Copilot Critical): if HEAD
    cannot be resolved, ``register_lane`` must raise rather than
    silently persisting ``registered_at_sha=None`` (which would later
    masquerade as a legacy record and bypass the commit-diff gate)."""
    # tmp_path is NOT a git repo
    root = tmp_path / "no-git"
    (root / ".specify").mkdir(parents=True)
    (root / "specs" / "888-test-feature").mkdir(parents=True)
    (root / "specs" / "888-test-feature" / "spec.md").write_text("# X\n")
    with pytest.raises(matriarch.MatriarchError) as exc:
        matriarch.register_lane("888-test-feature", repo_root=root)
    assert "LANE_REGISTRATION_HEAD_UNRESOLVED" in str(exc.value)


def test_complete_rejects_forged_final_commit_sha(repo: Path):
    """Regression for PR #58 (Copilot): a caller must not be able to
    bypass LANE_NO_COMMITS by passing an arbitrary final_commit_sha."""
    matriarch.register_lane("888-test-feature", repo_root=repo)
    # No new commits since registration.
    (repo / "specs" / "888-test-feature" / "review-code.md").write_text("ok\n")
    forged = "deadbeef" * 5  # 40-char fake SHA
    with pytest.raises(matriarch.MatriarchError) as exc:
        matriarch.mark_lane_complete(
            "888-test-feature", repo_root=repo, final_commit_sha=forged
        )
    assert "LANE_FINAL_SHA_MISMATCH" in str(exc.value)


def test_complete_legacy_record_skips_commit_gate(repo: Path):
    """Legacy LaneRecords (pre-017) have registered_at_sha=None. The commit
    gate should be skipped with a noted warning, not crash."""
    matriarch.register_lane("888-test-feature", repo_root=repo)
    from speckit_orca.matriarch import MatriarchPaths, _load_lane, _commit_lane_record
    paths = MatriarchPaths(repo)
    record = _load_lane(paths, "888-test-feature")
    # Simulate a legacy record
    record.registered_at_sha = None
    _commit_lane_record(paths, record, expected_revision=record.registry_revision)

    # No new commits, no review yet — review gate should still fire
    (repo / "specs" / "888-test-feature" / "review-code.md").write_text("ok\n")
    # Commit gate is skipped; review gate passes; complete succeeds
    result = matriarch.mark_lane_complete("888-test-feature", repo_root=repo)
    assert result.lifecycle_state == "completed"
    assert "commit-diff gate skipped" in result.notes

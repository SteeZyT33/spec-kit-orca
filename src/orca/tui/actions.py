"""Subprocess wrappers + filesystem probes used by collect_fleet.

Phase 2 ships only the read-only probes (tmux_alive, branch_merged,
last_event, last_setup_failed). Mutating actions land in Phase 4.
"""
from __future__ import annotations

import json
import os
import shlex
import subprocess
from dataclasses import dataclass
from pathlib import Path

# Tail-read cap for events.jsonl. Reading the whole file on every TUI refresh
# is O(file_size) and stalls on long-lived repos with months of history.
# 256KB ≈ 3-4k recent events — enough to cover active lanes. Ancient events
# from zombie lanes are dominated by newer ones anyway; derive_state falls
# back to idle/stale from sidecar data when event signals are absent.
# Override via ORCA_EVENT_INDEX_BYTE_CAP env var (int, bytes) if needed.
EVENT_INDEX_BYTE_CAP: int = int(
    os.environ.get("ORCA_EVENT_INDEX_BYTE_CAP", 262144)
)


def tmux_alive(session: str) -> bool:
    """True if `tmux has-session -t <session>` succeeds."""
    try:
        result = subprocess.run(
            ["tmux", "has-session", "-t", session],
            capture_output=True, timeout=2.0,
        )
        return result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


def branch_merged(repo_root: Path, branch: str, base: str) -> bool:
    """True if `branch` is reachable from `base` AND has >=1 commit beyond it.

    A 0-commits-ahead branch is technically reachable from base (it IS base)
    but isn't 'merged work needing cleanup' — it's just empty. Requiring
    >=1 ahead commit avoids the brand-new-branch circle false positive.
    """
    try:
        out = subprocess.run(
            ["git", "-C", str(repo_root), "branch", "--merged", base,
             "--format", "%(refname:short)"],
            capture_output=True, text=True, timeout=5.0,
        )
        if out.returncode != 0:
            return False
        merged_set = {ln.strip().lstrip("* ") for ln in out.stdout.splitlines()}
        if branch not in merged_set:
            return False
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False

    try:
        ahead = subprocess.run(
            ["git", "-C", str(repo_root), "rev-list", "--count",
             f"{base}..{branch}"],
            capture_output=True, text=True, timeout=5.0,
        )
        if ahead.returncode != 0:
            return False
        return int(ahead.stdout.strip() or "0") >= 1
    except (FileNotFoundError, subprocess.TimeoutExpired, ValueError):
        return False


def build_event_index(repo_root: Path) -> dict[str, dict[str, str | None]]:
    """Return per-lane state derived from events.jsonl. Tail-reads the
    last EVENT_INDEX_BYTE_CAP bytes to bound work on long-lived repos.

    Result: {lane_id: {"last_event": str|None, "last_setup": str|None}}

    Callers that need O(1) per-lane lookups should call this once per
    refresh instead of calling last_event/last_setup_failed per lane.
    """
    path = repo_root / ".orca" / "worktrees" / "events.jsonl"
    if not path.exists():
        return {}

    out: dict[str, dict[str, str | None]] = {}
    file_size = path.stat().st_size

    with path.open("rb") as fh:
        if file_size > EVENT_INDEX_BYTE_CAP:
            # Seek to last CAP bytes; advance past the partial line at the
            # boundary so we don't try to parse a truncated JSON object.
            fh.seek(file_size - EVENT_INDEX_BYTE_CAP)
            fh.readline()  # discard partial line at the seek boundary
        for raw in fh:
            try:
                entry = json.loads(raw)
            except json.JSONDecodeError:
                continue
            lane = entry.get("lane_id")
            if not lane:
                continue
            evt = entry.get("event", "")
            slot = out.setdefault(lane, {"last_event": None, "last_setup": None})
            slot["last_event"] = evt
            if evt.startswith("setup."):
                slot["last_setup"] = evt
    return out


def last_event(repo_root: Path, lane_id: str) -> str | None:
    """Most recent event type for `lane_id` from .orca/worktrees/events.jsonl.
    Returns None if no events for this lane.

    NOTE: This re-reads the full events.jsonl on every call — O(E) per lane.
    Use build_event_index() for batch lookups across many lanes.
    """
    path = repo_root / ".orca" / "worktrees" / "events.jsonl"
    if not path.exists():
        return None
    found: str | None = None
    with path.open() as fh:
        for line in fh:
            try:
                entry = json.loads(line)
            except json.JSONDecodeError:
                continue
            if entry.get("lane_id") == lane_id:
                found = entry.get("event")
    return found


def last_setup_failed(repo_root: Path, lane_id: str) -> bool:
    """True if the most recent setup.* event for the lane was a .failed.

    NOTE: This re-reads the full events.jsonl on every call — O(E) per lane.
    Use build_event_index() for batch lookups across many lanes.
    """
    path = repo_root / ".orca" / "worktrees" / "events.jsonl"
    if not path.exists():
        return False
    last_setup: str | None = None
    with path.open() as fh:
        for line in fh:
            try:
                entry = json.loads(line)
            except json.JSONDecodeError:
                continue
            if entry.get("lane_id") != lane_id:
                continue
            evt = entry.get("event", "")
            if evt.startswith("setup."):
                last_setup = evt
    return bool(last_setup and last_setup.endswith(".failed"))


@dataclass(frozen=True)
class ActionResult:
    rc: int
    stdout: str
    stderr: str


def close_lane(repo_root: Path, *, branch: str, force: bool = True) -> ActionResult:
    cmd = ["orca-cli", "wt", "rm", "--branch", branch]
    if force:
        cmd.append("--force")
    out = subprocess.run(cmd, cwd=str(repo_root), capture_output=True,
                         text=True, timeout=30)
    return ActionResult(out.returncode, out.stdout, out.stderr)


def new_lane(
    repo_root: Path, *, feature: str, agent: str = "claude",
    from_branch: str | None = None,
) -> ActionResult:
    cmd = ["orca-cli", "wt", "new", "--feature", feature, "--agent", agent]
    if from_branch:
        cmd += ["--from", from_branch]
    out = subprocess.run(cmd, cwd=str(repo_root), capture_output=True,
                         text=True, timeout=120)
    return ActionResult(out.returncode, out.stdout, out.stderr)


def doctor(repo_root: Path) -> ActionResult:
    cmd = ["orca-cli", "wt", "doctor", "--reap"]
    out = subprocess.run(cmd, cwd=str(repo_root), capture_output=True,
                         text=True, timeout=30)
    return ActionResult(out.returncode, out.stdout, out.stderr)


def open_shell(worktree_path: Path) -> int:
    """Spawn $SHELL -i in the worktree. Caller suspends Textual first."""
    shell = os.environ.get("SHELL", "/bin/sh")
    return subprocess.call([shell, "-i"], cwd=str(worktree_path))


def open_editor(worktree_path: Path) -> int:
    """Spawn $EDITOR (split via shlex) on the worktree. Caller suspends."""
    editor = os.environ.get("EDITOR", "vi")
    parts = shlex.split(editor)
    return subprocess.call([*parts, str(worktree_path)],
                            cwd=str(worktree_path))


def build_review_prompt(repo_root: Path, kind: str) -> str:
    """Run `orca-cli build-review-prompt --kind <kind>` and return stdout."""
    out = subprocess.run(
        ["orca-cli", "build-review-prompt", "--kind", kind],
        cwd=str(repo_root), capture_output=True, text=True, timeout=30,
    )
    return out.stdout if out.returncode == 0 else f"<error>\n{out.stderr}"

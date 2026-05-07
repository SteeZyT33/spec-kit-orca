"""Thin subprocess wrappers around git, scoped to TUI drill-down needs."""
from __future__ import annotations

import subprocess
from pathlib import Path


def recent_commits(
    repo_root: Path, branch: str, *, n: int = 20,
) -> list[tuple[str, str, str]]:
    """Return last n commits on `branch` as (short_sha, relative_date, subject)
    tuples. Empty list if branch missing or git fails.

    Format: tab-separated so subjects can contain spaces and middle-dot.
    """
    try:
        out = subprocess.run(
            ["git", "-C", str(repo_root), "log",
             "--pretty=%h\t%cr\t%s", f"-n{n}", branch, "--"],
            capture_output=True, text=True, timeout=5.0,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return []
    if out.returncode != 0:
        return []
    rows: list[tuple[str, str, str]] = []
    for line in out.stdout.splitlines():
        parts = line.split("\t", 2)
        if len(parts) == 3:
            rows.append((parts[0], parts[1], parts[2]))
    return rows


def ahead_behind(
    repo_root: Path, branch: str, base: str,
) -> tuple[int, int] | None:
    """Return (ahead, behind) commit counts of `branch` vs `base`. None if
    git fails (no upstream, branch missing, etc.).

    Uses `git rev-list --left-right --count <base>...<branch>` which prints
    `<behind>\\t<ahead>` (left=base=behind, right=branch=ahead).
    """
    try:
        out = subprocess.run(
            ["git", "-C", str(repo_root), "rev-list", "--left-right",
             "--count", f"{base}...{branch}"],
            capture_output=True, text=True, timeout=5.0,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return None
    if out.returncode != 0:
        return None
    parts = out.stdout.strip().split()
    if len(parts) != 2:
        return None
    try:
        left, right = int(parts[0]), int(parts[1])
    except ValueError:
        return None
    # --left-right --count prints <left_count>\t<right_count>
    # with base...branch: left=behind, right=ahead
    # Return as (ahead, behind) per caller contract
    return (left, right)


def show_commit(repo_root: Path, sha: str) -> int:
    """Spawn `git show <sha>` in the worktree. Caller is responsible for
    suspending Textual via `app.suspend()`. Returns subprocess exit code."""
    return subprocess.call(
        ["git", "-C", str(repo_root), "show", sha],
        cwd=str(repo_root),
    )

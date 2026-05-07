"""Init-time bugs: status line on first render, last_refresh floor, branch merged guard."""
from __future__ import annotations

import asyncio
from pathlib import Path


def test_status_line_renders_on_first_empty_set_rows(tmp_path: Path) -> None:
    asyncio.run(_run_status(tmp_path))


async def _run_status(tmp_path: Path) -> None:
    from orca.tui.app import FleetApp
    from textual.widgets import Static
    app = FleetApp(repo_root=tmp_path, read_only=True)
    async with app.run_test() as pilot:
        app.set_rows([])
        await pilot.pause()
        line = app.query_one("#status-line", Static)
        text = str(line.content)
        assert "0 lanes" in text, f"expected status line on empty render, got: {text!r}"


def test_last_refresh_floor_is_zero_seconds(tmp_path: Path) -> None:
    asyncio.run(_run_refresh(tmp_path))


async def _run_refresh(tmp_path: Path) -> None:
    from orca.tui.app import FleetApp
    app = FleetApp(repo_root=tmp_path, read_only=True)
    async with app.run_test() as pilot:
        app.set_rows([])
        await pilot.pause()
        label = app._last_refresh_label()
    assert label != "-", "initial last-refresh label must not be '-'"
    assert "ago" in label or "s" in label


def test_branch_merged_false_for_zero_commit_branch(tmp_path: Path, monkeypatch) -> None:
    """A branch reachable from base but with 0 commits ahead must NOT be 'merged'."""
    from orca.tui.actions import branch_merged

    def fake_run(cmd, **kw):
        class _CP:
            returncode = 0
            stdout = ""

        if cmd[3] == "branch" and "--merged" in cmd:
            _CP.stdout = "  empty-branch\n* main\n"
            return _CP()
        if cmd[3] == "rev-list":
            _CP.stdout = "0\n"
            return _CP()
        return _CP()

    monkeypatch.setattr("subprocess.run", fake_run)
    assert branch_merged(tmp_path, "empty-branch", "main") is False


def test_branch_merged_true_for_real_merge(tmp_path: Path, monkeypatch) -> None:
    """A branch reachable from base with >=1 commit ahead IS 'merged'."""
    from orca.tui.actions import branch_merged

    def fake_run(cmd, **kw):
        class _CP:
            returncode = 0
            stdout = ""

        if cmd[3] == "branch" and "--merged" in cmd:
            _CP.stdout = "  feat-x\n* main\n"
            return _CP()
        if cmd[3] == "rev-list":
            _CP.stdout = "5\n"
            return _CP()
        return _CP()

    monkeypatch.setattr("subprocess.run", fake_run)
    assert branch_merged(tmp_path, "feat-x", "main") is True

"""GIT LOG block is selectable; c opens the selected commit."""
from __future__ import annotations

import asyncio
from pathlib import Path


def test_git_log_block_is_a_datatable(tmp_path: Path, monkeypatch) -> None:
    asyncio.run(_run(tmp_path, monkeypatch))


async def _run(tmp_path: Path, monkeypatch) -> None:
    from orca.tui.app import FleetApp
    from orca.tui.flow_strip import strip_segments
    from orca.flow_state import FlowMilestone
    from orca.tui.models import FleetRow

    monkeypatch.setattr(
        "orca.tui.git.recent_commits",
        lambda repo, branch, n=20: [
            ("abc1234", "2 hours ago", "fix the thing"),
            ("def5678", "yesterday",   "add the feature"),
            ("0a1b2c3", "3 days ago",  "another commit"),
        ],
    )

    empty = strip_segments([
        FlowMilestone(stage=s, status="not_started")
        for s in ["brainstorm", "specify", "plan", "tasks", "implement",
                  "review-spec", "review-code", "review-pr"]
    ])
    row = FleetRow(lane_id="alpha", feature_id=None, branch="alpha",
                   worktree_path="/tmp/alpha", agent="claude", state="live",
                   stage_segments=empty, last_seen="12s",
                   done="·  ·  · ", health="")

    app = FleetApp(repo_root=tmp_path, read_only=True)
    async with app.run_test() as pilot:
        app.set_rows([row])
        await pilot.pause()
        await pilot.press("enter")
        await pilot.pause()
        from textual.widgets import DataTable
        git_table = app.screen.query_one("#lane-git-table", DataTable)
        assert git_table.row_count == 3, "expected 3 commit rows"


def test_c_in_git_log_opens_selected_commit(tmp_path: Path, monkeypatch) -> None:
    asyncio.run(_run_select(tmp_path, monkeypatch))


async def _run_select(tmp_path: Path, monkeypatch) -> None:
    from orca.tui.app import FleetApp
    from orca.tui.flow_strip import strip_segments
    from orca.flow_state import FlowMilestone
    from orca.tui.models import FleetRow

    shown: list[str] = []
    monkeypatch.setattr(
        "orca.tui.git.recent_commits",
        lambda repo, branch, n=20: [
            ("aaa", "now", "first"),
            ("bbb", "now", "second"),
        ],
    )
    monkeypatch.setattr(
        "orca.tui.git.show_commit",
        lambda repo, sha: shown.append(sha) or 0,
    )

    empty = strip_segments([
        FlowMilestone(stage=s, status="not_started")
        for s in ["brainstorm", "specify", "plan", "tasks", "implement",
                  "review-spec", "review-code", "review-pr"]
    ])
    row = FleetRow(lane_id="alpha", feature_id=None, branch="alpha",
                   worktree_path="/tmp/alpha", agent="claude", state="live",
                   stage_segments=empty, last_seen="12s",
                   done="·  ·  · ", health="")

    app = FleetApp(repo_root=tmp_path, read_only=True)
    async with app.run_test() as pilot:
        app.set_rows([row])
        await pilot.pause()
        await pilot.press("enter")
        await pilot.pause()
        # Focus the git log table, move cursor to second row, press c.
        from textual.widgets import DataTable
        git_table = app.screen.query_one("#lane-git-table", DataTable)
        git_table.focus()
        await pilot.pause()
        git_table.move_cursor(row=1)
        await pilot.pause()
        await pilot.press("c")
        await pilot.pause()

    assert shown == ["bbb"], f"expected ['bbb'], got {shown}"

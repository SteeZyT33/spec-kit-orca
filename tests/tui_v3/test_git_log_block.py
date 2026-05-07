"""Drill-down GIT LOG block shows recent commits on the row's branch."""
from __future__ import annotations

import asyncio
from pathlib import Path


def test_drilldown_renders_git_log_block(tmp_path: Path, monkeypatch) -> None:
    asyncio.run(_run(tmp_path, monkeypatch))


async def _run(tmp_path: Path, monkeypatch) -> None:
    from orca.tui.app import FleetApp
    from orca.tui.drilldown import LaneScreen
    from orca.tui.flow_strip import strip_segments
    from orca.flow_state import FlowMilestone
    from orca.tui.models import FleetRow

    monkeypatch.setattr(
        "orca.tui.git.recent_commits",
        lambda repo, branch, n=20: [
            ("abc1234", "2 hours ago", "fix the thing"),
            ("def5678", "yesterday",   "add the feature"),
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
        assert isinstance(app.screen, LaneScreen)
        from textual.widgets import DataTable
        git_table = app.screen.query_one("#lane-git-table", DataTable)
        assert git_table.row_count == 2, (
            f"expected 2 commit rows, got {git_table.row_count}"
        )
        # Verify commit shas are present as row keys.
        row_keys = {k.value for k in git_table.rows.keys()}
        assert "abc1234" in row_keys, f"abc1234 not in rows: {row_keys}"
        assert "def5678" in row_keys, f"def5678 not in rows: {row_keys}"

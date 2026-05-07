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
        from textual.widgets import Static
        git = app.screen.query_one("#lane-git", Static)
        text = str(git.content)
        assert "GIT LOG" in text
        assert "abc1234" in text
        assert "fix the thing" in text
        assert "def5678" in text

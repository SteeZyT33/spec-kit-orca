"""Clicking a stage line opens its evidence file in $EDITOR."""
from __future__ import annotations

import asyncio
from pathlib import Path


def test_click_stage_invokes_open_editor(tmp_path: Path, monkeypatch) -> None:
    asyncio.run(_run(tmp_path, monkeypatch))


async def _run(tmp_path: Path, monkeypatch) -> None:
    from orca.tui.app import FleetApp
    from orca.tui.flow_strip import strip_segments
    from orca.flow_state import FlowMilestone
    from orca.tui.models import FleetRow

    opened: list[Path] = []
    monkeypatch.setattr("orca.tui.actions.open_editor",
                        lambda p: opened.append(Path(p)) or 0)

    monkeypatch.setattr(
        "orca.tui.drilldown.LaneScreen._stage_lines",
        lambda self: [
            ("brainstorm", "done", "/tmp/some/spec.md"),
            ("specify", "—", ""),
        ],
    )

    empty = strip_segments([
        FlowMilestone(stage=s, status="not_started")
        for s in ["brainstorm", "specify", "plan", "tasks", "implement",
                  "review-spec", "review-code", "review-pr"]
    ])
    row = FleetRow(lane_id="alpha", feature_id="alpha", branch="alpha",
                   worktree_path="/tmp/alpha", agent="claude", state="live",
                   stage_segments=empty, last_seen="12s",
                   done="·  ·  · ", health="")

    app = FleetApp(repo_root=tmp_path, read_only=True)
    async with app.run_test() as pilot:
        app.set_rows([row])
        await pilot.pause()
        await pilot.press("enter")
        await pilot.pause()
        from textual.widgets import Static
        line = app.screen.query_one("#stage-brainstorm", Static)
        await pilot.click(line)
        await pilot.pause()

    assert opened == [Path("/tmp/some/spec.md")], f"opened={opened}"

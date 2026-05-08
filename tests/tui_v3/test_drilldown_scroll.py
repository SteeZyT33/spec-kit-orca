"""Drilldown body is scrollable so all panels are reachable at narrow heights."""
from __future__ import annotations

import asyncio
from pathlib import Path


def test_drilldown_body_is_scrollable(tmp_path: Path) -> None:
    asyncio.run(_run(tmp_path))


async def _run(tmp_path: Path) -> None:
    from orca.tui.app import FleetApp
    from orca.tui.flow_strip import strip_segments
    from orca.flow_state import FlowMilestone
    from orca.tui.models import FleetRow
    from textual.containers import VerticalScroll

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
    async with app.run_test(size=(80, 24)) as pilot:
        app.set_rows([row])
        await pilot.pause()
        await pilot.press("enter")
        await pilot.pause()
        # The drilldown screen should contain a VerticalScroll around the body.
        # At minimum, query for it and confirm it exists.
        scrolls = list(app.screen.query(VerticalScroll))
        assert len(scrolls) >= 1, (
            "drilldown body must be wrapped in a VerticalScroll for narrow heights"
        )

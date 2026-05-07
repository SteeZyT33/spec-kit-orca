"""Render stability: 50 identical-input set_rows must not re-render the
fleet table (no flicker). The status line is time-varying by design, so
full-SVG equality is not the contract — row-signature stability is."""
from __future__ import annotations

import asyncio
from pathlib import Path


def test_idle_render_is_stable(tmp_path: Path) -> None:
    asyncio.run(_run(tmp_path))


async def _run(tmp_path: Path) -> None:
    from orca.tui.app import FleetApp
    from orca.tui.fleet import FleetTable
    from orca.tui.flow_strip import strip_segments
    from orca.flow_state import FlowMilestone
    from orca.tui.models import FleetRow
    empty = strip_segments([
        FlowMilestone(stage=s, status="not_started")
        for s in ["brainstorm", "specify", "plan", "tasks", "implement",
                  "review-spec", "review-code", "review-pr"]
    ])
    rows = [FleetRow(lane_id="x", feature_id=None, branch="x",
                     worktree_path="/tmp/x", agent="claude", state="live",
                     stage_segments=empty, last_seen="1m",
                     done="·  ·  · ", health="")]
    app = FleetApp(repo_root=tmp_path, read_only=True)
    async with app.run_test(size=(100, 30)) as pilot:
        app.set_rows(rows)
        await pilot.pause()
        fleet = app.query_one(FleetTable)
        sig_after_first = fleet._last_signature
        row_count_after_first = fleet.row_count
        for _ in range(50):
            app.set_rows(rows)
            await pilot.pause()
        sig_after_50 = fleet._last_signature
        row_count_after_50 = fleet.row_count
    # The fleet table signature must be identical — no re-render of row data.
    assert sig_after_first == sig_after_50, (
        "FleetTable signature changed on identical input — flicker risk"
    )
    assert row_count_after_first == row_count_after_50, (
        "Row count changed on identical input"
    )

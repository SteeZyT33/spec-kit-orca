"""Lane + health columns widen with terminal width."""
from __future__ import annotations

import asyncio
from pathlib import Path


def test_lane_width_at_80_cols(tmp_path: Path) -> None:
    asyncio.run(_run(tmp_path, 80, expected_lane=22, expected_health=8))


def test_lane_width_at_100_cols(tmp_path: Path) -> None:
    asyncio.run(_run(tmp_path, 100, expected_lane=28, expected_health=14))


def test_lane_width_at_140_cols(tmp_path: Path) -> None:
    asyncio.run(_run(tmp_path, 140, expected_lane=36, expected_health=20))


async def _run(tmp_path: Path, width: int, expected_lane: int,
                expected_health: int) -> None:
    from orca.tui.app import FleetApp
    from orca.tui.fleet import FleetTable
    app = FleetApp(repo_root=tmp_path, read_only=True)
    async with app.run_test(size=(width, 30)) as pilot:
        app.set_rows([])
        await pilot.pause()
        table = app.query_one(FleetTable)
        # Find the column widths by their keys.
        cols = {c.key.value: c for c in table.columns.values()}
        lane_width = cols["lane"].width
        health_width = cols["health"].width
    assert lane_width == expected_lane, (
        f"lane width at {width} cols: got {lane_width}, want {expected_lane}"
    )
    assert health_width == expected_health, (
        f"health width at {width} cols: got {health_width}, want {expected_health}"
    )

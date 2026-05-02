"""One-off smoke that runs FleetApp against THIS repo (real data).

Not a regression test — captures snapshots so a human can eyeball the
empty-state and any-real-data behavior without spinning up tmux.
"""
from __future__ import annotations

import asyncio
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]


def test_live_against_real_repo() -> None:
    asyncio.run(_run())


async def _run() -> None:
    from orca.tui.app import FleetApp
    app = FleetApp(repo_root=REPO, read_only=True)
    async with app.run_test(size=(140, 44)) as pilot:
        await pilot.pause()
        out = Path(__file__).parent / "snapshots" / "live-real-repo-140x44.svg"
        out.write_text(app.export_screenshot())

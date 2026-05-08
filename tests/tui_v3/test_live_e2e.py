"""Phase 6 live e2e gate: real lane created, TUI rendered, fixes verified.

Gated behind ORCA_E2E=1 because it spawns subprocesses and creates real
worktrees. Run locally before declaring Phase 6 done.
"""
from __future__ import annotations

import asyncio
import os
import subprocess
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]


@pytest.mark.skipif(os.environ.get("ORCA_E2E") != "1",
                    reason="set ORCA_E2E=1 to run live e2e gate")
def test_phase6_live_against_real_repo() -> None:
    asyncio.run(_run())


async def _run() -> None:
    from orca.tui.app import FleetApp

    # 1. Empty-state assertion against the (currently empty) registry.
    app = FleetApp(repo_root=REPO, read_only=True)
    async with app.run_test(size=(140, 44)) as pilot:
        await pilot.pause()
        out = Path(__file__).parent / "snapshots" / "phase6-empty.svg"
        out.parent.mkdir(exist_ok=True)
        out.write_text(app.export_screenshot())
        text = out.read_text()
        # Empty-state hint visible
        assert "no lanes" in text, "empty-state hint missing"
        # Status line rendered (host: prefix is there)
        assert "host:" in text, "status line missing on empty render"
        # Lane count says zero
        assert "0 lanes" in text or "0&#160;lanes" in text, "lane count missing"

    # 2. Create a real lane via orca-cli wt new (positional branch arg).
    new_out = subprocess.run(
        ["orca-cli", "wt", "new", "--feature", "phase6-e2e",
         "--agent", "none", "--no-tmux", "--no-setup", "phase6-e2e"],
        cwd=str(REPO), capture_output=True, text=True,
    )
    assert new_out.returncode == 0, (
        f"wt new failed: stdout={new_out.stdout} stderr={new_out.stderr}"
    )

    try:
        # 3. Render with the real lane and verify Phase 6 fixes appear.
        app = FleetApp(repo_root=REPO, read_only=True)
        async with app.run_test(size=(140, 44)) as pilot:
            await pilot.pause()
            out = Path(__file__).parent / "snapshots" / "phase6-real-lane.svg"
            out.write_text(app.export_screenshot())
            text = out.read_text()

            # Lane shows up
            assert "phase6-e2e" in text, "lane not rendered"
            # Status line present
            assert "host:" in text, "status line missing"
            # Brand-new branch should NOT show ◯ (false-positive merged)
            assert text.count("◯") == 0, "false-positive merged glyph on new branch"
            # Live event tail strip exists ("last:" prefix)
            assert "last:" in text, "event tail missing"

            # 4. Drill into the lane.
            await pilot.press("enter")
            await pilot.pause()
            out2 = Path(__file__).parent / "snapshots" / "phase6-drilldown.svg"
            out2.write_text(app.export_screenshot())
            t2 = out2.read_text()

            assert "STAGE PROGRESS" in t2, "stage block missing"
            assert "GIT LOG" in t2, "git log block missing"
            # Stage labels should be human-readable, not raw enums.
            # `not_started` is the worst offender — it's the dim default
            # and used to leak verbatim. The spec replaces it with `—`.
            assert "not_started" not in t2, "raw enum 'not_started' leaked"
    finally:
        # Always clean up the test lane, even if assertions failed.
        subprocess.run(
            ["orca-cli", "wt", "rm", "phase6-e2e", "--force"],
            cwd=str(REPO), capture_output=True, text=True,
        )

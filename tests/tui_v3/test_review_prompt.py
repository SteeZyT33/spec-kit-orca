"""R keybinding builds a review prompt and pages it."""
from __future__ import annotations

import asyncio
from pathlib import Path


def test_R_pushes_review_kind_modal(tmp_path: Path) -> None:
    asyncio.run(_run(tmp_path))


async def _run(tmp_path: Path) -> None:
    from orca.tui.app import FleetApp
    from orca.tui.flow_strip import strip_segments
    from orca.flow_state import FlowMilestone
    from orca.tui.models import FleetRow
    from orca.tui.modals import ReviewKindModal

    empty = strip_segments([
        FlowMilestone(stage=s, status="not_started")
        for s in ["brainstorm", "specify", "plan", "tasks", "implement",
                  "review-spec", "review-code", "review-pr"]
    ])
    row = FleetRow(lane_id="x", feature_id="x", branch="x",
                   worktree_path="/tmp/x", agent="claude", state="live",
                   stage_segments=empty, last_seen="1m",
                   done="·  ·  · ", health="")
    app = FleetApp(repo_root=tmp_path, read_only=False)
    async with app.run_test() as pilot:
        app.set_rows([row])
        await pilot.pause()
        await pilot.press("R")
        await pilot.pause()
        assert isinstance(app.screen, ReviewKindModal)


def test_R_suppressed_in_read_only_mode(tmp_path: Path, monkeypatch) -> None:
    asyncio.run(_run_readonly(tmp_path, monkeypatch))


async def _run_readonly(tmp_path: Path, monkeypatch) -> None:
    from orca.tui.app import FleetApp
    from orca.tui.flow_strip import strip_segments
    from orca.flow_state import FlowMilestone
    from orca.tui.models import FleetRow

    called: list[str] = []
    monkeypatch.setattr(
        "orca.tui.actions.build_review_prompt",
        lambda repo, kind: called.append(kind) or "",
    )

    empty = strip_segments([
        FlowMilestone(stage=s, status="not_started")
        for s in ["brainstorm", "specify", "plan", "tasks", "implement",
                  "review-spec", "review-code", "review-pr"]
    ])
    row = FleetRow(lane_id="x", feature_id="x", branch="x",
                   worktree_path="/tmp/x", agent="claude", state="live",
                   stage_segments=empty, last_seen="1m",
                   done="·  ·  · ", health="")
    app = FleetApp(repo_root=tmp_path, read_only=True)
    async with app.run_test() as pilot:
        app.set_rows([row])
        await pilot.pause()
        await pilot.press("R")
        await pilot.pause()
    assert called == [], f"build_review_prompt called in read-only: {called}"

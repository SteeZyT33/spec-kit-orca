"""Modal stack reentrance: keybindings don't leak through to the fleet."""
from __future__ import annotations

import asyncio
from pathlib import Path


def test_r_in_confirm_modal_does_not_open_another(tmp_path: Path, monkeypatch) -> None:
    """While ConfirmModal is open, pressing 'r' should not push another."""
    asyncio.run(_run_double_r(tmp_path, monkeypatch))


async def _run_double_r(tmp_path: Path, monkeypatch) -> None:
    from orca.tui.app import FleetApp
    from orca.tui.flow_strip import strip_segments
    from orca.flow_state import FlowMilestone
    from orca.tui.models import FleetRow
    from orca.tui.modals import ConfirmModal

    push_count = [0]
    real_push = FleetApp.push_screen

    def counting_push(self, screen, *args, **kw):
        if isinstance(screen, ConfirmModal):
            push_count[0] += 1
        return real_push(self, screen, *args, **kw)

    monkeypatch.setattr(FleetApp, "push_screen", counting_push)

    empty = strip_segments([
        FlowMilestone(stage=s, status="not_started")
        for s in ["brainstorm", "specify", "plan", "tasks", "implement",
                  "review-spec", "review-code", "review-pr"]
    ])
    row = FleetRow(lane_id="x", feature_id=None, branch="x",
                   worktree_path="/tmp/x", agent="claude", state="live",
                   stage_segments=empty, last_seen="1m",
                   done="·  ·  · ", health="")
    app = FleetApp(repo_root=tmp_path, read_only=False)
    async with app.run_test() as pilot:
        app.set_rows([row])
        await pilot.pause()
        await pilot.press("r")
        await pilot.pause()
        # First ConfirmModal is now on top.
        assert push_count[0] == 1
        # Press 'r' again. Modal should consume it (or no-op).
        await pilot.press("r")
        await pilot.pause()
        # Should still be 1 — modal blocked the second push.
        assert push_count[0] == 1, (
            f"r pressed inside ConfirmModal pushed another modal: "
            f"count={push_count[0]}"
        )


def test_R_in_new_lane_modal_does_not_trigger_build_review(tmp_path: Path, monkeypatch) -> None:
    """While NewLaneModal is open, pressing 'R' should not push the
    review-kind chooser."""
    asyncio.run(_run_R_in_new(tmp_path, monkeypatch))


async def _run_R_in_new(tmp_path: Path, monkeypatch) -> None:
    from orca.tui.app import FleetApp
    from orca.tui.flow_strip import strip_segments
    from orca.flow_state import FlowMilestone
    from orca.tui.models import FleetRow

    pushes = []
    real_push = FleetApp.push_screen

    def tracking_push(self, screen, *args, **kw):
        pushes.append(type(screen).__name__)
        return real_push(self, screen, *args, **kw)

    monkeypatch.setattr(FleetApp, "push_screen", tracking_push)

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
        await pilot.press("n")
        await pilot.pause()
        assert "NewLaneModal" in pushes
        # Press 'R' — should NOT add a ReviewKindModal to the stack.
        await pilot.press("R")
        await pilot.pause()
        assert "ReviewKindModal" not in pushes, (
            f"R pressed inside NewLaneModal triggered review chooser: "
            f"pushes={pushes}"
        )

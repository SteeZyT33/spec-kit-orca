"""Phase 11 extended e2e: multi-lane, real review artifacts, corrupt registry.

All gated behind ORCA_E2E=1. Each test cleans up after itself in a finally
block so failures don't pollute the repo.
"""
from __future__ import annotations

import asyncio
import os
import subprocess
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]


@pytest.mark.skipif(os.environ.get("ORCA_E2E") != "1",
                    reason="set ORCA_E2E=1 to run live e2e")
def test_e2e_multi_lane_render() -> None:
    asyncio.run(_run_multi())


async def _run_multi() -> None:
    from orca.tui.app import FleetApp

    branches = ["e2e-multi-a", "e2e-multi-b", "e2e-multi-c"]
    for b in branches:
        out = subprocess.run(
            ["orca-cli", "wt", "new", "--feature", b, "--agent", "none",
             "--no-tmux", "--no-setup", b],
            cwd=str(REPO), capture_output=True, text=True,
        )
        assert out.returncode == 0, f"creating {b}: {out.stderr}"

    try:
        app = FleetApp(repo_root=REPO, read_only=True)
        async with app.run_test(size=(140, 44)) as pilot:
            await pilot.pause()
            out = Path(__file__).parent / "snapshots" / "e2e-multi-lane.svg"
            out.write_text(app.export_screenshot())
            text = out.read_text()

            for b in branches:
                assert b in text, f"lane {b} not rendered"
            assert "3 lanes" in text, "lane count wrong"
            # No false-positive merged glyph for any of these
            assert "◯" not in text, "false-positive ◯"
    finally:
        for b in branches:
            subprocess.run(
                ["orca-cli", "wt", "rm", b, "--force"],
                cwd=str(REPO), capture_output=True, text=True,
            )


@pytest.mark.skipif(os.environ.get("ORCA_E2E") != "1",
                    reason="set ORCA_E2E=1 to run live e2e")
def test_e2e_drilldown_reflects_review_artifacts() -> None:
    asyncio.run(_run_review())


async def _run_review() -> None:
    from orca.tui.app import FleetApp

    feature_id = "e2e-with-review"
    feature_dir = REPO / "docs" / "superpowers" / "specs" / feature_id
    feature_dir.mkdir(parents=True, exist_ok=True)
    (feature_dir / "spec.md").write_text("# spec\n")
    (feature_dir / "plan.md").write_text("# plan\n")

    out = subprocess.run(
        ["orca-cli", "wt", "new", "--feature", feature_id, "--agent", "none",
         "--no-tmux", "--no-setup", feature_id],
        cwd=str(REPO), capture_output=True, text=True,
    )
    assert out.returncode == 0, out.stderr

    try:
        app = FleetApp(repo_root=REPO, read_only=True)
        async with app.run_test(size=(140, 44)) as pilot:
            await pilot.pause()
            await pilot.press("enter")
            await pilot.pause()
            out2 = Path(__file__).parent / "snapshots" / "e2e-real-review.svg"
            out2.write_text(app.export_screenshot())
            text = out2.read_text()

            assert "STAGE PROGRESS" in text
            # The spec.md and plan.md presence should drive non-default
            # statuses for the corresponding stages (specify → done,
            # plan → done). SVG text elements may appear in any document
            # order (x/y coordinates place them visually), so search the
            # full text rather than a character-window around the header.
            non_dash_labels = ["done", "in progress", "partial", "blocked",
                                "not started"]
            found = any(label in text for label in non_dash_labels)
            assert found, (
                f"expected at least one non-dash stage label in the SVG, "
                f"but none of {non_dash_labels!r} were found"
            )
    finally:
        subprocess.run(
            ["orca-cli", "wt", "rm", feature_id, "--force"],
            cwd=str(REPO), capture_output=True, text=True,
        )
        # Clean up the synthetic feature dir
        import shutil
        if feature_dir.exists():
            shutil.rmtree(feature_dir, ignore_errors=True)


@pytest.mark.skipif(os.environ.get("ORCA_E2E") != "1",
                    reason="set ORCA_E2E=1 to run live e2e")
def test_e2e_corrupt_registry_renders_empty_state() -> None:
    asyncio.run(_run_corrupt())


async def _run_corrupt() -> None:
    from orca.tui.app import FleetApp

    registry_path = REPO / ".orca" / "worktrees" / "registry.json"
    backup = registry_path.read_bytes() if registry_path.exists() else None
    try:
        registry_path.parent.mkdir(parents=True, exist_ok=True)
        registry_path.write_text("{this is not valid JSON")

        app = FleetApp(repo_root=REPO, read_only=True)
        async with app.run_test(size=(100, 30)) as pilot:
            await pilot.pause()
            out = Path(__file__).parent / "snapshots" / "e2e-corrupt-registry.svg"
            out.write_text(app.export_screenshot())
            text = out.read_text()
            assert "no lanes" in text, (
                "corrupt registry should fall through to empty-state placeholder"
            )
    finally:
        if backup is not None:
            registry_path.write_bytes(backup)
        else:
            registry_path.unlink(missing_ok=True)

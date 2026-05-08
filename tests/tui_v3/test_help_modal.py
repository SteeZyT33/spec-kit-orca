"""? keybinding pushes a help modal listing all keys."""
from __future__ import annotations

import asyncio
from pathlib import Path


def test_question_mark_pushes_help_modal(tmp_path: Path) -> None:
    asyncio.run(_run(tmp_path))


async def _run(tmp_path: Path) -> None:
    from orca.tui.app import FleetApp
    from orca.tui.modals import HelpModal
    app = FleetApp(repo_root=tmp_path, read_only=True)
    async with app.run_test() as pilot:
        app.set_rows([])
        await pilot.pause()
        await pilot.press("question_mark")
        await pilot.pause()
        assert isinstance(app.screen, HelpModal)


def test_help_modal_lists_visible_keys_in_read_only(tmp_path: Path) -> None:
    asyncio.run(_run_text(tmp_path))


async def _run_text(tmp_path: Path) -> None:
    from orca.tui.app import FleetApp
    from orca.tui.modals import HelpModal
    app = FleetApp(repo_root=tmp_path, read_only=True)
    async with app.run_test() as pilot:
        app.set_rows([])
        await pilot.pause()
        await pilot.press("question_mark")
        await pilot.pause()
        # The help body should mention every binding.
        screen = app.screen
        from textual.widgets import Static
        # HelpModal uses a Static (or similar) for the body.
        body_text = ""
        for static in screen.query(Static):
            body_text += str(static.content if hasattr(static, "content")
                              else static.renderable)
        # In read-only mode, mutating keys should be marked as suppressed.
        # The help should still LIST them so operators know they exist.
        for key in ["q", "g", "o", "e", "r", "n", "d", "R", "?"]:
            assert key in body_text, f"binding '{key}' missing from help"

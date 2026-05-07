"""Live event tail: one-line strip with newest cross-lane event."""
from __future__ import annotations

import asyncio
import json
from pathlib import Path


def test_event_tail_shows_newest_event(tmp_path: Path) -> None:
    asyncio.run(_run(tmp_path))


async def _run(tmp_path: Path) -> None:
    from orca.tui.app import FleetApp
    from textual.widgets import Static
    wt_root = tmp_path / ".orca" / "worktrees"
    wt_root.mkdir(parents=True)
    (wt_root / "events.jsonl").write_text(
        json.dumps({"event": "lane.created", "lane_id": "a",
                    "ts": "2026-05-01T10:00:00+00:00"}) + "\n"
        + json.dumps({"event": "agent.launched", "lane_id": "b",
                      "ts": "2026-05-01T11:00:00+00:00",
                      "agent": "claude"}) + "\n"
    )

    app = FleetApp(repo_root=tmp_path, read_only=True)
    async with app.run_test() as pilot:
        app.set_rows([])
        await pilot.pause()
        tail = app.query_one("#event-tail", Static)
        text = str(tail.content if hasattr(tail, "content") else tail.renderable)
        assert "agent.launched" in text
        assert "b" in text


def test_event_tail_empty_when_no_events_file(tmp_path: Path) -> None:
    asyncio.run(_run_empty(tmp_path))


async def _run_empty(tmp_path: Path) -> None:
    from orca.tui.app import FleetApp
    from textual.widgets import Static
    app = FleetApp(repo_root=tmp_path, read_only=True)
    async with app.run_test() as pilot:
        app.set_rows([])
        await pilot.pause()
        tail = app.query_one("#event-tail", Static)
        text = str(tail.content if hasattr(tail, "content") else tail.renderable)
        assert text != ""

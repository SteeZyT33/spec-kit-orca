"""Empty-state placeholder row when no lanes."""
from __future__ import annotations

import asyncio
from pathlib import Path


def test_empty_state_placeholder_visible(tmp_path: Path) -> None:
    asyncio.run(_run(tmp_path))


async def _run(tmp_path: Path) -> None:
    from orca.tui.app import FleetApp
    from orca.tui.fleet import FleetTable
    app = FleetApp(repo_root=tmp_path, read_only=True)
    async with app.run_test() as pilot:
        app.set_rows([])
        await pilot.pause()
        table = app.query_one(FleetTable)
        assert table.row_count == 1, "empty state should show 1 placeholder row"
        first_row = list(table.rows)[0]
        cells = table.get_row(first_row)
        rendered = " ".join(str(c) for c in cells)
        assert "no lanes" in rendered, rendered

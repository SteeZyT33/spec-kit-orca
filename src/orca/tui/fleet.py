"""The fleet table — the only main-screen widget."""
from __future__ import annotations

from rich.text import Text
from textual.widgets import DataTable

from orca.tui.models import FleetRow


_STATE_GLYPH = {
    "live":   ("●", "green"),
    "stale":  ("◐", "yellow"),
    "merged": ("◯", "cyan"),
    "failed": ("✕", "red"),
    "idle":   ("·", "dim"),
}


class FleetTable(DataTable):
    """Single-screen fleet view. Row data comes pre-rendered from collect_fleet."""

    def __init__(self, *args: object, **kwargs: object) -> None:
        super().__init__(
            cell_padding=0,
            cursor_foreground_priority="renderable",
            *args,
            **kwargs,
        )
        self._last_signature: object = object()  # sentinel; never equals any real sig

    def on_mount(self) -> None:
        self.cursor_type = "row"
        self.zebra_stripes = False
        self.add_column("", width=1, key="state")
        self.add_column("agent", width=6, key="agent")
        self.add_column("lane", width=22, key="lane")
        self.add_column("stage", width=23, key="stage")
        self.add_column("seen", width=5, key="seen")
        self.add_column("s·c·p", width=7, key="done")
        self.add_column("health", width=8, key="health")
        self._apply_responsive_widths(self.app.size.width if self.app else 80)

    def set_rows(self, rows: list[FleetRow]) -> None:
        sig = tuple((r.lane_id, r.state, r.stage_segments, r.last_seen,
                     r.done, r.health) for r in rows)
        if sig == self._last_signature:
            return
        self._last_signature = sig
        prev_cursor = self.cursor_row if self.row_count else 0
        self.clear()

        if not rows:
            # Empty state: single placeholder row pointing the operator
            # at what to do next. Empty cells in the data columns; hint
            # text lives in the lane column where it's most visible.
            self.add_row(
                Text("·", style="dim"),
                "-",
                Text("(no lanes — press n to create one, d for doctor)",
                     style="dim italic"),
                Text(""),
                "",
                "",
                Text(""),
                key="__empty__",
            )
            return

        for r in rows:
            glyph, color = _STATE_GLYPH.get(r.state, ("·", "dim"))
            health_style = "red" if r.health else ""
            stage_text = Text()
            for seg_text, seg_style in r.stage_segments:
                stage_text.append(seg_text, style=seg_style)
            self.add_row(
                Text(glyph, style=f"bold {color}" if color != "dim" else "dim"),
                r.agent,
                _truncate(
                    f"{r.feature_id or '-'} · {r.branch}",
                    self._lane_width_now(),
                ),
                stage_text,
                r.last_seen,
                r.done,
                Text(r.health, style=health_style),
                key=r.lane_id,
            )
        if rows and 0 <= prev_cursor < len(rows):
            try:
                self.move_cursor(row=prev_cursor)
            except Exception:
                pass

    def _apply_responsive_widths(self, term_width: int) -> None:
        """Adjust lane + health column widths based on terminal width."""
        if term_width >= 120:
            lane_w, health_w = 36, 20
        elif term_width >= 100:
            lane_w, health_w = 28, 14
        else:
            lane_w, health_w = 22, 8
        cols = {c.key.value: c for c in self.columns.values()}
        if "lane" in cols:
            cols["lane"].width = lane_w
        if "health" in cols:
            cols["health"].width = health_w
        self.refresh()

    def on_resize(self, event) -> None:  # type: ignore[override]
        self._apply_responsive_widths(event.size.width)

    def _lane_width_now(self) -> int:
        cols = {c.key.value: c for c in self.columns.values()}
        col = cols.get("lane")
        return col.width if col else 22


def _truncate(value: str, width: int) -> str:
    return value if len(value) <= width else value[: max(0, width - 1)] + "…"

from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path

from textual.app import App, ComposeResult, SuspendNotSupported
from textual.binding import Binding
from textual.widgets import DataTable, Footer, Static

from orca.tui.fleet import FleetTable
from orca.tui.models import FleetRow


class FleetApp(App):
    """Top-level TUI app."""

    TITLE = "orca"
    SUB_TITLE = "fleet"
    ENABLE_COMMAND_PALETTE = False
    BINDINGS = [
        Binding("q", "quit", "quit"),
        Binding("g", "refresh", "refresh"),
        Binding("enter", "drill_in", "drill", show=True),
        Binding("o", "open_shell", "shell"),
        Binding("e", "open_editor", "edit"),
        Binding("r", "close_lane", "rm"),
        Binding("n", "new_lane", "new"),
        Binding("d", "doctor", "doctor"),
        Binding("R", "build_review", "review"),
        Binding("question_mark", "help", "help"),
    ]

    # Hide r/n/d/R from Footer when read_only.
    def check_action(self, action: str, parameters: tuple[object, ...]) -> bool | None:
        if self.read_only and action in {"close_lane", "new_lane", "doctor", "build_review"}:
            return False
        return True
    CSS_PATH = "theme.tcss"

    def __init__(self, repo_root: Path, read_only: bool = False, **kwargs) -> None:
        super().__init__(**kwargs)
        self.repo_root = repo_root
        self.read_only = read_only
        self._rows: list[FleetRow] = []
        self._last_refresh_at: datetime | None = None

    def export_screenshot(self, *args, **kwargs) -> str:
        """SVG export with HTML entities decoded to plain ASCII where safe.

        Textual's SVG exporter encodes every space as &#160; (non-breaking
        space) so that browsers don't collapse runs.  That makes plain-text
        `in` checks inside tests fail even when the word *is* visually present.
        We decode the two most common entities (&#160; → space, &amp; → &)
        before returning so callers can use simple substring assertions.
        The resulting SVG still renders correctly in browsers because SVG
        <text> elements preserve whitespace by default.
        """
        svg = super().export_screenshot(*args, **kwargs)
        return svg.replace("&#160;", " ").replace("&amp;", "&")

    def compose(self) -> ComposeResult:  # type: ignore[override]
        yield FleetTable(id="fleet")
        yield Static("", id="event-tail")
        yield Static("", id="status-line")
        yield Footer()

    def set_rows(self, rows: list[FleetRow]) -> None:
        fleet = self.query_one(FleetTable)
        self._rows = list(rows)
        fleet.set_rows(rows)
        # Always refresh the status line — its content (lane counts,
        # last-refresh timer) changes regardless of row signature.
        self._update_status_line()
        self._update_event_tail()

    def _update_status_line(self) -> None:
        n = len(self._rows)
        stale = sum(1 for r in self._rows if r.state == "stale")
        merged = sum(1 for r in self._rows if r.state == "merged")
        host = self._host_system_label()
        refresh = self._last_refresh_label()
        line = (f"  host: {host} · {n} lanes · {stale} stale · "
                f"{merged} ready-to-merge · last refresh: {refresh}")
        self.query_one("#status-line", Static).update(line)

    def _update_event_tail(self) -> None:
        from orca.tui.collect import latest_event_summary
        text = latest_event_summary(self.repo_root)
        self.query_one("#event-tail", Static).update(text)

    def _host_system_label(self) -> str:
        layout = getattr(self, "_layout_cache", None)
        if layout is None:
            try:
                from orca.core.host_layout import from_manifest
                layout = from_manifest(self.repo_root)
            except Exception:
                try:
                    from orca.core.host_layout.detect import detect
                    layout = detect(self.repo_root)
                except Exception:
                    layout = False  # sentinel
            self._layout_cache = layout
        if not layout:
            return "?"
        return layout.__class__.__name__.replace("Layout", "").lower()

    def _last_refresh_label(self) -> str:
        ts = self._last_refresh_at or datetime.now(timezone.utc)
        delta = max(0.0, (datetime.now(timezone.utc) - ts).total_seconds())
        if delta < 60:
            return f"{int(delta)}s ago"
        return f"{int(delta / 60)}m ago"

    def action_refresh(self) -> None:
        self._collect_and_set()

    def action_drill_in(self) -> None:
        from orca.tui.drilldown import LaneScreen
        from orca.tui.fleet import FleetTable
        table = self.query_one(FleetTable)
        if not self._rows:
            return
        idx = table.cursor_row
        if 0 <= idx < len(self._rows):
            row = self._rows[idx]
            self.push_screen(LaneScreen(self.repo_root, row))

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        self.action_drill_in()

    def _focused_row(self) -> FleetRow | None:
        from orca.tui.fleet import FleetTable
        try:
            table = self.query_one(FleetTable)
        except Exception:
            return None
        idx = table.cursor_row
        if idx is None or not self._rows or idx >= len(self._rows):
            return None
        return self._rows[idx]

    def action_open_shell(self) -> None:
        row = self._focused_row()
        if row is None or not row.worktree_path:
            return
        from orca.tui.actions import open_shell
        with self.suspend():
            open_shell(Path(row.worktree_path))

    def action_open_editor(self) -> None:
        row = self._focused_row()
        if row is None or not row.worktree_path:
            return
        from orca.tui.actions import open_editor
        with self.suspend():
            open_editor(Path(row.worktree_path))

    def action_close_lane(self) -> None:
        if self.read_only:
            return
        row = self._focused_row()
        if row is None:
            return
        from orca.tui.modals import ConfirmModal, ResultModal
        from orca.tui.actions import close_lane
        prompt = f"Close lane {row.branch}? (deletes worktree, removes registration)"

        def on_answer(ok: bool | None) -> None:
            if not ok:
                return
            res = close_lane(self.repo_root, branch=row.branch)
            self.push_screen(ResultModal(
                title=f"close {row.branch} — rc={res.rc}",
                body=(res.stdout + ("\n" + res.stderr if res.stderr else "")),
            ))
            self._collect_and_set()
        self.push_screen(ConfirmModal(prompt), on_answer)

    def action_new_lane(self) -> None:
        if self.read_only:
            return
        from orca.tui.modals import NewLaneModal, ResultModal
        from orca.tui.actions import new_lane

        def on_submit(payload: dict | None) -> None:
            if not payload:
                return
            res = new_lane(self.repo_root, feature=payload["feature"],
                            agent=payload["agent"])
            self.push_screen(ResultModal(
                title=f"new lane {payload['feature']} — rc={res.rc}",
                body=(res.stdout + ("\n" + res.stderr if res.stderr else "")),
            ))
            self._collect_and_set()
        self.push_screen(NewLaneModal(), on_submit)

    def action_build_review(self) -> None:
        if self.read_only:
            return
        from orca.tui.modals import ReviewKindModal, ResultModal
        from orca.tui.actions import build_review_prompt
        import tempfile
        import subprocess
        import os

        def on_kind(kind: str | None) -> None:
            if not kind:
                return
            text = build_review_prompt(self.repo_root, kind)
            # Write to tmp file and page with $PAGER (default less).
            with tempfile.NamedTemporaryFile(
                mode="w", suffix=f".{kind}-review-prompt.md",
                delete=False,
            ) as fh:
                fh.write(text)
                tmp_path = fh.name
            pager = os.environ.get("PAGER", "less")
            try:
                with self.suspend():
                    subprocess.call([pager, tmp_path])
            except SuspendNotSupported:
                # Headless mode (tests) — fall back to a result modal.
                self.push_screen(ResultModal(
                    title=f"build-review-prompt --kind {kind}",
                    body=text[:2000] + ("…" if len(text) > 2000 else ""),
                ))

        self.push_screen(ReviewKindModal(), on_kind)

    def action_help(self) -> None:
        from orca.tui.modals import HelpModal
        self.push_screen(HelpModal())

    def action_doctor(self) -> None:
        if self.read_only:
            return
        from orca.tui.modals import DoctorModal
        from orca.tui.actions import doctor
        res = doctor(self.repo_root)
        self.push_screen(DoctorModal(
            title=f"wt doctor — rc={res.rc}",
            body=(res.stdout + ("\n" + res.stderr if res.stderr else "")),
        ))
        self._collect_and_set()

    def on_mount(self) -> None:
        from orca.tui.watcher import Watcher
        self._collect_and_set()
        self._watcher = Watcher(
            self.repo_root,
            on_change=lambda _p: self.call_from_thread(self._collect_and_set),
        )

    def on_unmount(self) -> None:
        w = getattr(self, "_watcher", None)
        if w is not None:
            w.stop()

    def _collect_and_set(self) -> None:
        from orca.tui.collect import collect_fleet
        from orca.tui.actions import tmux_alive, branch_merged
        try:
            rows = collect_fleet(
                self.repo_root,
                tmux_alive=tmux_alive,
                branch_merged=lambda b, base: branch_merged(self.repo_root, b, base),
                # last_event / last_setup_failed default to None →
                # collect_fleet builds a single events.jsonl index per refresh
                # (O(events), not O(lanes × events)).
            )
            self.set_rows(rows)
        except Exception:
            self.set_rows([])
        self._last_refresh_at = datetime.now(timezone.utc)


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(prog="orca-tui")
    p.add_argument("--repo-root", default=".", help="Path to repo root")
    p.add_argument("--read-only", action="store_true",
                   help="Suppress mutating actions (r/n/d)")
    return p.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    FleetApp(repo_root=Path(args.repo_root).resolve(),
             read_only=args.read_only).run()
    return 0

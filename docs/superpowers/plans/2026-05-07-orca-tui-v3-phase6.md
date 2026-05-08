# orca TUI v3 Phase 6 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking. The user has explicitly authorized continuous looping; loop through tasks autonomously and run the live e2e gate at the end. Only escalate when blocked.

**Goal:** Close v3.0's gaps surfaced by live real-data testing — empty state, git log integration in drill-down, human-readable stage statuses, ahead/behind, live event tail, click-to-evidence — and gate completion on a live end-to-end render against this repo with a real lane.

**Architecture:** Layered changes on top of the v3 fleet view. New `git.py` helper for subprocess wrappers. Drilldown gets a third bordered region (GIT LOG). FleetApp gets an event-tail strip and corrected init logic. All keep the host-agnostic / read-only-by-default invariants.

**Tech Stack:** Python 3.11+, Textual ≥8.2.5, subprocess for git calls. Spec: `docs/superpowers/specs/2026-05-01-orca-tui-v3-phase6-design.md`.

**Branch:** `tui-v3-impl` (stacking on Phase 5, head `38d0bb8` at start of Phase 6).

---

## File Structure

```
src/orca/tui/
  app.py             # Modified: init bugs + event tail
  fleet.py           # Modified: empty-state placeholder
  drilldown.py       # Modified: stage status labels, GIT LOG block, ahead/behind, click-stage
  actions.py         # Modified: branch_merged probe gets ahead-count check
  git.py             # NEW: git log / ahead-behind / show wrappers
  flow_strip.py      # Modified: human-readable stage status helper
  theme.tcss         # Modified: CSS for #git-log block + #event-tail

tests/tui_v3/
  test_init_bugs.py      # NEW: status line on first render, last_refresh init, ◯ guard
  test_empty_state.py    # NEW: placeholder row when fleet is empty
  test_status_labels.py  # NEW: human-readable status mapping
  test_git_helpers.py    # NEW: git log + ahead/behind wrappers
  test_git_log_block.py  # NEW: drilldown shows commits
  test_event_tail.py     # NEW: bottom strip shows newest cross-lane event
  test_click_stage.py    # NEW: click on stage line invokes editor
  test_live_e2e.py       # NEW: full live render against real lane (final gate)
```

---

## Task 1: Status-line short-circuit fix + initial render

**Files:**
- Modify: `src/orca/tui/app.py:49-55` (`set_rows`) and `src/orca/tui/app.py:81-89` (`_last_refresh_label`)
- Test: `tests/tui_v3/test_init_bugs.py`

The empty-rows-on-first-call short-circuit silently skips `_update_status_line`. Fix by always calling it in `set_rows`. Also: `_last_refresh_label` returns `"-"` when `_last_refresh_at` is None, but on initial render that's the only state. Fix to return `"0s ago"` as the floor.

- [ ] **Step 1: Write failing test** (`tests/tui_v3/test_init_bugs.py`):

```python
"""Init-time bugs: status line on first render, last_refresh floor."""
from __future__ import annotations

import asyncio
from pathlib import Path


def test_status_line_renders_on_first_empty_set_rows(tmp_path: Path) -> None:
    asyncio.run(_run_status(tmp_path))


async def _run_status(tmp_path: Path) -> None:
    from orca.tui.app import FleetApp
    from textual.widgets import Static
    app = FleetApp(repo_root=tmp_path, read_only=True)
    async with app.run_test() as pilot:
        app.set_rows([])
        await pilot.pause()
        line = app.query_one("#status-line", Static)
        text = line.renderable
        assert "0 lanes" in str(text), f"expected status line on empty render, got: {text!r}"


def test_last_refresh_floor_is_zero_seconds(tmp_path: Path) -> None:
    asyncio.run(_run_refresh(tmp_path))


async def _run_refresh(tmp_path: Path) -> None:
    from orca.tui.app import FleetApp
    app = FleetApp(repo_root=tmp_path, read_only=True)
    async with app.run_test() as pilot:
        app.set_rows([])
        await pilot.pause()
        label = app._last_refresh_label()
    assert label != "-", "initial last-refresh label must not be '-'"
    assert "ago" in label or "s" in label
```

- [ ] **Step 2: Run RED**

```bash
uv run python -m pytest tests/tui_v3/test_init_bugs.py -v
```
Expected: 2 FAIL.

- [ ] **Step 3: Implement**

In `src/orca/tui/app.py`, replace the `set_rows` method (currently lines 49-55):

```python
    def set_rows(self, rows: list[FleetRow]) -> None:
        fleet = self.query_one(FleetTable)
        self._rows = list(rows)
        fleet.set_rows(rows)
        # Always refresh the status line — its content (lane counts,
        # last-refresh timer) changes regardless of row signature.
        self._update_status_line()
```

In `src/orca/tui/app.py`, replace `_last_refresh_label` body so it floors at "0s ago":

```python
    def _last_refresh_label(self) -> str:
        from datetime import datetime, timezone
        ts = getattr(self, "_last_refresh_at", None) or datetime.now(timezone.utc)
        delta = max(0.0, (datetime.now(timezone.utc) - ts).total_seconds())
        if delta < 60:
            return f"{int(delta)}s ago"
        return f"{int(delta / 60)}m ago"
```

- [ ] **Step 4: Run GREEN**

```bash
uv run python -m pytest tests/tui_v3/test_init_bugs.py tests/tui_v3/ -v
```
Expected: full v3 suite still green; the 2 new tests PASS.

- [ ] **Step 5: Commit**

```bash
git add src/orca/tui/app.py tests/tui_v3/test_init_bugs.py
git commit -m "fix(tui): status line renders on first empty set_rows"
```

---

## Task 2: Empty-state placeholder row

**Files:**
- Modify: `src/orca/tui/fleet.py` (`set_rows`)
- Test: `tests/tui_v3/test_empty_state.py`

When rows is empty, render a single placeholder row with a hint instead of leaving the table blank.

- [ ] **Step 1: Write failing test** (`tests/tui_v3/test_empty_state.py`):

```python
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
        # The first column of the placeholder row contains the hint text.
        # Pull through the table's row data:
        first_row = list(table.rows)[0]
        cells = table.get_row(first_row)
        rendered = " ".join(str(c) for c in cells)
        assert "no lanes" in rendered, rendered
```

- [ ] **Step 2: Run RED**

```bash
uv run python -m pytest tests/tui_v3/test_empty_state.py -v
```
Expected: FAIL (row_count is 0).

- [ ] **Step 3: Implement**

In `src/orca/tui/fleet.py`, modify `set_rows` to add a placeholder row when rows is empty. Replace the body of `set_rows` (currently around lines 42-onwards). Below is the COMPLETE method — paste over the existing `set_rows`:

```python
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
                _truncate(f"{r.feature_id or '-'} · {r.branch}", 22),
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
```

- [ ] **Step 4: Run GREEN**

```bash
uv run python -m pytest tests/tui_v3/test_empty_state.py tests/tui_v3/ -v
```
Expected: full v3 suite + new test PASS.

- [ ] **Step 5: Commit**

```bash
git add src/orca/tui/fleet.py tests/tui_v3/test_empty_state.py
git commit -m "feat(tui): empty-state placeholder row with hint"
```

---

## Task 3: Brand-new branch ◯ false positive

**Files:**
- Modify: `src/orca/tui/actions.py` (`branch_merged` function)
- Test: `tests/tui_v3/test_init_bugs.py` (append)

A branch with 0 commits ahead of base is technically reachable from base via `--merged`, but it's not "merged work needing cleanup." Require at least 1 commit ahead.

- [ ] **Step 1: Append failing test to `tests/tui_v3/test_init_bugs.py`**

```python
def test_branch_merged_false_for_zero_commit_branch(tmp_path: Path, monkeypatch) -> None:
    """A branch reachable from base but with 0 commits ahead must NOT be 'merged'."""
    from orca.tui.actions import branch_merged
    calls: list[list[str]] = []

    def fake_run(cmd, **kw):
        calls.append(cmd)

        class _CP:
            returncode = 0
            stdout = ""

        if cmd[3] == "branch" and "--merged" in cmd:
            _CP.stdout = "  empty-branch\n* main\n"
            return _CP()
        if cmd[3] == "rev-list":
            _CP.stdout = "0\n"  # 0 commits ahead
            return _CP()
        return _CP()

    monkeypatch.setattr("subprocess.run", fake_run)
    assert branch_merged(tmp_path, "empty-branch", "main") is False


def test_branch_merged_true_for_real_merge(tmp_path: Path, monkeypatch) -> None:
    """A branch reachable from base with ≥1 commit ahead IS 'merged'."""
    from orca.tui.actions import branch_merged

    def fake_run(cmd, **kw):
        class _CP:
            returncode = 0
            stdout = ""

        if cmd[3] == "branch" and "--merged" in cmd:
            _CP.stdout = "  feat-x\n* main\n"
            return _CP()
        if cmd[3] == "rev-list":
            _CP.stdout = "5\n"  # 5 commits ahead
            return _CP()
        return _CP()

    monkeypatch.setattr("subprocess.run", fake_run)
    assert branch_merged(tmp_path, "feat-x", "main") is True
```

- [ ] **Step 2: RED**

```bash
uv run python -m pytest tests/tui_v3/test_init_bugs.py -v
```
Expected: 2 new tests FAIL.

- [ ] **Step 3: Implement**

Modify `src/orca/tui/actions.py` `branch_merged`:

```python
def branch_merged(repo_root: Path, branch: str, base: str) -> bool:
    """True if `branch` is reachable from `base` AND has ≥1 commit beyond it.

    A 0-commits-ahead branch is technically reachable from base (it IS base)
    but isn't 'merged work needing cleanup' — it's just empty. Requiring
    ≥1 ahead commit avoids the brand-new-branch ◯ false positive.
    """
    try:
        out = subprocess.run(
            ["git", "-C", str(repo_root), "branch", "--merged", base,
             "--format", "%(refname:short)"],
            capture_output=True, text=True, timeout=5.0,
        )
        if out.returncode != 0:
            return False
        merged_set = {ln.strip().lstrip("* ") for ln in out.stdout.splitlines()}
        if branch not in merged_set:
            return False
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False

    # Branch is reachable. Now require it has ≥1 commit ahead of base.
    try:
        ahead = subprocess.run(
            ["git", "-C", str(repo_root), "rev-list", "--count",
             f"{base}..{branch}"],
            capture_output=True, text=True, timeout=5.0,
        )
        if ahead.returncode != 0:
            return False
        return int(ahead.stdout.strip() or "0") >= 1
    except (FileNotFoundError, subprocess.TimeoutExpired, ValueError):
        return False
```

- [ ] **Step 4: GREEN**

```bash
uv run python -m pytest tests/tui_v3/test_init_bugs.py tests/tui_v3/ -v
```

- [ ] **Step 5: Commit**

```bash
git add src/orca/tui/actions.py tests/tui_v3/test_init_bugs.py
git commit -m "fix(tui): branch_merged requires >=1 commit ahead of base"
```

---

## Task 4: Human-readable stage statuses

**Files:**
- Modify: `src/orca/tui/flow_strip.py` (add helper)
- Modify: `src/orca/tui/drilldown.py` (`_stage_block` uses helper)
- Test: `tests/tui_v3/test_status_labels.py`

Replace raw `not_started`, `incomplete`, `missing`, `phases_partial`, `overall_complete` enum strings in drill-down with operator-friendly labels.

- [ ] **Step 1: Write failing test** (`tests/tui_v3/test_status_labels.py`):

```python
"""Human-readable stage status mapping."""
from orca.tui.flow_strip import status_label


def test_known_statuses_map_to_labels():
    assert status_label("complete") == "done"
    assert status_label("in_progress") == "in progress"
    assert status_label("blocked") == "blocked"
    assert status_label("not_started") == "—"
    assert status_label("incomplete") == "incomplete"
    assert status_label("missing") == "not started"
    assert status_label("phases_partial") == "phases partial"
    assert status_label("overall_complete") == "done"


def test_unknown_status_falls_back_to_dash():
    assert status_label("ralph") == "—"
    assert status_label("") == "—"
```

- [ ] **Step 2: RED**

```bash
uv run python -m pytest tests/tui_v3/test_status_labels.py -v
```

- [ ] **Step 3: Implement**

Append to `src/orca/tui/flow_strip.py`:

```python
_STATUS_LABELS = {
    "complete":          "done",
    "in_progress":       "in progress",
    "blocked":           "blocked",
    "not_started":       "—",
    "incomplete":        "incomplete",
    "missing":           "not started",
    "phases_partial":    "phases partial",
    "overall_complete":  "done",
    "skipped":           "skipped",
}


def status_label(status: str) -> str:
    """Map a flow-state milestone status to an operator-friendly label."""
    return _STATUS_LABELS.get(status, "—")
```

In `src/orca/tui/drilldown.py` `_stage_block`, replace the line that uses raw `status` with the labeled version. Find the line:

```python
            lines.append(f"  {stage:14s}  {status:14s}  {evidence}")
```

Replace with:

```python
            from orca.tui.flow_strip import status_label
            lines.append(f"  {stage:14s}  {status_label(status):14s}  {evidence}")
```

- [ ] **Step 4: GREEN**

```bash
uv run python -m pytest tests/tui_v3/test_status_labels.py tests/tui_v3/ -v
```

- [ ] **Step 5: Commit**

```bash
git add src/orca/tui/flow_strip.py src/orca/tui/drilldown.py tests/tui_v3/test_status_labels.py
git commit -m "feat(tui): human-readable stage status labels in drill-down"
```

---

## Task 5: git.py helper module

**Files:**
- Create: `src/orca/tui/git.py`
- Test: `tests/tui_v3/test_git_helpers.py`

A small subprocess wrapper around the git commands the drill-down needs: `git log` (last N commits) and `git rev-list --left-right --count` (ahead/behind).

- [ ] **Step 1: Write failing test** (`tests/tui_v3/test_git_helpers.py`):

```python
"""Git subprocess wrappers for drill-down."""
from pathlib import Path

from orca.tui.git import recent_commits, ahead_behind


def test_recent_commits_parses_log_output(tmp_path: Path, monkeypatch):
    sample = (
        "abc1234 2 hours ago alpha subject\n"
        "def5678 yesterday   beta · subject with dot\n"
        "0a1b2c3 3 days ago  gamma\n"
    )

    class _CP:
        returncode = 0
        stdout = sample
        stderr = ""

    def fake_run(cmd, **kw):
        return _CP()

    monkeypatch.setattr("subprocess.run", fake_run)
    out = recent_commits(tmp_path, "feat-x", n=3)
    assert len(out) == 3
    assert out[0] == ("abc1234", "2 hours ago", "alpha subject")
    assert out[1] == ("def5678", "yesterday", "beta · subject with dot")


def test_recent_commits_empty_when_branch_missing(tmp_path: Path, monkeypatch):
    class _CP:
        returncode = 128
        stdout = ""
        stderr = "fatal: bad revision"

    def fake_run(cmd, **kw):
        return _CP()

    monkeypatch.setattr("subprocess.run", fake_run)
    out = recent_commits(tmp_path, "missing", n=20)
    assert out == []


def test_ahead_behind_parses_output(tmp_path: Path, monkeypatch):
    class _CP:
        returncode = 0
        stdout = "3\t7\n"
        stderr = ""

    def fake_run(cmd, **kw):
        return _CP()

    monkeypatch.setattr("subprocess.run", fake_run)
    ab = ahead_behind(tmp_path, "feat-x", "main")
    assert ab == (3, 7)


def test_ahead_behind_none_when_git_fails(tmp_path: Path, monkeypatch):
    class _CP:
        returncode = 128
        stdout = ""
        stderr = "fatal: ambiguous"

    def fake_run(cmd, **kw):
        return _CP()

    monkeypatch.setattr("subprocess.run", fake_run)
    assert ahead_behind(tmp_path, "x", "main") is None
```

- [ ] **Step 2: RED**

```bash
uv run python -m pytest tests/tui_v3/test_git_helpers.py -v
```

- [ ] **Step 3: Implement** (`src/orca/tui/git.py`):

```python
"""Thin subprocess wrappers around git, scoped to TUI drill-down needs."""
from __future__ import annotations

import subprocess
from pathlib import Path


def recent_commits(
    repo_root: Path, branch: str, *, n: int = 20,
) -> list[tuple[str, str, str]]:
    """Return last n commits on `branch` as (short_sha, relative_date, subject)
    tuples. Empty list if branch missing or git fails.

    Format: `git log --pretty='%h\\t%cr\\t%s' -n<N> <branch>` — tab-separated
    so subjects can contain spaces (and our middle-dot character).
    """
    try:
        out = subprocess.run(
            ["git", "-C", str(repo_root), "log",
             f"--pretty=%h\t%cr\t%s", f"-n{n}", branch, "--"],
            capture_output=True, text=True, timeout=5.0,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return []
    if out.returncode != 0:
        return []
    rows: list[tuple[str, str, str]] = []
    for line in out.stdout.splitlines():
        parts = line.split("\t", 2)
        if len(parts) == 3:
            rows.append((parts[0], parts[1], parts[2]))
    return rows


def ahead_behind(
    repo_root: Path, branch: str, base: str,
) -> tuple[int, int] | None:
    """Return (ahead, behind) commit counts of `branch` vs `base`. None if
    git fails (no upstream, branch missing, etc.).

    Uses `git rev-list --left-right --count <base>...<branch>` which prints
    `<behind>\\t<ahead>` — note the order: left=base (behind), right=branch
    (ahead).
    """
    try:
        out = subprocess.run(
            ["git", "-C", str(repo_root), "rev-list", "--left-right",
             "--count", f"{base}...{branch}"],
            capture_output=True, text=True, timeout=5.0,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return None
    if out.returncode != 0:
        return None
    parts = out.stdout.strip().split()
    if len(parts) != 2:
        return None
    try:
        behind, ahead = int(parts[0]), int(parts[1])
    except ValueError:
        return None
    return (ahead, behind)


def show_commit(repo_root: Path, sha: str) -> int:
    """Spawn `git show <sha>` via $PAGER (typically less) in the worktree.
    Caller is responsible for suspending Textual via `app.suspend()`.
    Returns the subprocess exit code.
    """
    return subprocess.call(
        ["git", "-C", str(repo_root), "show", sha],
        cwd=str(repo_root),
    )
```

- [ ] **Step 4: GREEN**

```bash
uv run python -m pytest tests/tui_v3/test_git_helpers.py tests/tui_v3/ -v
```

- [ ] **Step 5: Commit**

```bash
git add src/orca/tui/git.py tests/tui_v3/test_git_helpers.py
git commit -m "feat(tui): git.py helpers — recent_commits/ahead_behind/show"
```

---

## Task 6: GIT LOG block in drill-down

**Files:**
- Modify: `src/orca/tui/drilldown.py` (`compose` adds a third bordered region)
- Modify: `src/orca/tui/theme.tcss` (add `#lane-git` selector)
- Test: `tests/tui_v3/test_git_log_block.py`

Insert a `GIT LOG` panel between STAGE PROGRESS and RECENT EVENTS. Reads via `recent_commits(repo_root, row.branch, n=20)`.

- [ ] **Step 1: Write failing test** (`tests/tui_v3/test_git_log_block.py`):

```python
"""Drill-down GIT LOG block shows recent commits on the row's branch."""
from __future__ import annotations

import asyncio
from pathlib import Path


def test_drilldown_renders_git_log_block(tmp_path: Path, monkeypatch) -> None:
    asyncio.run(_run(tmp_path, monkeypatch))


async def _run(tmp_path: Path, monkeypatch) -> None:
    from orca.tui.app import FleetApp
    from orca.tui.drilldown import LaneScreen
    from orca.tui.flow_strip import strip_segments
    from orca.flow_state import FlowMilestone
    from orca.tui.models import FleetRow

    # Stub recent_commits via the drilldown's lookup path.
    monkeypatch.setattr(
        "orca.tui.git.recent_commits",
        lambda repo, branch, n=20: [
            ("abc1234", "2 hours ago", "fix the thing"),
            ("def5678", "yesterday",   "add the feature"),
        ],
    )

    empty = strip_segments([
        FlowMilestone(stage=s, status="not_started")
        for s in ["brainstorm", "specify", "plan", "tasks", "implement",
                  "review-spec", "review-code", "review-pr"]
    ])
    row = FleetRow(lane_id="alpha", feature_id=None, branch="alpha",
                   worktree_path="/tmp/alpha", agent="claude", state="live",
                   stage_segments=empty, last_seen="12s",
                   done="·  ·  · ", health="")

    app = FleetApp(repo_root=tmp_path, read_only=True)
    async with app.run_test() as pilot:
        app.set_rows([row])
        await pilot.pause()
        await pilot.press("enter")
        await pilot.pause()
        # The drill-down screen should now have a #lane-git widget.
        assert isinstance(app.screen, LaneScreen)
        from textual.widgets import Static
        git = app.screen.query_one("#lane-git", Static)
        text = str(git.renderable)
        assert "GIT LOG" in text
        assert "abc1234" in text
        assert "fix the thing" in text
        assert "def5678" in text
```

- [ ] **Step 2: RED**

```bash
uv run python -m pytest tests/tui_v3/test_git_log_block.py -v
```

- [ ] **Step 3: Implement**

Modify `src/orca/tui/drilldown.py`. Locate the `compose` method that yields metadata, stages, and events. Insert a new yield between stages and events. Find:

```python
        # 2. Stage progress block (new)
        yield Static(self._stage_block(), id="lane-stages")

        # 3. Recent events (unchanged)
```

Replace with:

```python
        # 2. Stage progress block
        yield Static(self._stage_block(), id="lane-stages")

        # 3. Git log block
        yield Static(self._git_block(), id="lane-git")

        # 4. Recent events
```

Add a new `_git_block` method to `LaneScreen`:

```python
    def _git_block(self) -> str:
        """Render the GIT LOG block: last 20 commits on the row's branch."""
        from orca.tui.git import recent_commits
        commits = recent_commits(self.repo_root, self.row.branch, n=20)
        lines = ["GIT LOG"]
        if not commits:
            lines.append("(no commits on this branch yet)")
            return "\n".join(lines)
        for sha, when, subject in commits:
            # Truncate subject so the line fits a typical terminal.
            if len(subject) > 60:
                subject = subject[:59] + "…"
            lines.append(f"  {sha}  {when:18s}  {subject}")
        return "\n".join(lines)
```

Append to `src/orca/tui/theme.tcss`:

```css
LaneScreen #lane-git {
    border: round $primary-darken-1;
    height: 1fr;
    padding: 0 1;
}

LaneScreen #lane-events {
    border: round $primary-darken-1;
    height: auto;
    padding: 0 1;
    max-height: 14;
}
```

(Reduce events block to a fixed-ish height so git log gets the flex grow.)

- [ ] **Step 4: GREEN**

```bash
uv run python -m pytest tests/tui_v3/test_git_log_block.py tests/tui_v3/ -v
```

- [ ] **Step 5: Commit**

```bash
git add src/orca/tui/drilldown.py src/orca/tui/theme.tcss tests/tui_v3/test_git_log_block.py
git commit -m "feat(tui): GIT LOG block in drill-down (last 20 commits)"
```

---

## Task 7: `c` in drill-down opens git show

**Files:**
- Modify: `src/orca/tui/drilldown.py` (BINDINGS, action_show_commit + cursor tracking)

This is the lighter version of the spec's "click commit." We add a `c` keypress that opens `git show <last_commit_sha>` in the pager via `subprocess.call`. (Per-commit cursor selection inside a Static is more involved; for v3 we ship "show most recent commit on this branch" as the v0.5 of this feature. Spec accepted.)

- [ ] **Step 1: Modify BINDINGS in `LaneScreen`**

Replace the BINDINGS list in `src/orca/tui/drilldown.py`:

```python
    BINDINGS = [
        ("escape", "app.pop_screen", "back"),
        ("c", "show_commit", "show commit"),
    ]
```

Add an action method:

```python
    def action_show_commit(self) -> None:
        """Open `git show <head>` in $PAGER for the row's branch."""
        from orca.tui.git import recent_commits, show_commit
        commits = recent_commits(self.repo_root, self.row.branch, n=1)
        if not commits:
            return
        sha = commits[0][0]
        with self.app.suspend():
            show_commit(self.repo_root, sha)
```

(No new test required — this is a thin keybinding over the already-tested `recent_commits` and `show_commit`. The `c` key works in a real terminal; it can't be exercised in Pilot because the `git show` subprocess pages.)

- [ ] **Step 2: Run full v3 suite**

```bash
uv run python -m pytest tests/tui_v3/ -v
```

Expected: still green.

- [ ] **Step 3: Commit**

```bash
git add src/orca/tui/drilldown.py
git commit -m "feat(tui): c in drill-down opens git show on branch HEAD"
```

---

## Task 8: Ahead/behind in drill-down metadata

**Files:**
- Modify: `src/orca/tui/drilldown.py` (`compose` metadata builder)

Add an `ahead/behind` line in the metadata block. Read base from `Sidecar.base_branch`, but our `FleetRow` doesn't have it. Solution: read it from the sidecar at drill-down time.

- [ ] **Step 1: Modify `LaneScreen.compose` metadata block**

In `src/orca/tui/drilldown.py`, the metadata block builder currently yields `path/branch/agent/state/feature/done/seen` (and conditionally health). Modify to read `base_branch` from the sidecar and call `ahead_behind`. Replace the metadata builder:

```python
    def compose(self) -> ComposeResult:  # type: ignore[override]
        # 1. Metadata block
        from orca.tui.git import ahead_behind
        from orca.core.worktrees.registry import read_sidecar, sidecar_path
        sc = read_sidecar(sidecar_path(
            self.repo_root / ".orca" / "worktrees", self.row.lane_id))
        base = sc.base_branch if sc else "main"
        ab = ahead_behind(self.repo_root, self.row.branch, base)
        ab_text = f" ({ab[0]} ahead, {ab[1]} behind {base})" if ab else ""

        meta_lines = [
            f"{self.row.lane_id} · {self.row.agent} · {self.row.state}",
            "",
            f"path     {self.row.worktree_path}",
            f"branch   {self.row.branch}{ab_text}",
            f"feature  {self.row.feature_id or '-'}",
            f"done     {self.row.done.strip()}",
            f"seen     {self.row.last_seen}",
        ]
        if self.row.health:
            meta_lines.append(f"health   {self.row.health}")
        yield Static("\n".join(meta_lines), id="lane-meta")

        # 2. Stage progress block
        yield Static(self._stage_block(), id="lane-stages")

        # 3. Git log block
        yield Static(self._git_block(), id="lane-git")

        # 4. Recent events
        events = load_recent_events(self.repo_root, self.row.lane_id)
        if not events:
            body = "(no events)"
        else:
            body = "\n".join(
                f"{e.get('ts', '?'):26s}  {e.get('event', '?'):24s}  "
                f"{e.get('agent', '')}"
                for e in events
            )
        yield Vertical(
            Static("RECENT EVENTS", classes="label"),
            Static(body),
            id="lane-events",
        )
        yield Footer()
```

- [ ] **Step 2: Run full v3 suite**

```bash
uv run python -m pytest tests/tui_v3/ -v
```

Expected: existing drill-down tests still pass (ahead_behind returns None for a tmp_path with no real branches → no parens added → metadata format unchanged for those tests).

- [ ] **Step 3: Commit**

```bash
git add src/orca/tui/drilldown.py
git commit -m "feat(tui): ahead/behind counts in drill-down metadata header"
```

---

## Task 9: Live event tail at fleet bottom

**Files:**
- Modify: `src/orca/tui/app.py` (compose adds a Static between fleet and status; refresh updates it)
- Modify: `src/orca/tui/theme.tcss` (`#event-tail` style)
- Test: `tests/tui_v3/test_event_tail.py`

A one-line strip showing the most recent event across all lanes. Reads tail of `events.jsonl`.

- [ ] **Step 1: Write failing test** (`tests/tui_v3/test_event_tail.py`):

```python
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
        text = str(tail.renderable)
        # Newest event is agent.launched on lane b.
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
        # When no events, tail renders dim placeholder.
        assert str(tail.renderable) != ""
```

- [ ] **Step 2: RED**

```bash
uv run python -m pytest tests/tui_v3/test_event_tail.py -v
```
Expected: FAIL — `#event-tail` widget doesn't exist.

- [ ] **Step 3: Implement**

In `src/orca/tui/app.py` `compose`, insert a Static between fleet and status-line. Replace the current `compose`:

```python
    def compose(self) -> ComposeResult:  # type: ignore[override]
        yield FleetTable(id="fleet")
        yield Static("", id="event-tail")
        yield Static("", id="status-line")
        yield Footer()
```

Add a method to compute the tail line:

```python
    def _update_event_tail(self) -> None:
        from orca.tui.collect import latest_event_summary
        text = latest_event_summary(self.repo_root)
        self.query_one("#event-tail", Static).update(text)
```

Call it from `set_rows` after `_update_status_line`:

```python
    def set_rows(self, rows: list[FleetRow]) -> None:
        fleet = self.query_one(FleetTable)
        self._rows = list(rows)
        fleet.set_rows(rows)
        self._update_status_line()
        self._update_event_tail()
```

In `src/orca/tui/collect.py`, add a `latest_event_summary` helper:

```python
def latest_event_summary(repo_root: Path) -> str:
    """Return a one-line summary of the most recent event in events.jsonl,
    or a dim placeholder if no events file exists."""
    path = repo_root / ".orca" / "worktrees" / "events.jsonl"
    if not path.exists():
        return "  last: (no events)"
    last: dict | None = None
    with path.open() as fh:
        for line in fh:
            try:
                entry = json.loads(line)
            except json.JSONDecodeError:
                continue
            last = entry
    if last is None:
        return "  last: (no events)"
    ts = last.get("ts", "?")
    age = format_age(ts)
    evt = last.get("event", "?")
    lane = last.get("lane_id", "?")
    agent = last.get("agent", "")
    pieces = [f"last: {age}", evt, lane]
    if agent:
        pieces.append(agent)
    return "  " + " · ".join(pieces)
```

(Add `from orca.tui.timefmt import format_age` and `import json` at top of `collect.py` if not already present.)

In `src/orca/tui/theme.tcss`, append:

```css
#event-tail {
    height: 1;
    padding: 0 1;
    color: $text-muted;
    background: $background;
}
```

- [ ] **Step 4: GREEN**

```bash
uv run python -m pytest tests/tui_v3/test_event_tail.py tests/tui_v3/ -v
```

- [ ] **Step 5: Commit**

```bash
git add src/orca/tui/app.py src/orca/tui/collect.py src/orca/tui/theme.tcss tests/tui_v3/test_event_tail.py
git commit -m "feat(tui): live event tail strip at fleet bottom"
```

---

## Task 10: Click-stage opens evidence file

**Files:**
- Modify: `src/orca/tui/drilldown.py` (replace static stage block with one whose lines are clickable)
- Test: `tests/tui_v3/test_click_stage.py`

Make each stage line in STAGE PROGRESS clickable: clicking it opens its evidence file in `$EDITOR`.

This requires turning `_stage_block` from a single Static into a Vertical of clickable Statics, each holding its evidence path. Use Textual's `on_click` event on Static.

- [ ] **Step 1: Write failing test** (`tests/tui_v3/test_click_stage.py`):

```python
"""Clicking a stage line opens its evidence file in $EDITOR."""
from __future__ import annotations

import asyncio
from pathlib import Path


def test_click_stage_invokes_open_editor(tmp_path: Path, monkeypatch) -> None:
    asyncio.run(_run(tmp_path, monkeypatch))


async def _run(tmp_path: Path, monkeypatch) -> None:
    from orca.tui.app import FleetApp
    from orca.tui.flow_strip import strip_segments
    from orca.flow_state import FlowMilestone
    from orca.tui.models import FleetRow

    opened: list[Path] = []
    monkeypatch.setattr("orca.tui.actions.open_editor",
                        lambda p: opened.append(Path(p)) or 0)

    # Stub _stage_block_lines so the drill-down has a clickable line with
    # a known evidence path.
    monkeypatch.setattr(
        "orca.tui.drilldown.LaneScreen._stage_lines",
        lambda self: [
            ("brainstorm", "done", "/tmp/some/spec.md"),
            ("specify", "—", ""),
        ],
    )

    empty = strip_segments([
        FlowMilestone(stage=s, status="not_started")
        for s in ["brainstorm", "specify", "plan", "tasks", "implement",
                  "review-spec", "review-code", "review-pr"]
    ])
    row = FleetRow(lane_id="alpha", feature_id="alpha", branch="alpha",
                   worktree_path="/tmp/alpha", agent="claude", state="live",
                   stage_segments=empty, last_seen="12s",
                   done="·  ·  · ", health="")

    app = FleetApp(repo_root=tmp_path, read_only=True)
    async with app.run_test() as pilot:
        app.set_rows([row])
        await pilot.pause()
        await pilot.press("enter")
        await pilot.pause()
        # Click the brainstorm stage line (has evidence).
        from textual.widgets import Static
        line = app.screen.query_one("#stage-brainstorm", Static)
        await pilot.click(line)
        await pilot.pause()

    assert opened == [Path("/tmp/some/spec.md")], f"opened={opened}"
```

- [ ] **Step 2: RED**

```bash
uv run python -m pytest tests/tui_v3/test_click_stage.py -v
```

- [ ] **Step 3: Implement**

Modify `src/orca/tui/drilldown.py`. Replace `_stage_block` (the str-returning method) with `_stage_lines` (returns list of triples) and a `compose` change. Below is the full new shape — replace the `_stage_block` method and the part of `compose` that yields `lane-stages`:

In `compose`, replace:

```python
        # 2. Stage progress block
        yield Static(self._stage_block(), id="lane-stages")
```

with:

```python
        # 2. Stage progress block (clickable)
        yield Vertical(
            Static("STAGE PROGRESS", classes="label"),
            *[_StageLine(stage, status, evidence)
              for stage, status, evidence in self._stage_lines()],
            id="lane-stages",
        )
```

Replace `_stage_block` body with a new `_stage_lines` method:

```python
    def _stage_lines(self) -> list[tuple[str, str, str]]:
        """Return list of (stage_name, label, evidence_path) per stage."""
        order = ["brainstorm", "specify", "plan", "tasks", "implement",
                 "review-spec", "review-code", "review-pr"]
        if not self.row.feature_id:
            return [(s, "—", "") for s in order]
        try:
            from orca.core.host_layout import from_manifest
            from orca.flow_state import compute_flow_state
            from orca.tui.flow_strip import status_label
            layout = from_manifest(self.repo_root)
            result = compute_flow_state(layout.resolve_feature_dir(self.row.feature_id),
                                         repo_root=self.repo_root)
        except Exception:
            return [(s, "—", "") for s in order]
        all_milestones = result.completed_milestones + result.incomplete_milestones
        by_stage = {m.stage: m for m in all_milestones}
        out: list[tuple[str, str, str]] = []
        for stage in order:
            m = by_stage.get(stage)
            status = m.status if m else "not_started"
            evidence = m.evidence_sources[0] if (m and m.evidence_sources) else ""
            out.append((stage, status_label(status), evidence))
        return out
```

Add the `_StageLine` widget class at module level:

```python
class _StageLine(Static):
    """One stage row, clickable when it has evidence."""

    def __init__(self, stage: str, label: str, evidence: str, **kwargs) -> None:
        super().__init__(
            f"  {stage:14s}  {label:14s}  {evidence}",
            id=f"stage-{stage}", **kwargs,
        )
        self.stage_name = stage
        self.evidence = evidence

    def on_click(self) -> None:
        if not self.evidence:
            return
        from orca.tui.actions import open_editor
        with self.app.suspend():
            open_editor(Path(self.evidence))
```

(Add `from textual.containers import Vertical` and `from textual.widgets import Static` to drilldown.py top imports if not already.)

- [ ] **Step 4: GREEN**

```bash
uv run python -m pytest tests/tui_v3/test_click_stage.py tests/tui_v3/ -v
```

- [ ] **Step 5: Commit**

```bash
git add src/orca/tui/drilldown.py tests/tui_v3/test_click_stage.py
git commit -m "feat(tui): click a stage line opens its evidence file in editor"
```

---

## Task 11: Live e2e gate (final)

**Files:**
- Create: `tests/tui_v3/test_live_e2e.py`

The success criterion of Phase 6: against THIS repo, with a real test lane, the TUI renders without any of the v3.0 gaps. This test is gated behind `ORCA_E2E=1` so CI can opt in. It creates a lane via `orca-cli`, snapshots the rendered TUI, asserts the Phase 6 fixes are visible, then removes the lane.

- [ ] **Step 1: Write the test**

```python
"""Phase 6 live e2e gate: real lane created, TUI rendered, fixes verified.

Gated behind ORCA_E2E=1 because it spawns subprocesses and creates
real worktrees. Run locally before declaring Phase 6 done.
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

    # Empty-state assertion first — render against the empty registry,
    # confirm status line is there and a placeholder row appears.
    app = FleetApp(repo_root=REPO, read_only=True)
    async with app.run_test(size=(140, 44)) as pilot:
        await pilot.pause()
        out = Path(__file__).parent / "snapshots" / "phase6-empty.svg"
        out.write_text(app.export_screenshot())
        text = out.read_text()
        assert "no lanes" in text, "empty-state hint missing"
        assert "host:" in text, "status line missing on empty render"
        assert "0 lanes" in text or "0&#160;lanes" in text, "lane count missing"

    # Now create a real lane.
    subprocess.run(
        ["orca-cli", "wt", "new", "--feature", "phase6-e2e",
         "--agent", "none", "--no-tmux", "--no-setup", "phase6-e2e"],
        cwd=str(REPO), check=True,
        capture_output=True, text=True,
    )

    try:
        # Render with the real lane and verify Phase 6 fixes appear.
        app = FleetApp(repo_root=REPO, read_only=True)
        async with app.run_test(size=(140, 44)) as pilot:
            await pilot.pause()
            out = Path(__file__).parent / "snapshots" / "phase6-real-lane.svg"
            out.write_text(app.export_screenshot())
            text = out.read_text()

            # Phase 6 fixes:
            assert "phase6-e2e" in text, "lane not rendered"
            assert "host:" in text, "status line missing"
            # Brand-new branch should NOT show ◯ (merged glyph). It's
            # a 0-commits-ahead branch — should be ·  (idle) or ●  (live)
            # but never ◯.
            assert "◯" not in text or text.count("◯") == 0, "false-positive merged glyph"
            # Live event tail should appear above status line.
            assert "last:" in text, "event tail missing"

            # Drill into the lane.
            await pilot.press("enter")
            await pilot.pause()
            out2 = Path(__file__).parent / "snapshots" / "phase6-drilldown.svg"
            out2.write_text(app.export_screenshot())
            t2 = out2.read_text()

            assert "STAGE PROGRESS" in t2, "stage block missing"
            assert "GIT LOG" in t2, "git log block missing"
            # Stage labels should be human-readable, not raw enums.
            assert "not_started" not in t2, "raw enum leaked into UI"
            assert "incomplete" not in t2 or "not started" in t2, "enum leak"
    finally:
        # Always clean up the test lane, even if assertions failed.
        subprocess.run(
            ["orca-cli", "wt", "rm", "phase6-e2e", "--force"],
            cwd=str(REPO),
            capture_output=True, text=True,
        )
```

- [ ] **Step 2: Run gated locally**

```bash
ORCA_E2E=1 uv run python -m pytest tests/tui_v3/test_live_e2e.py -v
```

Expected: PASS. Three SVGs land in `tests/tui_v3/snapshots/`:
- `phase6-empty.svg`
- `phase6-real-lane.svg`
- `phase6-drilldown.svg`

If anything fails, the test cleans up the lane in the `finally` block, then the assertion error tells you what's broken.

- [ ] **Step 3: Run with gate off — should skip**

```bash
uv run python -m pytest tests/tui_v3/test_live_e2e.py -v
```
Expected: SKIPPED.

- [ ] **Step 4: Confirm full v3 suite green**

```bash
uv run python -m pytest tests/tui_v3/ -v
```
Expected: 60+ passing + 1-2 skipped (e2e gates).

- [ ] **Step 5: Commit**

```bash
git add tests/tui_v3/test_live_e2e.py tests/tui_v3/snapshots/phase6-*.svg
git commit -m "test(tui): phase 6 live e2e gate against real lane"
```

---

## Task 12: Final tui-reviewer pass + PR update

After all 11 tasks above are committed, dispatch the tui-reviewer agent for a final visual review. Expected snapshots to feed it:

- `tests/tui_v3/snapshots/phase6-empty.svg`
- `tests/tui_v3/snapshots/phase6-real-lane.svg`
- `tests/tui_v3/snapshots/phase6-drilldown.svg`

Reviewer prompt (use this verbatim):

> Final Phase 6 review. Three SVGs in tests/tui_v3/snapshots/ (phase6-*). Spec: docs/superpowers/specs/2026-05-01-orca-tui-v3-phase6-design.md. Verify: empty state has hint + status line; brand-new branch shows · or ● not ◯; drill-down has STAGE PROGRESS with human-readable labels (no `not_started`/`incomplete`/`missing` raw enums) AND a GIT LOG block; ahead/behind in metadata; live event tail strip above status line. Approve or list specific issues.

If APPROVED, push and update PR #93 with a Phase 6 commit summary. If NEEDS WORK, address each issue with a follow-up commit + re-snapshot + re-review until APPROVED.

- [ ] **Final commit + push**

```bash
git push origin tui-v3-impl
gh pr comment 93 --body "Phase 6 shipped: empty state, GIT LOG block, ahead/behind, human-readable stage labels, live event tail, click-stage. Live e2e gate green. tui-reviewer: APPROVED."
```

---

## Production-readiness checklist

- [ ] All 11 implementation tasks committed.
- [ ] `uv run python -m pytest tests/tui_v3/ -q` green.
- [ ] `uv run python -m pytest -q` green at repo level (no regressions).
- [ ] `ORCA_E2E=1 uv run python -m pytest tests/tui_v3/test_live_e2e.py -v` PASS.
- [ ] tui-reviewer agent: APPROVED on final phase6 SVG bundle.
- [ ] PR #93 updated with Phase 6 summary.
- [ ] Pre-push hook clean (flake8 + commit subject ≤72 chars).

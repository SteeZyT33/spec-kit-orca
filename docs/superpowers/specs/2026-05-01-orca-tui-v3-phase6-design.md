# orca TUI v3 Phase 6 — Make It Actually Interactive

**Status:** Draft (2026-05-01, post-v3 ship critique)
**Owner:** Taylor
**Predecessor:** v3.0 fleet view (PR #93)

## Context

v3.0 shipped a focused fleet view + drill-down + 5 action keys. Live test against this repo's empty registry exposed real gaps the synthetic-fixture snapshots hid:

- **Empty state is invisible**: 0-lane register renders a void with no status line and no hint.
- **Drill-down shows orca lifecycle events, not git activity**: clicking a lane gives `lane.created` / `agent.launched` rows. An operator wants `git log <branch>` — what code actually changed.
- **Stage progress leaks raw enums**: `incomplete`, `not_started`, `missing` are internal vocab that should never reach a user.
- **No evidence paths** in stage progress despite spec; column rendered empty.
- **No ahead/behind** counts in drill-down despite spec.
- **No focused-lane filter on the event stream** — events list is per-lane already, but there's no parent-level "watch any lane" mode.

Spec calls these out as v3.1 work, not v4. Foundation stays.

## Goal

Make the TUI **answer real operator questions interactively**:

1. "What did this lane actually do?" → git log on the row's branch, scrollable, with one-keypress diff view.
2. "Where am I in flow?" → stage progress with human language + evidence file paths I can press Enter to open.
3. "How far ahead is this branch?" → ahead/behind shown in drill-down header.
4. "What's happening across all lanes right now?" → live tail of recent events at fleet-view bottom (not just inside drill-down).
5. "Why is the screen blank?" → useful empty state.

## Out of scope

- Inline diff viewer (just shell out to `git diff` via a key, like `e` opens editor).
- Cross-lane comparison.
- Mouse-driven sort/filter UI.
- Multi-pane tiling.

## What changes

### 1. Empty state

When `collect_fleet` returns `[]`, FleetTable renders a single placeholder row:

```
  ·     -      (no lanes — press n to create one, or d for doctor)
```

Status line still renders even when rows are empty: `host: <host> · 0 lanes · last refresh: 0s ago`. Fix the signature short-circuit so the first call with `()` signature still calls `_update_status_line()` once.

**Files**: `src/orca/tui/fleet.py`, `src/orca/tui/app.py`.

### 2. Git log in drill-down

Add a third bordered region between STAGE PROGRESS and RECENT EVENTS: **GIT LOG**.

Pulls last 20 commits via `git log --pretty='%h %cr %s' -n20 <branch>`. Each line is `<short_sha>  <relative date>  <subject>`. If the branch has no commits beyond base (or branch doesn't exist), show "(no commits on this branch yet)".

Pressing `c` while drill-down is focused → opens the focused commit in `$EDITOR` via `git show <sha>` (suspending Textual). Esc returns to drill-down.

**Files**: `src/orca/tui/drilldown.py`, `src/orca/tui/git.py` (new — thin wrapper over `subprocess.run(['git', '-C', ...])`).

### 3. Human-readable stage status

Replace raw enum strings with operator-friendly labels:

| Enum            | Display           |
|-----------------|-------------------|
| `complete`      | `done`            |
| `in_progress`   | `in progress`     |
| `blocked`       | `blocked`         |
| `not_started`   | `—`               |
| `incomplete`    | `incomplete`      |
| `missing`       | `not started`     |
| `phases_partial`| `phases partial`  |
| `overall_complete` | `done`         |

Add a tiny mapping table in `flow_strip.py` and use it from drilldown's `_stage_block`.

**Files**: `src/orca/tui/flow_strip.py`, `src/orca/tui/drilldown.py`.

### 4. Evidence paths populated

`FlowMilestone.evidence_sources` is already a list[str]. Drilldown already reads `evidence_sources[0]` but the field is empty for the test fixture's not-yet-real feature. For real features, this should populate. Confirm by adding a smoke that runs against THIS repo's real spec (the v3 spec itself) and checks evidence renders.

**Files**: `src/orca/tui/drilldown.py` (no logic change; just a regression test against real data).

### 5. Ahead/behind in drill-down header

Compute `git rev-list --left-right --count <base>...<branch>` → ahead/behind tuple. Render in metadata block:

```
branch   tui-v3-impl  (28 ahead, 0 behind main)
```

If the calculation fails (no upstream), omit the parens.

**Files**: `src/orca/tui/git.py` (new), `src/orca/tui/drilldown.py`.

### 6. Live event tail at fleet bottom

Add a one-line strip between the fleet table border and the status line, showing the most recent event across **all** lanes:

```
last: 2s ago · agent.launched · tui-v3-impl · claude
```

Reads the tail of `events.jsonl`, picks the newest event regardless of lane. Refreshes on watcher fire.

**Files**: `src/orca/tui/app.py`, new helper in `src/orca/tui/collect.py`.

### 7. Mouse click behavior

Already wired: clicking a row drills in. Add: clicking a stage in the drill-down opens its evidence file in `$EDITOR`. Use `on_click` on the stage block.

**Files**: `src/orca/tui/drilldown.py`.

## Quality gates

Same as v3.0:
- `tui-reviewer` agent must approve drill-down with new git log section
- Live snapshot against this repo (real data, real worktrees) at start and end
- `flake8` clean
- Full pytest suite green

## Production readiness

- [ ] Empty state shows hint + status line
- [ ] Drill-down has GIT LOG block with last 20 commits
- [ ] `c` from drill-down opens commit in $EDITOR
- [ ] Stage statuses are human-readable
- [ ] Evidence paths render for features that have them
- [ ] Ahead/behind shown in drill-down
- [ ] Live event tail at fleet bottom
- [ ] Click-stage opens evidence
- [ ] tui-reviewer APPROVED
- [ ] PR opened

## Effort estimate

Six discrete changes, each 1–2 commits. ~12–15 commits total. One reviewer round per phase boundary (drill-down rework is the only one needing visual review). Realistic ship: same-day if dispatched right after merge of #93.

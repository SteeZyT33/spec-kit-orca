# orca TUI v3 Phase 7 — Polish

**Status:** Draft (2026-05-07, post-Phase-6)
**Owner:** Taylor
**Predecessor:** Phase 6 (commits 281c339 → 2b545cf on tui-v3-impl)

## Context

Phase 6 closed real functional gaps. What's left are visible-but-not-blocking annoyances surfaced by live render:

1. **Lane column always truncates** at width=22 even on a 140-col terminal. Real lane IDs (e.g. `wt-contract · wt-contract`) routinely exceed 22.
2. **Health column always truncates** at width=8 (flex floor). `merged·cleanup` shows as `merged·c`; `setup-failed` as `setup-fa`. Operator can't read what's wrong without drilldown.
3. **GIT LOG block is a static blob.** No selection, no per-commit drilldown. Pressing `c` opens only the HEAD commit.
4. **`incomplete` enum still leaks.** Phase 6 mapped most enums but `incomplete` passes through verbatim. It's a raw word in the UI.

## Goal

Make the table feel like it scales with the terminal, and let the operator interact with individual commits.

## What changes

### 1. Responsive column widths

Two columns get widened when the terminal exceeds 100 cols:

| Width zone        | lane | health |
|-------------------|------|--------|
| ≤80 cols (narrow) | 22   | 8      |
| 81–119 (medium)   | 28   | 14     |
| ≥120 (wide)       | 36   | 20     |

Implementation: `FleetTable` listens for `on_resize` and re-applies column widths via `add_column` recreation OR direct width mutation if Textual supports it. Spec validation: at 80 cols, lane stays at 22 and total fixed-cost still fits; at 140 cols, lane shows 36 and `wt-contract · wt-contract` fits without `…`.

**Files**: `src/orca/tui/fleet.py`.

### 2. Selectable GIT LOG with per-commit drilldown

Replace the monolithic `Static` GIT LOG block with a `DataTable` (one row per commit). Cursor selects a commit. Pressing `c` opens `git show <selected_sha>` in `$PAGER`. Pressing `Enter` does the same.

**Files**: `src/orca/tui/drilldown.py`, `src/orca/tui/theme.tcss`.

### 3. Friendlier `incomplete` mapping

Change `_STATUS_LABELS["incomplete"]` from `"incomplete"` to `"partial"`. Update the test in `test_status_labels.py` to match. The reasoning: `incomplete` is a tautology in a status field; `partial` conveys what it actually means (some artifacts present, others missing).

**Files**: `src/orca/tui/flow_strip.py`, `tests/tui_v3/test_status_labels.py`.

## Quality gates

- `tui-reviewer` agent re-runs against regenerated SVGs at 80×24, 100×30, 140×44 (must show widening across the three).
- Live e2e (`ORCA_E2E=1 ... test_live_e2e.py`) re-runs and still passes.
- Full pytest suite green.
- flake8 clean.

## Out of scope

- Sort/filter (still spec'd as out-of-scope from v3).
- Mouse hover tooltips.
- Inline diff viewer (still using `git show` via $PAGER).

## Production readiness

- [ ] Lane column widens at 100+ and 120+ terminal widths
- [ ] Health column widens correspondingly
- [ ] GIT LOG block is a DataTable with row selection
- [ ] Pressing `c` or Enter on a GIT LOG row opens that specific commit
- [ ] `incomplete` enum no longer appears in UI
- [ ] tui-reviewer APPROVED
- [ ] Live e2e PASS
- [ ] Pre-push clean

---
description: Launch the orca TUI v3 — a single-screen fleet view of every worktree lane with state, stage progress, and at-a-glance health. Drill into any lane for git log + recent events. Mutating actions (close lane, new lane, doctor, build review prompt) shell out to orca-cli.
---

# /orca:tui

> **Status**: v3.0 — fleet-view redesign (replaces v1/v2).

The orca TUI shows your worktree fleet at a glance: which agent is on
which lane, where each lane is in flow, what's stale, what's ready to
clean up. Drilling into a lane reveals its stage progress, recent
commits, and lifecycle events. All mutations shell out to `orca-cli`.

## Launch

```bash
python -m orca.tui                              # current dir, full mode
python -m orca.tui --repo-root /path/to/repo    # specific repo
python -m orca.tui --read-only                  # suppress r/n/d/R bindings
```

The TUI runs against the current working directory by default and
refreshes on filesystem changes via watchdog (with a polling fallback
if watchdog isn't available).

## Fleet view

One row per lane. Columns:

| column   | meaning                                                       |
|----------|---------------------------------------------------------------|
| state    | `●` live / `◐` stale / `◯` merged / `✕` failed / `·` idle     |
| agent    | claude / codex / none                                         |
| lane     | feature_id · branch (truncates with `…` at narrow widths)     |
| stage    | 8-letter flow strip (br·sp·pl·ta·im·rs·rc·rp); UPPER = active |
| seen     | last_attached_at relative time (12s, 2m, 2h, 14d)             |
| s·c·p    | review verdicts (✓ done, ⏵ in_progress, ✕ blocked, · none)    |
| health   | stale / setup-failed / merged·cleanup / tmux-orphan / doctor  |

Lane width and health width grow on wider terminals (22/8 at ≤80 cols,
28/14 at 100+, 36/20 at 120+).

Bottom strip: live event tail (`last: <age> · <event> · <lane>`) and
status line (`host: <host_system> · N lanes · M stale · K ready-to-merge
· last refresh: Xs ago`).

## Drilldown

Pressing `Enter` (or clicking a row) pushes the lane drilldown:

1. **Metadata**: `lane · agent · state`, stage strip, path, branch
   (with ahead/behind counts), feature, done shorthand, seen, health.
2. **STAGE PROGRESS**: all 8 stages with human-readable status labels
   and evidence-source paths. Click a stage to open its evidence file
   in `$EDITOR`.
3. **GIT LOG**: last 20 commits on the lane's branch as a selectable
   DataTable. Press `c` (or Enter) on a row to open `git show <sha>`
   in `$PAGER`.
4. **RECENT EVENTS**: last 20 entries from `events.jsonl` for this lane.

`Esc` returns to the fleet view.

## Keybindings

Press `?` at any time for the full list. Quick reference:

**Fleet view:**

| key       | action                                                |
|-----------|-------------------------------------------------------|
| `↑↓`      | navigate                                              |
| `↵`       | drill into focused lane                               |
| `o`       | open shell in focused worktree                        |
| `e`       | open `$EDITOR` in focused worktree                    |
| `r`       | remove (close) focused lane (confirm modal)           |
| `n`       | new lane (modal prompts for feature_id + agent)       |
| `d`       | run `orca-cli wt doctor --reap`, show result          |
| `R`       | build review prompt (spec/code/pr chooser → `$PAGER`) |
| `g`       | manual refresh                                        |
| `q`       | quit                                                  |
| `?`       | help (this list)                                      |

**Drilldown:**

| key       | action                                          |
|-----------|-------------------------------------------------|
| `↑↓`      | navigate git log rows                           |
| `c` / `↵` | show selected commit (`git show <sha>` in pager)|
| click     | stage line opens its evidence file              |
| `esc`     | back to fleet                                   |

`--read-only` suppresses `r`, `n`, `d`, `R` (and hides them from the
help modal annotations).

## What it shows / what it doesn't

- **Reads**: `.orca/worktrees/registry.json`, per-lane sidecars,
  `events.jsonl`, host-resolved feature dirs (via `host_layout`),
  `git log` / `git rev-list` / `git branch --merged`, `tmux has-session`.
- **Writes**: nothing directly. All mutations shell out via `orca-cli`
  (`wt rm`, `wt new`, `wt doctor`) or the user's `$SHELL` / `$EDITOR` /
  `$PAGER`.
- **Host-agnostic**: works on spec-kit, openspec, superpowers, or bare
  repos. Adapter resolved via `.orca/adoption.toml`; falls back to
  filesystem detection if no manifest is present.

## Performance characteristics

- **events.jsonl**: tail-read (last 256KB ≈ ~3-4k events). Long-lived
  repos with 100k+ events refresh in <50ms.
- **Watcher debounce**: 500ms quiet window with a 2s max-delay cap, so
  sustained agent activity doesn't starve the refresh.
- **Render**: signature short-circuit on identical input — idle TUI
  costs zero re-render work.

## Invariants

- **Read-only TUI process.** The TUI never mutates repo state directly.
  Mutating keybindings spawn `orca-cli` subprocesses.
- **Projection not source.** Every cell traces to a file or git command
  the operator could run themselves.
- **Host-agnostic.** No spec-system path is hardcoded; all routing goes
  through `host_layout.from_manifest()` (or `detect()` as fallback).

## Related

- `docs/superpowers/specs/2026-05-01-orca-tui-v3-design.md` — design spec
- `docs/superpowers/specs/2026-05-01-orca-tui-v3-phase6-design.md` — Phase 6
- `docs/superpowers/specs/2026-05-07-orca-tui-v3-phase7-design.md` — Phase 7
- `docs/superpowers/specs/2026-05-07-orca-tui-v3-phase8-design.md` — Phase 8
- `src/orca/tui/` — implementation

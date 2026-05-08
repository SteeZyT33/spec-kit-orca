# orca TUI v3 Phase 8 — Reviews from inside + state fix

**Status:** Draft (2026-05-07, post-Phase-7)
**Owner:** Taylor

## Three changes

### 1. Fix brand-new lane false-positive stale

`derive_state` in `src/orca/tui/state.py` currently treats `last_attached_at = None` as stale:

```python
last = _parse_iso(inp.last_attached_at)
if last is None or (cur - last) > STALE_AFTER:
    return "stale"
```

A lane that was just created (no agent attached yet) is not stale — it's idle. Fix: when `last_attached_at` is None, fall through to `idle`. Stale only applies when the timestamp exists AND is older than 24h.

### 2. Trigger reviews from inside the TUI

New keybinding on the fleet view: `R` (capital R; lowercase `r` is already taken by close-lane). Pushes a modal: "Review which? [s]pec / [c]ode / [p]r / [esc] cancel". Selecting one runs:

- `orca-cli review-spec --feature <id> --feature-dir <feature_dir>` (and analogous for code/pr)

Output is captured into a `ResultModal` so the operator sees the verdict without leaving the TUI.

If the focused row has no `feature_id`, the binding no-ops with a brief flash (status-line message). `--read-only` suppresses `R` like it suppresses r/n/d.

### 3. Stage strip in drilldown header

The drilldown's metadata block currently shows `lane_id · agent · state` as the first line. Add a second line: the same 8-stage strip the fleet table renders. Operator gets visual continuity between fleet and drill.

## Out of scope

- Cancel/abort a running review.
- Live tail of review output during execution (just show final result).
- Filtering/sorting in fleet (still spec'd OOS).

## Quality gates

- tui-reviewer reviews regenerated drilldown SVGs
- Live e2e regenerates with the brand-new lane showing `·` (idle), not `◐` (stale)
- Full pytest + pre-push clean

## Production checklist

- [ ] `derive_state` returns `idle` for brand-new lanes (last_attached_at None, no other signals)
- [ ] `R` keybinding pushes review-type chooser modal
- [ ] Spec/code/pr selection invokes corresponding `orca-cli review-*` and shows result modal
- [ ] `--read-only` suppresses `R`
- [ ] Drilldown metadata header includes the stage strip
- [ ] Phase 7 SVG suite re-approved by tui-reviewer
- [ ] Live e2e PASS

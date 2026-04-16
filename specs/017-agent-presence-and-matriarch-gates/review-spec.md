# Review: 017 Agent Presence & Matriarch Completion Gates — Spec

**Stage**: review-spec (pre-plan adversarial review)
**Reviewed by**: claude (opus-4-7) — **AUTHOR OF THE SPEC**
**Date**: 2026-04-16
**Verdict**: `needs-revision` (self-critique; cross-pass required before merge)

## Context on reviewer identity

Per the review-spec contract this is supposed to be a cross-only adversarial
review by a different agent from the author. I authored the spec, so this is
a **self-pass critique**, not a valid cross-pass. A different agent (codex,
gemini, or similar) MUST review this spec before the PR merges. Findings
below are the honest self-critique I can produce given that constraint.

## Cross-spec consistency

**Risk: gate error-code convention is new.** No existing spec defines the
`LANE_*` error-code-prefix convention. Specs 010 (matriarch), 013 (spec-lite),
and 015 (adoption) raise `MatriarchError` with free-form messages. Introducing
a prefix convention in 017 without updating their contracts means:

- Callers can't uniformly switch on codes across all matriarch errors
- The spec-lite and adoption guards still raise un-coded messages
- Future specs may drift again

**Mitigation needed**: Either (a) extend 017 scope to back-fill codes on
existing guards (`LANE_IS_SPECLITE`, `LANE_IS_ADOPTION`), or (b) document
explicitly that codes are 017-forward-only and accept the inconsistency.

**Risk: `feature_dir` resolution depends on 005 flow-state.** The gate for
`LANE_REVIEW_MISSING` checks `<feature_dir>/review-code.md`. Spec 005
resolves `feature_dir` from `spec_id`. If 005's resolution changes (e.g.,
spec directory naming convention), 017's gate breaks silently.

**Mitigation needed**: Add a contract test in 017 that asserts
`_feature_dir` returns the expected path for a known spec_id.

## Feasibility

**OK — filesystem-backed presence is proven.** Spec-kitty already uses
this shape (`.worktrees/` + manifest). stdlib-only is trivially achievable.

**OK — flock is available on all target platforms.** `fcntl.flock` on
Unix, no Windows claim (spec documents this as a known limitation).

**Concern: race between reap and new session write.** The spec says "reap
stale → check conflict → write new session." Under the advisory lock this
is atomic, but the spec doesn't explicitly call out that lock-holding
duration includes the reap pass. If a reap pass takes >5s on a directory
with thousands of session files (unlikely but possible), new sessions time
out waiting on the lock.

**Mitigation needed**: Either bound the reap pass or move reap to a
separate shorter-critical-section pattern.

## Security implications

**Low risk surface overall.** No network, no shell exec, no eval. Filesystem
writes are bounded to `.specify/orca/sessions/`.

**Finding: session files disclose PID and hostname.** If the repo is
committed (accidentally), session files reveal the operator's machine.
Mitigation exists (the sessions dir can be gitignored) but 017 should
explicitly add `.specify/orca/sessions/` to the runtime-generated
gitignore or document the expected ignore rule.

**Finding: no authentication on session scope.** Any process with write
access to the repo can register a session claiming to be `claude` or
`codex`. This is fine for presence/conflict detection but must not be
mistaken for auth. Spec should explicitly call this out.

## Dependency risks

**OK — no new external dependencies.**

**Risk: legacy LaneRecord compat path adds test surface forever.** The
`registered_at_sha=None` fallback is a permanent degradation path. Every
future contributor has to remember the commit gate can be silently
skipped. Spec should add an FR saying "legacy compat path is removable
on next major version; add a deprecation warning."

## Industry patterns

**Good alignment with spec-kitty's orchestrator-api pattern.** The
error-code prefix convention, gate-at-transition shape, and filesystem-
backed state are all proven in their codebase.

**Missing: no equivalent of spec-kitty's `CONTRACT_VERSION_MISMATCH`.**
If 017 ships and then we change gate semantics in a later release,
callers with pinned old expectations will silently break. Adding a
contract version now is cheap.

## Findings summary

| # | Severity | Finding | Proposed action |
|---|---|---|---|
| 1 | Medium | Error-code convention not back-filled to existing guards | Decide: back-fill in 017 or defer explicitly |
| 2 | Low | Gate depends on 005's feature_dir resolution | Add contract test |
| 3 | Low | Reap-inside-lock may starve writers | Bound reap or move out of critical section |
| 4 | Low | Session files leak PID/hostname | Add gitignore rule to runtime output |
| 5 | Low | No auth on session scope | Document explicitly — not an auth primitive |
| 6 | Low | Legacy compat is permanent | Add deprecation note / future-removal FR |
| 7 | Medium | No contract version on the gate API | Add `GATES_CONTRACT_VERSION` constant |

## Verdict

`needs-revision` — the spec is implementable but three items should be
resolved before freeze:

1. Decide on error-code back-fill scope (finding #1)
2. Add contract version (finding #7)
3. Add the feature_dir contract test (finding #2)

Findings 3-6 can ship as known limitations if documented. A different
agent MUST still perform the actual cross-pass; this self-critique only
caught what I could see from the author's position.

## Required follow-up

- Route this spec to a cross-pass agent (codex, gemini, or another
  Claude session) via the cross-review mechanism before merging PR #58.
- Update spec to resolve findings 1, 2, and 7 (or document decisions to
  defer them).

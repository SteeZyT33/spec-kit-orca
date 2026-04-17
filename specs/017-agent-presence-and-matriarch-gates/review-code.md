# Review: 017 Agent Presence & Matriarch Gates — Code

**Stage**: review-code
**Date**: 2026-04-16

---

## Self-Pass — claude (opus-4-7)

### Scope

Files reviewed:
- `src/speckit_orca/session.py` (new, ~350 lines)
- `src/speckit_orca/matriarch.py` (diff: +~200 lines, gate helpers + `mark_lane_complete`, register_lane integration)
- `tests/test_session.py` (27 tests)
- `tests/test_matriarch_gates.py` (13 tests)

### Correctness

- **Gate ordering in register_lane**: worktree escape fires BEFORE session conflict check. Chose this order deliberately — an escaped worktree is unambiguous and cheap to detect, while session check does filesystem reads. If both conditions fire, the error names the actual problem.
- **Legacy compat path in mark_lane_complete**: `registered_at_sha is None` degrades to a note rather than crash. This was explicitly called out as a permanent-compat-path risk in the spec review; acceptable for the first release.
- **Reap inside lock**: `list_active_sessions` holds the session lock through the reap pass. Cheap in practice (small directory) but a theoretical starvation risk documented in the spec review (finding #3). Not addressed in this PR.
- **Scope overlap semantics**: `SessionScope.overlaps` treats same lane_id OR same feature_dir as conflict; worktree-only overlap is not. This matches the spec. Tests confirm all three cases.

### Code quality

- stdlib-only as required
- Type hints throughout
- Atomic writes via tempfile + rename
- flock timeout bounded (5s default) — won't hang indefinitely
- Context manager (`session_scope`) cleans up on exception

### Security

- `session.py` performs no shell exec, no network, no eval
- No untrusted input reaches subprocess — `_current_head_sha` uses fixed argv `["git", "rev-parse", "HEAD"]`
- Session files expose PID and hostname (spec review finding #4) — not addressed in this PR; gitignore rule is a follow-up

### Test coverage

- Every error code (`LANE_SCOPE_BUSY`, `LANE_WORKTREE_ESCAPED`, `LANE_NO_COMMITS`, `LANE_REVIEW_MISSING`, `LANE_ALREADY_COMPLETE`) has an explicit test
- Stale-session reap tested with both TTL-expired and corrupt-JSON cases
- Happy path for `mark_lane_complete` tested
- Legacy compat path tested
- No tests for flock contention between two processes — harder to write, deferred

### Deficiencies I know about

1. **No tests for concurrent-writer lock contention** — two actual processes hitting the lock simultaneously isn't exercised. The stdlib flock is proven but my usage of it isn't stress-tested.
2. **No integration test where register → work → review → complete runs end-to-end.** The individual gates are tested in isolation; a full lifecycle test would catch sequencing bugs.
3. **Windows path** — `fcntl` is Unix-only. Module imports fine on Windows but `flock` calls fail at runtime. Spec plan acknowledged this as a known limitation; no fallback implemented.
4. **`speckit-orca status --sessions` surface missing** — the public Python API is there but no CLI. Operators can't list sessions without writing Python.
5. **`register_lane` doesn't heartbeat a session on behalf of the registering agent.** A session must already exist for the conflict check to find it. If the agent forgets to `start_session()`, no conflict is detected. This is a real gap for the "presence is mandatory" goal.

### Verdict

**self-pass**: `ready-with-caveats` — code is correct and tested, but the five deficiencies above should be tracked. Items 4 and 5 in particular are operator-visible gaps.

---

## Cross-Pass — PENDING

**Required before merge.** The review-code contract requires a cross-pass by a different agent from the implementation author. I authored this code, so a cross-pass by codex, gemini, or a different Claude session is required before PR #58 merges.

**Suggested cross-pass scope**:
- Verify the flock pattern in `session.py` is correct (I'm not a systems-programming expert; an independent reviewer should check edge cases)
- Attempt to construct a scenario where a gate is bypassed (adversarial)
- Verify the spec-kitty comparison I made in the design is accurate
- Check test coverage gaps beyond what I listed as known deficiencies

**How to route**: Operator runs `/speckit.orca.review-code --cross` or equivalent with a different harness selected via matriarch's `select_cross_pass_agent`. Append findings to this file under a `## Cross-Pass — <agent>` header.

---

## Final Merge Verdict

**Cannot be set until cross-pass lands.** With self-pass only, status is `self-pass-ready, cross-pass-pending`.

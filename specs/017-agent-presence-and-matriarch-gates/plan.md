# Implementation Plan: 017 Agent Presence & Matriarch Gates

**Branch**: `017-agent-presence-and-matriarch-gates` | **Date**: 2026-04-16
**Spec**: [spec.md](./spec.md)

## Summary

Add a session-presence primitive (`src/speckit_orca/session.py`) and
five completion gates to `matriarch.py`. The session layer is new code
with no existing contract; the matriarch changes extend existing
operations with rejection codes.

## Technical Context

**Language**: Python 3.10+
**New module**: `src/speckit_orca/session.py` (~350 lines, stdlib-only)
**Modified**: `src/speckit_orca/matriarch.py` (+~200 lines for gates and
registered_at_sha field)
**Extended**: `src/speckit_orca/cli.py` (status --sessions flag, or new
`speckit-orca status` surface)
**Tests**: `tests/test_session.py` + `tests/test_matriarch_gates.py`
(~500 lines)

**Dependencies**: stdlib only (`fcntl`, `json`, `pathlib`, `datetime`,
`os`, `platform`, `secrets`, `tempfile`, `contextlib`).

**Storage**: `.specify/orca/sessions/<id>.json` + `.lock` flock file.

## Phase Breakdown

### Phase 1: Session primitive (session.py)

Status: implemented in this branch. Covers:

- `SessionScope`, `Session` dataclasses
- `start_session`, `heartbeat`, `end_session`, `session_scope` context manager
- `list_active_sessions` (with auto-reap)
- `find_conflicting_session`
- flock-backed advisory locking + atomic writes

### Phase 2: Matriarch integration

1. Add `registered_at_sha: str | None` to `LaneRecord` (FR-006, backward-compat)
2. `register_lane` — after spec-lite/AR guards, before any fs side-effects:
    - Call `find_conflicting_session(SessionScope(lane_id=lane_id))`
    - If found, raise `MatriarchError("LANE_SCOPE_BUSY: lane X held by session Y")`
3. `register_lane` — worktree check:
    - If `worktree_path` is set and not under `.specify/orca/worktrees/`
      and not equal to repo root, raise
      `MatriarchError("LANE_WORKTREE_ESCAPED: ...")`
4. `register_lane` — record `registered_at_sha` from `git rev-parse HEAD`
5. New public op `mark_lane_complete(lane_id, *, repo_root=None, final_commit_sha=None)`:
    - Load lane. If lifecycle_state is already "archived" or "completed",
      raise `LANE_ALREADY_COMPLETE`.
    - Read current HEAD SHA. If equals lane.registered_at_sha, raise
      `LANE_NO_COMMITS`. If `registered_at_sha` is None (legacy), skip
      this gate with a notes annotation.
    - Check `<feature_dir>/review-code.md` exists. If not, raise
      `LANE_REVIEW_MISSING`.
    - Recheck worktree escape (in case it was moved after registration).
    - On all checks passing: set lifecycle_state="completed",
      final_sha=current_sha, updated_at=now.

### Phase 3: CLI status surface

- Add `status_sessions()` in cli.py
- Wire `speckit-orca status --sessions` (or `speckit-orca sessions`)
- Output: table of agent, session_id, started, last_heartbeat, scope

### Phase 4: Tests

- `tests/test_session.py`: start/heartbeat/end roundtrip, stale reap,
  corrupt file reap, scope overlap, concurrent lock contention,
  session_scope context manager
- `tests/test_matriarch_gates.py`: each of the 5 error codes,
  legacy-compat path (no registered_at_sha), happy-path complete

### Phase 5: Docs + commit

- Spec updated with "Runtime status" once shipped
- README gets a one-line note under the matriarch experimental mention
- Commit, PR, post-merge tag

## Ordering Rationale

Session primitive first (no deps), then matriarch uses it (depends on
session), then CLI exposes it (depends on both), then tests validate
each layer. Can't parallelize phase 2 and 3 because phase 3 imports
from the new matriarch surface.

## Risks & Mitigations

| Risk | Mitigation |
|---|---|
| flock on Windows | fcntl is Unix-only; wrap import in try/except and fall back to best-effort no-lock on Windows (document limitation) |
| Clock skew across machines | 5-minute TTL absorbs normal skew; tests use injectable `now` |
| Session pileup if flock times out repeatedly | Timeout errors bubble up cleanly — no silent corruption |
| Legacy LaneRecords without registered_at_sha | Skip commit gate with a `notes` annotation; don't crash |

## Complexity Tracking

| Change | Why needed | Simpler alt rejected because |
|---|---|---|
| New session.py module | Presence is a new primitive with its own state machine | Shoehorning into matriarch would couple two different concerns |
| Error-code prefixes on MatriarchError | Callers need programmatic switch, not string parsing | Full enum hierarchy is over-engineered for 5 codes |
| registered_at_sha on LaneRecord | Required to diff commit history on complete | Calling git from complete's caller would duplicate logic |

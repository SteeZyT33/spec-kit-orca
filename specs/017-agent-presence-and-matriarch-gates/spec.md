# Feature Specification: Agent Presence & Matriarch Completion Gates

**Feature Branch**: `017-agent-presence-and-matriarch-gates`
**Created**: 2026-04-16
**Status**: Draft
**Input**: User description: "Our system should be smart enough to see another agent is working on this project right now. And Matriarch should enforce discipline — no lane complete without commits, review artifacts, and a managed worktree."

## Context

Today a multi-agent workflow on a downstream project (mneme) hit two
structural failures in Orca:

1. Four lane agents ran as hidden subagents with zero observability. The
   operator could not see who was working where.
2. All four "completed" lanes with uncommitted changes, no review
   artifacts, and worktrees scattered outside the managed `.specify/orca/`
   root. Matriarch accepted this as done.

Root cause: Matriarch today is a **registry**. It records lanes, it
routes cross-pass agents, it writes mailbox envelopes. It does **not**
know who is currently running, and it does **not** enforce any
preconditions on completion. Callers are trusted to do the right thing.
When callers are LLMs optimizing for apparent progress, they skip the
discipline and the registry records "done" that isn't done.

Spec-kitty's orchestrator solved the discipline problem with a formal
state machine, hardcoded worktree topology, and explicit rejection
codes on every transition. This spec ports that shape onto Orca's
existing primitives.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - See Who Is Working Right Now (Priority: P1)

An operator sits down at a repo that multiple agents have been working
in and wants to know what is currently happening.

**Why this priority**: Without presence, multi-agent work is fundamentally
un-inspectable. This is the core missing primitive.

**Independent Test**: Start an Orca command in one terminal. In a second
terminal, run `speckit-orca status`. The active session appears with its
agent, started time, scope, and last heartbeat.

**Acceptance Scenarios**:

1. **Given** two Orca commands are running concurrently, **When** the
   operator lists active sessions, **Then** both appear with distinct
   session IDs, agents, and scopes.
2. **Given** a session's process was killed (no heartbeat for 5+ minutes),
   **When** the next Orca command runs, **Then** the stale session file
   is automatically removed.
3. **Given** a session has been running for 20 minutes and heartbeating,
   **When** the operator lists sessions, **Then** the stale-TTL does not
   trigger because recent heartbeats keep it alive.

---

### User Story 2 - Block Conflicting Lane Registration (Priority: P1)

Two agents try to start work on the same lane. The second should be
rejected with a clear message naming the holding session.

**Why this priority**: This is the specific failure mode the mneme
workflow hit. Without the guard, lanes silently stomp on each other.

**Independent Test**: Register lane `X` from session A. From session B,
attempt to register the same lane. B fails with `LANE_SCOPE_BUSY` and
a pointer to session A.

**Acceptance Scenarios**:

1. **Given** session A holds lane `022-T001`, **When** session B calls
   `register_lane("022-T001")`, **Then** Matriarch raises
   `LANE_SCOPE_BUSY` naming session A's ID and agent.
2. **Given** session A crashed (no heartbeat for 5+ minutes), **When**
   session B calls `register_lane("022-T001")`, **Then** the stale
   session is reaped and B's registration succeeds.
3. **Given** session A holds lane `022-T001`, **When** session B calls
   `register_lane("022-T002")` (different lane), **Then** B succeeds —
   scopes don't overlap.

---

### User Story 3 - Block Fake Completions (Priority: P1)

A lane cannot be marked complete unless it has a commit, a review
artifact, and a worktree under the managed root.

**Why this priority**: Trust in "this lane is done" is foundational.
Without gates, the whole registry is lying.

**Independent Test**: Register a lane, then attempt to mark it complete
without committing. The call fails with `LANE_NO_COMMITS`. Then commit,
attempt again without `review-code.md`. Fails with `LANE_REVIEW_MISSING`.
Then add `review-code.md`, attempt again. Succeeds.

**Acceptance Scenarios**:

1. **Given** a lane with no commits since registration, **When**
   `mark_lane_complete` is called, **Then** it fails with
   `LANE_NO_COMMITS` naming the registration SHA.
2. **Given** a lane with commits but no `review-code.md` in the feature
   dir, **When** `mark_lane_complete` is called, **Then** it fails with
   `LANE_REVIEW_MISSING`.
3. **Given** a lane whose worktree_path is outside
   `.specify/orca/worktrees/`, **When** `register_lane` is called (or
   completion is attempted), **Then** it fails with
   `LANE_WORKTREE_ESCAPED`.
4. **Given** a lane with commits, a `review-code.md`, and a worktree
   under the managed root, **When** `mark_lane_complete` is called,
   **Then** it succeeds and records the final commit SHA.

---

### User Story 4 - Visible Status From One Command (DEFERRED to follow-up)

**Status**: Deferred out of scope for this iteration. The CLI status
surface (`speckit-orca status --sessions`) will land in a follow-up PR.
017 ships the session primitive (`session.py`) and the Matriarch
completion gates; operators can inspect presence directly via the
library API and the `.specify/orca/sessions/*.json` files in the
meantime. The acceptance criteria below describe the eventual target
shape.

**Acceptance Scenarios** (deferred):

1. **Given** two active sessions and three registered lanes, **When**
   the operator runs `speckit-orca status --sessions`, **Then** a
   human-readable listing shows each session's agent, scope, duration,
   and last heartbeat.
2. **Given** a session is holding a lane while another agent tried to
   acquire it, **When** status is inspected, **Then** the conflict (if
   any) is surfaced.

---

### Edge Cases

- **Session file corrupted**: A session file with unparseable JSON is
  treated as stale and reaped — no hard error.
- **Clock skew between hosts**: Heartbeat timestamps are UTC ISO-8601.
  Comparison uses the reading host's clock. TTL is generous (5 min)
  enough to tolerate normal skew.
- **Concurrent lock contention**: Session writes use `flock` on a
  lock file in the sessions dir. Timeout is 5 seconds. Callers that
  time out get a `TimeoutError` — not silently corrupted state.
- **Worktree at project root**: If worktree_path equals the project
  root (normal non-worktree run), the WORKTREE_ESCAPED check passes —
  "escaped" only triggers for paths that are neither the project root
  nor under `.specify/orca/worktrees/`.
- **Lane completed on a different machine than where it was registered**:
  The commit-check compares SHAs, not hosts. Register on machine A,
  push commits, complete on machine B — works.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Every Orca command that modifies Matriarch state MUST
  write a session heartbeat on entry and remove the session file on
  clean exit.
- **FR-002**: Session files MUST live under
  `.specify/orca/sessions/<session-id>.json`, one per active session.
- **FR-003**: Sessions MUST auto-reap when their last heartbeat is
  older than a configurable TTL (default 300 seconds / 5 minutes).
- **FR-004**: `matriarch.register_lane` MUST reject registration if
  another active session's scope overlaps the proposed lane.
  Rejection MUST name the holding session.
- **FR-005**: A new `matriarch.mark_lane_complete(lane_id, ...)`
  operation MUST enforce four preconditions:
    1. At least one commit exists on the lane's branch since the
       registration SHA (`LANE_NO_COMMITS` on failure).
    2. `review-code.md` exists in the lane's feature directory
       (`LANE_REVIEW_MISSING` on failure).
    3. The lane's worktree_path is inside
       `.specify/orca/worktrees/` OR equals the repo root
       (`LANE_WORKTREE_ESCAPED` on failure).
    4. Lane currently exists and is not already in a terminal state
       (`LANE_ALREADY_COMPLETE` on failure).
- **FR-006**: `register_lane` MUST record the current HEAD SHA as
  `registered_at_sha` so completion can diff against it.
- **FR-007**: All gate failures MUST raise `MatriarchError` with an
  error-code prefix (e.g., `LANE_NO_COMMITS: ...`) so callers and
  operators can switch on the code programmatically.
- **FR-008** (DEFERRED): `speckit-orca status` will gain a sessions
  view listing every active session with agent, scope, started, and
  last heartbeat. The CLI surface is deferred to a follow-up PR; 017
  only requires the session primitive and matriarch gates. Operators
  can list sessions via the library API
  (`speckit_orca.session.list_active_sessions`) until the CLI ships.
- **FR-009**: Session operations MUST use `flock`-backed advisory
  locking on `.specify/orca/sessions/.lock` to tolerate concurrent
  writers.
- **FR-010**: Session file writes MUST be atomic (tempfile + rename)
  so concurrent readers never observe a partial file.
- **FR-011**: Presence and gates MUST NOT require any external
  daemon, network calls, or dependencies outside the Python stdlib.

### Non-Functional Requirements

- **NFR-001**: Session file write + heartbeat update SHOULD complete in
  under 50ms on a warm SSD so adding it to every command call does not
  create operator-visible latency.
- **NFR-002**: Reap operations SHOULD run opportunistically (on every
  session operation), not on a timer.
- **NFR-003**: All new runtime code MUST have unit tests covering the
  stale-reap, concurrent-registration-conflict, and gate-rejection
  paths at minimum.
- **NFR-004**: The feature MUST be backwards-compatible with existing
  LaneRecords — old records without `registered_at_sha` MUST still load
  and MUST gracefully degrade the commit-check (skip it with a warning,
  don't crash).

## Design Decisions

### 1. Filesystem-backed, not daemon-backed

Presence is tracked via short-lived JSON files in a well-known directory
rather than a long-running process. Rationale: zero infrastructure,
trivial to inspect with `ls` and `cat`, no cross-platform daemon
concerns, survives machine reboots cleanly (stale files get reaped on
next access).

Rejected alternative: a `speckit-orca daemon` process emitting
heartbeats. Added complexity with no operational benefit at this scale.

### 2. TTL-based reap, no explicit session termination required

A session that dies (Ctrl-C, crash, network drop) cannot reliably clean
up after itself. Reap-on-access with a generous TTL handles this
without requiring cooperation.

### 3. Scope overlap semantics

Scopes conflict when they name the same `lane_id` OR same `feature_dir`.
Worktree paths alone do not conflict — two agents can inspect the same
directory read-only. Conflict requires intent-to-work scope, not mere
filesystem co-location.

### 4. Error codes as string prefixes, not enum

`MatriarchError("LANE_NO_COMMITS: lane X has no commits since registration at <sha>")`.
Callers switch on `str(err).startswith("LANE_NO_COMMITS:")`. Simpler than
an enum hierarchy; aligns with how spec-kitty's orchestrator-api codes
work (see their commands.py).

### 5. Gate checks deferred to mark_lane_complete

Gates don't fire on every operation — only on the one that claims
completion. This keeps intermediate operations (heartbeat, send
mailbox event) cheap and avoids false rejections during normal work.

## Out of Scope (Deferred)

- **User Story 4 / FR-008 `speckit-orca status --sessions` CLI
  surface**: deferred to a follow-up PR. Presence data is exposed via
  the library API (`list_active_sessions`) and direct filesystem
  inspection of `.specify/orca/sessions/*.json` in the meantime.
- Cross-machine presence (e.g., operator on Mac sees agent on
  Linux workstation). v1 is single-host.
- Session-to-session messaging beyond what Matriarch mailbox
  already supports.
- Visual TUI dashboard for active sessions — `speckit-orca status
  --sessions` plain output is enough.
- Auto-resume of crashed lanes based on presence data.
- Integration with external job schedulers (tmux, systemd, etc.).

## Dependencies

- `005-orca-flow-state` — read-only, for feature_dir resolution
- `010-orca-matriarch` — extends LaneRecord with `registered_at_sha`,
  adds gate checks to register_lane, adds mark_lane_complete
- No modifications to `013-spec-lite` or `015-brownfield-adoption`
  guards (those fire before presence checks)

## Success Criteria

The feature is successful when:

1. The mneme failure mode is mechanically impossible: agents cannot
   mark a lane complete without commits, reviews, and a managed worktree.
2. Two concurrent Orca sessions on the same project are visible to each
   other via the session library API (`list_active_sessions`) and, in
   the follow-up PR, via `speckit-orca status --sessions`.
3. A crashed agent's phantom lock is reaped within 5 minutes.
4. All new code ships with tests covering every `LANE_*` rejection path.

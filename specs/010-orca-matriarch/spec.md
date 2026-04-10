# Feature Specification: Orca Matriarch

**Feature Branch**: `010-orca-matriarch`  
**Created**: 2026-04-09  
**Status**: Draft  
**Input**: User description: "Add a careful multi-spec orchestration layer so Orca can manage multiple feature implementations, agents, worktrees, and review gates without requiring manual human coordination for every lane."

## Context

The current workflow upgrade is already exercising a coordination problem:
multiple specs can be active at once, dependencies matter, and humans are still
manually tracking which lane owns what. `orca-yolo` targets one feature run.
`orca-matriarch` is the higher-level supervisor that coordinates multiple
feature runs safely.

This feature must be treated conservatively. A weak implementation would create
automation theater and hide real blockers. The first version should emphasize
visibility, dependency awareness, lane assignment, and gate tracking over
aggressive autonomous control.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Coordinate Multiple Spec Implementations Without Manual Juggling (Priority: P1)

A maintainer is running several Orca feature lanes in parallel and wants one
system to track ownership, dependencies, and next actions so they do not have
to manage every spec manually.

**Why this priority**: This is the direct operational pain the feature exists
to solve.

**Independent Test**: Start multiple feature lanes with distinct dependencies
and verify Orca can show which lanes are active, blocked, review-ready, or
waiting on another spec.

**Acceptance Scenarios**:

1. **Given** multiple feature specs exist with implementation work in flight,
   **When** the maintainer inspects Matriarch state,
   **Then** Orca can show each lane's current stage, owner/agent, and blocker
   state from durable records.
2. **Given** one feature depends on another,
   **When** the upstream feature is incomplete,
   **Then** Matriarch marks the downstream lane as blocked instead of pretending
   it can progress independently.

---

### User Story 2 - Assign Worktrees And Agents Deliberately (Priority: P1)

A maintainer wants Orca to coordinate agent and worktree assignment so parallel
execution is structured instead of ad hoc.

**Why this priority**: Parallel work without explicit assignment is where lane
drift and duplicate effort begin.

**Independent Test**: Create multiple feature lanes and verify Matriarch can
record or recommend agent/worktree assignment without overwriting lane
boundaries.

**Acceptance Scenarios**:

1. **Given** a feature lane requires isolated implementation,
   **When** Matriarch assigns or records a worktree,
   **Then** the lane metadata links the feature, branch, and worktree identity.
2. **Given** multiple agents are available,
   **When** Matriarch records assignments,
   **Then** each active lane has a clear responsible agent or lane owner.

---

### User Story 3 - Aggregate Review Gates And Merge Readiness (Priority: P2)

A maintainer wants one place to see which active specs are implementation-ready,
review-ready, PR-ready, or blocked by findings.

**Why this priority**: Coordination only becomes truly useful when it exposes
quality gates rather than just task lists.

**Independent Test**: Update multiple features through implementation and
review, then verify Matriarch can summarize per-lane readiness from durable
artifacts instead of chat memory.

**Acceptance Scenarios**:

1. **Given** one lane has passing review artifacts and another does not,
   **When** Matriarch computes readiness,
   **Then** it distinguishes PR-ready work from blocked work using durable
   evidence.
2. **Given** a review stage is missing,
   **When** Matriarch summarizes the lane,
   **Then** it records the missing gate explicitly instead of inferring success.

### Edge Cases

- What happens if a lane is manually edited outside Matriarch? The system MUST
  detect or tolerate drift rather than assuming exclusive control.
- What happens if one agent abandons a lane? Matriarch MUST preserve durable
  lane state so reassignment is possible.
- What happens if dependencies change mid-stream? Matriarch MUST reflect the
  updated graph instead of preserving stale assumptions.
- What happens if a user wants to keep full manual control? The first version
  MUST support visibility and structured coordination without requiring
  autonomous execution.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Orca MUST define a multi-spec orchestration model for coordinating
  multiple feature lanes.
- **FR-002**: `orca-matriarch` MUST track lane identity, stage, ownership, and
  blocker state from durable artifacts.
- **FR-003**: `orca-matriarch` MUST support explicit dependency relationships
  between feature lanes.
- **FR-004**: `orca-matriarch` MUST integrate with worktree-aware execution
  without requiring every lane to use a worktree.
- **FR-005**: `orca-matriarch` MUST integrate with `005-orca-flow-state` for
  per-lane stage visibility.
- **FR-006**: `orca-matriarch` MUST integrate with `006-orca-review-artifacts`
  for review and readiness tracking.
- **FR-007**: `orca-matriarch` MUST integrate with `007-orca-context-handoffs`
  when lane ownership or session context changes.
- **FR-008**: `orca-matriarch` SHOULD integrate with `009-orca-yolo` as a
  single-lane execution worker, but MUST NOT require `009` for the first
  version's coordination value.
- **FR-009**: The first version MUST prioritize observability and safe
  coordination over aggressive autonomy.
- **FR-010**: The system MUST remain provider-agnostic and represent agent
  choices explicitly rather than encoding provider-specific behavior.

### Key Entities *(include if feature involves data)*

- **Managed Lane**: One active feature/spec lane under Matriarch supervision.
- **Lane Assignment**: The responsible agent, worktree, and branch metadata for
  one managed lane.
- **Lane Dependency**: A durable relationship indicating one lane cannot
  advance until another reaches a required state.
- **Lane Readiness**: The summarized implementation/review/PR state derived
  from durable artifacts.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A maintainer can inspect one durable view and understand the
  state of multiple active feature lanes.
- **SC-002**: Downstream lanes can be marked blocked by explicit dependencies
  instead of relying on human memory.
- **SC-003**: Lane assignment and review-readiness are discoverable without
  reconstructing chat history.

## Documentation Impact *(mandatory)*

- **README Impact**: Required
- **Why**: This feature adds a new supervisory workflow layer for multi-spec coordination, lane ownership, and readiness tracking.
- **Expected Updates**: `README.md`, program/coordination docs, future Matriarch command docs

## Assumptions

- `004-orca-workflow-system-upgrade` remains the umbrella dependency and wave
  authority.
- `005-orca-flow-state`, `006-orca-review-artifacts`, and
  `007-orca-context-handoffs` provide the lower-layer contracts Matriarch
  consumes.
- `009-orca-yolo` may later serve as a worker/runtime for one lane, but this
  feature should deliver coordination value even before YOLO is fully mature.

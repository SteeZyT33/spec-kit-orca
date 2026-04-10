# Tasks: Orca Review Artifacts

**Input**: Design documents from `/specs/006-orca-review-artifacts/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/, quickstart.md

**Tests**: This feature uses verification-driven development. Manual artifact checks are the primary end-to-end proof, with doc/runtime consistency checks where useful.

**Organization**: Tasks are grouped by user story so review-artifact architecture can be introduced incrementally: explicit stage evidence first, then summary/index behavior, then ownership polish for later systems.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g. US1, US2, US3)
- Include exact file paths in descriptions

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Prepare the review-artifact contracts and current review surfaces for implementation.

- [ ] T001 Review `specs/006-orca-review-artifacts/spec.md`, `specs/006-orca-review-artifacts/plan.md`, and `specs/006-orca-review-artifacts/contracts/` for implementation readiness
- [ ] T002 [P] Review `commands/code-review.md`, `commands/cross-review.md`, `commands/pr-review.md`, `commands/self-review.md`, and `templates/review-template.md` against the planned two-layer artifact model
- [ ] T003 [P] Document any current `review.md` assumptions in `README.md` that must be updated during implementation

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Lock the artifact set, ownership rules, and summary/index contract before command changes

**⚠️ CRITICAL**: No user story work should begin until these rules are stable

- [ ] T004 Finalize the preferred artifact set in `specs/006-orca-review-artifacts/contracts/review-artifact-files.md`
- [ ] T005 Finalize stage ownership rules in `specs/006-orca-review-artifacts/contracts/review-artifact-ownership.md`
- [ ] T006 Finalize summary/index responsibilities in `specs/006-orca-review-artifacts/contracts/review-summary-index.md`
- [ ] T007 Align `specs/006-orca-review-artifacts/data-model.md` with the finalized artifact and ownership contracts

**Checkpoint**: Review-artifact contracts are stable enough to drive command updates without ambiguous ownership.

---

## Phase 3: User Story 1 - Review Stages Leave Clear Durable Evidence (Priority: P1) 🎯 MVP

**Goal**: Make major Orca review stages leave explicit durable evidence instead of collapsing into one ambiguous file.

**Independent Test**: Simulate or run code-review, cross-review, and pr-review behavior and verify stage-specific artifacts exist or are clearly owned.

### Implementation for User Story 1

- [ ] T008 [US1] Update `commands/code-review.md` so `speckit.orca.code-review` owns `review-code.md` as its primary durable artifact
- [ ] T009 [US1] Update `commands/cross-review.md` so `speckit.orca.cross-review` owns `review-cross.md` as its primary durable artifact
- [ ] T010 [US1] Update `commands/pr-review.md` so `speckit.orca.pr-review` owns `review-pr.md` as its primary durable artifact
- [ ] T011 [US1] Update `commands/self-review.md` to reinforce that `self-review.md` remains a separate process artifact rather than part of the implementation-review bundle
- [ ] T012 [US1] Manually verify quickstart Scenarios 1 through 4 using `specs/006-orca-review-artifacts/quickstart.md`

**Checkpoint**: Each major review command has a clear primary durable artifact.

---

## Phase 4: User Story 2 - A Reader Can Understand Review Status From One Entry Point (Priority: P1)

**Goal**: Make `review.md` work as a human-readable summary/index without
collapsing the durable stage evidence back into one ambiguous file.

**Independent Test**: A reader can open `review.md` and quickly identify which
review stages exist, which are missing, and where the detailed findings live.

### Implementation for User Story 2

- [ ] T013 [US2] Update `templates/review-template.md` to reflect `review.md` as an umbrella summary/index instead of the only authoritative review record
- [ ] T014 [US2] Add explicit stage-artifact references and status-summary behavior to `templates/review-template.md`
- [ ] T015 [US2] Update `README.md` to describe the new review artifact architecture and how `review.md` relates to stage artifacts
- [ ] T016 [US2] Manually verify quickstart Scenario 5 using `specs/006-orca-review-artifacts/quickstart.md`

**Checkpoint**: Human readers can use `review.md` as the summary/index layer
without losing access to stage-specific evidence.

---

## Phase 5: User Story 3 - Later Orca Systems Can Consume Review Evidence Reliably (Priority: P1)

**Goal**: Define the detection and shape contracts that later Orca systems use
to reason about review progress without parsing one ambiguous umbrella file.

**Independent Test**: A later consumer can determine whether code review,
cross-review, or PR review is present by applying documented artifact rules
alone.

### Implementation for User Story 3

- [ ] T017 [US3] Add the stage-detection contract to `specs/006-orca-review-artifacts/contracts/review-artifact-files.md` so later consumers can distinguish `present`, `missing`, and `summary_only`
- [ ] T018 [US3] Clarify in `specs/006-orca-review-artifacts/data-model.md` that review-artifact fields are conceptual unless a later file-encoding contract is introduced
- [ ] T019 [US3] Update `commands/self-review.md` so self-review loads `review-code.md`, `review-cross.md`, and `review-pr.md` alongside `review.md` when they exist
- [ ] T020 [US3] Manually verify that a later consumer can determine review-stage presence from the documented artifact rules without treating `review.md` as the only source of truth

**Checkpoint**: Later Orca systems have a stable artifact-detection contract
for review progress.

---

## Phase 6: User Story 4 - Cross-Review And PR Review Stay Distinguishable (Priority: P2)

**Goal**: Ensure cross-review and PR review evidence remain separate from each
other and from code review evidence.

**Independent Test**: Review artifacts make it obvious whether a finding came
from implementation review, alternate-agent review, or PR lifecycle handling.

### Implementation for User Story 4

- [ ] T021 [US4] Tighten `commands/cross-review.md` so cross-review output and append behavior target `review-cross.md` distinctly from code review output
- [ ] T022 [US4] Tighten `commands/pr-review.md` so PR lifecycle, comment disposition, and post-merge evidence target `review-pr.md` distinctly from code-review findings
- [ ] T023 [US4] Update `specs/006-orca-review-artifacts/contracts/review-artifact-files.md` if implementation decisions refine the distinction between `review-cross.md` and `review-pr.md`
- [ ] T024 [US4] Manually verify that cross-review and PR-review evidence remain distinguishable in the resulting artifact set

**Checkpoint**: Cross-review and PR review are durably separated from code
review and from each other.

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Final consistency, migration clarity, and verification across the feature

- [ ] T025 [P] Update `specs/006-orca-review-artifacts/contracts/review-summary-index.md` and `specs/006-orca-review-artifacts/contracts/review-artifact-ownership.md` if implementation details shifted
- [ ] T026 [P] Run a command-doc consistency pass across `commands/code-review.md`, `commands/cross-review.md`, `commands/pr-review.md`, `commands/self-review.md`, and `README.md`
- [ ] T027 Run the full quickstart validation flow in `specs/006-orca-review-artifacts/quickstart.md`, including legacy-migration coverage, and record the verification evidence in `specs/006-orca-review-artifacts/tasks.md` or commit notes
- [ ] T028 Run final verification via `git diff --check` and `bash -n` on any touched shell wrappers if runtime glue was added

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: Can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion
- **User Story 1 (Phase 3)**: Depends on Foundational completion
- **User Story 2 (Phase 4)**: Depends on User Story 1 because summary/index behavior depends on stage artifact ownership being defined
- **User Story 3 (Phase 5)**: Depends on User Story 1 and benefits from User Story 2 summary/index alignment
- **Polish (Phase 7)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Delivers the MVP by making review-stage ownership explicit
- **User Story 2 (P1)**: Builds on US1 and makes the summary/index layer usable for human readers
- **User Story 3 (P1)**: Builds on US1 and defines the downstream artifact-detection contract for later Orca systems
- **User Story 4 (P2)**: Refines the distinction between review stages for cleaner evidence

### Within Each User Story

- Contract finalization before command updates
- Command ownership before summary/index template changes
- Distinction polishing before final verification

### Parallel Opportunities

- T002 and T003 can run in parallel during Setup
- T004, T005, and T006 can run in parallel before T007 aligns the data model
- T025 and T026 can run in parallel during Polish

---

## Parallel Example: User Story 1

```bash
# Parallel command ownership updates once foundational contracts are stable:
Task: "Update commands/code-review.md so speckit.orca.code-review owns review-code.md"
Task: "Update commands/cross-review.md so speckit.orca.cross-review owns review-cross.md"
Task: "Update commands/pr-review.md so speckit.orca.pr-review owns review-pr.md"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Setup
2. Complete Foundational contract alignment
3. Complete User Story 1 command ownership updates
4. Stop and validate that major review stages now have distinct durable artifacts

### Incremental Delivery

1. Define explicit review artifact ownership
2. Add summary/index behavior
3. Tighten cross-review and PR review distinction
4. Finish with docs and verification

### Out Of Scope In This Feature

- full flow-state implementation
- cross-review agent expansion
- historical migration of all old `review.md` files
- redesigning every review heuristic or pass

---

## Notes

- Keep `review.md` as summary/index, not as the only source of truth
- Keep `self-review.md` separate from implementation-review artifacts
- Prefer additive migration over disruptive replacement

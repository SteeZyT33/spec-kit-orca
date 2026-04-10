# Tasks: Orca Capability Packs

**Input**: Design documents from `/specs/008-orca-capability-packs/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/, quickstart.md

**Tests**: This feature uses document-level validation and optional config/manifest checks if activation support is introduced.

**Organization**: Tasks are grouped by user story so the capability-pack model can be delivered incrementally: first the pack model, then activation semantics, then alignment with the upgrade program and downstream orchestration.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g. US1, US2, US3)
- Include exact file paths in descriptions

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Align the feature with the repomix harvest and current Orca subsystem boundaries before refining the model.

- [ ] T001 Review `specs/008-orca-capability-packs/spec.md`, `specs/008-orca-capability-packs/brainstorm.md`, and `specs/008-orca-capability-packs/plan.md` for scope clarity
- [ ] T002 [P] Review `docs/orca-harvest-matrix.md` and `specs/004-orca-workflow-system-upgrade/` against `008` so the pack model stays aligned with the upgrade program
- [ ] T003 [P] Review `extension.yml`, `config-template.yml`, and representative Orca commands to understand where pack boundaries may matter later

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Establish the capability-pack model and core-vs-pack rules all later work depends on

**⚠️ CRITICAL**: No user story work should begin until the pack model and boundary rules are coherent

- [ ] T004 Refine `specs/008-orca-capability-packs/contracts/capability-pack-model.md` to define the minimum pack shape
- [ ] T005 Implement activation semantics in `specs/008-orca-capability-packs/contracts/pack-activation.md`
- [ ] T006 Implement explicit boundary rules in `specs/008-orca-capability-packs/contracts/core-vs-pack-boundaries.md`
- [ ] T007 Update `specs/008-orca-capability-packs/data-model.md` so pack entities and activation rules match the contracts exactly

**Checkpoint**: `008` has a stable capability-pack model, activation model, and boundary contract.

---

## Phase 3: User Story 1 - Optional Workflow Capabilities Stay Explicit (Priority: P1) 🎯 MVP

**Goal**: Make optional Orca behavior explicit enough that core commands stop absorbing every subsystem concern directly.

**Independent Test**: Define at least one realistic pack and verify its role, affected commands, and prerequisites are explicit without bloating the core workflow model.

### Implementation for User Story 1

- [ ] T008 [US1] Refine `specs/008-orca-capability-packs/spec.md` so the role of capability packs versus core behavior is explicit
- [ ] T009 [US1] Populate `specs/008-orca-capability-packs/contracts/core-vs-pack-boundaries.md` with realistic initial pack candidates tied to Orca subsystems
- [ ] T010 [US1] Update `specs/008-orca-capability-packs/quickstart.md` to validate that the core command set remains understandable without hidden pack logic
- [ ] T011 [US1] Manually verify that the pack model is clearly simpler than Spex traits-as-implemented and still useful

**Checkpoint**: Orca has an explicit, lightweight pack model for optional behavior.

---

## Phase 4: User Story 2 - Activation Semantics Stay Inspectable (Priority: P1)

**Goal**: Ensure packs can be understood and eventually activated without becoming opaque runtime magic.

**Independent Test**: Inspect the pack activation contract and verify activation modes and boundaries are explicit and inspectable.

### Implementation for User Story 2

- [ ] T012 [US2] Refine `specs/008-orca-capability-packs/contracts/pack-activation.md` so activation semantics are explicit and conservative
- [ ] T013 [US2] Update `specs/008-orca-capability-packs/plan.md` and `specs/008-orca-capability-packs/research.md` to clarify whether the first version is docs-first or runtime-visible
- [ ] T014 [US2] Add initial activation examples to `specs/008-orca-capability-packs/quickstart.md`
- [ ] T015 [US2] Manually verify that activation semantics do not make the core command set unreadable or unpredictable

**Checkpoint**: Capability packs now have an inspectable activation model.

---

## Phase 5: User Story 3 - Downstream Orchestration Can Consume Packs Safely (Priority: P2)

**Goal**: Make capability packs a real upstream architectural layer for later subsystems such as `009-orca-yolo`.

**Independent Test**: Review the `008` artifacts and verify later orchestration can rely on pack boundaries without making packs the foundation themselves.

### Implementation for User Story 3

- [ ] T016 [US3] Update `specs/008-orca-capability-packs/contracts/core-vs-pack-boundaries.md` to classify `yolo` explicitly as downstream rather than foundational
- [ ] T017 [US3] Reconcile `specs/008-orca-capability-packs/` with `specs/004-orca-workflow-system-upgrade/contracts/subsystem-integration.md` so pack assumptions are explicit
- [ ] T018 [US3] Update `specs/008-orca-capability-packs/quickstart.md` to validate downstream-pack reasoning
- [ ] T019 [US3] Manually verify that the pack model supports later orchestration without becoming a trait engine

**Checkpoint**: `008` is now a usable upstream architectural layer for later optional and downstream Orca behavior.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final consistency and alignment work across the pack model and the upgrade program

- [ ] T020 [P] Update `specs/008-orca-capability-packs/research.md` and `specs/008-orca-capability-packs/plan.md` if contract assumptions changed during refinement
- [ ] T021 Update `specs/004-orca-workflow-system-upgrade/contracts/subsystem-integration.md` only if `008` changes its promised role materially
- [ ] T022 Run the full document-level validation flow in `specs/008-orca-capability-packs/quickstart.md` and record the evidence in `specs/008-orca-capability-packs/tasks.md` or commit notes
- [ ] T023 [P] Run final consistency checks across `specs/008-orca-capability-packs/`, related upgrade artifacts, and `git diff --check`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: Can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion
- **User Story 1 (Phase 3)**: Depends on Foundational completion
- **User Story 2 (Phase 4)**: Depends on User Story 1 because activation semantics require a stable pack model
- **User Story 3 (Phase 5)**: Depends on User Stories 1 and 2 because downstream-pack behavior needs stable pack and activation boundaries
- **Polish (Phase 6)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Establishes the MVP pack model
- **User Story 2 (P1)**: Adds inspectable activation semantics
- **User Story 3 (P2)**: Makes packs safe to consume downstream

### Within Each User Story

- Pack model before activation semantics
- Activation semantics before downstream orchestration assumptions
- Manual validation at the end of each story

### Parallel Opportunities

- T002 and T003 can run in parallel during Setup
- T005 and T006 can run in parallel once T004 establishes the minimum pack model
- T020 and T023 can run in parallel during Polish

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Setup
2. Complete Foundational pack contracts
3. Complete User Story 1 explicit pack model
4. Stop and validate that Orca can describe optional behavior without core-command sprawl

### Incremental Delivery

1. Define the pack model
2. Define conservative activation semantics
3. Align packs with downstream orchestration
4. Finish with consistency validation

### Out Of Scope In This Feature

- copying Spex traits directly
- building a giant trait runtime
- implementing `009-orca-yolo`
- hiding core Orca behavior behind pack indirection

---

## Notes

- `008` is an architecture-layer feature, not a trait-engine feature
- keep it simpler than Spex while still making optional behavior explicit
- the value of this feature is preventing core-command sprawl

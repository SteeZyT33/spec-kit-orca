# Tasks: Multi-SDD Layer — Phase 1 (Adapter Interface + SpecKit Adapter)

**Input**: `specs/016-multi-sdd-layer/spec.md`, `specs/016-multi-sdd-layer/plan.md`, `specs/016-multi-sdd-layer/brainstorm.md`
**Prerequisites**: spec.md and plan.md reviewed. Current `flow_state.py` test suite green on `main`.
**TDD**: All implementation tasks follow red-green-refactor. Every GREEN has a RED before it.

**Organization**: Tasks follow the plan's sub-phase sequence (A through D). Phase 2 and Phase 3 of the broader multi-SDD program are out of scope here and have no tasks in this file.

## Format: `[ID] [P?] Description`

- **[P]**: Can run in parallel (different files, no dependencies)

---

## Phase A: Interface and Dataclasses (TDD)

**Purpose**: Create `src/speckit_orca/sdd_adapter.py` with the ABC and the four dataclasses. No concrete adapter yet.

**Target file**: `src/speckit_orca/sdd_adapter.py` (new)
**Test file**: `tests/test_sdd_adapter.py` (new)

- [ ] T001 RED: Write `test_feature_handle_fields` — assert `FeatureHandle` has fields `feature_id`, `display_name`, `root_path`, `adapter_name` with the types in plan section Design Decisions §1. Fails because module does not exist yet.
- [ ] T002 RED: Write `test_normalized_task_fields` — assert `NormalizedTask` has `task_id`, `text`, `completed`, `assignee` with correct types.
- [ ] T003 RED: Write `test_stage_progress_fields` — assert `StageProgress` has `stage`, `status`, `evidence_sources`, `notes`.
- [ ] T004 RED: Write `test_normalized_artifacts_fields` — assert `NormalizedArtifacts` carries the full field list from plan section Design Decisions §1, including `artifacts`, `tasks`, `task_summary_data`, `review_evidence`, `linked_brainstorms`, `worktree_lanes`, `ambiguities`, `notes`.
- [ ] T005 RED: Write `test_sdd_adapter_is_abstract` — `SddAdapter()` without override raises `TypeError`; a subclass implementing only `detect` still raises `TypeError` at instantiation.
- [ ] T006 RED: Write `test_sdd_adapter_required_methods` — a subclass that implements all five abstract methods (`detect`, `list_features`, `load_feature`, `compute_stage`, `id_for_path`) with trivial stubs can be instantiated and satisfies `isinstance(obj, SddAdapter)`.
- [ ] T007 GREEN: Create `src/speckit_orca/sdd_adapter.py` with the four dataclasses and the abstract base class. Minimal code to make T001-T006 pass. No `SpecKitAdapter` yet.

**Checkpoint**: Adapter module exists, dataclasses and ABC are defined, tests T001-T006 pass. Existing `tests/test_flow_state_*.py` still untouched and green.

---

## Phase B: SpecKitAdapter Implementation (TDD)

**Purpose**: Implement `SpecKitAdapter` by moving the spec-kit parsing logic out of `flow_state.py`. Original `flow_state.py` helpers stay in place during this phase; they are deleted in Phase C.

**Target file**: `src/speckit_orca/sdd_adapter.py`
**Test file**: `tests/test_sdd_adapter.py`

- [ ] T008 RED: Write `test_spec_kit_adapter_name` — `SpecKitAdapter().name == "spec-kit"`.
- [ ] T009 RED: Write `test_spec_kit_detect_true` — synthetic tree with `specs/001-foo/spec.md`; `detect(repo_root)` returns `True`.
- [ ] T010 RED: Write `test_spec_kit_detect_false` — synthetic tree with no `specs/` dir; `detect` returns `False`.
- [ ] T011 RED: Write `test_spec_kit_list_features` — synthetic tree with two feature dirs; `list_features` returns two `FeatureHandle` entries with `feature_id` matching the directory names and `adapter_name == "spec-kit"`.
- [ ] T012 RED: Write `test_spec_kit_id_for_path_inside_feature` — path under `specs/042-widget/anything.md` returns `"042-widget"`.
- [ ] T013 RED: Write `test_spec_kit_id_for_path_outside` — path under `docs/readme.md` returns `None`.
- [ ] T014 RED: Write `test_spec_kit_load_feature_empty_dir` — fixture feature dir with no artifacts; `load_feature` returns `NormalizedArtifacts` with empty tasks, empty `linked_brainstorms`, empty `worktree_lanes`, and review evidence with `exists=False` on each sub-evidence.
- [ ] T015 RED: Write `test_spec_kit_load_feature_full_tree` — fixture with `spec.md`, `plan.md`, `tasks.md` (including `T001`, `T002 [@agent]`, `- [x] T003`), and `review-spec.md` with a `- status: ready` line and `## Cross Pass (...)`. Assert: `tasks` is length 3, one is `completed=True`, one has `assignee` set; `review_evidence.review_spec.verdict == "ready"` and `has_cross_pass == True`.
- [ ] T016 RED: Write `test_spec_kit_load_feature_matches_legacy` — for a realistic fixture, build a `FeatureEvidence` via `collect_feature_evidence` on the pre-refactor code path, convert `NormalizedArtifacts` back to an equivalent `FeatureEvidence`, and assert field-by-field equality. This is the zero-behavior-change gate at the adapter boundary.
- [ ] T017 RED: Write `test_spec_kit_compute_stage_order` — on a fixture with spec + plan + tasks present but no reviews, `compute_stage` returns `StageProgress` entries in spec-kit's nine-stage order with correct status flags.
- [ ] T018 GREEN: Implement `SpecKitAdapter` in `sdd_adapter.py`. Port `_parse_tasks`, `_parse_review_evidence`, `_find_linked_brainstorms`, `_load_worktree_lanes`, `_find_repo_root`, and the artifact filename list as adapter internals. Make T008-T017 pass.
- [ ] T019 REFACTOR: If the ported helpers share logic with what remains in `flow_state.py`, extract shared constants (regexes, verdict sets) to module-level attributes on `sdd_adapter.py` and have `flow_state.py` import them during the transition. Do not duplicate them.

**Checkpoint**: `SpecKitAdapter` is complete and tested in isolation. T016 in particular proves the adapter produces the same shape as the legacy code path. Existing `tests/test_flow_state_*.py` still green and untouched.

---

## Phase C: flow_state Refactor to Use Adapter (TDD)

**Purpose**: Rewire `collect_feature_evidence` to route through `SpecKitAdapter`. Delete the now-duplicated private helpers from `flow_state.py`. The test for success is that the existing test suite still passes with zero edits.

**Target file**: `src/speckit_orca/flow_state.py`
**Test files**: existing `tests/test_flow_state_*.py` (unchanged), plus new Phase C coverage in `tests/test_sdd_adapter.py`.

- [ ] T020 RED: Write `test_flow_state_uses_adapter` — monkeypatch the module-level `_SPEC_KIT_ADAPTER` to a spy subclass of `SpecKitAdapter`; call `compute_flow_state` on a fixture and assert the spy's `load_feature` was called exactly once. Fails because `flow_state.py` does not yet reference the adapter.
- [ ] T021 RED: Write `test_flow_state_no_speckit_path_literals` — import `src/speckit_orca/flow_state.py` as text and assert none of `"spec.md"`, `"plan.md"`, `"tasks.md"`, `"review-spec.md"`, `"review-code.md"`, `"review-pr.md"`, `"brainstorm.md"` appear as string literals. Fails on pre-refactor code.
- [ ] T022 RED: Write `test_compute_flow_state_byte_identical` — for each fixture feature directory in the repo (e.g., `specs/009-orca-yolo/`, `specs/013-spec-lite/`, `specs/005-orca-flow-state/`), compute `FlowStateResult.to_dict()` and assert it equals a golden snapshot captured from the pre-refactor code. Golden snapshots live under `tests/fixtures/flow_state_snapshots/` and are generated once from `main` before the refactor starts. Fails until the refactor is semantically equivalent.
- [ ] T023 GREEN: Refactor `flow_state.collect_feature_evidence` to instantiate a module-level `_SPEC_KIT_ADAPTER = SpecKitAdapter()` and obtain data via `adapter.load_feature(handle)`. Construct `FeatureEvidence` from the returned `NormalizedArtifacts`. Keep all other public surfaces unchanged.
- [ ] T024 GREEN: Delete `_parse_tasks`, `_parse_review_evidence`, `_parse_review_spec_evidence`, `_parse_review_code_evidence`, `_parse_review_pr_evidence`, `_find_linked_brainstorms`, `_load_worktree_lanes`, and the per-name artifact filename literals from `flow_state.py`. Any remaining reference must go through the adapter or an imported constant.
- [ ] T025 GREEN: Confirm T020, T021, T022 now pass.
- [ ] T026 REFACTOR: Audit `flow_state.py` for dead imports after the helper deletions. Remove any import that is no longer referenced.

**Checkpoint**: `flow_state.py` routes through the adapter. Spec-kit-specific filename literals live only in `sdd_adapter.py`. All existing tests still pass with zero edits.

---

## Phase D: Regression Verification

**Purpose**: No new code. Prove the zero-behavior-change guarantee with evidence. Each task here maps to a success criterion in `spec.md`.

- [ ] T027 Verify SC-001: run `uv run pytest tests/` from a clean working tree. Every test passes. Record count in the checkpoint note.
- [ ] T028 [P] Verify SC-002: for every directory under `specs/` that contains a `spec.md`, run `compute_flow_state(dir)` and assert the result equals the pre-refactor snapshot captured for T022. Scripted assertion; any mismatch fails the gate.
- [ ] T029 [P] Verify SC-003: run `python -m speckit_orca.flow_state <target> --format json` on each fixture target (feature directory, a spec-lite record, an adoption record) and diff stdout against pre-refactor captures. Diff must be empty on all targets.
- [ ] T030 [P] Verify SC-004: run a grep/AST check that spec-kit artifact filename literals (`"spec.md"`, `"plan.md"`, `"tasks.md"`, `"review-spec.md"`, `"review-code.md"`, `"review-pr.md"`, `"brainstorm.md"`) do not appear in `src/speckit_orca/flow_state.py`. Encode this as a test so regressions are caught by CI.
- [ ] T031 [P] Verify SC-005: confirm `tests/test_sdd_adapter.py` has at least one direct test for each of `SpecKitAdapter.detect`, `list_features`, `load_feature`, `compute_stage`, `id_for_path`, plus one test each for the four dataclasses.
- [ ] T032 [P] Verify SC-006: write a smoke test that imports each public name from `speckit_orca.flow_state` (`compute_flow_state`, `compute_spec_lite_state`, `compute_adoption_state`, `collect_feature_evidence`, `list_yolo_runs_for_feature`, `write_resume_metadata`, `FlowStateResult`, `FeatureEvidence`, `FlowMilestone`, `ReviewMilestone`, etc.) and asserts each is callable/usable. Fails if any public surface was accidentally removed or renamed.
- [ ] T033 Final sign-off: update this tasks file's checkpoint with test counts, commit the snapshot fixtures, confirm no changes to `commands/`, `extension.yml`, or docs outside `specs/016-multi-sdd-layer/`.

**Checkpoint**: Phase 1 complete. Refactor has landed with evidence. Phase 2 (OpenSpec adapter) is unblocked.

---

## Dependencies and Execution Order

### Phase Dependencies

- **Phase A** (Interface + dataclasses): foundational. Must complete before B.
- **Phase B** (SpecKitAdapter): depends on A. Must complete before C.
- **Phase C** (flow_state refactor): depends on B. Must complete before D.
- **Phase D** (Regression verification): depends on C. No new code; pure verification.

### Parallel Opportunities

- T001-T006 in Phase A can be drafted as one test file commit; they are sibling assertions in the same file.
- T009-T013 in Phase B can be written in parallel since each hits an independent adapter method.
- T028-T032 in Phase D are all verification-only and can run concurrently.

### TDD Execution Rule

Every GREEN task MUST have its RED counterpart committed and verified failing first. No production code without a failing test. This applies uniformly across Phases A, B, and C. Phase D has no GREEN tasks; it is verification only.

---

## Out of Scope (Deferred to Later Phases)

Phase 2 and Phase 3 of the multi-SDD program are entirely out of scope for this tasks file:

- OpenSpec adapter implementation.
- BMAD and Taskmaster detection stubs.
- Adapter registry, auto-detection, and `--adapter` CLI flag.
- Stage-kind enum and per-format stage mapping.
- Adapter-aware matriarch, yolo, brainstorm memory, context handoffs.
- Cross-format review model.
- README and docs updates announcing the adapter layer.
- Any change to `extension.yml`, commands, or user-facing prompts.

These will have their own specs (016 Phase 2, 016 Phase 3, or separate numbered specs as appropriate) and their own tasks files. Do not creep them into this phase.

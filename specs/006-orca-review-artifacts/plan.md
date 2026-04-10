# Implementation Plan: Orca Review Artifacts

**Branch**: `006-orca-review-artifacts` | **Date**: 2026-04-09 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/006-orca-review-artifacts/spec.md`

## Summary

Introduce a durable review-artifact system that separates major Orca review
stages into explicit artifacts while preserving `review.md` as an umbrella
summary and compatibility surface. The feature should define artifact ownership
for `code-review`, `cross-review`, `pr-review`, and `self-review`, make review
stages discoverable for later flow-state and orchestration, and reduce
ambiguity in current single-file review evidence.

The preferred direction is a two-layer model:

- stage-specific artifacts as the primary durable evidence
- `review.md` as the umbrella summary/index

## Technical Context

**Language/Version**: Markdown command docs, Bash launcher/runtime hooks, Python 3.10+ available for helper logic if needed  
**Primary Dependencies**: existing Orca review commands, `templates/review-template.md`, current review artifact conventions, Spec Kit repo layout  
**Storage**: feature-local Markdown review artifacts under each `specs/<feature>/` directory  
**Testing**: manual artifact-generation verification, command-doc consistency checks, `bash -n` for touched shell wrappers, and `uv run python -m py_compile` only if helper code is introduced  
**Target Platform**: local developer workstations using Orca in Spec Kit repos  
**Project Type**: workflow extension / command-doc plus artifact-contract repository  
**Performance Goals**: artifact generation and summary updates should remain effectively instant relative to the review work itself  
**Constraints**: preserve current Orca usability during migration, keep `self-review.md` distinct as a process artifact, avoid ambiguous dual ownership of the same review findings, stay provider-agnostic  
**Scale/Scope**: one feature directory at a time, with review evidence spanning spec, plan, code, cross-review, PR review, and self-review stages

## Constitution Check

### Pre-design gates

1. **Provider-agnostic orchestration**: pass. The artifact model is stage-based
   and does not rely on provider-specific review files.
2. **Spec-driven delivery**: pass. This feature is being specified and planned
   before command/runtime changes.
3. **Safe parallel work**: pass. Explicit artifact ownership reduces collisions
   across commands and later parallel work.
4. **Verification before convenience**: pass. The plan includes artifact-level
   verification rather than relying on assumptions about future consumers.
5. **Small, composable runtime surfaces**: pass. The design favors clear file
   contracts over adding opaque orchestration.

### Post-design check

The chosen design remains constitution-aligned because it:

- makes durable review evidence explicit
- supports later workflow composition without hidden state
- keeps the runtime surface file-based and inspectable

No constitution violations need justification.

## Project Structure

### Documentation (this feature)

```text
specs/006-orca-review-artifacts/
├── spec.md
├── brainstorm.md
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── review-artifact-ownership.md
│   ├── review-artifact-files.md
│   └── review-summary-index.md
└── tasks.md
```

### Source Code (repository root)

```text
commands/
├── code-review.md
├── cross-review.md
├── pr-review.md
└── self-review.md

templates/
└── review-template.md

README.md
```

**Structure Decision**: Keep the first implementation centered on command docs
and artifact contracts rather than introducing new runtime code unless the
artifact-update logic proves too brittle. The main problem here is ownership and
durable evidence shape, not heavy execution logic.

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| Two-layer artifact model (`review.md` plus stage artifacts) | Needed to balance migration safety with explicit durable stage evidence | A single-file model remains too ambiguous; a hard switch away from `review.md` is too disruptive |

## Research Decisions

### 1. Keep `review.md` as the umbrella layer

Decision: retain `review.md` as the summary/index and compatibility entrypoint,
but stop treating it as the only authoritative review artifact.

Rationale:

- lowers migration friction
- preserves current user familiarity
- still allows stage-specific artifacts for later systems

Alternatives considered:

- keep only `review.md`: simplest short-term, but fails the whole point of the
  feature
- drop `review.md` entirely: cleaner eventually, but too abrupt

### 2. Each review command should own one primary stage artifact

Decision: define one primary durable artifact per review stage, with
`self-review.md` remaining distinct from implementation review artifacts.

Rationale:

- reduces ambiguous ownership
- makes later flow-state consumption feasible
- supports clearer audit trails

Alternatives considered:

- shared writes everywhere: reproduces the current ambiguity

### 3. Stage-specific artifacts should be the machine-facing source of truth

Decision: later Orca systems should consume stage artifacts directly, while
`review.md` acts as the human-facing overview.

Rationale:

- cleaner future flow-state logic
- easier to reason about which review stages occurred

Alternatives considered:

- make `review.md` the machine-facing source forever: too ambiguous

### 4. Do not redesign all review logic in this feature

Decision: keep the scope on artifact architecture and command ownership rather
than trying to solve every review-behavior problem simultaneously.

Rationale:

- avoids turning this into a massive review-pipeline rewrite
- keeps later features such as cross-review agent selection and flow-state
  orthogonal

Alternatives considered:

- full review-system rewrite now: too broad and likely to drift

## Design Decisions

### 1. Recommended stage artifact set

Preferred initial artifact set:

- `review.md` — umbrella summary/index
- `review-spec.md` — spec-focused review evidence
- `review-plan.md` — planning/design review evidence
- `review-code.md` — implementation review evidence
- `review-cross.md` — alternate-agent or external adversarial review evidence
- `review-pr.md` — PR lifecycle and post-merge review evidence
- `self-review.md` — process retrospective, separate from implementation review

### 2. Summary/index behavior must be explicit

`review.md` should summarize:

- which stage artifacts exist
- latest review stage timestamps
- high-level review status
- key blockers or unresolved items

It should not silently absorb all detailed findings as the only long-term store.

### 3. Ownership must be command-specific

Recommended ownership:

- `code-review` owns `review-code.md`
- `cross-review` owns `review-cross.md`
- `pr-review` owns `review-pr.md`
- `self-review` owns `self-review.md`

Open design choice:

- whether spec/plan review artifacts are created by future dedicated review
  commands or by design-stage review flows such as `cross-review --scope design`

### 4. Migration can be additive first

The first version should allow existing `review.md` flows to keep working while
new stage artifacts are introduced and linked. Historical backfill can be
deferred.

## Implementation Phases

### Phase 0: Artifact contract design

Define:

- file naming
- summary/index responsibilities
- stage artifact ownership
- what counts as authoritative stage evidence

### Phase 1: Command contract updates

Update review command docs to:

- write or update their primary stage artifact
- update `review.md` as summary/index
- stop implying that `review.md` alone is the durable source of review truth

### Phase 2: Template and summary alignment

Update templates and README-facing documentation to match the new artifact
architecture.

### Phase 3: Verification and compatibility checks

Validate that:

- new review artifacts are discoverable
- summary/index behavior remains usable
- stage ownership is not ambiguous

## Verification Strategy

### Primary verification

Manual artifact checks:

1. simulate or run a code review and verify `review-code.md` plus summary update
2. simulate or run a cross-review and verify `review-cross.md` plus summary update
3. simulate or run a PR review and verify `review-pr.md` plus summary update
4. verify `self-review.md` remains distinct
5. verify a later reader can determine completed review stages without parsing
   one generic file only

### Secondary verification

- `git diff --check`
- `bash -n` for touched shell wrappers if any runtime shell glue is added
- command-doc consistency pass across review commands and README

## Risks

### 1. Duplicate or conflicting evidence

If both `review.md` and stage artifacts contain overlapping authoritative
details, they can drift.

Mitigation:

- define stage artifacts as the primary durable evidence
- keep `review.md` as summary/index

### 2. Partial migration confusion

Users may not know which artifact matters during the transition.

Mitigation:

- explicit artifact-ownership contract
- README and command-doc updates in the same feature

### 3. Over-fragmentation

Too many files can become noisy if the boundaries are not meaningful.

Mitigation:

- keep only stage-level splits that support real workflow-state value
- defer speculative artifacts

## Non-goals

- redesigning all review logic
- expanding cross-review agent support in this feature
- implementing full flow-state itself
- backfilling every historical `review.md` into split artifacts

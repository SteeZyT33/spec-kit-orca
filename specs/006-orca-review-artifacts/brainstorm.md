# Brainstorm

## Problem

Orca's review workflow has grown into multiple distinct review stages:

- `code-review`
- `cross-review`
- `pr-review`
- `self-review`

But the durable artifact model has not kept up. In practice:

- `code-review` appends to `review.md`
- `cross-review` also appends to `review.md`
- `pr-review` also appends to `review.md`
- `self-review` writes `self-review.md`

This creates three problems:

1. Review stages are conceptually distinct, but their evidence is not clearly
   separated.
2. Later Orca systems such as `flow-state` and `orca-yolo` will need to know
   which review gates happened without parsing one ambiguous umbrella file.
3. Human readers cannot quickly tell whether spec review, plan review, code
   review, PR review, or cross-review actually happened versus just being
   mentioned in a generic review log.

The repomix harvest from `cc-spex` sharpened this. Spex's advantage is not just
that it has more commands. It has clearer durable review-stage evidence.

## Desired Outcome

Orca should have a review artifact system where:

- each major review stage leaves explicit durable evidence
- later Orca systems can consume review-stage completion cleanly
- human readers can immediately see what was reviewed, when, and by which
  reviewer
- current Orca review commands stay usable without forcing a chaotic migration

The artifact model should support:

- stage-level review discoverability
- explicit cross-review evidence
- PR review evidence distinct from implementation review
- an eventual flow-state/status system
- later full-cycle orchestration

## Constraints

- Orca already has command docs and runtime behavior built around `review.md`,
  so a hard break would create churn.
- `self-review.md` already exists as a distinct process artifact and should stay
  distinct from implementation review artifacts.
- The system must remain provider-agnostic and should not inherit Claude- or
  Spex-specific file names blindly.
- The artifact model should stay simple enough that command docs and runtime
  updates remain understandable.
- This feature should define durable review boundaries, not redesign all review
  logic at the same time.

## Existing Context

Current Orca state:

- [code-review.md](/home/taylor/spec-kit-orca/commands/code-review.md) writes to
  `FEATURE_DIR/review.md`
- [cross-review.md](/home/taylor/spec-kit-orca/commands/cross-review.md) appends
  cross-harness findings to `review.md`
- [pr-review.md](/home/taylor/spec-kit-orca/commands/pr-review.md) also appends
  PR lifecycle evidence to `review.md`
- [templates/review-template.md](/home/taylor/spec-kit-orca/templates/review-template.md)
  is still shaped around one umbrella review artifact

Relevant harvested direction from repomix:

- split review artifacts are foundational to flow tracking
- review-stage evidence should be durable and binary enough for later systems to
  reason over
- review architecture is separate from review-agent selection

This feature also sits adjacent to:

- `003-cross-review-agent-selection`
- `005-orca-flow-state`
- `009-orca-yolo`

So the artifact model needs to be useful to those later features.

## Options Considered

### Option 1: Keep only one `review.md`, improve its internal sections

Keep the current umbrella artifact but enforce stronger stage labels and section
structure inside it.

Pros:

- lowest migration cost
- minimal command/runtime disruption
- keeps existing behavior familiar

Cons:

- later Orca systems still need to parse one large ambiguous file
- stage completion remains harder to detect cleanly
- human review discoverability improves only a little

### Option 2: Split into stage-specific artifacts and drop `review.md`

Move immediately to distinct files such as:

- `review-spec.md`
- `review-plan.md`
- `review-code.md`
- `review-cross.md`
- `review-pr.md`

Pros:

- strongest stage separation
- easiest future machine consumption
- closest to the repomix/Spex insight

Cons:

- bigger migration cost
- more command changes at once
- likely too disruptive for current Orca usage

### Option 3: Keep `review.md` as an umbrella index, add stage-specific artifacts

Introduce explicit stage review artifacts while retaining `review.md` as:

- an index
- a summary
- a compatibility surface

Example shape:

- `review.md` as umbrella summary and latest-state overview
- `review-spec.md`
- `review-plan.md`
- `review-code.md`
- `review-cross.md`
- `review-pr.md`
- `self-review.md` remains separate

Pros:

- strongest long-term model with manageable migration
- later systems can use stage artifacts directly
- humans still get one summary entrypoint
- existing commands can migrate incrementally

Cons:

- two-layer artifact model needs discipline
- risk of duplicated or conflicting content if ownership is not defined clearly

## Recommendation

Favor **Option 3**.

This is the best Orca move because it balances:

- durable stage evidence
- forward compatibility with `flow-state` and `orca-yolo`
- incremental migration from current `review.md` usage

Recommended artifact ownership:

- `review.md`: umbrella summary, review status overview, latest entrypoint
- `review-spec.md`: spec-focused review evidence
- `review-plan.md`: plan/design-focused review evidence
- `review-code.md`: implementation review evidence
- `review-cross.md`: external or alternate-agent review evidence
- `review-pr.md`: PR lifecycle evidence
- `self-review.md`: process retrospective only

Recommended rule:

- each command owns exactly one primary stage artifact
- `review.md` is generated or updated as the summary/index layer, not the only
  authoritative store of all findings

## Open Questions

- Should `code-review` own both `review-code.md` and summary updates to
  `review.md`, or should summary generation be centralized?
- Should `cross-review` remain a subsection in `review-code.md` when it is
  code-scoped, or should it always own `review-cross.md` regardless of scope?
- Do we also want `review-design.md` instead of separate `review-spec.md` and
  `review-plan.md`, or is the finer split worth it?
- How much historical migration do we want from older single-file `review.md`
  artifacts?
- Should `pr-review` become the owner of post-merge verification evidence even
  when no PR exists yet?

## Ready For Spec

This already has a draft spec, but the main missing work is architecture and
artifact-boundary refinement rather than basic problem framing. The right next
step is `/speckit.plan` for `006-orca-review-artifacts`, followed by task
generation once the primary artifact ownership model is locked.

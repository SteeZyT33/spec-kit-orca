# Orca Harvest Matrix

## Purpose

Sharpen the `cc-spex` harvest plan into a concrete take/adapt/avoid matrix for
Orca.

This document is informed by:

- targeted review of `/home/taylor/cc-spex`
- the packed repository view at `/home/taylor/cc-spex/repomix-output.xml`
- Orca's current direction as a provider-agnostic workflow system

The core conclusion is:

**Spex's advantage is not any one command. Its advantage is the way memory,
state, review, optional capability layers, and orchestration are made
persistent and composable.**

## What Repomix Clarified

The packed repo view makes several things more obvious than file-by-file
inspection:

1. `cc-spex` is a workflow operating system, not a command bundle.
2. `brainstorm/` is first-class product surface, not a side utility.
3. split review artifacts are foundational to flow tracking:
   - `REVIEW-SPEC.md`
   - `REVIEW-PLAN.md`
   - `REVIEW-CODE.md`
4. traits/overlays are Spex's main answer to workflow composition.
5. `ship` depends on durable state, review stages, and idea memory. It is not
   the real foundation.
6. Spex has an explicit self-evolution discipline:
   - sync reports
   - adoption notes
   - internal specs for its own workflow upgrades

This means Orca should think in terms of:

- memory
- state
- handoffs
- review architecture
- capability packs
- orchestration

not just "add a YOLO command."

## Harvest Matrix

### Take Directly

These ideas are structurally good enough to adopt with minimal conceptual
change.

#### 1. Brainstorm memory model

Take:

- numbered brainstorm docs
- `00-overview.md` index
- explicit brainstorm statuses
- revisit/update behavior
- parked ideas and open-thread aggregation

Why:

- this is high-value daily-use memory
- it creates durable inputs for later automation
- it reduces idea loss and repeated discussion

Primary Spex references:

- [004-brainstorm-persistence spec](/home/taylor/cc-spex/specs/004-brainstorm-persistence/spec.md)
- [brainstorm/00-overview.md](/home/taylor/cc-spex/brainstorm/00-overview.md)

#### 2. Split review artifacts

Take:

- separate artifacts for spec, plan, and code review

Why:

- they create binary evidence of completed review stages
- they support flow tracking cleanly
- they make later status and orchestration simpler

Primary Spex references:

- [015-flow-status-line spec](/home/taylor/cc-spex/specs/015-flow-status-line/spec.md)

#### 3. Resume/start-from pipeline controls

Take:

- `--resume`
- `--start-from <stage>`
- persisted run state

Why:

- these are table stakes for reliable orchestration
- they reduce fragility once Orca gains full-cycle automation

Primary Spex references:

- [010-yolo-autonomous-workflow spec](/home/taylor/cc-spex/specs/010-yolo-autonomous-workflow/spec.md)

#### 4. Branch-based artifact resolution

Take:

- use the current feature branch as the default artifact lookup key

Why:

- it improves context-reset workflows
- it reduces interactive friction
- it matches how Spec Kit already thinks about feature directories

Primary Spex references:

- [012-context-isolation spec](/home/taylor/cc-spex/specs/012-context-isolation/spec.md)

#### 5. Self-evolution discipline

Take:

- sync/adoption reports
- explicit harvest tracking
- spec-backed upgrades to the workflow system itself

Why:

- Orca is now complex enough to need a formal harvest process
- otherwise good ideas stay in chat history and drift

Primary Spex references:

- [docs/sync-reports/README.md](/home/taylor/cc-spex/docs/sync-reports/README.md)
- [docs/upstream-sync-strategy.md](/home/taylor/cc-spex/docs/upstream-sync-strategy.md)

### Adapt Heavily

These are strong ideas, but the Spex implementation should not be copied as-is.

#### 1. Traits/overlays

Keep:

- optional behavior packs
- cross-cutting concerns outside the core command set
- explicit enable/disable model

Do not keep:

- the full Spex trait mechanism
- Claude-first assumptions
- layered overlays that make base commands unreadable

Orca direction:

- capability packs, not traits-as-implemented
- simpler, provider-agnostic activation model
- explicit pack boundaries for:
  - `brainstorm-memory`
  - `flow-state`
  - `worktrees`
  - `review`
  - `yolo`

Primary Spex references:

- [002-traits-infrastructure spec](/home/taylor/cc-spex/specs/002-traits-infrastructure/spec.md)
- [003-command-consolidation spec](/home/taylor/cc-spex/specs/003-command-consolidation/spec.md)

#### 2. Deep review

Keep:

- multi-perspective review
- severity classification
- structured findings artifact
- limited autonomous fix-loop ideas

Do not keep:

- Claude-specific teams assumptions
- external-tool contracts unless they are generalized for Orca

Orca direction:

- build on top of `code-review` and `cross-review`
- provider-neutral reviewer roles
- no complex fix-loop until review gates are stable

Primary Spex references:

- [009-deep-review-trait spec](/home/taylor/cc-spex/specs/009-deep-review-trait/spec.md)

#### 3. Worktree ergonomics

Keep:

- post-specify worktree handoff concept
- restore-main behavior in the original repo
- explicit handoff artifact
- cleanup/list lifecycle thinking

Do not keep:

- Spex's exact trait structure
- Claude session assumptions

Orca direction:

- merge these ideas into the existing metadata-first Orca worktree runtime

Primary Spex references:

- [007-worktrees-trait spec](/home/taylor/cc-spex/specs/007-worktrees-trait/spec.md)
- [brainstorm/worktrees-trait.md](/home/taylor/cc-spex/brainstorm/worktrees-trait.md)

#### 4. Flow status line

Keep:

- persistent workflow state
- milestone tracking
- review checklist tracking
- next-step hints

Do not keep:

- Spex branding or exact shell UX

Orca direction:

- state model first
- status surface second
- artifact-backed truth over session-local state

Primary Spex references:

- [015-flow-status-line spec](/home/taylor/cc-spex/specs/015-flow-status-line/spec.md)

#### 5. YOLO orchestration

Keep:

- stage runner model
- ask levels
- resume semantics
- final PR/handoff posture

Do not keep:

- the assumption that YOLO is the foundation

Orca direction:

- `orca-yolo` should be orchestration over stable primitives:
  - brainstorm memory
  - flow state
  - review artifacts
  - capability packs
  - worktree runtime

Primary Spex references:

- [010-yolo-autonomous-workflow spec](/home/taylor/cc-spex/specs/010-yolo-autonomous-workflow/spec.md)

### Avoid

These should not be imported into Orca beyond background reference.

#### 1. Claude-first plugin substrate

Avoid:

- plugin packaging assumptions
- `.claude`-specific runtime structure as a product foundation
- Claude marketplace assumptions

#### 2. Claude Teams implementation details

Avoid:

- directly porting the `teams*` execution model
- assuming one provider's subagent or session semantics

#### 3. High-indirection layering by default

Avoid:

- so many overlays that the core commands become hard to reason about
- implicit behavior injection without obvious user-facing boundaries

#### 4. Full autonomous fix loops too early

Avoid:

- deep repair automation before Orca review architecture settles

## What Orca Is Still Leaving On The Field

These are the major gaps that still remain after the recent worktree/runtime
progress:

1. durable brainstorm memory
2. split review artifacts
3. formal flow state
4. explicit context handoffs
5. a capability-pack model
6. a richer review architecture
7. a resumable full-cycle orchestrator

## Recommended Orca Program

The next phase should be treated as a coherent program, not a grab bag of
commands.

### Program Name

`Orca Workflow System`

### Recommended Feature Sequence

1. `orca-brainstorm-memory`
2. `orca-review-artifacts`
3. `orca-flow-state`
4. `orca-context-handoffs`
5. `orca-capability-packs`
6. `orca-review-architecture`
7. `orca-yolo`

### Why This Order

#### 1. `orca-brainstorm-memory`

This gives Orca durable ideation inputs and reduces idea loss. It is the
highest-value standalone gain and a strong prerequisite for later orchestration.

#### 2. `orca-review-artifacts`

This creates stable review evidence so later flow tracking is artifact-based
instead of heuristic.

#### 3. `orca-flow-state`

This makes workflow progression visible and resumable.

#### 4. `orca-context-handoffs`

This improves transitions between brainstorm, specify, worktree, implement, and
review without relying on fragile session memory.

#### 5. `orca-capability-packs`

This prevents Orca from hardcoding every future subsystem into the base command
surface.

#### 6. `orca-review-architecture`

This is where Orca should formalize:

- `review-spec`
- `review-plan`
- `code-review`
- `cross-review`
- `pr-review`
- optional future deep review

#### 7. `orca-yolo`

This should come last. By this point, it becomes a thin orchestrator over
stable runtime pieces rather than a fragile mega-command.

## Strong Recommendation

Do **not** make `orca-yolo` the next spec.

Make the next spec:

`orca-brainstorm-memory`

but write it with explicit downstream consumers in mind:

- flow state
- review artifacts
- worktree/context handoff
- eventual `orca-yolo`

## Decision Summary

If Orca wants the best of Spex without inheriting its baggage:

- take memory, state, and review artifact ideas directly
- adapt traits, deep review, worktrees, and YOLO heavily
- avoid Claude substrate and high-indirection implementation details

That is the cleanest path to an Orca system that is stronger than today's Orca
without becoming a provider-bound Spex clone.

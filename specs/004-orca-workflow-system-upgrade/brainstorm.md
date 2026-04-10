# Brainstorm

## Problem

Orca has crossed the line where incremental command tweaks are no longer enough.
The repomix view of `cc-spex` made the real gap obvious:

- Orca has promising workflow commands
- Orca now has early worktree runtime foundations
- Orca is gaining brainstorm memory and better cross-review capability
- but Orca still does not behave like one coherent workflow system

The missing layer is not just "more commands." The missing layer is an upgrade
program that defines how memory, state, review, handoffs, optional capability
layers, and orchestration fit together.

Without that umbrella program:

- child specs will drift into local optimizations
- implementation order will follow numbering or convenience instead of actual
  dependency
- future parallel-agent work will invent subsystem assumptions ad hoc
- `orca-yolo` will be tempting to build too early and will end up encoding weak
  workflow primitives

## Desired Outcome

Define Orca's workflow-system upgrade as a coherent application-level program
with:

- clear subsystem boundaries
- explicit dependency order
- integration contracts between child specs
- a credible first implementation wave
- enough architectural clarity that multiple agents can implement different
  subsystems in parallel without destabilizing the whole system

The umbrella feature should answer:

- what the whole Orca upgrade is
- what is foundation versus downstream
- which subsystems can move in parallel
- which artifacts become system truth
- how later orchestration depends on earlier workflow primitives

## Constraints

- Orca must stay provider-agnostic.
- We should borrow architecture from `cc-spex`, not Claude-specific substrate.
- The upgrade must preserve Orca's current practical simplicity where possible.
- We do not want a giant monolithic implementation plan pretending the entire
  system can be built as one change.
- Parallel implementation is a goal, so boundaries must be clean enough to hand
  off to multiple agents later.
- Existing work already started:
  - `001-orca-worktree-runtime`
  - `002-brainstorm-memory`
  - `003-cross-review-agent-selection`

## Existing Context

The repomix harvest already clarified the major architectural buckets:

- brainstorm memory
- flow state
- review artifacts / review architecture
- context handoffs
- capability packs
- yolo orchestration

Current Orca state:

- worktree runtime exists as a helper layer
- brainstorm-memory is specified and planned
- cross-review agent selection is specified and planned
- umbrella upgrade and remaining subsystems were only recently turned into real
  specs

Most important takeaway from the harvest:

**Spex's advantage is the way memory, state, review, optional capability
layers, and orchestration are made persistent and composable.**

That means `004` should not become a vague roadmap. It should be the
application-level integration spec that keeps the other features acting like one
system.

## Options Considered

### Option 1: Keep only separate child specs and let the system emerge

Pros:

- lowest overhead
- each subsystem can move fast

Cons:

- no real system contract
- high drift risk between child features
- parallel implementation becomes coordination-heavy
- makes integration order too implicit

Verdict:

- rejected as too loose for the scale Orca is entering

### Option 2: One giant monolithic "Orca v2" spec with all implementation details

Pros:

- everything lives in one place
- strong top-down framing

Cons:

- too heavy to maintain
- not actually implementable in one pass
- invites fake precision across subsystems we have not designed yet
- bad fit for parallel agent execution

Verdict:

- rejected as too monolithic

### Option 3: Umbrella program spec plus child subsystem specs

Pros:

- keeps the system-level architecture explicit
- preserves modular subsystem delivery
- gives parallel agents clean boundaries later
- allows dependency order to be reasoned about centrally
- matches what the repomix harvest is really telling us

Cons:

- requires discipline to keep umbrella and child specs aligned
- adds one more artifact layer to maintain

Verdict:

- favored path

## Recommendation

Use `004-orca-workflow-system-upgrade` as the umbrella integration spec for the
entire Orca application upgrade.

That umbrella should own:

- system purpose
- subsystem inventory
- dependency order
- integration contracts
- implementation waves
- what "done enough for `orca-yolo`" actually means

The child specs should own subsystem detail:

- `002` brainstorm memory
- `003` cross-review agent selection
- `005` flow state
- `006` review artifacts
- `007` context handoffs
- `008` capability packs
- `009` yolo

Recommended implementation waves:

### Wave 1: Foundations we can build and use immediately

- `003` cross-review-agent-selection
- `002` brainstorm-memory
- `005` flow-state

Why:

- better review infrastructure helps all later work
- brainstorm memory creates durable upstream context
- flow state gives the system a way to know where it is

### Wave 2: Integration-quality layers

- `006` review-artifacts
- `007` context-handoffs

Why:

- these tighten continuity and observability between stages

### Wave 3: Composition and orchestration

- `008` capability-packs
- `009` yolo

Why:

- both depend on the earlier layers being real enough to compose

### Role of `004`

`004` should not implement runtime itself. It should:

- define the application upgrade architecture
- define wave sequencing
- define integration rules between child specs
- define what can be parallelized safely

## Open Questions

- Should `004` eventually gain its own `plan.md`, or should it stay primarily a
  system-integration spec and roadmap artifact?
- How much explicit integration contract detail should live in `004` versus the
  child plans?
- Should `006` review-artifacts and `005` flow-state be planned together to
  avoid artifact-shape drift?
- Do we want `008` capability-packs before `007` context-handoffs, or is the
  current ordering still right?

## Ready For Spec

This already has a formal spec. The next correct handoff is
`/speckit.plan` for `004-orca-workflow-system-upgrade`, with emphasis on:

- integration contracts between child specs
- implementation waves
- safe parallel-agent sequencing
- what program-level checkpoints exist before `orca-yolo`

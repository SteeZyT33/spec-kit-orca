# Brainstorm

## Problem

Orca is accumulating real workflow subsystems:

- brainstorm memory
- flow state
- review artifacts
- context handoffs
- worktree runtime
- cross-review agent selection
- eventual orchestration

Right now the default failure mode is obvious: each new cross-cutting behavior
gets folded directly into the base command set and associated docs. That leads
to:

- bloated command contracts
- harder-to-read workflows
- hidden assumptions about what is "always on"
- no clean way to talk about optional or advanced Orca behavior

Repomix showed that Spex solves this with traits/overlays, but Orca should not
copy that system directly. Orca still needs a composition model though, or it
will keep growing sideways.

## Desired Outcome

Define a simpler Orca-native capability-pack model that:

- groups optional cross-cutting workflow behavior explicitly
- keeps the core command surface understandable
- lets maintainers reason about what a pack adds
- stays provider-agnostic
- avoids the indirection and complexity of Spex traits-as-implemented

This feature should answer:

- what a capability pack is
- what belongs in core vs a pack
- how packs are declared and understood
- whether packs are documentation-only, config-driven, or runtime-visible

## Constraints

- must stay much simpler than Spex traits
- should not hide core workflow behavior behind too much indirection
- must remain inspectable and scriptable
- must work with Orca's provider-agnostic direction
- should not require a giant plugin system just to express optional behavior
- should integrate with existing and planned subsystem specs

## Existing Context

Repomix harvest direction already says:

- keep the idea of optional behavior packs
- do not keep the full Spex trait mechanism
- Orca direction is "capability packs, not traits-as-implemented"

Current obvious candidate packs:

- brainstorm-memory
- flow-state
- worktrees
- review
- yolo

Current risk if we do nothing:

- the base command set becomes the only place to express every subsystem
- `004` loses its clean subsystem boundaries in practice
- later optional behavior becomes harder to activate or reason about cleanly

## Options Considered

### Option 1: Keep everything in the core command set

Pros:

- simplest immediate implementation
- no new composition model required

Cons:

- commands become increasingly bloated
- optional behavior remains implicit
- architecture drifts back toward the exact problem repomix exposed

Verdict:

- rejected

### Option 2: Copy Spex traits closely

Pros:

- proven conceptual pattern
- strong composability

Cons:

- too much complexity
- too much Claude/Spex substrate baggage
- wrong fit for Orca's current simplicity goals

Verdict:

- rejected

### Option 3: Define a lightweight Orca capability-pack model

Pros:

- explicit optional behavior
- simpler than traits
- aligns with Orca's scale and current repo structure
- can grow gradually

Cons:

- needs careful scoping so it stays lightweight
- may start docs-first before runtime activation is fully real

Verdict:

- favored path

## Recommendation

Build `008` around a lightweight Orca capability-pack model.

Initial pack role:

- describe optional workflow behavior coherently
- keep pack boundaries explicit
- make it clear which commands and artifacts a pack influences

Likely initial packs:

- `brainstorm-memory`
- `flow-state`
- `worktrees`
- `review`
- `yolo`

Likely pack fields:

- pack id
- purpose
- affected commands
- required artifacts/runtime prerequisites
- activation mode
- whether it is core, optional, experimental, or downstream

## Open Questions

- Are packs initially documentation/config concepts only, or should they be
  runtime-visible immediately?
- How should activation work: config file, manifest, or extension metadata?
- Which existing Orca behavior is "core forever" versus pack-scoped?
- Should `review` be one pack or split into finer review capabilities later?

## Ready For Spec

This already has a draft spec. The next correct handoff is `/speckit.plan` for
`008-orca-capability-packs`, with focus on:

- pack model
- activation semantics
- core vs pack boundary rules
- relation to `004` and `009`

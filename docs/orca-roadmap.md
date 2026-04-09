# Orca Roadmap

## Purpose

Define the next Orca evolution after the v1.4 command normalization work.

This roadmap is informed by two realities:

1. Orca now has a cleaner command surface, but it still lacks runtime-backed
   worktree metadata and stronger workflow enforcement.
2. `cc-spex` demonstrates stronger workflow architecture in several areas, but
   its implementation substrate remains Claude-specific and should not be
   adopted wholesale.

The goal is to borrow the right architectural ideas without inheriting the
wrong platform assumptions.

## Strategic Direction

Orca should evolve from a flat extension command bundle into:

- a small core workflow surface
- plus optional traits or modules for cross-cutting behavior

The most important architectural shift is:

**Stop packing every workflow concern directly into the base command set.**

Instead, Orca should have:

- a stable core
- protocol-backed runtime metadata
- orthogonal traits/modules for worktrees, delivery, deep review, and ship

## Core Principles

1. Keep the core workflow small and understandable.
2. Treat worktree and delivery metadata as runtime truth, not just docs.
3. Add advanced orchestration only after the protocol layers are real.
4. Steal architecture from `cc-spex`, not Claude plugin mechanics.
5. Prefer provider-agnostic workflow semantics over harness-specific features.

## Canonical Core Surface

The target stable core command set is:

- `speckit.orca.brainstorm`
- `speckit.orca.micro-spec`
- `speckit.orca.assign`
- `speckit.orca.code-review`
- `speckit.orca.cross-review`
- `speckit.orca.pr-review`
- `speckit.orca.self-review`

Compatibility aliases should be temporary only.

## v1.5: Consolidation And Runtime Foundations

This release should stabilize the current command surface and turn protocol docs
into runtime-backed behavior.

### Goals

- lock the normalized command vocabulary
- remove the last legacy alias after a short transition window
- add runtime worktree metadata support
- introduce the idea of Orca traits/modules
- improve reviewer-facing artifacts

### Scope

#### 1. Final command cleanup

- keep only the canonical commands listed above
- remove `speckit.orca.review` after the transition window
- ensure README, templates, and examples use only canonical names

#### 2. Runtime worktree metadata

Implement a helper/runtime layer that can:

- detect `.specify/orca/worktrees/registry.json`
- resolve active lanes for the current feature
- resolve the current lane from branch and path
- warn on stale or conflicting metadata
- degrade safely when no metadata exists

This runtime layer should feed:

- `assign`
- `code-review`
- `cross-review`
- `self-review`

#### 3. Reviewer-facing artifacts

Orca should keep `review.md` as the durable record, but also generate a more
reviewer-friendly summary artifact similar in spirit to `REVIEW-CODE.md`.

The purpose is not to duplicate findings, but to give human reviewers:

- key decisions
- risk areas
- deviation notes
- the best reading order for review

#### 4. Trait/module framing

Do not fully implement the trait architecture yet, but introduce it explicitly
in the docs and structure:

- `worktrees`
- `delivery`
- `deep-review` (future)
- `ship` (future)

### Acceptance Criteria

- canonical command set only
- runtime worktree metadata is consumed by existing commands
- reviewer summary artifact exists
- docs describe Orca as a core plus optional traits/modules

## v1.6: First Real Traits/Modules

This release should make Orca modular in practice, not just in language.

### Goals

- make worktrees a first-class Orca trait/module
- make delivery a first-class Orca trait/module
- strengthen spec-compliance review behavior

### Scope

#### 1. `worktrees` trait/module

Implement the first real Orca trait/module around the existing worktree
protocol.

Expected capabilities:

- lane discovery
- lane status inspection
- cleanup of merged/stale lanes
- optional `speckit.orca.worktree list|status|cleanup`

This should remain provider-agnostic and metadata-first.

#### 2. `delivery` trait/module

Move delivery rules out of informal docs and into actual checks:

- branch naming validation
- PR shape validation
- commit hygiene checks
- lane-vs-feature merge target checks

`pr-review` should consume this directly.

#### 3. Stronger `code-review`

Improve `code-review` by adding:

- explicit spec compliance scoring
- clearer deviation reporting
- better reviewer summaries
- stronger separation between implementation review and PR management

### Acceptance Criteria

- `worktrees` and `delivery` behave like distinct subsystems
- `pr-review` is delivery-aware through runtime checks
- `code-review` has stronger spec compliance reporting

## v1.7+: Advanced Orchestration

These should happen only after worktree and delivery traits/modules are stable.

### `deep-review`

Add an optional deep review mode or trait/module for:

- multi-perspective review
- stronger autonomous fix loops
- optional external review-tool integrations

This should be opt-in, not part of the default workflow.

### `ship`

Add an optional end-to-end orchestrator only after:

- stage metadata is stable
- resume semantics are real
- worktrees and delivery are trustworthy

`ship` should not be the foundation. It should be the last layer.

### Drift reconciliation

Add a dedicated Orca drift/reconciliation capability after the above:

- detect spec/code divergence
- guide whether to update spec or fix code
- integrate with review and delivery artifacts

## What To Borrow From `cc-spex`

These are the strongest ideas to adapt into Orca:

### Borrow now

- stronger stage discipline
- explicit spec-to-code compliance framing
- reviewer-friendly summary artifacts
- worktree lifecycle patterns

### Borrow later

- traits as first-class overlays/modules
- deep review as an opt-in subsystem
- autonomous ship pipeline after lower layers stabilize
- drift reconciliation as a dedicated workflow

### Do not borrow directly

- Claude plugin architecture
- `.claude`-specific runtime assumptions
- Claude hook/session mechanics
- Claude Teams integration substrate

## Recommended Implementation Order

1. Finish command-surface cleanup.
2. Implement runtime worktree metadata helpers.
3. Wire `assign`, `code-review`, `cross-review`, and `self-review` to runtime metadata.
4. Add reviewer summary artifacts.
5. Extract `worktrees` as the first real trait/module.
6. Extract `delivery` as the second real trait/module.
7. Strengthen spec compliance reporting in `code-review`.
8. Only then consider `deep-review`, `ship`, and drift reconciliation.

## Immediate Next Step

The next concrete Orca move should be:

**Implement runtime worktree metadata support and treat it as the foundation of
the future `worktrees` trait/module.**

That is the highest-leverage lesson from `cc-spex`, and it addresses Orca's
current weakness directly without importing Claude-specific complexity.

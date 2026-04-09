# Spex Adoption Notes

## Purpose

Capture the best ideas from `cc-spex` without turning Orca into a Claude-bound
fork or another large side project.

This document is intentionally pragmatic. The question is not:

- "Should Orca become spex?"

The question is:

- "Which parts of spex reduce real workflow pain for Orca, and how do we adopt
  them with the least architectural regret?"

## Current Position

Two things are true at once:

1. `cc-spex` is further along in workflow maturity.
2. Orca is closer to the provider-agnostic system we actually want.

That means Orca should **borrow aggressively** from spex while resisting the
temptation to wholesale absorb Claude-specific machinery.

## Decision

Do **not** fork `cc-spex` right now.

Do **not** try to upstream a provider-agnostic refactor into `cc-spex` right
now either.

Instead:

- keep Orca as the main repo
- use `cc-spex` as the reference implementation
- port only the highest-value workflow ideas
- keep the porting effort bounded and phased

This reduces the risk of getting trapped in another long-lived infrastructure
project while still capturing the hard-won legwork already present in spex.

## What To Steal First

These are the parts of spex that appear most valuable for Orca.

### 1. Trait Architecture

This is the biggest idea worth borrowing.

Spex separates cross-cutting workflow concerns from the core command surface by
using composable traits. Orca should move in the same direction.

Target Orca traits/modules:

- `worktrees`
- `delivery`
- `deep-review`
- `ship`

This avoids growing Orca into one monolithic extension where every concern
lives directly in the base command set.

### 2. Spec-Compliance-First Review

Spex's review flow is strongly centered on:

- does the code match the spec
- where does it deviate
- what should be fixed vs evolved

Orca `code-review` should adopt this posture more explicitly.

### 3. Reviewer-Facing Summaries

Spex generates reviewer-oriented artifacts that help a human reviewer spend
their limited review time well.

Orca should add a reviewer brief artifact that sits alongside `review.md` and
answers:

- what changed
- where to start reading
- what decisions need human eyes
- what deviations or risks matter most

### 4. Worktree Lifecycle Ideas

Spex has stronger operational worktree thinking than Orca currently does:

- create/list/cleanup lifecycle
- restore default branch after feature creation
- explicit user handoff into the worktree

Orca should not copy the implementation directly, but should adopt the lifecycle
thinking.

### 5. Stage Discipline

Spex is strict about not silently skipping stages.

Orca should borrow that discipline in a lighter form:

- no silent skipping of important review/gate steps
- explicit progression rules
- clear resume/start-point semantics when automation is introduced later

## What To Steal Later

These are good ideas, but not first.

### 1. Deep Review

Multi-perspective review and fix loops are valuable, but only after Orca has:

- stable worktree/runtime metadata
- stable `code-review`, `cross-review`, and `pr-review`
- delivery-aware review flow

### 2. Ship

An autonomous `ship` pipeline is tempting, but it should be the last layer, not
the foundation.

Do not add this until:

- worktrees are real at runtime
- delivery checks are real at runtime
- resume/state semantics are stable

### 3. Drift Reconciliation

Spex's evolve/reconcile concepts are worth studying, but Orca should not add a
drift command until the core review and delivery layers are more mature.

## What Not To Import

These are the main things Orca should avoid pulling in from spex.

### 1. Claude Plugin Substrate

Do not import:

- `.claude`-centric file structure
- Claude marketplace assumptions
- Claude restart semantics
- Claude-specific plugin packaging

### 2. Claude-Specific Hook Model

Do not import:

- Claude hook/session gating
- `AskUserQuestion`-driven interaction assumptions
- Claude Teams runtime dependencies

### 3. Full Complexity Up Front

Do not import:

- all traits at once
- full ship pipeline early
- every spex command just because it exists

The point is to steal leverage, not to recreate spex under a new name.

## Adoption Guardrails

To avoid turning Orca into another sprawling side project, use these guardrails.

### Guardrail 1: One subsystem at a time

Only adopt one major spex idea per release.

Recommended order:

1. runtime worktree support
2. reviewer brief artifact
3. trait/module framing
4. delivery checks
5. deep review
6. ship

### Guardrail 2: Runtime before automation

Do not add more automation until the runtime metadata exists.

That means:

- implement worktree metadata helpers first
- make existing Orca commands consume them
- only then add higher-level orchestration

### Guardrail 3: Keep command surface stable

Avoid adding lots of new commands just because spex has them.

Prefer:

- strengthening the existing Orca commands
- extracting traits/modules behind the scenes

### Guardrail 4: Adopt concepts, not branding

Orca should keep its own naming and workflow vocabulary unless a spex term is
materially better.

The goal is not to make Orca feel like a thin spex rename.

## Concrete Orca Plan

### Phase 1: Immediate

Implement:

- runtime worktree metadata helpers
- lane-aware command behavior
- reviewer brief artifact for `code-review`

### Phase 2: Near-Term

Refactor docs and implementation around traits/modules:

- `worktrees`
- `delivery`

These do not need a huge framework first. Start with clear boundaries and
runtime helpers.

### Phase 3: Later

After phases 1 and 2 are stable:

- consider `deep-review`
- consider `ship`
- consider drift reconciliation

## Decision Check

When evaluating a future spex idea for Orca, ask:

1. Does this reduce real workflow pain we actually feel?
2. Can it be implemented without Claude-specific runtime assumptions?
3. Does it strengthen Orca's core, or just make it bigger?
4. Would adding it now block more important protocol/runtime work?

If the answer to question 2 is "no", do not adopt it directly.

If the answer to question 3 is "it just makes Orca bigger", defer it.

## Bottom Line

The right move is:

- keep Orca
- steal the best parts of spex
- do it in bounded phases
- refuse the Claude-specific substrate

That gives us the best chance of benefiting from spex's maturity without
getting trapped in a fork-sized rewrite or another expanding workflow project.

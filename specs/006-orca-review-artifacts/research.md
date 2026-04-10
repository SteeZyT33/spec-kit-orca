# Research: Orca Review Artifacts

## Decision 1: Use a two-layer review artifact model

### Decision

Keep `review.md` as an umbrella summary/index while adding distinct stage
artifacts for the main review phases.

### Rationale

- preserves current Orca ergonomics
- introduces durable stage evidence for later systems
- reduces migration shock

### Alternatives Considered

- Keep only `review.md`: too ambiguous for later flow-state and orchestration.
- Drop `review.md` immediately: cleaner eventually, but too disruptive.

## Decision 2: Stage artifacts are the durable source of truth

### Decision

Stage-specific review artifacts should become the machine-facing durable evidence
of completed review stages, while `review.md` acts as human-facing summary.

### Rationale

- clearer future automation
- cleaner review-stage discoverability
- lower ambiguity about what actually happened

### Alternatives Considered

- Keep summary file as the sole authoritative source: too ambiguous.

## Decision 3: `self-review.md` remains separate

### Decision

Keep `self-review.md` separate from implementation review artifacts.

### Rationale

- self-review is a process retrospective, not an implementation review stage
- it should not be collapsed into code/PR review evidence

### Alternatives Considered

- fold self-review into the main review bundle: conflates two different concerns

## Decision 4: Additive migration first

### Decision

Introduce stage artifacts additively and keep historical migration out of the
first implementation unless it becomes unavoidable.

### Rationale

- reduces risk
- preserves current artifacts
- allows later cleanup once the new model is proven

### Alternatives Considered

- full retroactive migration immediately: too much churn for little immediate
  value

# Quickstart: Orca Review Artifacts

## Goal

Validate that Orca review stages leave explicit durable evidence and that the
umbrella summary remains readable.

## Setup

1. Work with a disposable feature directory in this repo.
2. Update only review artifact contracts and command docs unless helper logic
   proves necessary.

## Scenario 1: Code review artifact

1. Run or simulate `code-review`.
2. Verify:
   - `review-code.md` is created or updated
   - `review.md` reflects that code review occurred

## Scenario 2: Cross-review artifact

1. Run or simulate `cross-review`.
2. Verify:
   - `review-cross.md` is created or updated
   - `review.md` reflects the cross-review outcome

## Scenario 3: PR review artifact

1. Run or simulate `pr-review`.
2. Verify:
   - `review-pr.md` is created or updated
   - PR lifecycle evidence is distinguishable from code review evidence

## Scenario 4: Self-review separation

1. Run or simulate `self-review`.
2. Verify:
   - `self-review.md` remains separate
   - it is not conflated with implementation review artifacts

## Scenario 5: Human discoverability

1. Open only `review.md`.
2. Verify:
   - you can identify which review stages have durable evidence
   - you can find the right stage artifact quickly

## Scenario 6: Legacy migration

1. Start from a feature directory that has only a legacy `review.md`.
2. Run or simulate one review command under the new model.
3. Verify:
   - the appropriate stage artifact is created
   - the legacy `review.md` remains usable as a summary/index
   - the presence of `review.md` alone is not treated as proof that all review
     stages already occurred

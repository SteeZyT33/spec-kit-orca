# Contract: Review Artifact Ownership

## Primary Ownership

The preferred ownership model is:

- `speckit.orca.code-review` → `review-code.md`
- `speckit.orca.cross-review` → `review-cross.md`
- `speckit.orca.pr-review` → `review-pr.md`
- `speckit.orca.self-review` → `self-review.md`

## Summary Layer

- `review.md` is the umbrella summary/index
- it is updated alongside stage artifacts
- it is not the only durable source of review-stage truth

## Open Extension Point

If Orca later introduces dedicated spec or plan review commands, they should own:

- `review-spec.md`
- `review-plan.md`

Until then, those artifacts may remain planned but unused, or be produced by a
design-review flow if explicitly defined later.

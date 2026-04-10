# Contract: `/speckit.orca.cross-review`

## Purpose

Define the user-visible reviewer-selection contract for Orca cross-review.

## Inputs

- `--agent <name>`: canonical reviewer-selection input
- `--harness <name>`: legacy compatibility input
- `--scope design|code`
- `--phase N`
- optional free-form review focus text

## Resolution Order

When `--agent` is omitted, Orca resolves the reviewer in this order:

1. explicit `--agent`
2. configured `crossreview.agent`
3. legacy configured `crossreview.harness`
4. most recent successful reviewer, if enabled and still valid
5. highest-ranked installed Tier 1 non-current reviewer
6. ask the user if the choice is materially ambiguous
7. fallback to current provider with a warning

## Required Output

Cross-review output must report:

- requested agent
- resolved agent
- model
- effort
- selection reason
- support tier
- whether the review was truly cross-agent or same-agent fallback

## Required Failure Behavior

- known but unsupported agents must return structured unsupported-agent output
- missing adapters must not be reported as successful review
- runtime invocation failures must be surfaced as operational blockers

## Compatibility

- `--harness` remains accepted for a compatibility window
- `agent` is the canonical term in docs and output

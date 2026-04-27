# contradiction-detector

Detects when new synthesis or theory contradicts existing raw evidence or prior synthesis. Effectively `cross-agent-review` with a fixed contradiction prompt and a structured contradiction-shaped output.

## How it works

The capability bundles `new_content` (the new synthesis path) plus `prior_evidence[]` (paths to evidence to compare against), sends the bundle to one or more reviewer backends with a contradiction-focused prompt, and reshapes the returned findings into a contradiction-specific envelope.

## Input

See `schema/input.json`.

- `new_content`: path to the synthesis or theory document being checked.
- `prior_evidence`: array of paths to prior evidence (events.jsonl, experiments.tsv, prior synthesis versions, etc.). At least one required.
- `reviewer`: one of `claude`, `codex`, `cross`. Defaults to `cross`.

## Output

See `schema/output.json`.

- `contradictions[]`: each item is a structured contradiction with `new_claim`, `conflicting_evidence_ref`, `confidence`, `suggested_resolution`, `reviewer`.
- `partial`: true when one reviewer in cross mode failed but the other succeeded.
- `missing_reviewers`: tuple of failed reviewer names (sorted). Empty when all succeeded.
- `reviewer_metadata`: per-reviewer metadata (token counts, model, etc.).

## Confidence

Reviewer-reported confidence is preserved as-is. Hosts decide thresholds for blocking vs. warning.

## Errors

- `INPUT_INVALID`: unknown reviewer, missing/non-existent `new_content` path, missing `prior_evidence` (empty list), missing backend reviewer for cross mode.
- `BACKEND_FAILURE`: reviewer raised, all reviewers failed in cross mode, or reviewer returned malformed findings.

## Relationship to cross-agent-review

v1 is a thin wrapper: same bundle/reviewer mechanics, fixed contradiction prompt, structured output. v2 may collapse this into a `cross-agent-review` preset.

## CLI

`orca-cli contradiction-detector --new-content synthesis.md --prior-evidence events.jsonl --prior-evidence experiments.tsv --reviewer cross`

# Contract: Handoff Resolution

## Purpose

Define how Orca resolves upstream context when entering a stage.

## Resolution Inputs

1. explicit handoff artifact or section
2. current feature branch
3. current worktree/lane context when present
4. durable upstream artifacts for the current feature

## Resolver Search Scope

- Search only within the current feature's artifact set.
- Canonical handoff files are searched only under `specs/<feature>/handoffs/`.
- Embedded handoff sections are searched only in the upstream artifacts already
  selected for the candidate transition, not repo-wide.

## Resolution Order

1. exact canonical handoff file matching the requested `source -> target`
   transition
2. exact embedded handoff section matching the requested `source -> target`
   transition
3. branch-anchored upstream artifact set for the target stage
4. branch plus worktree/lane context
5. artifact-only fallback with explicit warning

## Deterministic Matching Rules

- Prefer an exact `source_stage` and `target_stage` match over any partial or
  stage-family match.
- Prefer the canonical handoff file over an embedded handoff section.
- Embedded handoff matches must be located by exact section-title text, not by
  renderer-specific Markdown fragment anchors.
- A branch match means exact string equality between the current git branch name
  and the serialized `Branch:` value after trimming surrounding whitespace.
- If multiple candidate handoff files exist for the same transition, prefer:
  1. branch match
  2. lane match
  3. most recent `Created` timestamp
  4. lexical file path order as the final deterministic tie-break
- Multiple canonical handoff files for the same transition remain a contract
  violation even when a deterministic diagnostic winner is chosen.
- Worktree/lane context is only a tie-breaker when the stage transition and
  feature anchor already match.
- Artifact-only fallback must never claim that a real handoff was found.

## Warning And Degradation Rules

- If no explicit handoff is found, the resolver must emit a warning that the
  transition was inferred.
- If branch context conflicts with the most recent matching handoff, the
  resolver must report branch ambiguity rather than silently picking one truth.
- If lane metadata is absent, resolution must continue without error and record
  that lane context was not used.

## Output

Resolution must surface:

- resolved upstream artifacts
- whether a real handoff was found
- whether branch/worktree context was used
- why this context was chosen
- which storage shape won (`file`, `embedded`, `artifact-only`)
- whether ambiguity was detected
- whether a uniqueness violation was detected

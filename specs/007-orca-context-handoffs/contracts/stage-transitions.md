# Contract: Stage Transitions

## Canonical Stage Ids

Use these normalized stage ids for enums, file names, and locator logic:

- `brainstorm`
- `specify`
- `plan`
- `tasks`
- `assign`
- `implement`
- `self-review`
- `code-review`
- `cross-review`
- `pr-review`

## Machine-Parseable Enum

```text
brainstorm
specify
plan
tasks
assign
implement
self-review
code-review
cross-review
pr-review
```

## Filename Sanitization Rule

- Stage ids are already filename-safe and must be used verbatim in canonical
  handoff file names.
- Canonical file name pattern:
  `<source_stage>-to-<target_stage>.md`
- No extra normalization, slash replacement, or alias expansion is allowed.

## Explicitly Supported Transitions

- brainstorm -> specify
- specify -> plan
- plan -> tasks
- tasks -> implement
- assign -> implement
- implement -> code-review
- cross-review -> pr-review
- code-review -> pr-review

## Minimum Inputs By Transition

| Transition | Minimum Upstream Inputs | Continuity Summary | Open Questions |
|---|---|---|---|
| `brainstorm -> specify` | brainstorm artifact, topic/title anchor | idea framing, scope signal, notable constraints | unresolved product/feature questions |
| `specify -> plan` | `spec.md`, clarification decisions if any | selected problem framing and accepted requirements | unresolved design questions |
| `plan -> tasks` | `plan.md`, supporting design artifacts | architectural direction and implementation phases | unresolved implementation strategy questions |
| `tasks -> implement` | `tasks.md`, selected work slice if available | task decomposition and intended acceptance target | unresolved implementation blockers |
| `assign -> implement` | `tasks.md`, assignment/ownership context | selected work slice and ownership intent | unresolved implementation blockers |
| `implement -> code-review` | implementation diff or changed files, relevant task context | what changed and what was intentionally left out | unresolved correctness or test concerns |
| `cross-review -> pr-review` | `review-cross.md`, review summary, branch/PR context if present | alternate-review status and remaining concerns | unresolved PR-blocking items |
| `code-review -> pr-review` | `review-code.md`, review summary, branch/PR context if present | implementation-review status and remaining concerns | unresolved PR-blocking items |

## Rule

Each supported transition must define:

- what upstream artifacts the next stage should read
- what continuity summary should be preserved
- what unresolved questions carry forward

## Degradation

If no explicit handoff exists, Orca may fall back to artifact resolution and
branch/worktree context, but it must report that the transition was inferred.

The inferred transition must still name which minimum inputs were actually
found versus missing.

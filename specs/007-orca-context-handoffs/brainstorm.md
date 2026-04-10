# Brainstorm

## Problem

Orca has started to acquire durable artifacts:

- brainstorm memory
- specs
- plans
- tasks
- reviews
- worktree metadata

But the transitions between stages are still mostly implicit. A new command or
fresh session has to infer too much from branch name, repo shape, or the user's
prompt. That creates several failures:

- key intent gets lost between brainstorm and spec
- worktree or fresh-session execution loses stage continuity
- review stages have to reconstruct upstream reasoning manually
- later orchestration such as `orca-yolo` would need to invent handoff logic at
  runtime

Repomix made the missing pattern obvious: reliable systems do not just store
artifacts, they also define the handoff rules between artifacts and stages.

## Desired Outcome

Define an Orca-native context handoff model that:

- preserves continuity between major workflow stages
- prefers durable artifacts over transient chat context
- works across fresh sessions and worktrees
- makes later consumers know what upstream artifacts they should read
- gives `orca-yolo` and future status/runtime layers a clean transition model

This feature should answer:

- what a handoff artifact or handoff contract is
- when a handoff should be written
- what stage-to-stage transitions Orca supports explicitly
- how branch/worktree context interacts with handoff resolution

## Constraints

- must stay provider-agnostic
- must not depend on active session memory
- must be compatible with the existing worktree runtime direction
- should integrate with brainstorm memory, flow state, and review artifacts
- should not become a giant general-purpose memory system
- should not require every command to duplicate the same transition logic in
  prose only

## Existing Context

Current relevant pieces:

- `002-brainstorm-memory` is creating durable ideation inputs
- `005-orca-flow-state` is intended to describe where a feature is
- `006-orca-review-artifacts` will clarify review-stage evidence
- `001-orca-worktree-runtime` already gives Orca a metadata-first lane/runtime
  substrate
- `004` says `007` is a Wave 2 integration-quality layer and a prerequisite for
  `009-orca-yolo`

The harvest matrix points toward:

- branch-based artifact resolution
- explicit context isolation/handoff behavior
- durable transition rules between stages

## Options Considered

### Option 1: Rely on branch-based artifact lookup only

Pros:

- very lightweight
- matches current Spec Kit habits

Cons:

- branch alone does not capture intent
- weak for brainstorm-to-spec or review-to-PR transitions
- too much implicit behavior

Verdict:

- insufficient by itself

### Option 2: Add handoff notes opportunistically inside existing artifacts

Pros:

- minimal new files
- easy to start

Cons:

- no consistent contract
- each command may encode handoff differently
- hard for later tooling to consume reliably

Verdict:

- useful as part of the solution, but too loose alone

### Option 3: Define explicit handoff contracts and lightweight durable handoff artifacts

Pros:

- clear stage-to-stage continuity
- durable enough for fresh sessions and orchestration
- easier for later tools to resolve upstream context intentionally

Cons:

- adds another artifact layer
- requires careful scope discipline

Verdict:

- favored path

## Recommendation

Build `007` around explicit stage handoff contracts plus lightweight durable
handoff artifacts or sections.

Core principle:

- commands should not just create their local artifact
- they should also make the next stage's upstream context resolvable

Likely major handoffs:

- brainstorm -> specify
- specify -> plan
- plan -> tasks
- tasks/assign -> implement
- implement -> code-review
- code-review/cross-review -> pr-review

Likely handoff contents:

- source stage
- target stage
- primary upstream artifacts
- current intent / summary
- unresolved questions
- branch or worktree context when relevant

## Open Questions

- Should handoffs be separate files, embedded sections, or both?
- Should every stage write a handoff, or only stages where continuity commonly
  breaks?
- How much of handoff resolution belongs in `007` versus `005` flow-state?
- Should worktree/lane context be required in handoffs, or only attached when
  present?

## Ready For Spec

This already has a draft spec. The next correct handoff is `/speckit.plan` for
`007-orca-context-handoffs`, with focus on:

- handoff artifact shape
- explicit stage transition coverage
- integration with `002`, `005`, and `006`

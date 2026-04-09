# Orca v1.4 Design

## Purpose

Define the next Orca workflow layer so it:

- owns brainstorming instead of delegating to `superpowers/brainstorm`
- uses one provider-agnostic worktree protocol across Claude, Codex, and future agents
- supports a constrained quicktask lane without losing planning, review, or traceability

This is a design document only. It does not authorize implementation details that
contradict the current Orca command set until those changes are explicitly made.

## Current State

Orca currently exposes the core workflow commands:

- `speckit.orca.code-review`
- `speckit.orca.pr-review`
- `speckit.orca.assign`
- `speckit.orca.cross-review`
- `speckit.orca.self-review`

The current recommended workflow is:

```text
specify → plan → tasks → assign → implement → code-review → crossreview → pr-review → self-review
```

The main structural gap is that worktree handling is not provider-agnostic.
Current `assign` guidance checks for active worktrees under `.claude/worktrees/`,
which is incompatible with Codex and creates inconsistent behavior across projects.

## Goals

1. Add an Orca-native pre-spec ideation command.
2. Establish one cross-agent worktree protocol owned by Orca.
3. Add a micro-spec quicktask lane for small work.
4. Preserve the Spec Kit audit trail instead of creating side channels.

## Non-Goals

- Replacing core Spec Kit commands.
- Building a full autonomous worktree orchestration engine in v1.4.
- Allowing quicktask to bypass documentation, planning, or review.
- Upstreaming the worktree protocol to Spec Kit core before it is proven in Orca.

## Design Principles

1. Orca should own workflow coordination, not depend on another tool's implied lifecycle.
2. Agent integration details are implementation details, not workflow truth.
3. Every work item must leave a durable artifact.
4. Small work may take a shorter path, but not an invisible path.
5. Promotion from lightweight flow to full spec flow must be explicit and cheap.

## Decision Summary

### Decision 1: Worktree protocol comes first

All new workflow features should sit on top of an Orca-owned worktree model.
Until that exists, brainstorm and quicktask will inherit inconsistent assumptions.

### Decision 2: `speckit.orca.brainstorm` stops before implementation

Orca brainstorming should produce a structured artifact and hand off to
`/speckit.specify` or `/speckit.plan`, not to implementation.

### Decision 3: `speckit.orca.micro-spec` is a micro-spec, not a spec bypass

Quicktask should create a durable record and include a mini-plan, a declared
verification mode, and review.
If the scope grows, it must promote to the standard Spec Kit flow.

## Proposed Command Additions

### `speckit.orca.brainstorm`

#### Intent

Capture structured ideation for new work or feature refinements without dropping
into implementation-oriented behavior.

#### Inputs

- free-form problem statement
- optional `--feature <id>`
- optional context constraints in the prompt

#### Outputs

- a `brainstorm.md` artifact
- a recommended next handoff:
  - `/speckit.specify`
  - `/speckit.plan`

#### Required sections

```markdown
# Brainstorm

## Problem
## Desired Outcome
## Constraints
## Existing Context
## Options Considered
## Recommendation
## Open Questions
## Ready For Spec
```

#### Artifact location

Use the first applicable destination:

1. `specs/<feature>/brainstorm.md`
2. `.specify/orca/inbox/brainstorm-<timestamp>.md` if no feature exists yet

#### Workflow contract

- Must not generate implementation tasks.
- Must not route directly to `implement`.
- May suggest that the request is too small for full brainstorming and better fit
  for `quicktask`.

### `speckit.orca.micro-spec`

#### Intent

Handle small bounded work without requiring a full `spec.md` + `plan.md` +
`tasks.md` flow, while preserving traceability and review.

#### Inputs

- free-form task statement
- optional `--feature <id>`
- optional `--files <paths>`

#### Outputs

- a quicktask record
- a mini-plan
- a verification plan
- a decision:
  - proceed as quicktask
  - promote to full spec flow

#### Allowed scope

- small bugfix
- limited refactor
- tooling tweak
- docs update
- narrow maintenance task

#### Disallowed scope

- new feature with multiple user stories
- architecture change
- data model or contract change
- anything likely to require parallel task decomposition
- high-risk security or migration work

#### Record format

```markdown
## QT-YYYY-MM-DD-XX

**Title**:
**Status**: planned | in_progress | reviewed | done
**Scope**:
**Files**:
**Reason**:
**Verification Mode**: test-first | characterization | evidence-first

### Plan
- step 1
- step 2

### Verification Plan

### Implementation Notes

### Review Summary

**Promotion Check**: stayed quicktask | promoted to full spec
```

#### Artifact location

Use the first applicable destination:

1. `specs/<feature>/quicktasks.md`
2. `specs/000-quicktasks/quicktasks.md` if no active feature exists

#### Workflow contract

- Must always write or update a record before implementation starts.
- Must include a mini-plan.
- Must declare a verification mode before implementation starts.
- Must include review output.
- Must stop and promote when scope exceeds quicktask rules.

#### Verification mode rules

Quicktask is not exempt from test discipline. It is only exempt from full
`tasks.md` decomposition.

Allowed verification modes:

- `test-first`: write a failing test first, then implement
- `characterization`: lock current behavior with a regression or characterization
  test before refactoring
- `evidence-first`: declare explicit non-test verification for docs, tooling, or
  config work where automated tests are not the right proof mechanism

Default expectation:

- use `test-first` for behavior-changing code
- use `characterization` for refactors
- use `evidence-first` only when test-first is genuinely not the right fit

## Provider-Agnostic Worktree Protocol

### Intent

Create one canonical worktree model for Orca workflows regardless of active AI
integration.

### Source of truth

Repo-local Orca metadata, not agent-specific directories.

### Root path

```text
.specify/orca/worktrees/
```

### Structure

```text
.specify/orca/
  worktrees/
    registry.json
    <lane-id>.json
  logs/
  inbox/
```

### Lane record schema

```json
{
  "id": "004-mneme-viz-ui",
  "feature": "004-mneme-viz",
  "branch": "004-mneme-viz-ui",
  "path": "/abs/path/to/worktree",
  "agent": "codex",
  "role": "frontend",
  "task_scope": ["T026", "T028", "T029"],
  "status": "active",
  "base_ref": "main",
  "parent_feature_branch": "004-mneme-viz",
  "created_at": "2026-04-08T20:00:00Z",
  "updated_at": "2026-04-08T20:30:00Z",
  "notes": "graph UI lane"
}
```

### Allowed statuses

- `planned`
- `active`
- `blocked`
- `merged`
- `retired`

### Rules

1. Every active worktree lane must have a metadata record.
2. Task scope must be bounded and explicit.
3. Shared-file or overlapping-lane work must be explicitly declared.
4. Commands may inspect `git worktree list`, but Orca metadata is the workflow
   source of truth.
5. Cleanup means status transition, not silent removal.

### Integration expectations

#### `assign`

- must read Orca worktree metadata
- must no longer rely on `.claude/worktrees/`
- may switch to "parallel dispatch mode" when active lane records exist

#### `code-review`

- should report findings by lane when lane metadata exists
- should note handoff risks when tasks span multiple lanes

#### `pr-review`

- should preserve lane and delivery context during external feedback handling
- should track PR-specific states separately from implementation review

#### `self-review`

- should evaluate workflow friction using worktree metadata when available

### Future command

This protocol should support a later `speckit.orca.worktree` command for:

- inspect
- create
- update status
- retire

That command is not required to ship in v1.4 if the metadata contract is stable.

## Promotion Rules For Quicktask

Quicktask must promote to the standard Spec Kit flow if any of the following are true:

1. More than one coherent user story emerges.
2. The mini-plan exceeds 5 to 7 meaningful steps.
3. Multiple domains require coordinated handoffs.
4. Parallel worktrees are needed.
5. Data model or contract changes are required.
6. Security, auth, migration, or destructive-risk work is involved.
7. No credible verification mode can be declared up front.

Promotion target:

```text
brainstorm (optional) → specify → plan → tasks → assign → implement → code-review → pr-review
```

## Artifact Strategy

### New work

- brainstorm creates `specs/<feature>/brainstorm.md`
- full flow continues into standard Spec Kit artifacts

### Existing feature refinement

- brainstorm writes into existing `specs/<feature>/brainstorm.md`
- quicktask appends to `specs/<feature>/quicktasks.md`

### No active feature

- brainstorm writes to `.specify/orca/inbox/`
- quicktask writes to `specs/000-quicktasks/quicktasks.md`

## Required Changes By Area

### Manifest

Update `extension.yml` to add:

- `speckit.orca.brainstorm`
- `speckit.orca.micro-spec`

Do not add a worktree command yet unless the metadata contract is implemented.

### Commands

Add:

- `commands/brainstorm.md`
- `commands/micro-spec.md`

Update:

- `commands/assign.md`
- `commands/code-review.md`
- `commands/pr-review.md`
- `commands/self-review.md`

### Docs

Add:

- `docs/worktree-protocol.md`

Update:

- `README.md`

## Rollout Plan

### Phase 1: Worktree foundation

- define metadata schema
- document protocol
- update `assign` to stop referencing `.claude/worktrees/`

### Phase 2: Brainstorm

- add command contract
- add artifact strategy
- document handoff to `specify` or `plan`

### Phase 3: Quicktask

- add command contract
- add micro-spec record format
- add promotion rules

### Phase 4: Documentation normalization

- update README command list
- update recommended workflow diagrams
- add examples for Codex and Claude

## Acceptance Criteria

### Worktree protocol

- no Orca command treats agent-specific directories as the source of truth
- lane metadata is sufficient to identify active parallel work
- the model works the same for Claude and Codex

### Brainstorm

- Orca can ideate without Superb installed
- result is written to a durable artifact
- command never directs users straight to implementation

### Quicktask

- every quicktask creates a durable record
- quicktask includes plan and review sections
- promotion criteria are explicit and enforced

## Open Questions

1. Should `quicktask` always require an active feature, or should `000-quicktasks`
   be the default inbox lane?
2. Should brainstorm support multiple iterations on the same artifact, or create
   new timestamped revisions?
3. Should worktree metadata include reviewer assignment, or only implementer lane
   ownership in v1.4?
4. Should `review` and `crossreview` operate against lane-local diffs when lane
   metadata is present, or continue to review feature-wide by default?

## Recommended Next Step

Before implementation, convert this document into a narrower execution plan with:

- exact command text contracts
- exact metadata schema file definitions
- migration notes for current projects that already encode ad hoc worktree paths
- a decision on the `000-quicktasks` fallback model

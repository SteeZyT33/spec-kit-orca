# Orca v1.4 Execution Plan

## Purpose

Translate the v1.4 design into a concrete implementation sequence with exact
file targets, decision locks, and verification steps.

This is still a planning artifact. It is intentionally specific enough to guide
 implementation without improvisation, but it is not the implementation itself.

## Scope

Included in this plan:

- provider-agnostic worktree protocol
- `speckit.orca.brainstorm`
- `speckit.orca.micro-spec`
- documentation and installer updates required to surface the new workflows

Excluded from this plan:

- full autonomous worktree provisioning
- upstream Spec Kit changes
- replacing core Spec Kit commands
- implementing a review engine specialized for lane-local diffs in v1.4

## Locked Decisions

The following decisions are treated as fixed for v1.4:

1. Worktree protocol is Orca-owned and repo-local under `.specify/orca/`.
2. `brainstorm` ends at a durable artifact and a handoff to `specify` or `plan`.
3. `quicktask` is a micro-spec path and must leave a durable record.
4. `quicktask` must declare verification before implementation begins.
5. Agent-specific directories are not the workflow source of truth.

## Decisions To Finalize Before Coding

These should be settled before implementation starts:

1. Quicktask fallback:
   - Option A: require an active feature
   - Option B: support `specs/000-quicktasks/quicktasks.md`
   - Recommendation: Option B for flexibility, with a clear promotion rule.

2. Brainstorm revision model:
   - Option A: single mutable `brainstorm.md`
   - Option B: timestamped brainstorm artifacts
   - Recommendation: Option A for active feature refinement, Option B only for inbox brainstorming before a feature exists.

3. Review scope with worktrees:
   - Option A: feature-wide by default
   - Option B: lane-local when metadata exists
   - Recommendation: Option A in v1.4. Add lane metadata awareness to reporting, but do not change review scope semantics yet.

## File-Level Plan

### Phase 1: Worktree Foundation

#### New files

- `docs/worktree-protocol.md`

Optional in v1.4 if metadata examples are embedded in the doc:

- `.specify/orca/templates/worktree-record.example.json`

#### Modified files

- `commands/assign.md`
- `commands/code-review.md`
- `commands/pr-review.md`
- `commands/self-review.md`
- `README.md`

#### Changes

##### `commands/assign.md`

Replace current worktree assumptions with protocol-aware logic:

- remove language that treats `.claude/worktrees/` as the canonical signal
- define Orca registry lookup under `.specify/orca/worktrees/`
- use `git worktree list` only as a secondary validation signal
- add language for "parallel dispatch mode" based on Orca lane records

Specific sections to update:

- context detection
- skip recommendation logic
- advisory reporting for dependency handoffs

##### `commands/code-review.md`

Add worktree protocol awareness:

- if lane metadata exists, note which lane produced the target work
- record lane context in `review.md`
- do not change core code-review scope in v1.4

##### `commands/pr-review.md`

Add delivery and external-feedback protocol awareness:

- preserve lane and delivery context during PR handling
- handle comment dispositions, review-thread state, and post-merge verification
- keep PR-review separate from implementation-review semantics

##### `commands/self-review.md`

Add worktree-aware friction signals:

- lane churn
- blocked lanes
- abandoned or stale worktrees
- repeated cross-lane handoffs

##### `README.md`

Add:

- worktree protocol summary
- note that worktree semantics are provider-agnostic
- revised workflow diagram reference

#### Acceptance criteria

- no command doc references `.claude/worktrees/` as canonical
- protocol doc defines the registry, lane record, and status model
- `assign`, `code-review`, `pr-review`, and `self-review` use the same terminology for lanes and statuses

### Phase 2: `speckit.orca.brainstorm`

#### New files

- `commands/brainstorm.md`

#### Modified files

- `extension.yml`
- `README.md`

Optional:

- `config-template.yml` if brainstorm gets configurable defaults later

#### Changes

##### `extension.yml`

Add:

- `speckit.orca.brainstorm`

No hook is required in v1.4. A `before_specify` hook can be added later once
the command stabilizes.

##### `commands/brainstorm.md`

Define:

- intent
- required output sections
- artifact placement rules
- handoff rules
- explicit non-goal: no implementation handoff

Suggested command contract:

```text
/speckit.orca.brainstorm [--feature <id>] [problem statement]
```

Behavior outline:

1. Determine whether this is new work or refinement of an active feature.
2. Gather constraints and existing context.
3. Produce structured options and recommendation.
4. Write artifact to the appropriate destination.
5. Recommend `/speckit.specify` or `/speckit.plan`.

##### `README.md`

Add:

- command description
- example usage
- updated workflow including brainstorm as optional pre-spec stage

#### Acceptance criteria

- command is listed in `extension.yml`
- brainstorm artifact destinations are unambiguous
- command text does not push into implementation
- README clearly distinguishes brainstorming from planning

### Phase 3: `speckit.orca.micro-spec`

#### New files

- `commands/micro-spec.md`

Optional:

- `docs/quicktask-format.md`

#### Modified files

- `extension.yml`
- `README.md`
- potentially `commands/code-review.md` if quicktask review language is referenced

#### Changes

##### `extension.yml`

Add:

- `speckit.orca.micro-spec`

##### `commands/micro-spec.md`

Define:

- scope gate
- record format
- artifact placement
- verification mode declaration
- promotion rules
- handoff behavior

Suggested command contract:

```text
/speckit.orca.micro-spec [--feature <id>] [--files <paths>] [task statement]
```

Behavior outline:

1. Determine if the request qualifies as quicktask.
2. If not, stop and promote to full Spec Kit flow.
3. If yes, write or update the quicktask record.
4. Produce a mini-plan.
5. Declare verification mode: `test-first`, `characterization`, or `evidence-first`.
6. Hand off to implementation and code-review within the quicktask record context.

##### `README.md`

Add:

- quicktask explanation
- when to use quicktask vs full spec flow
- one worked example

#### Acceptance criteria

- every quicktask path includes a durable record
- every quicktask declares verification before implementation
- promotion rules are explicit in the command text
- README warns against using quicktask for full feature work

### Phase 4: Workflow Normalization

#### Modified files

- `README.md`
- `docs/orca-v1.4-design.md`
- new protocol docs if needed

#### Changes

- update workflow diagrams
- document how brainstorm, quicktask, and worktree lanes relate
- document migration guidance for existing projects that already embed ad hoc worktree paths in artifacts

#### Acceptance criteria

- workflow docs no longer imply Claude-specific assumptions
- the same user can understand how to work in Codex or Claude without changing the Orca mental model

## Implementation Order

1. Worktree protocol documentation
2. `assign` updates
3. `code-review`, `pr-review`, and `self-review` updates
4. `extension.yml` additions for new commands
5. `brainstorm` command doc
6. `quicktask` command doc
7. README normalization

Reason:

- command docs should be updated against the new worktree terminology before
  adding new commands that depend on it
- `brainstorm` and `quicktask` both need stable artifact and lane terminology

## Suggested Pull Request Breakdown

### PR 1: Worktree Protocol

Files:

- `docs/worktree-protocol.md`
- `commands/assign.md`
- `commands/code-review.md`
- `commands/pr-review.md`
- `commands/self-review.md`

Outcome:

- provider-agnostic lane model

### PR 2: Brainstorm

Files:

- `extension.yml`
- `commands/brainstorm.md`
- `README.md`

Outcome:

- Orca-native ideation command

### PR 3: Quicktask

Files:

- `extension.yml`
- `commands/micro-spec.md`
- `README.md`
- optional `docs/quicktask-format.md`

Outcome:

- micro-spec workflow for bounded work

### PR 4: Documentation Cleanup

Files:

- `README.md`
- `docs/orca-v1.4-design.md`
- `docs/orca-v1.4-execution-plan.md`

Outcome:

- consistent final workflow story

## Testing And Verification Plan

Since this repo is command- and doc-heavy, verification should focus on:

1. Manifest correctness
   - `extension.yml` references valid command files
   - command names match the `speckit.orca.*` pattern

2. Command consistency
   - no command references removed or contradictory workflow semantics
   - brainstorm does not mention implementation handoff
   - quicktask includes explicit promotion rules
   - quicktask includes explicit verification-mode rules

3. Cross-command consistency
   - same worktree vocabulary across `assign`, `review`, and `self-review`
   - same artifact destinations across README and command docs

4. Installation visibility
   - new commands appear after Orca install/refresh for both Codex and Claude integrations

## Risks

### Risk 1: Worktree protocol is under-specified

If the metadata schema is vague, later commands will invent incompatible
interpretations.

Mitigation:

- write a concrete protocol doc before touching command behavior

### Risk 2: Quicktask becomes a loophole

If promotion rules are weak, users will use quicktask for feature work.

Mitigation:

- strict disallowed scope list
- explicit promotion checks

### Risk 3: Quicktask weakens test discipline

If quicktask allows implementation before verification strategy is declared, it
becomes an escape hatch from TDD and evidence-based completion.

Mitigation:

- require `test-first`, `characterization`, or `evidence-first` up front
- promote to full flow when no credible verification mode exists

### Risk 4: Brainstorm duplicates `plan`

If brainstorm contains architecture or implementation decomposition, the flow
will become redundant.

Mitigation:

- keep brainstorm focused on framing, options, and recommendation
- keep plan focused on architecture and implementation shape

## Recommended Immediate Next Step

Before implementation, create `docs/worktree-protocol.md` as the first concrete
artifact. That document should lock:

- registry path
- lane schema
- status transitions
- collision rules
- how command docs refer to active lane context

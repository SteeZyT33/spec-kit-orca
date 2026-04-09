# Orca v1.4 Decision Memo

## Purpose

Resolve the remaining open questions from the v1.4 design and execution plan so
implementation can proceed against stable defaults.

## Decisions

### 1. Quicktask fallback

Decision:

- support a fallback quicktask inbox at `specs/000-quicktasks/quicktasks.md`

Why:

- users will have real small work before a proper feature exists
- forcing a full feature first adds overhead and encourages undocumented work
- the fallback still preserves traceability inside `specs/`

Rule:

- if an active feature is clear, quicktask attaches to that feature
- otherwise it writes to `specs/000-quicktasks/quicktasks.md`
- if the quicktask grows, it promotes to a normal feature flow from there

### 2. Brainstorm revision model

Decision:

- use one mutable `brainstorm.md` per active feature
- use timestamped inbox brainstorm artifacts only before a feature exists

Why:

- feature refinement should converge in one place
- multiple brainstorm revisions inside an active feature will create noise faster
  than value
- inbox brainstorming is exploratory and may not become a feature, so timestamps
  are appropriate there

Rule:

- active feature: `specs/<feature>/brainstorm.md`
- no feature yet: `.specify/orca/inbox/brainstorm-<timestamp>.md`

### 3. Review scope with worktree metadata

Decision:

- keep code-review feature-wide by default in v1.4
- add lane context to reporting, but do not switch code-review semantics yet

Why:

- lane-local review is attractive but changes review behavior materially
- feature-wide code-review is safer while the worktree protocol is still new
- reporting can become lane-aware without forcing a new review mental model

Rule:

- `code-review` may mention lane ownership and lane risk
- `code-review` does not default to lane-local diff review in v1.4

### 4. Registry scope

Decision:

- keep the registry repo-scoped, with each lane record carrying its `feature`

Why:

- multiple features may be active in parallel
- repo-scoped discovery is simpler for commands
- feature-scoped filtering can be done from record fields without multiple
  registries

Rule:

- one repo-local `.specify/orca/worktrees/registry.json`
- lane records must include `feature`

### 5. `task_scope` format

Decision:

- allow both task IDs and bounded symbolic scope labels

Why:

- not all useful work is already decomposed into `T###` tasks
- brainstorm and quicktask may create lanes before formal task IDs exist
- forbidding labels would force fake task creation too early

Allowed examples:

- `["T026", "T028", "T029"]`
- `["UI-POLISH"]`
- `["QT-2026-04-08-01"]`

Constraint:

- labels must be stable and bounded
- free-form paragraph descriptions are not allowed in `task_scope`

### 6. `speckit.orca.worktree` in v1.4

Decision:

- do not ship a dedicated worktree command in the first implementation pass

Why:

- the protocol itself is the critical dependency
- adding command behavior too early will increase surface area before the model is
  proven
- command docs can reference the metadata model before a management command exists

Rule:

- v1.4 implements protocol-aware behavior
- a worktree management command becomes a follow-on once the protocol is used in
  practice

### 7. Quicktask verification model

Decision:

- quicktask must declare verification before implementation begins

Why:

- quicktask should not become a loophole around TDD or evidence-based completion
- many quicktasks should still be test-first
- some quicktasks need a proportional alternative to failing-test-first, not an
  exemption from verification discipline

Allowed modes:

- `test-first`
- `characterization`
- `evidence-first`

Rule:

- behavior-changing code should default to `test-first`
- refactors should default to `characterization`
- docs/tooling/config work may use `evidence-first` when automated tests are not
  the right proof mechanism
- if no credible verification mode can be declared, promote to the full flow

## Final Defaults

These are the implementation defaults for v1.4:

- quicktask fallback: `specs/000-quicktasks/quicktasks.md`
- feature brainstorm file: `specs/<feature>/brainstorm.md`
- pre-feature brainstorm file: `.specify/orca/inbox/brainstorm-<timestamp>.md`
- worktree registry: repo-scoped
- code-review semantics: feature-wide by default
- `task_scope`: task IDs or bounded symbolic labels
- quicktask verification: declared before implementation
- dedicated worktree command: deferred

## Resulting v1.4 Shape

### Minimum command additions

- `speckit.orca.brainstorm`
- `speckit.orca.micro-spec`

### Minimum protocol additions

- repo-scoped worktree registry
- lane record schema
- protocol-aware `assign`, `code-review`, `pr-review`, and `self-review`

### Deferred

- lane-local code-review mode
- automated worktree provisioning
- dedicated `speckit.orca.worktree` command

## Recommended Immediate Next Step

Implementation can now start in this order:

1. update `commands/assign.md` to adopt the worktree protocol
2. update `commands/code-review.md`, `commands/pr-review.md`, and `commands/self-review.md`
3. add `commands/brainstorm.md` and register it
4. add `commands/micro-spec.md` and register it
5. normalize README and docs

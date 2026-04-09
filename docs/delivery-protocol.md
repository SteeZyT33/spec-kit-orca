# Orca Delivery Protocol

## Purpose

Define branch, commit, and pull request standards for Orca-managed feature work,
especially when parallel lanes or worktrees are involved.

This document complements `worktree-protocol.md`.

- `worktree-protocol.md` defines execution topology
- `delivery-protocol.md` defines delivery hygiene

## Scope

This protocol covers:

- branch naming
- commit standards
- lane-to-PR expectations
- merge expectations
- how review and crossreview should reference delivery artifacts

This protocol does not cover:

- the mechanics of automatic PR creation
- repository-specific CI policy
- GitHub-specific labeling or automation details unless Orca later formalizes them

## Design Principles

1. Every lane should produce understandable history.
2. Delivery structure should reflect execution structure.
3. Parallel work should make integration easier, not harder.
4. PR structure should optimize reviewability, not ritual.
5. Feature-level traceability matters more than perfect theoretical cleanliness.

## Core Model

### Feature branch

The feature branch is the integration branch for a feature-level effort.

Example:

```text
004-mneme-viz
```

### Lane branch

A lane branch is a bounded delivery branch associated with a worktree lane.

Example:

```text
004-mneme-viz-ui
004-mneme-viz-backend
004-mneme-viz-review-hardening
```

### Delivery unit

The default delivery unit is:

- one lane branch for one coherent lane of work

This does not always mean one PR per lane, but that is the preferred default
when the lane has meaningful independent review value.

## Branch Naming Standard

### Feature branches

Use:

```text
<feature>
```

Examples:

- `004-mneme-viz`
- `005-auth-hardening`

### Lane branches

Use:

```text
<feature>-<lane>
```

Examples:

- `004-mneme-viz-ui`
- `004-mneme-viz-backend`
- `005-auth-hardening-migrations`

### Quicktask branches

If quicktask work is large enough to justify isolation, use:

```text
<feature-or-inbox>-qt-<short-name>
```

Examples:

- `004-mneme-viz-qt-obsidian-link-fix`
- `000-quicktasks-qt-orca-refresh`

### Rules

1. Branch names must align with lane metadata when lane metadata exists.
2. Two active lanes must not share a branch name.
3. Quicktask should not create a lane branch unless the change benefits from isolation.

## Commit Protocol

## Goals

Commits should be:

- small enough to review
- large enough to preserve intent
- traceable to a feature or quicktask record

## Commit message format

Preferred format:

```text
<type>(<scope>): <summary>
```

Where:

- `type` is one of: `feat`, `fix`, `refactor`, `docs`, `test`, `chore`
- `scope` is feature, lane, or subsystem-oriented

Examples:

```text
fix(orca): refresh installed extensions for current integration
docs(v1.4): add provider-agnostic worktree protocol
refactor(assign): replace claude-specific worktree detection
test(quicktask): add promotion-rule coverage
```

### Lane-aware guidance

If working in a lane, the scope should usually map to the lane or subsystem.

Good:

```text
feat(mneme-viz-ui): add graph lane metadata handling
fix(assign): use orca registry instead of .claude/worktrees
```

Weak:

```text
misc changes
update stuff
```

### Commit frequency

Preferred:

- one commit per meaningful unit of progress
- one commit per task or tightly coupled task group

Avoid:

- giant branch-long "final" commits
- dozens of trivial noise commits with no clear unit of intent

## Lane Commit Rules

### Single-lane work

Use normal coherent commits. No special rules beyond clarity and scope.

### Multi-lane work

Each lane should maintain its own coherent history.

Rules:

1. Do not mix unrelated lane work in one commit.
2. Do not use one lane branch as a dumping ground for leftover changes from another lane.
3. If a shared-file change is unavoidable, call it out explicitly in the commit message or PR summary.

## PR Protocol

## Default policy

Preferred default:

- one PR per meaningful lane

This is not mandatory when the lane is too small to justify review overhead.

## When to use one PR per lane

Use lane PRs when:

- the lane has clear independent scope
- the lane has meaningful diff volume
- cross-lane integration risk is real
- reviewers benefit from separated context

Examples:

- UI lane separate from backend lane
- migration lane separate from feature logic lane

## When to combine lanes into one feature PR

Combine into one PR when:

- lanes are very small
- separation adds more coordination overhead than review value
- the work only makes sense as one integrated change

Examples:

- one quicktask plus one tiny doc lane
- a small follow-up hardening diff on top of the same feature branch

## PR Base Rules

### Lane PRs

Preferred base:

- feature branch when one exists
- `main` only when the lane itself is the primary feature delivery branch

### Feature PRs

Preferred base:

- `main`

## PR Title Guidance

Preferred formats:

Lane PR:

```text
<feature>: <lane summary>
```

Examples:

```text
004-mneme-viz: graph UI lane
005-auth-hardening: migration lane
```

Feature PR:

```text
<feature>: <feature summary>
```

Examples:

```text
004-mneme-viz: add memory visualization dashboard
```

## PR Body Expectations

Minimum content:

- what changed
- lane or feature scope
- major files or subsystems touched
- risks
- validation performed
- relationship to feature artifacts

When lane metadata exists, PRs should reference:

- lane ID
- feature ID
- task scope or quicktask ID

## Merge Protocol

### Lane merge target

Lane branches should usually merge into the feature branch first.

Why:

- keeps feature integration visible
- avoids partially shipped feature fragments reaching `main`
- matches the Orca lane model

### Feature merge target

Feature branches merge into `main`.

### Exceptions

Lane branches may merge directly to `main` when:

- there is no true feature branch
- the work is a standalone quicktask
- the team deliberately chose a single-lane feature delivery model

## Squash vs Preserve

### Preserve history when

- lane history reflects meaningful staged work
- reviewers benefit from commit-by-commit reasoning
- the feature is complex and auditability matters

### Squash when

- the lane history is noisy
- the change is small
- the branch accumulated fixup commits without useful historical value

Default recommendation:

- preserve meaningful lane history during feature integration
- squash only when the resulting history is materially clearer

## Relationship To Orca Commands

### `speckit.orca.assign`

Should:

- treat branch and lane identity as linked
- avoid recommending parallel lanes without a coherent delivery shape

### `speckit.orca.code-review`

Should:

- mention lane branch when lane metadata exists
- note whether the target is lane review or feature review

### `speckit.orca.pr-review`

Should:

- track PR shape, comment-response status, and thread resolution state
- note whether the target is a lane PR or feature PR

### `speckit.orca.cross-review`

Should:

- include lane context when present
- identify whether the review target is lane-local or feature-wide

### `speckit.orca.self-review`

Should:

- use commit and PR structure as workflow evidence
- identify noisy history, unclear merge shape, or lane delivery friction

## Quicktask Delivery Rules

Quicktask defaults to the simplest delivery path.

Preferred:

- commit directly on the active feature branch when the change is truly small

Escalate to isolated branch or lane when:

- the diff is not trivially reviewable
- the quicktask touches risky files
- the change may need iterative review before integration

If quicktask promotes to full spec flow, delivery expectations immediately
follow the normal feature/lane rules.

## Anti-Patterns

Avoid:

1. One branch containing mixed unrelated lane work.
2. One PR containing multiple large lanes with no explanation.
3. Quicktask branches that become shadow features without promotion.
4. Merging active lanes to `main` while the feature branch still diverges.
5. Commit messages that hide why a lane existed.

## Minimum v1.4 Standard

The minimum acceptable delivery behavior for v1.4 is:

1. lane branches use stable feature-derived names
2. commits are coherent and scoped
3. PRs identify lane or feature context
4. lane work usually merges into the feature branch first
5. review artifacts can reference lane delivery context

## Recommended Follow-On

After v1.4 protocol adoption, consider:

- formal PR body templates for lane vs feature PRs
- lane-aware `crossreview` artifact naming
- optional automatic branch naming suggestions from Orca

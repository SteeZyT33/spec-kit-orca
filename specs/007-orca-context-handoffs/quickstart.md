# Quickstart: Orca Context Handoffs

## Goal

Validate that Orca can preserve workflow continuity across stage transitions
using durable artifacts instead of active session memory.

## Example Handoff Artifact

Create a handoff file at
`specs/007-orca-context-handoffs/handoffs/brainstorm-to-specify.md` using the
canonical format:

```text
# Handoff: brainstorm -> specify

Source: brainstorm
Target: specify
Branch: 007-orca-context-handoffs
Lane:
Created: 2026-04-09T00:00:00Z

## Summary
Convert the context-handoff idea into a formal feature spec focused on explicit
stage transitions and durable upstream references.

## Upstream Artifacts
- specs/007-orca-context-handoffs/brainstorm.md

## Open Questions
- Should handoffs live as dedicated files, embedded sections, or both?
```

The consumer entering `specify` should resolve that file first before falling
back to branch or artifact-only inference.

## Example Embedded Handoff Locator

If the handoff is embedded instead of stored as a dedicated file, use a locator
such as:

```text
specs/007-orca-context-handoffs/brainstorm.md::section-title=Handoff: brainstorm -> specify
```

The resolver must locate that handoff by finding a heading whose title text is
exactly:

```text
Handoff: brainstorm -> specify
```

## Scenario 1: Brainstorm -> Specify

1. Start from a brainstorm artifact.
2. Enter the specify stage.
3. Verify the intended upstream brainstorm context is explicitly resolvable.
4. Verify the resolver reports `file` as the winning storage shape.

## Scenario 2: Specify -> Plan

1. Start from a spec artifact.
2. Enter planning.
3. Verify the relevant upstream spec context and unresolved questions are still
   visible.
4. Verify that if no explicit handoff exists, the resolver reports the
   transition as inferred rather than explicit.

## Scenario 3: Implement -> Review

1. Start from implementation-ready artifacts.
2. Enter code review.
3. Verify review can resolve the intended upstream artifacts and summary.
4. Verify the resolution output includes whether branch or lane context was used.

## Scenario 4: Fresh Session / Worktree Continuity

1. Re-enter the feature from a fresh session or worktree.
2. Verify Orca can still resolve upstream context without replaying prior chat.
3. Verify missing lane metadata degrades safely and is reported as unused rather
   than treated as an error.

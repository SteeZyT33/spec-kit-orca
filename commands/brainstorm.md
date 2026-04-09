---
description: Structured pre-spec ideation that captures the problem, options, constraints, and recommendation without dropping into implementation.
handoffs:
  - label: Write The Spec
    agent: speckit.specify
    prompt: Turn the brainstorm output into a proper spec
  - label: Plan The Feature
    agent: speckit.plan
    prompt: Turn the brainstorm output into an implementation plan
  - label: Use Quicktask Instead
    agent: speckit.orca.micro-spec
    prompt: This looks small enough for the micro-spec lane
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Purpose

This command is Orca's native ideation stage. It exists to replace dependence on
external brainstorming workflows and keep early design work inside the same Spec
Kit ecosystem as the rest of the feature lifecycle.

This is **not** an implementation command.

## Workflow Contract

- Capture framing, constraints, alternatives, and a recommendation.
- Stop before implementation.
- Do not generate implementation tasks.
- Do not route directly to `/speckit.implement`.
- Hand off to `/speckit.specify`, `/speckit.plan`, or `/speckit.orca.micro-spec`.

## Outline

1. Determine whether the request is:
   - new feature ideation
   - refinement of an existing feature
   - small enough to fit the micro-spec lane instead

2. Resolve artifact destination:
   - If `--feature <id>` was provided, use `specs/<feature>/brainstorm.md`
   - Else if an active feature context can be resolved from the current branch or prerequisite script, use `specs/<feature>/brainstorm.md`
   - Else write a new inbox artifact to `.specify/orca/inbox/brainstorm-<timestamp>.md`

3. Gather the minimum context needed:
   - the user request
   - any existing `spec.md`, `plan.md`, `tasks.md`, `research.md`, or `review.md` for the target feature if it exists
   - any relevant repo constraints that materially shape the solution

4. Produce a structured brainstorm artifact with these sections:

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

5. In `## Options Considered`, include at least:
   - one favored path
   - one meaningful alternative
   - brief reasons for rejection or downgrade of the alternative

6. In `## Ready For Spec`, write a short handoff summary suitable for the next command:
   - If this needs a formal feature spec, recommend `/speckit.specify`
   - If a spec already exists and the main missing artifact is architecture/decomposition, recommend `/speckit.plan`
   - If the work is bounded enough for the micro-spec lane, recommend `/speckit.orca.micro-spec`

7. Output a concise summary to the user:
   - artifact path
   - recommended next command
   - any unresolved questions that block progression

## Guardrails

- If the work is clearly a small bugfix, narrow refactor, tooling tweak, or docs update, say so and recommend `/speckit.orca.micro-spec` instead of pretending it needs full feature ideation.
- If the request is still too vague after initial framing, state the open questions explicitly in the artifact instead of making false precision.
- If an existing feature artifact already contains a brainstorm file, update it in place rather than creating a parallel brainstorm file in the same feature directory.

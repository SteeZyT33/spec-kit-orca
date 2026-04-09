---
description: Canonical micro-spec workflow for bounded work. Requires a mini-plan, declared verification mode, code review, and promotion to full spec flow when the scope grows.
handoffs:
  - label: Implement The Micro-Spec
    agent: speckit.implement
    prompt: Implement the micro-spec against the recorded mini-plan and verification mode
  - label: Review The Micro-Spec
    agent: speckit.orca.code-review
    prompt: Review the micro-spec implementation and verification evidence
  - label: Promote To Full Spec
    agent: speckit.specify
    prompt: This micro-spec has grown and should be promoted to the full Spec Kit flow
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Purpose

This command handles bounded work without requiring a full `spec.md + plan.md +
tasks.md` flow, while preserving traceability, verification, and review.

This command is a **micro-spec** path, not a spec bypass.

## Workflow Contract

- Always create or update a durable micro-spec record before implementation.
- Always produce a mini-plan.
- Always declare a verification mode before implementation.
- Always include code review in the lifecycle.
- Promote to the full feature flow when the work exceeds micro-spec bounds.

## Verification Discipline

Micro-spec is not exempt from test discipline. It is only exempt from full task
decomposition.

Allowed verification modes:

- `test-first`: write a failing test first, then implement
- `characterization`: lock current behavior with a regression or characterization test before refactoring
- `evidence-first`: declare explicit non-test verification for docs, tooling, or config work where automated tests are not the right proof mechanism

Default expectations:

- behavior-changing code should default to `test-first`
- refactors should default to `characterization`
- `evidence-first` should be used only when test-first is genuinely the wrong proof mechanism

If no credible verification mode can be declared up front, stop and promote to
the full Spec Kit flow.

## Outline

1. Determine whether the request qualifies as a micro-spec.

   Suitable:
   - small bugfix
   - limited refactor
   - tooling tweak
   - docs update
   - narrow maintenance task

   Not suitable:
   - new feature with multiple user stories
   - architecture change
   - data model or contract change
   - work requiring parallel lane decomposition
   - security, auth, migration, or destructive-risk work

2. If the work does **not** qualify:
   - say so explicitly
   - recommend promotion to `/speckit.specify` and the normal feature flow
   - stop

3. Resolve artifact destination:
   - If `--feature <id>` was provided, append to `specs/<feature>/micro-specs.md`
   - Else if an active feature context can be resolved, append to `specs/<feature>/micro-specs.md`
   - Else append to `specs/000-micro-specs/micro-specs.md`

4. Create a new micro-spec record with a stable ID and this structure:

   ```markdown
   ## MS-YYYY-MM-DD-XX

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

   **Promotion Check**: stayed micro-spec | promoted to full spec
   ```

5. In `### Plan`, write the smallest useful ordered implementation plan.

6. In `### Verification Plan`, declare the verification mode and the concrete evidence that will be required:
   - failing test name or command for `test-first`
   - characterization/regression command for `characterization`
   - explicit command, output, screenshot, or manual verification steps for `evidence-first`

7. Before handing off to implementation, perform a promotion check. Promote immediately if:
   - more than one coherent user story appears
   - the mini-plan exceeds 5 to 7 meaningful steps
   - multiple domains require coordinated handoffs
   - parallel lanes are needed
   - data model or contract changes are required
   - security, auth, migration, or destructive-risk work is involved
   - no credible verification mode can be declared

8. If the micro-spec remains valid, summarize for the user:
   - micro-spec ID
   - artifact path
   - verification mode
   - recommended next step: implement, then code-review

## Finalization Rules

- Mark a micro-spec `done` only after verification evidence and review outcome are recorded.
- If the work grows during implementation, update `**Promotion Check**` to `promoted to full spec` and stop treating it as a micro-spec.
- If the micro-spec ends up requiring a branch or lane for isolation, that is allowed, but it still remains attached to its micro-spec record until promoted or completed.

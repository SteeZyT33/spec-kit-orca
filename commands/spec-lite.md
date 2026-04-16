---
description: Lightweight intake for bounded new work. Creates a single-file spec-lite record with problem, solution, acceptance scenario, and files affected. No phase gates, no mandatory reviews, no promotion command.
handoffs:
  - label: Implement It
    agent: speckit.implement
    prompt: Implement the change described in the spec-lite record
  - label: Mark Done
    agent: speckit.orca.spec-lite
    prompt: Mark the spec-lite record as implemented
  - label: Full Spec Instead
    agent: speckit.specify
    prompt: This work has grown beyond spec-lite scope — start a full feature spec
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Purpose

`spec-lite` is Orca's lightweight intake for bounded new work — a bug fix,
a one-module refactor, a doc update, a small behavior tweak. It exists so
operators have a durable record of what they're doing and why, without the
ceremony of the full `brainstorm → specify → plan → tasks → implement →
reviews` pipeline.

This is **not** a full spec. If the work touches multiple modules, needs a
plan, or benefits from review gates, recommend `/speckit.specify` instead.

## Workflow Contract

- Create or inspect a spec-lite record under `.specify/orca/spec-lite/`.
- Stop before implementation unless the user explicitly asks to proceed.
- Do not create matriarch lanes against spec-lite records (the guard will
  reject them).
- Do not invent a promotion command — if scope grows, the operator
  hand-authors a full spec and cites the spec-lite by ID.

## Outline

1. **Determine the action** from the user input:
   - If the user names a specific spec-lite ID (e.g., "SL-001"), inspect
     or update that record.
   - If the user describes new work, create a new record.
   - If the user says "list" or "show all", list records.

2. **For new records**, gather:
   - **Title**: a short name for the work
   - **Problem**: 1-2 sentences — what's broken, missing, or needed
   - **Solution**: 1-2 sentences — what you're doing about it
   - **Acceptance Scenario**: one BDD given/when/then (manual or test)
   - **Files Affected**: list of paths that will change

   Then create the record:

   ```bash
   uv run python -m speckit_orca.spec_lite --root <repo> create \
       --title "..." \
       --problem "..." \
       --solution "..." \
       --acceptance "..." \
       --files-affected "path1,path2"
   ```

3. **For status updates**, use:

   ```bash
   uv run python -m speckit_orca.spec_lite --root <repo> update-status <id> implemented
   ```

   Optionally attach verification evidence:

   ```bash
   uv run python -m speckit_orca.spec_lite --root <repo> update-status <id> implemented \
       --verification-evidence "pytest tests/test_foo.py -v → 3 passed"
   ```

4. **For inspection**, use flow-state on the record file:

   ```bash
   uv run python -m speckit_orca.flow_state .specify/orca/spec-lite/<id>.md
   ```

   Or list all records:

   ```bash
   uv run python -m speckit_orca.spec_lite --root <repo> list
   uv run python -m speckit_orca.spec_lite --root <repo> list --status open
   ```

5. **Output a concise summary** to the user:
   - Record path and ID
   - Current status
   - Recommended next action (implement → mark done → optional verification)

## Guardrails

- If the work clearly needs a plan, multiple review passes, or matriarch
  lane coordination, say so and recommend `/speckit.specify` instead of
  cramming it into spec-lite.
- If the user tries to register a matriarch lane against a spec-lite,
  explain that spec-lite doesn't participate in lanes. If they need
  coordination, they should promote to a full spec manually.
- Verification evidence is optional — don't push it. Many spec-lite
  records will never have it. That's by design.
- Reviews are opt-out — don't suggest cross-review unless the operator
  explicitly asks for one. Most spec-lite records will never be reviewed.
- If scope grows mid-implementation, recommend hand-authoring a full spec
  under `specs/NNN-<name>/` and citing the spec-lite by ID in the full
  spec's body. There is no `promote` command.
- The overview file `00-overview.md` is auto-regenerated on every
  create / update-status call — do not hand-edit it.

---
description: Brownfield intake for existing features. Creates a single-file adoption record with summary, location, and key behaviors. Reference-only — never reviewed, not drivable by yolo, cannot anchor a matriarch lane.
handoffs:
  - label: Full Spec For This Area
    agent: speckit.specify
    prompt: The area covered by this adoption record needs a full spec for new work
  - label: Supersede With Full Spec
    agent: speckit.orca.adopt
    prompt: A full spec has been authored that replaces this adoption record — run supersede
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Purpose

`adopt` is Orca's brownfield intake — it registers existing features that
predate Orca so flow-state can report on them and matriarch can reason
about work adjacent to them. Adoption records are reference-only: they
describe what already exists, not work being done.

Use `adopt` when: the codebase has features built before Orca that need
a durable record. Use `spec-lite` for small NEW work. Use the full spec
path for substantial new features.

## Workflow Contract

- Create, inspect, supersede, or retire adoption records under
  `.specify/orca/adopted/`.
- Do not start implementation against an adoption record — ARs describe
  existing code, not planned work.
- Do not register matriarch lanes against adoption records (the guard
  rejects them).
- Do not run reviews against ARs. `review_state` is hard-coded to
  `"not-applicable"` — there is nothing to review.
- If the operator needs coordination on an area an AR covers,
  recommend hand-authoring a full spec under `specs/` and citing the AR
  as context.

## Outline

1. **Determine the action** from the user input:
   - "adopt this feature" / "register <name>" → create a new AR
   - "list" / "show adopted" → list records
   - "supersede AR-NNN with <spec-id>" → supersede flow
   - "retire AR-NNN" → retirement flow
   - Naming a specific AR ID → inspect that record

2. **For new records**, gather:
   - **Title**: short name for the feature (e.g., "CLI entrypoint")
   - **Summary**: 1-3 sentences describing what the feature does
   - **Location**: file paths or module names where the feature lives
     (at least one)
   - **Key Behaviors**: observed behaviors as bullet points (at least one)
   - **Known Gaps** (optional): what's missing, unreviewed, or not yet
     Orca-managed

   Then create the record:

   ```bash
   uv run python -m speckit_orca.adoption --root <repo> create \
       --title "..." \
       --summary "..." \
       --location "src/foo/bar.py" \
       --location "src/foo/baz.py" \
       --key-behavior "Does X when invoked with Y" \
       --key-behavior "Loads config from Z on startup"
   ```

   The runtime auto-populates `Adopted-on` (today) and `Baseline Commit`
   (HEAD SHA). Pass `--no-baseline` to omit the commit field, or
   `--baseline-commit <sha>` to pin a specific value.

3. **For supersession**, the operator has already authored a full spec
   under `specs/<spec-id>/`. Run:

   ```bash
   uv run python -m speckit_orca.adoption --root <repo> supersede <ar-id> <spec-id>
   ```

   This validates that `specs/<spec-id>/spec.md` exists (rejects if
   not), writes `## Superseded By` into the AR, updates
   `Status: superseded`, and regenerates the overview.

4. **For retirement** (feature removed from the codebase):

   ```bash
   uv run python -m speckit_orca.adoption --root <repo> retire <ar-id> --reason "Removed in v3.0"
   ```

   Without `--reason`, no `## Retirement Reason` section is written —
   `Status: retired` is the signal. The AR file stays on disk as
   historical record.

5. **For inspection**, use flow-state on the record file:

   ```bash
   uv run python -m speckit_orca.flow_state .specify/orca/adopted/<id>.md
   ```

   Or list all records:

   ```bash
   uv run python -m speckit_orca.adoption --root <repo> list
   uv run python -m speckit_orca.adoption --root <repo> list --status superseded
   ```

6. **Output a concise summary** to the user:
   - Record path and ID
   - Current status and Baseline Commit (if present)
   - For new records: recommended next step (usually: "done — the
     feature is now known to Orca; proceed with other work")
   - For superseded/retired: confirm the transition and remind that
     the AR file is preserved

## Guardrails

- If the operator asks to review an AR or run yolo against one,
  explain that ARs are reference-only. `review_state: "not-applicable"`
  is a hard invariant. If they need quality gates, recommend authoring a
  full spec for the new work and running reviews against that.
- If the operator tries to register a matriarch lane against an AR,
  explain the guard rejection and direct them to author a full spec
  citing the AR.
- Do not confuse `adopt` with `spec-lite`. Spec-lite is for NEW bounded
  work. Adopt is for EXISTING features. Different shapes, different
  registries, different lifecycles.
- The `supersede` command requires the target spec to exist on disk.
  If the operator hasn't authored it yet, guide them to do so first
  (possibly via `/speckit.specify`), then come back and supersede.
- When the operator describes an existing feature to adopt, help them
  focus on **observable behaviors** and **file locations**, not on what
  should change or improve. The AR captures what IS, not what should be.
  Improvement ideas belong in a spec-lite or full spec.
- The overview file `00-overview.md` is auto-regenerated on every
  create / supersede / retire call — do not hand-edit it.
- If the operator wants to bulk-adopt many features at once, note that
  v1 is one record at a time. A future `adopt scan` command may add
  repo-wide discovery — for now, create ARs manually one by one.

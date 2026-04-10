# Data Model: Orca Context Handoffs

## Stage Handoff

Represents a durable transition from one workflow stage to another.

### Fields

| Field | Type | Required | Notes |
|---|---|---|---|
| `source_stage` | enum | yes | One canonical stage id from `contracts/stage-transitions.md` |
| `target_stage` | enum | yes | Next intended consumer stage |
| `summary` | string | yes | Short transition summary |
| `upstream_artifacts` | list | yes | Primary artifact paths the next stage should read |
| `open_questions` | list | no | Outstanding issues or unknowns |
| `branch` | string/null | no | Current feature branch when relevant |
| `lane_id` | string/null | no | Orca lane/worktree ID when relevant |
| `created_at` | datetime/date | yes | Transition creation/update time |
| `storage_shape` | enum | yes | `file` or `embedded` |
| `locator` | string | yes | Derived repo-relative path or section identifier |

### Validation Rules

- `source_stage` and `target_stage` must not be the same.
- `source_stage` and `target_stage` must use canonical stage ids from
  `contracts/stage-transitions.md`.
- `upstream_artifacts` must contain at least one durable artifact path.
- Missing branch/lane context must not invalidate the handoff.
- `storage_shape=file` should use the canonical `specs/<feature>/handoffs/<source>-to-<target>.md` locator pattern.
- The `summary` field maps exactly to the serialized `## Summary` section body.
- `created_at` must use RFC3339 so resolver tie-break comparisons remain deterministic.
- `storage_shape` and `locator` are derived from where the handoff is found and
  do not need explicit serialized keys in the canonical file body.

## Handoff Resolution Result

Represents what Orca resolved as the relevant upstream context for a stage.

### Fields

| Field | Type | Required | Notes |
|---|---|---|---|
| `target_stage` | enum | yes | Canonical stage id being entered |
| `resolved_handoff` | string/null | no | Matching handoff artifact or section identifier |
| `resolved_artifacts` | list | yes | Upstream artifacts to use |
| `resolution_reason` | string | yes | Why Orca chose this context |
| `used_branch_context` | boolean | yes | Whether branch/worktree context influenced resolution |
| `used_lane_context` | boolean | yes | Whether lane metadata influenced resolution |
| `winning_storage_shape` | enum | yes | `file`, `embedded`, or `artifact-only` |
| `ambiguity_detected` | boolean | yes | Whether multiple candidate contexts conflicted |
| `uniqueness_violation_detected` | boolean | yes | Whether more than one canonical handoff file existed for one transition |

### Validation Rules

- A missing handoff may degrade to artifact-only resolution, but that should be
  explicit in `resolution_reason`.
- `winning_storage_shape=artifact-only` means `resolved_handoff` must be null.
- `winning_storage_shape` is the resolver output field and does not replace the
  handoff artifact's `storage_shape` field.
- `storage_shape` describes how a stored handoff is encoded, while
  `winning_storage_shape` describes what the resolver selected at runtime.

## Stage Transition Contract

Defines which stage-to-stage transitions Orca supports explicitly.

### Fields

| Field | Type | Required | Notes |
|---|---|---|---|
| `source_stage` | enum | yes | Canonical upstream stage id |
| `target_stage` | enum | yes | Canonical downstream stage id |
| `required_inputs` | list | yes | Minimum durable inputs expected |
| `continuity_summary` | string | yes | What context must be preserved |
| `open_question_scope` | string | yes | Which unresolved questions carry forward |
| `optional_context` | list | no | Branch/lane or supplemental context |

### Validation Rules

- Supported transitions should cover the main Orca workflow only.

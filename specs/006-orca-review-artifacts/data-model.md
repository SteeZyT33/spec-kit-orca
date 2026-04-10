# Data Model: Orca Review Artifacts

## Representation Note

The fields in this data model are conceptual fields used to reason about review
artifact behavior and downstream consumption. In v1 they are not required to
appear as YAML frontmatter or another machine-readable header inside the files.

Unless a later contract says otherwise:

- `artifact_name`, `stage`, `owner_command`, `primary`, and `summary_only` are
  inferred from the artifact naming and ownership contracts
- `status` is inferred from the detection contract in
  `contracts/review-artifact-files.md`
- `last_updated` is logical metadata a future consumer may derive from file
  timestamps or commit history rather than an embedded field

## Review Artifact

Represents one durable review-stage artifact for a feature.

### Fields

| Field | Type | Required | Notes |
|---|---|---|---|
| `artifact_name` | string | yes | e.g. `review-code.md` |
| `stage` | enum | yes | `spec`, `plan`, `code`, `cross`, `pr`, `self`, `summary` |
| `owner_command` | string | yes | e.g. `speckit.orca.code-review` |
| `primary` | boolean | yes | Whether this is the authoritative artifact for the stage |
| `summary_only` | boolean | yes | True for summary/index artifacts such as `review.md` |
| `status` | enum | yes | `present`, `missing`, `stale`, `superseded` |

### Validation Rules

- only one primary artifact may exist per review stage
- `summary_only` artifacts must not be the only durable evidence for stage
  completion
- `present` and `missing` are the only required v1 statuses; `stale` and
  `superseded` remain future states unless separately defined

## Review Stage

Represents a workflow review boundary Orca wants to reason about durably.

### Fields

| Field | Type | Required | Notes |
|---|---|---|---|
| `name` | enum | yes | `spec`, `plan`, `code`, `cross`, `pr`, `self` |
| `artifact_path` | string | yes | expected primary artifact path |
| `completed` | boolean | yes | inferred from durable evidence |
| `last_updated` | date/null | no | latest durable evidence timestamp |

### Validation Rules

- `self` must remain distinct from implementation-review stages
- `cross` and `pr` must not be conflated with `code`

## Review Summary Index

Represents the umbrella summary entrypoint currently modeled as `review.md`.

### Fields

| Field | Type | Required | Notes |
|---|---|---|---|
| `artifact_path` | string | yes | `review.md` |
| `stage_overview` | list | yes | summary of stage artifacts and statuses |
| `latest_blockers` | list | no | unresolved high-level blockers |
| `latest_updates` | list | no | recent review events |

### Validation Rules

- the summary index must not be the only review artifact
- the summary must point clearly to stage artifacts

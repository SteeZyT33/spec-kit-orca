# Contract: Handoff Artifact

## Purpose

Define the minimum durable handoff shape Orca uses between workflow stages.

## Canonical Storage

The first implementation should support one canonical storage shape and one
compatible embedded shape:

- canonical file artifact:
  `specs/<feature>/handoffs/<source>-to-<target>.md`
- compatible embedded section:
  a Markdown heading whose title text is exactly
  `Handoff: <source> -> <target>` inside the upstream stage artifact

If both exist for the same transition, the dedicated handoff file is
authoritative.

## Required Fields

- source stage
- target stage
- transition summary
- upstream artifact paths
- unresolved questions
- branch or lane context when relevant

## Canonical File Shape

```text
# Handoff: <source> -> <target>

Source: <canonical source_stage>
Target: <canonical target_stage>
Branch: <feature branch or blank>
Lane: <lane id or blank>
Created: <RFC3339 timestamp>

## Summary
<short transition summary>

## Upstream Artifacts
- <repo-relative path>
- <repo-relative path>

## Open Questions
- <question>
- None
```

## Canonical Serialization Keys

The exact top-level serialized keys are:

- `Source`
- `Target`
- `Branch`
- `Lane`
- `Created`

The exact section headings are:

- `## Summary`
- `## Upstream Artifacts`
- `## Open Questions`

## Data Model Mapping

Serialized artifact fields map to the data model exactly as follows:

| Serialized shape | Data model field | Notes |
|---|---|---|
| `Source:` | `source_stage` | exact canonical stage id |
| `Target:` | `target_stage` | exact canonical stage id |
| `Branch:` | `branch` | blank maps to `null` |
| `Lane:` | `lane_id` | blank maps to `null` |
| `Created:` | `created_at` | must be RFC3339 |
| `## Summary` body | `summary` | preserve full section body |
| `## Upstream Artifacts` list | `upstream_artifacts` | repo-relative paths |
| `## Open Questions` list | `open_questions` | `- None` maps to empty list |

Additional data-model fields are derived, not serialized:

- `storage_shape`
  - `file` for canonical handoff files
  - `embedded` for embedded handoff sections
- `locator`
  - repo-relative file path for canonical files
  - `<artifact-path>::section-title=Handoff: <source> -> <target>` for embedded
    sections

## Locator Rules

- File paths must be repo-relative when serialized in the handoff body.
- File names must use the canonical stage ids from
  `contracts/stage-transitions.md`.
- One transition should have exactly zero or one valid canonical handoff file.
- If more than one canonical handoff file is detected for the same transition,
  that is a contract violation. The resolver may pick one deterministically for
  diagnostics, but it must also report ambiguity.
- If an embedded section is used instead of a dedicated file, it must preserve
  the same field set and section order closely enough for deterministic parsing.
- Embedded handoff lookup must use exact section-title text match against
  `Handoff: <source> -> <target>` with case-sensitive canonical stage ids.
- Embedded heading depth may vary, but the heading title text must match
  exactly after removing Markdown heading markers and one following space.

## Behavior

- Handoffs must prefer durable artifacts over prompt reconstruction.
- Handoffs may be separate files or embedded sections, but the canonical file
  shape above is the default for implementation and parser logic.
- Missing optional branch/lane context must not invalidate the handoff.
- Missing open questions must serialize as `- None` or an empty section rather
  than deleting the section entirely.
- The summary field in the data model maps exactly to the `## Summary` section
  body in serialized artifacts.

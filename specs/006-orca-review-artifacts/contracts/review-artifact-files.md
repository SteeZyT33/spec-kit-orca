# Contract: Review Artifact Files

## Preferred Artifact Set

```text
specs/<feature>/
├── review.md
├── review-code.md
├── review-cross.md
├── review-pr.md
└── self-review.md
```

Future-ready but optional:

```text
specs/<feature>/
├── review-spec.md
└── review-plan.md
```

## File Semantics

- `review.md`: summary/index of review stages, latest blockers, and links
- `review-code.md`: implementation review findings and actions
- `review-cross.md`: alternate-agent or external adversarial review findings
- `review-pr.md`: PR lifecycle evidence, comment disposition, and post-merge checks
- `self-review.md`: process retrospective only

## Detection Contract

For v1, later consumers such as `005-orca-flow-state` should use these rules:

- a stage is `present` if its primary stage artifact file exists in
  `specs/<feature>/`
- a stage is `missing` if its primary stage artifact file does not exist
- `review.md` is `summary_only` and must not by itself count as proof that code
  review, cross-review, or PR review happened
- `self-review.md` counts only for self-review and must not satisfy code
  review, cross-review, or PR review milestones
- `stale` and `superseded` states are reserved for later versions unless a
  future contract explicitly defines how to mark them

## Minimal Stage Artifact Shape

The first version does not require YAML frontmatter. Stage artifacts must be
structured enough for humans and later tools to distinguish them by purpose.

Required minimum:

- file name matches the owned stage artifact
- top-level heading identifies the review stage
- feature identification is present near the top of the file
- findings, blockers, or disposition notes appear in the stage artifact rather
  than only in `review.md`

`review.md` remains the summary/index and should link to or reference the stage
artifacts rather than duplicate every detailed finding.

## Migration Rule

The first implementation may keep existing `review.md` flows working while
adding stage artifacts additively.

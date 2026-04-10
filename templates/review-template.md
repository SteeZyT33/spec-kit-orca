---
description: "Summary/index template for feature review status"
---

# Review Summary: [FEATURE NAME]

**Feature Branch**: `[###-feature-name]`
**Spec**: [spec.md](spec.md)

<!--
  This file is the human-facing summary/index for review progress.
  Stage-specific artifacts hold the detailed durable evidence:
  - review-code.md
  - review-cross.md
  - review-pr.md
  - self-review.md
-->

## Review Artifacts

| Stage | Artifact | Status | Notes |
|---|---|---|---|
| Code Review | [review-code.md](review-code.md) | PRESENT \| MISSING | [latest note] |
| Cross-Review | [review-cross.md](review-cross.md) | PRESENT \| MISSING | [latest note] |
| PR Review | [review-pr.md](review-pr.md) | PRESENT \| MISSING | [latest note] |
| Self-Review | [self-review.md](self-review.md) | PRESENT \| MISSING | [latest note] |

## Latest Review Status

- Current blockers: [summary]
- Delivery readiness: ready for PR review | blocked | post-merge pending
- Latest review update: [date + artifact]

## Artifact Notes

- `review.md` is the summary/index only.
- Detailed findings belong in the stage artifacts, not duplicated here.
- If a stage artifact is missing, that stage should be treated as incomplete.

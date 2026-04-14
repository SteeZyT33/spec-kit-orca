---
description: "Summary/index template for feature review status (012 review model)"
---

# Review Summary: [FEATURE NAME]

**Feature Branch**: `[###-feature-name]`
**Spec**: [spec.md](spec.md)

<!--
  This file is the human-facing summary/index for review progress.
  The three review artifacts hold the detailed durable evidence:
  - review-spec.md  (cross-only adversarial spec review)
  - review-code.md  (self+cross per phase)
  - review-pr.md    (PR comment disposition + retro)
-->

## Review Artifacts

| Artifact | Status | Notes |
|---|---|---|
| [review-spec.md](review-spec.md) | PRESENT \| MISSING \| STALE | [latest note] |
| [review-code.md](review-code.md) | PRESENT \| MISSING | [latest note] |
| [review-pr.md](review-pr.md) | PRESENT \| MISSING | [latest note] |

## Latest Review Status

- Current blockers: [summary]
- Delivery readiness: ready for PR review | blocked | post-merge pending
- Latest review update: [date + artifact]

## Artifact Notes

- `review.md` is the summary/index only.
- Detailed findings belong in the three stage artifacts, not duplicated here.
- If a stage artifact is missing, that stage should be treated as incomplete.

---
description: "Template for review-pr.md — PR comment disposition + retro (012 review model)"
---

# Review: PR Comments

## PR Identifier
- repository: <owner>/<repo>
- number: <PR number>
- opened: YYYY-MM-DD

## External Comments

### Round 1 (YYYY-MM-DD)
- **Comment #N** (reviewer: <name>, date: YYYY-MM-DD)
  - thread: "<short quote or summary>"
  - disposition: addressed | rejected | deferred
  - commit: <sha> (if addressed)
  - response: "<explanation>" (if rejected or deferred)

## Retro Note

[One paragraph: what worked, what didn't, what to change for next
cycle. Required even when empty — use "No workflow changes needed
this cycle." as the minimum.]

## Verdict
- status: merged | pending-merge | reverted
- merged-at: YYYY-MM-DD (required if status is merged)

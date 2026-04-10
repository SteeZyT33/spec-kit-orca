---
description: Compatibility alias for the legacy overloaded review command. Prefer speckit.orca.code-review for implementation review and speckit.orca.pr-review for GitHub review handling.
handoffs:
  - label: Run Code Review
    agent: speckit.orca.code-review
    prompt: Run implementation review against the spec, plan, tasks, and changed code
  - label: Run PR Review
    agent: speckit.orca.pr-review
    prompt: Process PR comments, review threads, and post-merge verification
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Purpose

This command exists for backward compatibility only.

Orca now separates the old overloaded review workflow into two commands:

- `/speckit.orca.code-review` for implementation review
- `/speckit.orca.pr-review` for PR comments, reviewer feedback, thread handling,
  and post-merge verification

Under the current review-artifact model:

- `/speckit.orca.code-review` owns `review-code.md`
- `/speckit.orca.pr-review` owns `review-pr.md`
- `review.md` remains the human-facing summary/index

## Routing Rules

1. Parse the user input.

2. Route to `/speckit.orca.pr-review` when any of the following are true:
   - `--comments-only` is present
   - `--post-merge` is present
   - the request is about GitHub PR comments, review threads, or external reviewer feedback

3. Otherwise route to `/speckit.orca.code-review`.

4. Be explicit that `/speckit.orca.review` is deprecated and that the selected
   command is the canonical path going forward.

## Output

Use this format:

```text
`/speckit.orca.review` is deprecated.

Routing to: `/speckit.orca.code-review` | `/speckit.orca.pr-review`
Reason: [brief reason]

To use the canonical command directly next time:
- `/speckit.orca.code-review ...`
- `/speckit.orca.pr-review ...`
```

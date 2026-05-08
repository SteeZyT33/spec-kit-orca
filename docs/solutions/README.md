# docs/solutions/

Durable artifacts capturing non-trivial bug fixes and design patterns so future
sessions (human or agent) can grep them before re-deriving the same thing.

Pattern adapted from EveryInc/compound-engineering-plugin's `ce-compound`. See
`docs/decisions/2026-05-07-lean-skill-bundle.md` for the rationale on why this
directory exists.

## When to add a file here

Add a `<date>-<slug>.md` file when **all** of the following are true:

1. The fix or pattern took more than ~20 minutes to understand or implement.
2. The information is not obvious from reading the resulting code.
3. A future session (or future-you) would benefit from finding it via grep.

If the substance fits in a commit message, leave it in the commit message. If
it's a single-decision rationale (we chose A over B), use `docs/decisions/`
instead. Solutions are for *how something works* and *why a non-obvious fix
was correct*; decisions are for *which option was chosen and why*.

## File format

```markdown
---
title: <short title>
date: <YYYY-MM-DD>
track: bug | knowledge
category: <e.g. worktrees, contract, hooks, cli, tui>
related:
  - path/to/source.py
  - docs/superpowers/specs/...
---

## Symptom (bug track) or Pattern (knowledge track)

What was visible. Concrete. Include the error message verbatim if there
was one.

## Root cause

What was actually happening underneath. Aim for "minimum information
needed to recognize this class of problem next time."

## Fix or pattern

The change. Reference the commit SHA or PR number. Code snippet only if
the diff is non-obvious.

## Why this is correct

The invariant the fix preserves, or the property the pattern exploits.
This is the part future-you will care about most.

## Anti-patterns rejected

If you considered a different fix and chose this one for a non-obvious
reason, capture the rejected option here. Skip this section if there
was only one viable approach.
```

Keep entries under ~300 lines. If you need more, you're writing a spec or a
decision doc, not a solution.

## Finding solutions

```bash
# By category
ls docs/solutions/ | grep -i contract

# By keyword across content
grep -rli "atomic rename" docs/solutions/

# By related file
grep -l "src/orca/core/worktrees/auto_symlink.py" docs/solutions/*.md
```

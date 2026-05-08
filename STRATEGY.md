# Orca — Strategy

> Upstream anchor read by skills and humans. Concise on purpose. If something
> takes more than two paragraphs to explain here, it belongs in `docs/`.

## What this repo is

Orca is a personal AI-augmented engineering toolkit. The headline value is the
**worktree manager + cross-tool contract layer + cmux integration + live TUI**.
Drop a `.worktree-contract.json` in any repo and `orca-cli wt new <branch>` (or
`cmux new`) produces an isolated, properly-symlinked workspace with optional
agent launch. The TUI keeps lanes, event feed, and review state visible across
sessions.

## Who it is for

1. **Me, first.** Solo developer running multiple Claude Code / Codex / cmux
   sessions across worktrees. Every feature decision answers "does this make
   *my* day better?" before "would others want this?"
2. **Other solo or small-team users**, only when a feature has already proven
   itself in (1) and the marginal cost of generalizing is small.

## What is in scope

- Worktree lifecycle (create / list / switch / merge / remove)
- `.worktree-contract.json` cross-tool contract (orca + cmux + bare git)
- Cmux compatibility shim and `from-cmux` import
- Hook lifecycle (after_create / before_run / before_remove) with TOFU trust
- Per-host adoption manifest and host-system detection (spec-kit, superpowers,
  openspec, bare)
- TUI (Textual): lane list, event feed, review-artifact pane
- Diagnostics (`orca-cli wt doctor`, `speckit.orca.doctor`)
- `worktree-overlap-check` capability (catches conflicts between concurrent
  lanes touching the same files)

## What is out of scope as of v3.0.0

- The SDD review pipeline (`review-spec` / `review-code` / `review-pr`).
  Deprecated 2026-05-07 — see `docs/decisions/2026-05-07-lean-skill-bundle.md`.
  Capability code is preserved under `src/orca/capabilities/` and remains
  callable from `orca-cli` for anyone who explicitly opts in. The user-facing
  slash command surface no longer ships them.
- Cross-team review orchestration. Not the target audience.
- Citation validation, completion gates, contradiction detection, flow-state
  projection — niche, deprecated unless they prove themselves on a real solo
  workflow.

## Operating principles

- **Worktree-first.** Every feature lands in an isolated worktree; main is
  reserved for merged work.
- **Plan-then-execute via superpowers.** Brainstorm → writing-plans →
  subagent-driven-development → finishing-a-development-branch is the default
  loop.
- **Durable artifacts.** Decisions go in `docs/decisions/<date>-<slug>.md`,
  non-trivial bug fixes / patterns go in `docs/solutions/<date>-<slug>.md`,
  specs in `docs/superpowers/specs/`, plans in `docs/superpowers/plans/`,
  reviews in `docs/superpowers/reviews/`.
- **Reversibility over destruction.** When pruning surface area (e.g. the
  v3.0.0 skill demote), move to `deprecated/`, do not delete. Re-enable cost
  should be one PR and zero archaeology.

## Non-goals

- Replacing cmux. Cmux's interactive shell function and `cmux init` are its
  differentiators; the contract layer just standardizes the shared subset.
- Becoming a generic agent framework. Orca is opinionated about
  worktree-isolated multi-session work plus a TUI; if a feature works equally
  well outside this shape, it belongs upstream (superpowers, mattpocock,
  compound-engineering) instead of in orca.

## Where to read further

- `README.md` — install / quickstart
- `docs/superpowers/specs/2026-04-30-orca-worktree-manager-design.md` — Phase 1 design
- `docs/superpowers/specs/2026-05-01-orca-worktree-contract-design.md` — Phase 2 design
- `docs/decisions/` — single-decision rationales
- `docs/solutions/` — bug-fix and pattern artifacts (compound knowledge)

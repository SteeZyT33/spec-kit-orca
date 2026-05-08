# Lean skill bundle: deprecate the SDD review pipeline

**Status:** Decided 2026-05-07. Implemented in `chore/lean-skill-bundle`.

## Context

Orca shipped 8 user-facing slash commands (orca-brainstorm, -cite, -doctor, -gate, -review-spec, -review-code, -review-pr, -tui) backed by 6 capability modules (citation_validator, completion_gate, contradiction_detector, cross_agent_review, flow_state_projection, worktree_overlap_check). The SDD review pipeline (review-spec → review-code → review-pr) was the headline value proposition: cross-agent reviews catching what single-agent misses, plus capability gates blocking bad merges.

The framing was "build cross-agent SDD tooling for multi-developer teams." In practice, this repo is a personal toolkit. The owner is solo, single-Claude-session most of the time, and the cross-agent review pipeline has been invoked roughly zero times during recent feature work (worktree manager Phase 1+2, contract layer). Meanwhile the underlying infrastructure — worktree manager, contract layer, TUI, cmux integration — is genuinely useful and has no equivalent in the broader Claude Code skill ecosystem.

Two adjacent ecosystems were evaluated:
- **mattpocock/skills:** anti-framework, lightweight, CONTEXT.md/ADR glossary loop. Solo-dev fit is high.
- **EveryInc/compound-engineering-plugin:** maximalist team-style, named-engineer reviewer personas, knowledge-compounding `docs/solutions/`, STRATEGY.md as upstream anchor. 37 skills + 48 agents. Built for an editorial team.

Orca's SDD review pipeline lands closer to the CE plugin in spirit (gated, multi-agent, artifact-driven), and competes with it on a context (team) the owner does not actually operate in.

## Decision

Demote the SDD review pipeline and quality-gate skills to a `deprecated/` directory. Keep the worktree manager, contract layer, TUI, cmux integration, and `worktree-overlap-check` capability — these are the parts that pay for themselves. Bump extension to v3.0.0.

**Active commands (2):**
- `speckit.orca.tui` — live awareness pane (worktree lanes, event feed, review queue if present)
- `speckit.orca.doctor` — install diagnostics

**Deprecated commands (6) — kept for opt-in via explicit invocation:**
- `speckit.orca.brainstorm` → use `superpowers:brainstorming`
- `speckit.orca.review-spec` → defer to spec-design dialogue + manual review
- `speckit.orca.review-code` → use `superpowers:requesting-code-review` + CodeRabbit
- `speckit.orca.review-pr` → manual GitHub PR review
- `speckit.orca.gate` → CI status checks
- `speckit.orca.cite` → niche, kept opt-in for synthesis content

**Capability source code (`src/orca/capabilities/*.py`) is not removed.** The 5 deprecated capabilities remain runnable from `orca-cli` for anyone who reaches for them explicitly. Only the user-facing slash command surface is pruned. This keeps the door open to re-enable any single capability without code archaeology.

**Auto-trigger hooks removed:** `after_implement → review-code` and `after_review → review-pr` no longer auto-prompt. The `before_pr → coderabbit-review` hook is also dropped — invoke CodeRabbit explicitly when wanted.

## What replaces the deprecated layer (for solo work)

| Was | Is now |
|-----|--------|
| orca-brainstorm | `superpowers:brainstorming` (already used in practice) |
| orca-review-spec | spec-design dialogue + spec self-review per writing-plans skill |
| orca-review-code | `superpowers:requesting-code-review` + CodeRabbit on the PR |
| orca-review-pr | GitHub PR comment review + ad-hoc retro notes |
| orca-gate | CI status checks via `gh pr view --json statusCheckRollup` |
| orca-cite | not replaced; deprecated unless synthesis content publishing returns |

## Patterns adopted from external plugins

From the same evaluation, two patterns are imported:

1. **`STRATEGY.md` at repo root** (CE pattern). Single upstream anchor for "what is this repo trying to do, who is it for, what's in/out of scope." Downstream skills (and the human author) read it for grounding.
2. **`docs/solutions/` directory** (CE `ce-compound` pattern). Durable artifacts capturing non-trivial bug fixes and design decisions, with YAML frontmatter so future agents can grep them. Today's commit seeds the directory with a README explaining the convention; the existing decision doc + Phase 2 review can be migrated in over time.

`mattpocock/skills` `CONTEXT.md` + grilling-interview pattern is left for a future PR; the value is real but the integration design (where does CONTEXT.md live, what writes to it, how does it interact with `STRATEGY.md`) needs more thought than this scope-prune deserves.

## Reversibility

All deprecated content stays in git, just under `deprecated/` paths. To reinstate any single command: copy back to `plugins/claude-code/commands/<name>.md` and re-add to the active `commands:` block in `extension.yml`. To reinstate the auto-trigger hooks: copy the prior `hooks:` block from this commit's parent.

The 5 deprecated capability Python modules are unchanged and remain importable. Tests for them remain in `tests/capabilities/` and pass.

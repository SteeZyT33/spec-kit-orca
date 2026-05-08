# Orca - Claude Code Plugin

This plugin registers orca's worktree-management and TUI slash commands inside
a Claude Code host.

> **v3.0.0 (2026-05-07):** the SDD review pipeline (`review-spec`,
> `review-code`, `review-pr`) and the `cite` / `gate` / `brainstorm` commands
> are deprecated. They live under `commands/deprecated/` and remain opt-in
> for anyone who wants to wire them back up. Rationale:
> `docs/decisions/2026-05-07-lean-skill-bundle.md`.

## What gets installed

When the orca extension is added to a spec-kit repo (via `specify extension add`
or the direct-copy installer at `/tmp/install-phase3-orca.sh`), four things
land in the host:

- **2 SKILL.md wrappers** at `.claude/skills/orca-{tui,doctor}/SKILL.md`. These
  make the active slash commands user-invocable.
- **`extension.yml` registration** at `.specify/extensions/orca/extension.yml`,
  listing the 2 active commands plus 6 deprecated commands under
  `deprecated_commands:`.
- **Source command files** at
  `.specify/extensions/orca/plugins/claude-code/commands/{tui,doctor}.md`. The
  6 deprecated source files live under `commands/deprecated/`.
- **Helper scripts** at `.specify/extensions/orca/scripts/bash/`.

## Active slash commands

| Command | Purpose |
| --- | --- |
| `/orca:tui` | Live awareness pane: worktree lanes, event feed, review queue if present. |
| `/orca:doctor` | Health check: orca-cli, worktree config, SKILL.md, reviewer backends. Exit 0 if healthy. |

## Deprecated slash commands (opt-in)

Source files under `commands/deprecated/`. To re-enable any single command:
copy back to `commands/<name>.md` and re-add to the `commands:` block in
`extension.yml`.

| Command | Replacement |
| --- | --- |
| `/orca:brainstorm` | `superpowers:brainstorming` skill |
| `/orca:review-spec` | spec-design dialogue + the spec self-review step in `superpowers:writing-plans` |
| `/orca:review-code` | `superpowers:requesting-code-review` + CodeRabbit on the PR |
| `/orca:review-pr` | GitHub PR comment review + ad-hoc retro |
| `/orca:gate` | CI status checks (`gh pr view --json statusCheckRollup`) |
| `/orca:cite` | niche; deprecated unless publishing synthesis content |

The 5 underlying capability modules
(`citation_validator`, `completion_gate`, `contradiction_detector`,
`cross_agent_review`, `flow_state_projection`) remain in
`src/orca/capabilities/` and are still callable from `orca-cli` directly.
Only the user-facing slash command surface is pruned.

## Resolving orca-cli

The slash commands shell out to `orca-cli`. There are three install paths; the
Prerequisites block in each command file walks the resolution chain in order:

1. **`uv tool install /path/to/spec-kit-orca`** - puts `orca-cli` on PATH. Recommended for daily-driver setups.
2. **`export ORCA_PROJECT=/path/to/spec-kit-orca`** - commands resolve via `uv run --project "$ORCA_PROJECT" orca-cli`.
3. **`~/spec-kit-orca` fallback** - automatic when the source tree is cloned at that path. No env var needed.

If none of the three resolve, the command file prints a one-line error and exits.

## Re-syncing skills after edits

If you edit a source command file at
`.specify/extensions/orca/plugins/claude-code/commands/*.md`, the corresponding
SKILL.md does not auto-regenerate. Re-sync with:

```bash
bash .specify/extensions/orca/scripts/bash/sync-skills.sh
```

## Health check

```bash
/orca:doctor
```

Or directly:

```bash
bash .specify/extensions/orca/scripts/bash/orca-doctor.sh
```

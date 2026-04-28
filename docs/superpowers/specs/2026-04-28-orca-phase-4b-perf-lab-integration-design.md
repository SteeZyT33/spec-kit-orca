# Orca Phase 4b: Perf-Lab Integration (Spec Contribution)

**Date:** 2026-04-28
**Status:** Design (post-brainstorm, pre-implementation-plan)
**Predecessors:**
- `docs/superpowers/specs/2026-04-26-orca-toolchest-v1-design.md` (v1 north star)
- `docs/superpowers/specs/2026-04-28-orca-phase-4a-in-session-reviewer-design.md` (Phase 4a, just landed)

## Deliverable

Phase 4b ships a **spec contribution PR** to the perf-lab repo (not running code in the orca repo). The PR adds:

- New file: `perf-lab/specs/010-self-organizing-research-runtime/orca-integration.md` (the integration spec)
- One-paragraph addition to `perf-lab/specs/010-self-organizing-research-runtime/spec.md` "Future Integration Notes" section
- Implementation tasks block in `perf-lab/specs/010-self-organizing-research-runtime/tasks.md`, blocked on T000i (perf-event skill foundation)

Phase 4b deliberately does NOT ship running code. perf-lab v6 is mid-build (T000a-T000j unfinished); orca skill code waits for the perf-lab v6 skill foundation to land. This phase is the design that wires into v6 when ready.

## Context

The v1 north star originally proposed Phase 4 as a perf-lab integration shim living in the orca repo at `orca/integrations/perf_lab/`. After Phase 4a's "orca = JSON-in JSON-out library" framing, that location is wrong: perf-lab-specific event translation should live in the perf-lab repo so orca stays opaque. Phase 4b reflects that revised architecture.

The integration is **opt-in**: perf-lab v1 must continue to operate without orca. orca skills are tools agents may invoke; orca-driven enforcement at perf-synthesis or perf-lease boundaries is gated on per-claim config.

Phase 4a unblocks Phase 4b by removing the `ANTHROPIC_API_KEY` dependency. Inside perf-lab's devcontainer, claude/codex hosts can dispatch their own subagent reviewers, write findings to a file, and call `cross-agent-review --claude-findings-file ...`. No API key required.

## Architecture

Three new perf-lab skills wrap orca capabilities:

- **`perf-cite`** wraps `orca-cli citation-validator`
- **`perf-contradict`** wraps `orca-cli contradiction-detector` (with subagent dispatch for the LLM portion)
- **`perf-review`** wraps `orca-cli cross-agent-review` (with subagent dispatch)

Each follows perf-lab's existing skill conventions (per `perf-lab/specs/010-.../contracts/skills.md`):
- Lives at `/opt/perf-lab/skills/<name>/entry.sh`, called by absolute path inside the devcontainer
- Has `SKILL.md` with agentskills.io frontmatter
- Reads `CLAIM_ID` and `SHARED_ROOT` from env
- Emits events via `perf-event`
- Uses `flock` for shared-state writes
- Exit 0 on success, non-zero on failure

Two opt-in enforcement points (defaults OFF):
- `perf-synthesis` commit flow can call `perf-cite` and `perf-contradict` as gates if claim config sets `orca_policy.synthesis_validators`
- `perf-lease` grant flow can call `orca-cli worktree-overlap-check` if claim config sets `orca_policy.lease_overlap_check: "orca"`

## Skill Contracts

### `perf-cite`

```
perf-cite --content-path <path> [--reference-set <path>]... [--mode strict|lenient]
```

Wraps `orca-cli citation-validator`. Validates citation hygiene in synthesis text.

- Required: `--content-path` (markdown file inside `/shared/` to validate)
- Optional: `--reference-set` (repeatable; defaults auto-discover from claim's feature dir per Phase 3.2 backlog item 2 - `plan.md`, `data-model.md`, `research.md`, `quickstart.md`, `tasks.md`, `contracts/**/*.md`)
- Optional: `--mode strict|lenient` (default `strict`)

Behavior:
1. Resolve reference set
2. Shell to `orca-cli citation-validator --content-path ... --reference-set ... --mode ...`
3. Parse JSON envelope; on `Err(...)`, emit failure event and exit 1
4. Compute coverage; compare against operator-configured threshold (default 1.0)
5. Emit `synthesis_validated` event with payload `{capability: "citation-validator", version, duration_ms, coverage, uncited_count, broken_refs_count, threshold}`
6. Exit 0 if coverage >= threshold; exit 1 with stderr listing uncited claims and broken refs otherwise

Concurrency: `flock /shared/locks/cite.lock` only when writing reports (not for the validator call itself).

### `perf-contradict`

```
perf-contradict --content-path <path> --evidence-path <path>
```

Wraps `orca-cli contradiction-detector`. Validates new synthesis content against prior evidence to flag contradictions. Uses subagent dispatch (Phase 4a pattern) since contradiction-detector is LLM-backed.

- Required: `--content-path` (the new synthesis content to check)
- Required: `--evidence-path` (the prior evidence file or directory; `events.jsonl`, `experiments.tsv`, prior `synthesis/current.md`)

Behavior:
1. Build review prompt: `ORCA_PROMPT=$(orca-cli build-review-prompt --kind contradiction --criteria contradicts-evidence --criteria contradicts-prior-synthesis)` (note: `--kind contradiction` is reserved; v1 of build-review-prompt accepts any `--kind` without branching, so this works without orca changes)
2. Dispatch a `Code Reviewer` subagent via the host's Agent tool (Claude Code or Codex). The host inside perf-lab's devcontainer is whichever harness is running (env `HARNESS`).
3. Subagent input: `$ORCA_PROMPT` + content of `--content-path` + content of `--evidence-path`
4. Capture subagent response; pipe through `orca-cli parse-subagent-response` to write findings to `/shared/orca/<claim-id>/contradict-findings.json`
5. Call `orca-cli contradiction-detector --claude-findings-file <path> --content-path <path> --evidence-path <path>`
6. Parse JSON envelope; emit `contradiction_detected` event with payload `{capability: "contradiction-detector", version, duration_ms, contradiction_count, contradictions: [...]}`
7. Exit 0 if zero contradictions; exit 1 if any found (caller decides whether to escalate to a feedback_needed)

Note: this assumes `contradiction-detector --claude-findings-file` is supported. Phase 4a wired the flag for `cross-agent-review`; for Phase 4b's spec to work end-to-end, the same flag must be added to `contradiction-detector`. Tracked as a perf-lab orca-integration task: "verify orca-cli contradiction-detector supports --claude-findings-file; file orca PR if not."

Concurrency: `flock /shared/locks/contradict.lock` for shared writes.

### `perf-review`

```
perf-review --kind {spec,diff,pr,artifact} --target <path> [--criteria <c>]... [--feature-id <id>]
```

Wraps `orca-cli cross-agent-review` with subagent dispatch. Runs cross-agent review against an artifact (typically a research paper draft, theory document, or implementation diff).

- Required: `--kind` (one of: spec, diff, pr, artifact)
- Required: `--target` (path to subject inside `/shared/`)
- Optional: `--criteria` (repeatable)
- Optional: `--feature-id` (defaults to claim's feature ID)

Behavior:
1. Build review prompt via `orca-cli build-review-prompt`
2. Dispatch subagent reviewer (Phase 4a pattern)
3. Pipe response through `parse-subagent-response`; write to `/shared/orca/<claim-id>/review-findings.json`
4. Call `orca-cli cross-agent-review --claude-findings-file <path> --kind ... --target ... [--criteria ...]`
5. Parse envelope; emit `quality_gate` event with payload `{capability: "cross-agent-review", version, duration_ms, kind, finding_count, severity_breakdown: {blocker: N, high: N, medium: N, low: N, nit: N}}`
6. Exit 0 always (review is informational; agent reads findings and decides on next action)

Concurrency: `flock /shared/locks/review.lock` for shared writes.

## New Event Types

Three new event types added to `perf-event`'s FR-008 canonical list:

| Type | Payload fields | Notes |
|------|---------------|-------|
| `synthesis_validated` | `capability`, `version`, `duration_ms`, `coverage`, `uncited_count`, `broken_refs_count`, `threshold` | Emitted by `perf-cite`. Optional emit by `perf-synthesis` when `orca_policy.synthesis_validators` includes "cite". |
| `contradiction_detected` | `capability`, `version`, `duration_ms`, `contradiction_count`, `contradictions[]` | Emitted by `perf-contradict`. Optional emit by `perf-synthesis` when `orca_policy.synthesis_validators` includes "contradict". |
| `quality_gate` | `capability`, `version`, `duration_ms`, `kind`, `finding_count`, `severity_breakdown` | Emitted by `perf-review`. Always informational (perf-review exits 0 regardless). |

Each event also carries the standard perf-event fields (`event_id`, `timestamp`, `harness`, `image_digest`, `claim_id`).

## Claim Config Additions

Per-claim config gains an optional `orca_policy` block:

```json
{
  "claim_id": "abc123",
  "mode": "implement",
  "orca_policy": {
    "synthesis_validators": ["cite", "contradict"],
    "lease_overlap_check": "orca",
    "review_required_kind": "diff",
    "cite_threshold": 1.0,
    "cite_reference_set": ["plan.md", "research.md"]
  }
}
```

Field semantics (all optional, defaults null/disabled):

- `synthesis_validators`: list of `["cite", "contradict"]` subset. If non-empty, `perf-synthesis` invokes the named validators after building the synthesis content but BEFORE committing the lease. Validator failure -> synthesis commit aborts; agent gets a `feedback_needed` event.
- `lease_overlap_check`: if set to `"orca"`, `perf-lease` calls `orca-cli worktree-overlap-check` before granting any lease whose paths overlap an active lease. orca's pure-Python check is more thorough than perf-lease's built-in overlap detection.
- `review_required_kind`: if set, perf-synthesis or perf-artifact commit flows require a successful `perf-review` event for this claim before allowing commit.
- `cite_threshold`: float in [0.0, 1.0]; default 1.0. `perf-cite` exits non-zero if coverage falls below.
- `cite_reference_set`: list of relative paths from claim's feature dir; if unset, `perf-cite` auto-discovers per Phase 3.2 item 2 conventions.

Defaults: all unset. orca is invisible to vanilla claims. perf-lab v1 operates without orca exactly as it does without Phase 4b shipped.

## Devcontainer Installation

`perf-lab/.devcontainer/Dockerfile` (currently spec'd in T000b) needs orca-cli available at runtime. Recommended addition to the Dockerfile:

```dockerfile
# orca capability library (Phase 4b integration; opt-in via claim_config.orca_policy)
RUN pip install --no-cache-dir uv && \
    uv tool install spec-kit-orca==<version-pin>
```

Where `<version-pin>` is the orca git tag at perf-lab v6 release time (e.g., `0.4.0`). Pinning forces explicit Dockerfile bumps for orca upgrades.

Alternative for development: `ENV ORCA_PROJECT=/opt/orca` plus a bind mount of the orca source tree. This lets perf-lab developers iterate on orca without rebuilding the image. Document both paths in T000b.

## Failure Modes

| Scenario | Skill behavior |
|----------|----------------|
| orca-cli not in PATH and `ORCA_PROJECT` unset | Skill exits 2 with stderr `"orca-cli not found; check Dockerfile install or set ORCA_PROJECT"` |
| orca capability returns `Err(INPUT_INVALID)` | Skill emits its event with `payload.error = {kind, message}`; exits 1 |
| orca capability returns `Err(BACKEND_FAILURE)` | Skill emits its event with `payload.error`; exits 1 with stderr surfaced from orca |
| Subagent dispatch unavailable (host lacks Agent tool, e.g., pi.sh) | `parse-subagent-response` returns INPUT_INVALID; skill exits 1 with `"in-session reviewer unavailable on this host"` |
| `--content-path` outside `/shared/` | Skill exits 1 (security: prevent reading outside the runtime sandbox) |
| Skill invoked outside an active claim (`CLAIM_ID` unset) | Skill exits 1 with `"missing CLAIM_ID; orca skills run only inside a claim"` |
| orca version below perf-lab's required minimum | Skill exits 2 with `"orca-cli version X.Y.Z below required A.B.C; bump devcontainer image"` (requires orca-cli to support `--version`) |

## Test Plan (perf-lab side)

Following perf-lab spec 010's test conventions:

- **Skill smoke tests**: `tests/skills/test_perf_cite.bats`, `test_perf_contradict.bats`, `test_perf_review.bats`. Use Bats. Exercise happy path + each failure mode against fixture content. Stub `orca-cli` with a fake script returning canned envelopes.
- **Event schema validation**: extend `tests/events/test_event_schema.py` to validate the three new event types' payload shapes against the JSON schema.
- **Integration tests**: `tests/integration/test_orca_synthesis_gate.bats` (synthesis_validators policy), `test_orca_lease_overlap.bats` (lease_overlap_check policy). Mark as integration tests; require orca-cli installed in test environment.
- **Claim config validator**: existing perf-lab claim-config validator (T000? - check perf-lab tasks) extended to recognize the `orca_policy` block.

## Implementation Tasks (added to perf-lab tasks.md)

Block T0Z (orca integration), all blocked on T000i (skill foundation):

- T0Z01: Author `perf-lab/specs/010-.../orca-integration.md` (the spec contribution itself)
- T0Z02: Add `synthesis_validated`, `contradiction_detected`, `quality_gate` to FR-008 canonical event list in spec.md
- T0Z03: Implement `perf-cite` skill (entry.sh + SKILL.md + Bats tests)
- T0Z04: Implement `perf-contradict` skill (entry.sh + SKILL.md + Bats tests + subagent dispatch wiring)
- T0Z05: Implement `perf-review` skill (entry.sh + SKILL.md + Bats tests + subagent dispatch wiring)
- T0Z06: Extend claim config schema for `orca_policy` block (validator + tests)
- T0Z07: Wire `synthesis_validators` policy into `perf-synthesis` commit flow
- T0Z08: Wire `lease_overlap_check` policy into `perf-lease` grant flow
- T0Z09: Wire `review_required_kind` policy into commit flows
- T0Z10: Add orca-cli install line to `.devcontainer/Dockerfile` (T000b)
- T0Z11: Document orca-policy operator guide in `docs/runtime/orca-policy.md`

Each task gets perf-lab's standard task shape (description, files, acceptance criteria).

## Cross-Repo Considerations

Phase 4b lands in perf-lab repo. orca repo unchanged. But two cross-repo dependencies surface:

1. **`contradiction-detector --claude-findings-file`**: Phase 4a wired this flag for `cross-agent-review`. The contradiction-detector capability needs the same flag for Phase 4b to work. If not yet supported, file an orca PR before perf-lab v6 reaches T0Z04 (or update Phase 4b spec to use SDK-only contradiction-detector and document API key requirement for that one capability).

2. **orca-cli version contract**: perf-lab's Dockerfile pins a specific orca version. orca's release process should produce stable tags (semver). Phase 4b spec recommends but doesn't enforce semver; tracked as orca repo follow-up.

## Out of Scope (Phase 4b)

- Implementing the perf-lab skills (waits on T000i - perf-event foundation)
- New orca capabilities (use existing 6)
- flow-state-projection integration (perf-lab has its own scheduler; orca's projection is for SDD)
- completion-gate integration (SDD-specific stage gates don't apply to perf-lab's claim/round model)
- Automatic enforcement (per user decision: opt-in via claim config only; no global default-on)
- Cross-repo CI ensuring perf-lab and orca versions stay compatible (manual today; could add later)
- Operator UX for migrating existing perf-lab v5 runs to use orca skills (no migration; v6 is a fresh runtime)

## Resolved Design Decisions

- **Integration lives in perf-lab repo**, not orca repo (deviation from v1 north-star). Phase 4a's "orca = opaque library" framing made this the right call.
- **Three new agent-visible skills** (`perf-cite`, `perf-contradict`, `perf-review`) plus two opt-in enforcement points (synthesis validators, lease overlap check). Default behavior: orca invisible.
- **Spec deliverable only** for Phase 4b. perf-lab v6 implementation tasks block on T000i (skill foundation). Closing Phase 4b ships the design contract; running code lands when v6 ships.
- **Sibling file**, not invasive spec.md edit. `orca-integration.md` lives next to the existing `data-model.md`, `runtime-mechanics.md`, etc., in perf-lab spec 010 dir.
- **Claim-scoped opt-in**, not global config. Each claim decides whether orca runs in its synthesis/lease path. Mission defaults can set claim-config templates but every individual claim must carry its own `orca_policy` block (or none).
- **Subagent dispatch reused** from Phase 4a. `perf-contradict` and `perf-review` use the same build-review-prompt -> subagent -> parse-subagent-response -> file-flag chain that the Phase 3 slash commands use. No new orca-cli surface needed.

## Honest Scope Estimate

Phase 4b spec contribution PR: **half-day to one day** of focused work. The artifact is one ~400-line markdown file plus tasks-list additions and a one-paragraph spec.md update. No code, no tests, no smoke runs. The challenge is precision (skill contracts, event payload shapes, claim config schema) not volume.

The downstream perf-lab v6 implementation of the orca skills (T0Z03-T0Z11) is a separate project, blocks on perf-lab's T000i, and is out of scope for Phase 4b.

## Honest Value Statement

What Phase 4b uniquely delivers:

1. **Locks the integration contract** before perf-lab v6 builds its skill foundation. When T000i lands, T0Z work has a clear target.
2. **Forces clarity on opt-in semantics.** "perf-lab v1 must work without orca" is now a documented constraint at the spec level, not just a hope.
3. **Reuses Phase 4a's subagent dispatch** rather than inventing perf-lab-specific reviewer plumbing. The "host harness dispatches a subagent, file-backed reviewer reads the result" pattern works inside perf-lab's devcontainer the same way it works in Claude Code slash commands.

What Phase 4b does NOT deliver:

- Running orca-aware perf-lab. That's perf-lab v6 + T0Z block.
- New orca capabilities. The spec uses the existing 6.
- A hard guarantee that the integration contract is right. perf-lab v6 implementation may surface gaps; spec is a living document that may need a 4b-followup.

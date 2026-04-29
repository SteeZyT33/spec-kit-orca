# Review-Spec: Orca Phase 4b (Perf-Lab Integration Spec Contribution)

**Spec under review:** `docs/superpowers/specs/2026-04-28-orca-phase-4b-perf-lab-integration-design.md` (commit `bb78733`)
**Date:** 2026-04-28
**Reviewers:** Code Reviewer subagent (claude, 16 findings) + codex via legacy crossreview.sh (6 blocking + 5 non-blocking)
**Verdict:** **NEEDS-REVISION** (substantial)

---

## Round 1 - Cross-Pass

### Convergent blockers (both reviewers found these)

**B1. Event payload schemas conflict with existing perf-lab spec.md lines 436-438.**
The existing perf-lab Future Integration Notes already define payloads for the same three event types: `synthesis_validated -> {uncited_spans, broken_refs, citation_coverage}`, `contradiction_detected -> {contradictions[]}`, `quality_gate -> {gate_result_ref, blockers, target_stage}`. Phase 4b proposes incompatible shapes (`uncited_count`, `coverage`, `severity_breakdown`, etc.) and silently reassigns `quality_gate` semantics from completion-gate to cross-agent-review. The "one-paragraph addition" framing hides the conflict; the existing 25-line block must be rewritten or aligned, not appended to.

**B2. Subagent dispatch from a bash `entry.sh` is architecturally impossible.**
Phase 4a was explicit: subagent dispatch is the host LLM's responsibility, NOT something `orca-cli` or any non-LLM process can do. Phase 4b's perf-contradict and perf-review skills are bash scripts running under flock inside a devcontainer; they cannot call Claude Code's Agent tool. The skill convention (`/opt/perf-lab/skills/<name>/entry.sh`, one-shot, exit 0/1) cannot host subagent dispatch. Phase 4b silently breaks Phase 4a's framing.

**B3. `lease_overlap_check` wired into the wrong layer.**
perf-lab's `perf-lease` worker skill only exposes `check`/`info` operations. Lease *grants* are scheduler/host-side (`scripts/runtime-v6/lease.sh` per perf-lab T017-T018). Phase 4b directs operators to integrate `worktree-overlap-check` into a non-existent in-container grant flow.

**B4. `contradiction-detector --claude-findings-file` is unverified and load-bearing.**
Phase 4b admits the flag may not exist; if it doesn't, perf-contradict cannot be implemented at all, voiding T0Z04. The "verify and file orca PR if needed" framing makes this a Phase 4b merge blocker, not a follow-up.

**B5. Existing perf-lab spec.md contradicts Phase 4b's shim location.**
spec.md lines 442-444 explicitly say "the integration shim lives in the orca repo under integrations/perf_lab/." Phase 4b says the opposite without acknowledging the contradiction. The deliverable's "one-paragraph addition" doesn't fix the existing text.

### Codex-only blockers

**B6. orca-cli compatibility contract underspecified.**
Version-pin alone doesn't give implementers a contract for Phase 5/6 envelope changes. Need: minimum required capabilities/flags, expected envelope version, startup feature probe, fixture test matrix.

**B7. No timeout policy.**
v1 north-star line 449 mandates "Failed orca calls MUST NOT block perf-lab rounds indefinitely... default fallback is to emit feedback_needed rather than hang." Phase 4b is silent on timeouts and feedback_needed. A hanging subagent in synthesis_validators would hold synthesis.lock indefinitely.

### Claude-only highs

**H1. Model-tier policy from spec.md line 450 unaddressed.**
"Cheap tier worker invoking cross-agent-review MUST NOT escalate to a strong reviewer without explicit policy allowance." Phase 4b's perf-review has no model-tier inheritance.

**H2. feedback_needed fallback + synthesis-lock deadlock.**
Per spec.md line 449. Phase 4b doesn't release synthesis.lock on validator failure or emit feedback_needed; LLM-backed validators run while synthesis.lock is held, risking minutes-long lock-holds.

**H3. Event-type-before-emission ordering not enforced.**
perf-event rejects unknown types with exit 3. T0Z02 (FR-008 amendment) must be a hard prerequisite for skill-emission tasks T0Z03/04/05; Phase 4b doesn't declare this dependency.

**H4. Path validation gaps.**
`--evidence-path`, `--reference-set`, `--target` lack symlink rejection and resolved-path checks. `--evidence-path` allows directories (potential traversal). Phase 4a established defense-in-depth; Phase 4b regresses.

**H5. Two unverified upstream orca-cli capabilities are load-bearing.**
contradiction-detector --claude-findings-file (B4 above), orca-cli --version, and build-review-prompt accepting `--kind contradiction`. All three should be verified before opening the perf-lab PR.

### Convergent suggestions / mediums

- **opt-in default-off has no discovery path.** Without recommended profiles or template defaults, `orca_policy` will stay unset; perf-cite is largely aspirational.
- **Devcontainer install line uses `spec-kit-orca` package name** which may be wrong post-rename; not verified to publish to PyPI.
- **Test plan conflates spec-PR review with downstream implementation tests.** Bats smoke tests and runtime integration tests can't run against a code-less spec PR.
- **Capability/version metadata in payload conflicts with perf-event's `payload_version` convention** (data-model.md line 264-265). Naming collision.
- **`/shared/orca/<claim-id>/` path conventions undefined.** Who creates? Permissions? Cleanup? Race handling? Phase 4a uses timestamp suffixes; Phase 4b doesn't.
- **perf-cite's "compute coverage" duplicates orca-cli citation-validator's own output.** Should read from the envelope, not recompute.
- **perf-contradict on Codex hosts always fails.** Phase 4b acknowledges in failure-mode table but doesn't tell operators what to do (claim-config-level, fallback, or restrict to claude-code hosts).
- **`review_required_kind` underspecified.** Needs target_sha256, criteria_hash, reviewed_at, claim_id, kind to bind the event to content; otherwise stale events can satisfy gates.

---

## Recommended Path Forward

The spec is directionally right (perf-lab owns translation, orca stays opaque, opt-in defaults match perf-lab v1 compatibility), but it has too many architecturally-unsound details to ship as a perf-lab spec PR. Specifically:

1. **Rework subagent dispatch.** Restructure perf-contradict and perf-review so the LLM-backed step is host-side BEFORE skill invocation; the skill becomes pure orca-cli wrapping with `--claude-findings-file` passthrough. Mirror Phase 4a's slash-command pattern exactly.

2. **Move `lease_overlap_check` to host-side scheduler/lease.sh.** Worker `perf-lease` is read-only.

3. **Reconcile event payloads with spec.md 436-438.** Either align names or include a unified-diff replacement of the existing block.

4. **Verify or file orca PRs for the three load-bearing flags** (contradiction-detector --claude-findings-file, orca-cli --version, build-review-prompt --kind contradiction). Treat as merge prerequisites.

5. **Add timeout/feedback_needed/lease-release policy** per spec.md line 449.

6. **Add model-tier inheritance** per spec.md line 450.

7. **Split test plan** into "spec-PR review checks" (markdown lint, schema validation, no broken cross-refs) and "downstream T0Z implementation tests."

8. **Replace `quality_gate` reuse** with a new event type (e.g., `cross_review_summary`).

9. **Verify devcontainer install line** against actual orca PyPI publication state.

10. **Add path-validation rigor** to all path flags (symlinks rejected, resolved-path checks, directory-symlink rejection for `--evidence-path`).

This is a substantial v2 of the spec, not a polish pass.

---

## Verdict

**NEEDS-REVISION.** Recommend NOT proceeding to subagent-driven implementation until the spec is revised. Two paths:

- **A. Revise the spec inline now** addressing the 7 blockers + key highs. Then re-run /orca:review-spec. Estimated 1-2 sessions.
- **B. Defer Phase 4b.** Mark Phase 4 as fully closed with 4a as the substantive deliverable. Re-engage Phase 4b later, after perf-lab v6 ships skill foundation + lease.sh, with concrete answers to the model-tier / timeout / lease-release policy questions.

Phase 4a is shipped and unblocks the in-session reviewer use case. Phase 4b's value-add is integrating orca into perf-lab's runtime, but perf-lab v6 is mid-build (T000a-j unfinished) so the integration would land into a moving target. Option B may be the right call.

# Community Extension Audit

**Date**: 2026-04-05
**Purpose**: Evaluate every community extension for inclusion in our orchestration workflow.

## Decision Key

| Decision | Meaning |
|----------|---------|
| **COMPANION** | Auto-installed by bootstrap.sh — directly complements our commands |
| **ADOPT** | Worth installing manually — adds value we don't cover |
| **WATCH** | Interesting but not needed now — revisit when our workflow matures |
| **SKIP** | Overlaps with what we have, too opinionated, or not relevant |

## Full Audit

| Extension | Cmds | Decision | Reasoning |
|-----------|------|----------|-----------|
| **aide** | 7 | SKIP | Alternative 7-step workflow that replaces spec-kit's core flow. We use spec-kit's native specify→plan→tasks→implement. Adopting AIDE would mean running a parallel workflow. |
| **archive** | 1 | ADOPT | Archives merged features into project memory. We don't have this — after a feature ships and self-review runs, archiving the decisions/lessons would feed mneme. Lightweight, no overlap. |
| **azure-devops** | 1 | SKIP | We use GitHub, not Azure DevOps. Only relevant if project management moves to ADO. |
| **checkpoint** | 1 | WATCH | Commits mid-implementation to avoid giant single commits. Our review command already creates per-fix commits, and superb's TDD cycle commits at green. Marginal value on top of those. |
| **cleanup** | 1 | SKIP | Scout-rule quality gate: auto-fix small, task medium, analyze large. **Our review command already does this** with the same tiered model plus spec compliance and PR lifecycle. Direct overlap. |
| **conduct** | 1 | WATCH | Runs a single spec-kit phase via sub-agent to reduce context pollution. Interesting isolation pattern for large projects where context windows overflow. Not needed for our current scale. |
| **critique** | 1 | WATCH | Dual-lens review (product strategy + engineering risk) of spec and plan. Our crossreview covers adversarial review of artifacts, but critique's product-strategy lens is different. Could add value for product-heavy specs. |
| **docguard** | 6 | SKIP | CDD enforcement with scoring and traceability. Heavy (requires Node.js), opinionated about documentation structure. Our review + verify companions already validate spec compliance without adding a runtime dependency. |
| **doctor** | 1 | ADOPT | Diagnoses project health — structure, agents, features, scripts, extensions, git. Useful for debugging broken setups. No overlap with our commands. Quick sanity check. |
| **extensify** | 4 | SKIP | Creates and validates extensions. Only useful when building new extensions — we'd use it during development of this repo, not in project workflows. |
| **fix-findings** | 1 | SKIP | Automated analyze-fix-reanalyze loop. Our review already does tiered fixes and re-runs passes. Direct overlap. |
| **fixit** | 1 | ADOPT | Spec-aware bug fixing: maps bugs to spec artifacts, proposes minimal plan. Different from review (which is proactive) — fixit is reactive to reported bugs. Complementary. |
| **fleet** | 2 | SKIP | Full lifecycle orchestrator with human-in-the-loop gates. Overlaps with our assign + review + crossreview flow. Less flexible than composing our individual commands. |
| **iterate** | 2 | WATCH | Refine specs mid-implementation with a define-and-apply workflow. Our reconcile companion handles drift detection, but iterate's mid-flight spec refinement is a slightly different use case. Worth revisiting. |
| **jira** | 3 | SKIP | We use GitHub Issues (speckit.taskstoissues covers this). Only relevant if project management moves to Jira. |
| **learn** | 2 | SKIP | Generates educational guides from implementations. Not relevant to our workflow — we're building, not teaching. |
| **maqa** | 4 | WATCH | Full multi-agent orchestration (coordinator→feature→QA) with worktree isolation. More opinionated than our assign command. Worth studying the worktree isolation pattern, but adopting the whole framework would conflict with our lighter assign+review approach. |
| **maqa-azure-devops** | 2 | SKIP | MAQA companion for Azure DevOps. N/A without MAQA. |
| **maqa-ci** | 2 | SKIP | MAQA CI gate. N/A without MAQA. Our review Step 3 already does CI verification. |
| **maqa-github-projects** | 2 | SKIP | MAQA companion for GitHub Projects. N/A without MAQA. |
| **maqa-jira** | 2 | SKIP | MAQA companion for Jira. N/A without MAQA. |
| **maqa-linear** | 2 | SKIP | MAQA companion for Linear. N/A without MAQA. |
| **maqa-trello** | 2 | SKIP | MAQA companion for Trello. N/A without MAQA. |
| **onboard** | 7 | SKIP | Developer onboarding with gamification. Not relevant — we're the only operator. Would matter for a team. |
| **plan-review-gate** | 1 | WATCH | Requires spec+plan to be merged via PR before task generation. Good governance pattern. cc-spex's traits already handle stage gating. Redundant if using cc-spex, useful if not. |
| **presetify** | 4 | SKIP | Creates and validates presets. Only useful when building presets, not in project workflows. |
| **product-forge** | 10 | SKIP | Full product lifecycle from research to test. Alternative workflow that replaces spec-kit's core flow, similar to AIDE. Too opinionated — we compose our own pipeline. |
| **qa** | 1 | WATCH | Browser-driven or CLI-based QA validation of acceptance criteria. Interesting for web projects — validates specs against running UI. Not needed for backend/CLI work but worth adding for web features. |
| **ralph** | 2 | SKIP | Autonomous implementation loop using Copilot CLI. We use Claude/Codex, not Copilot CLI. Different toolchain. |
| **reconcile** | 1 | COMPANION | Detects and repairs spec-implementation drift. Directly feeds our review/crossreview findings. Already in bootstrap.sh. |
| **repoindex** | 3 | ADOPT | Generates repo overview, architecture, and module index. Useful for large codebases where agents need orientation. No overlap — pure information tool. |
| **retro** | 1 | SKIP | Sprint retrospective with metrics. **Our self-review command covers this** with the added ability to auto-improve extension commands. Direct overlap, ours is better. |
| **retrospective** | 1 | SKIP | Post-implementation retrospective with spec adherence scoring. Same as retro — **our self-review subsumes this** with the self-improvement loop. |
| **review** (community) | 7 | SKIP | 6 specialized review agents + coordinator. **Our review command is significantly more capable** — spec compliance, tiered fixes, PR lifecycle, comment management, merge conflict protocol. The community version is code-quality only with no spec awareness. |
| **ship** | 1 | ADOPT | Automates release pipeline: pre-flight checks, branch sync, changelog, CI verification, PR creation. We don't have a release/ship command. Complements our flow — review validates, ship releases. |
| **speckit-utils** | 3 | ADOPT | Resume interrupted workflows, validate health, verify spec-to-task traceability. The resume capability is valuable — if an agent crashes mid-implement, this picks up where it left off. No overlap. |
| **staff-review** | 1 | SKIP | Staff-engineer-level code review with spec compliance matrix. **Our review command already does this** plus tiered fixes and PR lifecycle. The spec coverage matrix output format is worth stealing (noted for self-review improvements). |
| **status** | 1 | COMPANION | Workflow progress dashboard. Already in bootstrap.sh. |
| **superb** | 8 | COMPANION | Superpowers bridge: TDD, verification, critique, debug. Already in bootstrap.sh. |
| **sync** | 5 | SKIP | Detect and resolve drift between specs and implementation. **Reconcile (our companion) already does this.** Sync is more feature-rich (bidirectional, backfill) but reconcile is simpler and sufficient. |
| **v-model** | 9 | SKIP | V-Model paired generation of dev specs + test specs. Safety-critical compliance pattern. Overkill for our workflow unless building regulated software. |
| **verify** | 1 | COMPANION | Evidence-based completion gate. Already in bootstrap.sh. |
| **verify-tasks** | 1 | ADOPT | Detects phantom completions — tasks marked done with no real implementation. Simple, high-value guard. Our review catches some of this but verify-tasks is a focused pre-check. |

## Summary

| Decision | Count | Extensions |
|----------|-------|------------|
| **COMPANION** | 4 | superb, verify, reconcile, status |
| **ADOPT** | 5 | archive, doctor, fixit, repoindex, ship, speckit-utils, verify-tasks |
| **WATCH** | 6 | checkpoint, conduct, critique, iterate, maqa, plan-review-gate, qa |
| **SKIP** | 24 | aide, azure-devops, cleanup, docguard, extensify, fix-findings, fleet, jira, learn, maqa-*, onboard, plan-review-gate, presetify, product-forge, ralph, retro, retrospective, review, staff-review, sync, v-model |

## Recommended Bootstrap Update

Add to `bootstrap.sh` ADOPT tier:
- `archive` — post-merge memory archival
- `doctor` — project health diagnostics
- `fixit` — reactive spec-aware bug fixing
- `repoindex` — repo orientation for agents
- `ship` — release pipeline automation
- `speckit-utils` — workflow resume and traceability
- `verify-tasks` — phantom completion detection

This would bring the full install to **~35+ commands** covering the entire lifecycle from spec through release.

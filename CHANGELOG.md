## [1.1.0] - 2026-04-05

### Added
- `/speckit.self-review` — process retrospective that evaluates workflow effectiveness across five dimensions (spec fidelity, plan accuracy, task decomposition, review effectiveness, workflow friction), dispatches agents to auto-improve LOW/MEDIUM risk issues in extension commands, and checks community catalog for new relevant extensions
- `bootstrap.sh` — one-command project setup that installs spec-kit + orchestration + companion extensions (superb, verify, reconcile, status)
- Companion extension recommendations in extension.yml (superb, verify, reconcile, status)

### Changed
- Extension version bumped to 1.1.0
- Updated README with full command reference, companion extensions table, and architecture notes

## [1.0.0] - 2026-04-05

### Added
- `/speckit.review` — spec-compliant post-implementation review with tiered fixes and PR lifecycle management
- `/speckit.assign` — agent-to-task assignment with capability matching and confidence scoring
- `/speckit.crossreview` — cross-harness adversarial review using alternate AI models
- Review template for structured phase review reports
- Cross-review JSON schema for structured harness communication
- Merge conflict resolution protocol (4-tier: regenerate, owner-resolve, auto-merge, flag)
- PR comment response protocol (ADDRESSED/REJECTED/ISSUED/CLARIFY)
- Thread resolution script for branch protection compliance
- Configuration template for review and cross-review settings

### Origin
Extracted from SteeZyT33/spec-kit fork (specs 001-005) into standalone extension.

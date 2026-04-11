# Cross-Review Agent Expansion Scope

**Status**: accepted into active Orca review-tooling scope

## Goal

Expand Orca cross-review from a narrow `harness` concept into a broader
agent-selection model that can support additional review runners such as:

- `opencode`
- `cursor-agent`
- existing review runners: `codex`, `claude`, `gemini`
- other installer-known Orca agent names where adapter support is available

This is now part of the active Orca review-tooling direction. It is not blocked
behind a separate decision anymore.

## Why This Matters

Right now Orca has two mismatched realities:

- the installer/extension setup already recognizes a broad set of agent names
- the cross-review runtime only supports `codex`, `claude`, and `gemini`

That mismatch causes friction:

- manual `opencode` review works, but Orca cannot invoke it through the normal
  cross-review path
- users can reasonably expect supported installed agents to be usable for review
- the current `harness` terminology is too narrow if Orca is going to stay
  provider-agnostic
- `pr-review` and `self-review` both conceptually depend on cross-review, so
  the naming and runtime limitations leak into other commands too

## Proposed Direction

### 1. Add `--agent` to `speckit.orca.cross-review`

The command should accept:

```text
/speckit.orca.cross-review --agent opencode
/speckit.orca.cross-review --agent cursor-agent --scope design
/speckit.orca.cross-review --agent codex --scope code
```

`--harness` should remain temporarily as a backward-compatible alias, but the
feature should normalize on `--agent`.

### 2. Move config from `crossreview.harness` to `crossreview.agent`

Preferred config shape:

```yaml
crossreview:
  agent: null
  model: null
  effort: "high"
```

Backward compatibility:

- if `crossreview.agent` is set, use it
- else if legacy `crossreview.harness` is set, use that
- warn in docs/review output that `harness` is now legacy naming

Preferred expanded config shape:

```yaml
crossreview:
  agent: null
  model: null
  effort: "high"
  ask_on_ambiguous: true
  remember_last_success: true
```

### 3. Add selection precedence when `--agent` is omitted

Recommended resolution order:

1. Explicit `--agent`
2. Configured `crossreview.agent`
3. Most recent successful review agent for this repo or feature
4. Highest-ranked installed non-current agent from a tier list
5. Ask the user when the situation is ambiguous and the review choice is likely
   to matter
6. Final fallback: current provider with a warning that the run is no longer
   truly cross-agent

This gives Orca discretion without becoming unpredictable.

### 4. Selection should be explained every time

Cross-review output should always say:

- requested agent, if any
- resolved agent
- why that agent was selected
- whether the result is truly cross-agent or same-agent fallback
- support tier for the selected agent

## Agent Support Model

Not every known agent should be treated as equally ready for cross-review.
Introduce explicit support tiers.

### Tier 1: First-class supported review agents

These have a tested adapter and structured output path:

- `codex`
- `claude`
- `gemini`
- `opencode`

Target for near-term addition:

- `cursor-agent`

### Tier 2: Best-effort supported review agents

These agents may be installed and callable, but Orca does not yet guarantee a
stable structured-review adapter for them.

Examples may include:

- `copilot`
- `cursor-agent`
- `windsurf`
- `junie`
- `amp`
- `auggie`
- `qodercli`
- `kiro-cli`
- `roo`
- `tabnine`
- `kimi`

These should not be auto-selected ahead of Tier 1 unless explicitly requested.

### Tier 3: Known but not review-enabled agents

These can remain installer-known without implying cross-review support. Orca
should list them as unsupported for cross-review until an adapter exists.

Examples may include:

- `generic`
- `bob`
- `shai`
- `kilo`

## Known Agent Matrix

Orca should distinguish:

- installer-known
- selectable for cross-review
- auto-selectable for cross-review

Initial matrix:

| Agent | Installer-known | Selectable | Auto-selectable | Notes |
|---|---|---:|---:|---|
| `codex` | yes | yes | yes | existing adapter |
| `claude` | yes | yes | yes | existing adapter |
| `gemini` | yes | yes | yes | existing adapter |
| `opencode` | yes | yes | yes | adapter to add now |
| `cursor-agent` | yes | target | no | add once adapter is verified |
| `copilot` | yes | maybe | no | do not auto-select until stable adapter exists |
| `windsurf` | yes | maybe | no | same rule |
| `junie` | yes | maybe | no | same rule |
| `amp` | yes | maybe | no | same rule |
| `auggie` | yes | maybe | no | same rule |
| `kiro-cli` | yes | maybe | no | same rule |
| `qodercli` | yes | maybe | no | same rule |
| `roo` | yes | maybe | no | same rule |
| `tabnine` | yes | maybe | no | same rule |
| `kimi` | yes | maybe | no | same rule |
| `generic` | yes | no | no | installer alias only, not a review runner |

This avoids the current mistake of implying that every known installer agent is
equally viable for adversarial review.

## Runtime Changes Needed

### Command contract

Update [cross-review.md](../commands/cross-review.md)
to:

- add `--agent`
- keep `--harness` as legacy alias for one compatibility window
- describe selection precedence
- distinguish `agent` selection from `model` override
- explain when Orca should ask the user instead of auto-selecting
- document support tiers and same-agent fallback behavior
- document the difference between `requested agent`, `resolved agent`, and
  `active provider`

### Config

Update [config-template.yml](../config-template.yml) to:

- introduce `crossreview.agent`
- keep `crossreview.harness` as legacy compatibility for one release window
- document tiered auto-selection behavior
- optionally add `ask_on_ambiguous`
- optionally add `remember_last_success`

### Launcher

Update [crossreview.sh](../scripts/bash/crossreview.sh)
to:

- accept `--agent`
- continue accepting `--harness` as normalized alias
- pass normalized selection into the backend
- surface the resolved agent in logs/output
- emit the selection reason in a stable format for review artifacts

### Backend

Update
[crossreview-backend.py](../scripts/bash/crossreview-backend.py)
to:

- replace the hard-coded `choices=["codex", "claude", "gemini"]`
- move to adapter dispatch by agent name
- add `opencode` adapter
- add `cursor-agent` adapter once its invocation contract is verified
- report structured "known but unsupported" errors for Tier 2/3 agents
- add adapter metadata so Orca can distinguish:
  - installed and runnable
  - known but unsupported
  - selectable but not auto-selectable

### Review artifacts

Update cross-review result output and `review.md` append behavior so each review
records:

- requested agent
- resolved agent
- model
- effort
- selection reason
- whether the review was cross-agent or same-agent fallback
- whether the agent was Tier 1, Tier 2, or unsupported

### Adjacent commands

Update the surrounding command docs so the terminology stays consistent:

- [pr-review.md](../commands/pr-review.md)
  should refer to cross-review as agent-based, not just harness-based
- [self-review.md](../commands/self-review.md)
  should treat failed/weak agent selection as review-pipeline friction evidence
- [README.md](../README.md)
  should stop describing cross-review as only `Codex`, `Claude`, and `Gemini`

## Selection Policy

### Auto-selection should prefer difference, not novelty

The goal is not to pick a random agent. The goal is to pick a useful reviewer.

Preferred ranking factors:

1. Different from the active provider
2. Tier 1 support
3. Recently successful in this repo
4. Reasonable review ergonomics for the current scope

### Suggested default ranking

For now:

1. `opencode`
2. `claude`
3. `gemini`
4. `codex`
5. `cursor-agent`

This is only a starter policy. The real ranking should be adjusted once adapter
quality and structured-output reliability are measured.

### When Orca should ask instead of choosing

Orca should ask the user when:

- multiple Tier 1 agents are installed and equally plausible
- the feature is high-risk and the active provider already matches the best
  auto-selected option
- prior review history is conflicting or absent
- the user is already expressing a preference for a particular provider family
- the available options are only Tier 2 and the choice materially affects trust

Orca should not ask when:

- an explicit `--agent` was provided
- config pins the agent
- only one viable Tier 1 reviewer exists
- the most recent successful reviewer is still installed and clearly better than
  the alternatives

### Remembering the most recent successful reviewer

If enabled, Orca should remember the last successful cross-review agent per repo
or feature and prefer it when:

- it is still installed
- it is different from the active provider
- no explicit override is present

This memory should be advisory, not mandatory.

## Active Scope Boundary

### In scope

- `--agent` flag
- config migration from `harness` to `agent`
- tiered auto-selection rules
- `opencode` adapter
- selection-reason reporting
- support-tier reporting
- review artifact updates for requested vs resolved agent
- `README.md`, `pr-review.md`, and `self-review.md` terminology updates
- review output that shows resolved agent, model, and selection reason
- structured unsupported-agent errors

### In scope if adapter contracts are verified quickly

- `cursor-agent` adapter, if the CLI contract is stable and machine-usable
- persistence of "most recent successful reviewer" per repo or per feature
- a single shared agent-resolution helper so command doc, launcher, and backend
  do not drift

### Out of scope

- adding every installer-known agent as a first-class reviewer immediately
- changing `code-review` semantics at the same time
- adding subjective scoring across agents before reliability evidence exists
- expanding installer-known agent support without a verified runtime contract

## Risks

### 1. False promise of support

If Orca treats every known agent as review-capable, users will assume parity
that does not exist.

Mitigation:

- support tiers
- explicit unsupported-agent errors
- conservative auto-selection
- clear `requested` vs `resolved` output

### 2. Adapter sprawl

Every new agent can add bespoke CLI quirks.

Mitigation:

- adapter pattern in backend
- Tier 1 only for agents with verified structured output paths
- shared resolution logic instead of embedding selection rules in multiple files

### 3. Ambiguous selection behavior

If Orca auto-selects opaquely, users will not trust the review choice.

Mitigation:

- always print the resolved agent and why it was chosen
- ask only when the ambiguity is material
- store success history only as advisory context

### 4. Terminology drift across Orca

If some docs say `harness` and others say `agent`, users will not know which is
canonical.

Mitigation:

- normalize on `agent`
- keep `harness` only as a legacy compatibility term in config/runtime
- update adjacent docs in the same scope

## Immediate Direction

This is now in scope for Orca cross-review improvements.

Immediate MVP:

1. add `--agent`
2. add `crossreview.agent`
3. add `opencode` adapter
4. implement explicit selection precedence
5. update review artifacts to record requested/resolved agent and selection
   reason
6. update README plus `pr-review`/`self-review` terminology
7. add `cursor-agent` when its adapter contract is verified

Practical note:

- changing only [cross-review.md](../commands/cross-review.md)
  would scope the UX, but not make the runtime real
- the actual delivery still touches the command contract, config, launcher, and
  backend

## Done Means

This scope is only complete when all of the following are true:

- users can run `/speckit.orca.cross-review --agent <name>`
- config can pin `crossreview.agent`
- Orca can auto-select from a documented precedence order
- `opencode` works through the normal Orca runtime, not just manually
- review output records requested agent, resolved agent, and selection reason
- unsupported known agents fail clearly instead of pretending support
- surrounding docs no longer describe cross-review as only three harnesses

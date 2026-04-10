# Research Engine Blueprint (Agent-Native for Claude Code + Codex)
_Last updated: April 9, 2026_

## What this document answers

This is the corrected blueprint for the system you actually asked for.

The goal is **not** “a generic CLI-first research app.”

The goal is:

- **plugin-style capabilities for Claude Code and Codex**
- usable both as **directly invoked skills** and as part of a **broader agent harness workflow**
- able to cover all three research tracks you asked for:
  1. **Deep web search for understanding**
  2. **Deep paper consolidation and synthesis**
  3. **Deep GitHub/repo analysis and comparison**

This document answers:

- What should we build?
- How should it plug into Claude Code and Codex?
- What is the right architecture for reusable, agent-native “research skills”?
- What tools should back each track?
- What should the first implementation phases look like?
- What is the best closed-source augmentation layer, if we want it?

---

## Executive decision

Build this as an **agent-native research layer** with four pieces:

1. **Skills** as the primary user interface  
   These are what Claude Code and Codex see and invoke.

2. **MCP servers** as the execution layer  
   These expose structured tools to the skills.

3. **Subagents** as the parallel decomposition layer  
   These keep noisy exploratory work off the main thread.

4. **Minimal project guidance** (`CLAUDE.md` / `AGENTS.md`) as the durable policy layer  
   These define stable rules, not long procedures.

The key design principle is:

> **Agent-native first, API-backed second.**

APIs are implementation details behind tools.  
The actual product surface is:

- Claude Code skill
- Codex skill
- MCP tool
- subagent
- project guidance

---

## What we are not building

Do **not** build this as:

- a standalone research website
- a single mega-agent with an enormous prompt
- a raw API-first service that agents happen to call later
- a monolithic “deep research” tool that tries to do everything in one pass
- a workflow that depends on scraping Google Scholar as the primary machine interface

Do **not** bury procedural workflows in `CLAUDE.md` or `AGENTS.md`.  
Those files should stay short and durable. Put repeatable workflows into **skills**.

---

## Product statement

You are building a **research cognition layer** for coding agents.

It should let you say things like:

- “Use `deep-web-research` to understand the state of X.”
- “Use `paper-synthesis` to consolidate papers on Y.”
- “Use `repo-context-analysis` on repo XYZ and explain how it implements A, B, and C.”
- “Use `compare-and-roadmap` to compare repo XYZ to our system and propose a roadmap.”

That should work:

- by direct invocation
- by automatic skill selection
- inside a larger multi-agent workflow
- without rewriting the underlying capability for every host

---

## The correct target: Claude Code + Codex

This blueprint is optimized first for **Claude Code** and **Codex**.

### Claude Code surfaces we should target

Use Claude Code’s extension surfaces like this:

- **`CLAUDE.md`** for standing repo conventions and small, durable instructions
- **Skills** for reusable workflows and research playbooks
- **Subagents** for delegated research tracks
- **Hooks** for deterministic preflight / postprocessing / validation
- **MCP** for external tools and shared context
- **Plugins** once the skills are mature enough to distribute

### Codex surfaces we should target

Use Codex’s customization stack like this:

- **`AGENTS.md`** for standing repo conventions and small, durable instructions
- **Skills** for reusable workflows
- **Subagents** for explicit parallel delegated work
- **MCP** for external tools and services
- **Plugins** when we want installable, reusable distribution
- **Automation / SDK** only after the skill workflows are already solid

### Why this matters

The core mistake in the earlier draft was treating “CLI compatibility” as the primary abstraction.

That is backwards for your use case.

The primary abstraction is:

- **host-native skill**
- backed by **shared MCP tools**
- optionally composed with **subagents**
- optionally automated later with **SDKs**

That lets the same capability feel native in both Claude Code and Codex without making raw API calls the front door.

---

## Design principles

### 1. Skills are the front door

Every major workflow should exist as a named skill.  
Users and agents should be able to invoke it directly.

### 2. MCP is the execution bus

Every external capability should be exposed behind an MCP tool, not hardcoded in prompts.

### 3. Subagents do the noisy work

Search fan-out, paper clustering, repo feature tracing, and evidence gathering should happen in subagents or delegated workers.

### 4. Guidance files stay small

`CLAUDE.md` and `AGENTS.md` should contain stable rules, not step-by-step workflows.

### 5. Outputs must be structured

The system should always return:

- a readable markdown answer
- a structured JSON artifact
- evidence/source lists
- explicit unknowns / open questions

### 6. Read-heavy before write-heavy

Most research tasks are read-heavy.  
Parallel write-heavy subagents create merge conflict and coordination risk. Default to read-only research unless the user explicitly asks for code changes.

### 7. Local-first for sensitive code

For private repos, start with local read-only analysis and only use external indexing/search systems when they materially improve results.

### 8. Provider selection lives in config, not prompts

Skills should reference tool names and workflow steps, not vendor-specific details.  
Swap providers through MCP server config.

---

## The architecture

## Canonical shape

```text
User prompt
  -> Claude Code skill / Codex skill
    -> main agent decides scope
      -> spawn subagents as needed
        -> call MCP tools
          -> provider adapters
            -> evidence store + structured artifacts
              -> final synthesis
```

## High-level components

```text
research-engine/
  docs/
    blueprint.md

  hosts/
    claude/
      CLAUDE.md
      .claude/
        skills/
        subagents/
        hooks/

    codex/
      AGENTS.md
      .agents/
        skills/
      codex-plugin/
        ...optional packaging later...

  skills-shared/
    deep-web-research/
    paper-synthesis/
    repo-context-analysis/
    compare-and-roadmap/

  mcp/
    research-web/
    research-papers/
    research-repo/
    research-orchestrator/     # optional composite layer later

  providers/
    web/
    papers/
    repo/

  schemas/
    research-run.schema.json
    web-brief.schema.json
    paper-synthesis.schema.json
    repo-analysis.schema.json
    comparison-roadmap.schema.json

  artifacts/
    reports/
    traces/
    evidence/

  tools/
    sync_skills.py
    validate_outputs.py
```

---

## How the host-specific packaging should work

## Shared source of truth

Create one canonical source tree for the skills:

```text
skills-shared/
  deep-web-research/
  paper-synthesis/
  repo-context-analysis/
  compare-and-roadmap/
```

Then mirror those into host-specific locations with a sync/build step.

Do **not** hand-edit two separate copies forever.

---

## Claude Code layout

Use repo-local skills during development:

```text
.claude/skills/<skill-name>/SKILL.md
```

Recommended project structure:

```text
.claude/
  skills/
    deep-web-research/
      SKILL.md
      reference.md
      examples.md
      scripts/
    paper-synthesis/
      SKILL.md
      reference.md
    repo-context-analysis/
      SKILL.md
      examples.md
    compare-and-roadmap/
      SKILL.md
      examples.md

  subagents/
    web-agent.md
    paper-agent.md
    repo-agent.md
    compare-agent.md

  hooks/
    preflight.sh
    validate-evidence.py
    persist-artifacts.py
```

Use personal skills later for generally useful research skills; use plugins only once the workflows are stable.

---

## Codex layout

Use repo-scoped skills during development:

```text
.agents/skills/<skill-name>/SKILL.md
```

Recommended project structure:

```text
AGENTS.md
.agents/
  skills/
    deep-web-research/
      SKILL.md
      references/
      scripts/
      agents/
        openai.yaml   # optional metadata / dependencies
    paper-synthesis/
      SKILL.md
    repo-context-analysis/
      SKILL.md
    compare-and-roadmap/
      SKILL.md
```

Later, when you want installable distribution, package the stable skill set as a **Codex plugin**.

---

## Minimal durable guidance files

## `CLAUDE.md`

Keep this short. It should define things like:

- project conventions
- repo layout hints
- what the research skills are called
- when Claude should prefer a skill instead of freeform reasoning
- basic output expectations

Example content:

```markdown
# Project guidance

Use research skills for deep analysis instead of ad hoc exploration.

Preferred skills:
- /repo-context-analysis
- /compare-and-roadmap
- /deep-web-research
- /paper-synthesis

Default behavior:
- prefer structured outputs
- include evidence references
- keep exploratory work in subagents when the task is broad
- do not modify code unless explicitly asked
```

## `AGENTS.md`

Keep the Codex version similarly short:

```markdown
# Project instructions

When a task is research-heavy, prefer repository skills over freeform reasoning.

Preferred workflows:
- repo-context-analysis for “how does this repo implement X?”
- compare-and-roadmap for repo-vs-repo or repo-vs-our-system requests
- deep-web-research for ecosystem/landscape understanding
- paper-synthesis for literature questions

Default expectations:
- return structured markdown plus explicit evidence
- use subagents when broad parallel exploration would help
- stay read-only unless the task explicitly requests implementation
```

---

## The four core skills

This system should begin with **four** skills, not twelve.

1. `repo-context-analysis`
2. `compare-and-roadmap`
3. `deep-web-research`
4. `paper-synthesis`

That is enough coverage for the actual workflows you described.

---

# Skill 1 — `repo-context-analysis`

## Purpose

Answer questions like:

- “How does this repo implement X?”
- “Map the architecture of this repo.”
- “Which files/classes/modules matter for Y?”
- “Explain how auth, memory, orchestration, evals, or agent routing work in this codebase.”

This is the first skill you should build.

## What good output looks like

The skill should return:

- architecture overview
- key modules/components
- feature trace for the requested concept
- important files/symbols/functions
- notable implementation patterns
- weaknesses / technical debt / assumptions
- adaptation opportunities

## Best implementation strategy

### Default local/private analysis path

Start local and read-only:

- local checkout
- `tree` / ripgrep / AST parsing / code search
- Aider repo map
- Repomix or Gitingest for whole-repo packaging
- host-native file search tools when available

This should be the default because it is:

- private
- cheap
- fast
- highly controllable

### Public repo augmentation

For public repos, add:

- **DeepWiki** for rapid architecture onboarding and public-repo Q&A
- **Open Aware** if you want open-source code intelligence via MCP or agent integration

### Enterprise/private augmentation

For large private or multi-repo analysis, optionally add:

- **Qodo Context Engine**
- **Sourcegraph Deep Search**

These are augmentation layers, not the initial dependency.

## MCP tools behind this skill

Recommended MCP tool surface:

- `repo.map_architecture`
- `repo.trace_feature`
- `repo.find_symbols`
- `repo.find_entrypoints`
- `repo.compare_patterns`
- `repo.generate_report`

### Example normalized input

```json
{
  "repo": "/path/or/url",
  "question": "How does this repo implement agent memory?",
  "focus": ["architecture", "memory"],
  "depth": "deep",
  "mode": "read-only"
}
```

### Example normalized output

```json
{
  "summary": "...",
  "architecture": {
    "top_level_components": [],
    "data_flows": [],
    "key_entrypoints": []
  },
  "feature_trace": [
    {
      "feature": "memory",
      "files": [],
      "symbols": [],
      "how_it_works": "..."
    }
  ],
  "patterns": [],
  "weaknesses": [],
  "evidence": []
}
```

## Subagents for this skill

Recommended delegated roles:

- `architecture-reader`
- `feature-tracer`
- `pattern-extractor`

The main agent should remain the synthesizer, not the raw explorer.

## Skill output template

```markdown
# Repo Analysis

## Executive take
...

## Architecture
...

## How `<feature>` is implemented
...

## Important files and modules
...

## Reusable patterns
...

## Risks / weaknesses
...

## What we should borrow
...
```

---

# Skill 2 — `compare-and-roadmap`

## Purpose

This is the most important skill in the system.

It answers the actual workflow you care about:

- “Review repo XYZ using context engine.”
- “Explain how it compares to our system.”
- “What is the best implementation of X?”
- “How should we implement the strongest ideas in our own system?”
- “Give me a roadmap.”

## What this skill should do

It should:

1. analyze the external system or repo
2. analyze your current system
3. compare architecture and implementation choices
4. rank strengths/weaknesses
5. produce an adoption roadmap

## Core behavior

### Always compare on explicit axes

For example:

- architecture clarity
- extensibility
- memory model
- orchestration model
- evaluation approach
- observability
- cost profile
- operational complexity
- developer ergonomics

### Always produce an “adopt / adapt / ignore” section

Do not just describe differences. Force the system to decide:

- **Adopt** as-is
- **Adapt** with changes
- **Ignore** for now

### Always return a staged roadmap

Minimum roadmap output:

- **Phase 1 — quick wins**
- **Phase 2 — foundational architecture**
- **Phase 3 — advanced/optional capabilities**

## Best implementation strategy

This skill is a **composite**.

It should orchestrate:

- one repo-analysis worker for the external system
- one repo-analysis worker for your codebase
- optional web or paper validation if the question touches best practices or academic approaches
- one synthesis writer

## MCP tools behind this skill

Recommended MCP surface:

- `repo.compare_repos`
- `repo.rank_implementations`
- `repo.generate_roadmap`
- `research.validate_with_web`
- `research.validate_with_papers`

### Example normalized input

```json
{
  "external_repo": "https://github.com/org/project",
  "internal_repo": "/workspace/perf-lab",
  "focus": ["agent orchestration", "memory", "evaluation"],
  "goal": "produce roadmap",
  "depth": "deep"
}
```

### Example normalized output

```json
{
  "verdict": "Project X has the stronger memory architecture; our orchestration layer is more flexible.",
  "comparison_axes": [],
  "adopt": [],
  "adapt": [],
  "ignore": [],
  "roadmap": [
    {
      "phase": "Phase 1",
      "objective": "...",
      "tasks": []
    }
  ],
  "risks": [],
  "evidence": []
}
```

## Output template

```markdown
# Comparison and Roadmap

## Verdict
...

## Feature-by-feature comparison
...

## What they do better
...

## What we do better
...

## Adopt / Adapt / Ignore
...

## Roadmap
### Phase 1
...
### Phase 2
...
### Phase 3
...

## Risks
...

## Open questions
...
```

## This skill should be the default for prompts like

- “Compare repo XYZ to our system”
- “Find the best implementation of X and justify it”
- “Review this repo deeply and tell me what we should borrow”
- “Map their orchestration design and turn it into our roadmap”

---

# Skill 3 — `deep-web-research`

## Purpose

Answer questions like:

- “What is the state of the art in deep research agents?”
- “What are the best open-source implementations of X?”
- “What is the current landscape of agent harness frameworks?”
- “Find the strongest competing systems and explain why.”

This is **ecosystem understanding**, not literature review and not codebase tracing.

## What good output looks like

The skill should return:

- a landscape map
- major approaches/vendors/projects
- strengths and weaknesses of each
- evidence from multiple sources
- the main unresolved debates / uncertainty
- recommended options for your use case

## Best implementation strategy

### Preferred open implementation

Use a hosted or self-run MCP-backed research stack with:

- **Tavily** for search and extraction
- **Firecrawl** for difficult pages, site crawl, structured extraction
- optional **SearXNG** for privacy or fallback metasearch

Above that, use one of:

- **GPT Researcher** if you want a purpose-built autonomous research layer with MCP integration
- **open_deep_research** if you want a very configurable open framework

### Closed-source augmentation layer

Use these only as premium backends or human validation tools, not as the only architecture:

- **OpenAI Deep Research**
- **Gemini Deep Research**
- **Perplexity Sonar Deep Research**

They are useful when you want best-in-class closed-source browsing/synthesis, but they should sit behind a tool boundary, not dictate your whole system architecture.

## MCP tools behind this skill

Recommended MCP surface:

- `web.expand_query`
- `web.search`
- `web.extract`
- `web.crawl_site`
- `web.research`
- `web.validate_claims`

### Example normalized input

```json
{
  "query": "best open-source agent harnesses for deep research",
  "goal": "landscape analysis",
  "depth": "deep",
  "time_range": "current"
}
```

### Example normalized output

```json
{
  "summary": "...",
  "landscape": [
    {
      "name": "Project A",
      "category": "open-source research agent",
      "strengths": [],
      "weaknesses": [],
      "evidence": []
    }
  ],
  "recommendations": [],
  "uncertainties": [],
  "evidence": []
}
```

## Subagents for this skill

Recommended delegated roles:

- `query-planner`
- `source-verifier`
- `landscape-writer`

## Important constraint

This skill is for **web understanding**, not paper synthesis.  
If the user asks for academic consensus, call `paper-synthesis` instead.

---

# Skill 4 — `paper-synthesis`

## Purpose

Answer questions like:

- “What does the literature say about agent memory?”
- “Consolidate the best papers on multi-agent orchestration.”
- “Find the strongest papers on retrieval for scientific research.”
- “Compare methods, results, and tradeoffs across the literature.”

This is a literature workflow, not a general web workflow.

## Best implementation strategy

### Primary machine-friendly scholarly stack

Use this as the default scholarly data layer:

- **Semantic Scholar API** as the first search/metadata layer
- **OpenAlex** as the second discovery layer
- **Crossref** for DOI/metadata resolution
- **Unpaywall** for open-access/full-text routing
- **Europe PMC** and **CORE** as domain/full-text supplements

### Synthesis engine

Use **PaperQA2** as the main open-source paper reasoning/synthesis layer.

### Closed-source augmentations

Use these as optional enhancements:

- **Undermind** for deep discovery / novelty / successive search style behavior
- **Elicit** for systematic-review-style screening, extraction, and report generation

## Important recommendation about Google Scholar

Do **not** make Google Scholar scraping the primary machine path.

Use Google Scholar only as:

- a manual sanity-check source
- a fallback discovery surface
- an occasional recall supplement

Your production machine path should rely on more stable, API-friendly scholarly systems.

## MCP tools behind this skill

Recommended MCP surface:

- `papers.search`
- `papers.fetch_metadata`
- `papers.fetch_fulltext`
- `papers.cluster_topics`
- `papers.extract_methods`
- `papers.extract_results`
- `papers.synthesize`
- `papers.check_novelty`   # optional premium adapter

### Example normalized input

```json
{
  "query": "multi-agent memory systems",
  "max_papers": 25,
  "goal": "compare methods and tradeoffs",
  "focus": ["methods", "results", "limitations"]
}
```

### Example normalized output

```json
{
  "summary": "...",
  "themes": [],
  "paper_table": [],
  "consensus": [],
  "disagreements": [],
  "gaps": [],
  "best_methods": [],
  "evidence": []
}
```

## Subagents for this skill

Recommended delegated roles:

- `paper-scout`
- `methods-extractor`
- `results-extractor`
- `contradiction-checker`

## Output template

```markdown
# Paper Synthesis

## Research question
...

## Major themes
...

## Best methods
...

## Where the literature agrees
...

## Where it disagrees
...

## Gaps / open questions
...

## What matters for our system
...
```

---

## Shared MCP tool design

You do **not** need dozens of arbitrary tools.  
Keep the tool surface compact and composable.

## Track-specific servers

### `research-web` MCP server

Expose:

- `web.expand_query`
- `web.search`
- `web.extract`
- `web.crawl_site`
- `web.research`
- `web.validate_claims`

### `research-papers` MCP server

Expose:

- `papers.search`
- `papers.fetch_metadata`
- `papers.fetch_fulltext`
- `papers.cluster_topics`
- `papers.extract_methods`
- `papers.extract_results`
- `papers.synthesize`

### `research-repo` MCP server

Expose:

- `repo.map_architecture`
- `repo.trace_feature`
- `repo.find_symbols`
- `repo.compare_repos`
- `repo.rank_implementations`
- `repo.generate_roadmap`

## Optional composite server

Later, if useful, add `research-orchestrator` with:

- `research.compare_and_roadmap`
- `research.deep_dive`
- `research.multi_track`

But do **not** start here. Start with the three track servers first.

---

## Why the repo track should be first

This is where your highest leverage is.

For your actual workflows, the first pain point is not “we cannot query the web.”  
It is:

- “How does this repo actually work?”
- “What is the best implementation of X?”
- “What can we steal and how should we integrate it?”

That means **repo analysis + compare/roadmap** should be Phase 1.

Only then add the deep web and paper tracks.

---

## Recommended provider stacks by track

## Track 1 — web understanding

### Open-source-first

- Tavily
- Firecrawl
- GPT Researcher or open_deep_research
- optional SearXNG

### Closed-source augmentations

- OpenAI Deep Research
- Gemini Deep Research
- Perplexity Sonar Deep Research

### Recommendation

Build your own `web.research` skill/tool stack and keep these provider choices behind adapters.

---

## Track 2 — paper synthesis

### Open-source-first

- Semantic Scholar
- OpenAlex
- Crossref
- Unpaywall
- Europe PMC
- CORE
- PaperQA2

### Closed-source augmentations

- Undermind
- Elicit

### Recommendation

Use PaperQA2 as the synthesis core and use your Semantic Scholar API as the first-class search layer.

---

## Track 3 — repo analysis

### Open-source/public path

- local checkout + code search + AST parsing
- Aider repo map
- Repomix
- Gitingest
- DeepWiki for public repos
- Open Aware

### Closed-source/private path

- Qodo Context Engine
- Sourcegraph Deep Search

### Recommendation

Default to local repo analysis first, then add DeepWiki/Qodo/Sourcegraph where it materially improves speed or depth.

---

## The recommended skill set by phase

## Phase 1 — Build the repo brain

Build:

- `repo-context-analysis`
- `compare-and-roadmap`

Back them with:

- local repo map / file search / symbol tracing
- optional DeepWiki for public repos
- optional Qodo / Sourcegraph adapters later

### Success criteria

You can reliably answer:

- “How does repo X implement Y?”
- “Which repo has the best implementation of Z, and why?”
- “Compare this repo to ours and give us an implementation roadmap.”

---

## Phase 2 — Add deep web understanding

Build:

- `deep-web-research`

Back it with:

- Tavily
- Firecrawl
- optional GPT Researcher or open_deep_research behind MCP

### Success criteria

You can answer:

- “What is the current landscape of X?”
- “What are the strongest open-source / closed-source options?”
- “What are the strongest arguments for and against approach Y?”

---

## Phase 3 — Add paper synthesis

Build:

- `paper-synthesis`

Back it with:

- Semantic Scholar
- OpenAlex
- Unpaywall
- PaperQA2
- optional Elicit / Undermind adapters

### Success criteria

You can answer:

- “What does the literature actually say?”
- “What methods dominate?”
- “What are the important tradeoffs and gaps?”
- “Which ideas are robust enough to bring into our own system?”

---

## Phase 4 — Package for distribution

Once the workflows are stable:

- package the Codex skill set as a plugin
- package the Claude skill set as a plugin if distribution is needed
- standardize MCP config
- standardize output schemas
- add installer / sync tooling

### Success criteria

Someone else can install the system without manually copying skills and tools around.

---

## Hooks and deterministic behavior

Use hooks sparingly, but use them where determinism matters.

## Good hook use cases

- preflight: detect repo root, branch, dirty worktree, environment
- post-tool: persist evidence/source metadata
- final-answer validation: ensure output includes required sections
- schema validation: ensure JSON artifacts are valid
- logging: store a trace of which skill and which tools were used

## Do not use hooks for

- core reasoning
- choosing providers
- turning the workflow into a brittle state machine

Hooks should enforce guardrails and artifact hygiene, not replace the agent.

---

## Subagent strategy

Subagents are not optional for the bigger workflows.  
They are how you avoid context pollution.

## Default role set

Use a small stable set of roles:

- `web-agent`
- `paper-agent`
- `repo-agent`
- `compare-agent`
- `synthesis-agent` (optional if the main agent is synthesizing)

## General rules

- use subagents for broad, read-heavy, parallel exploration
- keep the main thread focused on decisions and final output
- do not let multiple subagents write code in parallel by default
- subagents should return distilled notes, not raw logs

---

## Standard output contract

Every research run should produce both human-readable and machine-readable artifacts.

## Required artifacts

- `answer.md`
- `answer.json`
- `evidence.json`
- `trace.json`

## Optional artifacts by track

### Repo analysis

- `repo-map.md`
- `feature-trace.json`
- `comparison-matrix.csv`
- `roadmap.md`

### Paper synthesis

- `paper-table.csv`
- `clusters.json`
- `methods-vs-results.md`

### Web research

- `source-notes.md`
- `landscape-table.csv`

## Minimum JSON fields

```json
{
  "task_type": "repo|web|papers|comparison",
  "question": "...",
  "summary": "...",
  "recommendations": [],
  "risks": [],
  "open_questions": [],
  "evidence": []
}
```

For the comparison skill, add:

```json
{
  "adopt": [],
  "adapt": [],
  "ignore": [],
  "roadmap": []
}
```

---

## The exact workflows you care about

## Workflow A — “Review repo XYZ deeply”

Use:

- `repo-context-analysis`

Behavior:

1. map architecture
2. trace requested features
3. identify important files and flows
4. summarize reusable patterns
5. return risks and adoption ideas

### Example prompt

```text
Use repo-context-analysis on repo XYZ.
Focus on how it implements agent orchestration, memory, and evaluation.
Return architecture, key modules, feature traces, and what looks worth copying.
```

---

## Workflow B — “Find the best implementation of X with justification”

Use:

- `compare-and-roadmap`
- optionally `deep-web-research` if broader ecosystem evidence is needed

Behavior:

1. identify candidate repos/systems
2. analyze the strongest candidates
3. score them on explicit criteria
4. pick a winner or top two
5. explain why
6. translate findings into your roadmap

### Example prompt

```text
Use compare-and-roadmap.
Find the strongest implementation of agent memory among repos A, B, and C.
Compare the winner to our system and give a roadmap for how we should implement the strongest ideas.
```

---

## Workflow C — “How should we implement this in our own system?”

Use:

- `compare-and-roadmap`
- optionally `paper-synthesis` if academic grounding matters

Behavior:

1. analyze external implementation
2. analyze internal constraints
3. identify what transfers cleanly and what does not
4. produce phased plan
5. note risks and prerequisites

### Example prompt

```text
Use compare-and-roadmap against our system.
Explain what parts of repo XYZ’s orchestration architecture we should adopt, what we should adapt, and what we should ignore.
Then give a three-phase roadmap.
```

---

## Workflow D — “Give me the landscape first, then dive deep”

Use:

1. `deep-web-research`
2. `repo-context-analysis`
3. `compare-and-roadmap`

This lets the first skill identify the best candidates and the later skills deeply inspect the ones that matter.

---

## Recommendation on the first build

If you are actually implementing this now, do this:

## First build target

Build **only this**:

- one `research-repo` MCP server
- one `repo-context-analysis` skill
- one `compare-and-roadmap` skill
- one `repo-agent` subagent
- minimal `CLAUDE.md`
- minimal `AGENTS.md`
- output schema validation

That is enough to deliver value immediately.

## Why

Because the highest-value usage is already:

- compare repo X vs our system
- explain how repo X implements Y
- produce roadmap for our own implementation

You do not need the full web and paper machinery to start getting strong wins.

---

## Practical implementation order

### Week 1
- define output schemas
- implement repo map + feature trace tools
- create `repo-context-analysis` skill in Claude and Codex
- create minimal `repo-agent`

### Week 2
- implement `repo.compare_repos`
- implement `repo.generate_roadmap`
- create `compare-and-roadmap` skill
- add artifact persistence and validation

### Week 3
- add Tavily + Firecrawl behind `research-web`
- create `deep-web-research`
- add `web-agent`

### Week 4
- add Semantic Scholar + OpenAlex + PaperQA2 behind `research-papers`
- create `paper-synthesis`
- add `paper-agent`

### Week 5+
- plugin packaging
- provider config cleanup
- quality benchmarks
- broader automation

---

## Quality bar

A good research skill should do more than summarize.

It should:

- decompose the task well
- gather evidence
- force explicit comparison criteria
- name uncertainty
- produce actionable output
- connect analysis to implementation decisions

If a skill gives you a pretty summary but no evidence and no plan, it is not good enough.

---

## Evaluation harness

Create a small benchmark set of real prompts from your workflow.

## Example benchmark tasks

### Repo analysis
- “How does repo X implement memory?”
- “Which modules matter for orchestration?”
- “Explain how repo Y handles tool routing.”

### Comparison
- “Compare repo X and repo Y for agent harness design.”
- “Which repo has the better eval pipeline?”
- “Give us a roadmap to adopt the strongest design.”

### Web landscape
- “What are the strongest open-source deep research frameworks right now?”
- “What is the current state of agent skills across Claude Code and Codex?”

### Papers
- “What does the literature say about memory graphs for agents?”
- “Compare approaches to literature search automation.”

## Score each run on

- factual correctness
- evidence quality
- depth
- actionability
- structure
- implementation usefulness

---

## Security and operational guidance

## Local vs remote MCP

Use:

- **local stdio MCP** by default for private development and low-friction local tools
- **remote/HTTP MCP** only when you truly need shared internal services

If you expose remote MCP services:

- require auth
- log usage
- keep providers server-side
- treat secrets carefully
- separate read-only from write-capable tools

## Read-only by default

The research layer should default to:

- read code
- inspect docs
- search web
- synthesize findings

Write tools should be opt-in and usually belong in a separate implementation skill or coding workflow.

## Provider confidentiality

Be careful sending private code to hosted providers.  
That is why the default repo-analysis path should begin locally.

---

## Cost control

This kind of system can get expensive if you let every task escalate immediately.

## Cost rules

- use lighter-weight scouts for exploration
- escalate only the final synthesis to a stronger model
- cache URL extraction
- cache paper metadata and abstracts
- cache repo maps for unchanged commits
- keep research runs artifacted so repeated questions do not start from zero

---

## What to avoid

Do **not**:

- build one giant “research” skill that handles everything
- overfit the system to one provider
- use Google Scholar scraping as the core paper pipeline
- put entire procedures into `CLAUDE.md` or `AGENTS.md`
- create parallel write-heavy subagents by default
- skip structured outputs
- let evidence handling remain implicit

---

## Best open-source and closed-source options by track

## Web understanding

### Open-source / open-core
- Tavily Agent Skills
- GPT Researcher
- open_deep_research
- Firecrawl
- SearXNG

### Closed-source
- OpenAI Deep Research
- Gemini Deep Research
- Perplexity Sonar Deep Research

## Paper synthesis

### Open-source / API-friendly
- Semantic Scholar
- OpenAlex
- Crossref
- Unpaywall
- Europe PMC
- CORE
- PaperQA2

### Closed-source
- Undermind
- Elicit

## Repo analysis

### Open-source / local / public
- DeepWiki (especially for public onboarding)
- local code search / AST tracing
- Aider repo map
- Repomix
- Gitingest
- Open Aware

### Closed-source / enterprise
- Qodo Context Engine
- Sourcegraph Deep Search

---

## Final recommendation

If you want the strongest practical plan:

## Build first

- `repo-context-analysis`
- `compare-and-roadmap`

## Back them with

- local repo mapping and tracing
- optional DeepWiki for public repos
- optional Qodo / Sourcegraph adapters later

## Then add

- `deep-web-research` with Tavily + Firecrawl
- `paper-synthesis` with Semantic Scholar + OpenAlex + PaperQA2

## Keep the architecture

- host-native skills first
- MCP servers underneath
- subagents for parallel exploration
- guidance files short
- plugins only after the skills are mature

That is the cleanest, highest-leverage answer to the questions you actually asked.

---

## Build checklist

## Phase 1 checklist
- [ ] Define shared output schemas
- [ ] Build `research-repo` MCP server
- [ ] Implement `repo.map_architecture`
- [ ] Implement `repo.trace_feature`
- [ ] Implement `repo.compare_repos`
- [ ] Implement `repo.generate_roadmap`
- [ ] Create Claude `repo-context-analysis`
- [ ] Create Claude `compare-and-roadmap`
- [ ] Create Codex `repo-context-analysis`
- [ ] Create Codex `compare-and-roadmap`
- [ ] Add minimal `CLAUDE.md`
- [ ] Add minimal `AGENTS.md`
- [ ] Add read-only `repo-agent`
- [ ] Persist artifacts

## Phase 2 checklist
- [ ] Build `research-web` MCP server
- [ ] Add Tavily adapter
- [ ] Add Firecrawl adapter
- [ ] Create `deep-web-research`
- [ ] Add `web-agent`

## Phase 3 checklist
- [ ] Build `research-papers` MCP server
- [ ] Add Semantic Scholar adapter
- [ ] Add OpenAlex adapter
- [ ] Add PaperQA2 integration
- [ ] Add Unpaywall / Crossref / Europe PMC / CORE helpers
- [ ] Create `paper-synthesis`
- [ ] Add `paper-agent`

## Phase 4 checklist
- [ ] Package Codex skills as plugin
- [ ] Package Claude skills as plugin if needed
- [ ] Add sync/build tooling
- [ ] Add benchmark tasks
- [ ] Add scorecards / regression tests

---

## Appendix A — Minimal skill naming convention

Use the same names in both hosts where possible:

- `deep-web-research`
- `paper-synthesis`
- `repo-context-analysis`
- `compare-and-roadmap`

That gives you direct prompt portability.

---

## Appendix B — Suggested skill descriptions

### `deep-web-research`
Use when the task requires a broad current-state understanding of a topic across multiple web sources, with comparison, evidence, and synthesis.

### `paper-synthesis`
Use when the task requires scientific or scholarly literature consolidation, method comparison, consensus/disagreement analysis, or research gap identification.

### `repo-context-analysis`
Use when the task asks how a repository implements a concept, how the architecture is structured, or which modules/files are important for a feature.

### `compare-and-roadmap`
Use when the task asks to compare an external repo/system to our own, identify what to borrow, rank implementation quality, or create a phased roadmap.

---

## Appendix C — Official docs and current references used to align the architecture

### Claude Code
- Skills: https://code.claude.com/docs/en/skills
- Extend Claude Code: https://code.claude.com/docs/en/features-overview
- Subagents: https://code.claude.com/docs/en/sub-agents
- Hooks: https://docs.anthropic.com/en/docs/claude-code/hooks
- Agent SDK: https://code.claude.com/docs/en/agent-sdk/overview

### Codex
- Skills: https://developers.openai.com/codex/skills
- AGENTS.md: https://developers.openai.com/codex/guides/agents-md
- MCP: https://developers.openai.com/codex/mcp
- Customization: https://developers.openai.com/codex/concepts/customization
- Subagents: https://developers.openai.com/codex/concepts/subagents
- Agents SDK workflow with Codex MCP: https://developers.openai.com/codex/guides/agents-sdk

### MCP
- Intro: https://modelcontextprotocol.io/docs/getting-started/intro
- Security best practices: https://modelcontextprotocol.io/docs/tutorials/security/security_best_practices

### Supporting tools
- Tavily Agent Skills: https://docs.tavily.com/documentation/agent-skills
- Firecrawl: https://www.firecrawl.dev/
- GPT Researcher MCP: https://docs.gptr.dev/docs/gpt-researcher/mcp-server/getting-started
- open_deep_research: https://github.com/langchain-ai/open_deep_research
- PaperQA2: https://github.com/future-house/paper-qa
- Undermind: https://www.undermind.ai/
- Elicit: https://elicit.com/
- DeepWiki: https://cognition.ai/blog/deepwiki
- Qodo Context Engine: https://docs.qodo.ai/qodo-aware
- Sourcegraph Deep Search: https://sourcegraph.com/deep-search

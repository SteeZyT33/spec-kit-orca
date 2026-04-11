# Refinement Review — Product Surface Analysis

**Date**: 2026-04-11
**Target commit**: `d70ca5e` (post PR #21, `main` at the time of review)
**Source**: External structured review via GPT Pro, run against a repomix
snapshot of `main`. Imported verbatim from session notes on 2026-04-11.
**Reviewer lens**: product-surface and architectural heaviness, not
implementation correctness.

---

## Purpose

This is the first entry in `docs/refinement-reviews/`. These reviews are
deliberately separate from specs and roadmap docs:

- a **spec** documents what Orca intends to do
- the **roadmap** documents when
- a **refinement review** asks whether the product surface and architecture
  are still the right shape given what has shipped

They are meant to be occasional and structured, not continuous. Each review
should be timestamped, attributed, and preserved verbatim — later operators
need to compare "what the reviewer thought then" against "what the repo
looks like now" without re-deriving the lens.

This first review establishes the five-section framework every subsequent
refinement review should use. See **Template Usage** at the end of this
file for the structure and how to run another review in the same shape.

---

## Review Framework

The review below structures its analysis in five sections. Later refinement
reviews should reuse the same headers so findings are comparable over time:

1. **Thesis** — what architectural argument is the system actually making?
2. **Differentiators** — where is the argument load-bearing versus derivative?
3. **Heaviness** — where does the architecture create more cognitive cost
   than shipped value?
4. **Recommendations** — what should be kept, simplified, demoted, or finished?
5. **Judgment** — a short final call.

---

## Review

### Thesis

Orca has a real architectural thesis, and it is a good one: durable
workflow primitives first, coordination second, orchestration last. The
roadmap explicitly says Orca now has brainstorm memory, flow-state, split
review artifacts, context handoffs, capability packs, Matriarch, and Evolve,
and it warns not to make orchestration the foundation. It also says the
"stable center" is brainstorming and micro-spec intake, assignment and
review workflow, durable repo-backed state, optional capability boundaries,
and conservative multi-lane supervision.

### Differentiators

**1. Repo-backed continuity.** Most workflow repos stop at "specs plus
tasks plus maybe agent assignment." Orca is trying to make continuity
itself durable: early ideation, current stage, review state, handoffs,
lane state, and adoption history all live in the repo instead of in chat
memory. The README's built-in systems list makes that explicit, and the
flow-state spec reinforces that the intended model is computed from
artifacts rather than a hidden state machine.

**2. Micro-spec as a real escape hatch for small work.** The normal
workflow is still heavyweight, but the README says smaller work can go
through `micro-spec` rather than forcing the full feature-spec path, and
the command contract says `micro-spec` is a bounded path with a durable
record, mini-plan, declared verification mode, code review, and promotion
rules when scope grows. The "small work" problem is usually an
afterthought in workflow systems; Orca built the escape hatch on purpose.

**3. Matriarch's supervisory posture.** The command docs are very clear
that Matriarch is *"a supervisor, not a hidden swarm runtime"* — it owns
lane registration, dependencies, mailbox/report queues, and readiness
aggregation, while explicitly not owning feature-stage semantics, review
semantics, or uncontrolled execution. That boundary discipline is good.
A lot of multi-agent orchestration systems collapse into "smart swarm
manager" mush; Orca is trying not to.

### Heaviness

Where it becomes too heavy:

**1. Truth fragmentation.** The README surfaces brainstorm memory, Evolve
inventory, worktree metadata, flow-state, context handoffs, capability
packs, and Matriarch runtime as distinct systems, on top of the command
stack itself. That is powerful, but it also means Orca can start to feel
like a workflow OS for maintaining workflow state rather than a tool for
shipping software. The moment a user has to mentally track which fact
lives in brainstorm memory versus flow-state versus handoff docs versus
review artifacts versus Matriarch, the system becomes cognitively
expensive.

**2. The meta-architecture layer.** `004-orca-workflow-system-upgrade`
explicitly chose an umbrella spec plus child subsystem specs, because it
wanted system-level architecture, dependency order, integration contracts,
and implementation waves in one place. That is coherent, but it is also
one more artifact layer to maintain, and the spec itself admits that as a
con. This kind of structure is valuable when several agents or
collaborators really are working in parallel. It is less valuable when one
operator mostly needs the shortest correct path to execute a bounded
change.

**3. Capability packs, slightly ahead of proven need.** The capability-packs
plan says the goal is to stop the core command set from absorbing every
subsystem concern, and to do that with a simpler composition model than
Spex traits; but it also describes the feature as architecture and
configuration first, with a helper so packs are inspectable in practice.
That is exactly the kind of thing that can become elegant over-abstraction:
a clean answer to future growth before enough present pain has accumulated.
It may turn out to be right, but it is the first thing worth scrutinizing
for "system-building energy outrunning operator value."

**4. Evolve is clever, but unmistakably meta.** Its contracts say Orca
should capture harvested ideas as durable entries, assign adoption
decisions, map them into Orca targets, and update them as work advances;
the brainstorm says the point is to avoid letting useful ideas drift in
chat history. That is intellectually strong, but unless the operator is
actively harvesting external systems every week, it is not as core to
daily operator value as making the main execution loop brutally smooth.
It reads like a system for improving the system, not using the system.

**5. The repo already feels complexity pressure in its own docs.** The
README style guide says the README must not become a spec inventory, task
ledger, or internal planning dump, and it literally says to "simplify
aggressively" and cut internal planning residue. That is a strong signal.
Repos do not usually need a style guide this explicit unless the internal
architecture has already become more elaborate than the external product
story.

**6. Sequencing risk.** The roadmap/checkpoint doc says Checkpoint C is
still only partial because `010-orca-matriarch` is merged while
`009-orca-yolo` remains pending as the optional single-lane worker
beneath it. That is not a contradiction, but it does mean coordination
and supervision have grown faster than the core automated execution
layer. That can be fine for self-usage, but from a product perspective
it can look like the control plane is more mature than the thing it is
supervising.

### Recommendations

**Keep the core thesis.** Repo-backed primitives, micro-spec, review
discipline, and conservative lane supervision are the good part. Do not
cut them.

**Simplify the default surface area.** Make the public product story
four things only: intake, execution state, review, and lanes. Concretely,
that means "brainstorm or micro-spec," "flow-state," "review," and
"Matriarch when parallel work exists." Everything else should read as
implementation detail or advanced mode, not as a first-class thing every
user has to learn on day one.

**Make flow-state the visible aggregator of truth.** The flow-state spec
already says artifacts are primary truth and that persisted metadata must
stay secondary. Lean into that harder. The user should usually ask Orca
one question: *"where is this feature now?"* Then flow-state can point to
the underlying review artifact, handoff, or lane record. That is how to
avoid making every subsystem feel like a separate mental model.

**Demote capability packs from central product positioning** unless users
are actively toggling them. They can remain a real internal mechanism,
but they should not become another noun the average user must understand
before the workflow makes sense. The capability-pack docs themselves say
core commands must remain understandable and that the model should stay
simpler than traits; interpret that aggressively and keep packs mostly
backstage for now.

**Demote Evolve in the mainline narrative.** Keep it, because it is a
smart internal discipline, but present it as an advanced maintainer
subsystem rather than part of the operator's default mental model. Right
now it is one of the built-in systems in the README. Move it mentally
into "maintainer machinery," alongside internal architecture hygiene.

**Keep Matriarch, but only as an explicit advanced mode.** The docs
already support this reading: it is for when you need one durable view
over multiple active specs and lanes, not for ordinary single-lane work.
Preserve that and resist any temptation to make it feel like the default
front door.

**Finish the everyday execution story before adding more meta-layers.**
The roadmap says the remaining major runtime work is `orca-yolo`, and
Checkpoint C says the `009` worker relationship is still incomplete. That
strongly suggests the next highest-leverage move is not more governance,
adoption, or composition machinery. It is making the single-lane loop
feel excellent.

### Judgment

Orca is genuinely differentiated where it turns workflow continuity into
durable repo state and where it refuses to make orchestration the
foundation. It becomes too heavy where that discipline turns into too
many named subsystems competing for mindshare. The right move is not to
simplify the architecture by deleting the hard-won primitives. It is to
simplify the product surface by making most of those primitives
subordinate to one visible flow: intake, current state, review, and
optional lane supervision.

---

## Derived Action Items

Mapping each recommendation to a concrete deliverable against the current
repo. None of these are emergencies; they are refinement work to run
**after** the outstanding cleanup PR (deployment-readiness fixes) lands.

### Product-surface simplification

- **`README.md`** — collapse the "Built In Commands" and "Built In Systems"
  tables into a single four-concept story: intake (`brainstorm` /
  `micro-spec`), state (`flow-state`), review, lanes (Matriarch for
  parallel work only). Move the current system table into an "Advanced"
  or "Internals" section below the fold.
- **`README.md`** — flow-state should answer *"where is this feature now?"*
  as the default operator question. Add one example of that usage in the
  Basic Workflow section.
- **`README.md`** — demote capability packs to an "Internals" note unless
  the reader is opting into pack configuration.
- **`README.md`** — demote Evolve from Built In Systems to a "Maintainer
  Subsystems" section (or remove from the README entirely and link from
  `docs/`). The Evolve inventory keeps running; only the README framing
  changes.

### Flow-state as aggregator

- **`src/speckit_orca/flow_state.py`** — audit whether the CLI surface
  exposes a single "where is this feature?" entrypoint that takes a spec
  id and returns the current stage, the review gate status, and a pointer
  to the next artifact. If not, that is the tightest product-surface win
  available, and it is a small amount of code because `flow_state.py`
  already computes all the underlying pieces.
- **`commands/`** — verify the command prompts point operators at
  flow-state output rather than at raw review or handoff files when asked
  "what is going on with this feature?"

### Sequencing

- **`009-orca-yolo`** — runtime implementation is the highest-leverage
  next move per this review's judgment. The current cleanup PR should not
  expand into 009 work, but the next feature PR after cleanup should.
  Size estimate is days, not weeks (comparable to 011 evolve at 783 LOC
  or 007 handoffs at 633 LOC; the spec is already tight from PR #16).

### Matriarch positioning

- **`README.md`** and **`commands/matriarch.md`** — confirm framing is
  consistently "advanced mode for parallel work" and that no example
  suggests it is the default front door for single-feature work.

### Things to explicitly NOT do

- Do not delete capability packs, Evolve, or any of the durable primitives.
  The review says to demote them in the narrative, not remove them from
  the runtime.
- Do not rewrite `004-orca-workflow-system-upgrade` even though the
  reviewer called out meta-architecture heaviness. That spec is the
  durable record of the upgrade program and its retrospective cost is
  known. Changing it now would lose the program-level record.
- Do not touch the capability-packs runtime while moving it backstage in
  the narrative. It continues to work; users just do not need to know
  about it on day one.

---

## Template Usage

To run another refinement review later, reuse this file's shape. The
minimum inputs are:

1. **A repo snapshot.** A `repomix` pack of `main` at a known commit is
   sufficient. Include the commit SHA in the header of the review file.
2. **The current README and roadmap.** These are the primary product
   surface; the reviewer needs to see how Orca presents itself.
3. **Any open specs that are spec-only.** Give the reviewer enough
   context to distinguish "shipped" from "contract-only."
4. **A target reviewer with architectural judgment.** This review came
   from GPT Pro with a specific product-surface lens; other reviewers can
   be used as long as the five-section framework is preserved.

The review file lives in `docs/refinement-reviews/<YYYY-MM-DD>-<slug>.md`.
Header must carry date, target commit SHA, source, and reviewer lens.
Preserve the review verbatim — later comparisons need the original words,
not a summarized version. Derived action items can evolve after the
initial import, but the review body itself stays frozen.

### When to run one

Refinement reviews are not continuous. Good triggers:

- after a wave of specs merges and before the next wave is scoped
- when the repo is about to take on a large new surface area (new CLI,
  new subsystem, new integration)
- when the README starts feeling harder to maintain than the code
- annually, as a forcing function, if none of the above has triggered

Bad triggers:

- every PR
- after every contract change
- to validate a decision that has already been made

### What the framework is *not* for

- code review
- security review
- performance review
- test-coverage audit
- deployment-readiness audit

Those reviews already have their own lenses. Refinement reviews are
specifically about product surface and architectural heaviness. Running
one on a spec that has not yet shipped is also out of scope — refinement
reviews look at what *has* landed, not at forward design work.

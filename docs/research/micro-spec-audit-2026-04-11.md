# Audit: Existing `micro-spec` Surface (2026-04-11)

**Purpose**: Input for `013-spec-lite` plan. The 013 brainstorm's open
question #5 was *"are there any existing `micro-spec` records in the
repo that need migration?"* — this audit answers that and also maps
every file that references `micro-spec` as vocabulary, so the 013 plan
knows the full rename scope.

**Scope**: Static grep-and-find over the main branch at `4f76a66`.

## 1. Existing records on disk

**Count: 0.**

No files or directories matching `*micro*` exist under `.specify/`.
There are no in-flight `micro-spec` records to migrate, no data to
port, no legacy artifacts to preserve.

**Implication for 013 plan**: skip the migration-tool step entirely.
`013-spec-lite` is a **purely forward-looking** rename. The breaking
change cost is just vocabulary, not data.

## 2. Vocabulary references (16 files)

These are the files that mention `micro-spec` and will need updates
when 013 lands. Grouped by update type:

### Command prompt (retire)

- `commands/micro-spec.md` — 4848 bytes, Apr 8 snapshot. The
  command prompt itself. **Retired** in the 013 breaking wave,
  replaced by `commands/spec-lite.md`. Prompt rewrite is deferred
  per the same rule that governs 012 and 014.

### Command prompts that route to it (update)

- `commands/brainstorm.md` — the brainstorm command recommends
  `micro-spec` as a downstream option for bounded work. Update to
  `spec-lite`.

### Spec vocabulary (update in place)

- `specs/002-brainstorm-memory/contracts/brainstorm-command.md` —
  contract naming `micro-spec` as a routing target. Update to
  `spec-lite`.
- `specs/005-orca-flow-state/brainstorm.md` — historical brainstorm.
  **Leave as-is** (historical record) unless it names an
  operational expectation that's still load-bearing.
- `specs/009-orca-yolo/spec.md` — yolo spec mentions `micro-spec` as
  a valid start artifact for a yolo run. Update to acknowledge both
  `spec-lite` and full spec as start artifacts. (But see note on 009
  scope: 014 yolo runtime intentionally excludes spec-lite in v1, so
  this may be a no-op wording tweak.)
- `specs/009-orca-yolo/brainstorm.md` — historical brainstorm.
  **Leave as-is**.
- `specs/013-spec-lite/brainstorm.md` — the brainstorm proposing the
  rename. Already uses both vocabularies intentionally.

### Repo-level docs (update)

- `README.md` — touched by PR #24's four-concept workflow section.
  Update to `spec-lite` in the same breaking wave. Coordinate with
  013's plan to avoid double-updating.
- `extension.yml` — extension metadata may register `micro-spec` as
  a command. Needs a look — if it registers the command name, update
  to `spec-lite`.
- `src/speckit_orca/assets/speckit-orca-main.sh` — installer script
  references `micro-spec` somewhere (probably in help text or
  command listing). Needs a look. Update to `spec-lite`.

### Roadmap / design docs (update)

- `docs/orca-roadmap.md` — roadmap narrative mentions `micro-spec`.
  Update to `spec-lite` when 013 ships, same breaking wave as
  README.
- `docs/refinement-reviews/2026-04-11-product-surface.md` — GPT Pro
  refinement review. **Leave as-is** — it is a frozen review
  document by design, not a live spec. The `micro-spec` reference
  there is historical context.
- `docs/worktree-protocol.md` — protocol doc. Needs a look — if the
  reference is just vocabulary, update. If it's a load-bearing
  reference to a specific `micro-spec` behavior, plan more carefully.

### Legacy v1.4 planning docs (leave or archive)

- `docs/orca-v1.4-design.md`
- `docs/orca-v1.4-decisions.md`
- `docs/orca-v1.4-execution-plan.md`

These are the v1.4 planning snapshot docs. **Leave as-is** — they
are a frozen historical record. Adding "(renamed to spec-lite after
013)" as a pointer note would be nice but is not required.

## 3. Summary for 013 plan

| Category | Count | Action |
|---|---|---|
| Existing records to migrate | 0 | None |
| Files to retire | 1 | `commands/micro-spec.md` |
| Files to update vocabulary | ~8-10 | Rename `micro-spec` → `spec-lite` |
| Files to leave frozen | ~5-6 | Historical records, brainstorms, refinement reviews |

The 013 plan's "Rollout" section in the brainstorm proposed atomic
breaking change. This audit confirms that's realistic: there's no
data migration tool needed, the rename is purely vocabulary, and the
update set is bounded to <15 files.

**Recommendation for 013 plan**: group the rename into three commits:

1. **Runtime / prompts commit** — retire `commands/micro-spec.md`,
   create `commands/spec-lite.md`, update `commands/brainstorm.md`
   routing references, update `specs/002-brainstorm-memory/contracts/brainstorm-command.md`,
   update `src/speckit_orca/assets/speckit-orca-main.sh`,
   update `extension.yml` if it registers the command.
2. **Spec docs commit** — update `specs/009-orca-yolo/spec.md` to
   acknowledge spec-lite as a valid start artifact (or leave the
   reference since 014 runtime excludes spec-lite in v1 anyway).
3. **Repo-level docs commit** — update `README.md` and
   `docs/orca-roadmap.md`. `docs/worktree-protocol.md` gets
   evaluated during this commit — if it's vocabulary-only, update;
   if load-bearing, plan more carefully.

Legacy v1.4 design docs and the 2026-04-11 refinement review are
explicitly out of scope.

## 4. Open question resolved

**013 brainstorm open question #5**: *"Audit — are there existing
micro-spec records in the repo that need migration?"*

**Answer: No records exist. Migration scope is zero.**

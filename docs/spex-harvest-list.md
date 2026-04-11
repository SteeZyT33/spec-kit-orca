# Spex Harvest List (Retired)

This document has been retired. Its contents are now tracked durably in the
Orca Evolve inventory rather than as ad-hoc prose.

## Where the harvest lives now

- Overview: [`.specify/orca/evolve/00-overview.md`](../.specify/orca/evolve/00-overview.md)
- Entries: [`.specify/orca/evolve/entries/`](../.specify/orca/evolve/entries/)
- Spec: [`specs/011-orca-evolve/spec.md`](../specs/011-orca-evolve/spec.md)

Every spex-derived pattern that mattered in the original list has a durable
Evolve entry with source attribution, adoption decision, rationale, and target
mapping. New harvest items go through the Evolve CLI rather than this file:

```bash
uv run python -m speckit_orca.evolve --root . create --help
uv run python -m speckit_orca.evolve --root . list
```

## Why this was retired

Keeping a parallel prose inventory alongside the durable Evolve store created
two sources of truth. The prose version was guaranteed to rot as adoption
decisions changed. Retiring it makes the durable store unambiguously
authoritative.

# Spex Adoption Notes (Retired)

This document has been retired. The adoption posture it captured — borrow
aggressively from spex while resisting Claude-specific machinery — is now
encoded in the Orca Evolve inventory and in the Orca specs themselves.

## Where the adoption record lives now

- Overview: [`.specify/orca/evolve/00-overview.md`](../.specify/orca/evolve/00-overview.md)
- Entries: [`.specify/orca/evolve/entries/`](../.specify/orca/evolve/entries/)
- Evolve spec: [`specs/011-orca-evolve/spec.md`](../specs/011-orca-evolve/spec.md)

The four original adoption guardrails — one subsystem at a time, runtime
before automation, keep command surface stable, adopt concepts not branding —
are now reflected in the durable per-entry decision vocabulary
(`direct-take` | `adapt-heavily` | `defer` | `reject`) and the adoption-scope
field. The "what to steal first / later / not at all" partitioning is
captured by each entry's status and decision rather than by a prose bucket
list.

## Why this was retired

Keeping a parallel prose adoption document alongside the durable Evolve
store created two sources of truth. Retiring it makes the durable store
unambiguously authoritative. Future adoption decisions go through the
Evolve CLI:

```bash
uv run python -m speckit_orca.evolve --root . create --help
uv run python -m speckit_orca.evolve --root . list
```

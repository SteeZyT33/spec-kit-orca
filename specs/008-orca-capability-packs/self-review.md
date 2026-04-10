# Self-Review: Orca Capability Packs

## Outcome

The feature is in good shape after one real correction loop.

What went well:

- The implementation stayed small and inspectable: one deterministic helper,
  one example manifest, and contract/doc alignment around the runtime surface.
- The pack model is materially simpler than Spex traits while still being
  usable in practice.
- Review caught actual runtime bugs early enough to fix them before merge.

## Issues Found And Fixed During Review

- Corrected the `flow-state` heuristic so it only enables when `specs/` exists.
- Enforced the `owned_behaviors` validation rule from the data model.
- Turned invalid `always-on` disable overrides into validation failures.
- Made scaffold failure explicit when the template asset is missing.
- Updated stale extension repository/homepage URLs.
- Aligned `src/speckit_orca/__init__.py` version with `1.4.0`.
- Added targeted unit coverage for capability-pack resolution and validation.

## Remaining Risk

The main residual gap is repo-level test ergonomics: direct `pytest` invocation
still needs `PYTHONPATH=src`. That is not introduced by `008`, but it affects
how naturally the new tests run outside the packaged helper path.

## Verification Used

- `PYTHONPATH=src uv run pytest tests/test_capability_packs.py tests/test_brainstorm_memory.py`
- `uv run python -m py_compile src/speckit_orca/capability_packs.py`
- `uv run python -m speckit_orca.capability_packs list --root .`
- `uv run python -m speckit_orca.capability_packs validate --root .`
- `uv run --with build python -m build`
- `git diff --check`

## Assessment

- Scope discipline: strong
- Runtime simplicity: strong
- Contract alignment: strong after fixes
- Review effectiveness: strong because the first external pass found real bugs
- Merge readiness: yes, with the pytest path note recorded separately from the feature itself

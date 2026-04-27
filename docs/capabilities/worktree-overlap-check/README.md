# worktree-overlap-check

Detects path conflicts between active worktrees and against proposed writes. Pure Python; no git invocation, no LLM. Caller passes pre-collected worktree info.

## Use case

Perf-lab's `lease.sh` shells out here instead of reimplementing overlap detection. Returns `safe: false` when any two worktrees claim the same path, or when a `proposed_writes` entry is already claimed.

## Path matching

Exact path equality OR directory-prefix containment. `src/foo/` claims `src/foo/bar.py`. Comparison uses POSIX path semantics (`PurePosixPath`).

## Input
See `schema/input.json`. Each `worktree` has `path` (required), optional `branch`, `feature_id`, `claimed_paths`.

## Output
See `schema/output.json`. `conflicts[]` lists pair-wise overlaps; `proposed_overlaps[]` lists each proposed write blocked by an existing claim. `safe` is true when both lists are empty.

## CLI

`orca-cli worktree-overlap-check` (reads JSON from stdin or `--input <file>`)

## Library

`from orca.capabilities.worktree_overlap_check import worktree_overlap_check, WorktreeOverlapInput, WorktreeInfo`

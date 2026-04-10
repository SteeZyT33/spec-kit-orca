# Contract: Orchestration Policies

## Purpose

Define the minimum policy surface controlling how `orca-yolo` runs.

## Required Policies

- ask level or intervention mode
- start-from behavior
- resume behavior
- worktree behavior
- bounded retry behavior
- PR completion behavior

## Behavior

- Ask policy must control when `orca-yolo` pauses for human input.
- Start-from behavior must reject incompatible stage requests when prerequisites
  are missing.
- Retry behavior must be bounded and must not create infinite fix loops.
- PR completion must remain an explicit policy choice rather than an implied
  side effect.

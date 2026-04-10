# Contract: Run Stage Model

## Purpose

Define the minimum stage vocabulary `orca-yolo` uses for full-cycle workflow
execution.

## Required Stages

- brainstorm
- specify
- plan
- tasks
- implement
- self-review
- code-review
- cross-review
- pr-ready

## Optional Final Stage

- pr-create

## Behavior

- Stages must align with existing Orca workflow language where possible.
- `orca-yolo` must not skip required prerequisite stages unless the user starts
  from a later stage with the needed durable artifacts already present.
- Every stage transition must be inspectable through durable run state.

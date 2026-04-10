# Contract: Yolo Run State

## Purpose

Define the minimum durable state `orca-yolo` needs to support resume, stop, and
final outcome reporting.

## Required Fields

- run id
- anchor artifact or feature reference
- current stage
- current outcome
- ask policy
- retry policy
- worktree policy
- linked artifact paths
- stop reason when not actively progressing

## Behavior

- Run state must be durable enough to support resume after session loss.
- Run state must prefer explicit artifact links over reconstructing context from
  chat history.
- Final run state must expose whether the run completed, paused, blocked,
  failed, or was canceled.

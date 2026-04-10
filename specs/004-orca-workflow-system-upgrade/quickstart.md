# Quickstart: Orca Workflow System Upgrade

## Goal

Validate that the application upgrade program is coherent enough to guide later
parallel implementation.

## Scenario 1: Child inventory exists

1. Inspect the upgrade program artifacts.
2. Verify every major subsystem from the repomix harvest exists as a child spec.

## Scenario 2: Wave order is dependency-driven

1. Inspect the implementation waves contract.
2. Verify wave sequencing follows actual prerequisites rather than spec number.

## Scenario 3: `orca-yolo` is downstream

1. Inspect the upgrade checkpoints and `009` role.
2. Verify `orca-yolo` is gated behind memory, state, review, and handoff
   readiness.

## Scenario 4: Parallel implementation is safe

1. Compare child specs against the subsystem integration contract.
2. Verify the child specs can be assigned in parallel without hidden subsystem
   assumptions.

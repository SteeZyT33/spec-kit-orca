# Contract: Review Summary Index

## Purpose

`review.md` remains the human-facing entrypoint for review status, but no longer
acts as the only durable stage artifact.

## Required Contents

- feature identification
- list of available stage artifacts
- high-level review status per stage
- latest unresolved blockers
- latest PR/post-merge state when applicable

## Constraints

- `review.md` should summarize and point to stage artifacts
- it should not duplicate every detail if that creates drift
- a later system should be able to discover stage completion from stage
  artifacts directly and use `review.md` as the overview layer

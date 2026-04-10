# Contract: Pack Activation

## Purpose

Define how Orca represents whether a capability pack is active.

## Activation Modes

- `always-on`
- `config-enabled`
- `experimental-only`

## Rules

- experimental packs must never activate silently
- core behavior should not require pack activation to remain understandable
- pack activation should be inspectable from repo artifacts or config

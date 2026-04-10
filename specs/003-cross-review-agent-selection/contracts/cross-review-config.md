# Contract: Cross-Review Configuration

## Canonical Shape

```yaml
crossreview:
  agent: null
  model: null
  effort: "high"
  ask_on_ambiguous: true
  remember_last_success: true
```

## Compatibility Rules

- `crossreview.agent` is canonical
- `crossreview.harness` remains accepted temporarily as a legacy alias
- if both are present, `crossreview.agent` wins

## Behavioral Meaning

- `agent`: preferred explicit reviewer
- `model`: adapter-specific model override when supported
- `effort`: adapter-specific reasoning effort when supported
- `ask_on_ambiguous`: whether Orca may ask instead of auto-selecting when the
  choice materially affects trust
- `remember_last_success`: whether prior successful reviewer memory may be used
  as advisory selection context

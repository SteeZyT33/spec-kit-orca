from __future__ import annotations

import json
from pathlib import Path

import pytest

from orca.core.errors import ErrorKind
from orca.capabilities.completion_gate import (
    CompletionGateInput,
    completion_gate,
)


@pytest.fixture
def feature_dir(tmp_path: Path) -> Path:
    d = tmp_path / "specs" / "001"
    d.mkdir(parents=True)
    return d


def test_plan_ready_pass(feature_dir):
    (feature_dir / "spec.md").write_text("# Example\n\nNo unclarified items.\n")
    result = completion_gate(CompletionGateInput(
        feature_dir=str(feature_dir),
        target_stage="plan-ready",
    ))
    assert result.ok
    assert result.value["status"] == "pass"
    assert result.value["blockers"] == []
    assert result.value["stale_artifacts"] == []
    # gates_evaluated reports each gate's outcome
    gate_names = [g["gate"] for g in result.value["gates_evaluated"]]
    assert "spec_exists" in gate_names
    assert "no_unclarified" in gate_names


def test_plan_ready_blocked_when_spec_missing(feature_dir):
    result = completion_gate(CompletionGateInput(
        feature_dir=str(feature_dir),
        target_stage="plan-ready",
    ))
    assert result.ok
    assert result.value["status"] == "blocked"
    assert "spec_exists" in result.value["blockers"]


def test_plan_ready_blocked_on_unclarified(feature_dir):
    (feature_dir / "spec.md").write_text("# Example\n\n[NEEDS CLARIFICATION] should we...\n")
    result = completion_gate(CompletionGateInput(
        feature_dir=str(feature_dir),
        target_stage="plan-ready",
    ))
    assert result.ok
    assert result.value["status"] == "blocked"
    assert "no_unclarified" in result.value["blockers"]


def test_implement_ready_blocked_without_plan(feature_dir):
    (feature_dir / "spec.md").write_text("# Example\n")
    result = completion_gate(CompletionGateInput(
        feature_dir=str(feature_dir),
        target_stage="implement-ready",
    ))
    assert result.ok
    assert result.value["status"] == "blocked"
    assert "plan_exists" in result.value["blockers"]


def test_implement_ready_pass_with_spec_and_plan(feature_dir):
    (feature_dir / "spec.md").write_text("# Spec\n")
    (feature_dir / "plan.md").write_text("# Plan\n")
    result = completion_gate(CompletionGateInput(
        feature_dir=str(feature_dir),
        target_stage="implement-ready",
    ))
    assert result.ok
    assert result.value["status"] == "pass"


def test_pr_ready_requires_tasks(feature_dir):
    (feature_dir / "spec.md").write_text("# Spec\n")
    (feature_dir / "plan.md").write_text("# Plan\n")
    result = completion_gate(CompletionGateInput(
        feature_dir=str(feature_dir),
        target_stage="pr-ready",
    ))
    assert result.ok
    assert result.value["status"] == "blocked"
    assert "tasks_exists" in result.value["blockers"]


def test_merge_ready_requires_ci_green(feature_dir):
    """merge-ready needs evidence.ci_green=true even when all artifacts exist."""
    (feature_dir / "spec.md").write_text("# Spec\n")
    (feature_dir / "plan.md").write_text("# Plan\n")
    (feature_dir / "tasks.md").write_text("# Tasks\n")
    # No evidence.ci_green
    result = completion_gate(CompletionGateInput(
        feature_dir=str(feature_dir),
        target_stage="merge-ready",
    ))
    assert result.ok
    assert result.value["status"] == "blocked"
    assert "ci_green" in result.value["blockers"]


def test_merge_ready_pass_with_ci_green(feature_dir):
    (feature_dir / "spec.md").write_text("# Spec\n")
    (feature_dir / "plan.md").write_text("# Plan\n")
    (feature_dir / "tasks.md").write_text("# Tasks\n")
    result = completion_gate(CompletionGateInput(
        feature_dir=str(feature_dir),
        target_stage="merge-ready",
        evidence={"ci_green": True},
    ))
    assert result.ok
    assert result.value["status"] == "pass"


def test_stale_takes_precedence_over_blocked(feature_dir):
    """If evidence.stale_artifacts is non-empty, status is 'stale' even if other gates pass."""
    (feature_dir / "spec.md").write_text("# Spec\n")
    result = completion_gate(CompletionGateInput(
        feature_dir=str(feature_dir),
        target_stage="plan-ready",
        evidence={"stale_artifacts": ["spec.md"]},
    ))
    assert result.ok
    assert result.value["status"] == "stale"
    assert result.value["stale_artifacts"] == ["spec.md"]
    # blockers may or may not be populated; status reflects staleness


def test_invalid_target_stage(feature_dir):
    result = completion_gate(CompletionGateInput(
        feature_dir=str(feature_dir),
        target_stage="bogus",
    ))
    assert not result.ok
    assert result.error.kind == ErrorKind.INPUT_INVALID


def test_missing_feature_dir():
    result = completion_gate(CompletionGateInput(
        feature_dir="/nonexistent",
        target_stage="plan-ready",
    ))
    assert not result.ok
    assert result.error.kind == ErrorKind.INPUT_INVALID


def test_gates_evaluated_includes_all_gates_for_stage(feature_dir):
    """gates_evaluated reports each gate's outcome, even for blocked stages."""
    (feature_dir / "spec.md").write_text("# Spec\n")
    result = completion_gate(CompletionGateInput(
        feature_dir=str(feature_dir),
        target_stage="merge-ready",
    ))
    assert result.ok
    gate_names = [g["gate"] for g in result.value["gates_evaluated"]]
    # merge-ready inherits all prior stages' gates
    assert "spec_exists" in gate_names
    assert "no_unclarified" in gate_names
    assert "plan_exists" in gate_names
    assert "tasks_exists" in gate_names
    assert "ci_green" in gate_names


def test_output_validates_against_schema(feature_dir):
    pytest.importorskip("jsonschema")
    import jsonschema
    schema_path = (
        Path(__file__).resolve().parents[2]
        / "docs" / "capabilities" / "completion-gate" / "schema" / "output.json"
    )
    schema = json.loads(schema_path.read_text())

    (feature_dir / "spec.md").write_text("# Spec\n")
    result = completion_gate(CompletionGateInput(
        feature_dir=str(feature_dir),
        target_stage="plan-ready",
    ))
    assert result.ok
    jsonschema.validate(result.value, schema)

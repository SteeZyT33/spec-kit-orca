"""Tests for the multi-SDD adapter interface (016 Phase A).

Phase A: interface and dataclasses only. No concrete adapter yet.
Phase 1 invariant: zero user-visible behavior change in Orca.
"""

from __future__ import annotations

from dataclasses import fields
from pathlib import Path

import pytest


# ---------------------------------------------------------------------------
# Phase A: Dataclasses
# ---------------------------------------------------------------------------


class TestFeatureHandle:
    def test_feature_handle_fields(self):
        from speckit_orca.sdd_adapter import FeatureHandle

        field_map = {f.name: f.type for f in fields(FeatureHandle)}
        expected = {"feature_id", "display_name", "root_path", "adapter_name"}
        assert set(field_map.keys()) == expected

    def test_feature_handle_construction(self):
        from speckit_orca.sdd_adapter import FeatureHandle

        handle = FeatureHandle(
            feature_id="009-orca-yolo",
            display_name="Orca YOLO",
            root_path=Path("/tmp/specs/009-orca-yolo"),
            adapter_name="spec-kit",
        )
        assert handle.feature_id == "009-orca-yolo"
        assert handle.adapter_name == "spec-kit"


class TestNormalizedTask:
    def test_normalized_task_fields(self):
        from speckit_orca.sdd_adapter import NormalizedTask

        field_names = {f.name for f in fields(NormalizedTask)}
        assert field_names == {"task_id", "text", "completed", "assignee"}

    def test_normalized_task_construction(self):
        from speckit_orca.sdd_adapter import NormalizedTask

        task = NormalizedTask(
            task_id="T001", text="Write tests", completed=False, assignee=None
        )
        assert task.task_id == "T001"
        assert task.completed is False
        assert task.assignee is None


class TestStageProgress:
    def test_stage_progress_fields(self):
        from speckit_orca.sdd_adapter import StageProgress

        field_names = {f.name for f in fields(StageProgress)}
        assert field_names == {"stage", "status", "evidence_sources", "notes"}

    def test_stage_progress_construction(self):
        from speckit_orca.sdd_adapter import StageProgress

        progress = StageProgress(
            stage="specify",
            status="complete",
            evidence_sources=["/tmp/specs/009/spec.md"],
            notes=[],
        )
        assert progress.stage == "specify"
        assert progress.status == "complete"


class TestNormalizedArtifacts:
    def test_normalized_artifacts_fields(self):
        from speckit_orca.sdd_adapter import NormalizedArtifacts

        field_names = {f.name for f in fields(NormalizedArtifacts)}
        expected = {
            "feature_id",
            "feature_dir",
            "artifacts",
            "tasks",
            "task_summary_data",
            "review_evidence",
            "linked_brainstorms",
            "worktree_lanes",
            "ambiguities",
            "notes",
        }
        assert field_names == expected


# ---------------------------------------------------------------------------
# Phase A: Abstract Base Class
# ---------------------------------------------------------------------------


class TestSddAdapterABC:
    def test_sdd_adapter_is_abstract(self):
        from speckit_orca.sdd_adapter import SddAdapter

        with pytest.raises(TypeError):
            SddAdapter()  # type: ignore[abstract]

    def test_incomplete_subclass_still_abstract(self):
        from speckit_orca.sdd_adapter import SddAdapter

        class Incomplete(SddAdapter):
            @property
            def name(self) -> str:
                return "incomplete"

            def detect(self, repo_root: Path) -> bool:
                return False

            # Missing list_features, load_feature, compute_stage, id_for_path

        with pytest.raises(TypeError):
            Incomplete()  # type: ignore[abstract]

    def test_complete_subclass_can_instantiate(self):
        from speckit_orca.sdd_adapter import (
            FeatureHandle,
            NormalizedArtifacts,
            SddAdapter,
            StageProgress,
        )

        class Stub(SddAdapter):
            @property
            def name(self) -> str:
                return "stub"

            def detect(self, repo_root: Path) -> bool:
                return False

            def list_features(self, repo_root: Path) -> list[FeatureHandle]:
                return []

            def load_feature(
                self, handle: FeatureHandle
            ) -> NormalizedArtifacts:
                from speckit_orca.sdd_adapter import NormalizedArtifacts

                return NormalizedArtifacts(
                    feature_id=handle.feature_id,
                    feature_dir=handle.root_path,
                    artifacts={},
                    tasks=[],
                    task_summary_data={},
                    review_evidence=None,
                    linked_brainstorms=[],
                    worktree_lanes=[],
                    ambiguities=[],
                    notes=[],
                )

            def compute_stage(
                self, artifacts: NormalizedArtifacts
            ) -> list[StageProgress]:
                return []

            def id_for_path(self, path: Path) -> str | None:
                return None

        obj = Stub()
        assert isinstance(obj, SddAdapter)
        assert obj.name == "stub"

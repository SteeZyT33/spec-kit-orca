"""SDD Adapter interface for 016 multi-SDD-layer Phase 1.

Defines the adapter contract and normalized data shapes that let Orca
operate over multiple Spec-Driven Development repo formats. Phase 1
adds the interface and a spec-kit reference adapter without changing
any user-visible behavior.

Contracts:
  - SddAdapter: abstract base class. One adapter per SDD format.
  - FeatureHandle: opaque reference to a feature owned by an adapter.
  - NormalizedArtifacts: adapter-independent view of a feature's
    durable artifacts.
  - NormalizedTask: single task entry from the feature's task list.
  - StageProgress: one stage-row in the feature's progress model.

Later phases add concrete adapters (OpenSpec, BMAD, Taskmaster).
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class FeatureHandle:
    """Opaque handle to a feature discovered by an adapter.

    The handle is what callers pass back to `load_feature` and
    `compute_stage`. Different adapters may encode different semantics
    in `feature_id`; callers should treat it as a stable key, not parse it.
    """

    feature_id: str
    display_name: str
    root_path: Path
    adapter_name: str


@dataclass
class NormalizedTask:
    """A single task row normalized across SDD formats.

    Spec-kit stores tasks as `- [x] T001 [US1] [@agent] description`
    lines in tasks.md. Other formats (Taskmaster graph, OpenSpec
    proposals) normalize to this same shape.
    """

    task_id: str
    text: str
    completed: bool
    assignee: str | None


@dataclass
class StageProgress:
    """One stage's progress in the feature's lifecycle.

    The list of stages is adapter-specific. For spec-kit, this is the
    nine-stage model (brainstorm through pr-review). For other formats,
    the stage names and ordering differ; callers should not assume
    spec-kit semantics.
    """

    stage: str
    status: str
    evidence_sources: list[str]
    notes: list[str]


@dataclass
class NormalizedArtifacts:
    """Adapter-independent view of a feature's durable artifacts.

    This is the shape `flow_state.FeatureEvidence` gets built from in
    Phase 1. Phase 1 keeps `review_evidence` typed as `Any` so adapters
    can return the existing spec-kit ReviewEvidence object without
    forcing an immediate shape change. Later phases can tighten the
    type as the refactor stabilizes.
    """

    feature_id: str
    feature_dir: Path
    artifacts: dict[str, Path]
    tasks: list[NormalizedTask]
    task_summary_data: dict[str, Any]
    review_evidence: Any
    linked_brainstorms: list[Path]
    worktree_lanes: list[Any]
    ambiguities: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)


class SddAdapter(ABC):
    """Abstract base class for an SDD format adapter.

    One subclass per SDD format. Orca subsystems that used to parse
    spec-kit directly now go through an adapter instance. See
    specs/016-multi-sdd-layer/ for the full contract.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Stable identifier for this adapter (e.g. 'spec-kit')."""

    @abstractmethod
    def detect(self, repo_root: Path) -> bool:
        """Return True if this adapter recognizes the repo layout."""

    @abstractmethod
    def list_features(self, repo_root: Path) -> list[FeatureHandle]:
        """Return all features this adapter can see in the repo."""

    @abstractmethod
    def load_feature(self, handle: FeatureHandle) -> NormalizedArtifacts:
        """Load a feature's artifacts into the normalized shape."""

    @abstractmethod
    def compute_stage(
        self, artifacts: NormalizedArtifacts
    ) -> list[StageProgress]:
        """Compute per-stage progress from loaded artifacts."""

    @abstractmethod
    def id_for_path(self, path: Path) -> str | None:
        """Map a file path to a feature_id if it lives under one.

        Returns None if the path is not inside any feature this adapter
        manages.
        """

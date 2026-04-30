"""Protocol contract tests, parametrized over all host_layout implementations.

Each adapter must implement the same public surface; this file is the
canonical contract test. Adding a new adapter = parametrize it in.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from orca.core.host_layout import BareLayout, HostLayout


@pytest.fixture
def bare_repo(tmp_path: Path) -> Path:
    """A minimal repo with no spec system at all."""
    (tmp_path / "README.md").write_text("# bare\n")
    return tmp_path


def test_bare_layout_satisfies_protocol(bare_repo: Path) -> None:
    layout: HostLayout = BareLayout(repo_root=bare_repo)
    assert isinstance(layout.repo_root, Path)


def test_bare_layout_resolve_feature_dir(bare_repo: Path) -> None:
    layout = BareLayout(repo_root=bare_repo)
    fd = layout.resolve_feature_dir("001-example")
    assert fd == bare_repo / "docs" / "orca-specs" / "001-example"


def test_bare_layout_list_features_empty(bare_repo: Path) -> None:
    layout = BareLayout(repo_root=bare_repo)
    assert layout.list_features() == []


def test_bare_layout_list_features_after_creation(bare_repo: Path) -> None:
    (bare_repo / "docs" / "orca-specs" / "001-x").mkdir(parents=True)
    (bare_repo / "docs" / "orca-specs" / "002-y").mkdir(parents=True)
    layout = BareLayout(repo_root=bare_repo)
    assert sorted(layout.list_features()) == ["001-x", "002-y"]


def test_bare_layout_constitution_path_is_none(bare_repo: Path) -> None:
    layout = BareLayout(repo_root=bare_repo)
    assert layout.constitution_path() is None


def test_bare_layout_agents_md_path_default(bare_repo: Path) -> None:
    layout = BareLayout(repo_root=bare_repo)
    assert layout.agents_md_path() == bare_repo / "AGENTS.md"


def test_bare_layout_review_artifact_dir(bare_repo: Path) -> None:
    layout = BareLayout(repo_root=bare_repo)
    assert layout.review_artifact_dir() == bare_repo / "docs" / "orca-specs" / "_reviews"

"""Detection priority + override tests."""
from __future__ import annotations

from pathlib import Path

import pytest

from orca.core.host_layout import (
    BareLayout,
    OpenSpecLayout,
    SpecKitLayout,
    SuperpowersLayout,
    detect,
)


def test_detect_superpowers(tmp_path: Path) -> None:
    (tmp_path / "docs" / "superpowers" / "specs").mkdir(parents=True)
    layout = detect(tmp_path)
    assert isinstance(layout, SuperpowersLayout)


def test_detect_openspec(tmp_path: Path) -> None:
    (tmp_path / "openspec" / "changes").mkdir(parents=True)
    layout = detect(tmp_path)
    assert isinstance(layout, OpenSpecLayout)


def test_detect_spec_kit(tmp_path: Path) -> None:
    (tmp_path / ".specify").mkdir()
    layout = detect(tmp_path)
    assert isinstance(layout, SpecKitLayout)


def test_detect_bare(tmp_path: Path) -> None:
    layout = detect(tmp_path)
    assert isinstance(layout, BareLayout)


def test_detect_superpowers_wins_over_specify(tmp_path: Path) -> None:
    """When both .specify/ and docs/superpowers/specs/ exist (mid-migration),
    superpowers wins per priority order."""
    (tmp_path / ".specify").mkdir()
    (tmp_path / "docs" / "superpowers" / "specs").mkdir(parents=True)
    layout = detect(tmp_path)
    assert isinstance(layout, SuperpowersLayout)


def test_detect_openspec_wins_over_specify(tmp_path: Path) -> None:
    (tmp_path / ".specify").mkdir()
    (tmp_path / "openspec" / "changes").mkdir(parents=True)
    layout = detect(tmp_path)
    assert isinstance(layout, OpenSpecLayout)

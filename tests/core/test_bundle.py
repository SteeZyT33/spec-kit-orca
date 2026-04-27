from __future__ import annotations

from pathlib import Path

import pytest

from orca.core.bundle import ReviewBundle, BundleError, build_bundle


def test_build_bundle_from_paths(tmp_path: Path):
    f1 = tmp_path / "a.py"
    f1.write_text("print('a')\n")
    f2 = tmp_path / "b.py"
    f2.write_text("print('b')\n")

    bundle = build_bundle(
        kind="diff",
        target=[str(f1), str(f2)],
        feature_id="001-foo",
        criteria=["correctness"],
        context=[],
    )
    assert bundle.kind == "diff"
    assert bundle.feature_id == "001-foo"
    assert len(bundle.target_paths) == 2
    assert bundle.criteria == ("correctness",)


def test_build_bundle_rejects_unknown_kind(tmp_path: Path):
    with pytest.raises(BundleError, match="unknown kind"):
        build_bundle(kind="banana", target=[], feature_id=None, criteria=[], context=[])


def test_build_bundle_rejects_missing_path(tmp_path: Path):
    with pytest.raises(BundleError, match="not found"):
        build_bundle(
            kind="spec",
            target=[str(tmp_path / "nope.md")],
            feature_id=None,
            criteria=[],
            context=[],
        )


def test_bundle_hash_stable_across_calls(tmp_path: Path):
    f = tmp_path / "a.py"
    f.write_text("print('a')\n")
    b1 = build_bundle(kind="diff", target=[str(f)], feature_id=None, criteria=[], context=[])
    b2 = build_bundle(kind="diff", target=[str(f)], feature_id=None, criteria=[], context=[])
    assert b1.bundle_hash == b2.bundle_hash


def test_bundle_hash_changes_with_content(tmp_path: Path):
    f = tmp_path / "a.py"
    f.write_text("v1\n")
    b1 = build_bundle(kind="diff", target=[str(f)], feature_id=None, criteria=[], context=[])
    f.write_text("v2\n")
    b2 = build_bundle(kind="diff", target=[str(f)], feature_id=None, criteria=[], context=[])
    assert b1.bundle_hash != b2.bundle_hash


def test_build_bundle_rejects_missing_context(tmp_path: Path):
    f = tmp_path / "a.py"
    f.write_text("ok\n")
    with pytest.raises(BundleError, match="context not found"):
        build_bundle(
            kind="diff",
            target=[str(f)],
            feature_id=None,
            criteria=[],
            context=[str(tmp_path / "missing-context.md")],
        )


def test_bundle_hash_changes_with_feature_id(tmp_path: Path):
    f = tmp_path / "a.py"
    f.write_text("v1\n")
    b1 = build_bundle(kind="diff", target=[str(f)], feature_id="001", criteria=[], context=[])
    b2 = build_bundle(kind="diff", target=[str(f)], feature_id="002", criteria=[], context=[])
    assert b1.bundle_hash != b2.bundle_hash


def test_bundle_hash_changes_with_criteria(tmp_path: Path):
    f = tmp_path / "a.py"
    f.write_text("v1\n")
    b1 = build_bundle(kind="diff", target=[str(f)], feature_id=None, criteria=["a"], context=[])
    b2 = build_bundle(kind="diff", target=[str(f)], feature_id=None, criteria=["b"], context=[])
    assert b1.bundle_hash != b2.bundle_hash


def test_build_bundle_accepts_generator_inputs(tmp_path: Path):
    """Materialization fix: callers passing generators must work end-to-end."""
    f = tmp_path / "a.py"
    f.write_text("ok\n")
    bundle = build_bundle(
        kind="diff",
        target=(str(p) for p in [f]),
        feature_id=None,
        criteria=(c for c in ["correctness"]),
        context=(c for c in []),
    )
    assert bundle.target_paths == (Path(str(f)),)
    assert bundle.criteria == ("correctness",)

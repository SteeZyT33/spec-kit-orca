from __future__ import annotations

from orca.core.findings import Finding, Findings, Severity, Confidence


def test_finding_to_json_minimal():
    f = Finding(
        category="correctness",
        severity=Severity.HIGH,
        confidence=Confidence.HIGH,
        summary="Off-by-one in loop",
        detail="The range should be range(n+1) not range(n).",
        evidence=["src/foo.py:42"],
        suggestion="Use range(n+1)",
        reviewer="claude",
    )
    out = f.to_json()
    assert out["category"] == "correctness"
    assert out["severity"] == "high"
    assert out["confidence"] == "high"
    assert out["evidence"] == ["src/foo.py:42"]
    assert out["reviewer"] == "claude"
    assert "id" in out and len(out["id"]) == 16


def test_dedupe_id_stable_across_calls():
    base = dict(
        category="correctness",
        severity=Severity.HIGH,
        confidence=Confidence.HIGH,
        summary="Off-by-one in loop",
        detail="The range should be range(n+1) not range(n).",
        evidence=["src/foo.py:42"],
        suggestion="Use range(n+1)",
        reviewer="claude",
    )
    f1 = Finding(**base)
    f2 = Finding(**base)
    assert f1.dedupe_id() == f2.dedupe_id()


def test_dedupe_id_ignores_reviewer_and_confidence():
    base = dict(
        category="correctness",
        severity=Severity.HIGH,
        confidence=Confidence.HIGH,
        summary="Off-by-one in loop",
        detail="Detail text",
        evidence=["src/foo.py:42"],
        suggestion="Use range(n+1)",
    )
    f_claude = Finding(reviewer="claude", **base)
    f_codex = Finding(reviewer="codex", **{**base, "confidence": Confidence.MEDIUM})
    assert f_claude.dedupe_id() == f_codex.dedupe_id()


def test_dedupe_id_changes_with_evidence():
    base = dict(
        category="correctness",
        severity=Severity.HIGH,
        confidence=Confidence.HIGH,
        summary="x",
        detail="y",
        suggestion="z",
        reviewer="claude",
    )
    f1 = Finding(evidence=["a.py:1"], **base)
    f2 = Finding(evidence=["b.py:1"], **base)
    assert f1.dedupe_id() != f2.dedupe_id()


def test_findings_merge_dedupes_across_reviewers():
    a = Finding(
        category="correctness",
        severity=Severity.HIGH,
        confidence=Confidence.HIGH,
        summary="Off-by-one",
        detail="d",
        evidence=["x.py:1"],
        suggestion="s",
        reviewer="claude",
    )
    b = Finding(
        category="correctness",
        severity=Severity.HIGH,
        confidence=Confidence.MEDIUM,
        summary="Off-by-one",
        detail="d",
        evidence=["x.py:1"],
        suggestion="s",
        reviewer="codex",
    )
    merged = Findings.merge([a], [b])
    assert len(merged) == 1
    assert set(merged[0].reviewers) == {"claude", "codex"}


def test_findings_merge_keeps_distinct():
    a = Finding(
        category="correctness", severity=Severity.HIGH, confidence=Confidence.HIGH,
        summary="A", detail="d", evidence=["x.py:1"], suggestion="s", reviewer="claude",
    )
    b = Finding(
        category="security", severity=Severity.MEDIUM, confidence=Confidence.HIGH,
        summary="B", detail="d", evidence=["y.py:2"], suggestion="s", reviewer="codex",
    )
    merged = Findings.merge([a], [b])
    assert len(merged) == 2


def test_dedupe_id_normalizes_summary_punctuation_and_whitespace():
    base = dict(
        category="correctness",
        severity=Severity.HIGH,
        confidence=Confidence.HIGH,
        detail="d",
        evidence=["x.py:1"],
        suggestion="s",
        reviewer="claude",
    )
    f1 = Finding(summary="Off-by-one in loop", **base)
    f2 = Finding(summary="Off-by-one in loop.", **base)
    f3 = Finding(summary="Off-by-one  in  loop", **base)  # double spaces
    f4 = Finding(summary="off-by-one in loop!", **base)
    assert f1.dedupe_id() == f2.dedupe_id() == f3.dedupe_id() == f4.dedupe_id()


def test_finding_evidence_is_immutable_tuple():
    f = Finding(
        category="c", severity=Severity.HIGH, confidence=Confidence.HIGH,
        summary="x", detail="d", evidence=["a.py:1", "b.py:2"], suggestion="s",
        reviewer="claude",
    )
    assert isinstance(f.evidence, tuple)
    assert f.evidence == ("a.py:1", "b.py:2")

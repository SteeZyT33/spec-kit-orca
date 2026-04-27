from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from orca.core.bundle import ReviewBundle
from orca.core.findings import Confidence, Finding, Findings, Severity
from orca.core.reviewers.base import Reviewer, ReviewerError


@dataclass(frozen=True)
class CrossResult:
    """Output of CrossReviewer.review: merged findings + partial-success flags.

    `findings` are typed Finding objects (already converted from raw dicts).
    `partial=True` when at least one reviewer failed but at least one
    succeeded; `missing_reviewer` carries the first failed reviewer's name.
    `reviewer_metadata` maps reviewer name -> the RawFindings.metadata dict
    for downstream observability (e.g., capability emits this via shim).
    """

    findings: Findings
    partial: bool
    missing_reviewer: str | None
    reviewer_metadata: dict


class CrossReviewer:
    """Runs N reviewers (>= 2) on the same bundle, merges findings via
    stable dedupe id, and returns a CrossResult with partial-success flags.

    Unlike ClaudeReviewer/CodexReviewer/FixtureReviewer, CrossReviewer is
    a higher-level adapter — it produces typed Finding objects (via
    Findings.merge) rather than raw dicts. It does NOT itself implement
    the bare Reviewer protocol because review() returns CrossResult,
    not RawFindings. The capability layer (Task 8) calls CrossReviewer
    directly when reviewer=cross is requested.
    """

    name = "cross"

    def __init__(self, *, reviewers: Sequence[Reviewer]):
        if len(reviewers) < 2:
            raise ValueError(
                f"CrossReviewer requires at least 2 reviewers, got {len(reviewers)}"
            )
        self.reviewers = list(reviewers)

    def review(self, bundle: ReviewBundle, prompt: str) -> CrossResult:
        per_reviewer_findings: list[list[Finding]] = []
        failures: list[tuple[str, ReviewerError]] = []
        metadata: dict[str, dict] = {}

        for reviewer in self.reviewers:
            try:
                raw = reviewer.review(bundle, prompt)
            except ReviewerError as exc:
                failures.append((reviewer.name, exc))
                continue
            metadata[reviewer.name] = raw.metadata
            findings = [_to_finding(f, reviewer.name) for f in raw.findings]
            per_reviewer_findings.append(findings)

        if not per_reviewer_findings:
            messages = "; ".join(f"{name}: {err}" for name, err in failures)
            raise ReviewerError(f"all reviewers failed: {messages}")

        merged = Findings.merge(*per_reviewer_findings)
        partial = len(failures) > 0
        missing = failures[0][0] if partial else None

        return CrossResult(
            findings=merged,
            partial=partial,
            missing_reviewer=missing,
            reviewer_metadata=metadata,
        )


def _to_finding(raw: dict, reviewer_name: str) -> Finding:
    """Convert a raw finding dict (from RawFindings.findings) into a
    typed Finding. The capability layer would otherwise duplicate this.
    """
    return Finding(
        category=raw["category"],
        severity=Severity(raw["severity"]),
        confidence=Confidence(raw["confidence"]),
        summary=raw["summary"],
        detail=raw["detail"],
        evidence=list(raw.get("evidence", [])),
        suggestion=raw.get("suggestion", ""),
        reviewer=reviewer_name,
    )

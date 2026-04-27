"""contradiction-detector capability.

Detects when new synthesis or theory contradicts prior evidence. v1 is a
thin wrapper over CrossReviewer (or a single reviewer) with a fixed
contradiction prompt and a structured contradiction-shaped output. v2 may
collapse this into a cross-agent-review preset.
"""
from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any, TypedDict

from orca.core.bundle import BundleError, ReviewBundle, build_bundle
from orca.core.errors import Error, ErrorKind
from orca.core.findings import convert_raw_findings
from orca.core.result import Err, Ok, Result
from orca.core.reviewers.base import Reviewer, ReviewerError
from orca.core.reviewers.cross import CrossResult, CrossReviewer

VERSION = "0.1.0"

DEFAULT_CONTRADICTION_PROMPT = (
    "Compare the new content against the prior evidence. "
    "Return a JSON array of findings where each finding represents a CONTRADICTION between "
    "a claim in the new content and the prior evidence. Each finding MUST include: "
    "category='contradiction', severity, confidence, summary (the new claim), detail (why it conflicts), "
    "evidence (refs to prior evidence files/lines that conflict), suggestion (how to resolve)."
)

_VALID_REVIEWERS = ("claude", "codex", "cross")


class ContradictionEnvelope(TypedDict):
    """JSON envelope returned by contradiction_detector on success.

    Wire-boundary contract. Changes here are breaking changes for downstream.
    """

    contradictions: list[dict[str, Any]]
    partial: bool
    missing_reviewers: list[str]
    reviewer_metadata: dict[str, dict[str, Any]]


@dataclass(frozen=True)
class ContradictionDetectorInput:
    new_content: str
    prior_evidence: list[str]
    reviewer: str = "cross"


def contradiction_detector(
    inp: ContradictionDetectorInput,
    *,
    reviewers: Mapping[str, Reviewer],
) -> Result[ContradictionEnvelope, Error]:
    """Detect contradictions between new content and prior evidence.

    Three reviewer modes (claude / codex / cross). Cross mode delegates to
    CrossReviewer (requires both backends configured). Single-reviewer mode
    calls the named reviewer once.

    Errors:
    - INPUT_INVALID: unknown reviewer, missing/non-existent new_content,
      empty prior_evidence, missing backend for cross mode.
    - BACKEND_FAILURE: reviewer raised ReviewerError, all-cross-failed,
      or reviewer returned malformed findings (KeyError/ValueError from
      convert_raw_findings).
    """
    if inp.reviewer not in _VALID_REVIEWERS:
        return Err(Error(
            kind=ErrorKind.INPUT_INVALID,
            message=f"unknown reviewer: {inp.reviewer}; expected one of {list(_VALID_REVIEWERS)}",
        ))

    if not inp.prior_evidence:
        return Err(Error(
            kind=ErrorKind.INPUT_INVALID,
            message="prior_evidence must contain at least one path",
        ))

    try:
        bundle = build_bundle(
            kind="claim-output",
            target=[inp.new_content],
            feature_id=None,
            criteria=["contradiction"],
            context=inp.prior_evidence,
        )
    except BundleError as exc:
        return Err(Error(kind=ErrorKind.INPUT_INVALID, message=str(exc)))
    except OSError as exc:
        return Err(Error(
            kind=ErrorKind.INPUT_INVALID,
            message=f"failed to read bundle target/context: {exc}",
            detail={"errno": getattr(exc, "errno", None), "filename": getattr(exc, "filename", None)},
        ))

    if inp.reviewer == "cross":
        return _run_cross(bundle, reviewers)
    return _run_single(bundle, inp, reviewers)


def _run_cross(
    bundle: ReviewBundle,
    reviewers: Mapping[str, Reviewer],
) -> Result[ContradictionEnvelope, Error]:
    try:
        cross = CrossReviewer(reviewers=[reviewers["claude"], reviewers["codex"]])
    except KeyError as exc:
        return Err(Error(
            kind=ErrorKind.INPUT_INVALID,
            message=f"missing reviewer for cross mode: {exc}",
        ))
    try:
        cross_result = cross.review(bundle, DEFAULT_CONTRADICTION_PROMPT)
    except ReviewerError as exc:
        return Err(Error(
            kind=ErrorKind.BACKEND_FAILURE,
            message=str(exc),
            detail={"underlying": exc.underlying, "retryable": exc.retryable},
        ))

    return Ok(_render_cross(cross_result))


def _render_cross(result: CrossResult) -> ContradictionEnvelope:
    contradictions = [_to_contradiction(f.to_json()) for f in result.findings]
    return {
        "contradictions": contradictions,
        "partial": result.partial,
        "missing_reviewers": list(result.missing_reviewers),
        "reviewer_metadata": result.reviewer_metadata,
    }


def _run_single(
    bundle: ReviewBundle,
    inp: ContradictionDetectorInput,
    reviewers: Mapping[str, Reviewer],
) -> Result[ContradictionEnvelope, Error]:
    if inp.reviewer not in reviewers:
        return Err(Error(
            kind=ErrorKind.INPUT_INVALID,
            message=f"reviewer not configured: {inp.reviewer}",
        ))

    try:
        raw = reviewers[inp.reviewer].review(bundle, DEFAULT_CONTRADICTION_PROMPT)
    except ReviewerError as exc:
        return Err(Error(
            kind=ErrorKind.BACKEND_FAILURE,
            message=str(exc),
            detail={"underlying": exc.underlying, "retryable": exc.retryable},
        ))

    try:
        findings = convert_raw_findings(raw.findings, reviewer=raw.reviewer)
    except ReviewerError as exc:
        return Err(Error(
            kind=ErrorKind.BACKEND_FAILURE,
            message=str(exc),
            detail={
                "underlying": exc.underlying,
                "retryable": exc.retryable,
                "reviewer": raw.reviewer,
            },
        ))

    contradictions = [_to_contradiction(f.to_json()) for f in findings]
    return Ok({
        "contradictions": contradictions,
        "partial": False,
        "missing_reviewers": [],
        "reviewer_metadata": {raw.reviewer: raw.metadata},
    })


def _to_contradiction(finding: dict) -> dict:
    """Reshape a Finding's JSON into the contradiction-shaped envelope item.

    The `summary` -> `new_claim`, first `evidence[]` -> `conflicting_evidence_ref`,
    and `suggestion` -> `suggested_resolution`. `confidence` and `reviewer`
    pass through.
    """
    evidence = finding.get("evidence", [])
    return {
        "new_claim": finding.get("summary", ""),
        "conflicting_evidence_ref": evidence[0] if evidence else "",
        "confidence": finding.get("confidence", "low"),
        "suggested_resolution": finding.get("suggestion", ""),
        "reviewer": finding.get("reviewer", ""),
    }

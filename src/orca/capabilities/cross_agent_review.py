from __future__ import annotations

from dataclasses import dataclass, field
from typing import Mapping

from orca.core.bundle import BundleError, build_bundle
from orca.core.errors import Error, ErrorKind
from orca.core.findings import Finding, Findings
from orca.core.result import Err, Ok, Result
from orca.core.reviewers.base import Reviewer, ReviewerError
from orca.core.reviewers.cross import CrossReviewer, CrossResult

VERSION = "0.1.0"

_VALID_REVIEWERS = {"claude", "codex", "cross"}


@dataclass(frozen=True)
class CrossAgentReviewInput:
    kind: str
    target: list[str]
    reviewer: str
    feature_id: str | None = None
    criteria: list[str] = field(default_factory=list)
    context: list[str] = field(default_factory=list)
    prompt: str = "Review the following content. Return a JSON array of findings."


def cross_agent_review(
    inp: CrossAgentReviewInput,
    *,
    reviewers: Mapping[str, Reviewer],
) -> Result[dict, Error]:
    """Run cross-agent review and return a JSON-envelope-shaped Result.

    Three reviewer modes:
    - "claude" / "codex": single reviewer; findings carry that reviewer name.
    - "cross": delegates to CrossReviewer (requires both "claude" and "codex"
      configured); findings collapse via stable dedupe id with combined
      reviewers tuple.

    Errors map cleanly to ErrorKind:
    - INPUT_INVALID: unknown reviewer, missing target file, malformed kind,
      missing backend reviewer for cross mode
    - BACKEND_FAILURE: reviewer raised ReviewerError, all-cross-failed,
      reviewer returned malformed findings (KeyError/ValueError from
      Finding.from_raw)
    """
    if inp.reviewer not in _VALID_REVIEWERS:
        return Err(Error(
            kind=ErrorKind.INPUT_INVALID,
            message=f"unknown reviewer: {inp.reviewer}",
        ))

    try:
        bundle = build_bundle(
            kind=inp.kind,
            target=inp.target,
            feature_id=inp.feature_id,
            criteria=inp.criteria,
            context=inp.context,
        )
    except BundleError as exc:
        return Err(Error(kind=ErrorKind.INPUT_INVALID, message=str(exc)))

    if inp.reviewer == "cross":
        return _run_cross(bundle, inp, reviewers)
    return _run_single(bundle, inp, reviewers)


def _run_cross(
    bundle,
    inp: CrossAgentReviewInput,
    reviewers: Mapping[str, Reviewer],
) -> Result[dict, Error]:
    try:
        cross = CrossReviewer(reviewers=[reviewers["claude"], reviewers["codex"]])
    except KeyError as exc:
        return Err(Error(
            kind=ErrorKind.INPUT_INVALID,
            message=f"missing reviewer for cross mode: {exc}",
        ))
    try:
        cross_result = cross.review(bundle, inp.prompt)
    except ReviewerError as exc:
        return Err(Error(kind=ErrorKind.BACKEND_FAILURE, message=str(exc)))

    return Ok(_render_cross(cross_result))


def _render_cross(result: CrossResult) -> dict:
    return {
        "findings": result.findings.to_json(),
        "partial": result.partial,
        "missing_reviewers": list(result.missing_reviewers),
        "reviewer_metadata": result.reviewer_metadata,
    }


def _run_single(
    bundle,
    inp: CrossAgentReviewInput,
    reviewers: Mapping[str, Reviewer],
) -> Result[dict, Error]:
    if inp.reviewer not in reviewers:
        return Err(Error(
            kind=ErrorKind.INPUT_INVALID,
            message=f"reviewer not configured: {inp.reviewer}",
        ))

    try:
        raw = reviewers[inp.reviewer].review(bundle, inp.prompt)
    except ReviewerError as exc:
        return Err(Error(kind=ErrorKind.BACKEND_FAILURE, message=str(exc)))

    try:
        findings = Findings([Finding.from_raw(f, reviewer=raw.reviewer) for f in raw.findings])
    except (KeyError, ValueError) as exc:
        return Err(Error(
            kind=ErrorKind.BACKEND_FAILURE,
            message=f"{raw.reviewer} returned malformed finding: {exc}",
            detail={"underlying": "malformed_finding", "reviewer": raw.reviewer},
        ))

    return Ok({
        "findings": findings.to_json(),
        "partial": False,
        "missing_reviewers": [],
        "reviewer_metadata": {raw.reviewer: raw.metadata},
    })

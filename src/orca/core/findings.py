from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Iterable


class Severity(str, Enum):
    BLOCKER = "blocker"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    NIT = "nit"


class Confidence(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass(frozen=True)
class Finding:
    category: str
    severity: Severity
    confidence: Confidence
    summary: str
    detail: str
    evidence: list[str]
    suggestion: str
    reviewer: str
    reviewers: tuple[str, ...] = field(default=())

    def __post_init__(self) -> None:
        if not self.reviewers:
            object.__setattr__(self, "reviewers", (self.reviewer,))

    def dedupe_id(self) -> str:
        payload = {
            "category": self.category,
            "severity": self.severity.value,
            "summary": self.summary.strip().lower(),
            "evidence": sorted(self.evidence),
        }
        digest = hashlib.sha256(json.dumps(payload, sort_keys=True).encode("utf-8")).hexdigest()
        return digest[:16]

    def to_json(self) -> dict[str, Any]:
        return {
            "id": self.dedupe_id(),
            "category": self.category,
            "severity": self.severity.value,
            "confidence": self.confidence.value,
            "summary": self.summary,
            "detail": self.detail,
            "evidence": list(self.evidence),
            "suggestion": self.suggestion,
            "reviewer": self.reviewer,
            "reviewers": list(self.reviewers),
        }


class Findings(list):
    @staticmethod
    def merge(*groups: Iterable[Finding]) -> "Findings":
        by_id: dict[str, Finding] = {}
        for group in groups:
            for f in group:
                key = f.dedupe_id()
                if key in by_id:
                    existing = by_id[key]
                    combined = tuple(sorted(set(existing.reviewers) | set(f.reviewers)))
                    by_id[key] = Finding(
                        category=existing.category,
                        severity=existing.severity,
                        confidence=existing.confidence,
                        summary=existing.summary,
                        detail=existing.detail,
                        evidence=existing.evidence,
                        suggestion=existing.suggestion,
                        reviewer=existing.reviewer,
                        reviewers=combined,
                    )
                else:
                    by_id[key] = f
        return Findings(by_id.values())

    def to_json(self) -> list[dict[str, Any]]:
        return [f.to_json() for f in self]

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


VALID_KINDS = {"spec", "diff", "pr", "claim-output"}


class BundleError(Exception):
    """Raised by build_bundle on invalid input or missing files."""


@dataclass(frozen=True)
class ReviewBundle:
    kind: str
    target_paths: tuple[Path, ...]
    feature_id: str | None
    criteria: tuple[str, ...]
    context_paths: tuple[Path, ...]
    bundle_hash: str

    def render_text(self) -> str:
        chunks: list[str] = []
        for p in self.target_paths:
            chunks.append(f"### {p}\n{p.read_text(encoding='utf-8', errors='replace')}")
        return "\n\n".join(chunks)


def build_bundle(
    *,
    kind: str,
    target: Iterable[str],
    feature_id: str | None,
    criteria: Iterable[str],
    context: Iterable[str],
) -> ReviewBundle:
    if kind not in VALID_KINDS:
        raise BundleError(f"unknown kind: {kind}; expected one of {sorted(VALID_KINDS)}")

    # Materialize iterables exactly once. The caller may pass a generator;
    # we both hash and store the contents, so consume into tuples up front.
    target_paths = tuple(Path(p) for p in target)
    context_paths = tuple(Path(p) for p in context)
    criteria_tuple = tuple(criteria)

    for p in target_paths:
        if not p.exists():
            raise BundleError(f"target not found: {p}")

    for p in context_paths:
        if not p.exists():
            raise BundleError(f"context not found: {p}")

    hash_payload = {
        "kind": kind,
        "feature_id": feature_id,  # None encodes naturally as null in JSON
        "targets": [(str(p), p.read_bytes().hex()) for p in target_paths],
        "context": [(str(p), p.read_bytes().hex()) for p in context_paths],
        "criteria": list(criteria_tuple),
    }
    bundle_hash = hashlib.sha256(
        json.dumps(hash_payload, sort_keys=True).encode("utf-8")
    ).hexdigest()[:32]

    return ReviewBundle(
        kind=kind,
        target_paths=target_paths,
        feature_id=feature_id,
        criteria=criteria_tuple,
        context_paths=context_paths,
        bundle_hash=bundle_hash,
    )

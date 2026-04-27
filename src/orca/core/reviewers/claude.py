from __future__ import annotations

import json
import re
from typing import Any

from orca.core.bundle import ReviewBundle
from orca.core.reviewers.base import RawFindings, ReviewerError


_JSON_ARRAY = re.compile(r"\[.*\]", re.DOTALL)


class ClaudeReviewer:
    """Reviewer adapter over the Anthropic Messages API.

    Live mode hits the real API (gated behind ORCA_LIVE=1 by callers); tests
    pass a MagicMock client. Errors from the SDK are wrapped as ReviewerError
    with retryable=True so the cross combiner / capability layer can decide
    whether to retry or surface to the user.
    """

    name = "claude"

    def __init__(self, *, client: Any, model: str = "claude-sonnet-4-6", max_tokens: int = 4096):
        self.client = client
        self.model = model
        self.max_tokens = max_tokens

    def review(self, bundle: ReviewBundle, prompt: str) -> RawFindings:
        user_text = f"{prompt}\n\n{bundle.render_text()}"
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                messages=[{"role": "user", "content": user_text}],
            )
        except Exception as exc:  # SDK raises various subclasses; treat all as backend failure
            raise ReviewerError(
                str(exc),
                retryable=True,
                underlying=type(exc).__name__,
            ) from exc

        text = "".join(
            b.text for b in response.content if getattr(b, "type", None) == "text"
        )
        findings = _parse_findings(text)
        return RawFindings(
            reviewer=self.name,
            findings=findings,
            metadata={
                "model": self.model,
                "stop_reason": response.stop_reason,
                "input_tokens": response.usage.input_tokens,
                "output_tokens": response.usage.output_tokens,
            },
        )


def _parse_findings(text: str) -> list[dict[str, Any]]:
    match = _JSON_ARRAY.search(text)
    if not match:
        raise ReviewerError(
            f"could not parse JSON array from response: {text[:200]}"
        )
    try:
        data = json.loads(match.group(0))
    except json.JSONDecodeError as exc:
        raise ReviewerError(f"could not parse JSON: {exc}") from exc
    if not isinstance(data, list):
        raise ReviewerError("expected JSON array of findings")
    return data

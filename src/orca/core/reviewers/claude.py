from __future__ import annotations

import json
import re
from typing import Any

from orca.core.bundle import ReviewBundle
from orca.core.reviewers.base import RawFindings, ReviewerError


_JSON_ARRAY = re.compile(r"\[.*\]", re.DOTALL)


def _is_retryable(exc: BaseException) -> bool:
    """Classify whether an Anthropic SDK exception is worth retrying.

    The SDK is imported lazily so tests with MagicMock clients (no anthropic
    in scope at import time? no — anthropic is now a hard dep) still work.
    Unknown exceptions default to retryable=False (safer default — capability
    layer can override per-policy).
    """
    try:
        import anthropic  # type: ignore
    except ImportError:
        return False

    # 5xx and connection/rate-limit/timeout are retryable
    retryable_types = (
        getattr(anthropic, "RateLimitError", ()),
        getattr(anthropic, "APIConnectionError", ()),
        getattr(anthropic, "APITimeoutError", ()),
        getattr(anthropic, "InternalServerError", ()),
    )
    if any(isinstance(exc, t) for t in retryable_types if isinstance(t, type)):
        return True

    api_status = getattr(anthropic, "APIStatusError", None)
    if api_status is not None and isinstance(exc, api_status):
        status_code = getattr(exc, "status_code", None)
        return status_code is not None and 500 <= status_code < 600

    return False


class ClaudeReviewer:
    """Reviewer adapter over the Anthropic Messages API.

    Live mode hits the real API (gated behind ORCA_LIVE=1 by callers); tests
    pass a MagicMock client. Errors from the SDK are wrapped as ReviewerError
    with retryable classified per Anthropic SDK exception class so the cross
    combiner / capability layer can decide whether to retry or surface to
    the user.
    """

    name = "claude"

    def __init__(self, *, client: Any, model: str = "claude-sonnet-4-6", max_tokens: int = 4096):
        """Construct a ClaudeReviewer.

        max_tokens caps model output. The default 4096 is sufficient for
        diffs under ~500 lines of structured findings JSON. For larger
        diffs, raise to 8192+ or chunk the bundle. Truncated responses
        surface as ReviewerError with underlying='max_tokens_truncation'
        rather than confusing the parser.
        """
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
        except Exception as exc:
            raise ReviewerError(
                str(exc),
                retryable=_is_retryable(exc),
                underlying=type(exc).__name__,
            ) from exc

        text = "".join(
            b.text for b in response.content if getattr(b, "type", None) == "text"
        )
        # Defensive metadata extraction: SDK shape evolves; missing fields
        # become None rather than crashing a successful review.
        usage = getattr(response, "usage", None)
        metadata = {
            "model": self.model,
            "stop_reason": getattr(response, "stop_reason", None),
            "input_tokens": getattr(usage, "input_tokens", None) if usage else None,
            "output_tokens": getattr(usage, "output_tokens", None) if usage else None,
        }
        if metadata.get("stop_reason") == "max_tokens":
            raise ReviewerError(
                f"response truncated at max_tokens={self.max_tokens}; "
                "increase max_tokens or chunk the bundle",
                retryable=False,
                underlying="max_tokens_truncation",
            )
        findings = _parse_findings(text)
        return RawFindings(
            reviewer=self.name,
            findings=findings,
            metadata=metadata,
        )


def _parse_findings(text: str) -> list[dict[str, Any]]:
    """Extract a JSON array of finding dicts from model output.

    Returns raw `list[dict[str, Any]]`; per-finding schema validation is the
    caller's job (capability code constructs `Finding` instances). The parser
    is resilient to chatty models that mention bracketed lists in prose:
    if the greedy match fails, fall back to scanning for all balanced arrays
    and pick the last one that decodes as a list of dicts.
    """
    # Greedy first: typical case — model returns one JSON array, possibly
    # inside a code fence. Greedy match handles fenced + unfenced uniformly.
    match = _JSON_ARRAY.search(text)
    if match:
        try:
            data = json.loads(match.group(0))
            if isinstance(data, list):
                return data
        except json.JSONDecodeError:
            pass  # fall through to balanced-scan

    # Fallback: scan all balanced top-level arrays, pick the last one that
    # decodes as a list of dicts (final-answer convention).
    for candidate in reversed(_balanced_arrays(text)):
        try:
            data = json.loads(candidate)
        except json.JSONDecodeError:
            continue
        if isinstance(data, list) and (not data or isinstance(data[0], dict)):
            return data

    raise ReviewerError(
        f"could not parse JSON array from response: {text[:200]}"
    )


def _balanced_arrays(text: str) -> list[str]:
    """Find all top-level balanced [...] spans in text. Naive bracket-counting
    that ignores brackets inside JSON strings. Good enough for LLM output."""
    out: list[str] = []
    i = 0
    n = len(text)
    while i < n:
        if text[i] != "[":
            i += 1
            continue
        depth = 0
        in_string = False
        escape = False
        start = i
        while i < n:
            c = text[i]
            if escape:
                escape = False
            elif c == "\\":
                escape = True
            elif c == '"':
                in_string = not in_string
            elif not in_string:
                if c == "[":
                    depth += 1
                elif c == "]":
                    depth -= 1
                    if depth == 0:
                        out.append(text[start:i + 1])
                        i += 1
                        break
            i += 1
        else:
            # Unbalanced; abandon
            break
    return out

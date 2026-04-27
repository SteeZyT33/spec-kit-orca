from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from orca.core.bundle import build_bundle
from orca.core.reviewers.base import ReviewerError
from orca.core.reviewers.claude import ClaudeReviewer

FIXTURE = Path(__file__).parent.parent.parent / "fixtures" / "reviewers" / "claude" / "simple_review.json"


def _bundle(tmp_path):
    f = tmp_path / "foo.py"
    f.write_text("for i in range(n): pass\n")
    return build_bundle(kind="diff", target=[str(f)], feature_id=None, criteria=[], context=[])


def _fake_response_from_fixture():
    data = json.loads(FIXTURE.read_text())
    block = MagicMock()
    block.type = "text"
    block.text = data["content_text"]
    response = MagicMock()
    response.content = [block]
    response.stop_reason = data["stop_reason"]
    response.usage = MagicMock(input_tokens=data["usage"]["input_tokens"], output_tokens=data["usage"]["output_tokens"])
    return response


def test_claude_reviewer_parses_findings(tmp_path):
    client = MagicMock()
    client.messages.create.return_value = _fake_response_from_fixture()
    reviewer = ClaudeReviewer(client=client, model="claude-sonnet-4-6")
    raw = reviewer.review(_bundle(tmp_path), prompt="Review this diff.")
    assert raw.reviewer == "claude"
    assert len(raw.findings) == 1
    assert raw.findings[0]["summary"] == "Off-by-one in loop"
    assert raw.metadata["model"] == "claude-sonnet-4-6"
    assert raw.metadata["stop_reason"] == "end_turn"


def test_claude_reviewer_invalid_json_response(tmp_path):
    client = MagicMock()
    block = MagicMock()
    block.type = "text"
    block.text = "not json at all"
    response = MagicMock()
    response.content = [block]
    response.stop_reason = "end_turn"
    response.usage = MagicMock(input_tokens=1, output_tokens=1)
    client.messages.create.return_value = response

    reviewer = ClaudeReviewer(client=client, model="claude-sonnet-4-6")
    with pytest.raises(ReviewerError, match="parse"):
        reviewer.review(_bundle(tmp_path), prompt="any")


def test_claude_reviewer_api_error_wrapped(tmp_path):
    client = MagicMock()
    client.messages.create.side_effect = RuntimeError("rate limited")

    reviewer = ClaudeReviewer(client=client, model="claude-sonnet-4-6")
    with pytest.raises(ReviewerError, match="rate limited"):
        reviewer.review(_bundle(tmp_path), prompt="any")


def test_claude_reviewer_name_default(tmp_path):
    reviewer = ClaudeReviewer(client=MagicMock(), model="claude-sonnet-4-6")
    assert reviewer.name == "claude"

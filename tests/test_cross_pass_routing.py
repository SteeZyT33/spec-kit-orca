"""Tests for 012 cross-pass agent routing policy in matriarch.py."""
from __future__ import annotations

import pytest

from speckit_orca.matriarch import (
    CROSS_PASS_TIER_1,
    CROSS_PASS_TIER_2,
    MatriarchError,
    select_cross_pass_agent,
)


class TestHappyPath:
    def test_author_claude_returns_codex(self) -> None:
        assert select_cross_pass_agent(author_agent="claude") == "codex"

    def test_author_codex_returns_claude(self) -> None:
        result = select_cross_pass_agent(author_agent="codex")
        assert result == "claude"
        assert result != "codex"


class TestTierDowngrade:
    def test_tier1_downgrade_within_tier(self) -> None:
        result = select_cross_pass_agent(
            author_agent="claude", timed_out_agents=["codex"]
        )
        assert result == "gemini"

    def test_full_tier1_downgrade(self) -> None:
        result = select_cross_pass_agent(
            author_agent="claude",
            timed_out_agents=["codex", "gemini", "opencode"],
        )
        assert result == "cursor-agent"
        assert result in CROSS_PASS_TIER_2

    def test_all_tiers_exhausted_raises(self) -> None:
        with pytest.raises(MatriarchError, match="no different-agent alternative"):
            select_cross_pass_agent(
                author_agent="claude",
                timed_out_agents=["codex", "gemini", "opencode", "cursor-agent"],
            )


class TestNoSameAgentFallback:
    def test_never_returns_author(self) -> None:
        for author in CROSS_PASS_TIER_1:
            result = select_cross_pass_agent(author_agent=author)
            assert result != author

    def test_all_unavailable_raises_not_author(self) -> None:
        all_others = list(CROSS_PASS_TIER_1) + list(CROSS_PASS_TIER_2)
        with pytest.raises(MatriarchError):
            select_cross_pass_agent(
                author_agent="claude",
                timed_out_agents=[a for a in all_others if a != "claude"],
            )


class TestDeterminism:
    def test_same_inputs_same_output(self) -> None:
        results = {
            select_cross_pass_agent(
                author_agent="claude", timed_out_agents=["codex"]
            )
            for _ in range(100)
        }
        assert len(results) == 1


class TestTierModel:
    def test_tier1_has_four_agents(self) -> None:
        assert CROSS_PASS_TIER_1 == ("codex", "claude", "gemini", "opencode")

    def test_tier2_has_cursor_agent(self) -> None:
        assert CROSS_PASS_TIER_2 == ("cursor-agent",)

"""Orca v1 capability catalog. Each capability is a pure function returning Result."""

from orca.capabilities.cross_agent_review import (
    CrossAgentReviewInput,
    cross_agent_review,
)

__all__ = ["CrossAgentReviewInput", "cross_agent_review"]

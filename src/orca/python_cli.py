"""Canonical Python CLI for orca capabilities.

This is a sibling to `cli.py` (the bash launcher kept for the opinion layer's
slash commands). `python_cli.py` is the wire-format-canonical surface: each
capability gets a subcommand, args parse to the capability's input dataclass,
the Result envelope is emitted as JSON to stdout (or pretty-printed via
`--pretty`), and the exit code follows the design's universal Result contract:

  0  success
  1  capability returned Err (input_invalid / backend_failure / etc.)
  2  CLI argv parse error
  3  unknown capability

Reviewer backends are loaded from environment:
  ORCA_FIXTURE_REVIEWER_CLAUDE / _CODEX  -> FixtureReviewer (tests)
  ORCA_LIVE=1                            -> real backends (manual verification)
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from collections.abc import Sequence
from pathlib import Path

from orca.capabilities.cross_agent_review import (
    DEFAULT_REVIEW_PROMPT,
    VERSION as CROSS_AGENT_REVIEW_VERSION,
    CrossAgentReviewInput,
    cross_agent_review,
)
from orca.core.errors import ErrorKind
from orca.core.reviewers.claude import ClaudeReviewer
from orca.core.reviewers.codex import CodexReviewer
from orca.core.reviewers.fixtures import FixtureReviewer

CAPABILITIES = {
    "cross-agent-review": ("cross_agent_review", CROSS_AGENT_REVIEW_VERSION),
}


def main(argv: Sequence[str] | None = None) -> int:
    argv = list(argv) if argv is not None else sys.argv[1:]

    if not argv:
        _print_help()
        return 0

    if argv[0] in ("--list", "-l"):
        for name in CAPABILITIES:
            print(name)
        return 0

    if argv[0] in ("-h", "--help"):
        _print_help()
        return 0

    capability = argv[0]
    if capability not in CAPABILITIES:
        print(f"unknown capability: {capability}", file=sys.stderr)
        print(f"available: {', '.join(CAPABILITIES)}", file=sys.stderr)
        return 3

    if capability == "cross-agent-review":
        return _run_cross_agent_review(argv[1:])

    return 3


def _print_help() -> None:
    print("orca-cli - orca capability runner")
    print()
    print("Usage: orca-cli <capability> [options]")
    print()
    print("Capabilities:")
    for name in CAPABILITIES:
        print(f"  {name}")


def _run_cross_agent_review(args: list[str]) -> int:
    parser = argparse.ArgumentParser(prog="orca-cli cross-agent-review")
    parser.add_argument("--kind", required=True)
    parser.add_argument("--target", action="append", required=True, default=[])
    parser.add_argument("--reviewer", default="cross")
    parser.add_argument("--feature-id", default=None)
    parser.add_argument("--criteria", action="append", default=[])
    parser.add_argument("--context", action="append", default=[])
    parser.add_argument("--prompt", default=DEFAULT_REVIEW_PROMPT)
    parser.add_argument("--json", action="store_true",
                        help="emit JSON envelope to stdout (default)")
    parser.add_argument("--pretty", action="store_true",
                        help="emit human-readable summary instead of JSON")
    ns, unknown = parser.parse_known_args(args)

    if unknown:
        return _emit_envelope(
            envelope=_err_envelope(
                "cross-agent-review", CROSS_AGENT_REVIEW_VERSION,
                ErrorKind.INPUT_INVALID, f"unknown args: {unknown}",
            ),
            pretty=ns.pretty,
            exit_code=1,
        )

    inp = CrossAgentReviewInput(
        kind=ns.kind,
        target=ns.target,
        feature_id=ns.feature_id,
        reviewer=ns.reviewer,
        criteria=ns.criteria,
        context=ns.context,
        prompt=ns.prompt,
    )

    started = time.monotonic()
    reviewers = _load_reviewers()
    result = cross_agent_review(inp, reviewers=reviewers)
    duration_ms = int((time.monotonic() - started) * 1000)

    envelope = result.to_json(
        capability="cross-agent-review",
        version=CROSS_AGENT_REVIEW_VERSION,
        duration_ms=duration_ms,
    )
    exit_code = 0 if result.ok else 1
    return _emit_envelope(envelope=envelope, pretty=ns.pretty, exit_code=exit_code)


def _load_reviewers() -> dict:
    """Pick reviewer backends from env vars.

    Fixture overrides (ORCA_FIXTURE_REVIEWER_*) win for tests; ORCA_LIVE=1
    enables real backends for manual verification. If neither is set, the
    capability layer surfaces missing-reviewer as Err(INPUT_INVALID).
    """
    reviewers: dict = {}

    claude_fixture = os.environ.get("ORCA_FIXTURE_REVIEWER_CLAUDE")
    if claude_fixture:
        reviewers["claude"] = FixtureReviewer(
            scenario=Path(claude_fixture), name="claude",
        )
    elif os.environ.get("ORCA_LIVE") == "1":
        try:
            import anthropic  # type: ignore
            reviewers["claude"] = ClaudeReviewer(client=anthropic.Anthropic())
        except ImportError:
            pass

    codex_fixture = os.environ.get("ORCA_FIXTURE_REVIEWER_CODEX")
    if codex_fixture:
        reviewers["codex"] = FixtureReviewer(
            scenario=Path(codex_fixture), name="codex",
        )
    elif os.environ.get("ORCA_LIVE") == "1":
        reviewers["codex"] = CodexReviewer()

    return reviewers


def _err_envelope(capability: str, version: str, kind: ErrorKind, message: str) -> dict:
    return {
        "ok": False,
        "error": {"kind": kind.value, "message": message},
        "metadata": {"capability": capability, "version": version, "duration_ms": 0},
    }


def _emit_envelope(*, envelope: dict, pretty: bool, exit_code: int) -> int:
    if pretty:
        if envelope["ok"]:
            findings = envelope["result"].get("findings", [])
            print(f"OK ({len(findings)} findings)")
            for f in findings:
                evidence = ",".join(f.get("evidence", []))
                print(f"  [{f['severity']}] {f['summary']} - {evidence}")
        else:
            print(f"ERROR ({envelope['error']['kind']}): {envelope['error']['message']}")
    else:
        print(json.dumps(envelope, indent=2))
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())

"""Markdown renderers for orca-cli capability outputs.

Slash commands shell to `orca-cli <capability>` for JSON envelopes,
then pipe through `python -m orca.cli_output render-{type}` to get
the markdown that appends to the on-disk artifact.

This module is the boundary between machine-readable JSON contracts
and operator-readable markdown artifacts. Slash commands stay
declarative; capability output stays JSON; this module translates.
"""
from __future__ import annotations

import argparse
import json
import sys
from typing import Any


def render_error_block(envelope: dict[str, Any], *, round_num: int) -> str:
    """Render a failure envelope as a Round-N labeled markdown block.

    Common to all artifact renderers. Includes ErrorKind, message, and
    detail block (underlying + retryable when present).
    """
    err = envelope.get("error", {})
    kind = err.get("kind", "unknown")
    message = err.get("message", "(no message)")
    detail = err.get("detail") or {}

    lines = [
        f"### Round {round_num} - FAILED",
        "",
        f"- kind: {kind}",
        f"- message: {message}",
    ]
    for key, value in sorted(detail.items()):
        lines.append(f"- {key}: {value}")
    lines.append("")
    lines.append(render_metadata_footer(envelope))
    return "\n".join(lines)


def render_metadata_footer(envelope: dict[str, Any]) -> str:
    """Render the trailing metadata block all artifacts share."""
    meta = envelope.get("metadata", {})
    capability = meta.get("capability", "?")
    version = meta.get("version", "?")
    duration_ms = meta.get("duration_ms", 0)
    return (
        f"_capability: {capability}_  \n"
        f"_version: {version}_  \n"
        f"_duration: {duration_ms}ms_"
    )


def main(argv: list[str] | None = None) -> int:
    """CLI entrypoint: `python -m orca.cli_output render-{type} ...`.

    Wired up in Task 4. Skeleton here so the module is importable.
    """
    parser = argparse.ArgumentParser(prog="python -m orca.cli_output")
    parser.add_argument("subcommand", nargs="?", help="render-{type}")
    args, _ = parser.parse_known_args(argv if argv is not None else sys.argv[1:])
    if args.subcommand is None:
        parser.print_help()
        return 0
    print(f"unknown subcommand: {args.subcommand}", file=sys.stderr)
    return 3


if __name__ == "__main__":
    raise SystemExit(main())

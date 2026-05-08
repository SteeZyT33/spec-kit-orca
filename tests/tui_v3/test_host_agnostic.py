"""TUI works against any host system (bare / spec-kit / openspec / superpowers).

The host-agnostic invariant per CLAUDE.md: never hardcode a spec system path.
Always go through host_layout. This test renders the TUI against four
synthetic hosts and asserts no crash + sensible empty/populated output.
"""
from __future__ import annotations

import asyncio
import json
import textwrap
from datetime import datetime, timezone
from pathlib import Path

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_manifest(host_system: str) -> str:
    """Return a complete, valid adoption.toml for the given host system."""
    patterns = {
        "spec-kit": "specs/{feature_id}",
        "openspec": "openspec/changes/{feature_id}",
        "superpowers": "docs/superpowers/specs/{feature_id}",
        "bare": "docs/orca-specs/{feature_id}",
    }
    review_dirs = {
        "spec-kit": "specs/_reviews",
        "openspec": "openspec/changes",
        "superpowers": "docs/superpowers/reviews",
        "bare": "docs/orca-specs/_reviews",
    }
    pattern = patterns[host_system]
    review_dir = review_dirs[host_system]
    return textwrap.dedent(f"""
        schema_version = 1

        [host]
        system = "{host_system}"
        feature_dir_pattern = "{pattern}"
        agents_md_path = "AGENTS.md"
        review_artifact_dir = "{review_dir}"

        [orca]
        state_dir = ".orca"
        installed_capabilities = []

        [slash_commands]
        namespace = "orca"
        enabled = []
        disabled = []

        [claude_md]
        policy = "section"
        section_marker = "## Orca"
        namespace_prefix = "orca:"

        [constitution]
        policy = "respect-existing"

        [reversal]
        backup_dir = ".orca/adoption-backup"
    """).lstrip()


def _seed_manifest(repo: Path, host_system: str) -> None:
    """Drop a complete, valid adoption.toml for the named host system."""
    (repo / ".orca").mkdir(parents=True, exist_ok=True)
    (repo / ".orca" / "adoption.toml").write_text(_make_manifest(host_system))


def _seed_lane(repo: Path, lane_id: str, host_system: str) -> None:
    """Drop a registry+sidecar without touching the host's spec layout."""
    wt_root = repo / ".orca" / "worktrees"
    wt_root.mkdir(parents=True, exist_ok=True)
    now_iso = datetime(2026, 5, 7, 12, 0, 0, tzinfo=timezone.utc).isoformat()
    sidecar = {
        "schema_version": 2,
        "lane_id": lane_id, "lane_mode": "branch",
        "feature_id": lane_id, "lane_name": lane_id,
        "branch": lane_id, "base_branch": "main",
        "worktree_path": f"/tmp/{lane_id}",
        "created_at": now_iso,
        "tmux_session": "", "tmux_window": lane_id[:32],
        "agent": "none", "setup_version": "abc",
        "last_attached_at": now_iso,
        "host_system": host_system,
        "status": "active", "task_scope": [],
    }
    (wt_root / f"{lane_id}.json").write_text(json.dumps(sidecar))
    (wt_root / "registry.json").write_text(json.dumps({
        "schema_version": 2,
        "lanes": [{
            "branch": lane_id, "feature_id": lane_id,
            "lane_id": lane_id, "worktree_path": f"/tmp/{lane_id}",
        }],
    }))


# ---------------------------------------------------------------------------
# Core async render helper
# ---------------------------------------------------------------------------

async def _render(repo: Path, *, host: str | None, lane_id: str) -> None:
    from orca.tui.app import FleetApp

    _seed_lane(repo, lane_id, host or "bare")

    # Render fleet — must not crash.
    app = FleetApp(repo_root=repo, read_only=True)
    async with app.run_test(size=(140, 44)) as pilot:
        await pilot.pause()
        text = app.export_screenshot()
        assert lane_id in text, f"lane {lane_id} not rendered for host={host}"

        # Drill in — must not crash. Some hosts may not resolve the
        # feature_dir; STAGE PROGRESS will fall back to the all-dash default
        # which is fine.
        await pilot.press("enter")
        await pilot.pause()
        drill_text = app.export_screenshot()
        assert "STAGE PROGRESS" in drill_text, (
            f"drilldown didn't render for host={host}"
        )
        assert "GIT LOG" in drill_text, f"git log block missing for host={host}"


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_tui_works_against_bare_repo(tmp_path: Path) -> None:
    """No adoption manifest, no specs/, no docs/. Just .orca/worktrees/."""
    asyncio.run(_render(tmp_path, host=None, lane_id="bare-lane"))


def test_tui_works_against_spec_kit(tmp_path: Path) -> None:
    """spec-kit: feature_dir is `specs/<id>/`."""
    _seed_manifest(tmp_path, "spec-kit")
    asyncio.run(_render(tmp_path, host="spec-kit", lane_id="spec-kit-lane"))


def test_tui_works_against_openspec(tmp_path: Path) -> None:
    """openspec: different feature dir convention."""
    _seed_manifest(tmp_path, "openspec")
    asyncio.run(_render(tmp_path, host="openspec", lane_id="openspec-lane"))


def test_tui_works_against_superpowers(tmp_path: Path) -> None:
    """superpowers: control test, should match existing behavior."""
    _seed_manifest(tmp_path, "superpowers")
    asyncio.run(_render(tmp_path, host="superpowers", lane_id="sp-lane"))

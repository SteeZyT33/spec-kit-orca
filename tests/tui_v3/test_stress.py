"""Stress tests: time collect_fleet under load. Bound is generous to allow
slow CI runners but catches O(N*E) regressions."""
from __future__ import annotations

import json
import time
from datetime import datetime, timezone
from pathlib import Path

import pytest


def _write_registry(repo_root: Path, n_lanes: int) -> None:
    wt_root = repo_root / ".orca" / "worktrees"
    wt_root.mkdir(parents=True, exist_ok=True)
    (repo_root / ".orca" / "adoption.toml").write_text(
        '[host]\nsystem = "superpowers"\nconstitution_path = ""\n'
        'agents_md_path = "AGENTS.md"\n[install]\nslash_command_namespace = "orca"\n'
        '[scope]\nclaude_md = "track"\n'
    )
    lanes = []
    now_iso = datetime(2026, 5, 7, 12, 0, 0, tzinfo=timezone.utc).isoformat()
    for i in range(n_lanes):
        lid = f"lane-{i:03d}"
        lanes.append({
            "branch": lid, "feature_id": None,
            "lane_id": lid, "worktree_path": f"/tmp/{lid}",
        })
        sidecar = {
            "schema_version": 2,
            "lane_id": lid, "lane_mode": "branch",
            "feature_id": None, "lane_name": lid,
            "branch": lid, "base_branch": "main",
            "worktree_path": f"/tmp/{lid}",
            "created_at": now_iso,
            "tmux_session": "", "tmux_window": lid[:32],
            "agent": "none", "setup_version": "abc",
            "last_attached_at": now_iso,
            "host_system": "superpowers",
            "status": "active", "task_scope": [],
        }
        (wt_root / f"{lid}.json").write_text(json.dumps(sidecar))
    (wt_root / "registry.json").write_text(json.dumps({
        "schema_version": 2, "lanes": lanes,
    }))


def _write_events(repo_root: Path, n_events: int) -> None:
    wt_root = repo_root / ".orca" / "worktrees"
    wt_root.mkdir(parents=True, exist_ok=True)
    base_ts = datetime(2026, 5, 7, 10, 0, 0, tzinfo=timezone.utc)
    lines = []
    for i in range(n_events):
        ts = (base_ts.replace(second=i % 60).isoformat())
        lid = f"lane-{i % 50:03d}"
        lines.append(json.dumps({
            "event": "agent.launched" if i % 3 == 0 else "lane.attached",
            "lane_id": lid, "ts": ts,
            "agent": "claude" if i % 3 == 0 else "",
        }))
    (wt_root / "events.jsonl").write_text("\n".join(lines) + "\n")


def test_collect_fleet_50_lanes_no_events(tmp_path: Path) -> None:
    """50 lanes, no events file. Bound: 250ms."""
    from orca.tui.collect import collect_fleet

    _write_registry(tmp_path, 50)

    start = time.perf_counter()
    rows = collect_fleet(
        tmp_path,
        tmux_alive=lambda s: False,
        branch_merged=lambda b, base: False,
    )
    elapsed = time.perf_counter() - start
    assert len(rows) == 50
    assert elapsed < 0.25, f"50 lanes / no events took {elapsed:.3f}s, expected <0.25s"


def test_collect_fleet_50_lanes_10k_events(tmp_path: Path) -> None:
    """50 lanes + 10k events using the single-pass index path. Bound: 250ms.

    The per-lane callback path (O(lanes × events)) was the original bug;
    collect_fleet now builds build_event_index() once when no callbacks are
    injected, bringing this from ~900ms → ~10ms. The tight bound catches
    any future regression back to the O(N*E) pattern.
    """
    from orca.tui.collect import collect_fleet

    _write_registry(tmp_path, 50)
    _write_events(tmp_path, 10000)

    start = time.perf_counter()
    rows = collect_fleet(
        tmp_path,
        tmux_alive=lambda s: False,
        branch_merged=lambda b, base: False,
        # No last_event / last_setup_failed → collect_fleet builds the index once
    )
    elapsed = time.perf_counter() - start
    assert len(rows) == 50
    assert elapsed < 0.25, (
        f"50 lanes + 10k events took {elapsed:.3f}s — "
        f"expected <0.25s; suggests O(N*E) regression in events.jsonl reads"
    )


def test_collect_fleet_100_lanes_baseline(tmp_path: Path) -> None:
    """100 lanes baseline (no events) to ensure registry/sidecar IO scales."""
    from orca.tui.collect import collect_fleet

    _write_registry(tmp_path, 100)

    start = time.perf_counter()
    rows = collect_fleet(
        tmp_path,
        tmux_alive=lambda s: False,
        branch_merged=lambda b, base: False,
    )
    elapsed = time.perf_counter() - start
    assert len(rows) == 100
    assert elapsed < 0.5, f"100 lanes took {elapsed:.3f}s, expected <0.5s"

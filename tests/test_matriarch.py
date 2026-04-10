from __future__ import annotations

import json
from pathlib import Path

import pytest

from speckit_orca.matriarch import (
    MatriarchError,
    acknowledge_event,
    add_dependency,
    append_report_event,
    archive_lane,
    claim_delegated_work,
    complete_delegated_work,
    create_delegated_work,
    emit_startup_ack,
    list_mailbox_events,
    overall_status,
    register_lane,
    release_delegated_work,
    send_mailbox_event,
    summarize_lane,
)


def _repo(tmp_path: Path) -> Path:
    root = tmp_path / "repo"
    (root / ".specify").mkdir(parents=True)
    (root / "specs").mkdir()
    return root


def _spec(root: Path, spec_id: str, *, files: dict[str, str] | None = None) -> Path:
    feature_dir = root / "specs" / spec_id
    feature_dir.mkdir(parents=True)
    for name, content in (files or {"spec.md": "# Spec\n"}).items():
        (feature_dir / name).write_text(content, encoding="utf-8")
    return feature_dir


def test_register_lane_creates_registry_and_mailbox_paths(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    _spec(repo, "010-orca-matriarch")

    record = register_lane("010-orca-matriarch", repo_root=repo)

    assert record.lane_id == "010-orca-matriarch"
    assert record.spec_id == "010-orca-matriarch"
    assert record.registry_revision == 1
    assert record.mailbox_path == ".specify/orca/matriarch/mailbox/010-orca-matriarch"
    assert record.assignment_history == []
    assert (repo / ".specify" / "orca" / "matriarch" / "registry.json").exists()
    assert (repo / ".specify" / "orca" / "matriarch" / "mailbox" / "010-orca-matriarch").exists()


def test_dependency_on_missing_upstream_blocks_lane_until_upstream_exists(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    _spec(repo, "010-orca-matriarch")
    _spec(repo, "011-orca-evolve")

    register_lane("010-orca-matriarch", repo_root=repo, owner_type="human", owner_id="taylor")
    add_dependency(
        "010-orca-matriarch",
        "011-orca-evolve",
        repo_root=repo,
        target_kind="lane_exists",
        rationale="Wait for upstream setup.",
    )

    blocked = summarize_lane("010-orca-matriarch", repo_root=repo)
    assert blocked["effective_state"] == "blocked"
    assert blocked["dependencies"][0]["state"] == "active"

    register_lane("011-orca-evolve", repo_root=repo)

    unblocked = summarize_lane("010-orca-matriarch", repo_root=repo)
    assert unblocked["effective_state"] == "active"
    assert unblocked["dependencies"][0]["state"] == "satisfied"
    assert unblocked["assignment_history"][0]["owner_id"] == "taylor"


def test_lane_mutations_advance_registry_revision(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    _spec(repo, "010-orca-matriarch")

    registered = register_lane("010-orca-matriarch", repo_root=repo)
    assert registered.registry_revision == 1

    reassigned = add_dependency(
        "010-orca-matriarch",
        "missing-lane",
        repo_root=repo,
        target_kind="lane_exists",
    )
    assert reassigned.registry_revision == 2

    archived = archive_lane("010-orca-matriarch", repo_root=repo, reason="Done.")
    assert archived.registry_revision == 3

    status = overall_status(repo_root=repo)
    assert status["counts"]["archived"] == 1


def test_mailbox_and_report_events_use_shared_envelope(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    _spec(repo, "010-orca-matriarch")
    register_lane("010-orca-matriarch", repo_root=repo)

    outbound = send_mailbox_event(
        "010-orca-matriarch",
        repo_root=repo,
        direction="to_lane",
        sender="matriarch",
        recipient="worker-1",
        event_type="instruction",
        payload={"step": "inspect"},
    )
    ack = acknowledge_event(
        "010-orca-matriarch",
        repo_root=repo,
        sender="worker-1",
        recipient="matriarch",
        acked_event_id=outbound.id,
    )
    startup = emit_startup_ack(
        "010-orca-matriarch",
        repo_root=repo,
        sender="worker-1",
        deployment_id="010-orca-matriarch-direct-session",
        context_refs=["specs/010-orca-matriarch/spec.md"],
    )
    append_report_event(
        "010-orca-matriarch",
        repo_root=repo,
        sender="worker-1",
        event_type="status",
        payload={"message": "running"},
    )

    mailbox = list_mailbox_events("010-orca-matriarch", repo_root=repo)
    reports_path = repo / ".specify" / "orca" / "matriarch" / "reports" / "010-orca-matriarch" / "events.jsonl"
    reports = [json.loads(line) for line in reports_path.read_text(encoding="utf-8").splitlines() if line.strip()]

    assert mailbox["outbound"][0]["type"] == "instruction"
    assert mailbox["inbound"][0]["type"] == "ack"
    assert mailbox["inbound"][0]["ack_status"] == "acknowledged"
    assert mailbox["inbound"][0]["payload"]["acked_event_id"] == outbound.id
    assert startup.type == "ack"
    assert startup.ack_status == "acknowledged"
    assert reports[0]["payload"]["deployment_id"] == "010-orca-matriarch-direct-session"
    assert reports[1]["type"] == "status"


def test_delegated_work_rejects_stale_completion_and_can_be_released(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    _spec(repo, "010-orca-matriarch")
    register_lane("010-orca-matriarch", repo_root=repo)

    create_delegated_work("010-orca-matriarch", "T001", "Implement runtime", repo_root=repo)
    claimed = claim_delegated_work(
        "010-orca-matriarch",
        "T001",
        repo_root=repo,
        claimer_id="worker-1",
    )

    with pytest.raises(MatriarchError, match="Stale delegated-work completion rejected"):
        complete_delegated_work(
            "010-orca-matriarch",
            "T001",
            repo_root=repo,
            claim_token="bad-token",
            result_ref="notes.md",
        )

    released = release_delegated_work(
        "010-orca-matriarch",
        "T001",
        repo_root=repo,
        claim_token=claimed.claim_token or "",
    )
    assert released.status == "pending"

    reclaimed = claim_delegated_work(
        "010-orca-matriarch",
        "T001",
        repo_root=repo,
        claimer_id="worker-2",
    )
    completed = complete_delegated_work(
        "010-orca-matriarch",
        "T001",
        repo_root=repo,
        claim_token=reclaimed.claim_token or "",
        result_ref="specs/010-orca-matriarch/review.md",
    )
    assert completed.status == "completed"
    assert completed.result_ref == "specs/010-orca-matriarch/review.md"

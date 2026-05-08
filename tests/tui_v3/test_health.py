"""Health tag derivation: comma-separated short flags, empty when fine."""
from datetime import datetime, timedelta, timezone

import pytest

from orca.tui.health import derive_health, HealthInputs


@pytest.fixture
def now():
    return datetime(2026, 5, 1, 12, 0, 0, tzinfo=timezone.utc)


def _iso(now, **delta):
    return (now - timedelta(**delta)).isoformat()


def test_health_empty_when_fine(now):
    inp = HealthInputs(
        last_attached_at=_iso(now, minutes=5),
        last_setup_failed=False,
        branch_merged=False,
        tmux_alive=True,
        sidecar_active=True,
        doctor_warnings=[],
    )
    assert derive_health(inp, now=now) == ""


def test_health_stale_after_24h(now):
    inp = HealthInputs(
        last_attached_at=_iso(now, hours=48),
        last_setup_failed=False,
        branch_merged=False,
        tmux_alive=False,
        sidecar_active=True,
        doctor_warnings=[],
    )
    assert "stale 2d" in derive_health(inp, now=now)


def test_health_setup_failed(now):
    inp = HealthInputs(
        last_attached_at=_iso(now, minutes=5),
        last_setup_failed=True,
        branch_merged=False,
        tmux_alive=True,
        sidecar_active=True,
        doctor_warnings=[],
    )
    assert "setup-failed" in derive_health(inp, now=now)


def test_health_merged_cleanup(now):
    inp = HealthInputs(
        last_attached_at=_iso(now, hours=1),
        last_setup_failed=False,
        branch_merged=True,
        tmux_alive=False,
        sidecar_active=True,
        doctor_warnings=[],
    )
    assert "merged·cleanup" in derive_health(inp, now=now)


def test_health_tmux_orphan(now):
    inp = HealthInputs(
        last_attached_at=_iso(now, hours=1),
        last_setup_failed=False,
        branch_merged=False,
        tmux_alive=False,
        sidecar_active=True,
        tmux_configured=True,
        doctor_warnings=[],
    )
    assert "tmux-orphan" in derive_health(inp, now=now)


def test_health_no_tmux_orphan_when_tmux_not_configured(now):
    """A lane created --no-tmux (empty tmux_session) is NOT an orphan."""
    inp = HealthInputs(
        last_attached_at=_iso(now, hours=1),
        last_setup_failed=False,
        branch_merged=False,
        tmux_alive=False,
        sidecar_active=True,
        tmux_configured=False,
        doctor_warnings=[],
    )
    assert "tmux-orphan" not in derive_health(inp, now=now)


def test_health_tmux_orphan_when_configured_but_dead(now):
    """When tmux WAS configured but isn't alive, that IS an orphan."""
    inp = HealthInputs(
        last_attached_at=_iso(now, hours=1),
        last_setup_failed=False,
        branch_merged=False,
        tmux_alive=False,
        sidecar_active=True,
        tmux_configured=True,
        doctor_warnings=[],
    )
    assert "tmux-orphan" in derive_health(inp, now=now)


def test_health_doctor_passthrough(now):
    inp = HealthInputs(
        last_attached_at=_iso(now, minutes=5),
        last_setup_failed=False,
        branch_merged=False,
        tmux_alive=True,
        sidecar_active=True,
        doctor_warnings=["registry lock stale"],
    )
    assert "doctor: registry lock stale" in derive_health(inp, now=now)

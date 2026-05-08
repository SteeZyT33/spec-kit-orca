"""Human-readable stage status mapping."""
from orca.tui.flow_strip import status_label


def test_known_statuses_map_to_labels():
    assert status_label("complete") == "done"
    assert status_label("in_progress") == "in progress"
    assert status_label("blocked") == "blocked"
    assert status_label("not_started") == "—"
    assert status_label("incomplete") == "partial"
    assert status_label("missing") == "not started"
    assert status_label("phases_partial") == "phases partial"
    assert status_label("overall_complete") == "done"


def test_unknown_status_falls_back_to_dash():
    assert status_label("ralph") == "—"
    assert status_label("") == "—"

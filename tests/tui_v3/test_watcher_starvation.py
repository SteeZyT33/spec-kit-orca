"""Watcher debounce must not starve under sustained burst.

If file changes arrive faster than coalesce_window for an extended period,
the callback should still fire periodically (max-delay cap), not silently
hold off forever.
"""
from __future__ import annotations

import threading
import time
from pathlib import Path


def test_watcher_fires_under_sustained_burst(tmp_path: Path) -> None:
    """5-second burst at 50 changes/sec. Callback must fire at least 2 times
    (proving max-delay cap is active).

    Bound justification: 3-second burst with max_delay=1.0 should produce at
    least 2 fires (once at ~1.0s, once at ~2.0s, plus the settling fire after
    the burst). We assert >=2 to remain robust under CI timer jitter. If this
    bound proves unreliable, the max-delay cap is genuinely not working at 1.0s.
    """
    # Need a real watch target so watchdog attaches.
    watch_dir = tmp_path / ".orca" / "worktrees"
    watch_dir.mkdir(parents=True)

    from orca.tui.watcher import Watcher

    fire_count = [0]
    fire_lock = threading.Lock()

    def cb(_path):
        with fire_lock:
            fire_count[0] += 1

    w = Watcher(
        tmp_path, cb,
        coalesce_window=0.3,  # cancel within 300ms
        max_delay=1.0,         # but fire at least every 1.0s under sustained burst
    )
    try:
        # Sustained burst: 50 file writes / second for 3 seconds.
        deadline = time.time() + 3.0
        i = 0
        while time.time() < deadline:
            (watch_dir / f"churn-{i}.tmp").write_text("x")
            i += 1
            time.sleep(0.02)  # 50/sec

        # Give the last debounce timer a chance to fire.
        time.sleep(0.6)

        # Under sustained burst with no max-delay, fire_count would be 1
        # (only after the burst ends). With max-delay=1.0, we should see
        # at least 2 fires during the 3-second burst — proving forward
        # progress under load.
        with fire_lock:
            count = fire_count[0]
        assert count >= 2, (
            f"Expected ≥2 fires under sustained burst (max-delay cap), "
            f"got {count}. Watcher is starving."
        )
    finally:
        w.stop()


def test_watcher_settles_with_no_changes(tmp_path: Path) -> None:
    """No changes: callback should NOT fire from polling at the default
    5s interval within a 1s window."""
    watch_dir = tmp_path / ".orca" / "worktrees"
    watch_dir.mkdir(parents=True)

    from orca.tui.watcher import Watcher

    fire_count = [0]

    def cb(_path):
        fire_count[0] += 1

    w = Watcher(tmp_path, cb, coalesce_window=0.3, max_delay=1.0)
    try:
        time.sleep(0.5)
        assert fire_count[0] == 0, (
            f"Watcher fired {fire_count[0]} times with no changes — "
            f"polling shouldn't fire that fast"
        )
    finally:
        w.stop()

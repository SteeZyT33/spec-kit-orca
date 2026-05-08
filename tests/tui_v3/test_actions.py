"""Mutation actions: subprocess shells out to orca-cli."""
from __future__ import annotations

from pathlib import Path

from orca.tui.actions import close_lane, doctor


def test_close_lane_calls_orca_cli_wt_rm_with_positional_branch(tmp_path: Path, monkeypatch):
    calls: list[list[str]] = []

    class _CP:
        returncode = 0
        stdout = "ok"
        stderr = ""

    def fake_run(cmd, **kw):
        calls.append(cmd)
        return _CP()

    monkeypatch.setattr("subprocess.run", fake_run)
    res = close_lane(tmp_path, branch="my-branch")
    # POSITIONAL branch — no --branch flag
    assert calls and calls[0] == ["orca-cli", "wt", "rm", "my-branch", "--force"], (
        f"expected positional branch, got {calls[0]}"
    )
    assert res.rc == 0


def test_new_lane_passes_positional_branch(tmp_path: Path, monkeypatch):
    from orca.tui.actions import new_lane
    calls: list[list[str]] = []

    class _CP:
        returncode = 0
        stdout = "ok"
        stderr = ""

    def fake_run(cmd, **kw):
        calls.append(cmd)
        return _CP()

    monkeypatch.setattr("subprocess.run", fake_run)
    res = new_lane(tmp_path, feature="my-feat", agent="none")
    # branch positional must be last; defaults to feature
    assert calls and calls[0][-1] == "my-feat", (
        f"expected branch positional last, got {calls[0]}"
    )
    assert "--feature" in calls[0]
    assert res.rc == 0


def test_open_editor_uses_parent_dir_when_target_is_file(tmp_path: Path, monkeypatch):
    from orca.tui.actions import open_editor
    target = tmp_path / "spec.md"
    target.write_text("# spec")

    captured: dict = {}
    def fake_call(cmd, cwd):
        captured["cmd"] = cmd
        captured["cwd"] = cwd
        return 0

    monkeypatch.setattr("subprocess.call", fake_call)
    open_editor(target)
    # cwd must be a real directory — the parent of the file, not the file itself
    assert Path(captured["cwd"]).is_dir(), f"cwd not a dir: {captured['cwd']}"
    assert captured["cwd"] == str(tmp_path), f"expected parent dir, got {captured['cwd']}"
    # target arg passed unchanged
    assert str(target) in captured["cmd"]


def test_open_editor_uses_target_when_directory(tmp_path: Path, monkeypatch):
    from orca.tui.actions import open_editor
    captured: dict = {}
    def fake_call(cmd, cwd):
        captured["cwd"] = cwd
        return 0

    monkeypatch.setattr("subprocess.call", fake_call)
    open_editor(tmp_path)
    assert captured["cwd"] == str(tmp_path)


def test_doctor_calls_orca_cli_wt_doctor(tmp_path: Path, monkeypatch):
    calls: list[list[str]] = []

    class _CP:
        returncode = 0
        stdout = "no issues"
        stderr = ""

    def fake_run(cmd, **kw):
        calls.append(cmd)
        return _CP()

    monkeypatch.setattr("subprocess.run", fake_run)
    res = doctor(tmp_path)
    assert calls and calls[0][:4] == ["orca-cli", "wt", "doctor", "--reap"]
    assert res.rc == 0

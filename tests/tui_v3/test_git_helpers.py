"""Git subprocess wrappers for drill-down."""
from pathlib import Path

from orca.tui.git import recent_commits, ahead_behind


def test_recent_commits_parses_log_output(tmp_path: Path, monkeypatch):
    sample = (
        "abc1234\t2 hours ago\talpha subject\n"
        "def5678\tyesterday\tbeta · subject with dot\n"
        "0a1b2c3\t3 days ago\tgamma\n"
    )

    class _CP:
        returncode = 0
        stdout = sample
        stderr = ""

    def fake_run(cmd, **kw):
        return _CP()

    monkeypatch.setattr("subprocess.run", fake_run)
    out = recent_commits(tmp_path, "feat-x", n=3)
    assert len(out) == 3
    assert out[0] == ("abc1234", "2 hours ago", "alpha subject")
    assert out[1] == ("def5678", "yesterday", "beta · subject with dot")


def test_recent_commits_empty_when_branch_missing(tmp_path: Path, monkeypatch):
    class _CP:
        returncode = 128
        stdout = ""
        stderr = "fatal: bad revision"

    def fake_run(cmd, **kw):
        return _CP()

    monkeypatch.setattr("subprocess.run", fake_run)
    out = recent_commits(tmp_path, "missing", n=20)
    assert out == []


def test_ahead_behind_parses_output(tmp_path: Path, monkeypatch):
    """git rev-list --left-right --count emits `<behind>\\t<ahead>`.
    Function contract: return (ahead, behind)."""
    class _CP:
        returncode = 0
        stdout = "3\t7\n"  # 3 commits behind, 7 ahead
        stderr = ""

    def fake_run(cmd, **kw):
        return _CP()

    monkeypatch.setattr("subprocess.run", fake_run)
    ab = ahead_behind(tmp_path, "feat-x", "main")
    assert ab == (7, 3), f"expected (ahead=7, behind=3), got {ab}"


def test_ahead_behind_none_when_git_fails(tmp_path: Path, monkeypatch):
    class _CP:
        returncode = 128
        stdout = ""
        stderr = "fatal: ambiguous"

    def fake_run(cmd, **kw):
        return _CP()

    monkeypatch.setattr("subprocess.run", fake_run)
    assert ahead_behind(tmp_path, "x", "main") is None

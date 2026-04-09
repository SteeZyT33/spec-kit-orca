from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


def _script_path() -> Path:
    return Path(__file__).resolve().parent / "assets" / "speckit-orca.sh"


def main() -> int:
    script = _script_path()
    if not script.is_file():
        print(f"speckit-orca launcher missing: {script}", file=sys.stderr)
        return 1

    completed = subprocess.run(["bash", str(script), *sys.argv[1:]])
    return completed.returncode


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

if ! command -v uv >/dev/null 2>&1; then
  echo "orca-matriarch.sh requires 'uv' in PATH" >&2
  exit 1
fi

# Resolve the speckit_orca Python package location. In the orca source repo
# it lives at REPO_ROOT. In a target project that installed orca as an
# extension, it lives under .specify/extensions/orca/. Check installed
# extension first so commands work in target projects by default.
if [[ -f "$REPO_ROOT/.specify/extensions/orca/pyproject.toml" ]]; then
  ORCA_PROJECT="$REPO_ROOT/.specify/extensions/orca"
elif [[ -f "$REPO_ROOT/pyproject.toml" ]] && grep -q "name = \"spec-kit-orca\"" "$REPO_ROOT/pyproject.toml" 2>/dev/null; then
  ORCA_PROJECT="$REPO_ROOT"
else
  echo "orca-matriarch.sh: unable to locate speckit_orca module (checked .specify/extensions/orca and $REPO_ROOT)" >&2
  exit 1
fi

repo_root="${PWD}"
args=()

while [[ $# -gt 0 ]]; do
  case "$1" in
    --repo-root)
      [[ $# -ge 2 ]] || {
        echo "orca-matriarch.sh: --repo-root requires a value" >&2
        exit 1
      }
      repo_root="$2"
      shift 2
      ;;
    *)
      args+=("$1")
      shift
      ;;
  esac
done

if [[ ${#args[@]} -gt 0 ]]; then
  exec uv run --project "$ORCA_PROJECT" python -m speckit_orca.matriarch --repo-root "$repo_root" "${args[@]}"
fi

exec uv run --project "$ORCA_PROJECT" python -m speckit_orca.matriarch --repo-root "$repo_root"

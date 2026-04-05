#!/usr/bin/env bash
set -euo pipefail

# setup.sh — Install spec-kit + orchestration on a new or existing project.
#
# Safe to run on existing projects — only adds extensions and skills,
# never deletes specs, plans, tasks, constitution, or git history.
#
# Usage:
#   bash setup.sh                          # Current dir, default claude
#   bash setup.sh /path/to/project         # Specific project
#   bash setup.sh . --ai codex             # Different AI agent
#   bash setup.sh . --minimal              # Orchestration only, no companions

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
DIM='\033[2m'
NC='\033[0m'

ok()   { echo -e "  ${GREEN}✓${NC} $1"; }
warn() { echo -e "  ${YELLOW}!${NC} $1"; }
fail() { echo -e "  ${RED}✗${NC} $1" >&2; exit 1; }
dim()  { echo -e "  ${DIM}$1${NC}"; }

# ── Parse args ────────────────────────────────────────────────────────────────
PROJECT="${1:-.}"
shift 2>/dev/null || true

AI="claude"
MINIMAL=0
while [[ $# -gt 0 ]]; do
  case "$1" in
    --ai)      AI="$2"; shift 2 ;;
    --minimal) MINIMAL=1; shift ;;
    *)         echo "Unknown: $1" >&2; exit 1 ;;
  esac
done

echo ""
echo "  spec-kit + orchestration setup"
echo "  ──────────────────────────────"
echo ""

# ── 1. Check CLI ──────────────────────────────────────────────────────────────
if ! command -v specify &>/dev/null; then
  fail "specify not found. Install: uv tool install specify-cli --from git+https://github.com/github/spec-kit.git"
fi
ok "specify CLI available"

# ── 2. Init or detect ─────────────────────────────────────────────────────────
PROJECT="$(cd "$PROJECT" 2>/dev/null && pwd || echo "$PROJECT")"

if [[ -d "$PROJECT/.specify" ]]; then
  ok "Existing project detected — will add extensions only"
else
  dim "Initializing new spec-kit project..."
  mkdir -p "$PROJECT"
  (cd "$PROJECT" && specify init --here --ai "$AI" --script sh --no-git 2>&1 | tail -1)
  ok "Project initialized (ai=$AI)"
fi

# ── 3. Install orchestration ─────────────────────────────────────────────────
ORCH_URL="https://github.com/SteeZyT33/spec-kit-orchestration/archive/refs/tags/v1.2.0.zip"

if [[ -d "$PROJECT/.specify/extensions/orchestration" ]]; then
  ok "Orchestration already installed"
else
  dim "Installing orchestration extension..."
  (cd "$PROJECT" && specify extension add orchestration --from "$ORCH_URL" 2>&1 | tail -1)
  ok "Orchestration installed (review, assign, crossreview, self-review)"
fi

# ── 4. Install companions + adopted ──────────────────────────────────────────
if [[ "$MINIMAL" == "1" ]]; then
  warn "Minimal mode — skipping companion extensions"
else
  EXTENSIONS=(
    # Companions (directly complement orchestration)
    "superb"
    "verify"
    "reconcile"
    "status"
    # Adopted (high-value gap fillers)
    "archive"
    "doctor"
    "fixit"
    "repoindex"
    "ship"
    "speckit-utils"
    "verify-tasks"
  )

  ADDED=0
  PRESENT=0
  FAILED=0

  for ext in "${EXTENSIONS[@]}"; do
    if [[ -d "$PROJECT/.specify/extensions/$ext" ]]; then
      ((PRESENT++))
    else
      if (cd "$PROJECT" && specify extension add "$ext" 2>/dev/null 1>/dev/null); then
        ((ADDED++))
      else
        ((FAILED++))
      fi
    fi
  done

  ok "Extensions: $ADDED added, $PRESENT already present, $FAILED unavailable"
fi

# ── 5. Done ───────────────────────────────────────────────────────────────────
echo ""
echo "  Done. Available commands:"
echo ""
echo "  Core:          /speckit.specify  /speckit.plan  /speckit.tasks  /speckit.implement"
echo "  Orchestration: /speckit.orchestration.review  .assign  .crossreview  .self-review"
if [[ "$MINIMAL" != "1" ]]; then
  echo "  Companions:    /speckit.superb.*  /speckit.verify.run  /speckit.reconcile.run"
  echo "  Adopted:       /speckit.ship.run  /speckit.fixit.run  /speckit.archive.run  ..."
fi
echo ""
echo "  Workflow: specify → plan → tasks → assign → implement → review → crossreview → self-review"
echo ""

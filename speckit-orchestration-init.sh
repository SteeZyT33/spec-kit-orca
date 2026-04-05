#!/usr/bin/env bash
set -euo pipefail

# speckit-orchestration-init.sh
#
# One-liner from inside any project:
#
#   curl -fsSL https://raw.githubusercontent.com/SteeZyT33/spec-kit-orchestration/main/speckit-orchestration-init.sh | bash
#   curl -fsSL https://raw.githubusercontent.com/SteeZyT33/spec-kit-orchestration/main/speckit-orchestration-init.sh | bash -s -- --ai codex
#   curl -fsSL https://raw.githubusercontent.com/SteeZyT33/spec-kit-orchestration/main/speckit-orchestration-init.sh | bash -s -- --minimal
#
# Safe on existing projects — only adds extensions and skills,
# never deletes specs, plans, tasks, constitution, or git history.

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
AI="claude"
MINIMAL=0
while [[ $# -gt 0 ]]; do
  case "$1" in
    --ai)      AI="$2"; shift 2 ;;
    --minimal) MINIMAL=1; shift ;;
    --help|-h)
      echo "Usage: speckit-orchestration-init.sh [--ai claude|codex|copilot|...] [--minimal]"
      echo ""
      echo "Run from inside any project directory."
      echo "Installs spec-kit + orchestration extension + companion extensions."
      echo ""
      echo "  --ai NAME    AI agent to configure (default: claude)"
      echo "  --minimal    Skip companion and adopted extensions"
      exit 0
      ;;
    *) echo "Unknown: $1 (try --help)" >&2; exit 1 ;;
  esac
done

ORCH_VERSION="v1.2.0"
ORCH_URL="https://github.com/SteeZyT33/spec-kit-orchestration/archive/refs/tags/${ORCH_VERSION}.zip"

echo ""
echo "  speckit-orchestration init"
echo "  ─────────────────────────"
echo ""

# ── 1. Check specify CLI ─────────────────────────────────────────────────────
if ! command -v specify &>/dev/null; then
  fail "specify CLI not found. Install: uv tool install specify-cli --from git+https://github.com/github/spec-kit.git"
fi
ok "specify CLI found"

# ── 2. Init or detect existing project ────────────────────────────────────────
if [[ -d ".specify" ]]; then
  ok "Existing spec-kit project detected"
else
  dim "Initializing spec-kit in $(basename "$(pwd)")..."
  specify init --here --ai "$AI" --script sh --no-git 2>&1 | tail -1
  ok "Spec-kit initialized (ai=$AI)"
fi

# ── 3. Install orchestration extension ────────────────────────────────────────
if [[ -d ".specify/extensions/orchestration" ]]; then
  ok "Orchestration already installed"
else
  dim "Installing orchestration ${ORCH_VERSION}..."
  specify extension add orchestration --from "$ORCH_URL" 2>&1 | tail -1
  ok "Orchestration: review, assign, crossreview, self-review"
fi

# ── 4. Install companions + adopted ──────────────────────────────────────────
if [[ "$MINIMAL" == "1" ]]; then
  warn "Minimal — skipping companion extensions"
else
  EXTENSIONS=(
    superb verify reconcile status
    archive doctor fixit repoindex ship speckit-utils verify-tasks
  )

  ADDED=0 PRESENT=0 UNAVAILABLE=0
  for ext in "${EXTENSIONS[@]}"; do
    if [[ -d ".specify/extensions/$ext" ]]; then
      ((PRESENT++))
    elif specify extension add "$ext" 2>/dev/null 1>/dev/null; then
      ((ADDED++))
    else
      ((UNAVAILABLE++))
    fi
  done
  ok "Extensions: $ADDED added, $PRESENT present, $UNAVAILABLE unavailable"
fi

# ── Done ──────────────────────────────────────────────────────────────────────
echo ""
echo "  Ready. Commands:"
echo ""
echo "    /speckit.specify                      Create feature spec"
echo "    /speckit.plan                         Generate implementation plan"
echo "    /speckit.tasks                        Break down into tasks"
echo "    /speckit.implement                    Execute tasks"
echo "    /speckit.orchestration.assign         Assign agents to tasks"
echo "    /speckit.orchestration.review         Post-implementation review"
echo "    /speckit.orchestration.crossreview    Cross-harness adversarial review"
echo "    /speckit.orchestration.self-review    Process retrospective"
echo ""

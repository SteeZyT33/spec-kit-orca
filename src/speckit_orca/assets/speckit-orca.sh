#!/usr/bin/env bash
set -euo pipefail

# speckit-orca
#
# Install spec-kit + orchestration layer for one or more AI agents.
#
#   speckit-orca                    # Default: claude
#   speckit-orca codex              # Different agent
#   speckit-orca --minimal claude   # No companion extensions
#   speckit-orca --list             # Show available agents
#   speckit-orca --install-self     # Install launcher to ~/.local/bin
#   speckit-orca --uninstall-self   # Remove launcher from ~/.local/bin
#
# Install this command:
#   curl -fsSL https://raw.githubusercontent.com/SteeZyT33/spec-kit-orchestration/main/speckit-orca | sudo tee /usr/local/bin/speckit-orca > /dev/null && sudo chmod +x /usr/local/bin/speckit-orca
#
# Or without sudo:
#   curl -fsSL https://raw.githubusercontent.com/SteeZyT33/spec-kit-orchestration/main/speckit-orca -o ~/.local/bin/speckit-orca && chmod +x ~/.local/bin/speckit-orca

VERSION="1.4.0"
ORCH_URL="https://github.com/SteeZyT33/spec-kit-orchestration/archive/refs/tags/v${VERSION}.zip"
SELF_PATH="$(readlink -f "${BASH_SOURCE[0]}")"
LOCAL_BIN="${HOME}/.local/bin"
LOCAL_LINK="${LOCAL_BIN}/speckit-orca"

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
DIM='\033[2m'
BOLD='\033[1m'
NC='\033[0m'

ok()   { echo -e "  ${GREEN}✓${NC} $1"; }
warn() { echo -e "  ${YELLOW}!${NC} $1"; }
fail() { echo -e "  ${RED}✗${NC} $1" >&2; exit 1; }
dim()  { echo -e "  ${DIM}$1${NC}"; }

install_self() {
  mkdir -p "$LOCAL_BIN"
  ln -sfn "$SELF_PATH" "$LOCAL_LINK"
  ok "Installed launcher: $LOCAL_LINK -> $SELF_PATH"
  if command -v speckit-orca >/dev/null 2>&1; then
    ok "Available on PATH as: $(command -v speckit-orca)"
  else
    warn "~/.local/bin is not active in this shell yet"
    echo "  Add to ~/.zshrc or ~/.shell.sh:"
    echo '    export PATH="$HOME/.local/bin:$PATH"'
  fi
}

uninstall_self() {
  if [[ -L "$LOCAL_LINK" || -f "$LOCAL_LINK" ]]; then
    rm -f "$LOCAL_LINK"
    ok "Removed launcher: $LOCAL_LINK"
  else
    warn "No launcher installed at $LOCAL_LINK"
  fi
}

refresh_catalog_extension() {
  local ext="$1"
  local label="${2:-$1}"

  if extension_registered "$ext"; then
    echo -ne "  ${DIM}  Refreshing ${label}...${NC}"
    if specify extension remove "$ext" --keep-config --force 1>/dev/null 2>&1 && \
       specify extension add "$ext" 1>/dev/null 2>&1; then
      echo -e "\r  ${GREEN}✓${NC} ${label}                    "
      return 0
    fi
    echo -e "\r  ${YELLOW}!${NC} ${label} — refresh failed   "
    return 1
  fi

  echo -ne "  ${DIM}  Adding ${label}...${NC}"
  if specify extension add "$ext" 1>/dev/null 2>&1; then
    echo -e "\r  ${GREEN}✓${NC} ${label}                    "
    return 0
  fi
  echo -e "\r  ${YELLOW}!${NC} ${label} — unavailable      "
  return 1
}

extension_registered() {
  local ext="$1"
  local registry=".specify/extensions/.registry"
  [[ -f "$registry" ]] || return 1

  python3 - "$registry" "$ext" <<'PY' >/dev/null 2>&1
import json
import sys

registry_path, ext = sys.argv[1], sys.argv[2]
with open(registry_path, "r", encoding="utf-8") as f:
    data = json.load(f)
extensions = data.get("extensions", {})
raise SystemExit(0 if ext in extensions else 1)
PY
}

KNOWN_AGENTS="claude codex copilot cursor-agent opencode windsurf junie amp auggie kiro-cli qodercli roo kilo bob shai gemini tabnine kimi generic"

# ── Parse args ────────────────────────────────────────────────────────────────
AGENTS=()
MINIMAL=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --install-self)
      install_self
      exit 0 ;;
    --uninstall-self)
      uninstall_self
      exit 0 ;;
    --minimal) MINIMAL=1; shift ;;
    --all)
      AGENTS=($KNOWN_AGENTS)
      shift ;;
    --list)
      echo "Available agents: $KNOWN_AGENTS"
      exit 0 ;;
    --help|-h)
      echo "Usage: speckit-orca [OPTIONS] [AGENT...]"
      echo ""
      echo "Set up spec-kit + orchestration in the current directory."
      echo "Supports multiple AI agents simultaneously."
      echo ""
      echo "Examples:"
      echo "  speckit-orca                     # claude (default)"
      echo "  speckit-orca codex               # different agent"
      echo "  speckit-orca --minimal claude    # no companion extensions"
      echo "  speckit-orca --install-self      # install launcher globally"
      echo ""
      echo "Options:"
      echo "  --install-self  Symlink this launcher into ~/.local/bin"
      echo "  --uninstall-self Remove ~/.local/bin/speckit-orca"
      echo "  --minimal    Skip companion and adopted extensions"
      echo "  --all        Install for all supported AI agents"
      echo "  --list       Show available agent names"
      exit 0 ;;
    -*)
      echo "Unknown option: $1 (try --help)" >&2; exit 1 ;;
    *)
      AGENTS+=("$1"); shift ;;
  esac
done

# Default to claude if no agents specified
if [[ ${#AGENTS[@]} -eq 0 ]]; then
  AGENTS=("claude")
fi

echo ""
echo -e "  ${BOLD}speckit-orca${NC}"
echo "  ──────────────────"
echo ""

# ── 1. Check specify CLI ─────────────────────────────────────────────────────
if ! command -v specify &>/dev/null; then
  fail "specify CLI not found. Install: uv tool install specify-cli --from git+https://github.com/github/spec-kit.git"
fi
ok "specify CLI found"

# ── 2. Init with first agent, add integrations for the rest ───────────────────
PRIMARY="${AGENTS[0]}"

if [[ -d ".specify" ]]; then
  ok "Existing spec-kit project"
else
  dim "Initializing with ${PRIMARY}..."
  specify init --here --ai "$PRIMARY" --script sh --no-git 2>&1 | tail -1
  ok "Initialized (primary: $PRIMARY)"
fi

# Note: spec-kit supports one active integration at a time.
# Multi-agent support would require upstream changes.
if [[ ${#AGENTS[@]} -gt 1 ]]; then
  warn "spec-kit supports one active integration at a time"
  warn "Primary agent: $PRIMARY (additional agents ignored: ${AGENTS[*]:1})"
  warn "To switch later: specify integration switch <agent>"
fi

# ── 2b. Ensure community catalog is install-allowed ──────────────────────────
CATALOG_FILE=".specify/extension-catalogs.yml"
if [[ ! -f "$CATALOG_FILE" ]]; then
  cat > "$CATALOG_FILE" << 'CATALOGS'
catalogs:
  - name: default
    url: https://raw.githubusercontent.com/github/spec-kit/main/extensions/catalog.json
    priority: 1
    install_allowed: true
  - name: community
    url: https://raw.githubusercontent.com/github/spec-kit/main/extensions/catalog.community.json
    priority: 2
    install_allowed: true
CATALOGS
  ok "Community catalog enabled"
fi

# ── 3. Install or update orchestration ────────────────────────────────────────
# Migrate from old "orchestration" ID to "orca" if needed
if [[ -d ".specify/extensions/orchestration" && ! -d ".specify/extensions/orca" ]]; then
  dim "Migrating from orchestration → orca..."
  specify extension remove orchestration --force 2>/dev/null 1>/dev/null
  ok "Old orchestration extension removed"
fi

if [[ -d ".specify/extensions/orca" ]]; then
  # Check installed version against this script's version
  INSTALLED_VER=$(grep -m1 '^  version:' .specify/extensions/orca/extension.yml 2>/dev/null | sed 's/.*"\(.*\)".*/\1/' || echo "0.0.0")
  if [[ "$INSTALLED_VER" == "$VERSION" || "$INSTALLED_VER" == "v${VERSION}" ]]; then
    dim "Refreshing orchestration v${INSTALLED_VER} for current integration..."
    specify extension remove orca --keep-config --force 2>/dev/null 1>/dev/null
    echo -ne "  ${DIM}  Reinstalling...${NC}"
    if specify extension add orca --from "$ORCH_URL" 1>/dev/null 2>&1; then
      echo -e "\r  ${GREEN}✓${NC} Orchestration v${VERSION} refreshed           "
    else
      echo -e "\r  ${RED}✗${NC} Refresh failed — try: specify extension add orca --from $ORCH_URL"
    fi
  else
    dim "Updating orchestration ${INSTALLED_VER} → v${VERSION}..."
    specify extension remove orca --keep-config --force 2>/dev/null 1>/dev/null
    echo -ne "  ${DIM}  Downloading...${NC}"
    if specify extension add orca --from "$ORCH_URL" 1>/dev/null 2>&1; then
      echo -e "\r  ${GREEN}✓${NC} Orchestration updated to v${VERSION}          "
    else
      echo -e "\r  ${RED}✗${NC} Update failed — try: specify extension add orca --from $ORCH_URL"
    fi
  fi
else
  echo -ne "  ${DIM}  Installing orchestration v${VERSION}...${NC}"
  if specify extension add orca --from "$ORCH_URL" 1>/dev/null 2>&1; then
    echo -e "\r  ${GREEN}✓${NC} Orchestration: brainstorm, micro-spec, code-review, pr-review, assign, cross-review, self-review          "
  else
    echo -e "\r  ${RED}✗${NC} Install failed — try: specify extension add orca --from $ORCH_URL"
  fi
fi

# ── 4. Companions + adopted ──────────────────────────────────────────────────
if [[ "$MINIMAL" == "1" ]]; then
  warn "Minimal — skipping companions"
else
  EXTENSIONS=(
    superb verify reconcile status
    archive doctor fixit repoindex ship speckit-utils verify-tasks
  )

  ADDED=0 PRESENT=0 UNAVAIL=0
  for ext in "${EXTENSIONS[@]}"; do
    if extension_registered "$ext"; then
      if refresh_catalog_extension "$ext"; then
        PRESENT=$((PRESENT + 1))
      else
        UNAVAIL=$((UNAVAIL + 1))
      fi
    else
      if refresh_catalog_extension "$ext"; then
        ADDED=$((ADDED + 1))
      else
        UNAVAIL=$((UNAVAIL + 1))
      fi
    fi
  done
  ok "Extensions: $ADDED added, $PRESENT refreshed, $UNAVAIL unavailable"
fi

# ── Done ──────────────────────────────────────────────────────────────────────
echo ""
echo -e "  ${BOLD}Agents:${NC} ${AGENTS[*]}"
echo ""
echo "  Core:  /speckit.specify  .plan  .tasks  .implement"
echo "  Orca:  /speckit.orca.brainstorm  .micro-spec  .assign  .code-review  .pr-review  .cross-review  .self-review"
echo ""
echo "  Workflow: brainstorm → specify → plan → tasks → assign → implement → code-review → cross-review → pr-review → self-review"
echo "            micro-spec → mini-plan → verification-plan → implement → code-review"
echo ""

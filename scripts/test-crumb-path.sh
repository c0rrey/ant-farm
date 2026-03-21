#!/usr/bin/env bash
# test-crumb-path.sh — Smoke-test CRUMB resolution in build-review-prompts.sh.
#
# Verifies that both execution contexts (repo-local and installed location) resolve
# a crumb binary that supports the render-template subcommand (AF-248).
#
# Usage:
#   bash scripts/test-crumb-path.sh
#
# Exit codes:
#   0 — both paths resolved to a working render-template binary
#   1 — one or both paths failed

set -euo pipefail

PASS=0
FAIL=1
overall=0

# ---------------------------------------------------------------------------
# Helper: test one resolution context
# ---------------------------------------------------------------------------
test_context() {
    local label="$1"
    local script_dir="$2"

    # Replicate the CRUMB resolution logic from build-review-prompts.sh
    local crumb_cmd
    if [ -f "${script_dir}/../crumb.py" ]; then
        crumb_cmd="python3 ${script_dir}/../crumb.py"
    elif [ -f "${HOME}/.local/bin/crumb" ]; then
        crumb_cmd="${HOME}/.local/bin/crumb"
    else
        crumb_cmd="crumb"
    fi

    printf '[%s] SCRIPT_DIR=%s → CRUMB="%s"\n' "$label" "$script_dir" "$crumb_cmd"

    if $crumb_cmd render-template --help >/dev/null 2>&1; then
        printf '[%s] render-template: PASS\n' "$label"
        return $PASS
    else
        printf '[%s] render-template: FAIL (binary does not support render-template)\n' "$label" >&2
        printf '[%s] Fix: run ./scripts/setup.sh to install the current crumb.py to ~/.local/bin/crumb\n' "$label" >&2
        return $FAIL
    fi
}

# ---------------------------------------------------------------------------
# Context 1: repo-local (running from scripts/ inside the repo)
# ---------------------------------------------------------------------------
REPO_SCRIPTS_DIR="$(cd "$(dirname "$0")" && pwd)"
if ! test_context "repo-local" "$REPO_SCRIPTS_DIR"; then
    overall=1
fi

echo ""

# ---------------------------------------------------------------------------
# Context 2: installed location (~/.claude/orchestration/scripts/)
# ---------------------------------------------------------------------------
INSTALLED_SCRIPTS_DIR="${HOME}/.claude/orchestration/scripts"
if [ ! -d "$INSTALLED_SCRIPTS_DIR" ]; then
    printf '[installed] SKIP — installed scripts dir not found: %s\n' "$INSTALLED_SCRIPTS_DIR"
    printf '[installed] Run ./scripts/setup.sh to install first.\n'
else
    if ! test_context "installed" "$INSTALLED_SCRIPTS_DIR"; then
        overall=1
    fi
fi

echo ""

# ---------------------------------------------------------------------------
# Result
# ---------------------------------------------------------------------------
if [ "$overall" -eq 0 ]; then
    echo "test-crumb-path.sh: ALL PASS — both execution contexts resolve a working crumb binary."
else
    echo "test-crumb-path.sh: FAIL — one or more contexts could not resolve a working crumb binary." >&2
    exit 1
fi

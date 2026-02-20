#!/usr/bin/env bash
# scrub-pii.sh — Scrub PII (email addresses) from issues.jsonl
#
# Usage:
#   ./scripts/scrub-pii.sh [--check]
#
# By default, replaces email addresses in the "owner" and "created_by" fields
# of .beads/issues.jsonl with the non-PII token "ctc".
#
# --check mode: exit 0 if no PII found, exit 1 if PII is present (for CI).
#
# Designed to run as a git pre-commit hook so that bd sync cannot commit
# raw email addresses.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
ISSUES_FILE="$REPO_ROOT/.beads/issues.jsonl"
CHECK_ONLY=false

for arg in "$@"; do
    case "$arg" in
        --check) CHECK_ONLY=true ;;
        *) echo "Unknown argument: $arg" >&2; exit 1 ;;
    esac
done

if [[ ! -f "$ISSUES_FILE" ]]; then
    echo "[scrub-pii] No issues.jsonl found at $ISSUES_FILE — skipping." >&2
    exit 0
fi

# Pattern: email addresses in any JSON string value.
# Using a conservative pattern that matches the known PII format.
PII_PATTERN='[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}'

if $CHECK_ONLY; then
    if grep -qE "$PII_PATTERN" "$ISSUES_FILE" 2>/dev/null; then
        echo "[scrub-pii] FAIL: PII (email addresses) found in $ISSUES_FILE" >&2
        exit 1
    else
        echo "[scrub-pii] OK: No PII found in $ISSUES_FILE"
        exit 0
    fi
fi

# Replace email addresses in JSON string values with the non-PII token "ctc".
# Uses perl for reliable in-place editing on macOS (BSD sed -i requires an
# extension argument; perl -i works cross-platform).
perl -i -pe 's/[a-zA-Z0-9._%+\-]+\@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}/ctc/g' "$ISSUES_FILE"

if grep -qE '[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}' "$ISSUES_FILE" 2>/dev/null; then
    REMAINING=$(grep -cE '[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}' "$ISSUES_FILE" 2>/dev/null)
    echo "[scrub-pii] WARNING: $REMAINING email patterns still present after scrub." >&2
    exit 1
fi

echo "[scrub-pii] PII scrub complete: $ISSUES_FILE"

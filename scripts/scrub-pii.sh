#!/usr/bin/env bash
# scrub-pii.sh — Scrub PII (email addresses) from issues.jsonl
#
# Usage:
#   ./scripts/scrub-pii.sh [--check]
#
# By default, replaces email addresses in the "owner" and "created_by" fields
# of .beads/issues.jsonl with the self-documenting token "[REDACTED]".
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

# Pattern: email addresses in "owner" or "created_by" JSON field values only.
# Scoped to prevent accidental redaction of emails in titles, descriptions, or URLs.
#
# Coverage note: local-part matches common characters used by machine-generated
# addresses (GitHub, GitLab, CI systems, bd sync). RFC 5321 quoted local parts
# (e.g. "user name"@example.com) and uncommon special characters are intentionally
# excluded — they do not appear in this codebase's typical data sources and
# broadening the pattern adds maintenance complexity for negligible real-world gain.
PII_FIELD_PATTERN='"(owner|created_by)"\s*:\s*"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}"'

if $CHECK_ONLY; then
    if grep -qE "$PII_FIELD_PATTERN" "$ISSUES_FILE" 2>/dev/null; then
        echo "[scrub-pii] FAIL: PII (email addresses) found in owner/created_by fields in $ISSUES_FILE" >&2
        exit 1
    else
        echo "[scrub-pii] OK: No PII found in $ISSUES_FILE"
        exit 0
    fi
fi

# Replace email addresses in "owner" and "created_by" field values with the
# self-documenting token "[REDACTED]". Scoped substitution prevents touching
# emails that legitimately appear in other fields (titles, descriptions, URLs).
# Uses perl for reliable in-place editing on macOS (BSD sed -i requires an
# extension argument; perl -i works cross-platform).
perl -i -pe 's/("(?:owner|created_by)"\s*:\s*")[a-zA-Z0-9._%+\-]+\@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}(")/${1}[REDACTED]$2/g' "$ISSUES_FILE"

if grep -qE '"(owner|created_by)"\s*:\s*"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}"' "$ISSUES_FILE" 2>/dev/null; then
    REMAINING=$(grep -cE '"(owner|created_by)"\s*:\s*"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}"' "$ISSUES_FILE" 2>/dev/null)
    echo "[scrub-pii] WARNING: $REMAINING email patterns still present in owner/created_by fields after scrub." >&2
    exit 1
fi

echo "[scrub-pii] PII scrub complete: $ISSUES_FILE"

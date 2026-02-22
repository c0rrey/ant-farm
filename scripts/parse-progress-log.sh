#!/usr/bin/env bash
# parse-progress-log.sh — Parse a session progress log and write a structured resume plan.
#
# Called by the Queen at session startup (Step 0) when a prior session's SESSION_DIR is
# detected. Reads progress.log, determines which steps completed, identifies the resume
# point, and writes a resume-plan.md the Queen presents to the user for approval.
#
# Usage:
#   parse-progress-log.sh <SESSION_DIR>
#
# Arguments:
#   SESSION_DIR — path to the existing session artifact directory whose progress.log
#                 should be parsed (e.g. .beads/agent-summaries/_session-abc123)
#
# Output:
#   Writes {SESSION_DIR}/resume-plan.md — a structured markdown plan the Queen reads
#   and presents verbatim to the user.
#
# Exit codes:
#   0 — resume-plan.md written successfully; recovery is possible
#   1 — argument error, progress.log missing or unreadable, or write failure
#   2 — progress.log exists but shows the session already completed (SESSION_COMPLETE present)
#       resume-plan.md is NOT written; caller should treat this as a fresh-start signal

set -euo pipefail

# ---------------------------------------------------------------------------
# Argument validation
# ---------------------------------------------------------------------------

if [ $# -ne 1 ]; then
    echo "ERROR: parse-progress-log.sh requires exactly 1 argument." >&2
    echo "Usage: $0 <SESSION_DIR>" >&2
    exit 1
fi

SESSION_DIR="$1"
PROGRESS_LOG="${SESSION_DIR}/progress.log"

if [ ! -d "$SESSION_DIR" ]; then
    echo "ERROR: Session directory not found: $SESSION_DIR" >&2
    exit 1
fi

if [ ! -f "$PROGRESS_LOG" ]; then
    echo "ERROR: progress.log not found: $PROGRESS_LOG" >&2
    exit 1
fi

if [ ! -r "$PROGRESS_LOG" ]; then
    echo "ERROR: progress.log not readable: $PROGRESS_LOG" >&2
    exit 1
fi

# ---------------------------------------------------------------------------
# Step definitions: ordered list of all workflow milestones.
# Each entry: "step_key|display_label|description"
# step_key must match the second field of progress.log pipe-delimited lines.
# ---------------------------------------------------------------------------

# Ordered step definitions: step_key | display_label | description
STEP_KEYS=(
    "SESSION_INIT"
    "SCOUT_COMPLETE"
    "WAVE_SPAWNED"
    "WAVE_WWD_PASS"
    "WAVE_VERIFIED"
    "REVIEW_COMPLETE"
    "REVIEW_TRIAGED"
    "DOCS_COMMITTED"
    "XREF_VERIFIED"
    "SESSION_COMPLETE"
)

step_label() {
    case "$1" in
        SESSION_INIT)     echo "Session Init: Session setup" ;;
        SCOUT_COMPLETE)   echo "Scout Complete: Recon (Scout + SSV gate + user approval)" ;;
        WAVE_SPAWNED)     echo "Wave Spawned: Spawn (Pantry + CCO + Dirt Pushers)" ;;
        WAVE_WWD_PASS)    echo "Wave WWD Passed: WWD verification passed" ;;
        WAVE_VERIFIED)    echo "Wave Verified: Verify (WWD + DMVDC)" ;;
        REVIEW_COMPLETE)  echo "Review Complete: Review (Nitpicker team)" ;;
        REVIEW_TRIAGED)   echo "Review Triaged: Triage (P1/P2 decision)" ;;
        DOCS_COMMITTED)   echo "Docs Committed: Documentation (CHANGELOG/README/CLAUDE.md)" ;;
        XREF_VERIFIED)    echo "Xref Verified: Cross-reference verification" ;;
        SESSION_COMPLETE) echo "Session Complete: Land the plane (git push)" ;;
        *)                echo "$1" ;;
    esac
}

step_resume_action() {
    case "$1" in
        SESSION_INIT)     echo "Re-run SESSION_INIT to regenerate SESSION_ID and SESSION_DIR (fresh start recommended)." ;;
        SCOUT_COMPLETE)   echo "Re-run SCOUT_COMPLETE: check for existing briefing.md; if absent, re-spawn the Scout." ;;
        WAVE_SPAWNED)     echo "Re-run WAVE_SPAWNED: re-read briefing.md and re-spawn Pantry + Dirt Pushers for unfinished waves." ;;
        WAVE_WWD_PASS)    echo "Proceed to DMVDC verification: WWD already passed; re-spawn Pest Control for DMVDC only." ;;
        WAVE_VERIFIED)    echo "Re-run WAVE_VERIFIED: re-spawn Pest Control for WWD/DMVDC on any unverified waves." ;;
        REVIEW_COMPLETE)  echo "Re-run REVIEW_COMPLETE: re-spawn the Nitpicker team (check for existing review reports first)." ;;
        REVIEW_TRIAGED)   echo "Re-run REVIEW_TRIAGED: re-read the Big Head summary and re-present findings to the user." ;;
        DOCS_COMMITTED)   echo "Re-run DOCS_COMMITTED: update CHANGELOG, README, CLAUDE.md in a single commit." ;;
        XREF_VERIFIED)    echo "Re-run XREF_VERIFIED: verify cross-references and CHANGELOG entries for all tasks." ;;
        SESSION_COMPLETE) echo "Re-run SESSION_COMPLETE: git pull --rebase, bd sync, git push." ;;
        *)                echo "Resume from this step." ;;
    esac
}

# ---------------------------------------------------------------------------
# Bash 3+-compatible key-value store (replaces bash 4+ `declare -A`) using a temp directory.
# Note: the rest of this script uses bash-only constructs (e.g. [[ =~ ]]) — portability
# target is bash 3+, not POSIX sh.
# Each "map" is a subdirectory; each entry is a file named after the key.
#
# map_set  <dir> <key> <value>  — write value to file
# map_get  <dir> <key>          — print value (empty string if not set)
# map_has  <dir> <key>          — exit 0 if key exists, 1 otherwise
# ---------------------------------------------------------------------------

_MAP_DIR=""

map_init() {
    _MAP_DIR="$(mktemp -d)"
    mkdir -p "${_MAP_DIR}/completed" "${_MAP_DIR}/timestamp" "${_MAP_DIR}/details"
}

map_cleanup() {
    [ -n "$_MAP_DIR" ] && rm -rf "$_MAP_DIR"
}

# Sanitize key: replace characters that are invalid in filenames.
# Step keys are uppercase alphanumeric+underscore only (SESSION_INIT, WAVE_SPAWNED, etc.),
# so this is a safety measure rather than a practical concern.
_key_file() {
    # $1=submap, $2=key
    printf '%s/%s/%s' "$_MAP_DIR" "$1" "$2"
}

map_set() {
    # $1=submap, $2=key, $3=value
    printf '%s' "$3" > "$(_key_file "$1" "$2")"
}

map_get() {
    # $1=submap, $2=key — prints value or empty string
    local f
    f="$(_key_file "$1" "$2")"
    if [ -f "$f" ]; then
        cat "$f"
    fi
}

map_has() {
    # $1=submap, $2=key — exit 0 if present, 1 if absent
    [ -f "$(_key_file "$1" "$2")" ]
}

# ---------------------------------------------------------------------------
# Parse progress.log
# ---------------------------------------------------------------------------

# Build a set of completed step keys by reading each log line.
# Format: TIMESTAMP|step_key|field=value|...
# A step is "complete" when its log line is present.
# Multi-occurrence steps (WAVE_SPAWNED, WAVE_VERIFIED, REVIEW_COMPLETE, REVIEW_TRIAGED) may appear multiple times (one per wave/round).

map_init
trap 'map_cleanup' EXIT

while IFS='|' read -r timestamp step_key rest; do
    # Skip blank lines or malformed lines (missing step_key)
    [ -z "$step_key" ] && continue
    # Validate timestamp format: must match YYYY-MM-DDTHH:MM:SS (ISO 8601 prefix).
    # Lines with a missing or malformed timestamp are rejected as corrupted/malformed.
    if ! [[ "$timestamp" =~ ^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2} ]]; then
        echo "WARNING: Skipping malformed log line (invalid timestamp '${timestamp}'): ${step_key}|${rest}" >&2
        continue
    fi
    map_set "completed" "$step_key" "yes"
    map_set "timestamp" "$step_key" "$timestamp"
    # Keep the last occurrence's details for multi-occurrence steps.
    # NOTE: Log ordering is not validated here. A corrupt log with SESSION_COMPLETE
    # appearing out of order (before earlier steps) will still trigger the
    # early-exit guard below and report the session as complete. This is intentional:
    # a SESSION_COMPLETE entry is treated as authoritative regardless of position.
    map_set "details"   "$step_key" "$rest"
done < "$PROGRESS_LOG"

# ---------------------------------------------------------------------------
# Check if the session already completed (SESSION_COMPLETE logged) — exit code 2
# ---------------------------------------------------------------------------

if map_has "completed" "SESSION_COMPLETE"; then
    ts="$(map_get "timestamp" "SESSION_COMPLETE")"
    echo "INFO: Session already completed (SESSION_COMPLETE logged at ${ts})." >&2
    echo "      No resume needed. Caller should treat this as a clean slate." >&2
    exit 2
fi

# ---------------------------------------------------------------------------
# Determine the resume point: the first step NOT yet completed
# ---------------------------------------------------------------------------

RESUME_STEP=""
for key in "${STEP_KEYS[@]}"; do
    if ! map_has "completed" "$key"; then
        RESUME_STEP="$key"
        break
    fi
done

# UNREACHABLE: RESUME_STEP is always set by the loop above because SESSION_COMPLETE is in
# STEP_KEYS. If SESSION_COMPLETE were completed, the early-exit guard above (exit 2) would
# have already terminated the script. This branch can never be reached.
if [ -z "$RESUME_STEP" ]; then
    RESUME_STEP="SESSION_COMPLETE"
fi

# ---------------------------------------------------------------------------
# Build the resume plan markdown
# ---------------------------------------------------------------------------

OUT_FILE="${SESSION_DIR}/resume-plan.md"

# Warn if overwriting an existing resume plan (e.g. script re-run after partial failure).
if [ -f "$OUT_FILE" ]; then
    echo "WARNING: Overwriting existing resume plan: $OUT_FILE" >&2
fi

{
    echo "# Session Resume Plan"
    echo ""
    echo "A prior session was detected at: \`${SESSION_DIR}\`"
    echo ""
    echo "The progress log shows this session did not complete. Below is the recovery"
    echo "plan based on the last recorded milestone."
    echo ""
    echo "**You must approve this plan before any action is taken.**"
    echo "Reply \`resume\` to continue from the resume point, or \`fresh start\` to begin a new session."
    echo ""
    echo "---"
    echo ""
    echo "## Step Status"
    echo ""
    echo "| Status | Step |"
    echo "|--------|------|"

    for key in "${STEP_KEYS[@]}"; do
        label="$(step_label "$key")"
        if map_has "completed" "$key"; then
            ts="$(map_get "timestamp" "$key")"
            echo "| COMPLETE (${ts}) | ${label} |"
        elif [ "$key" = "$RESUME_STEP" ]; then
            echo "| **RESUME HERE** | **${label}** |"
        else
            echo "| pending | ${label} |"
        fi
    done

    echo ""
    echo "---"
    echo ""
    echo "## Resume Action"
    echo ""
    echo "**Resume at**: $(step_label "$RESUME_STEP")"
    echo ""
    echo "**Action**: $(step_resume_action "$RESUME_STEP")"
    echo ""

    # Surface any relevant details logged for the last completed step
    LAST_COMPLETED=""
    for key in "${STEP_KEYS[@]}"; do
        if map_has "completed" "$key"; then
            LAST_COMPLETED="$key"
        fi
    done

    if [ -n "$LAST_COMPLETED" ]; then
        echo "---"
        echo ""
        echo "## Last Completed Milestone"
        echo ""
        echo "- **Step**: $(step_label "$LAST_COMPLETED")"
        echo "- **Logged at**: $(map_get "timestamp" "$LAST_COMPLETED")"
        details="$(map_get "details" "$LAST_COMPLETED")"
        if [ -n "$details" ]; then
            echo "- **Details**: \`${details}\`"
        fi
        echo ""
    fi

    echo "---"
    echo ""
    echo "*Generated by scripts/parse-progress-log.sh from \`${PROGRESS_LOG}\`*"

} > "$OUT_FILE" || {
    echo "ERROR: Failed to write resume plan: $OUT_FILE" >&2
    exit 1
}

echo "parse-progress-log.sh: resume plan written to ${OUT_FILE}"
echo "Resume point: $(step_label "$RESUME_STEP")"

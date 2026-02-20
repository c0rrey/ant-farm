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
#   2 — progress.log exists but shows the session already completed (step6 present)
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
    "step0"
    "step1"
    "step2"
    "step3"
    "step3b"
    "step3c"
    "step4"
    "step5"
    "step6"
)

step_label() {
    case "$1" in
        step0)  echo "Step 0: Session setup" ;;
        step1)  echo "Step 1: Recon (Scout + SSV gate + user approval)" ;;
        step2)  echo "Step 2: Spawn (Pantry + CCO + Dirt Pushers)" ;;
        step3)  echo "Step 3: Verify (WWD + DMVDC)" ;;
        step3b) echo "Step 3b: Review (Nitpicker team)" ;;
        step3c) echo "Step 3c: Triage (P1/P2 decision)" ;;
        step4)  echo "Step 4: Documentation (CHANGELOG/README/CLAUDE.md)" ;;
        step5)  echo "Step 5: Cross-reference verification" ;;
        step6)  echo "Step 6: Land the plane (git push)" ;;
        *)      echo "$1" ;;
    esac
}

step_resume_action() {
    case "$1" in
        step0)  echo "Re-run Step 0 to regenerate SESSION_ID and SESSION_DIR (fresh start recommended)." ;;
        step1)  echo "Re-run Step 1: check for existing briefing.md; if absent, re-spawn the Scout." ;;
        step2)  echo "Re-run Step 2: re-read briefing.md and re-spawn Pantry + Dirt Pushers for unfinished waves." ;;
        step3)  echo "Re-run Step 3: re-spawn Pest Control for WWD/DMVDC on any unverified waves." ;;
        step3b) echo "Re-run Step 3b: re-spawn the Nitpicker team (check for existing review reports first)." ;;
        step3c) echo "Re-run Step 3c: re-read the Big Head summary and re-present findings to the user." ;;
        step4)  echo "Re-run Step 4: update CHANGELOG, README, CLAUDE.md in a single commit." ;;
        step5)  echo "Re-run Step 5: verify cross-references and CHANGELOG entries for all tasks." ;;
        step6)  echo "Re-run Step 6: git pull --rebase, bd sync, git push." ;;
        *)      echo "Resume from this step." ;;
    esac
}

# ---------------------------------------------------------------------------
# Parse progress.log
# ---------------------------------------------------------------------------

# Build a set of completed step keys by reading each log line.
# Format: TIMESTAMP|step_key|field=value|...
# A step is "complete" when its log line is present.
# Multi-occurrence steps (step2, step3, step3b, step3c) may appear multiple times (one per wave/round).

declare -A STEP_COMPLETED
declare -A STEP_TIMESTAMP
declare -A STEP_DETAILS

while IFS='|' read -r timestamp step_key rest; do
    # Skip blank lines or malformed lines
    [ -z "$step_key" ] && continue
    STEP_COMPLETED["$step_key"]="yes"
    STEP_TIMESTAMP["$step_key"]="$timestamp"
    # Keep the last occurrence's details for multi-occurrence steps
    STEP_DETAILS["$step_key"]="$rest"
done < "$PROGRESS_LOG"

# ---------------------------------------------------------------------------
# Check if the session already completed (step6 logged) — exit code 2
# ---------------------------------------------------------------------------

if [ "${STEP_COMPLETED[step6]+set}" = "set" ]; then
    echo "INFO: Session already completed (step6 logged at ${STEP_TIMESTAMP[step6]})." >&2
    echo "      No resume needed. Caller should treat this as a clean slate." >&2
    exit 2
fi

# ---------------------------------------------------------------------------
# Determine the resume point: the first step NOT yet completed
# ---------------------------------------------------------------------------

RESUME_STEP=""
for key in "${STEP_KEYS[@]}"; do
    if [ "${STEP_COMPLETED[$key]+set}" != "set" ]; then
        RESUME_STEP="$key"
        break
    fi
done

# If every step except step6 is done but step6 is absent, resume at step6
if [ -z "$RESUME_STEP" ]; then
    RESUME_STEP="step6"
fi

# ---------------------------------------------------------------------------
# Build the resume plan markdown
# ---------------------------------------------------------------------------

OUT_FILE="${SESSION_DIR}/resume-plan.md"

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
        if [ "${STEP_COMPLETED[$key]+set}" = "set" ]; then
            ts="${STEP_TIMESTAMP[$key]}"
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
        if [ "${STEP_COMPLETED[$key]+set}" = "set" ]; then
            LAST_COMPLETED="$key"
        fi
    done

    if [ -n "$LAST_COMPLETED" ]; then
        echo "---"
        echo ""
        echo "## Last Completed Milestone"
        echo ""
        echo "- **Step**: $(step_label "$LAST_COMPLETED")"
        echo "- **Logged at**: ${STEP_TIMESTAMP[$LAST_COMPLETED]}"
        if [ -n "${STEP_DETAILS[$LAST_COMPLETED]:-}" ]; then
            echo "- **Details**: \`${STEP_DETAILS[$LAST_COMPLETED]}\`"
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

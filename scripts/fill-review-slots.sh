#!/usr/bin/env bash
# fill-review-slots.sh — Script 2: fill slot markers in review skeleton files.
#
# Called by the Queen after all dirt-pushers finish (RULES.md Step 3b), instead of
# spawning a second Pantry (pantry-review) for review prompt composition.
#
# Reads skeleton files from {SESSION_DIR}/review-skeletons/ (written by Script 1),
# fills {{SLOT_NAME}} markers with actual values, and writes:
#   - Final review prompts  → {SESSION_DIR}/prompts/review-{type}.md
#   - Combined previews     → {SESSION_DIR}/previews/review-{type}-preview.md
#   - Big Head data file    → {SESSION_DIR}/prompts/review-big-head-consolidation.md
#
# Returns exit code only. Queen never reads file contents — paths are echoed to stdout.
#
# Usage:
#   fill-review-slots.sh <SESSION_DIR> <COMMIT_RANGE> <CHANGED_FILES_LIST> \
#                        <TASK_IDS_LIST> <TIMESTAMP> <REVIEW_ROUND>
#
# Arguments:
#   SESSION_DIR          — session artifact directory
#   COMMIT_RANGE         — git commit range, e.g. "abc1234..HEAD"
#   CHANGED_FILES_LIST   — newline-separated list of changed files (quote or use a file path)
#   TASK_IDS_LIST        — space-separated list of task IDs, e.g. "ant-farm-9oa ant-farm-7b2"
#   TIMESTAMP            — review timestamp in YYYYMMDD-HHmmss format (Queen generates once per cycle)
#   REVIEW_ROUND         — integer: 1, 2, 3, ...
#
# Note on CHANGED_FILES_LIST and TASK_IDS_LIST:
#   Pass them as file paths prefixed with "@" to avoid shell quoting issues with newlines:
#     fill-review-slots.sh ... @/tmp/changed-files.txt @/tmp/task-ids.txt ...
#   Or pass literal values (quoted) for simple cases.
#
# Exit codes:
#   0 — all prompts and previews written successfully
#   1 — missing argument, missing skeleton file, or write failure

set -euo pipefail

# ---------------------------------------------------------------------------
# Argument validation
# ---------------------------------------------------------------------------

if [ $# -ne 6 ]; then
    echo "ERROR: fill-review-slots.sh requires exactly 6 arguments." >&2
    echo "Usage: $0 <SESSION_DIR> <COMMIT_RANGE> <CHANGED_FILES_LIST> <TASK_IDS_LIST> <TIMESTAMP> <REVIEW_ROUND>" >&2
    exit 1
fi

SESSION_DIR="$1"
COMMIT_RANGE="$2"
CHANGED_FILES_RAW="$3"
TASK_IDS_RAW="$4"
TIMESTAMP="$5"
REVIEW_ROUND="$6"

# ---------------------------------------------------------------------------
# Resolve @file arguments for multiline values
# ---------------------------------------------------------------------------

resolve_arg() {
    local val="$1"
    if [[ "$val" == @* ]]; then
        local fpath="${val:1}"
        if [ ! -f "$fpath" ]; then
            echo "ERROR: @file argument not found: $fpath" >&2
            exit 1
        fi
        cat "$fpath"
    else
        printf '%s' "$val"
    fi
}

CHANGED_FILES="$(resolve_arg "$CHANGED_FILES_RAW")"
TASK_IDS="$(resolve_arg "$TASK_IDS_RAW")"

# ---------------------------------------------------------------------------
# Validate review round
# ---------------------------------------------------------------------------

if ! echo "$REVIEW_ROUND" | grep -qE '^[0-9]+$'; then
    echo "ERROR: REVIEW_ROUND must be a positive integer, got: $REVIEW_ROUND" >&2
    exit 1
fi

# ---------------------------------------------------------------------------
# Validate skeleton directory exists
# ---------------------------------------------------------------------------

SKELETON_DIR="${SESSION_DIR}/review-skeletons"
if [ ! -d "$SKELETON_DIR" ]; then
    echo "ERROR: Skeleton directory not found: $SKELETON_DIR" >&2
    echo "       Run compose-review-skeletons.sh first (Pantry Section 1)." >&2
    exit 1
fi

# ---------------------------------------------------------------------------
# Validate required skeleton files exist
# ---------------------------------------------------------------------------

REQUIRED_SKELETONS=(
    "${SKELETON_DIR}/skeleton-clarity.md"
    "${SKELETON_DIR}/skeleton-edge-cases.md"
    "${SKELETON_DIR}/skeleton-correctness.md"
    "${SKELETON_DIR}/skeleton-excellence.md"
    "${SKELETON_DIR}/skeleton-big-head.md"
)

for f in "${REQUIRED_SKELETONS[@]}"; do
    if [ ! -f "$f" ]; then
        echo "ERROR: Required skeleton file missing: $f" >&2
        echo "       Run compose-review-skeletons.sh to regenerate skeletons." >&2
        exit 1
    fi
done

# ---------------------------------------------------------------------------
# Output directory setup
# ---------------------------------------------------------------------------

mkdir -p "${SESSION_DIR}/prompts" || {
    echo "ERROR: Failed to create prompts directory: ${SESSION_DIR}/prompts" >&2
    exit 1
}
mkdir -p "${SESSION_DIR}/previews" || {
    echo "ERROR: Failed to create previews directory: ${SESSION_DIR}/previews" >&2
    exit 1
}
mkdir -p "${SESSION_DIR}/review-reports" || {
    echo "ERROR: Failed to create review-reports directory: ${SESSION_DIR}/review-reports" >&2
    exit 1
}

# ---------------------------------------------------------------------------
# Determine which review types to produce based on round
# ---------------------------------------------------------------------------

if [ "$REVIEW_ROUND" -eq 1 ]; then
    ACTIVE_REVIEW_TYPES=(clarity edge-cases correctness excellence)
else
    # Round 2+: correctness and edge-cases only
    ACTIVE_REVIEW_TYPES=(correctness edge-cases)
fi

# ---------------------------------------------------------------------------
# Helper: safe sed substitution for multiline values.
# Uses a temp file to avoid issues with special characters in sed replacement strings.
# Strategy: write slot value to a temp file, use Python for the substitution if available,
# otherwise fall back to a safe awk-based replacement.
# ---------------------------------------------------------------------------

fill_slot() {
    local slot="$1"     # e.g. {{COMMIT_RANGE}}
    local value="$2"    # the value to substitute
    local file="$3"     # file to perform in-place substitution on

    # Use a temp file for the replacement value to avoid sed special-char issues
    local tmpval
    tmpval="$(mktemp)"
    printf '%s' "$value" > "$tmpval"

    # Use awk for safe multiline substitution
    # awk reads the replacement from the temp file, avoids regex escaping issues
    awk -v slot="$slot" -v valfile="$tmpval" '
    BEGIN {
        # Read the full replacement value from file
        val = ""
        while ((getline line < valfile) > 0) {
            if (val != "") val = val "\n"
            val = val line
        }
        close(valfile)
    }
    {
        # Replace all occurrences of slot in each line
        while (index($0, slot) > 0) {
            sub(slot, val)
        }
        print
    }
    ' "$file" > "${file}.tmp" && mv "${file}.tmp" "$file"

    rm -f "$tmpval"
}

# ---------------------------------------------------------------------------
# Helper: write a filled review prompt for one review type
# ---------------------------------------------------------------------------

write_filled_review() {
    local review_type="$1"
    local skeleton_file="${SKELETON_DIR}/skeleton-${review_type}.md"
    local out_prompt="${SESSION_DIR}/prompts/review-${review_type}.md"
    local out_preview="${SESSION_DIR}/previews/review-${review_type}-preview.md"
    local report_output_path="${SESSION_DIR}/review-reports/${review_type}-review-${TIMESTAMP}.md"
    local data_file_path="${SESSION_DIR}/prompts/review-${review_type}.md"

    # Copy skeleton to output prompt file
    cp "$skeleton_file" "$out_prompt" || {
        echo "ERROR: Failed to copy skeleton for ${review_type}: $skeleton_file -> $out_prompt" >&2
        exit 1
    }

    # Fill all slot markers
    fill_slot "{{COMMIT_RANGE}}"        "$COMMIT_RANGE"          "$out_prompt"
    fill_slot "{{CHANGED_FILES}}"       "$CHANGED_FILES"         "$out_prompt"
    fill_slot "{{TASK_IDS}}"            "$TASK_IDS"              "$out_prompt"
    fill_slot "{{TIMESTAMP}}"           "$TIMESTAMP"             "$out_prompt"
    fill_slot "{{REVIEW_ROUND}}"        "$REVIEW_ROUND"          "$out_prompt"
    fill_slot "{{REPORT_OUTPUT_PATH}}"  "$report_output_path"    "$out_prompt"
    fill_slot "{{DATA_FILE_PATH}}"      "$data_file_path"        "$out_prompt"

    # Write combined preview (same content — the Nitpicker skeleton is already the combined format)
    cp "$out_prompt" "$out_preview" || {
        echo "ERROR: Failed to write preview for ${review_type}: $out_preview" >&2
        exit 1
    }

    echo "  Prompt:  $out_prompt"
    echo "  Preview: $out_preview"
    echo "  Report will be written to: $report_output_path"
}

# ---------------------------------------------------------------------------
# Helper: write the filled Big Head consolidation brief
# ---------------------------------------------------------------------------

write_big_head_brief() {
    local skeleton_file="${SKELETON_DIR}/skeleton-big-head.md"
    local out_file="${SESSION_DIR}/prompts/review-big-head-consolidation.md"
    local consolidated_output="${SESSION_DIR}/review-reports/review-consolidated-${TIMESTAMP}.md"

    # Build the expected report paths list (round-appropriate)
    local expected_paths=""
    for rt in "${ACTIVE_REVIEW_TYPES[@]}"; do
        expected_paths="${expected_paths}- ${SESSION_DIR}/review-reports/${rt}-review-${TIMESTAMP}.md\n"
    done
    # Remove trailing \n left by the loop
    expected_paths="$(printf '%b' "$expected_paths" | sed '/^$/d')"

    cp "$skeleton_file" "$out_file" || {
        echo "ERROR: Failed to copy Big Head skeleton: $skeleton_file -> $out_file" >&2
        exit 1
    }

    fill_slot "{{REVIEW_ROUND}}"              "$REVIEW_ROUND"          "$out_file"
    fill_slot "{{TIMESTAMP}}"                 "$TIMESTAMP"             "$out_file"
    fill_slot "{{DATA_FILE_PATH}}"            "$out_file"              "$out_file"
    fill_slot "{{CONSOLIDATED_OUTPUT_PATH}}"  "$consolidated_output"   "$out_file"
    fill_slot "{{EXPECTED_REPORT_PATHS}}"     "$expected_paths"        "$out_file"

    echo "  Big Head brief: $out_file"
    echo "  Consolidated output will be: $consolidated_output"
}

# ---------------------------------------------------------------------------
# Main execution
# ---------------------------------------------------------------------------

echo "fill-review-slots.sh: filling review prompt slots (round ${REVIEW_ROUND})"
echo "  Session dir:   ${SESSION_DIR}"
echo "  Commit range:  ${COMMIT_RANGE}"
echo "  Timestamp:     ${TIMESTAMP}"
echo "  Active reviews: ${ACTIVE_REVIEW_TYPES[*]}"
echo ""

for review_type in "${ACTIVE_REVIEW_TYPES[@]}"; do
    echo "Processing: ${review_type}"
    write_filled_review "$review_type"
    echo ""
done

echo "Processing: big-head"
write_big_head_brief
echo ""

# ---------------------------------------------------------------------------
# Verify all output files were written and are non-empty
# ---------------------------------------------------------------------------

echo "fill-review-slots.sh: verifying output files..."

ALL_OK=true
for review_type in "${ACTIVE_REVIEW_TYPES[@]}"; do
    for f in \
        "${SESSION_DIR}/prompts/review-${review_type}.md" \
        "${SESSION_DIR}/previews/review-${review_type}-preview.md"
    do
        if [ ! -f "$f" ]; then
            echo "ERROR: Expected output file missing: $f" >&2
            ALL_OK=false
        elif [ ! -s "$f" ]; then
            echo "ERROR: Output file is empty: $f" >&2
            ALL_OK=false
        fi
    done
done

if [ ! -f "${SESSION_DIR}/prompts/review-big-head-consolidation.md" ]; then
    echo "ERROR: Big Head consolidation brief not found: ${SESSION_DIR}/prompts/review-big-head-consolidation.md" >&2
    ALL_OK=false
fi

if [ "$ALL_OK" = false ]; then
    exit 1
fi

echo "fill-review-slots.sh: all review prompt files written successfully."
echo ""
echo "Return table:"
echo "| Review Type | Prompt | Preview | Report Output Path |"
echo "|-------------|--------|---------|-------------------|"
for review_type in "${ACTIVE_REVIEW_TYPES[@]}"; do
    echo "| ${review_type} | ${SESSION_DIR}/prompts/review-${review_type}.md | ${SESSION_DIR}/previews/review-${review_type}-preview.md | ${SESSION_DIR}/review-reports/${review_type}-review-${TIMESTAMP}.md |"
done
echo ""
echo "Big Head consolidation data: ${SESSION_DIR}/prompts/review-big-head-consolidation.md"
echo "Big Head consolidated output: ${SESSION_DIR}/review-reports/review-consolidated-${TIMESTAMP}.md"

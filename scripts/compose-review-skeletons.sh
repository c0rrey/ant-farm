#!/usr/bin/env bash
# compose-review-skeletons.sh — Script 1: assemble review skeleton files with slot markers.
#
# Called by the Pantry during Section 1 (implementation prompt composition).
# Reads reviews.md and nitpicker-skeleton.md template content and writes 5 skeleton files
# to {SESSION_DIR}/review-skeletons/ with {{SLOT_NAME}} markers for values not yet known
# (commit range, changed files, task IDs, timestamp).
#
# Usage:
#   compose-review-skeletons.sh <SESSION_DIR> <REVIEWS_MD_PATH> <NITPICKER_SKELETON_PATH> <BIG_HEAD_SKELETON_PATH>
#
# Arguments:
#   SESSION_DIR              — session artifact directory (e.g. .beads/agent-summaries/_session-abc123)
#   REVIEWS_MD_PATH          — path to orchestration/templates/reviews.md (runtime: ~/.claude/orchestration/templates/reviews.md)
#   NITPICKER_SKELETON_PATH  — path to orchestration/templates/nitpicker-skeleton.md
#   BIG_HEAD_SKELETON_PATH   — path to ~/.claude/orchestration/templates/big-head-skeleton.md
#
# Outputs (written to {SESSION_DIR}/review-skeletons/):
#   skeleton-clarity.md
#   skeleton-edge-cases.md
#   skeleton-correctness.md
#   skeleton-excellence.md
#   skeleton-big-head.md
#
# Exit codes:
#   0 — all 5 skeleton files written successfully
#   1 — missing argument, unreadable source file, or write failure

set -euo pipefail

# ---------------------------------------------------------------------------
# Argument validation
# ---------------------------------------------------------------------------

if [ $# -ne 4 ]; then
    echo "ERROR: compose-review-skeletons.sh requires exactly 4 arguments." >&2
    echo "Usage: $0 <SESSION_DIR> <REVIEWS_MD_PATH> <NITPICKER_SKELETON_PATH> <BIG_HEAD_SKELETON_PATH>" >&2
    exit 1
fi

SESSION_DIR="$1"
REVIEWS_MD="$2"
NITPICKER_SKELETON="$3"
BIG_HEAD_SKELETON="$4"

for f in "$REVIEWS_MD" "$NITPICKER_SKELETON" "$BIG_HEAD_SKELETON"; do
    if [ ! -f "$f" ]; then
        echo "ERROR: Source file not found: $f" >&2
        exit 1
    fi
    if [ ! -r "$f" ]; then
        echo "ERROR: Source file not readable: $f" >&2
        exit 1
    fi
done

# ---------------------------------------------------------------------------
# Output directory setup
# ---------------------------------------------------------------------------

SKELETON_DIR="${SESSION_DIR}/review-skeletons"
mkdir -p "$SKELETON_DIR" || {
    echo "ERROR: Failed to create skeleton directory: $SKELETON_DIR" >&2
    exit 1
}

# ---------------------------------------------------------------------------
# Helper: extract agent-facing section from a skeleton template file.
# Prints all lines after the first line containing only "---" (the delimiter
# line itself is excluded). Skeleton template files are expected to contain
# exactly one such delimiter separating the instruction block from the
# agent-facing content.
# ---------------------------------------------------------------------------
extract_agent_section() {
    local file="$1"
    awk '/^---$/{count++; next} count>=1{print}' "$file"
}

# ---------------------------------------------------------------------------
# Helper: write a review skeleton for one Nitpicker review type.
#
# Embeds:
#   {{REVIEW_TYPE}}    — clarity / edge-cases / correctness / excellence
#   {{DATA_FILE_PATH}} — filled by fill-review-slots.sh at slot-fill time
#   {{REPORT_OUTPUT_PATH}} — filled by fill-review-slots.sh at slot-fill time
#   {{REVIEW_ROUND}}   — filled by fill-review-slots.sh at slot-fill time
#   {{COMMIT_RANGE}}   — filled by fill-review-slots.sh (used in brief body)
#   {{CHANGED_FILES}}  — filled by fill-review-slots.sh
#   {{TIMESTAMP}}      — filled by fill-review-slots.sh
#
# The skeleton wraps the nitpicker-skeleton template body, then appends the
# review-type-specific focus block extracted from reviews.md.
# ---------------------------------------------------------------------------
write_nitpicker_skeleton() {
    local review_type="$1"
    local out_file="${SKELETON_DIR}/skeleton-${review_type}.md"

    # Extract the agent-facing portion of the nitpicker skeleton
    local skeleton_body
    skeleton_body="$(extract_agent_section "$NITPICKER_SKELETON")"

    # Convert single-brace uppercase placeholders to double-brace slot markers.
    # Pattern: {WORD} → {{WORD}} where WORD matches [A-Z][A-Z_]+ (2+ chars, all-caps with underscores).
    # Single-char tokens like {X} do NOT match and are left unchanged.
    # ASSUMPTION: template prose does not use {UPPERCASE_WORD} syntax for non-slot purposes.
    # Canonical slot names this regex is expected to convert (nitpicker skeletons):
    #   REVIEW_TYPE, REVIEW_ROUND, DATA_FILE_PATH, REPORT_OUTPUT_PATH,
    #   COMMIT_RANGE, CHANGED_FILES, TASK_IDS, TIMESTAMP.
    skeleton_body="$(printf '%s\n' "$skeleton_body" | sed -E 's/\{([A-Z][A-Z_]+)\}/{{\1}}/g')"

    # Then substitute the now-double-braced {{REVIEW_TYPE}} with the actual value.
    skeleton_body="$(printf '%s\n' "$skeleton_body" | sed "s/{{REVIEW_TYPE}}/${review_type}/g")"

    # Build the header comment so Pest Control (CCO) and future readers understand provenance
    {
        printf '<!-- Review skeleton: %s | Assembled by compose-review-skeletons.sh -->\n' "$review_type"
        printf '<!-- Slot markers: {{DATA_FILE_PATH}} {{REPORT_OUTPUT_PATH}} {{REVIEW_ROUND}} {{COMMIT_RANGE}} {{CHANGED_FILES}} {{TIMESTAMP}} -->\n'
        printf '<!-- Fill with: scripts/fill-review-slots.sh -->\n'
        echo ""
        echo "$skeleton_body"
        echo ""
        echo "---"
        echo "## Review Brief"
        echo ""
        echo "**Commit range**: {{COMMIT_RANGE}}"
        echo ""
        echo "**Review round**: {{REVIEW_ROUND}}"
        echo ""
        echo "**Files to review**:"
        echo "{{CHANGED_FILES}}"
        echo ""
        echo "**Task IDs** (for correctness review — run \`bd show <id>\` to retrieve acceptance criteria):"
        echo "{{TASK_IDS}}"
        echo ""
        echo "**Report output path**: {{REPORT_OUTPUT_PATH}}"
        echo ""
        echo "**Timestamp**: {{TIMESTAMP}}"
        echo ""
        echo "Do NOT file beads — Big Head handles all bead filing."
    } > "$out_file" || {
        echo "ERROR: Failed to write skeleton file: $out_file" >&2
        exit 1
    }

    echo "  Written: $out_file"
}

# ---------------------------------------------------------------------------
# Helper: write the Big Head skeleton
# ---------------------------------------------------------------------------
write_big_head_skeleton() {
    local out_file="${SKELETON_DIR}/skeleton-big-head.md"

    # Extract the agent-facing portion of the big-head skeleton
    local skeleton_body
    skeleton_body="$(extract_agent_section "$BIG_HEAD_SKELETON")"

    # Convert single-brace uppercase placeholders to double-brace slot markers.
    # Pattern: {WORD} → {{WORD}} where WORD matches [A-Z][A-Z_]+ (2+ chars, all-caps with underscores).
    # Single-char tokens like {X} do NOT match and are left unchanged.
    # ASSUMPTION: template prose does not use {UPPERCASE_WORD} syntax for non-slot purposes.
    # Canonical slot names this regex is expected to convert (Big Head skeleton):
    #   DATA_FILE_PATH, CONSOLIDATED_OUTPUT_PATH, REVIEW_ROUND, TIMESTAMP,
    #   EXPECTED_REPORT_PATHS.
    skeleton_body="$(printf '%s\n' "$skeleton_body" | sed -E 's/\{([A-Z][A-Z_]+)\}/{{\1}}/g')"

    {
        printf '<!-- Big Head skeleton | Assembled by compose-review-skeletons.sh -->\n'
        printf '<!-- Slot markers: {{DATA_FILE_PATH}} {{CONSOLIDATED_OUTPUT_PATH}} {{REVIEW_ROUND}} {{TIMESTAMP}} -->\n'
        printf '<!-- Fill with: scripts/fill-review-slots.sh -->\n'
        echo ""
        echo "$skeleton_body"
        echo ""
        echo "---"
        echo "## Consolidation Brief"
        echo ""
        echo "**Review round**: {{REVIEW_ROUND}}"
        echo "**Data file**: {{DATA_FILE_PATH}}"
        echo "**Consolidated output**: {{CONSOLIDATED_OUTPUT_PATH}}"
        echo "**Timestamp**: {{TIMESTAMP}}"
        echo ""
        echo "**Expected report paths** (all must exist before consolidation begins):"
        echo "{{EXPECTED_REPORT_PATHS}}"
    } > "$out_file" || {
        echo "ERROR: Failed to write Big Head skeleton file: $out_file" >&2
        exit 1
    }

    echo "  Written: $out_file"
}

# ---------------------------------------------------------------------------
# Main: write all 5 skeletons
# ---------------------------------------------------------------------------

echo "compose-review-skeletons.sh: assembling review skeletons in ${SKELETON_DIR}"

for review_type in clarity edge-cases correctness excellence; do
    write_nitpicker_skeleton "$review_type"
done

write_big_head_skeleton

# ---------------------------------------------------------------------------
# Verify all 5 output files were written and are non-empty
# ---------------------------------------------------------------------------

echo ""
echo "compose-review-skeletons.sh: verifying output files..."

ALL_OK=true
for expected in \
    "${SKELETON_DIR}/skeleton-clarity.md" \
    "${SKELETON_DIR}/skeleton-edge-cases.md" \
    "${SKELETON_DIR}/skeleton-correctness.md" \
    "${SKELETON_DIR}/skeleton-excellence.md" \
    "${SKELETON_DIR}/skeleton-big-head.md"
do
    if [ ! -f "$expected" ]; then
        echo "ERROR: Expected output file missing: $expected" >&2
        ALL_OK=false
    elif [ ! -s "$expected" ]; then
        echo "ERROR: Output file is empty: $expected" >&2
        ALL_OK=false
    fi
done

if [ "$ALL_OK" = false ]; then
    exit 1
fi

echo "compose-review-skeletons.sh: all 5 skeleton files written successfully."
echo ""
echo "Skeleton paths:"
echo "  ${SKELETON_DIR}/skeleton-clarity.md"
echo "  ${SKELETON_DIR}/skeleton-edge-cases.md"
echo "  ${SKELETON_DIR}/skeleton-correctness.md"
echo "  ${SKELETON_DIR}/skeleton-excellence.md"
echo "  ${SKELETON_DIR}/skeleton-big-head.md"

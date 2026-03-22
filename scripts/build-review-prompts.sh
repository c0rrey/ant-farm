#!/usr/bin/env bash
# build-review-prompts.sh — Build filled review prompts directly from master templates.
#
# Replaces the two-script pipeline (compose-review-skeletons.sh + fill-review-slots.sh)
# by reading master templates, extracting agent-facing sections, and filling all slots
# in a single pass. No intermediate skeleton files are created.
#
# Usage:
#   build-review-prompts.sh <SESSION_DIR> <COMMIT_RANGE> <CHANGED_FILES_LIST> \
#                           <TASK_IDS_LIST> <TIMESTAMP> <REVIEW_ROUND> \
#                           <REVIEWER_SKELETON_PATH> <REVIEW_CONSOLIDATOR_SKELETON_PATH>
#
# Arguments:
#   SESSION_DIR              — session artifact directory
#   COMMIT_RANGE             — git commit range, e.g. "abc1234..HEAD"
#   CHANGED_FILES_LIST       — newline-separated list of changed files (or @filepath)
#   TASK_IDS_LIST            — space-separated list of task IDs (or @filepath)
#   TIMESTAMP                — review timestamp in YYYYMMDD-HHmmss format
#   REVIEW_ROUND             — positive integer (1, 2, 3, ...)
#   REVIEWER_SKELETON_PATH  — path to reviewer-skeleton.md
#   REVIEW_CONSOLIDATOR_SKELETON_PATH   — path to review-consolidator-skeleton.md
#
# Note on CHANGED_FILES_LIST and TASK_IDS_LIST:
#   Pass them as file paths prefixed with "@" to avoid shell quoting issues with newlines:
#     build-review-prompts.sh ... @/tmp/changed-files.txt @/tmp/task-ids.txt ...
#   Or pass literal values (quoted) for simple cases.
#
# Outputs:
#   {SESSION_DIR}/prompts/review-{type}.md           — filled review prompts
#   {SESSION_DIR}/previews/review-{type}-preview.md  — combined previews
#   {SESSION_DIR}/prompts/review-consolidation.md — Review Consolidator brief
#   {SESSION_DIR}/review-reports/                    — directory created for reports
#
# Exit codes:
#   0 — all prompts and previews written successfully
#   1 — missing argument, unreadable file, or write failure

set -euo pipefail

# Maximum concurrent agents Claude Code supports in a single team.
MAX_TEAM_SIZE=15

# ---------------------------------------------------------------------------
# Script-level temp file cleanup (AF-258).
# Functions use trap RETURN for immediate cleanup on normal return, but RETURN
# traps do not fire when set -e exits the script mid-function. This EXIT trap
# provides a safety net: each function registers its temp file here, and
# cleanup_temp_files runs on any script exit. rm -f is idempotent, so
# double-removal (RETURN + EXIT) is harmless.
# ---------------------------------------------------------------------------
_TEMP_FILES_TO_CLEAN=()
cleanup_temp_files() {
    for f in ${_TEMP_FILES_TO_CLEAN[@]+"${_TEMP_FILES_TO_CLEAN[@]}"}; do
        rm -f "$f"
    done
}
trap cleanup_temp_files EXIT

# ---------------------------------------------------------------------------
# Locate crumb binary — context-aware fallback (AF-248).
#
# Resolution order:
#   1. Repo-local crumb.py: ${SCRIPT_DIR}/../crumb.py
#      Used when running from the repo scripts/ directory. Preferred because
#      it guarantees render-template is available.
#   2. PATH-installed crumb: ~/.local/bin/crumb (via $HOME resolution)
#      Used when running from the installed location (~/.claude/orchestration/scripts/).
#      setup.sh installs crumb.py to ~/.local/bin/crumb (confirmed: setup.sh:L515).
#   3. Plain 'crumb' on PATH (last resort).
#
# A startup validation below confirms the resolved binary supports render-template.
# ---------------------------------------------------------------------------
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
if [ -f "${SCRIPT_DIR}/../crumb.py" ]; then
    CRUMB=(python3 "${SCRIPT_DIR}/../crumb.py")
elif [ -f "${HOME}/.local/bin/crumb" ]; then
    CRUMB=("${HOME}/.local/bin/crumb")
else
    CRUMB=(crumb)
fi

# ---------------------------------------------------------------------------
# Startup validation: confirm resolved CRUMB supports render-template.
# Catches stale installs or missing PATH entries before the first $CRUMB call.
# ---------------------------------------------------------------------------
if ! "${CRUMB[@]}" render-template --help >/dev/null 2>&1; then
    echo "ERROR: crumb binary does not support 'render-template' subcommand." >&2
    echo "  Resolved CRUMB='${CRUMB[*]}'" >&2
    echo "  Run ./scripts/setup.sh to install the current crumb.py to ~/.local/bin/crumb." >&2
    exit 1
fi

# ---------------------------------------------------------------------------
# Argument validation
# ---------------------------------------------------------------------------

if [ $# -ne 8 ]; then
    echo "ERROR: build-review-prompts.sh requires exactly 8 arguments." >&2
    echo "Usage: $0 <SESSION_DIR> <COMMIT_RANGE> <CHANGED_FILES_LIST> <TASK_IDS_LIST> <TIMESTAMP> <REVIEW_ROUND> <REVIEWER_SKELETON_PATH> <REVIEW_CONSOLIDATOR_SKELETON_PATH>" >&2
    exit 1
fi

SESSION_DIR="$1"
COMMIT_RANGE="$2"
CHANGED_FILES_RAW="$3"
TASK_IDS_RAW="$4"
TIMESTAMP="$5"
REVIEW_ROUND="$6"
REVIEWER_SKELETON="$7"
REVIEW_CONSOLIDATOR_SKELETON="$8"

if [ -z "$SESSION_DIR" ]; then
    echo "ERROR: SESSION_DIR argument is empty." >&2
    exit 1
fi
if [ ! -d "$SESSION_DIR" ]; then
    echo "ERROR: SESSION_DIR does not exist: $SESSION_DIR" >&2
    exit 1
fi

for f in "$REVIEWER_SKELETON" "$REVIEW_CONSOLIDATOR_SKELETON"; do
    if [ ! -f "$f" ]; then
        echo "ERROR: Template file not found: $f" >&2
        exit 1
    fi
    if [ ! -r "$f" ]; then
        echo "ERROR: Template file not readable: $f" >&2
        exit 1
    fi
done

# ---------------------------------------------------------------------------
# Resolve @file arguments for multiline values
# ---------------------------------------------------------------------------

expand_at_file_arg() {
    local val="$1"
    if [[ "$val" == @* ]]; then
        local fpath="${val:1}"
        if [ ! -f "$fpath" ]; then
            echo "ERROR: @file argument not found: $fpath" >&2
            exit 1
        fi
        if [ ! -r "$fpath" ]; then
            echo "ERROR: @file argument not readable: $fpath" >&2
            exit 1
        fi
        cat "$fpath"
    else
        printf '%s' "$val"
    fi
}

CHANGED_FILES="$(expand_at_file_arg "$CHANGED_FILES_RAW")" || { echo "ERROR: expand_at_file_arg failed for CHANGED_FILES_RAW='${CHANGED_FILES_RAW}'" >&2; exit 1; }
TASK_IDS="$(expand_at_file_arg "$TASK_IDS_RAW")" || { echo "ERROR: expand_at_file_arg failed for TASK_IDS_RAW='${TASK_IDS_RAW}'" >&2; exit 1; }
if [[ -z "${TASK_IDS//[[:space:]]/}" ]]; then
    echo "ERROR: TASK_IDS is empty (got: '${TASK_IDS_RAW}')." >&2
    exit 1
fi

# ---------------------------------------------------------------------------
# Input validation (after @file resolution)
# ---------------------------------------------------------------------------

# CHANGED_FILES: must be non-empty (at least one changed file)
# Strip all whitespace via parameter expansion — no subprocesses required.
if [[ -z "${CHANGED_FILES//[[:space:]]/}" ]]; then
    echo "ERROR: CHANGED_FILES is empty (got: '${CHANGED_FILES_RAW}'). Expected: at least one file path (or a non-empty @file)." >&2
    exit 1
fi

# REVIEW_ROUND: must be a positive integer >= 1
if ! [[ "${REVIEW_ROUND}" =~ ^[1-9][0-9]*$ ]]; then
    echo "ERROR: REVIEW_ROUND must be a positive integer >= 1, got: '${REVIEW_ROUND}'. Expected format: ^[1-9][0-9]*\$ (e.g. 1, 2, 10)." >&2
    exit 1
fi

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
# Partitioning threshold (env var, default 8)
# ---------------------------------------------------------------------------

REVIEW_SPLIT_THRESHOLD="${REVIEW_SPLIT_THRESHOLD:-8}"
if ! [[ "${REVIEW_SPLIT_THRESHOLD}" =~ ^[1-9][0-9]*$ ]]; then
    echo "ERROR: REVIEW_SPLIT_THRESHOLD must be a positive integer >= 1, got: '${REVIEW_SPLIT_THRESHOLD}'." >&2
    exit 1
fi

# ---------------------------------------------------------------------------
# Determine which review types to produce based on round, applying
# file partitioning for Clarity and Drift when file count > threshold.
# ---------------------------------------------------------------------------

# Sort CHANGED_FILES with LC_ALL=C for reproducible partition assignments.
CHANGED_FILES_SORTED="$(printf '%s\n' "$CHANGED_FILES" | sed '/^[[:space:]]*$/d' | LC_ALL=C sort)"

# Count non-empty lines in the sorted list.
FILE_COUNT=0
while IFS= read -r line; do
    # || true prevents set -e exit: (( n++ )) returns exit code 1 when result is 0 (first iteration post-increment).
    [[ -n "$line" ]] && (( FILE_COUNT++ )) || true
done <<< "$CHANGED_FILES_SORTED"

# Per-type file list storage: stored in dynamically-named variables
# REVIEW_FILES__<key> where <key> is the review type with hyphens replaced by underscores.
# This avoids bash 4+ associative arrays and works on bash 3.2 (macOS default).
#
# set_review_files TYPE FILES — stores file list for a review type.
set_review_files() {
    local key="${1//-/_}"
    printf -v "REVIEW_FILES__${key}" '%s' "$2"
}

# get_review_files TYPE — prints the stored file list for a review type.
get_review_files() {
    local key="${1//-/_}"
    local varname="REVIEW_FILES__${key}"
    printf '%s' "${!varname}"
}

if [ "$REVIEW_ROUND" -eq 1 ]; then
    if [ "$FILE_COUNT" -gt "$REVIEW_SPLIT_THRESHOLD" ]; then
        # Partition files into groups of at most REVIEW_SPLIT_THRESHOLD.
        # Read sorted files into an indexed array.
        ALL_FILES_ARRAY=()
        while IFS= read -r line; do
            [[ -n "$line" ]] && ALL_FILES_ARRAY+=("$line")
        done <<< "$CHANGED_FILES_SORTED"

        # Compute number of partitions (ceiling division).
        NUM_PARTITIONS=$(( (FILE_COUNT + REVIEW_SPLIT_THRESHOLD - 1) / REVIEW_SPLIT_THRESHOLD ))

        ACTIVE_REVIEW_TYPES=()

        # Helper: build a newline-separated slice of ALL_FILES_ARRAY[start .. start+count-1].
        make_slice() {
            local start="$1"
            local count="$2"
            local i end result=""
            end=$(( start + count ))
            for (( i=start; i<end && i<${#ALL_FILES_ARRAY[@]}; i++ )); do
                result="${result}${ALL_FILES_ARRAY[$i]}"$'\n'
            done
            # Strip trailing newline
            printf '%s' "${result%$'\n'}"
        }

        # Add split Clarity instances.
        for (( part=1; part<=NUM_PARTITIONS; part++ )); do
            type_name="clarity-${part}"
            start=$(( (part - 1) * REVIEW_SPLIT_THRESHOLD ))
            slice="$(make_slice "$start" "$REVIEW_SPLIT_THRESHOLD")"
            set_review_files "$type_name" "$slice"
            ACTIVE_REVIEW_TYPES+=("$type_name")
        done

        # Edge Cases gets the full list (never partitioned).
        ACTIVE_REVIEW_TYPES+=(edge-cases)
        set_review_files "edge-cases" "$CHANGED_FILES_SORTED"

        # Correctness gets the full list (never partitioned).
        ACTIVE_REVIEW_TYPES+=(correctness)
        set_review_files "correctness" "$CHANGED_FILES_SORTED"

        # Add split Drift instances.
        for (( part=1; part<=NUM_PARTITIONS; part++ )); do
            type_name="drift-${part}"
            start=$(( (part - 1) * REVIEW_SPLIT_THRESHOLD ))
            slice="$(make_slice "$start" "$REVIEW_SPLIT_THRESHOLD")"
            set_review_files "$type_name" "$slice"
            ACTIVE_REVIEW_TYPES+=("$type_name")
        done
    else
        # Below threshold: single instance per type (unchanged behavior).
        ACTIVE_REVIEW_TYPES=(clarity edge-cases correctness drift)
        for rt in "${ACTIVE_REVIEW_TYPES[@]}"; do
            set_review_files "$rt" "$CHANGED_FILES_SORTED"
        done
    fi
else
    # Round 2+: correctness and edge-cases only (never partitioned).
    ACTIVE_REVIEW_TYPES=(correctness edge-cases)
    for rt in "${ACTIVE_REVIEW_TYPES[@]}"; do
        set_review_files "$rt" "$CHANGED_FILES_SORTED"
    done
fi

# ---------------------------------------------------------------------------
# Preflight: team-size check.
# Total expected team members = reviewer instances + Review Consolidator + Checkpoint Auditor.
# Claude Code supports at most MAX_TEAM_SIZE concurrent agents; exceeding this
# silently drops agents. Error early rather than silently under-review.
# ---------------------------------------------------------------------------
EXPECTED_TEAM_SIZE=$(( ${#ACTIVE_REVIEW_TYPES[@]} + 2 ))
if [ "$EXPECTED_TEAM_SIZE" -gt "$MAX_TEAM_SIZE" ]; then
    echo "ERROR: Team size check failed: expected_team_size=${EXPECTED_TEAM_SIZE} (${#ACTIVE_REVIEW_TYPES[@]} reviewer instances + Review Consolidator + Checkpoint Auditor) exceeds the ${MAX_TEAM_SIZE}-agent ceiling." >&2
    echo "Reduce REVIEW_SPLIT_THRESHOLD or limit the number of changed files per session." >&2
    exit 1
fi

# ---------------------------------------------------------------------------
# Helper: extract agent-facing section from a skeleton template file
# (everything after the line containing only "---")
# ---------------------------------------------------------------------------
extract_agent_section() {
    local file="$1"
    awk '/^---$/{found=1; next} found{print}' "$file"
}

# ---------------------------------------------------------------------------
# Helper: extract focus block for a given review type from review-focus-areas.md.
# Extracts content between <!-- FOCUS: {type} --> and <!-- /FOCUS: {type} --> markers.
# ---------------------------------------------------------------------------
# review-focus-areas.md must be a sibling of reviewer-skeleton.md in the templates directory.
# Both files are expected to live in the same directory (orchestration/templates/ by convention).
FOCUS_AREAS_FILE="$(dirname "$REVIEWER_SKELETON")/review-focus-areas.md"
if [ ! -f "$FOCUS_AREAS_FILE" ] || [ ! -r "$FOCUS_AREAS_FILE" ]; then
    echo "ERROR: Focus areas file not found or not readable: $FOCUS_AREAS_FILE" >&2
    exit 1
fi

# Extract the focus-area block for a given review type from the focus areas file.
# The file uses paired HTML comment markers to delimit each review type's block:
#   <!-- FOCUS: <type> -->
#   ... focus area content ...
#   <!-- /FOCUS: <type> -->
# These markers are invisible in rendered Markdown but machine-parseable by awk,
# allowing a single focus-areas file to contain blocks for all review types.
extract_focus_block() {
    local review_type="$1"
    # Strip trailing -N suffix from split instance names (e.g., clarity-1 -> clarity,
    # drift-2 -> drift) before looking up the focus block marker.
    local base_type="${review_type%-[0-9]*}"
    awk -v type="$base_type" '
        $0 ~ "<!-- FOCUS: " type " -->" { found=1; next }
        $0 ~ "<!-- /FOCUS: " type " -->" { found=0; next }
        found { print }
    ' "$FOCUS_AREAS_FILE"
}

# ---------------------------------------------------------------------------
# NOTE: fill_slot() has been removed.
# Slot substitution is now delegated to: crumb render-template
#
# Usage: crumb render-template <template-file> --slot KEY=VALUE [--slot ...]
# The command reads the template file, expands all {{KEY}} placeholders with
# the provided values, validates that all slots are supplied and no extras are
# given, then writes the rendered result to stdout.
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# Helper: build a filled review prompt for one Reviewer review type.
#
# Reads the master reviewer-skeleton.md, extracts the agent-facing section,
# converts placeholders, and delegates all slot substitution to
# crumb render-template. Orchestration/partitioning logic remains in shell.
# ---------------------------------------------------------------------------
build_reviewer_prompt() {
    local review_type="$1"
    local out_prompt="${SESSION_DIR}/prompts/review-${review_type}.md"
    local out_preview="${SESSION_DIR}/previews/review-${review_type}-preview.md"
    local report_output_path="${SESSION_DIR}/review-reports/${review_type}-review-${TIMESTAMP}.md"
    # The data file the agent reads IS the prompt file itself -- the Review
    # Brief section (appended below in step 4) embeds all review inputs inline
    # in the prompt. This self-referential assignment is safe because crumb
    # render-template reads from a temp file and writes to stdout; $out_prompt
    # is the render destination, not the source, so no read/write conflict.
    local data_file_path="${out_prompt}"

    # Resolve the file list for this review type.
    # Split instances (e.g. clarity-1) have a subset; non-split types use full list.
    local type_files
    type_files="$(get_review_files "$review_type")"
    # Fall back to full sorted list if nothing was stored (safety guard).
    [[ -z "$type_files" ]] && type_files="$CHANGED_FILES_SORTED"

    # 1. Extract agent-facing section from master template
    local body
    body="$(extract_agent_section "$REVIEWER_SKELETON")"

    # 2. Convert {UPPERCASE} -> {{UPPERCASE}} (crumb render-template slot format)
    body="$(printf '%s\n' "$body" | sed 's/{\([A-Z][A-Z_0-9]*\)}/{{\1}}/g')"

    # 3. Build a composite template containing the template body and the
    #    Review Brief section, with {{SLOT}} markers for all variable parts.
    #    crumb render-template will expand all markers in a single pass.
    local tmp_template
    tmp_template="$(mktemp)"
    _TEMP_FILES_TO_CLEAN+=("$tmp_template")
    # shellcheck disable=SC2064
    trap "rm -f '$tmp_template'" RETURN
    {
        printf '<!-- Review prompt: %s | Built by build-review-prompts.sh -->\n' "$review_type"
        echo ""
        echo "$body"
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
        echo "## Focus"
        echo ""
        extract_focus_block "$review_type"
        echo ""
        echo "**Task IDs** (for correctness review — run \`crumb show <id>\` to retrieve acceptance criteria):"
        echo "{{TASK_IDS}}"
        echo ""
        echo "**Report output path**: {{REPORT_OUTPUT_PATH}}"
        echo ""
        echo "**Timestamp**: {{TIMESTAMP}}"
        echo ""
        echo "Do NOT file crumbs — Review Consolidator handles all crumb filing."
    } > "$tmp_template" || {
        echo "ERROR: Failed to write template file: $tmp_template" >&2
        exit 1
    }

    # 4. Delegate all slot substitution to crumb render-template.
    #    Slots: REVIEW_TYPE, DATA_FILE_PATH, REPORT_OUTPUT_PATH, REVIEW_ROUND,
    #           COMMIT_RANGE, CHANGED_FILES, TASK_IDS, TIMESTAMP.
    #    Values with newlines are passed as quoted shell arguments; Python's
    #    argparse receives the full string including embedded newlines.
    "${CRUMB[@]}" render-template "$tmp_template" \
        --slot "REVIEW_TYPE=${review_type}" \
        --slot "DATA_FILE_PATH=${data_file_path}" \
        --slot "REPORT_OUTPUT_PATH=${report_output_path}" \
        --slot "REVIEW_ROUND=${REVIEW_ROUND}" \
        --slot "COMMIT_RANGE=${COMMIT_RANGE}" \
        --slot "CHANGED_FILES=${type_files}" \
        --slot "TASK_IDS=${TASK_IDS}" \
        --slot "TIMESTAMP=${TIMESTAMP}" \
        > "$out_prompt" || {
        echo "ERROR: crumb render-template failed for ${review_type}" >&2
        exit 1
    }

    # 5. Copy to preview
    cp "$out_prompt" "$out_preview" || {
        echo "ERROR: Failed to write preview for ${review_type}: $out_preview" >&2
        exit 1
    }

    echo "  Prompt:  $out_prompt"
    echo "  Preview: $out_preview"
    echo "  Report will be written to: $report_output_path"
}

# ---------------------------------------------------------------------------
# Helper: build the filled Review Consolidator consolidation brief.
#
# Delegates all slot substitution to crumb render-template.
# Orchestration logic (expected_paths construction) remains in shell.
# ---------------------------------------------------------------------------
build_review_consolidator_prompt() {
    local out_file="${SESSION_DIR}/prompts/review-consolidation.md"
    local consolidated_output="${SESSION_DIR}/review-reports/review-consolidated-${TIMESTAMP}.md"

    # Build the expected report paths list (round-appropriate)
    # Each path is embedded in a markdown list line, joined by literal newlines.
    local expected_paths=""
    for rt in "${ACTIVE_REVIEW_TYPES[@]}"; do
        [[ -n "$expected_paths" ]] && expected_paths="${expected_paths}"$'\n'
        expected_paths="${expected_paths}- ${SESSION_DIR}/review-reports/${rt}-review-${TIMESTAMP}.md"
    done

    # 1. Extract agent-facing section from master template
    local body
    body="$(extract_agent_section "$REVIEW_CONSOLIDATOR_SKELETON")"

    # 2. Convert {UPPERCASE} -> {{UPPERCASE}} (crumb render-template slot format)
    body="$(printf '%s\n' "$body" | sed 's/{\([A-Z][A-Z_0-9]*\)}/{{\1}}/g')"

    # 3. Build a composite template containing the template body and the
    #    Consolidation Brief section, with {{SLOT}} markers for all variable
    #    parts. crumb render-template will expand all markers in a single pass.
    #
    # NOTE: DATA_FILE_PATH is substituted with $out_file — the output file's
    # own path. This self-referential substitution is safe because crumb
    # render-template reads from a temp file and writes to stdout; $out_file
    # is the render destination, not the source, so no read/write conflict.
    local tmp_template
    tmp_template="$(mktemp)"
    _TEMP_FILES_TO_CLEAN+=("$tmp_template")
    # shellcheck disable=SC2064
    trap "rm -f '$tmp_template'" RETURN
    {
        printf '<!-- Review Consolidator prompt | Built by build-review-prompts.sh -->\n'
        echo ""
        echo "$body"
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
    } > "$tmp_template" || {
        echo "ERROR: Failed to write template file: $tmp_template" >&2
        exit 1
    }

    # 4. Delegate all slot substitution to crumb render-template.
    #    Slots: REVIEW_ROUND, DATA_FILE_PATH, CONSOLIDATED_OUTPUT_PATH,
    #           TIMESTAMP, EXPECTED_REPORT_PATHS.
    "${CRUMB[@]}" render-template "$tmp_template" \
        --slot "REVIEW_ROUND=${REVIEW_ROUND}" \
        --slot "DATA_FILE_PATH=${out_file}" \
        --slot "CONSOLIDATED_OUTPUT_PATH=${consolidated_output}" \
        --slot "TIMESTAMP=${TIMESTAMP}" \
        --slot "EXPECTED_REPORT_PATHS=${expected_paths}" \
        > "$out_file" || {
        echo "ERROR: crumb render-template failed for review-consolidator" >&2
        exit 1
    }

    echo "  Review Consolidator brief: $out_file"
    echo "  Consolidated output will be: $consolidated_output"
}

# ---------------------------------------------------------------------------
# Main execution
# ---------------------------------------------------------------------------

echo "build-review-prompts.sh: building review prompts (round ${REVIEW_ROUND})"
echo "  Session dir:    ${SESSION_DIR}"
echo "  Commit range:   ${COMMIT_RANGE}"
echo "  Timestamp:      ${TIMESTAMP}"
echo "  Active reviews: ${ACTIVE_REVIEW_TYPES[*]}"
echo ""

for review_type in "${ACTIVE_REVIEW_TYPES[@]}"; do
    echo "Processing: ${review_type}"
    build_reviewer_prompt "$review_type"
    echo ""
done

echo "Processing: review-consolidator"
build_review_consolidator_prompt
echo ""

# ---------------------------------------------------------------------------
# Verify all output files were written and are non-empty
# ---------------------------------------------------------------------------

echo "build-review-prompts.sh: verifying output files..."

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

if [ ! -f "${SESSION_DIR}/prompts/review-consolidation.md" ]; then
    echo "ERROR: Review Consolidator consolidation brief not found: ${SESSION_DIR}/prompts/review-consolidation.md" >&2
    ALL_OK=false
fi

if [ "$ALL_OK" = false ]; then
    exit 1
fi

# ---------------------------------------------------------------------------
# Post-write placeholder scan: check all output files for unfilled slots.
# Catches cases where a --slot argument was omitted from crumb render-template
# or a new template placeholder was added without a corresponding --slot.
# Patterns checked:
#   {{UPPERCASE}} — double-brace template slots used by crumb render-template.
#     Double braces are required because crumb render-template uses {{KEY}}
#     syntax to distinguish template slots from shell $variables, single-brace
#     constructs, and Markdown content. No double-brace slot should survive
#     substitution in any output file.
# ---------------------------------------------------------------------------

echo "build-review-prompts.sh: scanning for unfilled placeholders..."

SCAN_FILES=()
for review_type in "${ACTIVE_REVIEW_TYPES[@]}"; do
    SCAN_FILES+=("${SESSION_DIR}/prompts/review-${review_type}.md")
done
SCAN_FILES+=("${SESSION_DIR}/prompts/review-consolidation.md")

PLACEHOLDER_FOUND=false
for f in "${SCAN_FILES[@]}"; do
    # Check for unfilled {{UPPERCASE}} double-brace slots (applies to all output files).
    # These are the crumb render-template slot tokens — none should survive substitution.
    # Note: angle-bracket path placeholders (<session-dir>, <timestamp>) are NOT
    # scanned here because both Reviewer templates (e.g. <task-id>) and the Review Consolidator
    # template (e.g. <P>, <title>, <new-crumb-id>) contain intentional angle-bracket
    # tokens in instructional examples that are meant to reach the agent verbatim.
    # Those tokens are documented in the template source note added to reviews.md.
    if grep -qE '\{\{[A-Z][A-Z_0-9]*\}\}' "$f" 2>/dev/null; then
        echo "ERROR: Unfilled {{SLOT}} placeholder(s) found in: $f" >&2
        grep -nE '\{\{[A-Z][A-Z_0-9]*\}\}' "$f" | while IFS= read -r line; do
            echo "  $line" >&2
        done
        PLACEHOLDER_FOUND=true
    fi
done

if [ "$PLACEHOLDER_FOUND" = true ]; then
    echo "ERROR: One or more output files contain unfilled placeholders. Aborting." >&2
    echo "Root cause: a --slot argument is missing from the crumb render-template call, or a template placeholder was added without a corresponding --slot." >&2
    exit 1
fi

echo "build-review-prompts.sh: placeholder scan passed — no unfilled slots detected."
echo ""
echo "build-review-prompts.sh: all review prompt files written successfully."
echo ""
echo "Return table:"
echo "| Review Type | Prompt | Preview | Report Output Path |"
echo "|-------------|--------|---------|-------------------|"
for review_type in "${ACTIVE_REVIEW_TYPES[@]}"; do
    echo "| ${review_type} | ${SESSION_DIR}/prompts/review-${review_type}.md | ${SESSION_DIR}/previews/review-${review_type}-preview.md | ${SESSION_DIR}/review-reports/${review_type}-review-${TIMESTAMP}.md |"
done
echo ""
echo "Review Consolidator consolidation data: ${SESSION_DIR}/prompts/review-consolidation.md"
echo "Review Consolidator consolidated output: ${SESSION_DIR}/review-reports/review-consolidated-${TIMESTAMP}.md"

#!/usr/bin/env bash
# test_build_review_prompts_split.sh — Integration tests for split-instance file partitioning
# in build-review-prompts.sh (AF-170).
#
# These tests focus exclusively on the split-partitioning code path:
#   1. Below threshold (5 files, threshold 8): 4 prompt files, 4 return table rows.
#   2. Above threshold (20 files, threshold 8): 8 prompt files, 8 return table rows.
#   3. Concatenated clarity split file lists equal full sorted file list.
#   4. Correctness and Edge Cases prompts contain all 20 files.
#   5. Review Consolidator expected_paths lists one path per split instance (8 paths for 20-file/threshold-8).
#
# Usage:
#   bash tests/test_build_review_prompts_split.sh

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SCRIPT="$REPO_ROOT/scripts/build-review-prompts.sh"
NITPICKER_SKELETON="$REPO_ROOT/orchestration/templates/nitpicker-skeleton.md"
BIG_HEAD_SKELETON="$REPO_ROOT/orchestration/templates/big-head-skeleton.md"

PASS=0
FAIL=0

# ---------------------------------------------------------------------------
# Runner helpers
# ---------------------------------------------------------------------------

pass() { echo "  PASS: $1"; PASS=$((PASS + 1)); }
fail() { echo "  FAIL: $1"; echo "        $2"; FAIL=$((FAIL + 1)); }

run_test() {
    local name="$1"
    local body="$2"
    echo ""
    echo "--- $name ---"
    local rc=0
    (
        set -euo pipefail
        eval "$body"
    ) || rc=$?
    if [ "$rc" -eq 0 ]; then
        pass "$name"
    else
        fail "$name" "subshell exited with code $rc"
    fi
}

# make_session — creates a temp session directory. Prints the path.
make_session() {
    local tmp
    tmp="$(mktemp -d)"
    echo "$tmp"
}

# write_files_list TMPDIR FILE1 FILE2 ... — writes a newline-separated list
# of file names to $TMPDIR/changed-files.txt. Prints the @-prefixed path.
write_files_list() {
    local tmpdir="$1"; shift
    local fpath="$tmpdir/changed-files.txt"
    printf '%s\n' "$@" > "$fpath"
    echo "@$fpath"
}

# run_script SESSION_DIR FILES_ARG [ROUND] [THRESHOLD_ENV]
# Runs the script with standard boilerplate args. ROUND defaults to 1.
run_script() {
    local session_dir="$1"
    local files_arg="$2"
    local round="${3:-1}"
    local threshold_env="${4:-}"
    if [ -n "$threshold_env" ]; then
        env REVIEW_SPLIT_THRESHOLD="$threshold_env" bash "$SCRIPT" \
            "$session_dir" "abc1234..HEAD" "$files_arg" "AF-1" \
            "20260317-120000" "$round" \
            "$NITPICKER_SKELETON" "$BIG_HEAD_SKELETON"
    else
        bash "$SCRIPT" \
            "$session_dir" "abc1234..HEAD" "$files_arg" "AF-1" \
            "20260317-120000" "$round" \
            "$NITPICKER_SKELETON" "$BIG_HEAD_SKELETON"
    fi
}

# ---------------------------------------------------------------------------
# Test 1: Below threshold — 5 files / threshold 8 → 4 prompt files, 4 return table rows
# ---------------------------------------------------------------------------
run_test "below_threshold_5files_threshold8_produces_4_prompts_and_4_rows" '
    session="$(make_session)"
    trap 'rm -rf "$session"' EXIT
    files_arg="$(write_files_list "$session" a.sh b.sh c.sh d.sh e.sh)"

    output="$(run_script "$session" "$files_arg" 1 8)"

    # Expect exactly 4 review prompt files (clarity, edge-cases, correctness, drift).
    for t in clarity edge-cases correctness drift; do
        if [ ! -f "$session/prompts/review-${t}.md" ]; then
            echo "ASSERTION FAILED: expected prompt for $t not found" >&2
            exit 1
        fi
    done

    # Must NOT have split instances.
    for t in clarity-1 clarity-2 drift-1 drift-2; do
        if [ -f "$session/prompts/review-${t}.md" ]; then
            echo "ASSERTION FAILED: unexpected split prompt found: $t" >&2
            exit 1
        fi
    done

    # Exactly 4 review prompt files (excluding big-head).
    count="$(ls "$session/prompts"/review-*.md 2>/dev/null | grep -v big-head | wc -l | tr -d " ")"
    if [ "$count" -ne 4 ]; then
        echo "ASSERTION FAILED: expected 4 prompt files, got $count" >&2
        exit 1
    fi

    # Return table must have exactly 4 data rows.
    row_count="$(printf "%s\n" "$output" | grep "^| " | grep -v "Review Type" | grep -v "\-\-\-" | wc -l | tr -d " ")"
    if [ "$row_count" -ne 4 ]; then
        echo "ASSERTION FAILED: expected 4 return table rows, got $row_count" >&2
        exit 1
    fi

    # Each expected type must appear as a row.
    for t in clarity edge-cases correctness drift; do
        if ! printf "%s\n" "$output" | grep -qF "| ${t} |"; then
            echo "ASSERTION FAILED: return table missing row for $t" >&2
            exit 1
        fi
    done

    rm -rf "$session"
'

# ---------------------------------------------------------------------------
# Test 2: Above threshold — 20 files / threshold 8 → 8 prompt files, 8 return table rows
# ---------------------------------------------------------------------------
run_test "above_threshold_20files_threshold8_produces_8_prompts_and_8_rows" '
    session="$(make_session)"
    trap 'rm -rf "$session"' EXIT
    # 20 files → ceil(20/8) = 3 partitions for Clarity and Drift.
    # Total types: clarity-1,2,3 + edge-cases + correctness + drift-1,2,3 = 8.
    files_arg="$(write_files_list "$session" \
        f01.sh f02.sh f03.sh f04.sh f05.sh f06.sh f07.sh f08.sh \
        f09.sh f10.sh f11.sh f12.sh f13.sh f14.sh f15.sh f16.sh \
        f17.sh f18.sh f19.sh f20.sh)"

    output="$(run_script "$session" "$files_arg" 1 8)"

    # All 8 expected prompt files must exist.
    for t in clarity-1 clarity-2 clarity-3 edge-cases correctness drift-1 drift-2 drift-3; do
        if [ ! -f "$session/prompts/review-${t}.md" ]; then
            echo "ASSERTION FAILED: expected prompt for $t not found" >&2
            exit 1
        fi
    done

    # Unsplit clarity and drift must NOT exist.
    for t in clarity drift; do
        if [ -f "$session/prompts/review-${t}.md" ]; then
            echo "ASSERTION FAILED: unexpected unsplit prompt found: $t" >&2
            exit 1
        fi
    done

    # Exactly 8 review prompt files (excluding big-head).
    count="$(ls "$session/prompts"/review-*.md 2>/dev/null | grep -v big-head | wc -l | tr -d " ")"
    if [ "$count" -ne 8 ]; then
        echo "ASSERTION FAILED: expected 8 prompt files, got $count" >&2
        exit 1
    fi

    # Return table must have exactly 8 data rows.
    row_count="$(printf "%s\n" "$output" | grep "^| " | grep -v "Review Type" | grep -v "\-\-\-" | wc -l | tr -d " ")"
    if [ "$row_count" -ne 8 ]; then
        echo "ASSERTION FAILED: expected 8 return table rows, got $row_count" >&2
        exit 1
    fi

    # Each split instance must appear as a row.
    for t in clarity-1 clarity-2 clarity-3 edge-cases correctness drift-1 drift-2 drift-3; do
        if ! printf "%s\n" "$output" | grep -qF "| ${t} |"; then
            echo "ASSERTION FAILED: return table missing row for $t" >&2
            exit 1
        fi
    done

    rm -rf "$session"
'

# ---------------------------------------------------------------------------
# Test 3: Concatenated clarity split file lists equal full sorted file list
#         (no duplicates, no omissions across clarity-1, clarity-2, clarity-3)
# ---------------------------------------------------------------------------
run_test "clarity_split_file_lists_concat_equals_full_sorted_list" '
    session="$(make_session)"
    trap 'rm -rf "$session"' EXIT
    files_arg="$(write_files_list "$session" \
        f01.sh f02.sh f03.sh f04.sh f05.sh f06.sh f07.sh f08.sh \
        f09.sh f10.sh f11.sh f12.sh f13.sh f14.sh f15.sh f16.sh \
        f17.sh f18.sh f19.sh f20.sh)"

    run_script "$session" "$files_arg" 1 8 >/dev/null

    # Collect all file references across all three clarity partitions.
    # Files appear in the "Files to review" section of each prompt.
    # They match the pattern "f<digits>.sh" on their own line.
    clarity_files="$(grep -h "^f[0-9]" \
        "$session/prompts/review-clarity-1.md" \
        "$session/prompts/review-clarity-2.md" \
        "$session/prompts/review-clarity-3.md" \
        | LC_ALL=C sort)"

    # Expected: all 20 files in LC_ALL=C sorted order.
    expected="$(printf "f%02d.sh\n" {1..20} | LC_ALL=C sort)"

    if [ "$clarity_files" != "$expected" ]; then
        echo "ASSERTION FAILED: concatenated clarity split file lists do not equal full sorted list" >&2
        echo "expected:" >&2
        printf "%s\n" "$expected" >&2
        echo "got:" >&2
        printf "%s\n" "$clarity_files" >&2
        exit 1
    fi

    # Also verify no file appears in more than one partition (no duplicates).
    # total lines from all partitions must equal 20.
    total_lines="$(grep -h "^f[0-9]" \
        "$session/prompts/review-clarity-1.md" \
        "$session/prompts/review-clarity-2.md" \
        "$session/prompts/review-clarity-3.md" \
        | wc -l | tr -d " ")"
    if [ "$total_lines" -ne 20 ]; then
        echo "ASSERTION FAILED: expected 20 total file lines across clarity partitions, got $total_lines" >&2
        exit 1
    fi

    rm -rf "$session"
'

# ---------------------------------------------------------------------------
# Test 4: Correctness and Edge Cases prompts contain all 20 files
# ---------------------------------------------------------------------------
run_test "correctness_and_edge_cases_contain_all_20_files" '
    session="$(make_session)"
    trap 'rm -rf "$session"' EXIT
    files_arg="$(write_files_list "$session" \
        f01.sh f02.sh f03.sh f04.sh f05.sh f06.sh f07.sh f08.sh \
        f09.sh f10.sh f11.sh f12.sh f13.sh f14.sh f15.sh f16.sh \
        f17.sh f18.sh f19.sh f20.sh)"

    run_script "$session" "$files_arg" 1 8 >/dev/null

    for t in correctness edge-cases; do
        prompt="$session/prompts/review-${t}.md"
        for n in $(seq -w 01 20); do
            fname="f${n}.sh"
            if ! grep -qF "$fname" "$prompt"; then
                echo "ASSERTION FAILED: $t prompt is missing $fname" >&2
                exit 1
            fi
        done
        # Verify the file count in the prompt: all 20 files must appear.
        file_line_count="$(grep -c "^f[0-9]" "$prompt" || true)"
        if [ "$file_line_count" -ne 20 ]; then
            echo "ASSERTION FAILED: $t prompt has $file_line_count file lines, expected 20" >&2
            exit 1
        fi
    done

    rm -rf "$session"
'

# ---------------------------------------------------------------------------
# Test 5: Review Consolidator expected_paths lists one path per split instance (8 paths)
# ---------------------------------------------------------------------------
run_test "big_head_expected_paths_one_per_split_instance" '
    session="$(make_session)"
    trap 'rm -rf "$session"' EXIT
    files_arg="$(write_files_list "$session" \
        f01.sh f02.sh f03.sh f04.sh f05.sh f06.sh f07.sh f08.sh \
        f09.sh f10.sh f11.sh f12.sh f13.sh f14.sh f15.sh f16.sh \
        f17.sh f18.sh f19.sh f20.sh)"

    run_script "$session" "$files_arg" 1 8 >/dev/null

    brief="$session/prompts/review-big-head-consolidation.md"

    # The expected_paths section uses "- " list items after "Expected report paths".
    # Count those items. The awk range pattern depends on a blank line terminating
    # the paths list in the generated brief; if the output format changes (e.g.
    # trailing newline removed), this extraction will capture too many/few lines.
    path_count="$(awk "/Expected report paths/,/^$/" "$brief" | grep -c "^- " || true)"
    if [ "$path_count" -ne 8 ]; then
        echo "ASSERTION FAILED: Review Consolidator brief has $path_count expected_paths entries, want 8" >&2
        echo "Brief excerpt:" >&2
        awk "/Expected report paths/,/^$/" "$brief" >&2
        exit 1
    fi

    # Each split instance must have its own entry in the expected paths.
    for t in clarity-1 clarity-2 clarity-3 edge-cases correctness drift-1 drift-2 drift-3; do
        if ! grep -qF "${t}-review-20260317-120000.md" "$brief"; then
            echo "ASSERTION FAILED: Review Consolidator brief missing expected path for $t" >&2
            exit 1
        fi
    done

    # Unsplit clarity and drift must NOT appear as path entries.
    for t in clarity drift; do
        # Match the exact path pattern "<type>-review-<timestamp>.md" (not clarity-1, etc.)
        if grep -qE "/${t}-review-[0-9]{8}-[0-9]{6}\.md" "$brief"; then
            echo "ASSERTION FAILED: Review Consolidator brief has unsplit path entry for $t" >&2
            exit 1
        fi
    done

    rm -rf "$session"
'

# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------
echo ""
echo "========================================"
echo "Results: $PASS passed, $FAIL failed"
echo "========================================"

if [ "$FAIL" -gt 0 ]; then
    exit 1
fi
exit 0

#!/usr/bin/env bash
# test_build_review_prompts.sh — Shell tests for file partitioning logic in
# build-review-prompts.sh (AF-166).
#
# Test cases:
#   1. Below threshold (5 files, threshold 8): single instance per type, 4 prompts total.
#   2. At threshold (8 files, threshold 8): single instance per type, no split.
#   3. Above threshold (20 files, threshold 8): Clarity and Drift split; 3 partitions each.
#      Correctness and Edge Cases always contain the full file list.
#   4. Partition coverage: every file appears in exactly one Clarity instance and
#      one Drift instance (no duplication, no omission).
#   5. Sorting: files in prompts are LC_ALL=C sorted.
#   6. extract_focus_block strips -N suffix: clarity-1 focus block matches clarity focus block.
#   7. Custom threshold via env var (REVIEW_SPLIT_THRESHOLD=3 with 5 files → 2 partitions).
#   8. Round 2 never partitions regardless of file count.
#
# Each test runs in its own subshell. Failures are counted; the script exits
# non-zero if any test failed.
#
# Usage:
#   bash tests/test_build_review_prompts.sh

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

# make_session — creates a temp session directory and writes a files list.
# Prints the session dir path.
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
# Test 1: Below threshold — single instance per type (4 prompts)
# ---------------------------------------------------------------------------
run_test "below_threshold_single_instance_per_type" '
    session="$(make_session)"
    files_arg="$(write_files_list "$session" a.sh b.sh c.sh d.sh e.sh)"

    run_script "$session" "$files_arg" 1 >/dev/null

    # Expect exactly: clarity, edge-cases, correctness, drift
    for t in clarity edge-cases correctness drift; do
        if [ ! -f "$session/prompts/review-${t}.md" ]; then
            echo "ASSERTION FAILED: expected prompt for $t not found" >&2
            exit 1
        fi
    done

    # Must NOT have split instances
    for t in clarity-1 clarity-2 drift-1 drift-2; do
        if [ -f "$session/prompts/review-${t}.md" ]; then
            echo "ASSERTION FAILED: unexpected split prompt found: $t" >&2
            exit 1
        fi
    done

    # Exactly 4 review prompt files (excluding big-head)
    count="$(ls "$session/prompts"/review-*.md 2>/dev/null | grep -v big-head | wc -l | tr -d " ")"
    if [ "$count" -ne 4 ]; then
        echo "ASSERTION FAILED: expected 4 prompts, got $count" >&2
        exit 1
    fi

    rm -rf "$session"
'

# ---------------------------------------------------------------------------
# Test 2: At threshold — no split (8 files, threshold 8)
# ---------------------------------------------------------------------------
run_test "at_threshold_no_split" '
    session="$(make_session)"
    # Generate exactly 8 files
    files_arg="$(write_files_list "$session" \
        a.sh b.sh c.sh d.sh e.sh f.sh g.sh h.sh)"

    run_script "$session" "$files_arg" 1 8 >/dev/null

    # Single instances only
    for t in clarity edge-cases correctness drift; do
        if [ ! -f "$session/prompts/review-${t}.md" ]; then
            echo "ASSERTION FAILED: expected prompt for $t not found" >&2
            exit 1
        fi
    done
    for t in clarity-1 drift-1; do
        if [ -f "$session/prompts/review-${t}.md" ]; then
            echo "ASSERTION FAILED: unexpected split prompt found: $t" >&2
            exit 1
        fi
    done

    rm -rf "$session"
'

# ---------------------------------------------------------------------------
# Test 3: Above threshold — Clarity and Drift split; 3 partitions (20 files, threshold 8)
# ---------------------------------------------------------------------------
run_test "above_threshold_split_three_partitions" '
    session="$(make_session)"
    # 20 files → ceil(20/8) = 3 partitions
    files_arg="$(write_files_list "$session" \
        f01.sh f02.sh f03.sh f04.sh f05.sh f06.sh f07.sh f08.sh \
        f09.sh f10.sh f11.sh f12.sh f13.sh f14.sh f15.sh f16.sh \
        f17.sh f18.sh f19.sh f20.sh)"

    run_script "$session" "$files_arg" 1 8 >/dev/null

    # clarity-1, clarity-2, clarity-3, edge-cases, correctness, drift-1, drift-2, drift-3
    for t in clarity-1 clarity-2 clarity-3 edge-cases correctness drift-1 drift-2 drift-3; do
        if [ ! -f "$session/prompts/review-${t}.md" ]; then
            echo "ASSERTION FAILED: expected prompt for $t not found" >&2
            exit 1
        fi
    done

    # No unsplit clarity or drift
    for t in clarity drift; do
        if [ -f "$session/prompts/review-${t}.md" ]; then
            echo "ASSERTION FAILED: unexpected unsplit prompt found: $t" >&2
            exit 1
        fi
    done

    rm -rf "$session"
'

# ---------------------------------------------------------------------------
# Test 4: Partition coverage — every file appears in exactly one Clarity instance
#         and exactly one Drift instance (no duplicates, no omissions)
# ---------------------------------------------------------------------------
run_test "partition_coverage_no_duplicates_no_omissions" '
    session="$(make_session)"
    # 20 files → 3 partitions
    files_arg="$(write_files_list "$session" \
        f01.sh f02.sh f03.sh f04.sh f05.sh f06.sh f07.sh f08.sh \
        f09.sh f10.sh f11.sh f12.sh f13.sh f14.sh f15.sh f16.sh \
        f17.sh f18.sh f19.sh f20.sh)"

    run_script "$session" "$files_arg" 1 8 >/dev/null

    # Collect all files from Clarity partitions
    clarity_files="$(grep -h "\.sh" \
        "$session/prompts/review-clarity-1.md" \
        "$session/prompts/review-clarity-2.md" \
        "$session/prompts/review-clarity-3.md" \
        | grep "^f[0-9]" | LC_ALL=C sort)"

    # Collect all files from Drift partitions
    drift_files="$(grep -h "\.sh" \
        "$session/prompts/review-drift-1.md" \
        "$session/prompts/review-drift-2.md" \
        "$session/prompts/review-drift-3.md" \
        | grep "^f[0-9]" | LC_ALL=C sort)"

    # Expected: all 20 files sorted
    expected="$(printf "f%02d.sh\n" {1..20} | LC_ALL=C sort)"

    if [ "$clarity_files" != "$expected" ]; then
        echo "ASSERTION FAILED: clarity partitions do not cover all files exactly once" >&2
        echo "expected: $expected" >&2
        echo "got:      $clarity_files" >&2
        exit 1
    fi

    if [ "$drift_files" != "$expected" ]; then
        echo "ASSERTION FAILED: drift partitions do not cover all files exactly once" >&2
        echo "expected: $expected" >&2
        echo "got:      $drift_files" >&2
        exit 1
    fi

    rm -rf "$session"
'

# ---------------------------------------------------------------------------
# Test 5: Correctness and Edge Cases always get full file list when split
# ---------------------------------------------------------------------------
run_test "correctness_and_edge_cases_always_full_list" '
    session="$(make_session)"
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
    done

    rm -rf "$session"
'

# ---------------------------------------------------------------------------
# Test 6: Files are LC_ALL=C sorted before partitioning
#         (files in partition 1 should be the lexicographically first N files)
# ---------------------------------------------------------------------------
run_test "files_lc_all_c_sorted_before_partitioning" '
    session="$(make_session)"
    # Deliberately pass files in reverse order; partitioning should use sorted order.
    files_arg="$(write_files_list "$session" \
        z.sh y.sh x.sh w.sh v.sh u.sh t.sh s.sh r.sh q.sh)"

    run_script "$session" "$files_arg" 1 4 >/dev/null

    # With threshold=4, 10 files → 3 partitions.
    # LC_ALL=C sort: q.sh r.sh s.sh t.sh | u.sh v.sh w.sh x.sh | y.sh z.sh
    # Partition 1 (clarity-1) must contain q.sh, r.sh, s.sh, t.sh only.
    part1="$session/prompts/review-clarity-1.md"
    for expected_file in q.sh r.sh s.sh t.sh; do
        if ! grep -qF "$expected_file" "$part1"; then
            echo "ASSERTION FAILED: clarity-1 missing expected file: $expected_file" >&2
            exit 1
        fi
    done
    # Partition 1 must NOT contain files from partition 2+
    for unexpected_file in u.sh v.sh w.sh x.sh y.sh z.sh; do
        if grep -qF "$unexpected_file" "$part1"; then
            echo "ASSERTION FAILED: clarity-1 contains out-of-partition file: $unexpected_file" >&2
            exit 1
        fi
    done

    rm -rf "$session"
'

# ---------------------------------------------------------------------------
# Test 7: extract_focus_block strips -N suffix — clarity-1 focus == clarity focus
# ---------------------------------------------------------------------------
run_test "extract_focus_block_strips_suffix" '
    session="$(make_session)"
    files_arg="$(write_files_list "$session" \
        f01.sh f02.sh f03.sh f04.sh f05.sh \
        f06.sh f07.sh f08.sh f09.sh f10.sh)"

    run_script "$session" "$files_arg" 1 4 >/dev/null

    # The "## Focus" section of clarity-1 must contain the same content as the
    # canonical clarity focus block (Readable, consistent, well-documented).
    if ! grep -qF "Readable, consistent, well-documented" "$session/prompts/review-clarity-1.md"; then
        echo "ASSERTION FAILED: clarity-1 focus block does not match clarity focus" >&2
        exit 1
    fi

    # Similarly drift-1 must contain the drift focus text
    if ! grep -qF "The system agrees with itself" "$session/prompts/review-drift-1.md"; then
        echo "ASSERTION FAILED: drift-1 focus block does not match drift focus" >&2
        exit 1
    fi

    rm -rf "$session"
'

# ---------------------------------------------------------------------------
# Test 8: Custom threshold via REVIEW_SPLIT_THRESHOLD env var (threshold=3, 5 files → 2 partitions)
# ---------------------------------------------------------------------------
run_test "custom_threshold_env_var" '
    session="$(make_session)"
    files_arg="$(write_files_list "$session" a.sh b.sh c.sh d.sh e.sh)"

    run_script "$session" "$files_arg" 1 3 >/dev/null

    # 5 files with threshold 3 → ceil(5/3) = 2 partitions
    for t in clarity-1 clarity-2 drift-1 drift-2; do
        if [ ! -f "$session/prompts/review-${t}.md" ]; then
            echo "ASSERTION FAILED: expected split prompt $t not found" >&2
            exit 1
        fi
    done

    # No clarity-3 or drift-3
    for t in clarity-3 drift-3; do
        if [ -f "$session/prompts/review-${t}.md" ]; then
            echo "ASSERTION FAILED: unexpected extra partition $t found" >&2
            exit 1
        fi
    done

    # Partition 1 should have first 3 files (sorted), partition 2 should have remaining 2
    part1_clarity="$session/prompts/review-clarity-1.md"
    for f in a.sh b.sh c.sh; do
        if ! grep -qF "$f" "$part1_clarity"; then
            echo "ASSERTION FAILED: clarity-1 missing $f" >&2
            exit 1
        fi
    done
    part2_clarity="$session/prompts/review-clarity-2.md"
    for f in d.sh e.sh; do
        if ! grep -qF "$f" "$part2_clarity"; then
            echo "ASSERTION FAILED: clarity-2 missing $f" >&2
            exit 1
        fi
    done

    rm -rf "$session"
'

# ---------------------------------------------------------------------------
# Test 9: Round 2 never partitions regardless of file count
# ---------------------------------------------------------------------------
run_test "round2_never_partitions" '
    session="$(make_session)"
    # 20 files would normally trigger splitting in round 1
    files_arg="$(write_files_list "$session" \
        f01.sh f02.sh f03.sh f04.sh f05.sh f06.sh f07.sh f08.sh \
        f09.sh f10.sh f11.sh f12.sh f13.sh f14.sh f15.sh f16.sh \
        f17.sh f18.sh f19.sh f20.sh)"

    run_script "$session" "$files_arg" 2 8 >/dev/null

    # Round 2: only correctness and edge-cases, both unsplit
    for t in correctness edge-cases; do
        if [ ! -f "$session/prompts/review-${t}.md" ]; then
            echo "ASSERTION FAILED: round 2 expected $t prompt not found" >&2
            exit 1
        fi
    done

    # No clarity, no drift at all
    for t in clarity clarity-1 drift drift-1; do
        if [ -f "$session/prompts/review-${t}.md" ]; then
            echo "ASSERTION FAILED: round 2 should not produce $t prompt" >&2
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

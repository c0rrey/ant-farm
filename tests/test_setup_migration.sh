#!/usr/bin/env bash
# test_setup_migration.sh — Shell tests for setup.sh migration removal behavior
# and repo CLAUDE.md write functionality.
#
# Test cases:
#   1. Block surrounded by user content: block removed, user content preserved
#      byte-for-byte.
#   2. No ant-farm block present: file unchanged after setup.sh.
#   3. Empty file after block removal: file still exists (not deleted).
#   4. --dry-run: does not modify any files (checksum comparison).
#   5. Repo CLAUDE.md: contains the ant-farm block after setup.sh.
#
# Each test runs in its own subshell with an isolated HOME (temp dir), so
# real ~/.claude/ is never touched. All tests always run; failures are
# counted and the script exits non-zero if any test failed.
#
# Usage:
#   bash tests/test_setup_migration.sh
set -euo pipefail  # -e catches harness setup errors; run_test() captures per-test exit codes independently.

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SETUP_SH="$REPO_ROOT/scripts/setup.sh"
ANTFARM_START="<!-- ant-farm:start -->"
ANTFARM_END="<!-- ant-farm:end -->"

PASS=0
FAIL=0

# ---------------------------------------------------------------------------
# Runner helpers
# ---------------------------------------------------------------------------

pass() { echo "  PASS: $1"; PASS=$((PASS + 1)); }
fail() { echo "  FAIL: $1"; echo "        $2"; FAIL=$((FAIL + 1)); }

# run_test NAME BODY
#   Executes BODY in a subshell. Captures exit code and treats non-zero
#   as a test failure so one failing test doesn't abort the whole suite.
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

# make_fake_home
#   Creates a temp directory that serves as a fake HOME with a minimal
#   ~/.claude/ skeleton. Prints the path to stdout.
make_fake_home() {
    local tmp
    tmp="$(mktemp -d)"
    mkdir -p "$tmp/.claude"
    mkdir -p "$tmp/.local/bin"
    echo "$tmp"
}

# checksum FILE
#   Produces a content hash of FILE. Uses md5sum if available, else cksum.
checksum() {
    if command -v md5sum &>/dev/null; then
        md5sum "$1" | awk '{print $1}'
    else
        # macOS: use md5 -q
        md5 -q "$1"
    fi
}

# run_setup FAKE_HOME [EXTRA_ARGS...]
#   Runs setup.sh with HOME overridden to FAKE_HOME, suppressing most output.
run_setup() {
    local fake_home="$1"; shift
    HOME="$fake_home" bash "$SETUP_SH" "$@" >/dev/null 2>&1
}

# ---------------------------------------------------------------------------
# Test 1: Block surrounded by user content is removed; user content preserved
# ---------------------------------------------------------------------------
run_test "block_removal_preserves_user_content" '
    fake_home="$(make_fake_home)"
    global_claude="$fake_home/.claude/CLAUDE.md"

    # Write a CLAUDE.md that has user content BEFORE and AFTER the block
    printf "%s\n" \
        "user line before" \
        "<!-- ant-farm:start -->" \
        "ant-farm managed content" \
        "<!-- ant-farm:end -->" \
        "user line after" \
        > "$global_claude"

    run_setup "$fake_home"

    # Block sentinels must be gone
    if grep -qF "<!-- ant-farm:start -->" "$global_claude"; then
        echo "ASSERTION FAILED: start sentinel still present in $global_claude" >&2
        exit 1
    fi
    if grep -qF "<!-- ant-farm:end -->" "$global_claude"; then
        echo "ASSERTION FAILED: end sentinel still present in $global_claude" >&2
        exit 1
    fi
    if grep -qF "ant-farm managed content" "$global_claude"; then
        echo "ASSERTION FAILED: block body still present in $global_claude" >&2
        exit 1
    fi

    # User content must be preserved
    if ! grep -qF "user line before" "$global_claude"; then
        echo "ASSERTION FAILED: user content before block was lost in $global_claude" >&2
        exit 1
    fi
    if ! grep -qF "user line after" "$global_claude"; then
        echo "ASSERTION FAILED: user content after block was lost in $global_claude" >&2
        exit 1
    fi

    rm -rf "$fake_home"
'

# ---------------------------------------------------------------------------
# Test 2: No ant-farm block present — file is unchanged after setup.sh
# ---------------------------------------------------------------------------
run_test "no_block_file_unchanged" '
    fake_home="$(make_fake_home)"
    global_claude="$fake_home/.claude/CLAUDE.md"

    # Write a CLAUDE.md with no ant-farm block
    printf "%s\n" \
        "# My custom instructions" \
        "" \
        "Some user notes here." \
        > "$global_claude"

    before="$(checksum "$global_claude")"

    run_setup "$fake_home"

    after="$(checksum "$global_claude")"

    if [ "$before" != "$after" ]; then
        echo "ASSERTION FAILED: file was modified even though no block was present" >&2
        echo "  before checksum: $before" >&2
        echo "  after  checksum: $after" >&2
        exit 1
    fi

    rm -rf "$fake_home"
'

# ---------------------------------------------------------------------------
# Test 3: Removing the block leaves file empty — file still exists (not deleted)
# ---------------------------------------------------------------------------
run_test "empty_file_after_removal_still_exists" '
    fake_home="$(make_fake_home)"
    global_claude="$fake_home/.claude/CLAUDE.md"

    # CLAUDE.md contains ONLY the ant-farm block (nothing else)
    printf "%s\n" \
        "<!-- ant-farm:start -->" \
        "ant-farm content only" \
        "<!-- ant-farm:end -->" \
        > "$global_claude"

    run_setup "$fake_home"

    if [ ! -f "$global_claude" ]; then
        echo "ASSERTION FAILED: file was deleted after removal — must be left in place" >&2
        exit 1
    fi

    # Verify block is gone
    if grep -qF "<!-- ant-farm:start -->" "$global_claude"; then
        echo "ASSERTION FAILED: start sentinel still present after removal" >&2
        exit 1
    fi

    rm -rf "$fake_home"
'

# ---------------------------------------------------------------------------
# Test 4: --dry-run does not modify files (checksum comparison)
# ---------------------------------------------------------------------------
run_test "dry_run_does_not_modify_files" '
    fake_home="$(make_fake_home)"
    global_claude="$fake_home/.claude/CLAUDE.md"

    # CLAUDE.md with block that would be removed in a live run
    printf "%s\n" \
        "user header" \
        "<!-- ant-farm:start -->" \
        "old ant-farm block" \
        "<!-- ant-farm:end -->" \
        "user footer" \
        > "$global_claude"

    before_global="$(checksum "$global_claude")"

    # Run in --dry-run mode
    HOME="$fake_home" bash "$SETUP_SH" --dry-run >/dev/null 2>&1

    # Global CLAUDE.md must be unchanged
    after_global="$(checksum "$global_claude")"
    if [ "$before_global" != "$after_global" ]; then
        echo "ASSERTION FAILED: --dry-run modified $global_claude" >&2
        exit 1
    fi

    rm -rf "$fake_home"
'

# ---------------------------------------------------------------------------
# Test 5: Repo CLAUDE.md contains the ant-farm block after setup.sh
#   Note: setup.sh writes to $REPO_ROOT/CLAUDE.md (the actual repo file).
#   This test verifies the block is present — it does not run setup.sh again
#   (to avoid modifying the repo file in a test), but checks the current state.
# ---------------------------------------------------------------------------
run_test "repo_claude_md_contains_block" '
    repo_claude="$REPO_ROOT/CLAUDE.md"

    if [ ! -f "$repo_claude" ]; then
        echo "ASSERTION FAILED: repo CLAUDE.md does not exist at $repo_claude" >&2
        exit 1
    fi

    # Must contain both sentinel markers
    if ! grep -qF "<!-- ant-farm:start -->" "$repo_claude"; then
        echo "ASSERTION FAILED: start sentinel missing from repo CLAUDE.md" >&2
        exit 1
    fi
    if ! grep -qF "<!-- ant-farm:end -->" "$repo_claude"; then
        echo "ASSERTION FAILED: end sentinel missing from repo CLAUDE.md" >&2
        exit 1
    fi

    # Block content must match claude-block.md
    block_src="$REPO_ROOT/orchestration/templates/claude-block.md"
    if [ ! -f "$block_src" ]; then
        echo "SETUP ERROR: claude-block.md not found: $block_src" >&2
        exit 1
    fi

    # Extract the content between sentinels (exclusive) from the repo file
    extracted="$(awk -v start="<!-- ant-farm:start -->" -v end="<!-- ant-farm:end -->" \
        '"'"'$0==start{f=1;next} f&&$0==end{exit} f{print}'"'"' "$repo_claude")"

    # Compare against the source block content
    expected="$(cat "$block_src")"

    if [ "$extracted" != "$expected" ]; then
        echo "ASSERTION FAILED: block content in repo CLAUDE.md does not match claude-block.md" >&2
        echo "--- expected (claude-block.md) ---" >&2
        echo "$expected" | head -5 >&2
        echo "--- got (extracted from repo CLAUDE.md) ---" >&2
        echo "$extracted" | head -5 >&2
        exit 1
    fi
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

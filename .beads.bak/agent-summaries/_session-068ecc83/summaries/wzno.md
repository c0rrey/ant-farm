# Fix Summary: ant-farm-wzno

## Task
Correct a misleading "POSIX-compatible" heading comment in the key-value store section of `scripts/parse-progress-log.sh`. The comment claimed POSIX compatibility while the script freely uses bash-only constructs (e.g., `[[ =~ ]]`). The actual portability target is bash 3+, not POSIX sh.

## Design Approaches Considered

1. **Change line 105 only (minimal)**: Replace "POSIX-compatible" with "Bash 3+-compatible (replaces bash 4+ `declare -A`)" on the heading line and leave line 106 intact, accepting mild redundancy. Lowest risk, smallest diff.

2. **Merge heading and detail into one line, drop line 106**: Combine the heading description and the `declare -A` detail to eliminate redundancy. Cleaner result but removes a line users may rely on for context.

3. **Rewrite the entire header block**: Restructure all of lines 104-112 with fuller portability notes. Most thorough but exceeds the minimal fix scope.

4. **Replace only the word "POSIX-compatible" in place**: Single-word substitution on line 105, leaving surrounding text unchanged. Most minimal but leaves "POSIX-compatible" removed without any replacement context.

**Chosen approach**: Option 1 extended — changed line 105 to state "Bash 3+-compatible key-value store (replaces bash 4+ `declare -A`) using a temp directory" and replaced the now-redundant old line 106 with a clarifying note that the rest of the script also uses bash-only constructs (e.g., `[[ =~ ]]`) and that the portability target is bash 3+, not POSIX sh. This satisfies all three acceptance criteria, keeps the diff minimal (comment-only), and adds useful context about why the script is not POSIX sh.

## Files Changed

- `scripts/parse-progress-log.sh` — lines 105-107 (comment heading only, no code logic changed)

## Change Made

Before:
```
# ---------------------------------------------------------------------------
# POSIX-compatible key-value store using a temp directory.
# Replaces bash 4+ declare -A associative arrays.
# Each "map" is a subdirectory; each entry is a file named after the key.
```

After:
```
# ---------------------------------------------------------------------------
# Bash 3+-compatible key-value store (replaces bash 4+ `declare -A`) using a temp directory.
# Note: the rest of this script uses bash-only constructs (e.g. [[ =~ ]]) — portability
# target is bash 3+, not POSIX sh.
# Each "map" is a subdirectory; each entry is a file named after the key.
```

## Acceptance Criteria Verification

1. The comment heading no longer claims "POSIX-compatible" or "POSIX" compatibility — confirmed. The word "POSIX" appears only in the new note as "not POSIX sh" (a negation, not a claim).
2. The comment accurately states "Bash 3+" as the portability target — confirmed on line 105 ("Bash 3+-compatible") and line 107 ("target is bash 3+").
3. No code logic changed — only comment text on lines 105-107 was modified — confirmed.

## Commit

Branch: main
Commit message: `fix: correct POSIX-compatible comment to Bash 3+-compatible in parse-progress-log.sh (ant-farm-wzno)`
Commit hash: (recorded by Queen after `git pull --rebase && git add scripts/parse-progress-log.sh && git commit`)

## Assumptions Audit

- No assumptions were made about the intended runtime environment beyond what the task context stated (bash 3+).
- Adjacent issue noted: the script has other comment sections that may still imply portability without specifying bash version. These were observed but not touched per scope boundaries.
- The `[[ =~ ]]` construct referenced in the task appears at line ~169 of the file (not in the key-value store section). The fix accurately acknowledges this in the new note.

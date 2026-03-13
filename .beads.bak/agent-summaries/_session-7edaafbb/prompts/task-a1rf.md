# Task Brief: ant-farm-a1rf
**Task**: Bash scripting edge cases under set -euo pipefail
**Agent Type**: devops-engineer
**Summary output path**: .beads/agent-summaries/_session-7edaafbb/summaries/a1rf.md

## Context
- **Affected files**:
  - scripts/scrub-pii.sh:L52-55 -- grep -c returns non-zero on no match, which triggers set -e abort. Specifically L66: `REMAINING=$(grep -cE "$PII_FIELD_PATTERN" "$ISSUES_FILE" 2>/dev/null)` will exit 1 if no matches found, but the script expects to continue.
  - orchestration/RULES.md:L146-148 -- tr+sed whitespace check: `echo "${CHANGED_FILES}" | tr -s ' \n' | sed 's/^[[:space:]]*//;s/[[:space:]]*$//'` is fragile. The `-z` test on the subshell output may not behave consistently on all platforms.
  - scripts/install-hooks.sh:L27-31 -- backup cp failure: `cp "$HOOK_TARGET" "$BACKUP"` is not wrapped in error handling, so if the cp fails (e.g., permissions), set -e terminates the script without a clear error message.
- **Root cause**: Multiple bash scripts use constructs that are correct but subtly platform-sensitive under strict error handling (set -euo pipefail). grep -c returns non-zero on no match, which triggers set -e. tr+sed whitespace check is fragile across platforms. backup cp failure is not gracefully handled.
- **Expected behavior**: Add clarifying comments explaining the set -e interaction; simplify the whitespace check in RULES.md; wrap backup cp in install-hooks.sh with graceful failure handling.
- **Acceptance criteria**:
  1. grep -c usage has clarifying comment or is wrapped to prevent set -e exit
  2. Whitespace check simplified
  3. Backup cp wrapped with graceful failure handling

## Scope Boundaries
Read ONLY:
- scripts/scrub-pii.sh:L45-78 (PII pattern matching and verification section)
- orchestration/RULES.md:L140-155 (review input validation section)
- scripts/install-hooks.sh:L20-35 (backup and hook generation section)

Do NOT edit:
- scripts/scrub-pii.sh outside L45-78 (argument parsing, perl substitution logic)
- orchestration/RULES.md outside L140-155 (workflow steps, review protocol sections)
- scripts/install-hooks.sh outside L20-35 (pre-commit hook section)
- orchestration/templates/reviews.md
- scripts/fill-review-slots.sh

## Focus
Your task is ONLY to harden three specific bash constructs: (1) grep -c set -e interaction in scrub-pii.sh, (2) whitespace check in RULES.md, (3) backup cp failure handling in install-hooks.sh.
Do NOT fix adjacent issues you notice.

## Summary Doc Sections (all required)
1. Approaches Considered (4+ genuinely distinct)
2. Selected Approach with rationale
3. Implementation description
4. Correctness Review (per-file, with acceptance criteria verification)
5. Build/Test Validation
6. Acceptance Criteria checklist (each criterion + PASS/FAIL)

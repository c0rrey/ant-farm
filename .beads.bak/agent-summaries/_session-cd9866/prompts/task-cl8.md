# Task Brief: ant-farm-cl8
**Task**: scrub-pii.sh only matches quoted emails, misses unquoted occurrences
**Agent Type**: devops-engineer
**Summary output path**: .beads/agent-summaries/_session-cd9866/summaries/cl8.md

## Context
- **Affected files**: scripts/scrub-pii.sh:L38 (--check mode regex wraps PII pattern in double-quote anchors: `grep -qE "\"$PII_PATTERN\""` only matches `"email@example.com"` patterns), scripts/scrub-pii.sh:L52 (post-scrub verification regex also uses double-quote anchors: `grep -qE '"[pattern]"'` missing unquoted emails)
- **Root cause**: Both the --check mode (L38) and the post-scrub verification (L52) in scrub-pii.sh wrap the PII regex with double-quote anchors. The --check grep pattern is `"\"$PII_PATTERN\""` which only matches emails wrapped in double quotes (e.g., `"user@example.com"`). If an email appears unquoted in the JSONL (e.g., as a bare value, in a comment, or in a non-standard field), the check passes falsely and the scrub at L50 also only replaces quoted emails (using `s/"(pattern)"/"ctc"/g`). The scrub regex at L50 and the verification at L52-53 both use quote-anchored patterns.
- **Expected behavior**: --check mode detects emails regardless of quoting context. The scrub handles both quoted and unquoted email occurrences.
- **Acceptance criteria**:
  1. --check mode (L38) detects email addresses regardless of quoting context (with or without surrounding double quotes)
  2. Scrub operation (L50) and post-scrub verification (L52) handle both quoted and unquoted email patterns

## Scope Boundaries
Read ONLY: scripts/scrub-pii.sh:L1-59
Do NOT edit: scripts/install-hooks.sh, docs/installation-guide.md, orchestration/ files

## Focus
Your task is ONLY to fix the PII regex patterns in scrub-pii.sh to match emails regardless of quoting context.
Do NOT fix adjacent issues you notice.

## Summary Doc Sections (all required)
1. Approaches Considered (4+ genuinely distinct)
2. Selected Approach with rationale
3. Implementation description
4. Correctness Review (per-file, with acceptance criteria verification)
5. Build/Test Validation
6. Acceptance Criteria checklist (each criterion + PASS/FAIL)

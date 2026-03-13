# Fix Brief: ant-farm-aqlp

## Context
Review finding RC-2 (P2): In `scripts/compose-review-skeletons.sh`, the `sed` substitution at lines ~108 and ~163 converts ALL `{UPPERCASE}` tokens without an explicit allowlist. The comment also says "2+ chars" but the regex `[A-Z][A-Z_]*` matches 1+ chars. Risk: silently corrupting display text that happens to match the pattern.

## Fix
Two changes needed:
1. Fix the regex from `[A-Z][A-Z_]*` to `[A-Z][A-Z_]+` (requires 2+ uppercase chars, matching the comment's claim) at both sed substitution sites (~line 108 and ~163).
2. Add a comment above each sed block listing the canonical slot names that the regex is expected to match (e.g., REVIEW_TYPE, REVIEW_ROUND, DATA_FILE_PATH, REPORT_OUTPUT_PATH, CONSOLIDATED_OUTPUT_PATH, SESSION_DIR, COMMIT_RANGE, CHANGED_FILES, TASK_IDS, REVIEW_TIMESTAMP, MODEL).

## Scope Boundaries
- **Edit ONLY**: `scripts/compose-review-skeletons.sh` (the two sed substitution blocks)
- **Do NOT edit**: Any other file

## Acceptance Criteria
1. Regex at both sed sites uses `[A-Z][A-Z_]+` (2+ chars) instead of `[A-Z][A-Z_]*` (1+ chars)
2. A comment listing canonical slot names appears above each sed block
3. No other lines are modified beyond these targeted changes

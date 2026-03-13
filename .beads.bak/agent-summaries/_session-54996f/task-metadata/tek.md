# Task: ant-farm-tek
**Status**: success
**Title**: Polling loop in reviews.md Step 0a uses fragile wc -l line-counting with globs
**Type**: bug
**Priority**: P2
**Epic**: _standalone
**Agent Type**: prompt-engineer
**Dependencies**: blocks: [], blockedBy: []

## Affected Files
- orchestration/templates/reviews.md:370-383 — Polling loop that uses wc -l to count found report files; variable naming is inverted (stores found files but named MISSING_REPORTS), vulnerable to count exceeding 4 on re-runs, no post-loop timeout detection

## Root Cause
The polling loop in reviews.md Step 0a (lines 370-383) uses a fragile pattern: it chains 4 ls commands with && into a MISSING_REPORTS variable, then checks wc -l equals 4. Problems: (1) Variable name is inverted — it stores found files, not missing ones. (2) If a glob matches multiple files (e.g., from a re-run), wc -l exceeds 4 and the loop never breaks, silently timing out. (3) No post-loop check distinguishes timeout from success. (4) Shell state does not persist between Bash tool calls in Claude Code, so loop variables would reset if Big Head splits execution across calls.

## Expected Behavior
Replace wc -l counting with individual [ -f ] checks per exact filename. Add post-loop timeout detection. Add comment requiring single-invocation execution.

## Acceptance Criteria
1. Polling loop uses individual [ -f ] file existence checks instead of wc -l line counting
2. Variable naming accurately reflects contents (e.g., FOUND_REPORTS or individual checks)
3. Post-loop code distinguishes between timeout and success paths
4. A comment notes that the polling block must execute in a single Bash invocation

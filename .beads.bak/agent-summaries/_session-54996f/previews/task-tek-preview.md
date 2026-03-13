Execute bug for ant-farm-tek.

Step 0: Read your task context from .beads/agent-summaries/_session-54996f/prompts/task-tek.md
(Contains: affected files, root cause, acceptance criteria, scope boundaries.)

Execute these 6 steps in order:

1. **Claim**: `bd show ant-farm-tek` + `bd update ant-farm-tek --status=in_progress`
2. **Design** (MANDATORY): 4+ genuinely distinct approaches with tradeoffs. Document choice before coding.
3. **Implement**: Write clean, minimal code satisfying acceptance criteria.
4. **Review** (MANDATORY): Re-read EVERY changed file. Verify acceptance criteria. Assumptions audit.
5. **Commit**: `git pull --rebase && git add <changed-files> && git commit -m "<type>: <description> (ant-farm-tek)"`
   Use conventional commit type (fix/feat/refactor/etc). Record commit hash in summary doc.
6. **Summary doc** (MANDATORY): Write to .beads/agent-summaries/_session-54996f/summaries/tek.md with all required sections
   (see data file for section list). Only after the summary doc is successfully written:
   `bd close ant-farm-tek`

SCOPE: Only edit files listed in the task context. Document adjacent issues, don't fix them.
Do NOT push to remote. Do NOT modify CHANGELOG/README/CLAUDE.md.

---

# Task Brief: ant-farm-tek
**Task**: Polling loop in reviews.md Step 0a uses fragile wc -l line-counting with globs
**Agent Type**: prompt-engineer
**Summary output path**: .beads/agent-summaries/_session-54996f/summaries/tek.md

## Context
- **Affected files**: orchestration/templates/reviews.md:L370-383 -- Polling loop that uses wc -l to count found report files; variable naming is inverted (stores found files but named MISSING_REPORTS), vulnerable to count exceeding 4 on re-runs, no post-loop timeout detection
- **Root cause**: The polling loop in reviews.md Step 0a (lines 370-383) uses a fragile pattern: it chains 4 ls commands with && into a MISSING_REPORTS variable, then checks wc -l equals 4. Problems: (1) Variable name is inverted -- it stores found files, not missing ones. (2) If a glob matches multiple files (e.g., from a re-run), wc -l exceeds 4 and the loop never breaks, silently timing out. (3) No post-loop check distinguishes timeout from success. (4) Shell state does not persist between Bash tool calls in Claude Code, so loop variables would reset if Big Head splits execution across calls.
- **Expected behavior**: Replace wc -l counting with individual [ -f ] checks per exact filename. Add post-loop timeout detection. Add comment requiring single-invocation execution.
- **Acceptance criteria**:
  1. Polling loop uses individual [ -f ] file existence checks instead of wc -l line counting
  2. Variable naming accurately reflects contents (e.g., FOUND_REPORTS or individual checks)
  3. Post-loop code distinguishes between timeout and success paths
  4. A comment notes that the polling block must execute in a single Bash invocation

## Scope Boundaries
Read ONLY: orchestration/templates/reviews.md:L354-424 (Step 0a remediation path section)
Do NOT edit: Any lines outside L354-424 in reviews.md; any other files in orchestration/templates/

## Focus
Your task is ONLY to fix the fragile wc -l polling loop in reviews.md Step 0a (lines 370-383) by replacing it with individual file existence checks, fixing variable naming, and adding post-loop timeout detection.
Do NOT fix adjacent issues you notice.

## Summary Doc Sections (all required)
1. Approaches Considered (4+ genuinely distinct)
2. Selected Approach with rationale
3. Implementation description
4. Correctness Review (per-file, with acceptance criteria verification)
5. Build/Test Validation
6. Acceptance Criteria checklist (each criterion + PASS/FAIL)

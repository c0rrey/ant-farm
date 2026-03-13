Execute feature for ant-farm-0b4k.

Step 0: Read your task context from .beads/agent-summaries/_session-3a20de/prompts/task-0b4k.md
(Format: markdown. Sections: Context, Scope Boundaries, Focus.)

Execute these 6 steps in order:

1. **Claim**: `bd show ant-farm-0b4k` + `bd update ant-farm-0b4k --status=in_progress`
2. **Design** (MANDATORY) — 4+ genuinely distinct approaches with tradeoffs. Document choice before coding.
3. **Implement**: Write clean, minimal code satisfying acceptance criteria.
4. **Review** (MANDATORY) — Re-read EVERY changed file. Verify acceptance criteria. Assumptions audit.
5. **Commit**: `git pull --rebase && git add <changed-files> && git commit -m "<type>: <description> (ant-farm-0b4k)"`
   Use conventional commit type (fix/feat/refactor/etc). Record commit hash in summary doc.
6. **Summary doc** (MANDATORY) — Write to .beads/agent-summaries/_session-3a20de/summaries/0b4k.md with all required sections
   (see data file for section list). Only after the summary doc is successfully written:
   `bd close ant-farm-0b4k`

SCOPE: Only edit files listed in the task context. Document adjacent issues, don't fix them.
Do NOT push to remote. Do NOT modify CHANGELOG/README/CLAUDE.md.

---

# Task Brief: ant-farm-0b4k
**Task**: Add append-only progress log for Queen crash recovery
**Agent Type**: technical-writer
**Summary output path**: .beads/agent-summaries/_session-3a20de/summaries/0b4k.md

## Context
- **Affected files**:
  - orchestration/RULES.md:L53-150 -- Workflow section (Steps 0-6) where progress log append instructions must be added after each step
  - orchestration/RULES.md:L216-234 -- Session Directory section where progress.log path should be documented
  - NOTE: Scout metadata had bare filename (no line numbers). Lines identified by Pantry via content analysis.
- **Root cause**: If the Queen crashes mid-workflow, the next session has no structured way to determine what completed and what did not. The user must manually inspect session artifacts, git log, and beads status to reconstruct state.
- **Expected behavior**: Queen appends one line to a progress log after each workflow milestone. Recovery sessions read it once to determine the resume point.
- **Acceptance criteria**:
  1. Queen appends exactly one log entry after each workflow milestone listed above
  2. Log is append-only -- Queen never reads or overwrites the file during normal operation
  3. Each entry includes enough context (paths, counts, status) to determine resume point
  4. Progress log is written to {session-dir}/progress.log
  5. Format is human-readable with pipe-delimited fields

## Scope Boundaries
Read ONLY: orchestration/RULES.md:L53-150 (Workflow Steps 0-6), L216-234 (Session Directory section)
Do NOT edit: Queen Prohibitions (L14-21), Queen Read Permissions (L23-52), Hard Gates table (L152-162), Information Diet (L163-172), Agent Types (L174-184), Model Assignments (L186-204), Concurrency Rules (L206-214), Anti-Patterns (L237-251), Template Lookup (L253-268), Retry Limits (L269-278)

## Focus
Your task is ONLY to add append-only progress log instructions to the workflow steps in RULES.md.
Do NOT fix adjacent issues you notice.

## Summary Doc Sections (all required)
1. Approaches Considered (4+ genuinely distinct)
2. Selected Approach with rationale
3. Implementation description
4. Correctness Review (per-file, with acceptance criteria verification)
5. Build/Test Validation
6. Acceptance Criteria checklist (each criterion + PASS/FAIL)

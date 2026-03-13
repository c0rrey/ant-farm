Execute bug for ant-farm-crky.

Step 0: Read your task context from .beads/agent-summaries/_session-54996f/prompts/task-crky.md
(Contains: affected files, root cause, acceptance criteria, scope boundaries.)

Execute these 6 steps in order:

1. **Claim**: `bd show ant-farm-crky` + `bd update ant-farm-crky --status=in_progress`
2. **Design** (MANDATORY): 4+ genuinely distinct approaches with tradeoffs. Document choice before coding.
3. **Implement**: Write clean, minimal code satisfying acceptance criteria.
4. **Review** (MANDATORY): Re-read EVERY changed file. Verify acceptance criteria. Assumptions audit.
5. **Commit**: `git pull --rebase && git add <changed-files> && git commit -m "<type>: <description> (ant-farm-crky)"`
   Use conventional commit type (fix/feat/refactor/etc). Record commit hash in summary doc.
6. **Summary doc** (MANDATORY): Write to .beads/agent-summaries/_session-54996f/summaries/crky.md with all required sections
   (see data file for section list). Only after the summary doc is successfully written:
   `bd close ant-farm-crky`

SCOPE: Only edit files listed in the task context. Document adjacent issues, don't fix them.
Do NOT push to remote. Do NOT modify CHANGELOG/README/CLAUDE.md.

---

# Task Brief: ant-farm-crky
**Task**: Big Head skeleton and reviews.md have divergent failure handling for missing reports
**Agent Type**: prompt-engineer
**Summary output path**: .beads/agent-summaries/_session-54996f/summaries/crky.md

## Context
- **Affected files**:
  - orchestration/templates/big-head-skeleton.md:L57-66 -- Says "FAIL immediately if any missing" with no waiting; failure artifact written to review-consolidated-{TIMESTAMP}-FAILED.md
  - orchestration/templates/reviews.md:L354-424 -- Specifies a 30-second polling loop with timeout before failing; returns inline structured error on timeout
- **Root cause**: Big Head receives contradictory instructions about handling missing Nitpicker reports from two sources: (1) big-head-skeleton.md (lines 57-66) says "FAIL immediately if any missing" with no waiting; (2) reviews.md Step 0a (lines 354-424) specifies a 30-second polling loop with timeout before failing. Big Head must resolve the ambiguity at runtime. Additionally, the failure artifact paths differ: skeleton writes to review-consolidated-{TIMESTAMP}-FAILED.md while reviews.md returns an inline structured error.
- **Expected behavior**: Designate one template as authoritative. Update skeleton to reference the brief for remediation details, or add the polling protocol to the skeleton with consistent failure artifact paths.
- **Acceptance criteria**:
  1. One template is designated authoritative for missing-report handling
  2. The other template references the authoritative one rather than contradicting it
  3. Failure artifact paths are consistent between both templates
  4. Big Head has unambiguous instructions at runtime with no need to resolve contradictions

## Scope Boundaries
Read ONLY: orchestration/templates/big-head-skeleton.md:L47-80, orchestration/templates/reviews.md:L354-424
Do NOT edit: Lines outside the specified ranges; orchestration/RULES.md; orchestration/templates/pantry.md; any agent files

## Focus
Your task is ONLY to reconcile the divergent failure handling between big-head-skeleton.md and reviews.md so Big Head receives unambiguous instructions for missing Nitpicker reports.
Do NOT fix adjacent issues you notice.

## Summary Doc Sections (all required)
1. Approaches Considered (4+ genuinely distinct)
2. Selected Approach with rationale
3. Implementation description
4. Correctness Review (per-file, with acceptance criteria verification)
5. Build/Test Validation
6. Acceptance Criteria checklist (each criterion + PASS/FAIL)

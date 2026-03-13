Execute feature for ant-farm-fomy.

Step 0: Read your task context from .beads/agent-summaries/_session-2bb21f22/prompts/task-fomy.md
(Format: markdown. Sections: Context, Scope Boundaries, Focus.)

Execute these 6 steps in order:

1. **Claim**: `bd show ant-farm-fomy` + `bd update ant-farm-fomy --status=in_progress`
2. **Design** (MANDATORY) — 4+ genuinely distinct approaches with tradeoffs. Document choice before coding.
3. **Implement**: Write clean, minimal code satisfying acceptance criteria.
4. **Review** (MANDATORY) — Re-read EVERY changed file. Verify acceptance criteria. Assumptions audit.
5. **Commit**: `git pull --rebase && git add <changed-files> && git commit -m "<type>: <description> (ant-farm-fomy)"`
   Use conventional commit type (fix/feat/refactor/etc). Record commit hash in summary doc.
6. **Summary doc** (MANDATORY) — Write to .beads/agent-summaries/_session-2bb21f22/summaries/fomy.md with all required sections
   (see task brief for section list). Only after the summary doc is successfully written:
   `bd close ant-farm-fomy`

SCOPE: Only edit files listed in the task context. Document adjacent issues, don't fix them.
Do NOT push to remote. Do NOT modify CHANGELOG/README/CLAUDE.md.

---

# Task Brief: ant-farm-fomy
**Task**: Auto-approve Scout strategy in Step 1
**Agent Type**: technical-writer
**Summary output path**: .beads/agent-summaries/_session-2bb21f22/summaries/fomy.md

## Context
- **Affected files**: orchestration/RULES.md:L90-101 -- Step 1b SSV gate section; user approval gate after SSV PASS
- **Root cause**: The Queen currently waits for user approval after SSV PASS before spawning agents. This adds latency to the workflow. The persistent review team design (ant-farm-ygmj) already auto-approves fix-cycle Scout strategies, establishing precedent.
- **Expected behavior**: RULES.md Step 1b should auto-approve after SSV PASS instead of requiring user confirmation. A complexity threshold may gate auto-approval vs user prompt for larger sessions.
- **Acceptance criteria**:
  1. RULES.md Step 1b no longer requires user approval after SSV PASS
  2. Risk analysis documented: what could go wrong with auto-approval, what safety nets exist
  3. Decision on complexity threshold documented (always auto-approve vs threshold-based)

## Scope Boundaries
Read ONLY: orchestration/RULES.md:L85-110 (Step 1a/1b section and surrounding context)
Do NOT edit: Any file other than orchestration/RULES.md; do NOT edit Steps 2-6 or any other sections of RULES.md outside the Step 1b SSV gate area (L90-101)

## Focus
Your task is ONLY to modify the Step 1b SSV gate in RULES.md so it auto-approves after SSV PASS instead of requiring user confirmation, and to document the risk analysis and complexity threshold decision.
Do NOT fix adjacent issues you notice.

## Summary Doc Sections (all required)
1. Approaches Considered (4+ genuinely distinct)
2. Selected Approach with rationale
3. Implementation description
4. Correctness Review (per-file, with acceptance criteria verification)
5. Build/Test Validation
6. Acceptance Criteria checklist (each criterion + PASS/FAIL)

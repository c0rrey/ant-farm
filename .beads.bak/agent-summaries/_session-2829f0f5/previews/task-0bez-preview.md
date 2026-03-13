Execute bug for ant-farm-0bez.

Step 0: Read your task context from .beads/agent-summaries/_session-2829f0f5/prompts/task-0bez.md
(Format: markdown. Sections: Context, Scope Boundaries, Focus.)

Execute these 6 steps in order:

1. **Claim**: `bd show ant-farm-0bez` + `bd update ant-farm-0bez --status=in_progress`
2. **Design** (MANDATORY) — 4+ genuinely distinct approaches with tradeoffs. Document choice before coding.
3. **Implement**: Write clean, minimal code satisfying acceptance criteria.
4. **Review** (MANDATORY) — Re-read EVERY changed file. Verify acceptance criteria. Assumptions audit.
5. **Commit**: `git pull --rebase && git add <changed-files> && git commit -m "<type>: <description> (ant-farm-0bez)"`
   Use conventional commit type (fix/feat/refactor/etc). Record commit hash in summary doc.
6. **Summary doc** (MANDATORY) — Write to .beads/agent-summaries/_session-2829f0f5/summaries/0bez.md with all required sections
   (see data file for section list). Only after the summary doc is successfully written:
   `bd close ant-farm-0bez`

SCOPE: Only edit files listed in the task context. Document adjacent issues, don't fix them.
Do NOT push to remote. Do NOT modify CHANGELOG/README/CLAUDE.md.

---

# Task Brief: ant-farm-0bez
**Task**: fix: GLOSSARY pre-push hook entry omits sync-to-claude.sh details
**Agent Type**: technical-writer
**Summary output path**: .beads/agent-summaries/_session-2829f0f5/summaries/0bez.md

## Context
- **Affected files**:
  - GLOSSARY.md:L58 -- pre-push hook definition entry
- **Root cause**: GLOSSARY.md:L58 defines the pre-push hook as syncing "agents/*.md to ~/.claude/agents/ and orchestration/ files to ~/.claude/orchestration/" but omits the _archive/ exclusion from rsync, selective script sync (only 2 of 6), the CLAUDE.md copy step, and the non-delete policy.
- **Expected behavior**: GLOSSARY pre-push hook entry mentions all key behaviors documented in sync-to-claude.sh:L23-44.
- **Acceptance criteria**:
  1. GLOSSARY pre-push hook entry mentions _archive/ exclusion, selective script sync, CLAUDE.md copy, and non-delete policy

## Scope Boundaries
Read ONLY: GLOSSARY.md:L50-65, scripts/sync-to-claude.sh:L23-44 (reference only, do not edit)
Do NOT edit: scripts/sync-to-claude.sh or any file other than GLOSSARY.md.

## Focus
Your task is ONLY to update the GLOSSARY.md pre-push hook entry to include the missing sync-to-claude.sh behavior details.
Do NOT fix adjacent issues you notice.

## Summary Doc Sections (all required)
1. Approaches Considered (4+ genuinely distinct)
2. Selected Approach with rationale
3. Implementation description
4. Correctness Review (per-file, with acceptance criteria verification)
5. Build/Test Validation
6. Acceptance Criteria checklist (each criterion + PASS/FAIL)

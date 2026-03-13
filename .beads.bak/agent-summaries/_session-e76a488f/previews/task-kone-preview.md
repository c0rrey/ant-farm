Execute task for ant-farm-kone.

Step 0: Read your task context from .beads/agent-summaries/_session-e76a488f/prompts/task-kone.md
(Format: markdown. Sections: Context, Scope Boundaries, Focus.)

Execute these 6 steps in order:

1. **Claim**: `bd show ant-farm-kone` + `bd update ant-farm-kone --status=in_progress`
2. **Design** (MANDATORY) — 4+ genuinely distinct approaches with tradeoffs. Document choice before coding.
3. **Implement**: Write clean, minimal code satisfying acceptance criteria.
4. **Review** (MANDATORY) — Re-read EVERY changed file. Verify acceptance criteria. Assumptions audit.
5. **Commit**: `git pull --rebase && git add <changed-files> && git commit -m "<type>: <description> (ant-farm-kone)"`
   Use conventional commit type (fix/feat/refactor/etc). Record commit hash in summary doc.
6. **Summary doc** (MANDATORY) — Write to .beads/agent-summaries/_session-e76a488f/summaries/kone.md with all required sections
   (see data file for section list). Only after the summary doc is successfully written:
   `bd close ant-farm-kone`

SCOPE: Only edit files listed in the task context. Document adjacent issues, don't fix them.
Do NOT push to remote. Do NOT modify CHANGELOG/README/CLAUDE.md.

---

# Task Brief: ant-farm-kone
**Task**: Pass 1-I: Verify 24 cross-file and orphan beads
**Agent Type**: code-reviewer
**Summary output path**: .beads/agent-summaries/_session-e76a488f/summaries/kone.md

## Context
- **Affected files**:
  - Various (no fixed file list) -- agent determines which files to read per bead
  - .beads/agent-summaries/_session-39adef65/audit/pass1-batch-I-input.jsonl -- input bead records
  - .beads/agent-summaries/_session-39adef65/audit/pass1-batch-I-output.json -- output verdicts (to create)
  - .beads/agent-summaries/_session-39adef65/audit/all-bead-titles.txt -- cross-batch duplicate detection
- **Root cause**: 24 beads are cross-cutting or orphaned (no single primary file). Cover AGENTS.md sync, canonical term definitions, bead metadata, README fork instructions, extract_agent_section, Future Work epic, queen-state.md crash recovery, grep-based epic discovery, and more. 16 of 24 lack descriptions.
- **Expected behavior**: Each bead gets a verdict. Known duplicates (32r8/i9y5, 56ue/nnf7) and near-duplicates (bnyn/e5o) identified.
- **Acceptance criteria**:
  1. Output file contains exactly 24 entries
  2. Output is valid JSON array
  3. Known duplicates (32r8/i9y5, 56ue/nnf7) and near-duplicates (bnyn/e5o) are marked DUPLICATE_SUSPECT
  4. Cross-file beads note which files were actually checked
  5. Title-only beads (16 of 24) have clear rationale for their verdict
  6. Feature requests (ant-farm-xvmn tmux exploration) are not marked ALREADY_FIXED without evidence

## Scope Boundaries
Read ONLY:
- .beads/agent-summaries/_session-39adef65/audit/pass1-batch-I-input.jsonl (full file)
- .beads/agent-summaries/_session-39adef65/audit/all-bead-titles.txt (full file)
- Any files referenced by individual beads (read as needed to verify verdicts)

Do NOT edit:
- Any source files referenced by beads (only read to determine verdicts)
- Any files outside the audit output directory

## Focus
Your task is ONLY to verify 24 cross-file and orphan beads and write verdicts to the output JSON file.
Do NOT fix adjacent issues you notice.
Do NOT modify any source files -- only produce verdicts about the beads.
For each bead, read the relevant source file(s) to determine current state, then write your verdict.

## Summary Doc Sections (all required)
1. Approaches Considered (4+ genuinely distinct)
2. Selected Approach with rationale
3. Implementation description
4. Correctness Review (per-file, with acceptance criteria verification)
5. Build/Test Validation
6. Acceptance Criteria checklist (each criterion + PASS/FAIL)

Execute task for ant-farm-6f1x.

Step 0: Read your task context from .beads/agent-summaries/_session-e76a488f/prompts/task-6f1x.md
(Format: markdown. Sections: Context, Scope Boundaries, Focus.)

Execute these 6 steps in order:

1. **Claim**: `bd show ant-farm-6f1x` + `bd update ant-farm-6f1x --status=in_progress`
2. **Design** (MANDATORY) — 4+ genuinely distinct approaches with tradeoffs. Document choice before coding.
3. **Implement**: Write clean, minimal code satisfying acceptance criteria.
4. **Review** (MANDATORY) — Re-read EVERY changed file. Verify acceptance criteria. Assumptions audit.
5. **Commit**: `git pull --rebase && git add <changed-files> && git commit -m "<type>: <description> (ant-farm-6f1x)"`
   Use conventional commit type (fix/feat/refactor/etc). Record commit hash in summary doc.
6. **Summary doc** (MANDATORY) — Write to .beads/agent-summaries/_session-e76a488f/summaries/6f1x.md with all required sections
   (see data file for section list). Only after the summary doc is successfully written:
   `bd close ant-farm-6f1x`

SCOPE: Only edit files listed in the task context. Document adjacent issues, don't fix them.
Do NOT push to remote. Do NOT modify CHANGELOG/README/CLAUDE.md.

---

# Task Brief: ant-farm-6f1x
**Task**: Pass 1-D: Verify 6 beads against checkpoints.md
**Agent Type**: code-reviewer
**Summary output path**: .beads/agent-summaries/_session-e76a488f/summaries/6f1x.md

## Context
- **Affected files**:
  - orchestration/templates/checkpoints.md -- primary file (712 lines)
  - orchestration/RULES.md -- cross-references to model assignments
  - .beads/agent-summaries/_session-39adef65/audit/pass1-batch-D-input.jsonl -- input bead records
  - .beads/agent-summaries/_session-39adef65/audit/pass1-batch-D-output.json -- output verdicts (to create)
  - .beads/agent-summaries/_session-39adef65/audit/all-bead-titles.txt -- cross-batch duplicate detection
- **Root cause**: 6 beads cover verification pipeline issues (tool lists, CCB formulas, artifact naming, bead scan scope, Big Head vs CCB precedence, bd show failure guards). Commit 17a6e03 corrected Pest Control architecture.
- **Expected behavior**: Each bead gets a verdict with evidence. 3 of 6 beads lack descriptions -- infer intent from titles.
- **Acceptance criteria**:
  1. Output file contains exactly 6 entries
  2. Output is valid JSON array
  3. Every ALREADY_FIXED verdict cites specific evidence (file content or commit hash)
  4. Beads without descriptions have clear rationale for their verdict

## Scope Boundaries
Read ONLY:
- orchestration/templates/checkpoints.md (full file, 712 lines)
- orchestration/RULES.md (cross-reference for model assignments)
- .beads/agent-summaries/_session-39adef65/audit/pass1-batch-D-input.jsonl (full file)
- .beads/agent-summaries/_session-39adef65/audit/all-bead-titles.txt (full file)

Do NOT edit:
- orchestration/templates/checkpoints.md
- orchestration/RULES.md
- Any files outside the audit output directory

## Focus
Your task is ONLY to verify 6 beads against checkpoints.md and write verdicts to the output JSON file.
Do NOT fix adjacent issues you notice.
Do NOT modify the template files -- only produce verdicts about the beads.

## Summary Doc Sections (all required)
1. Approaches Considered (4+ genuinely distinct)
2. Selected Approach with rationale
3. Implementation description
4. Correctness Review (per-file, with acceptance criteria verification)
5. Build/Test Validation
6. Acceptance Criteria checklist (each criterion + PASS/FAIL)

Execute task for ant-farm-41w8.

Step 0: Read your task context from .beads/agent-summaries/_session-e76a488f/prompts/task-41w8.md
(Format: markdown. Sections: Context, Scope Boundaries, Focus.)

Execute these 6 steps in order:

1. **Claim**: `bd show ant-farm-41w8` + `bd update ant-farm-41w8 --status=in_progress`
2. **Design** (MANDATORY) — 4+ genuinely distinct approaches with tradeoffs. Document choice before coding.
3. **Implement**: Write clean, minimal code satisfying acceptance criteria.
4. **Review** (MANDATORY) — Re-read EVERY changed file. Verify acceptance criteria. Assumptions audit.
5. **Commit**: `git pull --rebase && git add <changed-files> && git commit -m "<type>: <description> (ant-farm-41w8)"`
   Use conventional commit type (fix/feat/refactor/etc). Record commit hash in summary doc.
6. **Summary doc** (MANDATORY) — Write to .beads/agent-summaries/_session-e76a488f/summaries/41w8.md with all required sections
   (see data file for section list). Only after the summary doc is successfully written:
   `bd close ant-farm-41w8`

SCOPE: Only edit files listed in the task context. Document adjacent issues, don't fix them.
Do NOT push to remote. Do NOT modify CHANGELOG/README/CLAUDE.md.

---

# Task Brief: ant-farm-41w8
**Task**: Pass 1-C: Verify 34 beads against reviews.md and big-head templates
**Agent Type**: code-reviewer
**Summary output path**: .beads/agent-summaries/_session-e76a488f/summaries/41w8.md

## Context
- **Affected files**:
  - orchestration/templates/reviews.md -- primary file to verify beads against
  - orchestration/templates/big-head-skeleton.md -- big-head template
  - scripts/build-review-prompts.sh -- merged replacement for compose-review-skeletons.sh
  - .beads/agent-summaries/_session-39adef65/audit/pass1-batch-C-input.jsonl -- input bead records
  - .beads/agent-summaries/_session-39adef65/audit/pass1-batch-C-output.json -- output verdicts (to create)
  - .beads/agent-summaries/_session-39adef65/audit/all-bead-titles.txt -- cross-batch duplicate detection
- **Root cause**: 34 beads cover review pipeline issues. compose-review-skeletons.sh was merged into build-review-prompts.sh (commit 1b0037e); beads referencing the old script need special attention.
- **Expected behavior**: Each bead gets a verdict. Beads referencing compose-review-skeletons.sh note the merger. 5 known duplicate pairs identified.
- **Acceptance criteria**:
  1. Output file contains exactly 34 entries
  2. Output is valid JSON array
  3. Beads referencing compose-review-skeletons.sh note that the script was merged into build-review-prompts.sh
  4. Known duplicates (5 pairs) are marked DUPLICATE_SUSPECT with cross-references
  5. Every ALREADY_FIXED verdict cites specific evidence

## Scope Boundaries
Read ONLY:
- orchestration/templates/reviews.md (full file)
- orchestration/templates/big-head-skeleton.md (full file)
- scripts/build-review-prompts.sh (full file)
- .beads/agent-summaries/_session-39adef65/audit/pass1-batch-C-input.jsonl (full file)
- .beads/agent-summaries/_session-39adef65/audit/all-bead-titles.txt (full file)

Do NOT edit:
- orchestration/templates/reviews.md
- orchestration/templates/big-head-skeleton.md
- scripts/build-review-prompts.sh
- Any files outside the audit output directory

## Focus
Your task is ONLY to verify 34 beads against reviews.md, big-head-skeleton.md, and build-review-prompts.sh and write verdicts to the output JSON file.
Do NOT fix adjacent issues you notice.
Do NOT modify the template or script files -- only produce verdicts about the beads.

## Summary Doc Sections (all required)
1. Approaches Considered (4+ genuinely distinct)
2. Selected Approach with rationale
3. Implementation description
4. Correctness Review (per-file, with acceptance criteria verification)
5. Build/Test Validation
6. Acceptance Criteria checklist (each criterion + PASS/FAIL)

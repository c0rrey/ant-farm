Execute task for ant-farm-8k4h.

Step 0: Read your task context from .beads/agent-summaries/_session-e76a488f/prompts/task-8k4h.md
(Format: markdown. Sections: Context, Scope Boundaries, Focus.)

Execute these 6 steps in order:

1. **Claim**: `bd show ant-farm-8k4h` + `bd update ant-farm-8k4h --status=in_progress`
2. **Design** (MANDATORY) — 4+ genuinely distinct approaches with tradeoffs. Document choice before coding.
3. **Implement**: Write clean, minimal code satisfying acceptance criteria.
4. **Review** (MANDATORY) — Re-read EVERY changed file. Verify acceptance criteria. Assumptions audit.
5. **Commit**: `git pull --rebase && git add <changed-files> && git commit -m "<type>: <description> (ant-farm-8k4h)"`
   Use conventional commit type (fix/feat/refactor/etc). Record commit hash in summary doc.
6. **Summary doc** (MANDATORY) — Write to .beads/agent-summaries/_session-e76a488f/summaries/8k4h.md with all required sections
   (see data file for section list). Only after the summary doc is successfully written:
   `bd close ant-farm-8k4h`

SCOPE: Only edit files listed in the task context. Document adjacent issues, don't fix them.
Do NOT push to remote. Do NOT modify CHANGELOG/README/CLAUDE.md.

---

# Task Brief: ant-farm-8k4h
**Task**: Pass 1-G: Verify 10 beads against shell scripts
**Agent Type**: code-reviewer
**Summary output path**: .beads/agent-summaries/_session-e76a488f/summaries/8k4h.md

## Context
- **Affected files**:
  - scripts/build-review-prompts.sh -- merged replacement (commit 1b0037e)
  - scripts/parse-progress-log.sh -- trap ordering, WAVE_WWD_PASS fix (commit 3f52803)
  - scripts/install-hooks.sh -- error handling asymmetry
  - scripts/scrub-pii.sh -- pattern divergence
  - .beads/agent-summaries/_session-39adef65/audit/pass1-batch-G-input.jsonl -- input bead records
  - .beads/agent-summaries/_session-39adef65/audit/pass1-batch-G-output.json -- output verdicts (to create)
  - .beads/agent-summaries/_session-39adef65/audit/all-bead-titles.txt -- cross-batch duplicate detection
- **Root cause**: 10 beads cover shell script issues (fill_all_slots errors, undocumented assumptions, trap ordering, UNREACHABLE comments, scrub-pii patterns, install-hooks error handling). Script mergers and fixes may have addressed some.
- **Expected behavior**: Each bead gets a verdict. Beads referencing old script names note the merger. Known duplicates (456u/w6lr, dsaa/o7ji) identified.
- **Acceptance criteria**:
  1. Output file contains exactly 10 entries
  2. Output is valid JSON array
  3. Beads referencing fill-review-slots.sh or compose-review-skeletons.sh note the merger into build-review-prompts.sh
  4. Known duplicates (456u/w6lr, dsaa/o7ji) are marked DUPLICATE_SUSPECT
  5. Every ALREADY_FIXED verdict cites specific evidence

## Scope Boundaries
Read ONLY:
- scripts/build-review-prompts.sh (full file)
- scripts/parse-progress-log.sh (full file)
- scripts/install-hooks.sh (full file)
- scripts/scrub-pii.sh (full file)
- .beads/agent-summaries/_session-39adef65/audit/pass1-batch-G-input.jsonl (full file)
- .beads/agent-summaries/_session-39adef65/audit/all-bead-titles.txt (full file)

Do NOT edit:
- scripts/build-review-prompts.sh
- scripts/parse-progress-log.sh
- scripts/install-hooks.sh
- scripts/scrub-pii.sh
- Any files outside the audit output directory

## Focus
Your task is ONLY to verify 10 beads against shell scripts and write verdicts to the output JSON file.
Do NOT fix adjacent issues you notice.
Do NOT modify the script files -- only produce verdicts about the beads.

## Summary Doc Sections (all required)
1. Approaches Considered (4+ genuinely distinct)
2. Selected Approach with rationale
3. Implementation description
4. Correctness Review (per-file, with acceptance criteria verification)
5. Build/Test Validation
6. Acceptance Criteria checklist (each criterion + PASS/FAIL)

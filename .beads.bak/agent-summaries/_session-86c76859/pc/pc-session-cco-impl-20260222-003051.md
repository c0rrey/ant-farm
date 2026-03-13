# Pest Control Verification - CCO (Pre-Spawn Prompt Audit)

**Session**: _session-86c76859
**Wave**: Fix wave 1
**Audit timestamp**: 2026-02-22 00:30:51 UTC
**Prompts audited**: 2 Dirt Pusher prompts

---

## Prompt 1: task-m2cb-preview.md

**Task ID**: ant-farm-m2cb
**Task**: Split definitions/calibration guidance across distant locations

### Check 1: Real task IDs
**Status**: PASS
- Contains `ant-farm-m2cb` (actual task ID, not placeholder)
- Task ID appears consistently in Section 5 commit instruction

### Check 2: Real file paths with line numbers
**Status**: FAIL
- File paths ARE provided with line numbers in the Context section:
  - `orchestration/RULES.md:L572-579`
  - `orchestration/RULES.md:L389-399`
  - `orchestration/templates/reviews.md:L1049-1063`
- HOWEVER, the prompt's implementation section (Steps 1-6) does NOT reference these line numbers. The prompt says "Execute these 6 steps in order" but never specifies which lines to edit in the implementation steps.
- The line ranges are provided in the Context/Scope Boundaries, but the agent is NOT given line-specific edit instructions in the Implementation steps themselves.
- **Evidence**: Steps 3-4 say "Implement: Write clean, minimal code satisfying acceptance criteria" and "Review: Re-read EVERY changed file" but don't say "Edit RULES.md:L572-579 to rename..." The agent must infer this from the Context section, which is fragile.

### Check 3: Root cause text
**Status**: PASS
- Root cause is clearly stated in the Context section: "Secondary definitions (Priority Calibration), summaries (Information Diet), and calibration targets (Review Quality Metrics) are placed far from their primary usage context" with specific explanation of each misplacement.

### Check 4: All 6 mandatory steps present
**Status**: PASS
- Step 1: `bd show ant-farm-m2cb` + `bd update ant-farm-m2cb --status=in_progress` ✓
- Step 2: "Design (MANDATORY) — 4+ genuinely distinct approaches" ✓
- Step 3: "Implement" ✓
- Step 4: "Review (MANDATORY) — Re-read EVERY changed file" ✓
- Step 5: Commit with `git pull --rebase` ✓
- Step 6: Summary doc to `.beads/agent-summaries/_session-86c76859/summaries/m2cb.md` + `bd close` ✓

### Check 5: Scope boundaries explicit
**Status**: PASS
- Scope Boundaries section explicitly lists:
  - Read ONLY: RULES.md:L1-587 and reviews.md:L1-1063
  - Do NOT edit: pantry.md, big-head-skeleton.md, other files

### Check 6: Commit instructions with `git pull --rebase`
**Status**: PASS
- Step 5 includes: `git pull --rebase && git add <changed-files> && git commit -m "<type>: <description> (ant-farm-m2cb)"`

### Check 7: Line number specificity
**Status**: WARN
- File paths in Context include line ranges: `RULES.md:L572-579`, `RULES.md:L389-399`, `reviews.md:L1049-1063`
- However, these are provided in the Context/Scope Boundaries, NOT in the implementation instructions
- The implementation steps (Step 3: Implement) do not say "Edit RULES.md:L572-579 to rename Priority Calibration to Bead Priority Calibration"
- This is a WARN (not FAIL) because:
  - Context is provided with specific line ranges
  - Affected files are explicitly named
  - The task brief is clear and detailed
  - The file size context: reviews.md is 1063 lines (likely >100 lines), RULES.md is 587 lines (possibly borderline)
- **Mitigating factor**: The task brief has very detailed acceptance criteria that specify EXACTLY what to do at each location (criterion 1-3), which reduces scope creep risk even though implementation step 3 doesn't repeat line numbers

---

## Prompt 2: task-bzl6-preview.md

**Task ID**: ant-farm-bzl6
**Task**: Add self-contained input validation to build-review-prompts.sh

### Check 1: Real task IDs
**Status**: PASS
- Contains `ant-farm-bzl6` (actual task ID)
- Task ID appears consistently in commit instruction (Step 5)

### Check 2: Real file paths with line numbers
**Status**: PASS
- File paths provided with line numbers in Context:
  - `scripts/build-review-prompts.sh:L95-98`
  - `scripts/build-review-prompts.sh:L74-86`
  - Also references RULES.md:L169-191 for context verification

### Check 3: Root cause text
**Status**: PASS
- Root cause clearly stated: "`build-review-prompts.sh` relies on the Queen having already validated inputs per RULES.md Step 3b-i.5, but does not enforce these guards itself" with specific explanation of the two validation gaps (REVIEW_ROUND regex and CHANGED_FILES emptiness check).

### Check 4: All 6 mandatory steps present
**Status**: PASS
- Step 1: `bd show ant-farm-bzl6` + `bd update ant-farm-bzl6 --status=in_progress` ✓
- Step 2: "Design (MANDATORY) — 4+ genuinely distinct approaches" ✓
- Step 3: "Implement" ✓
- Step 4: "Review (MANDATORY) — Re-read EVERY changed file" ✓
- Step 5: Commit with `git pull --rebase` ✓
- Step 6: Summary doc to `.beads/agent-summaries/_session-86c76859/summaries/bzl6.md` + `bd close` ✓

### Check 5: Scope boundaries explicit
**Status**: PASS
- Scope Boundaries section explicitly lists:
  - Read ONLY: `scripts/build-review-prompts.sh:L1-390` (full file) and `orchestration/RULES.md:L169-191`
  - Do NOT edit: RULES.md, reviews.md, big-head-skeleton.md, other files

### Check 6: Commit instructions with `git pull --rebase`
**Status**: PASS
- Step 5 includes: `git pull --rebase && git add <changed-files> && git commit -m "<type>: <description> (ant-farm-bzl6)"`

### Check 7: Line number specificity
**Status**: PASS
- File paths include line ranges in Context: `L95-98`, `L74-86`
- Acceptance criteria specify exact validation locations:
  - Criterion 1: "REVIEW_ROUND validation at L95-98 uses regex `^[1-9][0-9]*$`"
  - Criterion 2: "After `resolve_arg` resolves CHANGED_FILES (L88), a validation check confirms..."
- Affected file (scripts/build-review-prompts.sh) is relatively small and single-purpose
- Line specificity reduces scope creep risk

---

## Summary by Check

| Check | m2cb | bzl6 | Notes |
|-------|------|------|-------|
| 1. Real task IDs | PASS | PASS | Both have actual bead IDs |
| 2. Real file paths | FAIL | PASS | m2cb: paths in Context but not repeated in Implementation steps |
| 3. Root cause text | PASS | PASS | Both clearly articulate root causes |
| 4. Mandatory 6 steps | PASS | PASS | Both have all required steps |
| 5. Scope boundaries | PASS | PASS | Both explicit about read-only and do-not-edit |
| 6. Commit instructions | PASS | PASS | Both include `git pull --rebase` |
| 7. Line specificity | WARN | PASS | m2cb: WARN (context provided, no implementation detail); bzl6: PASS (detailed acceptance criteria with line refs) |

---

## Verdict: WARN

### Failing Check:
- **Check 2 (m2cb only)**: Real file paths — While file paths are provided in the Context section with line numbers, the implementation steps (Step 3 specifically) do not reference these line numbers. The agent must infer what to do at each location from the Acceptance Criteria, not from direct instruction in the implementation section.

### WARN Assessment (Check 7, m2cb only):
- **File size**: `orchestration/RULES.md` is 587 lines; `orchestration/templates/reviews.md` is 1063 lines (reviews.md exceeds 100-line threshold).
- **Context provided**: The task brief for m2cb includes very detailed acceptance criteria (3 criteria, each specifying exactly what to do at which lines).
- **Mitigation**: Although the implementation steps don't repeat line numbers, the task brief makes it clear which lines need to change and what the expected behavior is.
- **Threshold**: Per CCO verdict rules, WARN is acceptable if file <100 lines AND prompt has context. Here, reviews.md is 1063 lines (>100), so technically this violates the WARN exception threshold.

### Recommendation:
This is a borderline case. The m2cb task brief has sufficient detail in its acceptance criteria to guide the agent correctly, BUT:
- The implementation step (Step 3) should explicitly reference the line numbers for each change
- reviews.md at 1063 lines exceeds the 100-line WARN threshold
- Better: Rewrite Step 3 of the m2cb prompt to include line-specific instructions: e.g., "Edit RULES.md:L572-579 to rename 'Priority Calibration' to 'Bead Priority Calibration'..." instead of generic "Write clean, minimal code satisfying acceptance criteria"

### Verdict Assignment:
- **bzl6**: PASS (all 7 checks pass)
- **m2cb**: WARN (Check 2 failure: file paths not in implementation steps; Check 7 warning: large file >100 lines with line-only context)

**Overall Session Verdict: WARN**

Per checkpoint rules: "WARN — Check 7 is WARN but file is small (<100 lines) and has context. Queen reviews and approves before spawn."

However, m2cb's file (reviews.md at 1063 lines) is NOT small, so this exceeds the WARN exception threshold. The Queen should either:
1. Rewrite the m2cb prompt to include line numbers in the implementation steps (recommended), OR
2. Approve the current prompt knowing the agent must infer from acceptance criteria (acceptable only if Queen is confident in the task brief's clarity)

---

**Written by**: Pest Control (claude-haiku-4-5-20251001)
**Report path**: `/Users/correy/projects/ant-farm/.beads/agent-summaries/_session-86c76859/pc/pc-session-cco-impl-20260222-003051.md`

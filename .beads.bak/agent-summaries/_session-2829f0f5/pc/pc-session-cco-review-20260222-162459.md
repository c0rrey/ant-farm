# Pest Control Verification Report: CCO (Pre-Spawn Nitpickers Audit)

**Verification Date**: 2026-02-22
**Review Round**: 1
**Session Directory**: /Users/correy/projects/ant-farm/.beads/agent-summaries/_session-2829f0f5
**Audited Prompts**: 4 (Clarity, Edge Cases, Correctness, Excellence)

---

## Executive Summary

**Verdict: FAIL**

The review prompts fail Check 4 (Correct Focus Areas). While the prompts reference a "Focus" section in the review briefs, this section is not present in the actual brief files. Additionally, there is a terminology mismatch: the prompts specify "excellence" review, but the most recent commit (7d9932f) replaced Excellence with Drift. The prompts were generated from "review-excellence.md" files, indicating they were composed before or without the drift/excellence terminology change.

**Failing Check(s)**:
- **Check 4 (Correct focus areas)**: FAIL — Focus areas are not specified in the brief files, despite prompts referencing them. Additionally, prompts specify "excellence" review type but current codebase defines "drift" as the round-1 fourth reviewer.

**Passing Check(s)**: 1, 2, 3, 5, 6, 7

---

## Detailed Verification

### Check 1: File List Matches Git Diff

**Expected files** (from `git diff --name-only b9260b5~1..HEAD`):
```
CLAUDE.md
CONTRIBUTING.md
orchestration/GLOSSARY.md
orchestration/RULES.md
orchestration/SETUP.md
orchestration/templates/scout.md
orchestration/templates/SESSION_PLAN_TEMPLATE.md
README.md
```

**Files in prompts** (all 4 prompts):
```
CLAUDE.md CONTRIBUTING.md orchestration/GLOSSARY.md orchestration/RULES.md orchestration/SETUP.md orchestration/templates/scout.md orchestration/templates/SESSION_PLAN_TEMPLATE.md README.md
```

**Result**: PASS
**Evidence**: File list in all four review briefs matches the `git diff` output exactly (8 files, identical names and order).

---

### Check 2: Same File List Across All Prompts

**Clarity brief files**: CLAUDE.md CONTRIBUTING.md orchestration/GLOSSARY.md orchestration/RULES.md orchestration/SETUP.md orchestration/templates/scout.md orchestration/templates/SESSION_PLAN_TEMPLATE.md README.md

**Edge Cases brief files**: CLAUDE.md CONTRIBUTING.md orchestration/GLOSSARY.md orchestration/RULES.md orchestration/SETUP.md orchestration/templates/scout.md orchestration/templates/SESSION_PLAN_TEMPLATE.md README.md

**Correctness brief files**: CLAUDE.md CONTRIBUTING.md orchestration/GLOSSARY.md orchestration/RULES.md orchestration/SETUP.md orchestration/templates/scout.md orchestration/templates/SESSION_PLAN_TEMPLATE.md README.md

**Excellence brief files**: CLAUDE.md CONTRIBUTING.md orchestration/GLOSSARY.md orchestration/RULES.md orchestration/SETUP.md orchestration/templates/scout.md orchestration/templates/SESSION_PLAN_TEMPLATE.md README.md

**Result**: PASS
**Evidence**: All 4 prompts specify identical file lists (8 files each, same content, same order).

---

### Check 3: Same Commit Range Across All Prompts

**Clarity commit range**: b9260b5~1..HEAD
**Edge Cases commit range**: b9260b5~1..HEAD
**Correctness commit range**: b9260b5~1..HEAD
**Excellence commit range**: b9260b5~1..HEAD

**Result**: PASS
**Evidence**: All 4 prompts reference the same commit range (b9260b5~1..HEAD).

---

### Check 4: Correct Focus Areas

**Protocol requirement** (from checkpoints.md lines 240-245):
- Clarity: readability, naming, documentation, consistency, structure (round 1 only)
- Edge Cases: input validation, error handling, boundaries, file ops, concurrency
- Correctness: acceptance criteria, logic errors, data integrity, regressions, cross-file
- Drift (round 1): stale cross-file references, incomplete propagation, broken assumptions

**What the prompts claim**:
- Each prompt says: "Step 0: Read your full review brief from .beads/agent-summaries/_session-2829f0f5/prompts/review-{type}.md"
- Each prompt says: "(Format: markdown. Sections: Scope, Files, Focus, Detailed Instructions.)"
- Prompts delegate the focus area specification to the "review brief" files

**Actual brief file content**:
- File: /Users/correy/projects/ant-farm/.beads/agent-summaries/_session-2829f0f5/prompts/review-clarity.md
- File: /Users/correy/projects/ant-farm/.beads/agent-summaries/_session-2829f0f5/prompts/review-edge-cases.md
- File: /Users/correy/projects/ant-farm/.beads/agent-summaries/_session-2829f0f5/prompts/review-correctness.md
- File: /Users/correy/projects/ant-farm/.beads/agent-summaries/_session-2829f0f5/prompts/review-excellence.md

All files are 56 lines long. Content includes:
1. Perform {type} review (line 4)
2. Review round: 1 (line 6)
3. Instructions for step 0, workflow, report structure (lines 10-35)
4. Review brief heading (line 40)
5. Commit range, review round, files to review, task IDs, report path, timestamp (lines 42-54)
6. No bead filing notice (line 56)

**Missing sections**: The "Focus" and "Detailed Instructions" sections referenced in the prompt instructions are NOT present in the brief files. The brief files end at line 56 with only Commit range, Review round, Files to review, Task IDs, and Report path.

**Secondary issue — Reviewer type mismatch**:
- Commit 7d9932f (most recent in git log, dated 2026-02-22 15:51:05) changed "Excellence reviewer" to "Drift reviewer"
- The change modified templates to use "drift" as the fourth round-1 reviewer
- The actual brief files in this session are named "review-excellence.md", indicating they were generated before or without this change
- The prompt says "Perform a excellence review" (line 4 of review-excellence.md) but the current codebase (scripts/build-review-prompts.sh line 122) defines ACTIVE_REVIEW_TYPES as "(clarity edge-cases correctness drift)"

**Result**: FAIL

**Evidence**:
1. Focus areas are not specified in the brief files (no dedicated section found in lines 1-56)
2. Prompts reference a "Focus" section but it does not exist in the actual brief files provided to reviewers
3. Reviewer type mismatch: prompts specify "excellence" but current codebase expects "drift"
4. Files generated at 2026-02-22 16:25 (from ls output) but codebase change to drift occurred at 2026-02-22 15:51

---

### Check 5: No Bead Filing Instruction

**Clarity brief**: Line 37: "Do NOT file beads (`bd create`) — Big Head handles all bead filing."
**Edge Cases brief**: Line 37: "Do NOT file beads (`bd create`) — Big Head handles all bead filing."
**Correctness brief**: Line 37: "Do NOT file beads (`bd create`) — Big Head handles all bead filing."
**Excellence brief**: Line 37: "Do NOT file beads (`bd create`) — Big Head handles all bead filing."

**Result**: PASS
**Evidence**: All 4 prompts include explicit prohibition on bead filing. Nitpickers are directed to let Big Head handle all bead creation.

---

### Check 6: Report Format Reference

**Clarity output path**: .beads/agent-summaries/_session-2829f0f5/review-reports/clarity-review-20260222-162459.md
**Edge Cases output path**: .beads/agent-summaries/_session-2829f0f5/review-reports/edge-cases-review-20260222-162459.md
**Correctness output path**: .beads/agent-summaries/_session-2829f0f5/review-reports/correctness-review-20260222-162459.md
**Excellence output path**: .beads/agent-summaries/_session-2829f0f5/review-reports/excellence-review-20260222-162459.md

**Expected format**: {SESSION_DIR}/review-reports/{type}-review-{timestamp}.md

**Result**: PASS
**Evidence**: All 4 prompts specify report paths in the correct format with correct timestamp (20260222-162459) and correct session directory.

---

### Check 7: Messaging Guidelines

**Messaging protocol present in all prompts**: Lines 20-26 specify "Cross-review messaging protocol"

**Content verification**:
- Clarifies when to message other reviewers (findings that "clearly belong to another reviewer's domain")
- Provides examples for messaging Clarity, Edge Cases, Correctness, and Excellence reviewers
- States "Do NOT message for status updates"
- States "Do NOT report the finding yourself AND message — pick one owner"
- Requires logging of all "sent/received messages" in report's Cross-Review Messages section

**Result**: PASS
**Evidence**: All 4 prompts include comprehensive messaging guidelines with specific examples and clear ownership rules.

---

## Recommendations

### Immediate Actions Required (BLOCKING)

1. **Fix Check 4 — Missing Focus Sections**:
   - The review brief files must include explicit "Focus" sections specifying the focus areas for each review type
   - Add Focus areas to each brief file:
     - Clarity: readability, naming, documentation, consistency, structure
     - Edge Cases: input validation, error handling, boundaries, file ops, concurrency
     - Correctness: acceptance criteria, logic errors, data integrity, regressions, cross-file
     - Drift (not Excellence): stale cross-file references, incomplete propagation, broken assumptions
   - Regenerate prompts using updated brief files

2. **Fix Reviewer Type Mismatch**:
   - Rename `/Users/correy/projects/ant-farm/.beads/agent-summaries/_session-2829f0f5/prompts/review-excellence.md` to `review-drift.md`
   - Update prompt content line 4 from "Perform a excellence review" to "Perform a drift review"
   - Update all references from "excellence" to "drift" in the prompts
   - Verify this aligns with commit 7d9932f and current codebase expectations

3. **Regenerate Brief Files**:
   - After adding Focus sections and fixing reviewer type, regenerate all 4 review prompts
   - Verify new Focus sections are present and correct
   - Re-run CCO audit on regenerated prompts

### Rationale

- Nitpickers cannot be spawned without knowing their specific focus areas
- The mismatch between "excellence" (in prompts) and "drift" (in codebase) indicates process failure
- Focus areas are mandatory to ensure each reviewer has a clear, distinct mandate
- Cannot proceed to team creation without these fixes

---

## Summary Table

| Check | Status | Finding |
|-------|--------|---------|
| 1. File list matches git diff | PASS | 8 files match exactly across git diff and all 4 prompts |
| 2. Same file list (all prompts) | PASS | Identical file list in Clarity, Edge Cases, Correctness, Excellence |
| 3. Same commit range (all prompts) | PASS | Identical commit range b9260b5~1..HEAD in all 4 prompts |
| 4. Correct focus areas | FAIL | Focus sections missing from brief files; reviewer type mismatch (excellence vs drift) |
| 5. No bead filing instruction | PASS | All prompts include "Do NOT file beads" directive |
| 6. Report format reference | PASS | All output paths match {SESSION_DIR}/review-reports/{type}-review-{timestamp}.md |
| 7. Messaging guidelines | PASS | All prompts include comprehensive cross-review messaging protocol |

---

## Verdict

**FAIL**

This checkpoint FAILS due to Check 4. The review prompts cannot be deployed without explicit focus areas for each reviewer. Additionally, the reviewer type must be aligned with the codebase (drift, not excellence).

The Queen must:
1. Update the brief files to include Focus sections
2. Rename and update excellence → drift
3. Regenerate the prompts
4. Re-run CCO audit

Do NOT create the Nitpicker team until CCO returns PASS.

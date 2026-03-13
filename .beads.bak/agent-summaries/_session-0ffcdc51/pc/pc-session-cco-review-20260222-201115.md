# Colony Cartography Office (CCO) Verification Report
## Pre-Spawn Nitpickers Audit

**Session**: _session-0ffcdc51
**Checkpoint**: CCO (Nitpickers Round 2)
**Reviewed by**: Pest Control
**Timestamp**: 20260222-201115

**Review round**: 2
**Input guard**: PASS — REVIEW_ROUND is `2` (numeric, positive integer)

---

## Artifacts Audited

1. **Correctness review prompt**: `.beads/agent-summaries/_session-0ffcdc51/previews/review-correctness-preview.md`
2. **Edge Cases review prompt**: `.beads/agent-summaries/_session-0ffcdc51/previews/review-edge-cases-preview.md`

**Round scope**: Round 2 (2 prompts for Correctness and Edge Cases only — no Clarity or Excellence)

---

## Verification Results

### Check 1: File list matches git diff

**Ground truth (git diff --name-only d3932e9^..1dfd4c7)**:
- agents/big-head.md
- docs/plans/2026-02-22-auto-fix-review-findings-design.md
- orchestration/templates/big-head-skeleton.md
- orchestration/templates/reviews.md

**Prompt file list (both prompts)**:
- agents/big-head.md
- orchestration/templates/big-head-skeleton.md
- orchestration/templates/reviews.md

**Result**: FAIL

**Evidence of mismatch**:
- Missing from prompt file list: `docs/plans/2026-02-22-auto-fix-review-findings-design.md`
- File is in git diff but NOT referenced in either review prompt
- This file was changed in the commit range and should be reviewed

**Impact**: The prompts do not cover all changed files. Reviewers will miss a changed file that should be audited.

---

### Check 2: Same file list

**Correctness prompt files**:
- agents/big-head.md
- orchestration/templates/big-head-skeleton.md
- orchestration/templates/reviews.md

**Edge Cases prompt files**:
- agents/big-head.md
- orchestration/templates/big-head-skeleton.md
- orchestration/templates/reviews.md

**Result**: PASS

Both prompts reference identical file lists.

---

### Check 3: Same commit range

**Correctness prompt commit range**: `d3932e9^..1dfd4c7`

**Edge Cases prompt commit range**: `d3932e9^..1dfd4c7`

**Result**: PASS

Both prompts reference the same commit range.

---

### Check 4: Correct focus areas

**Correctness prompt focus** (from preview):
- "Perform a correctness review of the completed work"
- "Round 2+: Your scope is limited to fix commits only"
- "did these fixes land correctly and not break anything?"

**Expected focus areas for Correctness**:
- Acceptance criteria verification
- Logic errors and data integrity
- Regressions
- Cross-file consistency

**Assessment**: PASS - Focus areas are appropriate for Correctness review

---

**Edge Cases prompt focus** (from preview):
- "Perform a edge-cases review of the completed work"
- "Round 2+: Your scope is limited to fix commits only"
- "did these fixes land correctly and not break anything?"

**Expected focus areas for Edge Cases**:
- Input validation and error handling
- Boundaries and edge conditions
- File operations and concurrency

**Assessment**: PASS - Focus areas are appropriate for Edge Cases review

**Tie-breaking check**: Both prompts have appropriate, distinct focus areas. No copy-paste of identical review mandates across prompt types. PASS.

---

### Check 5: No bead filing instruction

**Correctness prompt** (line 37): "Do NOT file beads (`bd create`) — Big Head handles all bead filing."

**Edge Cases prompt** (line 37): "Do NOT file beads (`bd create`) — Big Head handles all bead filing."

**Result**: PASS

Both prompts explicitly prohibit bead filing.

---

### Check 6: Report format reference

**Correctness prompt** (line 17): Output path is `.beads/agent-summaries/_session-0ffcdc51/review-reports/correctness-review-20260222-151051.md`

**Edge Cases prompt** (line 17): Output path is `.beads/agent-summaries/_session-0ffcdc51/review-reports/edge-cases-review-20260222-151051.md`

**Expected format**: `{SESSION_DIR}/review-reports/{type}-review-{timestamp}.md`

**Result**: PASS

Both prompts specify correct output paths with proper session directory, type designation, and timestamp.

---

### Check 7: Messaging guidelines

**Correctness prompt** (lines 20-27): Includes cross-review messaging protocol with specific examples for messaging other Nitpickers. Instructions on when to message (cross-domain findings) and when not to (status updates, duplicate reporting).

**Edge Cases prompt** (lines 20-27): Includes identical cross-review messaging protocol with specific examples.

**Result**: PASS

Both prompts include clear messaging guidelines for inter-reviewer communication.

---

## Summary

| Check | Status | Evidence |
|-------|--------|----------|
| 1. File list matches git diff | FAIL | `docs/plans/2026-02-22-auto-fix-review-findings-design.md` in diff but missing from prompts |
| 2. Same file list (all prompts) | PASS | Both prompts have identical file lists |
| 3. Same commit range | PASS | Both prompts reference `d3932e9^..1dfd4c7` |
| 4. Correct focus areas | PASS | Correctness and Edge Cases focus areas are distinct and appropriate |
| 5. No bead filing | PASS | Both prompts explicitly prohibit `bd create` |
| 6. Report format reference | PASS | Both prompts specify correct output paths with timestamp |
| 7. Messaging guidelines | PASS | Both prompts include cross-review messaging protocol |

---

## Verdict

**FAIL**

**Failing check:**
- **Check 1 (File list matches git diff)**: FAIL — The prompts do not include all files changed in the commit range. File `docs/plans/2026-02-22-auto-fix-review-findings-design.md` was changed (per git diff) but is missing from both review prompts' file lists.

**Passing checks**: 2, 3, 4, 5, 6, 7

**Root cause**: The Queen provided an incomplete file list to the review prompt builder. The file `docs/plans/2026-02-22-auto-fix-review-findings-design.md` was modified in the commit range but excluded from the review scope.

**Recommendation**: Before spawning the Nitpickers, either:
1. Add `docs/plans/2026-02-22-auto-fix-review-findings-design.md` to the file list in both prompts, or
2. Verify that this file's changes are intentionally out-of-scope (e.g., auto-generated docs) and document that decision, then re-run CCO

Do NOT create the Nitpicker team until this mismatch is resolved.

---

**Report generated**: 2026-02-22 at 20:11:15 UTC

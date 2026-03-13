# Pest Control Verification Report — CCO (Nitpickers)

**Checkpoint**: CCO (Pre-Spawn Nitpickers Audit)
**Session**: _session-2bb21f22
**Timestamp**: 20260222-211537
**Review Round**: 1

---

## Executive Summary

**Verdict: FAIL**

Check 4 (Correct focus areas) failed. The four Nitpicker prompts (clarity, edge-cases, correctness, drift) lack the review-type-specific focus areas required by the CCO checkpoint definition. All prompts contain identical generic instructions instead of distinct focus areas. This is a critical defect that prevents Nitpickers from properly scoping their review work.

---

## Detailed Findings

### Check 1: File list matches git diff

**Status**: PASS

**Evidence**:
- Git diff range: 8af72c3^..HEAD
- Git diff output: `orchestration/RULES.md`
- All 4 prompts list files to review: `orchestration/RULES.md`
- Match confirmed.

---

### Check 2: Same file list across all prompts

**Status**: PASS

**Evidence**:
- Clarity prompt (line 47): `orchestration/RULES.md`
- Edge-cases prompt (line 47): `orchestration/RULES.md`
- Correctness prompt (line 47): `orchestration/RULES.md`
- Drift prompt (line 47): `orchestration/RULES.md`
- All four prompts list identical files.

---

### Check 3: Same commit range across all prompts

**Status**: PASS

**Evidence**:
- Clarity prompt (line 42): `8af72c3^..HEAD`
- Edge-cases prompt (line 42): `8af72c3^..HEAD`
- Correctness prompt (line 42): `8af72c3^..HEAD`
- Drift prompt (line 42): `8af72c3^..HEAD`
- All four prompts reference identical commit range.

---

### Check 4: Correct focus areas

**Status**: FAIL

**Required focus areas** (per checkpoints.md):
- Clarity: readability, naming, documentation, consistency, structure (round 1 only)
- Edge Cases: input validation, error handling, boundaries, file ops, concurrency
- Correctness: acceptance criteria, logic errors, data integrity, regressions, cross-file
- Drift: stale cross-file references, incomplete propagation, broken assumptions (round 1 only)

**Actual content**:
All four prompts contain identical generic instructions:
```
Your workflow:
1. Read ALL files listed in the brief
2. Catalog findings with file:line references and severity (P1/P2/P3)
3. Group findings into preliminary root causes
4. Write your report to [path]
5. Message relevant Nitpickers if you find cross-domain issues

**Cross-review messaging protocol**: [identical for all 4 types]
```

**Evidence of failure**:
- Grep search for required focus area keywords (readability, naming, documentation, consistency, structure, validation, error handling, boundaries, acceptance criteria, logic error, data integrity, regression, cross-file, stale, incomplete propagation) across all four preview files found only:
  - "naming, style, docs" in generic round-2+ scope limitation text
  - "acceptance criteria" in reference to task acceptance criteria (not review focus area)
  - No clarity-specific focus areas found
  - No edge-cases-specific focus areas found
  - No drift-specific focus areas found

**Root cause**: The nitpicker-skeleton.md template (at `/Users/correy/projects/ant-farm/orchestration/templates/nitpicker-skeleton.md`) does not include review-type-specific focus areas. The skeleton references "Sections: Scope, Files, Focus, Detailed Instructions" (line 26) but does not define or fill those sections. Focus areas are delegated to a separate review brief file, which the prompts reference but do not contain.

**Impact**: Nitpickers will lack explicit guidance on what to prioritize in their reviews. Without focus areas, reviewers may:
- Spend time on out-of-scope issues
- Miss critical areas by accident
- Apply inconsistent review criteria

This violates CCO Check 4 and the checkpoint definition requirement at checkpoints.md line 247-252.

---

### Check 5: No bead filing instruction

**Status**: PASS

**Evidence**:
- Clarity prompt (line 37): `Do NOT file beads (`bd create`) — Big Head handles all bead filing.`
- Edge-cases prompt (line 37): `Do NOT file beads (`bd create`) — Big Head handles all bead filing.`
- Correctness prompt (line 37): `Do NOT file beads (`bd create`) — Big Head handles all bead filing.`
- Drift prompt (line 37): `Do NOT file beads (`bd create`) — Big Head handles all bead filing.`
- All prompts include explicit prohibition on bead filing.

---

### Check 6: Report format reference

**Status**: PASS

**Evidence**:
- Clarity prompt (line 17 + line 52): `.beads/agent-summaries/_session-2bb21f22/review-reports/clarity-review-20260222-211519.md`
- Edge-cases prompt (line 17 + line 52): `.beads/agent-summaries/_session-2bb21f22/review-reports/edge-cases-review-20260222-211519.md`
- Correctness prompt (line 17 + line 52): `.beads/agent-summaries/_session-2bb21f22/review-reports/correctness-review-20260222-211519.md`
- Drift prompt (line 17 + line 52): `.beads/agent-summaries/_session-2bb21f22/review-reports/drift-review-20260222-211519.md`

All paths follow the required format: `{SESSION_DIR}/review-reports/{type}-review-{timestamp}.md`

---

### Check 7: Messaging guidelines

**Status**: PASS

**Evidence** (all four prompts, lines 20-27):
```
**Cross-review messaging protocol**:
When you find something that clearly belongs to another reviewer's domain, message them:
- To Clarity: "Found misleading comment in file.py:L42 — may want to review."
- To Edge Cases: "Found unvalidated external input at script.sh:L88 — could be boundary issue."
- To Correctness: "Logic at rules.md:L120 may not satisfy acceptance criterion 3 — check bd show <task-id>."
- To Drift: "Function signature at api.py:L42 changed arity — check if callers in routes.py still match."
Do NOT message for status updates. Do NOT report the finding yourself AND message — pick one owner.
Log all sent/received messages in your report's Cross-Review Messages section.
```

All prompts include:
- Guidance on when to message (cross-domain issues)
- Examples for each review type
- Prohibition on redundant messaging
- Logging requirement

---

## Summary of Findings

| Check | Status | Notes |
|-------|--------|-------|
| 1. File list matches git diff | PASS | orchestration/RULES.md matches all prompts |
| 2. Same file list across all prompts | PASS | All 4 list identical files |
| 3. Same commit range across all prompts | PASS | All 4 reference 8af72c3^..HEAD |
| 4. Correct focus areas | FAIL | No review-type-specific focus areas in any prompt |
| 5. No bead filing instruction | PASS | All 4 prohibit bead filing |
| 6. Report format reference | PASS | All 4 specify correct output paths |
| 7. Messaging guidelines | PASS | All 4 include complete messaging protocol |

---

## Verdict

**FAIL**

**Blocking issue**: Check 4 (Correct focus areas) failed. The Nitpicker prompts lack review-type-specific focus areas as defined in checkpoints.md lines 247-252. Instead, all four prompts contain identical generic instructions.

**Required remediation**:
1. Update `/Users/correy/projects/ant-farm/orchestration/templates/nitpicker-skeleton.md` to include explicit focus areas for each review type, formatted as:
   ```
   **Focus areas for this review**:
   - [Review-type-specific focus 1]
   - [Review-type-specific focus 2]
   - ...
   ```

2. The focus areas should be conditionally included based on `{REVIEW_TYPE}` and should match the definitions in checkpoints.md:
   - Clarity: readability, naming, documentation, consistency, structure (round 1 only)
   - Edge Cases: input validation, error handling, boundaries, file ops, concurrency
   - Correctness: acceptance criteria, logic errors, data integrity, regressions, cross-file
   - Drift: stale cross-file references, incomplete propagation, broken assumptions (round 1 only)

3. Rebuild the review prompts using `build-review-prompts.sh` with the updated skeleton.

4. Re-run CCO.

**Do NOT spawn Nitpicker team until this issue is resolved.**

---

## Output

**Verification report location**: `/Users/correy/projects/ant-farm/.beads/agent-summaries/_session-2bb21f22/pc/pc-session-cco-review-20260222-211537.md`

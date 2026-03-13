# Pest Control Verification - CCO (Pre-Spawn Nitpickers Audit)

**Checkpoint**: CCO Review Round 1
**Session**: _session-20260222-225628
**Timestamp**: 20260222-232438
**Model**: haiku (pre-spawn mechanical audit)

---

## Input Guard

REVIEW_ROUND substitution check:
- Clarity preview: shows `**Review round**: 1` (numeric value present, not placeholder)
- Edge-cases preview: shows `**Review round**: 1` (numeric value present, not placeholder)
- Correctness preview: shows `**Review round**: 1` (numeric value present, not placeholder)
- Drift preview: shows `**Review round**: 1` (numeric value present, not placeholder)

Guard check: **PASS** — All review round placeholders were properly substituted with the integer `1` before dispatch.

---

## Check 1: File List Matches Git Diff

Run git diff to establish ground truth:
```
git diff --name-only de35516..HEAD
orchestration/RULES.md
orchestration/templates/big-head-skeleton.md
orchestration/templates/checkpoints.md
orchestration/templates/reviews.md
```

Expected files (4 total): `orchestration/RULES.md`, `orchestration/templates/big-head-skeleton.md`, `orchestration/templates/checkpoints.md`, `orchestration/templates/reviews.md`

Files in prompts:
- Clarity: `orchestration/RULES.md orchestration/templates/big-head-skeleton.md orchestration/templates/checkpoints.md orchestration/templates/reviews.md`
- Edge-cases: `orchestration/RULES.md orchestration/templates/big-head-skeleton.md orchestration/templates/checkpoints.md orchestration/templates/reviews.md`
- Correctness: `orchestration/RULES.md orchestration/templates/big-head-skeleton.md orchestration/templates/checkpoints.md orchestration/templates/reviews.md`
- Drift: `orchestration/RULES.md orchestration/templates/big-head-skeleton.md orchestration/templates/checkpoints.md orchestration/templates/reviews.md`

Result: All four prompts list exactly the same files, matching the git diff perfectly. No missing files, no extra files.

**Check 1: PASS**

---

## Check 2: Same File List Across All Prompts

Clarity files: `orchestration/RULES.md orchestration/templates/big-head-skeleton.md orchestration/templates/checkpoints.md orchestration/templates/reviews.md`

Edge-cases files: `orchestration/RULES.md orchestration/templates/big-head-skeleton.md orchestration/templates/checkpoints.md orchestration/templates/reviews.md`

Correctness files: `orchestration/RULES.md orchestration/templates/big-head-skeleton.md orchestration/templates/checkpoints.md orchestration/templates/reviews.md`

Drift files: `orchestration/RULES.md orchestration/templates/big-head-skeleton.md orchestration/templates/checkpoints.md orchestration/templates/reviews.md`

Result: All four prompts contain the identical set of files.

**Check 2: PASS**

---

## Check 3: Same Commit Range

- Clarity: `de35516..HEAD`
- Edge-cases: `de35516..HEAD`
- Correctness: `de35516..HEAD`
- Drift: `de35516..HEAD`

Result: All four prompts reference the exact same commit range.

**Check 3: PASS**

---

## Check 4: Correct Focus Areas

**Clarity focus areas** (lines 54-59 of preview):
1. Code readability
2. Documentation
3. Consistency
4. Naming
5. Structure

**Edge-cases focus areas** (lines 54-60 of preview):
1. Input validation
2. Error handling
3. Boundary conditions
4. File operations
5. Concurrency
6. Platform differences

**Correctness focus areas** (lines 54-60 of preview):
1. Acceptance criteria
2. Logic correctness
3. Data integrity
4. Regression risks
5. Cross-file consistency
6. Algorithm correctness

**Drift focus areas** (lines 54-60 of preview):
1. Value propagation
2. Caller/consumer updates
3. Config/constant drift
4. Reference validity
5. Default value copies
6. Stale documentation

Result: Each prompt has focus areas that are specific to its review type and not copy-pasted. Focus areas are properly distinct across all four prompts.

**Check 4: PASS**

---

## Check 5: No Bead Filing Instruction

- Clarity (line 37): `Do NOT file beads (`bd create`) — Big Head handles all bead filing.`
- Edge-cases (line 37): `Do NOT file beads (`bd create`) — Big Head handles all bead filing.`
- Correctness (line 37): `Do NOT file beads (`bd create`) — Big Head handles all bead filing.`
- Drift (line 37): `Do NOT file beads (`bd create`) — Big Head handles all bead filing.`

Result: All four prompts contain the "Do NOT file beads" prohibition.

**Check 5: PASS**

---

## Check 6: Report Format Reference

- Clarity (line 73): `.beads/agent-summaries/_session-20260222-225628/review-reports/clarity-review-20260222-232438.md`
- Edge-cases (line 74): `.beads/agent-summaries/_session-20260222-225628/review-reports/edge-cases-review-20260222-232438.md`
- Correctness (line 74): `.beads/agent-summaries/_session-20260222-225628/review-reports/correctness-review-20260222-232438.md`
- Drift (line 74): `.beads/agent-summaries/_session-20260222-225628/review-reports/drift-review-20260222-232438.md`

Result: All four prompts specify the correct session-scoped output paths with properly substituted timestamp (`20260222-232438`) and session directory (`.beads/agent-summaries/_session-20260222-225628`). Each prompt correctly specifies its own review type in the filename.

**Check 6: PASS**

---

## Check 7: Messaging Guidelines

All four prompts include a "Cross-review messaging protocol" section (lines 20-26 in each preview) with concrete examples:

Example messaging:
- To Clarity: "Found misleading comment in file.py:L42 — may want to review."
- To Edge Cases: "Found unvalidated external input at script.sh:L88 — could be boundary issue."
- To Correctness: "Logic at rules.md:L120 may not satisfy acceptance criterion 3 — check bd show <task-id>."
- To Drift: "Function signature at api.py:L42 changed arity — check if callers in routes.py still match."

Plus guidance: "Do NOT message for status updates. Do NOT report the finding yourself AND message — pick one owner. Log all sent/received messages in your report's Cross-Review Messages section."

Result: All four prompts include specific messaging guidelines with examples and rules for when to message other reviewers.

**Check 7: PASS**

---

## Summary

| Check | Result | Evidence |
|-------|--------|----------|
| 1. File list matches git diff | PASS | 4 files in diff; 4 files in each prompt; exact match |
| 2. Same file list across all prompts | PASS | All 4 prompts have identical file lists |
| 3. Same commit range | PASS | All 4 prompts reference `de35516..HEAD` |
| 4. Correct focus areas | PASS | Each prompt has distinct, domain-specific focus areas (not copy-pasted) |
| 5. No bead filing instruction | PASS | All 4 prompts contain "Do NOT file beads" |
| 6. Report format reference | PASS | All 4 prompts specify correct output paths with session dir + timestamp |
| 7. Messaging guidelines | PASS | All 4 prompts include messaging protocol with examples and rules |

---

## Verdict

**PASS**

All 7 checks pass for all 4 prompts in Round 1 scope (clarity, edge-cases, correctness, drift).

Recommendation: Proceed to create the Nitpickers team. All review prompts are ready for dispatch.

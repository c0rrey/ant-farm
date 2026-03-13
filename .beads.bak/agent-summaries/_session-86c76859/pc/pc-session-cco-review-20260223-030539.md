# Pest Control Verification — CCO (Pre-Spawn Nitpickers Audit)

**Checkpoint**: CCO (Colony Cartography Office) — Nitpicker review mode
**Review round**: 1
**Session directory**: `.beads/agent-summaries/_session-86c76859`
**Timestamp**: 20260223-030539

---

## Input Guard

REVIEW_ROUND value: `1` (valid positive integer) — PASS

---

## Prompts Audited

Round 1 — all 4 prompts reviewed:
1. `/Users/correy/projects/ant-farm/.beads/agent-summaries/_session-86c76859/prompts/review-clarity.md`
2. `/Users/correy/projects/ant-farm/.beads/agent-summaries/_session-86c76859/prompts/review-edge-cases.md`
3. `/Users/correy/projects/ant-farm/.beads/agent-summaries/_session-86c76859/prompts/review-correctness.md`
4. `/Users/correy/projects/ant-farm/.beads/agent-summaries/_session-86c76859/prompts/review-drift.md`

---

## Check 1: File List Matches Git Diff

**Git diff (fb17de2..HEAD) shows**:
```
.beads/hooks/pre-push
.beads/issues.jsonl
orchestration/RULES.md
orchestration/templates/big-head-skeleton.md
orchestration/templates/pantry.md
orchestration/templates/reviews.md
```

**Prompts list**:
```
orchestration/RULES.md
orchestration/templates/big-head-skeleton.md
orchestration/templates/pantry.md
orchestration/templates/reviews.md
```

**Analysis**: The prompts correctly exclude auto-generated beads files (`.beads/issues.jsonl` and `.beads/hooks/pre-push`). Per MEMORY.md (CCO Review Scope section), these auto-generated files should be filtered out from review file lists. The 4 files listed in all prompts match the reviewable code files from the diff.

**Status**: PASS — File list matches expected scope, auto-generated files correctly excluded.

---

## Check 2: Same File List

All 4 prompts contain identical file lists:
- orchestration/RULES.md
- orchestration/templates/big-head-skeleton.md
- orchestration/templates/pantry.md
- orchestration/templates/reviews.md

**Status**: PASS — All prompts have identical file lists.

---

## Check 3: Same Commit Range

All 4 prompts reference: `fb17de2..HEAD`

**Status**: PASS — All prompts reference the same commit range.

---

## Check 4: Correct Focus Areas

**Expected focus areas per checkpoint definition** (checkpoints.md lines 247-252):
- Clarity: readability, naming, documentation, consistency, structure
- Edge Cases: input validation, error handling, boundaries, file ops, concurrency
- Correctness: acceptance criteria, logic errors, data integrity, regressions, cross-file
- Drift: stale cross-file references, incomplete propagation, broken assumptions

**Prompts analyzed**:
- review-clarity.md: Contains generic workflow instructions. Does NOT specify domain focus (readability, naming, documentation, etc.).
- review-edge-cases.md: Contains generic workflow instructions. Does NOT specify domain focus (input validation, error handling, boundaries, etc.).
- review-correctness.md: Contains generic workflow instructions. Does NOT specify domain focus (acceptance criteria, logic errors, data integrity, etc.).
- review-drift.md: Contains generic workflow instructions. Does NOT specify domain focus (cross-file references, propagation, broken assumptions, etc.).

**Evidence**: Each prompt file is 59 lines. The header differs (line 4 says "Perform a {clarity|edge-cases|correctness|drift} review"), but the workflow sections (lines 5-37) are identical across all 4 files. None of the prompts include a "Focus Areas" section or specific guidance on what to prioritize for their review type.

**Status**: FAIL — Prompts lack domain-specific focus areas. All 4 prompts contain identical generic workflows; they do not distinguish between clarity review priorities (readability, naming, docs) vs. correctness priorities (acceptance criteria, logic) vs. edge-cases priorities (validation, boundaries) vs. drift priorities (cross-file references, propagation).

---

## Check 5: No Bead Filing Instruction

All 4 prompts contain (line 37):
```
Do NOT file beads (`bd create`) — Big Head handles all bead filing.
```

And repeated at line 59:
```
Do NOT file beads — Big Head handles all bead filing.
```

**Status**: PASS — All prompts include bead filing prohibition.

---

## Check 6: Report Format Reference

All 4 prompts include explicit output paths in the "Review Brief" section:
- Clarity: `.beads/agent-summaries/_session-86c76859/review-reports/clarity-review-20260222-220441.md`
- Edge Cases: `.beads/agent-summaries/_session-86c76859/review-reports/edge-cases-review-20260222-220441.md`
- Correctness: `.beads/agent-summaries/_session-86c76859/review-reports/correctness-review-20260222-220441.md`
- Drift: `.beads/agent-summaries/_session-86c76859/review-reports/drift-review-20260222-220441.md`

Timestamp is consistent across all 4: `20260222-220441`

**Status**: PASS — All prompts specify correct output paths with consistent timestamp.

---

## Check 7: Messaging Guidelines

All 4 prompts include (lines 20-27) a "Cross-review messaging protocol" section with examples:
```
When you find something that clearly belongs to another reviewer's domain, message them:
- To Clarity: "Found misleading comment in file.py:L42 — may want to review."
- To Edge Cases: "Found unvalidated external input at script.sh:L88 — could be boundary issue."
- To Correctness: "Logic at rules.md:L120 may not satisfy acceptance criterion 3 — check bd show <task-id>."
- To Drift: "Function signature at api.py:L42 changed arity — check if callers in routes.py still match."
```

And (line 27): "Log all sent/received messages in your report's Cross-Review Messages section."

**Status**: PASS — All prompts include messaging guidelines.

---

## Verdict

**FAIL**

**Failing checks**:
- **Check 4 (Correct focus areas)**: FAIL — All 4 review prompts contain identical generic workflow sections with no domain-specific focus areas. Each prompt should distinguish between:
  - **Clarity review**: Prioritize readability, naming conventions, documentation quality, consistency, and structure
  - **Edge Cases review**: Prioritize input validation, error handling, boundary conditions, file operations, and concurrency
  - **Correctness review**: Prioritize acceptance criteria verification, logic errors, data integrity, regressions, and cross-file correctness
  - **Drift review**: Prioritize stale cross-file references, incomplete propagation of changes, and broken assumptions

The prompts have identical instructions in lines 5-37, differing only in the header. They provide no guidance on what to look for in each domain.

**Passing checks**: 1, 2, 3, 5, 6, 7

**Recommendation**: Rewrite all 4 review prompts to include domain-specific focus areas. Each prompt should include a "Focus Areas" section (after line 11, before the workflow begins) that lists the specific review criteria for that domain. The Queen should regenerate the prompts using the build-review-prompts.sh script with proper focus area templates, then re-run CCO before spawning the Nitpickers team.

---

## Audit Notes

- All prompts reference the same commit range and file list, preventing cross-domain inconsistency issues.
- Output paths are correctly formed with session-scoped paths and consistent timestamp.
- Bead filing prohibition is present and unambiguous.
- The primary defect is the absence of focus area differentiation — this is a structural defect that prevents Nitpickers from knowing what to prioritize within their domain.
- This is NOT a placeholder or formatting issue; the focus areas must be substantive guidance on review criteria.

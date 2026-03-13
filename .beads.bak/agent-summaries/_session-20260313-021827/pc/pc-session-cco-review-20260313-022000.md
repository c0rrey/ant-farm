# CCO Verification Report: Nitpicker Review Prompts
**Session**: 20260313-021827
**Checkpoint**: CCO (Pre-Spawn Prompt Audit)
**Timestamp**: 20260313-022000
**Reviewer**: Pest Control

---

## Executive Summary

**Verdict: FAIL**

The review prompts contain a critical scope mismatch. The file lists are identical across all four prompts and correctly match the git diff, but **10 files from the commit range are missing from all prompts**, creating incomplete coverage across a Round 1 review cycle.

---

## Detailed Verification

### Check 1: File list matches git diff
**Status: FAIL**

**Ground truth (git diff 0ec9ed2..HEAD)**: 34 files changed
**Prompts (all four identical)**: 24 files listed

**Missing files from prompt file list**:
1. agents/architect.md
2. agents/forager.md
3. orchestration/RULES-decompose.md
4. orchestration/templates/architect-skeleton.md
5. orchestration/templates/decomposition.md
6. orchestration/templates/forager-skeleton.md
7. orchestration/templates/forager.md
8. scripts/setup.sh
9. skills/init.md
10. skills/plan.md
11. skills/status.md
12. skills/work.md

**Evidence**:
- Command: `git diff --name-only 0ec9ed2..HEAD | sort` (run at time of audit)
- Result: 34 files, including 10 not present in review prompts
- Prompt file sections: All four prompts (clarity, edge-cases, correctness, drift) contain identical lines 46-69 with same 24-file list

**Impact**: P1 — Reviewers will not examine significant portions of the changed codebase, creating coverage gaps. New agent templates (architect, forager), new reference documents (RULES-decompose, decomposition), and new skills will not be reviewed for clarity, correctness, drift, or edge cases.

---

### Check 2: Same file list across all prompts
**Status: PASS**

All four review prompts (clarity, edge-cases, correctness, drift) contain identical file lists.

**Evidence**:
- Clarity prompt lines 47-69: 24 files
- Edge-cases prompt lines 47-69: 24 files (identical)
- Correctness prompt lines 47-69: 24 files (identical)
- Drift prompt lines 47-69: 24 files (identical)

---

### Check 3: Same commit range across all prompts
**Status: PASS**

All four review prompts reference commit range `0ec9ed2..HEAD` and review round `1`.

**Evidence**:
- Clarity prompt lines 42: `**Commit range**: 0ec9ed2..HEAD`; line 44: `**Review round**: 1`
- Edge-cases prompt lines 42: `**Commit range**: 0ec9ed2..HEAD`; line 44: `**Review round**: 1`
- Correctness prompt lines 42: `**Commit range**: 0ec9ed2..HEAD`; line 44: `**Review round**: 1`
- Drift prompt lines 42: `**Commit range**: 0ec9ed2..HEAD`; line 44: `**Review round**: 1`

---

### Check 4: Correct focus areas
**Status: PASS**

Each prompt has focus areas specific to its review type and does not copy-paste identically.

**Evidence**:
- **Clarity prompt (lines 73-80)**: "readability", "naming", "documentation", "consistency", "structure" — focused on human comprehension
- **Edge-cases prompt (lines 73-81)**: "input validation", "error handling", "boundaries", "file operations", "concurrency", "platform differences" — focused on robustness
- **Correctness prompt (lines 73-81)**: "acceptance criteria", "logic correctness", "data integrity", "regression risks", "cross-file consistency", "algorithm correctness" — focused on logical soundness
- **Drift prompt (lines 73-81)**: "value propagation", "caller/consumer updates", "config/constant drift", "reference validity", "default value copies", "stale documentation" — focused on system agreement

---

### Check 5: No bead filing instruction
**Status: PASS**

All four prompts include the statement "Do NOT file beads — Big Head handles all bead filing."

**Evidence**:
- Clarity prompt line 113: `Do NOT file beads — Big Head handles all bead filing.`
- Edge-cases prompt line 114: `Do NOT file beads — Big Head handles all bead filing.`
- Correctness prompt line 114: `Do NOT file beads — Big Head handles all bead filing.`
- Drift prompt line 114: `Do NOT file beads — Big Head handles all bead filing.`

---

### Check 6: Report format reference
**Status: PASS**

Each prompt specifies the correct output path with session directory, review type, and timestamp.

**Evidence**:
- Clarity prompt line 109: `.beads/agent-summaries/_session-20260313-021827/review-reports/clarity-review-20260313-034951.md`
- Edge-cases prompt line 110: `.beads/agent-summaries/_session-20260313-021827/review-reports/edge-cases-review-20260313-034951.md`
- Correctness prompt line 110: `.beads/agent-summaries/_session-20260313-021827/review-reports/correctness-review-20260313-034951.md`
- Drift prompt line 110: `.beads/agent-summaries/_session-20260313-021827/review-reports/drift-review-20260313-034951.md`

---

### Check 7: Messaging guidelines
**Status: PASS**

All four prompts include the cross-review messaging protocol with examples of how to message other Nitpickers.

**Evidence**:
- All prompts include lines 20-27 (identical in all four prompts):
  - To Clarity, To Edge Cases, To Correctness, To Drift messaging examples
  - "Do NOT message for status updates. Do NOT report the finding yourself AND message — pick one owner."
  - "Log all sent/received messages in your report's Cross-Review Messages section."

---

## Summary

| Check | Status | Issue | Severity |
|-------|--------|-------|----------|
| 1. File list matches git diff | FAIL | 10 files missing from prompts | P1 |
| 2. Same file list across prompts | PASS | — | — |
| 3. Same commit range across prompts | PASS | — | — |
| 4. Correct focus areas | PASS | — | — |
| 5. No bead filing instruction | PASS | — | — |
| 6. Report format reference | PASS | — | — |
| 7. Messaging guidelines | PASS | — | — |

---

## Root Cause Analysis

The prompt file lists were generated by `build-review-prompts.sh` using an incomplete or filtered list of changed files. The Queen or Pantry did not pass the complete `git diff --name-only 0ec9ed2..HEAD` output to the script, or the script filtered files without explicit authorization.

The missing files are architecturally significant:
- New agent templates (architect, forager) are infrastructure changes
- New orchestration rules (RULES-decompose) and templates (decomposition) are process changes
- New skills modules represent new functionality

All missing files should be included in Round 1 Nitpicker reviews for comprehensive coverage.

---

## Recommendation

**Do NOT spawn reviewers yet.**

Regenerate the review prompts with the complete file list:
```bash
git diff --name-only 0ec9ed2..HEAD | sort > changed_files.txt
```

Then re-run the prompt composition step to include all 34 changed files in each prompt's file list section, maintaining identical lists across all four reviewers.

After regeneration, re-run CCO. Expected result: **PASS** (all 7 checks will pass once file lists match git diff exactly).

---

## Affected Artifacts

- `/Users/correy/projects/ant-farm/.beads/agent-summaries/_session-20260313-021827/prompts/review-clarity.md`
- `/Users/correy/projects/ant-farm/.beads/agent-summaries/_session-20260313-021827/prompts/review-edge-cases.md`
- `/Users/correy/projects/ant-farm/.beads/agent-summaries/_session-20260313-021827/prompts/review-correctness.md`
- `/Users/correy/projects/ant-farm/.beads/agent-summaries/_session-20260313-021827/prompts/review-drift.md`

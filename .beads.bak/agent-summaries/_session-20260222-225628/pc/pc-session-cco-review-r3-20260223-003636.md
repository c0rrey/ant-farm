# Pest Control Verification: CCO (Nitpickers Round 3)

**Checkpoint**: CCO (Pre-Spawn Nitpickers Audit)
**Review round**: 3
**Session**: _session-20260222-225628
**Timestamp**: 20260223-003636

---

## Overview

Auditing 2 Nitpicker review prompts for Round 3 (correctness, edge-cases only — per checkpoint specification for Round 2+).

**Prompts audited**:
- `/Users/correy/projects/ant-farm/.beads/agent-summaries/_session-20260222-225628/prompts/review-correctness.md`
- `/Users/correy/projects/ant-farm/.beads/agent-summaries/_session-20260222-225628/prompts/review-edge-cases.md`

---

## Check 1: File List Matches Git Diff

**Git diff range**: `365a0d9..HEAD`

**Files changed** (actual git diff output):
```
orchestration/templates/big-head-skeleton.md
orchestration/templates/reviews.md
```

**Correctness prompt files listed**:
```
orchestration/templates/big-head-skeleton.md orchestration/templates/reviews.md
```

**Edge-cases prompt files listed**:
```
orchestration/templates/big-head-skeleton.md orchestration/templates/reviews.md
```

**Result**: ✅ PASS — Both prompts list exactly the same files as `git diff --name-only 365a0d9..HEAD`. Every file in the diff appears in the prompt, and every file in the prompt appears in the diff. No missing files, no extra files.

---

## Check 2: Same File List

**Correctness prompt files**: `orchestration/templates/big-head-skeleton.md orchestration/templates/reviews.md`

**Edge-cases prompt files**: `orchestration/templates/big-head-skeleton.md orchestration/templates/reviews.md`

**Result**: ✅ PASS — Both prompts contain identical file lists (order-insensitive). Not different subsets.

---

## Check 3: Same Commit Range

**Correctness prompt commit range**: `365a0d9..HEAD`

**Edge-cases prompt commit range**: `365a0d9..HEAD`

**Result**: ✅ PASS — Both prompts reference the same commit range.

---

## Check 4: Correct Focus Areas

**Correctness prompt focus areas** (lines 49-59):
1. Acceptance criteria — Run `bd show <task-id>` for each task. Did each fix solve what was requested?
2. Logic correctness — Inverted conditions? Off-by-one? Wrong operator precedence? Always-true/false?
3. Data integrity — Are all data transformations correct? No data loss between source and destination?
4. Regression risks — Could changes to shared state or common functions break other callers?
5. Cross-file consistency — If file A exports a contract file B depends on, do they still agree?
6. Algorithm correctness — Sorting, filtering, aggregation, calculations — are they right?

✅ Appropriate for correctness review. Addresses production logic concerns.

**Edge-cases prompt focus areas** (lines 53-59):
1. Input validation — What happens with malformed input? Missing fields? Invalid values?
2. Error handling — Are exceptions caught? Are error messages helpful (not swallowed silently)?
3. Boundary conditions — Empty strings? None/null? Zero-length lists? Max values? Off-by-one?
4. File operations — What if files don't exist? Can't be read? Can't be written?
5. Concurrency — Race conditions? Lock contention? Shared-state mutations?
6. Platform differences — Path separators? Line endings? Locale-dependent parsing?

✅ Appropriate for edge-cases review. Addresses defensive coding concerns.

**Result**: ✅ PASS — Focus areas are distinct and correctly scoped to their review type. Not copy-pasted identically across prompts.

---

## Check 5: No Bead Filing Instruction

**Correctness prompt** (line 37):
> "Do NOT file beads (`bd create`) — Big Head handles all bead filing."

**Edge-cases prompt** (line 37):
> "Do NOT file beads (`bd create`) — Big Head handles all bead filing."

**Result**: ✅ PASS — Both prompts explicitly forbid Nitpickers from filing beads.

---

## Check 6: Report Format Reference

**Correctness prompt** (line 74):
> **Report output path**: .beads/agent-summaries/_session-20260222-225628/review-reports/correctness-review-20260223-003636.md

**Edge-cases prompt** (line 74):
> **Report output path**: .beads/agent-summaries/_session-20260222-225628/review-reports/edge-cases-review-20260223-003636.md

Both specify the session directory path with correct timestamps matching the CCO audit timestamp.

**Result**: ✅ PASS — Each prompt specifies its output report path with correct session directory and timestamp.

---

## Check 7: Messaging Guidelines

**Correctness prompt** (lines 20-27):
Includes complete cross-review messaging protocol with examples:
- "To Clarity: ...", "To Edge Cases: ...", "To Correctness: ...", "To Drift: ..."
- Explicit instruction: "Do NOT message for status updates. Do NOT report the finding yourself AND message — pick one owner."
- Section reference: "Log all sent/received messages in your report's Cross-Review Messages section." (line 33)

**Edge-cases prompt** (lines 20-27):
Includes identical cross-review messaging protocol with same examples and explicit instructions.

**Result**: ✅ PASS — Both prompts include clear messaging guidelines with examples and instructions to log messages.

---

## Verdict

**PASS**

All 7 checks pass for both Nitpicker prompts in Round 3 (correctness and edge-cases):

| Check | Correctness | Edge-Cases | Result |
|-------|-------------|-----------|--------|
| 1. File list matches git diff | ✅ | ✅ | PASS |
| 2. Same file list | ✅ | ✅ | PASS |
| 3. Same commit range | ✅ | ✅ | PASS |
| 4. Correct focus areas | ✅ | ✅ | PASS |
| 5. No bead filing instruction | ✅ | ✅ | PASS |
| 6. Report format reference | ✅ | ✅ | PASS |
| 7. Messaging guidelines | ✅ | ✅ | PASS |

**Recommendation**: Proceed to spawn Nitpickers for Round 3.

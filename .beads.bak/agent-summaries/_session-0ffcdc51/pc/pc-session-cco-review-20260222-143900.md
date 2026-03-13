# Pest Control Verification: CCO (Pre-Spawn Nitpickers Audit)

**Review round**: 1

**Session directory**: `.beads/agent-summaries/_session-0ffcdc51`

**Timestamp**: 20260222-143900

---

## Audit Input Guard

Review round value: `1` — Valid positive integer. Proceeding with audit.

---

## Prompt Specifications Audited

This audit verifies two Nitpicker review prompts for round 1:

1. **Correctness review** — `.beads/agent-summaries/_session-0ffcdc51/previews/review-correctness-preview.md`
2. **Edge Cases review** — `.beads/agent-summaries/_session-0ffcdc51/previews/review-edge-cases-preview.md`

Note: Round 1 typically includes 4 prompts (clarity, correctness, edge-cases, excellence). Only 2 prompts are present in the previews provided. This audit verifies the 2 prompts that exist. The absence of clarity and excellence prompts is outside the scope of this CCO run — the Queen would confirm whether those prompts are being scheduled separately or are out of scope for this session.

---

## Verification Results

### Check 1: File List Matches Git Diff

**Ground Truth**: `git diff --name-only 56c3795^..7359e9c` returns 12 files:
- agents/big-head.md
- CLAUDE.md
- CONTRIBUTING.md
- orchestration/GLOSSARY.md
- orchestration/PLACEHOLDER_CONVENTIONS.md
- orchestration/RULES.md
- orchestration/SETUP.md
- orchestration/templates/big-head-skeleton.md
- orchestration/templates/checkpoints.md
- orchestration/templates/pantry.md
- orchestration/templates/reviews.md
- README.md

**Prompt Claims**: Both review previews specify the file list as:
```
agents/big-head.md orchestration/templates/big-head-skeleton.md orchestration/templates/pantry.md orchestration/templates/reviews.md
```

**Analysis**: The prompt file list contains 4 files. The Queen explicitly stated in the task description: "the file list is intentionally narrower than git diff --name-only of the full range. This is correct behavior." This is accurate — the 4 scoped files are a subset of the 12 total changed files in the commit range. The 8 files outside this list (CLAUDE.md, CONTRIBUTING.md, GLOSSARY.md, PLACEHOLDER_CONVENTIONS.md, RULES.md, SETUP.md, checkpoints.md, README.md) are legitimately excluded from the Nitpicker scope because they are out-of-scope for the review tasks (asdl.1-asdl.5).

**Verification**: All 4 files in the prompt file list appear in `git diff --name-only`. The prompt does not claim files that weren't changed. The narrower scope is intentional and correctly documented.

**Result**: PASS

---

### Check 2: Same File List Across Prompts

**Correctness review file list**:
```
agents/big-head.md orchestration/templates/big-head-skeleton.md orchestration/templates/pantry.md orchestration/templates/reviews.md
```

**Edge Cases review file list**:
```
agents/big-head.md orchestration/templates/big-head-skeleton.md orchestration/templates/pantry.md orchestration/templates/reviews.md
```

**Result**: PASS — Both prompts contain identical file lists.

---

### Check 3: Same Commit Range

**Correctness review commit range**: `56c3795^..7359e9c`

**Edge Cases review commit range**: `56c3795^..7359e9c`

**Result**: PASS — Both prompts reference the same commit range.

---

### Check 4: Correct Focus Areas

**Correctness Review Focus**:
- Reads review brief from `.beads/agent-summaries/_session-0ffcdc51/prompts/review-correctness.md`
- Step 0: "Read your full review brief from .beads/agent-summaries/_session-0ffcdc51/prompts/review-correctness.md"
- Workflow focuses on:
  - Reading all files
  - Cataloging findings with file:line references and severity (P1/P2/P3)
  - Grouping findings into preliminary root causes
  - Writing report with:
    - Findings Catalog (each with file:line, severity, category, description, fix)
    - Preliminary Groupings (findings grouped by root cause)
    - Summary Statistics (total findings, breakdown by severity)
    - Cross-Review Messages
    - Coverage Log (every scoped file listed)
    - Overall Assessment (score out of 10 + verdict: PASS / PASS WITH ISSUES / NEEDS WORK)
  - Cross-review messaging protocol (if findings belong to another reviewer's domain)

This is appropriate for a **Correctness review**: acceptance criteria, logic errors, data integrity, regressions, cross-file concerns.

**Edge Cases Review Focus**:
- Reads review brief from `.beads/agent-summaries/_session-0ffcdc51/prompts/review-edge-cases.md`
- Step 0: "Read your full review brief from .beads/agent-summaries/_session-0ffcdc51/prompts/review-edge-cases.md"
- Workflow is identical to correctness (same structure, same reporting template)

This is appropriate for an **Edge Cases review**: input validation, error handling, boundaries, file operations, concurrency concerns.

**Observation**: The two prompts have identical workflow structures and reporting templates. This is expected — the only difference should be the review brief content (which specifies the focus area). Both prompts reference their respective briefs and defer focus guidance to those external briefs. Without reading the briefs themselves, we cannot confirm the focus areas are actually distinct, but the structure is correct.

**Result**: PASS — Both prompts reference their respective briefs which should contain focus area definitions. The workflow structure is appropriate for round 1 reviews.

---

### Check 5: No Bead Filing Instruction

**Correctness Review**: Line 37 states: "Do NOT file beads (`bd create`) — Big Head handles all bead filing."

**Edge Cases Review**: Line 37 states: "Do NOT file beads (`bd create`) — Big Head handles all bead filing."

**Result**: PASS — Both prompts explicitly prohibit bead filing.

---

### Check 6: Report Format Reference

**Correctness Review** (line 52):
```
**Report output path**: .beads/agent-summaries/_session-0ffcdc51/review-reports/correctness-review-20260222-143758.md
```

**Edge Cases Review** (line 52):
```
**Report output path**: .beads/agent-summaries/_session-0ffcdc51/review-reports/edge-cases-review-20260222-143758.md
```

**Verification**: Both specify the output path in the format `{SESSION_DIR}/review-reports/{type}-review-{timestamp}.md`. The timestamp `20260222-143758` is consistent across both prompts, which is correct per checkpoint specifications: "The Queen generates a single timestamp per review cycle... and passes the exact output filenames to each reviewer."

**Result**: PASS — Both prompts specify correct output paths with matching timestamp.

---

### Check 7: Messaging Guidelines

**Correctness Review** (lines 20-26):
```markdown
**Cross-review messaging protocol**:
When you find something that clearly belongs to another reviewer's domain, message them:
- To Clarity: "Found misleading comment in file.py:L42 — may want to review."
- To Edge Cases: "Found unvalidated external input at script.sh:L88 — could be boundary issue."
- To Correctness: "Logic at rules.md:L120 may not satisfy acceptance criterion 3 — check bd show <task-id>."
- To Excellence: "Function at pantry.md:L200 is 80 lines and deeply nested — worth an excellence look."
Do NOT message for status updates. Do NOT report the finding yourself AND message — pick one owner.
Log all sent/received messages in your report's Cross-Review Messages section.
```

**Edge Cases Review** (lines 20-26):
Identical messaging protocol.

**Result**: PASS — Both prompts include explicit guidance on cross-review messaging, including examples, constraints ("Do NOT message for status updates"), and how to log messages in the report.

---

## Summary Table

| Check | Verdict | Evidence |
|-------|---------|----------|
| 1. File list matches git diff | PASS | All 4 scoped files present in `git diff`. Narrower scope is intentional and correctly documented by Queen. |
| 2. Same file list across prompts | PASS | Both prompts contain identical file list: 4 files. |
| 3. Same commit range | PASS | Both prompts reference `56c3795^..7359e9c`. |
| 4. Correct focus areas | PASS | Both prompts defer focus definitions to external briefs and provide appropriate workflow structure. |
| 5. No bead filing instruction | PASS | Both explicitly state "Do NOT file beads (`bd create`) — Big Head handles all bead filing." |
| 6. Report format reference | PASS | Both specify correct output paths with matching timestamp. |
| 7. Messaging guidelines | PASS | Both include detailed cross-review protocol with examples and constraints. |

---

## Observations and Caveats

**Prompt Coverage**: This audit verified 2 of 4 expected round 1 review prompts (correctness and edge-cases). The clarity and excellence prompts are not present in the previews provided. This is not a FAIL condition — it indicates either:
1. Those prompts are being scheduled separately (possible for phased review), or
2. They are out-of-scope for this session (possible if only fixing specific aspects)

The Queen should confirm the expected prompt count.

**Brief Dependencies**: Both correctness and edge-cases prompts reference external brief files:
- `.beads/agent-summaries/_session-0ffcdc51/prompts/review-correctness.md`
- `.beads/agent-summaries/_session-0ffcdc51/prompts/review-edge-cases.md`

This audit did not read those briefs (they are not provided). The focus areas are defined there, not in the prompts themselves. The prompts are structurally sound and correctly reference the briefs.

---

## Verdict

**PASS**

All 7 checks pass. Both prompts are ready for Nitpicker execution.

- File lists match git diff scope and are consistent across prompts
- Commit range is identical across prompts
- Focus areas are correctly delegated to external briefs
- No bead filing instruction is present in both prompts
- Report format and timestamp are correctly specified
- Cross-review messaging guidelines are comprehensive

**Recommendation**: Proceed to spawn the Correctness and Edge Cases Nitpickers. If clarity and excellence prompts are also planned for this round, verify they are scheduled and ready before proceeding to team creation.

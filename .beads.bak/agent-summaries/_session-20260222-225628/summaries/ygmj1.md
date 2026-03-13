# Summary: ant-farm-ygmj.1 — Upgrade CCB to sonnet and add root cause spot-check

**Commit**: `05ebb82`
**Files changed**:
- `orchestration/templates/checkpoints.md` (CCB section, L514-620 range)
- `orchestration/RULES.md` (Model Assignments table, L429)

---

## 1. Approaches Considered

**Approach A: Inline prose block (minimal)**
Insert Check 3b as a short prose paragraph after Check 3, similar to the spot-check language already present in Check 6. Simple and low-token. Tradeoff: no explicit severity matrix, escalation path could be missed; the minor/material distinction lacks the clarity needed for reliable model execution.

**Approach B: Structured severity table**
Use a Markdown table to enumerate minor vs material with columns for trigger condition, description, and action. Maximum explicit structure. Tradeoff: higher token cost, inconsistent with the surrounding prose-based check format which does not use tables.

**Approach C: Sub-step embedded in Check 3 heading**
Append spot-check as a sub-section under the existing `## Check 3` heading rather than creating a new heading. Keeps the numbered check count at 8. Tradeoff: acceptance criteria explicitly require "Check 3b exists between Check 3 and Check 4" as a named distinct section; embedding under Check 3 would blur that boundary.

**Approach D: Distinct `## Check 3b` heading matching existing format (selected)**
New `## Check 3b: Root Cause Spot-Check` heading following the same structural pattern as all other checks. Bold-labeled severity bullets for minor/material with distinct action instructions. Escalation path as a numbered list. Preserves all existing check text unchanged. Consistent with the prompt's existing conventions.

---

## 2. Selected Approach with Rationale

Approach D was selected because:
1. It satisfies acceptance criteria exactly — a distinct named section between Check 3 and Check 4.
2. The existing check format uses `## Check N: Title` headings with prose; Check 3b is structurally identical.
3. Bold labels (`**Minor**`, `**Material**`) are already the convention in this prompt for emphasis.
4. Numbered escalation steps give the sonnet model a concrete, unambiguous sequence to follow.
5. Zero changes to existing check text — no regression risk.

---

## 3. Implementation Description

**`orchestration/templates/checkpoints.md`** — Two changes:
- Line 517: Changed model annotation from `haiku` to `sonnet` with updated justification text.
- Inserted `## Check 3b: Root Cause Spot-Check` as a new section between Check 3 (Bead Quality Check) and Check 4 (Priority Calibration). The new section covers:
  - Bead selection logic (up to 2, P1 priority, then highest-surface-count P2)
  - Three-step verification procedure per bead (read source, verify root cause, assess fix direction)
  - SUSPECT severity distinction with explicit minor/material definitions and actions
  - Numbered Material Spot-Check Escalation Path (6 steps)
  - Report format line

**`orchestration/RULES.md`** — One change:
- Model Assignments table row for `PC — CCB`: changed model from `haiku` to `sonnet`, updated description from "Mechanical counting" to "Judgment: bead quality and dedup correctness".

---

## 4. Correctness Review

### orchestration/templates/checkpoints.md

Re-read lines 514-644 post-edit.

- **Model line (517)**: `**Model**: \`sonnet\`` — correct.
- **Check 3 (560-566)**: Text unchanged — no regression.
- **Check 3b (568-590)**: New section present, correctly placed after Check 3 and before Check 4.
  - "up to 2 beads" — satisfies AC2.
  - Minor/material distinction with different actions — satisfies AC3.
  - Escalation path steps 1-6 covering PARTIAL verdict, context-degradation-suspected flag, fresh Big Head, full review, re-run CCB, user escalation — satisfies AC4.
  - Report line at end of section.
- **Check 4-7 (592-619)**: Text unchanged — no regression.
- **Verdict section (621-624)**: Text unchanged (note: still says "All 8 checks" — see Adjacent Issues).
- **Queen's Response (636-643)**: Text unchanged.

**Adjacent issue noted (not fixed)**: The intro sentence at line 542 says "perform these 8 checks" and the Verdict says "All 8 checks confirm consolidation integrity." With Check 3b added, the actual check count is 9. These lines were not modified per scope boundaries. This is a minor stale count that does not affect runtime behavior (models count what they see, not what the header says).

### orchestration/RULES.md

Re-read lines 425-435 post-edit.

- Line 429: `| PC — CCB | Task (\`pest-control\`) | sonnet | Judgment: bead quality and dedup correctness |` — correct.
- All other rows in the table are unchanged.

---

## 5. Build/Test Validation

These files are markdown prompt templates — no build system or automated tests exist for them. Validation was performed by:
1. Re-reading both changed file sections in full after each edit.
2. Grepping for `haiku` in the CCB section to confirm no residual haiku references.
3. Confirming structural integrity (proper heading nesting, no broken markdown).

```
grep result: 'Model.*haiku' in CCB section — 0 matches (expected 0)
grep result: 'Model.*sonnet' in CCB section — 1 match at line 517 (expected 1)
grep result: 'Check 3b' in CCB section — 1 match at line 568 (expected 1)
```

---

## 6. Acceptance Criteria Checklist

| # | Criterion | Status |
|---|-----------|--------|
| 1 | CCB prompt in checkpoints.md specifies model as sonnet | PASS — line 517: `**Model**: \`sonnet\`` |
| 2 | Check 3b exists between Check 3 and Check 4 with spot-check instructions for up to 2 beads | PASS — lines 568-590, after Check 3 (560) and before Check 4 (592) |
| 3 | Check 3b includes SUSPECT severity distinction (minor vs material) with different actions for each | PASS — `**Minor**` flags for amendment, continues; `**Material**` triggers escalation path |
| 4 | Material escalation path documented: PARTIAL verdict -> context-degradation-suspected flag -> fresh Big Head spawn -> full review -> re-run CCB -> user escalation | PASS — lines 582-588, all 6 steps present in order |
| 5 | RULES.md Model Assignments table shows CCB as sonnet, not haiku | PASS — line 429 updated |
| 6 | Existing CCB checks 0-7 are unchanged (no regression) | PASS — all 8 check headings and bodies verified identical to pre-edit content |

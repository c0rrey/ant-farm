# Summary: ant-farm-z3j

**Task**: Checkpoint thresholds undefined: small file, sampling N<3, CCB bd list unbounded
**Commit**: `7ee2d0a`
**File changed**: `orchestration/templates/checkpoints.md`

---

## 1. Approaches Considered

**Approach A: Minimal surgical edits (selected)**
Make the smallest possible change at each affected location: update the formula string in two places, add a row to the worked-examples table, correct one row, and scope the bd list command. No restructuring, no new sections.
Tradeoff: Lowest blast radius; each fix is independently verifiable; no risk of breaking adjacent prose.

**Approach B: Consolidate "small file" into a single canonical definition block**
Add a named definition (e.g., "> **Small file**: fewer than 100 lines") at the top of the Verdict Thresholds section and replace all four inline occurrences with "see definition above."
Tradeoff: Better DRY principle for long-term maintenance, but changes more text and disrupts reading flow for agents that read sections in isolation.

**Approach C: Rewrite the DMVDC Check 1 section with a decision tree**
Replace the table with a prose decision tree: "If N < 3, sample = N. Else sample = max(3, min(5, ceil(N/3)))."
Tradeoff: More readable for humans, but departs from the existing table convention and makes the formula harder to verify mechanically.

**Approach D: Add guard prose without changing the formula**
Keep the formula as-is and add a sentence: "If the formula result exceeds N, cap at N."
Tradeoff: Avoids touching the formula but leaves the formula itself inconsistent with what the prose says; auditors may follow the formula rather than the override note.

---

## 2. Selected Approach

**Approach A: Minimal surgical edits.**

Rationale: The task is a precision threshold-definition fix, not a refactoring task. The three issues are isolated: one formula string appears in two places, one table has two incorrect rows, and one CLI command lacks a flag. Surgical edits minimize scope creep risk (per the task scope boundaries) and make the correctness review straightforward — each changed line can be diffed and verified independently.

---

## 3. Implementation Description

Three groups of changes, all in `orchestration/templates/checkpoints.md`:

**Fix 1 — "small file" threshold consistency (acceptance criterion 1)**
- L123: Changed `"small": fewer than 100 lines of code OR fewer than 5 logical sections/functions` to `"small": fewer than 100 lines`. The OR clause created an inconsistency with L87, L158, and L163 which all use `<100 lines` without the OR condition.
- L87, L158, L163 were already correct; no changes needed at those sites.

**Fix 2 — DMVDC sampling formula guard (acceptance criterion 2)**
- L76 (Verdict Thresholds Summary table): Updated formula from `max(3, min(5, ceil(N/3)))` to `min(N, max(3, min(5, ceil(N/3))))`.
- L425 (DMVDC Nitpicker Check 1 prose): Same formula update.
- L427 (plain-English description): Changed "If the report has fewer than 3 findings, verify all of them" to "If N is less than 3, verify all of them (sample size = N)" — makes the cap explicit.
- Worked examples table: Added a 6th column `min(N, ...)` to show the outer min step. Added N=1 row (sample=1). Corrected N=2 row from sample=3 to sample=2, with note "fewer findings than minimum — verify all."

**Fix 3 — CCB Check 7 bead list scoping (acceptance criterion 3)**
- L514: Added `{SESSION_START_DATE}` variable declaration to the CCB prompt header so the Queen knows to supply it.
- L575: Changed `bd list --status=open` to `bd list --status=open --after={SESSION_START_DATE}` and added an inline bullet explaining the variable and why scoping is needed.

---

## 4. Correctness Review

**orchestration/templates/checkpoints.md** — re-read in full after all edits.

- L72/74 (Verdict Thresholds Summary table): `Small file = <100 lines` for CCO and WWD rows — unchanged and correct.
- L76: Formula now reads `min(N, max(3, min(5, ceil(N/3))))` — outer `min(N,...)` guard present. Correct.
- L87: `file <100 lines` — correct, consistent with other sites.
- L123: `"small": fewer than 100 lines` — OR clause removed, now consistent with L87/L158/L163. Correct.
- L128: `file is large (≥100 lines)` — complement is correct and unchanged.
- L158: `small file (<100 lines)` — correct, unchanged.
- L163: `file is small (<100 lines)` — correct, unchanged.
- L425: Formula `min(N, max(3, min(5, ceil(N/3))))` — consistent with L76. Correct.
- L427: Plain-English updated to match formula behavior for N<3. Correct.
- L431 (table header): Added `min(N, ...)` column. Correct.
- L433 (N=1 row): `ceil(1/3)=1, min(5,1)=1, max(3,1)=3, min(1,3)=1` → sample=1. Math verified. Correct.
- L434 (N=2 row): `ceil(2/3)=1, min(5,1)=1, max(3,1)=3, min(2,3)=2` → sample=2. Math verified. Correct.
- L435-L439 (N=6,9,12,15,30): All existing rows updated for new column; sample sizes unchanged and correct.
- L514: `{SESSION_START_DATE}` variable added to CCB prompt header. Correct.
- L575: `bd list --status=open --after={SESSION_START_DATE}` — scoped command with inline explanation. Correct.

No unintended changes detected. All prose surrounding the edits is intact.

---

## 5. Build/Test Validation

No build or test infrastructure applies to markdown orchestration templates. Correctness validated by:
- Manual math verification of all worked-example table rows against the corrected formula.
- Grep to confirm no other instances of the old formula remain in the file.
- `git diff` review confirming only `checkpoints.md` was modified.
- `git show` confirming 17 insertions, 14 deletions — consistent with the three targeted changes.

---

## 6. Acceptance Criteria Checklist

| # | Criterion | Status |
|---|---|---|
| 1 | Define "small file" = fewer than 100 lines at every usage site in checkpoints.md (L87, L121-128, L158, L163) | PASS — All four sites now read `<100 lines` or `fewer than 100 lines`; OR clause removed from L123 to achieve consistency |
| 2 | Fix sampling formula to `min(N, max(3, min(5, ceil(N/3))))` at L76 and L424, and update worked-examples table (N=1 yields 1, N=2 yields 2) | PASS — Formula updated at both sites; table corrected with N=1 row (sample=1) and N=2 row (sample=2) |
| 3 | Scope CCB Check 7 bead list to session-start date (e.g., `bd list --status=open --after=<session-start-date>`) | PASS — Command updated to `bd list --status=open --after={SESSION_START_DATE}`; variable added to CCB prompt header |

---

## Adjacent Issues Found

None observed. All three issues were contained to the locations specified in the task brief. No other threshold inconsistencies or formula errors were noticed while reading the file.

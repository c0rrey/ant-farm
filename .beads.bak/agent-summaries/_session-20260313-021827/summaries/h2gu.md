# Task Summary: ant-farm-h2gu — Migrate checkpoints.md (semantic)

**Commit**: 15fe938
**File changed**: `orchestration/templates/checkpoints.md`

---

## 1. Approaches Considered

**Approach A — Global word-boundary sed replacement**
Replace every `\bbd\b` with `crumb` in a single pass using sed or a scripted tool. Simple to execute and guarantees zero remaining `bd` matches. Risk: indiscriminate replacement could corrupt unintended matches if `bd` appeared in non-command prose with a different meaning.

**Approach B — Line-targeted edits from task spec**
Edit only the exact line numbers cited in the task brief (L157, L294, L311, etc.) one by one. Maximally surgical; eliminates any risk of touching unrelated content. Risk: tedious and error-prone if any cited line number shifts due to earlier edits.

**Approach C — Backtick-scoped replacement only**
Replace `bd` only where it appears inside backtick code spans (`` `bd ...` ``). Leaves section headings and prose untouched. Risk: the acceptance criterion requires `grep -c '\bbd\b'` = 0, and prose occurrences like "bd show Failure Handling" and "used to scope bd list" would remain, causing the grep check to fail.

**Approach D — Grep-driven targeted edits with semantic ESV flag change (selected)**
Use grep to enumerate every `\bbd\b` occurrence with context, then apply targeted Edit tool calls for each distinct block. Handle the ESV/CCB `--after` semantic change explicitly by replacing `--status=open --after={date}` with `--open --after {date}`. Verify with grep afterward. This approach is precise, auditable, and isolates the semantic flag change from the mechanical `bd -> crumb` substitutions.

---

## 2. Selected Approach with Rationale

**Selected: Approach D.**

Approach D was chosen because it combines correctness with auditability. By enumerating occurrences first via grep, each edit could be reviewed in context before being applied — preventing accidental changes to unrelated content. The ESV/CCB `--after` semantic change required deliberate handling distinct from the `bd -> crumb` substitution, which a blanket find-and-replace (Approach A) would have missed. Approach C was disqualified because the acceptance criterion requires a full zero-match grep, including prose.

---

## 3. Implementation Description

Reviewed all `\bbd\b` occurrences across checkpoints.md (18 match locations across 6 checkpoint definitions). Applied 11 targeted edits covering:

- **SSV checkpoint** (Check 2, Check 3): `bd show {TASK_ID}` -> `crumb show {TASK_ID}`; GUARD section headings and error message strings updated; `bd show` failure references updated throughout.
- **CCO checkpoint** (Check 4): `bd create`, `bd update`, `bd close` -> `crumb create`, `crumb update`, `crumb close`; remediation step updated.
- **WWD checkpoint**: Expected files reference updated from `bd show` to `crumb show`.
- **DMVDC checkpoint** (Check 2): `bd show {TASK_ID}` and all GUARD prose updated to `crumb show`.
- **CCB checkpoint** (Check 2, Check 7): `bd show <id>` -> `crumb show <id>`; semantic flag change applied: `bd list --status=open --after={SESSION_START_DATE}` -> `crumb list --open --after {SESSION_START_DATE}`.
- **ESV checkpoint** (L775, Check 3, example verdict): All `bd show` and `bd list` commands updated; both `--status=open --after=` occurrences on L816-L817 updated to `--open --after`; example FAIL verdict on L888 updated; "used to scope bd list" -> "used to scope crumb list".
- **Task prompt check** (L157): `bd show` + `bd update --status=in_progress` -> `crumb show` + `crumb update --status=in_progress`.

No pass/fail logic, verdict thresholds, checkpoint ordering, or verification workflows were altered.

---

## 4. Correctness Review

**File: orchestration/templates/checkpoints.md**

Reviewed all changed locations by re-reading surrounding context after edits:

- L157: `crumb show` + `crumb update --status=in_progress` — correct, matches task step 1 pattern.
- L294: `crumb show {TASK_ID}` in WWD expected-files line — correct.
- L311: `crumb show {TASK_ID}` in WWD PASS verdict — correct.
- L378-385: DMVDC Check 2 fully updated — command, GUARD heading, error strings, and fallback note all reference `crumb show`.
- L478-481: CCO Check 4 fully updated — all three command variants and remediation step updated.
- L556: CCB Check 2 `crumb show <id>` — correct.
- L615: CCB Check 7 `crumb list --open --after {SESSION_START_DATE}` — semantic flag change applied correctly (space before `{date}`, `--open` instead of `--status=open`).
- L681-693: SSV Check 2 fully updated — command, GUARD heading, error strings, skip markers, PASS condition all reference `crumb show`.
- L701, L706: SSV Check 3 command and GUARD reference updated.
- L775: ESV "used to scope crumb list" — correct.
- L806-822: ESV Check 3 fully updated — `crumb show <id>`, GUARD heading, error strings, skip markers, `crumb list --open --after {SESSION_START_DATE}` (both occurrences), discrepancy report strings, PASS condition all updated.
- L888: ESV example FAIL verdict `crumb show` — correct.

Verification logic (verdict thresholds, PASS/FAIL conditions, check numbering, section structure) confirmed unchanged.

---

## 5. Build/Test Validation

```
$ grep -c '\bbd\b' orchestration/templates/checkpoints.md
0
```

Zero remaining `bd` word-boundary matches confirmed.

---

## 6. Acceptance Criteria Checklist

| Criterion | Status |
|---|---|
| All 6 checkpoint definitions (SSV, CCO, WWD, DMVDC, CCB, ESV) have bd -> crumb command updates | PASS |
| ESV --after flag updated: `bd list --status=open --after={date}` -> `crumb list --open --after {date}` | PASS — applied to both ESV Check 3 occurrences (L816, L817) and CCB Check 7 (L615) |
| Checkpoint verification logic (pass/fail criteria) remains unchanged | PASS — verdict thresholds, PASS/FAIL conditions, and check structure are unmodified |
| `grep -c '\bbd\b' orchestration/templates/checkpoints.md` returns 0 | PASS — confirmed 0 |
| All command examples in checkpoints reflect valid crumb CLI syntax | PASS — all commands use `crumb show`, `crumb update`, `crumb list --open --after`, `crumb create`, `crumb close` |

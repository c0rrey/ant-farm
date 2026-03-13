# Report: Correctness Review (Round 2)

**Scope**: Fix commits only — `7ee2d0a..HEAD` (5 commits)
**Reviewer**: Correctness Review (Round 2) — nitpicker agent
**Review round**: 2 — scope limited to fix commits; out-of-scope findings only reportable if they cause runtime failure or silently wrong results

**AMENDED**: Finding 1 severity upgraded from P3 to P2 following cross-review message from edge-cases-r2 that identified the actual failure mode. Original assessment incorrectly concluded the Pantry would remove guard lines for round 2+; the `<IF ROUND 1>` markers are not present around the guard's `for _path` loop.

## Fix Commits Reviewed

| Commit | Task | Description |
|--------|------|-------------|
| `04c96f5` | ant-farm-4bna | Move scrub-pii.sh check inside staged-file guard |
| `9843978` | ant-farm-yjrj | Scope PII scrub regex to owner/created_by fields only |
| `43bdeca` | ant-farm-l3d5 | Add placeholder substitution validation guards |
| `d4aa294` | ant-farm-88zh | Register {REVIEW_TIMESTAMP} in placeholder conventions |
| `4643816` | ant-farm-2gde | Replace dead GLOSSARY.md links with inline wave definition |

---

## Findings Catalog

### Finding 1: Placeholder guard's `for _path` loop in reviews.md will false-positive abort Big Head in every round 2+ session

- **File(s)**: `orchestration/templates/reviews.md:520-537`
- **Severity**: P2
- **Category**: correctness
- **Description**: The placeholder substitution guard added by ant-farm-l3d5 (lines 520-537) iterates over all 4 report paths — including `clarity-review-<timestamp>.md` and `excellence-review-<timestamp>.md` at lines 523-524. The `case` pattern `*'<'*|*'>'*` fires on any path containing angle brackets. The `<IF ROUND 1>` conditional markers exist only in the while-loop body (lines 553-556), **not** around the guard's `for _path` loop. In round 2+, the Pantry omits the `<IF ROUND 1>` block from the while loop per the "Pantry responsibility" note (line 572), but has no instruction to remove lines 523-524 from the guard. Those lines will remain with the literal template strings `<session-dir>/review-reports/clarity-review-<timestamp>.md` and `<session-dir>/review-reports/excellence-review-<timestamp>.md`, which contain `<` and `>` characters. The guard detects them, sets `PLACEHOLDER_ERROR=1`, and calls `exit 1` — aborting Big Head before any consolidation work begins. This will block the round 2+ review termination path on every session.
- **Suggested fix**: Add `<IF ROUND 1>` markers around lines 523-524 of the guard's `for _path` loop, mirroring the existing markers in the while loop:
  ```bash
  PLACEHOLDER_ERROR=0
  for _path in \
    "<session-dir>/review-reports/correctness-review-<timestamp>.md" \
    "<session-dir>/review-reports/edge-cases-review-<timestamp>.md" \
  # <IF ROUND 1>
    "<session-dir>/review-reports/clarity-review-<timestamp>.md" \
    "<session-dir>/review-reports/excellence-review-<timestamp>.md" \
  # </IF ROUND 1>
    ; do
  ```
  And update the "Pantry responsibility" note to explicitly say the Pantry removes these lines (both in the guard and the while loop) for round 2+. Alternatively, the Pantry could substitute all 4 paths with real values in the guard in round 2+ (paths that will never exist) — but that would cause a different confusing failure. The cleanest fix is consistent `<IF ROUND 1>` markers in both locations.
- **Cross-reference**: Raised by edge-cases-r2 as a boundary-condition issue.

---

## Acceptance Criteria Verification

### ant-farm-4bna: Pre-commit hook blocks ALL commits when scrub-pii.sh is missing

**AC (from bd show)**: Move the executable check inside the staged-file guard; update installation-guide.md:47 to document blocking behavior.

**Criterion 1 — check moved inside staged-file guard:**
`scripts/install-hooks.sh` (the hook template embedded in the script):
- Before fix: `if [[ ! -x "$SCRUB_SCRIPT" ]]; then ... exit 1; fi` appeared at lines 71-77, BEFORE the `if git diff --cached` staged-file guard.
- After fix: The executable check now appears inside the `if git diff --cached` block (lines 76-79 of the installed hook).
- **PASS** — fix correctly reorders the checks so the executable check only runs when issues.jsonl is staged.

**Criterion 2 — installation-guide.md:47 updated:**
- Before: "Skips silently if `scrub-pii.sh` is not found or not executable"
- After: "Blocks the commit with an error if `scrub-pii.sh` is not found or not executable (only when `issues.jsonl` is staged)"
- **PASS** — documentation now accurately describes the blocking behavior and its conditional scope.

**Verdict: PASS** — Both acceptance criteria met.

---

### ant-farm-yjrj: scrub-pii.sh regex is overly broad (global replace, not field-scoped)

**AC (from bd show)**: Scope the perl regex to target only owner and created_by field values.

**Criterion 1 — PII_FIELD_PATTERN scoped to owner/created_by fields:**
- Old grep pattern: `'[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}'` — global, matches any email anywhere.
- New grep pattern: `'"(owner|created_by)"\s*:\s*"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}"'` — scoped to field-value context.
- **PASS**

**Criterion 2 — perl substitution regex correctly scoped:**
- Old perl: `s/[a-zA-Z0-9._%+\-]+\@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}/ctc/g` — replaces all email patterns globally.
- New perl: `s/("(?:owner|created_by)"\s*:\s*")[a-zA-Z0-9._%+\-]+\@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}(")/$1ctc$2/g` — replaces only in owner/created_by field values, preserving surrounding structure.
- Verified: `echo '"owner":"test@example.com"'` piped through new perl command produces `"owner":"ctc"` — correct.
- **PASS**

**Criterion 3 — post-scrub residual check also scoped:**
- Both `grep -qE` (existence check) and `grep -cE` (count check) after scrub now use `PII_FIELD_PATTERN` — consistent with the substitution scope.
- **PASS**

**Verdict: PASS** — Regex correctly scoped. No regression: emails in titles/descriptions/URLs are now preserved.

**Note on `\s*` in BSD grep**: BSD grep on macOS supports `\s` in ERE patterns. Verified empirically — the pattern matches correctly with whitespace variants.

---

### ant-farm-l3d5: Template placeholder substitution not validated at consumption point

**AC (from bd show)**: Add placeholder-presence guard at consumption point in reviews.md:519-526 (Big Head polling loop) and checkpoints.md:198-199 (CCO input guard).

**Criterion 1 — reviews.md Big Head polling loop guard:**
- Added at `orchestration/templates/reviews.md:515-537`: a `for _path` loop that checks each expected path for unsubstituted `<`, `>`, `{`, `}` characters before entering the polling loop.
- The guard logic is structurally present and the error messages are specific.
- **PARTIAL PASS** — guard is present but has a logic defect in round 2+ (see Finding 1). The guard will produce false-positive aborts in round 2+ because the `<IF ROUND 1>` scoping markers are absent from the guard's `for _path` path list. The fix is present at the right location but incomplete in its conditional coverage.

**Criterion 2 — checkpoints.md CCO input guard enhanced:**
- Before: Guard checked if `{REVIEW_ROUND}` was "missing, blank, or non-numeric" — but this condition is ambiguous when the literal text `{REVIEW_ROUND}` is passed.
- After: Guard explicitly checks for literal text `{REVIEW_ROUND}` (curly braces present) as a specific substitution-failure signal, plus the original numeric validation. The error message now provides: root cause ("upstream substitution failure"), fix instruction ("fill in REVIEW_ROUND as a plain integer"), and the actual value received.
- **PASS**

**Verdict: PARTIAL PASS** — The checkpoints.md CCO guard criterion is fully met. The reviews.md guard criterion is only partially met: the guard exists and handles round 1 correctly, but will falsely abort in every round 2+ session (Finding 1, P2).

---

### ant-farm-88zh: {REVIEW_TIMESTAMP} introduced then removed — AC#4 unmet

**AC (from bd show)**: Re-introduce {REVIEW_TIMESTAMP} in PLACEHOLDER_CONVENTIONS.md and reference in RULES.md Step 3b-i.

**Criterion 1 — {REVIEW_TIMESTAMP} added to PLACEHOLDER_CONVENTIONS.md Tier 1 examples:**
- Added at `orchestration/PLACEHOLDER_CONVENTIONS.md:36`: correct entry with description.
- **PASS**

**Criterion 2 — ${TIMESTAMP} Tier 3 shell variable entry added:**
- Added at `orchestration/PLACEHOLDER_CONVENTIONS.md:88-89`: correct entry linking to `{REVIEW_TIMESTAMP}`.
- **PASS**

**Criterion 3 — RULES.md Step 3b-i updated to cross-reference PLACEHOLDER_CONVENTIONS.md:**
- Added at `orchestration/RULES.md:133-135`: cross-reference to `orchestration/PLACEHOLDER_CONVENTIONS.md` (Tier 1 uppercase), explaining when to use `${TIMESTAMP}` vs `{REVIEW_TIMESTAMP}`.
- **PASS**

**Criterion 4 — Audit table in PLACEHOLDER_CONVENTIONS.md updated:**
- The RULES.md row in the audit table now lists `{REVIEW_TIMESTAMP}` in the Tier 1 column and `${TIMESTAMP}` in the Tier 3 column.
- **PASS**

**Verdict: PASS** — AC#4 of ant-farm-bi3 is now satisfied.

---

### ant-farm-2gde: GLOSSARY.md dead link in checkpoints.md

**AC (from bd show)**: Create GLOSSARY.md with the referenced anchor, or remove the links and define wave inline.

**Chosen approach**: Inline definition — removed dead link and replaced with inline prose definition.

**Before** (`orchestration/templates/checkpoints.md:261-262`):
```
**When**: After agent commits, BEFORE spawning next agent in same wave (see [Glossary: wave](../GLOSSARY.md#workflow-concepts))
```

**After**:
```
**When**: After agent commits, BEFORE spawning next agent in same wave (a "wave" is a group of agents spawned in parallel for the same execution round — e.g. all Nitpickers in round 1 constitute one wave)
```

- Dead link removed: **PASS**
- Inline definition provided: **PASS** — the definition is factually correct and consistent with how "wave" is used throughout RULES.md.
- No other references to `GLOSSARY.md` were introduced.

**Verdict: PASS** — Dead link removed, inline definition is accurate.

---

## Regression Analysis

### Did any fix break something else?

**ant-farm-4bna (pre-commit hook reordering):**
- Hook logic is self-contained. SCRUB_SCRIPT path variable is set at top of hook block — accessible inside the nested conditional. ISSUES_FILE used in `git add "$ISSUES_FILE"` — still in scope.
- **No regression introduced.**

**ant-farm-yjrj (scoped PII regex):**
- Post-scrub residual check uses `PII_FIELD_PATTERN` consistent with substitution scope.
- Behavior change (documented, intentional): emails in description/title fields are no longer scrubbed. This is the fix, not a regression.
- **No regression introduced.**

**ant-farm-l3d5 (placeholder guards):**
- The guard introduced a new defect (Finding 1) that will abort Big Head in round 2+. This is a regression relative to the state before the fix — round 2+ previously had no guard and would proceed (albeit with silent placeholder failures); now it exits early with a false-positive error.
- **Regression introduced in round 2+ path** — see Finding 1.

**ant-farm-88zh (PLACEHOLDER_CONVENTIONS.md + RULES.md):**
- Documentation-only additions. No logic was removed.
- **No regression introduced.**

**ant-farm-2gde (dead link removal):**
- Single-line change in an instruction file. No code paths affected.
- **No regression introduced.**

---

## Preliminary Groupings

### Group A: Pre-commit hook correctness (ant-farm-4bna) — no issues
- All criteria met; fix correctly reorders checks.

### Group B: PII regex scope (ant-farm-yjrj) — no issues
- All criteria met; verified by manual test.

### Group C: Placeholder validation guard incomplete (ant-farm-l3d5) — Finding 1
- Finding 1 (P2): guard for-loop does not have `<IF ROUND 1>` markers, causing false-positive aborts in round 2+.
- Root cause: the fix applied `<IF ROUND 1>` scope only to the while-loop body but not to the guard's path list. Both code blocks share the same round-conditional logic but only one has the markers.

### Group D: Documentation consistency (ant-farm-88zh, ant-farm-2gde) — no issues
- All criteria met.

---

## Summary Statistics

- Total findings: 1
- By severity: P1: 0, P2: 1, P3: 0
- Preliminary groups: 1

---

## Cross-Review Messages

### Sent
- None

### Received
- From edge-cases-r2: "Flagged `orchestration/templates/reviews.md:519-535` — the placeholder guard iterates all 4 paths including round-1-only clarity/excellence paths; in round 2+, Pantry only removes the `<IF ROUND 1>` block from the while loop, leaving angle-bracket paths in the guard that trigger a false-positive exit 1." — Action taken: re-read the template carefully, confirmed the failure mode is real, upgraded Finding 1 from P3 to P2 and updated the verdict for ant-farm-l3d5.

### Deferred Items
- None

---

## Coverage Log

| File | Status | Evidence |
|------|--------|----------|
| `docs/installation-guide.md` | Reviewed — no issues | 1 changed line (L47); text matches new hook behavior |
| `orchestration/PLACEHOLDER_CONVENTIONS.md` | Reviewed — no issues | 3 additions: Tier 1 entry, Tier 3 entry, audit table row update; all consistent |
| `orchestration/RULES.md` | Reviewed — no issues | 4-line addition to Step 3b-i; cross-reference to PLACEHOLDER_CONVENTIONS.md is accurate |
| `orchestration/templates/checkpoints.md` | Reviewed — no issues | 2 changes: expanded CCO input guard text (correct); dead-link-to-inline-definition replacement (correct) |
| `orchestration/templates/reviews.md` | Finding #1 (P2) | 24-line addition of placeholder guard; guard correctly detects unsubstituted paths but lacks round-conditional scoping for clarity/excellence paths, causing false-positive abort in round 2+ |
| `scripts/install-hooks.sh` | Reviewed — no issues | Pre-commit hook template: executable check correctly moved inside staged-file guard |
| `scripts/scrub-pii.sh` | Reviewed — no issues | All 3 regex patterns (check, substitute, residual-check) consistently scoped to owner/created_by fields; verified by manual test |

---

## Overall Assessment

**Score**: 7/10
**Verdict**: PASS WITH ISSUES

Four of five fix tasks (ant-farm-4bna, ant-farm-yjrj, ant-farm-88zh, ant-farm-2gde) are correct and complete. The fifth fix (ant-farm-l3d5) is partially correct: the checkpoints.md CCO guard criterion is fully met, but the reviews.md guard has a P2 defect — missing `<IF ROUND 1>` scoping markers in the guard's `for _path` path list, which will cause a false-positive `exit 1` abort in every round 2+ Big Head consolidation run. The fix must be amended to add those markers (or equivalent Pantry guidance) before round 2+ can complete successfully.

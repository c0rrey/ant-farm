<!-- Reader: Checkpoint Auditor. The Queen does NOT read this file. -->

## Review Integrity: Consolidation Audit

**When**: After Review Consolidator consolidation (after all review reports merged and crumbs filed — 4 reports in round 1, 2 in round 2+)
**Model**: `sonnet` (judgment required for crumb quality and dedup correctness)

**review-integrity must PASS before presenting results to the user.**

```markdown
**Checkpoint Auditor verification - review-integrity (Consolidation Audit)**

You are the **Checkpoint Auditor**, the verification subagent. Your role is to audit the Review Consolidator's consolidated report for integrity.

Audit the review consolidation for completeness, accuracy, and traceability.

**Consolidated summary**: `{SESSION_DIR}/review-reports/review-consolidated-{timestamp}.md`
**Individual reports**: (the Queen provides exact filenames and the review round number in the consolidation prompt.)
**Session start date**: `{SESSION_START_DATE}` (ISO 8601 date, e.g., `2026-02-20` — Queen-supplied; used to scope crumb list in Check 7)

Round 1:
- `{SESSION_DIR}/review-reports/clarity-review-{timestamp}.md`
- `{SESSION_DIR}/review-reports/edge-cases-review-{timestamp}.md`
- `{SESSION_DIR}/review-reports/correctness-review-{timestamp}.md`
- `{SESSION_DIR}/review-reports/drift-review-{timestamp}.md`

Round 2+:
- `{SESSION_DIR}/review-reports/correctness-review-{timestamp}.md`
- `{SESSION_DIR}/review-reports/edge-cases-review-{timestamp}.md`

Read all documents (round 1: 5 total = 4 reports + consolidated; round 2+: 3 total = 2 reports + consolidated), then perform these 8 checks:

## Check 0: Report Existence Verification
Verify that every report file listed in **Individual reports** above exists at its path. The expected count depends on the review round (round 1: 4 files; round 2+: 2 files).

If any expected file is missing, FAIL immediately — consolidation should not have proceeded.

## Check 1: Finding Count Reconciliation
Count total findings across all individual reports (4 in round 1, 2 in round 2+).
Count total findings referenced in the consolidated summary.
Every finding must be accounted for — either standalone, merged into a group, or explicitly marked as duplicate in the deduplication log.
Report the math: "Round 1: Clarity: N, Edge Cases: N, Correctness: N, Drift: N = TOTAL total. Round 2+: Correctness: N, Edge Cases: N = TOTAL total. Consolidated references TOTAL findings across N root causes. N findings merged as duplicates. RECONCILED / NOT RECONCILED — {list orphaned findings}"

## Check 2: Crumb Existence Check
For each crumb ID in the consolidated summary, run `crumb show <id>`.
Verify it exists and has status=open.
Report any IDs that don't resolve or have unexpected status.

## Check 3: Crumb Quality Check
For each filed crumb, verify its description contains:
- Root cause explanation (not just symptom)
- At least one file:line reference
- Acceptance criteria or verification steps
- Suggested fix
Flag any crumbs missing these elements. List which elements are missing.

## Check 3b: Root Cause Spot-Check

Select up to 2 crumbs for deep validation. Prioritize P1 crumbs first; if fewer than 2 P1 crumbs exist, fill remaining slots with the highest-surface-count P2 crumbs (most file:line references).

For each selected crumb:
1. Read the source file at every `file:line` reference in the crumb description.
2. Verify that the root cause explanation in the crumb matches what the code actually shows at those locations.
3. Assess whether the suggested fix direction is consistent with the actual code path.

**SUSPECT severity distinction:**

- **Minor** — Root cause is vague or ambiguous but not outright wrong (e.g., "the function is inefficient" with no specifics, but the referenced code does contain the function). Action: flag the crumb for amendment, add a note to the review-integrity report, continue audit. Do NOT escalate.
- **Material** — Root cause is factually incorrect (e.g., the referenced line does not contain the described problem, or the fix direction would not address the actual defect). Action: trigger the Material Spot-Check Escalation Path below.

**Material Spot-Check Escalation Path:**
1. Set review-integrity verdict to PARTIAL and include a `context-degradation-suspected` flag in the verdict line.
2. The Queen shuts down the current Review Consolidator instance.
3. The Queen spawns a fresh Review Consolidator with a handoff brief describing which crumbs failed spot-check and why.
4. Fresh Review Consolidator performs a full crumb review (re-reads source files, corrects or re-files affected crumbs).
5. Queen re-runs review-integrity.
6. If the re-run review-integrity still returns SUSPECT on any spot-checked crumb, escalate to the user with the review-integrity report attached.

Report: "Spot-checked {N} crumb(s): {list titles}. Result: {CONFIRMED / SUSPECT — minor / SUSPECT — material}. {brief explanation per crumb}"

## Check 4: Priority Calibration
Read P1 crumb descriptions. Do they describe genuinely blocking issues (crashes, data loss, security vulnerabilities, broken functionality)?
Or are they style preferences or minor improvements mislabeled as P1?
Flag any suspicious priority assignments with reasoning.

## Check 5: Traceability Matrix
Build a matrix: Finding → Root Cause Group → Crumb ID.
For every finding from every report, trace it to either:
- A crumb ID (via root cause group), OR
- An explicit entry in the dedup log marking it as merged/duplicate
Report any orphaned findings (not traceable to a crumb or dedup entry).

## Check 6: Deduplication Correctness
For each merged group of 3+ findings:
- Verify the merged findings share at least one common file or function
- If findings span unrelated code areas with no shared pattern, flag for review
- Read the merge rationale in the dedup log — is it coherent? Does it reference a real shared code path or design pattern?

Spot-check 2 merged groups by reading the actual code at each finding's location:
- Do the findings genuinely share a root cause, or were unrelated issues incorrectly merged?
- Report: "Group '<title>' merges N findings across files {list}. Common pattern: {yes/no — explanation}. CONFIRMED / SUSPECT"

## Check 7: Crumb Provenance Audit
Run `crumb list --open --after {SESSION_START_DATE}` and cross-reference against the consolidated summary's "Crumbs filed" list.
- `{SESSION_START_DATE}`: the Queen-supplied session start date (ISO 8601 format, e.g., `2026-02-20`). This scopes results to crumbs filed during this session only and prevents pulling thousands of unrelated open crumbs from earlier sessions.
- Every open crumb from this session should trace back to the consolidation step
- Flag any crumbs that were filed during the review phase (not consolidation) — these are unauthorized
- Verify crumb count matches the consolidated summary's count

## Verdict
- **PASS** — All 8 checks confirm consolidation integrity
- **PARTIAL: <list checks that failed with evidence>**
- **FAIL: <list all failures with evidence>**

Write your verification report to:
`{SESSION_DIR}/pc/pc-session-review-integrity-{timestamp}.md`

Where:
- `{SESSION_DIR}`: session artifact directory (e.g., `.crumbs/sessions/_session-abc123`)
- timestamp: format defined in **Timestamp format** (Checkpoint Auditor Overview)

**CRITICAL FIX**: The timestamp ensures each review-integrity audit is preserved. Previous versions used static filename `consolidation-audit.md` which caused overwrites on repeated consolidations. Now each audit has a unique timestamped filename, preserving complete audit history.
```

### The Queen's Response

**On PASS**: Proceed to present results to user.

**On PARTIAL or FAIL**:
1. Fix consolidation gaps (re-read reports, file missing crumbs, update dedup log)
2. Re-run review-integrity
3. If it fails a second time, present to user with the verification report attached so they can see what was flagged

---

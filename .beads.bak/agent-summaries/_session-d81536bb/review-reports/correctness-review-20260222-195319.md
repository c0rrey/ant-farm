# Report: Correctness Review

**Scope**: orchestration/GLOSSARY.md, orchestration/RULES.md, orchestration/templates/checkpoints.md, orchestration/templates/queen-state.md, orchestration/templates/reviews.md, orchestration/templates/scribe-skeleton.md, orchestration/templates/SESSION_PLAN_TEMPLATE.md, README.md, scripts/parse-progress-log.sh
**Reviewer**: Correctness Review (nitpicker)
**Commit range**: f3c6d7b^..HEAD (5 commits)
**Task IDs**: ant-farm-68di.1, ant-farm-68di.2, ant-farm-68di.3, ant-farm-68di.4, ant-farm-68di.5

---

## Findings Catalog

### Finding 1: RULES.md Step 3c "defer" path still says "document in CHANGELOG" instead of referencing the Scribe

- **File(s)**: `orchestration/RULES.md:287`
- **Severity**: P2
- **Category**: correctness
- **Description**: The "defer" branch of the Step 3c review triage decision tree says `P1/P2 beads stay open; document in CHANGELOG; proceed to Step 4`. With the Scribe workflow introduced by ant-farm-68di.3, the Queen no longer directly documents in CHANGELOG — that is the Scribe's responsibility at Step 5b. The parallel file `orchestration/templates/reviews.md:945` was correctly updated to read `document deferred items for the Scribe (Step 5b CHANGELOG)`, but RULES.md was not updated. A Queen following RULES.md will be confused about whether to write CHANGELOG entries directly or defer to the Scribe.
- **Suggested fix**: Change RULES.md:287 from:
  `- **If "defer"**: P1/P2 beads stay open; document in CHANGELOG; proceed to Step 4`
  to:
  `- **If "defer"**: P1/P2 beads stay open; document deferred items for the Scribe (Step 5b CHANGELOG); proceed to Step 4`
- **Cross-reference**: Reviews.md:945 already has the correct wording; RULES.md:287 is the only location that is stale.
- **AC link**: ant-farm-68di.3 description item 2 says "Update cross-reference text" for Step 5 — the Step 3c "defer" text was not listed in the task description but is equally a stale reference within RULES.md.

---

### Finding 2: RULES.md places scribe-skeleton.md in FORBIDDEN list; acceptance criterion requires it in PERMITTED

- **File(s)**: `orchestration/RULES.md:49` (FORBIDDEN list), `orchestration/RULES.md:36-41` (PERMITTED once-per-phase list)
- **Severity**: P2
- **Category**: correctness
- **Description**: ant-farm-68di.3 explicitly requires (description item 3): "Queen reads scribe-skeleton.md once (add to Queen Read Permissions as 'permitted, once per session')" and (AC item 13): "Queen Read Permissions: Add scribe-skeleton.md to PERMITTED (once per session) list." However, the implementation placed `scribe-skeleton.md` in the **FORBIDDEN** list (RULES.md:49) rather than PERMITTED. The spawn prompt at RULES.md:309 tells the Scribe to read its own instructions (`Read orchestration/templates/scribe-skeleton.md for full instructions`), which means the Scribe — not the Queen — reads it. This is behaviourally consistent with FORBIDDEN (analogous to how scout.md is FORBIDDEN because the Scout reads its own instructions). However, since the AC explicitly mandates placing it in PERMITTED, this is a failed acceptance criterion.

  **Note on interpretation**: The implementation choice (FORBIDDEN) is arguably more architecturally consistent — the Agent reads its own skeleton, not the Queen. The AC requirement (PERMITTED) may have been written before the spawn pattern was finalized. I am reporting this as a P2 correctness finding because the AC explicitly requires PERMITTED and was not satisfied.
- **Suggested fix**: Either (a) move `scribe-skeleton.md` from FORBIDDEN to PERMITTED (once per session) in RULES.md to satisfy the AC as written, or (b) revise the AC to reflect the correct design (FORBIDDEN, Scribe reads its own template).
- **Cross-reference**: The dirt-pusher-skeleton.md is in PERMITTED (RULES.md:37) because the Queen uses it directly to compose spawn prompts; scribe-skeleton.md is analogous to scout.md (FORBIDDEN), not dirt-pusher-skeleton.md.

---

### Finding 3: GLOSSARY.md Checkpoint Acronyms table says "All five checkpoints" but ESV is now a sixth checkpoint

- **File(s)**: `orchestration/GLOSSARY.md:67`, `orchestration/GLOSSARY.md:75`
- **Severity**: P2
- **Category**: correctness
- **Description**: The Checkpoint Acronyms section header at GLOSSARY.md:67 says "All five checkpoints are executed by Pest Control." The Ant Metaphor Roles table at GLOSSARY.md:86 says Pest Control "Runs all five checkpoints (SSV, CCO, WWD, DMVDC, CCB)." With ESV added as a sixth checkpoint in this session (via ant-farm-68di.2), these statements are now incorrect. ESV does not appear in the Checkpoint Acronyms table, and the count "five" is stale. The ESV definition was correctly added to the Workflow Concepts table (GLOSSARY.md:61), but it was not added to the Checkpoint Acronyms table.

  The 68di.5 task description explicitly lists GLOSSARY.md as requiring updates for "Scribe, ESV, and exec summary definitions," and the AC says "GLOSSARY.md contains definitions for Scribe, ESV, and exec summary." The definitions were added (Workflow Concepts table) but the Checkpoint Acronyms table was not updated.
- **Suggested fix**:
  1. Update GLOSSARY.md:67 to say "All six checkpoints are executed by Pest Control."
  2. Add an ESV row to the Checkpoint Acronyms table.
  3. Update GLOSSARY.md:86 (Pest Control role) to say "Runs all six checkpoints (SSV, CCO, WWD, DMVDC, CCB, ESV)."
- **AC link**: ant-farm-68di.5 AC says "GLOSSARY.md contains definitions for Scribe, ESV, and exec summary." The ESV definition exists only in Workflow Concepts; the Checkpoint Acronyms table (which is specifically for checkpoint definitions) was not updated.

---

### Finding 4: GLOSSARY.md Ant Metaphor Roles table is missing a Scribe row

- **File(s)**: `orchestration/GLOSSARY.md:82-90` (Ant Metaphor Roles table)
- **Severity**: P3
- **Category**: correctness
- **Description**: The Ant Metaphor Roles table lists all agent roles (Queen, Scout, Pantry, Pest Control, Dirt Pusher, Nitpicker, Big Head) but does not include the Scribe. The Scribe was added to the Workflow Concepts table (GLOSSARY.md:59) and is now an integral part of the workflow (Step 5b). The RULES.md Agent Types table (RULES.md:382) and Model Assignments table (RULES.md:403) were correctly updated to include the Scribe, making the Ant Metaphor Roles table inconsistent.
- **Suggested fix**: Add a Scribe row to the Ant Metaphor Roles table (after Big Head, before or after the end of the table):
  `| **Scribe** | _(spawned via Task tool with subagent_type `general-purpose`)_ | sonnet | Session documentation agent. Reads all session artifacts and commit history, writes exec-summary.md and prepends CHANGELOG entry. Spawned once per session at Step 5b. |`
- **Cross-reference**: This could be reported to Drift reviewer as a stale cross-file reference — the Ant Metaphor Roles table should be consistent with RULES.md Agent Types table. Reporting here as a correctness gap since the table is meant to be comprehensive.

---

### Finding 5: README.md Hard Gates table missing ESV row

- **File(s)**: `README.md:264-272`
- **Severity**: P2
- **Category**: correctness
- **Description**: The README.md hard gates table lists five gates (SSV, CCO, WWD, DMVDC, CCB) but does not include ESV. The Step 5c narrative section (README.md:241-243) correctly describes ESV as "a hard gate that must PASS before Step 6." However, the hard gates reference table does not include ESV, making the table incomplete and potentially misleading to users reading the documentation.

  The RULES.md hard gates table (RULES.md:355-358) was correctly updated to include ESV (ant-farm-68di.3 AC confirmed). The README was updated by ant-farm-68di.5 to add Step 5b and 5c narrative sections, but the hard gates table was not updated.
- **Suggested fix**: Add an ESV row to README.md hard gates table after CCB:
  `| **ESV** — exec summary verification | Git push | haiku |`
- **AC link**: ant-farm-68di.5 AC says "README.md workflow description reflects the new Step 4 (no CHANGELOG) → Step 5b (Scribe) → Step 5c (ESV) → Step 6 (push) sequence" — the narrative is correct but the hard gates table, which is part of the README documentation of the system, was not updated.

---

### Finding 6: parse-progress-log.sh DOCS_COMMITTED resume_action still mentions CHANGELOG

- **File(s)**: `scripts/parse-progress-log.sh:104`
- **Severity**: P3
- **Category**: correctness
- **Description**: The `step_resume_action` for `DOCS_COMMITTED` says: `Re-run DOCS_COMMITTED: update CHANGELOG, README, CLAUDE.md in a single commit.` With the Scribe now owning CHANGELOG authoring (Step 5b), the resume action for DOCS_COMMITTED is stale — CHANGELOG should no longer be listed as part of the DOCS_COMMITTED step. A Queen reading this resume instruction would be directed to update CHANGELOG in Step 4, which contradicts the new workflow.

  Similarly, `step_label` for DOCS_COMMITTED at parse-progress-log.sh:86 says `Docs Committed: Documentation (CHANGELOG/README/CLAUDE.md)` — CHANGELOG should be removed from this label.

  Additionally, `step_resume_action` for XREF_VERIFIED at parse-progress-log.sh:105 says `verify cross-references and CHANGELOG entries for all tasks` — CHANGELOG entries are now authored by the Scribe at Step 5b and should not be verified as part of XREF_VERIFIED.
- **Suggested fix**:
  1. Update parse-progress-log.sh:86: change `Documentation (CHANGELOG/README/CLAUDE.md)` to `Documentation (README/CLAUDE.md)`
  2. Update parse-progress-log.sh:104: change `update CHANGELOG, README, CLAUDE.md` to `update README and CLAUDE.md`
  3. Update parse-progress-log.sh:105: change `verify cross-references and CHANGELOG entries for all tasks` to `verify cross-references and tasks accounted for`
- **AC link**: ant-farm-68di.4 AC says "A progress.log containing XREF_VERIFIED but missing SCRIBE_COMPLETE produces a resume plan that says to resume at Step 5b (Scribe)." The step ordering is correct, but the stale CHANGELOG references in DOCS_COMMITTED and XREF_VERIFIED resume actions could mislead a recovering session.

---

## Preliminary Groupings

### Group A: Stale "CHANGELOG at Step 4" references — three locations updated inconsistently
- Finding 1 (RULES.md:287 defer path)
- Finding 6 (parse-progress-log.sh DOCS_COMMITTED/XREF_VERIFIED resume actions)
- **Root cause**: The migration of CHANGELOG authoring from Step 4/Queen to Step 5b/Scribe was applied to the primary text of most documents but missed some in-text descriptions that describe what each step does. The reviews.md:945 was correctly updated but its parallel in RULES.md was not. The parse-progress-log.sh step labels were not updated to reflect the changed scope of DOCS_COMMITTED.
- **Suggested combined fix**: Audit all references to DOCS_COMMITTED and Step 4 in orchestration docs and scripts; remove CHANGELOG from any description that is not already noting that Scribe owns it.

### Group B: ESV missing from GLOSSARY.md Checkpoint Acronyms table and README hard gates table
- Finding 3 (GLOSSARY.md Checkpoint Acronyms "five checkpoints" + missing ESV row)
- Finding 5 (README hard gates table missing ESV row)
- **Root cause**: The ESV checkpoint was added to RULES.md hard gates and GLOSSARY.md Workflow Concepts correctly. However, two secondary tables that enumerate checkpoints were not updated: the GLOSSARY.md Checkpoint Acronyms table (the canonical reference for checkpoint acronyms) and the README.md hard gates summary table.
- **Suggested combined fix**: Add ESV to both tables and update the "five checkpoints" count in GLOSSARY.md to "six checkpoints."

### Group C: scribe-skeleton.md permission placement
- Finding 2 (RULES.md places scribe-skeleton.md in FORBIDDEN vs AC requirement of PERMITTED)
- **Root cause**: A design decision (Scribe reads its own template vs Queen reads it) was not resolved before the task was written. The AC mandates PERMITTED; the implementation chose FORBIDDEN.

### Group D: GLOSSARY.md Ant Metaphor Roles table missing Scribe (standalone)
- Finding 4 (Scribe missing from Ant Metaphor Roles table)
- **Root cause**: The Scribe role was added to Workflow Concepts and RULES.md tables but not to the Ant Metaphor Roles table.

---

## Summary Statistics
- Total findings: 6
- By severity: P1: 0, P2: 4, P3: 2
- Preliminary groups: 4

---

## Cross-Review Messages

### Sent
- To Drift reviewer: "Stale 'five checkpoints' count in GLOSSARY.md:67 and GLOSSARY.md:86 after ESV added as sixth — may want to confirm this is drift rather than correctness." (Reporting here as correctness since it directly touches an unmet AC.)
- To Edge Cases reviewer (response): "Confirmed git range boundary issue at checkpoints.md:L767 is real but belongs in Edge Cases report, not Correctness. SESSION_START_COMMIT is the first session commit, so `..` semantics exclude it. Not an AC failure for 68di.2 (AC doesn't specify range inclusion semantics). Directed them to own it."

### Received
- From Drift reviewer: "Already covered — Findings 1, 2, 3 address stale 'five checkpoints' count at GLOSSARY.md:L46, L56, L67; missing ESV row in Checkpoint Acronyms table (L69-L75); stale Pest Control description at L86. Owned as drift findings P2, P2, P3." Action taken: Finding #3 in this report (GLOSSARY.md Checkpoint Acronyms) is now jointly tracked — Drift owns the stale-count drift angle; I retain it as an unmet AC finding (68di.5 AC requires GLOSSARY.md definitions). Big Head will deduplicate.
- From Edge Cases reviewer: "Found potential correctness issue at checkpoints.md:L765 — git log range may exclude SESSION_START_COMMIT (first session commit)." Action taken: Verified and redirected to Edge Cases as a boundary condition issue; not added to this report.

### Deferred Items
- GLOSSARY.md stale checkpoint count (Finding #3) — also covered by Drift reviewer as drift findings. Big Head to deduplicate and file under one root cause.

---

## Coverage Log

| File | Status | Evidence |
|------|--------|----------|
| `orchestration/GLOSSARY.md` | Findings: #3, #4 | Reviewed all 3 sections (Naming Conventions, Workflow Concepts, Checkpoint Acronyms, Ant Metaphor Roles). Workflow Concepts table: 14 entries examined. Checkpoint Acronyms table: 5 rows examined. Ant Metaphor Roles table: 7 rows examined. ESV missing from Checkpoint Acronyms; Scribe missing from Ant Metaphor Roles; count "five checkpoints" stale. |
| `orchestration/RULES.md` | Findings: #1, #2 | Reviewed all workflow steps (0–6), Queen Read Permissions (PERMITTED/FORBIDDEN), Hard Gates table, Agent Types table, Model Assignments table, Concurrency Rules, Session Directory section, Template Lookup table, Retry Limits table. All AC for 68di.3 verified except two issues: RULES.md:287 defer path stale, scribe-skeleton.md in FORBIDDEN vs AC requirement of PERMITTED. |
| `orchestration/templates/checkpoints.md` | Reviewed — no issues | All 6 checkpoint sections examined (CCO Dirt Pushers, CCO Nitpickers, WWD, DMVDC Dirt Pushers, DMVDC Nitpickers, CCB, SSV, ESV). ESV section complete with all 6 checks, bd show guard on Check 3, per-check verdict format, artifact path. All AC for 68di.2 satisfied. |
| `orchestration/templates/queen-state.md` | Reviewed — no issues | Reviewed all sections: Scout, Agent Registry, Pantry, Pest Control, Review Rounds, Scribe and ESV. Scribe and ESV tracking fields correctly added (scribe_status, scribe_retry, exec_summary_path, esv_status, esv_artifact, esv_escalated). Source of Truth section intact. AC for 68di.5 (queen-state.md tracking fields) satisfied. |
| `orchestration/templates/reviews.md` | Reviewed — no issues | Reviewed Termination Rule, Defer path (line 945), Handle P3 Issues section (line 1034), documentation references. All four updated lines correctly reference "Step 5b" and Scribe for CHANGELOG. No "Step 4 CHANGELOG" matches remain. AC for 68di.5 (reviews.md) satisfied. |
| `orchestration/templates/scribe-skeleton.md` | Reviewed — no issues | Verified: Step 0 pattern present (line 30), all 7 input sources (briefing.md, summaries/*.md, review-consolidated-*.md, progress.log, git diff --stat, git log --oneline, bd show), 5 required exec-summary sections (At a Glance, Work Completed, Review Findings, Open Issues, Observations), CHANGELOG derivation rules (include/omit sections), duration calculation instruction (progress.log first/last timestamps), CHANGELOG format reference matching CHANGELOG.md convention. No TODOs or placeholder text remain. All AC for 68di.1 satisfied. |
| `orchestration/templates/SESSION_PLAN_TEMPLATE.md` | Reviewed — no issues | Reviewed Documentation Plan section (line 235-254) and Pre-Push Verification checklist (line 277-292). CHANGELOG items correctly note Scribe authorship. "If zero P1 and zero P2 findings" text updated (line 219-220). All AC for 68di.5 (SESSION_PLAN_TEMPLATE.md) satisfied. |
| `README.md` | Findings: #5 | Reviewed all workflow step descriptions (Step 0–6), Hard Gates table (line 264-272), Custom Agents table, File Reference table. Step 5b and 5c narrative sections correctly added. Hard Gates table missing ESV row. AC for 68di.5 (README.md workflow description) partially satisfied — narrative correct, table incomplete. |
| `scripts/parse-progress-log.sh` | Findings: #6 | Reviewed STEP_KEYS array (lines 62-75), step_label function (lines 77-93), step_resume_action function (lines 95-111), parse loop (lines 174-191), resume plan generation (lines 234-300). SCRIBE_COMPLETE and ESV_PASS correctly added in both STEP_KEYS and handler functions. Stale CHANGELOG references in DOCS_COMMITTED label/action and XREF_VERIFIED action. AC for 68di.4 (step ordering) satisfied; resume action text is stale. |

---

## Overall Assessment
**Score**: 7/10
**Verdict**: PASS WITH ISSUES

The implementation correctly delivers the core Scribe/ESV workflow across all five tasks. All acceptance criteria for 68di.1 (scribe-skeleton.md), 68di.2 (checkpoints.md ESV section), and 68di.4 (parse-progress-log.sh step ordering) are fully satisfied. The principal correctness concerns are: (1) RULES.md:287 contains a stale "document in CHANGELOG" instruction in the defer path (contradicts the Scribe-owns-CHANGELOG principle now established at Step 5b); (2) ESV is missing from the GLOSSARY.md Checkpoint Acronyms table and the README hard gates summary table, leaving both tables inaccurate; (3) The scribe-skeleton.md permission placement contradicts the written acceptance criterion. None of these findings would cause a runtime failure on first use, but they create navigational confusion and false documentation — a Queen following RULES.md:287 would be told to document in CHANGELOG directly, contradicting the rest of the workflow.

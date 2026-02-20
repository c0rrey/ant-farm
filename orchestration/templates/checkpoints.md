<!-- Reader: Pest Control. The Queen does NOT read this file. -->
# Verification Checkpoints

**Term definitions (canonical across all orchestration templates):**

For detailed extraction rules and examples, see `~/.claude/orchestration/reference/dependency-analysis.md` (Term Definitions section).

- `{TASK_ID}` — full bead ID including project prefix (e.g., `ant-farm-9oa` or `my-project-74g.1`)
- `{TASK_SUFFIX}` — suffix portion only; extracted by splitting on the LAST hyphen (e.g., `9oa` from `ant-farm-9oa`, or `74g1` from `my-project-74g.1`)
- `{SESSION_DIR}` — session artifact directory path (e.g., `.beads/agent-summaries/_session-abc123`)

## Pest Control Overview

All checkpoint verifications (CCO, WWD, DMVDC, CCB) are executed by **Pest Control**, a dedicated verification subagent that cross-checks orchestrator and agent work against ground truth.

**Pest Control responsibilities:**
- Pre-spawn prompt audits (CCO)
- Post-commit scope verification (WWD)
- Post-completion substance verification (DMVDC)
- Consolidation integrity audits (CCB)

**Artifact naming conventions:**
- **Task-specific checkpoints (CCO, WWD, DMVDC for Dirt Pushers):** `pc-{TASK_SUFFIX}-{checkpoint}-{timestamp}.md`
  - Example: `pc-74g1-cco-20260215-001145.md`
  - Example: `pc-74g1-dmvdc-20260215-003422.md`
- **Session-wide checkpoints (CCO-review, CCB):** `pc-session-{checkpoint}-{timestamp}.md`
  - Example: `pc-session-cco-review-20260215-001145.md`
  - Example: `pc-session-ccb-20260215-010520.md`

All checkpoints write to `{SESSION_DIR}/pc/`.

**Task suffix derivation:** See `~/.claude/orchestration/reference/dependency-analysis.md` (Term Definitions section) for extraction algorithm. Example: `74g1` from `hs_website-74g.1`.

**Timestamp format:** `YYYYMMDD-HHmmss` (UTC)

**Directory creation**: the Queen creates `{SESSION_DIR}/pc/` at session start (Step 0 in RULES.md). Agents and Pest Control can write immediately without creating directories.

**The Queen's responsibility**: the Queen MUST include `**Summary output path**` in Dirt Pusher prompt context. For review prompts, include the session-scoped review report paths and all participating epic IDs (for context). Reviewers write to `{SESSION_DIR}/review-reports/`, not per-epic directories.

**Review timestamp convention**: the Queen generates a single timestamp per review cycle (format defined in **Timestamp format** above) and passes the exact output filenames to each reviewer and Big Head. This prevents reviewers from independently generating different timestamps.

---

## Verdict Thresholds Summary

This section provides a unified reference for all checkpoint verdict definitions and tie-breaking rules.

### Common Verdict Definitions

All checkpoints use the following verdict states:

**PASS**: Verification succeeded. No action required. Proceed to next phase.

**WARN** (checkpoints: CCO, WWD only):
- CCO WARN: Small file exception approved. Queen reviews and approves before spawn.
- WWD WARN: Legitimate extra files. Soft gate — does not block queue. Queen approves concurrently.

**PARTIAL** (DMVDC and CCB only): Some checks failed. Agent can repair and resubmit, or consolidation can be amended. Does not escalate to user.

**FAIL**: Verification failed. Blocking issue detected. Pause and remediate before continuing.

### Checkpoint-Specific Thresholds

| Checkpoint | Quantitative Threshold | Tie-Breaking Rule | Queue Blocking |
|---|---|---|---|
| **CCO (Dirt Pushers)** | Small file = <100 lines | First-listed section/function | WARN does not block; Queen approves before spawn |
| **CCO (Nitpickers)** | All round-active prompts identical file list (round 1: 4; round 2+: 2) | (No tie-breaking) | FAIL blocks spawn |
| **WWD** | Small file = <100 lines | First-listed changed file | WARN does not block queue; FAIL blocks queue |
| **DMVDC (Dirt Pushers)** | Pick 2 criteria: first-listed OR identified-as-critical OR all if <2 | First-listed acceptance criterion | PARTIAL allows resubmission; FAIL escalates |
| **DMVDC (Nitpickers)** | Sample size = max(3, min(5, ceil(N/3))) | Include highest-severity + all tiers | PARTIAL allows resubmission; FAIL escalates |
| **CCB** | Finding count must reconcile to 100% | Earliest-filed bead per root cause | PARTIAL: fix and re-run; FAIL blocks user presentation |

### Details by Checkpoint

**CCO Verdict Specifics:**
- PASS: All 7 checks pass
- WARN: Check 7 is WARN (file-level scope) + file <100 lines + prompt has context. Acceptable.
- FAIL: Any check fails, or Check 7 is WARN + file ≥100 lines

**WWD Verdict Specifics:**
- PASS: All changed files in expected scope
- WARN: Extra files changed that are legitimate build artifacts (require Queen approval but don't block queue)
- FAIL: Scope creep (files outside task scope). Blocks queue pending investigation.

**DMVDC Verdict Specifics:**
- PASS: All 4 checks confirm (Check 1: git diff matches claims, Check 2: 2 criteria verified, Check 3: approaches distinct, Check 4: correctness evidence specific)
- PARTIAL: Some checks fail (agent can resubmit)
- FAIL: Multiple checks fail or critical fabrication (escalate to user)

**CCB Verdict Specifics:**
- PASS: All 8 checks confirm (finding reconciliation, bead quality, priority calibration, traceability, dedup correctness, provenance)
- PARTIAL: Some checks fail (fix and re-run)
- FAIL: Critical failures (e.g., missing reports, orphaned findings). Must resolve before presenting to user.

---

## Colony Cartography Office (CCO): Pre-Spawn Prompt Audit

### Dirt Pushers

**When**: After orchestrator composes agent prompt(s), BEFORE spawning
**Model**: `haiku` (mechanical checklist — cheap, fast)
**Agent type**: `code-reviewer`

**Why**: The orchestrator has a self-policing checklist, but nobody audits the orchestrator. Catching prompt defects before spawn is 100x cheaper than catching them after.

#### Verdict Thresholds for CCO

**PASS verdict**: All 7 checks pass without exceptions.

**WARN verdict** (acceptable for small files only):
- Check 7 is WARN instead of PASS, AND
- The file in question is "small": fewer than 100 lines of code OR fewer than 5 logical sections/functions, AND
- The prompt includes specific context about what the agent should modify (e.g., "update the error message on line 15")
- Example WARN: "Edit config.json (update API endpoint)" is WARN if config.json is 45 lines. The Queen reviews and approves.
- Example FAIL: "Edit templates/macros/jsonld.html" is FAIL because it provides no line specificity and the file is likely >100 lines. Needs rewrite.

**FAIL verdict**: Any check fails without WARN exception, or Check 7 is WARN but the file is large (≥100 lines) or lacks context.

```markdown
**Pest Control verification - CCO (Pre-Spawn Prompt Audit)**

You are **Pest Control**, the verification subagent. Your role is to audit the composed agent prompt before spawn. See "Pest Control Overview" section above for full conventions.

Audit the following Dirt Pusher prompt for completeness and correctness.
Do NOT execute the prompt — only verify its contents.

<prompt>
{paste the composed agent prompt here}
</prompt>

## Verify each item (PASS or FAIL with evidence):

1. **Real task IDs**: Contains actual task IDs (e.g., `hs_website-abc`), NOT placeholders like `<task-id>` or `<id>`
2. **Real file paths**: Contains actual file paths with line numbers (e.g., `build.py:L200`), NOT placeholders like `<list from bead>` or `<file>`
3. **Root cause text**: Contains a specific root cause description, NOT `<copy from bead>` or similar placeholders
4. **All 6 mandatory steps present**:
   - Step 1: `bd show` + `bd update --status=in_progress`
   - Step 2: "Design at least 4 approaches" (MANDATORY keyword present)
   - Step 3: Implementation instructions
   - Step 4: "Review EVERY file" or per-file correctness review (MANDATORY keyword present)
   - Step 5: Commit with `git pull --rebase`
   - Step 6: Write summary doc to `{SESSION_DIR}/summaries/`
5. **Scope boundaries**: Contains explicit limits on which files to read (not open-ended "explore the codebase")
6. **Commit instructions**: Includes `git pull --rebase` before commit
7. **Line number specificity** (NEW - prevents scope creep): File paths include specific line ranges or section markers
   - ✅ PASS: "Edit templates/macros/jsonld.html lines 23-24 (image property only)"
   - ⚠️ WARN: "Edit templates/macros/jsonld.html (image property)" — file-level scope, acceptable if small file (<100 lines)
   - ❌ FAIL: "Edit templates/macros/jsonld.html" — vague, high scope creep risk

## Verdict
- **PASS** — All 7 checks pass
- **WARN** — Check 7 is WARN but file is small (<100 lines) and has context. Queen reviews and approves before spawn.
- **FAIL** — One or more checks fail, or Check 7 is WARN and file is large (≥100 lines). Rewrite prompt.

Write your verification report to:
`{SESSION_DIR}/pc/pc-{TASK_SUFFIX}-cco-{timestamp}.md`

Where:
- `{TASK_SUFFIX}`: suffix portion of bead ID with no project prefix (e.g., `74g1` from `hs_website-74g.1`)
- `{SESSION_DIR}`: session artifact directory (e.g., `.beads/agent-summaries/_session-abc123`)
- timestamp: format defined in **Timestamp format** (Pest Control Overview)
```

### The Nitpickers

**When**: After composing all review prompts (round 1: 4 prompts; round 2+: 2 prompts), BEFORE creating the team
**Model**: `haiku`
**Agent type**: `code-reviewer`

```markdown
**Pest Control verification - CCO (Pre-Spawn Nitpickers Audit)**

You are **Pest Control**, the verification subagent. Your role is to audit the Nitpickers prompts before spawn.

**Review round**: {REVIEW_ROUND}
Audit the following Nitpicker prompts for completeness and consistency.
Round 1: 4 prompts (clarity, edge-cases, correctness, excellence).
Round 2+: 2 prompts (correctness, edge-cases only).
Do NOT execute the prompts — only verify their contents.

Round 1 — paste all 4 prompts:
<prompt_clarity>
{paste clarity review prompt — round 1 only}
</prompt_clarity>

<prompt_excellence>
{paste excellence review prompt — round 1 only}
</prompt_excellence>

Both rounds — paste these 2 prompts:
<prompt_edge_cases>
{paste edge cases review prompt}
</prompt_edge_cases>

<prompt_correctness>
{paste correctness review prompt}
</prompt_correctness>

## Verify each item (PASS or FAIL with evidence):

1. **File list matches git diff**: the Queen provides the commit range (`<first-commit>..<last-commit>`) in the spawn prompt — use those exact values. This is session-wide, spanning all epics. Run `git diff --name-only <first-commit>..<last-commit>` and verify the prompt file list matches exactly. Every file in the diff must appear in the prompt, and every file in the prompt must appear in the diff. If there is a mismatch, FAIL with the list of missing/extra files.
2. **Same file list**: All prompts contain the same set of files to review (not different subsets)
3. **Same commit range**: All prompts reference the same commit range
4. **Correct focus areas**: Each prompt has focus areas specific to its review type:
   - Clarity: readability, naming, documentation, consistency, structure (round 1 only)
   - Edge Cases: input validation, error handling, boundaries, file ops, concurrency
   - Correctness: acceptance criteria, logic errors, data integrity, regressions, cross-file
   - Excellence: best practices, performance, security, maintainability, architecture (round 1 only)
   (Flag if focus areas are copy-pasted identically across prompts)
5. **No bead filing instruction**: Each prompt contains "Do NOT file beads" or equivalent
6. **Report format reference**: Each prompt specifies the output path `{SESSION_DIR}/review-reports/{type}-review-{timestamp}.md`
7. **Messaging guidelines**: Each prompt includes guidance on when to message other Nitpickers

## Verdict
- **PASS** — All 7 checks pass for all prompts in scope for this round
- **FAIL: <list each failing check, specifying which prompt(s)>**

Write your verification report to:
`{SESSION_DIR}/pc/pc-session-cco-review-{timestamp}.md`

Where:
- `{SESSION_DIR}`: session artifact directory (e.g., `.beads/agent-summaries/_session-abc123`)
- timestamp: format defined in **Timestamp format** (Pest Control Overview)
```

### The Queen's Response

**On PASS**: Proceed to spawn the agent(s) or create the team.

**On FAIL**: Fix the specific gaps in the prompt(s), then re-run CCO. Do NOT spawn until PASS.

---

## Wandering Worker Detection (WWD): Post-Commit Scope Verification

**When**: After agent commits, BEFORE spawning next agent in same wave (see [Glossary: wave](orchestration/GLOSSARY.md#workflow-concepts))
**Model**: `haiku` (mechanical file list comparison — cheap, fast)
**Agent type**: `code-reviewer`

**Why**: Catches scope creep in real-time between agents, before DMVDC runs. Prevents cascading work attribution errors when multiple agents work on related files.

**Known failure mode**: In Wave 1 of Epic 74g, agent 74g.6 (comment task) made functional changes belonging to 74g.7 (foundingDate filter), which cascaded into 74g.7 making changes belonging to 74g.4 (sameAs conditional). WWD would have caught the first scope violation immediately.

```markdown
**Pest Control verification - WWD (Post-Commit Scope Verification)**

You are **Pest Control**, the verification subagent. Your role is to verify agent commits match task scope.

**Task ID**: {TASK_ID}
**Expected files** (from `bd show {TASK_ID}`): {list files from task description}

## Verification Steps

1. Run `git log --oneline -1` to get the latest commit hash
2. Run `git show --stat {commit-hash}` to list files changed
3. Compare changed files to expected files from task description

## Check

**Files changed match expected scope?**
- ✅ All changed files are in the expected list
- ⚠️ Extra files changed (e.g., regenerated HTML from template changes) — check if legitimate
- ❌ Unexpected files changed (e.g., different template, unrelated config)

#### Verdict Thresholds and Queue Blocking Behavior for WWD

**PASS verdict**: All changed files are in the expected scope (from `bd show {TASK_ID}`), or any extra files are clearly legitimate build outputs (e.g., HTML regenerated from template change, CSS compiled from SASS).

**WARN verdict**: Extra files changed that need the Queen's judgment before continuing to the next task in the wave. Does NOT block the queue — only requires Queen review.
- Examples: template changes that cascade into multiple HTML files, configuration changes affecting derived docs
- Queen decision: approve as legitimate build artifact, or escalate to user if suspicious

**FAIL verdict**: Scope creep detected — agent edited files outside the expected scope (different feature, unrelated config, cross-epic work). Indicates a real work attribution problem that needs correction.

## Verdict
- **PASS** — Files match expected scope (or extra files are legitimate build outputs)
- **WARN: <list extra files with rationale>** — Extra files need the Queen's review but do NOT block queue continuation. Queen approves and proceeds, or escalates if suspicious.
- **FAIL: <list unexpected files>** — Agent edited files outside task scope (scope creep detected). Blocks queue progression until documented.

Write your verification report to:
`{SESSION_DIR}/pc/pc-{TASK_SUFFIX}-wwd-{timestamp}.md`
```

### The Queen's Response

**On PASS**: Continue normally (run DMVDC, backfill queue).

**On WARN** (does NOT block queue):
- Review the extra files within 30 seconds of receiving this report
- If legitimate (e.g., HTML rebuild from template, derived artifact), log approval and continue immediately
- If suspicious, escalate to user for decision before spawning next agent in wave
- Queue does NOT pause while Queen reviews — this is a soft gate (concurrent review is acceptable)

**On FAIL (scope creep detected)** (blocks queue progression):
1. Log the violation in queen-state.md immediately
2. Do NOT spawn the next queued agent yet
3. Investigate: check if overlapping work affects queued agents (may need to adjust scope or cancel)
4. Document the violation and decide on next steps (escalate, adjust queue, or retry agent)
5. Once resolved, document for post-mortem analysis

Note: FAIL blocks queue progression because scope creep may invalidate queued tasks' work scope. WARN does not block because legitimate build artifacts don't create dependencies.

---

## Dirt Moved vs Dirt Claimed (DMVDC): Substance Verification

### Dirt Pushers

**When**: After each agent completes
**Model**: `sonnet` (needs judgment to compare claims against actual code)
**Agent type**: `code-reviewer`

**Why sonnet not haiku**: This checkpoint reads actual source code and compares it to report claims. "Is this finding description accurate for what's at build.py:L200?" requires understanding both the code and the claim. Haiku can check format; sonnet can check truth.

```markdown
**Pest Control verification - DMVDC (Substance Verification)**

You are **Pest Control**, the verification subagent. Your role is to cross-check agent claims against ground truth. See "Pest Control Overview" section above for full conventions.

Verify the substance of the Dirt Pusher's work by cross-checking claims against ground truth.

**Summary doc**: `{SESSION_DIR}/summaries/{TASK_SUFFIX}.md`
**Task ID**: {TASK_ID}

Read the summary doc first, then perform these 4 checks:

## Check 1: Git Diff Verification
Run `git log --oneline -5` to identify the agent's commit(s), then run `git diff {before-commit}..{after-commit}` (or `git show {commit}` for single commits).
Compare the actual changes to the summary doc's "Files changed" and "Implementation" sections.
- Do the claimed file changes actually exist in the diff?
- Are there files changed in the diff but NOT listed in the summary?
- Are there files listed in the summary but NOT changed in the diff?

## Check 2: Acceptance Criteria Spot-Check
Run `bd show {TASK_ID}` to get the task's acceptance criteria.

**GUARD: bd show Failure Handling (INFRASTRUCTURE FAILURE)**
If `bd show {TASK_ID}` fails (task not found, unreadable, or bd command error):
- Record the infrastructure failure: "{TASK_ID} — bd show failed: {error details}"
- Write a note in your review report: "Could not retrieve acceptance criteria for {TASK_ID} via `bd show`: {error}. Proceeding with criteria from summary doc only."
- Do NOT abort the review; use the acceptance criteria listed in the agent's summary doc instead
- Clearly mark this fallback in your findings: "[Note: Criteria from summary doc, not from `bd show`]"

**Tie-breaking rule for selecting which criteria to verify** (when multiple criteria exist):
1. Pick the first 2 criteria listed in the acceptance criteria section, OR
2. If the summary doc identifies specific criteria as "critical," pick those 2, OR
3. If fewer than 2 criteria exist, verify all of them

For each selected criterion:
- Read the actual code that should satisfy this criterion
- Verify it's genuinely met (not just marked "PASS" in the summary)
- Quote the specific code that satisfies (or fails to satisfy) each criterion

## Check 3: Approaches Substance Check
Read the 4+ approaches in the summary doc.
- Are they genuinely distinct strategies? (e.g., different algorithms, different data structures, different architectural patterns)
- Or are they trivial variations? (e.g., "use a list" vs "use a tuple", or the same approach with minor cosmetic differences)
- Flag any approaches that are not meaningfully distinct

## Check 4: Correctness Review Evidence
The summary claims "Re-read: yes" for each file.
Pick 1 changed file and read the agent's correctness notes for it.
- Are the notes specific to the actual file content? (e.g., "verified that line 42 handles the None case")
- Or are they generic boilerplate? (e.g., "no issues found, code looks clean")
- Read the actual file and verify the notes are accurate

## Verdict
- **PASS** — All 4 checks confirm substance
- **PARTIAL: <list checks that failed with evidence>** — Some checks failed
- **FAIL: <list all failures with evidence>** — Multiple checks failed or critical fabrication detected

Write your verification report to:
`{SESSION_DIR}/pc/pc-{TASK_SUFFIX}-dmvdc-{timestamp}.md`

Where:
- `{TASK_SUFFIX}`: suffix portion of bead ID with no project prefix (e.g., `74g1` from `hs_website-74g.1`)
- `{SESSION_DIR}`: session artifact directory (e.g., `.beads/agent-summaries/_session-abc123`)
- timestamp: format defined in **Timestamp format** (Pest Control Overview)
```

### Nitpickers

**When**: After each Nitpicker completes its report
**Model**: `sonnet`
**Agent type**: `code-reviewer`

```markdown
**Pest Control verification - DMVDC (Nitpicker Substance Verification)**

You are **Pest Control**, the verification subagent. Your role is to cross-check Nitpicker findings against actual code.

Verify the substance of a Nitpicker's report by cross-checking findings against actual code.

**Report path**: `{SESSION_DIR}/review-reports/{review-type}-review-{timestamp}.md`
**Review type**: {clarity|edge-cases|correctness|excellence}

Read the report first, then perform these 4 checks:

## Check 1: Code Pointer Verification
Pick `max(3, min(5, ceil(N/3)))` random findings from the report (where N = total findings; minimum 3, or all findings if fewer than 3). Always include the highest-severity finding and at least one finding from each severity tier present in the report.
For each finding:
- Read the actual code at the referenced file:line
- Verify the finding description matches what's actually there
- Report: "Finding N claims {file}:L{line} has {description}. Actual code at L{line}: `{actual code}`. CONFIRMED / REFUTED — {explanation}"

## Check 2: Scope Coverage
Compare files listed in the report's "Scope" against both the Findings Catalog AND the Coverage Log.
- Every scoped file MUST appear in either the Findings Catalog (with specific findings) or the Coverage Log (with "Reviewed — no issues" and evidence of review depth)
- If any scoped file appears in NEITHER section, FAIL this check — the file was silently skipped
- For files marked "Reviewed — no issues," verify the evidence is specific (function count, line count) not generic ("looks fine")
- List any files that were skipped without acknowledgment

## Check 3: Finding Specificity
For each finding, check that it is actionable:
- Flag findings that use weasel language: "could be improved", "might cause issues", "may not be ideal", "consider refactoring"
- Every finding needs: what's wrong, where (file:line), and how to fix it
- List any findings that fail the specificity bar

## Check 4: Process Compliance
Search the report for `bd create`, `bd update`, `bd close`, or bead ID patterns (e.g., `hs_website-xxx`).
- Nitpickers must NOT file beads
- If any bead-filing commands or IDs are found, FAIL this check
- If unauthorized bead filing is detected, this is a FAIL (not just a flag). The remediation step is: delete the unauthorized bead (`bd close <id> --reason="unauthorized filing during review"`) and document the violation in the verification report.

## Verdict
- **PASS** — All 4 checks confirm substance and compliance
- **PARTIAL: <list checks that failed with evidence>**
- **FAIL: <list all failures with evidence>**

Write your verification report to:
`{SESSION_DIR}/pc/pc-{TASK_SUFFIX}-dmvdc-review-{timestamp}.md`

Where:
- `{TASK_SUFFIX}`: Nitpicker task suffix (e.g., `review-clarity`, `review-edge`)
- `{SESSION_DIR}`: session artifact directory (e.g., `.beads/agent-summaries/_session-abc123`)
- timestamp: format defined in **Timestamp format** (Pest Control Overview)
```

### The Queen's Response

**On PASS**: Proceed normally (close task, backfill queue).

**On PARTIAL or FAIL**:
1. Log the failure and specific gaps
2. Resume the original agent (using its agent ID) with a prompt:
   ```
   Your work was substance-verified and gaps were found:
   <paste specific failures from verification report>
   Please address these gaps: re-do the missing work, update your summary doc, and recommit.
   ```
3. Re-run DMVDC after the agent updates
4. If it fails a second time, flag to user for manual review

---

## Colony Census Bureau (CCB): Consolidation Audit

**When**: After Big Head consolidation (after all review reports merged and beads filed — 4 reports in round 1, 2 in round 2+)
**Model**: `haiku` (mechanical counting + record-checking)
**Agent type**: `code-reviewer`

**CCB must PASS before presenting results to the user.**

```markdown
**Pest Control verification - CCB (Consolidation Audit)**

You are **Pest Control**, the verification subagent. Your role is to audit Big Head's consolidated report for integrity.

Audit the review consolidation for completeness, accuracy, and traceability.

**Consolidated summary**: `{SESSION_DIR}/review-reports/review-consolidated-{timestamp}.md`
**Individual reports**: (the Queen provides exact filenames and the review round number in the consolidation prompt.)

Round 1:
- `{SESSION_DIR}/review-reports/clarity-review-{timestamp}.md`
- `{SESSION_DIR}/review-reports/edge-cases-review-{timestamp}.md`
- `{SESSION_DIR}/review-reports/correctness-review-{timestamp}.md`
- `{SESSION_DIR}/review-reports/excellence-review-{timestamp}.md`

Round 2+:
- `{SESSION_DIR}/review-reports/correctness-review-{timestamp}.md`
- `{SESSION_DIR}/review-reports/edge-cases-review-{timestamp}.md`

Read all documents (round 1: 5 total = 4 reports + consolidated; round 2+: 3 total = 2 reports + consolidated), then perform these 8 checks:

## Check 0: Report Existence Verification
Verify the expected report files exist at their paths. The expected count depends on the review round:

**Round 1** — verify exactly 4 report files:
- `{SESSION_DIR}/review-reports/clarity-review-{timestamp}.md`
- `{SESSION_DIR}/review-reports/edge-cases-review-{timestamp}.md`
- `{SESSION_DIR}/review-reports/correctness-review-{timestamp}.md`
- `{SESSION_DIR}/review-reports/excellence-review-{timestamp}.md`

**Round 2+** — verify exactly 2 report files:
- `{SESSION_DIR}/review-reports/correctness-review-{timestamp}.md`
- `{SESSION_DIR}/review-reports/edge-cases-review-{timestamp}.md`

If any expected file is missing, FAIL immediately — consolidation should not have proceeded.

## Check 1: Finding Count Reconciliation
Count total findings across all individual reports (4 in round 1, 2 in round 2+).
Count total findings referenced in the consolidated summary.
Every finding must be accounted for — either standalone, merged into a group, or explicitly marked as duplicate in the deduplication log.
Report the math: "Round 1: Clarity: N, Edge Cases: N, Correctness: N, Excellence: N = TOTAL total. Round 2+: Correctness: N, Edge Cases: N = TOTAL total. Consolidated references TOTAL findings across N root causes. N findings merged as duplicates. RECONCILED / NOT RECONCILED — {list orphaned findings}"

## Check 2: Bead Existence Check
For each bead ID in the consolidated summary, run `bd show <id>`.
Verify it exists and has status=open.
Report any IDs that don't resolve or have unexpected status.

## Check 3: Bead Quality Check
For each filed bead, verify its description contains:
- Root cause explanation (not just symptom)
- At least one file:line reference
- Acceptance criteria or verification steps
- Suggested fix
Flag any beads missing these elements. List which elements are missing.

## Check 4: Priority Calibration
Read P1 bead descriptions. Do they describe genuinely blocking issues (crashes, data loss, security vulnerabilities, broken functionality)?
Or are they style preferences or minor improvements mislabeled as P1?
Flag any suspicious priority assignments with reasoning.

## Check 5: Traceability Matrix
Build a matrix: Finding → Root Cause Group → Bead ID.
For every finding from every report, trace it to either:
- A bead ID (via root cause group), OR
- An explicit entry in the dedup log marking it as merged/duplicate
Report any orphaned findings (not traceable to a bead or dedup entry).

## Check 6: Deduplication Correctness
For each merged group of 3+ findings:
- Verify the merged findings share at least one common file or function
- If findings span unrelated code areas with no shared pattern, flag for review
- Read the merge rationale in the dedup log — is it coherent? Does it reference a real shared code path or design pattern?

Spot-check 2 merged groups by reading the actual code at each finding's location:
- Do the findings genuinely share a root cause, or were unrelated issues incorrectly merged?
- Report: "Group '<title>' merges N findings across files {list}. Common pattern: {yes/no — explanation}. CONFIRMED / SUSPECT"

## Check 7: Bead Provenance Audit
Run `bd list --status=open` and cross-reference against the consolidated summary's "Beads filed" list.
- Every open bead should trace back to the consolidation step
- Flag any beads that were filed during the review phase (not consolidation) — these are unauthorized
- Verify bead count matches the consolidated summary's count

## Verdict
- **PASS** — All 8 checks confirm consolidation integrity
- **PARTIAL: <list checks that failed with evidence>**
- **FAIL: <list all failures with evidence>**

Write your verification report to:
`{SESSION_DIR}/pc/pc-session-ccb-{timestamp}.md`

Where:
- `{SESSION_DIR}`: session artifact directory (e.g., `.beads/agent-summaries/_session-abc123`)
- timestamp: format defined in **Timestamp format** (Pest Control Overview)

**CRITICAL FIX**: The timestamp ensures each CCB audit is preserved. Previous versions used static filename `consolidation-audit.md` which caused overwrites on repeated consolidations. Now each audit has a unique timestamped filename, preserving complete audit history.
```

### The Queen's Response

**On PASS**: Proceed to present results to user.

**On PARTIAL or FAIL**:
1. Fix consolidation gaps (re-read reports, file missing beads, update dedup log)
2. Re-run CCB
3. If it fails a second time, present to user with the verification report attached so they can see what was flagged

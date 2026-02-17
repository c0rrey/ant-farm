<!-- Reader: Pest Control. The Queen does NOT read this file. -->
# Verification Checkpoints

**Term definitions (canonical across all orchestration templates):**
- `{TASK_ID}` — full bead ID including project prefix (e.g., `ant-farm-9oa` or `hs_website-74g.1`)
- `{TASK_SUFFIX}` — suffix portion only, no project prefix (e.g., `9oa` from `ant-farm-9oa`, or `74g1` from `hs_website-74g.1`)
- `{EPIC_ID}` — epic suffix only (e.g., `74g` from `hs_website-74g`), or `_standalone` for tasks with no epic parent

## Pest Control Overview

All checkpoint verifications (CCO, WWD, DMVDC, CCB) are executed by **Pest Control**, a dedicated verification subagent that cross-checks orchestrator and agent work against ground truth.

**Pest Control responsibilities:**
- Pre-spawn prompt audits (CCO)
- Post-commit scope verification (WWD)
- Post-completion substance verification (DMVDC)
- Consolidation integrity audits (CCB)

**Artifact naming conventions:**
- **Task-specific checkpoints (CCO, DMVDC):** `pc-{TASK_SUFFIX}-{checkpoint}-{timestamp}.md`
  - Example: `pc-74g1-cco-20260215-001145.md`
  - Example: `pc-74g1-dmvdc-20260215-003422.md`
- **Consolidation audits (CCB):** `pc-{EPIC_ID}-ccb-{timestamp}.md`
  - Example: `pc-74g-ccb-20260215-010520.md`
- **Storage:** All artifacts in `.beads/agent-summaries/{EPIC_ID}/verification/pc/`
  Cross-epic verification files are duplicated to each participating epic's verification directory.

**Task suffix derivation:**
- `{TASK_SUFFIX}` = suffix portion of bead ID with no project prefix (e.g., `74g1` from `hs_website-74g.1`)
- Use `standalone` for tasks without epic parent

**Epic ID format (CCB only):**
- Use 3-char epic suffix (e.g., `74g` from `hs_website-74g`)
- Use `multi` for consolidations spanning multiple epics

**Timestamp format:** `YYYYMMDD-HHMMSS`

**Epic ID resolution:** When constructing paths that include `{EPIC_ID}`, resolve the epic ID from the task ID:

| Task ID Pattern | Epic ID | Example |
|----------------|---------|---------|
| `hs_website-<X>.<N>` | `X` | `hs_website-74g.1` → `74g` |
| `<X>.<N>` (non-prefixed) | `X` | `74g.8` → `74g` |
| No epic parent | `_standalone` | `hs_website-596y` → `_standalone` |

**Directory creation**: The Queen pre-creates `.beads/agent-summaries/{EPIC_ID}/verification/pc/` at Step 2 (see RULES.md Epic Artifact Directories) and `.beads/agent-summaries/{EPIC_ID}/review-reports/` at Step 3b (see reviews.md Pre-Spawn Directory Setup). Agents and Pest Control can write immediately without creating directories.

**The Queen's responsibility**: The Queen MUST include `**Epic ID**` and `**Summary output path**` in the agent prompt context section. For review prompts, include all participating epic IDs and instruct reviewers to write reports to each epic's `review-reports/` directory.

**Review timestamp convention**: The Queen generates a single timestamp per review cycle (format: `YYYYMMDD-HHMMSS`) and passes the exact output filenames to each reviewer and Big Head. This prevents reviewers from independently generating different timestamps.

---

## Colony Cartography Office (CCO): Pre-Spawn Prompt Audit

### Dirt Pushers

**When**: After orchestrator composes agent prompt(s), BEFORE spawning
**Model**: `haiku` (mechanical checklist — cheap, fast)
**Agent type**: `code-reviewer`

**Why**: The orchestrator has a self-policing checklist, but nobody audits the orchestrator. Catching prompt defects before spawn is 100x cheaper than catching them after.

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
   - Step 6: Write summary doc to `.beads/agent-summaries/{EPIC_ID}/`
5. **Scope boundaries**: Contains explicit limits on which files to read (not open-ended "explore the codebase")
6. **Commit instructions**: Includes `git pull --rebase` before commit
7. **Line number specificity** (NEW - prevents scope creep): File paths include specific line ranges or section markers
   - ✅ PASS: "Edit templates/macros/jsonld.html lines 23-24 (image property only)"
   - ⚠️ WARN: "Edit templates/macros/jsonld.html (image property)" — file-level scope, acceptable if small file
   - ❌ FAIL: "Edit templates/macros/jsonld.html" — vague, high scope creep risk

## Verdict
- **PASS** — All 7 checks pass
- **FAIL: <list each failing check with evidence>**

Write your verification report to:
`.beads/agent-summaries/{EPIC_ID}/verification/pc/pc-{TASK_SUFFIX}-cco-{timestamp}.md`

Where:
- `{TASK_SUFFIX}`: suffix portion of bead ID with no project prefix (e.g., `74g1` from `hs_website-74g.1`), or `standalone` if no epic
- `{EPIC_ID}`: epic suffix only (e.g., `74g`), or `_standalone` for tasks with no epic parent
- timestamp: YYYYMMDD-HHMMSS format
```

### The Nitpickers

**When**: After composing all 4 review prompts, BEFORE creating the team
**Model**: `haiku`
**Agent type**: `code-reviewer`

```markdown
**Pest Control verification - CCO (Pre-Spawn Nitpickers Audit)**

You are **Pest Control**, the verification subagent. Your role is to audit the Nitpickers prompts before spawn.

Audit the following 4 Nitpickers prompts for completeness and consistency.
Do NOT execute the prompts — only verify their contents.

<prompt_clarity>
{paste clarity review prompt}
</prompt_clarity>

<prompt_edge_cases>
{paste edge cases review prompt}
</prompt_edge_cases>

<prompt_correctness>
{paste correctness review prompt}
</prompt_correctness>

<prompt_excellence>
{paste excellence review prompt}
</prompt_excellence>

## Verify each item (PASS or FAIL with evidence):

0. **File list matches git diff**: The Queen provides the commit range (`<first-commit>..<last-commit>`) in the spawn prompt — use those exact values. Run `git diff --name-only <first-commit>..<last-commit>` and verify the prompt file list matches exactly. Every file in the diff must appear in the prompt, and every file in the prompt must appear in the diff. If there is a mismatch, FAIL with the list of missing/extra files.
1. **Same file list**: All 4 prompts contain the same set of files to review (not different subsets)
2. **Same commit range**: All 4 prompts reference the same commit range
3. **Correct focus areas**: Each prompt has focus areas specific to its review type:
   - Clarity: readability, naming, documentation, consistency, structure
   - Edge Cases: input validation, error handling, boundaries, file ops, concurrency
   - Correctness: acceptance criteria, logic errors, data integrity, regressions, cross-file
   - Excellence: best practices, performance, security, maintainability, architecture
   (Flag if focus areas are copy-pasted identically across prompts)
4. **No bead filing instruction**: Each prompt contains "Do NOT file beads" or equivalent
5. **Report format reference**: Each prompt specifies the output path `.beads/agent-summaries/{EPIC_ID}/review-reports/{type}-review-{timestamp}.md`
6. **Messaging guidelines**: Each prompt includes guidance on when to message other Nitpickers

## Verdict
- **PASS** — All 7 checks pass for all 4 prompts
- **FAIL: <list each failing check, specifying which prompt(s)>**

Write your verification report to:
`.beads/agent-summaries/{EPIC_ID}/verification/pc/pc-{EPIC_ID}-cco-review-{timestamp}.md`

Where:
- `{EPIC_ID}`: epic suffix only (e.g., `74g` from `hs_website-74g`), or `multi` for multi-epic reviews
- timestamp: YYYYMMDD-HHMMSS format
```

### The Queen's Response

**On PASS**: Proceed to spawn the agent(s) or create the team.

**On FAIL**: Fix the specific gaps in the prompt(s), then re-run CCO. Do NOT spawn until PASS.

---

## Wandering Worker Detection (WWD): Post-Commit Scope Verification

**When**: After agent commits, BEFORE spawning next agent in same wave
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

## Verdict
- **PASS** — Files match expected scope (or extra files are legitimate build outputs)
- **WARN: <list extra files with rationale>** — Extra files need the Queen's review (e.g., "index.html regenerated from template change — legitimate")
- **FAIL: <list unexpected files>** — Agent edited files outside task scope (scope creep detected)

Write your verification report to:
`.beads/agent-summaries/{EPIC_ID}/verification/pc/pc-{TASK_SUFFIX}-wwd-{timestamp}.md`
```

### The Queen's Response

**On PASS**: Continue normally (run DMVDC, backfill queue).

**On WARN**: Review the extra files. If legitimate (e.g., HTML rebuild from template), accept and continue. If suspicious, escalate to user.

**On FAIL (scope creep detected)**:
1. Log the violation in queen-state.md
2. Mark task with scope creep note in final closure
3. Check if overlapping work affects queued agents (may need to adjust or cancel)
4. Continue but document for post-mortem

**Do NOT retry** — the code is already committed. Focus on documenting and preventing cascade effects.

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

**Summary doc**: `.beads/agent-summaries/{EPIC_ID}/{TASK_SUFFIX}.md`
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
Pick the 2 most critical criteria. For each:
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
`.beads/agent-summaries/{EPIC_ID}/verification/pc/pc-{TASK_SUFFIX}-dmvdc-{timestamp}.md`

Where:
- `{TASK_SUFFIX}`: suffix portion of bead ID with no project prefix (e.g., `74g1` from `hs_website-74g.1`)
- `{EPIC_ID}`: epic suffix only (e.g., `74g`), or `_standalone` for tasks with no epic parent
- timestamp: YYYYMMDD-HHMMSS format
```

### Nitpickers

**When**: After each Nitpicker completes its report
**Model**: `sonnet`
**Agent type**: `code-reviewer`

```markdown
**Pest Control verification - DMVDC (Nitpicker Substance Verification)**

You are **Pest Control**, the verification subagent. Your role is to cross-check Nitpicker findings against actual code.

Verify the substance of a Nitpicker's report by cross-checking findings against actual code.

**Report path**: `.beads/agent-summaries/{EPIC_ID}/review-reports/{review-type}-review-{timestamp}.md`
**Review type**: {clarity|edge-cases|correctness|excellence}

Read the report first, then perform these 4 checks:

## Check 1: Code Pointer Verification
Pick `min(5, ceil(N/3))` random findings from the report (where N = total findings; minimum 3, or all findings if fewer than 3). Always include the highest-severity finding and at least one finding from each severity tier present in the report.
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
`.beads/agent-summaries/{EPIC_ID}/verification/pc/pc-{TASK_SUFFIX}-dmvdc-review-{timestamp}.md`

Where:
- `{TASK_SUFFIX}`: Nitpicker task suffix (e.g., `review-clarity`, `review-edge`)
- `{EPIC_ID}`: epic suffix only (e.g., `74g`), or `_standalone` for tasks with no epic parent
- timestamp: YYYYMMDD-HHMMSS format
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

**When**: After Big Head consolidation (after all 4 review reports merged and beads filed)
**Model**: `haiku` (mechanical counting + record-checking)
**Agent type**: `code-reviewer`

**CCB must PASS before presenting results to the user.**

```markdown
**Pest Control verification - CCB (Consolidation Audit)**

You are **Pest Control**, the verification subagent. Your role is to audit Big Head's consolidated report for integrity.

Audit the review consolidation for completeness, accuracy, and traceability.

**Consolidated summary**: `.beads/agent-summaries/{EPIC_ID}/review-reports/review-consolidated-{timestamp}.md`
**Individual reports**: (The Queen provides exact filenames in the consolidation prompt.)
- `.beads/agent-summaries/{EPIC_ID}/review-reports/clarity-review-{timestamp}.md`
- `.beads/agent-summaries/{EPIC_ID}/review-reports/edge-cases-review-{timestamp}.md`
- `.beads/agent-summaries/{EPIC_ID}/review-reports/correctness-review-{timestamp}.md`
- `.beads/agent-summaries/{EPIC_ID}/review-reports/excellence-review-{timestamp}.md`

Read all 5 documents, then perform these 8 checks:

## Check 0: Report Existence Verification
Verify exactly 4 report files exist at their expected paths (the Queen provides exact filenames):
- `.beads/agent-summaries/{EPIC_ID}/review-reports/clarity-review-{timestamp}.md`
- `.beads/agent-summaries/{EPIC_ID}/review-reports/edge-cases-review-{timestamp}.md`
- `.beads/agent-summaries/{EPIC_ID}/review-reports/correctness-review-{timestamp}.md`
- `.beads/agent-summaries/{EPIC_ID}/review-reports/excellence-review-{timestamp}.md`
If any file is missing, FAIL immediately — consolidation should not have proceeded.

## Check 1: Finding Count Reconciliation
Count total findings across all 4 individual reports.
Count total findings referenced in the consolidated summary.
Every finding must be accounted for — either standalone, merged into a group, or explicitly marked as duplicate in the deduplication log.
Report the math: "Clarity: N, Edge Cases: N, Correctness: N, Excellence: N = TOTAL total. Consolidated references TOTAL findings across N root causes. N findings merged as duplicates. RECONCILED / NOT RECONCILED — {list orphaned findings}"

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
`.beads/agent-summaries/{EPIC_ID}/verification/pc/pc-{EPIC_ID}-ccb-{timestamp}.md`

Where:
- `{EPIC_ID}`: epic suffix only (e.g., `74g` from `hs_website-74g`), or `multi` for multi-epic consolidations
- timestamp: YYYYMMDD-HHMMSS format

**CRITICAL FIX**: The timestamp ensures each CCB audit is preserved. Previous versions used static filename `consolidation-audit.md` which caused overwrites on repeated consolidations. Now each audit has a unique timestamped filename, preserving complete audit history.
```

### The Queen's Response

**On PASS**: Proceed to present results to user.

**On PARTIAL or FAIL**:
1. Fix consolidation gaps (re-read reports, file missing beads, update dedup log)
2. Re-run CCB
3. If it fails a second time, present to user with the verification report attached so they can see what was flagged

<!-- Reader: Pest Control. The Queen does NOT read this file. -->
# Verification Checkpoints

**Term definitions (canonical across all orchestration templates):**

For the full extraction algorithm, see `~/.claude/orchestration/reference/dependency-analysis.md` (Term Definitions section).

- `{TASK_ID}` — full crumb ID including project prefix. Two formats exist:
  - **Standalone task** (no epic sub-ID): `ant-farm-596y`, `hs_website-9oa`
  - **Epic sub-task** (dotted sub-ID): `ant-farm-74g.1`, `my-project-74g.1`
- `{TASK_SUFFIX}` — the short identifier used in file paths and artifact names. Derived by taking everything after the LAST hyphen, then converting any dot to nothing (joining the alphanumeric parts):
  - `ant-farm-596y` → `596y` (standalone task — no dot, suffix is the bare token after the last hyphen)
  - `ant-farm-74g.1` → `74g1` (epic sub-task — dot-normalized)
  - `my-project-74g.1` → `74g1` (project name contains a hyphen — split on LAST hyphen, then dot-normalize)
- `{SESSION_DIR}` — session artifact directory path (e.g., `.crumbs/sessions/_session-abc123`)
- `{checkpoint}` — lowercase checkpoint abbreviation used in artifact filenames (e.g., `cco`, `wwd`, `dmvdc`, `ccb`, `cco-review`, `dmvdc-review`)

## Pest Control Overview

All checkpoint verifications (SSV, CCO, WWD, DMVDC, CCB, ESV) are executed by **Pest Control**, a dedicated verification subagent that cross-checks orchestrator and agent work against ground truth.

**Role distinction**: The Queen spawns Pest Control to run a checkpoint. Pest Control executes all checkpoint logic directly — it does not spawn subagents. Pest Control has tools: Bash, Read, Write, Glob, Grep (no Task tool).

**Pest Control responsibilities:**
- Pre-implementation Scout strategy verification (SSV)
- Pre-spawn prompt audits (CCO)
- Post-commit scope verification (WWD)
- Post-completion substance verification (DMVDC)
- Consolidation integrity audits (CCB)
- Exec summary and CHANGELOG verification before push (ESV)

**Artifact naming conventions:**
- **Task-specific checkpoints (WWD, DMVDC for Dirt Pushers):** `pc-{TASK_SUFFIX}-{checkpoint}-{timestamp}.md`
  - Example: `pc-74g1-wwd-20260215-001045.md`
  - Example: `pc-74g1-dmvdc-20260215-003422.md`
- **Session-wide checkpoints (SSV, CCO for Dirt Pushers, CCO-review, CCB, ESV):** `pc-session-{checkpoint}-{timestamp}.md`
  - Example: `pc-session-ssv-20260215-001045.md`
  - Example: `pc-session-cco-impl-20260215-001145.md` (Dirt Pusher CCO: Queen batches all wave prompts into one audit)
  - Example: `pc-session-cco-review-20260215-001145.md`
  - Example: `pc-session-ccb-20260215-010520.md`
  - Example: `pc-session-esv-20260215-012345.md`
  - Note: Dirt Pusher CCO uses session-wide naming because the Queen audits all prompts for a wave in a single CCO run. Per-task CCO naming (`pc-{TASK_SUFFIX}-cco-{timestamp}.md`) applies only when auditing a single Dirt Pusher prompt in isolation (rare).
- **Historical (pre-_session-068ecc83):** Earlier sessions used varied naming formats that do not match the conventions above. Common patterns included wave-based checkpoint letters (`pest-control-{session}-checkpoint-{A|B}-{timestamp}.md`), trail-scoped directories (`{trail}/verification/pc/` instead of `{SESSION_DIR}/pc/`), and non-standardized prefixes (`pc-review-cco-`, `pest-control-`). `_session-068ecc83` is the first session to use the current standard fully. Artifacts from earlier sessions are expected to diverge from the current convention; do not treat those divergences as errors.

All checkpoints write to `{SESSION_DIR}/pc/`.

**Task suffix derivation:** See `~/.claude/orchestration/reference/dependency-analysis.md` (Term Definitions section) for extraction algorithm. Example: `74g1` from `my-project-74g.1`.

**Timestamp format:** `YYYYMMDD-HHmmss` (UTC)

**Directory creation**: the Queen creates `{SESSION_DIR}/pc/` at session start (Step 0 in RULES.md). Agents and Pest Control can write immediately without creating directories.

**The Queen's responsibility**: the Queen MUST include `**Summary output path**` in Dirt Pusher prompt context. For review prompts, include the session-scoped review report paths and all participating trail IDs (for context). Reviewers write to `{SESSION_DIR}/review-reports/`, not per-trail directories.

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
| **SSV** | All 3 checks must pass | First-listed violation per check | FAIL blocks Pantry spawn and all downstream steps |
| **CCO (Dirt Pushers)** | Small file = <100 lines | First-listed section/function | WARN does not block; Queen approves before spawn |
| **CCO (Nitpickers)** | All round-active prompts identical file list (round 1: 4; round 2+: 2) | (No tie-breaking) | FAIL blocks spawn |
| **WWD** | Small file = <100 lines | First-listed changed file | WARN does not block queue; FAIL blocks queue |
| **DMVDC (Dirt Pushers)** | Pick 2 criteria: first-listed OR identified-as-critical OR all if <2 | First-listed acceptance criterion | PARTIAL allows resubmission; FAIL escalates |
| **DMVDC (Nitpickers)** | Sample size = min(N, max(3, min(5, ceil(N/3)))) — see Check 1 for worked examples | Include highest-severity + all tiers | PARTIAL allows resubmission; FAIL escalates |
| **CCB** | Finding count must reconcile to 100% | Earliest-filed crumb per root cause | PARTIAL: fix and re-run; FAIL blocks user presentation |
| **ESV** | All 6 checks must pass | First-listed violation per check | FAIL blocks git push; one Scribe retry allowed before escalation |

### Details by Checkpoint

**SSV Verdict Specifics:**
- PASS: All 3 checks pass (no file overlaps within a wave, file lists match crumb descriptions, no intra-wave dependency violations)
- FAIL: Any check fails. Blocks Pantry spawn and all downstream spawning until Scout re-runs or issue is resolved.

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
- PASS: All 8 checks confirm (finding reconciliation, crumb quality, priority calibration, traceability, dedup correctness, provenance)
- PARTIAL: Some checks fail (fix and re-run)
- FAIL: Critical failures (e.g., missing reports, orphaned findings). Must resolve before presenting to user.

**ESV Verdict Specifics:**
- PASS: All 6 checks pass (task coverage, commit coverage, open crumb accuracy, CHANGELOG fidelity, section completeness, metric consistency)
- FAIL: Any check fails. Blocks git push. Re-spawn Scribe with specific violations (max 1 retry). Second failure escalates to user.

---

## Colony Cartography Office (CCO): Pre-Spawn Prompt Audit

### Dirt Pushers

**When**: After orchestrator composes agent prompt(s), BEFORE spawning
**Model**: `haiku` (mechanical checklist — cheap, fast)

**Why**: The orchestrator has a self-policing checklist, but nobody audits the orchestrator. Catching prompt defects before spawn is 100x cheaper than catching them after.

#### Verdict Thresholds for CCO

**PASS verdict**: All 7 checks pass without exceptions.

**WARN verdict** (acceptable for small files only):
- Check 7 is WARN instead of PASS, AND
- The file in question is "small": fewer than 100 lines, AND
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

1. **Real task IDs**: Contains actual task IDs (e.g., `my-project-abc`), NOT placeholders like `<task-id>` or `<id>`
2. **Real file paths**: Contains actual file paths with line numbers (e.g., `build.py:L200`), NOT placeholders like `<list from crumb>` or `<file>`
3. **Root cause text**: Contains a specific root cause description, NOT `<copy from crumb>` or similar placeholders
4. **All 6 mandatory steps present**:
   - Step 1: `crumb show` + `crumb update --status=in_progress`
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

**Example FAIL verdict:**

> **Verdict: FAIL**
>
> Failed checks:
> - Check 2 (Real file paths): FAIL — prompt contains placeholder `<list from crumb>` instead of actual file paths with line numbers.
> - Check 5 (Scope boundaries): FAIL — no explicit file or directory limits; prompt says "explore the codebase for related issues."
>
> Passing checks: 1, 3, 4, 6, 7
>
> Recommendation: Rewrite prompt with actual file paths (e.g., `build.py:L200-215`) and explicit scope boundaries before re-running CCO.

Write your verification report to:

**Batch mode (most common):** `{SESSION_DIR}/pc/pc-session-cco-impl-{timestamp}.md`
- Use when the Queen runs CCO over all Dirt Pusher prompts for a wave in a single audit.
- The suffix `impl` distinguishes this artifact from the Nitpicker CCO (`cco-review`) in the same session.

**Per-task mode (single-prompt audit):** `{SESSION_DIR}/pc/pc-{TASK_SUFFIX}-cco-{timestamp}.md`
- Use only when auditing a single Dirt Pusher prompt in isolation.
- Example: `{SESSION_DIR}/pc/pc-74g1-cco-{timestamp}.md`

Where:
- `{TASK_SUFFIX}`: suffix portion of crumb ID with no project prefix (e.g., `74g1` from `my-project-74g.1`)
- `{SESSION_DIR}`: session artifact directory (e.g., `.crumbs/sessions/_session-abc123`)
- timestamp: format defined in **Timestamp format** (Pest Control Overview)
```

### The Nitpickers

**When**: After composing all review prompts (round 1: 4 prompts; round 2+: 2 prompts), BEFORE creating the team
**Model**: `haiku`

```markdown
**Pest Control verification - CCO (Pre-Spawn Nitpickers Audit)**

You are **Pest Control**, the verification subagent. Your role is to audit the Nitpickers prompts before spawn.

**Review round**: {REVIEW_ROUND}
**Input guard**: If {REVIEW_ROUND} still appears as the literal text `{REVIEW_ROUND}` (curly braces present), or is missing, blank, or non-numeric (not a positive integer), return the following message and do NOT proceed with the audit:

"CCO ABORTED: REVIEW_ROUND placeholder was not substituted before spawning CCO (got: '{REVIEW_ROUND}'). Root cause: upstream substitution failure — the Queen or Pantry did not replace `{REVIEW_ROUND}` in the CCO prompt before dispatch. Fix: ensure the prompt-composition step fills in REVIEW_ROUND as a plain integer (e.g. `1`) before spawning Pest Control."

Audit the following Nitpicker prompts for completeness and consistency.
Round 1: 4 prompts (clarity, edge-cases, correctness, drift).
Round 2+: 2 prompts (correctness, edge-cases only).
Do NOT execute the prompts — only verify their contents.

Round 1 — paste all 4 prompts:
<prompt_clarity>
{paste clarity review prompt — round 1 only}
</prompt_clarity>

<prompt_drift>
{paste drift review prompt — round 1 only}
</prompt_drift>

Both rounds — paste these 2 prompts:
<prompt_edge_cases>
{paste edge cases review prompt}
</prompt_edge_cases>

<prompt_correctness>
{paste correctness review prompt}
</prompt_correctness>

## Verify each item (PASS or FAIL with evidence):

1. **File list matches git diff**: the Queen provides the commit range (`<first-commit>..<last-commit>`) in the spawn prompt — use those exact values. This is session-wide, spanning all trails. Run `git diff --name-only <first-commit>..<last-commit>` and verify the prompt file list matches exactly. Every file in the diff must appear in the prompt, and every file in the prompt must appear in the diff. If there is a mismatch, FAIL with the list of missing/extra files.
   > **Known limitation**: The commit range is Queen-provided. If the Queen passes incorrect commit hashes (e.g., too narrow or too broad), this check validates against wrong ground truth. There is no independent way for Pest Control to derive the "correct" commit range. Mitigation: WWD (Post-Commit Scope Verification) independently validates per-task scope after each agent commits, catching scope errors that slip through here.
2. **Same file list**: All prompts contain the same set of files to review (not different subsets)
3. **Same commit range**: All prompts reference the same commit range
4. **Correct focus areas**: Each prompt has focus areas specific to its review type:
   - Clarity: readability, naming, documentation, consistency, structure (round 1 only)
   - Edge Cases: input validation, error handling, boundaries, file ops, concurrency
   - Correctness: acceptance criteria, logic errors, data integrity, regressions, cross-file
   - Drift: stale cross-file references, incomplete propagation, broken assumptions (round 1 only)
   (Flag if focus areas are copy-pasted identically across prompts)
5. **No crumb filing instruction**: Each prompt contains "Do NOT file crumbs" or equivalent
6. **Report format reference**: Each prompt specifies the output path `{SESSION_DIR}/review-reports/{type}-review-{timestamp}.md`
7. **Messaging guidelines**: Each prompt includes guidance on when to message other Nitpickers

## Verdict
- **PASS** — All 7 checks pass for all prompts in scope for this round
- **FAIL: <list each failing check, specifying which prompt(s)>**

Write your verification report to:
`{SESSION_DIR}/pc/pc-session-cco-review-{timestamp}.md`

Where:
- `{SESSION_DIR}`: session artifact directory (e.g., `.crumbs/sessions/_session-abc123`)
- timestamp: format defined in **Timestamp format** (Pest Control Overview)
```

### The Queen's Response

**On PASS**: Proceed to spawn the agent(s) or create the team.

**On FAIL**: Fix the specific gaps in the prompt(s), then re-run CCO. Do NOT spawn until PASS.

---

## Wandering Worker Detection (WWD): Post-Commit Scope Verification

**When**: Two execution modes depending on how agents were spawned (a "wave" is a group of agents spawned for the same execution round):
- **Serial mode**: After each individual agent commits, BEFORE spawning the next agent in the wave. Agents were spawned one at a time; true per-agent gating is possible.
- **Batch mode**: After ALL agents in the wave have committed (agents were spawned in parallel in a single message, so per-agent serial gating is mechanically impossible). One WWD instance per committed task, run concurrently. All WWD reports must PASS before DMVDC runs.

**Mode selection rule**: If the Queen spawned agents in a single message (parallel wave), use batch mode. If the Queen spawned agents individually in separate messages, use serial mode. (Authoritative source: RULES.md Step 3.)
**Model**: `haiku` (mechanical file list comparison — cheap, fast)

**Why**: Catches scope creep in real-time between agents, before DMVDC runs. Prevents cascading work attribution errors when multiple agents work on related files.

**Known failure mode**: In Wave 1 of Epic 74g, agent 74g.6 (comment task) made functional changes belonging to 74g.7 (foundingDate filter), which cascaded into 74g.7 making changes belonging to 74g.4 (sameAs conditional). WWD would have caught the first scope violation immediately.

```markdown
**Pest Control verification - WWD (Post-Commit Scope Verification)**

You are **Pest Control**, the verification subagent. Your role is to verify agent commits match task scope.

**Task ID**: {TASK_ID}
**Expected files** (from `crumb show {TASK_ID}`): {list files from task description}

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

**PASS verdict**: All changed files are in the expected scope (from `crumb show {TASK_ID}`), or any extra files are clearly legitimate build outputs (e.g., HTML regenerated from template change, CSS compiled from SASS).

**WARN verdict**: Extra files changed that need the Queen's judgment before continuing to the next task in the wave. Does NOT block the queue — only requires Queen review.
- Examples: template changes that cascade into multiple HTML files, configuration changes affecting derived docs
- Queen decision: approve as legitimate build artifact, or escalate to user if suspicious

**FAIL verdict**: Scope creep detected — agent edited files outside the expected scope (different feature, unrelated config, cross-trail work). Indicates a real work attribution problem that needs correction.

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
Run `crumb show {TASK_ID}` to get the task's acceptance criteria.

**GUARD: crumb show Failure Handling (INFRASTRUCTURE FAILURE)**
If `crumb show {TASK_ID}` fails (task not found, unreadable, or crumb command error):
- Record the infrastructure failure: "{TASK_ID} — crumb show failed: {error details}"
- Write a note in your review report: "Could not retrieve acceptance criteria for {TASK_ID} via `crumb show`: {error}. Proceeding with criteria from summary doc only."
- Do NOT abort the review; use the acceptance criteria listed in the agent's summary doc instead
- Clearly mark this fallback in your findings: "[Note: Criteria from summary doc, not from `crumb show`]"

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
- `{TASK_SUFFIX}`: suffix portion of crumb ID with no project prefix (e.g., `74g1` from `my-project-74g.1`)
- `{SESSION_DIR}`: session artifact directory (e.g., `.crumbs/sessions/_session-abc123`)
- timestamp: format defined in **Timestamp format** (Pest Control Overview)
```

### Nitpickers

**When**: After each Nitpicker completes its report
**Model**: `sonnet`

```markdown
**Pest Control verification - DMVDC (Nitpicker Substance Verification)**

You are **Pest Control**, the verification subagent. Your role is to cross-check Nitpicker findings against actual code.

Verify the substance of a Nitpicker's report by cross-checking findings against actual code.

**Report path**: `{SESSION_DIR}/review-reports/{review-type}-review-{timestamp}.md`
**Review type**: {clarity|edge-cases|correctness|drift}

Read the report first, then perform these 4 checks:

## Check 1: Code Pointer Verification
Pick a sample of findings to verify. The sample size formula is `min(N, max(3, min(5, ceil(N/3))))` where N is the total number of findings in the report.

**Plain English**: Take one-third of all findings (rounded up), but never fewer than 3 and never more than 5. If N is less than 3, verify all of them (sample size = N).

**Worked examples:**

| Total findings (N) | ceil(N/3) | min(5, ceil(N/3)) | max(3, ...) | min(N, ...) | Sample size |
|---|---|---|---|---|---|
| 1 | 1 | 1 | 3 | 1 | 1 (fewer findings than minimum — verify all) |
| 2 | 1 | 1 | 3 | 2 | 2 (fewer findings than minimum — verify all) |
| 6 | 2 | 2 | 3 | 3 | 3 (floor of 3 applies) |
| 9 | 3 | 3 | 3 | 3 | 3 |
| 12 | 4 | 4 | 4 | 4 | 4 |
| 15 | 5 | 5 | 5 | 5 | 5 |
| 30 | 10 | 5 | 5 | 5 | 5 (cap of 5 applies) |

Always include the highest-severity finding and at least one finding from each severity tier present in the report.
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
Search the report for `crumb create`, `crumb update`, `crumb close`, or crumb ID patterns (e.g., `my-project-xxx`).
- Nitpickers must NOT file crumbs
- If any crumb-filing commands or IDs are found, FAIL this check
- If unauthorized crumb filing is detected, this is a FAIL (not just a flag). The remediation step is: delete the unauthorized crumb (`crumb close <id> --reason="unauthorized filing during review"`) and document the violation in the verification report.

## Verdict
- **PASS** — All 4 checks confirm substance and compliance
- **PARTIAL: <list checks that failed with evidence>**
- **FAIL: <list all failures with evidence>**

Write your verification report to:
`{SESSION_DIR}/pc/pc-{TASK_SUFFIX}-dmvdc-{timestamp}.md`

Where:
- `{TASK_SUFFIX}`: Nitpicker review type (e.g., `review-correctness`, `review-edge-cases`, `review-clarity`, `review-drift`)
- `{SESSION_DIR}`: session artifact directory (e.g., `.crumbs/sessions/_session-abc123`)
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

**When**: After Big Head consolidation (after all review reports merged and crumbs filed — 4 reports in round 1, 2 in round 2+)
**Model**: `sonnet` (judgment required for crumb quality and dedup correctness)

**CCB must PASS before presenting results to the user.**

```markdown
**Pest Control verification - CCB (Consolidation Audit)**

You are **Pest Control**, the verification subagent. Your role is to audit Big Head's consolidated report for integrity.

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

- **Minor** — Root cause is vague or ambiguous but not outright wrong (e.g., "the function is inefficient" with no specifics, but the referenced code does contain the function). Action: flag the crumb for amendment, add a note to the CCB report, continue audit. Do NOT escalate.
- **Material** — Root cause is factually incorrect (e.g., the referenced line does not contain the described problem, or the fix direction would not address the actual defect). Action: trigger the Material Spot-Check Escalation Path below.

**Material Spot-Check Escalation Path:**
1. Set CCB verdict to PARTIAL and include a `context-degradation-suspected` flag in the verdict line.
2. The Queen shuts down the current Big Head instance.
3. The Queen spawns a fresh Big Head with a handoff brief describing which crumbs failed spot-check and why.
4. Fresh Big Head performs a full crumb review (re-reads source files, corrects or re-files affected crumbs).
5. Queen re-runs CCB.
6. If the re-run CCB still returns SUSPECT on any spot-checked crumb, escalate to the user with the CCB report attached.

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
`{SESSION_DIR}/pc/pc-session-ccb-{timestamp}.md`

Where:
- `{SESSION_DIR}`: session artifact directory (e.g., `.crumbs/sessions/_session-abc123`)
- timestamp: format defined in **Timestamp format** (Pest Control Overview)

**CRITICAL FIX**: The timestamp ensures each CCB audit is preserved. Previous versions used static filename `consolidation-audit.md` which caused overwrites on repeated consolidations. Now each audit has a unique timestamped filename, preserving complete audit history.
```

### The Queen's Response

**On PASS**: Proceed to present results to user.

**On PARTIAL or FAIL**:
1. Fix consolidation gaps (re-read reports, file missing crumbs, update dedup log)
2. Re-run CCB
3. If it fails a second time, present to user with the verification report attached so they can see what was flagged

---

## Scout Strategy Verification (SSV): Pre-Implementation Strategy Audit

**When**: After Scout returns `{SESSION_DIR}/briefing.md` and BEFORE spawning Pantry (Step 2 in RULES.md)
**Model**: `haiku` (pure set comparisons — no judgment required)

**Why**: The Scout's strategy (wave groupings, task-to-wave assignments, file conflict analysis) is currently validated only by human approval, which misses mechanical errors like file/task mismatches or intra-wave dependency violations. A lightweight automated check before Pantry is spawned catches strategy defects at the cheapest possible point — before any implementation prompts are composed.

**Why haiku**: All three checks are set comparisons and dependency graph traversals with no ambiguity. No judgment or code comprehension is required. Haiku handles this class of verification faster and cheaper than sonnet.

```markdown
**Pest Control verification - SSV (Scout Strategy Verification)**

You are **Pest Control**, the verification subagent. Your role is to verify the Scout's execution strategy for mechanical correctness before any implementation work begins. See "Pest Control Overview" section above for full conventions.

**Briefing file**: `{SESSION_DIR}/briefing.md`
**Session directory**: `{SESSION_DIR}`

Read the briefing file first to extract the full wave plan (wave numbers, task IDs per wave, affected files per task, and inter-task dependencies). Then run all three checks below.

## Check 1: No File Overlaps Within a Wave

For each wave in the strategy:
1. Collect all affected files listed for every task in that wave.
2. Check whether any file appears in two or more tasks within the same wave.
3. Report each violation as: "Wave N: file `<path>` appears in tasks <id1> AND <id2> — parallel edits would conflict."

A file overlap within a wave means two agents would edit the same file simultaneously, causing merge conflicts or lost changes. Tasks sharing a file must be serialized into separate waves.

**PASS condition**: No file appears in more than one task within any single wave.
**FAIL condition**: One or more files appear in multiple tasks within the same wave. List every violation.

## Check 2: File Lists Match Crumb Descriptions

For each task in the strategy:
1. Run `crumb show {TASK_ID}` to retrieve the crumb's recorded affected files.
2. Compare the Scout's reported affected files (from briefing.md) against the crumb's actual affected files.
3. Report each mismatch as: "Task {TASK_ID}: Scout lists `<file>` but crumb does not — OR — crumb lists `<file>` but Scout omits it."

**GUARD: crumb show Failure Handling (INFRASTRUCTURE FAILURE)**
If `crumb show {TASK_ID}` fails (task not found, unreadable, or crumb command error):
- Record the failure: "{TASK_ID} — crumb show failed: {error details}"
- Write a note in your verification report: "Could not verify file list for {TASK_ID} via `crumb show`: {error}. Skipping this task's file list check."
- Continue with the remaining tasks — do NOT abort the entire check.
- Clearly mark skipped tasks in your findings: "[SKIPPED: crumb show failed]"
- If more than half the tasks fail `crumb show`, FAIL the check with: "Infrastructure failure: could not verify file lists for majority of tasks."

**PASS condition**: For every task where `crumb show` succeeds, the Scout's file list exactly matches the crumb's recorded affected files (same set, order-insensitive).
**FAIL condition**: Any file list mismatch detected, or infrastructure failure threshold exceeded. List every discrepancy.

## Check 3: No Intra-Wave Dependency Violations

For each wave in the strategy:
1. Identify all tasks in that wave.
2. Check whether any task in wave N is listed as blocking (or blocked by) another task in the same wave N.
3. To retrieve dependencies: run `crumb show {TASK_ID}` for each task and examine its DEPENDENCIES section.
4. Report each violation as: "Wave N: task <id1> blocks task <id2> — both are in wave N; <id2> must move to a later wave."

An intra-wave dependency means an agent that is supposed to start in parallel actually depends on another agent finishing first. This defeats the purpose of wave grouping and may cause incorrect ordering.

**GUARD: crumb show Failure Handling**: Same as Check 2 — if `crumb show` fails for a task, skip dependency check for that task and note the skip.

**PASS condition**: No task in wave N has a "blocks" or "blocked-by" relationship with another task in the same wave N.
**FAIL condition**: One or more intra-wave dependency violations detected. List every violation.

## Verdict

**PASS** — All 3 checks pass. Report PASS to the Queen. The Queen will auto-proceed to spawn Pantry (Step 2) — do NOT spawn Pantry yourself.

**FAIL: <list each failing check>** — One or more checks failed. Do NOT spawn Pantry. Report specific violations so Scout can revise the strategy.

**Example FAIL verdict:**

> **Verdict: FAIL**
>
> Check 1 (File Overlaps): FAIL
> - Wave 2: file `src/api/routes.py` appears in tasks ant-farm-abc AND ant-farm-def — parallel edits would conflict.
>
> Check 2 (File List Match): PASS
>
> Check 3 (Intra-Wave Dependencies): FAIL
> - Wave 1: task ant-farm-xyz blocks task ant-farm-uvw — both are in Wave 1; ant-farm-uvw must move to Wave 2.
>
> Recommendation: Re-run Scout with these violations noted. Move ant-farm-def or ant-farm-abc to a different wave (file conflict), and move ant-farm-uvw to Wave 2 or later (dependency ordering).

Write your verification report to:
`{SESSION_DIR}/pc/pc-session-ssv-{timestamp}.md`

Where:
- `{SESSION_DIR}`: session artifact directory (e.g., `.crumbs/sessions/_session-abc123`)
- timestamp: format defined in **Timestamp format** (Pest Control Overview)
```

### The Queen's Response

**On PASS**: Auto-proceed to spawn Pantry (Step 2 in RULES.md). The SSV validates mechanical correctness (no file conflicts, no dependency violations); a PASS is sufficient to begin implementation without waiting for user approval.

**On FAIL**:
1. Log the violation details from the SSV report.
2. Do NOT spawn Pantry.
3. Re-run Scout with a prompt that includes the specific violations:
   ```
   SSV found strategy errors that must be corrected before implementation can begin:
   <paste specific violations from SSV report>
   Please revise the wave plan to resolve these issues and rewrite {SESSION_DIR}/briefing.md.
   ```
4. After Scout revises `{SESSION_DIR}/briefing.md`, re-run SSV.
5. If SSV fails a second time, escalate to user with the full violation report.

---

## Exec Summary Verification (ESV): Pre-Push Session Output Audit

**When**: After Scribe writes `{SESSION_DIR}/exec-summary.md` and CHANGELOG.md, BEFORE `git push` (Step 5c in RULES.md)
**Model**: `haiku` (mechanical counting and set comparisons — no judgment required)

**Why**: The Scribe produces an exec summary and CHANGELOG entry that are the permanent record of the session. Errors here (missed tasks, phantom commits, stale crumb statuses) mislead future sessions and create audit gaps. A lightweight automated check before push catches output defects at zero implementation cost — the session is already complete, so no rework cascades.

**Why haiku**: All six checks are set comparisons, count reconciliations, and status lookups with no ambiguity. No judgment or code comprehension is required. Haiku handles this class of verification faster and cheaper than sonnet.

```markdown
**Pest Control verification - ESV (Exec Summary Verification)**

You are **Pest Control**, the verification subagent. Your role is to verify the Scribe's session output for correctness before the session is pushed to remote. See "Pest Control Overview" section above for full conventions.

**Exec summary**: `{SESSION_DIR}/exec-summary.md`
**Session directory**: `{SESSION_DIR}`
**Session start commit**: `{SESSION_START_COMMIT}` (Queen-supplied; first commit of this session, used to scope git log)
**Session end commit**: `{SESSION_END_COMMIT}` (Queen-supplied; final commit before push)
**Session start date**: `{SESSION_START_DATE}` (ISO 8601, e.g., `2026-02-22` — Queen-supplied; used to scope crumb list)

Read the exec summary first. Then run all six checks below.

## Check 1: Task Coverage

1. Read `{SESSION_DIR}/briefing.md` (or `{SESSION_DIR}/progress.log` if briefing is unavailable) to extract all task IDs planned for this session.
2. Read the exec summary's "Work Completed" section and extract every task ID mentioned.
3. Every task ID from the briefing/progress log must appear in the exec summary.
4. Report each missing task as: "Task `{TASK_ID}` — in briefing/progress log but not in exec summary."

**PASS condition**: Every planned task ID appears in the exec summary's Work Completed section.
**FAIL condition**: One or more task IDs are absent. List every missing task ID.

## Check 2: Commit Coverage

1. Before running the git log range command, guard against a root-commit edge case:
   - Run `git rev-parse {SESSION_START_COMMIT}^ 2>/dev/null` to check whether `{SESSION_START_COMMIT}` has a parent.
   - **If the command succeeds** (exit code 0): run `git log --oneline {SESSION_START_COMMIT}^..{SESSION_END_COMMIT}` to list all commits in this session's range.
     > **Range boundary**: The `^` suffix on `{SESSION_START_COMMIT}` means "start from the parent of SESSION_START_COMMIT", which causes git to include SESSION_START_COMMIT itself in the output. This is intentional — `..` (without `^`) would exclude the first session commit. Always use `^..` here so the first commit of the session is included.
   - **If the command fails** (exit code non-zero, i.e. `{SESSION_START_COMMIT}` is the repo's root commit with no parent): run `git log --oneline {SESSION_START_COMMIT}..{SESSION_END_COMMIT}` instead, and note in your report: "SESSION_START_COMMIT is the repo root commit — used `..` range (no parent exists); SESSION_START_COMMIT itself is not included in the git log output."
2. Extract all commit hashes mentioned in the exec summary.
3. Every commit hash from the git log must be accounted for in the exec summary (either listed explicitly or covered by a task entry that references it).
4. Report each unaccounted commit as: "Commit `{HASH}` (`{message}`) — in git log but not referenced in exec summary."

**PASS condition**: Every commit in the session range is accounted for in the exec summary.
**FAIL condition**: One or more commits are unaccounted for. List every missing commit hash and its message.

## Check 3: Open Crumb Accuracy

1. Read the exec summary's "Open Issues" section and extract every crumb ID listed as open.
2. Run `crumb show <id>` for each listed crumb to verify it is actually open.

**GUARD: crumb show Failure Handling (INFRASTRUCTURE FAILURE)**
If `crumb show <id>` fails (task not found, unreadable, or crumb command error):
- Record the infrastructure failure: "`<id>` — crumb show failed: {error details}"
- Write a note in your verification report: "Could not verify status of `<id>` via `crumb show`: {error}. Skipping this crumb's status check."
- Do NOT abort the review; continue with remaining crumbs.
- Clearly mark skipped crumbs in your findings: "[SKIPPED: crumb show failed]"
- If more than half the listed crumbs fail `crumb show`, FAIL the check with: "Infrastructure failure: could not verify status for majority of listed crumbs."

3. Run `crumb list --open --after {SESSION_START_DATE}` to detect any open crumbs from this session that are NOT listed in the exec summary.
   > **Empty list handling**: If `crumb list --open --after {SESSION_START_DATE}` returns zero results AND the exec summary's "Open Issues" section says "None" (or equivalent), this is a PASS — no discrepancy exists. Proceed directly to Check 4. Only fail if the exec summary lists crumbs as open but `crumb show` contradicts them, or if `crumb list` returns crumbs that the exec summary omits.
4. Report each discrepancy as one of:
   - "Crumb `<id>` listed as open in exec summary but `crumb show` reports status={status}."
   - "Crumb `<id>` is open and filed during this session but not listed in exec summary's Open Issues."

**PASS condition**: Every crumb listed as open in exec summary is actually open (per `crumb show`), and no unlisted open crumbs from this session exist. If `crumb list` returns zero results and the exec summary states "None", this is also PASS.
**FAIL condition**: Any status mismatch, or unlisted open crumbs exist. List every discrepancy.

## Check 4: CHANGELOG Derivation Fidelity

1. Identify the new CHANGELOG.md entry written by the Scribe for this session (it will be the most recently added entry).
2. Read the exec summary's task IDs and commit hashes.
3. Verify that every task ID and commit hash present in the exec summary also appears in the CHANGELOG entry.
4. Report each missing item as: "Task ID `{TASK_ID}` in exec summary but absent from CHANGELOG entry." or "Commit `{HASH}` in exec summary but absent from CHANGELOG entry."

**PASS condition**: Every task ID and commit hash from the exec summary is present in the CHANGELOG entry.
**FAIL condition**: One or more items are missing from the CHANGELOG. List every missing item.

## Check 5: Section Completeness

1. Read the exec summary and verify that all 5 required sections are present:
   - **At a Glance** — summary table with key metrics
   - **Work Completed** — per-task outcome list
   - **Review Findings** — Nitpicker findings summary (may be "None" if no review ran)
   - **Open Issues** — list of open crumbs from this session (may be "None")
   - **Observations** — process notes, patterns, or handoff context

2. Report each missing section as: "Section '{section name}' is absent from exec summary."

**PASS condition**: All 5 required sections are present.
**FAIL condition**: One or more sections are missing. List every absent section.

## Check 6: Metric Consistency

1. Read the "At a Glance" table in the exec summary and extract all numeric counts (e.g., "Tasks completed: N", "Commits: N", "Crumbs filed: N").
2. For each count, verify it against the actual item count in the corresponding body section:
   - "Tasks completed" count must match the number of task entries in "Work Completed"
   - "Commits" count must match the number of commits in the session range (`git log --oneline` output)
   - "Crumbs filed" count must match the number of crumb IDs listed in "Open Issues" (or the review findings section if crumbs were filed there)
3. Report each mismatch as: "At a Glance says '{label}: {claimed}' but actual count in body is {actual}."

**PASS condition**: All numeric counts in "At a Glance" match the actual item counts in the body sections.
**FAIL condition**: One or more counts are inconsistent. List every mismatch with claimed and actual values.

## Verdict

Per-check status — report each check individually:

```
Check 1 (Task Coverage): PASS / FAIL — {evidence or "All task IDs present"}
Check 2 (Commit Coverage): PASS / FAIL — {evidence or "All commits accounted for"}
Check 3 (Open Crumb Accuracy): PASS / FAIL — {evidence or "All crumb statuses confirmed"}
Check 4 (CHANGELOG Fidelity): PASS / FAIL — {evidence or "All items present in CHANGELOG"}
Check 5 (Section Completeness): PASS / FAIL — {evidence or "All 5 sections present"}
Check 6 (Metric Consistency): PASS / FAIL — {evidence or "All counts consistent"}
```

**PASS** — All 6 checks pass. Report PASS to the Queen. The Queen may proceed with `git push`.

**FAIL: <list each failing check with evidence>** — One or more checks failed. Do NOT push. Re-spawn Scribe with specific violations.

**Example FAIL verdict:**

> **Verdict: FAIL**
>
> Check 1 (Task Coverage): PASS
>
> Check 2 (Commit Coverage): FAIL
> - Commit `a3f9c12` ("chore: sync crumbs JSONL") — in git log but not referenced in exec summary.
>
> Check 3 (Open Crumb Accuracy): FAIL
> - Crumb `ant-farm-99z` listed as open in exec summary but `crumb show` reports status=closed.
>
> Check 4 (CHANGELOG Fidelity): PASS
>
> Check 5 (Section Completeness): PASS
>
> Check 6 (Metric Consistency): FAIL
> - At a Glance says "Tasks completed: 4" but Work Completed section lists 3 tasks.
>
> Recommendation: Re-spawn Scribe with these violations. Scribe must update exec-summary.md and CHANGELOG to resolve Check 2, Check 3, and Check 6 before re-running ESV.

Write your verification report to:
`{SESSION_DIR}/pc/pc-session-esv-{timestamp}.md`

Where:
- `{SESSION_DIR}`: session artifact directory (e.g., `.crumbs/sessions/_session-abc123`)
- timestamp: format defined in **Timestamp format** (Pest Control Overview)
```

### The Queen's Response

**On PASS**: Proceed with `git push` (Step 6 in RULES.md).

**On FAIL**:
1. Log the failing check details from the ESV report.
2. Do NOT push to remote.
3. Re-spawn Scribe with a prompt that includes the specific violations:
   ```
   ESV found errors in the exec summary or CHANGELOG that must be corrected before push:
   <paste specific failures from ESV report>
   Please update {SESSION_DIR}/exec-summary.md and CHANGELOG.md to resolve these issues.
   ```
4. After Scribe updates the outputs, re-run ESV.
5. If ESV fails a second time, escalate to user — present the failed ESV report and ask whether to fix manually or push as-is. Do NOT push with undisclosed failures.

---

## Trail Decomposition Verification (TDV): Post-Decomposition Structure Audit

**When**: After Architect completes trail decomposition and writes crumbs to the crumb store, BEFORE handoff to the implementation wave
**Model**: `haiku` (set comparisons, graph traversals, field existence checks — no judgment required)

**Why**: The Architect produces a decomposition (trail + crumbs) that defines all downstream implementation work. Structural defects here — missing fields, circular dependencies, file conflicts within a wave, broken trail linkage — cannot be caught by the implementing agents and cascade into incorrect or conflicting work. A lightweight automated check immediately after decomposition catches defects at the cheapest possible point.

**Why haiku**: All five structural checks are set comparisons, graph traversals, and field presence validations with no ambiguity. The three heuristic warnings require pattern matching but no code comprehension. Haiku handles this class of verification faster and cheaper than sonnet.

### TDV Property Table

| Property | Value |
|---|---|
| **Name** | Trail Decomposition Verification (TDV) |
| **Run by** | Pest Control |
| **Model** | `haiku` |
| **When** | After Architect completes decomposition, before implementation wave |
| **Blocks** | Handoff to implementation wave (FAIL blocks; PASS proceeds) |
| **Max retries** | 2 (Architect retries); escalate to user after second failure |
| **Checks** | 5 structural (blockers) + 3 heuristic (warnings only) |

```markdown
**Pest Control verification - TDV (Trail Decomposition Verification)**

You are **Pest Control**, the verification subagent. Your role is to verify the Architect's trail decomposition for structural correctness before any implementation work begins. See "Pest Control Overview" section above for full conventions.

**Trail ID**: `{TRAIL_ID}`
**Session directory**: `{SESSION_DIR}`

> **Decomposition context**: When TDV runs during decomposition (spawned by the Planner via
> `RULES-decompose.md`), substitute `{DECOMPOSE_DIR}` for `{SESSION_DIR}` in all output paths.
> The Planner passes `DECOMPOSE_DIR` as the session directory value when filling this template.

Read the trail and all associated crumbs first (run `crumb show {TRAIL_ID}` and `crumb trail status {TRAIL_ID}` to enumerate child crumb IDs, then `crumb show <crumb-id>` for each). Then run all five structural checks and three heuristic checks below.

## Check 1: Coverage — Spec Requirements Map to Crumb Acceptance Criteria

1. Read the trail's `description` field to extract all stated requirements.
2. For each requirement, verify that at least one crumb's `acceptance_criteria` explicitly addresses it.
3. Report each unmapped requirement as: "Requirement '{text}' in trail description has no crumb acceptance criterion that addresses it."

**PASS condition**: Every requirement in the trail description maps to at least one crumb acceptance criterion.
**FAIL condition**: One or more requirements are unmapped. List every gap.

## Check 2: Completeness — Every Crumb Has All Required Fields

For each crumb in the decomposition, verify the presence and non-emptiness of these fields:
- `title` — crumb has a non-empty title
- `description` — crumb has a non-empty description
- `acceptance_criteria` — crumb has at least one acceptance criterion
- `scope.files` — crumb lists at least one affected file
- `scope.agent_type` — crumb specifies an agent type
- `links.parent` — crumb references a parent trail ID

Run `crumb show <crumb-id>` for each crumb and check each field.

Report each missing or empty field as: "Crumb `{crumb-id}`: missing or empty field `{field}`."

**PASS condition**: Every crumb has all 6 required fields populated.
**FAIL condition**: Any crumb is missing one or more required fields. List every violation.

## Check 3: Dependency Validity — No Circular Chains, All Referenced IDs Exist

1. For each crumb, read its `blocked_by` list (dependencies).
2. Verify that every referenced ID exists in the crumb store (run `crumb show <id>` for each).
3. Detect circular dependency chains: starting from each crumb, follow the `blocked_by` chain. If you return to the starting crumb, a cycle exists.
   - Represent the cycle as: "Circular dependency: `{crumb-id-A}` → `{crumb-id-B}` → ... → `{crumb-id-A}`."
4. Report each non-existent ID as: "Crumb `{crumb-id}`: `blocked_by` references `{missing-id}` which does not exist."

**GUARD: crumb show Failure Handling (INFRASTRUCTURE FAILURE)**
If `crumb show <id>` fails (ID not found, unreadable, or crumb command error):
- Record the failure: "`<id>` — crumb show failed: {error details}"
- Write a note in your verification report: "Could not verify `<id>` via `crumb show`: {error}. Skipping dependency check for this ID."
- Continue with the remaining IDs — do NOT abort the entire check.
- Clearly mark skipped IDs: "[SKIPPED: crumb show failed]"
- If more than half the referenced IDs fail `crumb show`, FAIL the check with: "Infrastructure failure: could not verify dependencies for majority of crumbs."

**PASS condition**: No circular chains exist and all referenced IDs resolve.
**FAIL condition**: Any circular dependency or unresolvable ID reference found. List every violation.

## Check 4: Scope Coherence — No Two Crumbs in the Same Provisional Wave Touch the Same File

### Provisional Wave Computation Algorithm

The decomposition does not explicitly label waves. Compute provisional waves as follows:

1. Build a directed acyclic graph (DAG) where each crumb is a node and each `blocked_by` edge points from dependent → dependency.
2. Assign each crumb a wave number equal to 1 + the maximum wave number of all its dependencies (crumbs with no dependencies are Wave 1).
3. Repeat until all crumbs have a wave assignment.

**Example**: Crumbs A, B (no deps) → Wave 1. Crumb C (blocked_by A) → Wave 2. Crumb D (blocked_by B, C) → Wave 3.

Once wave assignments are computed:

4. For each wave, collect all affected files listed in `scope.files` for every crumb in that wave.
5. Check whether any file appears in two or more crumbs within the same wave.
6. Report each conflict as: "Wave {N}: file `{path}` appears in crumbs `{crumb-id-1}` AND `{crumb-id-2}` — parallel edits would conflict."

**PASS condition**: No file appears in more than one crumb within any single wave.
**FAIL condition**: One or more files appear in multiple crumbs in the same wave. List every conflict.

## Check 5: Trail Integrity — Every Crumb Has a Parent Trail, Every Trail Has at Least One Child

1. For each crumb, verify that `links.parent` references `{TRAIL_ID}` (the decomposed trail).
2. Verify that the trail has at least one crumb listed as a child (i.e., the decomposition produced at least one crumb).
3. Report each orphaned crumb as: "Crumb `{crumb-id}`: `links.parent` is `{actual-value}`, expected `{TRAIL_ID}`."
4. If the trail has zero children, report: "Trail `{TRAIL_ID}` has no child crumbs — decomposition produced no work items."

**PASS condition**: Every crumb's `links.parent` matches `{TRAIL_ID}`, and the trail has at least one child.
**FAIL condition**: Any crumb has an incorrect parent, or the trail has zero children. List every violation.

---

## Heuristic Warnings (Non-Blocking)

The following three checks produce **WARN** verdicts only — they do not block handoff. Report them separately after the five structural checks. The Queen reviews and uses judgment to act or proceed.

### Warning 1: Acceptance Criteria Quality

For each crumb, assess whether each acceptance criterion is testable and specific:
- **Vague**: "Works correctly", "No errors", "Is complete", "Behaves as expected" — no observable measurement
- **Specific**: "Returns HTTP 200 when given valid input", "File `foo.py` no longer imports `deprecated_module`"

Flag any crumb where more than half of its acceptance criteria are vague. Report as: "WARN — Crumb `{crumb-id}`: {N} of {total} acceptance criteria are vague (e.g., '{example}'). Consider rewriting with observable outcomes."

### Warning 2: Dependency Chain Depth Greater Than 3

If any crumb's dependency chain (the longest path from it to a root crumb) exceeds 3 hops, flag it:
"WARN — Crumb `{crumb-id}` has dependency depth {N} (chain: {crumb-id} → ... → root). Deep chains amplify cascade risk — consider whether intermediate dependencies can be collapsed."

### Warning 3: Directory Overlap in the Same Wave

Even when no single file conflicts exist (Check 4 PASS), two crumbs in the same wave that both touch files in the same directory may indicate logical coupling missed by the Architect.

For each wave, identify crumbs whose `scope.files` share a common parent directory. Report as: "WARN — Wave {N}: crumbs `{crumb-id-1}` and `{crumb-id-2}` both touch files under `{directory}/`. Verify they do not have implicit coupling (e.g., shared imports, shared config, shared test fixtures)."

Only flag directory overlaps where both crumbs each touch at least 2 files in the shared directory (single-file incidental overlap is not worth flagging).

---

## Verdict

**PASS** — All 5 structural checks pass (heuristic warnings may be present). Report PASS to the Queen. The Queen will proceed to implementation handoff — do NOT begin handoff yourself.

**FAIL: <list each failing structural check>** — One or more structural checks failed. Do NOT proceed to handoff. Report specific violations so the Architect can revise the decomposition.

**Example FAIL verdict:**

> **Verdict: FAIL**
>
> Check 1 (Coverage): PASS
>
> Check 2 (Completeness): FAIL
> - Crumb `ant-farm-abc`: missing field `scope.agent_type`
> - Crumb `ant-farm-def`: missing field `acceptance_criteria`
>
> Check 3 (Dependency Validity): FAIL
> - Crumb `ant-farm-ghi`: `blocked_by` references `ant-farm-zzz` which does not exist.
>
> Check 4 (Scope Coherence): PASS
>
> Check 5 (Trail Integrity): PASS
>
> Warnings:
> - WARN — Crumb `ant-farm-abc`: 2 of 3 acceptance criteria are vague (e.g., "Works as expected").
>
> Recommendation: Resume Architect with these violations. Architect must add `scope.agent_type` and `acceptance_criteria` to missing crumbs, and remove the non-existent dependency reference, then rewrite the decomposition before re-running TDV.

Write your verification report to:
`{SESSION_DIR}/pc/pc-session-tdv-{timestamp}.md`

Where:
- `{SESSION_DIR}`: session artifact directory (e.g., `.crumbs/sessions/_session-abc123`)
- `{TRAIL_ID}`: the trail crumb ID being decomposed (e.g., `ant-farm-f4h5`)
- timestamp: format defined in **Timestamp format** (Pest Control Overview)
```

### The Queen's Response

**On PASS**: Proceed to implementation handoff. Heuristic warnings (if any) are advisory — note them in queen-state.md and use judgment about whether to act on them before spawning implementation agents.

**On FAIL**:
1. Log the failing check details from the TDV report.
2. Do NOT proceed to implementation handoff.
3. Resume the Architect with a prompt that includes the specific violations:
   ```
   TDV found decomposition errors that must be corrected before implementation can begin:
   <paste specific violations from TDV report>
   Please revise the decomposition to resolve these issues and update the crumbs in the crumb store.
   ```
4. After Architect revises the decomposition, re-run TDV.
5. If TDV fails a second time, escalate to user with the full violation report — do NOT attempt a third Architect retry automatically.

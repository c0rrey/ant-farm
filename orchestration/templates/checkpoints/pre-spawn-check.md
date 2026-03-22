<!-- Reader: Checkpoint Auditor. The Queen does NOT read this file. -->

## Pre-Spawn Check: Pre-Spawn Prompt Audit

### Crumb Gatherers

**When**: After orchestrator composes agent prompt(s), BEFORE spawning
**Model**: `haiku` (mechanical checklist — cheap, fast)

**Why**: The orchestrator has a self-policing checklist, but nobody audits the orchestrator. Catching prompt defects before spawn is 100x cheaper than catching them after.

#### Verdict Thresholds for pre-spawn-check

**PASS verdict**: All 7 checks pass without exceptions.

**WARN verdict** (acceptable for small files only):
- Check 7 is WARN instead of PASS, AND
- The file in question is "small": fewer than 100 lines, AND
- The prompt includes specific context about what the agent should modify (e.g., "update the error message on line 15")
- Example WARN: "Edit config.json (update API endpoint)" is WARN if config.json is 45 lines. The Queen reviews and approves.
- Example FAIL: "Edit templates/macros/jsonld.html" is FAIL because it provides no line specificity and the file is likely >100 lines. Needs rewrite.

**FAIL verdict**: Any check fails without WARN exception, or Check 7 is WARN but the file is large (≥100 lines) or lacks context.

```markdown
**Checkpoint Auditor verification - pre-spawn-check (Pre-Spawn Prompt Audit)**

You are the **Checkpoint Auditor**, the verification subagent. Your role is to audit the composed agent prompt before spawn. See "Checkpoint Auditor Overview" section above for full conventions.

Audit the following Crumb Gatherer prompt for completeness and correctness.
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
7. **Line number specificity**: File paths include specific line ranges or section markers
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
> Recommendation: Rewrite prompt with actual file paths (e.g., `build.py:L200-215`) and explicit scope boundaries before re-running pre-spawn-check.

Write your verification report to:

**Batch mode (most common):** `{SESSION_DIR}/pc/pc-session-pre-spawn-check-impl-{timestamp}.md`
- Use when the Queen runs pre-spawn-check over all Crumb Gatherer prompts for a wave in a single audit.
- The suffix `impl` distinguishes this artifact from the Reviewer pre-spawn-check (`pre-spawn-check-review`) in the same session.

**Per-task mode (single-prompt audit):** `{SESSION_DIR}/pc/pc-{TASK_SUFFIX}-pre-spawn-check-{timestamp}.md`
- Use only when auditing a single Crumb Gatherer prompt in isolation.
- Example: `{SESSION_DIR}/pc/pc-74g1-pre-spawn-check-{timestamp}.md`

Where:
- `{TASK_SUFFIX}`: suffix portion of crumb ID with no project prefix (e.g., `74g1` from `my-project-74g.1`)
- `{SESSION_DIR}`: session artifact directory (e.g., `.crumbs/sessions/_session-abc123`)
- timestamp: format defined in **Timestamp format** (Checkpoint Auditor Overview)
```

### The Reviewers

**When**: After composing all review prompts (round 1: 4 prompts; round 2+: 2 prompts), BEFORE creating the team
**Model**: `haiku`

```markdown
**Checkpoint Auditor verification - pre-spawn-check (Pre-Spawn Reviewers Audit)**

You are the **Checkpoint Auditor**, the verification subagent. Your role is to audit the reviewer prompts before spawn.

**Review round**: {REVIEW_ROUND}
**Input guard**: If {REVIEW_ROUND} still appears as the literal text `{REVIEW_ROUND}` (curly braces present), or is missing, blank, or non-numeric (not a positive integer), return the following message and do NOT proceed with the audit:

"pre-spawn-check ABORTED: REVIEW_ROUND placeholder was not substituted before spawning pre-spawn-check (got: '{REVIEW_ROUND}'). Root cause: upstream substitution failure — the Queen or Pantry did not replace `{REVIEW_ROUND}` in the pre-spawn-check prompt before dispatch. Fix: ensure the prompt-composition step fills in REVIEW_ROUND as a plain integer (e.g. `1`) before spawning the Checkpoint Auditor."

Audit the following reviewer prompts for completeness and consistency.
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
   > **Known limitation**: The commit range is Queen-provided. If the Queen passes incorrect commit hashes (e.g., too narrow or too broad), this check validates against wrong ground truth. There is no independent way for the Checkpoint Auditor to derive the "correct" commit range. Mitigation: scope-verify (Post-Commit Scope Verification) independently validates per-task scope after each agent commits, catching scope errors that slip through here.
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
7. **Messaging guidelines**: Each prompt includes guidance on when to message other reviewers

## Verdict
- **PASS** — All 7 checks pass for all prompts in scope for this round
- **FAIL: <list each failing check, specifying which prompt(s)>**

Write your verification report to:
`{SESSION_DIR}/pc/pc-session-pre-spawn-check-review-{timestamp}.md`

Where:
- `{SESSION_DIR}`: session artifact directory (e.g., `.crumbs/sessions/_session-abc123`)
- timestamp: format defined in **Timestamp format** (Checkpoint Auditor Overview)
```

### The Queen's Response

**On PASS**: Proceed to spawn the agent(s) or create the team.

**On FAIL**: Fix the specific gaps in the prompt(s), then re-run pre-spawn-check. Do NOT spawn until PASS.

---

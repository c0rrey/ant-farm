# Pest Control Verification - CCO (Pre-Spawn Prompt Audit)

**Session**: _session-86c76859
**Checkpoint**: CCO - Dirt Pusher Pre-Spawn Audit
**Timestamp**: 20260223-030145
**Audited Prompts**: 3 (task-q59z, task-vxcn, task-m4si)

---

## Summary

All 3 Dirt Pusher preview prompts PASS the CCO verification. Each prompt contains actual task IDs, real file paths with line numbers, specific root cause text, all 6 mandatory workflow steps, explicit scope boundaries, proper git instructions, and line-level specificity.

---

## Per-Prompt Audit

### Prompt 1: task-q59z (Big Head CCB Timeout)

**Verdict: PASS**

**Check 1 (Real task IDs)**: PASS
- Contains `ant-farm-q59z` (actual task ID), not placeholder
- Task ID appears in Step 1 claim, Step 5 commit message template, and Step 6 summary path

**Check 2 (Real file paths)**: PASS
- Specific line ranges provided:
  - `orchestration/templates/reviews.md:L774-805` (Step 4 timeout/retry protocol)
  - `orchestration/templates/big-head-skeleton.md:L121-124` (Step 10 await instructions)
- Both paths include line numbers and contextual line ranges (L770-810 and L115-135 for reading context)

**Check 3 (Root cause text)**: PASS
- Explicit root cause provided: "After sending the consolidated report path to Pest Control, Big Head runs `sleep 60` in Bash to 'wait' for the reply... When the sleep completes, Big Head is already in the timeout branch and declares failure."
- Root cause explains the mechanism and timing issue
- Not a placeholder like `<copy from bead>`

**Check 4 (All 6 mandatory steps)**: PASS
- Step 1: `bd show ant-farm-q59z` + `bd update ant-farm-q59z --status=in_progress` (line 8)
- Step 2: "Design (MANDATORY) — 4+ genuinely distinct approaches" (line 9)
- Step 3: "Implement: Write clean, minimal code satisfying acceptance criteria" (line 10)
- Step 4: "Review (MANDATORY) — Re-read EVERY changed file" (line 11)
- Step 5: `git pull --rebase && git add <changed-files> && git commit` with task ID (lines 12-13)
- Step 6: Write summary doc to `.beads/agent-summaries/_session-86c76859/summaries/q59z.md` then `bd close ant-farm-q59z` (lines 14-16)

**Check 5 (Scope boundaries)**: PASS
- Explicit "Read ONLY" section (lines 42-44) listing:
  - `orchestration/templates/reviews.md:L770-810`
  - `orchestration/templates/big-head-skeleton.md:L115-135`
- Explicit "Do NOT edit" section (lines 46-50) with 5 exclusions
- No open-ended "explore the codebase" language

**Check 6 (Commit instructions)**: PASS
- Step 5 includes `git pull --rebase` before commit (line 12)
- Conventional commit format specified with task ID template

**Check 7 (Line number specificity)**: PASS
- File paths include specific line ranges: `L774-805`, `L121-124` for target edits, plus context ranges `L770-810`, `L115-135` for reading
- Example: "Edit big-head-skeleton.md lines 121-124 (Step 10 await instructions)" provides both file and line specificity
- Not vague file-level edits

---

### Prompt 2: task-vxcn (Pantry Preview File Missing)

**Verdict: PASS**

**Check 1 (Real task IDs)**: PASS
- Contains `ant-farm-vxcn` (actual task ID), not placeholder
- Task ID appears in Step 1, Step 5 commit, and Step 6 summary path

**Check 2 (Real file paths)**: PASS
- Specific line ranges provided:
  - `orchestration/templates/pantry.md:L141-169` (Step 3 and Step 4 where preview file is mentioned)
- Reading scope specified as `L141-210` (lines 40) to include full context through Step 5
- Do NOT edit boundaries include `L1-140` and `L214-418` (lines 43-44)

**Check 3 (Root cause text)**: PASS
- Explicit root cause: "The Pantry agent writes the task brief to prompts/task-{suffix}.md but returns without writing the combined preview to previews/task-{suffix}-preview.md. The agent narrates the step but exits before executing it."
- Root cause explains both the narration without execution and the missing verification
- Includes filename patterns: `prompts/task-{suffix}.md` and `previews/task-{suffix}-preview.md`

**Check 4 (All 6 mandatory steps)**: PASS
- Step 1: `bd show ant-farm-vxcn` + `bd update ant-farm-vxcn --status=in_progress` (line 8)
- Step 2: "Design (MANDATORY) — 4+ genuinely distinct approaches" (line 9)
- Step 3: "Implement: Write clean, minimal code satisfying acceptance criteria" (line 10)
- Step 4: "Review (MANDATORY) — Re-read EVERY changed file" (line 11)
- Step 5: `git pull --rebase && git add <changed-files> && git commit` with task ID (lines 12-13)
- Step 6: Write summary to `.beads/agent-summaries/_session-86c76859/summaries/vxcn.md` then `bd close ant-farm-vxcn` (lines 14-16)

**Check 5 (Scope boundaries)**: PASS
- Explicit "Read ONLY" section (lines 39-40) with `orchestration/templates/pantry.md:L141-210` as target range
- Explicit "Do NOT edit" section (lines 42-48) with 6 exclusions:
  - Lines 1-140 of pantry.md (earlier steps)
  - Lines 214-418 of pantry.md (deprecated section)
  - RULES.md
  - dirt-pusher-skeleton.md
  - implementation.md
  - All scripts/ files
- Focused scope on preview writing and verification steps only

**Check 6 (Commit instructions)**: PASS
- Step 5 includes `git pull --rebase` before commit (line 12)
- Conventional commit type specified

**Check 7 (Line number specificity)**: PASS
- Target lines specified: `L141-169` for Steps 3-4 where preview file is mentioned
- Context range specified: `L141-210` to include Steps 3-5 for full verification understanding
- Not a vague file-level edit; editing is scoped to specific step sections

---

### Prompt 3: task-m4si (Progress Log Key Naming)

**Verdict: PASS**

**Check 1 (Real task IDs)**: PASS
- Contains `ant-farm-m4si` (actual task ID), not placeholder
- Task ID appears in Step 1, Step 5 commit, and Step 6 summary path

**Check 2 (Real file paths)**: PASS
- Specific line provided:
  - `orchestration/RULES.md:L116` (progress log key `tasks_approved`)
  - Reading scope: `L110-125` (lines 41, with context for Step 1b)
  - Also lists `scripts/parse-progress-log.sh` (full file) for confirmation of any references

**Check 3 (Root cause text)**: PASS
- Explicit root cause: "The progress log line at orchestration/RULES.md:L116 was not fully updated when the user-approval gate was removed in ant-farm-fomy. The key name `tasks_approved=<N>` implies a human approved the task list, which is no longer accurate -- approval is now automatic after SSV PASS."
- Root cause explains the stale semantic (word "approved" no longer reflects automation)
- Includes reference to prior commit (ant-farm-fomy) that introduced the change context
- Explains that derivation of `<N>` is unspecified

**Check 4 (All 6 mandatory steps)**: PASS
- Step 1: `bd show ant-farm-m4si` + `bd update ant-farm-m4si --status=in_progress` (line 8)
- Step 2: "Design (MANDATORY) — 4+ genuinely distinct approaches" (line 9)
- Step 3: "Implement: Write clean, minimal code satisfying acceptance criteria" (line 10)
- Step 4: "Review (MANDATORY) — Re-read EVERY changed file" (line 11)
- Step 5: `git pull --rebase && git add <changed-files> && git commit` with task ID (lines 12-13)
- Step 6: Write summary to `.beads/agent-summaries/_session-86c76859/summaries/m4si.md` then `bd close ant-farm-m4si` (lines 14-16)

**Check 5 (Scope boundaries)**: PASS
- Explicit "Read ONLY" section (lines 40-42):
  - `orchestration/RULES.md:L110-125` (context for Step 1b)
  - `scripts/parse-progress-log.sh` (full file for reference confirmation)
- Explicit "Do NOT edit" section (lines 44-47):
  - RULES.md outside L116 area
  - All orchestration/templates/
  - scripts/parse-progress-log.sh (unless a reference is discovered)
- Clear restriction to progress log line only

**Check 6 (Commit instructions)**: PASS
- Step 5 includes `git pull --rebase` before commit (line 12)
- Conventional commit type specified with task ID

**Check 7 (Line number specificity)**: PASS
- Specific line number provided: `L116` for the progress log key
- Context range provided: `L110-125` for Step 1b context
- Not a vague file-level edit; editing is scoped to the specific line and derivation documentation

---

## Cross-Prompt Consistency Check

All 3 prompts follow the same structure and quality standard:
- Identical 6-step workflow format
- All use the same git pull --rebase pattern
- All reference correct session directory and summary paths
- All include explicit scope boundaries with "Read ONLY" and "Do NOT edit" sections
- All specify line numbers with context ranges
- All include full task brief with acceptance criteria
- All explicitly state "Do NOT push to remote. Do NOT modify CHANGELOG/README/CLAUDE.md."

No cosmetic placeholder issues detected. No missing mandatory keywords. No scope ambiguity.

---

## Verdict

**PASS**

All 7 checks pass for all 3 prompts. No exceptions or clarifications needed. The prompts are ready for agent spawn.

**Recommendation**: Proceed to spawn all 3 Dirt Pushers in parallel.

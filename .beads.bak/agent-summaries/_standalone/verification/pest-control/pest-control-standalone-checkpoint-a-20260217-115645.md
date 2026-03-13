# Pest Control -- Checkpoint A (Pre-Spawn Prompt Audit)

**Timestamp**: 2026-02-17 11:56:45
**Epic**: _standalone
**Previews audited**: 4

---

## Preview 1: agent-1-rules-batch-preview.md

**Tasks in batch**: ant-farm-6jv, ant-farm-e9w, ant-farm-fr2, ant-farm-tsw (sequential -- all modify RULES.md)

### Check 1: Real task IDs
**PASS** -- All 4 tasks use real IDs: `ant-farm-6jv`, `ant-farm-e9w`, `ant-farm-fr2`, `ant-farm-tsw`. No placeholders like `<task-id>` found.

### Check 2: Real file paths
**PASS** -- Each task's data file section contains specific file paths with line numbers:
- 6jv: `~/.claude/orchestration/RULES.md:L61-69` (Information Diet section)
- e9w: `~/.claude/orchestration/RULES.md:L27-28`, `~/.claude/orchestration/RULES.md:L97-111`
- fr2: `~/.claude/orchestration/RULES.md:L14-16`, `~/.claude/orchestration/RULES.md:L18-25`, `~/.claude/orchestration/RULES.md:L27-33`, `~/.claude/orchestration/RULES.md:L83-86`
- tsw: `~/.claude/orchestration/RULES.md:L86`

No placeholder text like `<list from bead>` or `<file>` found.

### Check 3: Root cause text
**PASS** -- Each task contains a specific root cause:
- 6jv: "RULES.md Information Diet at L67 says 'DO NOT READ: source code, tests, data files, configs...' but 'data files' is ambiguous..."
- e9w: "RULES.md says the Queen creates epic directories at Step 2 (L27-28, L97-111) but provides no explicit timing relative to Pantry spawn..."
- fr2: "RULES.md Step 0 (L14-16, L83-86) generates SESSION_ID and creates the session dir. Step 1 (L19) says to pass 'session dir path' to the Scout. But RULES.md does not show HOW..."
- tsw: "Pantry writes data files to {session-dir}/prompts/ but nobody creates that directory. RULES.md Step 0 at L86 creates {session-dir}/{task-metadata,previews} but prompts/ is not included..."

All root causes are specific descriptions, not placeholders.

### Check 4: All 6 mandatory steps present
**PASS** -- Each of the 4 task blocks contains all 6 steps:
1. Step 1 (Claim): `bd show ant-farm-XXX` + `bd update ant-farm-XXX --status=in_progress` -- PRESENT for all 4
2. Step 2 (Design): "4+ genuinely distinct approaches" with MANDATORY keyword -- PRESENT for all 4
3. Step 3 (Implement): "Write clean, minimal code satisfying acceptance criteria" -- PRESENT for all 4
4. Step 4 (Review): "Re-read EVERY changed file" with MANDATORY keyword -- PRESENT for all 4
5. Step 5 (Commit): `git pull --rebase` + commit with task ID -- PRESENT for all 4
6. Step 6 (Summary doc): Write to `.beads/agent-summaries/_standalone/XXX.md` -- PRESENT for all 4

### Check 5: Scope boundaries
**PASS** -- Each task has explicit scope boundaries:
- 6jv: "Read ONLY: `~/.claude/orchestration/RULES.md:L61-69`... Do NOT edit: Lines outside L61-69"
- e9w: "Read ONLY: `~/.claude/orchestration/RULES.md:L27-33`, `...L40-44`, `...L97-111`... Do NOT edit: Lines outside the Step 2, Step 3b, and Epic Artifact Directories sections"
- fr2: "Read ONLY: `~/.claude/orchestration/RULES.md:L14-33`, `...L81-95`... Do NOT edit: Lines outside Steps 0-2 and Session Directory sections"
- tsw: "Read ONLY: `~/.claude/orchestration/RULES.md:L83-86`... Do NOT edit: Lines outside L83-86"

Global scope statement also present: "SCOPE: Only edit files listed in the task context. Document adjacent issues, don't fix them."

### Check 6: Commit instructions
**PASS** -- All 4 task blocks include: `git pull --rebase && git add <changed-files> && git commit -m "<type>: <description> (ant-farm-XXX)"`. The batch footer also says "Run `git pull --rebase` to stack commits cleanly."

### Check 7: Line number specificity
**PASS** -- All file paths include specific line ranges:
- 6jv: L61-69 (9 lines, single section)
- e9w: L27-28, L40-44, L97-111 (specific ranges per section)
- fr2: L14-16, L18-25, L27-33, L83-86 (4 specific ranges)
- tsw: L86 (single line)

All line references verified against actual RULES.md content:
- L61-69 is indeed the Information Diet section. Confirmed: L67 contains "data files".
- L86 is indeed the mkdir command: `mkdir -p .beads/agent-summaries/_session-${SESSION_ID}/{task-metadata,previews}` -- confirmed missing `prompts/`.
- L83-86 is indeed the Session Directory section start.

### Line Number Accuracy Spot-Check
Verified critical claims against actual file content:
- **6jv claims L67 says "DO NOT READ: source code, tests, data files, configs..."**: CONFIRMED. Actual L67: `**DO NOT READ:** source code, tests, data files, configs, implementation.md, checkpoints.md, reviews.md,`
- **tsw claims L86 mkdir creates {task-metadata,previews} but not prompts/**: CONFIRMED. Actual L86: `mkdir -p .beads/agent-summaries/_session-${SESSION_ID}/{task-metadata,previews}` -- no `prompts/` in brace expansion.
- **e9w claims L97-111 is Epic Artifact Directories**: CONFIRMED. L97 heading: `## Epic Artifact Directories`.

### Batch Structure Check
**PASS** -- Preview correctly identifies this as a sequential batch (all 4 tasks modify RULES.md). This is appropriate because concurrent edits to the same file would cause merge conflicts. The batch footer instructs `bd close` for all 4 tasks after completion.

**VERDICT: PASS** -- All 7 checks pass for all 4 tasks in this batch.

---

## Preview 2: agent-2-checkpoints-pantry-batch-preview.md

**Tasks in batch**: ant-farm-af0, ant-farm-iih (sequential -- af0 modifies pantry.md + checkpoints.md, iih modifies checkpoints.md)

### Check 1: Real task IDs
**PASS** -- Both tasks use real IDs: `ant-farm-af0`, `ant-farm-iih`. No placeholders found.

### Check 2: Real file paths
**PASS** -- Specific file paths with line numbers:
- af0: `~/.claude/orchestration/templates/pantry.md:L97-98`, `~/.claude/orchestration/templates/checkpoints.md:L45`
- iih: `~/.claude/orchestration/templates/checkpoints.md:L134`

### Check 3: Root cause text
**PASS** -- Specific root causes:
- af0: "pantry.md Section 2 Step 2 at L97-98 says 'Generate a single review timestamp' -- implying the Pantry generates it. checkpoints.md at L45 says 'The Queen generates a single timestamp per review cycle' -- implying the Queen generates it."
- iih: "checkpoints.md CCO section for review prompts at L134 says 'Run git diff --name-only <first-commit>..<last-commit>' but does not explain how Pest Control receives these commit range values."

### Check 4: All 6 mandatory steps present
**PASS** -- Both task blocks contain all 6 steps with correct structure, MANDATORY keywords for Design and Review, `git pull --rebase` in commit step.

### Check 5: Scope boundaries
**PASS** -- Explicit scope boundaries:
- af0: "Read ONLY: `~/.claude/orchestration/templates/pantry.md:L89-125`, `~/.claude/orchestration/templates/checkpoints.md:L43-46`... Do NOT edit: Any sections of pantry.md outside Section 2 Steps 1-4. Any sections of checkpoints.md outside the review timestamp convention paragraph."
- iih: "Read ONLY: `~/.claude/orchestration/templates/checkpoints.md:L108-157`... Do NOT edit: Any sections of checkpoints.md outside the Nitpickers Checkpoint A section."

### Check 6: Commit instructions
**PASS** -- Both include `git pull --rebase && git add <changed-files> && git commit`.

### Check 7: Line number specificity
**PASS** -- All references are line-specific:
- af0: pantry.md:L97-98, checkpoints.md:L45, pantry.md:L89-125, checkpoints.md:L43-46
- iih: checkpoints.md:L134, checkpoints.md:L108-157

### Line Number Accuracy Spot-Check
- **af0 claims pantry.md L97-98 says "Generate a single review timestamp"**: CONFIRMED. Actual L96-98: `### Step 2: Generate Timestamp` / (blank) / `Generate a single review timestamp: \`YYYYMMDD-HHMMSS\` format.`
- **af0 claims checkpoints.md L45 says "The Queen generates a single timestamp per review cycle"**: CONFIRMED. Actual L45: `**Review timestamp convention**: The Queen generates a single timestamp per review cycle...`
- **iih claims checkpoints.md L134 says "Run git diff --name-only <first-commit>..<last-commit>"**: CONFIRMED. Actual L134: `0. **File list matches git diff**: Run \`git diff --name-only <first-commit>..<last-commit>\`...`

### Batch Structure Check
**PASS** -- Sequential batch is correct: both af0 and iih modify checkpoints.md (af0 modifies pantry.md + checkpoints.md, iih modifies checkpoints.md), so they cannot run concurrently.

**VERDICT: PASS** -- All 7 checks pass for both tasks in this batch.

---

## Preview 3: agent-3-big-head-skeleton-preview.md

**Task**: ant-farm-obd (single task)

### Check 1: Real task IDs
**PASS** -- Uses real ID `ant-farm-obd`. No placeholders.

### Check 2: Real file paths
**PASS** -- Specific paths: `~/.claude/orchestration/templates/big-head-skeleton.md:L1-37`, `~/.claude/orchestration/RULES.md:L40-44`, `~/.claude/orchestration/RULES.md:L135`

### Check 3: Root cause text
**PASS** -- "big-head-skeleton.md uses {PLACEHOLDER} syntax (L5, L9-11) as if it were a Task tool template, but Big Head is actually a team member spawned via TeamCreate + SendMessage, not a standalone Task agent."

### Check 4: All 6 mandatory steps present
**PASS** -- All 6 steps present with MANDATORY keywords and correct structure.

### Check 5: Scope boundaries
**PASS** -- "Read ONLY: `~/.claude/orchestration/templates/big-head-skeleton.md:L1-37`, `~/.claude/orchestration/RULES.md:L40-44`... Do NOT edit: RULES.md (the fix belongs in big-head-skeleton.md). Do NOT edit any other template files."

### Check 6: Commit instructions
**PASS** -- `git pull --rebase && git add <changed-files> && git commit`.

### Check 7: Line number specificity
**PASS** -- big-head-skeleton.md:L1-37 (entire file, which is only 37 lines -- appropriate). RULES.md:L40-44 (specific 5-line range for Step 3b). RULES.md:L135 (single line, Template Lookup Big Head entry).

### Line Number Accuracy Spot-Check
- **Claims big-head-skeleton.md L5 uses {PLACEHOLDER}**: CONFIRMED. Actual L5: `Fill in all \`{PLACEHOLDER}\` values (uppercase) and use the result as the Task tool \`prompt\` parameter.`
- **Claims big-head-skeleton.md L9-11 has placeholder definitions**: CONFIRMED. Actual L9-11: `- {DATA_FILE_PATH}`, `- {EPIC_ID}`, `- {CONSOLIDATED_OUTPUT_PATH}`
- **Claims the file is 37 lines (L1-37)**: CONFIRMED. The file ends at L37.
- **Claims RULES.md L40-44 mentions Big Head in Step 3b**: CONFIRMED. L40-44: `**Step 3b:** Review -- spawn the Pantry (review mode)... After team completes, spawn Pest Control for B + C`

### Scope Constraint Check
**PASS** -- The scope correctly prohibits editing RULES.md ("Do NOT edit: RULES.md (the fix belongs in big-head-skeleton.md)") while allowing reads of RULES.md L40-44 for context. This is correct since the affected-files list includes RULES.md as read-only context.

**VERDICT: PASS** -- All 7 checks pass.

---

## Preview 4: agent-4-dirt-pusher-skeleton-preview.md

**Task**: ant-farm-9oa (single task)

### Check 1: Real task IDs
**PASS** -- Uses real ID `ant-farm-9oa`. No placeholders.

### Check 2: Real file paths
**PASS** -- Specific paths: `~/.claude/orchestration/templates/dirt-pusher-skeleton.md:L8-11`, `~/.claude/orchestration/templates/dirt-pusher-skeleton.md:L18-36`

### Check 3: Root cause text
**PASS** -- "dirt-pusher-skeleton.md defines {TASK_TYPE}, {DATA_FILE_PATH}, {SUMMARY_OUTPUT_PATH} in its placeholder list at L8-11, and also defines {TASK_ID} at L10. However... the definition does not clarify whether TASK_ID is the full ID (e.g., ant-farm-9oa) or a suffix (e.g., 9oa), and the example uses the hs_website project format rather than a generic format."

### Check 4: All 6 mandatory steps present
**PASS** -- All 6 steps present with MANDATORY keywords and correct structure.

### Check 5: Scope boundaries
**PASS** -- "Read ONLY: `~/.claude/orchestration/templates/dirt-pusher-skeleton.md:L1-37`... Do NOT edit: Any other template files. Do NOT edit RULES.md or implementation.md."

### Check 6: Commit instructions
**PASS** -- `git pull --rebase && git add <changed-files> && git commit`.

### Check 7: Line number specificity
**PASS** -- dirt-pusher-skeleton.md:L8-11 (placeholder definitions, 4 lines), L18-36 (template body, 19 lines), L1-37 (entire file for read scope, file is 37 lines).

### Line Number Accuracy Spot-Check
- **Claims L8-11 is placeholder definitions list**: CONFIRMED. Actual L8-11: `Placeholders:` / `- {TASK_TYPE}: bead type (bug/feature/task)` / `- {TASK_ID}: full bead ID (e.g., hs_website-74g.1)` / `- {DATA_FILE_PATH}: from the Pantry verdict table`
- **Claims L10 defines {TASK_ID} as "full bead ID (e.g., hs_website-74g.1)"**: CONFIRMED. Actual L10: `- {TASK_ID}: full bead ID (e.g., hs_website-74g.1)`
- **Claims {TASK_ID} is used at L18, L25, L29, L36**: CONFIRMED. L18: `Execute {TASK_TYPE} for {TASK_ID}.`, L25: `bd show {TASK_ID}` + `bd update {TASK_ID}`, L29: `git commit -m "... ({TASK_ID})"`, L36: `bd close {TASK_ID}`
- **Claims the example uses hs_website project format**: CONFIRMED. L10 says `e.g., hs_website-74g.1`.

**VERDICT: PASS** -- All 7 checks pass.

---

## Cross-Preview Checks

### File Conflict Analysis
The batch structure correctly serializes file conflicts:
- **Preview 1** (agent-1): 4 tasks all modify RULES.md -- sequential batch. CORRECT.
- **Preview 2** (agent-2): 2 tasks sharing checkpoints.md -- sequential batch. CORRECT.
- **Preview 3** (agent-3): modifies big-head-skeleton.md only. No conflict with others. Can run concurrently.
- **Preview 4** (agent-4): modifies dirt-pusher-skeleton.md only. No conflict with others. Can run concurrently.

Agents 1 and 2 both touch RULES.md indirectly (agent-1 tasks modify RULES.md, agent-2's af0 scope says "Do NOT edit RULES.md or any other files" -- only pantry.md and checkpoints.md). No cross-agent file conflict.

### Data File Integrity
All 8 task data files exist in `{session-dir}/prompts/` and match the content embedded in the previews exactly. No orphaned or missing data files.

### Summary Output Path Consistency
All tasks correctly specify `.beads/agent-summaries/_standalone/{suffix}.md` for summary docs, consistent with epic ID `_standalone`.

---

## OVERALL VERDICT: PASS

All 4 previews pass all 7 Checkpoint A criteria. No fabricated data, no placeholder text, no missing steps, no vague scope boundaries. Line number claims verified against source files. Batch serialization is correct for file conflicts.

Ready to spawn.

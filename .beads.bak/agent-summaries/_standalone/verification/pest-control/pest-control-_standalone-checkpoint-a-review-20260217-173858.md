# Pest Control - Checkpoint A: Pre-Spawn Nitpickers Audit

**Timestamp**: 2026-02-17T17:38:58Z
**Epic ID**: _standalone
**Session**: _session-ae4401

**Prompts audited**:
1. `/Users/correy/projects/ant-farm/.beads/agent-summaries/_session-ae4401/previews/review-clarity-preview.md`
2. `/Users/correy/projects/ant-farm/.beads/agent-summaries/_session-ae4401/previews/review-edge-cases-preview.md`
3. `/Users/correy/projects/ant-farm/.beads/agent-summaries/_session-ae4401/previews/review-correctness-preview.md`
4. `/Users/correy/projects/ant-farm/.beads/agent-summaries/_session-ae4401/previews/review-excellence-preview.md`

---

## Check 0: File list matches git diff -- PASS

**Method**: Ran `git diff --name-only 992f7c8..54b59cf`

**Git diff files** (repo-relative paths):
- `orchestration/RULES.md`
- `orchestration/templates/big-head-skeleton.md`
- `orchestration/templates/checkpoints.md`
- `orchestration/templates/dirt-pusher-skeleton.md`
- `orchestration/templates/pantry.md`

**Prompt file lists** (all 4 prompts use identical list):
- `~/.claude/orchestration/RULES.md`
- `~/.claude/orchestration/templates/pantry.md`
- `~/.claude/orchestration/templates/checkpoints.md`
- `~/.claude/orchestration/templates/big-head-skeleton.md`
- `~/.claude/orchestration/templates/dirt-pusher-skeleton.md`

**Analysis**: Same 5 files in both lists. Prompts use `~/.claude/orchestration/` prefix while git diff uses repo-relative `orchestration/` prefix. The repo copies are the canonical versioned source; `~/.claude/` is a deployment location synced from the repo. Both point to the same logical files.

**Note**: A `diff` of `~/.claude/orchestration/RULES.md` vs the repo copy shows they are currently out of sync (the repo version has updates from commits in the range). Reviewers reading from `~/.claude/` may see stale content. This is a deployment sync concern, not a prompt composition defect -- the prompt correctly references the files that were changed.

No missing files. No extra files. **PASS**.

---

## Check 1: Same file list -- PASS

All 4 prompts contain the identical 5-file list:
- `~/.claude/orchestration/RULES.md`
- `~/.claude/orchestration/templates/pantry.md`
- `~/.claude/orchestration/templates/checkpoints.md`
- `~/.claude/orchestration/templates/big-head-skeleton.md`
- `~/.claude/orchestration/templates/dirt-pusher-skeleton.md`

**Evidence**: Clarity preview line 37-41, Edge Cases preview line 37-41, Correctness preview line 37-41, Excellence preview line 37-41. All identical. **PASS**.

---

## Check 2: Same commit range -- PASS

All 4 prompts specify:
- **Commit range**: `992f7c8..54b59cf`

**Evidence**:
- Clarity preview line 30: `**Commit range**: 992f7c8..54b59cf`
- Edge Cases preview line 31: `**Commit range**: 992f7c8..54b59cf`
- Correctness preview line 31: `**Commit range**: 992f7c8..54b59cf`
- Excellence preview line 31: `**Commit range**: 992f7c8..54b59cf`

Both commits verified to exist via `git rev-parse`. The range contains 10 commits. **PASS**.

---

## Check 3: Correct focus areas -- PASS

Each prompt has focus areas specific to its review type:

**Clarity** (preview lines 45-49): Code readability, Documentation, Consistency, Naming, Structure.
**Edge Cases** (preview lines 45-50): Input validation, Error handling, Boundary conditions, File operations, Concurrency, Platform differences.
**Correctness** (preview lines 45-50): Acceptance criteria verification, Logic correctness, Data integrity, Regression risks, Cross-file consistency, Algorithm correctness.
**Excellence** (preview lines 45-51): Best practices, Performance, Security, Maintainability, Architecture, Scalability, Modern features.

**Analysis**: All four have distinct, non-overlapping focus areas appropriate to their review type. No copy-paste duplication detected. The correctness prompt additionally includes a Task-to-File Mapping table (lines 63-78) with 10 specific task IDs and their commit hashes/files -- this is valuable extra context. **PASS**.

---

## Check 4: No bead filing instruction -- PASS

All 4 prompts contain explicit prohibition:

- Clarity preview line 21: `Do NOT file beads (\`bd create\`) -- Big Head handles all bead filing.`
- Edge Cases preview line 21: `Do NOT file beads (\`bd create\`) -- Big Head handles all bead filing.`
- Correctness preview line 21: `Do NOT file beads (\`bd create\`) -- Big Head handles all bead filing.`
- Excellence preview line 21: `Do NOT file beads (\`bd create\`) -- Big Head handles all bead filing.`

Each prompt also repeats the instruction in the Report section (clarity L61, edge-cases L59, correctness L62, excellence L60). **PASS**.

---

## Check 5: Report format reference -- PASS

Each prompt specifies the correct output path matching the pattern `.beads/agent-summaries/{EPIC_ID}/review-reports/{type}-review-{timestamp}.md`:

- Clarity preview line 31: `.beads/agent-summaries/_standalone/review-reports/clarity-review-20260217-120000.md`
- Edge Cases preview line 32: `.beads/agent-summaries/_standalone/review-reports/edge-cases-review-20260217-120000.md`
- Correctness preview line 32: `.beads/agent-summaries/_standalone/review-reports/correctness-review-20260217-120000.md`
- Excellence preview line 32: `.beads/agent-summaries/_standalone/review-reports/excellence-review-20260217-120000.md`

All use the same timestamp `20260217-120000`, consistent with the review timestamp convention (Queen generates a single timestamp per review cycle). Epic ID `_standalone` is correct per the task context. **PASS**.

---

## Check 6: Messaging guidelines -- PASS

All 4 prompts include a "Messaging Guidelines" section with identical guidance:

**Evidence**:
- Clarity preview lines 66-74
- Edge Cases preview lines 70-80
- Correctness preview lines 89-99
- Excellence preview lines 73-83

Each includes:
- Three "SHOULD message" scenarios (cross-domain findings, coverage coordination, helpful context)
- Three "should NOT message" scenarios (status updates, general observations, Big Head questions)

**PASS**.

---

## Additional Observations

1. **Unfilled placeholders check**: Searched all 4 preview files for patterns `{UPPER_CASE}`, `<lower-case>`, `TODO`, `FIXME`, `PLACEHOLDER`, `TBD`. All matches found are inside the Nitpicker Report Format template section (e.g., `<reviewer>`, `<summary of message>`, `<file:line references>`) which are intentional formatting examples for the reviewers to fill in -- not unfilled prompt parameters. No genuine unfilled placeholders found.

2. **Correctness prompt bonus**: The correctness review prompt includes a detailed Task-to-File Mapping table (lines 65-78) with 10 concrete task IDs (`ant-farm-6jv`, `ant-farm-e9w`, etc.), their specific commit hashes, and files modified. It also instructs the reviewer to run `bd show <task-id>` for each task to retrieve acceptance criteria from the source of truth. This is substantially more detailed than the minimum requirement.

3. **File path sync concern (informational)**: The prompts direct reviewers to `~/.claude/orchestration/` paths. A diff shows the `~/.claude/` copy of `RULES.md` is out of sync with the repo version at `orchestration/RULES.md`. Reviewers may read stale content. This does not affect the prompt composition quality (which is what Checkpoint A validates), but may affect review accuracy downstream.

---

## Verdict: PASS

All 7 checks (0-6) pass. The four Nitpicker prompts are complete, consistent, and ready for team spawn.

| Check | Result | Summary |
|-------|--------|---------|
| 0. File list matches git diff | PASS | 5 files match exactly (path prefix difference is deployment vs repo) |
| 1. Same file list | PASS | All 4 prompts have identical 5-file scope |
| 2. Same commit range | PASS | All 4 use `992f7c8..54b59cf` (verified both exist) |
| 3. Correct focus areas | PASS | Distinct, type-appropriate focus areas in all 4 |
| 4. No bead filing instruction | PASS | All 4 include explicit `Do NOT file beads` prohibition |
| 5. Report format reference | PASS | All 4 specify correct output paths with shared timestamp |
| 6. Messaging guidelines | PASS | All 4 include when-to/when-not-to messaging guidance |

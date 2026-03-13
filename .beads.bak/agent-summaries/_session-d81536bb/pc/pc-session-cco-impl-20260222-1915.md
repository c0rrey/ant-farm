**Pest Control verification - CCO (Pre-Spawn Prompt Audit)**

**Session**: _session-d81536bb
**Timestamp**: 2026-02-22T19:15 UTC
**Auditor**: Pest Control
**Model**: Haiku

---

## Executive Summary

**Verdict: PASS**

Both Dirt Pusher prompts (task-68di1 and task-68di2) pass all 7 CCO checks. All mandatory components are present: real task IDs, actual file paths with line specificity, concrete root cause descriptions, all 6 mandatory steps, explicit scope boundaries, git rebase commit instructions, and line number specificity where applicable. The prompts are ready for agent spawn.

---

## Prompt 1: ant-farm-68di.1 (Create Scribe skeleton template)

### Check 1: Real task IDs
**Status**: PASS

Evidence:
- Task ID present: `ant-farm-68di.1` (line 23, section header)
- Referenced consistently in Step 1: `bd show ant-farm-68di.1` (line 8)
- Referenced in Step 5 commit format: `(ant-farm-68di.1)` (line 12)
- No placeholders detected. Real IDs throughout.

### Check 2: Real file paths
**Status**: PASS

Evidence:
- Actual file paths with line specificity:
  - `orchestration/templates/scribe-skeleton.md` — NEW FILE to create (line 30)
  - `orchestration/templates/dirt-pusher-skeleton.md:L27-32` — read-only reference (line 31)
  - `CHANGELOG.md:L1-50` — read-only reference (line 32)
  - `docs/plans/2026-02-22-exec-summary-scribe-design.md:L1-207` — read-only reference (line 33)
- All file paths are absolute (no relative paths)
- Line ranges provided where applicable (e.g., L1-50, L27-32, L1-207)
- No placeholders like `<list from bead>` or `<file>`

### Check 3: Root cause text
**Status**: PASS

Evidence:
- Root cause explicitly stated (line 34): "N/A (feature task). No Scribe skeleton template exists yet. The exec summary agent needs a skeleton template following the same structural pattern as the dirt-pusher-skeleton.md."
- Not a placeholder; contains specific context about why the template is needed
- Provides actionable baseline for agent understanding

### Check 4: All 6 mandatory steps present
**Status**: PASS

Evidence:
1. Step 1 (line 8): `bd show ant-farm-68di.1` + `bd update ant-farm-68di.1 --status=in_progress` ✓
2. Step 2 (line 9): "Design (MANDATORY) — 4+ genuinely distinct approaches with tradeoffs. Document choice before coding." ✓
3. Step 3 (line 10): "Implement": Write clean, minimal code satisfying acceptance criteria. ✓
4. Step 4 (line 11): "Review (MANDATORY) — Re-read EVERY changed file. Verify acceptance criteria. Assumptions audit." ✓ (MANDATORY keyword present)
5. Step 5 (line 12): Commit with `git pull --rebase && git add <changed-files> && git commit` ✓
6. Step 6 (lines 14-16): "Summary doc (MANDATORY) — Write to .beads/agent-summaries/_session-d81536bb/summaries/68di1.md" ✓

All 6 mandatory steps present with MANDATORY keywords in Steps 2 and 4.

### Check 5: Scope boundaries
**Status**: PASS

Evidence:
- Explicit scope boundaries section (lines 47-58)
- Read-only files clearly marked (lines 47-50):
  - orchestration/templates/dirt-pusher-skeleton.md:L1-48
  - CHANGELOG.md:L1-50
  - docs/plans/2026-02-22-exec-summary-scribe-design.md:L1-207
- Do NOT edit list (lines 52-58) explicitly prohibits adjacent modifications
- Scope is bounded to specific files and line ranges, not open-ended exploration

### Check 6: Commit instructions
**Status**: PASS

Evidence:
- Line 12 includes explicit git pull --rebase: `git pull --rebase && git add <changed-files> && git commit -m "<type>: <description> (ant-farm-68di.1)"`
- Specifies conventional commit type format
- Records commit hash requirement in summary doc
- No force push or destructive flags

### Check 7: Line number specificity
**Status**: PASS

Evidence:
- New file creation task: `orchestration/templates/scribe-skeleton.md — NEW FILE to create` (line 30) — file-level scope is appropriate for new file creation
- Read-only reference files have specific line ranges:
  - `dirt-pusher-skeleton.md:L27-32` (pattern reference)
  - `CHANGELOG.md:L1-50` (convention reference)
  - `docs/plans/2026-02-22-exec-summary-scribe-design.md:L1-207` (full design spec)
- Context provided for each reference (line 31-33 comments explain purpose)
- Appropriate specificity: for a new file, naming the file is sufficient; for read-only references, line ranges prevent scope creep

---

## Prompt 2: ant-farm-68di.2 (Add ESV checkpoint to checkpoints.md)

### Check 1: Real task IDs
**Status**: PASS

Evidence:
- Task ID present: `ant-farm-68di.2` (line 23, section header)
- Referenced in Step 1: `bd show ant-farm-68di.2` (line 8)
- Referenced in Step 5 commit format: `(ant-farm-68di.2)` (line 12)
- No placeholders detected. Real IDs throughout.

### Check 2: Real file paths
**Status**: PASS

Evidence:
- Actual file paths with line specificity:
  - `orchestration/templates/checkpoints.md:L1-723` — add new ESV section (line 30)
  - `docs/plans/2026-02-22-exec-summary-scribe-design.md:L121-145` — ESV checkpoint specification (line 44)
- All file paths are absolute (no relative paths)
- Line ranges provided (L1-723, L121-145)
- Specific insertion points referenced: "add new ESV section following existing checkpoint patterns (WWD at L270, DMVDC at L342, CCB at L507, SSV at L616)" (line 30)
- No placeholders

### Check 3: Root cause text
**Status**: PASS

Evidence:
- Root cause explicitly stated (line 31): "N/A (feature task). The ESV (Exec Summary Verification) checkpoint does not exist yet. It needs to be added to checkpoints.md so Pest Control can verify exec summary and CHANGELOG correctness before push."
- Not a placeholder; provides specific context about why the checkpoint is needed and its purpose
- Explains the role of the checkpoint in the verification pipeline

### Check 4: All 6 mandatory steps present
**Status**: PASS

Evidence:
1. Step 1 (line 8): `bd show ant-farm-68di.2` + `bd update ant-farm-68di.2 --status=in_progress` ✓
2. Step 2 (line 9): "Design (MANDATORY) — 4+ genuinely distinct approaches with tradeoffs. Document choice before coding." ✓
3. Step 3 (line 10): "Implement": Write clean, minimal code satisfying acceptance criteria. ✓
4. Step 4 (line 11): "Review (MANDATORY) — Re-read EVERY changed file. Verify acceptance criteria. Assumptions audit." ✓ (MANDATORY keyword present)
5. Step 5 (line 12): Commit with `git pull --rebase && git add <changed-files> && git commit` ✓
6. Step 6 (lines 14-16): "Summary doc (MANDATORY) — Write to .beads/agent-summaries/_session-d81536bb/summaries/68di2.md" ✓

All 6 mandatory steps present with MANDATORY keywords in Steps 2 and 4.

### Check 5: Scope boundaries
**Status**: PASS

Evidence:
- Explicit scope boundaries section (lines 41-50)
- Read-only files clearly marked (lines 42-44):
  - orchestration/templates/checkpoints.md:L1-723
  - docs/plans/2026-02-22-exec-summary-scribe-design.md:L121-145
- Do NOT edit list (lines 46-50) explicitly prohibits editing other checkpoint sections and adjacent files
- Scope is bounded to the new ESV section addition; does not permit modification of existing checkpoint patterns
- Insertion point guidance (line 30): "following the structural pattern of existing checkpoints (WWD at L270, DMVDC at L342, CCB at L507, SSV at L616)"

### Check 6: Commit instructions
**Status**: PASS

Evidence:
- Line 12 includes explicit git pull --rebase: `git pull --rebase && git add <changed-files> && git commit -m "<type>: <description> (ant-farm-68di.2)"`
- Specifies conventional commit type format
- Records commit hash requirement in summary doc
- No force push or destructive flags

### Check 7: Line number specificity
**Status**: PASS

Evidence:
- Edit target has specific line context: `orchestration/templates/checkpoints.md:L1-723 — add new ESV section following existing checkpoint patterns (WWD at L270, DMVDC at L342, CCB at L507, SSV at L616)` (line 30)
- Multiple reference line ranges to existing checkpoints for pattern matching:
  - WWD pattern at L270
  - DMVDC pattern at L342
  - CCB pattern at L507
  - SSV pattern at L616 (explicitly recommended as most recent pattern)
- Design spec reference: `docs/plans/2026-02-22-exec-summary-scribe-design.md:L121-145` (line 44)
- Focus section (line 55): "Follow the structural pattern of existing checkpoints (especially SSV at L616 as the most recently added checkpoint) for formatting conventions."
- High specificity: agent knows exactly which patterns to follow and where to insert the new section

---

## Cross-Prompt Consistency

Both prompts follow the identical structural template:
- Same mandatory step sequence (6 steps)
- Same scope boundary format (Read ONLY / Do NOT edit sections)
- Same commit instruction pattern (git pull --rebase)
- Same summary doc location format (.beads/agent-summaries/_session-d81536bb/summaries/{TASK_SUFFIX}.md)
- Same acceptance criteria checklist requirement

No conflicts detected.

---

## Verdict: PASS

**All 7 checks PASS for both prompts.**

Passing checks:
1. Real task IDs — both prompts use actual task IDs (ant-farm-68di.1, ant-farm-68di.2)
2. Real file paths — both prompts contain actual file paths with line specificity
3. Root cause text — both prompts include specific, concrete root cause descriptions (not placeholders)
4. All 6 mandatory steps — both prompts include all mandatory steps with keyword markers
5. Scope boundaries — both prompts explicitly limit scope with Read ONLY and Do NOT edit sections
6. Commit instructions — both prompts include `git pull --rebase` before commit
7. Line number specificity — both prompts provide line ranges and contextual guidance; new file creation and section insertion are appropriately scoped

**Recommendation**: Proceed to spawn both Dirt Pusher agents. Both prompts are complete and ready for execution.

---

## Artifact Metadata

- **Session directory**: .beads/agent-summaries/_session-d81536bb
- **Output path**: .beads/agent-summaries/_session-d81536bb/pc/pc-session-cco-impl-20260222-1915.md
- **Checkpoint type**: CCO (Dirt Pushers)
- **Verdict threshold**: All 7 checks must pass for PASS verdict
- **Tie-breaking rule**: First-listed section/function (N/A — all checks pass)

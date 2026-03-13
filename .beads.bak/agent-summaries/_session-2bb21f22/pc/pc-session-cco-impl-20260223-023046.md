# Pest Control Verification: CCO (Pre-Spawn Prompt Audit)

**Session**: _session-2bb21f22
**Wave**: 2 (fix wave)
**Timestamp**: 2026-02-23 02:30:46 UTC
**Checkpoint**: Colony Cartography Office (CCO) - Dirt Pusher prompts
**Auditor**: Pest Control

---

## Summary

This audit verifies the Dirt Pusher prompts composed for Wave 2 (fix wave) before agent spawn.

- **Prompts audited**: 2 (ant-farm-i7wl + ant-farm-sfe0 combined; ant-farm-or8q)
- **Total checks**: 7 per prompt (14 total)
- **Overall verdict**: PASS

---

## Prompt 1: ant-farm-i7wl + ant-farm-sfe0 (combined)

**File**: `.beads/agent-summaries/_session-2bb21f22/previews/task-i7wl-sfe0-preview.md`
**Lines**: 72
**Task IDs**: ant-farm-i7wl, ant-farm-sfe0
**Summary output path**: `.beads/agent-summaries/_session-2bb21f22/summaries/i7wl-sfe0.md`

### Check 1: Real task IDs
**Status**: PASS

Evidence:
- Line 8 contains actual task ID `ant-farm-i7wl` (not placeholder)
- Line 8 contains actual task ID `ant-farm-sfe0` (not placeholder)
- No `<task-id>` or `<id>` placeholders detected

### Check 2: Real file paths with line numbers
**Status**: PASS

Evidence:
- Line 30: `orchestration/RULES.md:97-99` (actual path with line range)
- Line 31: `orchestration/RULES.md:100-101` (actual path with line range)
- Line 32: `orchestration/RULES.md:516-526` (actual path with line range)
- Line 33: `orchestration/RULES.md:28` (actual path with line number)
- Line 34: `orchestration/RULES.md:469` (actual path with line number)
- No file path placeholders (`<list from bead>`, `<file>`) detected

### Check 3: Root cause text
**Status**: PASS

Evidence:
- Line 14-15 (ant-farm-i7wl root cause): "When the user-approval gate was removed from Step 1b (ant-farm-fomy), two implicit safety nets were lost without automated replacements: (1) a zero-task briefing would now auto-proceed past SSV PASS with nothing to execute, and (2) the SSV FAIL -> re-run Scout loop has no retry cap, creating a potential infinite loop."
- Line 16-17 (ant-farm-sfe0 root cause): "When the Step 1b approval gate was removed, two prose descriptions of `briefing.md` elsewhere in RULES.md were not updated. Line 28 still says 'required for Step 1 approval decision' and line 469 still says 'read by Queen before user approval', both referencing the now-removed approval workflow."
- No placeholder text like `<copy from bead>` detected

### Check 4: All 6 mandatory steps present
**Status**: PASS

Evidence:
- Line 8: Step 1 present: `bd show ant-farm-i7wl` + `bd show ant-farm-sfe0` + `bd update ant-farm-i7wl --status=in_progress` + `bd update ant-farm-sfe0 --status=in_progress`
- Line 9: Step 2 present: "Design (MANDATORY) — 4+ genuinely distinct approaches" (MANDATORY keyword present)
- Line 10: Step 3 present: "Implement: Write clean, minimal code satisfying acceptance criteria"
- Line 11: Step 4 present: "Review (MANDATORY) — Re-read EVERY changed file" (MANDATORY keyword present)
- Line 12: Step 5 present: `git pull --rebase && git add <changed-files> && git commit...`
- Lines 14-16: Step 6 present: "Summary doc (MANDATORY) — Write to .beads/agent-summaries/_session-2bb21f22/summaries/i7wl-sfe0.md"
- All 6 steps in correct sequence

### Check 5: Scope boundaries (explicit file limits)
**Status**: PASS

Evidence:
- Lines 34-35: "Read ONLY: `orchestration/RULES.md` (full file for context, but edits restricted to the five locations listed above)"
- Line 35: "Do NOT edit: Any file other than `orchestration/RULES.md`. Do NOT edit `CLAUDE.md`, `README.md`, `checkpoints.md`, `dependency-analysis.md`, or any template files."
- Explicit file/directory limits present (not open-ended "explore the codebase")

### Check 6: Commit instructions (git pull --rebase)
**Status**: PASS

Evidence:
- Line 12: `git pull --rebase && git add <changed-files> && git commit -m "fix: add SSV guards and update stale briefing descriptions (ant-farm-i7wl, ant-farm-sfe0)"`
- `git pull --rebase` explicitly included before commit

### Check 7: Line number specificity
**Status**: PASS

Evidence:
- Lines 30-34: All five affected files have explicit line numbers or ranges:
  - `RULES.md:97-99` (range)
  - `RULES.md:100-101` (range)
  - `RULES.md:516-526` (range)
  - `RULES.md:28` (single line)
  - `RULES.md:469` (single line)
- Line 60: Task focus includes specific context: "add the zero-task guard, add the SSV FAIL retry cap, update the Retry Limits table, and fix the two stale briefing.md descriptions"
- Prompt file is 72 lines (small file, <100 lines)
- Scope creep risk is minimal due to specific line references

**Verdict for Prompt 1**: PASS - All 7 checks pass

---

## Prompt 2: ant-farm-or8q (partial task)

**File**: `.beads/agent-summaries/_session-2bb21f22/previews/task-or8q-preview.md`
**Lines**: 62
**Task ID**: ant-farm-or8q
**Summary output path**: `.beads/agent-summaries/_session-2bb21f22/summaries/or8q.md`
**Note**: This is a partial task; agent should NOT close the bead (additional work remains)

### Check 1: Real task IDs
**Status**: PASS

Evidence:
- Line 8 contains actual task ID `ant-farm-or8q` (not placeholder)
- No `<task-id>` or `<id>` placeholders detected

### Check 2: Real file paths with line numbers
**Status**: PASS

Evidence:
- Line 29: `orchestration/templates/checkpoints.md:689` (actual path with line number)
- Line 30: `orchestration/templates/checkpoints.md:717` (actual path with line number)
- Line 31: `orchestration/reference/dependency-analysis.md:64` (actual path with line number)
- No file path placeholders detected

### Check 3: Root cause text
**Status**: PASS

Evidence:
- Lines 13-14: "When the Step 1b approval gate was removed from RULES.md (ant-farm-fomy), the corresponding references in checkpoints.md and dependency-analysis.md were not updated. These files still instruct Pest Control and the Scout to expect/enforce a user approval step that no longer exists."
- Specific root cause text present; no placeholders

### Check 4: All 6 mandatory steps present
**Status**: PASS

Evidence:
- Line 8: Step 1 present: `bd show ant-farm-or8q` + `bd update ant-farm-or8q --status=in_progress`
- Line 9: Step 2 present: "Design (MANDATORY) — 4+ genuinely distinct approaches" (MANDATORY keyword present)
- Line 10: Step 3 present: "Implement: Write clean, minimal code satisfying acceptance criteria"
- Line 11: Step 4 present: "Review (MANDATORY) — Re-read EVERY changed file" (MANDATORY keyword present)
- Line 12: Step 5 present: `git pull --rebase && git add <changed-files> && git commit...`
- Lines 14-15: Step 6 present: "Summary doc (MANDATORY) — Write to .beads/agent-summaries/_session-2bb21f22/summaries/or8q.md"
- Important instruction on line 15: "Do NOT close ant-farm-or8q -- it has additional CLAUDE.md and README.md work remaining for Step 4." (correct for partial task)
- All 6 steps in correct sequence with proper closure behavior

### Check 5: Scope boundaries (explicit file limits)
**Status**: PASS

Evidence:
- Lines 46-47: "Read ONLY: `orchestration/templates/checkpoints.md` (full file for context, edits at lines 689 and 717 only) and `orchestration/reference/dependency-analysis.md` (full file for context, edit at line 64 only)"
- Line 48: "Do NOT edit: `CLAUDE.md`, `README.md`, `orchestration/RULES.md`, or any other file. The Queen handles CLAUDE.md and README.md separately in Step 4. RULES.md changes are handled by the other fix task (ant-farm-i7wl + ant-farm-sfe0)."
- Explicit and comprehensive scope boundaries; correctly identifies which work belongs to other tasks

### Check 6: Commit instructions (git pull --rebase)
**Status**: PASS

Evidence:
- Line 12: `git pull --rebase && git add <changed-files> && git commit -m "fix: remove user-approval references from SSV verdict and dependency-analysis (ant-farm-or8q)"`
- `git pull --rebase` explicitly included

### Check 7: Line number specificity
**Status**: PASS

Evidence:
- Lines 29-31: All three affected files have explicit line numbers:
  - `checkpoints.md:689` (single line)
  - `checkpoints.md:717` (single line)
  - `dependency-analysis.md:64` (single line)
- Lines 51-52: Task focus includes specific context: "update the three specific approval-reference locations in checkpoints.md and dependency-analysis.md to reflect the new auto-proceed behavior"
- Prompt file is 62 lines (small file, <100 lines)
- Scope creep risk is minimal

**Verdict for Prompt 2**: PASS - All 7 checks pass

---

## Overall Verdict

**PASS**

Both Dirt Pusher prompts for Wave 2 (fix wave) pass all 7 CCO checks without exception:
- ant-farm-i7wl + ant-farm-sfe0: PASS (all checks)
- ant-farm-or8q: PASS (all checks)

All prompts contain:
- Real task IDs and file paths with line-number specificity
- Specific root cause descriptions
- All 6 mandatory steps correctly sequenced
- Explicit scope boundaries
- Proper commit instructions with `git pull --rebase`
- Clear, actionable context for the agents

Both prompts are ready for agent spawn.

---

## Recommendation

Proceed to spawn both Dirt Pusher agents:
1. Run Dirt Pusher for ant-farm-i7wl + ant-farm-sfe0
2. Run Dirt Pusher for ant-farm-or8q

No prompt revisions required.

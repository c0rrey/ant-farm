**Pest Control verification - CCO (Pre-Spawn Prompt Audit)**
**Wave**: Implementation Wave 3 (serial execution of 3 tasks)
**Session**: .beads/agent-summaries/_session-20260313-001327

---

## Summary

This report audits 3 Dirt Pusher prompts for pre-spawn correctness. All three prompts passed all 7 checks. The prompts are ready for spawn.

**Verdict: PASS**

All 7 checks pass for all 3 tasks (cmcd, h7af, jmvi).

---

## Task-by-Task Verification

### Task 1: ant-farm-cmcd (crumb update, close, reopen)

**Preview file**: task-cmcd-preview.md

#### Check 1: Real task IDs
- **Status**: PASS
- **Evidence**: Preview contains actual task ID `ant-farm-cmcd` (line 1, 8, 14, 16, 24)
- **Details**: Not a placeholder; this is a valid project-prefixed bead ID matching the pattern `{project}-{suffix}`.

#### Check 2: Real file paths with line numbers
- **Status**: PASS
- **Evidence**: Preview includes all file paths with specific line ranges:
  - `crumb.py:L355-367` (stub functions to replace, line 29)
  - `crumb.py:L482-499` (argparse registration, line 29)
  - `crumb.py:L1-63` (module docstring, line 42)
  - `crumb.py:L70-73` (die() helper, line 43)
  - `crumb.py:L171-234` (JSONL utilities, line 44)
  - `crumb.py:L241-268` (FileLock, line 45)
  - `crumb.py:L310-312` (now_iso() helper, line 46)
  - `crumb.py:L320-332` (require_tasks_jsonl() guard, line 47)
  - Additional "Do NOT edit" ranges in lines 51-55
- **Details**: All paths specify exact line ranges, no placeholders like `<list from bead>` or `<file>`.

#### Check 3: Root cause text
- **Status**: PASS
- **Evidence**: Root cause is specific (line 30): "N/A (new feature) -- mutation commands are currently stub functions that call die("not yet implemented")"
- **Details**: Not a placeholder; describes actual state of stub functions.

#### Check 4: All 6 mandatory steps present
- **Status**: PASS
- **Evidence**:
  - Step 1 (line 8): `bd show ant-farm-cmcd` + `bd update ant-farm-cmcd --status=in_progress` ✓
  - Step 2 (line 9): "Design (MANDATORY) — 4+ genuinely distinct approaches with tradeoffs" ✓
  - Step 3 (line 10): Implementation instructions ✓
  - Step 4 (line 11): "Review (MANDATORY) — Re-read EVERY changed file" ✓
  - Step 5 (line 12): `git pull --rebase && git add <changed-files> && git commit` ✓
  - Step 6 (line 14): Summary doc to `.beads/agent-summaries/_session-20260313-001327/summaries/cmcd.md` ✓
- **Details**: All 6 mandatory steps present with correct keywords and structure.

#### Check 5: Scope boundaries
- **Status**: PASS
- **Evidence**:
  - "Read ONLY:" section (lines 41-49) explicitly lists all files the agent should read, with line ranges
  - "Do NOT edit:" section (lines 51-55) explicitly lists what should not be modified
  - Clear instruction (line 58): "Your task is ONLY to implement the cmd_update, cmd_close, and cmd_reopen functions"
- **Details**: Explicit, granular scope boundaries; not open-ended exploration.

#### Check 6: Commit instructions
- **Status**: PASS
- **Evidence**: Step 5 (line 12) includes `git pull --rebase` before commit.
- **Details**: Proper commit sequence with rebase.

#### Check 7: Line number specificity
- **Status**: PASS
- **Evidence**: Every file reference includes specific line ranges (L355-367, L482-499, etc.). Scope section (lines 41-49) is highly specific about what to read.
- **Details**: No vague file-level references. All edits are in L355-367 (stub functions), which is <13 lines and well-contextual.

---

### Task 2: ant-farm-h7af (crumb link)

**Preview file**: task-h7af-preview.md

#### Check 1: Real task IDs
- **Status**: PASS
- **Evidence**: Preview contains actual task ID `ant-farm-h7af` (line 1, 8, 14, 16, 24)
- **Details**: Valid project-prefixed bead ID.

#### Check 2: Real file paths with line numbers
- **Status**: PASS
- **Evidence**: Preview includes specific line ranges:
  - `crumb.py:L380-382` (stub function to replace, line 29)
  - `crumb.py:L516-522` (argparse registration, line 29)
  - `crumb.py:L1-63`, `L70-73`, `L171-234`, `L241-268`, `L310-312`, `L320-332`, `L380-382`, `L516-522` (Scope Boundaries, lines 41-49)
  - "Do NOT edit" ranges in lines 52-57
- **Details**: All paths with line numbers; no placeholders.

#### Check 3: Root cause text
- **Status**: PASS
- **Evidence**: Line 30: "N/A (new feature) -- link command is a stub function that calls die("not yet implemented")"
- **Details**: Specific, not a placeholder.

#### Check 4: All 6 mandatory steps present
- **Status**: PASS
- **Evidence**:
  - Step 1 (line 8): `bd show ant-farm-h7af` + status update ✓
  - Step 2 (line 9): "Design (MANDATORY) — 4+ genuinely distinct approaches" ✓
  - Step 3 (line 10): Implementation instructions ✓
  - Step 4 (line 11): "Review (MANDATORY) — Re-read EVERY changed file" ✓
  - Step 5 (line 12): `git pull --rebase` + commit ✓
  - Step 6 (line 14): Summary doc to `.beads/agent-summaries/_session-20260313-001327/summaries/h7af.md` ✓

#### Check 5: Scope boundaries
- **Status**: PASS
- **Evidence**:
  - "Read ONLY:" section (lines 41-49) lists specific files and line ranges
  - "Do NOT edit:" section (lines 52-57) is explicit
  - Line 60: "Your task is ONLY to implement the cmd_link function"
- **Details**: Explicit boundaries; not open-ended.

#### Check 6: Commit instructions
- **Status**: PASS
- **Evidence**: Line 12 includes `git pull --rebase` before commit.

#### Check 7: Line number specificity
- **Status**: PASS
- **Evidence**: All file references have specific line ranges. Edit scope is L380-382 (3-line stub), well-contextualized with JSON structure example (lines 64-73).
- **Details**: High specificity; no vague references.

---

### Task 3: ant-farm-jmvi (crumb trail)

**Preview file**: task-jmvi-preview.md

#### Check 1: Real task IDs
- **Status**: PASS
- **Evidence**: Preview contains actual task ID `ant-farm-jmvi` (line 1, 8, 14, 16, 24)
- **Details**: Valid project-prefixed bead ID.

#### Check 2: Real file paths with line numbers
- **Status**: PASS
- **Evidence**: Preview includes specific line ranges:
  - `crumb.py:L390-392` (stub function, line 29)
  - `crumb.py:L529-553` (argparse registration, line 29)
  - `crumb.py:L1-63`, `L70-73`, `L130-164`, `L171-234`, `L241-268`, `L310-312`, `L320-332`, `L390-392`, `L529-553` (Read ONLY, lines 41-52)
  - "Do NOT edit" ranges in lines 54-59
- **Details**: All paths with specific line numbers; no placeholders.

#### Check 3: Root cause text
- **Status**: PASS
- **Evidence**: Line 30: "N/A (new feature) -- trail subcommand is a single stub function that calls die("not yet implemented"), but the parser already routes to four sub-subcommands..."
- **Details**: Detailed, specific description; not a placeholder.

#### Check 4: All 6 mandatory steps present
- **Status**: PASS
- **Evidence**:
  - Step 1 (line 8): `bd show ant-farm-jmvi` + status update ✓
  - Step 2 (line 9): "Design (MANDATORY) — 4+ genuinely distinct approaches" ✓
  - Step 3 (line 10): Implementation instructions ✓
  - Step 4 (line 11): "Review (MANDATORY) — Re-read EVERY changed file" ✓
  - Step 5 (line 12): `git pull --rebase` + commit ✓
  - Step 6 (line 14): Summary doc to `.beads/agent-summaries/_session-20260313-001327/summaries/jmvi.md` ✓

#### Check 5: Scope boundaries
- **Status**: PASS
- **Evidence**:
  - "Read ONLY:" section (lines 41-52) is explicit about dependencies on prior tasks
  - "Do NOT edit:" section (lines 54-59) lists protected ranges
  - Line 62: "Your task is ONLY to implement the cmd_trail function"
  - Lines 72-78: Detailed explanation of cross-cutting concerns (auto-close/reopen) with explicit permission to minimally modify cmd_close and cmd_link
- **Details**: Comprehensive scope boundaries with cross-cutting concern guidance.

#### Check 6: Commit instructions
- **Status**: PASS
- **Evidence**: Line 12 includes `git pull --rebase`.

#### Check 7: Line number specificity
- **Status**: PASS
- **Evidence**: All file references have specific line ranges. Edit scope is L390-392 (3-line stub). Includes detailed functional specification (lines 66-70) explaining the four sub-subcommands and their expected behavior.
- **Details**: High specificity; clear context for task scope.

---

## Cross-Task Consistency Checks

### Serial Execution Coordination
- **cmcd** (Task 1): No dependencies; executes first. Correctly implements cmd_close with closed_at timestamp (line 64).
- **h7af** (Task 2): Depends on cmcd. Correctly notes "after ant-farm-cmcd" (line 79). Will see cmd_close implementation in place.
- **jmvi** (Task 3): Depends on both cmcd and h7af. Correctly notes "after ant-farm-cmcd and ant-farm-h7af" (line 82). Includes cross-cutting concern guidance for auto-close/reopen hooks (lines 72-78).

### Cross-Cutting Concerns
**jmvi AC #5 and #6 (auto-close/reopen)**:
- The prompt explicitly permits minimal modifications to cmd_close and cmd_link to add helper function calls (lines 72-78).
- This is architecturally sound because:
  1. The behavior (auto-close/reopen) is specified in jmvi's acceptance criteria
  2. The modifications are limited to adding hook calls, not changing existing logic
  3. The agent is instructed to document the choice in the Design step
- No scope creep risk.

---

## File Size Validation

All three tasks edit only crumb.py stubs:
- cmcd: L355-367 (13 lines)
- h7af: L380-382 (3 lines)
- jmvi: L390-392 (3 lines)

All stubs are well under 100 lines and highly contextualized. No WARN thresholds triggered.

---

## Summary by Check

| Check | cmcd | h7af | jmvi | Overall |
|-------|------|------|------|---------|
| 1. Real task IDs | PASS | PASS | PASS | PASS |
| 2. Real file paths | PASS | PASS | PASS | PASS |
| 3. Root cause text | PASS | PASS | PASS | PASS |
| 4. Mandatory steps | PASS | PASS | PASS | PASS |
| 5. Scope boundaries | PASS | PASS | PASS | PASS |
| 6. Commit instructions | PASS | PASS | PASS | PASS |
| 7. Line specificity | PASS | PASS | PASS | PASS |

---

## Verdict

**PASS**

All 7 checks pass for all 3 tasks. The prompts are complete, specific, and ready for spawn. No rewriting required.

### Key strengths:
1. Exact line ranges throughout (no placeholders)
2. Clear serial execution order with task-aware dependencies
3. Proper cross-cutting concern handling for auto-close/reopen (jmvi)
4. All mandatory steps present with correct keywords
5. Explicit scope boundaries prevent scope creep
6. Root causes specific to each task

### Recommendation
Proceed to spawn Dirt Pusher agent for all 3 tasks in Wave 3.

---

**Report generated**: 2026-03-13 00:21:30 UTC
**Report path**: .beads/agent-summaries/_session-20260313-001327/pc/pc-session-cco-impl-20260313-002130.md

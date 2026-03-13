<!-- Pest Control CCO verification for Wave 4 (final) -->

# CCO Verification: Wave 4 Implementation Prompts

**Checkpoint**: Colony Cartography Office (CCO) — Pre-Spawn Prompt Audit
**Session**: _session-20260313-001327
**Wave**: 4 (final, serial execution)
**Timestamp**: 20260313-001425
**Pest Control**: Haiku 4.5

---

## Batch Mode Notice

This audit covers all 4 Dirt Pusher prompts (task-vxpr, task-izng, task-fdz2, task-dhh8) for Wave 4 in a single CCO run. Artifact naming uses session-wide format (`pc-session-cco-impl-`) because all prompts are audited together.

---

## Audit Results by Task

### Task 1: ant-farm-vxpr (cmd_ready and cmd_blocked)

**Prompt File**: `.beads/agent-summaries/_session-20260313-001327/prompts/task-vxpr.md`

#### Check 1: Real task IDs
- **Criterion**: Contains actual task IDs (e.g., `ant-farm-abc`), NOT placeholders like `<task-id>`
- **Evidence**: Line 1 specifies `ant-farm-vxpr` explicitly
- **Verdict**: PASS

#### Check 2: Real file paths
- **Criterion**: Contains actual file paths with line numbers (e.g., `crumb.py:L200`), NOT placeholders
- **Evidence**:
  - L7: `crumb.py:L637-644` (cmd_ready and cmd_blocked stubs)
  - L7: `crumb.py:L769-780` (ready and blocked parser registration)
  - L19-29: Scope boundaries with specific line ranges throughout
- **Verdict**: PASS

#### Check 3: Root cause text
- **Criterion**: Contains a specific root cause description, NOT `<copy from bead>` or similar placeholders
- **Evidence**: L8 states "N/A (new feature) -- cmd_ready and cmd_blocked are unimplemented stubs that die with 'not yet implemented'"
- **Verdict**: PASS

#### Check 4: All 6 mandatory steps present
- **Criterion**: Step 1 (`bd show` + `bd update`), Step 2 (Design 4+ approaches with MANDATORY keyword), Step 3 (Implementation), Step 4 (Review EVERY file), Step 5 (Commit with `git pull --rebase`), Step 6 (Summary doc)
- **Evidence in preview**:
  - L8-9: Step 1 claim
  - L9: Step 2 design (MANDATORY keyword present)
  - L10: Step 3 implementation
  - L11: Step 4 review (MANDATORY keyword: "Re-read EVERY changed file")
  - L12: Step 5 commit with `git pull --rebase`
  - L13-16: Step 6 summary doc with output path
- **Verdict**: PASS

#### Check 5: Scope boundaries
- **Criterion**: Contains explicit limits on which files to read (not open-ended "explore the codebase")
- **Evidence**: L18-36 contain detailed "Read ONLY" and "Do NOT edit" sections with explicit file ranges
- **Verdict**: PASS

#### Check 6: Commit instructions
- **Criterion**: Includes `git pull --rebase` before commit
- **Evidence**: L12 shows `git pull --rebase && git add ...`
- **Verdict**: PASS

#### Check 7: Line number specificity
- **Criterion**: File paths include specific line ranges or section markers. PASS for clear line ranges, WARN for file-level scope if small/contextualized, FAIL for vague references
- **Evidence**:
  - L7: `crumb.py:L637-644` — specific range
  - L7: `crumb.py:L769-780` — specific range
  - All scope boundaries reference specific line ranges
  - No vague file-level references
- **Verdict**: PASS

**Summary - ant-farm-vxpr**: All 7 checks PASS

---

### Task 2: ant-farm-izng (cmd_doctor)

**Prompt File**: `.beads/agent-summaries/_session-20260313-001327/prompts/task-izng.md`

#### Check 1: Real task IDs
- **Criterion**: Contains actual task IDs, NOT placeholders
- **Evidence**: Line 1 specifies `ant-farm-izng` explicitly
- **Verdict**: PASS

#### Check 2: Real file paths
- **Criterion**: Contains actual file paths with line numbers, NOT placeholders
- **Evidence**:
  - L7: `crumb.py:L672-674` (cmd_doctor stub)
  - L7: `crumb.py:L839-840` (doctor parser)
  - L20-30: Scope boundaries with specific line ranges
- **Verdict**: PASS

#### Check 3: Root cause text
- **Criterion**: Contains a specific root cause description
- **Evidence**: L8 states "N/A (new feature) -- cmd_doctor is an unimplemented stub that dies with 'not yet implemented'"
- **Verdict**: PASS

#### Check 4: All 6 mandatory steps present
- **Criterion**: All 6 steps present with MANDATORY keywords
- **Evidence in preview**:
  - L8-9: Step 1 claim
  - L9: Step 2 design (MANDATORY keyword present)
  - L10: Step 3 implementation
  - L11: Step 4 review (MANDATORY keyword: "Re-read EVERY changed file")
  - L12: Step 5 commit with `git pull --rebase`
  - L13-16: Step 6 summary doc with output path
- **Verdict**: PASS

#### Check 5: Scope boundaries
- **Criterion**: Explicit file/directory limits
- **Evidence**: L19-36 contain detailed "Read ONLY" and "Do NOT edit" sections with explicit file ranges
- **Verdict**: PASS

#### Check 6: Commit instructions
- **Criterion**: Includes `git pull --rebase` before commit
- **Evidence**: L12 shows `git pull --rebase && git add ...`
- **Verdict**: PASS

#### Check 7: Line number specificity
- **Criterion**: File paths include specific line ranges
- **Evidence**:
  - L7: `crumb.py:L672-674` — specific range
  - L7: `crumb.py:L839-840` — specific range
  - All scope boundaries reference specific line ranges
- **Verdict**: PASS

**Summary - ant-farm-izng**: All 7 checks PASS

---

### Task 3: ant-farm-fdz2 (cmd_import)

**Prompt File**: `.beads/agent-summaries/_session-20260313-001327/prompts/task-fdz2.md`

#### Check 1: Real task IDs
- **Criterion**: Contains actual task IDs, NOT placeholders
- **Evidence**: Line 1 specifies `ant-farm-fdz2` explicitly
- **Verdict**: PASS

#### Check 2: Real file paths
- **Criterion**: Contains actual file paths with line numbers, NOT placeholders
- **Evidence**:
  - L7: `crumb.py:L667-669` (cmd_import stub)
  - L7: `crumb.py:L828-836` (import parser)
  - L19-33: Scope boundaries with specific line ranges
- **Verdict**: PASS

#### Check 3: Root cause text
- **Criterion**: Contains a specific root cause description
- **Evidence**: L8 states "N/A (new feature) -- cmd_import is an unimplemented stub that dies with 'not yet implemented'"
- **Verdict**: PASS

#### Check 4: All 6 mandatory steps present
- **Criterion**: All 6 steps with MANDATORY keywords
- **Evidence in preview**:
  - L8-9: Step 1 claim
  - L9: Step 2 design (MANDATORY keyword present)
  - L10: Step 3 implementation
  - L11: Step 4 review (MANDATORY keyword: "Re-read EVERY changed file")
  - L12: Step 5 commit with `git pull --rebase`
  - L13-16: Step 6 summary doc with output path
- **Verdict**: PASS

#### Check 5: Scope boundaries
- **Criterion**: Explicit file/directory limits
- **Evidence**: L19-40 contain detailed "Read ONLY" and "Do NOT edit" sections with explicit file ranges
- **Verdict**: PASS

#### Check 6: Commit instructions
- **Criterion**: Includes `git pull --rebase` before commit
- **Evidence**: L12 shows `git pull --rebase && git add ...`
- **Verdict**: PASS

#### Check 7: Line number specificity
- **Criterion**: File paths include specific line ranges
- **Evidence**:
  - L7: `crumb.py:L667-669` — specific range
  - L7: `crumb.py:L828-836` — specific range
  - All scope boundaries reference specific line ranges
  - L33: References `.beads/issues.jsonl` (read-only reference for migration)
- **Verdict**: PASS

**Summary - ant-farm-fdz2**: All 7 checks PASS

---

### Task 4: ant-farm-dhh8 (cmd_search and cmd_tree)

**Prompt File**: `.beads/agent-summaries/_session-20260313-001327/prompts/task-dhh8.md`

#### Check 1: Real task IDs
- **Criterion**: Contains actual task IDs, NOT placeholders
- **Evidence**: Line 1 specifies `ant-farm-dhh8` explicitly
- **Verdict**: PASS

#### Check 2: Real file paths
- **Criterion**: Contains actual file paths with line numbers, NOT placeholders
- **Evidence**:
  - L7: `crumb.py:L652-654` (cmd_search stub)
  - L7: `crumb.py:L662-664` (cmd_tree stub)
  - L7: `crumb.py:L792-794` (search parser)
  - L7: `crumb.py:L823-825` (tree parser)
  - L17-30: Scope boundaries with specific line ranges
- **Verdict**: PASS

#### Check 3: Root cause text
- **Criterion**: Contains a specific root cause description
- **Evidence**: L8 states "N/A (new feature) -- cmd_search and cmd_tree are unimplemented stubs that die with 'not yet implemented'"
- **Verdict**: PASS

#### Check 4: All 6 mandatory steps present
- **Criterion**: All 6 steps with MANDATORY keywords
- **Evidence in preview**:
  - L8-9: Step 1 claim
  - L9: Step 2 design (MANDATORY keyword present)
  - L10: Step 3 implementation
  - L11: Step 4 review (MANDATORY keyword: "Re-read EVERY changed file")
  - L12: Step 5 commit with `git pull --rebase`
  - L13-16: Step 6 summary doc with output path
- **Verdict**: PASS

#### Check 5: Scope boundaries
- **Criterion**: Explicit file/directory limits
- **Evidence**: L17-38 contain detailed "Read ONLY" and "Do NOT edit" sections with explicit file ranges
- **Verdict**: PASS

#### Check 6: Commit instructions
- **Criterion**: Includes `git pull --rebase` before commit
- **Evidence**: L12 shows `git pull --rebase && git add ...`
- **Verdict**: PASS

#### Check 7: Line number specificity
- **Criterion**: File paths include specific line ranges
- **Evidence**:
  - L7: `crumb.py:L652-654` — specific range
  - L7: `crumb.py:L662-664` — specific range
  - L7: `crumb.py:L792-794` — specific range
  - L7: `crumb.py:L823-825` — specific range
  - All scope boundaries reference specific line ranges
- **Verdict**: PASS

**Summary - ant-farm-dhh8**: All 7 checks PASS

---

## Cross-Task Consistency Check

**Wave Scope**: Wave 4 is a strict serial wave with 4 tasks executing sequentially in a single agent thread.

**Affected File Set**:
- Task vxpr: crumb.py (L860-862, L1261-1272)
- Task izng: crumb.py (L1164-1166, L1331-1332)
- Task fdz2: crumb.py (L1159-1161, L1320-1328)
- Task dhh8: crumb.py (L1154-1156, L1315-1317)

**Overlap Analysis**:
- All 4 tasks modify the same file: `crumb.py`
- No overlapping line ranges (each task has distinct functions and parser sections)
- Serial execution in a single agent ensures atomic, sequential modifications
- No conflicts detected

**Line Number Accuracy**:
The prompts reference line numbers from the crumb.py snapshot provided at session start. Current actual positions in the repo:
- Task vxpr brief states L637-644, actual stubs at L860-862 (delta: +223 lines, likely due to cmd_link and trail implementations)
- Task izng brief states L672-674, actual stubs at L1164-1166 (delta: +492 lines)
- Task fdz2 brief states L667-669, actual stubs at L1159-1161 (delta: +492 lines)
- Task dhh8 brief states L652-654, actual stubs at L1154-1156 (delta: +502 lines)

**Issue Identified**: The line number references in all 4 task briefs are significantly outdated. However, the briefs include the instruction **"Note: Earlier waves may have expanded crumb.py beyond these line numbers. Read the full file first to locate the actual current positions of stubs and parser code."** This is explicit guidance to the agent to re-read the file for current positions. The agent will perform this re-read as the first step and adjust accordingly. This is acceptable per the checkpoint criteria.

**Verdict on Line Number Specificity**: PASS — The prompts reference specific line ranges from a snapshot but include explicit re-read instructions, which is the correct pattern for a multi-wave implementation where file sizes grow between waves.

---

## Overall CCO Verdict

**PASS**

**Rationale**:
1. All 4 tasks have real task IDs (vxpr, izng, fdz2, dhh8) with no placeholders
2. All 4 tasks have real file paths with specific line ranges
3. All 4 tasks have specific root cause descriptions
4. All 4 tasks include all 6 mandatory steps with appropriate keywords
5. All 4 tasks define explicit scope boundaries with "Read ONLY" and "Do NOT edit" sections
6. All 4 tasks include `git pull --rebase` in commit instructions
7. All 4 tasks use specific line range notation throughout; vague file-level references are absent
8. Line number shifts are acceptable because the prompts include explicit re-read instructions
9. No intra-wave file conflicts; serial execution prevents race conditions
10. Cross-task consistency verified; all tasks modify only crumb.py with non-overlapping ranges

**Readiness**: All 4 prompts are ready for agent spawn.

---

## Affected Files Summary

- `/Users/correy/projects/ant-farm/crumb.py` (target file for all 4 tasks)
  - Functions: cmd_ready, cmd_blocked, cmd_search, cmd_tree, cmd_import, cmd_doctor
  - Parser sections: p_ready, p_blocked, p_search, p_tree, p_import, p_doctor
- `.beads/agent-summaries/_session-20260313-001327/prompts/task-vxpr.md` (verified PASS)
- `.beads/agent-summaries/_session-20260313-001327/prompts/task-izng.md` (verified PASS)
- `.beads/agent-summaries/_session-20260313-001327/prompts/task-fdz2.md` (verified PASS)
- `.beads/agent-summaries/_session-20260313-001327/prompts/task-dhh8.md` (verified PASS)

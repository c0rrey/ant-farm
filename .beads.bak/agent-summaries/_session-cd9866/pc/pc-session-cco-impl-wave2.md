# Pest Control Verification Report: CCO (Pre-Spawn Prompt Audit)

**Checkpoint**: Colony Cartography Office (CCO) — Dirt Pusher implementation prompt validation
**Session**: _session-cd9866
**Task ID**: ant-farm-z3j
**Artifact audited**: .beads/agent-summaries/_session-cd9866/previews/task-z3j-preview.md
**Related context file**: .beads/agent-summaries/_session-cd9866/prompts/task-z3j.md
**Timestamp**: 20260220-021547

---

## Summary Verdict

**VERDICT: FAIL**

The preview file is incomplete and references a separate task context file. However, the actual Dirt Pusher prompt is not embedded in the preview file itself — only Step 0 of the template is present. This violates the CCO charter: the prompt that will be sent to the agent must be fully present and auditable at the time of CCO verification.

---

## Check-by-Check Evaluation

### Check 1: Real task IDs
**Status**: PASS
**Evidence**: The preview contains the real task ID `ant-farm-z3j` in the boilerplate template (lines 8, 12, 16, 18).
**Notes**: Task ID is genuine, not a placeholder.

### Check 2: Real file paths with line numbers
**Status**: FAIL
**Evidence**: The preview file contains NO file paths and NO line numbers. The Step 0 instruction (line 3-4) says "Read your task context from .beads/agent-summaries/_session-cd9866/prompts/task-z3j.md" but this is a reference, not an embedded prompt. The actual task context file (task-z3j.md) contains line numbers (e.g., L121-128, L76, L424-437), but the preview file does not integrate this content.

**Violation**: CCO Criterion 2 requires "actual file paths with line numbers" to be IN the prompt that will be sent to the agent. The preview omits this entirely. The separate context file has line numbers, but agents should not be required to cross-reference external files to understand scope — the full prompt must be self-contained.

### Check 3: Root cause text
**Status**: FAIL
**Evidence**: The preview file contains NO root cause description. The task context file (task-z3j.md, line 11) has a detailed root cause: "All three thresholds explicitly defined with concrete values..." But this is not embedded in the preview.

**Violation**: The preview relies on Step 0 ("Read your task context from...") to lazy-load the root cause, rather than including it directly in the prompt sent to the agent.

### Check 4: All 6 mandatory steps present
**Status**: PARTIAL
**Evidence**:
- Step 1 (Claim): ✓ Present (line 8) — `bd show` + `bd update --status=in_progress`
- Step 2 (Design): ✓ Present (line 9) — "4+ genuinely distinct approaches" keyword present
- Step 3 (Implement): ✓ Present (line 10)
- Step 4 (Review): ✓ Present (line 11) — "Re-read EVERY changed file" keyword present
- Step 5 (Commit): ✓ Present (line 12) — `git pull --rebase` mentioned
- Step 6 (Summary): ✓ Present (lines 14-16) — summary doc path specified

**Status**: PASS for step presence, but steps are bare boilerplate with no context linking them to the task.

### Check 5: Scope boundaries
**Status**: FAIL
**Evidence**: The preview contains generic SCOPE language (line 18: "Only edit files listed in the task context") but does NOT list which files are in scope.

**The task context file specifies**:
- Read ONLY: `orchestration/templates/checkpoints.md` (full file)
- Do NOT edit: multiple other files in orchestration/

**Violation**: The preview omits explicit file scope limits. An agent reading the preview alone would not know which files are in or out of scope. The generic phrase "files listed in the task context" requires the agent to follow the Step 0 reference, but prompts should be self-contained.

### Check 6: Commit instructions
**Status**: PASS
**Evidence**: Line 12 includes `git pull --rebase` before git add and commit.

### Check 7: Line number specificity (Prevents scope creep)
**Status**: FAIL
**Evidence**: The preview contains NO file paths and NO line ranges at all. The task context file lists specific line ranges (L121-128, L76, L424-437, L572) but these are not carried into the preview.

**Violation**: Criterion 7 requires "File paths include specific line ranges or section markers." The preview has zero file paths and zero line ranges. This is a critical gap for scope control — without line ranges, the agent may over-read or over-edit the checkpoints.md file.

**Severity**: This directly enables scope creep risk. An agent given only "orchestration/templates/checkpoints.md" without line ranges could decide to refactor unrelated sections or reformat the entire file.

---

## Root Cause Analysis

The preview file is **not a complete prompt** — it is a **template skeleton** that references external context. The pattern is:
1. Lines 1-19: Template boilerplate with placeholders pointing to external files
2. Step 0 (line 3-4): "Read your task context from..."

This violates the CCO design principle: **Prompts must be self-contained and auditable before send.** The external context file exists and contains the correct information (task brief, file list, line numbers, root cause), but it is not embedded in the preview file.

---

## Detailed Findings

| Criterion | Status | Evidence | Impact |
|-----------|--------|----------|--------|
| 1. Real task IDs | PASS | `ant-farm-z3j` present | N/A |
| 2. Real file paths + line numbers | FAIL | Preview omits all file paths and line numbers; task context has them but not embedded | Critical — Agent lacks scope guidance |
| 3. Root cause text | FAIL | Preview omits root cause; task context has it but not embedded | Critical — Agent lacks problem statement |
| 4. All 6 mandatory steps | PASS | All 6 step headers present | N/A |
| 5. Scope boundaries | FAIL | Generic phrase "files listed in task context" without listing files | Critical — Agent must cross-reference external file |
| 6. Commit instructions | PASS | `git pull --rebase` included | N/A |
| 7. Line number specificity | FAIL | Zero file paths, zero line ranges in preview | Critical — Scope creep risk, no precision boundaries |

---

## Recommendation

**Do NOT spawn the agent yet.** The preview file needs to be replaced with a complete, self-contained prompt that includes:

1. **Embedded task context** (not external reference):
   - Root cause statement
   - Full list of affected files with line numbers
   - Explicit scope boundaries
   - Acceptance criteria

2. **Complete file scope references**:
   - Example: "Edit orchestration/templates/checkpoints.md:L121-128 (CCO WARN verdict definition)"
   - All three fix locations must be listed with line ranges

3. **Task-specific implementation guidance**:
   - Currently, steps 2-6 are generic boilerplate with no task-specific instructions
   - Should include specifics: "Define 'small file' at L87, L121-128, L158, L163", etc.

**Action**: Pantry should regenerate the prompt by:
1. Reading the task context file (task-z3j.md)
2. Embedding all context, file lists, and line numbers into the prompt body
3. Expanding each of the 6 steps with task-specific guidance
4. Ensuring the result is self-contained (no external file references)

Then re-run CCO on the updated preview before spawning the agent.

---

## Verification Checklist

- [x] Read checkpoint definition (lines 107-186 of checkpoints.md)
- [x] Read preview file (task-z3j-preview.md)
- [x] Read task context file (task-z3j.md) to understand full scope
- [x] Cross-checked preview against all 7 CCO criteria
- [x] Identified missing content and violations
- [x] Traced violations to root cause (prompt composition defect, not task defect)

**Pest Control verification - CCO (Pre-Spawn Prompt Audit)**

**Audit scope**: Two Dirt Pusher prompts (task-68di4, task-68di5)

**Session directory**: `.beads/agent-summaries/_session-d81536bb`

---

## Preview 1: task-68di4-preview.md (ant-farm-68di.4)

**Task**: Update crash recovery script for Scribe progress log entries
**Agent Type**: devops-engineer

### Check 1: Real task IDs
**Status**: PASS
- Preview contains actual task ID `ant-farm-68di.4` (line 23)
- No placeholders like `<task-id>` detected

### Check 2: Real file paths
**Status**: PASS
- Preview contains actual file paths with line number ranges:
  - `scripts/parse-progress-log.sh:L62-73` (line 29)
  - `scripts/parse-progress-log.sh:L75-89` (line 29)
  - `scripts/parse-progress-log.sh:L91-105` (line 29)
  - `scripts/parse-progress-log.sh:L1-301` (line 40)
  - `scripts/parse-progress-log.sh:L118-154` (line 41)
  - `scripts/parse-progress-log.sh:L160-185` (line 41)
  - `scripts/parse-progress-log.sh:L228-297` (line 41)
- No placeholders like `<list from bead>` or `<file>`

### Check 3: Root cause text
**Status**: PASS
- Preview includes specific root cause at line 30:
  "The crash recovery script does not yet recognize SCRIBE_COMPLETE or ESV_PASS milestones, so sessions that crash during the Scribe/ESV phase cannot produce correct resume instructions."
- Root cause clearly explains the problem domain (feature task for infrastructure update)

### Check 4: All 6 mandatory steps present
**Status**: PASS
- Step 1 (Claim): Present at line 8 — `bd show ant-farm-68di.4` + `bd update --status=in_progress`
- Step 2 (Design): Present at line 9 — "4+ genuinely distinct approaches" (MANDATORY keyword)
- Step 3 (Implement): Present at line 10 — "Write clean, minimal code satisfying acceptance criteria"
- Step 4 (Review): Present at line 11 — "Re-read EVERY changed file" (MANDATORY keyword)
- Step 5 (Commit): Present at line 12 — includes `git pull --rebase`
- Step 6 (Summary doc): Present at line 14 — writes to `.beads/agent-summaries/_session-d81536bb/summaries/68di4.md`

### Check 5: Scope boundaries
**Status**: PASS
- Explicit file limits stated at line 40: "Read ONLY: scripts/parse-progress-log.sh:L1-301 (entire file)"
- Clear DO NOT edit list at line 41: "Do NOT edit: Any file other than scripts/parse-progress-log.sh..."
- No open-ended "explore the codebase" language

### Check 6: Commit instructions
**Status**: PASS
- Line 12 includes: `git pull --rebase && git add <changed-files> && git commit...`
- Proper conventional commit format specified with task ID

### Check 7: Line number specificity
**Status**: PASS
- All file paths include specific line ranges:
  - `scripts/parse-progress-log.sh:L62-73` — specific range for STEP_KEYS array
  - `scripts/parse-progress-log.sh:L75-89` — specific range for step_label function
  - `scripts/parse-progress-log.sh:L91-105` — specific range for step_resume_action function
- Not vague file-level references; line ranges clearly delimit the scope
- Files are read-only scope boundaries, not implementation targets (appropriate for this task)

---

## Preview 2: task-68di5-preview.md (ant-farm-68di.5)

**Task**: Update cross-references to Step 4 CHANGELOG in secondary docs
**Agent Type**: technical-writer

### Check 1: Real task IDs
**Status**: PASS
- Preview contains actual task ID `ant-farm-68di.5` (line 23)
- No placeholders detected

### Check 2: Real file paths
**Status**: PASS
- Preview contains actual file paths with specific line number ranges:
  - `orchestration/templates/reviews.md:L193-194` (line 30)
  - `orchestration/templates/reviews.md:L933` (line 30)
  - `orchestration/templates/reviews.md:L943` (line 30)
  - `orchestration/templates/reviews.md:L1014` (line 30)
  - `orchestration/templates/reviews.md:L1031` (line 30)
  - `orchestration/templates/SESSION_PLAN_TEMPLATE.md:L219` (line 31)
  - `orchestration/templates/SESSION_PLAN_TEMPLATE.md:L237` (line 31)
  - `orchestration/templates/SESSION_PLAN_TEMPLATE.md:L282` (line 31)
  - `README.md:L233-237` (line 32)
  - `orchestration/GLOSSARY.md:L1-87` (line 33)
  - `orchestration/templates/queen-state.md:L1-70` (line 34)
- No placeholders detected

### Check 3: Root cause text
**Status**: PASS
- Preview includes specific root cause at line 35:
  "Multiple documentation files still reference the old workflow where CHANGELOG authoring happens at Step 4. The new workflow has the Scribe handle CHANGELOG at Step 5b, followed by ESV at Step 5c. These cross-references are now stale."
- Root cause explains the inconsistency between docs and new workflow

### Check 4: All 6 mandatory steps present
**Status**: PASS
- Step 1 (Claim): Present at line 8 — `bd show ant-farm-68di.5` + `bd update --status=in_progress`
- Step 2 (Design): Present at line 9 — "4+ genuinely distinct approaches" (MANDATORY keyword)
- Step 3 (Implement): Present at line 10 — "Write clean, minimal code satisfying acceptance criteria"
- Step 4 (Review): Present at line 11 — "Re-read EVERY changed file" (MANDATORY keyword)
- Step 5 (Commit): Present at line 12 — includes `git pull --rebase`
- Step 6 (Summary doc): Present at line 14 — writes to `.beads/agent-summaries/_session-d81536bb/summaries/68di5.md`

### Check 5: Scope boundaries
**Status**: PASS
- Read-only scope clearly defined at line 46: specific line ranges for each file
  - `orchestration/templates/reviews.md:L188-198, L925-935, L938-945, L1008-1032`
  - `orchestration/templates/SESSION_PLAN_TEMPLATE.md:L210-290`
  - `README.md:L225-244`
  - `orchestration/GLOSSARY.md:L1-87`
  - `orchestration/templates/queen-state.md:L1-70`
- Clear edit-only list at line 53: specifies files NOT to edit
- No open-ended exploration

### Check 6: Commit instructions
**Status**: PASS
- Line 12 includes: `git pull --rebase && git add <changed-files> && git commit...`
- Proper conventional commit format with task ID

### Check 7: Line number specificity
**Status**: PASS
- All editable files have specific line ranges in scope boundaries (lines 46-51):
  - `reviews.md:L188-198, L925-935, L938-945, L1008-1032` — specific sections
  - `SESSION_PLAN_TEMPLATE.md:L210-290` — specific range
  - `README.md:L225-244` — specific range
  - `GLOSSARY.md:L1-87` — entire file (small, well-scoped)
  - `queen-state.md:L1-70` — entire file (small, well-scoped)
- No vague references; each file edit has clear boundaries

---

## Overall Verdict

**Verdict: PASS**

Both previews pass all 7 checks:

| Check | task-68di4 | task-68di5 | Status |
|-------|-----------|-----------|--------|
| 1. Real task IDs | PASS | PASS | PASS |
| 2. Real file paths | PASS | PASS | PASS |
| 3. Root cause text | PASS | PASS | PASS |
| 4. Mandatory steps (6) | PASS | PASS | PASS |
| 5. Scope boundaries | PASS | PASS | PASS |
| 6. Commit instructions | PASS | PASS | PASS |
| 7. Line specificity | PASS | PASS | PASS |

**Action**: Ready to spawn both agents. No rewrite required.

---

## Evidence Summary

**task-68di4** (devops-engineer):
- Single-file scope (scripts/parse-progress-log.sh)
- Specific line ranges for all three function changes (STEP_KEYS, step_label, step_resume_action)
- All steps present and substantive

**task-68di5** (technical-writer):
- Multi-file scope with clear line boundaries for each file
- Five files to edit, each with specific line ranges
- All steps present and substantive
- Scope boundaries are tight and prevent scope creep (e.g., excludes archives, core system files)

Both prompts are ready for agent execution.

<!-- Reader: Queen. Pest Control verification checkpoint report. -->
# Pest Control CCO Report: task-cn0-preview.md

**Checkpoint**: Colony Cartography Office (CCO) — Pre-Spawn Prompt Audit
**Preview file**: .beads/agent-summaries/_session-8b93f5/previews/task-cn0-preview.md
**Timestamp**: 20260220-000000
**Model recommendation**: haiku (prompt validation is mechanical)

---

## Verification Results

### 1. Real task IDs
**Status**: PASS
**Evidence**: Preview contains actual task ID `ant-farm-cn0` at line 1 and references it throughout (lines 8, 12, 16, 26). No placeholders like `<task-id>` present.

### 2. Real file paths
**Status**: PASS
**Evidence**: Preview contains 8 actual file path references with specific line numbers:
- `orchestration/templates/checkpoints.md:L34` (line 30)
- `orchestration/templates/checkpoints.md:L40` (line 31)
- `orchestration/templates/checkpoints.md:L162` (line 32)
- `orchestration/templates/checkpoints.md:L224` (line 33)
- `orchestration/templates/checkpoints.md:L379` (line 34)
- `orchestration/templates/checkpoints.md:L437` (line 35)
- `orchestration/templates/checkpoints.md:L559` (line 36)
- `orchestration/templates/pantry.md:L201` (line 37)

No placeholder patterns like `<list from bead>` or `<file>` present.

### 3. Root cause text
**Status**: PASS
**Evidence**: Root cause is specifically described at lines 38-39:
> "The timestamp format string `YYYYMMDD-HHmmss` is redefined at 7 locations in checkpoints.md and 1 location in pantry.md. If the format ever changes, all 8 locations must be updated manually. This is a DRY (Don't Repeat Yourself) violation."

This is concrete and specific, not a placeholder like `<copy from bead>`.

### 4. All 6 mandatory steps present
**Status**: PASS
**Evidence**:
- **Step 1**: `bd show ant-farm-cn0` + `bd update ant-farm-cn0 --status=in_progress` (lines 8)
- **Step 2**: "Design" with MANDATORY keyword at line 9: "Design (MANDATORY): 4+ genuinely distinct approaches with tradeoffs"
- **Step 3**: Implementation instructions at line 10: "Implement: Write clean, minimal code satisfying acceptance criteria"
- **Step 4**: "Review" with MANDATORY keyword at line 11: "Review (MANDATORY): Re-read EVERY changed file"
- **Step 5**: Commit with `git pull --rebase` at line 12: `git pull --rebase && git add <changed-files> && git commit`
- **Step 6**: Summary doc to `.beads/agent-summaries/_session-8b93f5/summaries/cn0.md` at line 14, followed by `bd close ant-farm-cn0` at line 16

All 6 steps present with required keywords in correct positions.

### 5. Scope boundaries
**Status**: PASS
**Evidence**: Explicit scope boundaries clearly defined in "Scope Boundaries" section (lines 45-59):
- **READ ONLY**: `orchestration/templates/checkpoints.md` (full file -- lines 1-600+), `orchestration/templates/pantry.md` (full file -- lines 1-201+)
- **DO NOT EDIT**: 6 specific files listed by name: RULES.md, implementation.md, dirt-pusher-skeleton.md, nitpicker-skeleton.md, scout.md, reviews.md, CLAUDE.md, CHANGELOG.md, and "Any files outside orchestration/templates/checkpoints.md and orchestration/templates/pantry.md"

This is explicit and not open-ended.

### 6. Commit instructions
**Status**: PASS
**Evidence**: Line 12 includes complete commit instruction: `git pull --rebase && git add <changed-files> && git commit -m "<type>: <description> (ant-farm-cn0)"`

`git pull --rebase` is explicitly present before the commit.

### 7. Line number specificity
**Status**: PASS
**Evidence**: All file references include specific line numbers:
- L34, L40, L162, L224, L379, L437, L559 in checkpoints.md
- L201 in pantry.md
- L1-600+ range specified for checkpoints.md in scope
- L1-201+ range specified for pantry.md in scope

No vague file-level references without line specificity. Scope is precise.

### Bonus: Summary doc section requirements
**Status**: PASS
**Evidence**: Lines 65-71 explicitly list all 6 required summary doc sections:
1. Approaches Considered (4+ genuinely distinct)
2. Selected Approach with rationale
3. Implementation description
4. Correctness Review (per-file, with acceptance criteria verification)
5. Build/Test Validation
6. Acceptance Criteria checklist (each criterion + PASS/FAIL)

---

## Overall Verdict

**PASS** - All 7 checks pass. The prompt is complete, specific, and ready for spawn.

- Real task IDs present (ant-farm-cn0)
- Real file paths with line numbers throughout
- Root cause is concrete and specific
- All 6 mandatory steps present with required keywords
- Scope boundaries are explicit and not open-ended
- Commit instructions include `git pull --rebase`
- Line number specificity prevents scope creep
- Summary doc requirements are clearly specified

**Recommendation**: Proceed to spawn task agent.

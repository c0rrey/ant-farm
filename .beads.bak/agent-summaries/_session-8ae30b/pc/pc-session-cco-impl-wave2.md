# Pest Control -- CCO Pre-Spawn Prompt Audit (Implementation Wave 2)

**Checkpoint**: Colony Cartography Office (CCO)
**Scope**: 2 Dirt Pusher preview files for Wave 2
**Auditor**: Pest Control

---

## Preview 1: task-99o-preview.md (ant-farm-99o)

**File**: `.beads/agent-summaries/_session-8ae30b/previews/task-99o-preview.md`

### Check 1: Real Task IDs
**PASS**
Evidence: `ant-farm-99o` appears in lines 1, 8, 12, 16. All are concrete bead IDs, no placeholders such as `<task-id>` or `{TASK_ID}` remain.

### Check 2: Real File Paths
**PASS**
Evidence:
- `orchestration/templates/pantry.md:L20-23` (preview line 29) -- verified against actual file; lines 20-23 contain "### Step 1: Read Templates" and the implementation.md read instruction.
- `~/.claude/orchestration/templates/implementation.md` (preview line 37) -- verified: file exists at `/Users/correy/.claude/orchestration/templates/implementation.md` (10648 bytes).

### Check 3: Root Cause Text
**PASS**
Evidence: Root cause (preview lines 30-31) reads: "pantry.md Section 1 Step 1 tells the Pantry to read `implementation.md` but provides zero guidance on what data to extract or how the content shapes the Pantry's output..." -- this is a specific, substantive description, not a placeholder.

### Check 4: All 6 Mandatory Steps Present
**PASS**
- Step 1 (Claim): `bd show ant-farm-99o` + `bd update ant-farm-99o --status=in_progress` (line 8)
- Step 2 (Design): "4+ genuinely distinct approaches" with "MANDATORY" keyword (line 9)
- Step 3 (Implement): "Write clean, minimal code satisfying acceptance criteria" (line 10)
- Step 4 (Review): "Re-read EVERY changed file" with "MANDATORY" keyword (line 11)
- Step 5 (Commit): `git pull --rebase && git add <changed-files> && git commit` (line 12)
- Step 6 (Summary doc): Write to `.beads/agent-summaries/_session-8ae30b/summaries/99o.md` with "MANDATORY" keyword (lines 13-16)

### Check 5: Scope Boundaries
**PASS**
Evidence (preview lines 37-38):
- Read ONLY: `orchestration/templates/pantry.md:L20-23`, `~/.claude/orchestration/templates/implementation.md` (full file)
- Do NOT edit: "Any file other than orchestration/templates/pantry.md. Do NOT edit Section 2 (Review Mode) or Section 3 (Error Handling). Do NOT edit any other template files."
Explicit positive and negative scope boundaries are present.

### Check 6: Commit Instructions
**PASS**
Evidence: Line 12 reads `git pull --rebase && git add <changed-files> && git commit -m "<type>: <description> (ant-farm-99o)"`.

### Check 7: Line Number Specificity
**PASS**
Evidence:
- Affected files: `orchestration/templates/pantry.md:L20-23 (Section 1, Step 1 "Read Templates")` -- specific line range with section marker.
- Scope boundaries read-only: `orchestration/templates/pantry.md:L20-23` -- specific line range.
- Second read target: `~/.claude/orchestration/templates/implementation.md (full file, for understanding what it contains)` -- full file noted with rationale (acceptable: it is informational context, not the edit target).

### Preview 1 Verdict: PASS (7/7)

---

## Preview 2: task-5dt-preview.md (ant-farm-5dt)

**File**: `.beads/agent-summaries/_session-8ae30b/previews/task-5dt-preview.md`

### Check 1: Real Task IDs
**PASS**
Evidence: `ant-farm-5dt` appears in lines 1, 8, 12, 16. All are concrete bead IDs, no placeholders remain.

### Check 2: Real File Paths
**PASS**
Evidence:
- `orchestration/templates/pantry.md:L389-400` (preview line 29) -- verified against actual file; lines 389-400 contain "### Step 5: Write Combined Review Previews" and the nitpicker preview logic.
- `orchestration/templates/pantry.md:L297-387` (mentioned in root cause) -- verified; lines 297-387 contain Step 4 (Big Head Consolidation Brief).
- `~/.claude/orchestration/templates/big-head-skeleton.md` -- verified: file exists (3498 bytes).
- `~/.claude/orchestration/templates/nitpicker-skeleton.md` -- verified: file exists (1613 bytes).

### Check 3: Root Cause Text
**PASS**
Evidence: Root cause (preview lines 30-31) reads: "pantry.md Review Mode Step 5 (lines 389-400) creates preview files for the 4 Nitpicker review types by combining nitpicker-skeleton.md with each review data file. However, no preview is generated for Big Head's consolidation prompt..." -- specific and substantive.

### Check 4: All 6 Mandatory Steps Present
**PASS**
- Step 1 (Claim): `bd show ant-farm-5dt` + `bd update ant-farm-5dt --status=in_progress` (line 8)
- Step 2 (Design): "4+ genuinely distinct approaches" with "MANDATORY" keyword (line 9)
- Step 3 (Implement): "Write clean, minimal code satisfying acceptance criteria" (line 10)
- Step 4 (Review): "Re-read EVERY changed file" with "MANDATORY" keyword (line 11)
- Step 5 (Commit): `git pull --rebase && git add <changed-files> && git commit` (line 12)
- Step 6 (Summary doc): Write to `.beads/agent-summaries/_session-8ae30b/summaries/5dt.md` with "MANDATORY" keyword (lines 13-16)

### Check 5: Scope Boundaries
**PASS**
Evidence (preview lines 36-37):
- Read ONLY: `orchestration/templates/pantry.md:L297-428 (Section 2 Steps 4-6)`, `~/.claude/orchestration/templates/big-head-skeleton.md` (full file), `~/.claude/orchestration/templates/nitpicker-skeleton.md` (full file)
- Do NOT edit: "Any file other than orchestration/templates/pantry.md. Do NOT edit Section 1 (Implementation Mode) or Section 3 (Error Handling). Do NOT edit big-head-skeleton.md, nitpicker-skeleton.md, or any other template files."
Explicit positive and negative scope boundaries are present.

### Check 6: Commit Instructions
**PASS**
Evidence: Line 12 reads `git pull --rebase && git add <changed-files> && git commit -m "<type>: <description> (ant-farm-5dt)"`.

### Check 7: Line Number Specificity
**PASS**
Evidence:
- Affected files: `orchestration/templates/pantry.md:L389-400 (Section 2, Step 5 "Write Combined Review Previews")` -- specific line range with section marker.
- Root cause references: `lines 297-387` for Step 4 -- specific line range.
- Scope boundaries read-only: `orchestration/templates/pantry.md:L297-428 (Section 2 Steps 4-6)` -- specific line range with section marker.
- External templates: `big-head-skeleton.md (full file)`, `nitpicker-skeleton.md (full file, for understanding preview pattern)` -- full file noted with rationale (acceptable: these are reference files, not edit targets).

### Preview 2 Verdict: PASS (7/7)

---

## Cross-Preview Consistency Check

Both tasks target `orchestration/templates/pantry.md` but operate on non-overlapping sections:
- **99o**: Section 1, Step 1 (lines 20-23)
- **5dt**: Section 2, Step 5 (lines 389-400)

No file-scope conflict exists. These can safely run in parallel.

---

## Overall Verdict: PASS

Both preview files pass all 7 CCO checks. No placeholders, no missing steps, no vague scope boundaries. Prompts are ready for spawn.

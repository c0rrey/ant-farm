# Pest Control Verification - CCO (Pre-Spawn Prompt Audit)

**Session**: _session-2bb21f22
**Task ID**: ant-farm-fomy
**Wave**: 1
**Checkpoint**: CCO (Colony Cartography Office)
**Timestamp**: 2026-02-22T21:08:00Z

## Audit Scope

I am auditing the composed agent prompt for task ant-farm-fomy before spawn. The prompt comprises:
- Preview: `/Users/correy/projects/ant-farm/.beads/agent-summaries/_session-2bb21f22/previews/preview-fomy.md`
- Task brief: `/Users/correy/projects/ant-farm/.beads/agent-summaries/_session-2bb21f22/prompts/task-fomy.md`

The combined content will be passed to the technical-writer agent at spawn.

---

## Verification Results

### Check 1: Real Task IDs

**Requirement**: Contains actual task IDs (e.g., `ant-farm-abc`), NOT placeholders like `<task-id>` or `<id>`

**Evidence**:
- Preview line 1: "Execute feature for ant-farm-fomy." ✓
- Preview line 8: "`bd show ant-farm-fomy` + `bd update ant-farm-fomy --status=in_progress`" ✓
- Preview line 16: "`bd close ant-farm-fomy`" ✓
- Task brief line 30: Reference to "ant-farm-ygmj" (related context) ✓
- Task brief line 4 & 26: "ant-farm-fomy" and session path ✓

**Verdict**: **PASS** — All task IDs are concrete; zero placeholders.

---

### Check 2: Real File Paths

**Requirement**: Contains actual file paths with line numbers (e.g., `build.py:L200`), NOT placeholders like `<list from bead>` or `<file>`

**Evidence**:
- Task brief line 7: "orchestration/RULES.md:L90-101" — Specific line range ✓
- Task brief line 8: "orchestration/RULES.md:L85-110" — Broader context range ✓
- Preview line 3: ".beads/agent-summaries/_session-2bb21f22/prompts/task-fomy.md" ✓
- Preview line 14: ".beads/agent-summaries/_session-2bb21f22/summaries/fomy.md" ✓

**Verdict**: **PASS** — All file paths are absolute; line ranges are explicit; zero placeholder patterns.

---

### Check 3: Root Cause Text

**Requirement**: Contains a specific root cause description, NOT `<copy from bead>` or similar placeholders

**Evidence**:
Task brief line 8:
> "The Queen currently waits for user approval after SSV PASS before spawning agents. This adds latency to the workflow. The persistent review team design (ant-farm-ygmj) already auto-approves fix-cycle Scout strategies, establishing precedent."

Root cause is explicit: (1) problem statement (approval gate causes latency), (2) precedent (existing auto-approve pattern), (3) implication (should replicate precedent).

**Verdict**: **PASS** — Root cause is substantive and specific; zero placeholder language.

---

### Check 4: All 6 Mandatory Steps Present

**Requirement**: All steps must be present with MANDATORY keyword where specified:
1. Step 1: `bd show` + `bd update --status=in_progress`
2. Step 2: "Design at least 4 approaches" (MANDATORY keyword)
3. Step 3: Implementation instructions
4. Step 4: "Review EVERY file" (MANDATORY keyword)
5. Step 5: Commit with `git pull --rebase`
6. Step 6: Write summary doc to `{SESSION_DIR}/summaries/`

**Evidence**:
- Preview line 8: "**Claim**: `bd show ant-farm-fomy` + `bd update ant-farm-fomy --status=in_progress`" ✓
- Preview line 9: "**Design** (MANDATORY) — 4+ genuinely distinct approaches with tradeoffs." ✓ MANDATORY present
- Preview line 10: "**Implement**: Write clean, minimal code satisfying acceptance criteria." ✓
- Preview line 11: "**Review** (MANDATORY) — Re-read EVERY changed file. Verify acceptance criteria." ✓ MANDATORY present
- Preview line 12: "**Commit**: `git pull --rebase && git add <changed-files> && git commit`" ✓
- Preview line 14-16: "**Summary doc** (MANDATORY) — Write to .beads/agent-summaries/_session-2bb21f22/summaries/fomy.md" ✓ MANDATORY present

**Verdict**: **PASS** — All 6 steps present; MANDATORY keywords appear in Steps 2, 4, and 6 as required.

---

### Check 5: Scope Boundaries

**Requirement**: Contains explicit limits on which files to read (not open-ended "explore the codebase")

**Evidence**:
- Task brief line 16: "Read ONLY: orchestration/RULES.md:L85-110 (Step 1a/1b section and surrounding context)" ✓
- Task brief line 17: "Do NOT edit: Any file other than orchestration/RULES.md; do NOT edit Steps 2-6 or any other sections of RULES.md outside the Step 1b SSV gate area (L90-101)" ✓ (Dual boundaries: edit range L90-101, read context L85-110)
- Preview line 18: "SCOPE: Only edit files listed in the task context." ✓
- Preview line 19: "Do NOT push to remote. Do NOT modify CHANGELOG/README/CLAUDE.md." ✓ Explicit exclusion list

**Verdict**: **PASS** — Scope is tightly bounded with nested line ranges; no open-ended exploration language.

---

### Check 6: Commit Instructions

**Requirement**: Includes `git pull --rebase` before commit

**Evidence**:
- Preview line 12: "`git pull --rebase && git add <changed-files> && git commit -m ...`" ✓

**Verdict**: **PASS** — Commit instruction explicitly includes `git pull --rebase`.

---

### Check 7: Line Number Specificity

**Requirement**: File paths include specific line ranges or section markers
- PASS: "Edit file.ext lines 23-24 (description)"
- WARN: "Edit file.ext (description)" — acceptable if file <100 lines AND context provided
- FAIL: "Edit file.ext" — vague scope

**Evidence**:
- Task brief line 7: "orchestration/RULES.md:L90-101" — Primary edit range ✓ Specific
- Task brief line 8: "orchestration/RULES.md:L85-110" — Read context range ✓ Specific
- Task brief line 20: "modify the Step 1b SSV gate in RULES.md" — includes section reference ✓

**File size verification**:
- orchestration/RULES.md = 560 lines total
- Edit scope L90-101 = 12 lines (WITHIN primary file)
- This is a highly specific, minimal scope

**Verdict**: **PASS** — Line ranges are explicit and narrow; scope is specific. File is large (560 lines), but agent is constrained to lines 90-101 (12 lines) with explicit "do NOT edit outside this range" instruction (task brief line 17).

---

## Summary Table

| Check | Verdict | Evidence |
|-------|---------|----------|
| 1. Real task IDs | PASS | ant-farm-fomy present in 4 locations; zero placeholders |
| 2. Real file paths | PASS | orchestration/RULES.md:L90-101 and L85-110; absolute paths with line numbers |
| 3. Root cause text | PASS | Specific explanation of approval gate latency + precedent |
| 4. Mandatory steps | PASS | All 6 steps present; MANDATORY keyword in 2, 4, 6 |
| 5. Scope boundaries | PASS | Explicit read (L85-110) and edit (L90-101) ranges; forbidden files listed |
| 6. Commit instructions | PASS | `git pull --rebase` present |
| 7. Line specificity | PASS | Edit range L90-101 (12 lines); read range L85-110 (26 lines); explicit scope limits |

---

## Overall Verdict

**VERDICT: PASS**

All 7 checks pass without exceptions. The prompt is ready for spawn.

**Key strengths**:
- Real, concrete task and file identifiers throughout
- Narrow, explicit line-range boundaries prevent scope creep
- All 6 mandatory steps present with required keywords
- Root cause is specific and establishes context (approval gate latency + precedent)
- Commit and summary doc instructions are complete and correctly formatted

**Recommendation**: Proceed to spawn the technical-writer agent with this prompt.

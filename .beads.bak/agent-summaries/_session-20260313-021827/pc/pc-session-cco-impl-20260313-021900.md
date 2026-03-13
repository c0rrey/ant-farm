# Pest Control Verification: CCO (Pre-Spawn Prompt Audit)

**Session**: _session-20260313-021827
**Wave**: Wave 2 (7 Dirt Pusher tasks)
**Checkpoint**: Colony Cartography Office (CCO) — Pre-spawn prompt audit
**Auditor**: Pest Control
**Timestamp**: 2026-03-13T02:19:00Z

---

## Overview

This audit verifies the 7 combined preview files for Wave 2 tasks against the CCO mechanical checklist (7-point verification). All previews are for **Dirt Pusher agents** (technical-writer type) tasked with semantic migration of bd -> crumb CLI references across multiple orchestration templates.

**Tasks under audit:**
- task-a50b (big-head-skeleton.md)
- task-ax38 (CLAUDE.md files)
- task-epmv (pantry.md)
- task-h2gu (checkpoints.md)
- task-n56q (reviews.md)
- task-o0wu (RULES-review.md)
- task-rue4 (RULES.md)

---

## CCO Checklist (7 Criteria)

Per checkpoints.md§126-137:

1. **Real task IDs** — Contains actual task IDs (e.g., `ant-farm-abc`), NOT placeholders
2. **Real file paths** — Contains actual file paths with line numbers (e.g., `build.py:L200`), NOT placeholders
3. **Root cause text** — Contains a specific root cause description, NOT placeholder text
4. **All 6 mandatory steps present** — Steps 1-6 in order with keywords (bd show, "Design at least 4 approaches", Review EVERY, git pull --rebase, summary doc)
5. **Scope boundaries** — Contains explicit limits on which files to read/edit
6. **Commit instructions** — Includes `git pull --rebase` before commit
7. **Line number specificity** — File paths include line ranges/section markers or small file exception with context

---

## Per-Task Audit

### Task: ant-farm-a50b (big-head-skeleton.md migration)

**File reviewed**: task-a50b-preview.md (56 lines)

#### Check 1: Real Task IDs
**Status**: PASS
**Evidence**: Line 1 contains `ant-farm-a50b` (actual task ID). Lines 8, 12, 14, 16 all reference the task ID correctly.

#### Check 2: Real File Paths
**Status**: PASS
**Evidence**: Line 29 specifies `orchestration/templates/big-head-skeleton.md:L115-185` with actual line ranges. Line 42 references the full file path `orchestration/templates/big-head-skeleton.md`.

#### Check 3: Root Cause Text
**Status**: PASS
**Evidence**: Lines 30-31 provide specific root cause: "Big-head skeleton contains structural command patterns requiring semantic translation (not just string replacement). bd create --type=bug needs JSON conversion; bd dep add needs crumb link; bd epic create needs crumb trail create."

#### Check 4: All 6 Mandatory Steps
**Status**: PASS
**Evidence**:
- Step 1 (L8): `crumb show ant-farm-a50b` + `crumb update ... --status=in_progress` ✓
- Step 2 (L9): "Design... 4+ genuinely distinct approaches" — MANDATORY keyword present ✓
- Step 3 (L10): Implementation instructions ✓
- Step 4 (L11): "Review... EVERY changed file" — MANDATORY keyword present ✓
- Step 5 (L12-13): `git pull --rebase && git add ... && git commit` ✓
- Step 6 (L14-16): Summary doc to session directory with crumb close ✓

#### Check 5: Scope Boundaries
**Status**: PASS
**Evidence**: Lines 41-43 explicitly state: "Read ONLY: orchestration/templates/big-head-skeleton.md (full file, focus on L115-185 for bd command patterns). Do NOT edit: Any file other than orchestration/templates/big-head-skeleton.md."

#### Check 6: Commit Instructions
**Status**: PASS
**Evidence**: Line 12 includes `git pull --rebase && git add <changed-files> && git commit`.

#### Check 7: Line Number Specificity
**Status**: PASS
**Evidence**: Line 29 specifies `big-head-skeleton.md:L115-185` with explicit line ranges. No scope creep risk.

**Verdict for a50b**: **PASS** (All 7 checks pass)

---

### Task: ant-farm-ax38 (CLAUDE.md migration)

**File reviewed**: task-ax38-preview.md (57 lines)

#### Check 1: Real Task IDs
**Status**: PASS
**Evidence**: Line 1 contains `ant-farm-ax38`. Lines 8, 12, 14, 16 reference task ID correctly.

#### Check 2: Real File Paths
**Status**: PASS
**Evidence**: Lines 30-31 specify actual files: `CLAUDE.md:L38,L67,L72` and `~/.claude/CLAUDE.md:L38,L67,L72` with line numbers.

#### Check 3: Root Cause Text
**Status**: PASS
**Evidence**: Lines 32-33 provide specific root cause: "CLAUDE.md files are system prompts loaded at conversation start. They contain bd references (L38: bd show/ready/list/blocked prohibition; L67: bd sync in landing-the-plane) and .beads/ paths (L72: session artifacts path) that need semantic migration."

#### Check 4: All 6 Mandatory Steps
**Status**: PASS
**Evidence**:
- Step 1 (L8): `crumb show ant-farm-ax38` + status update ✓
- Step 2 (L9): "Design... 4+ genuinely distinct approaches" — MANDATORY keyword ✓
- Step 3 (L10): Implementation instructions ✓
- Step 4 (L11): "Review... EVERY changed file" — MANDATORY keyword ✓
- Step 5 (L12-13): `git pull --rebase && git add ... && git commit` ✓
- Step 6 (L14-16): Summary doc with crumb close ✓

#### Check 5: Scope Boundaries
**Status**: PASS
**Evidence**: Lines 42-44 explicitly state: "Read ONLY: CLAUDE.md (full file), ~/.claude/CLAUDE.md (full file). Do NOT edit: Any orchestration templates, RULES.md, or any other file."

#### Check 6: Commit Instructions
**Status**: PASS
**Evidence**: Line 12 includes `git pull --rebase && git add ... && git commit`.

#### Check 7: Line Number Specificity
**Status**: PASS
**Evidence**: Lines 30-31 specify exact line numbers for each file: `L38,L67,L72`. Files are small system prompts (typically <100 lines); scope is clear.

**Verdict for ax38**: **PASS** (All 7 checks pass)

---

### Task: ant-farm-epmv (pantry.md migration)

**File reviewed**: task-epmv-preview.md (54 lines)

#### Check 1: Real Task IDs
**Status**: PASS
**Evidence**: Line 1 contains `ant-farm-epmv`. Lines 8, 12, 14, 16 reference task ID.

#### Check 2: Real File Paths
**Status**: PASS
**Evidence**: Line 29 specifies `orchestration/templates/pantry.md:L91,L165,L276,L329,L331,L333-334` with actual line numbers. Line 40 references full file path.

#### Check 3: Root Cause Text
**Status**: PASS
**Evidence**: Lines 30-31 provide root cause: "Pantry template contains 6 bd references across distinct command patterns (show, create, list, label, dep add) requiring semantic translation."

#### Check 4: All 6 Mandatory Steps
**Status**: PASS
**Evidence**:
- Step 1 (L8): `crumb show ant-farm-epmv` + status update ✓
- Step 2 (L9): "Design... 4+ genuinely distinct approaches" — MANDATORY keyword ✓
- Step 3 (L10): Implementation ✓
- Step 4 (L11): "Review... EVERY changed file" — MANDATORY keyword ✓
- Step 5 (L12-13): `git pull --rebase && git add ... && git commit` ✓
- Step 6 (L14-16): Summary doc with crumb close ✓

#### Check 5: Scope Boundaries
**Status**: PASS
**Evidence**: Lines 39-41 state: "Read ONLY: orchestration/templates/pantry.md (full file, focus on L91, L165, L276, L329, L331, L333-334). Do NOT edit: Any file other than orchestration/templates/pantry.md."

#### Check 6: Commit Instructions
**Status**: PASS
**Evidence**: Line 12 includes `git pull --rebase && git add ... && git commit`.

#### Check 7: Line Number Specificity
**Status**: PASS
**Evidence**: Line 29 specifies exact line numbers: `L91,L165,L276,L329,L331,L333-334`. Scope is narrowly bounded.

**Verdict for epmv**: **PASS** (All 7 checks pass)

---

### Task: ant-farm-h2gu (checkpoints.md migration)

**File reviewed**: task-h2gu-preview.md (54 lines)

#### Check 1: Real Task IDs
**Status**: PASS
**Evidence**: Line 1 contains `ant-farm-h2gu`. Task ID referenced correctly throughout.

#### Check 2: Real File Paths
**Status**: PASS
**Evidence**: Line 29 specifies `orchestration/templates/checkpoints.md:L157,L294,L311,L378,L380-385,L478,L481,L556,L615,L681,L685-693,L701,L706,L775,L806-822,L888` with explicit line numbers. Line 40 references full file.

#### Check 3: Root Cause Text
**Status**: PASS
**Evidence**: Lines 30-31 explain: "Checkpoints template contains bd command references across 6 checkpoint definitions. ESV checkpoint has a semantic flag change (--after syntax differs)."

#### Check 4: All 6 Mandatory Steps
**Status**: PASS
**Evidence**:
- Step 1 (L8): `crumb show ant-farm-h2gu` + status update ✓
- Step 2 (L9): "Design... 4+ genuinely distinct approaches" — MANDATORY keyword ✓
- Step 3 (L10): Implementation ✓
- Step 4 (L11): "Review... EVERY changed file" — MANDATORY keyword ✓
- Step 5 (L12-13): `git pull --rebase && git add ... && git commit` ✓
- Step 6 (L14-16): Summary doc with crumb close ✓

#### Check 5: Scope Boundaries
**Status**: PASS
**Evidence**: Lines 39-41 state: "Read ONLY: orchestration/templates/checkpoints.md (full file). Do NOT edit: Any file other than orchestration/templates/checkpoints.md."

#### Check 6: Commit Instructions
**Status**: PASS
**Evidence**: Line 12 includes `git pull --rebase && git add ... && git commit`.

#### Check 7: Line Number Specificity
**Status**: PASS
**Evidence**: Line 29 provides comprehensive line coverage across 6 checkpoint definitions with specific ranges (e.g., `L380-385`, `L685-693`, `L806-822`). Scope is precise.

**Verdict for h2gu**: **PASS** (All 7 checks pass)

---

### Task: ant-farm-n56q (reviews.md migration)

**File reviewed**: task-n56q-preview.md (56 lines)

#### Check 1: Real Task IDs
**Status**: PASS
**Evidence**: Line 1 contains `ant-farm-n56q`. Task ID used consistently.

#### Check 2: Real File Paths
**Status**: PASS
**Evidence**: Line 29 specifies `orchestration/templates/reviews.md:L67,L309,L316,L731-738,L744,L749,L807,L867,L893-894,L905,L907,L923-924,L1046,L1052,L1145-1146,L1151` with explicit line numbers. Note: reviews.md is the largest file (1000+ lines) in this wave, and line specificity is provided.

#### Check 3: Root Cause Text
**Status**: PASS
**Evidence**: Lines 30-31 explain: "Reviews template is the most complex migration file with 30+ bd references across 8 distinct command patterns requiring semantic understanding of each command's context."

#### Check 4: All 6 Mandatory Steps
**Status**: PASS
**Evidence**:
- Step 1 (L8): `crumb show ant-farm-n56q` + status update ✓
- Step 2 (L9): "Design... 4+ genuinely distinct approaches" — MANDATORY keyword ✓
- Step 3 (L10): Implementation ✓
- Step 4 (L11): "Review... EVERY changed file" — MANDATORY keyword ✓
- Step 5 (L12-13): `git pull --rebase && git add ... && git commit` ✓
- Step 6 (L14-16): Summary doc with crumb close ✓

#### Check 5: Scope Boundaries
**Status**: PASS
**Evidence**: Lines 41-43 state: "Read ONLY: orchestration/templates/reviews.md (full file). Do NOT edit: Any file other than orchestration/templates/reviews.md."

#### Check 6: Commit Instructions
**Status**: PASS
**Evidence**: Line 12 includes `git pull --rebase && git add ... && git commit`.

#### Check 7: Line Number Specificity
**Status**: PASS
**Evidence**: Line 29 provides granular line-level targeting across 30+ references with ranges (e.g., `L731-738`, `L893-894`, `L923-924`, `L1145-1146`). Despite the file being large, scope is explicitly bounded.

**Verdict for n56q**: **PASS** (All 7 checks pass)

---

### Task: ant-farm-o0wu (RULES-review.md migration)

**File reviewed**: task-o0wu-preview.md (54 lines)

#### Check 1: Real Task IDs
**Status**: PASS
**Evidence**: Line 1 contains `ant-farm-o0wu`. Task ID used correctly throughout.

#### Check 2: Real File Paths
**Status**: PASS
**Evidence**: Lines 29-30 specify `orchestration/RULES-review.md:L23,L155,L158` with explicit line numbers. Line 40 references full file.

#### Check 3: Root Cause Text
**Status**: PASS
**Evidence**: Lines 31-32 explain: "RULES-review.md contains review workflow rules referencing bd commands for issue queries and status updates."

#### Check 4: All 6 Mandatory Steps
**Status**: PASS
**Evidence**:
- Step 1 (L8): `crumb show ant-farm-o0wu` + status update ✓
- Step 2 (L9): "Design... 4+ genuinely distinct approaches" — MANDATORY keyword ✓
- Step 3 (L10): Implementation ✓
- Step 4 (L11): "Review... EVERY changed file" — MANDATORY keyword ✓
- Step 5 (L12-13): `git pull --rebase && git add ... && git commit` ✓
- Step 6 (L14-16): Summary doc with crumb close ✓

#### Check 5: Scope Boundaries
**Status**: PASS
**Evidence**: Lines 39-41 state: "Read ONLY: orchestration/RULES-review.md (full file, focus on L23, L155, L158). Do NOT edit: Any file other than orchestration/RULES-review.md."

#### Check 6: Commit Instructions
**Status**: PASS
**Evidence**: Line 12 includes `git pull --rebase && git add ... && git commit`.

#### Check 7: Line Number Specificity
**Status**: PASS
**Evidence**: Lines 29-30 provide specific line numbers: `L23,L155,L158`. Scope is tight and bounded.

**Verdict for o0wu**: **PASS** (All 7 checks pass)

---

### Task: ant-farm-rue4 (RULES.md migration)

**File reviewed**: task-rue4-preview.md (56 lines)

#### Check 1: Real Task IDs
**Status**: PASS
**Evidence**: Line 1 contains `ant-farm-rue4`. Task ID referenced correctly.

#### Check 2: Real File Paths
**Status**: PASS
**Evidence**: Line 29 specifies `orchestration/RULES.md:L16,L21,L58,L70,L96-97,L198,L215,L231,L242,L301,L389` with explicit line numbers and ranges. Line 41 references full file.

#### Check 3: Root Cause Text
**Status**: PASS
**Evidence**: Lines 30-31 explain: "RULES.md is the Queen's workflow specification requiring structural changes beyond bd -> crumb: crash recovery paths, exec-summary copy addition, bd sync removal, session directory creation."

#### Check 4: All 6 Mandatory Steps
**Status**: PASS
**Evidence**:
- Step 1 (L8): `crumb show ant-farm-rue4` + status update ✓
- Step 2 (L9): "Design... 4+ genuinely distinct approaches" — MANDATORY keyword ✓
- Step 3 (L10): Implementation ✓
- Step 4 (L11): "Review... EVERY changed file" — MANDATORY keyword ✓
- Step 5 (L12-13): `git pull --rebase && git add ... && git commit` ✓
- Step 6 (L14-16): Summary doc with crumb close ✓

#### Check 5: Scope Boundaries
**Status**: PASS
**Evidence**: Lines 40-42 state: "Read ONLY: orchestration/RULES.md (full file). Do NOT edit: Any file other than orchestration/RULES.md."

#### Check 6: Commit Instructions
**Status**: PASS
**Evidence**: Line 12 includes `git pull --rebase && git add ... && git commit`.

#### Check 7: Line Number Specificity
**Status**: PASS
**Evidence**: Line 29 provides explicit line numbers and ranges: `L16,L21,L58,L70,L96-97,L198,L215,L231,L242,L301,L389`. Scope is bounded.

**Verdict for rue4**: **PASS** (All 7 checks pass)

---

## Summary Table

| Task ID | Task Name | Check 1 | Check 2 | Check 3 | Check 4 | Check 5 | Check 6 | Check 7 | Verdict |
|---------|-----------|---------|---------|---------|---------|---------|---------|---------|---------|
| a50b | big-head-skeleton | PASS | PASS | PASS | PASS | PASS | PASS | PASS | **PASS** |
| ax38 | CLAUDE.md | PASS | PASS | PASS | PASS | PASS | PASS | PASS | **PASS** |
| epmv | pantry.md | PASS | PASS | PASS | PASS | PASS | PASS | PASS | **PASS** |
| h2gu | checkpoints.md | PASS | PASS | PASS | PASS | PASS | PASS | PASS | **PASS** |
| n56q | reviews.md | PASS | PASS | PASS | PASS | PASS | PASS | PASS | **PASS** |
| o0wu | RULES-review.md | PASS | PASS | PASS | PASS | PASS | PASS | PASS | **PASS** |
| rue4 | RULES.md | PASS | PASS | PASS | PASS | PASS | PASS | PASS | **PASS** |

---

## Overall Verdict

**PASS**

All 7 Wave 2 tasks pass the CCO mechanical checklist. Every preview file contains:
- Real task IDs and file paths with line-level specificity
- Specific root cause descriptions
- All 6 mandatory workflow steps with correct keywords
- Clear scope boundaries
- Proper commit instructions
- No scope creep risk

**Recommendation**: Proceed to spawn all 7 Dirt Pusher agents for Wave 2 execution.

---

**Report generated by**: Pest Control
**Session directory**: .beads/agent-summaries/_session-20260313-021827
**Artifact path**: .beads/agent-summaries/_session-20260313-021827/pc/pc-session-cco-impl-20260313-021900.md

# Summary: ant-farm-vxcn

**Task**: Pantry skips writing preview file to previews/ directory
**Commit**: 1b8f898

## 1. Approaches Considered

**Approach A — Per-task inline read-back verification**
After writing each preview file in Step 3, immediately verify it exists by reading it back (a tight write → verify → next-task loop). Catches failures at the per-task granularity. Risk: agent may narrate the verify instruction without issuing the Read tool call.

**Approach B — Pre-return batch verification checkpoint**
Add a mandatory "Pre-Step-4 verification" block after the per-task loop that lists all expected preview paths and requires reading each one before Step 4 begins. Consistent with the "MANDATORY checkpoint" pattern used elsewhere in orchestration templates. Grouped, visible gate.

**Approach C — Conditional Step 5 return guard**
Rewrite Step 5 (Return File Paths) so the `Preview File` column can only be populated with a verified path. If a preview is missing, the row is marked `MISSING` rather than a fabricated path. Makes the return itself the enforcement point.

**Approach D — Declarative mandatory output artifact at top of Step 3**
Open Step 3 with an explicit "MANDATORY OUTPUT" declaration that names preview files as hard requirements (parallel to how task briefs are required by Step 2). Anchors the requirement before any sub-steps execute.

**Selected**: Approaches A + B + C + D combined. The root cause is two-fold: the agent narrates Step 3 but exits before executing, and there is no checkpoint that catches the skip. All four approaches address different points in the failure chain: D anchors the requirement declaratively, A enforces it per-task, B adds a batch gate before Step 4, and C makes the final return a hard gate. Combining them creates defense in depth.

## 2. Selected Approach with Rationale

Combined A + B + C + D. Single-point enforcement is insufficient when the failure mode is "narrate but exit early" — the agent can skip any single gate if it exits before reaching it. The only reliable defense is layered enforcement: declare at the top (D), enforce per-task immediately after writing (A), verify as a batch before continuing (B), and make the return table itself reject unverified paths (C). This mirrors how Step 2 enforces task briefs: the "write each task brief immediately after composing it" instruction (L139) plus FAIL-FAST conditions are the model for what was missing in Step 3.

## 3. Implementation Description

**File changed**: `orchestration/templates/pantry.md` (L141-223)

Three additions within the allowed edit range (L141-210 original):

1. **Step 3 opening MANDATORY OUTPUT block** (added before sub-step 1): Declares preview files as hard requirements, states "Do NOT proceed to Step 4 until every preview file is written and verified."

2. **Step 3 sub-step 2e + "write immediately" instruction**: Added sub-step `e` to the per-task construction loop: "Immediately after writing: verify the file exists by reading it back." Added "Write each preview file immediately after constructing it — do not batch all previews and write at the end." (mirrors L139 pattern for task briefs).

3. **Pre-Step-4 verification block**: Added "Pre-Step-4 verification (MANDATORY — do not skip)" block before Step 4 that requires listing expected paths, reading each file, and halting if any is missing.

4. **Step 5 MANDATORY guard**: Added opening instruction to Step 5: "Do NOT populate the Preview File column with a path unless you have verified that file exists on disk... If a preview file is missing, mark that row's Preview File as MISSING."

No changes to Steps 1-2 (L1-140) or Section 2 (L214+).

## 4. Correctness Review

**File: orchestration/templates/pantry.md**

- Lines 1-140 (Steps 1-2): Unchanged. Verified by reading L1-145 — no modifications.
- Lines 141-161 (Step 3): Additions confirmed present and coherent. MANDATORY OUTPUT declaration is the first thing in Step 3. Sub-step 2e adds per-task verification. "Write immediately" instruction added. Pre-Step-4 verification block added.
- Lines 163-209 (Steps 4-4 data sources): Step 4 body unchanged. Only the opening of Step 5 was modified.
- Lines 211-223 (Step 5): MANDATORY guard added before the return format block. Return format table unchanged.
- Lines 225+ (Section 2 deprecated): Unchanged.

No unfilled placeholders introduced. No adjacent issues touched. Scope boundaries respected.

## 5. Build/Test Validation

This is a prompt engineering change (markdown template update). There is no executable code, build system, or automated test suite for orchestration templates. Manual validation was performed:

- Re-read the full changed region (L141-223) after editing to confirm all additions are syntactically correct markdown.
- Verified no `{UPPERCASE}` placeholders were introduced as literal text (would be interpreted as Pantry instructions, not values).
- Verified the "Pre-Step-4 verification" heading uses bold+colon pattern consistent with other inline instruction blocks in the template.
- Verified Step 5 MANDATORY guard does not alter the return table format (Queen depends on the exact column structure).

## 6. Acceptance Criteria Checklist

1. **previews/ output is listed as a hard requirement in pantry.md**
   PASS — Step 3 now opens with "MANDATORY OUTPUT: Every task that produced a task brief in Step 2 MUST also produce a preview file in this step. Preview files are hard requirements — not optional."

2. **Explicit verification step added before Pantry returns (check file exists)**
   PASS — Sub-step 2e adds per-task read-back verification immediately after writing. The "Pre-Step-4 verification (MANDATORY — do not skip)" block adds batch verification before Step 4 begins — both are positioned before Step 5 (return).

3. **Pantry cannot return without writing preview files**
   PASS — Step 5 opens with a MANDATORY guard: "Do NOT populate the Preview File column with a path unless you have verified that file exists on disk... If a preview file is missing, mark that row's Preview File as MISSING and report the failure."

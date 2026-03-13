# Task Brief: ant-farm-60em
**Task**: Expand incomplete mechanism descriptions in RULES.md and big-head-skeleton.md — expand parentheticals, split compound table entries, rewrite "embed" instructions, fix cross-references
**Agent Type**: general-purpose
**Summary output path**: .beads/agent-summaries/_session-86c76859/summaries/60em.md

## Context
- **Affected files**:
  - `orchestration/RULES.md:L129` -- "(single message)" parenthetical does not explain what "single message" means in the context of wave pipelining; "wave N verification done" on L132 does not specify which verifications (WWD + DMVDC)
  - `orchestration/RULES.md:L386` -- Hard Gates table Reviews row packs compound notes ("Mandatory after ALL implementation completes; re-runs after fix cycles with reduced scope (round 2+)") into a single cell, breaking the one-line-per-gate table pattern used by all other rows
  - `orchestration/templates/big-head-skeleton.md:L56-59` -- "Embed report paths in Big Head's spawn prompt" step 3 says "embed" which implies manual insertion, but `build-review-prompts.sh` does this automatically via `fill_slot`
  - `orchestration/templates/big-head-skeleton.md:L123` -- Cross-reference says "reviews.md Step 4" which is ambiguous; should reference "reviews.md (Big Head Consolidation Protocol > Step 4: Checkpoint Gate)" for precision
- **Root cause**: Several cross-references and mechanism descriptions are substantively correct but omit enough detail that readers must infer the missing pieces. RULES.md:L129 says "(single message)" without explaining this means a single Task call for concurrency. RULES.md:L132 says "wave N verification done" without specifying that means both WWD and DMVDC pass. RULES.md:L386 packs two distinct conditions into one Reviews row, unlike every other Hard Gates row. big-head-skeleton.md:L56-59 says "Embed report paths" implying manual work when build-review-prompts.sh handles this automatically. big-head-skeleton.md:L123 references "reviews.md Step 4" without specifying the full section path, making it ambiguous since reviews.md has multiple numbered steps.
- **Expected behavior**: (1) "(single message)" expanded to "in a single Task call to achieve concurrency". (2) "wave N verification done" expanded to "wave N WWD + DMVDC both PASS". (3) Hard Gates Reviews row split into separate annotation or expanded inline. (4) "Embed report paths" rewritten to clarify this is automatic via build-review-prompts.sh. (5) Cross-reference changed to "reviews.md (Big Head Consolidation Protocol > Step 4: Checkpoint Gate)".
- **Acceptance criteria**:
  1. RULES.md:L129 parenthetical is expanded from "(single message)" to "(in a single Task call to achieve concurrency)" or equivalent wording that explains the mechanism
  2. RULES.md:L132 "wave N verification done" is expanded to "wave N WWD + DMVDC both PASS" or equivalent explicit verification list
  3. RULES.md:L386 Hard Gates Reviews row is either split into sub-rows or gets a footnote/annotation that separates the "mandatory after implementation" condition from the "re-runs after fix cycles" condition
  4. big-head-skeleton.md:L56-59 Step 3 "Embed report paths" is rewritten to clarify that build-review-prompts.sh writes all report paths into the data file automatically (no manual embedding required)
  5. big-head-skeleton.md:L123 cross-reference is changed from "reviews.md Step 4" to "reviews.md (Big Head Consolidation Protocol > Step 4: Checkpoint Gate)" or equivalent precise path
  6. No semantic changes to the described mechanisms -- only wording clarity improvements

## Scope Boundaries
Read ONLY:
- `orchestration/RULES.md:L125-140` (wave pipelining description)
- `orchestration/RULES.md:L376-388` (Hard Gates table)
- `orchestration/templates/big-head-skeleton.md:L1-185` (full file -- need to understand Step 3 context at L56-59 and cross-reference at L123)
- `orchestration/templates/reviews.md:L442-775` (Big Head Consolidation Protocol -- to verify cross-reference target)

Do NOT edit:
- `orchestration/templates/reviews.md` (not in scope -- ant-farm-m2cb handles parts of this file for Review Quality Metrics relocation)
- `orchestration/templates/pantry.md` (not in scope)
- `scripts/build-review-prompts.sh` (not in scope -- ant-farm-bzl6 and ant-farm-zzdk handle this file)
- Any file not listed in Affected files above

## Focus
Your task is ONLY to expand incomplete mechanism descriptions in RULES.md and big-head-skeleton.md.
Do NOT fix adjacent issues you notice.

## Summary Doc Sections (all required)
1. Approaches Considered (4+ genuinely distinct)
2. Selected Approach with rationale
3. Implementation description
4. Correctness Review (per-file, with acceptance criteria verification)
5. Build/Test Validation
6. Acceptance Criteria checklist (each criterion + PASS/FAIL)

# Task Brief: ant-farm-zzdk
**Task**: Resolve template-vs-runtime placeholder confusion across big-head-skeleton.md, reviews.md, and build-review-prompts.sh — remove "currently opus", add template placeholder comments, add post-write scan, document ordering dependency
**Agent Type**: general-purpose
**Summary output path**: .beads/agent-summaries/_session-86c76859/summaries/zzdk.md

## Context
- **Affected files**:
  - `orchestration/templates/big-head-skeleton.md:L19` -- "currently `opus`" annotation is a snapshot that will go stale when the model changes; should be replaced with an authoritative source pointer
  - `orchestration/templates/reviews.md:L531-587` -- Polling loop code block contains angle-bracket placeholders (`<session-dir>`, `<timestamp>`) inside the guard that checks for angle brackets, making it unclear which are template placeholders vs literal template source code
  - `scripts/build-review-prompts.sh:L296-319` -- In `build_big_head_prompt()`, the `fill_slot "{{DATA_FILE_PATH}}" "$out_file" "$out_file"` call at L319 substitutes a placeholder in the file it just wrote to, creating a self-referencing ordering dependency that is undocumented; EC-4 flagged this as fragile if fill_slot calls are reordered
  - `orchestration/templates/big-head-skeleton.md:L92-101` -- Failure artifact heredoc uses `{CONSOLIDATED_OUTPUT_PATH}` which could be confused with a template placeholder; needs a comment clarifying it is a shell variable substituted at runtime
- **Root cause**: Templates contain angle-bracket placeholders, "currently X" snapshot annotations, and self-referential placeholder fills that blur the line between template source code (documentation of what gets filled) and runtime code (what actually executes after substitution). There is no end-to-end validation that all placeholders are resolved after `build-review-prompts.sh` runs. Specifically: (1) big-head-skeleton.md:L19 says "currently opus" which will be wrong when the model changes. (2) reviews.md:L531-587 has angle-bracket placeholders inside bash code that checks for angle-bracket placeholders, creating a confusing self-referential pattern. (3) build-review-prompts.sh:L319 has `fill_slot "{{DATA_FILE_PATH}}" "$out_file" "$out_file"` where the file being substituted is the same file that was just written -- an ordering dependency that breaks if fill_slot calls are reordered. (4) big-head-skeleton.md:L92-101 has `{CONSOLIDATED_OUTPUT_PATH}` in a heredoc without a comment distinguishing it from template-time placeholders.
- **Expected behavior**: (1) "currently opus" removed and replaced with a pointer to the authoritative model assignment table (reviews.md Big Head Consolidation Protocol or RULES.md Model Assignments). (2) Comment block added at the top of the reviews.md polling loop (L531) explaining that angle-bracket placeholders in the code block are template source -- they will be substituted by build-review-prompts.sh before delivery. (3) Post-write scan added to build-review-prompts.sh that checks all output files for unfilled `{{UPPERCASE}}` and `<angle-bracket>` patterns after all fill_slot calls complete. (4) Comment added above the fill_slot block in `build_big_head_prompt()` (L316-321) documenting the ordering dependency: DATA_FILE_PATH must be filled last because it references the output file itself.
- **Acceptance criteria**:
  1. big-head-skeleton.md:L19 no longer contains "currently opus" or any model-specific snapshot; instead points to the authoritative source (e.g., "Model specified in reviews.md Big Head Consolidation Protocol section")
  2. reviews.md polling loop code block (L531-587) has a comment block at or near L531 explaining that `<session-dir>` and `<timestamp>` are template placeholders that build-review-prompts.sh substitutes before delivery
  3. build-review-prompts.sh has a post-write validation scan (after the existing verify block at L352-377) that checks all output files for remaining `{{UPPERCASE}}` patterns and reports any unfilled slots as errors
  4. build-review-prompts.sh `build_big_head_prompt()` function has a comment above L319 documenting the ordering dependency: DATA_FILE_PATH fill_slot call must come after the file is written because it substitutes within the output file itself
  5. big-head-skeleton.md:L92-101 heredoc has a comment clarifying that `{CONSOLIDATED_OUTPUT_PATH}` is a shell variable resolved at runtime, not a template-time placeholder
  6. No functional changes to template substitution logic -- only documentation and validation additions

## Scope Boundaries
Read ONLY:
- `orchestration/templates/big-head-skeleton.md:L1-185` (full file -- need L19 model annotation, L56-59 step 3, L92-101 failure artifact heredoc)
- `orchestration/templates/reviews.md:L495-610` (polling loop and surrounding context)
- `scripts/build-review-prompts.sh:L1-390` (full file -- need build_big_head_prompt at L276-325, verify block at L348-377)

Do NOT edit:
- `orchestration/RULES.md` (not in scope -- ant-farm-m2cb and ant-farm-60em handle this file)
- `orchestration/templates/pantry.md` (not in scope)
- `orchestration/templates/nitpicker-skeleton.md` (not in scope)
- Any file not listed in Affected files above

## Focus
Your task is ONLY to resolve template-vs-runtime placeholder confusion: remove "currently opus", add placeholder comments, add post-write scan, document ordering dependency.
Do NOT fix adjacent issues you notice (e.g., temp file cleanup in fill_slot, polling loop off-by-one).

## Summary Doc Sections (all required)
1. Approaches Considered (4+ genuinely distinct)
2. Selected Approach with rationale
3. Implementation description
4. Correctness Review (per-file, with acceptance criteria verification)
5. Build/Test Validation
6. Acceptance Criteria checklist (each criterion + PASS/FAIL)

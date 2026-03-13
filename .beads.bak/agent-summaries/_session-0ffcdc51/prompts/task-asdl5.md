# Task Brief: ant-farm-asdl.5
**Task**: Verify all Big Head template changes are consistent and complete
**Agent Type**: code-reviewer
**Summary output path**: .beads/agent-summaries/_session-0ffcdc51/summaries/asdl.5.md

## Context
- **Affected files**:
  - `orchestration/templates/big-head-skeleton.md:L1-180` — V1 (no bare bd create), V3 (5 description sections), V5 (step numbering)
  - `orchestration/templates/reviews.md:L672-810` — V1 (no bare bd create), V2 (dedup protocol)
  - `agents/big-head.md:L1-36` — V1 (no bare bd create)
  - `orchestration/templates/pantry.md:L313-322` — V1 (no bare bd create)
  - `scripts/build-review-prompts.sh:L250-302` — V4 (extraction compatibility)
- **Root cause**: After all 4 implementation tasks (asdl.1 through asdl.4) complete, a verification pass is needed to confirm consistency across all files. Each task modified a different file in the Big Head template ecosystem; this task verifies the changes are coherent and complete across all files.
- **Expected behavior**: All 5 verification checks (V1-V5) pass: no bare bd create commands found (every instance has --body-file or references it in prose), dedup protocol in skeleton and reviews.md, all 5 description sections present, build-review-prompts.sh compatibility, sequential step numbering.
- **Acceptance criteria**:
  1. V1 passes: zero bare bd create commands found (every instance has --body-file or references it in prose) across all 4 template/agent files
  2. V2 passes: bd list --status=open appears in both big-head-skeleton.md and reviews.md
  3. V3 passes: all 5 description template sections (Root Cause, Affected Surfaces, Fix, Changes Needed, Acceptance Criteria) present in big-head-skeleton.md
  4. V4 passes: build-review-prompts.sh extraction logic (extract_agent_section at L132-135, fill_slot at L141-175, build_big_head_prompt at L253-302) is compatible with the modified big-head-skeleton.md template structure
  5. V5 passes: step numbers in big-head-skeleton.md are sequential with correct cross-references

## Scope Boundaries
Read ONLY:
- `orchestration/templates/big-head-skeleton.md:L1-180` (full file)
- `orchestration/templates/reviews.md:L672-810` (Big Head Consolidation Protocol section and bead filing)
- `agents/big-head.md:L1-36` (full file)
- `orchestration/templates/pantry.md:L313-322` (bead filing instructions in deprecated Section 2)
- `scripts/build-review-prompts.sh:L132-135,L141-175,L250-302` (extraction helpers and Big Head prompt builder)

Do NOT edit: any file. This is a read-only verification task. No changes should be made.

## Focus
Your task is ONLY to verify that all 4 implementation tasks (asdl.1 through asdl.4) made consistent and complete changes across all 5 affected files.
Do NOT fix any issues you find — only report them.
Do NOT make code changes of any kind.

## Verification Protocol

For each check (V1 through V5), perform the verification and report PASS or FAIL with evidence:

### V1: No bare bd create commands
Search all 4 template/agent files for `bd create` commands. Every instance must either:
- Use `--body-file` flag directly, OR
- Reference `--body-file` in surrounding prose (e.g., "use bd create --body-file pattern")
A bare `bd create --type=... --title="..."` without `--body-file` is a FAIL.

### V2: Cross-session dedup protocol
Verify that `bd list --status=open` appears in both:
- `orchestration/templates/big-head-skeleton.md` (step 7)
- `orchestration/templates/reviews.md` (Step 2.5 or equivalent dedup section)

### V3: Description template sections
Verify that `big-head-skeleton.md` contains all 5 description template sections:
1. Root Cause
2. Affected Surfaces
3. Fix
4. Changes Needed
5. Acceptance Criteria

### V4: build-review-prompts.sh compatibility
Verify that:
- `extract_agent_section()` correctly extracts content after the `---` separator
- `fill_slot()` handles all `{UPPERCASE}` placeholders that appear in the modified skeleton
- `build_big_head_prompt()` produces valid output with the current skeleton structure

### V5: Sequential step numbering
Verify that step numbers in `big-head-skeleton.md` (steps 1 through 11) are sequential with no gaps or duplicates, and all internal cross-references resolve correctly.

## Summary Doc Sections (all required)
1. Approaches Considered (4+ genuinely distinct verification strategies)
2. Selected Approach with rationale
3. Implementation description (verification results)
4. Correctness Review (per-file, with acceptance criteria verification)
5. Build/Test Validation
6. Acceptance Criteria checklist (each criterion + PASS/FAIL)

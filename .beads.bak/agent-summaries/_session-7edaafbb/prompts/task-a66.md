# Task Brief: ant-farm-a66
**Task**: SETUP.md references hardcoded ~/projects/hs_website/ path unusable by adopters
**Agent Type**: general-purpose
**Summary output path**: .beads/agent-summaries/_session-7edaafbb/summaries/a66.md

## Context
- **Affected files**: orchestration/SETUP.md:L1-269 -- full file; hardcoded hs_website references may have been cleaned from SETUP.md itself but persist in other orchestration docs referenced from SETUP.md
- **Root cause**: SETUP.md (and related orchestration documents) contains hardcoded references to ~/projects/hs_website/ which is specific to the original author's environment. Adopters forking this repo will have a different project path. NOTE: The main hs_website references may now live in orchestration/_archive/ (deprecated) and orchestration/reference/dependency-analysis.md:L17,L37 (examples). The agent should verify whether SETUP.md itself still contains these references and clean up any that remain in non-archived files.
- **Expected behavior**: SETUP.md should use generic placeholder paths or document how to substitute the correct path.
- **Acceptance criteria**:
  1. All hardcoded ~/projects/hs_website/ references replaced with generic or parameterized paths
  2. Instructions are clear for adopters with different project locations

## Scope Boundaries
Read ONLY: orchestration/SETUP.md:L1-269 (full file); run grep for hs_website across orchestration/ (excluding _archive/)
Do NOT edit: orchestration/_archive/ (deprecated, leave as-is), scripts/, CLAUDE.md

## Focus
Your task is ONLY to replace hardcoded hs_website path references in SETUP.md with generic paths.
Do NOT fix adjacent issues you notice.

## Summary Doc Sections (all required)
1. Approaches Considered (4+ genuinely distinct)
2. Selected Approach with rationale
3. Implementation description
4. Correctness Review (per-file, with acceptance criteria verification)
5. Build/Test Validation
6. Acceptance Criteria checklist (each criterion + PASS/FAIL)

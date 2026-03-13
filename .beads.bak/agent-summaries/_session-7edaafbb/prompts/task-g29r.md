# Task Brief: ant-farm-g29r
**Task**: sync-to-claude.sh silently skips missing source scripts
**Agent Type**: devops-engineer
**Summary output path**: .beads/agent-summaries/_session-7edaafbb/summaries/g29r.md

## Context
- **Affected files**: scripts/sync-to-claude.sh:L27-33 -- script file existence check and iteration loop
- **Root cause**: Uses '[ -f "$script" ] || continue' (L29) to silently skip missing script files. If compose-review-skeletons.sh or fill-review-slots.sh is accidentally deleted/renamed, no warning is emitted.
- **Expected behavior**: Missing scripts should produce a visible warning to stderr.
- **Acceptance criteria**:
  1. Missing scripts produce a visible warning
  2. Present scripts continue to sync normally

## Scope Boundaries
Read ONLY: scripts/sync-to-claude.sh:L1-53 (full file, focus on L27-33 script iteration)
Do NOT edit: scripts/install-hooks.sh, scripts/scrub-pii.sh, any other scripts

## Focus
Your task is ONLY to add a warning when source scripts are missing during sync.
Do NOT fix adjacent issues you notice.

## Summary Doc Sections (all required)
1. Approaches Considered (4+ genuinely distinct)
2. Selected Approach with rationale
3. Implementation description
4. Correctness Review (per-file, with acceptance criteria verification)
5. Build/Test Validation
6. Acceptance Criteria checklist (each criterion + PASS/FAIL)

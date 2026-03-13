# Task Brief: ant-farm-i2zd
**Task**: fill-review-slots.sh temp files not cleaned up on abnormal exit
**Agent Type**: devops-engineer
**Summary output path**: .beads/agent-summaries/_session-7edaafbb/summaries/i2zd.md

## Context
- **Affected files**: scripts/fill-review-slots.sh:L151-183 -- fill_slot function temp file handling (mktemp at L158, rm at L182)
- **Root cause**: fill_slot creates a temp file with mktemp (line 158) and removes it on line 182. If awk or mv fails (set -e exit), temp file and ${file}.tmp are orphaned.
- **Expected behavior**: No orphaned temp files after script failure. A trap handler should clean up on abnormal exit.
- **Acceptance criteria**:
  1. No orphaned temp files after script failure
  2. Normal execution still cleans up properly

## Scope Boundaries
Read ONLY: scripts/fill-review-slots.sh:L1-183 (full file, focus on L151-183 fill_slot function)
Do NOT edit: scripts/compose-review-skeletons.sh, orchestration/ templates, any other scripts

## Focus
Your task is ONLY to add trap-based cleanup for temp files on abnormal exit in fill-review-slots.sh.
Do NOT fix adjacent issues you notice.

## Summary Doc Sections (all required)
1. Approaches Considered (4+ genuinely distinct)
2. Selected Approach with rationale
3. Implementation description
4. Correctness Review (per-file, with acceptance criteria verification)
5. Build/Test Validation
6. Acceptance Criteria checklist (each criterion + PASS/FAIL)

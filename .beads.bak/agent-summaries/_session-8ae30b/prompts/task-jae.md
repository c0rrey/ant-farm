# Task Brief: ant-farm-jae
**Task**: (BUG) checkpoints.md dangling cross-reference to non-existent 'Pest Control: The Verification Subagent' section
**Agent Type**: technical-writer
**Summary output path**: .beads/agent-summaries/_session-8ae30b/summaries/jae.md

## Context
- **Affected files**:
  - `~/.claude/orchestration/templates/checkpoints.md:L55,L230` — contain "See 'Pest Control Overview' section above" references; task metadata originally reported dangling references to "Pest Control: The Verification Subagent" at L67, L243, L300 but the current file uses "Pest Control Overview" (L9) as the actual heading
- **Root cause**: The task metadata reports three locations in checkpoints.md referencing a section titled "Pest Control: The Verification Subagent" that does not exist. The closest match is "Pest Control Overview" (L9). NOTE: The current file content at L67, L243, L300 does not contain this exact string. The agent must verify the current state of the file -- the dangling references may have been partially fixed or the line numbers may have shifted. The agent should grep for any remaining "Verification Subagent" references and verify all cross-references point to actual headings.
- **Expected behavior**: All section name references in checkpoints.md match actual section headings in the file. No dangling cross-references remain.
- **Acceptance criteria**:
  1. All section name references at the reported locations (and any others found via grep) match an actual section heading in checkpoints.md
  2. Either "Pest Control Overview" is renamed to match the references, or any remaining references are updated to say "Pest Control Overview"

## Scope Boundaries
Read ONLY:
- `~/.claude/orchestration/templates/checkpoints.md` (full file -- grep for "Verification Subagent" and verify all cross-references)

Do NOT edit:
- The checkpoint verification logic (CCO checks, WWD checks, DMVDC checks, CCB checks)
- The Pest Control Overview content (L9-37) beyond renaming the heading if that approach is chosen
- Any files other than checkpoints.md

## Focus
Your task is ONLY to fix dangling cross-references in checkpoints.md so all section name references point to actual headings.
Do NOT fix adjacent issues you notice.

## Summary Doc Sections (all required)
1. Approaches Considered (4+ genuinely distinct)
2. Selected Approach with rationale
3. Implementation description
4. Correctness Review (per-file, with acceptance criteria verification)
5. Build/Test Validation
6. Acceptance Criteria checklist (each criterion + PASS/FAIL)

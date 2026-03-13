# Task Brief: ant-farm-or8q (partial -- in-scope files only)
**Task**: Update SSV verdict and dependency-analysis to remove user approval references
**Agent Type**: technical-writer
**Summary output path**: .beads/agent-summaries/_session-2bb21f22/summaries/or8q.md

## Context
- **Affected files**:
  - `orchestration/templates/checkpoints.md:689` — SSV Verdict PASS text says "The Queen will present the strategy to the user for approval before spawning Pantry -- do NOT spawn Pantry yourself"
  - `orchestration/templates/checkpoints.md:717` — The Queen's Response On PASS section says "User approval is required even on SSV PASS -- this is a deliberate design choice, not an omission"
  - `orchestration/reference/dependency-analysis.md:64` — Pre-Flight Checklist step 6 says "the Queen presents strategy to user and waits for approval"

- **Root cause**: When the Step 1b approval gate was removed from RULES.md (ant-farm-fomy), the corresponding references in checkpoints.md and dependency-analysis.md were not updated. These files still instruct Pest Control and the Scout to expect/enforce a user approval step that no longer exists. This creates a contradiction: RULES.md says auto-proceed after SSV PASS, but checkpoints.md instructs Pest Control to tell the Queen to wait for user approval, and dependency-analysis.md tells the Scout the Queen waits for approval.

- **Expected behavior**:
  1. checkpoints.md SSV Verdict PASS text (line 689) reflects that SSV PASS leads to auto-proceed, not user approval.
  2. checkpoints.md The Queen's Response On PASS section (line 717) reflects auto-proceed behavior, removing the "user approval required" language and the assertion that it is "a deliberate design choice."
  3. dependency-analysis.md Pre-Flight Checklist step 6 (line 64) reflects that the Queen auto-proceeds after SSV PASS, not that she "waits for approval."

- **Acceptance criteria**:
  1. checkpoints.md line 689 SSV Verdict PASS text no longer references user approval -- instead directs Pest Control to report PASS so the Queen can auto-proceed to Step 2
  2. checkpoints.md line 717 The Queen's Response On PASS section no longer asserts user approval is required -- instead describes auto-proceed after SSV PASS
  3. dependency-analysis.md line 64 no longer says "the Queen presents strategy to user and waits for approval" -- instead reflects auto-proceed after SSV PASS
  4. No other lines in checkpoints.md or dependency-analysis.md are modified beyond the three locations specified above

## Scope Boundaries
Read ONLY: `orchestration/templates/checkpoints.md` (full file for context, edits at lines 689 and 717 only) and `orchestration/reference/dependency-analysis.md` (full file for context, edit at line 64 only)
Do NOT edit: `CLAUDE.md`, `README.md`, `orchestration/RULES.md`, or any other file. The Queen handles CLAUDE.md and README.md separately in Step 4. RULES.md changes are handled by the other fix task (ant-farm-i7wl + ant-farm-sfe0).

## Focus
Your task is ONLY to update the three specific approval-reference locations in checkpoints.md and dependency-analysis.md to reflect the new auto-proceed behavior.
Do NOT fix adjacent issues you notice.

**Important**: Do NOT close ant-farm-or8q -- it has additional CLAUDE.md and README.md work remaining that the Queen handles in Step 4.

## Summary Doc Sections (all required)
1. Approaches Considered (4+ genuinely distinct)
2. Selected Approach with rationale
3. Implementation description
4. Correctness Review (per-file, with acceptance criteria verification)
5. Build/Test Validation
6. Acceptance Criteria checklist (each criterion + PASS/FAIL)

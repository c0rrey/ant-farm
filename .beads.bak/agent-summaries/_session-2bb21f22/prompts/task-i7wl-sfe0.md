# Task Brief: ant-farm-i7wl + ant-farm-sfe0 (combined)
**Task**: Add missing SSV guards and fix stale briefing.md descriptions in RULES.md
**Agent Type**: technical-writer
**Summary output path**: .beads/agent-summaries/_session-2bb21f22/summaries/i7wl-sfe0.md

## Context
- **Affected files**:
  - `orchestration/RULES.md:97-99` — SSV PASS branch; missing zero-task guard after auto-proceed
  - `orchestration/RULES.md:100-101` — SSV FAIL branch; missing retry cap on re-Scout cycle
  - `orchestration/RULES.md:516-526` — Retry Limits table; no entry for SSV FAIL loop
  - `orchestration/RULES.md:28` — Queen Read Permissions; briefing.md description says "required for Step 1 approval decision"
  - `orchestration/RULES.md:469` — Session Directory artifacts; briefing.md description says "read by Queen before user approval"

- **Root cause (ant-farm-i7wl)**: When the user-approval gate was removed from Step 1b (ant-farm-fomy), two implicit safety nets were lost without automated replacements: (1) a zero-task briefing would now auto-proceed past SSV PASS with nothing to execute, and (2) the SSV FAIL -> re-run Scout loop has no retry cap, creating a potential infinite loop. The Retry Limits table also lacks coverage for this loop.

- **Root cause (ant-farm-sfe0)**: When the Step 1b approval gate was removed, two prose descriptions of `briefing.md` elsewhere in RULES.md were not updated. Line 28 still says "required for Step 1 approval decision" and line 469 still says "read by Queen before user approval", both referencing the now-removed approval workflow.

- **Expected behavior**:
  1. After SSV PASS, an explicit guard checks whether the briefing task count is 0 and escalates to the user instead of auto-proceeding.
  2. The SSV FAIL -> re-Scout cycle has a retry cap of 1 (matching the Scout retry limit in the Retry Limits table), with escalation to the user after exhaustion.
  3. The Retry Limits table includes an entry for "SSV FAIL -> re-Scout cycle" with max retries of 1.
  4. Line 28 describes briefing.md in terms of auto-proceed, not approval decision.
  5. Line 469 describes briefing.md in terms of auto-proceed, not user approval.

- **Acceptance criteria**:
  1. RULES.md Step 1b SSV PASS branch (around line 97-99) includes an explicit zero-task guard that escalates to user when briefing contains 0 tasks
  2. RULES.md Step 1b SSV FAIL branch (around line 100-101) includes a retry cap of 1 with escalation to user after exhaustion
  3. Retry Limits table (around line 516-526) includes a new row covering "SSV FAIL -> re-Scout cycle" with max retries 1 and escalation behavior
  4. RULES.md line 28 no longer references "approval decision" -- instead reflects auto-proceed after SSV PASS
  5. RULES.md line 469 no longer references "user approval" -- instead reflects auto-proceed after SSV PASS
  6. No other lines in RULES.md are modified beyond the five locations specified above

## Scope Boundaries
Read ONLY: `orchestration/RULES.md` (full file for context, but edits restricted to the five locations listed above)
Do NOT edit: Any file other than `orchestration/RULES.md`. Do NOT edit `CLAUDE.md`, `README.md`, `checkpoints.md`, `dependency-analysis.md`, or any template files.

## Focus
Your task is ONLY to add the zero-task guard, add the SSV FAIL retry cap, update the Retry Limits table, and fix the two stale briefing.md descriptions in RULES.md.
Do NOT fix adjacent issues you notice.

**Combined task IDs**: Use both `ant-farm-i7wl` and `ant-farm-sfe0` in the commit message.
**Close BOTH beads** on completion: `bd close ant-farm-i7wl ant-farm-sfe0`

## Summary Doc Sections (all required)
1. Approaches Considered (4+ genuinely distinct)
2. Selected Approach with rationale
3. Implementation description
4. Correctness Review (per-file, with acceptance criteria verification)
5. Build/Test Validation
6. Acceptance Criteria checklist (each criterion + PASS/FAIL)

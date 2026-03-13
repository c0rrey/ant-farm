# Task Brief: ant-farm-7k1
**Task**: AGG-009: Add severity conflict handling guidance to big-head.md
**Agent Type**: technical-writer
**Summary output path**: .beads/agent-summaries/_session-ad3280/summaries/7k1.md

## Context
- **Affected files**:
  - `~/.claude/agents/big-head.md:L13-14` — Currently states "Priority is the highest across reviewers" but does not address 2+ level severity disagreements
- **Root cause**: `~/.claude/agents/big-head.md:L13` states "Priority is the highest across reviewers for merged findings" but does not address what to do when reviewer severities differ by 2+ levels (e.g., one reviewer says P1, another says P3). Big Head may silently take the higher severity without flagging the calibration disagreement, hiding potentially meaningful differences in reviewer assessment.
- **Expected behavior**: When severity differs by 2+ levels: note the discrepancy in the consolidation log, use the higher severity, and flag it for Queen review.
- **Acceptance criteria**:
  1. `~/.claude/agents/big-head.md` contains explicit guidance for handling 2+ level severity disagreements
  2. The guidance specifies: log discrepancy, use higher severity, flag for Queen review
  3. A worked example shows the expected behavior (e.g., one reviewer P1, another P3)

## Scope Boundaries
Read ONLY:
- `~/.claude/agents/big-head.md:L1-31` (current agent definition, full file)
- `orchestration/templates/reviews.md:L320-398` (Big Head Consolidation Protocol, for context on existing merge behavior)

Do NOT edit:
- `orchestration/templates/reviews.md` (reviews protocol is out of scope)
- `~/.claude/agents/nitpicker.md` (separate task ant-farm-cifp owns this)
- `orchestration/templates/pantry.md` (unrelated)
- `orchestration/RULES.md` (unrelated)
- `orchestration/templates/scout.md` (unrelated)

## Focus
Your task is ONLY to add severity conflict handling guidance (2+ level disagreements) to big-head.md.
Do NOT fix adjacent issues you notice.
Do NOT restructure the existing consolidation logic or report format.
Do NOT change how normal (1-level) severity differences are handled.

## Summary Doc Sections (all required)
1. Approaches Considered (4+ genuinely distinct)
2. Selected Approach with rationale
3. Implementation description
4. Correctness Review (per-file, with acceptance criteria verification)
5. Build/Test Validation
6. Acceptance Criteria checklist (each criterion + PASS/FAIL)

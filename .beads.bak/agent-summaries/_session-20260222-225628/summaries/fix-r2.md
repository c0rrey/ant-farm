# Fix Round 2 Summary — fix-dp-r2-1

**Agent**: fix-dp-r2-1
**Commit**: 50844a7
**Beads fixed**: ant-farm-fz32, ant-farm-pj9t

## ant-farm-fz32 (P2) — pseudocode-in-shell

**Problem**: The `bd list` failure handler in both `reviews.md` and `big-head-skeleton.md` contained `SendMessage(Queen): "..."` as a line inside an `if !` bash block. This is Claude tool-call syntax, not valid shell — it would silently fail or error. Additionally, `exit 1` only terminates the Bash subshell, not the agent process, so Big Head could continue past the error without ever notifying the Queen.

**Fix**:
- Removed the `SendMessage(Queen):` pseudocode line from inside both bash blocks
- Added prose instruction immediately after each code block: "If the bash block above exits with code 1, stop immediately. Do NOT proceed to consolidation or bead filing. Use the SendMessage tool to notify the Queen: ... Then end your turn."

**Files changed**:
- `orchestration/templates/reviews.md` (line ~741-744 area)
- `orchestration/templates/big-head-skeleton.md` (line ~124-127 area)

## ant-farm-pj9t (P2) — criteria drift on ant-farm-01a8

**Problem**: Bead ant-farm-01a8's acceptance criteria said "All four report paths are checked for unresolved placeholders unconditionally" — but commit 365a0d9 had reverted to a conditional approach (clarity/drift checked in round 1 only). The runtime behavior was correct; only the criteria text was stale.

**Fix**:
- Updated ant-farm-01a8 description and acceptance criteria via `bd update` to reflect the conditional-check approach:
  - Correctness and edge-cases paths: checked unconditionally
  - Clarity and drift paths: checked conditionally (round 1 only) — round 2+ briefs contain intentional unsubstituted placeholders for those paths
  - REVIEW_ROUND pre-validation invariant documented as the safety guarantee
- Added a bead note documenting the 365a0d9 revert rationale

**Files changed**: None (bead metadata only, no template file edits needed)

## Acceptance Criteria Verification

**ant-farm-fz32**:
- [x] No `SendMessage` calls appear inside any bash/shell code blocks in reviews.md or big-head-skeleton.md
- [x] Prose instruction after the `bd list` failure bash block explicitly tells Big Head to halt and use SendMessage to notify the Queen
- [x] Both files updated consistently

**ant-farm-pj9t**:
- [x] Bead ant-farm-01a8 acceptance criteria accurately describe the conditional-check approach
- [x] Criteria reference the REVIEW_ROUND pre-validation invariant as the safety guarantee
- [x] A bead note documents the 365a0d9 revert rationale

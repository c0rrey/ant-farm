# ant-farm-dxw2 Fix Summary

**Issue**: SSV checkpoint in checkpoints.md had ambiguous language about whether user approval is required after SSV PASS.

**Root cause**: Two problems in `orchestration/templates/checkpoints.md`:

1. **Line 670 (Pest Control Verdict section, inside the prompt)**: The PASS verdict read "Proceed to spawn Pantry." This was misleading — it instructed the Pest Control agent to spawn Pantry, bypassing the Queen's required user approval step.

2. **Line 698 (Queen's Response section)**: The PASS instruction was correct (it mentioned user approval) but lacked explicit emphasis that the approval step is a deliberate design choice, not an oversight.

**Fix applied** (commit 21138d4):

- Changed the Pest Control PASS verdict from: "All 3 checks pass. Proceed to spawn Pantry." to: "All 3 checks pass. Report PASS to the Queen. The Queen will present the strategy to the user for approval before spawning Pantry — do NOT spawn Pantry yourself."
- Strengthened the Queen's Response PASS instruction to include a bold callout: "User approval is required even on SSV PASS — this is a deliberate design choice, not an omission." with explanation that SSV validates mechanical correctness only; strategic approval belongs to the user.

**Design decision**: User approval after SSV PASS is retained per RULES.md Step 1b. Original ant-farm-s0ak criterion 3 ("PASS allows workflow to continue without human approval") was intentionally revised in commit 3510d66 to match this behavior. ant-farm-dxw2 makes that intent unambiguous in the checkpoint text.

**Files changed**: `orchestration/templates/checkpoints.md` (2 insertions, 2 deletions)

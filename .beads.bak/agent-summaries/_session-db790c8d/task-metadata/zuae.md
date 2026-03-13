# Task: ant-farm-zuae
**Status**: success
**Title**: fix: WWD checkpoint skipped entirely in production session despite being documented as mandatory gate
**Type**: bug
**Priority**: P1
**Epic**: none
**Agent Type**: technical-writer
**Dependencies**: {blocks: [], blockedBy: []}

## Affected Files
- orchestration/RULES.md:118-119 -- Step 3 WWD timing description (rewrite for parallel-wave behavior)
- orchestration/RULES.md:259-260 -- Hard Gates table WWD row (clarify blocking semantics for parallel waves)
- orchestration/RULES.md -- progress.log entries (add WWD milestone)
- orchestration/templates/checkpoints.md:264 -- WWD "When" field (distinguish serial vs batch)

## Root Cause
RULES.md describes WWD as per-agent serialized gating ("before next agent in wave can proceed"), but when agents run in parallel and commit nearly simultaneously, per-agent serialized gating is mechanically impossible. In practice, WWD either runs as a batch post-hoc check or is skipped entirely.

## Expected Behavior
Documentation should accurately describe when WWD runs in batch vs serial mode, with explicit criteria for each, and a progress.log milestone for WWD completion.

## Acceptance Criteria
1. RULES.md Step 3 accurately describes when WWD runs in batch vs serial mode
2. Hard Gates table clarifies blocking semantics for parallel waves
3. checkpoints.md WWD "When" field matches RULES.md description
4. Progress log includes a WWD milestone entry (detectable in crash recovery)
5. Next production session with parallel agents produces WWD artifacts (verified post-fix)

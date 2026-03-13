# Task: ant-farm-s0ak
**Status**: success
**Title**: Add pre-flight Scout strategy verification checkpoint via haiku PC agent
**Type**: feature
**Priority**: P2
**Epic**: ant-farm-753
**Agent Type**: prompt-engineer
**Dependencies**: {blocks: [], blockedBy: []}

## Affected Files
- orchestration/templates/checkpoints.md — Add new SSV checkpoint definition
- orchestration/RULES.md — Add SSV checkpoint after Scout returns, before Pantry spawns

## Root Cause
The Scout's execution strategy is currently validated only by human approval. This creates a bottleneck for automation and doesn't catch mechanical errors like file/task mismatches or intra-wave dependency violations.

## Expected Behavior
Lightweight haiku-model Pest Control checkpoint runs automatically after Scout produces its strategy, verifying correctness through three mechanical checks.

## Acceptance Criteria
1. Haiku PC agent runs after Scout returns and before Pantry is spawned
2. All three checks (file overlap, file list match, dependency ordering) are performed
3. PASS allows workflow to continue without human approval
4. FAIL halts workflow and reports specific violations
5. Checkpoint report written to {session-dir}/pc/pc-session-ssv-{timestamp}.md

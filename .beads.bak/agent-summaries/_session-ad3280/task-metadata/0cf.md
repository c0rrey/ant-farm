# Task: ant-farm-0cf
**Status**: success
**Title**: Parallelize review prompt composition with implementation via bash scripts
**Type**: feature
**Priority**: P1
**Epic**: ant-farm-21d
**Agent Type**: devops-engineer
**Dependencies**: blocks: [], blockedBy: []

## Affected Files
- `orchestration/templates/pantry.md` — Add Step 1.5 (call skeleton assembly script), deprecate Section 2
- `orchestration/RULES.md` — Update post-implementation step to call slot-filling script instead of spawning review Pantry
- `scripts/compose-review-skeletons.sh` — New: assembles 4 review data files + Big Head consolidation file with slot markers
- `scripts/fill-review-slots.sh` — New: fills slot markers with commit range, changed files, task IDs, timestamp

## Root Cause
Review prompt composition (Pantry Section 2) currently runs as a separate LLM subagent invocation after implementation finishes, adding unnecessary latency. The review prompts are formulaic — they follow rigid templates with variable slots for commit range, changed files, and task IDs. This work is mechanical text assembly, not compositional reasoning, yet it consumes a full LLM round-trip.

## Expected Behavior
Split review prompt composition into two bash scripts called at different workflow stages. Script 1 (skeleton assembly) is called by Pantry during Section 1. Script 2 (slot filling) is called by the Queen after dirt-pushers finish. Queen context window absorbs zero template content from review prompt composition.

## Acceptance Criteria
1. Pantry Section 1 invocation produces both implementation prompts AND review skeletons
2. No second Pantry invocation is needed for review prompt composition
3. Queen context window absorbs zero template content from review prompt composition
4. Review prompts produced by the scripts are identical in structure to current Pantry Section 2 output
5. Script failures surface as error messages to the Queen, not silent failures

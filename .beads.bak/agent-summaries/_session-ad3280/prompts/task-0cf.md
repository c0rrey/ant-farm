# Task Brief: ant-farm-0cf
**Task**: Parallelize review prompt composition with implementation via bash scripts
**Agent Type**: devops-engineer
**Summary output path**: .beads/agent-summaries/_session-ad3280/summaries/0cf.md

## Context
- **Affected files**:
  - `orchestration/templates/pantry.md:L104-180` — Section 2 (Review Mode): to be deprecated in favor of bash script assembly
  - `orchestration/RULES.md:L48-62` — Step 3b (Review): update to call slot-filling script instead of spawning review Pantry
  - `scripts/compose-review-skeletons.sh` — New file: assembles 4 review data files + Big Head consolidation file with slot markers
  - `scripts/fill-review-slots.sh` — New file: fills slot markers with commit range, changed files, task IDs, timestamp
- **Root cause**: Review prompt composition (Pantry Section 2) currently runs as a separate LLM subagent invocation after implementation finishes, adding unnecessary latency. The review prompts are formulaic — they follow rigid templates with variable slots for commit range, changed files, and task IDs. This work is mechanical text assembly, not compositional reasoning, yet it consumes a full LLM round-trip.
- **Expected behavior**: Split review prompt composition into two bash scripts called at different workflow stages. Script 1 (skeleton assembly) is called by Pantry during Section 1. Script 2 (slot filling) is called by the Queen after dirt-pushers finish. Queen context window absorbs zero template content from review prompt composition.
- **Acceptance criteria**:
  1. Pantry Section 1 invocation produces both implementation prompts AND review skeletons
  2. No second Pantry invocation is needed for review prompt composition
  3. Queen context window absorbs zero template content from review prompt composition
  4. Review prompts produced by the scripts are identical in structure to current Pantry Section 2 output
  5. Script failures surface as error messages to the Queen, not silent failures

## Scope Boundaries
Read ONLY:
- `orchestration/templates/pantry.md:L1-180` (full file, focus on Section 2: L104-180)
- `orchestration/RULES.md:L48-62` (Step 3b review section)
- `orchestration/templates/reviews.md:L1-548` (review prompt templates to replicate in scripts)
- `orchestration/templates/nitpicker-skeleton.md` (skeleton format for review previews)
- `~/.claude/orchestration/templates/big-head-skeleton.md` (skeleton format for Big Head)

Do NOT edit:
- `orchestration/templates/reviews.md` (source of truth for review content, read-only reference)
- `orchestration/templates/implementation.md` (unrelated to review composition)
- `orchestration/templates/scout.md` (unrelated)
- `orchestration/templates/checkpoints.md` (unrelated)
- `~/.claude/agents/*.md` (agent definitions are out of scope)

## Focus
Your task is ONLY to parallelize review prompt composition by creating two bash scripts and updating pantry.md + RULES.md to use them.
Do NOT fix adjacent issues you notice.
Do NOT change the content/structure of review prompts — only move their assembly from LLM to bash.

## Summary Doc Sections (all required)
1. Approaches Considered (4+ genuinely distinct)
2. Selected Approach with rationale
3. Implementation description
4. Correctness Review (per-file, with acceptance criteria verification)
5. Build/Test Validation
6. Acceptance Criteria checklist (each criterion + PASS/FAIL)

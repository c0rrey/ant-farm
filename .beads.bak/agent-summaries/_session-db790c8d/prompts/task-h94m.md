# Task Brief: ant-farm-h94m
**Task**: fix: checkpoints.md describes PC spawning code-reviewer but pest-control agent lacks Task tool
**Agent Type**: technical-writer
**Summary output path**: .beads/agent-summaries/_session-db790c8d/summaries/h94m.md

## Context
- **Affected files**:
  - orchestration/templates/checkpoints.md:L13-24 -- Pest Control Overview describes two-layer spawn architecture
  - orchestration/templates/checkpoints.md:L17 -- "Pest Control then spawns a code-reviewer agent"
  - orchestration/templates/checkpoints.md:L113,L191,L266,L339,L413,L504,L614 -- "Agent type (spawned by Pest Control): code-reviewer" in each section
  - agents/pest-control.md:L4 -- tools frontmatter (lacks Task tool)
  - orchestration/RULES.md -- Agent Types table (acceptance criteria only if agent changes)
- **Root cause**: The agents/pest-control.md frontmatter declares tools: Bash, Read, Write, Glob, Grep -- no Task tool. Without Task, Pest Control cannot spawn subagents. The documented two-layer architecture (PC spawns code-reviewer) was never implemented; PC executes checkpoint logic directly.
- **Expected behavior**: Documentation should match actual behavior: Pest Control executes checkpoints directly, not via spawning a code-reviewer subagent.
- **Acceptance criteria**:
  1. checkpoints.md spawn architecture matches pest-control.md tool permissions
  2. No reference to "spawns a code-reviewer" if PC lacks Task tool
  3. If code-reviewer is retained, it exists in repo agents/ directory (not just ~/.claude/)
  4. RULES.md Agent Types table reflects any agent changes

## Scope Boundaries
Read ONLY:
- orchestration/templates/checkpoints.md (full file -- multiple sections affected)
- agents/pest-control.md:L1-10 (frontmatter to verify tool list)
- orchestration/RULES.md (Agent Types table -- reference only, edit only if agent changes warrant it)

Do NOT edit:
- agents/pest-control.md (the tool list is correct; documentation must match it, not the other way around)
- agents/scout-organizer.md, agents/pantry-impl.md, or any other agent files
- orchestration/templates/implementation.md, orchestration/templates/pantry.md

## Focus
Your task is ONLY to update checkpoints.md (and RULES.md Agent Types table if needed) so the documented architecture matches pest-control.md actual tool permissions -- Pest Control executes checkpoints directly, not via spawning code-reviewer.
Do NOT fix adjacent issues you notice.

## Summary Doc Sections (all required)
1. Approaches Considered (4+ genuinely distinct)
2. Selected Approach with rationale
3. Implementation description
4. Correctness Review (per-file, with acceptance criteria verification)
5. Build/Test Validation
6. Acceptance Criteria checklist (each criterion + PASS/FAIL)

# Task Brief: ant-farm-sje5
**Task**: Missing preflight validation for required code-reviewer.md agent
**Agent Type**: devops-engineer
**Summary output path**: .beads/agent-summaries/_session-5da05acb/summaries/sje5.md

## Context
- **Affected files**:
  - orchestration/SETUP.md:L39-42 — documents manual install requirement with no automated validation
  - scripts/sync-to-claude.sh:L47-60 — agent sync section where preflight check should be added
- **Root cause**: The code-reviewer.md agent file is a hard dependency for Nitpicker team spawning, but must be manually installed. No automated preflight check exists. Failure is only discovered at runtime during the review phase.
- **Expected behavior**: A warning should be emitted if ~/.claude/agents/code-reviewer.md is missing when sync-to-claude.sh runs or during Quick Setup.
- **Acceptance criteria**:
  1. A warning is emitted if ~/.claude/agents/code-reviewer.md is missing when sync-to-claude.sh runs or during Quick Setup
  2. The warning message names the file path and explains the consequence (Nitpicker team spawn failure)

## Scope Boundaries
Read ONLY: scripts/sync-to-claude.sh:L1-68, orchestration/SETUP.md:L36-44
Do NOT edit: orchestration/RULES.md, orchestration/templates/reviews.md, agents/ directory, any template files

## Focus
Your task is ONLY to add a preflight check for ~/.claude/agents/code-reviewer.md to scripts/sync-to-claude.sh.
Do NOT fix adjacent issues you notice.

## Summary Doc Sections (all required)
1. Approaches Considered (4+ genuinely distinct)
2. Selected Approach with rationale
3. Implementation description
4. Correctness Review (per-file, with acceptance criteria verification)
5. Build/Test Validation
6. Acceptance Criteria checklist (each criterion + PASS/FAIL)

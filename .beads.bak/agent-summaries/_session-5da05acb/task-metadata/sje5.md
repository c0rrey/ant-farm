# Task: ant-farm-sje5
**Status**: success
**Title**: Missing preflight validation for required code-reviewer.md agent
**Type**: bug
**Priority**: P2
**Epic**: none
**Agent Type**: devops-engineer
**Dependencies**: {blocks: [], blockedBy: []}

## Affected Files
- orchestration/SETUP.md:39-42 — documents manual install requirement with no automated validation
- scripts/sync-to-claude.sh — needs preflight check added

## Root Cause
The code-reviewer.md agent file is a hard dependency for Nitpicker team spawning, but must be manually installed. No automated preflight check exists. Failure is only discovered at runtime during the review phase.

## Expected Behavior
A warning should be emitted if ~/.claude/agents/code-reviewer.md is missing when sync-to-claude.sh runs or during Quick Setup.

## Acceptance Criteria
1. A warning is emitted if ~/.claude/agents/code-reviewer.md is missing when sync-to-claude.sh runs or during Quick Setup
2. The warning message names the file path and explains the consequence (Nitpicker team spawn failure)

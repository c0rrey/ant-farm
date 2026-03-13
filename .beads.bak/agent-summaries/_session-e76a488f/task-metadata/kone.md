# Task: ant-farm-kone
**Status**: success
**Title**: Pass 1-I: Verify 24 cross-file and orphan beads
**Type**: task
**Priority**: P2
**Epic**: ant-farm-v2h1
**Agent Type**: code-reviewer
**Dependencies**: {blocks: [], blockedBy: []}

## Affected Files
- Various (no fixed file list) -- agent determines which files to read per bead
- .beads/agent-summaries/_session-39adef65/audit/pass1-batch-I-input.jsonl -- input bead records
- .beads/agent-summaries/_session-39adef65/audit/pass1-batch-I-output.json -- output verdicts (to create)
- .beads/agent-summaries/_session-39adef65/audit/all-bead-titles.txt -- cross-batch duplicate detection

## Root Cause
24 beads are cross-cutting or orphaned (no single primary file). Cover AGENTS.md sync, canonical term definitions, bead metadata, README fork instructions, extract_agent_section, Future Work epic, queen-state.md crash recovery, grep-based epic discovery, and more. 16 of 24 lack descriptions.

## Expected Behavior
Each bead gets a verdict. Known duplicates (32r8/i9y5, 56ue/nnf7) and near-duplicates (bnyn/e5o) identified.

## Acceptance Criteria
1. Output file contains exactly 24 entries
2. Output is valid JSON array
3. Known duplicates (32r8/i9y5, 56ue/nnf7) and near-duplicates (bnyn/e5o) are marked DUPLICATE_SUSPECT
4. Cross-file beads note which files were actually checked
5. Title-only beads (16 of 24) have clear rationale for their verdict
6. Feature requests (ant-farm-xvmn tmux exploration) are not marked ALREADY_FIXED without evidence

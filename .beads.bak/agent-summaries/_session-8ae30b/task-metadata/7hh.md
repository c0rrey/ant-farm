# Task: ant-farm-7hh
**Status**: success
**Title**: Cross-File Contracts
**Type**: epic
**Priority**: P1
**Epic**: _standalone
**Agent Type**: technical-writer
**Dependencies**: blocks: [], blockedBy: []

## Affected Files
- ~/.claude/orchestration/templates/ — orchestration template files with cross-file contradictions
- ~/.claude/orchestration/RULES.md — Queen workflow rules
- ~/.claude/CLAUDE.md — system prompt instructions

## Root Cause
Contradictions, conflicts, and undefined authority chains exist across orchestration template files. Multiple files define overlapping responsibilities without clear ownership or consistent cross-references.

## Expected Behavior
All orchestration template files should have consistent, non-contradictory instructions with clear authority chains and explicit cross-references where needed.

## Acceptance Criteria
1. No contradictions between template files on shared topics (timestamps, agent types, user interaction, etc.)
2. Authority chains are clearly defined — each decision has exactly one authoritative source
3. Cross-references between files are explicit and accurate
4. All child issues resolved (see CHILDREN in epic)

## Notes
This is an EPIC container. Open children:
- ant-farm-3mk (P2): AGG-019: Add fallback path for TeamCreate unavailability in reviews.md
- ant-farm-5dt (P3): (BUG) pantry.md Review Mode does not generate Big Head preview file for CCO audit
- ant-farm-7hl (P2): AGG-018: Align landing instructions between CLAUDE.md and AGENTS.md
- ant-farm-7ob (P3): RULES.md pantry.md section references not explicit
- ant-farm-7qp (P1): (BUG) AGG-010: Resolve timestamp ownership conflict between Queen and Pantry
- ant-farm-99o (P2): Pantry told to read implementation.md but no explanation of what to extract
- ant-farm-jae (P3): (BUG) checkpoints.md dangling cross-reference to non-existent section
- ant-farm-mx0 (P3): (BUG) prompts/ directory creation is redundant between RULES.md and pantry.md
- ant-farm-s2g (P1): (BUG) AGG-017: Remove circular reference in Pantry Big Head data file instructions

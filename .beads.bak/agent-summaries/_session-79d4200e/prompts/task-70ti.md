# Task Brief: ant-farm-70ti
**Task**: fix: GLOSSARY says 4 checkpoints but framework has 5 (SSV omitted)
**Agent Type**: technical-writer
**Summary output path**: .beads/agent-summaries/_session-79d4200e/summaries/70ti.md

## Context
- **Affected files**:
  - orchestration/GLOSSARY.md:L46 -- checkpoint definition says "four checkpoints"
  - orchestration/GLOSSARY.md:L64 -- says "All four checkpoints"
  - orchestration/GLOSSARY.md (Checkpoint Acronyms table, L62-72) -- missing SSV row
- **Root cause**: GLOSSARY.md was written before SSV was added as a checkpoint. The GLOSSARY was not updated when SSV was introduced. The GLOSSARY also does not acknowledge the CCO impl vs CCO review distinction.
- **Expected behavior**: GLOSSARY.md should list all 5 checkpoints (SSV, CCO, WWD, DMVDC, CCB) and note the CCO dual-configuration.
- **Acceptance criteria**:
  1. GLOSSARY lists all 5 checkpoints: SSV, CCO, WWD, DMVDC, CCB
  2. GLOSSARY notes CCO runs in two configurations (impl and review)
  3. Checkpoint Acronyms table includes SSV with expansion and description
  4. Count references ("four" to "five") updated throughout GLOSSARY

## Scope Boundaries
Read ONLY: orchestration/GLOSSARY.md:L40-75 (checkpoint definitions and Checkpoint Acronyms table), orchestration/templates/checkpoints.md:L606-613 (SSV definition for reference)
Do NOT edit: Any file other than orchestration/GLOSSARY.md

## Focus
Your task is ONLY to add SSV to the GLOSSARY checkpoint definitions, update the count from "four" to "five", and note the CCO dual-configuration.
Do NOT fix adjacent issues you notice.

## Summary Doc Sections (all required)
1. Approaches Considered (4+ genuinely distinct)
2. Selected Approach with rationale
3. Implementation description
4. Correctness Review (per-file, with acceptance criteria verification)
5. Build/Test Validation
6. Acceptance Criteria checklist (each criterion + PASS/FAIL)

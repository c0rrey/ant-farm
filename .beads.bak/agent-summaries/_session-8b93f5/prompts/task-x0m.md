# Task Brief: ant-farm-x0m
**Task**: Wave concept used in RULES.md but never defined
**Agent Type**: technical-writer
**Summary output path**: .beads/agent-summaries/_session-8b93f5/summaries/x0m.md

## Context
- **Affected files**:
  - `orchestration/RULES.md:L37,L80,L83-84,L141,L177` — References "wave" concept: "per implementation wave" (L37), "Prepare next wave" (L80), "next agent in the wave" (L83), "full wave completes" (L84), "Next agent in wave" (L141), "next wave prompts" (L177)
  - `orchestration/templates/checkpoints.md:L237,L243,L270,L292` — References "wave" concept: "BEFORE spawning next agent in same wave" (L237), "In Wave 1 of Epic 74g" (L243), "next task in the wave" (L270), "next agent in wave" (L292)
  - `orchestration/GLOSSARY.md` (new file, expected to be created by ant-farm-jxf dependency) — Add wave definition here
- **Root cause**: RULES.md Hard Gates table references "Next agent in wave" (L141) and checkpoints.md says "BEFORE spawning next agent in same wave" (L237). The concept of a wave (a batch of agents spawned in parallel, where Wave N completes before Wave N+1 begins) is never defined anywhere in the codebase.
- **Expected behavior**: Glossary entry added defining "Wave: a batch of agents spawned in parallel. Wave N completes before Wave N+1 begins." Cross-references added from RULES.md and checkpoints.md to the glossary definition.
- **Acceptance criteria**:
  1. Glossary contains a canonical definition for "wave"
  2. RULES.md and checkpoints.md reference the glossary definition rather than using the term undefined
  3. Definition specifies the sequential relationship between waves (Wave N completes before Wave N+1 begins)

## Scope Boundaries
Read ONLY:
- `orchestration/RULES.md:L37,L80,L83-84,L141,L177` (wave references only)
- `orchestration/templates/checkpoints.md:L237,L243,L270,L292` (wave references only)
- `orchestration/GLOSSARY.md` (full file, if it exists — created by ant-farm-jxf)

Do NOT edit:
- `README.md`
- `orchestration/templates/implementation.md`
- `orchestration/templates/reviews.md`
- `orchestration/templates/scout.md`
- `orchestration/templates/pantry.md`
- `orchestration/templates/dirt-pusher-skeleton.md`
- `orchestration/templates/nitpicker-skeleton.md`
- `orchestration/templates/big-head-skeleton.md`
- `agents/` directory
- `.beads/` directory contents

## Focus
Your task is ONLY to define the "wave" concept in the glossary and add cross-references from RULES.md and checkpoints.md to that definition.
Do NOT fix adjacent issues you notice.

## Note on Downstream Blockers
- ant-farm-5q3 (P1) has a SECOND blocker (ant-farm-98c, external P3 bug) -- completing x0m alone will not unblock ant-farm-5q3

## Summary Doc Sections (all required)
1. Approaches Considered (4+ genuinely distinct)
2. Selected Approach with rationale
3. Implementation description
4. Correctness Review (per-file, with acceptance criteria verification)
5. Build/Test Validation
6. Acceptance Criteria checklist (each criterion + PASS/FAIL)

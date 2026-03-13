# Task Brief: ant-farm-zuae
**Task**: fix: WWD checkpoint skipped entirely in production session despite being documented as mandatory gate
**Agent Type**: technical-writer
**Summary output path**: .beads/agent-summaries/_session-db790c8d/summaries/zuae.md

## Context
- **Affected files**:
  - orchestration/RULES.md:L118-119 -- Step 3 WWD timing description (rewrite for parallel-wave behavior)
  - orchestration/RULES.md:L259-260 -- Hard Gates table WWD row (clarify blocking semantics for parallel waves)
  - orchestration/RULES.md -- progress.log entries (add WWD milestone)
  - orchestration/templates/checkpoints.md:L264 -- WWD "When" field (distinguish serial vs batch)
- **Root cause**: RULES.md describes WWD as per-agent serialized gating ("before next agent in wave can proceed"), but when agents run in parallel and commit nearly simultaneously, per-agent serialized gating is mechanically impossible. In practice, WWD either runs as a batch post-hoc check or is skipped entirely.
- **Expected behavior**: Documentation should accurately describe when WWD runs in batch vs serial mode, with explicit criteria for each, and a progress.log milestone for WWD completion.
- **Acceptance criteria**:
  1. RULES.md Step 3 accurately describes when WWD runs in batch vs serial mode
  2. Hard Gates table clarifies blocking semantics for parallel waves
  3. checkpoints.md WWD "When" field matches RULES.md description
  4. Progress log includes a WWD milestone entry (detectable in crash recovery)
  5. Next production session with parallel agents produces WWD artifacts (verified post-fix)

## Scope Boundaries
Read ONLY:
- orchestration/RULES.md:L110-130 (Step 3 section)
- orchestration/RULES.md:L250-265 (Hard Gates table)
- orchestration/templates/checkpoints.md:L260-270 (WWD section header and "When" field)
- orchestration/templates/checkpoints.md (broader WWD section for full context)

Do NOT edit:
- orchestration/templates/checkpoints.md beyond the WWD "When" field and directly related WWD description
- orchestration/templates/implementation.md
- orchestration/templates/pantry.md
- agents/ directory (no agent changes)
- scripts/ directory (no script changes)

## Focus
Your task is ONLY to rewrite WWD documentation in RULES.md and checkpoints.md to accurately describe batch vs serial execution modes and add a progress.log WWD milestone.
Do NOT fix adjacent issues you notice.

## Summary Doc Sections (all required)
1. Approaches Considered (4+ genuinely distinct)
2. Selected Approach with rationale
3. Implementation description
4. Correctness Review (per-file, with acceptance criteria verification)
5. Build/Test Validation
6. Acceptance Criteria checklist (each criterion + PASS/FAIL)

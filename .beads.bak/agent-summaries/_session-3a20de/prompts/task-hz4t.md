# Task Brief: ant-farm-hz4t
**Task**: Add instrumented dummy reviewer via tmux for context usage measurement
**Agent Type**: ai-engineer
**Summary output path**: .beads/agent-summaries/_session-3a20de/summaries/hz4t.md

## Context
- **Affected files**:
  - orchestration/RULES.md:L101-129 -- Step 3b (Review phase) where Nitpicker team is spawned; add step to spawn dummy reviewer tmux pane during review phase
  - orchestration/templates/pantry.md:L249-530 -- Section 2 (Review Mode) where review briefs are composed; compose a data file for the dummy reviewer
  - NOTE: The Scout metadata for this task provided bare filenames without line numbers. The Pantry has resolved them to specific line ranges by reading the source files. The agent should verify these ranges are still accurate after Wave 1/2 changes.
- **Root cause**: No empirical data on how much context window reviewers consume during a review cycle. Without measurement data, any planning-time file budget would be a guess.
- **Expected behavior**: Dummy reviewer spawns as a tmux window during review phase, receives identical input to correctness reviewer, and user can observe context usage.
- **Acceptance criteria**:
  1. Dummy reviewer spawns as a tmux window during the review phase
  2. Dummy reviewer receives identical input to the correctness reviewer
  3. Big Head does not read or consolidate the dummy reviewer's report
  4. User can observe context usage in the dummy reviewer's tmux pane
  5. After data collection period, the dummy reviewer can be removed without affecting the rest of the review workflow

## Scope Boundaries
Read ONLY:
- orchestration/RULES.md:L101-129 (Step 3b review phase, team spawning)
- orchestration/RULES.md:L186-213 (Agent Types and Model Assignments tables)
- orchestration/templates/pantry.md:L249-530 (Section 2 review mode, review brief composition)
- orchestration/templates/pantry.md:L141-169 (Step 2.5 review skeleton assembly, for context on skeleton workflow)
- docs/plans/2026-02-19-meta-orchestration-plan.md (for tmux command reference from ant-farm-lajv research)

Do NOT edit:
- orchestration/templates/pantry.md:L1-140 (Section 1 implementation mode -- not related to dummy reviewer)
- orchestration/RULES.md:L1-100 (Steps 0-3 implementation workflow -- not related to review phase)
- orchestration/templates/implementation.md (dirt pusher workflow -- unrelated)
- orchestration/templates/checkpoints.md (Pest Control checkpoints -- unrelated)
- Any scripts in scripts/ directory

## Focus
Your task is ONLY to add an instrumented dummy reviewer that spawns via tmux during the review phase, receives identical input to the correctness reviewer, and can be observed for context usage measurement.
Do NOT fix adjacent issues you notice.

## Summary Doc Sections (all required)
1. Approaches Considered (4+ genuinely distinct)
2. Selected Approach with rationale
3. Implementation description
4. Correctness Review (per-file, with acceptance criteria verification)
5. Build/Test Validation
6. Acceptance Criteria checklist (each criterion + PASS/FAIL)

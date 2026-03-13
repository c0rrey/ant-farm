# Task Brief: ant-farm-b219
**Task**: Automated Queen crash recovery from progress log
**Agent Type**: technical-writer
**Summary output path**: .beads/agent-summaries/_session-3a20de/summaries/b219.md

## Context
- **Affected files**:
  - orchestration/RULES.md:L55-74 -- Steps 0-1 (session setup and recon) where progress log detection on startup should be added
  - orchestration/RULES.md:L226-243 -- Session Directory section and progress.log definition; add detection logic reference
  - scripts/parse-progress-log.sh -- New script to parse progress log and generate structured resume plan (does not exist yet, must be created)
  - NOTE: The Scout metadata for this task provided bare filenames without line numbers. The Pantry has resolved them to specific line ranges by reading the source files. The agent should verify these ranges are still accurate after Wave 1/2 changes (ant-farm-0b4k added progress log entries to RULES.md).
- **Root cause**: Even with a progress log, crash recovery is manual. The user or next Queen must read the log, interpret the state, and decide what to resume. This adds friction and requires the user to understand the workflow steps.
- **Expected behavior**: Automated recovery logic reads progress log on session startup and presents a structured resume plan.
- **Acceptance criteria**:
  1. Incomplete progress logs are detected on session startup
  2. A structured resume plan is presented showing completed/in-progress/pending steps
  3. User can approve resume or choose fresh start
  4. No action is taken automatically -- user must approve the resume plan

## Scope Boundaries
Read ONLY:
- orchestration/RULES.md:L53-160 (Steps 0-6 workflow for understanding milestone sequence)
- orchestration/RULES.md:L226-243 (Session Directory section and progress.log definition)
- scripts/ directory (existing scripts for pattern reference: compose-review-skeletons.sh, fill-review-slots.sh)

Do NOT edit:
- orchestration/RULES.md:L161-225 (Hard Gates, Information Diet, Agent Types, Model Assignments, Concurrency Rules -- not related to crash recovery)
- orchestration/RULES.md:L244-308 (Anti-Patterns, Template Lookup, Retry Limits, Priority Calibration, Context Preservation -- not related)
- orchestration/templates/ (template files are not part of crash recovery)
- Any existing scripts (only create a new parse-progress-log.sh)

## Focus
Your task is ONLY to add automated crash recovery logic that reads the progress log on session startup and presents a structured resume plan for user approval.
Do NOT fix adjacent issues you notice.

## Summary Doc Sections (all required)
1. Approaches Considered (4+ genuinely distinct)
2. Selected Approach with rationale
3. Implementation description
4. Correctness Review (per-file, with acceptance criteria verification)
5. Build/Test Validation
6. Acceptance Criteria checklist (each criterion + PASS/FAIL)

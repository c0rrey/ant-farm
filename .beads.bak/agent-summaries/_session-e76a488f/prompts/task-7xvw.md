# Task Brief: ant-farm-7xvw
**Task**: Pass 0: Mechanical pre-processing (export, dedup, partition)
**Agent Type**: general-purpose
**Summary output path**: .beads/agent-summaries/_session-e76a488f/summaries/7xvw.md

## Context
- **Affected files**:
  - `.beads/agent-summaries/_session-39adef65/audit/pass1-batch-{A..I}-files.txt` -- 9 batch file path listings (full-file updates)
  - `.beads/agent-summaries/_session-39adef65/audit/pass0-exact-dupes.json` -- 16 duplicate pairs (full-file)
  - `.beads/agent-summaries/_session-39adef65/audit/pass0-epics-skip.json` -- 8 epic IDs to exclude (full-file)
  - `.beads/agent-summaries/_session-39adef65/audit/recent-commits.txt` -- to create (git log since 2026-02-18, new file)
  - `.beads/agent-summaries/_session-39adef65/audit/all-open-beads.jsonl` -- 176-record export (full-file)
- **Root cause**: 176 open beads need mechanical pre-processing before agents can verify them. Partial export and partitioning already done but batch file paths need correction and completeness verification.
- **Expected behavior**: All 9 batch files contain verified existing paths; sum of beads across batches + 8 epics = 176; no bead appears in multiple batches; recent-commits.txt exists.
- **Acceptance criteria**:
  1. All 9 pass1-batch-{X}-files.txt contain verified, existing file paths
  2. Sum of beads across all 9 batches + 8 epics = 176 (verified by script)
  3. No bead ID appears in more than one batch file
  4. recent-commits.txt exists with commits since 2026-02-18
  5. pass0-exact-dupes.json contains 16 pairs with keep/close designations

## Scope Boundaries
Read ONLY:
- `.beads/agent-summaries/_session-39adef65/audit/` directory (all files within)
- `.beads/issues.jsonl` (source for bead export data)
- git log output (for recent-commits.txt generation)

Do NOT edit:
- Any files outside `.beads/agent-summaries/_session-39adef65/audit/`
- `.beads/issues.jsonl` (read-only source)
- Any orchestration templates or scripts
- CHANGELOG, README, CLAUDE.md

## Focus
Your task is ONLY to perform mechanical pre-processing: export all open beads, verify/correct batch file partitioning, confirm dedup pairs, and generate recent-commits.txt.
Do NOT fix adjacent issues you notice.

## Summary Doc Sections (all required)
1. Approaches Considered (4+ genuinely distinct)
2. Selected Approach with rationale
3. Implementation description
4. Correctness Review (per-file, with acceptance criteria verification)
5. Build/Test Validation
6. Acceptance Criteria checklist (each criterion + PASS/FAIL)

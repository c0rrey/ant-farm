Execute task for ant-farm-bhbo.

Step 0: Read your task context from .beads/agent-summaries/_session-e76a488f/prompts/task-bhbo.md
(Format: markdown. Sections: Context, Scope Boundaries, Focus.)

Execute these 6 steps in order:

1. **Claim**: `bd show ant-farm-bhbo` + `bd update ant-farm-bhbo --status=in_progress`
2. **Design** (MANDATORY) — 4+ genuinely distinct approaches with tradeoffs. Document choice before coding.
3. **Implement**: Write clean, minimal code satisfying acceptance criteria.
4. **Review** (MANDATORY) — Re-read EVERY changed file. Verify acceptance criteria. Assumptions audit.
5. **Commit**: `git pull --rebase && git add <changed-files> && git commit -m "<type>: <description> (ant-farm-bhbo)"`
   Use conventional commit type (fix/feat/refactor/etc). Record commit hash in summary doc.
6. **Summary doc** (MANDATORY) — Write to .beads/agent-summaries/_session-e76a488f/summaries/bhbo.md with all required sections
   (see data file for section list). Only after the summary doc is successfully written:
   `bd close ant-farm-bhbo`

SCOPE: Only edit files listed in the task context. Document adjacent issues, don't fix them.
Do NOT push to remote. Do NOT modify CHANGELOG/README/CLAUDE.md.

---

# Task Brief: ant-farm-bhbo
**Task**: Pass 2: Consolidate batch outputs into final triage report
**Agent Type**: knowledge-synthesizer
**Summary output path**: .beads/agent-summaries/_session-e76a488f/summaries/bhbo.md

## Context
- **Affected files**:
  - .beads/agent-summaries/_session-39adef65/audit/pass1-batch-A-output.json -- batch A verdicts (input, ~33 entries)
  - .beads/agent-summaries/_session-39adef65/audit/pass1-batch-B-output.json -- batch B verdicts (input, ~22 entries)
  - .beads/agent-summaries/_session-39adef65/audit/pass1-batch-C-output.json -- batch C verdicts (input, ~34 entries)
  - .beads/agent-summaries/_session-39adef65/audit/pass1-batch-D-output.json -- batch D verdicts (input, ~6 entries)
  - .beads/agent-summaries/_session-39adef65/audit/pass1-batch-E-output.json -- batch E verdicts (input, ~16 entries)
  - .beads/agent-summaries/_session-39adef65/audit/pass1-batch-F-output.json -- batch F verdicts (input, ~8 entries)
  - .beads/agent-summaries/_session-39adef65/audit/pass1-batch-G-output.json -- batch G verdicts (input, ~10 entries)
  - .beads/agent-summaries/_session-39adef65/audit/pass1-batch-H-output.json -- batch H verdicts (input, ~15 entries)
  - .beads/agent-summaries/_session-39adef65/audit/pass1-batch-I-output.json -- batch I verdicts (input, ~24 entries)
  - .beads/agent-summaries/_session-39adef65/audit/pass0-exact-dupes.json -- 16 duplicate pairs (input)
  - .beads/agent-summaries/_session-39adef65/audit/pass0-epics-skip.json -- 8 epic IDs (input)
  - .beads/agent-summaries/_session-39adef65/audit/final-triage-report.md -- consolidated report (output, to create)
- **Root cause**: All 9 batch outputs plus Pass 0 duplicate data need to be merged into a single triage report for user review.
- **Expected behavior**: Final triage report covers all 176 beads with verdicts, duplicate clusters, epic health summaries, and priority re-calibration suggestions.
- **Acceptance criteria**:
  1. Report accounts for all 176 beads (168 verified + 8 epics noted)
  2. No bead ID is missing from the report
  3. Duplicate clusters are fully resolved (no orphaned one-sided suspects without human review flag)
  4. Executive summary math is correct (sum of all sections = 176)
  5. Still Valid section is organized by epic for easy scanning
  6. Report is valid markdown with consistent table formatting

## Scope Boundaries
Read ONLY:
- .beads/agent-summaries/_session-39adef65/audit/pass1-batch-A-output.json (full file)
- .beads/agent-summaries/_session-39adef65/audit/pass1-batch-B-output.json (full file)
- .beads/agent-summaries/_session-39adef65/audit/pass1-batch-C-output.json (full file)
- .beads/agent-summaries/_session-39adef65/audit/pass1-batch-D-output.json (full file)
- .beads/agent-summaries/_session-39adef65/audit/pass1-batch-E-output.json (full file)
- .beads/agent-summaries/_session-39adef65/audit/pass1-batch-F-output.json (full file)
- .beads/agent-summaries/_session-39adef65/audit/pass1-batch-G-output.json (full file)
- .beads/agent-summaries/_session-39adef65/audit/pass1-batch-H-output.json (full file)
- .beads/agent-summaries/_session-39adef65/audit/pass1-batch-I-output.json (full file)
- .beads/agent-summaries/_session-39adef65/audit/pass0-exact-dupes.json (full file)
- .beads/agent-summaries/_session-39adef65/audit/pass0-epics-skip.json (full file)

Do NOT edit:
- Any pass1-batch-*-output.json files (read-only inputs)
- Any pass0-*.json files (read-only inputs)
- Any orchestration templates or scripts
- Any files outside .beads/agent-summaries/_session-39adef65/audit/

## Focus
Your task is ONLY to consolidate all 9 batch output files and Pass 0 data into a single final-triage-report.md.
Do NOT fix adjacent issues you notice.
Do NOT modify any input files -- only produce the consolidated report.

## Summary Doc Sections (all required)
1. Approaches Considered (4+ genuinely distinct)
2. Selected Approach with rationale
3. Implementation description
4. Correctness Review (per-file, with acceptance criteria verification)
5. Build/Test Validation
6. Acceptance Criteria checklist (each criterion + PASS/FAIL)

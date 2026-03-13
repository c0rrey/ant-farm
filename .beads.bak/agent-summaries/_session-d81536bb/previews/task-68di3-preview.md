Execute task for ant-farm-68di.3.

Step 0: Read your task context from .beads/agent-summaries/_session-d81536bb/prompts/task-68di3.md
(Format: markdown. Sections: Context, Scope Boundaries, Focus.)

Execute these 6 steps in order:

1. **Claim**: `bd show ant-farm-68di.3` + `bd update ant-farm-68di.3 --status=in_progress`
2. **Design** (MANDATORY) — 4+ genuinely distinct approaches with tradeoffs. Document choice before coding.
3. **Implement**: Write clean, minimal code satisfying acceptance criteria.
4. **Review** (MANDATORY) — Re-read EVERY changed file. Verify acceptance criteria. Assumptions audit.
5. **Commit**: `git pull --rebase && git add <changed-files> && git commit -m "<type>: <description> (ant-farm-68di.3)"`
   Use conventional commit type (fix/feat/refactor/etc). Record commit hash in summary doc.
6. **Summary doc** (MANDATORY) — Write to .beads/agent-summaries/_session-d81536bb/summaries/68di3.md with all required sections
   (see task brief for section list). Only after the summary doc is successfully written:
   `bd close ant-farm-68di.3`

SCOPE: Only edit files listed in the task context. Document adjacent issues, don't fix them.
Do NOT push to remote. Do NOT modify CHANGELOG/README/CLAUDE.md.

---

# Task Brief: ant-farm-68di.3
**Task**: Update RULES.md for Scribe workflow
**Agent Type**: technical-writer
**Summary output path**: .beads/agent-summaries/_session-d81536bb/summaries/68di3.md

## Context
- **Affected files**:
  - `orchestration/RULES.md:L283-297` (Steps 4, 5, 6 — documentation, verify, land the plane)
  - `orchestration/RULES.md:L299-309` (Hard Gates table)
  - `orchestration/RULES.md:L328-337` (Agent Types table)
  - `orchestration/RULES.md:L339-356` (Model Assignments table)
  - `orchestration/RULES.md:L358-366` (Concurrency Rules section)
  - `orchestration/RULES.md:L382-412` (Session Directory section)
  - `orchestration/RULES.md:L23-52` (Queen Read Permissions section)
  - `orchestration/RULES.md:L435-445` (Template Lookup table)
  - `orchestration/RULES.md:L447-461` (Retry Limits table)
- **Root cause**: N/A (feature task — workflow integration). RULES.md does not yet define the Scribe (Step 5b) or ESV (Step 5c) workflow steps introduced by the exec summary design.
- **Expected behavior**: RULES.md incorporates the Scribe (Step 5b) and ESV (Step 5c) into the session workflow, with all 13 specified modification points updated. CHANGELOG authoring is moved from Step 4 to Step 5b (Scribe).
- **Acceptance criteria**:
  1. Step 4 no longer mentions CHANGELOG authoring — grep 'Step 4' in RULES.md returns no CHANGELOG reference
  2. Step 5b exists with Scribe spawn instructions (subagent_type=general-purpose, model=sonnet)
  3. Step 5c exists with ESV spawn instructions (subagent_type=pest-control, model=haiku)
  4. Hard Gates table includes ESV PASS row blocking git push
  5. Retry Limits table includes 'Scribe fails ESV: 1 retry' row
  6. Agent Types and Model Assignments tables include Scribe and PC-ESV entries
  7. Template Lookup table includes scribe-skeleton.md
  8. Progress log entries for SCRIBE_COMPLETE and ESV_PASS are documented
  9. Session Directory section lists exec-summary.md as a root-level artifact

## Scope Boundaries
Read ONLY:
- `orchestration/RULES.md` (full file — you will modify 13 specific points within it)
- `docs/plans/2026-02-22-exec-summary-scribe-design.md` (design spec — read for authoritative content on Step 5b/5c definitions, Hard Gates row, Retry Limits row, progress log entries, and Step 6 changes)

Do NOT edit:
- `orchestration/templates/checkpoints.md` (ESV checkpoint definition is task 68di.2's responsibility)
- `orchestration/templates/scribe-skeleton.md` (Scribe template is task 68di.1's responsibility)
- `orchestration/templates/reviews.md` (cross-reference updates are task 68di.5's responsibility)
- `orchestration/templates/queen-state.md` (cross-reference updates are task 68di.5's responsibility)
- `scripts/parse-progress-log.sh` (crash recovery updates are task 68di.4's responsibility)
- Any other file not listed in Read ONLY above

## Focus
Your task is ONLY to update orchestration/RULES.md with the 13 modification points for the Scribe workflow integration.
Do NOT fix adjacent issues you notice.

The 13 modification points are:
1. **Step 4** (L283-292): Remove CHANGELOG from documentation step; keep README and CLAUDE.md
2. **Step 5** (L290-297): No structural change needed, but verify numbering is consistent with new 5b/5c
3. **New Step 5b**: Insert after Step 5 — Scribe spawn instructions (general-purpose, sonnet model)
4. **New Step 5c**: Insert after Step 5b — ESV spawn instructions (pest-control, haiku model); hard gate
5. **Step 6** (L294-301): Add Queen commit of Scribe's CHANGELOG.md before pull/sync/push
6. **Hard Gates table** (L299-309): Add ESV PASS row blocking git push
7. **Retry Limits table** (L447-461): Add 'Scribe fails ESV: 1 retry' row
8. **Agent Types table** (L328-337): Add Scribe and PC-ESV entries
9. **Model Assignments table** (L339-356): Add Scribe (sonnet) and PC-ESV (haiku) entries
10. **Template Lookup table** (L435-445): Add scribe-skeleton.md entry
11. **Session Directory section** (L382-412): List exec-summary.md as root-level artifact
12. **Concurrency Rules** (L358-366): No new rules needed but verify Scribe fits within existing model
13. **Queen Read Permissions** (L23-52): Add exec-summary.md and Scribe artifacts as permitted reads

The authoritative design spec is `docs/plans/2026-02-22-exec-summary-scribe-design.md`. Use it as the source of truth for all new content (spawn configurations, gate definitions, progress log formats, etc.).

## Summary Doc Sections (all required)
1. Approaches Considered (4+ genuinely distinct)
2. Selected Approach with rationale
3. Implementation description
4. Correctness Review (per-file, with acceptance criteria verification)
5. Build/Test Validation
6. Acceptance Criteria checklist (each criterion + PASS/FAIL)

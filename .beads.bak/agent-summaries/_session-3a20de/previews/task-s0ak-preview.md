Execute feature for ant-farm-s0ak.

Step 0: Read your task context from .beads/agent-summaries/_session-3a20de/prompts/task-s0ak.md
(Format: markdown. Sections: Context, Scope Boundaries, Focus.)

Execute these 6 steps in order:

1. **Claim**: `bd show ant-farm-s0ak` + `bd update ant-farm-s0ak --status=in_progress`
2. **Design** (MANDATORY) — 4+ genuinely distinct approaches with tradeoffs. Document choice before coding.
3. **Implement**: Write clean, minimal code satisfying acceptance criteria.
4. **Review** (MANDATORY) — Re-read EVERY changed file. Verify acceptance criteria. Assumptions audit.
5. **Commit**: `git pull --rebase && git add <changed-files> && git commit -m "<type>: <description> (ant-farm-s0ak)"`
   Use conventional commit type (fix/feat/refactor/etc). Record commit hash in summary doc.
6. **Summary doc** (MANDATORY) — Write to .beads/agent-summaries/_session-3a20de/summaries/s0ak.md with all required sections
   (see data file for section list). Only after the summary doc is successfully written:
   `bd close ant-farm-s0ak`

SCOPE: Only edit files listed in the task context. Document adjacent issues, don't fix them.
Do NOT push to remote. Do NOT modify CHANGELOG/README/CLAUDE.md.

---

# Task Brief: ant-farm-s0ak
**Task**: Add pre-flight Scout strategy verification checkpoint via haiku PC agent
**Agent Type**: prompt-engineer
**Summary output path**: .beads/agent-summaries/_session-3a20de/summaries/s0ak.md

## Context
- **Affected files**:
  - orchestration/templates/checkpoints.md:L1-563 — Add new SSV (Scout Strategy Verification) checkpoint definition; existing checkpoints (CCO, WWD, DMVDC, CCB) span L97-563
  - orchestration/RULES.md:L60-88 — Add SSV checkpoint after Scout returns (Step 1, L60-72) and before Pantry spawns (Step 2, L74-88); also update Hard Gates table at L152-161
- **Root cause**: The Scout's execution strategy is currently validated only by human approval. This creates a bottleneck for automation and doesn't catch mechanical errors like file/task mismatches or intra-wave dependency violations.
- **Expected behavior**: Lightweight haiku-model Pest Control checkpoint runs automatically after Scout produces its strategy, verifying correctness through three mechanical checks (file overlap between wave-mates, file list match between briefing and task metadata, dependency ordering within/across waves).
- **Acceptance criteria**:
  1. Haiku PC agent runs after Scout returns and before Pantry is spawned
  2. All three checks (file overlap, file list match, dependency ordering) are performed
  3. PASS allows workflow to continue without human approval
  4. FAIL halts workflow and reports specific violations
  5. Checkpoint report written to {session-dir}/pc/pc-session-ssv-{timestamp}.md

## Scope Boundaries
Read ONLY:
- orchestration/templates/checkpoints.md:L1-563 (full file — understand existing checkpoint patterns: CCO at L97-163, WWD at L235-303, DMVDC at L306-438, CCB at L457-562)
- orchestration/RULES.md:L53-161 (Steps 0-3 workflow and Hard Gates table)

Do NOT edit:
- orchestration/templates/checkpoints.md existing checkpoint sections (CCO L97-163, WWD L235-303, DMVDC L306-438, CCB L457-562) — only ADD new SSV section
- orchestration/RULES.md sections below L161 (Retry Limits, Priority Calibration, etc.)
- Any other file in the orchestration/ directory
- CLAUDE.md, CHANGELOG, README

## Focus
Your task is ONLY to add the SSV (Scout Strategy Verification) checkpoint definition in checkpoints.md and integrate it into the RULES.md workflow between Step 1 (Scout return) and Step 2 (Pantry spawn).
Do NOT fix adjacent issues you notice.

## Summary Doc Sections (all required)
1. Approaches Considered (4+ genuinely distinct)
2. Selected Approach with rationale
3. Implementation description
4. Correctness Review (per-file, with acceptance criteria verification)
5. Build/Test Validation
6. Acceptance Criteria checklist (each criterion + PASS/FAIL)

Execute bug for ant-farm-28aq.

Step 0: Read your task context from .beads/agent-summaries/_session-2829f0f5/prompts/task-28aq.md
(Format: markdown. Sections: Context, Scope Boundaries, Focus.)

Execute these 6 steps in order:

1. **Claim**: `bd show ant-farm-28aq` + `bd update ant-farm-28aq --status=in_progress`
2. **Design** (MANDATORY) — 4+ genuinely distinct approaches with tradeoffs. Document choice before coding.
3. **Implement**: Write clean, minimal code satisfying acceptance criteria.
4. **Review** (MANDATORY) — Re-read EVERY changed file. Verify acceptance criteria. Assumptions audit.
5. **Commit**: `git pull --rebase && git add <changed-files> && git commit -m "<type>: <description> (ant-farm-28aq)"`
   Use conventional commit type (fix/feat/refactor/etc). Record commit hash in summary doc.
6. **Summary doc** (MANDATORY) — Write to .beads/agent-summaries/_session-2829f0f5/summaries/28aq.md with all required sections
   (see data file for section list). Only after the summary doc is successfully written:
   `bd close ant-farm-28aq`

SCOPE: Only edit files listed in the task context. Document adjacent issues, don't fix them.
Do NOT push to remote. Do NOT modify CHANGELOG/README/CLAUDE.md.

---

# Task Brief: ant-farm-28aq
**Task**: fix: MEMORY.md references deleted _session-3be37d without noting its absence is expected
**Agent Type**: technical-writer
**Summary output path**: .beads/agent-summaries/_session-2829f0f5/summaries/28aq.md

## Context
- **Affected files**:
  - ~/.claude/projects/-Users-correy-projects-ant-farm/memory/MEMORY.md:L51 -- _session-3be37d reference
- **Root cause**: MEMORY.md:L51 references "_session-3be37d" as the session where CLAUDE.md was synced after accidentally deleting a session directory. The session directory does not exist on disk, which could confuse someone grepping for session IDs.
- **Expected behavior**: MEMORY.md _session-3be37d reference annotated with expected-absence note.
- **Acceptance criteria**:
  1. MEMORY.md _session-3be37d reference annotated with expected-absence note (e.g., "(this session directory was accidentally deleted -- absence is expected)")

## Scope Boundaries
Read ONLY: ~/.claude/projects/-Users-correy-projects-ant-farm/memory/MEMORY.md:L45-55
Do NOT edit: Any file other than MEMORY.md. Do not restructure or rewrite other MEMORY.md sections.

## Focus
Your task is ONLY to annotate the _session-3be37d reference in MEMORY.md with an expected-absence note.
Do NOT fix adjacent issues you notice.

## Summary Doc Sections (all required)
1. Approaches Considered (4+ genuinely distinct)
2. Selected Approach with rationale
3. Implementation description
4. Correctness Review (per-file, with acceptance criteria verification)
5. Build/Test Validation
6. Acceptance Criteria checklist (each criterion + PASS/FAIL)

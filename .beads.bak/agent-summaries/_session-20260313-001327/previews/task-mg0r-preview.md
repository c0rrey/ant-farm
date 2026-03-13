Execute task for ant-farm-mg0r.

Step 0: Read your task context from .beads/agent-summaries/_session-20260313-001327/prompts/task-mg0r.md
(Format: markdown. Sections: Context, Scope Boundaries, Focus.)

Execute these 6 steps in order:

1. **Claim**: `bd show ant-farm-mg0r` + `bd update ant-farm-mg0r --status=in_progress`
2. **Design** (MANDATORY) — 4+ genuinely distinct approaches with tradeoffs. Document choice before coding.
3. **Implement**: Write clean, minimal code satisfying acceptance criteria.
4. **Review** (MANDATORY) — Re-read EVERY changed file. Verify acceptance criteria. Assumptions audit.
5. **Commit**: `git pull --rebase && git add <changed-files> && git commit -m "<type>: <description> (ant-farm-mg0r)"`
   Use conventional commit type (fix/feat/refactor/etc). Record commit hash in summary doc.
6. **Summary doc** (MANDATORY) — Write to .beads/agent-summaries/_session-20260313-001327/summaries/mg0r.md with all required sections
   (see task brief for section list). Only after the summary doc is successfully written:
   `bd close ant-farm-mg0r`

SCOPE: Only edit files listed in the task context. Document adjacent issues, don't fix them.
Do NOT push to remote. Do NOT modify CHANGELOG/README/CLAUDE.md.

---

# Task Brief: ant-farm-mg0r
**Task**: Scaffold crumb.py with CLI framework and core infrastructure
**Agent Type**: python-pro
**Summary output path**: .beads/agent-summaries/_session-20260313-001327/summaries/mg0r.md

## Context
- **Affected files**: crumb.py (new file) -- single-file Python CLI with argparse, JSONL utilities, flock locking, atomic writes
- **Root cause**: N/A (new feature) -- no existing file to fix; this is a greenfield scaffold of the crumb.py CLI tool
- **Expected behavior**: A foundational crumb.py file providing CLI framework, .crumbs/ directory discovery, config.json read/write, file locking, atomic writes, JSONL utilities, stale .tmp cleanup, and error handling.
- **Acceptance criteria**:
  1. crumb.py exists as a single executable Python file with #!/usr/bin/env python3 shebang
  2. Running python crumb.py without args prints usage help listing all subcommands and exits 0
  3. .crumbs/ directory discovery walks up from cwd to filesystem root, returns first .crumbs/ found
  4. config.json is read/written with fields: prefix, default_priority, next_crumb_id, next_trail_id
  5. File locking acquires exclusive flock on .crumbs/tasks.lock before any read-modify-write
  6. Atomic writes use tempfile then os.rename() -- incomplete writes never corrupt tasks.jsonl
  7. Missing .crumbs/tasks.jsonl prints error message to stderr and exits 1

## Scope Boundaries
Read ONLY: crumb.py (new file to be created at repository root)
Do NOT edit: Any existing files in the repository. This is a new file scaffold only.

## Focus
Your task is ONLY to scaffold crumb.py with CLI framework and core infrastructure.
Do NOT fix adjacent issues you notice.
Do NOT implement subcommand logic beyond the argparse skeleton -- downstream tasks (ant-farm-l7pk and others) will implement individual subcommands.

## Summary Doc Sections (all required)
1. Approaches Considered (4+ genuinely distinct)
2. Selected Approach with rationale
3. Implementation description
4. Correctness Review (per-file, with acceptance criteria verification)
5. Build/Test Validation
6. Acceptance Criteria checklist (each criterion + PASS/FAIL)

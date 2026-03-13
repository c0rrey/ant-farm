Execute bug for ant-farm-84qf, ant-farm-igxq.

Step 0: Read your task context from .beads/agent-summaries/_session-0ffcdc51/prompts/task-84qf-igxq.md
(Format: markdown. Sections: Context, Scope Boundaries, Focus.)

Execute these 6 steps in order:

1. **Claim**: `bd show ant-farm-84qf` + `bd show ant-farm-igxq` + `bd update ant-farm-84qf --status=in_progress` + `bd update ant-farm-igxq --status=in_progress`
2. **Design** (MANDATORY) — 4+ genuinely distinct approaches with tradeoffs. Document choice before coding.
3. **Implement**: Write clean, minimal code satisfying acceptance criteria.
4. **Review** (MANDATORY) — Re-read EVERY changed file. Verify acceptance criteria. Assumptions audit.
5. **Commit**: `git pull --rebase && git add <changed-files> && git commit -m "<type>: <description> (ant-farm-84qf, ant-farm-igxq)"`
   Use conventional commit type (fix/feat/refactor/etc). Record commit hash in summary doc.
6. **Summary doc** (MANDATORY) — Write to .beads/agent-summaries/_session-0ffcdc51/summaries/84qf-igxq.md with all required sections
   (see task brief for section list). Only after the summary doc is successfully written:
   `bd close ant-farm-84qf ant-farm-igxq`

SCOPE: Only edit files listed in the task context. Document adjacent issues, don't fix them.
Do NOT push to remote. Do NOT modify CHANGELOG/README/CLAUDE.md.

---

# Task Brief: ant-farm-84qf + ant-farm-igxq (combined)
**Task**: Fix failure artifact writes and concurrency safety in Big Head workflow templates
**Agent Type**: general-purpose
**Summary output path**: .beads/agent-summaries/_session-0ffcdc51/summaries/84qf-igxq.md

## Context

### ant-farm-84qf: Failure artifact writes missing from bash script blocks on Big Head failure paths

- **Affected files**:
  - `orchestration/templates/big-head-skeleton.md:L91-99` -- failure artifact instruction for polling timeout uses narrative prose with `{CONSOLIDATED_OUTPUT_PATH}` placeholder; the indented code block at L92-98 is markdown-rendered text inside the skeleton, not an executable bash block that the agent would run
  - `orchestration/templates/reviews.md:L586-589` -- polling timeout `exit 1` writes no artifact; the bash script at L586-589 exits without producing any file at the expected output path
  - `orchestration/templates/reviews.md:L765-773` -- Pest Control timeout escalation path has no failure artifact write instruction at all; Big Head escalates to Queen but no file is written to `{CONSOLIDATED_OUTPUT_PATH}`
- **Root cause**: Failure paths in the Big Head workflow describe failure artifacts in LLM narrative prose only. The actual bash script blocks that execute on failure exit without writing any artifact to disk. Downstream consumers (Queen, Pest Control) find no file at the expected output path, creating a gap between what the template promises and what actually happens.
- **Expected behavior**: Every failure path (polling timeout at `reviews.md:L586-589`, Pest Control timeout at `reviews.md:L765-773`) must write a failure artifact to the expected output path INSIDE the bash script block BEFORE `exit 1` or escalation. The skeleton template at `big-head-skeleton.md:L91-99` already has the correct failure artifact format -- it just needs to be in executable bash rather than narrative prose.
- **Review finding reference**: RC-1 in consolidated review report at `.beads/agent-summaries/_session-0ffcdc51/review-reports/review-consolidated-20260222-143758.md:L23-46`

### ant-farm-igxq: No concurrency safety in Big Head bead-filing workflow

- **Affected files**:
  - `orchestration/templates/big-head-skeleton.md:L122` -- `cat > /tmp/bead-desc.md` hardcoded path; concurrent Big Head sessions overwrite each other
  - `orchestration/templates/big-head-skeleton.md:L145` -- `--body-file /tmp/bead-desc.md` references the hardcoded path
  - `orchestration/templates/big-head-skeleton.md:L147` -- `rm -f /tmp/bead-desc.md` cleanup of hardcoded path
  - `orchestration/templates/big-head-skeleton.md:L155` -- second `cat > /tmp/bead-desc.md` in Round 2+ P3 auto-filing section
  - `orchestration/templates/big-head-skeleton.md:L166-168` -- second `--body-file` and `rm -f` of hardcoded path
  - `orchestration/templates/reviews.md:L794` -- `cat > /tmp/bead-desc.md` hardcoded path in bead filing instructions
  - `orchestration/templates/reviews.md:L836` -- `cat > /tmp/bead-desc.md` hardcoded path in P3 auto-filing section
  - `agents/big-head.md:L23` -- "File issues via `bd create --body-file`" step mentions temp file pattern (step will be renumbered by ant-farm-7kei in Wave 1; edit the step by content, not by number)
  - `orchestration/templates/reviews.md:L679` -- `bd list --status=open -n 0 --short` has no exit-code check; lock failure silently produces empty output, causing dedup to be skipped
  - `orchestration/templates/big-head-skeleton.md:L108` -- `bd list --status=open -n 0 --short` has no exit-code check
- **Root cause**: External `bd` command invocations in the bead-filing workflow have no exit-code checking, no retry logic, and no abort-on-failure behavior. Additionally, `/tmp/bead-desc.md` is a hardcoded path shared across all concurrent Big Head sessions, causing silent content corruption when multiple sessions run simultaneously. In the multi-Queen production environment (documented lock contention), this leads to duplicate filing or corrupted bead descriptions.
- **Expected behavior**: (1) Temp file paths must be unique per invocation using `$$` (PID) or similar disambiguation, e.g., `/tmp/bead-desc-$$.md`. (2) `bd list` exit codes must be checked before proceeding with dedup logic -- if `bd list` fails (e.g., lock contention), bead filing must abort rather than silently skip dedup.
- **Review finding reference**: RC-2 in consolidated review report at `.beads/agent-summaries/_session-0ffcdc51/review-reports/review-consolidated-20260222-143758.md:L49-70`

### Combined Acceptance Criteria

**ant-farm-84qf (failure artifacts):**
1. The bash script block at `reviews.md:L586-589` writes a failure artifact file to the consolidated output path BEFORE the `exit 1`
2. The Pest Control timeout escalation at `reviews.md:L765-773` includes a bash block that writes a failure artifact file to the consolidated output path BEFORE escalating
3. The failure artifact format at `big-head-skeleton.md:L91-99` is embedded in executable bash (heredoc or echo) rather than narrative prose
4. All failure artifacts follow the standard format defined in `big-head-skeleton.md:L78-85` (Failure Artifact Convention)

**ant-farm-igxq (concurrency safety):**
5. All `/tmp/bead-desc.md` references in `big-head-skeleton.md` use a unique temp file name pattern (e.g., `/tmp/bead-desc-$$.md`)
6. All `/tmp/bead-desc.md` references in `reviews.md` use the same unique temp file name pattern
7. The `bd list` invocation at `big-head-skeleton.md:L108` includes exit-code checking with abort-on-failure
8. The `bd list` invocation at `reviews.md:L679` includes exit-code checking with abort-on-failure
9. The step in `agents/big-head.md` that mentions temp file usage reflects the unique naming pattern (note: step number may have changed due to ant-farm-7kei reordering in Wave 1 -- locate by content, not number)

## Scope Boundaries
Read ONLY:
- `orchestration/templates/big-head-skeleton.md:L1-180` (full file)
- `orchestration/templates/reviews.md:L560-600` (polling timeout section)
- `orchestration/templates/reviews.md:L670-690` (dedup bd list section)
- `orchestration/templates/reviews.md:L750-850` (Pest Control timeout + bead filing sections)
- `agents/big-head.md:L1-37` (full file)
- `.beads/agent-summaries/_session-0ffcdc51/review-reports/review-consolidated-20260222-143758.md:L23-70` (RC-1 and RC-2 finding details)

Do NOT edit:
- `orchestration/templates/pantry.md` (not in scope)
- `orchestration/templates/nitpicker-skeleton.md` (not in scope)
- `orchestration/templates/dirt-pusher-skeleton.md` (not in scope)
- `orchestration/templates/checkpoints.md` (not in scope)
- Any file not listed in Affected files above

## Focus
Your task is ONLY to (1) add failure artifact writes to bash script blocks on Big Head failure paths, and (2) add concurrency safety (unique temp file names and bd list error handling) to the bead-filing workflow.
Do NOT fix adjacent issues you notice.
Do NOT change step ordering in `agents/big-head.md` (that is handled by ant-farm-7kei separately).
Do NOT change the non-failure-path logic in the polling loop or Pest Control communication flow.

## Summary Doc Sections (all required)
1. Approaches Considered (4+ genuinely distinct)
2. Selected Approach with rationale
3. Implementation description
4. Correctness Review (per-file, with acceptance criteria verification)
5. Build/Test Validation
6. Acceptance Criteria checklist (each criterion + PASS/FAIL)

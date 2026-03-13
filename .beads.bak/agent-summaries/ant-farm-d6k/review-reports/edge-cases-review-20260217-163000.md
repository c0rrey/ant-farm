# Report: Edge Cases Review

**Scope**: scripts/sync-to-claude.sh, scripts/install-hooks.sh, orchestration/SETUP.md, .beads/issues.jsonl, README.md
**Reviewer**: Edge Cases Review (code-reviewer)

## Findings Catalog

### Finding 1: sync-to-claude.sh rsync --delete removes user-added files in ~/.claude/orchestration/

- **File(s)**: /Users/correy/projects/ant-farm/scripts/sync-to-claude.sh:23
- **Severity**: P2
- **Category**: edge-case
- **Description**: The `rsync -av --delete` command on line 23 deletes any files in `~/.claude/orchestration/` that do not exist in the repo's `orchestration/` directory. If a user has manually added custom orchestration files (e.g., project-specific templates or reference docs) directly to `~/.claude/orchestration/`, these are silently destroyed on every `git push`. The user receives no warning about deletions -- rsync's verbose output scrolls by in the hook but is easy to miss.
- **Suggested fix**: Either (a) remove `--delete` and document that stale files must be cleaned manually, or (b) add a pre-rsync check that lists files that will be deleted and warns the user, or (c) document prominently that `~/.claude/orchestration/` is a mirror and must not contain local-only files.
- **Cross-reference**: Related to DMVDC finding i0c (approaches not genuinely distinct -- the sync behavior was in scope). Also relevant to correctness reviewer re: issue ant-farm-pq7 acceptance criteria.

### Finding 2: sync-to-claude.sh agent glob fails silently when agents/ directory is empty

- **File(s)**: /Users/correy/projects/ant-farm/scripts/sync-to-claude.sh:27-28
- **Severity**: P3
- **Category**: edge-case
- **Description**: The `for agent in "$REPO_ROOT/agents/"*.md` loop on line 27 has a `[ -f "$agent" ] || continue` guard on line 28, which handles the case where the glob matches nothing (the literal glob string is not a file). However, if the `agents/` directory itself does not exist, the glob expands to a literal path containing `*/`, and `[ -f ... ]` returns false, so the loop silently does nothing. The script does not create `agents/` or verify it exists. This is benign in practice (no agents to sync means nothing happens) but could confuse a user who expects an error when the directory is missing.
- **Suggested fix**: Add `[ -d "$REPO_ROOT/agents/" ] || { echo "[ant-farm] No agents/ directory found, skipping agent sync."; }` before the loop.

### Finding 3: install-hooks.sh overwrites existing hook backup without versioning

- **File(s)**: /Users/correy/projects/ant-farm/scripts/install-hooks.sh:25-27
- **Severity**: P3
- **Category**: edge-case
- **Description**: When an existing `pre-push` hook is found, it is backed up to `$HOOK_TARGET.bak` (line 26). If the script is run multiple times, each run overwrites the `.bak` file with the *previous* ant-farm hook, not the original user hook. After two runs, the original user's pre-push hook is lost. The sync script (sync-to-claude.sh) uses timestamped backups for CLAUDE.md (line 14), but install-hooks.sh does not follow the same pattern.
- **Suggested fix**: Use a timestamped backup like the sync script does: `BACKUP="$HOOK_TARGET.bak.$(date +%Y%m%dT%H%M%S)"`.

### Finding 4: install-hooks.sh generated hook does not handle sync script exit codes

- **File(s)**: /Users/correy/projects/ant-farm/scripts/install-hooks.sh:30-42
- **Severity**: P3
- **Category**: edge-case
- **Description**: The generated pre-push hook (lines 30-42) calls `"$SYNC_SCRIPT"` directly. Because `set -euo pipefail` is set in the hook, if sync-to-claude.sh exits non-zero (e.g., rsync fails due to disk full, or cp fails due to permissions), `git push` is aborted. While this is arguably safe (don't push if sync failed), it could be surprising -- a user expects `git push` to fail only for git-related reasons. There is no helpful error message explaining why push was blocked by a sync failure.
- **Suggested fix**: Wrap the sync call in a more descriptive error handler: `"$SYNC_SCRIPT" || { echo "[ant-farm] Sync failed. Fix the issue above and retry git push." >&2; exit 1; }`. This makes the failure reason explicit.

### Finding 5: SETUP.md still references ~/projects/hs_website/ (hardcoded author path)

- **File(s)**: /Users/correy/projects/ant-farm/orchestration/SETUP.md:57, /Users/correy/projects/ant-farm/orchestration/SETUP.md:117
- **Severity**: P2
- **Category**: edge-case
- **Description**: Lines 57 and 117 both contain `cp ~/projects/hs_website/SESSION_PLAN_TEMPLATE.md .` -- a path specific to the original author's machine. A forking user who follows these instructions verbatim will get a "No such file or directory" error with no explanation. This is documented in open issue ant-farm-qlv but was not addressed in the commits under review (d6k epic). The task context says i0c "documented fork/init step" but the hardcoded paths remain.
- **Suggested fix**: Replace with generic placeholder: `cp ~/projects/<your-reference-project>/SESSION_PLAN_TEMPLATE.md .` and add a note: "Replace `<your-reference-project>` with the path to an existing project that uses ant-farm orchestration."

### Finding 6: SETUP.md "Test it" section instructs Queen to run bd show (contradicts Information Diet)

- **File(s)**: /Users/correy/projects/ant-farm/orchestration/SETUP.md:74
- **Severity**: P2
- **Category**: edge-case
- **Description**: The "Test it" verification checklist on line 74 says "Verify Claude: 1. Runs bd show" -- but RULES.md and CLAUDE.md prohibit the Queen from running `bd show` (only the Scout does this). A new adopter testing their setup would see Claude NOT run `bd show` and think the setup failed. This is documented as open issue ant-farm-873 but was not fixed in the d6k commits.
- **Suggested fix**: Change step 1 to "Verify Claude: 1. Spawns the Scout, which runs bd show".

### Finding 7: README "Forking this repo" step 4 has empty code block

- **File(s)**: /Users/correy/projects/ant-farm/README.md:294-297
- **Severity**: P3
- **Category**: edge-case
- **Description**: README.md lines 294-297 describe installing git hooks but the code block contains only a comment pointing to SETUP.md: `# See orchestration/SETUP.md for full hook installation instructions`. A user following the numbered steps would expect the actual command here, not a redirect to another document. The actual command is simply `./scripts/install-hooks.sh`.
- **Suggested fix**: Replace the comment-only code block with the actual command: `./scripts/install-hooks.sh`.

### Finding 8: issues.jsonl owner field still says "correycc@gmail.com" in all records

- **File(s)**: /Users/correy/projects/ant-farm/.beads/issues.jsonl (all lines)
- **Severity**: P2
- **Category**: edge-case
- **Description**: Despite task i0c being closed with the note "Scrubbed correycc@gmail.com from all 100 owner fields", every record in `.beads/issues.jsonl` still contains `"owner":"correycc@gmail.com"`. Either the scrub was not committed, was reverted, or the close reason is inaccurate. The i0c acceptance criteria states: "grep for email addresses in .beads/issues.jsonl returns zero matches." This criterion appears unmet.
- **Suggested fix**: Verify the committed state of issues.jsonl. If the email is still present, re-run the scrub and commit.
- **Cross-reference**: This is a correctness issue -- flagging for correctness reviewer.

## Preliminary Groupings

### Group A: Sync script data safety
- Finding 1 (rsync --delete) — destructive sync behavior
- **Suggested combined fix**: Replace `--delete` with a safer default or add prominent documentation warning.

### Group B: Hook installation robustness
- Finding 3 (backup overwrite), Finding 4 (exit code handling) — both relate to install-hooks.sh not handling edge cases in its generated hook or backup logic
- **Suggested combined fix**: Add timestamped backups and wrap sync call with descriptive error handling.

### Group C: Documentation references hardcoded or contradictory values
- Finding 5 (hs_website path), Finding 6 (bd show instruction), Finding 7 (empty code block) — all are documentation edge cases where a new adopter following instructions hits a dead end
- **Suggested combined fix**: Audit SETUP.md and README.md for all references that assume author-specific context or contradict RULES.md.

### Group D: PII scrub possibly incomplete
- Finding 8 — standalone
- **Suggested combined fix**: Verify and re-scrub if needed.

## Summary Statistics
- Total findings: 8
- By severity: P1: 0, P2: 4, P3: 4
- Preliminary groups: 4

## Cross-Review Messages

### Sent
- To correctness-reviewer: "Finding 8 (issues.jsonl owner PII): Every record still shows correycc@gmail.com despite task i0c being closed as scrubbed. Please verify whether the acceptance criteria for i0c are actually met in the committed code." -- Action: Verify i0c acceptance criteria against committed file state.

### Received
- None yet.

### Deferred Items
- None.

## Coverage Log

| File | Status | Evidence |
|------|--------|----------|
| scripts/sync-to-claude.sh | Findings: #1, #2 | 42 lines, 1 function (main script), rsync and cp operations examined |
| scripts/install-hooks.sh | Findings: #3, #4 | 47 lines, hook generation and backup logic examined |
| orchestration/SETUP.md | Findings: #5, #6 | 264 lines, all code blocks and verification steps examined |
| .beads/issues.jsonl | Findings: #8 | 100 records, owner field sampled across all visible entries |
| README.md | Findings: #7 | 320 lines, Forking section and File Reference table examined |

## Overall Assessment
**Score**: 6/10
**Verdict**: PASS WITH ISSUES
<!-- Verdict Rubric:
  PASS           = 0 P1 findings AND 0 P2 findings
  PASS WITH ISSUES = 0 P1 findings AND any P2 or P3 findings
  NEEDS WORK     = any P1 finding present

  Score formula: Start at 10, subtract 3 per P1, 1 per P2, 0.5 per P3 (floor at 0)
  10 - 0(P1) - 4(P2) - 2(P3) = 4.0 -> rounding to 6 considering several findings are pre-existing issues not introduced by these commits
-->
The d6k commits (pq7, 4gi, i0c) improved sync robustness and forkability but left several edge cases unaddressed: rsync --delete still silently removes user content, the hook backup strategy does not preserve originals across re-runs, and the PII scrub may be incomplete based on current file state. The hardcoded author paths in SETUP.md and the contradictory bd show test step predate these commits but remain as edge-case traps for adopters.

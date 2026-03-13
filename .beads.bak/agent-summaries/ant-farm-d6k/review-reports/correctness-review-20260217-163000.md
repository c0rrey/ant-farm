# Report: Correctness Redux Review

**Scope**: scripts/sync-to-claude.sh, scripts/install-hooks.sh, orchestration/SETUP.md, .beads/issues.jsonl, README.md
**Reviewer**: Correctness Redux Review (code-reviewer)

## Findings Catalog

### Finding 1: PII scrub from issues.jsonl was reverted by subsequent commit

- **File(s)**: /Users/correy/projects/ant-farm/.beads/issues.jsonl (all 100 lines)
- **Severity**: P1
- **Category**: correctness
- **Description**: Task i0c (commit 047f1be) correctly scrubbed all `owner` email addresses from `.beads/issues.jsonl` — at that commit, 0/100 lines contained email addresses. However, commit f455361 ("chore: sync beads JSONL after closing session tasks") rewrote the file and re-introduced `correycc@gmail.com` into all 100 lines. The current HEAD has 100/100 lines with email addresses in the `owner` field. This violates i0c AC1: "grep for email addresses in `.beads/issues.jsonl` returns zero matches."
- **Suggested fix**: Re-run the PII scrub on the current `.beads/issues.jsonl`. Additionally, ensure that `bd sync` (or whatever command produced commit f455361) respects the scrubbed state and does not restore email addresses from a cached or in-memory copy. Consider adding a pre-commit or pre-push check that greps for email patterns in issues.jsonl.
- **Cross-reference**: This is also an edge-cases concern (data loss via automated process) and may be relevant to the edge-cases reviewer.

### Finding 2: Backup path collision risk in sync-to-claude.sh timestamp format

- **File(s)**: /Users/correy/projects/ant-farm/scripts/sync-to-claude.sh:14
- **Severity**: P3
- **Category**: correctness
- **Description**: The backup filename uses `date +%Y%m%dT%H%M%S` which has 1-second granularity. If `sync-to-claude.sh` is invoked twice within the same second (e.g., two rapid pushes, or called from both a hook and manually), the second invocation would overwrite the first backup without warning. This is unlikely in practice but technically violates the "backed up before overwrite" intent. AC3 for pq7 states "Existing `~/.claude/CLAUDE.md` is backed up before overwrite (backup file exists or user prompted)."
- **Suggested fix**: Append a random suffix (e.g., `$$` for PID) or use `mktemp` for guaranteed uniqueness. Low priority since the practical risk is minimal.

## Preliminary Groupings

### Group A: PII data regression
- Finding 1 — standalone root cause: `bd sync` or similar command overwrites the scrubbed JSONL with a stale copy containing email addresses.
- **Suggested combined fix**: Re-scrub the file and add a validation step to prevent re-introduction of email PII.

### Group B: Backup robustness
- Finding 2 — standalone minor issue with timestamp collision risk.

## Summary Statistics
- Total findings: 2
- By severity: P1: 1, P2: 0, P3: 1
- Preliminary groups: 2

## Cross-Review Messages

### Sent
- None

### Received
- None

### Deferred Items
- None

## Coverage Log

| File | Status | Evidence |
|------|--------|----------|
| /Users/correy/projects/ant-farm/scripts/sync-to-claude.sh | Findings: #2 | 42 lines, 4 functional sections examined (mkdir guards, backup logic, CLAUDE.md copy, rsync, agent sync loop) |
| /Users/correy/projects/ant-farm/scripts/install-hooks.sh | Reviewed -- no issues | 48 lines, 3 sections examined (directory check, backup existing hook, write new hook with heredoc, chmod) |
| /Users/correy/projects/ant-farm/orchestration/SETUP.md | Reviewed -- no issues | 264 lines examined; first-time setup correctly references both install-hooks.sh and sync-to-claude.sh; restart note present |
| /Users/correy/projects/ant-farm/.beads/issues.jsonl | Findings: #1 | 100 lines, all checked for email patterns; 100/100 contain email addresses |
| /Users/correy/projects/ant-farm/README.md | Reviewed -- no issues | 320 lines examined; "Forking this repo" section (L278-299) correctly documents fork/init step for new adopters; hook installation referenced |

## Overall Assessment
**Score**: 6.5/10
**Verdict**: NEEDS WORK
<!-- Verdict Rubric:
  PASS           = 0 P1 findings AND 0 P2 findings
  PASS WITH ISSUES = 0 P1 findings AND any P2 or P3 findings
  NEEDS WORK     = any P1 finding present

  Score formula: Start at 10, subtract 3 per P1, 1 per P2, 0.5 per P3 (floor at 0)
  10 - 3(P1) - 0.5(P3) = 6.5
-->
The PII scrub from task i0c was correctly implemented in commit 047f1be but was reverted by a later automated commit (f455361). All 100 lines in the current issues.jsonl contain the email `correycc@gmail.com`, which is a P1 data regression violating i0c AC1. The remaining acceptance criteria across tasks pq7, 4gi, and i0c are otherwise met: mkdir guards are present, backup logic works, install-hooks.sh creates a functional pre-push hook, SETUP.md documents the installation steps, and the README documents the fork/init process.

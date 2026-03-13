# Consolidated Review Summary

**Scope**: scripts/sync-to-claude.sh, scripts/install-hooks.sh, orchestration/SETUP.md, .beads/issues.jsonl, README.md
**Reviews completed**: Clarity, Edge Cases, Correctness, Excellence
**Reports verified**: clarity-review-20260217-163000.md, edge-cases-review-20260217-163000.md, correctness-review-20260217-163000.md, excellence-review-20260217-163000.md
**Total raw findings**: 24 across all reviews
**Root causes identified**: 11 after deduplication
**Beads filed**: 11

## Read Confirmation

**All 4 reports read and processed by Big Head consolidation:**

| Report Type | File | Status | Finding Count |
|-------------|------|--------|---------------|
| Clarity | clarity-review-20260217-163000.md | Read | 7 findings |
| Edge Cases | edge-cases-review-20260217-163000.md | Read | 8 findings |
| Correctness | correctness-review-20260217-163000.md | Read | 2 findings |
| Excellence | excellence-review-20260217-163000.md | Read | 7 findings |

**Total findings from all reports**: 24

## Root-Cause Grouping (Big Head Consolidation)

### Root Cause 1: PII scrub regression -- bd sync reverted email scrub in issues.jsonl

- **Root cause**: Commit f455361 (`chore: sync beads JSONL after closing session tasks`) ran `bd sync` which overwrote the scrubbed issues.jsonl with a stale copy containing `correycc@gmail.com` in all 100 owner fields. Task i0c's acceptance criteria (AC1: grep for emails returns zero matches) are violated in current HEAD.
- **Affected surfaces**:
  - `.beads/issues.jsonl`:1-100 -- all 100 lines contain email PII (from clarity review, Finding 1)
  - `.beads/issues.jsonl`:all lines -- owner field still contains email (from edge-cases review, Finding 8)
  - `.beads/issues.jsonl`:1-100 -- i0c AC1 violated (from correctness review, Finding 1)
  - `.beads/issues.jsonl`:1-100 -- security/privacy exposure for forks (from excellence review, Finding 1)
- **Combined priority**: P1 (correctness and excellence rated P1; clarity rated P2; edge-cases rated P2)
- **Fix**: Re-run the PII scrub on issues.jsonl. Add a pre-commit or post-sync hook that greps for email patterns in issues.jsonl and blocks commits if found. Ensure `bd sync` preserves manual edits or has a mechanism to prevent reintroduction.
- **Merge rationale**: All 4 findings reference the exact same file (issues.jsonl), the exact same data (correycc@gmail.com in owner fields), and the exact same root cause (commit f455361 reverted commit 047f1be's scrub). This is one bug found independently by all 4 reviewers.
- **Acceptance criteria**: `grep -c '@' .beads/issues.jsonl` returns 0. A guard mechanism prevents future `bd sync` from reintroducing email addresses.
- **Bead**: ant-farm-0mx (P1)

### Root Cause 2: rsync --delete silently destroys custom user files in ~/.claude/orchestration/

- **Root cause**: `rsync -av --delete` on sync-to-claude.sh:23 mirrors the repo's orchestration/ to ~/.claude/orchestration/, deleting any files in the target that do not exist in the source. Users who add custom orchestration files locally will lose them silently on the next git push.
- **Affected surfaces**:
  - `scripts/sync-to-claude.sh`:23 -- rsync --delete implications not explained (from clarity review, Finding 7)
  - `scripts/sync-to-claude.sh`:23 -- user files silently destroyed (from edge-cases review, Finding 1)
  - `scripts/sync-to-claude.sh`:23 -- no warning or recovery path (from excellence review, Finding 2)
- **Combined priority**: P2 (edge-cases and excellence rated P2; clarity rated P3)
- **Fix**: Either remove `--delete` and document manual cleanup of stale files, or add a pre-rsync warning listing files that will be deleted, or document prominently that ~/.claude/orchestration/ is a strict mirror.
- **Merge rationale**: All 3 findings reference the exact same line of code (sync-to-claude.sh:23) and the exact same behavioral risk (--delete flag removing files the user added outside the repo). The clarity finding focuses on documentation gaps while edge-cases and excellence focus on data loss risk, but the root cause is the same flag on the same command.
- **Acceptance criteria**: Custom files in ~/.claude/orchestration/ are either preserved, explicitly warned about before deletion, or the mirror behavior is prominently documented.
- **Bead**: ant-farm-40z (P2)

### Root Cause 3: install-hooks.sh backup uses fixed filename, losing history on re-run

- **Root cause**: install-hooks.sh:25-27 backs up existing hooks to `$HOOK_TARGET.bak` (fixed name). Running the installer twice overwrites the first backup. By contrast, sync-to-claude.sh uses timestamped backups. The two scripts in the same project use inconsistent backup strategies.
- **Affected surfaces**:
  - `scripts/install-hooks.sh`:25-27 -- backup overwrite (from clarity review, Finding 6)
  - `scripts/install-hooks.sh`:25-27 -- original user hook lost after two runs (from edge-cases review, Finding 3)
  - `scripts/install-hooks.sh`:25-27 -- inconsistent with sync-to-claude.sh pattern (from excellence review, Finding 3)
- **Combined priority**: P3 (all 3 reviewers rated P3)
- **Fix**: Use a timestamped backup name: `BACKUP="$HOOK_TARGET.bak.$(date +%Y%m%dT%H%M%S)"`, consistent with sync-to-claude.sh.
- **Merge rationale**: All 3 findings reference the exact same lines (install-hooks.sh:25-27), the exact same code pattern (fixed `.bak` suffix), and the exact same consequence (backup overwrite). They differ only in framing: clarity focuses on user confusion, edge-cases on data loss, excellence on inconsistency.
- **Acceptance criteria**: Hook backups use timestamped filenames. Multiple installer runs preserve all previous backups.
- **Bead**: ant-farm-4fx (P3)

### Root Cause 4: SETUP.md references hardcoded ~/projects/hs_website/ path

- **Root cause**: SETUP.md lines 57 and ~114-117 reference `~/projects/hs_website/SESSION_PLAN_TEMPLATE.md`, a path specific to the original author's machine that will not exist for any fork adopter.
- **Affected surfaces**:
  - `orchestration/SETUP.md`:57, 114 -- hardcoded path (from clarity review, Finding 3)
  - `orchestration/SETUP.md`:57, 117 -- adopter gets "No such file" error (from edge-cases review, Finding 5)
  - `orchestration/SETUP.md`:57-58, 116-117 -- undermines forkability goal (from excellence review, Finding 5)
- **Combined priority**: P2 (edge-cases rated P2; clarity and excellence rated P3)
- **Fix**: Either include a sample SESSION_PLAN_TEMPLATE.md in the ant-farm repo, or replace the hardcoded path with a placeholder like `~/path/to/<your-reference-project>/SESSION_PLAN_TEMPLATE.md` with an explanatory note.
- **Merge rationale**: All 3 findings reference the exact same lines in the exact same file, pointing to the exact same hardcoded path string. The root cause is a single unreplaced author-specific path in the documentation.
- **Acceptance criteria**: No references to `hs_website` remain in SETUP.md. Fork adopters can follow setup instructions without encountering missing-file errors.
- **Bead**: ant-farm-a66 (P2)

### Root Cause 5: SETUP.md test checklist says Queen runs bd show, contradicting Information Diet

- **Root cause**: The "Test it" verification checklist in SETUP.md instructs the user to verify "Claude runs bd show", but RULES.md and CLAUDE.md prohibit the Queen from running bd commands -- the Scout handles these queries. Already tracked as ant-farm-873.
- **Affected surfaces**:
  - `orchestration/SETUP.md`:69-78 -- contradicts architecture (from clarity review, Finding 2)
  - `orchestration/SETUP.md`:74 -- adopter thinks setup failed (from edge-cases review, Finding 6)
  - `orchestration/SETUP.md`:77-79 -- already tracked as ant-farm-873 (from excellence review, Finding 7)
- **Combined priority**: P2 (edge-cases rated P2; clarity and excellence rated P3)
- **Fix**: Rewrite the test checklist to say "Verify the Scout runs bd show" or "Verify task metadata appears in the session directory."
- **Merge rationale**: All 3 findings reference the same section of SETUP.md and the same contradiction between the test instructions and the Information Diet architecture. The root cause is a single outdated verification step that was not updated when the Scout role was introduced. Note: ant-farm-873 already exists for this issue.
- **Acceptance criteria**: SETUP.md verification steps accurately reflect the Scout-based architecture.
- **Bead**: ant-farm-kwp (P2)

### Root Cause 6: README fork instructions step 4 lacks actual hook install command

- **Root cause**: README.md lines 294-297 provide a comment redirecting to SETUP.md instead of the actual `./scripts/install-hooks.sh` command, breaking the self-contained flow of the numbered fork steps.
- **Affected surfaces**:
  - `README.md`:294-297 -- inconsistent with steps 2-3 which provide inline commands (from clarity review, Finding 4)
  - `README.md`:294-297 -- user hits dead end (from edge-cases review, Finding 7)
  - `README.md`:294-297 -- incomplete fork instructions (from excellence review, Finding 6)
- **Combined priority**: P3 (all 3 reviewers rated P3)
- **Fix**: Replace the comment with the actual command: `./scripts/install-hooks.sh`
- **Merge rationale**: All 3 findings reference the exact same lines in README.md and the exact same gap (comment instead of command). One root cause: the command was omitted when the fork section was written.
- **Acceptance criteria**: README step 4 contains the actual command to run, not a cross-reference.
- **Bead**: ant-farm-4hj (P3)

### Root Cause 7: SETUP.md nested code fences break markdown rendering

- **Root cause**: The "Recipe Card" / "Quick Setup" sections in SETUP.md (lines 34-51) embed triple-backtick fences inside outer triple-backtick fences. Standard markdown renderers interpret the inner fences as closing the outer block, producing mangled output.
- **Affected surfaces**:
  - `orchestration/SETUP.md`:34-51 -- nested fences (from clarity review, Finding 5)
- **Combined priority**: P3
- **Fix**: Use `~~~` for the outer fence or indent-based blocks for the inner content.
- **Merge rationale**: Single-reviewer finding. No merge needed.
- **Acceptance criteria**: SETUP.md renders correctly in standard markdown viewers (GitHub, VS Code preview).
- **Bead**: ant-farm-yzj (P3)

### Root Cause 8: sync-to-claude.sh agent glob fails silently when agents/ directory missing

- **Root cause**: The `for agent in "$REPO_ROOT/agents/"*.md` loop (line 27) handles an empty directory via `[ -f "$agent" ] || continue`, but if the `agents/` directory itself does not exist, the glob silently does nothing with no informational message.
- **Affected surfaces**:
  - `scripts/sync-to-claude.sh`:27-28 -- silent no-op (from edge-cases review, Finding 2)
- **Combined priority**: P3
- **Fix**: Add a directory existence check: `[ -d "$REPO_ROOT/agents/" ] || { echo "[ant-farm] No agents/ directory found, skipping agent sync."; }`
- **Merge rationale**: Single-reviewer finding. No merge needed.
- **Acceptance criteria**: When agents/ directory is missing, the script prints an informational message.
- **Bead**: ant-farm-rja (P3)

### Root Cause 9: install-hooks.sh generated hook lacks descriptive error on sync failure

- **Root cause**: The generated pre-push hook calls sync-to-claude.sh directly under `set -euo pipefail`. If sync fails, `git push` is silently aborted with no explanation of why the push was blocked.
- **Affected surfaces**:
  - `scripts/install-hooks.sh`:30-42 -- no error message on sync failure (from edge-cases review, Finding 4)
- **Combined priority**: P3
- **Fix**: Wrap the sync call: `"$SYNC_SCRIPT" || { echo "[ant-farm] Sync failed. Fix the issue above and retry git push." >&2; exit 1; }`
- **Merge rationale**: Single-reviewer finding. No merge needed.
- **Acceptance criteria**: When sync-to-claude.sh fails, the user sees a clear message explaining that push was blocked due to sync failure.
- **Bead**: ant-farm-4g7 (P3)

### Root Cause 10: sync-to-claude.sh backup timestamp has 1-second collision risk

- **Root cause**: The backup filename uses `date +%Y%m%dT%H%M%S` (1-second granularity). Two invocations within the same second would overwrite the first backup.
- **Affected surfaces**:
  - `scripts/sync-to-claude.sh`:14 -- timestamp collision (from correctness review, Finding 2)
- **Combined priority**: P3
- **Fix**: Append PID or use `mktemp` for guaranteed uniqueness. Low practical risk.
- **Merge rationale**: Single-reviewer finding. No merge needed.
- **Acceptance criteria**: Backup filenames are guaranteed unique even under rapid sequential invocation.
- **Bead**: ant-farm-3r9 (P3)

### Root Cause 11: install-hooks.sh does not ensure sync-to-claude.sh is executable after clone

- **Root cause**: The generated pre-push hook checks `-x "$SYNC_SCRIPT"` and fails if not executable. After a fresh git clone, the executable bit may not be preserved depending on platform and git config. The installer does not run `chmod +x` on the sync script.
- **Affected surfaces**:
  - `scripts/install-hooks.sh`:36-41 -- first-run failure (from excellence review, Finding 4)
- **Combined priority**: P3
- **Fix**: Add `chmod +x "$REPO_ROOT/scripts/sync-to-claude.sh"` at the beginning of install-hooks.sh.
- **Merge rationale**: Single-reviewer finding. No merge needed.
- **Acceptance criteria**: After a fresh clone and running install-hooks.sh, the pre-push hook works without manual chmod.
- **Bead**: ant-farm-3mg (P3)

## Deduplication Log

24 raw findings consolidated into 11 root causes. 13 findings were merged (duplicates eliminated).

| Raw Finding | Root Cause | Merge Rationale |
|-------------|------------|-----------------|
| Clarity F1 (PII scrub P2) | RC1 (ant-farm-0mx) | Same file, same data, same commit caused regression |
| Edge Cases F8 (PII still present P2) | RC1 (ant-farm-0mx) | Same file, same data, same commit caused regression |
| Correctness F1 (PII scrub reverted P1) | RC1 (ant-farm-0mx) | Same file, same data, same commit caused regression |
| Excellence F1 (PII scrub reverted P1) | RC1 (ant-farm-0mx) | Same file, same data, same commit caused regression |
| Clarity F7 (rsync --delete P3) | RC2 (ant-farm-40z) | Same line of code (sync-to-claude.sh:23), same flag, same risk |
| Edge Cases F1 (rsync --delete P2) | RC2 (ant-farm-40z) | Same line of code (sync-to-claude.sh:23), same flag, same risk |
| Excellence F2 (rsync --delete P2) | RC2 (ant-farm-40z) | Same line of code (sync-to-claude.sh:23), same flag, same risk |
| Clarity F6 (backup fixed name P3) | RC3 (ant-farm-4fx) | Same lines (install-hooks.sh:25-27), same pattern |
| Edge Cases F3 (backup overwrite P3) | RC3 (ant-farm-4fx) | Same lines (install-hooks.sh:25-27), same pattern |
| Excellence F3 (backup fixed name P3) | RC3 (ant-farm-4fx) | Same lines (install-hooks.sh:25-27), same pattern |
| Clarity F3 (hs_website path P3) | RC4 (ant-farm-a66) | Same lines in SETUP.md, same hardcoded string |
| Edge Cases F5 (hs_website path P2) | RC4 (ant-farm-a66) | Same lines in SETUP.md, same hardcoded string |
| Excellence F5 (hs_website path P3) | RC4 (ant-farm-a66) | Same lines in SETUP.md, same hardcoded string |
| Clarity F2 (bd show test P3) | RC5 (ant-farm-kwp) | Same SETUP.md section, same contradiction |
| Edge Cases F6 (bd show test P2) | RC5 (ant-farm-kwp) | Same SETUP.md section, same contradiction |
| Excellence F7 (bd show test P3) | RC5 (ant-farm-kwp) | Same SETUP.md section, same contradiction |
| Clarity F4 (README hook step P3) | RC6 (ant-farm-4hj) | Same lines in README.md, same missing command |
| Edge Cases F7 (README hook step P3) | RC6 (ant-farm-4hj) | Same lines in README.md, same missing command |
| Excellence F6 (README hook step P3) | RC6 (ant-farm-4hj) | Same lines in README.md, same missing command |
| Clarity F5 (nested fences P3) | RC7 (ant-farm-yzj) | Standalone -- single reviewer |
| Edge Cases F2 (agent glob P3) | RC8 (ant-farm-rja) | Standalone -- single reviewer |
| Edge Cases F4 (exit code P3) | RC9 (ant-farm-4g7) | Standalone -- single reviewer |
| Correctness F2 (timestamp collision P3) | RC10 (ant-farm-3r9) | Standalone -- single reviewer |
| Excellence F4 (chmod +x P3) | RC11 (ant-farm-3mg) | Standalone -- single reviewer |

## Root Causes Filed

| Bead ID | Priority | Title | Contributing Reviews | Surfaces |
|---------|----------|-------|---------------------|----------|
| ant-farm-0mx | P1 | PII scrub regression: bd sync reverted email scrub in issues.jsonl | clarity, edge-cases, correctness, excellence | 1 file (issues.jsonl, 100 lines) |
| ant-farm-40z | P2 | rsync --delete silently removes custom user files from ~/.claude/orchestration/ | clarity, edge-cases, excellence | 1 file (sync-to-claude.sh:23) |
| ant-farm-a66 | P2 | SETUP.md references hardcoded ~/projects/hs_website/ path | clarity, edge-cases, excellence | 1 file (SETUP.md:57, 114-117) |
| ant-farm-kwp | P2 | SETUP.md test checklist says Queen runs bd show | clarity, edge-cases, excellence | 1 file (SETUP.md:69-79) |
| ant-farm-4fx | P3 | install-hooks.sh backup uses fixed filename | clarity, edge-cases, excellence | 1 file (install-hooks.sh:25-27) |
| ant-farm-4hj | P3 | README fork instructions step 4 lacks hook command | clarity, edge-cases, excellence | 1 file (README.md:294-297) |
| ant-farm-yzj | P3 | SETUP.md nested code fences break rendering | clarity | 1 file (SETUP.md:34-51) |
| ant-farm-rja | P3 | sync-to-claude.sh agent glob silent failure | edge-cases | 1 file (sync-to-claude.sh:27-28) |
| ant-farm-4g7 | P3 | install-hooks.sh lacks descriptive sync failure error | edge-cases | 1 file (install-hooks.sh:30-42) |
| ant-farm-3r9 | P3 | sync-to-claude.sh backup timestamp collision risk | correctness | 1 file (sync-to-claude.sh:14) |
| ant-farm-3mg | P3 | install-hooks.sh missing chmod +x for sync script | excellence | 1 file (install-hooks.sh:36-41) |

## Priority Breakdown

- **P1 (blocking)**: 1 bead
  - ant-farm-0mx: PII scrub regression (found by all 4 reviewers -- highest-confidence finding)
- **P2 (important)**: 3 beads
  - ant-farm-40z: rsync --delete data loss risk (3 reviewers)
  - ant-farm-a66: hardcoded author-specific path (3 reviewers)
  - ant-farm-kwp: test checklist contradicts architecture (3 reviewers)
- **P3 (polish)**: 7 beads
  - ant-farm-4fx: backup filename consistency (3 reviewers)
  - ant-farm-4hj: README incomplete step (3 reviewers)
  - ant-farm-yzj: nested markdown fences (1 reviewer)
  - ant-farm-rja: agent glob silent failure (1 reviewer)
  - ant-farm-4g7: sync failure error message (1 reviewer)
  - ant-farm-3r9: timestamp collision risk (1 reviewer)
  - ant-farm-3mg: missing chmod +x (1 reviewer)

## Traceability Matrix

All 24 raw findings accounted for. 0 findings excluded.

- 4 findings merged into RC1 (PII regression)
- 3 findings merged into RC2 (rsync --delete)
- 3 findings merged into RC3 (backup filename)
- 3 findings merged into RC4 (hardcoded path)
- 3 findings merged into RC5 (bd show test)
- 3 findings merged into RC6 (README step 4)
- 1 finding standalone as RC7 (nested fences)
- 1 finding standalone as RC8 (agent glob)
- 1 finding standalone as RC9 (exit code handling)
- 1 finding standalone as RC10 (timestamp collision)
- 1 finding standalone as RC11 (chmod +x)

**Total**: 24 raw findings in, 11 root causes out, 0 excluded.

## Verdict

**NEEDS WORK**

The d6k (Setup & Forkability) epic has one P1 blocker: the PII scrub from task i0c was reverted by a subsequent `bd sync` commit, leaving all 100 issues.jsonl records with the author's email address. This is a data regression that violates the task's acceptance criteria and poses a privacy risk for anyone forking the repo. The 3 P2 issues (rsync --delete data loss, hardcoded author paths, contradictory test checklist) are all forkability gaps that would cause real friction for adopters. The 7 P3 items are polish-level improvements to script robustness and documentation consistency. The P1 must be fixed before this epic can be considered complete.

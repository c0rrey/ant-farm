# Consolidated Review Report — Round 2

**Session**: 20260313-021748
**Timestamp**: 20260313-101452
**Consolidator**: Big Head
**Review round**: 2
**Commit range**: 8ebb3ba^..344a18d

---

## Read Confirmation

| Report | Reviewer | Findings Count | Actionable |
|--------|----------|----------------|------------|
| correctness-r2-20260313-101452.md | Correctness | 0 new findings (7/7 fix beads PASS) | 0 |
| edge-cases-r2-20260313-101452.md | Edge Cases | 4 | 4 |
| **Total** | | **4** | **4** |

All 2 expected Round 2 reports read and inventoried.

**Fix Bead Verification Summary**: All 7 fix beads from Round 1 verified PASS by Correctness reviewer. No regressions on the correctness side.

**Unaddressed R1 Findings Noted by Correctness**: F-13 (P2, missing research/ mkdir — ant-farm-m7hn) and F-14 (P1, shell operator-precedence — ant-farm-7bn5) remain open. These have existing beads filed from R1 and are not in scope for this round's fix set.

---

## Root Cause Groups

### RC-R2-1: Incomplete injection fix — printf literal substitution creates single-quote injection (P2)

**Root cause**: The fix for ant-farm-3iye replaced the heredoc-based `input.txt` write with `printf '%s\n' '<INPUT_TEXT>'`. The heredoc delimiter collision (R1 EC-05) is resolved, but `<INPUT_TEXT>` is wrapped in single quotes in the instruction prose. When an agent substitutes actual spec content containing apostrophes or single quotes, the shell command breaks with a syntax error (`unmatched '`), causing the write to fail silently. Real-world specs routinely contain contractions and possessives, making this a higher-probability failure than the original heredoc collision.

Additionally, the `jq --argjson class_score <CLASS_SCORE>` usage for manifest.json will reject non-integer values from a parsing error, leaving `manifest.json` unwritten with no error surfaced to the user.

**Affected surfaces**:
- `skills/plan.md:140` — `printf '%s\n' '<INPUT_TEXT>'` single-quote injection (Edge Cases R2-EC-01)
- `skills/plan.md:127-134` — `jq --argjson class_score` rejects non-integer silently (Edge Cases R2-EC-02)

**Merge rationale**: Both findings are in the same file, same commit (ant-farm-3iye fix), same pattern (incomplete input sanitization in the fix itself). R2-EC-01 is the higher-probability failure; R2-EC-02 is a narrower latent risk. Same root cause: the fix pass did not fully account for shell quoting semantics.

**Highest severity**: P2 (Edge Cases)

**Suggested fix**: Replace `printf '%s\n' '<INPUT_TEXT>'` with `printf '%s\n' "${INPUT_TEXT}"` (shell variable, not literal substitution). For `class_score`, use `--arg class_score "<CLASS_SCORE>"` (string type) or validate it is an integer before the `jq` call.

**Cross-session dedup**: `ant-farm-3iye` is the original bead for the R1 finding, but these are *new issues introduced by the fix*, not duplicates of the original. Mark for filing as a new bead.

---

### RC-R2-2: Inconsistent backup_and_copy error handling on non-loop call sites (P3)

**Root cause**: The `return 1` fix for ant-farm-li6e was correctly propagated to the agent loop (L113) and orchestration loop (L154) call sites with `|| { warn ...; continue; }` guards. However, three other `backup_and_copy` call sites — build-review-prompts.sh install (L177), crumb.py install (L193), and CLAUDE.md install (L210) — do NOT have guards. With `set -euo pipefail` active, a `return 1` from `backup_and_copy` at those sites causes an immediate hard abort with no diagnostic message.

**Affected surfaces**:
- `scripts/setup.sh:177` — build-review-prompts.sh install, unguarded (Edge Cases R2-EC-04)

**Highest severity**: P3 (Edge Cases)

**Suggested fix**: Add `|| warn "Failed to install: $file"` on the unguarded `backup_and_copy` calls at L177, L193, L210.

**Cross-session dedup**: `ant-farm-li6e` is the original bead. This is a *new finding introduced by the fix*. Mark for filing as new bead (P3, auto-file to Future Work).

---

### RC-R2-3: Tmpfile leak on signal kill in setup.sh find loop (P3)

**Root cause**: The fix for ant-farm-li6e replaced process substitution with a tmpfile approach for `find`. The tmpfile is correctly cleaned up in both the success and failure code paths. However, if the script is killed by a signal (SIGTERM, SIGKILL) between `mktemp` and the cleanup, the tmpfile persists in `/tmp`. This is a common limitation of the shell pattern and has minimal production impact (tmpfiles are ephemeral).

**Affected surfaces**:
- `scripts/setup.sh:140-157` — tmpfile not cleaned up on signal (Edge Cases R2-EC-03)

**Highest severity**: P3 (Edge Cases)

**Suggested fix**: Add `trap 'rm -f "$find_output"' EXIT` after `mktemp`.

**Cross-session dedup**: No existing bead matches. Mark for filing (P3, auto-file to Future Work).

---

## Severity Conflicts

No severity conflicts of 2+ levels exist between reviewers assessing the same root cause. Only Edge Cases reviewed in this round; Correctness found no new findings.

---

## Deduplication Log

### Merged findings (same root cause):

| Consolidated RC | Merged Findings | Merge Rationale |
|----------------|-----------------|-----------------|
| RC-R2-1 | R2-EC-01, R2-EC-02 | Same file, same commit, same fix pass — incomplete input sanitization in two places |

### Unmerged findings (unique root cause):

| Consolidated RC | Finding | Reason unmerged |
|----------------|---------|-----------------|
| RC-R2-2 | R2-EC-04 | Unique: inconsistent error handling propagation across call sites |
| RC-R2-3 | R2-EC-03 | Unique: tmpfile lifecycle on signal interruption |

### Cross-session duplicates (skipped):

None. All findings are new issues introduced by fixes, not duplicates of existing beads.

---

## Traceability Matrix

| Raw Finding | Source | Severity | Consolidated RC | Disposition |
|-------------|--------|----------|-----------------|-------------|
| R2-EC-01 | Edge Cases | P2 | RC-R2-1 | File as P2 |
| R2-EC-02 | Edge Cases | P2 | RC-R2-1 | File as P2 (merged) |
| R2-EC-03 | Edge Cases | P3 | RC-R2-3 | File as P3 (auto-file to Future Work) |
| R2-EC-04 | Edge Cases | P3 | RC-R2-2 | File as P3 (auto-file to Future Work) |

**Raw count**: 4 findings in -> 3 root causes out
- 1 to file as P2 (RC-R2-1)
- 2 to auto-file as P3 to Future Work (RC-R2-2, RC-R2-3)
- 0 cross-session dedup skips

---

## Priority Breakdown — Beads to File

| Priority | Count | RC IDs |
|----------|-------|--------|
| P1 | 0 | — |
| P2 | 1 | RC-R2-1 |
| P3 | 2 | RC-R2-2, RC-R2-3 |
| **Total** | **3** | |

---

## Overall Verdict

**Score**: 8/10 — PASS WITH ISSUES

All 7 fix beads from Round 1 verified PASS by the Correctness reviewer. No regressions on correctness. The Edge Cases reviewer found 1 P2 regression in the ant-farm-3iye fix (single-quote injection via `printf` literal substitution — higher probability failure than the original heredoc issue it replaced) and 2 P3 findings (inconsistent error handling propagation and tmpfile leak on signal). The P2 should be addressed before production use. The two P3s are minor polish items for the Future Work epic.

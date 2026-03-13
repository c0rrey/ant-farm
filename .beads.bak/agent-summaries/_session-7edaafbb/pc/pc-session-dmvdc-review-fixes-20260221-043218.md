# Pest Control — DMVDC (Dirt Moved vs Dirt Claimed)
# Review Fix Wave — Session 7edaafbb
# Timestamp: 20260221-043218

---

## Scope

Seven fix agents verified in this wave:

| Task | Priority | File | Commit |
|---|---|---|---|
| ant-farm-ul02 | P1 | scripts/compose-review-skeletons.sh | f5c812a |
| ant-farm-viyd | P2 | scripts/scrub-pii.sh | d7702eb |
| ant-farm-ub8a | P2 | scripts/sync-to-claude.sh | efec458 |
| ant-farm-shkt | P2 | orchestration/templates/reviews.md | 8dafdd4 |
| ant-farm-sjyg | P2 | orchestration/SETUP.md | e9cd3dd |
| ant-farm-2qmt | P2 | orchestration/templates/big-head-skeleton.md | 7813b8d |
| ant-farm-bhgt | P2 | scripts/install-hooks.sh | 6f449b8 |

Ground-truth sources: `git show <commit>`, `bd show <task-id>`, live file reads.

---

## Per-Agent Results

---

### ant-farm-ul02 (P1) — compose-review-skeletons.sh

**Commit**: f5c812a

#### Check 1: Git Diff Verification — PASS

Diff confirms exactly 1 line changed in `scripts/compose-review-skeletons.sh` at line 73:

```
-    awk '/^---$/{count++; next} count>=2{print}' "$file"
+    awk '/^---$/{count++; next} count>=1{print}' "$file"
```

Summary claims: "1 line changed (awk pattern at line 73)" — matches diff exactly.
No files changed outside the summary's "Files Changed" list.
No files listed in summary but absent from diff.

#### Check 2: Acceptance Criteria Spot-Check — PASS

`bd show ant-farm-ul02` returned:

> P1 BLOCKER: The awk change from found=1 to count>=2 in compose-review-skeletons.sh:73 requires two --- delimiters, but skeleton files only have one --- separator. Fix: revert to count>=1.

Criterion 1 (first-listed): Revert to `count>=1`. Live file at line 73 reads:
`awk '/^---$/{count++; next} count>=1{print}' "$file"` — SATISFIED.

Criterion 2: The fix description matches the bead. Summary correctly explains that skeleton files use a single `---` separator between instruction block and agent-facing body. Reading `orchestration/templates/big-head-skeleton.md` confirms the `---` pattern is singular.

#### Check 3: Approaches Substance Check — FAIL

The summary doc contains no "Approaches Considered" section. There are zero mentions of the words "approach", "option", "strategy", or "alternative" in the file. The DMVDC template requires 4+ genuinely distinct approaches to be documented and assessed. This is absent.

#### Check 4: Correctness Review Evidence — FAIL

The summary doc contains no "Correctness Review" section and no "Re-read" confirmation for any changed file. The template requires per-file correctness notes specific to actual file content (e.g., "verified that line 42 handles the None case"). None exist.

---

### ant-farm-viyd (P2) — scrub-pii.sh

**Commit**: d7702eb

#### Check 1: Git Diff Verification — PASS

Diff confirms exactly 1 line changed in `scripts/scrub-pii.sh` at line 46:

```
-PII_FIELD_PATTERN='"(owner|created_by)"\s*:\s*"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}"'
+PII_FIELD_PATTERN='"(owner|created_by)"[[:space:]]*:[[:space:]]*"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}"'
```

Summary claims the pattern fix is at line 46. Live file read at line 46 confirms the `[[:space:]]` pattern is present. Grep call sites at lines 49 and 65 reference `$PII_FIELD_PATTERN` by variable, so they inherit the fix without direct edits — consistent with summary explanation.

Summary also correctly notes the `\s` at line 63 is inside a Perl regex (`perl -i -pe`), which supports `\s` cross-platform; that line was correctly left unchanged. Verified in live file at line 63.

No files changed outside the summary's scope. No files listed in summary but absent from diff.

#### Check 2: Acceptance Criteria Spot-Check — PASS

`bd show ant-farm-viyd` returned:

> macOS BSD grep does not support \s in ERE mode. Fix: replace \s with [[:space:]] or [ \t].

Criterion 1 (first-listed): Replace `\s` with `[[:space:]]`. Live file line 46 shows `[[:space:]]` — SATISFIED.

Criterion 2 (from bead description): The fix scopes to the grep-consumed variable only (not the perl line). Summary correctly explains this distinction and the live file confirms the perl line at 63 is unchanged.

#### Check 3: Approaches Substance Check — FAIL

The summary doc contains no "Approaches Considered" section. Zero mentions of "approach", "option", "strategy", or "alternative". The DMVDC template requires 4+ documented approaches.

#### Check 4: Correctness Review Evidence — FAIL

The summary doc contains no "Correctness Review" section and no "Re-read" confirmation. No file-specific correctness notes exist.

---

### ant-farm-ub8a (P2) — sync-to-claude.sh

**Commit**: efec458

#### Check 1: Git Diff Verification — PASS

Diff confirms exactly 1 line changed in `scripts/sync-to-claude.sh` at line 27:

```
-rsync -av --exclude='scripts/' "$REPO_ROOT/orchestration/" ~/.claude/orchestration/
+rsync -av --exclude='scripts/' --exclude='_archive/' "$REPO_ROOT/orchestration/" ~/.claude/orchestration/
```

Summary claims: "added `--exclude='_archive/'` to rsync command" in `scripts/sync-to-claude.sh` — matches diff exactly.
Live file at line 27 confirms the `--exclude='_archive/'` flag is present.

Note: Summary uses the absolute path `/Users/correy/projects/ant-farm/scripts/sync-to-claude.sh` instead of the repo-relative path, which is cosmetically inconsistent but not a correctness error.

#### Check 2: Acceptance Criteria Spot-Check — PASS

`bd show ant-farm-ub8a` returned:

> Fix: add --exclude='_archive/' to the rsync command.

Criterion 1 (first-listed): Add `--exclude='_archive/'`. Live file at line 27 confirms — SATISFIED.

Criterion 2: The description notes stale files must be manually removed once. This is correctly documented in the summary's "Outcome" section. The fix correctly prevents new syncs from re-creating the archive; it does not retroactively delete existing stale files, consistent with bead intent.

#### Check 3: Approaches Substance Check — FAIL

The summary doc contains no "Approaches Considered" section. Zero mentions of "approach", "option", "strategy", or "alternative".

#### Check 4: Correctness Review Evidence — FAIL

The summary doc contains no "Correctness Review" section and no "Re-read" confirmation.

---

### ant-farm-shkt (P2) — reviews.md

**Commit**: 8dafdd4

#### Check 1: Git Diff Verification — PASS

Diff confirms 9 lines inserted into `orchestration/templates/reviews.md` immediately after line 502 (`REVIEW_ROUND={{REVIEW_ROUND}}`):

```bash
case "$REVIEW_ROUND" in
  *'{'*|*'}'*)
    echo "PLACEHOLDER ERROR: REVIEW_ROUND was not substituted by fill-review-slots.sh (got: $REVIEW_ROUND)"
    echo "This brief was delivered with an unresolved {{REVIEW_ROUND}} placeholder."
    echo "Root cause: fill-review-slots.sh was bypassed or failed during prompt composition."
    echo "Do NOT proceed. Return this error to the Queen immediately."
    exit 1
    ;;
esac
```

Summary claims: "9 lines inserted after line 502" — matches diff exactly.
Live file at lines 503-511 confirms the `case` guard is present.

No files changed outside the summary's scope.

#### Check 2: Acceptance Criteria Spot-Check — PASS

`bd show ant-farm-shkt` returned:

> Fix: add a guard check after the assignment.

Criterion 1 (first-listed): Guard check after `REVIEW_ROUND=` assignment. Live file at lines 503-511 shows the `case` guard immediately follows the assignment — SATISFIED.

Criterion 2: Guard must produce a clear diagnostic error (not a confusing arithmetic error). Live file shows the echo messages are explicit: "PLACEHOLDER ERROR: REVIEW_ROUND was not substituted" with root cause and remediation — SATISFIED.

#### Check 3: Approaches Substance Check — FAIL

The summary doc contains no "Approaches Considered" section. Zero mentions of "approach", "option", "strategy", or "alternative".

#### Check 4: Correctness Review Evidence — FAIL

The summary doc contains no "Correctness Review" section and no "Re-read" confirmation.

---

### ant-farm-sjyg (P2) — SETUP.md

**Commit**: e9cd3dd

#### Check 1: Git Diff Verification — PASS

Diff confirms exactly 1 line changed in `orchestration/SETUP.md` at line 211:

```
-1. Gather all task metadata (bd show <id>)
+1. Spawn the Scout subagent to gather all task metadata (do NOT run bd show directly as Queen)
```

Summary claims: "line 211 only" — matches diff exactly.
Live file at line 211 confirms the reworded instruction.

#### Check 2: Acceptance Criteria Spot-Check — PASS

`bd show ant-farm-sjyg` returned:

> Fix: reword to instruct spawning the Scout instead.

Criterion 1 (first-listed): Reword line 211 to delegate to Scout. Live file reads "Spawn the Scout subagent to gather all task metadata (do NOT run bd show directly as Queen)" — SATISFIED.

Criterion 2: The fix must not contradict RULES.md / CLAUDE.md Scout-delegation discipline. The new text explicitly names Scout and adds the prohibition — consistent with the discipline.

#### Check 3: Approaches Substance Check — FAIL

The summary doc contains no "Approaches Considered" section. Zero mentions of "approach", "option", "strategy", or "alternative".

#### Check 4: Correctness Review Evidence — FAIL

The summary doc contains no "Correctness Review" section and no "Re-read" confirmation.

---

### ant-farm-2qmt (P2) — big-head-skeleton.md

**Commit**: 7813b8d

#### Check 1: Git Diff Verification — PASS

Diff confirms exactly 1 line changed in `orchestration/templates/big-head-skeleton.md` at line 91:

```
-   - **On timeout (TIMED_OUT=1)**: Before returning the error to the Queen, write a failure artifact
+   - **On timeout (REPORTS_FOUND=0)**: Before returning the error to the Queen, write a failure artifact
```

Summary claims: "Line 91 — Before: `TIMED_OUT=1`, After: `REPORTS_FOUND=0`" — matches diff exactly.
Live file at line 91 confirms `REPORTS_FOUND=0`.

Summary correctly notes scope: "Only `orchestration/templates/big-head-skeleton.md` was modified." The diff confirms no other files changed.

#### Check 2: Acceptance Criteria Spot-Check — PASS

`bd show ant-farm-2qmt` returned:

> big-head-skeleton.md:91 references TIMED_OUT variable but reviews.md commit 306a457 renamed it to REPORTS_FOUND. Fix: update to REPORTS_FOUND.

Criterion 1 (first-listed): Update line 91 to `REPORTS_FOUND`. Live file at line 91 reads `REPORTS_FOUND=0` — SATISFIED.

Criterion 2: The rename traceability. Summary correctly attributes the source rename to commit 306a457 (ant-farm-j6jq), which is the commit referenced in the bead description. This is consistent.

#### Check 3: Approaches Substance Check — FAIL

The summary doc contains no "Approaches Considered" section. Zero mentions of "approach", "option", "strategy", or "alternative".

#### Check 4: Correctness Review Evidence — FAIL

The summary doc contains no "Correctness Review" section and no "Re-read" confirmation.

---

### ant-farm-bhgt (P2) — install-hooks.sh

**Commit**: 6f449b8

#### Check 1: Git Diff Verification — PASS

Diff confirms changes to `scripts/install-hooks.sh`: 8 insertions, 6 deletions (net +2) inside the pre-commit hook heredoc:

Before (inside heredoc):
```bash
if [[ ! -x "$SCRUB_SCRIPT" ]]; then
    echo "[ant-farm] ERROR: scrub-pii.sh not found or not executable — cannot scrub PII. Commit blocked." >&2
    exit 1
fi
"$SCRUB_SCRIPT"
git add "$ISSUES_FILE"
echo "[ant-farm] PII scrub applied and re-staged: .beads/issues.jsonl"
```

After (inside heredoc):
```bash
if [[ ! -x "$SCRUB_SCRIPT" ]]; then
    echo "[ant-farm] WARNING: scrub-pii.sh not found or not executable — PII scrub skipped." >&2
    echo "[ant-farm]   Risk:  email addresses in .beads/issues.jsonl may enter git history." >&2
    echo "[ant-farm]   Fix:   add scripts/scrub-pii.sh and re-run scripts/install-hooks.sh." >&2
else
    "$SCRUB_SCRIPT"
    git add "$ISSUES_FILE"
    echo "[ant-farm] PII scrub applied and re-staged: .beads/issues.jsonl"
fi
```

Summary claims: "8 insertions, 6 deletions (net +2 lines inside heredoc)" — matches diff exactly.
Live file at lines 87-97 confirms the warning-based structure with `else` branch.

Note: Summary claims the fix converts an unconditional `exit 1` to a warning, which is correct. The `$SCRUB_SCRIPT` call is now inside the `else` branch, preserving normal operation when the script exists.

#### Check 2: Acceptance Criteria Spot-Check — PASS

`bd show ant-farm-bhgt` returned:

> Fix: check for scrub-pii.sh existence before installing the pre-commit hook, or make the hook tolerate a missing script.

Criterion 1 (first-listed): Make the hook tolerate a missing script. Live file at lines 87-97 shows the `if/else` structure that continues (via `else`) rather than blocking with `exit 1` — SATISFIED.

Criterion 2: Behavior when script is present must be preserved. The `else` branch still calls `$SCRUB_SCRIPT`, re-stages, and echoes confirmation — behavior unchanged for the normal path.

#### Check 3: Approaches Substance Check — FAIL

The summary doc contains no "Approaches Considered" section. Zero mentions of "approach", "option", "strategy", or "alternative".

#### Check 4: Correctness Review Evidence — FAIL

The summary doc contains no "Correctness Review" section and no "Re-read" confirmation.

---

## Structural Finding: Missing Summary Sections (All 7 Agents)

All 7 summary docs are missing the two sections required by the DMVDC template:

1. **Section 3 (Approaches Considered)**: None of the 7 summaries document 4+ distinct approaches to the fix. The DMVDC Check 3 requires genuinely distinct strategies, not cosmetic variations.

2. **Section 4 (Correctness Review / Re-read)**: None of the 7 summaries contain per-file correctness notes or "Re-read: yes" confirmations. DMVDC Check 4 requires specific, file-anchored notes.

These sections are absent, not weak — there is literally zero content for Checks 3 and 4 to evaluate across all 7 agents.

**Mitigating context**: All 7 fixes are single-line or minimal-line changes (1 line changed in 5 cases; 9 lines inserted in 1 case; 8 insertions/6 deletions in 1 case). The actual code changes are correct and match the bead descriptions exactly. The risk of a 1-line awk change being substantively wrong is low when the diff is fully visible and verifiable. Nonetheless, the template requires these sections and they are absent.

---

## Verdict Table

| Task | Check 1 (Git Diff) | Check 2 (Criteria) | Check 3 (Approaches) | Check 4 (Correctness) | Verdict |
|---|---|---|---|---|---|
| ant-farm-ul02 | PASS | PASS | FAIL | FAIL | PARTIAL |
| ant-farm-viyd | PASS | PASS | FAIL | FAIL | PARTIAL |
| ant-farm-ub8a | PASS | PASS | FAIL | FAIL | PARTIAL |
| ant-farm-shkt | PASS | PASS | FAIL | FAIL | PARTIAL |
| ant-farm-sjyg | PASS | PASS | FAIL | FAIL | PARTIAL |
| ant-farm-2qmt | PASS | PASS | FAIL | FAIL | PARTIAL |
| ant-farm-bhgt | PASS | PASS | FAIL | FAIL | PARTIAL |

**Session-wide verdict: PARTIAL**

All 7 agents: Checks 1 and 2 PASS. Checks 3 and 4 FAIL uniformly due to absent summary sections.

---

## Recommendation to Queen

Checks 1 and 2 PASS across all 7 agents: the actual code changes are correct, minimal, and match bead descriptions exactly. No fabrication, no scope creep.

Checks 3 and 4 FAIL because all 7 summary docs omit the "Approaches Considered" and "Correctness Review" sections required by the DMVDC template.

**Options**:

1. **Accept as-is with documentation**: For single-line fixes verified by visual diff, the absence of approaches/correctness sections is a documentation gap, not a correctness risk. Document the gap in the session CHANGELOG and close.

2. **Resume agents for summary updates**: Resume each agent with the specific DMVDC failures and request updated summaries. Then re-run DMVDC. Low substance risk given the simplicity of each fix, but adds session overhead.

The Queen decides; DMVDC reports PARTIAL as required by the checkpoint spec.

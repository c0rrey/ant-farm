# Correctness Review Report

**Reviewer**: Correctness Nitpicker
**Review round**: 1
**Commit range**: 7569c5e^..c78875b
**Timestamp**: 20260222-101920

---

## Findings Catalog

### F-001
- **File**: `orchestration/RULES.md`
- **Line**: 261 (WWD "When" description in checkpoints.md also at line 263–265)
- **Severity**: P3
- **Category**: Cross-file consistency
- **Description**: The WWD section in `checkpoints.md` (lines 263–265) now describes two execution modes (serial and batch), and `RULES.md` Step 3 (lines 121–131) documents the same two modes with a deterministic mode selection rule. However, `checkpoints.md` does not include the **mode selection rule** itself ("If you spawned agents in a single message, use batch mode; if individually in separate messages, use serial mode"). `RULES.md` has the rule at line 129–130; `checkpoints.md` does not. Pest Control reads `checkpoints.md` at runtime; the Queen reads `RULES.md`. A Pest Control agent executing WWD would read the two mode descriptions but would have no instruction for determining which mode applies when. This creates an ambiguity gap for the runtime executor.
- **Suggested fix**: Add the mode selection rule to `checkpoints.md`'s WWD section, after the Batch mode bullet, mirroring `RULES.md` Step 3's language: "**Mode selection rule**: Use batch mode when agents were spawned in a single message (parallel wave). Use serial mode when agents were spawned one at a time in separate messages."

### F-002
- **File**: `orchestration/RULES.md`
- **Line**: 273 (Hard Gates table, WWD row)
- **Severity**: P3
- **Category**: Data integrity / cross-file consistency
- **Description**: The Hard Gates table WWD row was updated to: "Serial mode: next agent spawn; Batch mode: DMVDC spawn (all wave agents checked before DMVDC)". This correctly distinguishes the two blocking behaviors. The corresponding `README.md` Hard Gates table (line 267–273) still reads "Next agent in wave" for WWD — unchanged from before the fix commits. The README describes what each gate blocks and a reader who uses the README as an entry point will see stale semantics for the WWD gate.
- **Suggested fix**: Update `README.md` Hard Gates table WWD row to match `RULES.md` language, e.g. "Serial mode: next agent spawn; Batch mode: DMVDC spawn".

### F-003
- **File**: `orchestration/templates/checkpoints.md`
- **Line**: 15–17 (Pest Control Overview, "Role distinction" paragraph)
- **Severity**: P3
- **Category**: Correctness / cross-file consistency
- **Description**: The updated "Role distinction" paragraph correctly removes the two-layer spawn language and now reads "Pest Control executes all checkpoint logic directly — it does not spawn subagents. Pest Control has tools: Bash, Read, Write, Glob, Grep (no Task tool)." The GLOSSARY.md Ant Metaphor Roles table (line 82) describes Pest Control without mentioning the absence of the Task tool. This is not an error — the GLOSSARY is a role description, not a tool manifest. However, the `agents/pest-control.md` file was not part of the changed files list, so it was not reviewed here. If the underlying fix relied solely on documentation (removing the spawn language from checkpoints.md) without adding the Task tool to pest-control.md, then the fix is correct (Option A). This is confirmed: the commit message says "Remove two-layer spawn architecture references — Pest Control executes all checkpoint logic directly." No new capability gap is introduced.
- **Suggested fix**: No action needed — Option A (align docs to reality) was implemented correctly.

### F-004
- **File**: `scripts/parse-progress-log.sh`
- **Line**: 62–72 (`STEP_KEYS` array)
- **Severity**: P2
- **Category**: Acceptance criteria failure (ant-farm-zuae criterion 4)
- **Description**: `RULES.md:131` (added by the ant-farm-zuae fix) instructs the Queen to log `WAVE_WWD_PASS` as a progress milestone. Acceptance criterion 4 for ant-farm-zuae states: "Progress log includes a WWD milestone entry (detectable in crash recovery)." The `WAVE_WWD_PASS` key is absent from the `STEP_KEYS` array in `scripts/parse-progress-log.sh` (lines 62–72). The script's `while read` loop (line 165) will parse a `WAVE_WWD_PASS` line and store it in the map, but the key never appears in `STEP_KEYS`, so it is never consulted when determining the resume point or rendering the Step Status table. A session that crashes after logging `WAVE_WWD_PASS` but before logging `WAVE_VERIFIED` will be told to resume at `WAVE_VERIFIED` — which means WWD will be re-run unnecessarily. More critically, the milestone is logged but invisible to the crash recovery system, directly contradicting "detectable in crash recovery." This is not merely a documentation gap: the acceptance criterion explicitly required crash recovery detectability and the fix did not deliver it. The script `parse-progress-log.sh` was not in the scoped changed-files list, but the criterion's correctness depends on it. Flagging as P2 because incorrect resume behavior (re-running WWD when it already passed) wastes resources and could cause spurious failures if the WWD artifacts are in a state that confuses Pest Control on re-run.
- **Suggested fix**: Add `WAVE_WWD_PASS` to the `STEP_KEYS` array in `scripts/parse-progress-log.sh` between `WAVE_SPAWNED` and `WAVE_VERIFIED`. Add corresponding entries to `step_label()` and `step_resume_action()`: label "Wave WWD Pass: WWD verification completed for wave"; resume action "Re-run WAVE_WWD_PASS: check existing WWD artifacts in pc/ and re-run any that are missing or FAIL." Note: `WAVE_WWD_PASS` is a multi-occurrence step (one per wave), same as `WAVE_SPAWNED` and `WAVE_VERIFIED` — the existing multi-occurrence handling already supports this.

---

## Acceptance Criteria Verification

### ant-farm-x8iw: Scout/Pantry model reference fix

Criteria from `bd show`:
1. **agents/scout-organizer.md frontmatter says `model: opus`** — CONFIRMED. Line 5 of `agents/scout-organizer.md` now reads `model: opus` (verified via git show 7569c5e).
2. **orchestration/GLOSSARY.md Scout row says `opus`** — CONFIRMED. Line 80 now reads `opus` for Scout.
3. **orchestration/GLOSSARY.md Pantry row says `opus`** — CONFIRMED. Line 81 now reads `opus` for Pantry.
4. **README.md Scout description says "opus" not "sonnet"** — CONFIRMED. Line 75 reads "an opus subagent".
5. **No other files reference Scout or Pantry as sonnet-tier agents (grep verification)** — CONFIRMED. grep of changed files finds no remaining Scout/Pantry sonnet references.

All 5 acceptance criteria: MET.

### ant-farm-h94m: Pest Control architecture fix

Criteria from `bd show`:
1. **checkpoints.md spawn architecture matches pest-control.md tool permissions** — CONFIRMED. checkpoints.md Pest Control Overview now says "Pest Control executes all checkpoint logic directly — it does not spawn subagents. Pest Control has tools: Bash, Read, Write, Glob, Grep (no Task tool)."
2. **No reference to "spawns a code-reviewer" if PC lacks Task tool** — CONFIRMED. All 7 "Agent type (spawned by Pest Control): code-reviewer" lines removed.
3. **If code-reviewer is retained, it exists in repo agents/ directory (not just ~/.claude/)** — Option A was chosen (remove spawn language rather than add Task tool), so this criterion is N/A. No code-reviewer dependency added.
4. **RULES.md Agent Types table reflects any agent changes** — No agent changes were made (Option A), so the Agent Types table needs no change. CONFIRMED.

All 4 acceptance criteria: MET.

### ant-farm-wg2i: Pre-push hook and CONTRIBUTING.md fix

Criteria from `bd show`:
1. **Installed .git/hooks/pre-push matches output of install-hooks.sh (non-fatal sync)** — CONFIRMED. The installed hook wraps sync in `if ! "$SYNC_SCRIPT"; then ... echo WARNING ... fi` and exits 0 on sync failure. The fatal `set -euo pipefail` is still present at the script level, but the sync call is now inside a conditional that catches the failure, making sync non-fatal.
2. **CONTRIBUTING.md rsync description matches actual sync-to-claude.sh behavior (no --delete, excludes _archive/)** — CONFIRMED. Line 161 now reads "via rsync without `--delete`, excluding `scripts/` and `_archive/`".
3. **CONTRIBUTING.md includes guidance on re-running install-hooks.sh after pulling changes** — CONFIRMED. New paragraph added at line 180.
4. **Push succeeds even when sync-to-claude.sh fails (manual test)** — Not verifiable by static review. The code path is correct; a runtime test would confirm. Flagging as outside review scope.

Criteria 1–3: MET. Criterion 4 is a runtime validation.

### ant-farm-zuae: WWD batch vs serial documentation fix

Criteria from `bd show`:
1. **RULES.md Step 3 accurately describes when WWD runs in batch vs serial mode** — CONFIRMED. Step 3 (lines 121–131) now defines serial mode, batch mode, and a deterministic mode selection rule.
2. **Hard Gates table clarifies blocking semantics for parallel waves** — CONFIRMED. Line 273 now reads "Serial mode: next agent spawn; Batch mode: DMVDC spawn (all wave agents checked before DMVDC)".
3. **checkpoints.md WWD "When" field matches RULES.md description** — PARTIALLY MET. checkpoints.md lines 263–265 now distinguish serial vs batch modes. However, the mode selection rule (how to choose between them) is present only in RULES.md, not in checkpoints.md. Since Pest Control reads checkpoints.md directly at runtime, the mode selection rule gap creates an ambiguity (see F-001).
4. **Progress log includes a WWD milestone entry (detectable in crash recovery)** — NOT MET. RULES.md line 131 adds `WAVE_WWD_PASS` to the progress log instructions, but `scripts/parse-progress-log.sh` does not include `WAVE_WWD_PASS` in its `STEP_KEYS` array (lines 62–72). The milestone is logged but ignored by crash recovery. See F-004.
5. **Next production session with parallel agents produces WWD artifacts (verified post-fix)** — Runtime validation; outside static review scope.

Criteria 1, 2: MET. Criterion 3: PARTIAL (see F-001). Criterion 4: NOT MET (see F-004). Criterion 5: runtime only.

---

## Preliminary Groupings

### Group A: Cross-file consistency gaps introduced by the WWD fix (F-001, F-002)

Root cause: The WWD documentation fix (ant-farm-zuae) correctly updated RULES.md but did not propagate all new information to the downstream consumers. Pest Control reads checkpoints.md for WWD guidance; the mode selection rule was not added there (F-001). README.md's Hard Gates table was not updated to match RULES.md's new WWD blocking semantics (F-002).

Both findings are P3 — they create reader confusion and potential executor ambiguity but do not produce incorrect output given that RULES.md (the Queen-facing document) is complete and correct.

### Group B: Incomplete acceptance criterion delivery for ant-farm-zuae (F-004)

Root cause: The ant-farm-zuae fix added the `WAVE_WWD_PASS` log instruction to RULES.md but did not update `scripts/parse-progress-log.sh` to recognize the new key. Criterion 4 explicitly required "detectable in crash recovery" — the fix only delivered the first half (the log instruction) and omitted the second half (making crash recovery aware of the key). This is a P2 acceptance criteria failure: incorrect resume behavior on a WWD-post-crash scenario.

### Group C: Architecture fix completeness (F-003)

Root cause: ant-farm-h94m chose Option A (align docs to reality, not add the Task tool). This is the correct and complete fix — no capability gap was introduced. This group contains no actionable finding. Noted for coverage completeness.

---

## Summary Statistics

| Severity | Count |
|----------|-------|
| P1 | 0 |
| P2 | 1 (F-004) |
| P3 | 2 (F-001, F-002) |
| **Total** | **3** |

F-003 was evaluated and found to require no action.

---

## Cross-Review Messages

**Sent**: None — F-004 is a correctness/acceptance criteria failure; keeping it here rather than delegating.

**Received**: Message from edge-cases-reviewer — "Logic gap at `scripts/parse-progress-log.sh:62-72` — the `WAVE_WWD_PASS` milestone added in `orchestration/RULES.md:131` is not in `STEP_KEYS`. A session that crashes after logging `WAVE_WWD_PASS` but before `WAVE_VERIFIED` would be told to resume at WAVE_VERIFIED and re-run WWD unnecessarily. May want to check whether parse-progress-log.sh correctly reflects the post-diff milestone sequence — this could be an acceptance criteria concern for task ant-farm-zuae."

**Action taken**: Verified the gap in `parse-progress-log.sh:62-72`. Confirmed the acceptance criterion 4 for ant-farm-zuae is NOT MET. Added F-004 (P2) to this report. The finding is a correctness/acceptance-criteria failure; edge-cases-reviewer flagged the boundary gap, but the root issue is an unmet criterion — correctly owned by this reviewer.

---

## Coverage Log

| File | Status | Notes |
|------|--------|-------|
| `agents/scout-organizer.md` | Reviewed — no correctness issues | Model field changed from `sonnet` to `opus`. Matches RULES.md Model Assignments table. |
| `CONTRIBUTING.md` | Reviewed — no correctness issues | rsync --delete claim fixed. Re-run reminder added. Both match actual install-hooks.sh behavior. |
| `orchestration/GLOSSARY.md` | Reviewed — no correctness issues | Scout and Pantry model rows updated from `sonnet` to `opus`. All other rows unchanged and consistent. |
| `orchestration/RULES.md` | Reviewed — P3 issue found (F-002 partial context; F-001 is in checkpoints.md but originates from this fix) | WWD Step 3 and Hard Gates table updated. Mode selection rule is present here. README Hard Gates table gap noted at F-002. |
| `orchestration/templates/checkpoints.md` | Reviewed — P3 issue found (F-001) | code-reviewer spawn language removed. WWD "When" updated for serial/batch. Mode selection rule missing from checkpoints.md. |
| `README.md` | Reviewed — P3 issue found (F-002) | Scout model fixed. Hard Gates table WWD row not updated. |
| `scripts/parse-progress-log.sh` | Reviewed — P2 issue found (F-004) | Not in original scoped file list, but reviewed after edge-cases-reviewer tip. `WAVE_WWD_PASS` absent from `STEP_KEYS` array (lines 62–72). Acceptance criterion 4 for ant-farm-zuae is not met. |

---

## Overall Assessment

**Score**: 6/10

**Verdict**: NEEDS WORK

**Rationale**: Three of four tasks are fully correct. The ant-farm-zuae fix has one unmet acceptance criterion: "Progress log includes a WWD milestone entry (detectable in crash recovery)" (criterion 4). The `WAVE_WWD_PASS` key was added to RULES.md's log instructions but not to `scripts/parse-progress-log.sh`'s `STEP_KEYS` array — making it logged but invisible to the crash recovery system. This is a P2 finding (F-004): a WWD-post-crash session will resume at the wrong point and re-run WWD unnecessarily. The two P3 findings (F-001, F-002) represent incomplete propagation of the WWD serial/batch change to `checkpoints.md` and `README.md`. No P1 issues found. Fix required: add `WAVE_WWD_PASS` to `parse-progress-log.sh` STEP_KEYS with appropriate label and resume action.

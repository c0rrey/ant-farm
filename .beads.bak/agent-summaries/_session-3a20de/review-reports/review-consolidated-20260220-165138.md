# Consolidated Review Summary

**Scope**: docs/plans/2026-02-19-meta-orchestration-plan.md, orchestration/RULES.md, orchestration/templates/checkpoints.md, orchestration/templates/pantry.md, orchestration/templates/reviews.md, scripts/parse-progress-log.sh
**Reviews completed**: Round 1 -- Clarity, Edge Cases, Correctness, Excellence
**Total raw findings**: 28 across all reviews
**Root causes identified**: 9 after dedup
**Beads filed**: 9 (ant-farm-35wk, ant-farm-purh, ant-farm-yf5p, ant-farm-dxw2, ant-farm-nq4f, ant-farm-npfx, ant-farm-164n, ant-farm-e1u6, ant-farm-kzz6)

---

## Read Confirmation

**Reports read and processed by Big Head consolidation:**

Round 1: 4 reports (clarity, edge-cases, correctness, excellence)

| Report Type | File | Status | Finding Count |
|-------------|------|--------|---------------|
| Clarity | clarity-review-20260220-165138.md | Read | 7 findings |
| Edge Cases | edge-cases-review-20260220-165138.md | Read | 6 findings |
| Correctness | correctness-review-20260220-165138.md | Read | 7 findings |
| Excellence | excellence-review-20260220-165138.md | Read | 8 findings |

**Total findings from all reports**: 28

---

## Root Causes Filed

| RC | Bead ID | Priority | Title | Contributing Reviews | Surfaces | Raw Findings Merged |
|----|---------|----------|-------|---------------------|----------|---------------------|
| RC-1 | ant-farm-35wk | P1 | parse-progress-log.sh bash/zsh incompatibility breaks crash recovery | Edge Cases, Correctness, Excellence | scripts/parse-progress-log.sh | EC-1, EC-2, CR-7, EX-3 |
| RC-2 | ant-farm-purh | P2 | Progress log step3b embeds non-existent `big-head-summary.md` filename | Clarity, Edge Cases, Correctness | orchestration/RULES.md:186 | CL-1, EC-3, CR-2 |
| RC-3 | ant-farm-yf5p | P2 | TIMESTAMP variable undefined in Step 3b-v dummy reviewer | Clarity, Edge Cases, Excellence | orchestration/RULES.md:176 | CL-2, EC-4b, EX-6 |
| RC-4 | ant-farm-dxw2 | P2 | SSV PASS retains human approval gate vs ant-farm-s0ak criterion 3 | Correctness | orchestration/RULES.md:94, orchestration/templates/checkpoints.md:698 | CR-1 |
| RC-5 | ant-farm-nq4f | P2 | Progress log milestone naming diverges from ant-farm-0b4k spec | Correctness | orchestration/RULES.md (multiple lines) | CR-3, CR-4 |
| RC-6 | ant-farm-npfx | P3 | parse-progress-log.sh hardening gaps (overwrite, dead branch, corruption) | Excellence | scripts/parse-progress-log.sh | EX-2, EX-4, EX-8 |
| RC-7 | ant-farm-164n | P3 | Dual placeholder conventions for round-conditional blocks | Excellence | orchestration/templates/pantry.md, orchestration/templates/reviews.md | EX-1, EX-5 |
| RC-8 | ant-farm-e1u6 | P3 | No tmux guard for dummy reviewer spawn | Edge Cases | orchestration/RULES.md:168-177 | EC-4 |
| RC-9 | ant-farm-kzz6 | P3 | Documentation polish: terminology, wording, and examples | Clarity, Correctness, Edge Cases, Excellence | Multiple files | CL-3, CL-4, CL-5, CL-6, CL-7, CR-5, CR-6, EC-5, EX-7 |

---

## Root Cause Details

### RC-1 [P1]: parse-progress-log.sh bash/zsh incompatibility breaks crash recovery

**Root cause**: `scripts/parse-progress-log.sh` uses `declare -A` (bash 4+ associative arrays) but ships with `#!/usr/bin/env bash`. On macOS, the system bash is 3.2 (no associative array support) and the default shell is zsh (different associative array semantics). The script's core crash recovery function is completely broken on the primary target platform.

**Affected surfaces**:
- `scripts/parse-progress-log.sh:25,113-115` -- `declare -A` fails on bash 3.2, exits with code 2 (from Edge Cases Finding 1)
- `scripts/parse-progress-log.sh:113-115,130-133` -- Under zsh, `declare -A` runs but lookups via `${arr[key]+set}` always return empty, causing all step detection to fail silently (from Edge Cases Finding 2)
- `scripts/parse-progress-log.sh:113-115,25` -- Verified on this machine: bash 3.2.57, `declare -A` exits code 2, blocking ant-farm-b219 criteria 1 and 2 in production (from Correctness Finding 7)
- `scripts/parse-progress-log.sh:130,179` -- The `${var+set}` pattern is fragile under older bash versions with `set -u` (from Excellence Finding 3)

**Merge rationale**: All four findings trace to the identical root cause: associative array syntax that requires bash 4+ in a script that runs on macOS where bash 3.2 and zsh are the available shells. EC-1 and EC-2 are the two platform-specific failure modes; CR-7 is independent verification with acceptance criteria impact analysis; EX-3 is the underlying code pattern concern. Same data structure (`declare -A STEP_COMPLETED`), same file, same incompatibility.

**Fix**: Add a bash version guard at the top of the script (before `set -euo pipefail`):
```bash
if [ "${BASH_VERSINFO[0]}" -lt 4 ]; then
    echo "ERROR: parse-progress-log.sh requires bash 4+. System has bash ${BASH_VERSINFO[0]}." >&2
    echo "       Install bash 4+ via homebrew: brew install bash" >&2
    exit 1
fi
```
Or rewrite step detection using POSIX-compatible parallel arrays/grep-based lookup to eliminate the bash 4+ dependency entirely.

**Acceptance criteria**:
- Script exits with a clear error on bash < 4 (not exit code 2)
- OR script works correctly on bash 3.2 and zsh without associative arrays
- All step detection, completion check, and resume point determination produce correct results on macOS

---

### RC-2 [P2]: Progress log step3b embeds non-existent `big-head-summary.md` filename

**Root cause**: RULES.md line 186 hardcodes `big-head-summary.md` as the consolidated report filename in the step3b progress log entry, but the actual filename is `review-consolidated-{timestamp}.md` (documented in reviews.md:138,632,801 and pantry.md:464).

**Affected surfaces**:
- `orchestration/RULES.md:186` -- The echo command: `report=${SESSION_DIR}/review-reports/big-head-summary.md` (from Clarity Finding 1, Edge Cases Finding 3, Correctness Finding 2)

**Merge rationale**: All three findings cite the exact same line (RULES.md:186) and the exact same filename mismatch. Clarity frames it as a misleading instruction, Edge Cases as a future runtime risk, Correctness as a recovery failure scenario. One line, one wrong filename, one fix.

**Fix**: Change `big-head-summary.md` to `review-consolidated-${TIMESTAMP}.md` in the step3b progress log echo on RULES.md:186.

**Acceptance criteria**:
- The step3b progress log entry references the correct consolidated report filename
- The filename matches the pattern used by Big Head in reviews.md

---

### RC-3 [P2]: TIMESTAMP variable undefined in Step 3b-v dummy reviewer

**Root cause**: RULES.md Step 3b-v (line 176) uses `${TIMESTAMP}` in a `tmux send-keys` command, but no prior instruction in Step 3b assigns this value to a variable named `TIMESTAMP`. Step 3b-i describes generating a timestamp but does not define the variable name.

**Affected surfaces**:
- `orchestration/RULES.md:176` -- `tmux send-keys ... dummy-review-${TIMESTAMP}.md` (from Clarity Finding 2, Edge Cases Finding 4b, Excellence Finding 6)

**Merge rationale**: All three findings cite the same line (RULES.md:176) and identify the same gap: `${TIMESTAMP}` is referenced but never formally bound. CL-2 frames it as ambiguity for human readers; EC-4b frames it as an edge case (unset variable in shell expansion producing malformed filename `dummy-review-.md`); EX-6 frames it as a runtime risk of empty expansion. Same variable, same line, same missing definition.

**Fix**: Add explicit variable assignment in Step 3b-i: `TIMESTAMP=$(date +%Y%m%d-%H%M%S)` and add a cross-reference note in Step 3b-v: "Uses the TIMESTAMP variable from Step 3b-i."

**Acceptance criteria**:
- Step 3b-i explicitly assigns the timestamp to a named variable
- Step 3b-v's `${TIMESTAMP}` reference resolves to the correct value

---

### RC-4 [P2]: SSV PASS retains human approval gate vs ant-farm-s0ak criterion 3

**Root cause**: ant-farm-s0ak acceptance criterion 3 states "PASS allows workflow to continue without human approval." The implementation in RULES.md:94 and checkpoints.md:698 explicitly preserves user approval after SSV PASS. A deliberate fix commit (3510d66) re-introduced user approval to align with RULES.md's design, leaving the bead's criterion unmet.

**Affected surfaces**:
- `orchestration/RULES.md:94` -- "On SSV PASS: Present the recommended strategy to the user for approval." (from Correctness Finding 1)
- `orchestration/templates/checkpoints.md:698` -- "On PASS: Present the recommended strategy to the user for approval" (from Correctness Finding 1)

**Merge rationale**: Standalone finding from one reviewer. The tension is between the bead specification and the implementation's design choice.

**Fix**: Either (a) update ant-farm-s0ak criterion 3 to reflect the retained approval gate (if the design decision is intentional), or (b) remove the user approval gate to match the original criterion.

**Acceptance criteria**:
- The bead specification and the implementation agree on whether SSV PASS requires human approval
- If approval is retained, the bead documents the design rationale

---

### RC-5 [P2]: Progress log milestone naming diverges from ant-farm-0b4k spec

**Root cause**: The progress log implementation uses step-numbered keys (step0, step1, ..., step6) with per-wave granularity, while ant-farm-0b4k specifies event-named milestones (SCOUT_COMPLETE, DIRT_PUSHER_COMPLETE per agent, SESSION_CLOSE_STARTED, etc.) with per-agent granularity.

**Affected surfaces**:
- `orchestration/RULES.md:59,98,115,123,186,207,210,213,216` -- All progress log echo commands use step-numbered keys (from Correctness Finding 3)
- `scripts/parse-progress-log.sh:130` -- Checks for `step6` instead of `SESSION_CLOSE_STARTED` (from Correctness Finding 4)

**Merge rationale**: CR-4 is a specific instance of the broader CR-3 design divergence. Both findings address the same gap: the implementation chose a simpler naming scheme than the bead specifies. The per-agent vs per-wave granularity affects recovery precision.

**Fix**: Either (a) add per-dirt-pusher log entries and rename milestone keys to match the bead spec, or (b) update ant-farm-0b4k to reflect the implemented design (step-numbered, per-wave).

**Acceptance criteria**:
- Progress log milestone names match the authoritative specification (bead or updated bead)
- Per-agent recovery granularity is either implemented or explicitly descoped in the bead

---

### RC-6 [P3]: parse-progress-log.sh hardening gaps

**Root cause**: First-pass implementation of parse-progress-log.sh handles the happy path correctly but lacks defensive coding for edge scenarios.

**Affected surfaces**:
- `scripts/parse-progress-log.sh:157-224` -- Silently overwrites existing resume-plan.md (from Excellence Finding 2)
- `scripts/parse-progress-log.sh:148-151` -- Redundant dead branch with misleading comment (from Excellence Finding 4)
- `scripts/parse-progress-log.sh:117-124` -- No validation for corrupted/malformed log lines (from Excellence Finding 8)

**Merge rationale**: All three are hardening gaps in the same new script. They share the characteristic of a first-pass implementation that correctly handles normal input but does not defend against abnormal conditions. Different code paths, but all addressable in a single hardening pass of the same file.

**Fix**: Single hardening pass: (1) add overwrite notice for resume-plan.md, (2) fix or remove the misleading comment at line 148, (3) add timestamp format validation for log line parsing.

**Acceptance criteria**:
- Overwrite of existing resume-plan.md produces a stderr notice
- Dead branch comment accurately describes the code's defensive purpose
- Malformed log lines are rejected with timestamp format validation

---

### RC-7 [P3]: Dual placeholder conventions for round-conditional blocks

**Root cause**: pantry.md uses `{PANTRY_ROUND_1_CHECK_START/END}` braces while reviews.md uses `<IF ROUND 1>` angle brackets for the same conditional construct. Two conventions for one purpose.

**Affected surfaces**:
- `orchestration/templates/pantry.md:382-416` -- Uses `{PANTRY_ROUND_1_CHECK_START/END}` markers (from Excellence Finding 1)
- `orchestration/templates/reviews.md:466-545` -- Uses `<IF ROUND 1>` markers (from Excellence Finding 1)
- `orchestration/templates/pantry.md:399-419` -- Risk of unresolved markers in composed briefs (from Excellence Finding 5)

**Merge rationale**: EX-1 identifies the inconsistency across files; EX-5 identifies the downstream risk of unresolved markers. Same design gap (two conventions), different manifestations (inconsistency vs runtime risk).

**Fix**: Standardize on one marker convention across both files. Add a Pantry self-check for leftover marker patterns in composed briefs.

**Acceptance criteria**:
- One consistent marker convention used in pantry.md and reviews.md
- Pantry validates composed briefs for leftover markers

---

### RC-8 [P3]: No tmux guard for dummy reviewer spawn

**Root cause**: RULES.md Step 3b-v runs `tmux display-message` without checking whether the Queen is inside a tmux session. The current single-Queen workflow does not require tmux.

**Affected surfaces**:
- `orchestration/RULES.md:168-177` -- tmux commands with no `$TMUX` environment guard (from Edge Cases Finding 4)

**Merge rationale**: Standalone finding.

**Fix**: Add `if [ -z "$TMUX" ]; then echo "Not in tmux -- dummy reviewer skipped"; else ... fi` guard.

**Acceptance criteria**:
- Dummy reviewer section does not error when run outside tmux
- Inside tmux, behavior is unchanged

---

### RC-9 [P3]: Documentation polish -- terminology, wording, and examples

**Root cause**: Minor documentation quality items across multiple files. Each is a standalone polish item that does not share a code path with others, but collectively they represent the expected cleanup from a multi-file change set.

**Sub-items**:
1. `scripts/parse-progress-log.sh:61-62` -- "step_key" vs "step name" terminology inconsistency (CL-3)
2. `orchestration/RULES.md:158-180` -- Step 1/Step 2 sub-numbering clashes with outer step numbering (CL-4)
3. `orchestration/templates/checkpoints.md:431` -- "floor of 3 applies" should be "minimum of 3 applies" (CL-5)
4. `orchestration/templates/pantry.md:141-167` -- Missing deprecation reminder on Step 3.5 (CL-6)
5. `orchestration/templates/reviews.md:11` -- Run-on sentence in transition gate text (CL-7)
6. `orchestration/templates/checkpoints.md:674-686` -- SSV section has FAIL example but no PASS example (CR-5)
7. `orchestration/templates/reviews.md:10` -- "most recent by timestamp" ordering method unspecified (CR-6)
8. `orchestration/templates/checkpoints.md:362-366` -- DMVDC Check 2 fallback no guard for missing AC (EC-5)
9. `orchestration/templates/checkpoints.md:670-683` -- Example uses `ant-farm-` prefix IDs that could be confused with real beads (EX-7)

**Merge rationale**: These 9 findings are grouped for reporting efficiency, not because they share a root cause. They are all P3 documentation/clarity items that individually have minimal impact. Filing as a single "documentation polish" bead to avoid bead bloat.

**Fix**: Address each sub-item individually during a documentation polish pass.

**Acceptance criteria**:
- Each sub-item's suggested fix applied
- No runtime impact expected from any of these changes

---

## Deduplication Log

**28 raw findings consolidated into 9 root causes:**

| Raw Finding | Root Cause | Merge Reason |
|-------------|-----------|--------------|
| CL-1 (Clarity P2) | RC-2 | Same line (RULES.md:186), same wrong filename |
| CL-2 (Clarity P2) | RC-3 | Same line (RULES.md:176), same undefined variable |
| CL-3 (Clarity P3) | RC-9 | Standalone P3 polish, grouped for efficiency |
| CL-4 (Clarity P3) | RC-9 | Standalone P3 polish, grouped for efficiency |
| CL-5 (Clarity P3) | RC-9 | Standalone P3 polish, grouped for efficiency |
| CL-6 (Clarity P3) | RC-9 | Standalone P3 polish, grouped for efficiency |
| CL-7 (Clarity P3) | RC-9 | Standalone P3 polish, grouped for efficiency |
| EC-1 (Edge Cases P1) | RC-1 | Same data structure (declare -A), same platform incompatibility |
| EC-2 (Edge Cases P1) | RC-1 | Same data structure (declare -A), same platform incompatibility |
| EC-3 (Edge Cases P3) | RC-2 | Same line (RULES.md:186), same wrong filename |
| EC-4 (Edge Cases P3) | RC-8 | Standalone -- no tmux guard |
| EC-4b (Edge Cases P2) | RC-3 | Same line (RULES.md:176), same undefined TIMESTAMP variable; cross-ref from clarity reviewer |
| EC-5 (Edge Cases P3) | RC-9 | Standalone P3 polish, grouped for efficiency |
| CR-1 (Correctness P2) | RC-4 | Standalone -- SSV approval gate design tension |
| CR-2 (Correctness P2) | RC-2 | Same line (RULES.md:186), same wrong filename |
| CR-3 (Correctness P2) | RC-5 | Same design divergence -- milestone naming scheme |
| CR-4 (Correctness P3) | RC-5 | Specific instance of CR-3's naming divergence |
| CR-5 (Correctness P3) | RC-9 | Standalone P3 polish, grouped for efficiency |
| CR-6 (Correctness P3) | RC-9 | Standalone P3 polish, grouped for efficiency |
| CR-7 (Correctness P1) | RC-1 | Same declare -A issue, verified on this machine; cross-ref from edge-cases reviewer |
| EX-1 (Excellence P3) | RC-7 | Dual marker conventions, same design gap |
| EX-2 (Excellence P3) | RC-6 | parse-progress-log.sh hardening, same file |
| EX-3 (Excellence P3) | RC-1 | Same data structure (declare -A), same bash version issue |
| EX-4 (Excellence P3) | RC-6 | parse-progress-log.sh hardening, same file |
| EX-5 (Excellence P3) | RC-7 | Unresolved markers, downstream of same dual-convention gap |
| EX-6 (Excellence P2) | RC-3 | Same line (RULES.md:176), same undefined variable |
| EX-7 (Excellence P3) | RC-9 | Standalone P3 polish, grouped for efficiency |
| EX-8 (Excellence P3) | RC-6 | parse-progress-log.sh hardening, same file |

**Dedup statistics**: 28 raw findings -> 9 root causes (19 merges, 68% dedup rate)

---

## Severity Conflicts

When 2+ reviewers assess the same root cause and their severity assignments differ by 2 or more levels:

### RC-1: parse-progress-log.sh bash/zsh incompatibility

- **Edge Cases (EC-1, EC-2)**: P1 -- crash recovery completely broken on macOS; wrong exit codes cause data loss risk
- **Correctness (CR-7)**: P1 -- verified on this machine (bash 3.2.57); blocks ant-farm-b219 criteria 1 and 2 in production
- **Excellence (EX-3)**: P3 -- code pattern is fragile under older bash versions; portability concern

**Gap**: P1 vs P3 (2 levels, between Edge Cases/Correctness and Excellence). The edge-cases and correctness reviewers assessed the platform-level impact (script non-functional on primary target), while the excellence reviewer focused on the code quality pattern. The P1 assessment is correct: the script's core function (crash recovery) is completely broken on macOS, which is the primary development platform.

**Final severity**: P1. Flag for Queen review -- the gap suggests the excellence reviewer may have evaluated the code pattern in isolation without testing on macOS bash 3.2 / zsh.

### RC-2: Progress log step3b wrong filename

- **Clarity (CL-1)**: P2 -- misleading operational instruction
- **Edge Cases (EC-3)**: P3 -- documentation inaccuracy with limited current runtime impact
- **Correctness (CR-2)**: P2 -- incorrect filename causes recovery failure

**Gap**: P2 vs P3 (1 level for CL-1/CR-2 vs EC-3). This is a 1-level gap, which does NOT meet the 2+ level threshold. No severity conflict to flag.

---

## Priority Breakdown

- **P1 (blocking)**: 1 root cause (RC-1)
- **P2 (important)**: 4 root causes (RC-2, RC-3, RC-4, RC-5)
- **P3 (polish)**: 4 root causes (RC-6, RC-7, RC-8, RC-9)

---

## Traceability Matrix

Every raw finding accounted for:

| Finding ID | Source | Severity | Disposition | Root Cause |
|-----------|--------|----------|-------------|-----------|
| CL-1 | Clarity | P2 | Merged | RC-2 |
| CL-2 | Clarity | P2 | Merged | RC-3 |
| CL-3 | Clarity | P3 | Grouped | RC-9 |
| CL-4 | Clarity | P3 | Grouped | RC-9 |
| CL-5 | Clarity | P3 | Grouped | RC-9 |
| CL-6 | Clarity | P3 | Grouped | RC-9 |
| CL-7 | Clarity | P3 | Grouped | RC-9 |
| EC-1 | Edge Cases | P1 | Merged | RC-1 |
| EC-2 | Edge Cases | P1 | Merged | RC-1 |
| EC-3 | Edge Cases | P3 | Merged | RC-2 |
| EC-4 | Edge Cases | P3 | Standalone | RC-8 |
| EC-4b | Edge Cases | P2 | Merged | RC-3 |
| EC-5 | Edge Cases | P3 | Grouped | RC-9 |
| CR-1 | Correctness | P2 | Standalone | RC-4 |
| CR-2 | Correctness | P2 | Merged | RC-2 |
| CR-3 | Correctness | P2 | Merged | RC-5 |
| CR-4 | Correctness | P3 | Merged | RC-5 |
| CR-5 | Correctness | P3 | Grouped | RC-9 |
| CR-6 | Correctness | P3 | Grouped | RC-9 |
| CR-7 | Correctness | P1 | Merged | RC-1 |
| EX-1 | Excellence | P3 | Merged | RC-7 |
| EX-2 | Excellence | P3 | Merged | RC-6 |
| EX-3 | Excellence | P3 | Merged | RC-1 |
| EX-4 | Excellence | P3 | Merged | RC-6 |
| EX-5 | Excellence | P3 | Merged | RC-7 |
| EX-6 | Excellence | P2 | Merged | RC-3 |
| EX-7 | Excellence | P3 | Grouped | RC-9 |
| EX-8 | Excellence | P3 | Merged | RC-6 |

**All 28 findings accounted for. 0 exclusions.**

---

## Reviewer Verdicts Summary

| Reviewer | Score | Verdict | P1 | P2 | P3 |
|----------|-------|---------|----|----|-----|
| Clarity | 8/10 | PASS WITH ISSUES | 0 | 2 | 5 |
| Edge Cases | 5/10 | NEEDS WORK | 2 | 1 | 3 |
| Correctness | 7/10 | PASS WITH ISSUES | 1 | 3 | 3 |
| Excellence | 8.5/10 | PASS WITH ISSUES | 0 | 1 | 7 |

---

## Verdict

**NEEDS WORK**

One P1 root cause (RC-1: parse-progress-log.sh is non-functional on macOS due to bash 4+ associative array dependency) and four P2 root causes require attention before this change set can be considered complete. The P1 is a blocking issue: the crash recovery script -- the primary deliverable of ant-farm-b219 -- does not work on the target platform. The P2s include a wrong filename in a progress log entry (RC-2), an undefined variable in the dummy reviewer command (RC-3), an unmet acceptance criterion for SSV (RC-4), and a design divergence from the progress log spec (RC-5).

The four P3 root causes are polish items that do not affect runtime correctness.

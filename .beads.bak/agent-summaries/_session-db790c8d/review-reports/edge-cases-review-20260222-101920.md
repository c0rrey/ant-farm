# Edge Cases Review Report

**Review type**: Edge Cases
**Review round**: 1
**Commit range**: 7569c5e^..c78875b
**Timestamp**: 20260222-101920
**Reviewer**: Nitpicker (Edge Cases specialization)

---

## Findings Catalog

### FINDING EC-01

**File**: `/Users/correy/projects/ant-farm/scripts/parse-progress-log.sh:62-72`
**Severity**: P2
**Category**: Missing input validation / boundary condition — milestone key gap

**Description**: The new `WAVE_WWD_PASS` progress log milestone introduced in `orchestration/RULES.md:131` is not in the `STEP_KEYS` array in `parse-progress-log.sh`. The array (lines 62-72) contains:

```
SESSION_INIT
SCOUT_COMPLETE
WAVE_SPAWNED
WAVE_VERIFIED
REVIEW_COMPLETE
REVIEW_TRIAGED
DOCS_COMMITTED
XREF_VERIFIED
SESSION_COMPLETE
```

`WAVE_WWD_PASS` sits between `WAVE_SPAWNED` and `WAVE_VERIFIED` in the workflow but is absent. If a session crashes after the Queen logs `WAVE_WWD_PASS` but before logging `WAVE_VERIFIED`, the recovery script will:
- Correctly detect that `WAVE_SPAWNED` is present
- Incorrectly conclude that `WAVE_VERIFIED` is the resume point (the first key NOT in the log)
- Ignore the fact that WWD already passed for the wave

This causes the Queen to re-run WWD on wave agents that already passed, wasting resources. More critically, the step status table in `resume-plan.md` will never show `WAVE_WWD_PASS` as COMPLETE for any session, making recovery plans inaccurate for anyone reading them. The resume action for `WAVE_VERIFIED` says "re-spawn Pest Control for WWD/DMVDC on any unverified waves" — which would duplicate WWD runs already logged as complete.

**Note**: `parse-progress-log.sh` is not in the review file list (it was not changed in this commit range). However, RULES.md:131 introduced a new milestone key that this script must handle. The defect is a cross-file consistency gap introduced by the RULES.md change. Reporting here because the behavioral impact is incorrect crash recovery — the key was introduced in the reviewed diff.

**Suggested fix**: Add `WAVE_WWD_PASS` to the `STEP_KEYS` array in `parse-progress-log.sh` (between `WAVE_SPAWNED` and `WAVE_VERIFIED`), add a `step_label` case for it (e.g., `"WWD Pass: Scope verification (WWD) complete for wave"`), and add a `step_resume_action` case (e.g., `"Re-run WWD for unverified tasks in the current wave, or proceed to DMVDC if all WWD reports passed"`).

---

### FINDING EC-02

**File**: `/Users/correy/projects/ant-farm/orchestration/RULES.md:121-130`
**Severity**: P3
**Category**: Boundary condition — partial wave commit in batch mode

**Description**: The batch mode description says "After ALL wave agents have committed, spawn one Pest Control instance per committed task (can be concurrent)." The boundary case of a partial wave commit is not handled: if some agents in a parallel wave commit successfully but others crash without committing, the trigger condition "ALL wave agents have committed" is never met, and no WWD runs at all.

The mid-wave decision tree in RULES.md (lines 335-341) covers agent failure at a high level: "Log failure, file a beads issue for the failed task, continue with remaining agents." However, there is no explicit instruction on when to run WWD for a partially-committed batch wave. Should WWD run for the agents that did commit once failure of others is confirmed? Or should WWD wait indefinitely?

This is a P3 because the existing wave failure threshold (line 431: "If more than 50% of agents in a single wave fail... the Queen must stop spawning new agents") provides a fallback, but the combination of partial commits + batch mode creates an ambiguous trigger for WWD that could leave committed work unverified.

**Suggested fix**: Add a clarifying sentence to the batch mode description: "If some agents fail without committing, run WWD only for agents that did commit, then proceed to DMVDC for the committed subset. Treat uncommitted agents as failures per the Wave Failure Threshold rules."

---

### FINDING EC-03

**File**: `/Users/correy/projects/ant-farm/orchestration/RULES.md:129-130`
**Severity**: P3
**Category**: Boundary condition — mode selection edge case

**Description**: The mode selection rule says: "If you spawned agents in a single message (parallel wave), use batch mode. If you spawned agents individually in separate messages, use serial mode." This does not address the edge case of a single agent spawned alone in a single message — technically "a single message," which would trigger batch mode, but functionally identical to serial mode.

In batch mode, the Queen waits for "ALL wave agents" to commit before running WWD. For a single agent this is fine (it works either way). But the phrase "one WWD instance per committed task, run concurrently" implies there's a benefit to batch mode that doesn't apply when N=1. The text doesn't break down, but a reader following the rules literally would choose batch mode for single-agent waves and produce identical behavior.

This is a P3 because there's no behavior difference for N=1 — the outcome is the same either way. The ambiguity only creates reader confusion, not a runtime failure.

**Suggested fix**: Add a parenthetical clarification: "For single-agent waves, either mode produces equivalent results; serial mode is simpler."

---

## Preliminary Groupings

### Group A: Missing milestone key in crash-recovery script (Root cause: cross-file sync gap)

- **EC-01** — `parse-progress-log.sh` does not know about `WAVE_WWD_PASS`, a milestone added to RULES.md in this diff.

This is a recurring pattern in this codebase: adding a new log milestone in RULES.md requires a parallel update to `parse-progress-log.sh`'s `STEP_KEYS` array. There is no automated check or documented dependency table entry enforcing this. CONTRIBUTING.md's cross-file dependency tables (lines 186-248) do not mention this relationship.

### Group B: Batch mode boundary conditions (Root cause: new feature incomplete edge handling)

- **EC-02** — partial wave commit unhandled in batch mode
- **EC-03** — N=1 edge case in mode selection rule

Both stem from the batch mode documentation being written primarily for the N>1 parallel case, with insufficient attention to boundary values (0 commits, 1 agent).

---

## Summary Statistics

| Severity | Count | Findings |
|----------|-------|----------|
| P1 | 0 | — |
| P2 | 1 | EC-01 |
| P3 | 2 | EC-02, EC-03 |
| **Total** | **3** | |

---

## Cross-Review Messages

### Sent

- **To Correctness reviewer**: "Logic gap at `/Users/correy/projects/ant-farm/scripts/parse-progress-log.sh:62-72` — the `WAVE_WWD_PASS` milestone added in RULES.md:131 is not in `STEP_KEYS`. This affects crash-recovery correctness: a session that crashed after logging `WAVE_WWD_PASS` would be told to resume at WAVE_VERIFIED and re-run WWD unnecessarily. May want to check whether parse-progress-log.sh correctly reflects the post-diff milestone sequence."

### Received

- **From Excellence reviewer**: "Found a potential boundary/edge-cases gap in RULES.md:L119-L131. The batch-mode WWD description says 'After ALL wave agents have committed, spawn one Pest Control instance per committed task.' It assumes all wave agents have committed by the time batch WWD fires, but provides no guard for agents that crashed or timed out before committing. In batch mode, those uncommitted tasks would be silently skipped by WWD with no error path. Serial mode is not affected. May want to review."
  - **Disposition**: Already cataloged as EC-02 (P3) in this report. No duplicate filing needed — Big Head will handle deduplication.

---

## Coverage Log

| File | Status | Notes |
|------|--------|-------|
| `/Users/correy/projects/ant-farm/agents/scout-organizer.md` | Reviewed — no issues | Single-line change: `model: sonnet` → `model: opus`. No edge case concerns — frontmatter value change only, no conditional logic. |
| `/Users/correy/projects/ant-farm/CONTRIBUTING.md` | Reviewed — no issues | Two changes: (1) rsync flag documentation corrected (`--delete` removed, `_archive/` exclusion added); (2) re-run warning added for install-hooks.sh. Both are documentation-only. The rsync description change accurately reflects non-destructive sync behavior; no edge case concerns in the documentation itself. |
| `/Users/correy/projects/ant-farm/orchestration/GLOSSARY.md` | Reviewed — no issues | Two rows updated from `sonnet` to `opus` for Scout and Pantry model assignments. Documentation-only change; no logic or boundary conditions involved. |
| `/Users/correy/projects/ant-farm/orchestration/RULES.md` | Reviewed — 3 findings (EC-01, EC-02, EC-03) | New WWD batch/serial execution mode documentation introduced. Cross-file milestone sync gap (EC-01) and boundary condition gaps (EC-02, EC-03) found. |
| `/Users/correy/projects/ant-farm/orchestration/templates/checkpoints.md` | Reviewed — no issues | Two types of changes: (1) WWD "When" section expanded to describe serial vs. batch modes, consistent with RULES.md; (2) `Agent type (spawned by Pest Control): code-reviewer` lines removed from all 5 checkpoint sections, consistent with the corrected role distinction (Pest Control executes directly, does not spawn subagents). No edge case concerns — the removal eliminates incorrect instructions rather than introducing new ones. |
| `/Users/correy/projects/ant-farm/README.md` | Reviewed — no issues | Single change: "a sonnet subagent" → "an opus subagent" in Step 1 description. Documentation-only; no boundary conditions. |

---

## Overall Assessment

**Score**: 8/10

**Verdict**: PASS WITH ISSUES

The changes in this commit range are primarily documentation corrections (model references, role descriptions, rsync flags) that are straightforward and do not introduce edge case risks. The WWD batch/serial execution mode documentation is a meaningful improvement in clarity and completeness.

The one actionable edge case concern (EC-01, P2) is a cross-file sync gap: the new `WAVE_WWD_PASS` milestone added to RULES.md's progress log examples was not added to `parse-progress-log.sh`'s milestone key list. This means crash recovery for sessions that logged `WAVE_WWD_PASS` but not yet `WAVE_VERIFIED` will produce an inaccurate resume plan (telling the Queen to re-run WWD for a wave that already passed). The fix is a small addition to `parse-progress-log.sh` — not to the reviewed files themselves, but the gap was introduced by the reviewed change.

The P3 findings (EC-02, EC-03) are minor documentation gaps in the new batch mode text and do not cause failures.

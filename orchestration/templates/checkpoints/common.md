<!-- Reader: Checkpoint Auditor. The Orchestrator does NOT read this file. -->
# Verification Checkpoints

**Term definitions (canonical across all orchestration templates):**

For the full extraction algorithm, see `~/.claude/orchestration/reference/dependency-analysis.md` (Term Definitions section).

- `{TASK_ID}` — full crumb ID including project prefix. Two formats exist:
  - **Standalone task** (no epic sub-ID): `ant-farm-596y`, `hs_website-9oa`
  - **Epic sub-task** (dotted sub-ID): `ant-farm-74g.1`, `my-project-74g.1`
- `{TASK_SUFFIX}` — the short identifier used in file paths and artifact names. Derived by taking everything after the LAST hyphen, then converting any dot to nothing (joining the alphanumeric parts):
  - `ant-farm-596y` → `596y` (standalone task — no dot, suffix is the bare token after the last hyphen)
  - `ant-farm-74g.1` → `74g1` (epic sub-task — dot-normalized)
  - `my-project-74g.1` → `74g1` (project name contains a hyphen — split on LAST hyphen, then dot-normalize)
- `{SESSION_DIR}` — session artifact directory path (e.g., `.crumbs/sessions/_session-abc123`)
- `{checkpoint}` — lowercase checkpoint name used in artifact filenames (e.g., `pre-spawn-check`, `scope-verify`, `claims-vs-code`, `review-integrity`, `pre-spawn-check-review`, `claims-vs-code-review`)

## Checkpoint Auditor Overview

All checkpoint verifications (startup-check, pre-spawn-check, scope-verify, claims-vs-code, review-integrity, session-complete) are executed by the **Checkpoint Auditor**, a dedicated verification subagent that cross-checks orchestrator and agent work against ground truth.

**Role distinction**: The Orchestrator spawns the Checkpoint Auditor to run a checkpoint. The Checkpoint Auditor executes all checkpoint logic directly — it does not spawn subagents. The Checkpoint Auditor has tools: Bash, Read, Write, Glob, Grep (no Task tool).

**Checkpoint Auditor responsibilities:**
- Pre-implementation Recon Planner strategy verification (startup-check)
- Pre-spawn prompt audits (pre-spawn-check)
- Post-commit scope verification (scope-verify)
- Post-completion substance verification (claims-vs-code)
- Consolidation integrity audits (review-integrity)
- Exec summary and CHANGELOG verification before push (session-complete)

**Artifact naming conventions:**
- **Task-specific checkpoints (scope-verify, claims-vs-code for Implementers):** `pc-{TASK_SUFFIX}-{checkpoint}-{timestamp}.md`
  - Example: `pc-74g1-scope-verify-20260215-001045.md`
  - Example: `pc-74g1-claims-vs-code-20260215-003422.md`
- **Session-wide checkpoints (startup-check, pre-spawn-check for Implementers, pre-spawn-check-review, review-integrity, session-complete):** `pc-session-{checkpoint}-{timestamp}.md`
  - Example: `pc-session-startup-check-20260215-001045.md`
  - Example: `pc-session-pre-spawn-check-impl-20260215-001145.md` (Implementer pre-spawn-check: Orchestrator batches all wave prompts into one audit)
  - Example: `pc-session-pre-spawn-check-review-20260215-001145.md`
  - Example: `pc-session-review-integrity-20260215-010520.md`
  - Example: `pc-session-session-complete-20260215-012345.md`
  - Note: Implementer pre-spawn-check uses session-wide naming because the Orchestrator audits all prompts for a wave in a single run. Per-task naming (`pc-{TASK_SUFFIX}-pre-spawn-check-{timestamp}.md`) applies only when auditing a single Implementer prompt in isolation (rare).
<!-- Historical (pre-_session-068ecc83): Earlier sessions used varied naming formats that do not match the conventions above. Common patterns included wave-based checkpoint letters (checkpoint-auditor-{session}-checkpoint-{A|B}-{timestamp}.md), trail-scoped directories ({trail}/verification/pc/ instead of {SESSION_DIR}/pc/), and non-standardized prefixes (pc-review-pre-spawn-check-, checkpoint-auditor-). _session-068ecc83 is the first session to use the current standard fully. Artifacts from earlier sessions are expected to diverge from the current convention; do not treat those divergences as errors. -->

All checkpoints write to `{SESSION_DIR}/pc/`.

**Task suffix derivation:** See `~/.claude/orchestration/reference/dependency-analysis.md` (Term Definitions section) for extraction algorithm. Example: `74g1` from `my-project-74g.1`.

**Timestamp format:** `YYYYMMDD-HHmmss` (UTC)

**Directory creation**: the Orchestrator creates `{SESSION_DIR}/pc/` at session start (Step 0 in RULES.md). Agents and the Checkpoint Auditor can write immediately without creating directories.

**The Orchestrator's responsibility**: the Orchestrator MUST include `**Summary output path**` in Implementer prompt context. For review prompts, include the session-scoped review report paths and all participating trail IDs (for context). Reviewers write to `{SESSION_DIR}/review-reports/`, not per-trail directories.

**Review timestamp convention**: the Orchestrator generates a single timestamp per review cycle (format defined in **Timestamp format** above) and passes the exact output filenames to each reviewer and Review Consolidator. This prevents reviewers from independently generating different timestamps.

---

## Verdict Thresholds Summary

This section provides a unified reference for all checkpoint verdict definitions and tie-breaking rules.

### Common Verdict Definitions

All checkpoints use the following verdict states:

**PASS**: Verification succeeded. No action required. Proceed to next phase.

**WARN** (checkpoints: pre-spawn-check, scope-verify only):
- pre-spawn-check WARN: Small file exception approved. Orchestrator reviews and approves before spawn.
- scope-verify WARN: Legitimate extra files. Soft gate — does not block queue. Orchestrator approves concurrently.

**PARTIAL** (claims-vs-code and review-integrity only): Some checks failed. Agent can repair and resubmit, or consolidation can be amended. Does not escalate to user.

**FAIL**: Verification failed. Blocking issue detected. Pause and remediate before continuing.

### Checkpoint-Specific Thresholds

| Checkpoint | Threshold / Condition | Tie-Breaking Rule | Queue Blocking |
|---|---|---|---|
| **startup-check** | All 4 checks must pass (1, 1b, 2, 3) | First-listed violation per check | FAIL blocks Prompt Composer spawn and all downstream steps |
| **pre-spawn-check (Implementers)** | Check 7 WARN allowed if file < 100 lines | First-listed section/function | WARN does not block; Orchestrator approves before spawn |
| **pre-spawn-check (Reviewers)** | All round-active prompts identical file list (round 1: 4; round 2+: 2) | (No tie-breaking) | FAIL blocks spawn |
| **scope-verify** | Small file = <100 lines | First-listed changed file | WARN does not block queue; FAIL blocks queue |
| **claims-vs-code (Implementers)** | Pick 2 criteria: first-listed OR identified-as-critical (or all, if fewer than 2 total) | First-listed acceptance criterion | PARTIAL allows resubmission; FAIL escalates |
| **claims-vs-code (Reviewers)** | Sample size = min(N, max(3, min(5, ceil(N/3)))) — see Check 1 for worked examples | Include highest-severity + all tiers | PARTIAL allows resubmission; FAIL escalates |
| **review-integrity** | Finding count must reconcile to 100% | Earliest-filed crumb per root cause | PARTIAL: fix and re-run; FAIL blocks user presentation |
| **session-complete** | All 6 checks must pass | First-listed violation per check | FAIL blocks git push; one Session Scribe retry allowed before escalation |

### Details by Checkpoint

**startup-check Verdict Specifics:**
- PASS: All 4 checks pass (no unresolved file overlaps within a wave, no agent exceeds 3 tasks per wave, file lists match crumb descriptions, no intra-wave dependency violations). File overlaps between tasks assigned to the same agent are resolved — not violations.
- FAIL: Any check fails. Blocks Prompt Composer spawn and all downstream spawning until Recon Planner re-runs or issue is resolved.

**pre-spawn-check Verdict Specifics:**
- PASS: All 7 checks pass
- WARN: Check 7 is WARN (file-level scope: path given but no line numbers specified) + file <100 lines + prompt has context. Acceptable.
- FAIL: Any check fails, or Check 7 is WARN + file ≥100 lines

**scope-verify Verdict Specifics:**
- PASS: All changed files in expected scope
- WARN: Extra files changed that are legitimate build artifacts (require Orchestrator approval but don't block queue)
- FAIL: Scope creep (files outside task scope). Blocks queue pending investigation.

**claims-vs-code Verdict Specifics:**
- PASS: All 5 checks confirm (Check 1: git diff matches claims, Check 2: 2 criteria verified, Check 3: approaches distinct, Check 4: correctness evidence specific, Check 5: test-first ordering confirmed or skipped)
- PARTIAL: Some checks fail (agent can resubmit)
- FAIL: Multiple checks fail or critical fabrication (escalate to user)

**review-integrity Verdict Specifics:**
- PASS: All 9 checks confirm (finding reconciliation, crumb quality, root cause spot-check, priority calibration, traceability, dedup correctness, provenance)
- PARTIAL: Some checks fail (fix and re-run)
- FAIL: Critical failures (e.g., missing reports, orphaned findings). Must resolve before presenting to user.

**session-complete Verdict Specifics:**
- PASS: All 6 checks pass (task coverage, commit coverage, open crumb accuracy, CHANGELOG fidelity, section completeness, metric consistency)
- FAIL: Any check fails. Blocks git push. Re-spawn Session Scribe with specific violations (max 1 retry). Second failure escalates to user.

---

## Sentinel File Write (Background Agents)

When running as a background agent (`run_in_background: true`), write a sentinel file as your absolute
last action after completing all checkpoint work and writing the checkpoint artifact:

```bash
echo "VERDICT: {PASS|WARN|PARTIAL|FAIL}
CHECKPOINT: {checkpoint-name}
ARTIFACT: {path-to-checkpoint-artifact}
SUMMARY: {one-line verdict description}" > "${SESSION_DIR}/signals/{checkpoint-name}.done"
```

This signals completion to the Orchestrator without requiring TaskOutput. The Orchestrator polls for `.done` files
in `${SESSION_DIR}/signals/`. If you are running as a foreground agent (the common case), skip this step.

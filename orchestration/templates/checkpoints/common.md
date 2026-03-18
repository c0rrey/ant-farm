<!-- Reader: Pest Control. The Queen does NOT read this file. -->
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
- `{checkpoint}` — lowercase checkpoint abbreviation used in artifact filenames (e.g., `cco`, `wwd`, `cmvcc`, `ccb`, `cco-review`, `cmvcc-review`)

## Pest Control Overview

All checkpoint verifications (SSV, CCO, WWD, CMVCC, CCB, ESV) are executed by **Pest Control**, a dedicated verification subagent that cross-checks orchestrator and agent work against ground truth.

**Role distinction**: The Queen spawns Pest Control to run a checkpoint. Pest Control executes all checkpoint logic directly — it does not spawn subagents. Pest Control has tools: Bash, Read, Write, Glob, Grep (no Task tool).

**Pest Control responsibilities:**
- Pre-implementation Scout strategy verification (SSV)
- Pre-spawn prompt audits (CCO)
- Post-commit scope verification (WWD)
- Post-completion substance verification (CMVCC)
- Consolidation integrity audits (CCB)
- Exec summary and CHANGELOG verification before push (ESV)

**Artifact naming conventions:**
- **Task-specific checkpoints (WWD, CMVCC for Crumb Gatherers):** `pc-{TASK_SUFFIX}-{checkpoint}-{timestamp}.md`
  - Example: `pc-74g1-wwd-20260215-001045.md`
  - Example: `pc-74g1-cmvcc-20260215-003422.md`
- **Session-wide checkpoints (SSV, CCO for Crumb Gatherers, CCO-review, CCB, ESV):** `pc-session-{checkpoint}-{timestamp}.md`
  - Example: `pc-session-ssv-20260215-001045.md`
  - Example: `pc-session-cco-impl-20260215-001145.md` (Crumb Gatherer CCO: Queen batches all wave prompts into one audit)
  - Example: `pc-session-cco-review-20260215-001145.md`
  - Example: `pc-session-ccb-20260215-010520.md`
  - Example: `pc-session-esv-20260215-012345.md`
  - Note: Crumb Gatherer CCO uses session-wide naming because the Queen audits all prompts for a wave in a single CCO run. Per-task CCO naming (`pc-{TASK_SUFFIX}-cco-{timestamp}.md`) applies only when auditing a single Crumb Gatherer prompt in isolation (rare).
- **Historical (pre-_session-068ecc83):** Earlier sessions used varied naming formats that do not match the conventions above. Common patterns included wave-based checkpoint letters (`pest-control-{session}-checkpoint-{A|B}-{timestamp}.md`), trail-scoped directories (`{trail}/verification/pc/` instead of `{SESSION_DIR}/pc/`), and non-standardized prefixes (`pc-review-cco-`, `pest-control-`). `_session-068ecc83` is the first session to use the current standard fully. Artifacts from earlier sessions are expected to diverge from the current convention; do not treat those divergences as errors.

All checkpoints write to `{SESSION_DIR}/pc/`.

**Task suffix derivation:** See `~/.claude/orchestration/reference/dependency-analysis.md` (Term Definitions section) for extraction algorithm. Example: `74g1` from `my-project-74g.1`.

**Timestamp format:** `YYYYMMDD-HHmmss` (UTC)

**Directory creation**: the Queen creates `{SESSION_DIR}/pc/` at session start (Step 0 in RULES.md). Agents and Pest Control can write immediately without creating directories.

**The Queen's responsibility**: the Queen MUST include `**Summary output path**` in Crumb Gatherer prompt context. For review prompts, include the session-scoped review report paths and all participating trail IDs (for context). Reviewers write to `{SESSION_DIR}/review-reports/`, not per-trail directories.

**Review timestamp convention**: the Queen generates a single timestamp per review cycle (format defined in **Timestamp format** above) and passes the exact output filenames to each reviewer and Big Head. This prevents reviewers from independently generating different timestamps.

---

## Verdict Thresholds Summary

This section provides a unified reference for all checkpoint verdict definitions and tie-breaking rules.

### Common Verdict Definitions

All checkpoints use the following verdict states:

**PASS**: Verification succeeded. No action required. Proceed to next phase.

**WARN** (checkpoints: CCO, WWD only):
- CCO WARN: Small file exception approved. Queen reviews and approves before spawn.
- WWD WARN: Legitimate extra files. Soft gate — does not block queue. Queen approves concurrently.

**PARTIAL** (CMVCC and CCB only): Some checks failed. Agent can repair and resubmit, or consolidation can be amended. Does not escalate to user.

**FAIL**: Verification failed. Blocking issue detected. Pause and remediate before continuing.

### Checkpoint-Specific Thresholds

| Checkpoint | Quantitative Threshold | Tie-Breaking Rule | Queue Blocking |
|---|---|---|---|
| **SSV** | All 3 checks must pass | First-listed violation per check | FAIL blocks Pantry spawn and all downstream steps |
| **CCO (Crumb Gatherers)** | Small file = <100 lines | First-listed section/function | WARN does not block; Queen approves before spawn |
| **CCO (Nitpickers)** | All round-active prompts identical file list (round 1: 4; round 2+: 2) | (No tie-breaking) | FAIL blocks spawn |
| **WWD** | Small file = <100 lines | First-listed changed file | WARN does not block queue; FAIL blocks queue |
| **CMVCC (Crumb Gatherers)** | Pick 2 criteria: first-listed OR identified-as-critical OR all if <2 | First-listed acceptance criterion | PARTIAL allows resubmission; FAIL escalates |
| **CMVCC (Nitpickers)** | Sample size = min(N, max(3, min(5, ceil(N/3)))) — see Check 1 for worked examples | Include highest-severity + all tiers | PARTIAL allows resubmission; FAIL escalates |
| **CCB** | Finding count must reconcile to 100% | Earliest-filed crumb per root cause | PARTIAL: fix and re-run; FAIL blocks user presentation |
| **ESV** | All 6 checks must pass | First-listed violation per check | FAIL blocks git push; one Scribe retry allowed before escalation |

### Details by Checkpoint

**SSV Verdict Specifics:**
- PASS: All 3 checks pass (no file overlaps within a wave, file lists match crumb descriptions, no intra-wave dependency violations)
- FAIL: Any check fails. Blocks Pantry spawn and all downstream spawning until Scout re-runs or issue is resolved.

**CCO Verdict Specifics:**
- PASS: All 7 checks pass
- WARN: Check 7 is WARN (file-level scope) + file <100 lines + prompt has context. Acceptable.
- FAIL: Any check fails, or Check 7 is WARN + file ≥100 lines

**WWD Verdict Specifics:**
- PASS: All changed files in expected scope
- WARN: Extra files changed that are legitimate build artifacts (require Queen approval but don't block queue)
- FAIL: Scope creep (files outside task scope). Blocks queue pending investigation.

**CMVCC Verdict Specifics:**
- PASS: All 4 checks confirm (Check 1: git diff matches claims, Check 2: 2 criteria verified, Check 3: approaches distinct, Check 4: correctness evidence specific)
- PARTIAL: Some checks fail (agent can resubmit)
- FAIL: Multiple checks fail or critical fabrication (escalate to user)

**CCB Verdict Specifics:**
- PASS: All 8 checks confirm (finding reconciliation, crumb quality, priority calibration, traceability, dedup correctness, provenance)
- PARTIAL: Some checks fail (fix and re-run)
- FAIL: Critical failures (e.g., missing reports, orphaned findings). Must resolve before presenting to user.

**ESV Verdict Specifics:**
- PASS: All 6 checks pass (task coverage, commit coverage, open crumb accuracy, CHANGELOG fidelity, section completeness, metric consistency)
- FAIL: Any check fails. Blocks git push. Re-spawn Scribe with specific violations (max 1 retry). Second failure escalates to user.

---

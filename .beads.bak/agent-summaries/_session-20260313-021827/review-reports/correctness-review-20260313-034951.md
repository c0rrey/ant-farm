# Correctness Review Report
**Session**: _session-20260313-021827
**Round**: 1
**Commit range**: 0ec9ed2..HEAD
**Timestamp**: 20260313-034951
**Reviewer**: correctness

---

## Findings Catalog

### F-001 — `crumb sync` referenced in AGENTS.md but does not exist in crumb.py
- **File:line**: `AGENTS.md:12` and `AGENTS.md:28`
- **Severity**: P1
- **Category**: Acceptance Criteria Violation / Logic Correctness
- **Description**: AGENTS.md includes `crumb sync` in two places:
  1. L12 (quick reference table): `crumb sync` listed as a sync command
  2. L28 (landing-the-plane push block): `crumb sync` is a required step in the session-completion workflow

  `crumb.py` has no `sync` subcommand. Running `crumb sync` will produce a command-not-found error. Any agent following AGENTS.md for session completion will fail at the `crumb sync` step.

  This directly violates ant-farm-vjhe acceptance criterion: "No broken links or references to removed Beads/Dolt tools — all `bd` and Dolt-related references replaced with crumb equivalents or removed."

  `crumb sync` was a `bd sync` analogue that was added to AGENTS.md, but no corresponding `sync` subcommand was implemented in crumb.py.
- **Suggested fix**: Remove `crumb sync` from AGENTS.md:12 (quick reference table row) and AGENTS.md:28 (push block step). The landing-the-plane push workflow in AGENTS.md should match CLAUDE.md (L65-69), which correctly omits `crumb sync`.

---

### F-002 — Stale session artifact path in AGENTS.md
- **File:line**: `AGENTS.md:33`
- **Severity**: P2
- **Category**: Acceptance Criteria Violation
- **Description**: AGENTS.md:33 references `.crumbs/agent-summaries/_session-*/` as the retained session artifact path. RULES.md (L509) defines the session directory as `.crumbs/sessions/_session-${SESSION_ID}`, and queen-state.md (L8) and skills/work.md (L108) both use `.crumbs/sessions/_session-*/`. The path in AGENTS.md is stale and does not match where sessions are actually written.

  This violates ant-farm-vjhe AC requirement that all references be updated to correct crumb equivalents.
- **Suggested fix**: Update AGENTS.md:33 to reference `.crumbs/sessions/_session-*/` instead of `.crumbs/agent-summaries/_session-*/`.

  Note: Cross-file reference propagation aspect of this finding is being forwarded to the Drift reviewer.

---

### F-003 — Stale session artifact path in CLAUDE.md
- **File:line**: `CLAUDE.md:71`
- **Severity**: P2
- **Category**: Acceptance Criteria Violation
- **Description**: CLAUDE.md:71 references `.crumbs/agent-summaries/_session-*/` as the session artifact path in the cleanup step of the Landing the Plane workflow. The correct path per RULES.md, queen-state.md, and skills/work.md is `.crumbs/sessions/_session-*/`. Because setup.sh (and sync-to-claude.sh) copies CLAUDE.md to `~/.claude/CLAUDE.md`, this stale path propagates to the global config that all agents read.

  This violates ant-farm-vjhe AC for correct references and ant-farm-ax38 requirement that "Global ~/.claude/CLAUDE.md: matching changes applied (files should stay in sync)" — the stale path means the synced file has a wrong path in it.
- **Suggested fix**: Update CLAUDE.md:71 from `.crumbs/agent-summaries/_session-*/` to `.crumbs/sessions/_session-*/`. Re-run setup.sh (or sync-to-claude.sh) to propagate the fix to `~/.claude/CLAUDE.md`.

  Note: Cross-file reference propagation aspect forwarded to Drift reviewer.

---

### F-004 — setup.sh does not copy CLAUDE.md to ~/.claude/CLAUDE.md despite claiming to replace sync-to-claude.sh
- **File:line**: `scripts/setup.sh:4`
- **Severity**: P2
- **Category**: Acceptance Criteria Violation
- **Description**: setup.sh:4 contains the comment "# Replaces sync-to-claude.sh" and is introduced by ant-farm-ax38 as the unified setup script. However, setup.sh does NOT copy `CLAUDE.md` to `~/.claude/CLAUDE.md`. The existing sync-to-claude.sh DOES perform this copy. If a user runs setup.sh thinking it is a complete replacement for sync-to-claude.sh, `~/.claude/CLAUDE.md` will not be updated.

  ant-farm-ax38 acceptance criterion: "Global ~/.claude/CLAUDE.md: matching changes applied (files should stay in sync)" — this criterion cannot be satisfied by setup.sh alone.

  Files setup.sh DOES sync: `agents/*.md` → `~/.claude/agents/`, `orchestration/` → `~/.claude/orchestration/`, `build-review-prompts.sh` → `~/.claude/orchestration/scripts/`, `crumb.py` → `~/.local/bin/crumb`.
  Files setup.sh does NOT sync: `CLAUDE.md` → `~/.claude/CLAUDE.md`.
- **Suggested fix**: Either (a) add a step to setup.sh to copy `CLAUDE.md` to `~/.claude/CLAUDE.md`, or (b) update the comment on setup.sh:4 to clarify that sync-to-claude.sh must also be run for CLAUDE.md sync, or (c) merge sync-to-claude.sh into setup.sh entirely and remove sync-to-claude.sh to avoid confusion.

---

### F-005 — Landing-the-plane instructions inconsistent between AGENTS.md and CLAUDE.md
- **File:line**: `AGENTS.md:27-30` vs `CLAUDE.md:65-69`
- **Severity**: P3
- **Category**: Cross-file consistency
- **Description**: The push block in AGENTS.md (L27-30) includes `crumb sync` as a required step. The push block in CLAUDE.md (L65-69) does NOT include `crumb sync`. These two files present conflicting landing-the-plane instructions to agents. CLAUDE.md is correct (no crumb sync); AGENTS.md is wrong (references nonexistent command). This is secondary to F-001 — resolving F-001 will resolve this inconsistency.
- **Suggested fix**: Resolved by fixing F-001. After removing `crumb sync` from AGENTS.md, both files will align.

---

## Preliminary Groupings

### Root Cause A: `crumb sync` added to AGENTS.md without crumb.py implementation (F-001, F-005)
`crumb sync` was written into AGENTS.md as a migration equivalent for `bd sync`, but no `sync` subcommand was implemented in crumb.py. This affects the quick reference table (L12) and the landing-the-plane push block (L28), and creates an inconsistency with CLAUDE.md's push block (F-005).

**Severity**: P1 (F-001), P3 (F-005)

### Root Cause B: Session directory path not updated in AGENTS.md and CLAUDE.md (F-002, F-003)
The session artifact directory was renamed from `.crumbs/agent-summaries/_session-*/` to `.crumbs/sessions/_session-*/` in RULES.md, queen-state.md, and skills/work.md, but the new path was not propagated to AGENTS.md (L33) and CLAUDE.md (L71). Because CLAUDE.md syncs to `~/.claude/CLAUDE.md`, the stale path spreads to the global config.

**Severity**: P2 (both)

### Root Cause C: setup.sh scope gap — CLAUDE.md sync omitted (F-004)
setup.sh is described as replacing sync-to-claude.sh but does not replicate the CLAUDE.md → ~/.claude/CLAUDE.md copy step. This is a scope gap in ant-farm-ax38's implementation.

**Severity**: P2

---

## Summary Statistics

| Severity | Count | Finding IDs |
|----------|-------|-------------|
| P1       | 1     | F-001       |
| P2       | 3     | F-002, F-003, F-004 |
| P3       | 1     | F-005       |
| **Total**| **5** |             |

**Root cause count**: 3

---

## Acceptance Criteria Verification

| Task ID | AC Status | Notes |
|---------|-----------|-------|
| ant-farm-6gg6 | PASS | Could not verify via `bd show` (bd CLI no longer available) — reviewed scope by reading file content. Files reviewed match expected migration scope. |
| ant-farm-eifm | PASS | Forager template file clean; no bd references found. |
| ant-farm-gvd4 | PASS | CONTRIBUTING.md clean; no bd references. |
| ant-farm-k03k | PASS | RULES.md: all `bd` references replaced with `crumb` equivalents. SESSION_DIR uses `.crumbs/sessions/`. |
| ant-farm-mmo3 | PASS | README.md: bd references removed; crumb equivalents present. |
| ant-farm-vjhe | FAIL (P1) | AGENTS.md contains `crumb sync` (L12, L28) — command does not exist. Also contains stale path (L33). See F-001, F-002. |
| ant-farm-6d3f | PASS | skills/ files all use crumb commands. |
| ant-farm-a50b | PASS | big-head-skeleton.md uses crumb commands throughout. |
| ant-farm-ax38 | FAIL (P2) | setup.sh does not copy CLAUDE.md to ~/.claude/CLAUDE.md. CLAUDE.md:71 has stale path. See F-003, F-004. |
| ant-farm-epmv | PASS | nitpicker-skeleton.md clean. |
| ant-farm-h2gu | PASS | scout-organizer.md, forager-skeleton.md clean. |
| ant-farm-n56q | PASS | pantry.md clean. |
| ant-farm-o0wu | PASS | reviews.md, SESSION_PLAN_TEMPLATE.md, implementation.md, queen-state.md, scout.md clean. |
| ant-farm-rue4 | PASS | RULES.md: exec-summary copy to `.crumbs/history/exec-summary-${SESSION_ID}.md` present at L420-421. |
| ant-farm-veht | PASS | checkpoints.md: TDV section added (L925-1112) with 5 structural checks, 3 heuristic warnings, provisional wave algorithm, verdict definitions, max 2 retries. |

**Tasks FAILING AC**: ant-farm-vjhe, ant-farm-ax38

---

## Cross-Review Messages

### Sent

**To: drift** — "Stale session path at `AGENTS.md:33` and `CLAUDE.md:71` references `.crumbs/agent-summaries/_session-*/` but RULES.md/queen-state.md/skills/work.md use `.crumbs/sessions/_session-*/`. The old path was not propagated to these files. This is a cross-file drift issue. I'm reporting it as P2 under correctness (AC violation); you may want to capture the propagation angle."

**To: edge-cases-reviewer** (response to received message) — "Confirmed bash operator precedence bug at `skills/init.md:40` and `skills/init.md:43`. Same pattern affects java detection at L43. Bug introduced in commit range (commit 4429953). No AC citation from correctness side — skills/init.md is not scoped to any of the 15 task IDs. Not double-reporting; file it under your domain."

### Received

**From: edge-cases-reviewer** — Flagged bash operator precedence issue at `skills/init.md:L38-43`. `[ -f pyproject.toml ] || [ -f setup.py ] || [ -f requirements.txt ] && echo "python"` parses as `[ -f pyproject.toml ] || [ -f setup.py ] || ([ -f requirements.txt ] && echo "python")` — only requirements.txt presence triggers echo. Requested AC verification from correctness side.

---

## Coverage Log

All 34 scoped files reviewed. Files with no issues marked CLEAN.

| File | Status |
|------|--------|
| AGENTS.md | FINDINGS: F-001 (L12, L28), F-002 (L33), F-005 (L27-30) |
| agents/architect.md | CLEAN |
| agents/forager.md | CLEAN |
| agents/nitpicker.md | CLEAN |
| agents/scout-organizer.md | CLEAN |
| CLAUDE.md | FINDINGS: F-003 (L71) |
| CONTRIBUTING.md | CLEAN |
| docs/installation-guide.md | CLEAN |
| orchestration/reference/dependency-analysis.md | CLEAN |
| orchestration/RULES-decompose.md | CLEAN (bd references intentional — decomposition workflow retained) |
| orchestration/RULES-review.md | CLEAN |
| orchestration/RULES.md | CLEAN |
| orchestration/SETUP.md | CLEAN |
| orchestration/templates/architect-skeleton.md | CLEAN (bd references intentional — decomposition/Architect workflow) |
| orchestration/templates/big-head-skeleton.md | CLEAN |
| orchestration/templates/checkpoints.md | CLEAN |
| orchestration/templates/decomposition.md | CLEAN (bd references intentional — Architect workflow) |
| orchestration/templates/dirt-pusher-skeleton.md | CLEAN |
| orchestration/templates/forager-skeleton.md | CLEAN |
| orchestration/templates/forager.md | CLEAN |
| orchestration/templates/implementation.md | CLEAN |
| orchestration/templates/nitpicker-skeleton.md | CLEAN |
| orchestration/templates/pantry.md | CLEAN |
| orchestration/templates/queen-state.md | CLEAN |
| orchestration/templates/reviews.md | CLEAN |
| orchestration/templates/scout.md | CLEAN |
| orchestration/templates/scribe-skeleton.md | CLEAN |
| orchestration/templates/SESSION_PLAN_TEMPLATE.md | CLEAN |
| README.md | CLEAN |
| scripts/build-review-prompts.sh | CLEAN |
| scripts/setup.sh | FINDINGS: F-004 (L4 comment + missing CLAUDE.md sync) |
| skills/init.md | CLEAN |
| skills/plan.md | CLEAN |
| skills/status.md | CLEAN |
| skills/work.md | CLEAN |

**Note on out-of-scope bd references**: RULES-decompose.md, architect-skeleton.md, and decomposition.md contain `bd` commands. These are assessed as intentional — the decomposition/Planner/Architect workflow intentionally continues using the Beads CLI for trail and crumb creation. None of the 15 task IDs scoped any of these files for migration. These are NOT correctness findings.

---

## Overall Assessment

**Score**: 6/10

**Verdict**: NEEDS WORK

**Rationale**:

The migration from `bd` to `crumb` commands is largely successful across the 34 scoped files. The majority of templates, agent definitions, skills, and documentation are clean. The TDV checkpoint (ant-farm-veht) and exec-summary history (ant-farm-rue4) features are correctly implemented.

However, three issues block a clean PASS:

1. **P1 (F-001)**: `crumb sync` is documented in AGENTS.md at two locations as a required workflow command, but this command does not exist in crumb.py. Any agent following AGENTS.md session-completion instructions will encounter a command error. This is a runtime-breaking issue.

2. **P2 (F-002, F-003)**: The session artifact directory path `.crumbs/agent-summaries/_session-*/` was not updated in AGENTS.md or CLAUDE.md, while RULES.md and other authoritative sources use the correct `.crumbs/sessions/_session-*/` path.

3. **P2 (F-004)**: setup.sh, described as a replacement for sync-to-claude.sh, does not copy CLAUDE.md to `~/.claude/CLAUDE.md`. The ant-farm-ax38 requirement for keeping global CLAUDE.md in sync is not satisfied by setup.sh alone.

Total: 1 P1, 3 P2, 1 P3 across 3 root causes.

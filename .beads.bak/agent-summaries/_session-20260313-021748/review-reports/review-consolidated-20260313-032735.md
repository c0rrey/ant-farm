# Consolidated Review Report

**Session**: 20260313-021748
**Timestamp**: 20260313-032735
**Consolidator**: Big Head
**Review round**: 1
**Commit range**: 0ec9ed2^..HEAD

---

## Read Confirmation

| Report | Reviewer | Findings Count | Actionable |
|--------|----------|----------------|------------|
| clarity-review-20260313-032735.md | Clarity | 15 | 14 (1 cleared: F-009) |
| edge-cases-review-20260313-032735.md | Edge Cases | 15 | 15 |
| correctness-review-20260313-032735.md | Correctness | 14 | 14 |
| drift-review-20260313-032735.md | Drift | 7 | 7 |
| **Total** | | **51** | **50** |

All 4 reports read and inventoried.

---

## Root Cause Groups

### RC-1: Incomplete bd-to-crumb CLI migration in Architect executable templates (P1)

**Root cause**: The migration from `bd` to `crumb` CLI updated agent definition files and surrounding documentation but left the **executable** CLI command blocks in `decomposition.md`, `architect-skeleton.md`, and `RULES-decompose.md` using `bd trail create`, `bd create --from-json`, `bd dep add`, `bd show`, and `bd dolt` commands. The Architect agent reads and executes these templates directly. All `bd` commands will fail because `crumb` is the active CLI.

Additionally, `crumb create --from-json` takes an inline JSON string (not a file path like `bd`), so the usage pattern must change beyond the binary name. For `--type blocks`, the argument order inverts: `bd dep add {blocker} {blocked}` maps to `crumb link {blocked} --blocked-by {blocker}`.

**Affected surfaces**:
- `orchestration/templates/decomposition.md:115` — `bd trail create` in good-example block (Correctness F-08, Drift DRIFT-006)
- `orchestration/templates/decomposition.md:117` — `bd show` in good-example block (Correctness F-08, Drift DRIFT-006)
- `orchestration/templates/decomposition.md:208` — `bd trail create` in Step 7, **executed at runtime** (Correctness F-01, Drift DRIFT-006)
- `orchestration/templates/decomposition.md:265` — `bd create --from-json` with file path instead of inline JSON (Correctness F-02, Drift DRIFT-006)
- `orchestration/templates/decomposition.md:275` — `bd dep add --type parent-child` (Correctness F-03, Drift DRIFT-006)
- `orchestration/templates/decomposition.md:280` — `bd show` verification call (Correctness F-05, Drift DRIFT-006)
- `orchestration/templates/decomposition.md:287` — `bd dep add --type blocks` (Correctness F-04, Drift DRIFT-006)
- `orchestration/templates/decomposition.md:292-299` — `bd dolt` mode switching block, no crumb equivalent (Correctness F-06, Drift DRIFT-006)
- `orchestration/templates/decomposition.md:397` — `bd dep add` in prohibitions (Correctness F-07, Drift DRIFT-006)
- `orchestration/templates/architect-skeleton.md:77-80` — `bd` CLI commands in spawn prompt (Correctness F-09, Drift DRIFT-006)
- `orchestration/templates/architect-skeleton.md:111` — `bd dep add` in spawn prompt prohibitions (Correctness F-10, Drift DRIFT-006)
- `orchestration/RULES-decompose.md:20` — `bd show`, `bd ready`, `bd list`, `bd blocked` in prohibition list (Drift DRIFT-006, DRIFT-007)
- `orchestration/RULES-decompose.md:27` — "only the Architect does this via `bd` CLI" (Drift DRIFT-006)
- `orchestration/RULES-decompose.md:47` — table row references `bd` CLI (Drift DRIFT-006)
- `orchestration/RULES-decompose.md:108` — `bd show`, `bd list`, `bd trail status` in FORBIDDEN list (Drift DRIFT-006, DRIFT-007)
- `orchestration/RULES-decompose.md:287` — `bd dep add` in Architect capability summary (Correctness F-11, Drift DRIFT-006)
- `orchestration/RULES-decompose.md:289` — "Creates trails and crumbs via `bd` CLI" (Drift DRIFT-006)

**Highest severity**: P1 (Correctness, Drift)

**Canonical replacements** (from design spec at `docs/superpowers/specs/2026-03-12-crumbs-and-decomposition-design.md:534`):
- `bd trail create "..."` -> `crumb trail create --title "..."`
- `bd create --from-json file.json` -> `crumb create --from-json '{...}'` (inline JSON, not file path)
- `bd dep add {child} {parent} --type parent-child` -> `crumb link {child} --parent {parent}`
- `bd dep add {blocker} {blocked} --type blocks` -> `crumb link {blocked} --blocked-by {blocker}` (arg order inverts)
- `bd show {id}` -> `crumb show {id}`
- `bd dolt ...` -> no equivalent; entire dolt-mode warning block should be removed
- `bd list` / `bd trail status` / `bd ready` -> `crumb list` / `crumb trail list` / `crumb ready`

Remove the Dolt mode warning block (`decomposition.md:292-299`) entirely.

**Cross-session dedup**: No existing bead matches this root cause. Mark for filing.

---

### RC-2: DECOMPOSE_DIR path mismatch — .beads/ vs .crumbs/ (P1)

**Root cause**: The system migrated from `.beads/decompose/` to `.crumbs/sessions/` directory structure, but the migration was incomplete. `skills/plan.md` was updated to use `.crumbs/sessions/`; `orchestration/RULES-decompose.md` still uses `.beads/decompose/`. When the Planner runs, RULES-decompose.md overwrites the correct path set by the skill, causing all decomposition artifacts to be written to the wrong location.

**Affected surfaces**:
- `skills/plan.md:120` vs `orchestration/RULES-decompose.md:118` — path constant mismatch (Drift DRIFT-001)
- `orchestration/RULES-decompose.md:416,427` — directory tree diagram still shows `.beads/decompose/` (Drift DRIFT-001)
- `orchestration/templates/surveyor-skeleton.md:13`, `surveyor.md:15`, `forager.md:18`, `architect-skeleton.md:24`, `decomposition.md:11`, `agents/surveyor.md:23`, `agents/forager.md:22` — example paths show `.beads/decompose/` (Drift DRIFT-003)
- `orchestration/templates/forager-skeleton.md:18` — stale `SESSION_DIR`, `TASK_ID`, `TASK_SUFFIX` term definitions with `.beads/` paths (Drift DRIFT-002)

**Highest severity**: P1 (Drift)

**Suggested fix**: Update `RULES-decompose.md:118` to use `.crumbs/sessions/_decompose-${DECOMPOSE_ID}`. Update all 7 example paths in template term definitions from `.beads/decompose/` to `.crumbs/sessions/`. Remove stale `SESSION_DIR`/`TASK_ID`/`TASK_SUFFIX` definitions from `forager-skeleton.md`.

**Cross-session dedup**: No existing bead matches. Mark for filing.

---

### RC-3: Missing research/ subdirectory creation in plan skill (P2)

**Root cause**: `skills/plan.md:121` creates `DECOMPOSE_DIR` with `mkdir -p` but does NOT create the `research/` subdirectory. It then routes to `RULES-decompose.md` starting at Step 1, skipping Step 0 which contains the `research/` mkdir. Forager agents need `research/` to write output files. Some Foragers may self-heal (their error handling creates the directory), but this is not guaranteed.

**Affected surfaces**:
- `skills/plan.md:119-121` — mkdir missing `/research` (Correctness F-13, Drift DRIFT-004)

**Merge rationale**: Correctness F-13 and Drift DRIFT-004 describe the same gap from different angles. Correctness identifies the missing subdirectory; Drift identifies it as a consequence of the path migration. Same code path, same fix.

**Highest severity**: P2 (both reviewers agree)

**Suggested fix**: Change `mkdir -p "${DECOMPOSE_DIR}"` to `mkdir -p "${DECOMPOSE_DIR}/research"` in `skills/plan.md:121`.

**Cross-session dedup**: No existing bead matches. Mark for filing.

---

### RC-4: Shell operator-precedence bug in init skill language detection (P1)

**Root cause**: `skills/init.md` lines 40 and 43 use `||` and `&&` without grouping. Shell `&&` binds tighter than `||`, so `[ -f pyproject.toml ] || [ -f setup.py ] || [ -f requirements.txt ] && echo "python"` evaluates as `A || B || (C && echo)` instead of `(A || B || C) && echo`. Python projects using `pyproject.toml` or `setup.py` without `requirements.txt` are not detected. Same pattern for Java/`pom.xml`.

**Affected surfaces**:
- `skills/init.md:40` — Python detection (Correctness F-14, Clarity F-015)
- `skills/init.md:43` — Java detection (Correctness F-14)

**Merge rationale**: Clarity F-015 flagged the misleading code structure; Correctness F-14 flagged the logic error. Same two lines, same root cause (missing grouping).

**Highest severity**: P1 (Correctness)

**Suggested fix**:
```bash
{ [ -f pyproject.toml ] || [ -f setup.py ] || [ -f requirements.txt ]; } && echo "python"
{ [ -f pom.xml ] || [ -f build.gradle ]; } && echo "java"
```

**Cross-session dedup**: No existing bead matches. Mark for filing.

---

### RC-5: Misleading "both" prose annotation in architect-skeleton.md (P1)

**Root cause**: `architect-skeleton.md:82` states "The CHILD/BLOCKED crumb is the first argument in **both** dep-add patterns." The word "both" incorrectly extends the parent-child CHILD-first rule to `--type blocks`. The code example one line above shows BLOCKER first for `--type blocks`, and `decomposition.md:290` confirms "BLOCKER is the first argument." An agent reading only the prose would invert all `--type blocks` dependency wiring.

**Affected surfaces**:
- `orchestration/templates/architect-skeleton.md:82` (Clarity F-010)

**Highest severity**: P1 (Clarity)

**Note**: This finding overlaps with RC-1 (the `bd` CLI references in the same file), but the root cause is distinct. RC-1 is about the wrong CLI binary; RC-5 is about wrong argument-order documentation that would be wrong even after the CLI migration is complete. The fix for RC-1 (replacing `bd dep add` with `crumb link`) would eliminate the specific `bd dep add` syntax, but the prose annotation about argument order should still be corrected to prevent future confusion.

**Suggested fix**: Replace line 82 with: "For `--type parent-child`, the CHILD (crumb) is the first argument and the TRAIL (parent) is the second. For `--type blocks`, the BLOCKER is the first argument and the BLOCKED crumb is the second."

**Cross-session dedup**: No existing bead matches. Mark for filing.

---

### RC-6: Config schema mismatch in init skill (P2)

**Root cause**: `skills/init.md` generates `config.json` with `"counters": { "task": 1, "trail": 1 }`, but `crumb.py` reads `config.get("next_crumb_id", 1)` and `config.get("next_trail_id", 1)`. The `counters` key is ignored. No crash occurs due to fallback defaults, but the generated config is structurally wrong.

**Affected surfaces**:
- `skills/init.md:107-115` (Correctness F-12)

**Highest severity**: P2 (Correctness)

**Suggested fix**: Replace `"counters": { "task": 1, "trail": 1 }` with `"next_crumb_id": 1, "next_trail_id": 1`.

**Cross-session dedup**: No existing bead matches. Mark for filing.

---

### RC-7: Contradictory "follow exactly / except" structure in work.md (P2)

**Root cause**: `skills/work.md:115-128` says "Read `orchestration/RULES.md` and follow its workflow from Step 1 onward" and then immediately lists exceptions (crumb commands instead of bd). The "follow exactly" instruction contradicts the override list. Easy to miss the overrides and apply RULES.md literally.

**Affected surfaces**:
- `skills/work.md:115-128` (Clarity F-005)

**Highest severity**: P2 (Clarity)

**Suggested fix**: Restructure to: "Read `orchestration/RULES.md`. Follow its workflow, **EXCEPT** substitute the following crumbs-specific commands wherever RULES.md references `bd` equivalents: [list]."

**Cross-session dedup**: No existing bead matches. Mark for filing.

---

### RC-8: Inconsistent initialization guard in work.md (P2)

**Root cause**: `skills/work.md:24-26` checks only `tasks.jsonl` for initialization. `skills/init.md`, `skills/plan.md`, and `skills/status.md` all check both `tasks.jsonl` AND `config.json`. A partially initialized project (missing `config.json`) will pass the guard and fail later with unclear errors.

**Affected surfaces**:
- `skills/work.md:24-26` (Edge Cases EC-07)

**Highest severity**: P2 (Edge Cases)

**Suggested fix**: Check both files: `[ -f .crumbs/tasks.jsonl ] && [ -f .crumbs/config.json ]`.

**Cross-session dedup**: No existing bead matches. Mark for filing.

---

### RC-9: Shell script robustness gaps in setup.sh (P2)

**Root cause**: `scripts/setup.sh` lacks defensive handling for several shell edge cases: glob expansion with no matches (relies on coincidental counter check), `find` exit codes not handled under `set -e`, and `exit 1` vs `return 1` ambiguity in process substitution contexts.

**Affected surfaces**:
- `scripts/setup.sh:100` — glob expansion without `nullglob` (Edge Cases EC-01, P3)
- `scripts/setup.sh:149` — `find` exit code not handled (Edge Cases EC-02, P2)
- `scripts/setup.sh:67` — `exit 1` in function called from process substitution (Edge Cases EC-03, P2)

**Merge rationale**: All three share the pattern of relying on implicit shell behavior rather than explicit error handling in the same file's install loops.

**Highest severity**: P2 (Edge Cases)

**Suggested fix**: (1) Add `shopt -s nullglob` before agent glob. (2) Add post-loop check for `orchestration_installed > 0`. (3) Use `return 1` instead of `exit 1` in `backup_and_copy`.

**Cross-session dedup**: No existing bead matches. Mark for filing.

---

### RC-10: Heredoc/JSON injection via unsanitized user input in plan.md (P2)

**Root cause**: `skills/plan.md` constructs file content via heredocs and string interpolation without sanitizing user-supplied content. Heredoc delimiter collision and JSON injection from unescaped paths share the same lack of input sanitization.

**Affected surfaces**:
- `skills/plan.md:127-145` — heredoc delimiter collision risk with `SPEC_EOF` (Edge Cases EC-05, P2)
- `skills/plan.md:119-122` — JSON injection via unescaped `INPUT_SOURCE` (Edge Cases EC-06, P2)

**Merge rationale**: Same file, same pattern (user input interpolated into structured output without sanitization).

**Highest severity**: P2 (Edge Cases)

**Suggested fix**: Use `jq -n` for JSON construction. Use a more obscure heredoc delimiter or `printf '%s\n'` for text files.

**Cross-session dedup**: No existing bead matches. Mark for filing.

---

### RC-11: Silent failures in orchestration workflow — unverified agent actions (P2)

**Root cause**: Multiple points in the orchestration workflow rely on agents correctly performing actions (substituting placeholders, self-truncating output) without enforced verification. Failures produce incorrect results rather than errors.

**Affected surfaces**:
- `orchestration/RULES-decompose.md:127` — unsubstituted `{CODEBASE_ROOT}` causes silent greenfield misclassification (Edge Cases EC-09, P2)
- `orchestration/RULES-decompose.md:250` — Forager line cap has no enforcement mechanism (Edge Cases EC-10, P3)

**Note**: EC-13 (Dolt mode silent failure) was originally in this group but is subsumed by RC-1 — the entire Dolt warning block is vestigial `bd` code to be removed.

**Highest severity**: P2 (Edge Cases)

**Suggested fix**: Add a guard for `CODEBASE_ROOT` substitution. Add post-research `wc -l` truncation step.

**Cross-session dedup**: No existing bead matches. Mark for filing.

---

### RC-12: Empty feature request validation in surveyor.md (P2)

**Root cause**: The Surveyor's error handling says to return an error for empty feature requests, but the actual check is ambiguous — a blank line after the "Feature request:" header could pass a syntactic check.

**Affected surfaces**:
- `orchestration/templates/surveyor.md:367-375` (Edge Cases EC-12)

**Highest severity**: P2 (Edge Cases)

**Suggested fix**: Document an explicit whitespace-stripped emptiness check.

**Cross-session dedup**: No existing bead matches. Mark for filing.

---

### RC-13 (P3): Placeholder convention inconsistency in plan.md

**Affected surfaces**: Clarity F-002, F-003
**Cross-session dedup**: Matches ant-farm-8awb and ant-farm-0zws. **Skipped.**

### RC-14 (P3): Minor clarity/documentation issues

**Affected surfaces**: Clarity F-001, F-004, F-006, F-007, F-008, F-013, F-014
**Disposition**: P3 — Round 1, Queen handles.

### RC-15 (P3): Minor edge-case boundary conditions

**Affected surfaces**: Edge Cases EC-04, EC-08, EC-14, EC-15
**Disposition**: P3 — Round 1, Queen handles.

### RC-16 (P3): Silent directory auto-creation masks Planner bug

**Affected surfaces**: Edge Cases EC-11
**Disposition**: P3 — Round 1, Queen handles.

### RC-17 (P3): setup.sh / init skill responsibility boundary undocumented

**Affected surfaces**: Drift DRIFT-005
**Disposition**: P3 — Round 1, Queen handles.

---

## Severity Conflicts

No severity conflicts of 2+ levels exist between reviewers assessing the same root cause.

- RC-3 (Missing research/ subdirectory): Correctness P2, Drift P2 — agree.
- RC-4 (Operator precedence): Correctness P1, Clarity P3 — **but these are different aspects** (logic bug vs. readability). The clarity reviewer explicitly noted "flagged correctness angle separately" and did not assess the logic error. Not a calibration conflict.
- EC-13 vs Correctness F-06: Edge Cases P2 (enforcement gap) vs Correctness P1 (wrong CLI). Different root causes assessed independently — not a conflict.

---

## Deduplication Log

### Merged findings (same root cause):

| Consolidated RC | Merged Findings | Merge Rationale |
|----------------|-----------------|-----------------|
| RC-1 | Correctness F-01 through F-11, Drift DRIFT-006, DRIFT-007, Edge Cases EC-13 | All are `bd` CLI references left behind by incomplete migration. Correctness found the executable command blocks in decomposition.md and architect-skeleton.md. Drift DRIFT-006 adds 6 additional RULES-decompose.md surfaces (lines 20, 27, 47, 108, 287, 289) and the canonical replacement table from the design spec. DRIFT-007 (P3) adds the prohibition list naming stale commands. EC-13 is subsumed because the Dolt warning block is vestigial bd code. |
| RC-2 | Drift DRIFT-001, DRIFT-002, DRIFT-003 | All are `.beads/` path references left behind by the same directory migration |
| RC-3 | Correctness F-13, Drift DRIFT-004 | Same missing `research/` mkdir, identified from correctness and drift angles |
| RC-4 | Correctness F-14, Clarity F-015 | Same two lines — logic bug (correctness) and misleading structure (clarity) |
| RC-9 | Edge Cases EC-01, EC-02, EC-03 | Same file, same pattern: implicit shell behavior without explicit error handling |
| RC-10 | Edge Cases EC-05, EC-06 | Same file, same pattern: unsanitized user input in structured output |
| RC-11 | Edge Cases EC-09, EC-10 | Same pattern: instruction without enforcement in orchestration workflow |
| RC-13 | Clarity F-002, F-003 | Same file, same convention deviation |
| RC-14 | Clarity F-001, F-004, F-006, F-007, F-008, F-013, F-014 | Misc minor clarity issues |
| RC-15 | Edge Cases EC-04, EC-08, EC-14, EC-15 | Misc minor boundary conditions |

### Unmerged findings (unique root cause):

| Consolidated RC | Finding | Reason unmerged |
|----------------|---------|-----------------|
| RC-5 | Clarity F-010 | Distinct from RC-1 — wrong prose logic, not wrong CLI binary |
| RC-6 | Correctness F-12 | Unique schema mismatch |
| RC-7 | Clarity F-005 | Unique structural contradiction |
| RC-8 | Edge Cases EC-07 | Unique guard inconsistency |
| RC-12 | Edge Cases EC-12 | Unique validation gap |
| RC-17 | Drift DRIFT-005 | Unique documentation boundary |

### Cleared findings:
| Finding | Reason |
|---------|--------|
| Clarity F-009 | Resolved by Drift review — `decomposition.md:278` confirmed correct |

### Cross-session duplicates (skipped):
| RC | Matching Bead | Reason |
|----|---------------|--------|
| RC-13 | ant-farm-8awb, ant-farm-0zws | Placeholder convention inconsistency already tracked |

---

## Traceability Matrix

| Raw Finding | Source | Severity | Consolidated RC | Disposition |
|-------------|--------|----------|-----------------|-------------|
| Clarity F-001 | Clarity | P3 | RC-14 | P3 — Queen handles |
| Clarity F-002 | Clarity | P3 | RC-13 | Skipped (dedup: ant-farm-8awb) |
| Clarity F-003 | Clarity | P3 | RC-13 | Skipped (dedup: ant-farm-8awb) |
| Clarity F-004 | Clarity | P3 | RC-14 | P3 — Queen handles |
| Clarity F-005 | Clarity | P2 | RC-7 | File as P2 |
| Clarity F-006 | Clarity | P3 | RC-14 | P3 — Queen handles |
| Clarity F-007 | Clarity | P3 | RC-14 | P3 — Queen handles |
| Clarity F-008 | Clarity | P3 | RC-14 | P3 — Queen handles |
| Clarity F-009 | Clarity | CLEARED | — | Cleared by Drift review |
| Clarity F-010 | Clarity | P1 | RC-5 | File as P1 |
| Clarity F-011 | Clarity | P3 | RC-14 | P3 — Queen handles |
| Clarity F-012 | Clarity | P3 | RC-14 | P3 — Queen handles |
| Clarity F-013 | Clarity | P3 | RC-14 | P3 — Queen handles |
| Clarity F-014 | Clarity | P3 | RC-14 | P3 — Queen handles |
| Clarity F-015 | Clarity | P3 | RC-4 | Merged -> P1 |
| EC-01 | Edge Cases | P2 | RC-9 | File as P2 (merged) |
| EC-02 | Edge Cases | P2 | RC-9 | File as P2 (merged) |
| EC-03 | Edge Cases | P2 | RC-9 | File as P2 (merged) |
| EC-04 | Edge Cases | P3 | RC-15 | P3 — Queen handles |
| EC-05 | Edge Cases | P2 | RC-10 | File as P2 (merged) |
| EC-06 | Edge Cases | P2 | RC-10 | File as P2 (merged) |
| EC-07 | Edge Cases | P2 | RC-8 | File as P2 |
| EC-08 | Edge Cases | P3 | RC-15 | P3 — Queen handles |
| EC-09 | Edge Cases | P2 | RC-11 | File as P2 (merged) |
| EC-10 | Edge Cases | P3 | RC-11 | File as P2 (merged) |
| EC-11 | Edge Cases | P3 | RC-16 | P3 — Queen handles |
| EC-12 | Edge Cases | P2 | RC-12 | File as P2 |
| EC-13 | Edge Cases | P2 | RC-1 | Subsumed — Dolt block removed by RC-1 |
| EC-14 | Edge Cases | P3 | RC-15 | P3 — Queen handles |
| EC-15 | Edge Cases | P3 | RC-15 | P3 — Queen handles |
| Correctness F-01 | Correctness | P1 | RC-1 | File as P1 (merged) |
| Correctness F-02 | Correctness | P1 | RC-1 | File as P1 (merged) |
| Correctness F-03 | Correctness | P1 | RC-1 | File as P1 (merged) |
| Correctness F-04 | Correctness | P1 | RC-1 | File as P1 (merged) |
| Correctness F-05 | Correctness | P1 | RC-1 | File as P1 (merged) |
| Correctness F-06 | Correctness | P1 | RC-1 | File as P1 (merged) |
| Correctness F-07 | Correctness | P1 | RC-1 | File as P1 (merged) |
| Correctness F-08 | Correctness | P1 | RC-1 | File as P1 (merged) |
| Correctness F-09 | Correctness | P1 | RC-1 | File as P1 (merged) |
| Correctness F-10 | Correctness | P1 | RC-1 | File as P1 (merged) |
| Correctness F-11 | Correctness | P2 | RC-1 | File as P1 (merged, same migration gap) |
| Correctness F-12 | Correctness | P2 | RC-6 | File as P2 |
| Correctness F-13 | Correctness | P2 | RC-3 | File as P2 (merged with DRIFT-004) |
| Correctness F-14 | Correctness | P1 | RC-4 | File as P1 (merged with Clarity F-015) |
| DRIFT-001 | Drift | P1 | RC-2 | File as P1 |
| DRIFT-002 | Drift | P2 | RC-2 | File as P1 (merged) |
| DRIFT-003 | Drift | P2 | RC-2 | File as P1 (merged) |
| DRIFT-004 | Drift | P2 | RC-3 | File as P2 (merged with Correctness F-13) |
| DRIFT-005 | Drift | P3 | RC-17 | P3 — Queen handles |
| DRIFT-006 | Drift | P1 | RC-1 | File as P1 (merged — adds RULES-decompose.md:20,27,47,108,287,289 surfaces and canonical replacement table) |
| DRIFT-007 | Drift | P3 | RC-1 | File as P1 (merged — prohibition list naming stale bd commands, same root cause) |

**Raw count**: 51 findings in -> 17 root causes out
- 12 to file (4 P1, 8 P2)
- 1 cross-session dedup skip (RC-13)
- 4 P3 groups deferred to Queen (RC-14, RC-15, RC-16, RC-17)

---

## Priority Breakdown — Beads to File

| Priority | Count | RC IDs |
|----------|-------|--------|
| P1 | 4 | RC-1, RC-2, RC-4, RC-5 |
| P2 | 8 | RC-3, RC-6, RC-7, RC-8, RC-9, RC-10, RC-11, RC-12 |
| P3 | 0 | (deferred to Queen per round 1 rules) |
| **Total** | **12** | |

---

## Overall Verdict

**Score**: 5/10 — NEEDS WORK

The decomposition workflow has two blocking P1 issues: (1) the Architect's executable templates and Planner workflow still use `bd` CLI commands that do not exist in the active `crumb` CLI across 17+ affected lines in `decomposition.md`, `architect-skeleton.md`, and `RULES-decompose.md` (RC-1), and (2) RULES-decompose.md overwrites the correct `.crumbs/sessions/` path with a stale `.beads/decompose/` path (RC-2). Together, these mean any `/ant-farm:plan` invocation will fail. A third P1 (RC-4, shell operator-precedence in init language detection) silently breaks Python/Java detection for common project structures. A fourth P1 (RC-5, misleading prose annotation) would cause wrong dependency wiring even after CLI migration.

The 8 P2 findings are real and actionable but non-blocking — they cause degraded behavior, unclear errors, or injection risks rather than hard failures.

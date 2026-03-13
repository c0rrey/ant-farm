# Consolidated Review Report
**Session**: _session-20260313-021827
**Review round**: 1
**Timestamp**: 20260313-034951
**Consolidator**: Big Head

---

## Read Confirmation

| Report | Reviewer | Finding Count | Verdict |
|--------|----------|---------------|---------|
| clarity-review-20260313-034951.md | Clarity | 21 (0 P1, 3 P2, 18 P3) | PASS WITH ISSUES (7/10) |
| edge-cases-review-20260313-034951.md | Edge Cases | 16 (2 P1, 8 P2, 6 P3) | PASS WITH ISSUES (6.5/10) |
| correctness-review-20260313-034951.md | Correctness | 5 (1 P1, 3 P2, 1 P3) | NEEDS WORK (6/10) |
| drift-review-20260313-034951.md | Drift | 9 (0 P1, 6 P2, 3 P3) | PASS WITH ISSUES (7/10) |
| **Totals** | **4 reports** | **51 raw findings (3 P1, 20 P2, 28 P3)** | |

---

## Consolidated Findings by Root Cause

### RC-1: `crumb sync` referenced in AGENTS.md but does not exist in crumb.py
**Severity**: P1
**Sources**: Correctness F-001 (P1), Correctness F-005 (P3), Drift F7 (P3), Clarity F-03 (P3)

| Source | Finding | File:Line | Original Severity |
|--------|---------|-----------|-------------------|
| Correctness F-001 | `crumb sync` at AGENTS.md:12 and AGENTS.md:28 -- command does not exist | AGENTS.md:12, AGENTS.md:28 | P1 |
| Correctness F-005 | Landing-the-plane inconsistency between AGENTS.md and CLAUDE.md (secondary to F-001) | AGENTS.md:27-30 vs CLAUDE.md:65-69 | P3 |
| Drift F7 | `crumb sync` in AGENTS.md but absent from RULES.md push workflow | AGENTS.md:28 | P3 |
| Clarity F-03 | CLAUDE.md missing `crumb sync` compared to AGENTS.md | CLAUDE.md:38-39 | P3 |

**Merge rationale**: All four findings concern the same nonexistent `crumb sync` command. Correctness F-001 identifies the root cause (command does not exist in crumb.py). Correctness F-005 identifies the resulting inconsistency between AGENTS.md and CLAUDE.md. Drift F7 identifies the same inconsistency from the drift perspective (AGENTS.md vs RULES.md). Clarity F-03 notes CLAUDE.md is missing the step compared to AGENTS.md -- the real fix is removing it from AGENTS.md, not adding it to CLAUDE.md. All share the same code path: AGENTS.md:28 `crumb sync`.

**Affected surfaces**:
- `AGENTS.md:12` -- quick reference table lists `crumb sync`
- `AGENTS.md:28` -- landing-the-plane push block includes `crumb sync`

**Fix**: Remove `crumb sync` from AGENTS.md:12 (quick reference row) and AGENTS.md:28 (push block). Do NOT add it to CLAUDE.md or RULES.md -- the command does not exist.

**AC violation**: ant-farm-vjhe ("No broken links or references to removed Beads/Dolt tools")

**Cross-session dedup**: No matching existing bead found. File as new.

---

### RC-2: Stale SESSION_DIR path (`.crumbs/agent-summaries/_session-*` should be `.crumbs/sessions/_session-*`)
**Severity**: P2
**Sources**: Drift F1 (P2), Drift F2 (P2), Drift F3 (P2), Drift F4 (P2), Drift F5 (P2), Drift F6 (P2), Correctness F-002 (P2), Correctness F-003 (P2), Clarity F-02 (P3)

| Source | Finding | File:Line | Original Severity |
|--------|---------|-----------|-------------------|
| Drift F1 | Stale SESSION_DIR example path | dependency-analysis.md:49-51 | P2 |
| Drift F2 | Stale SESSION_DIR example path | dirt-pusher-skeleton.md:13 | P2 |
| Drift F3 | Stale SESSION_DIR example path | scout.md:14 | P2 |
| Drift F4 | Stale SESSION_DIR example path | scribe-skeleton.md:11 | P2 |
| Drift F5 | Stale session path in CLAUDE.md cleanup | CLAUDE.md:71 | P2 |
| Drift F6 | Stale session path in AGENTS.md cleanup | AGENTS.md:33 | P2 |
| Correctness F-002 | Stale session path in AGENTS.md | AGENTS.md:33 | P2 |
| Correctness F-003 | Stale session path in CLAUDE.md | CLAUDE.md:71 | P2 |
| Clarity F-02 | Session path inconsistency in AGENTS.md | AGENTS.md:33 | P3 |

**Merge rationale**: All 9 findings report the same stale value (`.crumbs/agent-summaries/_session-*`) in different files. The root cause is a single rename (to `.crumbs/sessions/_session-*`) that was applied to RULES.md, queen-state.md, and skills/work.md but not propagated to 6 other files. Drift F5/Correctness F-003 are the same finding (CLAUDE.md:71) from two reviewers. Drift F6/Correctness F-002/Clarity F-02 are the same finding (AGENTS.md:33) from three reviewers.

**Affected surfaces**:
- `orchestration/reference/dependency-analysis.md:49-51`
- `orchestration/templates/dirt-pusher-skeleton.md:13`
- `orchestration/templates/scout.md:14`
- `orchestration/templates/scribe-skeleton.md:11`
- `CLAUDE.md:71`
- `AGENTS.md:33`

**Fix**: Update all 6 files to use `.crumbs/sessions/_session-*` (or `_session-<session-id>` for example values). Re-run setup.sh to propagate CLAUDE.md changes to `~/.claude/CLAUDE.md`.

**AC violation**: ant-farm-vjhe (stale references), ant-farm-ax38 (CLAUDE.md sync)

**Cross-session dedup**: No matching existing bead found. File as new.

---

### RC-3: setup.sh does not copy CLAUDE.md to ~/.claude/CLAUDE.md
**Severity**: P2
**Sources**: Correctness F-004 (P2)

| Source | Finding | File:Line | Original Severity |
|--------|---------|-----------|-------------------|
| Correctness F-004 | setup.sh claims to replace sync-to-claude.sh but omits CLAUDE.md copy | scripts/setup.sh:4 | P2 |

**Merge rationale**: Single-source finding. No other reviewer flagged this specific gap.

**Affected surfaces**:
- `scripts/setup.sh` -- missing CLAUDE.md sync step

**Fix**: Add a step to setup.sh that copies `CLAUDE.md` to `~/.claude/CLAUDE.md` using the existing `backup_and_copy` pattern, or merge sync-to-claude.sh into setup.sh entirely.

**AC violation**: ant-farm-ax38 ("Global ~/.claude/CLAUDE.md: matching changes applied")

**Cross-session dedup**: Existing bead `ant-farm-hqfb` (P2) "Restore sync-to-claude.sh integration in pre-push hook" is related but addresses the pre-push hook, not setup.sh. The root cause differs (hook integration vs setup script scope). File as new.

---

### RC-4: Pantry placeholder contamination detection rule ambiguous for `{UPPERCASE}` patterns
**Severity**: P1
**Sources**: Edge Cases F-10 (P1)

| Source | Finding | File:Line | Original Severity |
|--------|---------|-----------|-------------------|
| Edge Cases F-10 | Condition 3 has ambiguous detection for `{UPPERCASE}` vs `<angle-bracket>` | pantry.md:44-89 | P1 |

**Merge rationale**: Single-source finding. The ambiguity is specific to the Pantry's fail-fast Condition 3 contamination check.

**Affected surfaces**:
- `orchestration/templates/pantry.md:44-89` -- fail-fast Condition 3

**Fix**: Clarify the contamination detection rule with a precise syntactic definition: only flag `<angle-bracket text>` patterns (starts with `<`, ends with `>`, word chars/spaces inside). Explicitly state `{UPPERCASE}` patterns are never contamination in metadata files. Add an example showing a task that references `{SESSION_DIR}` in its root cause field.

**Cross-session dedup**: Existing bead `ant-farm-3ysr` (P3) "Pantry guard edge cases: whitespace handling and contamination detection carve-out" is related but addresses a broader set of guard edge cases at P3. This finding is more specific and higher severity (P1 -- reliability gap in model-judgment check). File as new.

---

### RC-5: build-review-prompts.sh missing `-r` (readable) check on FOCUS_AREAS_FILE
**Severity**: P1
**Sources**: Edge Cases F-01 (P1), Clarity F-18 (P2)

| Source | Finding | File:Line | Original Severity |
|--------|---------|-----------|-------------------|
| Edge Cases F-01 | FOCUS_AREAS_FILE missing `-r` check; permission failure silently produces empty focus blocks | build-review-prompts.sh:149-153 | P1 |
| Clarity F-18 | FOCUS_AREAS_FILE path derivation is fragile and undocumented | build-review-prompts.sh:149-150 | P2 |

**Merge rationale**: Both findings concern the same code location (build-review-prompts.sh L149-153) and the same file reference (FOCUS_AREAS_FILE). Edge Cases F-01 identifies the missing `-r` check (the runtime failure mode). Clarity F-18 identifies the undocumented path derivation (the developer confusion). Same code path, same variable, same file.

**Affected surfaces**:
- `scripts/build-review-prompts.sh:149-153` -- FOCUS_AREAS_FILE validation

**Fix**: (1) Add `-r` check: `if [ ! -f "$FOCUS_AREAS_FILE" ] || [ ! -r "$FOCUS_AREAS_FILE" ]; then`. (2) Add comment explaining that `review-focus-areas.md` must be a sibling of `nitpicker-skeleton.md` in the templates directory.

**Cross-session dedup**: No matching existing bead found. File as new.

---

### RC-6: Shell script error propagation failure in build-review-prompts.sh (subshell exit code swallowing)
**Severity**: P2
**Sources**: Edge Cases F-02 (P2)

| Source | Finding | File:Line | Original Severity |
|--------|---------|-----------|-------------------|
| Edge Cases F-02 | resolve_arg exit in subshell silently swallowed | build-review-prompts.sh:74-86 | P2 |

**Merge rationale**: Single-source finding specific to `resolve_arg` function.

**Affected surfaces**:
- `scripts/build-review-prompts.sh:74-86` -- resolve_arg function

**Fix**: Check exit code after assignment: `CHANGED_FILES="$(resolve_arg "$CHANGED_FILES_RAW")" || { echo "ERROR: resolve_arg failed" >&2; exit 1; }`

**Cross-session dedup**: No matching existing bead found. File as new.

---

### RC-7: Temp file lifecycle management -- missing cleanup on error paths
**Severity**: P2
**Sources**: Edge Cases F-03 (P2), Edge Cases F-11 (P2)

| Source | Finding | File:Line | Original Severity |
|--------|---------|-----------|-------------------|
| Edge Cases F-03 | fill_slot temp file leak on awk failure | build-review-prompts.sh:168-202 | P2 |
| Edge Cases F-11 | open-crumbs temp file not cleaned up | big-head-skeleton.md:114-127 | P2 |

**Merge rationale**: Both findings share the same pattern: temp file created via mktemp or `$$`-based naming, no cleanup on error paths. Different files but identical root cause pattern (missing trap/cleanup).

**Affected surfaces**:
- `scripts/build-review-prompts.sh:168-202` -- fill_slot function
- `orchestration/templates/big-head-skeleton.md:114-127` -- cross-session dedup block

**Fix**: (1) In fill_slot: add `trap "rm -f '$tmpval'" RETURN`. (2) In big-head-skeleton.md: add `rm -f /tmp/open-crumbs-$$.txt` after dedup logic completes.

**Cross-session dedup**: Existing bead `ant-farm-8kds` (P3) "build-review-prompts.sh fill_slot temp file leak on awk failure" matches Edge Cases F-03. The big-head-skeleton F-11 component is new. Filing as new (covers both surfaces; note partial overlap with ant-farm-8kds).

---

### RC-8: setup.sh silent failure when find encounters permission errors
**Severity**: P2
**Sources**: Edge Cases F-04 (P2)

**Cross-session dedup**: Existing bead `ant-farm-li6e` (P2) "Shell script robustness gaps in setup.sh -- glob, find, exit/return" covers this root cause. **SKIPPED -- already filed.**

---

### RC-9: `{CODEBASE_ROOT}` template literal in executable shell block without substitution guidance
**Severity**: P2
**Sources**: Edge Cases F-06 (P2)

| Source | Finding | File:Line | Original Severity |
|--------|---------|-----------|-------------------|
| Edge Cases F-06 | find command uses literal `{CODEBASE_ROOT}` -- agent may run verbatim and get count=0 | RULES-decompose.md:127-143 | P2 |

**Merge rationale**: Single-source finding.

**Affected surfaces**:
- `orchestration/RULES-decompose.md:127-143` -- brownfield detection block

**Fix**: Add explicit note before the block: "Before running: substitute `{CODEBASE_ROOT}` with the absolute repo root path."

**Cross-session dedup**: No matching existing bead found. File as new.

---

### RC-10: Dolt mode switch in Architect workflow has no rollback on error
**Severity**: P2
**Sources**: Edge Cases F-07 (P2)

| Source | Finding | File:Line | Original Severity |
|--------|---------|-----------|-------------------|
| Edge Cases F-07 | Dolt mode switch with no rollback -- system left in embedded mode on failure | decomposition.md:292-300 | P2 |

**Merge rationale**: Single-source finding specific to the Architect's Dolt mode switch sequence.

**Affected surfaces**:
- `orchestration/templates/decomposition.md:292-300`

**Fix**: Wrap the embedded-mode sequence in error handling. Ensure `bd dolt set mode server && bd dolt start` runs even on `bd dep add` failures.

**Cross-session dedup**: No matching existing bead found. File as new.

---

### RC-11: Big-head-skeleton.md polling timeout value hardcoded separately from actual consolidation brief
**Severity**: P2
**Sources**: Edge Cases F-08 (P2)

| Source | Finding | File:Line | Original Severity |
|--------|---------|-----------|-------------------|
| Edge Cases F-08 | Polling timeout documented in skeleton may diverge from actual brief | big-head-skeleton.md:91-106 | P2 |

**Merge rationale**: Single-source finding.

**Affected surfaces**:
- `orchestration/templates/big-head-skeleton.md:91-106`

**Fix**: Source the timeout value from a single location (the consolidation brief template) instead of hardcoding in the skeleton.

**Cross-session dedup**: No matching existing bead found. File as new.

---

### RC-12: Scout continues with errored tasks in wave plan, producing potentially invalid conflict analysis
**Severity**: P2
**Sources**: Edge Cases F-09 (P2)

| Source | Finding | File:Line | Original Severity |
|--------|---------|-----------|-------------------|
| Edge Cases F-09 | crumb show failure tasks included in wave plans without complete data | scout.md:83-110 | P2 |

**Merge rationale**: Single-source finding.

**Affected surfaces**:
- `orchestration/templates/scout.md:83-110` (error handling), Steps 4-5 (conflict analysis, strategy proposals)

**Fix**: Scout should exclude errored tasks from wave 1 or at minimum warn that conflict analysis for error tasks is unreliable.

**Cross-session dedup**: No matching existing bead found. File as new.

---

### RC-13: work.md task count check includes trails, producing false negatives
**Severity**: P2
**Sources**: Edge Cases F-14 (P2)

| Source | Finding | File:Line | Original Severity |
|--------|---------|-----------|-------------------|
| Edge Cases F-14 | `crumb list --short | wc -l` includes trails in count | work.md:37-43 | P2 |

**Merge rationale**: Single-source finding.

**Affected surfaces**:
- `skills/work.md:37-43`

**Fix**: Filter to tasks only: `crumb list --type=task --short 2>/dev/null | wc -l`

**Cross-session dedup**: No matching existing bead found. File as new.

---

### RC-14: CLI tool naming inconsistency (crumb vs bd) never explained in user-facing docs
**Severity**: P2
**Sources**: Clarity F-01 (P2), Clarity F-09 (P3)

| Source | Finding | File:Line | Original Severity |
|--------|---------|-----------|-------------------|
| Clarity F-01 | `crumb` vs `bd` distinction unclear in AGENTS.md | AGENTS.md:3 | P2 |
| Clarity F-09 | RULES.md prohibitions use `crumb` while CLAUDE.md uses `bd` | RULES.md (prohibitions) | P3 |

**Merge rationale**: Both concern the same naming confusion between `crumb` and `bd`. Same root cause: two CLI names, no explanation of relationship.

**Affected surfaces**:
- `AGENTS.md:3`
- `orchestration/RULES.md` (prohibitions section)
- `CLAUDE.md` (parallel work mode prohibitions)

**Fix**: Add a brief note clarifying: `crumb` is the task-management CLI (installed from crumb.py); `bd` is the beads database CLI used in orchestration/decomposition workflows. Align prohibition language.

**Cross-session dedup**: No matching existing bead found. File as new.

---

### RC-15: Deprecated `pantry-review` row still in README.md custom agents table
**Severity**: P2
**Sources**: Clarity F-17 (P2)

**Cross-session dedup**: Existing beads `ant-farm-c1n2` / `ant-farm-4lcv` (P3) "README.md deprecated agent row inconsistently formatted" match this root cause. **SKIPPED -- already filed.**

---

### RC-16: docs/installation-guide.md inaccurate sync behavior and hook descriptions
**Severity**: P3
**Sources**: Clarity F-06 (P3), Clarity F-07 (P3), Drift F8 (P3)

| Source | Finding | File:Line | Original Severity |
|--------|---------|-----------|-------------------|
| Clarity F-06 | False claim about `rsync --delete` behavior | docs/installation-guide.md:66-67 | P3 |
| Clarity F-07 | Hook output filename reference inconsistent | docs/installation-guide.md:110-115 | P3 |
| Drift F8 | Pre-commit hook target filename mismatch | CONTRIBUTING.md:183 vs installation-guide.md:41 | P3 |

**Merge rationale**: All three concern inaccurate descriptions in the installation guide, arising from stale content after the sync-to-claude.sh to setup.sh migration. F-07 and F8 share the same underlying fact (wrong hook filename).

**Cross-session dedup**: No matching bead. P3 -- deferred to Queen per Round 1 protocol.

---

### RC-17: sync-to-claude.sh references not updated to setup.sh in documentation
**Severity**: P3
**Sources**: Drift F9 (P3)

**Cross-session dedup**: No matching bead. P3 -- deferred to Queen.

---

### RC-18: Stale reader comment in reviews.md references old script name
**Severity**: P3
**Sources**: Clarity F-15 (P3)

**Cross-session dedup**: No matching bead. P3 -- deferred to Queen.

---

### RC-19: Stale/deprecated content not clearly marked or removed
**Severity**: P3
**Sources**: Clarity F-14 (P3), Clarity F-16 (P3)

**Cross-session dedup**: Existing beads `ant-farm-bo7d`/`ant-farm-gl11` (P3) and `ant-farm-pxsk` (P3) match these findings. **SKIPPED -- already filed.**

---

### RC-20: build-review-prompts.sh undocumented sed regex
**Severity**: P3
**Sources**: Clarity F-19 (P3)

**Cross-session dedup**: No matching bead. P3 -- deferred to Queen.

---

### RC-21: Emoji usage inconsistency in implementation.md
**Severity**: P3
**Sources**: Clarity F-12 (P3), Clarity F-13 (P3)

**Cross-session dedup**: No matching bead. P3 -- deferred to Queen.

---

### RC-22: Standalone Clarity P3 findings
**Severity**: P3

| Source | Finding | File:Line | Cross-session dedup |
|--------|---------|-----------|-------------------|
| Clarity F-04 | Placeholder phase distinction unclear | CONTRIBUTING.md:104 | No match -- deferred |
| Clarity F-05 | Template inventory "Read by" column inconsistent | CONTRIBUTING.md:87-101 | No match -- deferred |
| Clarity F-08 | surveyor-skeleton.md reference missing from inventory | RULES-decompose.md:185 | No match -- deferred |
| Clarity F-10 | big-head-skeleton comment phrasing colloquial | big-head-skeleton.md:98 | SKIP -- matches ant-farm-9aj1 |
| Clarity F-11 | Historical note buried in operational section | checkpoints.md:38 | No match -- deferred |
| Clarity F-20 | setup.sh file comment inaccurate | setup.sh:9 | No match -- deferred |
| Clarity F-21 | DECOMPOSE_DIR path mismatch | skills/plan.md:119-146 | SKIP -- matches ant-farm-i9nt (P1) |

---

### RC-23: Standalone Edge Cases P3 findings
**Severity**: P3

| Source | Finding | File:Line | Cross-session dedup |
|--------|---------|-----------|-------------------|
| Edge Cases F-05 | PATH check locale/shell dependent | setup.sh:190-195 | No match -- deferred |
| Edge Cases F-12 | Bash operator precedence in init.md | skills/init.md:38-43 | SKIP -- matches ant-farm-7bn5 (P1) |
| Edge Cases F-13 | .gitignore update without permission check | skills/init.md:140-145 | No match -- deferred |
| Edge Cases F-15 | git rebase conflict no escalation path | implementation.md:59-61 | No match -- deferred |
| Edge Cases F-16 | RULES-review.md unset variable edge case | RULES-review.md:33-51 | No match -- deferred |

---

## Severity Conflicts

No severity conflicts (2+ level disagreements) were found across reviewers for the same root cause.

The closest case was RC-5 (FOCUS_AREAS_FILE): Edge Cases assessed P1, Clarity assessed P2. This is a 1-level difference, below the 2-level threshold for flagging.

---

## Deduplication Log

### Raw finding to consolidated root cause mapping

| Raw Finding | Consolidated RC | Action |
|-------------|----------------|--------|
| Correctness F-001 | RC-1 | Merged (4 findings -> 1 RC) |
| Correctness F-002 | RC-2 | Merged (9 findings -> 1 RC) |
| Correctness F-003 | RC-2 | Merged |
| Correctness F-004 | RC-3 | Standalone |
| Correctness F-005 | RC-1 | Merged |
| Drift F1 | RC-2 | Merged |
| Drift F2 | RC-2 | Merged |
| Drift F3 | RC-2 | Merged |
| Drift F4 | RC-2 | Merged |
| Drift F5 | RC-2 | Merged |
| Drift F6 | RC-2 | Merged |
| Drift F7 | RC-1 | Merged |
| Drift F8 | RC-16 | Merged |
| Drift F9 | RC-17 | Standalone |
| Clarity F-01 | RC-14 | Merged (2 findings -> 1 RC) |
| Clarity F-02 | RC-2 | Merged |
| Clarity F-03 | RC-1 | Merged |
| Clarity F-04 | RC-22 | Standalone P3 |
| Clarity F-05 | RC-22 | Standalone P3 |
| Clarity F-06 | RC-16 | Merged |
| Clarity F-07 | RC-16 | Merged |
| Clarity F-08 | RC-22 | Standalone P3 |
| Clarity F-09 | RC-14 | Merged |
| Clarity F-10 | RC-22 | Cross-session dedup (ant-farm-9aj1) |
| Clarity F-11 | RC-22 | Standalone P3 |
| Clarity F-12 | RC-21 | Merged (2 findings -> 1 RC) |
| Clarity F-13 | RC-21 | Merged |
| Clarity F-14 | RC-19 | Cross-session dedup (ant-farm-bo7d/gl11) |
| Clarity F-15 | RC-18 | Standalone P3 |
| Clarity F-16 | RC-19 | Cross-session dedup (ant-farm-pxsk) |
| Clarity F-17 | RC-15 | Cross-session dedup (ant-farm-c1n2/4lcv) |
| Clarity F-18 | RC-5 | Merged (2 findings -> 1 RC) |
| Clarity F-19 | RC-20 | Standalone P3 |
| Clarity F-20 | RC-22 | Standalone P3 |
| Clarity F-21 | RC-22 | Cross-session dedup (ant-farm-i9nt) |
| Edge Cases F-01 | RC-5 | Merged |
| Edge Cases F-02 | RC-6 | Standalone |
| Edge Cases F-03 | RC-7 | Merged (2 findings -> 1 RC) |
| Edge Cases F-04 | RC-8 | Cross-session dedup (ant-farm-li6e) |
| Edge Cases F-05 | RC-23 | Standalone P3 |
| Edge Cases F-06 | RC-9 | Standalone |
| Edge Cases F-07 | RC-10 | Standalone |
| Edge Cases F-08 | RC-11 | Standalone |
| Edge Cases F-09 | RC-12 | Standalone |
| Edge Cases F-10 | RC-4 | Standalone |
| Edge Cases F-11 | RC-7 | Merged |
| Edge Cases F-12 | RC-23 | Cross-session dedup (ant-farm-7bn5) |
| Edge Cases F-13 | RC-23 | Standalone P3 |
| Edge Cases F-14 | RC-13 | Standalone |
| Edge Cases F-15 | RC-23 | Standalone P3 |
| Edge Cases F-16 | RC-23 | Standalone P3 |

**Summary**: 51 raw findings -> 23 root causes. 3 RCs skipped (cross-session dedup). 3 individual findings within RCs also skipped (cross-session dedup). P3 RCs deferred to Queen per Round 1 protocol.

---

## Cross-Session Dedup Log

| Root Cause | Existing Bead | Action |
|------------|---------------|--------|
| RC-8 (setup.sh find failure) | ant-farm-li6e (P2) | SKIP -- already filed |
| RC-15 (deprecated pantry-review in README) | ant-farm-c1n2 / ant-farm-4lcv (P3) | SKIP -- already filed |
| RC-19 (stale/deprecated content) | ant-farm-bo7d / ant-farm-gl11 / ant-farm-pxsk (P3) | SKIP -- already filed |
| RC-22 Clarity F-21 (DECOMPOSE_DIR mismatch) | ant-farm-i9nt (P1) | SKIP -- already filed |
| RC-22 Clarity F-10 (big-head comment phrasing) | ant-farm-9aj1 (P3) | SKIP -- already filed |
| RC-23 Edge Cases F-12 (bash operator precedence) | ant-farm-7bn5 (P1) | SKIP -- already filed |

---

## Priority Breakdown (to file)

| Priority | Count | Root Causes |
|----------|-------|-------------|
| P1 | 3 | RC-1, RC-4, RC-5 |
| P2 | 9 | RC-2, RC-3, RC-6, RC-7, RC-9, RC-10, RC-11, RC-12, RC-13, RC-14 |
| P3 | 6 RCs | RC-16, RC-17, RC-18, RC-20, RC-21, RC-22/23 (deferred to Queen) |
| Skipped | 3 RCs + 3 findings | Cross-session duplicates |

Note: P2 count is 10 (RC-2, RC-3, RC-6, RC-7, RC-9, RC-10, RC-11, RC-12, RC-13, RC-14).

---

## Overall Verdict

**NEEDS WORK** -- 3 P1 root causes require fixes before the session can be considered clean.

- **RC-1** (P1): `crumb sync` does not exist -- runtime failure for any agent following AGENTS.md session completion
- **RC-4** (P1): Pantry placeholder contamination detection ambiguity -- reliability gap in fail-fast check
- **RC-5** (P1): FOCUS_AREAS_FILE missing `-r` check -- silent review quality degradation on permission failure

The P2 cluster is dominated by RC-2 (stale SESSION_DIR path in 6 files), which is a mechanical find-and-replace.

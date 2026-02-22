# Orchestration Framework Drift Audit

**Date:** 2026-02-21
**Scope:** RULES.md, orchestration/templates/*, orchestration/reference/*, CLAUDE.md, agents/*.md, scripts/*.sh, session artifacts
**Methodology:** 4 parallel audit agents performing systematic doc-vs-implementation cross-referencing across 8 domains

---

## Executive Summary

**Total findings: 32** (after deduplication from 39 raw findings across 4 agents)

| Severity | Count | Description |
|----------|-------|-------------|
| S1 (Breaking) | 4 | Following docs produces incorrect behavior |
| S2 (Misleading) | 15 | Docs create false mental model |
| S3 (Cosmetic) | 13 | Stale references, harmless gaps |

| Category | Count |
|----------|-------|
| Contradiction | 17 |
| Dead Doc | 9 |
| Undocumented | 6 |

---

## Findings Summary Table

| ID | Sev | Category | Summary |
|----|-----|----------|---------|
| DRIFT-001 | S1 | Contradiction | Scout frontmatter `model: sonnet` conflicts with RULES.md `model: opus` |
| DRIFT-002 | S1 | Contradiction | PC lacks Task tool but checkpoints.md says it spawns code-reviewer subagents |
| DRIFT-003 | S1 | Contradiction | Installed pre-push hook is fatal on sync failure; install-hooks.sh generates non-fatal hook |
| DRIFT-004 | S1 | Contradiction | WWD entirely absent in largest observed session despite docs requiring per-agent gate |
| DRIFT-005 | S2 | Dead Doc | SSV checkpoint omitted from RULES.md Model Assignments table |
| DRIFT-006 | S2 | Undocumented | `review-skeletons/` and `review-reports/` missing from Step 0 mkdir command |
| DRIFT-007 | S2 | Contradiction | CLAUDE.md Landing annotation "Corresponds to RULES.md Step 6" but content spans Steps 4-6 with gaps |
| DRIFT-008 | S2 | Contradiction | GLOSSARY says 4 checkpoints; checkpoints.md says 5; Hard Gates table has 7 rows |
| DRIFT-009 | S2 | Contradiction | CCO artifact naming: per-task in docs vs session-wide in practice |
| DRIFT-010 | S2 | Contradiction | DMVDC Nitpicker artifact naming: documented format differs from actual filenames |
| DRIFT-011 | S2 | Contradiction | CONTRIBUTING.md says rsync uses `--delete`; sync-to-claude.sh intentionally omits it |
| DRIFT-012 | S2 | Dead Doc | `orchestrator-state*.md` in Session Directory artifact list; never created in any session |
| DRIFT-013 | S2 | Dead Doc | `step3b-transition-gate.md` in Session Directory artifact list; never created in any session |
| DRIFT-014 | S2 | Dead Doc | `HANDOFF-*.md` in Session Directory artifact list; never created in any session |
| DRIFT-015 | S2 | Undocumented | One-TeamCreate-per-session constraint undocumented in RULES.md, CLAUDE.md, CONTRIBUTING.md |
| DRIFT-016 | S2 | Contradiction | README Nitpicker team shows 5 members; RULES.md requires 6 (adding Pest Control) |
| DRIFT-017 | S2 | Contradiction | Scout and Pantry models listed as `sonnet` in GLOSSARY and README; RULES.md assigns `opus` |
| DRIFT-018 | S2 | Undocumented | `{{REVIEW_ROUND}}` double-brace placeholder tier absent from PLACEHOLDER_CONVENTIONS.md |
| DRIFT-019 | S2 | Contradiction | Older sessions use wave-based artifact naming inconsistent with current documented convention |
| DRIFT-020 | S3 | Undocumented | `code-reviewer` is a custom agent type; docs do not clarify it is not a built-in |
| DRIFT-021 | S3 | Dead Doc | `pantry-review` appears in scout.md exclusion list; agent is archived |
| DRIFT-022 | S3 | Dead Doc | SESSION_PLAN_TEMPLATE.md references stale term "Boss-Bot" and model "Claude Sonnet 4.5" |
| DRIFT-023 | S3 | Undocumented | sync-to-claude.sh exclusions and non-delete policy not described in GLOSSARY |
| DRIFT-024 | S3 | Undocumented | `briefing.md` and `session-summary.md` absent from Session Directory artifact list |
| DRIFT-025 | S3 | Dead Doc | `_session-3be37d` referenced in MEMORY.md does not exist on disk |
| DRIFT-026 | S3 | Contradiction | `bd` prohibition wording differs slightly between CLAUDE.md and RULES.md |
| DRIFT-027 | S3 | Dead Doc | MEMORY.md Project Structure lists colony-tsa.md as "being eliminated"; file is archived |
| DRIFT-028 | S3 | Dead Doc | MEMORY.md "minimum file requirements still TBD" claim may be stale |
| DRIFT-029 | S3 | Dead Doc | CONTRIBUTING.md cross-file update checklist omits GLOSSARY.md |
| DRIFT-030 | S3 | Undocumented | Dummy reviewer prompt created in sessions but output report never appears |
| DRIFT-031 | S3 | Undocumented | fill-review-slots.sh `@file` prefix notation for multiline args not documented in RULES.md |
| DRIFT-032 | S3 | Undocumented | scrub-pii.sh / pre-commit hook not described in SETUP.md or README.md |

---

## Detailed Findings

### S1 — Breaking

---

### DRIFT-001: Scout frontmatter `model: sonnet` conflicts with RULES.md `model: opus`
- **Category**: CONTRADICTION
- **Severity**: S1
- **Intent**: Accidental
- **Source agents**: AE (finding A2-a)
- **Doc source**: `/Users/correy/projects/ant-farm/orchestration/RULES.md`:294 — `| Scout | Task (\`scout-organizer\`) | opus | Orchestration role |`
- **Impl source**: `/Users/correy/projects/ant-farm/agents/scout-organizer.md`:5 — `model: sonnet`
- **Additional surfaces**: The same model mismatch appears in GLOSSARY.md:80 (listed as sonnet; see DRIFT-017) and README.md:75 (see DRIFT-017). The frontmatter mismatch is the S1 concern; documentation-level contradictions across GLOSSARY and README are grouped under DRIFT-017 (S2).
- **Impact**: RULES.md Model Assignments table is the authoritative runtime reference. If the Queen supplies `model: "opus"` as instructed by RULES.md, the frontmatter is silently overridden — still a false mental model. If the Queen omits the model parameter (e.g., following a partial read of instructions), Claude Code loads the frontmatter value and the Scout runs as sonnet instead of opus. Either way the frontmatter actively misleads operators and any agent that inspects the file.
- **Suggested fix**: Update `agents/scout-organizer.md` frontmatter to `model: opus` to match the Model Assignments table. Optionally add a comment noting the Queen overrides this at spawn time anyway. Also apply the companion fixes in DRIFT-017 (GLOSSARY and README).

---

### DRIFT-002: Pest Control lacks Task tool but checkpoints.md says it spawns code-reviewer subagents
- **Category**: CONTRADICTION
- **Severity**: S1
- **Intent**: UNCERTAIN — may be aspirational design that was never implemented, or the "spawning" language may be misleading rather than literal
- **Source agents**: AE (finding A3), CD (finding C3)
- **Doc source**: `/Users/correy/projects/ant-farm/orchestration/templates/checkpoints.md`:17 — `"Pest Control is the orchestrator — the Queen spawns it to run a checkpoint. Pest Control then spawns a \`code-reviewer\` agent to execute the actual checks."` and repeated at lines 113, 191, 266, 339, 413, 504, 614: `**Agent type (spawned by Pest Control)**: \`code-reviewer\``
- **Impl source**: `/Users/correy/projects/ant-farm/agents/pest-control.md`:4 — `tools: Bash, Read, Write, Glob, Grep`
- **Additional surfaces**: The `Task` tool is absent from pest-control.md's tools list. The code-reviewer agent itself exists at `~/.claude/agents/code-reviewer.md` (not in the repo's `agents/` directory).
- **Impact**: Without the Task tool, Pest Control cannot spawn any subagent. Every checkpoint section in checkpoints.md describes a two-layer architecture (PC spawns code-reviewer) that is architecturally impossible given PC's tool permissions. In practice, Pest Control almost certainly executes checkpoint logic directly using its Bash/Read/Glob/Grep tools. An agent reading checkpoints.md literally will attempt a spawn and fail silently at the tool boundary. This creates a false mental model for anyone reading the documentation.
- **Suggested fix**: Pick one of two paths: (a) If Pest Control runs checks directly (the likely current reality), remove all "Pest Control spawns a code-reviewer" framing from checkpoints.md and replace with direct execution language. Update the "Pest Control Overview" section (lines 13-24) to describe PC as the executor, not the orchestrator. (b) If two-layer spawning is desired, add `Task` to pest-control.md's tools frontmatter and ensure code-reviewer.md is in the repo's `agents/` directory so sync-to-claude.sh deploys it.

---

### DRIFT-003: Installed pre-push hook is fatal on sync failure; install-hooks.sh generates non-fatal hook
- **Category**: CONTRADICTION
- **Severity**: S1
- **Intent**: Accidental — the installed hook appears to be an older version not regenerated after install-hooks.sh was updated
- **Source agents**: CD (finding D2)
- **Doc source**: `/Users/correy/projects/ant-farm/scripts/install-hooks.sh`:50-57 — the hook template wraps sync in a non-fatal check: `if ! "$SYNC_SCRIPT"; then echo "[ant-farm] WARNING: sync-to-claude.sh failed — push continuing without sync." ... fi` (sync failure prints warning but exits 0, allowing push to proceed)
- **Impl source**: `/Users/correy/projects/ant-farm/.git/hooks/pre-push`:11 — `"$SYNC_SCRIPT"` — the installed hook calls the sync script with `set -euo pipefail` active (line 2) and no error handling; any sync failure exits non-zero and blocks the push
- **Impact**: A developer pushing code will experience a blocked push if sync-to-claude.sh fails for any reason (disk full, permission error, rsync failure). The design intent documented in install-hooks.sh is that sync failure is non-fatal — the push should always succeed. The installed hook enforces the opposite policy. Running `./scripts/install-hooks.sh` would fix the installed hook, but until re-run, every push is at risk of being blocked by a sync error.
- **Suggested fix**: Re-run `./scripts/install-hooks.sh` to replace the installed hook with the current non-fatal version. Then add a note to CONTRIBUTING.md reminding contributors to re-run install-hooks.sh after pulling changes to that script.

---

### DRIFT-004: WWD entirely absent in largest observed session despite docs requiring per-agent gate
- **Category**: CONTRADICTION
- **Severity**: S1
- **Intent**: Accidental
- **Source agents**: B (finding B6)
- **Doc source**: `/Users/correy/projects/ant-farm/orchestration/RULES.md`:118-119 — `after each agent commits, spawn Pest Control (\`model: "haiku"\`) for Wandering Worker Detection (WWD) (scope check before next agent in the wave can proceed)` and `/Users/correy/projects/ant-farm/orchestration/templates/checkpoints.md`:264 — `**When**: After agent commits, BEFORE spawning next agent in same wave`
- **Impl source**: `/Users/correy/projects/ant-farm/.beads/agent-summaries/_session-7edaafbb/pc/` — zero WWD artifacts despite wave 1 having 7 agents across 26 tasks. No `*-wwd-*` files exist anywhere in the session directory. By contrast, `_session-068ecc83/pc/` contains 6 WWD files (per-task naming: `pc-oc9v-wwd-*`, `pc-6jxn-wwd-*`, `pc-n0or-wwd-*`, etc.) — but timing shows all three wave-1 commits occurred within 8 seconds and WWD artifacts appeared 47-78 seconds later, effectively batched rather than individually gated.
- **Impact**: The documentation states WWD is mandatory after every agent commit to prevent scope creep cascading. checkpoints.md cites a known failure mode (Epic 74g, agent 74g.6) where WWD would have caught a violation. In the largest observed session (30 tasks), WWD was entirely skipped. This is the highest-risk gap: the "before next agent in wave" blocking gate was not enforced. In session 068ecc83, WWD ran but timing shows per-agent serialization was not enforced for parallel commits.
- **Suggested fix**: Two fixes: (1) Add a note in RULES.md Step 3 clarifying that when agents commit roughly simultaneously in a parallel wave, WWD gates are run in batch after all commits — and this is acceptable. (2) Investigate why `_session-7edaafbb` has no WWD artifacts. If intentionally skipped for large waves, document the exception criteria. If accidentally skipped, flag as process violation and add enforcement guidance.

---

### S2 — Misleading

---

### DRIFT-005: SSV checkpoint omitted from RULES.md Model Assignments table
- **Category**: DEAD DOC
- **Severity**: S2
- **Intent**: Accidental
- **Source agents**: AE (finding A4), B (finding B4), CD (finding C1)
- **Doc source**: `/Users/correy/projects/ant-farm/orchestration/RULES.md`:288-304 — Model Assignments table covers Scout, Pantry (impl), Dirt Pushers, PC-CCO, PC-WWD, PC-DMVDC, PC-CCB, Nitpickers, Big Head, PC (team member), Fix Dirt Pushers. No row for `PC — SSV`.
- **Impl source**: `/Users/correy/projects/ant-farm/orchestration/RULES.md`:89 — `spawn Pest Control (\`pest-control\`, \`model: "haiku"\`) for Scout Strategy Verification (SSV)` and `/Users/correy/projects/ant-farm/orchestration/templates/checkpoints.md`:612 — `**Model**: \`haiku\` (pure set comparisons — no judgment required)`. Session artifact `_session-068ecc83/pc/pc-session-ssv-20260221-173632.md` confirms SSV runs in practice.
- **Additional surfaces**: The table header states "Every Task tool call the Queen makes MUST include the model parameter from this table" — an omitted entry is effectively dead documentation for anyone relying on the table alone.
- **Impact**: A Queen following the table to select models will find no SSV guidance and must hunt in Step 1b prose. The table is stated to be the authoritative reference, so an omitted entry leaves a gap.
- **Suggested fix**: Add a row between SSV and Pantry (impl): `| PC — SSV | Task (\`pest-control\`) | haiku | Pure set comparisons — no judgment required |`

---

### DRIFT-006: `review-skeletons/` and `review-reports/` missing from Step 0 mkdir command
- **Category**: UNDOCUMENTED
- **Severity**: S2
- **Intent**: Intentional (lazy creation by respective workflow phases) but undocumented
- **Source agents**: B (finding B1), FGH (finding F1a)
- **Doc source**: `/Users/correy/projects/ant-farm/orchestration/RULES.md`:336 — `mkdir -p "${SESSION_DIR}"/{task-metadata,previews,prompts,pc,summaries}`
- **Impl source**: `/Users/correy/projects/ant-farm/.beads/agent-summaries/_session-068ecc83/` and `_session-7edaafbb/` — both contain `review-reports/` and `review-skeletons/` directories not listed in the mkdir command. `review-reports/` present in 10/13 sessions; `review-skeletons/` in 6/13 sessions with reviews. `review-reports/` is created by `mkdir -p` at RULES.md line 175 (Step 3b-iii); `review-skeletons/` is created by `compose-review-skeletons.sh` (called by Pantry Section 1).
- **Impact**: The Step 0 Session Directory section implies the mkdir command is the complete setup. A reader has an incomplete mental model of the session directory structure and will be surprised when these directories appear later.
- **Suggested fix**: Add a note after RULES.md line 336: "Additional subdirectories are created during later phases: `review-skeletons/` — written by Pantry via compose-review-skeletons.sh (Step 2); `review-reports/` — created by `mkdir -p` at Step 3b-iii (line 175)."

---

### DRIFT-007: CLAUDE.md Landing annotation "Corresponds to RULES.md Step 6" spans Steps 4-6 with content gaps in both directions
- **Category**: CONTRADICTION
- **Severity**: S2
- **Intent**: Accidental
- **Source agents**: B (finding B10)
- **Doc source**: `/Users/correy/projects/ant-farm/CLAUDE.md`:54 — `(Corresponds to RULES.md Step 6.)` labels the entire 8-step Landing the Plane section as corresponding to RULES.md Step 6 only
- **Impl source**: `/Users/correy/projects/ant-farm/orchestration/RULES.md`:244-251 — Step 4 is documentation commit (CHANGELOG, README, CLAUDE.md); Step 5 is cross-reference verification; Step 6 is `git pull --rebase, bd sync, git push, clean up`
- **Additional surfaces**: CLAUDE.md's landing checklist covers material from RULES.md Steps 4, 5, and 6 but omits the CHANGELOG/README/CLAUDE.md documentation commit (RULES.md Step 4) and cross-reference verification (RULES.md Step 5) entirely. CLAUDE.md also adds steps with no RULES.md equivalents (file issues, quality gates, review-findings gate, issue status update, verify, hand off). RULES.md Step 6 lacks the `git status` verification present in CLAUDE.md.
- **Impact**: A Queen following CLAUDE.md's landing checklist would skip the CHANGELOG documentation commit (RULES.md Step 4) and cross-reference verification (RULES.md Step 5). The false cross-reference annotation creates confusion about which file is authoritative for the landing procedure.
- **Suggested fix**: Update CLAUDE.md line 54 to `(Corresponds to RULES.md Steps 4-6.)` and add the missing steps: a "Update documentation (CHANGELOG, README, CLAUDE.md in a single commit)" step and a "Verify cross-references" step between CLAUDE.md steps 3 and 4. Also add `git status` verification to RULES.md Step 6.

---

### DRIFT-008: GLOSSARY says 4 checkpoints; checkpoints.md says 5; Hard Gates table has 7 rows
- **Category**: CONTRADICTION
- **Severity**: S2
- **Intent**: Accidental — different documents updated at different times
- **Source agents**: CD (finding C4b)
- **Doc source**: `/Users/correy/projects/ant-farm/orchestration/GLOSSARY.md`:46 — `**checkpoint** | A mandatory verification gate that blocks the next phase of work until it returns PASS (or an approved WARN). There are four checkpoints: CCO, WWD, DMVDC, and CCB.` and GLOSSARY.md:64 — `All four checkpoints are executed by Pest Control.`
- **Impl source**: `/Users/correy/projects/ant-farm/orchestration/RULES.md`:255-263 — Hard Gates table lists SSV PASS, CCO PASS (impl), CCO PASS (review), WWD PASS, DMVDC PASS, CCB PASS, Reviews (7 rows); `/Users/correy/projects/ant-farm/orchestration/templates/checkpoints.md`:15 — `All checkpoint verifications (SSV, CCO, WWD, DMVDC, CCB) are executed by **Pest Control**` (5 checkpoints)
- **Impact**: The GLOSSARY is the stated single source of truth for term definitions. A reader using it as authoritative will be unaware of SSV and will not understand that CCO runs in two distinct configurations (impl vs. review). This is materially misleading: someone troubleshooting a failed gate using only the GLOSSARY will search for a checkpoint that was "never defined."
- **Suggested fix**: Update GLOSSARY.md's "checkpoint" definition to list all 5 checkpoints (SSV, CCO, WWD, DMVDC, CCB), note the CCO impl vs. review distinction, and update the "Checkpoint Acronyms" table to add SSV.

---

### DRIFT-009: CCO artifact naming: per-task in checkpoints.md vs session-wide in practice
- **Category**: CONTRADICTION
- **Severity**: S2
- **Intent**: UNCERTAIN — per-task spec may have been abandoned in favor of batch, or PC uses its own judgment
- **Source agents**: B (finding B4b)
- **Doc source**: `/Users/correy/projects/ant-farm/orchestration/templates/checkpoints.md`:179 — `\`{SESSION_DIR}/pc/pc-{TASK_SUFFIX}-cco-{timestamp}.md\`` and example at line 28: `pc-74g1-cco-20260215-001145.md`
- **Impl source**: `/Users/correy/projects/ant-farm/.beads/agent-summaries/_session-068ecc83/pc/pc-session-cco-20260221-133156.md` and `_session-7edaafbb/pc/pc-session-cco-20260220-221023.md` — both use `pc-session-cco-{timestamp}.md` (session-wide format). The RULES.md Hard Gates table (line 258) uses wildcard `${SESSION_DIR}/pc/*-cco-*.md` which matches the actual `pc-session-cco-*` pattern.
- **Impact**: checkpoints.md specifies per-task naming; actual files use session-wide naming. A future Pest Control agent following checkpoints.md literally would write per-task files — the wildcard gate would still match, but naming would be inconsistent. Anyone querying `pc/` for `*{TASK_SUFFIX}-cco-*` will find nothing.
- **Suggested fix**: Update checkpoints.md CCO Dirt Pushers section to document that when the Queen batches multiple prompts into one CCO run, the output should use `pc-session-cco-{timestamp}.md`. Update the per-task example on line 28 accordingly.

---

### DRIFT-010: DMVDC Nitpicker artifact naming: documented format differs from actual filenames
- **Category**: CONTRADICTION
- **Severity**: S2
- **Intent**: Accidental
- **Source agents**: CD (finding C5)
- **Doc source**: `/Users/correy/projects/ant-farm/orchestration/templates/checkpoints.md`:475 — `\`{SESSION_DIR}/pc/pc-{TASK_SUFFIX}-dmvdc-review-{timestamp}.md\`` and line 478 — `\`{TASK_SUFFIX}\`: Nitpicker task suffix (e.g., \`review-clarity\`, \`review-edge\`)`
- **Impl source**: `/Users/correy/projects/ant-farm/.beads/agent-summaries/_session-068ecc83/pc/` — actual files: `pc-review-correctness-dmvdc-20260221-182700.md`, `pc-review-edge-cases-dmvdc-20260221-182700.md`
- **Additional surfaces**: Two deviations from the documented format: (1) the trailing `-review` segment after `dmvdc` is absent in actual files; (2) the TASK_SUFFIX used is the bare review type (`correctness`, `edge-cases`) rather than the documented `review-{type}` compound (`review-clarity`, `review-edge`). Anyone querying `pc/` for `*dmvdc-review*` patterns will find zero matches.
- **Impact**: Queries against the documented pattern fail. The example values on line 478 (`review-clarity`, `review-edge`) also do not match actual practice (`correctness`, `edge-cases`).
- **Suggested fix**: Update checkpoints.md line 475 to match the actual convention: `\`pc-{review-type}-dmvdc-{timestamp}.md\``. Update line 478 example values to `correctness`, `edge-cases`, `clarity`, `excellence` to reflect actual Nitpicker task suffix values.

---

### DRIFT-011: CONTRIBUTING.md says rsync uses `--delete`; sync-to-claude.sh intentionally omits it
- **Category**: CONTRADICTION
- **Severity**: S2
- **Intent**: Accidental — CONTRIBUTING.md was not updated when the --delete flag was intentionally removed
- **Source agents**: CD (finding D1)
- **Doc source**: `/Users/correy/projects/ant-farm/CONTRIBUTING.md`:161 — `orchestration/` to `~/.claude/orchestration/` (via rsync \`--delete\`, excluding \`scripts/\`)`
- **Impl source**: `/Users/correy/projects/ant-farm/scripts/sync-to-claude.sh`:27 — `rsync -av --exclude='scripts/' --exclude='_archive/' "$REPO_ROOT/orchestration/" ~/.claude/orchestration/` — no `--delete` flag. Script comment at lines 24-25 explains this is intentional: omitting `--delete` preserves custom files adopters have placed under `~/.claude/orchestration/`.
- **Additional surfaces**: CONTRIBUTING.md also omits the `--exclude='_archive/'` exclusion that the script applies.
- **Impact**: A developer relying on CONTRIBUTING.md will falsely believe that deleting a source file causes it to be removed from `~/.claude/orchestration/` on next push. Stale templates from deleted source files remain active at runtime after sync. This is the opposite of documented behavior.
- **Suggested fix**: Update CONTRIBUTING.md line 161 to: `orchestration/` to `~/.claude/orchestration/` (via rsync without `--delete`, preserving any custom files; also excludes `scripts/` and `_archive/`).

---

### DRIFT-012: `orchestrator-state*.md` in Session Directory artifact list; never created in any session
- **Category**: DEAD DOC
- **Severity**: S2
- **Intent**: Accidental
- **Source agents**: FGH (finding F2/Finding-4)
- **Doc source**: `/Users/correy/projects/ant-farm/orchestration/RULES.md`:345 — `- \`orchestrator-state*.md\` — orchestrator snapshots`
- **Impl source**: `find /Users/correy/projects/ant-farm/.beads/agent-summaries/ -name "orchestrator-state*.md"` — no output across all 13 `_session-*` directories.
- **Impact**: Readers debugging or recovering a session expect to find orchestrator snapshots at this path. The file is never written by any current workflow step, making the artifact list entry misleading for recovery scenarios.
- **Suggested fix**: Remove the entry. If orchestrator state snapshots are desired, define the mechanism that creates them or replace this entry with `queen-state.md` (which has a template at `orchestration/templates/queen-state.md` and appears to be the intended artifact).

---

### DRIFT-013: `step3b-transition-gate.md` in Session Directory artifact list; never created in any session
- **Category**: DEAD DOC
- **Severity**: S2
- **Intent**: Accidental
- **Source agents**: FGH (finding F2/Finding-5)
- **Doc source**: `/Users/correy/projects/ant-farm/orchestration/RULES.md`:346 — `- \`step3b-transition-gate.md\` — review transition gate`
- **Impl source**: `find /Users/correy/projects/ant-farm/.beads/agent-summaries/ -name "step3b-transition-gate.md"` — no output across all 13 `_session-*` directories.
- **Impact**: The transition gate check is documented in RULES.md Step 3b (verify all agents completed, all DMVDC checks passed, git log shows expected commits) but produces no artifact. Anyone inspecting a session to verify the gate passed will find nothing.
- **Suggested fix**: Either write this file when the gate passes (`echo "PASS|$(date -u +%Y%m%dT%H%M%SZ)" > "${SESSION_DIR}/step3b-transition-gate.md"`) or remove the entry from the artifact list.

---

### DRIFT-014: `HANDOFF-*.md` in Session Directory artifact list; never created in any session
- **Category**: DEAD DOC
- **Severity**: S2
- **Intent**: Accidental
- **Source agents**: FGH (finding F2/Finding-6)
- **Doc source**: `/Users/correy/projects/ant-farm/orchestration/RULES.md`:347 — `- \`HANDOFF-*.md\` — handoff documents`
- **Impl source**: `find /Users/correy/projects/ant-farm/.beads/agent-summaries/ -name "HANDOFF-*.md"` — no output across all 13 `_session-*` directories. One session (`_session-8ae30b`) contains `EXECUTION_HANDOFF.md` at the top level — not a `HANDOFF-*.md` — suggesting an older workflow wrote this differently.
- **Impact**: Operators attempting to find handoff context from a past session will find nothing at the documented path pattern. The artifact list entry is entirely non-functional.
- **Suggested fix**: Remove the entry, or update it to reflect the actual artifact (e.g., `EXECUTION_HANDOFF.md` in `_session-8ae30b` suggests the file name that an earlier workflow used).

---

### DRIFT-015: One-TeamCreate-per-session constraint undocumented in RULES.md, CLAUDE.md, CONTRIBUTING.md
- **Category**: UNDOCUMENTED
- **Severity**: S2
- **Intent**: Accidental — constraint was captured in MEMORY.md but never propagated to operator-facing docs
- **Source agents**: FGH (finding G3b)
- **Doc source**: `/Users/correy/.claude/projects/-Users-correy-projects-ant-farm/memory/MEMORY.md`:19-21 — "Claude Code only supports one TeamCreate per session. The Nitpicker team (4 reviewers + Big Head) uses this slot. QA coordination (Pantry ↔ Pest Control) must use file-based handoff, not teams."
- **Impl source**: `grep -in "one team\|one TeamCreate\|team per session" /Users/correy/projects/ant-farm/orchestration/RULES.md` — no matches. Not mentioned in CLAUDE.md or CONTRIBUTING.md either.
- **Impact**: An operator extending the workflow (e.g., trying to create a second TeamCreate for a QA coordination team) will encounter a runtime failure with no prior warning in any authoritative doc. This constraint shapes the entire review architecture — why PC is a Nitpicker team member rather than spawned separately — but that rationale is invisible to anyone reading RULES.md.
- **Suggested fix**: Add a note to RULES.md Step 3b-iv: "Note: Claude Code supports only one TeamCreate per session. Pest Control is included as a team member (not spawned separately after the team completes) because a second TeamCreate for a standalone PC spawn would fail at runtime."

---

### DRIFT-016: README Nitpicker team shows 5 members; RULES.md requires 6 (Pest Control inside team)
- **Category**: CONTRADICTION
- **Severity**: S2
- **Intent**: Accidental — README was not updated when Pest Control was added as a team member
- **Source agents**: FGH (finding H1b)
- **Doc source**: `/Users/correy/projects/ant-farm/README.md`:59 — `│  the Nitpickers (4 reviewers + Big Head)                │` and line 218 — `├──create Nitpicker team (4 reviewers + Big Head)──►` and line 201 implies PC is spawned separately after the team completes
- **Impl source**: `/Users/correy/projects/ant-farm/orchestration/RULES.md`:179 — `Round 1: 6 members — 4 reviewers + Big Head + Pest Control` and line 182 — `Pest Control MUST be a team member so Big Head can SendMessage to it` and line 184 — `After team completes, DMVDC and CCB have already run inside the team`
- **Impact**: An operator following the README Step 3b flow diagram would spawn a 5-member team (4 reviewers + Big Head) and then separately spawn Pest Control. Per RULES.md, the correct architecture is a 6-member team with PC inside it. If the operator follows the README, Big Head cannot `SendMessage` to PC (they are not on the same team), breaking the team-internal DMVDC/CCB flow.
- **Suggested fix**: Update the README architecture diagram, Step 3b narrative, and flow diagram to reflect: 6-member Nitpicker team (4 reviewers + Big Head + Pest Control); DMVDC and CCB run inside the team; the Queen does NOT spawn a separate PC after the team completes.

---

### DRIFT-017: Scout and Pantry models listed as `sonnet` in GLOSSARY and README; RULES.md assigns `opus`
- **Category**: CONTRADICTION
- **Severity**: S2
- **Intent**: Accidental — GLOSSARY and README were not updated when Scout and Pantry were promoted from sonnet to opus
- **Source agents**: AE (findings A2-b, A2-c), FGH (finding H1a)
- **Doc source (Scout — GLOSSARY)**: `/Users/correy/projects/ant-farm/orchestration/GLOSSARY.md`:80 — `| **Scout** | \`agents/scout-organizer.md\` | sonnet | Pre-flight reconnaissance agent. |`
- **Doc source (Pantry — GLOSSARY)**: `/Users/correy/projects/ant-farm/orchestration/GLOSSARY.md`:81 — `| **Pantry** | \`agents/pantry-impl.md\` ... | sonnet | Prompt composition agent. |`
- **Doc source (Scout — README)**: `/Users/correy/projects/ant-farm/README.md`:75 — `a sonnet subagent that performs all pre-flight reconnaissance`
- **Impl source**: `/Users/correy/projects/ant-farm/orchestration/RULES.md`:294-295 — `| Scout | Task (\`scout-organizer\`) | opus | Orchestration role |` and `| Pantry (impl) | Task (\`pantry-impl\`) | opus | Prompt composition + review skeleton assembly (Script 1) |`
- **Additional surfaces**: The Scout frontmatter contradiction (agents/scout-organizer.md says `model: sonnet`) is the S1 issue covered by DRIFT-001. This finding covers the documentation-level surfaces only (GLOSSARY and README).
- **Impact**: A reader building a mental model from GLOSSARY or README will assume Scout and Pantry run on sonnet. When they observe the Queen's tool calls using `model: "opus"` for both, it contradicts their expectations. The GLOSSARY is stated to be the single source of truth for role definitions.
- **Suggested fix**: Update GLOSSARY.md line 80 Scout row to `opus`. Update GLOSSARY.md line 81 Pantry row to `opus` (implementation mode). Update README.md line 75 from "a sonnet subagent" to "an opus subagent."

---

### DRIFT-018: `{{REVIEW_ROUND}}` double-brace placeholder tier absent from PLACEHOLDER_CONVENTIONS.md
- **Category**: UNDOCUMENTED
- **Severity**: S2
- **Intent**: Intentional usage (explained inline in reviews.md) but undocumented in the conventions file
- **Source agents**: AE (finding E1/E2)
- **Doc source**: `/Users/correy/projects/ant-farm/orchestration/PLACEHOLDER_CONVENTIONS.md` — defines three tiers: `{UPPERCASE}` (Tier 1), `{lowercase-kebab}` (Tier 2), `${SHELL_VAR}` (Tier 3). No mention of `{{double-brace}}` syntax. The File-by-File Audit table marks `reviews.md` as PASS with "None (uses angle-bracket syntax...)" — inaccurate.
- **Impl source**: `/Users/correy/projects/ant-farm/orchestration/templates/reviews.md`:502 — `REVIEW_ROUND={{REVIEW_ROUND}}` and line 592 — `fill-review-slots.sh substitutes \`{{REVIEW_ROUND}}\` with the actual round integer before delivering this brief to Big Head.`
- **Impact**: `{{REVIEW_ROUND}}` is a fourth placeholder tier substituted by `fill-review-slots.sh` (a shell script), not by the Queen. This is a distinct substitution mechanism. A template author extending reviews.md would not know this fourth tier exists, how it works, or that the File-by-File Audit table's `reviews.md` PASS result is inaccurate (it incorrectly states there are no curly-brace placeholders).
- **Suggested fix**: Add a "Tier 4: Script-Substituted (`{{DOUBLE_BRACE}}`)" entry to PLACEHOLDER_CONVENTIONS.md explaining these are filled by `fill-review-slots.sh` before delivery. Update the File-by-File Audit table row for reviews.md to acknowledge the double-brace tier and mark it correctly.

---

### DRIFT-019: Older sessions use wave-based artifact naming inconsistent with current documented convention
- **Category**: CONTRADICTION
- **Severity**: S2
- **Intent**: Accidental — artifact of pre-task-suffix era
- **Source agents**: CD (findings C2a, C2b)
- **Doc source**: `/Users/correy/projects/ant-farm/orchestration/templates/checkpoints.md`:27-33 — task-specific checkpoints (CCO, WWD, DMVDC for Dirt Pushers) use `pc-{TASK_SUFFIX}-{checkpoint}-{timestamp}.md`; session-wide checkpoints (SSV, CCO-review, CCB) use `pc-session-{checkpoint}-{timestamp}.md`. Line 39: timestamp format `YYYYMMDD-HHmmss` (UTC).
- **Impl source (session 7edaafbb)**: `_session-7edaafbb/pc/` — `pc-session-dmvdc-20260221-034922.md`, `pc-session-dmvdc-20260221-042058.md`, `pc-wave2-dmvdc-20260221-040754.md`, `pc-session-dmvdc-review-fixes-20260221-043218.md` — session-scoped and wave-based naming for DMVDC artifacts. **Impl source (session cd9866)**: `_session-cd9866/pc/` — `pc-session-cco-impl-wave1.md`, `pc-session-cco-impl-wave2.md`, `pc-session-dmvdc-wave1.md`, `pc-session-dmvdc-wave2.md`, `pc-session-wwd-wave1.md`, `pc-session-wwd-wave2.md` — wave-based suffix with no timestamp, session-scoped for all checkpoint types.
- **Impact**: `_session-cd9866` violates both current conventions (task-suffix scoping and timestamp format); `_session-7edaafbb` violates task-suffix scoping for DMVDC artifacts. The most recent session (`_session-068ecc83`) follows the documented pattern correctly. Historical sessions cannot be audited by the current documented convention.
- **Suggested fix**: No change to current docs needed — current docs reflect the correct target convention. Add a note in checkpoints.md that sessions prior to `_session-068ecc83` used wave-based naming, documenting the transition point for historical reference.

---

### S3 — Cosmetic

---

### DRIFT-020: `code-reviewer` is a custom agent type; docs do not clarify it is not a built-in
- **Category**: UNDOCUMENTED
- **Severity**: S3
- **Intent**: Accidental
- **Source agents**: AE (finding A5)
- **Doc source**: `/Users/correy/projects/ant-farm/orchestration/templates/checkpoints.md`:17 — `"Pest Control then spawns a \`code-reviewer\` agent to execute the actual checks."` No clarification on whether `code-reviewer` is built-in or custom.
- **Impl source**: `/Users/correy/.claude/agents/code-reviewer.md`:1-6 — custom agent file in the user's global `~/.claude/agents/`. Not in the ant-farm repo's `agents/` directory. The Agent Types table in RULES.md lines 278-286 does not list `code-reviewer`.
- **Impact**: `code-reviewer` is not a built-in Claude Code type. A reader assuming it is built-in may be confused when it does not exist in a fresh environment. Because it is in `~/.claude/agents/` rather than the repo's `agents/`, sync-to-claude.sh does not deploy it — new adopters on a fresh machine would not have this agent. (Note: the spawning architecture described in checkpoints.md is itself contradicted by DRIFT-002.)
- **Suggested fix**: If the two-layer spawn architecture in checkpoints.md is retained, add a note clarifying that `code-reviewer` is a custom agent that must be present in `~/.claude/agents/`. Consider moving it into the repo's `agents/` directory so sync-to-claude.sh handles deployment. Also add it to the Agent Types table in RULES.md.

---

### DRIFT-021: `pantry-review` appears in scout.md exclusion list; agent is archived
- **Category**: DEAD DOC
- **Severity**: S3
- **Intent**: Accidental — exclusion list was not updated when pantry-review was archived
- **Source agents**: AE (finding A6)
- **Doc source**: `/Users/correy/projects/ant-farm/orchestration/templates/scout.md`:63 — `scout-organizer, pantry-impl, pantry-review, pest-control, nitpicker, big-head`
- **Impl source**: No `agents/pantry-review.md` exists in the repo. The file is at `/Users/correy/projects/ant-farm/orchestration/_archive/pantry-review.md` (archived) and `~/.claude/agents/pantry-review.md` (stale global copy).
- **Additional surfaces**: GLOSSARY.md lines 28 and 81 use strikethrough markup (`~~pantry-review.md~~`) with "(deprecated; see RULES.md Step 3b)" annotations — intentional and correct. `pantry.md` line 256 warns "Do NOT spawn `pantry-review` for a second invocation" — correct. `reviews.md` line 1 says "replaces pantry-review" — informational and correct. Only the scout.md exclusion list reference is problematic.
- **Impact**: Because `pantry-review` has no agent file in `agents/`, it would not appear in the Scout's catalog anyway. The reference is harmless but signals the exclusion list was not updated on deprecation. A Scout reading its own instructions sees a reference to a non-existent agent.
- **Suggested fix**: Remove `pantry-review` from the exclusion list in `orchestration/templates/scout.md` line 63.

---

### DRIFT-022: SESSION_PLAN_TEMPLATE.md references stale term "Boss-Bot" and model "Claude Sonnet 4.5"
- **Category**: DEAD DOC
- **Severity**: S3
- **Intent**: Accidental — template predates the renaming of the orchestrator role from "Boss-Bot" to "the Queen"
- **Source agents**: AE (finding E4), FGH (finding H3/Finding-11)
- **Doc source**: `/Users/correy/projects/ant-farm/orchestration/templates/SESSION_PLAN_TEMPLATE.md`:8 — `**Boss-Bot:** Claude Sonnet 4.5`; line 340 — `- Implementation files read in boss-bot window: ___ (target: <10)`; line 342 — `- Boss-bot stayed focused: ✅ / ❌`
- **Impl source**: `/Users/correy/projects/ant-farm/orchestration/GLOSSARY.md`:79 and RULES.md throughout — the orchestrator role is "Queen." "Boss-Bot" appears nowhere in GLOSSARY.md, RULES.md, or any active template. Current model tier for the orchestrator is `opus` per RULES.md; `Claude Sonnet 4.5` is both a stale model name and the wrong tier.
- **Impact**: A user copying this template to plan a new session will see undefined terminology ("Boss-Bot" has no GLOSSARY entry) and a stale model name. The term maps to the Queen but creates confusion for anyone cross-referencing with GLOSSARY.md.
- **Suggested fix**: Replace all instances of "Boss-Bot" / "boss-bot" with "Queen" / "the Queen." Replace "Claude Sonnet 4.5" with the generic tier `opus` or point readers to the RULES.md Model Assignments table. Consider moving SESSION_PLAN_TEMPLATE.md to `_archive/` if it is no longer used as an active template (the Scout now generates briefing.md automatically).

---

### DRIFT-023: sync-to-claude.sh exclusions and non-delete policy not described in GLOSSARY
- **Category**: UNDOCUMENTED
- **Severity**: S3
- **Intent**: Accidental — GLOSSARY entry is a summary, not a specification
- **Source agents**: AE (pre-identified #12 partial confirmation)
- **Doc source**: `/Users/correy/projects/ant-farm/orchestration/GLOSSARY.md`:58 — `**pre-push hook** | ... syncs \`agents/*.md\` to \`~/.claude/agents/\` and \`orchestration/\` files to \`~/.claude/orchestration/\`` — does not mention: the `_archive/` exclusion, that only 2 of 6 scripts are synced, the CLAUDE.md sync, or the non-delete policy.
- **Impl source**: `/Users/correy/projects/ant-farm/scripts/sync-to-claude.sh`:23-44 — inline comments document the full sync behavior including exclusions and non-delete rationale.
- **Impact**: A developer relying on the GLOSSARY for a complete understanding of what sync-to-claude.sh does will not know about the selective script sync, archive exclusion, or the preservation policy for custom files. The gaps are documented inline in the script itself but not surfaced in the GLOSSARY. Cosmetic only since sync behavior is not a decision-making input at runtime.
- **Suggested fix**: Expand the GLOSSARY `pre-push hook` entry to note: the `_archive/` exclusion, that only `fill-review-slots.sh` and `compose-review-skeletons.sh` (not all 6 scripts) are synced, the CLAUDE.md copy step, and the non-delete policy preserving custom files.

---

### DRIFT-024: `briefing.md` and `session-summary.md` absent from Session Directory artifact list
- **Category**: UNDOCUMENTED
- **Severity**: S3
- **Intent**: Accidental
- **Source agents**: FGH (finding F1b)
- **Doc source**: `/Users/correy/projects/ant-farm/orchestration/RULES.md`:343-349 — artifact list includes `queen-state.md`, `orchestrator-state*.md`, `step3b-transition-gate.md`, `HANDOFF-*.md`, `progress.log`, `resume-plan.md`. Does not mention `briefing.md` or `session-summary.md`.
- **Impl source**: All 13 `_session-*` directories contain `briefing.md` (written by Scout; referenced in RULES.md lines 86 and 99 but not in the artifact list). `session-summary.md` appears in 5 sessions and is documented in `orchestration/templates/pantry.md`:184 but not in RULES.md.
- **Impact**: The artifact list is incomplete. Someone reading it would not know these two commonly-present files exist or what created them.
- **Suggested fix**: Add to RULES.md lines 343-349: `- \`briefing.md\` — pre-flight recon report written by Scout (Step 1a)` and `- \`session-summary.md\` — session completion summary written by Pantry (optional)`.

---

### DRIFT-025: `_session-3be37d` referenced in MEMORY.md does not exist on disk
- **Category**: DEAD DOC
- **Severity**: S3
- **Intent**: Accidental — the referenced session was the one that was accidentally deleted, hence its absence
- **Source agents**: FGH (finding F4)
- **Doc source**: `/Users/correy/.claude/projects/-Users-correy-projects-ant-farm/memory/MEMORY.md`:51 — "The global `~/.claude/CLAUDE.md` was synced to match in session 3be37d after accidentally deleting a session directory."
- **Impl source**: The 13 actual `_session-*` directories do not include `_session-3be37d`. The absence is consistent with it being the session that was deleted.
- **Impact**: Non-recoverable historical pointer. The MEMORY.md entry is correct as a narrative record but points to a session that does not exist. Cosmetic only.
- **Suggested fix**: No action required — the entry is a historical note. Optionally annotate: "(this session directory was the one that was accidentally deleted — absence is expected)."

---

### DRIFT-026: `bd` prohibition wording differs slightly between CLAUDE.md and RULES.md
- **Category**: CONTRADICTION
- **Severity**: S3
- **Intent**: Accidental — likely copy drift over time
- **Source agents**: FGH (finding G2)
- **Doc source (CLAUDE.md)**: `/Users/correy/projects/ant-farm/CLAUDE.md`:38 — `- NEVER run \`bd show\`, \`bd ready\`, \`bd list\`, \`bd blocked\`, or any \`bd\` query command. The Scout subagent does this.`
- **Doc source (RULES.md)**: `/Users/correy/projects/ant-farm/orchestration/RULES.md`:16 — `- **NEVER** run \`bd show\`, \`bd ready\`, \`bd list\`, \`bd blocked\`, or any \`bd\` query command — the Scout does this`
- **Impact**: Functionally identical — both enumerate the same four commands and include the "any bd query command" catch-all. Differences are formatting (`**NEVER**` vs `NEVER`) and attribution ("The Scout subagent does this." vs "the Scout does this"). Not a breaking difference.
- **Suggested fix**: Normalize wording across both files. Prefer CLAUDE.md's more explicit phrasing: "The Scout subagent does this."

---

### DRIFT-027: MEMORY.md Project Structure lists colony-tsa.md as "being eliminated" when already archived
- **Category**: DEAD DOC
- **Severity**: S3
- **Intent**: Accidental — the "Completed: Colony TSA Eliminated" section below correctly records completion, but the "Project Structure" section was never updated
- **Source agents**: FGH (finding G3a)
- **Doc source**: `/Users/correy/.claude/projects/-Users-correy-projects-ant-farm/memory/MEMORY.md`:28 — `- \`orchestration/templates/colony-tsa.md\` — Colony TSA (being eliminated, see HANDOFF)`
- **Impl source**: No `orchestration/templates/colony-tsa.md` exists. The file is at `/Users/correy/projects/ant-farm/orchestration/_archive/colony-tsa.md` (confirmed archived).
- **Impact**: The "Project Structure" section of MEMORY.md still shows colony-tsa.md at its old path as an active file "being eliminated." A reader who consults this section before reading the "Completed" section below it will have a false picture of the current state.
- **Suggested fix**: Update the "Project Structure" section to read: `orchestration/_archive/colony-tsa.md — Colony TSA (archived; replaced by direct Queen → Pest Control spawns)`.

---

### DRIFT-028: MEMORY.md "minimum file requirements still TBD" claim may be stale
- **Category**: DEAD DOC
- **Severity**: S3
- **Intent**: Accidental
- **Source agents**: FGH (finding G3c)
- **Doc source**: `/Users/correy/.claude/projects/-Users-correy-projects-ant-farm/memory/MEMORY.md`:17 — "Minimum file requirements still TBD — short files (9 lines) failed while full-body agents (200+ lines) work. Needs more testing to find the threshold."
- **Impl source**: `/Users/correy/projects/ant-farm/CONTRIBUTING.md`:33-35 — "Claude Code loads agent files once at startup. Adding or editing an agent file requires a full quit and reopen of Claude Code." The "minimum file requirements TBD" caveat is absent from CONTRIBUTING.md.
- **Impact**: If the threshold was discovered and file size is no longer an issue, MEMORY.md is misleading. If still unknown, CONTRIBUTING.md is missing a useful warning. Current state is unclear.
- **Suggested fix**: Determine current status. If file size is no longer a constraint (all current agent files exceed 200 lines), remove the caveat from MEMORY.md. If still relevant, add a warning to CONTRIBUTING.md about short agent files potentially failing silently.

---

### DRIFT-029: CONTRIBUTING.md cross-file update checklist omits GLOSSARY.md
- **Category**: DEAD DOC
- **Severity**: S3
- **Intent**: Accidental
- **Source agents**: FGH (finding H2)
- **Doc source**: `/Users/correy/projects/ant-farm/CONTRIBUTING.md`:37-41 — the cross-file update checklist when adding an agent lists: (1) README.md "Custom agents" table, (2) RULES.md "Agent Types" and "Model Assignments" tables, (3) scout.md (noted as usually unnecessary).
- **Impl source**: `/Users/correy/projects/ant-farm/orchestration/GLOSSARY.md`:77-85 — the "Ant Metaphor Roles" table lists all six agents with file paths, model assignments, and role descriptions. Adding a new agent without updating this table leaves the GLOSSARY inconsistent.
- **Impact**: A contributor adding an agent following CONTRIBUTING.md will omit the GLOSSARY.md "Ant Metaphor Roles" table update, leaving that table stale.
- **Suggested fix**: Add step 2.5 to the cross-file update checklist in CONTRIBUTING.md: "`orchestration/GLOSSARY.md` — add the agent to the 'Ant Metaphor Roles' table with file path, model tier, and role description."

---

### DRIFT-030: Dummy reviewer prompt created in sessions but output report never appears
- **Category**: UNDOCUMENTED
- **Severity**: S3
- **Intent**: Intentional (output is described as discarded, but the mechanism for writing it appears to be silently failing)
- **Source agents**: B (finding B8)
- **Doc source**: `/Users/correy/projects/ant-farm/orchestration/RULES.md`:186-219 — Step 3b-v describes spawning a dummy reviewer with: `Write your report to ${SESSION_DIR}/review-reports/dummy-review-${TIMESTAMP}.md`
- **Impl source**: `_session-068ecc83/prompts/review-dummy.md` and `_session-7edaafbb/prompts/review-dummy.md` — dummy prompt files exist (copy step completed). No `dummy-review-*.md` files found in either session's `review-reports/` directory.
- **Impact**: RULES.md says the dummy reviewer output "is discarded" and excluded from Big Head, so the absence of the output file does not affect workflow correctness. However, the context-usage instrumentation goal is silently not achieved. The tmux launch (Step 2 of the dummy reviewer process) may be failing silently.
- **Suggested fix**: Add a note to RULES.md Step 3b-v clarifying the expected outcome. After the review team completes, log a note if the dummy output file is missing (do not block workflow). If consistently failing to produce output, advance the sunset timeline noted in RULES.md line 186.

---

### DRIFT-031: fill-review-slots.sh `@file` prefix notation for multiline args not documented in RULES.md
- **Category**: UNDOCUMENTED
- **Severity**: S3
- **Intent**: Intentional — the `@file` feature is a convenience addition; plain strings still work
- **Source agents**: CD (finding D3)
- **Doc source**: `/Users/correy/projects/ant-farm/orchestration/RULES.md`:168-170 — documents the script invocation with 6 positional arguments. No mention of the `@file` prefix feature.
- **Impl source**: `/Users/correy/projects/ant-farm/scripts/fill-review-slots.sh`:78-94 — implements `@file` prefix notation allowing multiline arguments to be passed via file paths rather than inline strings. Particularly useful for `<changed-files>` and `<task-IDs>` which often contain newlines.
- **Impact**: The argument count and order match exactly (MATCH on core spec). A Queen constructing the invocation in RULES.md style with inline multiline strings may encounter shell escaping issues that `@file` notation would solve — but the feature is undiscoverable from RULES.md alone.
- **Suggested fix**: Optionally add a parenthetical to RULES.md Step 3b-ii: "For multiline arguments (`<changed-files>`, `<task-IDs>`), pass `@/path/to/file` instead of an inline string to avoid shell escaping issues."

---

### DRIFT-032: scrub-pii.sh / pre-commit hook not described in SETUP.md or README.md
- **Category**: UNDOCUMENTED
- **Severity**: S3
- **Intent**: Accidental omission — SETUP.md and README.md focus on the minimal quick-start path
- **Source agents**: CD (finding D5)
- **Doc source**: `/Users/correy/projects/ant-farm/CONTRIBUTING.md`:176-178 — documents two hooks: pre-push (runs sync-to-claude.sh) and pre-commit (runs scrub-pii.sh to strip email addresses from `.beads/issues.jsonl`). `/Users/correy/projects/ant-farm/orchestration/SETUP.md` — no mention of scrub-pii.sh or pre-commit hook.
- **Impl source**: `/Users/correy/projects/ant-farm/scripts/scrub-pii.sh` — present and installed by `install-hooks.sh`. If absent or non-executable when `.beads/issues.jsonl` is staged, the pre-commit hook prints a WARNING and continues (non-breaking).
- **Impact**: Developers following SETUP.md will learn about the pre-push hook but not the pre-commit hook or PII scrubbing. They may not understand warnings from the pre-commit hook or why PII scrubbing exists.
- **Suggested fix**: Add a note to SETUP.md's "Quick Setup" section (after the `install-hooks.sh` line) explaining that two hooks are installed: pre-push (sync) and pre-commit (PII scrub for `.beads/issues.jsonl`).

---

## Pre-Identified Findings Coverage

| # | Status | DRIFT ID | Notes |
|---|--------|----------|-------|
| 1 | Confirmed | DRIFT-001 | Reclassified from pre-identified S1 to DRIFT-001 S1. DRIFT-017 covers the companion GLOSSARY and README documentation surfaces. |
| 2 | Confirmed | DRIFT-003 | Confirmed S1 Contradiction. Installed hook is fatal; install-hooks.sh generates non-fatal. Re-running install-hooks.sh resolves the discrepancy. |
| 3 | Confirmed, reclassified S1 | DRIFT-002 | Pre-identified as S2; reclassified S1 by agent AE. PC lacks Task tool making the documented spawn architecturally impossible. |
| 4 | Confirmed | DRIFT-012 | Confirmed S2 Dead Doc. `orchestrator-state*.md` not found in any of the 13 `_session-*` directories. |
| 5 | Confirmed | DRIFT-013 | Confirmed S2 Dead Doc. `step3b-transition-gate.md` not found in any of the 13 `_session-*` directories. |
| 6 | Confirmed | DRIFT-014 | Confirmed S2 Dead Doc. `HANDOFF-*.md` not found in any session directory. One session has `EXECUTION_HANDOFF.md` at top level suggesting an older convention. |
| 7 | Confirmed | DRIFT-006 | Confirmed S2 Undocumented. Both dirs are created by later workflow phases; the mkdir command at Step 0 omits them without explanation. |
| 8 | Confirmed | DRIFT-019 | Confirmed S2 Contradiction. Sessions `_session-7edaafbb` and `_session-cd9866` use wave-based naming; `_session-cd9866` also omits timestamps. Current docs are correct; older sessions diverge. |
| 9 | Confirmed | DRIFT-005 | Confirmed S2 Dead Doc. Three agents independently found this issue. The table omits SSV despite the inline Step 1b text specifying `haiku`. |
| 10 | Confirmed | DRIFT-010 | Confirmed S2 Contradiction. Documented: `pc-{TASK_SUFFIX}-dmvdc-review-{timestamp}.md`. Actual: `pc-{review-type}-dmvdc-{timestamp}.md`. Two deviations from spec. |
| 11 | Confirmed | DRIFT-022 | Confirmed S3 Dead Doc. Two agents independently found this. SESSION_PLAN_TEMPLATE.md uses "Boss-Bot" and "Claude Sonnet 4.5" — both stale. |
| 12 | Partially confirmed | DRIFT-023 | GLOSSARY `pre-push hook` entry omits: `_archive/` exclusion, selective script sync (2 of 6), CLAUDE.md copy step, non-delete policy. S3 cosmetic since sync behavior is not a runtime decision input and the script's inline comments document it fully. |

All 12 pre-identified findings are accounted for in the consolidated report.

---

## Appendix: Files Audited

The following files were examined across all 4 audit agents:

**Orchestration rules and reference:**
- `/Users/correy/projects/ant-farm/orchestration/RULES.md`
- `/Users/correy/projects/ant-farm/orchestration/GLOSSARY.md`
- `/Users/correy/projects/ant-farm/orchestration/PLACEHOLDER_CONVENTIONS.md`
- `/Users/correy/projects/ant-farm/orchestration/SETUP.md`

**Templates:**
- `/Users/correy/projects/ant-farm/orchestration/templates/checkpoints.md`
- `/Users/correy/projects/ant-farm/orchestration/templates/reviews.md`
- `/Users/correy/projects/ant-farm/orchestration/templates/scout.md`
- `/Users/correy/projects/ant-farm/orchestration/templates/pantry.md`
- `/Users/correy/projects/ant-farm/orchestration/templates/SESSION_PLAN_TEMPLATE.md`
- `/Users/correy/projects/ant-farm/orchestration/templates/queen-state.md`
- `/Users/correy/projects/ant-farm/orchestration/templates/dirt-pusher-skeleton.md`
- `/Users/correy/projects/ant-farm/orchestration/templates/nitpicker-skeleton.md`
- `/Users/correy/projects/ant-farm/orchestration/templates/big-head-skeleton.md`
- `/Users/correy/projects/ant-farm/orchestration/templates/implementation.md`

**Archived templates:**
- `/Users/correy/projects/ant-farm/orchestration/_archive/colony-tsa.md`
- `/Users/correy/projects/ant-farm/orchestration/_archive/pantry-review.md`

**Agent definitions (repo):**
- `/Users/correy/projects/ant-farm/agents/pest-control.md`
- `/Users/correy/projects/ant-farm/agents/pantry-impl.md`
- `/Users/correy/projects/ant-farm/agents/scout-organizer.md`
- `/Users/correy/projects/ant-farm/agents/nitpicker.md`
- `/Users/correy/projects/ant-farm/agents/big-head.md`

**Agent definitions (global):**
- `/Users/correy/.claude/agents/code-reviewer.md`
- `/Users/correy/.claude/agents/pantry-review.md` (stale global copy)

**Scripts:**
- `/Users/correy/projects/ant-farm/scripts/sync-to-claude.sh`
- `/Users/correy/projects/ant-farm/scripts/install-hooks.sh`
- `/Users/correy/projects/ant-farm/scripts/parse-progress-log.sh`
- `/Users/correy/projects/ant-farm/scripts/fill-review-slots.sh`
- `/Users/correy/projects/ant-farm/scripts/compose-review-skeletons.sh`
- `/Users/correy/projects/ant-farm/scripts/scrub-pii.sh`

**Installed hook:**
- `/Users/correy/projects/ant-farm/.git/hooks/pre-push`

**Top-level documentation:**
- `/Users/correy/projects/ant-farm/CLAUDE.md`
- `/Users/correy/.claude/CLAUDE.md`
- `/Users/correy/projects/ant-farm/README.md`
- `/Users/correy/projects/ant-farm/CONTRIBUTING.md`
- `/Users/correy/projects/ant-farm/AGENTS.md`

**Memory:**
- `/Users/correy/.claude/projects/-Users-correy-projects-ant-farm/memory/MEMORY.md`

**Session artifacts examined:**
- `/Users/correy/projects/ant-farm/.beads/agent-summaries/_session-068ecc83/` (all subdirs)
- `/Users/correy/projects/ant-farm/.beads/agent-summaries/_session-7edaafbb/` (all subdirs)
- `/Users/correy/projects/ant-farm/.beads/agent-summaries/_session-cd9866/` (pc/ subdir)
- `/Users/correy/projects/ant-farm/.beads/agent-summaries/_session-8ae30b/` (top level)
- All 13 `_session-*` directories surveyed for artifact presence/absence

---

## Appendix: Checks That Passed

The following checks confirmed consistency between documentation and implementation:

**Agent definitions:**
- All five agent files have `name:` frontmatter matching their filename minus `.md`: `pest-control`, `pantry-impl`, `scout-organizer`, `nitpicker`, `big-head` — MATCH
- All six named custom agent types in the RULES.md Agent Types table have corresponding files in `agents/`. No files in `agents/` are absent from the table. (`pantry-review.md` is archived, not in `agents/`, and correctly absent from the table.) — MATCH
- CLAUDE.md `/Users/correy/projects/ant-farm/CLAUDE.md` and `~/.claude/CLAUDE.md` are byte-for-byte identical (81 lines). Sync mechanism working correctly. — MATCH

**Workflow steps:**
- `parse-progress-log.sh` exit codes match RULES.md documentation exactly: exit 0 (resume-plan written), exit 1 (error cases), exit 2 (SESSION_COMPLETE present). — MATCH
- Scout mode parameters (`ready`, `epic <id>`, `tasks <id1>, <id2>,...`, `filter <description>`) appear consistently across RULES.md lines 79-82, `agents/scout-organizer.md` lines 21-24, and `orchestration/templates/scout.md` lines 34-39. — MATCH
- SSV artifact path `${SESSION_DIR}/pc/pc-session-ssv-{timestamp}.md` matches actual artifact `_session-068ecc83/pc/pc-session-ssv-20260221-173632.md` and `checkpoints.md` line 696. — MATCH
- Wave pipelining confirmed by timestamp analysis: Wave 2 Pantry ran concurrently with Wave 1 Dirt Pushers (overlap window 03:46-03:55 UTC) in `_session-7edaafbb`, matching RULES.md Step 2 wave pipelining spec. — MATCH
- Review team composition consistent: RULES.md line 179 "Round 1: 6 members — 4 reviewers + Big Head + Pest Control" matches `reviews.md` lines 60 and 172. Session evidence: both `_session-068ecc83/review-skeletons/` and `_session-7edaafbb/review-skeletons/` contain exactly 5 skeleton files (big-head + 4 reviewers), consistent with the 6-member team (PC joins as team member with its own prompt). — MATCH
- Termination and round-cap logic: RULES.md lines 226-229 and `reviews.md` lines 188-197 specify identical termination conditions. Both observed sessions logged `decision=terminated` at round 2, consistent with documented termination check. — MATCH
- Four PC checkpoint model assignments (CCO: haiku, WWD: haiku, DMVDC: sonnet, CCB: haiku) match between `checkpoints.md` and RULES.md Model Assignments table. — MATCH
- Five checkpoint gates in RULES.md Hard Gates table have exact counterpart descriptions and matching artifact path formats in `checkpoints.md`. — MATCH

**Scripts:**
- `fill-review-slots.sh` argument count (6) and order (SESSION_DIR, COMMIT_RANGE, CHANGED_FILES, TASK_IDS, TIMESTAMP, REVIEW_ROUND) match exactly between RULES.md Step 3b-ii (lines 168-170) and script argument parsing (lines 67-72). — MATCH
- `compose-review-skeletons.sh` invocation in `pantry.md` Step 2.5 (4 arguments: SESSION_DIR, REVIEWS_MD_PATH, NITPICKER_SKELETON_PATH, BIG_HEAD_SKELETON_PATH) matches script argument validation (lines 35-44). — MATCH
- Core sync actions in CONTRIBUTING.md (CLAUDE.md copy, orchestration/ rsync, two scripts, agents/*.md) all match actions in sync-to-claude.sh. — MATCH (discrepancy only in `--delete` flag, reported as DRIFT-011)
- AGENTS.md `bd` command syntax (`bd update <id> --status in_progress`, `bd close <id>`) confirmed valid per `bd update --help` and `bd close --help`. — MATCH

**Templates:**
- Placeholder tier usage is correct across all templates: Tier 1 `{UPPERCASE}` for Queen-filled; Tier 2 `{lowercase-kebab}` for agent-filled; `${SHELL_VAR}` for shell. — MATCH
- All templates using `{UPPERCASE}` placeholders include the required term definition block (pantry.md, checkpoints.md, dirt-pusher-skeleton.md, big-head-skeleton.md, scout.md, nitpicker-skeleton.md). — MATCH
- All GLOSSARY-defined core terms (wave, checkpoint, briefing, data file, preview file, verdict, hard gate, information diet, summary doc, pre-push hook) are used in RULES.md and templates with consistent meanings. No orphaned defined terms. — MATCH
- `bd` prohibition scope is consistent across CLAUDE.md:38 and RULES.md:16 — both enumerate the same four commands plus "any bd query command" catch-all. (Minor wording drift reported as DRIFT-026.) — MATCH (functionally)
- Colony TSA elimination confirmed complete: `orchestration/_archive/colony-tsa.md` exists; no `colony-tsa.md` in `orchestration/templates/`. MEMORY.md "Completed" section correctly records this. — MATCH
- `bd dep add --type parent-child` syntax confirmed: `--type string` flag present with `parent-child` as valid type; positional order (child-id first, epic-id second) matches MEMORY.md documentation. — MATCH
- `progress.log` format confirmed: 11 entries in `_session-068ecc83/progress.log` use `TIMESTAMP|EVENT_TYPE|key=value|...` format matching RULES.md shell command templates at lines 60, 99, 116, 124, 221, 242, 245, 248, 251. — MATCH
- CONTRIBUTING.md "Adding a New Checkpoint" checklist correctly lists RULES.md Hard Gates table and Model Assignments table as update targets. — MATCH
- `pantry-review` deprecation handled correctly in GLOSSARY.md (strikethrough markup), `pantry.md` (active warning), and `reviews.md` ("replaces pantry-review"). No `pantry-review.md` in `agents/`. — MATCH (only scout.md exclusion list is stale; see DRIFT-021)
- README correctly marks `pantry-review` as DEPRECATED (line 309) with note it was replaced by `fill-review-slots.sh`. — MATCH
- All README-described roles (Queen, Scout, Pantry, Pest Control, Dirt Pushers, Nitpickers, Big Head) exist as agent files or documented orchestrator roles. No phantom roles. — MATCH
- AGENTS.md `bd close <id>` and `bd update --status` confirmed syntactically correct per help output. — MATCH
- Five core session subdirs (`task-metadata`, `previews`, `prompts`, `pc`, `summaries`) are present in all examined sessions. — MATCH

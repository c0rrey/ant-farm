> **Note**: This document was written during the Beads era. CLI commands shown as `bd` have been replaced by `crumb` equivalents.

# Audit Findings: Domains C + D (Checkpoints + Scripts)
**Audited:** 2026-02-21
**Checks performed:** 10
**Findings:** 9 (S1: 2, S2: 6, S3: 1)

---

## Findings

### C1: SSV checkpoint missing from Model Assignments table
- **Category**: DEAD DOC
- **Severity**: S2
- **Intent**: Accidental
- **Doc source**: `/Users/correy/projects/ant-farm/orchestration/templates/checkpoints.md`:612 — `**Model**: \`haiku\` (pure set comparisons — no judgment required)`
- **Impl source**: `/Users/correy/projects/ant-farm/orchestration/RULES.md`:288-304 — Model Assignments table; no row for "PC — SSV"
- **Impact**: The Queen's Model Assignments table (the authoritative runtime reference for which model to pass to each Task call) lists four PC checkpoint rows (CCO, WWD, DMVDC, CCB) but omits SSV entirely. A Queen following the table to select models will find no guidance for the SSV spawn. RULES.md Step 1b (line 89) does specify `model: "haiku"` inline, but any future editor normalizing all model specs to the table will not know SSV belongs there. The checkpoints.md SSV section documents `haiku` as the correct model; the table omits the row entirely.
- **Suggested fix**: Add a row to the Model Assignments table: `| PC — SSV | Task (\`pest-control\`) | haiku | Set comparisons — no judgment required |`

---

### C2a: Older sessions use session-scoped DMVDC artifact naming (wave-based)
- **Category**: CONTRADICTION
- **Severity**: S2
- **Intent**: Accidental (artifact of pre-task-suffix era)
- **Doc source**: `/Users/correy/projects/ant-farm/orchestration/templates/checkpoints.md`:27-33 — `**Task-specific checkpoints (CCO, WWD, DMVDC for Dirt Pushers):** \`pc-{TASK_SUFFIX}-{checkpoint}-{timestamp}.md\`` and `**Session-wide checkpoints (SSV, CCO-review, CCB):** \`pc-session-{checkpoint}-{timestamp}.md\``
- **Impl source**: `/Users/correy/projects/ant-farm/.beads/agent-summaries/_session-7edaafbb/pc/` — files: `pc-session-dmvdc-20260221-034922.md`, `pc-session-dmvdc-20260221-042058.md`, `pc-wave2-dmvdc-20260221-040754.md`, `pc-session-dmvdc-review-fixes-20260221-043218.md`; `/Users/correy/projects/ant-farm/.beads/agent-summaries/_session-cd9866/pc/` — files: `pc-session-dmvdc-wave1.md`, `pc-session-dmvdc-wave2.md`, `pc-session-cco-impl-wave1.md`, `pc-session-cco-impl-wave2.md`, `pc-session-wwd-wave1.md`, `pc-session-wwd-wave2.md`
- **Impact**: The documented naming pattern requires task-suffix-scoped names (e.g., `pc-6jxn-dmvdc-{timestamp}.md`) and session-scoped names only for SSV, CCO-review, and CCB. Session `_session-7edaafbb` and `_session-cd9866` used session-scoped and wave-based naming for DMVDC, WWD, and CCO artifacts. Anyone auditing these sessions by the current docs will expect task-suffix files and not find them, or vice versa. The most recent session (`_session-068ecc83`) does follow the documented pattern correctly.
- **Suggested fix**: No change to docs needed — current docs are correct for the current naming scheme. Consider adding a note in checkpoints.md that sessions prior to `_session-068ecc83` used wave-based naming, or retroactively document the transition date.

---

### C2b: Third-most-recent session (_session-cd9866) uses wave-based naming with no timestamp
- **Category**: CONTRADICTION
- **Severity**: S2
- **Intent**: Accidental (legacy naming from before timestamp convention was finalized)
- **Doc source**: `/Users/correy/projects/ant-farm/orchestration/templates/checkpoints.md`:39 — `**Timestamp format:** \`YYYYMMDD-HHmmss\` (UTC)` and line 27: `pc-{TASK_SUFFIX}-{checkpoint}-{timestamp}.md`
- **Impl source**: `/Users/correy/projects/ant-farm/.beads/agent-summaries/_session-cd9866/pc/` — files: `pc-session-cco-impl-wave1.md`, `pc-session-cco-impl-wave2.md`, `pc-session-dmvdc-wave1.md`, `pc-session-dmvdc-wave2.md`, `pc-session-wwd-wave1.md`, `pc-session-wwd-wave2.md` — none have timestamps; none use task-suffix segmentation
- **Impact**: Six artifact files in `_session-cd9866` use a `wave1`/`wave2` suffix with no timestamp and session-scoped rather than task-scoped naming. This violates both documented conventions (task-suffix and timestamp). Historical audit trail for that session cannot be reconstructed using the documented conventions.
- **Suggested fix**: Same as C2a — document the transition. No retrospective rename needed.

---

### C3: checkpoints.md claims Pest Control spawns a code-reviewer agent, but Pest Control lacks the Task tool
- **Category**: CONTRADICTION
- **Severity**: S2
- **Intent**: UNCERTAIN — may be aspirational design that was never implemented, or the "spawning" language may be misleading rather than literal
- **Doc source**: `/Users/correy/projects/ant-farm/orchestration/templates/checkpoints.md`:17 — `Pest Control is the orchestrator — the Queen spawns it to run a checkpoint. Pest Control then spawns a \`code-reviewer\` agent to execute the actual checks. The **Agent type (spawned by Pest Control)** fields in each section below specify the type of agent that Pest Control spawns, not Pest Control itself.`; also line 113: `**Agent type (spawned by Pest Control)**: \`code-reviewer\``; line 191: `**Agent type (spawned by Pest Control)**: \`code-reviewer\``; line 266: `**Agent type (spawned by Pest Control)**: \`code-reviewer\``;  line 339: `**Agent type (spawned by Pest Control)**: \`code-reviewer\``; line 504: `**Agent type (spawned by Pest Control)**: \`code-reviewer\``
- **Impl source**: `/Users/correy/projects/ant-farm/agents/pest-control.md`:4 — `tools: Bash, Read, Write, Glob, Grep`
- **Impact**: The `tools:` frontmatter for `pest-control.md` lists only `Bash, Read, Write, Glob, Grep`. The `Task` tool is not present. Without the Task tool, Pest Control cannot spawn any subagent. Every checkpoint section in checkpoints.md describes Pest Control as spawning a `code-reviewer` subagent to do the actual verification work, but this is architecturally impossible given PC's tool permissions. Either (a) Pest Control does all checks itself (the "code-reviewer" label is misleading) or (b) the two-level spawning design was intended but never implemented. Agents reading checkpoints.md will follow the "PC spawns code-reviewer" model and fail silently at the tool boundary.
- **Suggested fix**: Either add the `Task` tool to `pest-control.md` and create a `code-reviewer` agent type, or update all "Agent type (spawned by Pest Control): `code-reviewer`" lines in checkpoints.md to clarify that Pest Control runs checks directly. The "Pest Control Overview" section introduction (lines 13-24) should be updated to match the actual architecture.

---

### C4: Hard Gates table omits "Reviews" gate artifact path
- **Category**: DEAD DOC
- **Severity**: S3
- **Intent**: Intentional omission (Reviews gate has no single artifact path — it spans all review reports)
- **Doc source**: `/Users/correy/projects/ant-farm/orchestration/RULES.md`:263 — `| Reviews | Mandatory after ALL implementation completes; re-runs after fix cycles with reduced scope (round 2+) |`
- **Impl source**: The "Reviews" row in the Hard Gates table has only 2 columns populated ("Gate" and "Blocks") but the table has 3 columns ("Gate", "Blocks", "Artifact"). The "Artifact" cell is empty/missing. All other 5 gates have artifact paths.
- **Impact**: The table is visually inconsistent and the Reviews row's blocking behavior description is in the wrong column (it appears in "Blocks" but reads like a description, not a list of what gets blocked). Minor cosmetic issue — does not cause incorrect behavior since the Reviews gate is described in full detail in Steps 3b-3c.
- **Suggested fix**: Either add an artifact path (e.g., `${SESSION_DIR}/review-reports/review-consolidated-{timestamp}.md`) or split the description across the correct columns. The row as written conflates the "Blocks" column with a narrative explanation.

---

### C4b: Hard Gates table has 7 rows but checkpoints.md documents 5 checkpoints; GLOSSARY says 4
- **Category**: CONTRADICTION
- **Severity**: S2
- **Intent**: Accidental — different documents were updated at different times
- **Doc source**: `/Users/correy/projects/ant-farm/orchestration/GLOSSARY.md`:46 — `**checkpoint** | A mandatory verification gate that blocks the next phase of work until it returns PASS (or an approved WARN). There are four checkpoints: CCO, WWD, DMVDC, and CCB.`; also GLOSSARY.md line 64: `All four checkpoints are executed by Pest Control.`
- **Impl source**: `/Users/correy/projects/ant-farm/orchestration/RULES.md`:255-263 — Hard Gates table lists 6 gates: SSV PASS, CCO PASS (impl), CCO PASS (review), WWD PASS, DMVDC PASS, CCB PASS, Reviews; `/Users/correy/projects/ant-farm/orchestration/templates/checkpoints.md`:15 — `All checkpoint verifications (SSV, CCO, WWD, DMVDC, CCB) are executed by **Pest Control**` (5 checkpoints listed)
- **Impact**: The GLOSSARY says there are four checkpoints and names CCO, WWD, DMVDC, CCB — omitting SSV entirely. checkpoints.md lists five (adding SSV). RULES.md's Hard Gates table has seven rows (splitting CCO into impl and review variants, plus a Reviews gate). A reader using the GLOSSARY as the authoritative definition will have an incorrect mental model: SSV will be unknown to them, and they will not understand that CCO runs in two distinct configurations (impl vs. review). The GLOSSARY is the stated "single source of truth" for term definitions, making this discrepancy materially misleading.
- **Suggested fix**: Update GLOSSARY.md's "checkpoint" definition to list all 5 checkpoints (SSV, CCO, WWD, DMVDC, CCB) and note the CCO impl vs. review distinction. Update the "Checkpoint Acronyms" table to add SSV.

---

### C5: DMVDC Nitpicker artifact naming: documented format vs actual filenames
- **Category**: CONTRADICTION
- **Severity**: S2
- **Intent**: Accidental
- **Doc source**: `/Users/correy/projects/ant-farm/orchestration/templates/checkpoints.md`:475 — `\`{SESSION_DIR}/pc/pc-{TASK_SUFFIX}-dmvdc-review-{timestamp}.md\``; line 478 — `\`{TASK_SUFFIX}\`: Nitpicker task suffix (e.g., \`review-clarity\`, \`review-edge\`)`
- **Impl source**: `/Users/correy/projects/ant-farm/.beads/agent-summaries/_session-068ecc83/pc/` — actual files: `pc-review-correctness-dmvdc-20260221-182700.md`, `pc-review-edge-cases-dmvdc-20260221-182700.md`
- **Impact**: The documented format is `pc-{TASK_SUFFIX}-dmvdc-review-{timestamp}.md`, where `{TASK_SUFFIX}` would be something like `review-clarity`. Applied literally, this yields `pc-review-clarity-dmvdc-review-{timestamp}.md`. The actual files use `pc-review-correctness-dmvdc-{timestamp}.md` and `pc-review-edge-cases-dmvdc-{timestamp}.md` — the `-review` suffix after `dmvdc` is absent, and the review type (`correctness`, `edge-cases`) is used directly as the suffix component rather than a `review-{type}` compound. Two deviations: (1) missing trailing `-review` in the checkpoint segment, and (2) the actual TASK_SUFFIX used is the bare review type rather than `review-{type}`. Anyone querying the `pc/` directory for `*dmvdc-review*` patterns will find zero matches.
- **Suggested fix**: Either update checkpoints.md line 475 to match the actual convention — `pc-{review-type}-dmvdc-{timestamp}.md` — or update Pest Control's behavior to generate files with the `-review` suffix. The TASK_SUFFIX note on line 478 should also be updated to give the correct example values (`correctness`, `edge-cases` rather than `review-clarity`, `review-edge`).

---

### D1: CONTRIBUTING.md documents rsync with --delete but sync-to-claude.sh does not use --delete
- **Category**: CONTRADICTION
- **Severity**: S1
- **Intent**: Accidental
- **Doc source**: `/Users/correy/projects/ant-farm/CONTRIBUTING.md`:161 — `orchestration/` to `~/.claude/orchestration/` (via rsync `--delete`, excluding `scripts/`)`
- **Impl source**: `/Users/correy/projects/ant-farm/scripts/sync-to-claude.sh`:27 — `rsync -av --exclude='scripts/' --exclude='_archive/' "$REPO_ROOT/orchestration/" ~/.claude/orchestration/`
- **Impact**: CONTRIBUTING.md explicitly states the rsync uses `--delete`, which would remove stale files from the target `~/.claude/orchestration/` that no longer exist in the source. The actual script does NOT use `--delete` — it intentionally omits it (the script comments on line 24-25 explain this: "removing it preserves any custom files adopters have placed under `~/.claude/orchestration/`"). A developer relying on the CONTRIBUTING.md description to understand sync behavior will have a false expectation: they will believe that deleting a source file causes it to be removed from `~/.claude/orchestration/` on next push, when in fact it is preserved. This can lead to stale templates remaining active at runtime. Furthermore, the script also excludes `_archive/` from sync — CONTRIBUTING.md does not document this exclusion.
- **Suggested fix**: Update CONTRIBUTING.md line 161 to: `orchestration/` to `~/.claude/orchestration/` (via rsync without `--delete`, preserving custom files; also excludes `scripts/` and `_archive/`)`. Or more precisely match the script comment's explanation.

---

### D2: Installed pre-push hook is fatal on sync failure; install-hooks.sh generates non-fatal hook
- **Category**: CONTRADICTION
- **Severity**: S1
- **Intent**: Accidental — the installed hook appears to be an older version that was not regenerated after install-hooks.sh was updated
- **Doc source**: `/Users/correy/projects/ant-farm/scripts/install-hooks.sh`:50-57 — the hook template written by install-hooks.sh wraps the sync script in a non-fatal check: `if ! "$SYNC_SCRIPT"; then echo "[ant-farm] WARNING: sync-to-claude.sh failed — push continuing without sync." ... fi` (sync failure prints a warning but exits 0, allowing the push to proceed)
- **Impl source**: `/Users/correy/projects/ant-farm/.git/hooks/pre-push`:11 — `"$SYNC_SCRIPT"` — the installed hook calls the sync script with `set -euo pipefail` active (line 2) and no error handling. If `sync-to-claude.sh` exits non-zero, the pre-push hook immediately exits non-zero (due to `set -e`), blocking the push.
- **Impact**: A developer pushing code will experience a blocked push if `sync-to-claude.sh` fails for any reason (disk full, permission error, rsync failure). The design intent documented in `install-hooks.sh` is that sync failure is non-fatal — the push should always succeed and the developer should fix the sync separately. The installed hook enforces the opposite policy. This is an S1 behavioral discrepancy: running `./scripts/install-hooks.sh` would fix the installed hook to match the documented intent, but until it is re-run, every push is at risk of being blocked by a sync error.
- **Suggested fix**: Re-run `./scripts/install-hooks.sh` to replace the installed hook with the version that makes sync failure non-fatal. Then confirm the installed hook matches the template in `install-hooks.sh` lines 39-58.

---

### D3: RULES.md fill-review-slots.sh invocation uses placeholder argument strings, not real syntax
- **Category**: UNDOCUMENTED
- **Severity**: S3
- **Intent**: Intentional — angle-bracket placeholders are standard documentation style for "fill in your value here"
- **Doc source**: `/Users/correy/projects/ant-farm/orchestration/RULES.md`:168-170 —
  ```bash
  bash ~/.claude/orchestration/scripts/fill-review-slots.sh \
    "${SESSION_DIR}" "<commit-range>" "<changed-files>" \
    "<task-IDs>" "<timestamp>" "<round>"
  ```
- **Impl source**: `/Users/correy/projects/ant-farm/scripts/fill-review-slots.sh`:15-25 — the script's own usage comment documents the argument order identically: `fill-review-slots.sh <SESSION_DIR> <COMMIT_RANGE> <CHANGED_FILES_LIST> <TASK_IDS_LIST> <TIMESTAMP> <REVIEW_ROUND>` (6 positional args, same order as RULES.md)
- **Assessment**: The documented invocation in RULES.md matches the script's argument parsing exactly. RULES.md argument order: SESSION_DIR, commit-range, changed-files, task-IDs, timestamp, round. Script positional vars (lines 67-72): SESSION_DIR=$1, COMMIT_RANGE=$2, CHANGED_FILES_RAW=$3, TASK_IDS_RAW=$4, TIMESTAMP=$5, REVIEW_ROUND=$6. This is a MATCH on argument count and order. The one undocumented feature is the `@file` prefix notation (lines 78-94 of the script) for passing multiline arguments via file paths — this is a convenience feature not mentioned in RULES.md. It is non-breaking (plain strings still work).
- **Suggested fix**: Optionally add a note in RULES.md Step 3b-ii about the `@file` prefix for multiline arguments, particularly for `<changed-files>` and `<task-IDs>` which often contain newlines.

---

### D5: scrub-pii.sh is documented in CONTRIBUTING.md but not in SETUP.md or README.md
- **Category**: UNDOCUMENTED
- **Severity**: S3
- **Intent**: Accidental omission — SETUP.md and README.md focus on the minimal quick-start path
- **Doc source**: `/Users/correy/projects/ant-farm/CONTRIBUTING.md`:176-178 — `This installs two hooks: **pre-push** -- runs \`sync-to-claude.sh\` on every push; **pre-commit** -- runs \`scrub-pii.sh\` to strip email addresses from \`.beads/issues.jsonl\` before commits`
- **Impl source**: `/Users/correy/projects/ant-farm/orchestration/SETUP.md` (no mention of scrub-pii.sh or pre-commit hook); `/Users/correy/projects/ant-farm/README.md` (no mention of scrub-pii.sh or pre-commit hook)
- **Impact**: Developers following SETUP.md as their primary onboarding document will learn about the pre-push hook but not the pre-commit hook or PII scrubbing. If `scrub-pii.sh` is absent or non-executable and `.beads/issues.jsonl` is staged, the pre-commit hook (installed by `install-hooks.sh`) prints a WARNING and continues — so this is not breaking. However, developers may not understand why their commits sometimes trigger a warning or why PII scrubbing matters. SETUP.md does reference `install-hooks.sh` (line 11) without explaining what it installs.
- **Suggested fix**: Add a note to SETUP.md's "Quick Setup" section (after the `install-hooks.sh` line) explaining that two hooks are installed: pre-push (sync) and pre-commit (PII scrub). This matches the level of detail in CONTRIBUTING.md.

---

## Checks That Passed (MATCHes)

**C1 (partial MATCH)**: The four non-SSV PC checkpoint model assignments — PC-CCO (haiku), PC-WWD (haiku), PC-DMVDC (sonnet), PC-CCB (haiku) — all match between checkpoints.md and the RULES.md Model Assignments table. Only SSV is missing from the table (reported as finding C1).

**C4 (partial MATCH)**: Five of the six checkpoint gates in RULES.md Hard Gates table (lines 255-263) have exact counterpart descriptions in checkpoints.md. SSV PASS → "FAIL blocks Pantry spawn" (checkpoints.md line 83); CCO PASS (impl) → "FAIL verdict: Any check fails" (checkpoints.md line 128); CCO PASS (review) → "FAIL: <list>" (checkpoints.md line 244); WWD PASS → "FAIL: ... Blocks queue" (checkpoints.md line 306); DMVDC PASS → "FAIL: ... FAIL escalates" (checkpoints.md line 399); CCB PASS → "FAIL: ... Must resolve before presenting" (checkpoints.md line 587). Artifact path formats also match between the two documents for all six gates.

**D3 (MATCH)**: `fill-review-slots.sh` argument count (6) and order (SESSION_DIR, COMMIT_RANGE, CHANGED_FILES, TASK_IDS, TIMESTAMP, REVIEW_ROUND) match exactly between RULES.md Step 3b-ii (lines 168-170) and the script's argument parsing (lines 67-72 of `/Users/correy/projects/ant-farm/scripts/fill-review-slots.sh`).

**D4 (MATCH)**: `compose-review-skeletons.sh` is invoked in pantry.md Step 2.5 (lines 148-153) with 4 arguments: SESSION_DIR, REVIEWS_MD_PATH, NITPICKER_SKELETON_PATH, BIG_HEAD_SKELETON_PATH. The script's argument validation (lines 35-44 of `/Users/correy/projects/ant-farm/scripts/compose-review-skeletons.sh`) requires exactly 4 positional arguments in the same order. The pantry.md example uses `~/.claude/orchestration/templates/reviews.md`, `~/.claude/orchestration/templates/nitpicker-skeleton.md`, and `~/.claude/orchestration/templates/big-head-skeleton.md` — matching the script's REVIEWS_MD, NITPICKER_SKELETON, BIG_HEAD_SKELETON positional vars.

**D1 (partial MATCH — sync target actions)**: The core sync actions documented in CONTRIBUTING.md (CLAUDE.md copy, orchestration/ rsync, two orchestration scripts, agents/*.md) all match actions in sync-to-claude.sh. The discrepancy is only in the `--delete` flag description (reported as finding D1).

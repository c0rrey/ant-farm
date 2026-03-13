> **Note**: This document was written during the Beads era. CLI commands shown as `bd` have been replaced by `crumb` equivalents.

# Audit Findings: Domains A + E (Agent Definitions + Term Consistency)
**Audited:** 2026-02-21
**Checks performed:** 10 (A1–A6, E1–E4)
**Findings:** 9 (S1: 2, S2: 4, S3: 3)

---

## Findings

### A2-a: Scout agent `model: sonnet` vs RULES.md `model: opus`
- **Category**: CONTRADICTION
- **Severity**: S1 (Breaking)
- **Intent**: Accidental
- **Doc source**: `/Users/correy/projects/ant-farm/orchestration/RULES.md`:294 — `| Scout | Task (\`scout-organizer\`) | opus | Orchestration role |`
- **Impl source**: `/Users/correy/projects/ant-farm/agents/scout-organizer.md`:5 — `model: sonnet`
- **Impact**: RULES.md Model Assignments table is authoritative: the Queen is told to spawn Scout with `model: "opus"`. The agent frontmatter says `model: sonnet`. Claude Code loads the frontmatter model when no explicit override is given at spawn time. If the Queen omits the `model` parameter (violating the RULES.md instruction), the Scout runs as sonnet instead of opus. Conversely, if the Queen supplies `model: "opus"` as RULES.md requires, the frontmatter is overridden and the contradiction is silent but still a false mental model. Either way, the frontmatter actively misleads about which model the agent expects.
- **Suggested fix**: Update `agents/scout-organizer.md` frontmatter to `model: opus` to match the Model Assignments table. Alternatively, add a comment in the frontmatter noting that the Queen overrides the model at spawn time.

---

### A2-b: GLOSSARY Scout model listed as `sonnet` vs RULES.md `opus`
- **Category**: CONTRADICTION
- **Severity**: S2 (Misleading)
- **Intent**: Accidental
- **Doc source**: `/Users/correy/projects/ant-farm/orchestration/GLOSSARY.md`:80 — `| **Scout** | \`agents/scout-organizer.md\` | sonnet | Pre-flight reconnaissance agent. ...`
- **Impl source**: `/Users/correy/projects/ant-farm/orchestration/RULES.md`:294 — `| Scout | Task (\`scout-organizer\`) | opus | Orchestration role |`
- **Impact**: The GLOSSARY Ant Metaphor Roles table is a reference document read by humans. It says sonnet; RULES.md says opus. Someone consulting the GLOSSARY to understand the system gets the wrong model for Scout. This is a documentation-level contradiction rather than a spawn-time one, but it compounds A2-a.
- **Suggested fix**: Update the GLOSSARY Ant Metaphor Roles table Scout row to `opus` so it matches RULES.md. Do this alongside A2-a.

---

### A2-c: GLOSSARY Pantry model listed as `sonnet` vs RULES.md `opus`
- **Category**: CONTRADICTION
- **Severity**: S2 (Misleading)
- **Intent**: Accidental
- **Doc source**: `/Users/correy/projects/ant-farm/orchestration/GLOSSARY.md`:81 — `| **Pantry** | \`agents/pantry-impl.md\` (implementation), ~~\`agents/pantry-review.md\`~~ (deprecated; see RULES.md Step 3b) | sonnet | Prompt composition agent. ...`
- **Impl source**: `/Users/correy/projects/ant-farm/orchestration/RULES.md`:295 — `| Pantry (impl) | Task (\`pantry-impl\`) | opus | Prompt composition + review skeleton assembly (Script 1) |`
- **Impact**: GLOSSARY says Pantry runs as sonnet; RULES.md Model Assignments says opus. A reader using the GLOSSARY as their mental model of the system would not understand why the Pantry is expensive. Neither `agents/pantry-impl.md` nor `agents/scout-organizer.md` have a `model:` frontmatter field for pantry-impl (pantry-impl.md has no `model:` field at all), so the Queen's explicit `model: "opus"` at spawn time is the only enforcement — but the GLOSSARY documents it incorrectly.
- **Suggested fix**: Update GLOSSARY Ant Metaphor Roles Pantry row to show `opus` for implementation mode.

---

### A3: Pest Control lacks `Task` tool but checkpoints.md says it spawns `code-reviewer` subagents
- **Category**: CONTRADICTION
- **Severity**: S1 (Breaking)
- **Intent**: UNCERTAIN
- **Doc source**: `/Users/correy/projects/ant-farm/orchestration/templates/checkpoints.md`:17 — `"Pest Control is the orchestrator — the Queen spawns it to run a checkpoint. Pest Control then spawns a \`code-reviewer\` agent to execute the actual checks."` and repeated across all checkpoint sections (lines 113, 191, 266, 339, 413, 504, 614): `**Agent type (spawned by Pest Control)**: \`code-reviewer\``
- **Impl source**: `/Users/correy/projects/ant-farm/agents/pest-control.md`:4 — `tools: Bash, Read, Write, Glob, Grep`
- **Impact**: The `Task` tool is required to spawn a subagent (`code-reviewer`). Pest Control's `tools:` list does not include `Task`. If the model follows checkpoints.md literally and attempts to spawn a code-reviewer subagent, it will fail — the tool is not available. In practice, Pest Control likely executes the checkpoint logic itself (it has all the necessary read/write/bash tools to do so) despite the checkpoints.md doc claiming there is a spawned sub-subagent. This creates a false mental model in anyone reading checkpoints.md: they believe there are two layers of agents (PC + code-reviewer) when in practice there is one. Intent is UNCERTAIN because it is possible checkpoints.md describes an aspirational design that was never implemented, or that PC actually does need Task tool and should have it.
- **Suggested fix**: Pick one: (a) If Pest Control is intended to run checkpoints directly (no sub-spawn), remove the "Pest Control spawns a code-reviewer" framing from checkpoints.md and replace it with direct execution language; (b) If Pest Control should spawn a code-reviewer, add `Task` to the `tools:` frontmatter in `agents/pest-control.md`.

---

### A4: Agent Types table lists agents matching actual files — but `SSV` checkpoint model is omitted
- **Category**: DEAD DOC
- **Severity**: S2 (Misleading)
- **Intent**: Accidental
- **Doc source**: `/Users/correy/projects/ant-farm/orchestration/RULES.md`:288–304 (Model Assignments table) — The table covers Scout, Pantry (impl), Dirt Pushers, PC—CCO, PC—WWD, PC—DMVDC, PC—CCB, Nitpickers, Big Head, PC (team member), Fix Dirt Pushers. It does NOT include a row for `PC — SSV`.
- **Impl source**: `/Users/correy/projects/ant-farm/orchestration/RULES.md`:89 — `spawn Pest Control (\`pest-control\`, \`model: "haiku"\`) for Scout Strategy Verification (SSV)`
- **Impact**: The SSV checkpoint model (haiku) is documented inline in Step 1b but absent from the Model Assignments table. A Queen following the table to know which model to use for each Pest Control spawn will not find SSV there and must hunt in Step 1b text. The table claims to be the authoritative reference ("Every Task tool call the Queen makes MUST include the model parameter from this table"), so an omitted entry is effectively DEAD DOC for anyone relying on the table alone.
- **Suggested fix**: Add a `PC — SSV` row to the Model Assignments table: `| PC — SSV | Task (\`pest-control\`) | haiku | Pure set comparisons — no judgment required |`

---

### A5: `code-reviewer` is a custom agent in `~/.claude/agents/`, not a built-in — docs do not clarify this
- **Category**: UNDOCUMENTED
- **Severity**: S3 (Cosmetic)
- **Intent**: Accidental
- **Doc source**: `/Users/correy/projects/ant-farm/orchestration/templates/checkpoints.md`:17 — `"Pest Control then spawns a \`code-reviewer\` agent to execute the actual checks."` (and repeated across all checkpoint sections). No clarification is given on whether `code-reviewer` is a built-in or custom agent type.
- **Impl source**: `/Users/correy/.claude/agents/code-reviewer.md`:1–6 — `---\nname: code-reviewer\ndescription: Expert code reviewer ...\ntools: Read, Write, Edit, Bash, Glob, Grep\nmodel: opus\n---`
- **Impact**: `code-reviewer` is a custom agent file in `~/.claude/agents/`. A reader of checkpoints.md who assumes it is a built-in Claude Code type (like `general-purpose`) may be confused when it does not exist in a fresh environment. The `code-reviewer.md` file is in the user's global `~/.claude/agents/` directory but is NOT in the ant-farm repo's `agents/` directory, meaning `sync-to-claude.sh` does not sync it. New adopters of ant-farm running on a fresh machine would not have this agent. The Agent Types table in RULES.md lines 278–286 does not list `code-reviewer` at all.
- **Suggested fix**: Add a note in checkpoints.md clarifying that `code-reviewer` is a custom agent type (not a built-in) and that it must be present in `~/.claude/agents/`. Consider either moving it into the repo's `agents/` directory so sync-to-claude.sh handles it, or documenting in SETUP.md that `code-reviewer` must be installed separately.

---

### A6: `pantry-review` reference in active scout.md exclusion list
- **Category**: DEAD DOC
- **Severity**: S3 (Cosmetic)
- **Intent**: Accidental
- **Doc source**: `/Users/correy/projects/ant-farm/orchestration/templates/scout.md`:63 — `scout-organizer, pantry-impl, pantry-review, pest-control, nitpicker, big-head`
- **Impl source**: No `agents/pantry-review.md` file exists in the repo. The file exists only at `/Users/correy/projects/ant-farm/orchestration/_archive/pantry-review.md` (archived) and at `~/.claude/agents/pantry-review.md` (stale global copy).
- **Impact**: The Scout's exclusion list for Dirt Pusher recommendations includes `pantry-review`. Because `pantry-review` is deprecated and has no agent file in `agents/`, it would not appear in the Scout's catalog anyway. The reference is harmless but signals that the exclusion list was not updated when pantry-review was archived. A Scout reading its own instructions sees a reference to a non-existent agent.
- **Suggested fix**: Remove `pantry-review` from the exclusion list in `orchestration/templates/scout.md` line 63.

**Note on other `pantry-review` references**: `GLOSSARY.md` lines 28 and 81 use strikethrough markup (`~~pantry-review.md~~`) with "(deprecated; see RULES.md Step 3b)" annotations — these are intentional and correctly signal deprecation. `pantry.md` line 256 ("Do NOT spawn `pantry-review` for a second invocation") is an active warning that correctly acknowledges the deprecation. `reviews.md` line 1 says "replaces pantry-review" — this is informational and correct. Only the scout.md exclusion list reference is problematic.

---

### E1/E2: `{{REVIEW_ROUND}}` double-brace syntax in `reviews.md` not defined in PLACEHOLDER_CONVENTIONS.md
- **Category**: UNDOCUMENTED
- **Severity**: S2 (Misleading)
- **Intent**: Intentional (per the doc explanation) but UNDOCUMENTED in the conventions file
- **Doc source**: `/Users/correy/projects/ant-farm/orchestration/PLACEHOLDER_CONVENTIONS.md` — defines three tiers: `{UPPERCASE}` (Tier 1), `{lowercase-kebab}` (Tier 2), `${SHELL_VAR}` (Tier 3). No mention of `{{double-brace}}` syntax. The File-by-File Audit table (line 112) marks `reviews.md` as PASS with "None (uses angle-bracket syntax...)" — but `{{REVIEW_ROUND}}` does appear in reviews.md.
- **Impl source**: `/Users/correy/projects/ant-farm/orchestration/templates/reviews.md`:502 — `REVIEW_ROUND={{REVIEW_ROUND}}` and line 592: `fill-review-slots.sh substitutes \`{{REVIEW_ROUND}}\` with the actual round integer before delivering this brief to Big Head.`
- **Impact**: `{{REVIEW_ROUND}}` is a fourth placeholder tier used exclusively in reviews.md — it is substituted by `fill-review-slots.sh` (a shell script), not by the Queen. This is a distinct substitution agent (neither the Queen, nor the agent, nor the shell interpreter in the usual sense). The PLACEHOLDER_CONVENTIONS.md audit table explicitly marks reviews.md as PASS with "None" for all three tiers, which is inaccurate: double-brace placeholders exist and are substituted by a different mechanism. A template author extending reviews.md would not know this fourth tier exists or how it works.
- **Suggested fix**: Add a "Tier 4: Script-Substituted (`{{DOUBLE_BRACE}}`)" entry to PLACEHOLDER_CONVENTIONS.md explaining that these are filled by `fill-review-slots.sh` before delivery. Update the File-by-File Audit table row for reviews.md accordingly.

---

### E4: SESSION_PLAN_TEMPLATE.md uses stale term "Boss-Bot" and old model name
- **Category**: DEAD DOC
- **Severity**: S3 (Cosmetic)
- **Intent**: Accidental
- **Doc source**: `/Users/correy/projects/ant-farm/orchestration/templates/SESSION_PLAN_TEMPLATE.md`:8 — `**Boss-Bot:** Claude Sonnet 4.5` and line 340: `- Implementation files read in boss-bot window: ___ (target: <10)`
- **Impl source**: `/Users/correy/projects/ant-farm/orchestration/GLOSSARY.md`:79 — The orchestrator role is called "Queen" throughout all current documentation. "Boss-Bot" appears nowhere in GLOSSARY.md, RULES.md, or any active template. The current model for the Queen (orchestrator) is described as `opus` in RULES.md and GLOSSARY.md, not `Claude Sonnet 4.5`.
- **Impact**: SESSION_PLAN_TEMPLATE.md predates the current orchestration framework (it is from an earlier design iteration). "Boss-Bot" is not defined in the GLOSSARY, making the term undefined. "Claude Sonnet 4.5" is both a stale model name and the wrong tier — the Queen runs as opus. Any session created using this template as a starting point would contain terminology inconsistent with the current framework, creating confusion for anyone cross-referencing with GLOSSARY.md or RULES.md.
- **Suggested fix**: Update SESSION_PLAN_TEMPLATE.md to use "Queen" instead of "Boss-Bot" / "boss-bot", and update the model name to `opus` (or remove the specific model version since it changes over time). Alternatively, move SESSION_PLAN_TEMPLATE.md to `_archive/` if it is no longer used as an active template (given that the Scout now generates briefing.md automatically).

---

## Checks That Passed (MATCHes)

**A1 — Agent name vs filename conformance**
All five agent files have `name:` frontmatter matching their filename (minus `.md`):
- `agents/pest-control.md` → `name: pest-control` (line 2) — MATCH
- `agents/pantry-impl.md` → `name: pantry-impl` (line 2) — MATCH
- `agents/scout-organizer.md` → `name: scout-organizer` (line 2) — MATCH
- `agents/nitpicker.md` → `name: nitpicker` (line 2) — MATCH
- `agents/big-head.md` → `name: big-head` (line 2) — MATCH

**A4 — Agent Types table vs actual files**
The Agent Types table at RULES.md lines 278–286 lists: Scout (`scout-organizer`), Pantry impl (`pantry-impl`), Pest Control (`pest-control`), Dirt Pushers (dynamic), Nitpickers (`nitpicker`), Big Head (`big-head`). All six named custom agent types have corresponding files in `agents/`. No files in `agents/` are absent from the table (the `pantry-review.md` file is archived, not in `agents/`, and correctly absent from the table). MATCH.

**A5 — Built-in vs custom clarification (partial)**
`code-reviewer` IS confirmed as a custom agent (has a file at `~/.claude/agents/code-reviewer.md`, not a built-in). The finding A5 above documents that it is neither in the repo's `agents/` directory nor covered in SETUP.md. The check itself (confirming it is custom) is resolved; the undocumented gap is the finding.

**E1 — Placeholder tier usage per file**
All templates in `orchestration/templates/*.md` use the correct tier casing for their respective placeholders:
- `scout.md`: `{SESSION_DIR}` (Tier 1), `{session-dir}` (Tier 2) — MATCH
- `pantry.md`: `{TASK_ID}`, `{TASK_SUFFIX}`, `{SESSION_DIR}` (Tier 1), `{session-dir}` (Tier 2) — MATCH with term def block at lines 5–11
- `checkpoints.md`: `{TASK_ID}`, `{TASK_SUFFIX}`, `{SESSION_DIR}` (Tier 1), `{checkpoint}`, `{N}`, `{list}` (Tier 2) — MATCH with term def block at lines 4–11
- `dirt-pusher-skeleton.md`: `{TASK_ID}`, `{TASK_SUFFIX}`, `{AGENT_TYPE}`, etc. (Tier 1) — MATCH with term def block at lines 10–13
- `nitpicker-skeleton.md`: `{REVIEW_TYPE}`, `{DATA_FILE_PATH}`, `{REPORT_OUTPUT_PATH}`, `{REVIEW_ROUND}` (Tier 1) — MATCH with partial term def block at lines 8–13
- `big-head-skeleton.md`: `{TASK_ID}`, `{TASK_SUFFIX}`, `{TIMESTAMP}`, `{SESSION_DIR}`, `{REVIEW_ROUND}` (Tier 1) — MATCH with term def block at lines 8–13
- `implementation.md`: angle-bracket syntax only (`<task-id>`, `<file>`) — MATCH (no curly-brace Tier 1/2 needed; not a Queen-filled template)
- `queen-state.md`: angle-bracket syntax for human-editing fields — MATCH

**E2 — Mandatory term definition blocks**
Templates using `{UPPERCASE}` placeholders include the required term definition block:
- `pantry.md`: Yes (lines 5–11) — MATCH
- `checkpoints.md`: Yes (lines 4–11) — MATCH
- `dirt-pusher-skeleton.md`: Yes (lines 10–13) — MATCH
- `big-head-skeleton.md`: Yes (lines 8–13) — MATCH
- `scout.md`: Has term definitions at lines 12–14 (inline style rather than the block template, but covers the three canonical terms) — MATCH (minor style variation, not a violation)
- `nitpicker-skeleton.md`: Partial block (lines 8–13 cover REVIEW_TYPE, DATA_FILE_PATH, REPORT_OUTPUT_PATH, REVIEW_ROUND, but not the three canonical terms TASK_ID/TASK_SUFFIX/SESSION_DIR, which are not used in this template) — MATCH (the block only needs to define the terms the template actually uses)

**E3 — GLOSSARY term cross-reference (terms defined and used)**
The GLOSSARY defines: session, wave, checkpoint, scope boundary, data file, briefing, preview file, verdict, information diet, escalation, adjacent issue, summary doc, hard gate, context window, pre-push hook. Cross-referencing against RULES.md and templates:
- All core terms (wave, checkpoint, briefing, data file, preview file, verdict, hard gate, information diet, summary doc) are actively used in RULES.md and templates with consistent meanings — MATCH.
- "pre-push hook" is defined in GLOSSARY (line 58) and referenced in RULES.md and SETUP.md — MATCH.
- No orphaned defined terms found (all GLOSSARY terms appear in active docs). No critically undefined terms found in RULES.md/templates that should be in GLOSSARY but are not — with the caveat noted in A5 (`code-reviewer`) and E1/E2 (`{{REVIEW_ROUND}}`).

**E4 — SESSION_PLAN_TEMPLATE.md stale terminology (partial)**
Finding E4 above covers "Boss-Bot" and model names. All other terminology in SESSION_PLAN_TEMPLATE.md (wave, P1/P2/P3, CHANGELOG, bd commands) is consistent with GLOSSARY definitions.

---

## Pre-Identified Findings: Confirmation Status

| # | Description | Confirmed? | This Audit's ID |
|---|-------------|------------|-----------------|
| #1 | Scout `model: sonnet` vs RULES.md `model: opus` — S1 Contradiction | **CONFIRMED** | A2-a |
| #3 | checkpoints.md says PC spawns code-reviewer, but PC agent lacks Task tool — S2 Contradiction | **CONFIRMED and reclassified S1** — spawning requires Task tool which is absent from the tools list | A3 |
| #9 | SSV checkpoint missing from Model Assignments table — S2 Dead doc | **CONFIRMED** | A4 |
| #12 | sync-to-claude.sh exclusions/extras not described in GLOSSARY — S3 Undocumented | **PARTIALLY CONFIRMED** — sync-to-claude.sh behavior (what it includes/excludes) is not documented in GLOSSARY. The pre-push hook entry (GLOSSARY line 58) says "syncs `agents/*.md` to `~/.claude/agents/` and `orchestration/` files to `~/.claude/orchestration/`" but does not mention: the `_archive/` exclusion, the selective script sync (only 2 of 6 scripts), the CLAUDE.md sync, or the `--delete` omission policy. This is an undocumented gap in the GLOSSARY entry, but it is described in inline comments in sync-to-claude.sh itself (lines 23–44). Because the GLOSSARY entry is a summary rather than a specification, the gap is S3 cosmetic rather than misleading. |

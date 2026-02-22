# Audit Findings: Domains F + G + H (Session Artifacts + CLAUDE.md + README/CONTRIBUTING)
**Audited:** 2026-02-21
**Checks performed:** 18 (F1–F4, G1–G3, H1–H3, plus sub-checks within each)
**Findings:** 12 (S1: 0, S2: 7, S3: 5)

---

## Findings

### F1a: Session directory `mkdir` omits `review-reports` and `review-skeletons`
- **Category**: DEAD DOC
- **Severity**: S3
- **Intent**: Accidental
- **Doc source**: `/Users/correy/projects/ant-farm/orchestration/RULES.md`:336 — `mkdir -p "${SESSION_DIR}"/{task-metadata,previews,prompts,pc,summaries}`
- **Impl source**: All 13 `_session-*` directories — actual contents include `review-reports/` (present in 10/13 sessions) and `review-skeletons/` (present in 6/13 sessions with reviews), neither of which appear in the `mkdir` command.
- **Impact**: The Session Directory section gives the impression those are the only subdirectories. New readers don't know `review-reports/` and `review-skeletons/` will appear. (Both are created later: `review-reports` by the `mkdir -p` at Step 3b-iii line 175, `review-skeletons` by `compose-review-skeletons.sh`.)
- **Suggested fix**: Add a note beneath the `mkdir` block: "Additional subdirectories (`review-skeletons/`, `review-reports/`) are created during review phases; see Steps 2 and 3b-iii."

---

### F1b: `briefing.md` and `session-summary.md` present in sessions but absent from Session Directory artifact list
- **Category**: UNDOCUMENTED
- **Severity**: S3
- **Intent**: Accidental
- **Doc source**: `/Users/correy/projects/ant-farm/orchestration/RULES.md`:343–349 — the artifact list (`queen-state.md`, `orchestrator-state*.md`, `step3b-transition-gate.md`, `HANDOFF-*.md`, `progress.log`, `resume-plan.md`) does not mention `briefing.md` or `session-summary.md`.
- **Impl source**: All 13 `_session-*` directories contain `briefing.md` (written by the Scout; referenced in RULES.md line 86 and 99 but not in the artifact list). `session-summary.md` appears in 5 sessions (`_session-068ecc83`, `_session-7edaafbb`, `_session-3a20de`, `_session-cd9866`, `_session-8ae30b`) and is documented in `/Users/correy/projects/ant-farm/orchestration/templates/pantry.md`:184 but not in RULES.md.
- **Impact**: The artifact list is incomplete. Someone reading it would not know these files exist or what created them.
- **Suggested fix**: Add `briefing.md` and `session-summary.md` to the Session Directory artifact list in RULES.md lines 343–349 with one-line descriptions of who writes them.

---

### F2/Finding-4: `orchestrator-state*.md` listed as session artifact, never created
- **Category**: DEAD DOC
- **Severity**: S2
- **Intent**: Accidental
- **Doc source**: `/Users/correy/projects/ant-farm/orchestration/RULES.md`:345 — `- \`orchestrator-state*.md\` — orchestrator snapshots`
- **Impl source**: `find /Users/correy/projects/ant-farm/.beads/agent-summaries/ -name "orchestrator-state*.md"` → no output (not found in any of the 13 `_session-*` directories)
- **Impact**: Readers expect to find orchestrator snapshots when examining session artifacts. The file is never written, making the entry misleading for debugging or recovery scenarios.
- **Suggested fix**: Remove the entry or replace it with `queen-state.md` if that is the intended artifact (see `orchestration/templates/queen-state.md`).

---

### F2/Finding-5: `step3b-transition-gate.md` listed as session artifact, never created
- **Category**: DEAD DOC
- **Severity**: S2
- **Intent**: Accidental
- **Doc source**: `/Users/correy/projects/ant-farm/orchestration/RULES.md`:346 — `- \`step3b-transition-gate.md\` — review transition gate`
- **Impl source**: `find /Users/correy/projects/ant-farm/.beads/agent-summaries/ -name "step3b-transition-gate.md"` → no output (not found in any of the 13 `_session-*` directories)
- **Impact**: The transition gate check is documented in RULES.md Step 3b ("Before launching reviews, verify: all agents completed, all DMVDC checks passed, git log shows expected commits") but produces no artifact. Anyone looking for this file to verify a session completed the gate will find nothing.
- **Suggested fix**: Either write this file when the transition gate passes (trivial: `echo "PASS|$(date -u ...)" > ${SESSION_DIR}/step3b-transition-gate.md`) or remove the entry from the artifact list.

---

### F2/Finding-6: `HANDOFF-*.md` listed as session artifact, never created
- **Category**: DEAD DOC
- **Severity**: S2
- **Intent**: Accidental
- **Doc source**: `/Users/correy/projects/ant-farm/orchestration/RULES.md`:347 — `- \`HANDOFF-*.md\` — handoff documents`
- **Impl source**: `find /Users/correy/projects/ant-farm/.beads/agent-summaries/ -name "HANDOFF-*.md"` → no output (not found in any `_session-*` directory). Note: one session (`_session-8ae30b`) contains `EXECUTION_HANDOFF.md` at the top level of the session dir — not a `HANDOFF-*.md` — and appears to be a one-off artifact not in any documented pattern.
- **Impact**: Readers attempting to find handoff context from a past session will find nothing. The pattern `HANDOFF-*.md` is never written by any current workflow step.
- **Suggested fix**: Remove the entry or update it to reflect the actual file that was written (`EXECUTION_HANDOFF.md` in `_session-8ae30b` suggests some earlier workflow wrote this differently).

---

### F3: `progress.log` format matches documentation
*(See Checks That Passed section — this is a MATCH.)*

---

### F4: `_session-3be37d` referenced in MEMORY.md does not exist
- **Category**: DEAD DOC
- **Severity**: S3
- **Intent**: Accidental
- **Doc source**: `/Users/correy/.claude/projects/-Users-correy-projects-ant-farm/memory/MEMORY.md`:51 — "The global `~/.claude/CLAUDE.md` was synced to match in session 3be37d after accidentally deleting a session directory."
- **Impl source**: `ls /Users/correy/projects/ant-farm/.beads/agent-summaries/ | grep "3be37d"` → no output. The 13 actual `_session-*` directories are: `_session-068ecc83`, `_session-3a20de`, `_session-405acc`, `_session-50c2c6`, `_session-54996f`, `_session-7edaafbb`, `_session-8ae30b`, `_session-8b93f5`, `_session-a658ad`, `_session-ad3280`, `_session-b1bbe3`, `_session-cd9866`, `_session-dfc8d3`.
- **Impact**: The session referenced in MEMORY.md as the one that "accidentally deleted a session directory" and triggered retention policy does not exist in the artifact directory. This is consistent with it having been the deleted session referenced in the story, but the reference in MEMORY.md is a non-recoverable historical pointer.
- **Suggested fix**: Cosmetic only. No action required — the memory entry is a historical note, not a pointer to a recoverable artifact.

---

### G1: CLAUDE.md files are identical
*(See Checks That Passed section — this is a MATCH.)*

---

### G2: `bd` prohibition wording differs slightly between CLAUDE.md and RULES.md but scope is consistent
- **Category**: CONTRADICTION (minor wording)
- **Severity**: S3
- **Intent**: Accidental — likely a copy drift over time
- **Doc source (CLAUDE.md)**: `/Users/correy/projects/ant-farm/CLAUDE.md`:38 — `- NEVER run \`bd show\`, \`bd ready\`, \`bd list\`, \`bd blocked\`, or any \`bd\` query command. The Scout subagent does this.`
- **Doc source (RULES.md)**: `/Users/correy/projects/ant-farm/orchestration/RULES.md`:16 — `- **NEVER** run \`bd show\`, \`bd ready\`, \`bd list\`, \`bd blocked\`, or any \`bd\` query command — the Scout does this`
- **Impact**: Functionally identical — both enumerate the same four commands and include the "any bd query command" catch-all. The only differences are formatting (`**NEVER**` vs `NEVER`) and attribution phrasing ("The Scout subagent does this" vs "the Scout does this"). Not a breaking difference but deviates from a stricter reading that the two files should be verbatim-consistent on prohibitions.
- **Suggested fix**: Normalize wording across both files for consistency. Prefer "The Scout subagent does this." as it is more explicit.

---

### G3a: MEMORY.md "Project Structure" section stale — colony-tsa.md listed as "being eliminated"
- **Category**: DEAD DOC
- **Severity**: S3
- **Intent**: Accidental — the "Completed: Colony TSA Eliminated" section at line 57 correctly records completion, but the "Project Structure" section at line 28 was never updated to remove the stale entry.
- **Doc source**: `/Users/correy/.claude/projects/-Users-correy-projects-ant-farm/memory/MEMORY.md`:28 — `- \`orchestration/templates/colony-tsa.md\` — Colony TSA (being eliminated, see HANDOFF)`
- **Impl source**: `ls /Users/correy/projects/ant-farm/orchestration/templates/colony-tsa.md` → `NOT FOUND in templates`. The file is at `/Users/correy/projects/ant-farm/orchestration/_archive/colony-tsa.md` (confirmed by `ls`).
- **Impact**: The "Project Structure" section of MEMORY.md still lists colony-tsa.md at its old path as an active file "being eliminated." Someone reading this section (before reading the "Completed" section below it) would form a false picture of the current state.
- **Suggested fix**: Update the "Project Structure" section to remove the colony-tsa.md entry or replace with `orchestration/_archive/colony-tsa.md — Colony TSA (archived; replaced by direct Queen → Pest Control spawns)`.

---

### G3b: MEMORY.md "One Team Per Session" constraint not documented in RULES.md, CLAUDE.md, or CONTRIBUTING.md
- **Category**: UNDOCUMENTED
- **Severity**: S2
- **Intent**: Accidental — the constraint was captured in MEMORY.md but never propagated to operator-facing docs.
- **Doc source**: `/Users/correy/.claude/projects/-Users-correy-projects-ant-farm/memory/MEMORY.md`:19–21 — "Claude Code only supports one TeamCreate per session. The Nitpicker team (4 reviewers + Big Head) uses this slot. QA coordination (Pantry ↔ Pest Control) must use file-based handoff, not teams."
- **Impl source**: `grep -n "one team\|One Team\|one TeamCreate\|team per session" /Users/correy/projects/ant-farm/orchestration/RULES.md -i` → no output. Not mentioned in CLAUDE.md or CONTRIBUTING.md either.
- **Impact**: An operator extending the workflow (e.g., trying to create a second TeamCreate for a QA coordination team) will encounter a runtime failure with no prior warning in any authoritative doc. This constraint shapes the entire architecture (why PC must be a Nitpicker team member, why file-based handoff is used) but is only recorded in the private MEMORY file.
- **Suggested fix**: Add a note to RULES.md Step 3b-iv: "Note: Claude Code supports only one TeamCreate per session. Pest Control is included as a team member (not spawned separately after) because a second TeamCreate for a standalone PC spawn would fail."

---

### G3c: MEMORY.md "Custom Agents Require Process Restart" documented in CONTRIBUTING.md but "minimum file requirements still TBD" claim is stale
- **Category**: DEAD DOC
- **Severity**: S3
- **Intent**: Accidental
- **Doc source**: `/Users/correy/.claude/projects/-Users-correy-projects-ant-farm/memory/MEMORY.md`:17 — "Minimum file requirements still TBD — short files (9 lines) failed while full-body agents (200+ lines) work. Needs more testing to find the threshold."
- **Impl source**: `/Users/correy/projects/ant-farm/CONTRIBUTING.md`:33–35 — "Claude Code loads agent files once at startup. Adding or editing an agent file requires a full quit and reopen of Claude Code." The "minimum file requirements TBD" caveat is absent from CONTRIBUTING.md, which means either the issue was resolved and MEMORY.md was never updated, or CONTRIBUTING.md is missing a useful warning.
- **Impact**: If the threshold was discovered and file size is no longer an issue, the MEMORY.md note is misleading. If the threshold is still unknown, CONTRIBUTING.md is missing a warning that short agent files may fail silently.
- **Suggested fix**: Determine current status. If file size is no longer a constraint, remove the caveat from MEMORY.md. If still relevant, add a warning to CONTRIBUTING.md.

---

### H1a: README describes Scout as "a sonnet subagent" but RULES.md assigns it `opus`
- **Category**: CONTRADICTION
- **Severity**: S2
- **Intent**: Accidental — README was not updated when Scout was promoted from sonnet to opus.
- **Doc source**: `/Users/correy/projects/ant-farm/README.md`:75 — "The Queen spawns **the Scout** (`orchestration/templates/scout.md`), a sonnet subagent that performs all pre-flight reconnaissance"
- **Impl source**: `/Users/correy/projects/ant-farm/orchestration/RULES.md`:76 — "`scout-organizer` subagent, `model: \"opus\"`" and line 294 — `| Scout | Task (\`scout-organizer\`) | opus | Orchestration role |`
- **Impact**: A reader building mental model from the README will assume Scout runs on sonnet. When they observe the Queen's tool call using `model: "opus"` for the Scout, it will contradict their expectations. GLOSSARY.md line 80 also incorrectly lists Scout model as "sonnet", compounding the error.
- **Suggested fix**: Change README line 75 "a sonnet subagent" to "an opus subagent" (or simply "a subagent"). Also update GLOSSARY.md line 80 `| **Scout** | ... | sonnet |` to `| **Scout** | ... | opus |`.

---

### H1b: README and RULES.md contradict each other on Nitpicker team composition
- **Category**: CONTRADICTION
- **Severity**: S2
- **Intent**: Accidental — README was not updated when Pest Control was added as a team member.
- **Doc source**: `/Users/correy/projects/ant-farm/README.md`:59 — `│  the Nitpickers (4 reviewers + Big Head)                │` and line 218 — `├──create Nitpicker team (4 reviewers + Big Head)──►`. Also README line 201 says "the Queen spawns **Pest Control**" after the team completes, implying PC is separate.
- **Impl source**: `/Users/correy/projects/ant-farm/orchestration/RULES.md`:179 — "Round 1: 6 members — 4 reviewers + Big Head + Pest Control" and line 182 — "Pest Control MUST be a team member so Big Head can SendMessage to it" and line 184 — "After team completes, DMVDC and CCB have already run inside the team"
- **Impact**: Following the README Step 3b flow diagram, an operator would spawn a 5-member team (4 reviewers + Big Head) and then separately spawn Pest Control. Per RULES.md, the correct architecture is a 6-member team with PC inside it. If the operator follows the README, Big Head cannot `SendMessage` to PC (they are not on the same team), breaking the team-internal DMVDC/CCB flow.
- **Suggested fix**: Update the README architecture diagram, Step 3b narrative, and flow diagram to reflect: 6-member Nitpicker team (4 reviewers + Big Head + Pest Control); DMVDC and CCB run inside the team; the Queen does NOT spawn a separate PC after the team completes.

---

### H2: CONTRIBUTING.md "cross-file updates when adding an agent" omits GLOSSARY.md
- **Category**: DEAD DOC
- **Severity**: S3
- **Intent**: Accidental
- **Doc source**: `/Users/correy/projects/ant-farm/CONTRIBUTING.md`:37–41 — the cross-file update checklist when adding an agent lists only (1) README.md "Custom agents" table, (2) RULES.md "Agent Types" and "Model Assignments" tables, (3) scout.md (noted as usually unnecessary).
- **Impl source**: `/Users/correy/projects/ant-farm/orchestration/GLOSSARY.md`:77–85 — the "Ant Metaphor Roles" table lists all six agents with agent file paths, model assignments, and role descriptions. Adding a new agent type without updating this table leaves the GLOSSARY inconsistent.
- **Impact**: A contributor adding an agent following CONTRIBUTING.md will omit the GLOSSARY.md "Ant Metaphor Roles" table update, leaving that table stale.
- **Suggested fix**: Add step 2.5 to the cross-file update checklist: "`orchestration/GLOSSARY.md` — add the agent to the 'Ant Metaphor Roles' table."

---

### H3/Finding-11: SESSION_PLAN_TEMPLATE.md references "Boss-Bot: Claude Sonnet 4.5"
- **Category**: DEAD DOC
- **Severity**: S3
- **Intent**: Accidental — template predates the renaming of the orchestrator role from "Boss-Bot" to "the Queen."
- **Doc source**: `/Users/correy/projects/ant-farm/orchestration/templates/SESSION_PLAN_TEMPLATE.md`:8 — `**Boss-Bot:** Claude Sonnet 4.5` and line 340 — `- Implementation files read in boss-bot window: ___ (target: <10)` and line 342 — `- Boss-bot stayed focused: ✅ / ❌`
- **Impl source**: `/Users/correy/projects/ant-farm/orchestration/RULES.md` and README.md use "the Queen" throughout. No current documentation uses "Boss-Bot." The current model is also incorrect: RULES.md line 294 assigns opus to the Scout, and the Queen itself runs on opus per its role as top-level Claude Code session.
- **Impact**: A user copying this template to plan a new session will see "Boss-Bot" (stale name) and "Claude Sonnet 4.5" (stale model). The template instructs them to track "boss-bot window" reads, which maps to the Queen. The model name `Sonnet 4.5` is also stale — current RULES.md uses generic model tier names (`opus`, `sonnet`, `haiku`), not specific version strings.
- **Suggested fix**: Replace all instances of "Boss-Bot" / "boss-bot" with "Queen" / "the Queen". Replace "Claude Sonnet 4.5" with either a generic tier ("opus") or remove the model field and point readers to the RULES.md Model Assignments table.

---

## Checks That Passed (MATCHes)

**F1 (session directory structure)**: The five subdirectories created by the `mkdir -p` at RULES.md:336 (`task-metadata`, `previews`, `prompts`, `pc`, `summaries`) are present in all or nearly all sessions examined. `_session-068ecc83` and `_session-7edaafbb` both contain all five. The presence of additional undocumented dirs (review-reports, review-skeletons) is logged as F1a/F1b above.

**F3 (progress.log format)**: The documented format (`RULES.md`:348) is "one pipe-delimited line per completed step." The actual `_session-068ecc83/progress.log` contains 11 lines in the format `TIMESTAMP|EVENT_TYPE|key=value|...` matching the exact shell command templates in RULES.md lines 60, 99, 116, 124, 221, 242, 245, 248, 251. Format is fully consistent.

**F4 (session count)**: 13 `_session-*` directories exist under `.beads/agent-summaries/`. No documentation specifies a maximum or target count, so this is informational only. The CLAUDE.md Landing section (line 72) correctly states "Session artifacts in .beads/agent-summaries/_session-*/ are retained for posterity."

**G1 (CLAUDE.md identity)**: `/Users/correy/projects/ant-farm/CLAUDE.md` and `/Users/correy/.claude/CLAUDE.md` are byte-for-byte identical (both 81 lines, identical content). The sync mechanism (pre-push hook via `sync-to-claude.sh`) is working correctly.

**G2 (bd prohibition scope)**: Both CLAUDE.md:38 and RULES.md:16 enumerate the same four prohibited commands (`bd show`, `bd ready`, `bd list`, `bd blocked`) plus "any bd query command." The scope of the prohibition is consistent across both files. (Minor wording drift logged as G2 finding above.)

**G3 (MEMORY.md factual claims — mostly verified)**:
- "Colony TSA replaced" → CONFIRMED: `/Users/correy/projects/ant-farm/orchestration/_archive/colony-tsa.md` exists.
- "Session artifacts retained" → CONFIRMED: CLAUDE.md:72 "Session artifacts in .beads/agent-summaries/_session-*/ are retained for posterity."
- "Never Use run_in_background on Task Agents" → CONFIRMED: CLAUDE.md:40 "NEVER set `run_in_background` on Task agents."
- "bd dep add --type parent-child syntax" → CONFIRMED: `bd dep add --help` shows `-t, --type string` with `parent-child` as a valid type. The positional argument order (child first, epic second) matches documented `bd dep add <child-id> <epic-id>` syntax.

**H1 (README architecture roles)**: All roles described in the README ("Queen," "Scout," "Pantry," "Pest Control," "Dirt Pushers," "Nitpickers," "Big Head") exist as agent files (`agents/`) or as documented orchestrator roles. No phantom roles exist. Agent file names in the "Custom agents" table match actual `agents/` directory contents: `scout-organizer.md`, `pantry-impl.md`, `pest-control.md`, `nitpicker.md`, `big-head.md`.

**H1 (pantry-review deprecation)**: README:309 correctly marks `pantry-review` as `**DEPRECATED**` with a note it was replaced by `fill-review-slots.sh`. No `pantry-review.md` exists in `agents/` (only in `orchestration/_archive/`). RULES.md Agent Types table does not include pantry-review. This is consistent.

**H2 (CONTRIBUTING.md checkpoint cross-file updates)**: The "Adding a New Checkpoint" checklist in CONTRIBUTING.md:51–64 correctly lists RULES.md Hard Gates table and Model Assignments table as update targets.

**H3 (AGENTS.md bd command syntax)**: `/Users/correy/projects/ant-farm/AGENTS.md` contains `bd update <id> --status in_progress`. The actual `bd update --help` confirms `-s, --status string` is a valid flag, and the long form `--status` with a space-separated value (`--status in_progress`) is standard CLI usage. `bd close <id>` is also confirmed valid per `bd close --help`. The AGENTS.md `bd` examples are syntactically correct.

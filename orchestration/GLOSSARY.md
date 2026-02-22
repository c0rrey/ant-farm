# ant-farm Glossary

Canonical definitions for all framework terms, checkpoint acronyms, and ant metaphor role names used across the orchestration system. This document is the single source of truth — when a term appears in `RULES.md`, `checkpoints.md`, `reviews.md`, or any template, its meaning is defined here.

---

## Naming Conventions

### Agent Names: Casing and Article Usage

Agent role names are title-case proper nouns. When preceded by a definite article in prose, the article is lowercase:

| Context | Correct | Incorrect |
|---------|---------|-----------|
| Mid-sentence prose | "the Queen spawns agents" | "The Queen spawns agents" |
| Mid-sentence prose | "the Scout writes the briefing" | "The Scout writes the briefing" |
| Mid-sentence prose | "the Pantry composes prompts" | "The Pantry composes prompts" |
| Mid-sentence prose | "the Nitpickers review the work" | "The Nitpickers review the work" |
| Sentence start | "The Queen reads the briefing" | n/a (sentence start is always capitalized) |
| Section/document header | "The Queen's Session State" | n/a (headers use title case) |

**Summary of the rule**: lowercase article ("the"), title-case role name ("Queen", "Scout", "Pantry", "Nitpickers", "Big Head"). The article is only capitalized when it begins a sentence or appears in a title or heading.

### Filenames

Agent definition files and orchestration template files use kebab-case:

- Agent files: `scout-organizer.md`, `pantry-impl.md`, ~~`pantry-review.md`~~ (deprecated; see RULES.md Step 3b), `pest-control.md`, `nitpicker.md`, `big-head.md`
- Template files: `dirt-pusher-skeleton.md`, `nitpicker-skeleton.md`, `big-head-skeleton.md`, `queen-state.md`

### Role Names Without Article

In tables, diagrams, and other non-prose contexts where the article is omitted, role names are title-case without a preceding article:

- Table column value: "Queen", "Scout", "Pantry", "Pest Control", "Big Head", "Nitpicker"
- ASCII diagram labels: "the Queen (orchestrator)" — article included for readability; lowercase

---

## Workflow Concepts

| Term | Definition |
|------|------------|
| **session** | A single invocation of the orchestration system, from "let's get to work" through `git push`. Identified by a unique session ID and backed by a session directory (`.beads/agent-summaries/_session-<id>/`). |
| **wave** | A batch of implementation agents that run concurrently within a session. Wave boundaries are chosen to avoid file conflicts: tasks that touch the same file are placed in different waves. Wave N+1 does not start until all agents in wave N have committed and passed WWD. |
| **checkpoint** | A mandatory verification gate that blocks the next phase of work until it returns PASS (or an approved WARN). There are four checkpoints: CCO, WWD, DMVDC, and CCB. |
| **scope boundary** | The explicit list of files and line ranges an agent is permitted to edit. Defined in the agent's data file. Changes outside the scope boundary are a WWD violation. |
| **data file** | A per-task artifact written by the Pantry that contains the task's scope boundaries, affected files, root cause, acceptance criteria, agent type, and off-limits areas. The agent reads this file at Step 0. |
| **briefing** | A ~40-line summary written by the Scout to `{session-dir}/briefing.md`. Contains ready/blocked task counts, proposed execution strategies with wave groupings, risk assessments, and agent type recommendations. The Queen reads only this — not raw task data. |
| **preview file** | A combined file written by the Pantry to `{session-dir}/previews/` that merges the agent prompt skeleton with the task's data file. Pest Control audits these under CCO before the Queen spawns any agent. |
| **verdict** | The outcome of a checkpoint audit. Valid values: PASS, WARN (CCO and WWD only), PARTIAL (DMVDC and CCB only), or FAIL. See `checkpoints.md` for per-checkpoint thresholds. |
| **information diet** | The design constraint that the Queen never reads source code, tests, configs, or implementation templates. It reads only the Scout's briefing, agent notifications, commit messages, and verdict tables. |
| **escalation** | When a failing agent or stuck checkpoint exceeds its retry limit and the Queen surfaces the problem to the user with full context rather than retrying again. |
| **adjacent issue** | A defect or improvement opportunity noticed by an agent that falls outside its scope boundary. Agents document these in their summary docs but do not fix them. |
| **summary doc** | A structured artifact written by each agent to `{session-dir}/summaries/<task-suffix>.md` at Step 6. Required sections: approaches considered, selected approach, implementation description, correctness review, build/test validation, and acceptance criteria checklist. |
| **hard gate** | A checkpoint that must return PASS before the system proceeds to the next phase. All four checkpoints (CCO, WWD, DMVDC, CCB) are hard gates. |
| **context window** | The token budget available to a model in a single session. The Queen's information diet keeps its context window clean by offloading reads to subagents. |
| **pre-push hook** | A git hook that syncs `agents/*.md` to `~/.claude/agents/` and `orchestration/` files to `~/.claude/orchestration/` on every `git push`, keeping the runtime copies in sync with the repo. |

---

## Checkpoint Acronyms

All four checkpoints are executed by Pest Control. Full definitions live in `orchestration/templates/checkpoints.md`.

| Acronym | Expansion | When it runs | What it verifies | Blocks |
|---------|-----------|--------------|------------------|--------|
| **CCO** | Colony Cartography Office | After Pantry composes prompts, before agent spawn | Pre-spawn prompt quality: real task IDs, real file paths with line numbers, root cause text, all 6 mandatory steps, scope boundaries, commit instructions, and line-number specificity | Agent spawn |
| **WWD** | Wandering Worker Detection | After agent commits, before next agent in same wave spawns | Post-commit scope verification: files changed in the commit match the task's expected scope — no scope creep | Next agent in wave |
| **DMVDC** | Dirt Moved vs Dirt Claimed | After agent completes its summary doc | Substance verification: git diff matches summary claims, acceptance criteria are genuinely met, 4 design approaches are substantively distinct, correctness review is specific rather than boilerplate | Task closure |
| **CCB** | Colony Census Bureau | After the Nitpicker team and Big Head complete, before results are presented to the user | Consolidation integrity: finding counts reconcile, every filed issue has required fields, priority calibration is correct, traceability matrix is complete, deduplication is accurate, no unauthorized issues were filed | Presenting results to user |

---

## Ant Metaphor Roles

| Name | Agent file | Model | Role description |
|------|-----------|-------|-----------------|
| **Queen** | _(orchestrator — no agent file; runs as the top-level Claude Code session)_ | opus | The orchestrator. Reads only briefings, verdict tables, commit messages, and agent notifications. Never reads source code or implementation templates. The only agent that pushes to remote. Spawns all subagents and makes all go/no-go decisions. |
| **Scout** | `agents/scout-organizer.md` | opus | Pre-flight reconnaissance agent. Discovers ready and blocked tasks, builds a file modification matrix, assesses conflict risk, recommends specialist agent types, proposes 2–3 execution strategies with wave groupings, and writes the session briefing. |
| **Pantry** | `agents/pantry-impl.md` (implementation), ~~`agents/pantry-review.md`~~ (deprecated; see RULES.md Step 3b) | opus | Prompt composition agent. Reads implementation or review templates, extracts per-task context from Scout metadata, writes data files and combined prompt previews, and returns a file-path table to the Queen. Keeps template content out of the Queen's context. |
| **Pest Control** | `agents/pest-control.md` | haiku (CCO, WWD, CCB), sonnet (DMVDC) | Verification auditor. Runs all four checkpoints (CCO, WWD, DMVDC, CCB) and writes timestamped audit reports to `{session-dir}/pc/`. Cross-checks orchestrator and agent work against ground truth. |
| **Dirt Pusher** | _(spawned via `orchestration/templates/dirt-pusher-skeleton.md` with a specialist `subagent_type`)_ | varies by task | Implementation agent. Executes exactly 6 mandatory steps: claim, design, implement, review, commit, summary doc. Constrained to its scope boundary. Documents adjacent issues without fixing them. |
| **Nitpicker** | `agents/nitpicker.md` | sonnet | Code review agent. Reads all changed files, catalogs findings with file:line references and severity, groups findings into preliminary root causes, and writes a structured review report. There are four Nitpicker specializations: Clarity (P3), Edge Cases (P2), Correctness (P1–P2), and Excellence (P3). Does not file issues — only Big Head does. |
| **Big Head** | `agents/big-head.md` | opus | Consolidation reviewer. Reads all four Nitpicker reports, merges duplicate findings, groups by root cause, documents merge rationale, files one issue per root cause with all affected surfaces, and writes a consolidated summary with deduplication log and priority breakdown. |

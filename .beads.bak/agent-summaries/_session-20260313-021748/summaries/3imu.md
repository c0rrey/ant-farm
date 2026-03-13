# Summary: ant-farm-3imu — Write /ant-farm:init skill definition

**Commit**: 4429953
**File created**: skills/init.md

---

## 1. Approaches Considered

**Approach A — Shell-command-heavy**: Every step expressed as bash scripts the model executes verbatim. Maximum determinism for shell execution, explicit file creation via heredocs. Downside: verbose, brittle across macOS/Linux PATH differences, embeds all template content inline making the skill hard to update.

**Approach B — Declarative prose only**: Natural language instructions with no bash snippets. Very readable and concise. Downside: ambiguous idempotency semantics — the model may interpret "check if it exists" differently on each run, reducing reliability and consistency.

**Approach C — Mixed: prose steps with targeted bash snippets** (selected): Prose-driven step narrative with embedded bash snippets only where precision matters — existence checks, gitignore manipulation, PATH verification. Follows the exact pattern established in `skills/work.md`. Balances readability with precision and matches the existing skill authoring convention.

**Approach D — Template-file-driven with heredoc embeds**: The skill instructs the model to emit exact file contents via heredocs. Very precise for config.json schema, but forces schema into the skill document — schema drift requires updating the skill. Also makes the document harder to scan and understand.

---

## 2. Selected Approach

**Approach C — Mixed prose + targeted bash snippets.**

Rationale: `skills/work.md` established a clear convention for skill authoring in this project. It uses prose for step narration, bash code blocks for precise shell operations (existence checks, directory creation), and blockquote formatting for user-facing messages. Matching this convention makes the new skill immediately legible to maintainers familiar with `work.md`. The mixed approach also allows precise idempotency checks (bash) while keeping the overall flow human-readable (prose), which is important since skill files are authored for model consumption and human review simultaneously.

---

## 3. Implementation Description

`skills/init.md` was written as a 9-step skill definition:

- **Frontmatter** (YAML): `name: ant-farm-init`, description with trigger phrases, `version: 1.0.0`
- **Trigger Conditions** section listing activation phrases
- **Step 0**: Already-initialized check — enters idempotent repair mode rather than aborting
- **Step 1**: Language/stack detection via file presence checks; derives `DERIVED_PREFIX` from directory name
- **Step 2**: `mkdir -p` for `.crumbs/sessions/` and `.crumbs/history/` (idempotent by nature)
- **Step 3**: Interactive prefix prompt with auto-derived default, validation rules
- **Step 4**: `tasks.jsonl` creation guarded by `[ -f ... ] || touch`
- **Step 5**: `config.json` creation guarded by existence check; JSON template with prefix, `default_priority: P2`, `counters: {task: 1, trail: 1}`, language, timestamp
- **Step 6**: `.gitignore` update appending `.crumbs/sessions/` only (not `.crumbs/`); guarded by `grep -qF`
- **Step 7**: crumb.py installation — `command -v crumb` check, find-in-repo, copy to `~/.local/bin/crumb`, `chmod +x`, post-install PATH verification with shell profile instructions
- **Step 8**: Agent type suggestion table keyed by detected language
- **Step 9**: Initialization summary with per-item status and next-step instructions
- **Error Reference** table covering all failure modes

---

## 4. Correctness Review

### skills/init.md

Reviewed line by line. Key checks:

- **Frontmatter valid**: `name`, `description`, `version` fields present with correct values. Trigger phrases in description match the "Trigger Conditions" section.
- **Directory creation**: `mkdir -p .crumbs/sessions` and `mkdir -p .crumbs/history` cover both required subdirectories. Parent `.crumbs/` is implicitly created by `mkdir -p`.
- **tasks.jsonl**: Created via `touch` guarded by `[ -f ... ] ||` — will not overwrite on re-run.
- **config.json**: JSON template contains `prefix`, `default_priority: "P2"`, `counters: {task: 1, trail: 1}`. Creation guarded by `[ -f ... ]` check.
- **gitignore**: Appends `.crumbs/sessions/` specifically (not `.crumbs/`). Guarded by `grep -qF` — no duplicate entries on re-run.
- **crumb.py installation**: `command -v crumb` guards skip; `find . -maxdepth 3 -name 'crumb.py'` locates source; `cp` + `chmod +x` installs; post-install `command -v crumb` verifies PATH.
- **Idempotency**: All file-creation steps are individually guarded. Step 0 explicitly enters repair mode on re-run rather than aborting. No step can destroy existing data.

No issues found.

---

## 5. Build/Test Validation

This task creates a documentation/skill file only — no Python, test suite, or build system is involved. No automated tests applicable. Manual review of the file content performed in Step 4 above.

---

## 6. Acceptance Criteria Checklist

- [x] **skills/init.md exists with correct skill frontmatter (name, description, trigger pattern)** — PASS. Lines 1-5: `name: ant-farm-init`, description with `/ant-farm:init` trigger, `version: 1.0.0`. Trigger patterns in both frontmatter description and Trigger Conditions section.

- [x] **Skill creates .crumbs/tasks.jsonl, .crumbs/config.json, .crumbs/sessions/, .crumbs/history/** — PASS. Step 2 creates sessions/ and history/ via `mkdir -p`. Step 4 creates tasks.jsonl via `touch`. Step 5 creates config.json with explicit JSON content.

- [x] **config.json populated with prefix (prompted or auto-derived), default_priority P2, counters at 1** — PASS. Step 3 prompts with auto-derived default. Step 5 JSON template: `"default_priority": "P2"`, `"counters": {"task": 1, "trail": 1}`.

- [x] **.crumbs/sessions/ added to .gitignore (not the whole .crumbs/)** — PASS. Step 6 appends `.crumbs/sessions/` specifically with a comment. Explicitly notes "Data files (tasks.jsonl, config.json, history/) remain tracked."

- [x] **crumb.py installation step included with PATH verification** — PASS. Step 7: `command -v crumb` check, find-in-repo, `cp` + `chmod +x`, post-install `command -v crumb` verification, shell profile instructions if not on PATH.

- [x] **Idempotent: re-running on existing .crumbs/ doesn't overwrite data** — PASS. Step 0 detects existing init and continues in repair mode. Steps 4 and 5 use `[ -f ... ]` guards. Step 6 uses `grep -qF` guard. `mkdir -p` is inherently idempotent.

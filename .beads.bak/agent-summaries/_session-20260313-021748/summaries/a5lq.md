# Task Summary: ant-farm-a5lq
**Task**: Write /ant-farm:plan skill definition
**Commit**: 467aa6e
**File created**: skills/plan.md

---

## 1. Approaches Considered

**Approach A — Minimal Router**
A thin skill with only frontmatter and a single delegation step to RULES-decompose.md. No embedded logic — all behavior lives in the decompose rules file.
- Pro: Maximally thin, zero duplication.
- Con: No pre-flight gate layer; unhelpful errors if RULES-decompose.md is absent or .crumbs/ uninitialized; all input handling pushed into the decompose workflow.

**Approach B — Self-Contained Workflow**
Embed the full decomposition workflow inline in plan.md — spec parsing, task creation via `crumb create`, and dependency linking all in one file.
- Pro: Single file is fully self-documenting.
- Con: Duplicates logic that RULES-decompose.md should own; any change to decomposition strategy requires editing plan.md rather than one rules file.

**Approach C — Hybrid Gate + Delegate (selected)**
The skill owns the entry gate: pre-flight checks, input type detection, input classification, DECOMPOSE_DIR creation, and explicit handoff to RULES-decompose.md with documented context variables. The decompose rules own the parsing and task creation.
- Pro: Clean separation of concerns; mirrors the established init.md/work.md pattern; each acceptance criterion maps to an explicit step.
- Con: Two-file coordination, but this is the intended architecture per the task description.

**Approach D — Conversational Intake**
Before routing, ask the user clarifying questions (desired output types, priority levels, epic grouping preferences) via interactive prompts.
- Pro: More targeted output from the decompose workflow.
- Con: Adds latency and UX friction; these decisions belong in the decompose rules, not the gate skill; inconsistent with the one-shot usage pattern of other skills.

---

## 2. Selected Approach

**Approach C — Hybrid Gate + Delegate.**

Rationale: The task description explicitly lists acceptance criteria that map 1:1 to gate responsibilities (pre-flight check, input detection, classification, DECOMPOSE_DIR, routing). The existing skills (init.md, work.md) both follow the same gate-then-delegate pattern. Keeping decomposition execution in RULES-decompose.md allows that file to evolve independently without changing the plan.md trigger skill.

---

## 3. Implementation Description

Created `skills/plan.md` with:

- **YAML frontmatter**: `name`, `description`, `version` — matching the format of init.md and work.md.
- **Trigger Conditions**: Lists invocation patterns including slash command, natural-language triggers ("plan this", "decompose this spec", etc.).
- **Step 0 — Pre-flight Error Handling**: Two fatal checks — `.crumbs/` not initialized (checks both `tasks.jsonl` and `config.json`), and no argument provided (with usage message showing both file and inline modes).
- **Step 1 — Detect Input Type**: File path heuristic (leading `/./..`, doc extensions, no whitespace + file exists); reads file via `cat` if file path, stores as inline if not; errors on file-not-found and empty-after-read.
- **Step 2 — Classify Input**: 6-signal scoring table (headings, lists, acceptance criteria, requirements language, numbered sections, technical specificity). Threshold: 3 = STRUCTURED, 2 or fewer = FREEFORM. Surfaces classification and score to user.
- **Step 3 — Create DECOMPOSE_DIR**: `date +%Y%m%d-%H%M%S` timestamp naming under `.crumbs/sessions/_decompose-${DECOMPOSE_ID}`. Writes `manifest.json` (id, source, class, score, timestamp) and `input.txt` (raw spec content).
- **Step 4 — Route to RULES-decompose.md**: Explicit read instruction with context variables to pass (`DECOMPOSE_DIR`, `INPUT_CLASS`, `INPUT_TEXT`). Documents the decompose workflow's responsibilities.
- **Error Reference table**: 8 conditions covering all acceptance criteria error cases plus additional edge cases (RULES-decompose.md not found, mkdir failure, crumb CLI missing).

---

## 4. Correctness Review

**File: skills/plan.md**

Line-by-line review:
- Frontmatter (lines 1-5): `name: ant-farm-plan`, `version: 1.0.0`, description captures all trigger patterns. Matches format of init.md and work.md exactly.
- Trigger Conditions (lines 11-17): Covers slash command, file path arg, inline text arg, and natural language variants.
- Step 0 (lines 19-46): Two distinct fatal conditions with hard stops. `.crumbs/` check tests both required files (tasks.jsonl and config.json), consistent with init.md's own check.
- Step 1 (lines 48-85): File path heuristics are clearly enumerated. `cat` command reads file. `INPUT_SOURCE` set to `"file:<ARGUMENT>"` for file path, `"inline"` for inline text — used in Step 3 manifest and Step 2 output.
- Step 2 (lines 87-113): Heuristic table has 6 distinct signals covering structured spec markers. Threshold of 3/6 is documented. User-facing output includes score for transparency.
- Step 3 (lines 114-146): `date +%Y%m%d-%H%M%S` is consistent with `work.md`'s `SESSION_ID` pattern. Manifest JSON captures all classification metadata. `input.txt` uses heredoc to preserve spec content verbatim.
- Step 4 (lines 148-159): Routes to `orchestration/RULES-decompose.md`. Context variables listed. Decompose workflow responsibilities documented (does not over-specify).
- Error Reference (lines 161-173): 8 rows. All 6 acceptance criteria error cases covered. Additional: RULES-decompose.md not found, mkdir failure, crumb CLI missing.

No adjacent-issue fixes. No out-of-scope file edits.

---

## 5. Build/Test Validation

This task creates a markdown skill definition file. There is no compilation step.

Manual consistency checks performed:
- Frontmatter format matches init.md and work.md (name, description, version fields).
- Bash snippets use the same shell idioms as init.md and work.md (bracket tests, heredocs, `date` formatting).
- DECOMPOSE_DIR naming pattern (`.crumbs/sessions/_decompose-TIMESTAMP`) follows the SESSION_DIR pattern from work.md (`.crumbs/sessions/_session-TIMESTAMP`).
- All `INPUT_*` and `DECOMPOSE_*` variable names are used consistently throughout.

---

## 6. Acceptance Criteria Checklist

| Criterion | Status |
|---|---|
| 1. skills/plan.md exists with correct skill frontmatter and trigger pattern | PASS — YAML frontmatter with name/description/version at lines 1-5; Trigger Conditions section at lines 11-17 |
| 2. Accepts file path argument (reads file contents) or inline text | PASS — Step 1 detects file path vs inline text, reads file via `cat`, stores as INPUT_TEXT in both cases |
| 3. Input classification heuristic documented (structured vs freeform detection) | PASS — Step 2 has 6-signal scoring table with threshold (score >= 3 = STRUCTURED) |
| 4. Routes to RULES-decompose.md workflow | PASS — Step 4 reads `orchestration/RULES-decompose.md` and passes DECOMPOSE_DIR, INPUT_CLASS, INPUT_TEXT |
| 5. Creates DECOMPOSE_DIR with timestamp-based naming | PASS — Step 3 uses `date +%Y%m%d-%H%M%S` under `.crumbs/sessions/_decompose-${DECOMPOSE_ID}` |
| 6. Error handling: missing file path, empty input, .crumbs/ not initialized | PASS — Step 0 covers .crumbs/ not initialized and empty input; Step 1 covers file-not-found; Error Reference covers all cases |

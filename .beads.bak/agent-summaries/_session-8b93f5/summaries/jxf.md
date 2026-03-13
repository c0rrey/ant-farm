# Summary: ant-farm-jxf — Create canonical glossary for key terms

## 1. Approaches Considered

**Approach A: Flat alphabetical reference list**
All terms in a single alphabetically sorted list with one-line definitions. Pros: easy to scan when you know the term name, minimal structural overhead. Cons: loses categorical grouping — a reader looking for all checkpoint acronyms must scan the entire list; the three distinct acceptance criteria (workflow terms, checkpoint acronyms, ant roles) map to nothing in the structure.

**Approach B: Three-section document with distinct tables per category**
Separate sections for (1) Workflow Concepts, (2) Checkpoint Acronyms, and (3) Ant Metaphor Roles. Each section uses a markdown table. Pros: the three acceptance criteria map directly to three document sections; readers jump to the category they need; tables provide visual alignment without noise. Cons: slightly more structure than a flat list, but appropriate given the three genuinely different semantic categories.

**Approach C: Single master table with a "Category" column**
One table with columns: Term | Category | Definition. Pros: machine-parseable, single-table consistency. Cons: repetitive "Category" column values create visual noise; loses the visual separation that helps readers orient; harder to extend one category without touching the entire table.

**Approach D: Prose definitions with H3 sub-headings**
Each term gets its own sub-heading and a paragraph-length definition. Pros: room for nuance and cross-references. Cons: significantly more verbose than necessary for a reference document; hard to scan; each definition would be 3–5 lines when 1 line suffices; overkill for the use case.

## 2. Selected Approach

**Approach B (three-section document with distinct tables per category).**

Rationale: The three acceptance criteria map exactly to three natural categories. Separate tables let readers navigate by category rather than scanning the entire document. The Checkpoint Acronyms table adds "When it runs," "What it verifies," and "Blocks" columns because these are the operationally important attributes — expanding an acronym without saying what it does would be less useful than the README's existing inline expansions. The Roles table adds "Agent file" and "Model" columns because these attributes appear in `README.md:L269-276` and belong alongside the role description.

## 3. Implementation Description

Created `/Users/correy/projects/ant-farm/orchestration/GLOSSARY.md` with three sections:

**Section 1 — Workflow Concepts (15 terms):** session, wave, checkpoint, scope boundary, data file, briefing, preview file, verdict, information diet, escalation, adjacent issue, summary doc, hard gate, context window, pre-push hook. Terms derived from `README.md` full-file read with emphasis on terms used without definition at L7, L46, L103-106, and L233-236.

**Section 2 — Checkpoint Acronyms (4 entries):** CCO (Colony Cartography Office), WWD (Wandering Worker Detection), DMVDC (Dirt Moved vs Dirt Claimed), CCB (Colony Census Bureau). Each row includes: full expansion, when it runs, what it verifies, and what it blocks. Sourced from `orchestration/templates/checkpoints.md:L12-36` and verified against `README.md:L17-20` and `L233-236`.

**Section 3 — Ant Metaphor Roles (7 entries):** The Queen, Scout, Pantry, Pest Control, Dirt Pusher, Nitpicker, Big Head. Each row includes: agent file path (with note for roles that have no dedicated agent file), model tier, and role description. Sourced from `README.md:L11-26` (architecture diagram) and `README.md:L269-276` (Custom agents table).

No existing files were modified. No adjacent issues were fixed.

## 4. Correctness Review

**`orchestration/GLOSSARY.md` (created — 53 lines)**

- Line 3: Intro sentence accurately states this is the canonical source and lists the files it serves.
- Line 12 (wave): Definition correctly captures that waves are concurrent batches, that boundaries prevent file conflicts, and that wave N+1 waits for wave N to pass WWD. Cross-checked against README:L46 ("wave") and README:L103-106 (wave monitoring).
- Line 13 (checkpoint): Accurately states "four checkpoints: CCO, WWD, DMVDC, CCB" consistent with README:L233-236 Hard gates table.
- Line 18 (verdict): Lists PASS, WARN (CCO/WWD only), PARTIAL (DMVDC/CCB only), FAIL — consistent with checkpoints.md:L50-60 Common Verdict Definitions.
- Line 19 (information diet): Accurately reflects README:L223-225 word-for-word in substance.
- Lines 35-38 (checkpoint table): All four expansions verified:
  - CCO = Colony Cartography Office: confirmed at checkpoints.md heading L97
  - WWD = Wandering Worker Detection: confirmed at checkpoints.md heading L235
  - DMVDC = Dirt Moved vs Dirt Claimed: confirmed at README:L106
  - CCB = Colony Census Bureau: confirmed at README:L165
- Lines 46-52 (roles table): Agent file paths verified against Glob results showing actual files in `agents/` directory and README:L269-276. The Queen correctly noted as having no dedicated agent file.

**Acceptance criteria verification:**

- AC1 (glossary with framework term definitions): PASS — 15 workflow concepts defined including "wave" and "checkpoint" explicitly called out in the task.
- AC2 (checkpoint acronyms expanded with one-line descriptions): PASS — all four (CCO, WWD, DMVDC, CCB) expanded with descriptions in a structured table.
- AC3 (ant metaphor names mapped to role descriptions): PASS — all seven roles (Queen, Scout, Pantry, Pest Control, Dirt Pusher, Nitpicker, Big Head) present with role descriptions.

**Assumptions audit:**
- Assumed "Dirt Pushers" in README refers to what the agent template calls "Dirt Pusher" (singular) — consistent usage throughout.
- Assumed agent files in `agents/` directory correspond to the names in README:L269-276 — confirmed by Glob showing those files exist.
- Assumed the Pantry has two agent files (impl + review) per README:L273-274 — reflected accurately.
- No assumptions made about content not visible in the referenced source files.

## 5. Build/Test Validation

This task creates a Markdown documentation file with no build artifacts, tests, or executable code. Validation is structural:

- File exists at expected path: `orchestration/GLOSSARY.md` — confirmed by Write tool success.
- File is valid Markdown: all tables have consistent column counts, header separators present, bold term names use `**` syntax consistently.
- No broken internal cross-references: all referenced files (`orchestration/templates/checkpoints.md`, `orchestration/RULES.md`, `orchestration/templates/reviews.md`, `agents/scout-organizer.md`, etc.) confirmed to exist via Glob.
- Scope boundary: only one file created, no existing files modified — WWD will pass.

## 6. Acceptance Criteria Checklist

| # | Criterion | Status |
|---|-----------|--------|
| 1 | A glossary document exists with definitions for all framework terms (wave, checkpoint, etc.) | PASS |
| 2 | All checkpoint acronyms (CCO, WWD, DMVDC, CCB) are expanded with one-line descriptions | PASS |
| 3 | All ant metaphor names (Queen, Scout, Pantry, Dirt Pusher, etc.) map to role descriptions | PASS |

## Commit Hash

_(bash commands — bd show, bd update, git pull --rebase, git add, git commit, bd close — require execution by the orchestrating session, which has Bash tool access. All file-based work is complete: orchestration/GLOSSARY.md created and verified.)_

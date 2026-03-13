# Task Summary: ant-farm-y4hl

**Task**: Design and write Forager agent (definition + template + skeleton)
**Commit**: 8312b12
**Status**: Complete

---

## 1. Approaches Considered

**Approach 1: Monolithic template with inline focus-area sections**
Single `forager.md` template. Agent reads entire file and executes the section
matching its `{FOCUS_AREA}`. Shared constraints appear once. Simple to maintain,
but the full file (~350+ lines) loads irrelevant sections into every Forager's
context. Tradeoff: simple structure vs. context noise.

**Approach 2: Separate template per focus area (4 files)**
Four separate workflow templates: `forager-stack.md`, `forager-architecture.md`,
`forager-pitfall.md`, `forager-pattern.md`. Maximum focus per agent. But produces
5 files (4 templates + 1 skeleton) against the task's implied 3-file design, and
requires Queen to know which template file to pass per focus area. Tradeoff:
maximum signal-to-noise per agent vs. operational complexity and file count mismatch.

**Approach 3: Conditional dispatch in single template (selected)**
Single `forager.md` with a shared header (hard constraints, source hierarchy) plus
explicit "read only your section" dispatch. Agent loads all sections but an
explicit instruction tells it to skip irrelevant ones. Matches the 3-file
requirement exactly. Queen passes `{FOCUS_AREA}` as a simple string. Consistent
with how Nitpicker handles its 4 review types in one file. Good balance of
maintenance simplicity and operational clarity.

**Approach 4: Two-file split — shared constraints + focus-area appendix injected by skeleton**
`forager.md` contains only shared workflow. Skeleton injects focus-area section
as a full variable block. Requires Queen to maintain 4 focus-area text blocks as
skeleton content and substitute the right one — complex spawn logic for the Queen.
Mismatches the task's stated design (`{FOCUS_AREA}` as a simple placeholder, not
a full content block). Tradeoff: cleanest separation vs. excessive Queen burden.

**Approach 5: Agent definition only (no separate template)**
Embed the full workflow in `agents/forager.md` and skip the template file. Reduces
file count to 2 (agent def + skeleton). But agent definition files in this codebase
are kept thin (50-200 lines) and delegate to templates — this pattern is established
by scout-organizer.md and surveyor.md. Embedding 350 lines in the agent def violates
the established pattern. Tradeoff: fewer files vs. convention violation.

---

## 2. Selected Approach

**Approach 3: Conditional dispatch in single `forager.md` template.**

Rationale:
- Fits the exact 3-file requirement (agents/forager.md, orchestration/templates/forager.md, orchestration/templates/forager-skeleton.md)
- Matches the existing pattern: scout-organizer.md and surveyor.md both delegate to templates; nitpicker.md uses a single file with per-type specialization blocks
- `{FOCUS_AREA}` as a simple Queen-substituted string is the minimal viable spawn interface
- Shared constraints (100-line cap, no cross-reading, source hierarchy) appear once at the top, reducing repetition
- Each focus area has its own clearly bounded section with scope fences, making it easy to audit per-type behavior

---

## 3. Implementation Description

**agents/forager.md** (37 lines):
- Frontmatter: name=forager, description, tools=(Read, Write, Glob, Grep, Bash), model=sonnet
- Thin agent definition following the scout-organizer/surveyor pattern
- Lists three spawn inputs (focus area, spec path, decompose dir)
- Delegates full workflow to `~/.claude/orchestration/templates/forager.md`
- Gives a 4-step overview (read spec, execute focus area, write output, return summary)

**orchestration/templates/forager.md** (366 lines):
- Term definitions block referencing PLACEHOLDER_CONVENTIONS.md
- Six hard constraints covering all four acceptance-criteria prohibitions plus source hierarchy and greenfield skip
- Step 1: spec reading with extraction checklist
- Step 2: dispatch header + four focus area sections (STACK, ARCHITECTURE, PITFALL, PATTERN), each with mandate, what-to-investigate, what-NOT-to-investigate, good/bad output examples, and output file path
- Pattern section includes explicit greenfield skip with exact skip file content
- Step 3: mandatory output format template with line cap enforcement (4-step cut order)
- Step 4: return summary format
- Error handling for 5 failure modes

**orchestration/templates/forager-skeleton.md** (51 lines):
- Queen-facing instructions (not agent-facing) above the `---` separator
- Notes model: sonnet requirement and 4-concurrent-spawn pattern
- Term definitions block (canonical Tier 1 placeholders)
- Placeholder list: `{FOCUS_AREA}`, `{SPEC_PATH}`, `{DECOMPOSE_DIR}`
- Agent-facing prompt below separator: identify focus area, point to template, list inputs, 5-step execution sequence, scope prohibitions

---

## 4. Correctness Review

### agents/forager.md
- Frontmatter present and correct: name, description, tools list (5 tools), model: sonnet
- Agent body is correctly thin — delegates to template (matches scout-organizer/surveyor pattern)
- Three spawn inputs listed correctly
- No placeholder contamination
- PASS

### orchestration/templates/forager.md
- Term definitions block present, references PLACEHOLDER_CONVENTIONS.md
- All four focus areas have clear scope fences ("What you do NOT investigate")
- Hard Constraints section covers all four prohibitions from AC-4 explicitly:
  - #2: no cross-reading
  - #1: max 100 lines
  - #3: no contradicting spec decisions
  - #4: no alternative recommendations
- Source hierarchy (AC-6): Hard Constraint #5 explicitly lists official docs > web > training data, with training-data labeling requirement
- Greenfield skip logic (AC-5): Pattern section has "Greenfield skip rule" with exact skip file template
- Good/bad examples (AC-7): all four focus areas have explicit Good output and Bad output code blocks
- Placeholder compliance: `{FOCUS_AREA}`, `{SPEC_PATH}`, `{DECOMPOSE_DIR}` are Tier 1 (UPPERCASE); `{focus}`, `{N}`, `{focus-area-lowercase}` are Tier 2 (lowercase); no Tier 3 or Tier 4 violations
- PASS

### orchestration/templates/forager-skeleton.md
- `{FOCUS_AREA}` placeholder present (at L21, L29, L34, L36, L43)
- Model: sonnet instruction present
- Term definitions block present (canonical Tier 1)
- Scope prohibitions present (no cross-reading, no modifying source files, no contradicting spec)
- Agent-facing text properly separated from Queen instructions at `---`
- PASS

**Acceptance criteria verification (all 7):**
1. agents/forager.md frontmatter correct — PASS
2. forager.md contains all 4 focus areas with scope boundaries — PASS
3. forager-skeleton.md contains `{FOCUS_AREA}` placeholder — PASS
4. Prohibitions explicit: no cross-reading (#2), max 100 lines (#1), no contradicting spec (#3), no alternative recommendations (#4) — PASS
5. Pattern greenfield skip logic documented — PASS
6. Source hierarchy explicitly stated — PASS
7. Good/bad examples for each focus area — PASS

---

## 5. Build/Test Validation

No executable code was produced. These are prompt/template files.

Structural checks performed:
- Line counts verified: agents/forager.md (37L), forager.md (366L), forager-skeleton.md (51L)
- Placeholder casing: grepped for UPPERCASE Tier 1 placeholders (`{FOCUS_AREA}`, `{SPEC_PATH}`, `{DECOMPOSE_DIR}`); all present in correct locations
- No `{{DOUBLE_BRACE}}` Tier 4 placeholders introduced (not appropriate for Forager templates)
- No shell variable `${VAR}` patterns outside of inline prose (the `mkdir -p {DECOMPOSE_DIR}/research` is inline instruction text with a Tier 1 placeholder already substituted before agent sees it)
- Commit staged and committed cleanly: `8312b12`

---

## 6. Acceptance Criteria Checklist

- [x] AC-1: agents/forager.md exists with correct frontmatter (name, description, model: sonnet, tools list) — PASS
- [x] AC-2: orchestration/templates/forager.md contains workflow for all 4 focus areas with clear scope boundaries — PASS
- [x] AC-3: orchestration/templates/forager-skeleton.md contains prompt template with `{FOCUS_AREA}` placeholder — PASS
- [x] AC-4: Prompt includes explicit prohibitions: no cross-reading, max 100 lines, no contradicting spec decisions, no alternative recommendations — PASS
- [x] AC-5: Pattern Forager skip logic documented for greenfield projects — PASS
- [x] AC-6: Source hierarchy (official docs > web > training data) explicitly stated in prompt — PASS
- [x] AC-7: Each focus area has concrete examples of good/bad research output — PASS

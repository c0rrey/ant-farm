# Summary: ant-farm-xtu9
**Task**: Design and write Architect agent (definition + template + skeleton)
**Agent**: prompt-engineer
**Status**: completed
**Files changed**:
- agents/architect.md (new)
- orchestration/templates/decomposition.md (new)
- orchestration/templates/architect-skeleton.md (new)

**Commit**: eb1fae4

---

## Approaches Considered

### 1. Thin Agent Definition + Self-Referencing Workflow (Selected)
**Strategy**: Agent file (agents/architect.md) is minimal with frontmatter and a brief role description pointing to orchestration/templates/decomposition.md. The decomposition.md file contains the full workflow. architect-skeleton.md is the Queen's spawn wrapper.
**Pros**: Matches established pattern (surveyor.md, forager.md, pantry-impl.md); separation of concerns — agent def is stable API, workflow template can evolve independently; aligns with how all other agents in the codebase work.
**Cons**: Requires two reads at runtime (agent def + decomposition.md); the indirection may be slightly confusing on first reading.

### 2. Monolithic Agent File
**Strategy**: All workflow, prohibitions, and output format live directly in agents/architect.md. No separate orchestration template needed.
**Pros**: Everything in one place; fully self-contained agent.
**Cons**: Breaks the established pattern; decomposition.md would need to be essentially empty, violating acceptance criterion AC-2; agent files should be stable type definitions, not full workflow documents.

### 3. Skeleton-First Design (skeleton drives everything)
**Strategy**: architect-skeleton.md is the master document containing all instructions inline. decomposition.md is a CLI-command-only appendix. The agent file points to the skeleton.
**Pros**: Single file for the Queen to read when spawning.
**Cons**: Skeleton files are templates for the Queen (spawn-time), not documents agents read at runtime; this conflates two distinct audiences; inconsistent with surveyor-skeleton.md and forager-skeleton.md conventions.

### 4. Three-Layer With Inlined Prohibitions in All Three Files
**Strategy**: Same three-layer separation, but prohibitions and coverage rules are only in decomposition.md — neither the agent def nor the skeleton restates them.
**Pros**: DRY — no repetition.
**Cons**: The skeleton must be usable as a self-contained spawn prompt the Queen reads without loading decomposition.md; if the skeleton omits the prohibitions, a Queen that skims the skeleton might miss them. Better to repeat the key constraints in the skeleton's "Critical Constraints" section for visibility.

---

## Selected Approach
**Choice**: Approach 1 (Thin Agent Definition + Self-Referencing Workflow), with the refinement from Approach 4's insight — key constraints are also summarized in architect-skeleton.md for Queen visibility, with full canonical definitions in decomposition.md.
**Rationale**: Matches the existing pattern used by all agents in the codebase (surveyor, forager, pantry-impl each have a thin agent def pointing to an orchestration template). Rejected Approach 2 because it violates the acceptance criteria requiring decomposition.md to contain the full workflow. Rejected Approach 3 because skeleton files have a specific purpose (Queen spawn templates) that does not include being the agent's workflow document.

---

## Implementation

Three files created:

**agents/architect.md**: Agent definition with YAML frontmatter (name: architect, description, model: opus, tools). Body describes the agent's role, lists its inputs (spec.md + four research briefs + codebase), outputs (trails, crumbs, decomposition-brief.md), and a 8-step workflow summary that references decomposition.md for full details. Mirrors the format of agents/surveyor.md and agents/forager.md exactly.

**orchestration/templates/decomposition.md**: Full 9-step workflow template readable by the Architect at runtime. Contains:
- Term definitions (trail, crumb, DECOMPOSE_DIR, CODEBASE_ROOT)
- Step 1: Read inputs with fail-fast on missing files
- Step 2: Brownfield vs greenfield codebase scan
- Step 3: Trail identification with sizing rules and naming conventions
- Step 4: Crumb decomposition with scope budget (5-8 files, hard constraint), banned acceptance criteria phrases, agent type assignment, all required crumb fields
- Step 5: Dependency wiring with explicit dependency rules, circular dep prohibition, orphan crumb prohibition
- Step 6: 100% spec coverage mandatory gate with coverage table format
- Step 7: CLI commands for trail creation, crumb creation (--from-json), parent-child wiring, blocks wiring, dolt mode warning
- Step 8: decomposition-brief.md output format with all required sections
- Step 9: Return format to Queen
- Prohibitions section (8 explicit prohibitions)

**orchestration/templates/architect-skeleton.md**: Queen spawn template with {DECOMPOSE_DIR}, {CODEBASE_ROOT}, {SPEC_PATH} uppercase placeholders. Includes prerequisite checklist (verify all 5 input files exist before spawning), model requirement (opus), step summary, and "Critical Constraints" section that surfaces scope budget, 100% coverage gate, all prohibitions, and brownfield/greenfield handling for Queen visibility without requiring the Queen to read decomposition.md.

---

## Correctness Review

### agents/architect.md
- **Re-read**: yes
- **Acceptance criteria verified**:
  - AC-1: Correct frontmatter with name, description, model: opus, tools list — PASS
- **Issues found**: none
- **Cross-file consistency**: References decomposition.md at `~/.claude/orchestration/templates/decomposition.md` — consistent with how surveyor.md and forager.md reference their workflow templates

### orchestration/templates/decomposition.md
- **Re-read**: yes
- **Acceptance criteria verified**:
  - AC-2: Full decomposition workflow with crumb CLI commands (`bd trail create`, `bd create --from-json`, `bd dep add`) — PASS
  - AC-4: 100% spec coverage requirement ("mandatory gate", "Do NOT proceed to Step 7 until it passes") — PASS
  - AC-5: Scope budget (5-8 files) explicitly stated as "hard constraint, not a guideline" — PASS
  - AC-6: Explicit prohibitions section with all 8 prohibitions including no code writing, no orphan crumbs, no circular deps, no vague scope, no unverifiable criteria — PASS
  - AC-7: Brownfield vs greenfield documented in Step 2 with explicit handling for each case — PASS
  - AC-8: decomposition-brief.md output format specified in Step 8 with exact markdown template — PASS
- **Issues found**: none
- **Cross-file consistency**: Step 7 CLI commands match the `bd dep add` direction documented in project MEMORY (child-first, parent-second for parent-child type; blocker-first, blocked-second for blocks type)

### orchestration/templates/architect-skeleton.md
- **Re-read**: yes
- **Acceptance criteria verified**:
  - AC-3: Prompt template with input file placeholders ({SPEC_PATH}, {DECOMPOSE_DIR}, {CODEBASE_ROOT}) — PASS
  - AC-4: 100% spec coverage requirement restated ("mandatory gate; do not proceed until coverage is PASS") — PASS
  - AC-5: Scope budget restated ("hard scope budget", "A crumb touching 9+ files MUST be split") — PASS
  - AC-6: Prohibitions listed in "Critical Constraints" section — PASS
  - AC-7: Brownfield vs greenfield section present — PASS
  - AC-8: decomposition-brief.md output sections listed in step 8 summary — PASS
- **Issues found**: none
- **Cross-file consistency**: Uppercase placeholders ({SPEC_PATH}, {DECOMPOSE_DIR}, {CODEBASE_ROOT}) follow the convention established in surveyor-skeleton.md and forager-skeleton.md

---

## Build/Test Validation
- **Command run**: Files created and read back to verify content
- **Result**: All three files written successfully and read back without errors. No automated tests applicable to markdown template files.

---

## Acceptance Criteria

- [x] agents/architect.md exists with correct frontmatter (name, description, model: opus, tools list) — PASS
- [x] orchestration/templates/decomposition.md contains full decomposition workflow with crumb CLI commands — PASS
- [x] orchestration/templates/architect-skeleton.md contains prompt template with input file placeholders — PASS
- [x] Prompt specifies 100% spec coverage requirement (every requirement maps to >=1 crumb acceptance criterion) — PASS
- [x] Scope budget (5-8 files per crumb) explicitly stated and enforced — PASS
- [x] Prompt includes explicit prohibitions: no code writing, no orphan crumbs, no circular deps, no vague scope, no unverifiable criteria — PASS
- [x] Brownfield vs greenfield handling documented (reference existing files vs propose new paths) — PASS
- [x] decomposition-brief.md output format specified — PASS

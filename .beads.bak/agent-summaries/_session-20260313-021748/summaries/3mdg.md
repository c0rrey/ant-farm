# Task Summary: ant-farm-3mdg
**Task**: Define Planner orchestrator behavior
**Commit**: 6f3485e

## 1. Approaches Considered

**Approach A — New standalone file** (`orchestration/RULES-planner-behavior.md`):
A completely separate document dedicated to Planner orchestrator behavior, linked from RULES-decompose.md.
- Pro: Clean separation of concerns; easy to find the behavior spec in isolation.
- Con: Scope boundaries in the task brief specify RULES-decompose.md as the affected file. Cross-file reading adds cognitive overhead; the Planner would need to read two files.

**Approach B — Expand and rename existing "Planner Read Permissions" section**:
Rename the section to "Planner Behavior" and inline state tracking and Queen distinction into the existing section.
- Pro: Consolidates all Planner behavior under one heading without adding a new section.
- Con: The existing section header ("Read Permissions") is descriptively accurate for its content; renaming it to encompass behavior conflates two concerns. The resulting section would be unwieldy.

**Approach C — New top-level "Planner Orchestrator Profile" section** (selected):
Insert a new section between "Planner Prohibitions" and "Planner Read Permissions" that adds a Queen comparison table, a dedicated state tracking subsection, and a context budget subsection with reasoning.
- Pro: Single file; discoverable; doesn't duplicate existing content; provides a holistic profile in one place. All six acceptance criteria are satisfied by this section plus the existing Read Permissions section it references.
- Con: Some overlap in the context budget target (also mentioned in Step 0 workflow). This is intentional — the profile section explains *why*, the workflow section restates *what* for inline reference.

**Approach D — Scatter additions across existing sections**:
Add Queen distinction note to Prohibitions, state tracking to Workflow Step 0, budget reasoning inline in the step where it's most relevant.
- Pro: Minimal new content; changes feel like refinements rather than additions.
- Con: The acceptance criteria require each item to be explicitly and findably documented. Scattering makes it difficult to audit coverage. The "Distinction from Queen explicitly called out" criterion implies a consolidated, not scattered, treatment.

## 2. Selected Approach

**Approach C — New "Planner Orchestrator Profile" section.**

Rationale: The task's acceptance criteria read like a checklist for a single coherent section: read permissions, prohibited reads, state tracking, context budget, Queen distinction. Approach C creates exactly that — a reference section that a reader can scan to understand the Planner holistically. It augments the existing Read Permissions section (which already handles AC2 and AC3 in detail) with the three missing pieces: state tracking, context budget reasoning, and Queen comparison.

## 3. Implementation Description

Added a new `## Planner Orchestrator Profile` section to `orchestration/RULES-decompose.md`, positioned between the existing "Planner Prohibitions" and "Planner Read Permissions" sections. The new section contains three subsections:

- **Distinction from Queen**: An 8-row comparison table covering trigger, purpose, workflow file, read permissions, state tracking, primary agents, context budget, and bd CLI usage. Closes with explicit mutual-exclusion statement ("The Planner MUST NOT read RULES.md. The Queen MUST NOT read this file.").

- **State Tracking**: Defines in-context-only state (no disk file), enumerates tracked items (current step 0–6, per-agent retry counts with maximums), explicitly states the Planner does NOT use queen-state.md, and documents progress.log as the recovery mechanism.

- **Context Budget**: States the 15–20% target, provides the reasoning (multiple agent round-trips consume context), lists what the budget must preserve capacity for (Forager summaries, Surveyor spec, Architect brief, gate check outputs), and reiterates the large-input summarization instruction from Step 0.

Total change: 61 lines inserted, 0 lines deleted.

## 4. Correctness Review

**orchestration/RULES-decompose.md** (sole changed file):

- Section placement: Inserted after Planner Prohibitions and before Planner Read Permissions. This is the natural reading order — prohibitions first, then the behavioral profile, then the detailed permission list.
- AC1 — Planner orchestrator behavior documented: The "Planner Orchestrator Profile" section provides comprehensive behavior documentation. PASS.
- AC2 — Read permissions explicitly stated (spec.md and decomposition-brief.md only): Stated in the Distinction from Queen table (row 4) and detailed in the existing Planner Read Permissions section (lines 97-100 of final file). PASS.
- AC3 — Prohibited reads listed (research briefs, task JSONL, source code): The existing Planner Read Permissions FORBIDDEN block lists all prohibited reads including research briefs, source code files, and bd CLI outputs. The Planner Prohibitions section (NEVER read source code) also contributes. PASS.
- AC4 — State tracking mechanism defined (step + retry count, not queen-state.md): The State Tracking subsection explicitly defines step number + per-agent retry count, and explicitly states the Planner does NOT use queen-state.md. PASS.
- AC5 — Context budget target (15-20%) with reasoning documented: The Context Budget subsection states the 15–20% target and documents the multi-agent round-trip reasoning. PASS.
- AC6 — Distinction from Queen explicitly called out (permissions, state, budget): The comparison table covers all three dimensions plus five more, and is titled "Distinction from Queen." PASS.

No regressions to existing content — the edit was an insertion-only change.

## 5. Build/Test Validation

This task modifies only a documentation file (RULES-decompose.md). No build artifacts, test suite, or source code was changed. No compilation or test run is required or applicable.

Manual validation: re-read the full modified file to confirm insertion correctness, section ordering, and markdown table formatting. The file renders correctly with proper table alignment and section hierarchy.

## 6. Acceptance Criteria Checklist

| # | Criterion | Status |
|---|-----------|--------|
| 1 | Planner orchestrator behavior documented (within RULES-decompose.md or separate file) | PASS |
| 2 | Read permissions explicitly stated: spec.md and decomposition-brief.md only | PASS |
| 3 | Prohibited reads listed: research briefs content, task JSONL, source code | PASS |
| 4 | State tracking mechanism defined (step + retry count, not queen-state.md) | PASS |
| 5 | Context budget target (15-20%) with reasoning documented | PASS |
| 6 | Distinction from Queen explicitly called out (permissions, state, budget) | PASS |

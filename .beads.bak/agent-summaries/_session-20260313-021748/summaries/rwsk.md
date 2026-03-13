# Task Summary: ant-farm-rwsk — Write RULES-decompose.md

**Task**: Create orchestration/RULES-decompose.md
**Commit**: 8ab12f5
**Status**: Complete

---

## 1. Approaches Considered

### Approach A: Mirror RULES.md structure exactly
Copy the section structure of RULES.md (including wave management, Dirt Pushers, Nitpickers) and
populate only the decomposition-relevant parts. Maximizes structural familiarity for engineers who
know RULES.md.

**Tradeoff**: RULES.md contains extensive content irrelevant to decomposition (wave pipelining,
Nitpicker teams, fix cycles). Including it as empty or N/A sections would add noise; omitting it
would require careful annotation. The Planner would spend effort distinguishing "does not apply"
sections from genuine workflow steps.

### Approach B: Thin overlay / difference document
Write RULES-decompose.md as a short document covering only what differs from RULES.md, with
references back to RULES.md for shared concepts.

**Tradeoff**: Forces the Planner to mentally merge two documents while orchestrating. The risk of
applying a Queen-specific rule (e.g., "only the Queen pushes to remote") to a decomposition context
is high. Saved token count is outweighed by error-prone dual-document orchestration.

### Approach C: Self-contained standalone document (selected)
Write RULES-decompose.md as a complete document covering the full decomposition workflow. The
Planner reads only this file. Format aligns with RULES.md's tables, step formatting, and progress
log patterns for familiarity, but the content is entirely decomposition-specific.

**Tradeoff**: Some duplication of conventions (progress log format, path reference convention,
directory naming). Acceptable because the duplication is structural boilerplate that varies per
workflow, not business logic that risks diverging.

### Approach D: Two-tier structure with quick-reference section
Add a compact "Quick Reference" section at the top listing the 3 hard gates, concurrency limits,
and retry counts in a summary box, then the full step workflow below.

**Tradeoff**: Useful for an experienced Planner doing fast lookups, but the Planner reads this
file exactly once per session at session start — the additional navigation layer adds complexity
without clear runtime benefit. The existing tables in Concurrency Rules and Hard Gates already
serve the quick-reference purpose.

---

## 2. Selected Approach with Rationale

**Approach C: Self-contained standalone document**

Rationale: RULES-review.md establishes this pattern in the codebase — it is self-contained within
its scope (Steps 3b-3c) and does not require reading RULES.md to use. RULES-decompose.md follows
the same pattern for the decomposition workflow. This eliminates cross-document merging errors and
gives the Planner a single source of truth. Format alignment with RULES.md (table style, progress
log format, step numbering, prohibitions block at top) provides familiarity while keeping the
content completely decomposition-scoped.

---

## 3. Implementation Description

Created `orchestration/RULES-decompose.md` (378 lines) with:

- **Preamble**: directs Planner to read this file alone; references RULES.md as separate/irrelevant
- **Path Reference Convention**: repo-root relative paths with runtime translation rules
- **Planner Prohibitions**: 6 prohibitions including NEVER read bd commands, NEVER read agent
  instruction files, NEVER set run_in_background, NEVER spawn Architect early
- **Planner Read Permissions**: PERMITTED (spec.md, decomposition-brief.md only) and FORBIDDEN
  (all agent templates, research briefs, source code)
- **Steps 0-6**: Full workflow with progress log lines per step, hard gate checks inline,
  brownfield detection heuristic (5+ non-config files = brownfield) and context budget (15-20%)
  in Step 0, input classification in Step 1, Surveyor spawn in Step 2, 4x parallel Forager spawn
  in Step 3, solo Architect spawn in Step 4, verification in Step 5, handoff in Step 6
- **Hard Gates table**: spec quality gate, research complete, TDV PASS
- **Retry Limits table**: Surveyor (1), Forager per focus (1), Forager line cap (0/truncate),
  Architect (2)
- **Concurrency Rules**: max 4 Foragers, Surveyor alone, Architect alone, no Forager cross-reads
- **Agent Types and Models table**: surveyor-agent/opus, forager-agent/sonnet, architect-agent/opus
- **Decompose Directory Structure**: annotated tree diagram
- **Anti-Patterns**: 6 common mistakes

---

## 4. Correctness Review

**File reviewed**: `orchestration/RULES-decompose.md`

- Steps 0-6 are present and in order with no gaps.
- Each step specifies: agent spawned (Surveyor in Step 2, 4x Forager in Step 3, Architect in
  Step 4), model (opus/sonnet as appropriate), input files, output files, and hard gate conditions.
- Hard Gates table lists all 3 required gates with step references and failure actions.
- Concurrency Rules section explicitly states max 4 Foragers concurrent, Surveyor runs alone,
  Architect runs alone.
- Retry Limits table has 4 rows with escalation paths for all agents including the Forager
  truncation edge case.
- Planner Read Permissions section explicitly limits Planner reads to spec.md and
  decomposition-brief.md; all agent templates and research briefs are in FORBIDDEN.
- Context budget "15-20%" stated in Step 0 with rationale: "This leaves room for up to 4 Forager
  returns, the Surveyor spec, and the Architect's brief."
- Brownfield heuristic: `find` command in Step 0 + explicit "5 or more non-config files →
  brownfield. Fewer than 5 → greenfield."

No assumptions were made beyond what the task brief and `bd show` description specified.

---

## 5. Build/Test Validation

This task creates a documentation file only. No code was changed. No tests or builds to run.

File created successfully:
- `orchestration/RULES-decompose.md` — 378 lines, committed as `8ab12f5`

---

## 6. Acceptance Criteria Checklist

- [x] orchestration/RULES-decompose.md exists with all 7 steps (0-6) documented
      PASS — Steps 0 through 6 are all present in the Workflow section.

- [x] Each step specifies: agent to spawn, model, input files, output files, hard gate conditions
      PASS — Steps 2, 3, and 4 each specify agent type, model, input/output files, and gate.
      Steps 0, 1, 5, 6 are non-agent steps (setup/classification/verification/handoff).

- [x] Hard gates table present: spec quality gate, research complete, TDV PASS
      PASS — Hard Gates table at end of document lists all three gates with step references,
      blocking conditions, and failure actions.

- [x] Concurrency rules documented: max 4 Foragers, Surveyor/Architect run alone
      PASS — Concurrency Rules section states all three rules explicitly.

- [x] Retry limits table present with escalation paths
      PASS — Retry Limits table covers Surveyor (1 retry), Forager/missing (1 retry per),
      Forager/line-cap (0 retries/truncate), Architect (2 retries), each with escalation path.

- [x] Planner read permissions explicitly defined (reads spec.md and decomposition-brief.md only)
      PASS — Planner Read Permissions section shows PERMITTED list of exactly these two files;
      all agent templates and research briefs are explicitly FORBIDDEN.

- [x] Context budget target (15-20%) documented with rationale
      PASS — Step 0 states target and explains why: "room for up to 4 Forager returns, the
      Surveyor spec, and the Architect's brief."

- [x] Brownfield vs greenfield detection heuristic documented (5+ non-config files = brownfield)
      PASS — Step 0 includes a `find` command that excludes config/doc files and states the
      "5 or more non-config files = brownfield" threshold explicitly.

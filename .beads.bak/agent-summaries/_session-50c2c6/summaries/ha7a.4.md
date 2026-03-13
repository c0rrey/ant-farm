# Task Summary: ant-farm-ha7a.4

**Task**: Add P3 auto-filing, termination check, and mandatory re-review to reviews.md
**Agent type**: technical-writer
**Status**: Complete

## Approaches Considered

### Approach 1: Single block at end of Bead Filing section (selected)
Add the P3 Auto-Filing section as a named subsection immediately after the `bd label add` line at the end of the bead filing block. This places auto-filing logic adjacent to the existing manual bead filing instructions, making the distinction between round 1 and round 2+ immediately legible to Big Head.

Tradeoffs:
- Pro: Logical placement — the P3 auto-filing follows directly from bead filing, which is where Big Head is operating
- Pro: Keeps all Big Head responsibilities in the Big Head Consolidation section
- Con: Slightly separates it from the Queen's Step 3c/4 where P3 handling is also discussed

### Approach 2: Add P3 Auto-Filing inside the Big Head Consolidation Checklist
Place a note about P3 auto-filing inside the existing checklist block rather than as a standalone section. This would keep checklist items together.

Tradeoffs:
- Pro: Users scanning the checklist would see it
- Con: A checklist item cannot contain bash code blocks — the detail required does not fit a bullet
- Con: Harder to reference from the "Handle P3 Issues" section's "Round 1 only" blockquote
- Rejected: Too cramped for the content needed

### Approach 3: Add P3 Auto-Filing as a subsection of Queen's Step 3c
Place the auto-filing instructions inside the Queen's triage section alongside the Termination Check.

Tradeoffs:
- Pro: Keeps all P3 handling near each other in the Queen's workflow
- Con: The P3 auto-filing in round 2+ is Big Head's responsibility, not the Queen's — placing it under Queen's Step 3c misattributes ownership
- Rejected: Ownership mismatch

### Approach 4: Inline note only (no new section)
Rather than a separate section, add a one-line note after `bd label add` saying Big Head auto-files P3s in round 2+, with a pointer to Handle P3 Issues.

Tradeoffs:
- Pro: Minimal doc surface
- Con: Does not satisfy acceptance criterion 1 (requires `### P3 Auto-Filing (Round 2+ Only)` heading) or criterion 2 (requires both `bd epic create` and `bd dep add --type parent-child`)
- Rejected: Does not meet acceptance criteria

### Approach 5: Split into two files (separate Big Head doc and Queen doc)
Extract Big Head consolidation logic into a dedicated file so P3 auto-filing has its own space.

Tradeoffs:
- Pro: Better separation of concerns long-term
- Con: Out of scope for this task; scope boundary explicitly limits edits to reviews.md only
- Rejected: Out of scope

## Selected Approach

**Approach 1** — add as a named subsection immediately after the bead filing block.

Rationale: This is the approach specified by the implementation plan (Task 4, Step 1). It places Big Head's P3 auto-filing responsibility directly in the Big Head Consolidation Protocol section, adjacent to the bead filing instructions it extends. The `### P3 Auto-Filing (Round 2+ Only)` heading satisfies acceptance criterion 1 verbatim, and the bash blocks satisfy criterion 2.

## Implementation Description

Four targeted edits were made to `orchestration/templates/reviews.md`:

1. **P3 Auto-Filing section** — inserted after the closing ` ``` ` of the bead filing bash block (after `bd label add <id> <primary-review-type>`), before `## The Queen's Checklists`. The new section is `### P3 Auto-Filing (Round 2+ Only)` and contains a four-step workflow including `bd epic create` and `bd dep add <bead-id> <future-work-epic-id> --type parent-child`.

2. **Termination Check subsection** — inserted in `## Queen's Step 3c: User Triage on P1/P2 Issues`, between the `**Prerequisite**` line and `### If P1 or P2 issues found:`. The subsection is `### Termination Check (zero P1/P2 findings)` with four numbered steps covering round 2+, round 1, session state update, and proceed instruction.

3. **MANDATORY re-review** — replaced the `c. **Re-run reviews** (optional):` bullet and its two sub-bullets with `c. **Re-run reviews** (MANDATORY):` and three new sub-bullets specifying the exact re-run protocol: re-run Step 3b with an incremented round number, round 2+ scope restriction, and loop-until-zero-P1P2 termination.

4. **Round 1 only blockquote** — inserted a `> **Round 1 only.**` blockquote immediately after the `### Handle P3 Issues (Queen's Step 4)` heading, before `**Create "Future Work" epic if needed**:`.

No other sections were touched. The scope boundary was respected: Step 0, Step 0a, Step 3 of Big Head Consolidation, review type definitions, Team Setup, Round-Aware Review Protocol, Nitpicker Checklist, and Big Head Consolidation Checklist were all left unchanged.

## Correctness Review

**File reviewed**: `/Users/correy/projects/ant-farm/orchestration/templates/reviews.md`

### P3 Auto-Filing section (lines 671-699)
- Heading `### P3 Auto-Filing (Round 2+ Only)` present and exact
- `bd epic create` present in step 1 bash block
- `bd dep add <bead-id> <future-work-epic-id> --type parent-child` present in step 2 bash block
- Round 1 vs Round 2+ distinction clearly stated at bottom of section
- Section is inside Big Head Consolidation Protocol, after bead filing block, before `## The Queen's Checklists` — correct placement
- Markdown renders correctly: bash fenced blocks use triple backticks; the P3 summary table uses triple tilde fences to avoid conflict with outer code blocks

### Termination Check subsection (lines 740-749)
- Heading `### Termination Check (zero P1/P2 findings)` present and exact
- Four numbered steps cover both round contexts, session state, and onward routing
- Positioned at lines 740-749, before `### If P1 or P2 issues found:` at line 751 — correct

### MANDATORY re-review (lines 778-780)
- Text reads `c. **Re-run reviews** (MANDATORY):` — matches acceptance criterion 4 pattern `Re-run reviews.*MANDATORY`
- Three sub-bullets: re-run instruction, round 2+ scope, loop termination condition
- Old "optional" language and its sub-bullets fully removed

### Round 1 only blockquote (lines 788-790)
- `### Handle P3 Issues (Queen's Step 4)` heading at line 788
- Blank line at line 789
- `> **Round 1 only.** In round 2+, P3s are auto-filed by Big Head during consolidation (see "P3 Auto-Filing" above). This section applies only when round 1 terminates with P3 findings.` at line 790
- The heading is immediately followed by the blockquote — correct per criterion 5

### Assumptions audit
- Assumed that "immediately after the heading" in criterion 5 allows one blank line between heading and blockquote (standard Markdown practice) — this is consistent with how ha7a.3 structured similar blockquotes in the same file.
- Assumed the implementation plan's exact text is authoritative where it provides verbatim content — all verbatim strings match.
- No other files were read or modified outside the permitted scope.

## Build/Test Validation

This task modifies Markdown documentation only. There are no build artifacts, test suites, or linting configurations that apply. Validation was performed by:

1. Grep for each acceptance criterion pattern to confirm presence
2. Line-number spot-reads to confirm positional ordering (Termination Check before If P1/P2)
3. Full read of the modified region (lines 659-802) to confirm no unintended changes to surrounding sections

## Acceptance Criteria Checklist

1. `grep "### P3 Auto-Filing (Round 2+ Only)" orchestration/templates/reviews.md` returns a match
   **PASS** — heading present at line 671

2. P3 Auto-Filing section contains both `bd epic create` and `bd dep add` with `--type parent-child`
   **PASS** — `bd epic create` at line 680; `bd dep add <bead-id> <future-work-epic-id> --type parent-child` at line 686

3. `grep "### Termination Check" orchestration/templates/reviews.md` returns a match, positioned before `### If P1 or P2 issues found:`
   **PASS** — `### Termination Check (zero P1/P2 findings)` at line 740; `### If P1 or P2 issues found:` at line 751

4. `grep "Re-run reviews.*MANDATORY" orchestration/templates/reviews.md` returns a match (not "optional")
   **PASS** — `c. **Re-run reviews** (MANDATORY):` at line 778; "optional" text fully removed

5. `### Handle P3 Issues (Queen's Step 4)` is followed immediately by a `> **Round 1 only.**` blockquote
   **PASS** — heading at line 788, blockquote at line 790 (one blank line between, standard Markdown)

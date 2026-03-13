# Task Summary: ant-farm-ha7a.5

**Task**: Update review checklists for round-aware team composition
**Agent type**: technical-writer
**Status**: Complete

---

## 1. Approaches Considered

### Approach A: Full section replacement (heading + body)
Replace the entire block from each heading line through the last checklist item, including the heading itself. This guarantees no stale heading text survives, but introduces unnecessary risk of heading text mismatch if surrounding whitespace or punctuation differs by even one character.

### Approach B: Body-only replacement (selected)
Match and replace only the checklist item lines between each heading and the next section heading, leaving the headings untouched. Two Edit calls — one per checklist. This is precise, minimal in scope, and keeps the surrounding document structure completely intact.

### Approach C: Line-range write (full file rewrite)
Read the entire file, manipulate it as a string with explicit line-range splicing, then write the whole file back. This is the highest-risk approach: any off-by-one in line numbering (which the plan explicitly warned about due to earlier wave edits) could corrupt sections far outside the target checklists.

### Approach D: Item-by-item replacement
Replace each old checklist item individually with its new equivalent. Most surgical, but requires 8+ separate Edit calls and risks a partially-applied state if any single edit fails to match due to whitespace differences. Also harder to verify as a coherent unit.

---

## 2. Selected Approach with Rationale

**Approach B (body-only replacement)** was selected because:
- It touches the minimum necessary text — only the checklist item lines, not headings or surrounding prose.
- Two clean Edit calls are easy to verify end-to-end.
- The implementation plan explicitly warned that line numbers shift across waves; by matching the literal checklist text (not line numbers), the edits are immune to that problem.
- Leaves all surrounding sections (P3 Auto-Filing, After Consolidation Complete, etc.) completely untouched, satisfying the strict scope boundary from the task brief.

---

## 3. Implementation Description

Two Edit operations on `/Users/correy/projects/ant-farm/orchestration/templates/reviews.md`:

**Edit 1 — Nitpicker Checklist** (located by heading `### Nitpicker Checklist (verify before launching team)`):

Replaced the 8-item checklist with an 11-item round-aware version that adds:
- `Review round number passed to Pantry` item (first position)
- Round 1 / Round 2+ split on the prompt count item
- `Round 2+ reviewers include out-of-scope finding bar` item
- Round 1 / Round 2+ split on team member count item (replacing the old single-round "6 members" item)
- `Round 2+: Big Head prompt includes review round number and P3 auto-filing instructions` item (last position)

**Edit 2 — Big Head Consolidation Checklist** (located by heading `### Big Head Consolidation Checklist (after all Nitpickers finish)`):

Replaced the 8-item checklist with a 9-item round-aware version that:
- Made the first item round-aware: `Round 1: Read all 4 Nitpicker reports; Round 2+: Read 2 reports (Correctness, Edge Cases)`
- Inserted `Round 2+ on PASS: P3 beads auto-filed to "Future Work" epic (not presented to user)` after the existing `On PASS` item

All other checklist items (dedup, root-cause grouping, consolidated summary path, SendMessage, Pest Control verdict, FAIL escalation) were preserved verbatim.

---

## 4. Correctness Review

**File reviewed**: `/Users/correy/projects/ant-farm/orchestration/templates/reviews.md`

Post-edit read of lines 700-731 confirmed:

- The `## The Queen's Checklists` heading is untouched (line 701).
- The `### Nitpicker Checklist (verify before launching team)` heading is untouched (line 703).
- The Nitpicker checklist intro line `Before launching the review agent team, confirm:` is untouched (line 705).
- The 11 new Nitpicker checklist items appear exactly as specified in Task 5 of the implementation plan (lines 706-716).
- The `### Big Head Consolidation Checklist (after all Nitpickers finish)` heading is untouched (line 718).
- The Big Head checklist intro line `Before filing beads, confirm Big Head has:` is untouched (line 720).
- The 9 new Big Head checklist items appear exactly as specified in Task 5 of the implementation plan (lines 721-729).
- The `## After Consolidation Complete` heading and all content below it are untouched (line 731 onward).
- No edits were made outside the two checklist item blocks.

**Scope compliance**: Only the two checklist item blocks were modified. No other section was touched.

---

## 5. Build/Test Validation

These are markdown template files read by AI agents at runtime — there is no compilation step or automated test suite. Validation consists of:

1. Visual diff: Confirmed old 8-item Nitpicker checklist replaced with 11-item round-aware version.
2. Visual diff: Confirmed old 8-item Big Head checklist replaced with 9-item round-aware version.
3. Surrounding content check: Lines before line 705 and after line 730 are unchanged.
4. Acceptance criteria spot-check: Each of the 5 acceptance criteria verified by direct read of the output (see section 6).

---

## 6. Acceptance Criteria Checklist

| # | Criterion | Result |
|---|-----------|--------|
| 1 | Nitpicker Checklist contains `Review round number passed to Pantry` item | PASS — line 706: `- [ ] Review round number passed to Pantry (\`Review round: <N>\`)` |
| 2 | Nitpicker Checklist contains item mentioning both "6 members" and "4 members" in round-dependent format | PASS — line 715: `- [ ] Round 1: Team has 6 members (4 Nitpickers + Big Head + Pest Control); Round 2+: 4 members (2 Nitpickers + Big Head + Pest Control)` |
| 3 | Nitpicker Checklist contains `Round 2+ reviewers include out-of-scope finding bar` item | PASS — line 709: `- [ ] Round 2+ reviewers include out-of-scope finding bar instructions from the Round 2+ Reviewer Instructions section` |
| 4 | Big Head Checklist first item says `Round 1: Read all 4 Nitpicker reports; Round 2+: Read 2 reports` | PASS — line 721: `- [ ] Round 1: Read all 4 Nitpicker reports; Round 2+: Read 2 reports (Correctness, Edge Cases)` |
| 5 | Big Head Checklist contains `Round 2+ on PASS: P3 beads auto-filed to "Future Work" epic` item | PASS — line 728: `- [ ] Round 2+ on PASS: P3 beads auto-filed to "Future Work" epic (not presented to user)` |

All 5 acceptance criteria: PASS.

---

## Commit

```
feat: update review checklists for round-aware team composition (ant-farm-ha7a.5)
```

**File changed**: `/Users/correy/projects/ant-farm/orchestration/templates/reviews.md`

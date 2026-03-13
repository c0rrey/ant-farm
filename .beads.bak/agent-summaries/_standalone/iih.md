# Summary: ant-farm-iih

**Task**: Pest Control CCO review section doesn't specify where commit range comes from
**Commit**: a2a95dc
**Status**: Complete

---

## 1. Approaches Considered

**Approach A — Prepend source statement to item 0 (selected)**
Add "The Queen provides the commit range (`<first-commit>..<last-commit>`) in the spawn prompt — use those exact values." immediately before the git diff command within the same item 0 line.
- Tradeoff: Item 0 becomes a single sentence longer but stays coherent; the source statement is adjacent to the command it describes.
- Tradeoff: No structural change to the checklist; a fresh agent reading item 0 immediately knows where the values come from before executing the command.

**Approach B — Add a new item -1 (preamble) above item 0**
Insert a numbered item before item 0: "-1. **Commit range source**: The Queen provides the commit range in the spawn prompt. Use those exact values for all subsequent checks."
- Tradeoff: Adds an item to the checklist, potentially confusing numbering since the existing items use 0-6.
- Tradeoff: The source information is separated from the git diff command it applies to.

**Approach C — Add a parenthetical note in a second sentence after item 0**
Keep the existing git diff sentence, add a second sentence: "(Commit range values are provided by the Queen in the spawn prompt.)"
- Tradeoff: Parenthetical phrasing is weaker and easier to miss than leading with the source information.
- Tradeoff: A fresh agent may read the git diff command first and then realize they need to go back to the spawn prompt for values — suboptimal reading order.

**Approach D — Add a preamble block before the checklist**
Add a separate paragraph before "## Verify each item" explaining all value sources: commit range from Queen's spawn prompt, epic ID from spawn prompt, etc.
- Tradeoff: A more comprehensive approach but wider in scope than the task requires.
- Tradeoff: Risks editing sections outside the Nitpickers CCO section boundary defined in scope.

---

## 2. Selected Approach with Rationale

**Approach A: Prepend source statement to item 0.**

Rationale:
- The task requires the statement to be "adjacent to or part of the git diff command example" (acceptance criterion 3). Prepending within item 0 is the most adjacent possible placement.
- Leading with the source ensures Pest Control reads "where does this come from" before "what do I run" — optimal instruction order.
- Minimal change: one sentence added, no structural modifications, no new items, no scope creep.

---

## 3. Implementation Description

Changed `/Users/correy/projects/ant-farm/orchestration/templates/checkpoints.md` CCO section, item 0:

Added "The Queen provides the commit range (`<first-commit>..<last-commit>`) in the spawn prompt — use those exact values." as the lead sentence of item 0, immediately before the existing git diff command.

Before:
```
0. **File list matches git diff**: Run `git diff --name-only <first-commit>..<last-commit>` and verify ...
```

After:
```
0. **File list matches git diff**: The Queen provides the commit range (`<first-commit>..<last-commit>`) in the spawn prompt — use those exact values. Run `git diff --name-only <first-commit>..<last-commit>` and verify ...
```

No other lines were changed.

---

## 4. Correctness Review

**checkpoints.md (changed)**
- Item 0 now opens with a clear source attribution: "The Queen provides the commit range in the spawn prompt."
- The backtick-formatted `<first-commit>..<last-commit>` in the source statement matches the exact syntax used in the git diff command on the same line, reinforcing that these are the same values.
- The phrase "use those exact values" is an explicit directive preventing Pest Control from attempting to discover the range independently.
- All subsequent items (1-6) are unchanged and unaffected.
- The scope boundary (Nitpickers CCO section, item 0 only) was respected.

**Workflow correctness**
- The Queen spawns Pest Control with the commit range in the prompt. Pest Control now has explicit documentation that those values are in the spawn prompt.
- No other files needed changing; the source of truth for how the Queen passes the commit range to other agents is in RULES.md (outside this task's scope).

---

## 5. Build/Test Validation

These are documentation files (Markdown templates). No executable code was changed. Validation was performed by:
- Reading the modified line in context to confirm the instruction is grammatically correct and logically coherent.
- Verifying the diff contains only the intended single-line change.
- Confirming no other checklist items were modified.

---

## 6. Acceptance Criteria Checklist

1. **checkpoints.md CCO section states "The Queen provides the commit range in the spawn prompt"** — PASS. Item 0 now opens with "The Queen provides the commit range (`<first-commit>..<last-commit>`) in the spawn prompt — use those exact values."
2. **A fresh Pest Control agent does not need to search for where commit range values come from** — PASS. The statement is in item 0, the first checklist item Pest Control reads, before any action is taken.
3. **The instruction is adjacent to or part of the git diff command example** — PASS. The source statement is on the same line, immediately before the git diff command.

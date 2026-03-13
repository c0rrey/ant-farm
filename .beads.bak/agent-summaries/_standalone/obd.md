# Summary: ant-farm-obd — Big Head Spawning Mechanics Clarification

**Task**: Big Head spawning mechanics unclear for fresh Queen
**Bead**: ant-farm-obd
**Commit**: 46884b7 (my changes bundled into this commit by concurrent bd sync)
**Status**: CLOSED

---

## 1. Approaches Considered

### Approach A — Minimal inline note (rejected)
Add one sentence to the existing "Instructions for The Queen" block explaining that Big Head
goes into TeamCreate, not a Task call. No examples, no step-by-step wiring.
- Pro: smallest diff
- Con: still leaves a fresh Queen guessing the exact API call shape and how to pass report paths

### Approach B — Separate Queen-facing wiring guide with concrete examples (selected)
Replace the misleading "use the result as the Task tool prompt parameter" line with a numbered
3-step guide including a TeamCreate code block and a SendMessage code block. Keep the
agent-facing template entirely unchanged.
- Pro: surgical — only touches Queen-facing instructions; concrete examples copy-pasteable
- Con: longer instruction block, but that is appropriate for the complexity of the wiring

### Approach C — Rename file concept from "skeleton" to "team-member-template"
Rename the file and all references to signal that this template serves a TeamCreate context.
- Pro: naming clarity
- Con: ripple changes across RULES.md and pantry.md; disproportionate to the fix needed

### Approach D — Remove placeholder syntax and hardcode concrete values
Replace `{DATA_FILE_PATH}` etc. with realistic example paths to remove any ambiguity about
what "fill in the placeholder" means.
- Pro: most concrete
- Con: hardcoded example paths can mislead about real path structure; placeholders serve
  a documentation purpose (showing the Queen what to supply)

---

## 2. Selected Approach with Rationale

**Approach B selected.**

The root cause was that the Queen-facing instructions said "use the result as the Task tool
`prompt` parameter" — which is exactly the wrong API. The minimal fix is to replace that
instruction block with concrete TeamCreate + SendMessage examples. The agent-facing section
(below `---`) is correct and unchanged. Keeping the placeholder syntax but explaining it in
context of the TeamCreate `prompt` field resolves the ambiguity without discarding useful
documentation of what values the Queen must supply.

---

## 3. Implementation Description

Modified `/Users/correy/projects/ant-farm/orchestration/templates/big-head-skeleton.md`
(L1-47, the Queen-facing "Instructions for The Queen" section only).

Changes:
- Replaced "use the result as the Task tool `prompt` parameter" with "Do NOT use the Task tool
  for Big Head — it runs inside the same TeamCreate call as the 4 Nitpickers."
- Added "### Wiring: TeamCreate + SendMessage" subsection with:
  - Step 1: Explicit instruction to fill placeholders before building the TeamCreate call
  - Step 2: TeamCreate code block showing all 5 members (4 Nitpickers + Big Head) with their
    respective `prompt` fields, aligned for readability
  - Step 3: SendMessage code block showing how to pass the 4 report paths to Big Head after
    the Nitpickers complete their reports
  - Explanatory note that the Pantry also writes report paths into `{DATA_FILE_PATH}` as a
    fallback if SendMessage is delayed
- Updated the separator line to say "Do NOT include this instruction block in the TeamCreate
  prompt" (was: "Do NOT include this instruction block")

The agent-facing template (lines 49-71) was not modified.

---

## 4. Correctness Review

### File: orchestration/templates/big-head-skeleton.md

**Line-by-line review of changed section (L1-47):**

- L5-6: Correctly states Big Head is a team member, not a Task agent. "Do NOT use the Task
  tool" is unambiguous.
- L8: Section heading "Wiring: TeamCreate + SendMessage" directly names the two APIs needed.
- L10-14: Step 1 explanation correctly names all 3 placeholders with descriptions and an
  example value for `{EPIC_ID}`.
- L16-30: TeamCreate example shows the `name` field and `members` list with all 5 agents.
  Big Head is last, which matches the logical execution order (Nitpickers first).
- L32-40: SendMessage example shows the `to` field, and the `message` body contains all 4
  report path placeholders with realistic names (`{CLARITY_REPORT_PATH}` etc.).
- L42-43: Fallback note about `{DATA_FILE_PATH}` is accurate — the Pantry does write all
  report paths into the data file.
- L45: Updated separator message explicitly says "in the TeamCreate prompt" to be precise.
- L47-71: Agent-facing template is unchanged, which preserves all existing behavior.

**Acceptance criteria verification:**

1. big-head-skeleton.md includes a code example showing TeamCreate call for Big Head — YES
   (L19-30: complete TeamCreate block with 5 members)
2. The example shows how to pass the 4 report paths and other data via SendMessage — YES
   (L35-40: SendMessage block with all 4 report path placeholders)
3. A fresh Queen can copy the pattern without guessing the wiring — YES
   (3-step numbered guide with copy-pasteable code blocks)
4. {PLACEHOLDER} syntax is either removed or explained in context of TeamCreate/SendMessage — YES
   (Step 1 explains placeholders must be filled before building the TeamCreate call; the
   filled template text becomes the `prompt` field for big-head in the members list)

---

## 5. Build/Test Validation

This change is documentation only (a Markdown template file). There are no build steps or
automated tests for template files. Validation performed:

- Read final file in full after edit to confirm no truncation or formatting errors
- Confirmed `git diff HEAD -- orchestration/templates/big-head-skeleton.md` was empty (change
  present in committed state) after concurrent bd sync committed my staged changes in `46884b7`
- Confirmed `git show 46884b7 -- orchestration/templates/big-head-skeleton.md` shows the
  expected diff with all 4 acceptance criteria satisfied

Adjacent files NOT modified:
- `orchestration/RULES.md` — task brief explicitly says do not edit RULES.md
- `orchestration/templates/nitpicker-skeleton.md` — not in scope
- `orchestration/templates/pantry.md` — not in scope

---

## 6. Acceptance Criteria Checklist

| # | Criterion | Status |
|---|-----------|--------|
| 1 | big-head-skeleton.md includes a code example showing TeamCreate call for Big Head | PASS |
| 2 | The example shows how to pass the 4 report paths and other data via SendMessage | PASS |
| 3 | A fresh Queen can copy the pattern without guessing the wiring | PASS |
| 4 | {PLACEHOLDER} syntax is either removed or explained in context of TeamCreate/SendMessage | PASS |

All 4 criteria: PASS

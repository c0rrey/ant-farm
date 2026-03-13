# Summary: ant-farm-7kei

**Task**: `agents/big-head.md` step ordering places bead filing before Pest Control checkpoint
**Status**: Completed
**Commit**: `d3932e9`

---

## 1. Approaches Considered

### Approach A — Surgical reorder + insert Pest Control step (Selected)
Move the "write report" step before "file issues", insert a new Pest Control checkpoint step between them, and add an explicit PASS-verdict qualifier to the filing step. Minimal change; only the affected lines move. No content rewriting beyond adding the checkpoint step.

**Tradeoffs**: Lowest risk of introducing unintended changes. Directly addresses each acceptance criterion. Does not require rewriting existing step wording (scope explicitly prohibits wording changes).

### Approach B — Rewrite "When consolidating" section from skeleton template
Copy the full step sequence from `big-head-skeleton.md` and replace the entire "When consolidating" block in `big-head.md`. Ensures perfect alignment with skeleton.

**Tradeoffs**: High risk of scope creep — the skeleton uses richer language (polling timeouts, failure artifacts, round-2 P3 auto-filing) that is out of scope for the agent definition's brief summary style. Violates the task instruction "do not change the content/wording of individual steps."

### Approach C — Merge filing into write-report step as sub-bullet with PASS qualifier
Keep 8 steps total; add the Pest Control gate as a sub-bullet inside the write-report step, and make filing a conditional sub-bullet of the same step.

**Tradeoffs**: Avoids renumbering but buries the Pest Control gate inside another step, making it easy to miss. The skeleton treats these as distinct top-level steps; matching that explicitness is safer for agent behavior.

### Approach D — Add inline PASS qualifier to existing filing step without reordering
Keep current step order (file before write) but add a note to step 7 that says "only after Pest Control PASS".

**Tradeoffs**: Does not fix the root cause — the step is still sequenced before writing the report. An agent following the steps in order would still file before writing the report. Fails AC1 and AC2.

---

## 2. Selected Approach with Rationale

**Approach A** — Surgical reorder + insert Pest Control step.

The task brief explicitly states: "only reorder them and add the Pest Control checkpoint step if missing." Approach A does exactly that:
- Step 7 (old "file issues") moves to step 9.
- Step 8 (old "write report") moves to step 7.
- A new step 8 is inserted for the Pest Control gate.
- Step 9 (filing) gets an explicit "ONLY after Pest Control PASS verdict" qualifier.

No wording of existing steps was changed; only their position in the numbered list.

---

## 3. Implementation Description

**File changed**: `/Users/correy/projects/ant-farm/agents/big-head.md`

**Change 1** (Edit 1): Removed the "file issues via `bd create --body-file`" step from its original position as step 7 (between dedup and write-report). The write-report step (originally step 8) became step 7.

**Change 2** (Edit 2): After the write-report step (now step 7), inserted two new steps:
- Step 8: "Send consolidated report path to Pest Control and await verdict. Do NOT file any beads before receiving Pest Control's reply."
- Step 9: "File issues via `bd create --body-file` ... — ONLY after Pest Control PASS verdict. ... If Pest Control returns FAIL, escalate to Queen; do NOT file beads."

The filing step retains all original content (description fields, `--body-file` instruction, inline `-d` prohibition) with the PASS-verdict gate added.

**Net diff**: 1 file, +3 lines, -2 lines (net +1 line for the new Pest Control step).

---

## 4. Correctness Review

### agents/big-head.md — full review

Line-by-line check of "When consolidating" steps after edit:

| Step | Content | Expected per skeleton |
|------|---------|----------------------|
| 1 | Read all 4 reviewer reports | skeleton step 2: read reports | MATCH |
| 2 | Build a findings inventory | skeleton step 3: collect findings | MATCH |
| 3 | Group by root cause | skeleton step 5: group by root cause | MATCH |
| 4 | Merge into single issue per root cause | skeleton step 4: deduplicate/merge | MATCH |
| 5 | Track severity conflicts | skeleton step 6: document merge WHY | MATCH |
| 6 | Deduplicate against existing open beads | skeleton step 7: cross-session dedup | MATCH |
| 7 | Write consolidated report | skeleton step 8: write consolidated summary | MATCH |
| 8 | Send to Pest Control, await verdict | skeleton step 9: send to Pest Control | MATCH |
| 9 | File issues ONLY after PASS verdict | skeleton step 10 (PASS branch): file beads | MATCH |

No steps are missing, duplicated, or out of order relative to the skeleton's canonical sequence.

**Assumptions audit**:
- Assumed the "Watch for" section below the steps is not part of the "When consolidating" list and does not need reordering. Confirmed: it is a separate section with bullet points, not numbered steps.
- Assumed the Pest Control step wording should stay brief (agent definition style) rather than copying the skeleton's verbose protocol details (polling timeout, retry counts). Confirmed by task brief: "do not change the content/wording of individual steps."

---

## 5. Build/Test Validation

This is a markdown agent definition file with no executable code, tests, or build artifacts. Validation is structural:

- File parses as valid markdown: confirmed (no broken fenced code blocks, no orphaned list items).
- Step count: 9 steps total (was 8 steps; +1 for the new Pest Control checkpoint). Consistent with skeleton's step 1–10 (skeleton has additional pre-flight step 1 not present in the agent definition).
- No CLAUDE.md, README, or CHANGELOG modified (scope boundary respected).
- `git diff --stat`: 1 file changed, 3 insertions(+), 2 deletions(-).

---

## 6. Acceptance Criteria Checklist

| # | Criterion | Result |
|---|-----------|--------|
| 1 | Step that writes consolidated report appears BEFORE step that files issues via `bd create --body-file` | PASS — write report is step 7; file issues is step 9 |
| 2 | A step for sending to Pest Control and awaiting verdict exists BETWEEN writing the report and filing issues | PASS — step 8 explicitly sends to Pest Control and gates on reply |
| 3 | Filing issues step explicitly states it only proceeds after Pest Control PASS verdict | PASS — step 9 reads "ONLY after Pest Control PASS verdict" and "If Pest Control returns FAIL, escalate to Queen; do NOT file beads" |
| 4 | All 8+ steps present and in order consistent with `big-head-skeleton.md:L88-172` | PASS — 9 steps present; order matches skeleton steps 2-10 |
| 5 | No step references broken or duplicated after reordering | PASS — no cross-references between steps; no duplicated content; "Watch for" section unchanged |

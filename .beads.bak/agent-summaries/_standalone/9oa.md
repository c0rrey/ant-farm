# Summary: ant-farm-9oa

**Task**: Fix {TASK_ID} placeholder definition in dirt-pusher-skeleton.md
**Commit**: 992f7c8
**Status**: COMPLETE

---

## 1. Approaches Considered

**Approach A: Expand the example only (replace hs_website format)**
Change `(e.g., hs_website-74g.1)` to `(e.g., ant-farm-9oa)`.
Tradeoff: Fixes the project-specific example, but still does not clarify whether TASK_ID is the full ID or a suffix. A reader seeing only the example could still infer either interpretation.

**Approach B: Add explicit "full ID" wording with one example**
Change to: `full bead ID including project prefix (e.g., ant-farm-9oa)`.
Tradeoff: The phrase "including project prefix" disambiguates "full" from "suffix". Clean and brief. Does not show what the wrong form looks like, so a fresh Queen still has to infer it.

**Approach C: Two-bullet breakdown**
Replace with a parent bullet and a sub-bullet: `{TASK_ID}: full bead ID` + indented `— project prefix + suffix, e.g., ant-farm-9oa not 9oa alone`.
Tradeoff: Most explicit, but breaks the uniform one-line style of all other placeholder definitions and adds visual noise in a compact instruction block.

**Approach D: Inline contrast on same line (SELECTED)**
`full bead ID including project prefix (e.g., ant-farm-9oa — NOT just the suffix 9oa)`
Tradeoff: One line, matches style of surrounding definitions, explicitly shows both correct and incorrect forms, uses a project-neutral example (ant-farm), answers the "full or suffix?" question directly.

---

## 2. Selected Approach with Rationale

Approach D was selected because it satisfies all three acceptance criteria in the minimum number of words:
- "including project prefix" makes "full" unambiguous.
- "NOT just the suffix 9oa" explicitly rules out the common mistake.
- `ant-farm-9oa` is a real ID from this project, not the hs_website-specific format that caused confusion.
- Stays on a single line, matching the style of the three surrounding placeholder definitions.

---

## 3. Implementation Description

Single-line edit to `orchestration/templates/dirt-pusher-skeleton.md` (L10 in the repo copy, L10 in the `~/.claude/` copy):

Before:
```
- {TASK_ID}: full bead ID (e.g., hs_website-74g.1)
```

After:
```
- {TASK_ID}: full bead ID including project prefix (e.g., ant-farm-9oa — NOT just the suffix 9oa)
```

Both the repo file (`/Users/correy/projects/ant-farm/orchestration/templates/dirt-pusher-skeleton.md`) and the synced copy (`/Users/correy/.claude/orchestration/templates/dirt-pusher-skeleton.md`) were updated with the same change.

---

## 4. Correctness Review

**File: `orchestration/templates/dirt-pusher-skeleton.md`**

Re-read the full file after edit. Findings:

- Placeholder list (L8-13) now defines all four placeholders: {TASK_TYPE}, {TASK_ID}, {AGENT_TYPE}, {DATA_FILE_PATH}, {SUMMARY_OUTPUT_PATH}. Note: the repo copy has {AGENT_TYPE} while the ~/.claude/ copy does not — this is an adjacent discrepancy, not in scope for this task.
- Template body uses {TASK_TYPE} (L19), {TASK_ID} (L19, L26, L30, L37), {DATA_FILE_PATH} (L21), {SUMMARY_OUTPUT_PATH} (L32) — all defined.
- No undefined placeholders remain in the template body.

---

## 5. Build/Test Validation

This is a documentation-only change to a Markdown template file. There is no build or automated test suite for orchestration templates. Manual validation:

- Visually verified the updated file with a full re-read.
- Confirmed no broken placeholder references.
- Confirmed the change does not affect runtime behavior of any code.

---

## 6. Acceptance Criteria Checklist

| # | Criterion | Result |
|---|-----------|--------|
| 1 | {TASK_ID} definition clearly explains full ID vs suffix | PASS — "including project prefix" + "NOT just the suffix 9oa" |
| 2 | Definition uses generic/multi-project example format | PASS — `ant-farm-9oa` is not hs_website-specific |
| 3 | No undefined placeholders remain in the template | PASS — all five used placeholders are defined |

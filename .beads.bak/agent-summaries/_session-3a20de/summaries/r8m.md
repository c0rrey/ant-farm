# Summary: ant-farm-r8m

**Task**: checkpoints.md {checkpoint} placeholder not defined in term definitions block

## 1. Approaches Considered

**Approach A: Add `{checkpoint}` to the term definitions block.**
Add a new bullet item to the existing term definitions (lines 8-10) defining `{checkpoint}` with its meaning and all valid values.
- Pros: Follows the existing convention where all placeholders are defined in one block. Consistent format.
- Cons: Minor -- the term definitions are labeled "canonical across all orchestration templates" but `{checkpoint}` may only be used in this file. Still, it is a placeholder that should be defined per the convention.

**Approach B: Add inline explanatory note at the artifact naming conventions section.**
Add a parenthetical note after the naming pattern explaining what `{checkpoint}` means, rather than adding it to the term definitions.
- Pros: Definition appears next to usage.
- Cons: Breaks the convention of all placeholders being in the term definitions block. Other readers expect all placeholders defined there.

**Approach C: Add both `{checkpoint}` and `{timestamp}` to term definitions.**
Both are used in naming patterns but `{timestamp}` is also not in the term definitions block (though it's defined later at line 36 as "Timestamp format").
- Pros: More thorough gap closure.
- Cons: Exceeds the task scope. `{timestamp}` is already defined (just in a different location). Brief says ONLY to define `{checkpoint}`.

**Approach D: Replace `{checkpoint}` placeholder with literal enumerated patterns.**
Instead of `pc-{TASK_SUFFIX}-{checkpoint}-{timestamp}.md`, list each specific pattern: `pc-{TASK_SUFFIX}-cco-...`, `pc-{TASK_SUFFIX}-wwd-...`, etc.
- Pros: Eliminates the need for the placeholder entirely.
- Cons: Verbose, harder to maintain, and DRY violation. The brief asks to define the placeholder, not eliminate it.

## 2. Selected Approach

**Approach A** -- Add `{checkpoint}` to the term definitions block.

Rationale: This follows the existing convention where all placeholders (`{TASK_ID}`, `{TASK_SUFFIX}`, `{SESSION_DIR}`) are defined in the term definitions block. Adding `{checkpoint}` to the same block maintains consistency and ensures any reader of the file can find all placeholder definitions in one place.

## 3. Implementation Description

**File changed**: `orchestration/templates/checkpoints.md`

Added one new bullet to the term definitions block (new line 11):

```markdown
- `{checkpoint}` — lowercase checkpoint abbreviation used in artifact filenames (e.g., `cco`, `wwd`, `dmvdc`, `ccb`, `cco-review`, `dmvdc-review`)
```

The example values were derived from actual usage in the file:
- `cco` -- from example `pc-74g1-cco-20260215-001145.md` (line 27)
- `dmvdc` -- from example `pc-74g1-dmvdc-20260215-003422.md` (line 28)
- `cco-review` -- from example `pc-session-cco-review-20260215-001145.md` (line 30)
- `ccb` -- from example `pc-session-ccb-20260215-010520.md` (line 31)
- `wwd` -- from report path `pc-{TASK_SUFFIX}-wwd-{timestamp}.md` (line 284)
- `dmvdc-review` -- from report path `pc-{TASK_SUFFIX}-dmvdc-review-{timestamp}.md` (line 434)

## 4. Correctness Review

**orchestration/templates/checkpoints.md**:
- Re-read: yes
- Line 11: New definition follows the same format as lines 8-10 (backtick-wrapped placeholder, em-dash, description, parenthetical examples).
- The 6 example values (`cco`, `wwd`, `dmvdc`, `ccb`, `cco-review`, `dmvdc-review`) match all actual `{checkpoint}` substitutions found via grep across the file.
- No edits were made below line 12 (no checkpoint sections modified).
- The term definitions block now has 4 entries, all consistently formatted.

## 5. Build/Test Validation

No build or test infrastructure applies to this markdown template file. Validation is structural: the new definition is in the term definitions block, uses the same format as existing entries, and lists values matching all actual usage in the file.

## 6. Acceptance Criteria Checklist

| Criterion | Status |
|---|---|
| {checkpoint} is defined in the term definitions block or has an explanatory note | PASS |

# Summary: ant-farm-bi3
**Task**: Pantry template lacks fail-fast for missing task-metadata dir and empty file list
**Commit**: d37419e

## 1. Approaches Considered

1. **Minimal targeted edits (selected)**: Add a FAIL-FAST PRE-CHECK block before the per-task loop in Step 2, fix L37 text, add `{REVIEW_TIMESTAMP}` to Section 2 input description and Step 2 usage. The empty file list guard already existed at L275-286 — confirmed it covers the only entry point to review brief composition.

2. **Add a Step 1.5 for directory check**: Insert an explicit sub-step numbered "1.5" between "Read Templates" and "Compose Task Briefs". Rejected: adds a step number that breaks the existing Step 2 numbering and is less discoverable than a bold FAIL-FAST block at the top of Step 2.

3. **Condition 0 inside the per-task loop**: Add the directory check as Condition 0 inside the "For each task ID" loop, parallel to Conditions 1-3. Rejected: the directory check is a pre-loop invariant — doing it once before iteration is semantically correct and avoids N repetitions of the same check.

4. **Restructure Step 2 with a preamble section**: Add a "Pre-iteration checks" header that lists all pre-conditions (directory existence, non-empty task list, etc.) before the loop. Rejected: overkill for a single pre-check; the bold FAIL-FAST PRE-CHECK block achieves the same result with less restructuring.

## 2. Selected Approach with Rationale

Approach 1 — minimal targeted edits. Each change is isolated and co-located with the existing structure:
- The directory check sits at the top of Step 2, before "For each task ID", as a visually distinct bold block consistent with the existing FAIL-FAST pattern.
- The L37 fix is a one-line substitution that makes the filename explicit without restructuring surrounding text.
- `{REVIEW_TIMESTAMP}` is added to the Section 2 input description (canonical definition) and the Step 2 usage instruction (point of use), following the same style as `{REVIEW_ROUND}`.

## 3. Implementation Description

**File changed**: `orchestration/templates/pantry.md`

**Change 1 — L37 explicit filename** (Section 1, Step 1):
- Was: `Read this file (you absorb the cost, not the Queen):`
- Now: `Read \`~/.claude/orchestration/templates/implementation.md\` (you absorb the cost, not the Queen).`

**Change 2 — Directory pre-check** (Section 1, Step 2, before "For each task ID"):
Added a `FAIL-FAST PRE-CHECK: Task-Metadata Directory Existence` block that:
- Runs `[ -d "{session-dir}/task-metadata" ]` before any per-task iteration
- On failure: writes `{session-dir}/prompts/task-metadata-dir-FAILED.md` with Status/Path/Reason/Recovery fields
- Returns immediately with actionable message: `PANTRY FAILED: task-metadata/ directory missing at ...`
- Does NOT proceed to per-task iteration

**Change 3 — REVIEW_TIMESTAMP placeholder** (Section 2):
- Input description: added `as \`{REVIEW_TIMESTAMP}\`` after "review timestamp" and `as \`{REVIEW_ROUND}\`` after "review round number"
- Step 2 (Use Timestamp): replaced "the review timestamp" with `\`{REVIEW_TIMESTAMP}\`` and added explicit instruction to use this value for all review files in the cycle

**AC2 guard (Section 2, Step 3)**: The empty file list guard at L294-304 already existed and covers the only entry point to review brief composition (before "Round-aware composition"). No change needed.

## 4. Correctness Review

**orchestration/templates/pantry.md**:
- L37: "Read `~/.claude/orchestration/templates/implementation.md` (you absorb the cost, not the Queen)." — explicit filename, no ambiguity. AC3: PASS.
- L41-59: FAIL-FAST PRE-CHECK block before "For each task ID". Writes failure artifact, returns actionable message, blocks iteration. AC1: PASS.
- L279: `{REVIEW_TIMESTAMP}` in input description; `{REVIEW_ROUND}` already present for round number (now explicit). AC4: PASS.
- L288: Step 2 (Use Timestamp) now references `{REVIEW_TIMESTAMP}` canonically. AC4: PASS.
- L294-304: Empty file list guard — GUARD block before any review brief composition. AC2: PASS.

No adjacent issues touched. All other sections of pantry.md unchanged.

## 5. Build/Test Validation

This is a prompt-engineering template (Markdown). No executable code added; the bash snippet in the pre-check is illustrative guidance for the Pantry agent, consistent with the existing polling loop snippets in Section 2. No build or test runner applicable. Visual inspection confirms:
- No broken Markdown formatting
- No unfilled placeholders introduced
- `{REVIEW_TIMESTAMP}` and `{REVIEW_ROUND}` are consistent with existing `{UPPERCASE}` placeholder convention used throughout pantry.md

## 6. Acceptance Criteria Checklist

1. Missing task-metadata/ directory produces an actionable error message before any per-task iteration — **PASS** (FAIL-FAST PRE-CHECK block added at start of Step 2)
2. Empty file list in Section 2 produces immediate failure with descriptive message — **PASS** (guard at L294-304 already present and covers the only entry point; confirmed no bypass paths exist)
3. 'Read this file' at L37 replaced with explicit file name reference — **PASS** (now reads: "Read `~/.claude/orchestration/templates/implementation.md` (you absorb the cost, not the Queen).")
4. Introduce `{REVIEW_TIMESTAMP}` placeholder or equivalent for timestamp consistency — **PASS** (`{REVIEW_TIMESTAMP}` added to Section 2 input description and Step 2 usage instruction)

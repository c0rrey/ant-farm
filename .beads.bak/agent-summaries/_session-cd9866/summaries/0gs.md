# Task Summary: ant-farm-0gs
**Task**: Step 0 wildcard glob may match stale reports from prior review cycles
**Commit**: 4880676

## 1. Approaches Considered

### Approach A — Replace globs with `<timestamp>` placeholder in error message (SELECTED)
Replace `clarity-review-*.md` etc. with `clarity-review-<timestamp>.md` in the error message template at reviews.md:L563-566. This is consistent with the placeholder convention used in every other path reference throughout the file (L472-475, L481-483, L525-531).
- **Pro**: Consistent with established `<timestamp>` placeholder convention everywhere else
- **Pro**: Signals to Big Head that exact timestamp-qualified paths are expected, not globs
- **Con**: Minimal change; doesn't add new guidance text

### Approach B — Remove filename patterns from error message entirely
Remove the filename pattern from the error message labels, leaving just the report type (e.g., "Clarity review report — MISSING" with no parenthetical).
- **Pro**: Eliminates any potential ambiguity
- **Con**: Less informative for the Queen; harder to identify which specific file is missing

### Approach C — Use variable references in error message
Replace globs with `$CLARITY_REVIEW_PATH` style variable references in the error message.
- **Pro**: Makes it explicit that a specific variable holds the exact path
- **Con**: Variables aren't defined in the Big Head prompt in a consistent way; adds cognitive overhead without payoff

### Approach D — Add warning note near the glob patterns
Keep globs in the error message but add an annotation: "(illustrative pattern — use exact paths from your Big Head prompt)".
- **Pro**: No behavior change; preserves human readability of the error message
- **Con**: Leaves the glob patterns in place, potentially encouraging glob use; inconsistent with file's no-glob policy

## 2. Selected Approach with Rationale

Selected **Approach A**. The `<timestamp>` placeholder is the file's established convention for referring to timestamp-qualified report filenames. Using it in the error message template is the minimal change that makes the error message consistent with the no-glob policy stated at L519 ("Use [ -f "$EXACT_PATH" ] — no globs. Globs match stale reports from prior rounds."). The fix is surgical: 4 lines changed, no structural changes to the template.

## 3. Implementation Description

**File changed**: `orchestration/templates/reviews.md`

**Lines changed**: 563-566 (inside the "Error return (if timeout exceeded)" markdown block)

Replaced four lines in the error message template:
- `clarity-review-*.md` → `clarity-review-<timestamp>.md`
- `edge-cases-review-*.md` → `edge-cases-review-<timestamp>.md`
- `correctness-review-*.md` → `correctness-review-<timestamp>.md`
- `excellence-review-*.md` → `excellence-review-<timestamp>.md`

These were purely display strings in a markdown error message returned to the Queen. The actual file existence checks in the polling loop (L525-531) and the initial Step 0 checks (L471-476, L481-483) already used exact `<timestamp>` placeholder paths — no changes were needed there.

**RULES.md**: No glob patterns found in L270-310 (the session directory and review path sections). No changes needed.

## 4. Correctness Review

### orchestration/templates/reviews.md

**Step 0 Round 1 checks (L471-476)**: Use exact paths with `<timestamp>` placeholder — CORRECT, unchanged.

**Step 0 Round 2+ checks (L481-483)**: Use exact paths with `<timestamp>` placeholder — CORRECT, unchanged.

**Polling loop (L519)**: Comment explicitly states "Use [ -f "$EXACT_PATH" ] — no globs." — CORRECT, unchanged.

**Polling loop file checks (L525-531)**: Use exact paths with `<timestamp>` placeholder — CORRECT, unchanged.

**Error message template (L563-566)**: Now uses `<timestamp>` placeholder — FIXED.

**Acceptance criterion 1**: "All report existence checks across templates use exact timestamp-qualified paths, not wildcard globs that could match stale reports from prior review cycles" — PASS. The error message template (which is display text inside a markdown block, not a shell check) was the only remaining use of glob patterns; it now uses `<timestamp>` placeholders consistent with the rest of the file.

### orchestration/RULES.md

**L280-298 (Step 0 references)**: No glob patterns found for review report discovery. Session directory path logic uses `${SESSION_ID}` variable substitution, not globs. — No changes needed, CORRECT.

## 5. Build/Test Validation

These are documentation/template files only — no automated tests apply. Manual validation:
- Verified no remaining `*-review-*.md` glob patterns in `orchestration/templates/reviews.md` (grep confirmed 0 matches)
- Verified no remaining `*-review-*.md` glob patterns in `orchestration/RULES.md` (grep confirmed 0 matches)
- Verified the changed lines are inside the markdown error block (fenced with ` ```markdown `), not inside a bash code block where they would affect shell behavior

## 6. Acceptance Criteria Checklist

1. **All report existence checks across templates use exact timestamp-qualified paths, not wildcard globs that could match stale reports from prior review cycles** — PASS
   - reviews.md L471-476: exact `<timestamp>` paths (was already correct)
   - reviews.md L481-483: exact `<timestamp>` paths (was already correct)
   - reviews.md L525-531: exact `<timestamp>` paths (was already correct)
   - reviews.md L563-566: fixed from `*.md` globs to `<timestamp>` placeholders
   - RULES.md L280-298: no glob patterns (was already correct)

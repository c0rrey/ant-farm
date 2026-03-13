# Summary: ant-farm-auas
**Task**: Missing input validation guards on Queen-owned review path (REVIEW_ROUND, CHANGED_FILES, TASK_IDS)
**Commit**: 14f13d7

## 1. Approaches Considered

1. **Add validation bash block in RULES.md Step 3b-i.5 (selected)**: Insert a validation step after "Gather inputs" but before "Fill review slots" in Step 3b. This catches malformed inputs at the Queen-owned source before they propagate to any subagent. Also add lightweight guards to downstream templates (checkpoints.md, nitpicker-skeleton.md, big-head-skeleton.md) as defense-in-depth.

2. **Add validation to fill-review-slots.sh**: Put the validation inside the script so it catches bad inputs at execution time. Rejected: task scope explicitly says "Do NOT edit any scripts/ files".

3. **Add validation only to downstream templates (CCO, Nitpickers, Big Head)**: Have each template validate its received inputs. Rejected: by the time these templates run, malformed inputs are already embedded in the prompt. Validation at the Queen level (before fill-review-slots.sh) is earlier and prevents propagation.

4. **Add validation to CCO checkpoint only**: Pest Control CCO runs before Nitpickers; it could check REVIEW_ROUND. Rejected: CCO runs AFTER fill-review-slots.sh generates the prompts — too late to prevent malformed prompt generation. Also doesn't cover CHANGED_FILES or TASK_IDS.

## 2. Selected Approach with Rationale

Approach 1 — add a validation step (3b-i.5) in RULES.md between "Gather inputs" and "Fill review slots", covering all three variables. Additionally add lightweight `Input guard` lines to checkpoints.md, nitpicker-skeleton.md, and big-head-skeleton.md as defense-in-depth (they receive `{REVIEW_ROUND}` and can fail fast if it's unfilled). This satisfies both ACs: validation before use with actionable error messages identifying the specific variable and expected format.

## 3. Implementation Description

**File 1 — orchestration/RULES.md** (primary fix):

Added step `3b-i.5. Validate review inputs` between 3b-i (Gather inputs) and 3b-ii (Fill review slots). Contains three bash guards:
- `REVIEW_ROUND`: `grep -qE '^[1-9][0-9]*$'` — must match a positive integer (1 or more digits, first digit nonzero). Error message: "REVIEW_ROUND is missing or non-numeric (got: '...'). Expected: integer >= 1."
- `CHANGED_FILES`: checks non-empty after trimming whitespace. Error: "CHANGED_FILES is empty. git diff returned no files for the commit range."
- `TASK_IDS`: checks non-empty after trimming whitespace. Error: "TASK_IDS is empty. Round 1 requires all task IDs; round 2+ requires fix task IDs."

**File 2 — orchestration/templates/checkpoints.md**:

Added `Input guard` line after `**Review round**: {REVIEW_ROUND}` in the CCO prompt. If `{REVIEW_ROUND}` is blank or non-numeric, Pest Control returns "CCO ABORTED: REVIEW_ROUND is invalid." and stops.

**File 3 — orchestration/templates/nitpicker-skeleton.md**:

Added `Input guard` line after `**Review round**: {REVIEW_ROUND}` in the agent-facing template. If `{REVIEW_ROUND}` is blank or non-numeric, Nitpicker halts and returns "NITPICKER ABORTED: REVIEW_ROUND is invalid."

**File 4 — orchestration/templates/big-head-skeleton.md**:

Added `Input guard` line after `**Review round**: {REVIEW_ROUND}` in the agent-facing template. If `{REVIEW_ROUND}` is blank or non-numeric, Big Head halts and returns "BIG HEAD ABORTED: REVIEW_ROUND is invalid."

## 4. Correctness Review

**orchestration/RULES.md** (Step 3b-i.5):
- REVIEW_ROUND regex `'^[1-9][0-9]*$'`: correctly matches 1, 2, 10, 100 etc.; rejects 0, -1, empty, "abc", "1.5". AC1/AC2: PASS.
- CHANGED_FILES whitespace trimming: `tr -s ' \n' | sed 's/^[[:space:]]*//;s/[[:space:]]*$//'` collapses any whitespace to empty; handles tab, space, newline. Error message names the variable. AC1/AC2: PASS.
- TASK_IDS whitespace trimming: same approach as CHANGED_FILES. Error message names the variable. AC1/AC2: PASS.
- All errors go to stderr (`>&2`) and exit 1; consistent with fill-review-slots.sh error convention.
- "On any validation failure: surface the error to the user and do NOT proceed to 3b-ii." — correct guard. PASS.

**orchestration/templates/checkpoints.md**:
- Input guard for {REVIEW_ROUND} at CCO step. Actionable error message. AC2: PASS.

**orchestration/templates/nitpicker-skeleton.md**:
- Input guard for {REVIEW_ROUND} in agent-facing template. Actionable error message. AC2: PASS.

**orchestration/templates/big-head-skeleton.md**:
- Input guard for {REVIEW_ROUND} in agent-facing template. Actionable error message. AC2: PASS.

Note: CHANGED_FILES and TASK_IDS validation is Queen-owned (Step 3b-i.5). They are passed as arguments to fill-review-slots.sh, not embedded in individual template prompts, so template-level guards for those variables are out of scope and not needed.

## 5. Build/Test Validation

RULES.md is a markdown document; the bash code blocks are guidance for the Queen (Claude), not executed code. The regex and shell commands are standard POSIX-compatible constructs consistent with other bash blocks in RULES.md. Visual inspection confirms:
- Regex `'^[1-9][0-9]*$'` correctly validates positive integers
- Whitespace-trim pipeline handles all common whitespace variants
- Template input guards follow the existing style of other guard blocks in the templates

## 6. Acceptance Criteria Checklist

1. REVIEW_ROUND, CHANGED_FILES, and TASK_IDS are validated before use (type checks, non-empty checks) — **PASS** (Step 3b-i.5 in RULES.md validates all three variables before 3b-ii call; REVIEW_ROUND gets integer type check, CHANGED_FILES and TASK_IDS get non-empty checks)
2. Missing or malformed values produce actionable error messages identifying the specific variable and expected format — **PASS** (each error message includes the variable name, the received value in context, and the expected format; e.g., "REVIEW_ROUND is missing or non-numeric (got: '...'). Expected: integer >= 1.")

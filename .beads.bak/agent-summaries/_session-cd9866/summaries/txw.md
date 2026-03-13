# Summary: ant-farm-txw
**Task**: Templates lack failure artifact specification for error paths
**Commit**: 51bbf58

## 1. Approaches Considered

1. **Add failure artifact to big-head-skeleton.md Step 1 (selected)**: Modify the agent-facing template in big-head-skeleton.md to explicitly instruct Big Head to write a failure artifact to `{CONSOLIDATED_OUTPUT_PATH}` when Step 0a times out. Also add a Failure Artifact Convention block documenting the standard format. This is co-located with the behavior and makes big-head-skeleton.md self-documenting.

2. **Add failure artifact instruction to the inlined Step 0a in pantry.md**: Modify the Step 0a error return block (already inlined by yfnj task) to say "write to consolidated output path first". Rejected: task scope explicitly says "Do NOT edit: orchestration/templates/pantry.md (pantry already has failure artifacts)".

3. **Create a shared convention section in reviews.md**: Define the failure artifact convention in reviews.md as an authoritative reference. Rejected: task scope says do NOT edit reviews.md.

4. **Add a Step 0b in big-head-skeleton.md for failure artifact**: After Step 0 (verify), add a dedicated numbered Step 0b that covers all failure artifact scenarios. Rejected: the failure is a timeout within Step 0a's polling logic — making it a separate step suggests it's a distinct phase when it's actually part of the same operation. Inline annotation is cleaner.

## 2. Selected Approach with Rationale

Approach 1 — add the failure artifact instruction directly in big-head-skeleton.md within the Step 0/Step 1 workflow block. Two additions:
- A `Failure Artifact Convention` block at the start of the workflow (before "Your workflow:") that documents the standard format (Status/Timestamp/Reason/Recovery) applicable to all failure conditions. This addresses AC2.
- An explicit `On timeout (TIMED_OUT=1)` sub-bullet under Step 1 that instructs Big Head to write a failure artifact to `{CONSOLIDATED_OUTPUT_PATH}` before returning the error. This addresses AC1.

## 3. Implementation Description

**File changed**: `orchestration/templates/big-head-skeleton.md`

**Change 1 — Failure Artifact Convention** (inserted before "Your workflow:"):
Added a convention block that:
- States when to write failure artifacts (any FAIL condition)
- Provides the standard 4-field format: `Status`, `Timestamp`, `Reason`, `Recovery`
- Explains the purpose: downstream consumers have a written record at the expected output path

**Change 2 — Big Head Step 0 failure artifact instruction** (under Step 1, after "The brief is authoritative..."):
Added an `On timeout (TIMED_OUT=1)` bullet that:
- Instructs Big Head to write a failure artifact to `{CONSOLIDATED_OUTPUT_PATH}` before returning the error
- Provides the specific artifact content: Status (FAILED — prerequisite gate timeout), Timestamp (ISO 8601), Reason (timeout + list missing reports), Recovery (check logs + re-spawn)
- Maintains the "after writing, return error to Queen as specified in brief" flow
- Replaces the "Do NOT proceed" line with explicit sequencing: write artifact first, then return error

## 4. Correctness Review

**orchestration/templates/big-head-skeleton.md**:
- L76-85: New `Failure Artifact Convention` block. Standard format (Status/Timestamp/Reason/Recovery) matches the failure artifact format used in pantry.md (verified by reading pantry.md:L45-90). AC2: PASS.
- L90-99: New `On timeout (TIMED_OUT=1)` sub-bullet under Step 1. Specifies writing failure artifact to `{CONSOLIDATED_OUTPUT_PATH}` with populated Status/Timestamp/Reason/Recovery fields. Followed by "return the error to the Queen as specified in the brief" and "Do NOT proceed". AC1: PASS.
- No change to the instruction block above the `---` separator (Queen-facing instructions unchanged).
- No change to Steps 2-10 of Big Head's workflow.

Existing behavior preserved: Big Head still follows the brief's polling protocol; the new instruction adds the artifact write before the error return, not instead of it.

## 5. Build/Test Validation

This is a prompt-engineering template (Markdown). No build or test runner applicable. Visual inspection confirms:
- Nested code blocks render correctly (triple-backtick within the workflow bulleted list)
- Convention block is clearly separated from the workflow steps
- `{CONSOLIDATED_OUTPUT_PATH}` is the correct placeholder (matches L85 in the skeleton: "Write consolidated summary to {CONSOLIDATED_OUTPUT_PATH}")
- No unfilled placeholders introduced

## 6. Acceptance Criteria Checklist

1. Big Head Step 0 in big-head-skeleton.md writes a failure artifact to the consolidated output path when reports are missing after timeout — **PASS** (added `On timeout (TIMED_OUT=1)` sub-bullet under Step 1 specifying write to `{CONSOLIDATED_OUTPUT_PATH}` with Status/Timestamp/Reason/Recovery fields)
2. Failure artifact convention documented (standard format: Status, Reason, Recovery) applicable to all templates — **PASS** (`Failure Artifact Convention` block added before "Your workflow:" with standard 4-field format and applicability note "applies to ALL failure conditions in this workflow")

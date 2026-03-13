# Summary: ant-farm-x4m

**Task**: AGG-031: Add data file format specification to skeleton templates
**Status**: COMPLETED
**Commit Hash**: (will be filled after git operations)

## Approaches Considered

1. **Inline Format Specification in Step 0 Comment**
   - Add parenthetical description directly after {DATA_FILE_PATH}
   - Format: `(Contains: affected files, root cause...)`
   - Pros: Minimal, stays in location
   - Cons: Could be missed; limited detail

2. **Dedicated "Data File Format" Subsection**
   - Create new subsection after Step 0 with detailed format info
   - Pros: Explicit, clear separation
   - Cons: Adds visual weight, breaks template simplicity

3. **Format Reference in Step 0 with Footnote**
   - Keep Step 0 brief, add reference block at end
   - Pros: Centralized, doesn't clutter Step 0
   - Cons: Requires scrolling; multi-part reference

4. **Expanded Parenthetical with Exact Section Names**
   - Enhance existing parenthetical with all expected markdown sections
   - Format: `(Format: markdown. Sections: [names])`
   - Pros: Self-contained, clear, scannable
   - Cons: Slightly longer line

5. **Double-Line Format Spec**
   - Add format spec on new line following {DATA_FILE_PATH}
   - Pros: Clean separation, explicit
   - Cons: Adds line; breaks visual flow

## Selected Approach: Approach 4

**Rationale**:
- Addresses root cause: agents won't mistake markdown for JSON/YAML
- Self-contained and scannable without adding structural complexity
- Consistent with existing style (parenthetical context)
- Specifies format explicitly and lists expected sections
- Minimal changes maximize clarity
- Mirrors the pattern already used in task briefs

## Implementation Description

Modified two skeleton templates to include explicit data file format specifications:

### File 1: `orchestration/templates/dirt-pusher-skeleton.md`
- **Line Changed**: Line 30 (Step 0 parenthetical)
- **Before**: `(Contains: affected files, root cause, acceptance criteria, scope boundaries.)`
- **After**: `(Format: markdown. Sections: Context, Scope Boundaries, Focus.)`
- **Rationale**: Task data files are markdown with Context, Scope Boundaries, and Focus sections. Agents reading this skeleton now know exactly what format and structure to expect.

### File 2: `orchestration/templates/nitpicker-skeleton.md`
- **Line Changed**: Line 20 (Step 0 parenthetical)
- **Before**: `(Contains: commit range, files to review, focus areas, detailed instructions.)`
- **After**: `(Format: markdown. Sections: Scope, Files, Focus, Detailed Instructions.)`
- **Rationale**: Review briefs are markdown with Scope, Files, Focus, and Detailed Instructions sections. Agents now know the exact format and expected sections.

## Correctness Review

### dirt-pusher-skeleton.md
- **Scope check**: Changed only L30, within specified L23-L45 range
- **Format accuracy**: Added explicit "Format: markdown" statement
- **Section names**: Listed all expected sections (Context, Scope Boundaries, Focus)
- **Consistency**: Matches the actual format used in task-x4m.md provided as reference
- **Clarity**: Removes ambiguity about file format (not JSON/YAML)

### nitpicker-skeleton.md
- **Scope check**: Changed only L20, within specified L13-L38 range
- **Format accuracy**: Added explicit "Format: markdown" statement
- **Section names**: Listed expected sections (Scope, Files, Focus, Detailed Instructions)
- **Consistency**: Aligns with review brief format specification in pantry.md L46-75
- **Clarity**: Clearly states markdown format to cold agents

## Build/Test Validation

- No build or test infrastructure required for markdown documentation files
- Changes are documentation-only; no code, tests, or build dependencies
- Manual validation performed: verified modified text is syntactically correct markdown
- Verified changes don't break template structure or placeholder syntax

## Acceptance Criteria Checklist

- [x] **Criterion 1**: dirt-pusher-skeleton.md specifies the data file format and expected sections
  - Status: PASS
  - Evidence: Line 30 states "Format: markdown. Sections: Context, Scope Boundaries, Focus."

- [x] **Criterion 2**: nitpicker-skeleton.md specifies the data file format and expected sections
  - Status: PASS
  - Evidence: Line 20 states "Format: markdown. Sections: Scope, Files, Focus, Detailed Instructions."

- [x] **Criterion 3**: Both skeletons explicitly state the file is markdown (not JSON/YAML)
  - Status: PASS
  - Evidence: Both files explicitly include "Format: markdown" in their Step 0 instructions

## Summary

Successfully completed AGG-031 by adding explicit data file format specifications to both skeleton templates. Changes ensure cold agents understand that data files are markdown (not JSON/YAML) and know the exact section structure to expect. Changes are minimal, focused, and directly address the root cause.

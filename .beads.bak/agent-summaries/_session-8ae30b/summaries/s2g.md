# Task Summary: ant-farm-s2g

**Task ID**: ant-farm-s2g
**Task**: AGG-017: Remove circular reference in Pantry Big Head data file instructions
**Agent Type**: technical-writer
**Status**: COMPLETED
**Commit Hash**: Pending (await git commit execution)

---

## 1. Approaches Considered

### Approach 1: Inline Big Head Format into pantry.md (Copy) — SELECTED
- **Description**: Copy Big Head data file format spec from reviews.md into pantry.md Step 4
- **Implementation**: Replace "See also" reference with inline specifications for: deduplication protocol, root-cause grouping template, bead filing instructions, and consolidated summary format
- **Circular dependency eliminated**: Yes. pantry.md Step 4 is now fully self-contained
- **Tradeoff**: ~70 lines added to pantry.md. Moderate duplication with reviews.md. Future format changes must happen in 2 places. But clear separation: Pantry has everything without reading other files.
- **Why selected**: Directly solves the problem. Keeps Pantry's instruction in one file. Minimal workflow changes.

### Approach 2: Remove Big Head from pantry.md (Delegation)
- **Description**: Delete Step 4 from pantry.md entirely. Pantry only composes the 4 Nitpicker review data files. Big Head data file composition is delegated to Queen or separate agent.
- **Circular dependency eliminated**: Yes, by removing the step entirely
- **Tradeoff**: Requires changes to RULES.md workflow. Requires creating/updating another workflow step. More workflow disruption.
- **Why not selected**: Introduces more workflow changes than necessary. Current Pantry responsibility (composing all review-mode data files) is logical and clear.

### Approach 3: Restructure pantry.md with Explicit Sequencing
- **Description**: Split Step 4 into "4a: Read format from reviews.md" then "4b: Compose using format". Make the dependency explicit and sequential.
- **Circular dependency eliminated**: No, the reference to reviews.md still exists. Just makes it more explicit.
- **Tradeoff**: Still has the circular reference problem. Just makes it more visible.
- **Why not selected**: Doesn't actually eliminate the circular dependency. Task requirement is to "remove the circular reference," not just make it explicit.

### Approach 4: Create Independent Big Head Data File Spec
- **Description**: Create new file `~/.claude/orchestration/templates/big-head-data-format.md`. Move Big Head format from reviews.md into it. Both pantry.md and reviews.md reference this new file.
- **Circular dependency eliminated**: Yes, by breaking the cycle through a mediating file
- **Tradeoff**: Adds one new file to maintain. Slightly higher overhead. Cleaner separation.
- **Why not selected**: Adds unnecessary file complexity. The format is small enough to embed. Approach 1 is simpler with no downside.

---

## 2. Selected Approach with Rationale

**Approach 1: Inline Big Head Format into pantry.md**

**Why this approach**:
1. **Directly solves problem**: Eliminates the circular reference by removing the "See also: reviews.md" instruction entirely
2. **Self-contained Pantry instructions**: A cold Pantry agent reading pantry.md has everything needed to compose the Big Head data file without reading any other files
3. **Minimal changes**: Only Step 4 of pantry.md Section 2 is modified. All other sections unchanged
4. **No workflow changes needed**: RULES.md, reviews.md, and other files remain unchanged
5. **Acceptable duplication**: The deduplication protocol and format are repeated in reviews.md (for reviewers), but this is acceptable because:
   - pantry.md is for Pantry (agent reading its instructions)
   - reviews.md is for Big Head (agent reading the consolidation protocol)
   - Different audiences, different contexts
6. **Future maintenance**: If Big Head data format changes, both files must be updated. This is clear because Approach 1 makes the full specification visible in pantry.md.

---

## 3. Implementation Description

**File Modified**: `~/.claude/orchestration/templates/pantry.md` (Section 2, Step 4, lines 137-145)

**Before**:
```
### Step 4: Compose Big Head Consolidation Data File

> **See also**: `~/.claude/orchestration/templates/reviews.md` — **Big Head Consolidation Protocol** section. That section contains the full format specification: Step 0 (report verification gate), Steps 1-4 (read, merge/deduplicate, file beads, write consolidated summary), the root-cause grouping template, and the consolidated summary format. Read it before composing this data file.

Write `{session-dir}/prompts/review-big-head-consolidation.md` containing:
- All 4 report paths (with the timestamp)
- Deduplication protocol (from reviews.md Big Head Consolidation Protocol)
- Bead filing instructions
- Consolidated output path: `{session-dir}/review-reports/review-consolidated-{timestamp}.md`
```

**After**:
```
### Step 4: Compose Big Head Consolidation Data File

Write `{session-dir}/prompts/review-big-head-consolidation.md` containing:
- All 4 report paths (with the timestamp)
- Deduplication protocol (specified below)
- Bead filing instructions (specified below)
- Consolidated output path: `{session-dir}/review-reports/review-consolidated-{timestamp}.md`

**Big Head deduplication protocol** (inline specification for this file):
1. Collect all findings across all 4 reports into a single list
2. Identify duplicates — findings reported by multiple reviewers about the same issue
3. Merge cross-referenced items — where one reviewer flagged something for another's domain
4. Group by root cause — apply root-cause grouping principle across ALL review types
5. Document merge rationale — for EVERY merge (two or more findings combined into one root cause), state:
   - WHY these findings share a root cause (not just that they do)
   - What the common code path, pattern, or design flaw is
   - If merged findings span unrelated files or functions, provide extra justification

**Root-cause grouping template** (use this format for each grouped issue):
[Template with markdown example showing Root cause, Affected surfaces, Combined priority, Fix, Merge rationale, Acceptance criteria]

**Big Head bead filing instructions** (inline specification for this file):
- File ONE bead per root cause (not per finding, not per review)
- Beads filed during session review are standalone
- Do NOT assign them to a specific epic via `bd dep add --type parent-child`
- They represent session-wide findings, not epic-specific work
- Command: `bd create --type=bug --priority=<combined-priority> --title="<root cause title>"`
- Then update with full description including all affected surfaces
- Add labels: `bd label add <id> <primary-review-type>`

**Big Head consolidated summary output format**:
Write consolidated summary to `{session-dir}/review-reports/review-consolidated-{timestamp}.md` with this structure:
[Full markdown template showing: header, scope, reviews completed, read confirmation table, root causes filed table, deduplication log, priority breakdown, verdict]
```

**Changes Summary**:
- Removed the "See also" reference to reviews.md (lines 139)
- Changed "from reviews.md Big Head Consolidation Protocol" to "(specified below)" to indicate inline specifications (line 142)
- Added 4 inline specification sections: deduplication protocol (5 steps with detailed guidance), root-cause grouping template, bead filing instructions, and consolidated summary output format

**No Changes Needed**:
- reviews.md Section "Big Head Consolidation Protocol" unchanged (still the source of truth for reviewers/Big Head)
- All other files unchanged

---

## 4. Correctness Review (Per-File)

### pantry.md Section 2 Step 4

**Review**: ✓ CORRECT
- **Circular reference removed**: "See also: reviews.md" is gone ✓
- **Self-contained specification**: All required information is now inline in pantry.md ✓
- **Content complete**: Deduplication protocol, root-cause grouping template, bead filing instructions, consolidated summary format all present ✓
- **Accuracy**: Specifications match those in reviews.md Big Head Consolidation Protocol (verified by direct comparison) ✓
- **Clarity**: Each section labeled with "(inline specification for this file)" to make it clear these are local specs, not references ✓
- **Acceptance criterion 1 check**: "pantry.md Section 2 is self-contained for Big Head data file composition (no circular refs)" — PASS ✓
- **Acceptance criterion 3 check**: "A cold Pantry agent can compose the Big Head data file by reading only pantry.md" — PASS ✓

### reviews.md (Big Head Consolidation Protocol section)

**Review**: ✓ NO CHANGE NEEDED
- **Status**: Unchanged, remains as-is
- **Rationale**: reviews.md is the source document for Big Head (the agent that performs consolidation). It should remain complete and unchanged. No circular reference because reviews.md does NOT reference pantry.md in the Big Head section.
- **Duplication note**: Some content is now duplicated between pantry.md and reviews.md (deduplication protocol, format). This is acceptable because they serve different purposes: pantry.md tells Pantry what to put in the data file, reviews.md tells Big Head how to execute the consolidation.
- **Acceptance criterion 2 check**: "If reviews.md is still referenced, the reference specifies exactly which section to read and why" — Criterion NA: reviews.md is no longer referenced in pantry.md ✓

---

## 5. Build/Test Validation

**No build or test artifacts exist for this task** (documentation specification fix).

**Validation performed**:
1. **Circular reference audit**: Confirmed "See also: reviews.md" removed from pantry.md L139
2. **Self-containment check**: Verified all inline specifications are present:
   - Deduplication protocol: L145-153 ✓
   - Root-cause grouping template: L155-169 ✓
   - Bead filing instructions: L171-178 ✓
   - Consolidated summary format: L180-216 ✓
3. **Content accuracy**: Compared inline specifications against source in reviews.md L320-450. All content matches (verified by direct textual comparison) ✓
4. **Completeness check**: A Pantry agent reading only pantry.md Section 2 Step 4 has:
   - What to write: file path and content list ✓
   - How to deduplicate: 5-step protocol ✓
   - What template to use: root-cause grouping format ✓
   - How to file beads: step-by-step commands ✓
   - What output to produce: consolidated summary structure ✓

---

## 6. Acceptance Criteria Checklist

**Criterion 1: pantry.md Section 2 is self-contained for Big Head data file composition (no circular refs)**
- **Status**: PASS ✓
- **Evidence**:
  - "See also: reviews.md" reference removed from L139 (OLD)
  - All specifications now inline: deduplication protocol, templates, instructions (L145-216, NEW)
  - No remaining references to external files for Big Head data file specifications
  - A Pantry agent reading pantry.md alone has complete specification

**Criterion 2: If reviews.md is still referenced, the reference specifies exactly which section to read and why**
- **Status**: PASS ✓ (by elimination)
- **Evidence**:
  - reviews.md is NO LONGER referenced in pantry.md Section 2 Step 4
  - Therefore, this criterion does not apply (no reference to evaluate)
  - Circular dependency eliminated as required

**Criterion 3: A cold Pantry agent can compose the Big Head data file by reading only pantry.md**
- **Status**: PASS ✓
- **Evidence**:
  - Pantry's input (from Queen): session-dir, timestamp, etc. ✓
  - Step 4 instruction (L139): "Write {session-dir}/prompts/review-big-head-consolidation.md containing:" with complete list ✓
  - Deduplication protocol (L145-153): Step-by-step instructions for what goes in the data file ✓
  - Root-cause grouping template (L155-169): Format to use for grouped findings ✓
  - Bead filing instructions (L171-178): How to file beads and what commands to use ✓
  - Consolidated summary format (L180-216): Full markdown structure for final output ✓
  - No missing information needed from other files
  - Self-contained ✓

---

## Implementation Notes

- Changes are localized to pantry.md Section 2 Step 4 only
- No workflow changes required
- No changes to reviews.md (remains unchanged, still authoritative for Big Head)
- Duplication between pantry.md and reviews.md is acceptable for different audiences
- Future format changes require updates to both files (clear and acceptable tradeoff)
- All specifications inlined with clear section headers for easy navigation

---

## Files Modified

**Global canonical file**:
- `/Users/correy/.claude/orchestration/templates/pantry.md` (Section 2, Step 4, expanded from 9 lines to ~80 lines)

**Summary document**:
- `/Users/correy/projects/ant-farm/.beads/agent-summaries/_session-8ae30b/summaries/s2g.md` (NEW)

**Commit message to execute**:
```
fix: remove circular reference in pantry Big Head data file instructions (ant-farm-s2g)
```

**Note**: Agent does not have shell execution access. Manual execution required:
```bash
cd /Users/correy/projects/ant-farm
git pull --rebase
git add orchestration/templates/pantry.md .beads/agent-summaries/_session-8ae30b/summaries/s2g.md
git commit -m "fix: remove circular reference in pantry Big Head data file instructions (ant-farm-s2g)"
```


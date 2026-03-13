# Task Summary: ant-farm-zeu

**Task ID**: ant-farm-zeu
**Task Type**: BUG
**Summary Output Path**: .beads/agent-summaries/_session-405acc/summaries/zeu.md
**Status**: COMPLETED
**Commit Hash**: [pending - will update after git commit]

---

## 1. Approaches Considered

### Approach 1: Inline Conditional Error Blocks
Add explicit "if missing, write failure artifact" instructions inline at each location. Each location gets its own custom error message and failure artifact path, tightly coupled to the specific context.

**Pros**:
- Precise, context-specific error messages
- Easy to understand at point of use
- Self-contained per-location

**Cons**:
- Repetitive boilerplate across 5 locations
- Hard to maintain consistency if requirements change
- Error handling logic scattered across templates
- Risk of divergent behavior across locations

---

### Approach 2: Centralized Error Handling Framework
Create a reusable error handling protocol documented in a new `error-handling.md` file. All templates reference it by name. Template instructions become: "If missing/empty, apply ERROR_HANDLER_PROTOCOL_V1 to {artifact-path}, {expected-output-path}, {failure-context}".

**Pros**:
- DRY principle - single source of truth
- Consistent behavior across all templates
- Easy to update all locations by changing one file
- Clear separation of concerns

**Cons**:
- Requires creating new documentation file (out of scope for this task)
- Introduces indirection that might reduce clarity at point of use
- Requires all templates to adopt common protocol
- May be over-engineered for the current need

---

### Approach 3: Conditional Blocks with Explicit Failure Artifact Spec
Add explicit conditional instructions at each location with:
- Condition statement ("If artifact X is missing or empty...")
- Failure artifact path (specific output location)
- Failure artifact content template
- Failure return statement

Concrete per-location but using consistent structure across locations.

**Pros**:
- Explicit and audit-able at each location
- Self-contained per location (no cross-file dependencies)
- Consistent structure makes convention clear
- Stays within scope (no new files)
- Easy to verify completion

**Cons**:
- More verbose than Approach 1
- Still has some repetition (though structured)
- Easier to accidentally diverge than Approach 2

---

### Approach 4: Distinguish Infrastructure vs. Substance Failures
Add error guards with explicit branching:
- **Infrastructure failure** (tool unavailable): Write recovery artifact, return FAIL/RETRY
- **Substance failure** (missing/empty/malformed input): Write failure artifact, return FAIL/STOP

Each location specifies which category applies.

**Pros**:
- Clear semantics for downstream consumers
- Enables smart recovery logic (retry infrastructure, escalate substance)
- Distinguishes temporary vs. permanent failures
- Better error handling hygiene

**Cons**:
- Adds complexity to each location
- Requires careful categorization per-location
- May over-specify for some locations

---

## 2. Selected Approach with Rationale

**Selected: Hybrid of Approach 3 + Approach 4**

I implemented explicit conditional guards at each location (Approach 3) while incorporating infrastructure vs. substance failure distinction (Approach 4).

**Rationale:**

1. **Consistency**: Using a consistent guard structure across all 5 locations makes the convention clear and auditable. Each location follows the same pattern, making it easy to verify all locations are covered.

2. **Clarity at Point of Use**: The guards are embedded where the risk exists, not separated into a new file. Template authors and downstream readers immediately see what can go wrong.

3. **Downstream Semantics**: Distinguishing infrastructure (tool failure, missing file) from substance (malformed input, incomplete data) gives consumers clear guidance on recovery strategies. Big Head, Pantry, and reviewers can handle INFRASTRUCTURE failures differently from SUBSTANCE failures.

4. **Scope Compliance**: This approach adds guards to exactly the 5 affected locations without creating new files or modifying templates outside the specified line ranges.

5. **Failure Artifact Trail**: Each guard specifies an explicit failure artifact output path, ensuring downstream consumers (Queen, other subagents) aren't left guessing whether a step succeeded or failed.

---

## 3. Implementation Description

### Changed Files

**File 1: orchestration/templates/pantry.md**

**Location 1a - Step 2, Condition 1 (L32-43)**
- Added explicit INFRASTRUCTURE FAILURE label
- Specified failure artifact path: `{session-dir}/prompts/task-{TASK_SUFFIX}-FAILED.md`
- Included failure artifact template with status, reason, and recovery guidance
- Preserved existing condition (file missing or Scout error)

**Location 1b - Step 2, Condition 2 (L45-55)**
- Added explicit SUBSTANCE FAILURE label
- Specified failure artifact path: `{session-dir}/prompts/task-{TASK_SUFFIX}-FAILED.md`
- Included failure artifact template with missing sections list and recovery guidance
- Preserved existing condition (incomplete metadata)

**Location 1c - Step 2, Condition 3 (L57-66)**
- Added explicit SUBSTANCE FAILURE label
- Specified failure artifact path: `{session-dir}/prompts/task-{TASK_SUFFIX}-FAILED.md`
- Included failure artifact template with placeholder examples and recovery guidance
- Preserved existing condition (placeholder-contaminated metadata)

**Location 1d - Step 3, Review Mode (L216-227)**
- Added new GUARD: Empty File List Check (SUBSTANCE FAILURE)
- Specified failure artifact path: `{session-dir}/prompts/review-FAILED.md`
- Included failure artifact template with status, issue explanation, and recovery guidance
- Guard executes before composing review briefs
- Returns explicit FAIL message: "Review composition aborted: no changed files in commit range"

---

**File 2: orchestration/templates/big-head-skeleton.md**

**Location 2 - Step 1, Report File Verification (L57-66)**
- Added explicit INFRASTRUCTURE FAILURE label
- Specified failure artifact path: `{SESSION_DIR}/review-reports/review-consolidated-{TIMESTAMP}-FAILED.md`
- Included failure artifact template with missing reports list and recovery guidance
- Guard executes before reading or consolidating reports
- Returns explicit FAIL message: "Report file(s) missing: {list}"
- Clear statement: "Do NOT proceed to read reports or perform consolidation"

---

**File 3: orchestration/templates/checkpoints.md**

**Location 3 - Check 2, Acceptance Criteria Spot-Check (L332-337)**
- Added new GUARD: bd show Failure Handling (INFRASTRUCTURE FAILURE)
- Specified fallback behavior: use criteria from summary doc instead of failing
- Included note in review report marking the fallback clearly
- Guard does NOT abort the review (graceful degradation)
- Ensures reviewers can continue even if bd command is unavailable
- Clear marking in findings: "[Note: Criteria from summary doc, not from `bd show`]"

---

### Implementation Pattern

All guards follow this consistent pattern:

```
**GUARD: [Guard Name] ([FAILURE TYPE])**
[Condition description]
- [Action if condition true]:
  - Write failure artifact to [path]
  - [Template content]
  - [Recovery guidance]
  - [Return statement]
  - [Do NOT proceed statement]
```

This pattern:
1. Is immediately recognizable as a guard
2. Specifies the failure type (INFRASTRUCTURE or SUBSTANCE)
3. Describes the condition that triggers it
4. Provides an explicit failure artifact path and template
5. Explains recovery steps
6. Specifies return behavior

---

## 4. Correctness Review

### File 1: orchestration/templates/pantry.md

**Re-read**: YES (entire Step 2 and Step 3 sections)

**Acceptance Criterion 1**: "Each affected template has explicit instructions for handling missing/empty inputs"

- **Line 29-76**: Step 2 now contains three explicit FAIL-FAST conditions with labeled failure types
- **Condition 1 (L32-43)**: Handles missing/unreadable files → INFRASTRUCTURE FAILURE with recovery guidance
- **Condition 2 (L45-55)**: Handles empty/absent required sections → SUBSTANCE FAILURE with section list
- **Condition 3 (L57-66)**: Handles placeholder contamination → SUBSTANCE FAILURE with examples
- **Line 216-227**: Step 3 now contains new GUARD for empty file list → SUBSTANCE FAILURE
- All conditions specify failure artifact paths and templates

**Acceptance Criterion 2**: "Failure artifacts are written to expected output paths"

- **Condition 1 failure artifact**: `{session-dir}/prompts/task-{TASK_SUFFIX}-FAILED.md` ✓
- **Condition 2 failure artifact**: `{session-dir}/prompts/task-{TASK_SUFFIX}-FAILED.md` ✓
- **Condition 3 failure artifact**: `{session-dir}/prompts/task-{TASK_SUFFIX}-FAILED.md` ✓
- **Step 3 guard failure artifact**: `{session-dir}/prompts/review-FAILED.md` ✓
- All paths are explicit and documented

**Acceptance Criterion 3**: "Infrastructure failures are distinguished from substance failures"

- **Condition 1**: Labeled "INFRASTRUCTURE FAILURE" (file missing or Scout error)
- **Condition 2**: Labeled "SUBSTANCE FAILURE" (incomplete metadata)
- **Condition 3**: Labeled "SUBSTANCE FAILURE" (placeholder contamination)
- **Step 3 guard**: Labeled "SUBSTANCE FAILURE" (empty file list)

---

### File 2: orchestration/templates/big-head-skeleton.md

**Re-read**: YES (Step 1 of Big Head workflow)

**Acceptance Criterion 1**: "Each affected template has explicit instructions for handling missing/empty inputs"

- **Line 57-66**: Step 1 now contains explicit guard for missing report files
- **Condition**: "If any report file is missing"
- **Response**: Write failure artifact, return FAIL, do NOT proceed
- **Clarity**: "Do NOT proceed to read reports or perform consolidation"

**Acceptance Criterion 2**: "Failure artifacts are written to expected output paths"

- **Failure artifact path**: `{SESSION_DIR}/review-reports/review-consolidated-{TIMESTAMP}-FAILED.md` ✓
- **Failure artifact content**: Includes status, missing reports list, recovery guidance
- **Path is explicit** and follows session-specific naming convention

**Acceptance Criterion 3**: "Infrastructure failures are distinguished from substance failures"

- **Step 1 guard**: Labeled "INFRASTRUCTURE FAILURE" (missing report files from Nitpickers)
- **Recovery guidance**: "Verify that all 4 Nitpickers have completed and written their reports"
- **Semantics**: Implies temporary issue (wait for Nitpickers), not permanent quality issue

---

### File 3: orchestration/templates/checkpoints.md

**Re-read**: YES (Check 2 section)

**Acceptance Criterion 1**: "Each affected template has explicit instructions for handling missing/empty inputs"

- **Line 332-337**: Check 2 now contains explicit GUARD for bd show failures
- **Condition**: "If `bd show {TASK_ID}` fails"
- **Response**: Record failure, write note in report, proceed with fallback data
- **Clarity**: Specifies what to do (fallback to summary doc) and how to mark it

**Acceptance Criterion 2**: "Failure artifacts are written to expected output paths"

- **Note in review report**: Required output documented as review-report content
- **Marker text**: "[Note: Criteria from summary doc, not from `bd show`]"
- **No separate failure artifact**: Graceful degradation (not a hard failure)
- **Clear documentation** in the review report itself

**Acceptance Criterion 3**: "Infrastructure failures are distinguished from substance failures"

- **Check 2 guard**: Labeled "INFRASTRUCTURE FAILURE" (bd command error, not task quality)
- **Recovery**: "use the acceptance criteria listed in the agent's summary doc instead"
- **Non-blocking**: Review continues (temporary unavailability of bd)

---

## 5. Build/Test Validation

**Changes made**: 5 locations across 3 files updated with explicit guards
- pantry.md: 4 guards (3 refined conditions + 1 new Step 3 guard)
- big-head-skeleton.md: 1 guard (Step 1 report verification)
- checkpoints.md: 1 guard (Check 2 bd show)

**Validation approach**:

1. **Syntax Validation**: All markdown is valid. Guards follow consistent formatting:
   ```
   **GUARD: [Name] ([TYPE])**
   [Condition]
   - **If [condition]**: [action with artifact path and template]
   ```

2. **Completeness Check**:
   - All 5 locations from task context have been addressed ✓
   - No locations outside the specified ranges were modified ✓
   - No new files created (stayed within scope) ✓

3. **Convention Consistency**:
   - All 5 guards include explicit failure artifact paths ✓
   - All failures are categorized as INFRASTRUCTURE or SUBSTANCE ✓
   - All guards specify recovery guidance ✓
   - All guards include "Do NOT proceed" statements (except checkpoints Check 2, which explicitly allows graceful degradation) ✓

4. **Read-through verification**:
   - Step 2 Conditions 1-3: Properly labeled, artifact paths specified, recovery guidance clear
   - Step 3 guard: Positioned before brief composition, prevents empty file lists from reaching reviewers
   - Big Head Step 1: Prevents reading missing files, writes explicit failure artifact
   - Checkpoints Check 2: Enables graceful degradation with clear marking in report

**No test suite exists** for template orchestration (these are documentation/instruction templates, not runnable code). Validation is purely through manual re-reading and consistency checking.

---

## 6. Acceptance Criteria Checklist

| Criterion | Status | Evidence |
|-----------|--------|----------|
| Each affected template has explicit instructions for handling missing/empty inputs | PASS | pantry.md L32-76 (3 refined conditions) + L216-227 (new guard); big-head-skeleton.md L57-66; checkpoints.md L332-337 |
| Failure artifacts are written to expected output paths so downstream consumers are not left guessing | PASS | All 5 locations specify explicit failure artifact paths: task-{SUFFIX}-FAILED.md (Pantry), review-FAILED.md (Pantry Step 3), review-consolidated-{TS}-FAILED.md (Big Head), review-report content (Checkpoints) |
| Infrastructure failures (tool unavailability) are distinguished from substance failures (agent quality) | PASS | All 5 locations labeled as either INFRASTRUCTURE FAILURE or SUBSTANCE FAILURE with appropriate recovery guidance and non-blocking/blocking semantics |

---

## Implementation Notes

**Scope adherence**:
- Only modified files and line ranges specified in task context
- No adjacent issues were fixed (as instructed)
- No CHANGELOG, README, or CLAUDE.md modifications

**Consistency achieved**:
- All guards use recognizable **GUARD:** prefix
- All guards label failure type (INFRASTRUCTURE / SUBSTANCE)
- All guards specify artifact path and template
- All guards provide recovery guidance
- Pattern is replicable for future guards

**Downstream impact**:
- Pantry Step 2: Prevents corrupted task metadata from reaching agents
- Pantry Step 3: Prevents empty review scope from creating pointless reviews
- Big Head Step 1: Prevents reading missing Nitpicker reports
- Checkpoints Check 2: Gracefully handles bd unavailability in correctness reviews

**Rationale for checkpoints Check 2 design**:
Unlike other guards (which hard-fail), checkpoints Check 2 gracefully degrades using criteria from the summary doc. This design choice reflects that bd unavailability is a temporary infrastructure issue, not a blocker - reviewers should still be able to verify acceptance criteria using available data.

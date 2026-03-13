# Big Head Consolidation Brief

## Report Paths

All 4 Nitpicker reports to consolidate:

1. `.beads/agent-summaries/_session-54996f/review-reports/clarity-review-20260219-120000.md`
2. `.beads/agent-summaries/_session-54996f/review-reports/edge-cases-review-20260219-120000.md`
3. `.beads/agent-summaries/_session-54996f/review-reports/correctness-review-20260219-120000.md`
4. `.beads/agent-summaries/_session-54996f/review-reports/excellence-review-20260219-120000.md`

**Consolidated output path**: `.beads/agent-summaries/_session-54996f/review-reports/review-consolidated-20260219-120000.md`

## Step 0: Verify All Reports Exist (MANDATORY GATE)

Before reading any reports, verify all 4 expected files exist:

```bash
ls .beads/agent-summaries/_session-54996f/review-reports/clarity-review-*.md \
   .beads/agent-summaries/_session-54996f/review-reports/edge-cases-review-*.md \
   .beads/agent-summaries/_session-54996f/review-reports/correctness-review-*.md \
   .beads/agent-summaries/_session-54996f/review-reports/excellence-review-*.md
```

**All 4 files MUST exist.** If any file is missing:
1. Identify which reviewer failed to produce output
2. Check if the reviewer is still running, errored, or wrote to the wrong path
3. Do NOT proceed with consolidation until all 4 reports are present

### Step 0a: Remediation Path for Missing Reports (TIMEOUT + ERROR RETURN)

> **Authoritative source**: This section is the authoritative protocol for missing-report handling. The big-head-skeleton.md step 1 defers to this brief. If any apparent conflict exists between the skeleton and this brief, follow this brief.

If any report file is missing after the initial check, do NOT wait indefinitely. Instead:

**Timeout specification:** Wait a maximum of 30 seconds for all 4 reports to appear.
- Check once at T=0
- If all 4 reports exist, proceed to Step 1
- If any reports are missing, enter the polling loop below

**Polling loop (if files missing):**
```bash
# IMPORTANT: This entire block must execute in a single Bash invocation.
# Shell state (variables) does not persist across separate Bash tool calls.

# Poll up to 30 seconds total for missing reports
TIMEOUT=30
ELAPSED=0
POLL_INTERVAL=2
TIMED_OUT=1

while [ $ELAPSED -lt $TIMEOUT ]; do
  # Check each report type individually with [ -f ] to avoid wc -l count fragility.
  # head -1 ensures re-runs with multiple matching files don't break the check.
  FOUND_CLARITY=$(ls .beads/agent-summaries/_session-54996f/review-reports/clarity-review-*.md 2>/dev/null | head -1)
  FOUND_EDGE=$(ls .beads/agent-summaries/_session-54996f/review-reports/edge-cases-review-*.md 2>/dev/null | head -1)
  FOUND_CORRECTNESS=$(ls .beads/agent-summaries/_session-54996f/review-reports/correctness-review-*.md 2>/dev/null | head -1)
  FOUND_EXCELLENCE=$(ls .beads/agent-summaries/_session-54996f/review-reports/excellence-review-*.md 2>/dev/null | head -1)

  if [ -f "$FOUND_CLARITY" ] && [ -f "$FOUND_EDGE" ] && [ -f "$FOUND_CORRECTNESS" ] && [ -f "$FOUND_EXCELLENCE" ]; then
    # All 4 reports now present, proceed
    TIMED_OUT=0
    break
  fi
  sleep $POLL_INTERVAL
  ELAPSED=$((ELAPSED + POLL_INTERVAL))
done

if [ $TIMED_OUT -eq 1 ]; then
  # Timeout reached -- fall through to the error return below
  echo "TIMEOUT: Not all 4 reports arrived within ${TIMEOUT}s"
fi
```

**Error return (if timeout exceeded):**

If timeout is reached and any reports are still missing, IMMEDIATELY return an error to the Queen:

```markdown
# Big Head Consolidation - BLOCKED: Missing Nitpicker Reports

**Status**: FAILED (timeout after 30 seconds)
**Timestamp**: <current ISO 8601 timestamp>

## Missing Reports

The following expected Nitpicker report files were not found:
- Clarity review report (clarity-review-*.md) -- MISSING
- Edge cases review report (edge-cases-review-*.md) -- MISSING [or: FOUND at <path>]
- Correctness review report (correctness-review-*.md) -- MISSING [or: FOUND at <path>]
- Excellence review report (excellence-review-*.md) -- MISSING [or: FOUND at <path>]

## Remediation

Big Head cannot proceed with consolidation without all 4 reports present. The prerequisite gate (Step 0) FAILED.

**Action required from Queen:**
1. Check review agent logs for errors or crashes
2. Verify all 4 Nitpicker team members completed their reviews
3. Confirm reports were written to: .beads/agent-summaries/_session-54996f/review-reports/
4. Once all 4 reports are confirmed present, re-spawn Big Head consolidation

**Re-spawn instruction:**
~~~
Spawn Big Head again with all 4 report paths provided in the consolidation prompt.
~~~

**Do not proceed** with partial or missing review data.
```

Once the error is returned:
- Return the error message and STOP (do not continue to Steps 1-4)
- The Queen receives this error and must decide: retry with fresh Nitpicker spawn, or abort session

## Deduplication Protocol

### Step 1: Read All Reports

Read all 4 reports listed above.

### Step 2: Merge and Deduplicate

1. **Collect all findings** across all 4 reports into a single list
2. **Identify duplicates** -- findings reported by multiple reviewers about the same issue
3. **Merge cross-referenced items** -- where one reviewer flagged something for another's domain
4. **Group by root cause** -- apply the root-cause grouping principle across ALL review types
5. **Document merge rationale** -- for EVERY merge (two or more findings combined into one root cause), state:
   - WHY these findings share a root cause (not just that they do)
   - What the common code path, pattern, or design flaw is
   - If merged findings span unrelated files or functions, provide extra justification

Root-cause grouping format:

```markdown
## Root-Cause Grouping (Big Head Consolidation)

For each group of related findings across all 4 reviews:
- **Root cause**: <what's systematically wrong>
- **Affected surfaces**:
  - file1:L10 -- <specific instance> (from clarity review)
  - file2:L25 -- <specific instance> (from edge-cases review)
  - file3:L100 -- <specific instance> (from correctness review)
- **Combined priority**: <highest priority from any contributing finding>
- **Fix**: <one fix that covers all surfaces>
- **Merge rationale**: <why these specific findings share this root cause -- must reference shared code path, pattern, or design flaw>
- **Acceptance criteria**: <how to verify across all surfaces>
```

### Step 3: Write Consolidated Summary

Write the consolidated summary to `.beads/agent-summaries/_session-54996f/review-reports/review-consolidated-20260219-120000.md` using the format below:

```markdown
# Consolidated Review Summary

**Scope**: orchestration/templates/reviews.md, orchestration/templates/big-head-skeleton.md, orchestration/templates/pantry.md, orchestration/RULES.md
**Reviews completed**: Clarity, Edge Cases, Correctness, Excellence
**Reports verified**: clarity-review.md, edge-cases-review.md, correctness-review.md, excellence-review.md
**Total raw findings**: <N across all reviews>
**Root causes identified**: <N after dedup>
**Beads filed**: <N>

## Read Confirmation

**All 4 reports read and processed by Big Head consolidation:**

| Report Type | File | Status | Finding Count |
|-------------|------|--------|----------------|
| Clarity | clarity-review-20260219-120000.md | Read | <N> findings |
| Edge Cases | edge-cases-review-20260219-120000.md | Read | <N> findings |
| Correctness | correctness-review-20260219-120000.md | Read | <N> findings |
| Excellence | excellence-review-20260219-120000.md | Read | <N> findings |

**Total findings from all reports**: <N>

## Root Causes Filed

| Bead ID | Priority | Title | Contributing Reviews | Surfaces |
|---------|----------|-------|---------------------|----------|
| <id> | P<N> | <title> | clarity, edge-cases | <N> files |
| ... | ... | ... | ... | ... |

## Deduplication Log

Findings merged:
- <Finding X from clarity> + <Finding Y from edge-cases> -> Root Cause A
- ...

## Priority Breakdown
- P1 (blocking): <N> beads
- P2 (important): <N> beads
- P3 (polish): <N> beads

## Verdict
<PASS / PASS WITH ISSUES / NEEDS WORK>
<overall quality assessment>
```

### Step 4: Checkpoint Gate -- Await Pest Control Validation Before Filing Beads

**Do NOT file any beads yet.** After writing the consolidated summary (Step 3), notify Pest Control and wait for its verdict before calling `bd create`.

**Notification to Pest Control (SendMessage):**
```
SendMessage(
  to="pest-control",
  message="Consolidated report ready. Path: .beads/agent-summaries/_session-54996f/review-reports/review-consolidated-20260219-120000.md. Please run DMVDC and CCB checkpoints and reply with PASS or FAIL + specifics."
)
```

**Wait for Pest Control reply. Then act on verdict:**

- **PASS**: File ONE bead per root cause. See bead filing instructions below.
- **FAIL**: Big Head MUST escalate to the Queen with specifics. File beads ONLY for findings that passed. Do NOT file beads for flagged findings. Use this escalation format:

```
Big Head checkpoint escalation to Queen:
- Pest Control verdict: FAIL
- Findings that failed validation: <list with reasons per finding>
- Findings that passed: <list>
- Beads filed for validated findings: <ids or "none">
- Action required: User decides whether to drop, adjust, or re-review failed findings.
```

## Bead Filing Instructions

**After Pest Control PASS only.** File ONE bead per root cause (not per finding, not per review).

**Important**: Beads filed during session review are standalone. Do NOT assign them to a specific epic via `bd dep add --type parent-child`. They represent session-wide findings, not epic-specific work.

```bash
bd create --type=bug --priority=<combined-priority> --title="<root cause title>"
# Then update with full description including all affected surfaces
bd label add <id> <primary-review-type>
```

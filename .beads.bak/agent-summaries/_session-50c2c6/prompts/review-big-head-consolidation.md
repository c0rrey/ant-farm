# Big Head Consolidation Brief

**Review Round**: 1
**Timestamp**: 20260219-120000
**Consolidated Output Path**: .beads/agent-summaries/_session-50c2c6/review-reports/review-consolidated-20260219-120000.md

## Report Paths (All 4 Must Exist Before Proceeding)

1. `.beads/agent-summaries/_session-50c2c6/review-reports/clarity-review-20260219-120000.md`
2. `.beads/agent-summaries/_session-50c2c6/review-reports/edge-cases-review-20260219-120000.md`
3. `.beads/agent-summaries/_session-50c2c6/review-reports/correctness-review-20260219-120000.md`
4. `.beads/agent-summaries/_session-50c2c6/review-reports/excellence-review-20260219-120000.md`

## Step 0: Verify All Reports Exist (MANDATORY GATE)

Before reading any reports, verify all 4 expected files exist:

```bash
ls .beads/agent-summaries/_session-50c2c6/review-reports/clarity-review-*.md \
   .beads/agent-summaries/_session-50c2c6/review-reports/edge-cases-review-*.md \
   .beads/agent-summaries/_session-50c2c6/review-reports/correctness-review-*.md \
   .beads/agent-summaries/_session-50c2c6/review-reports/excellence-review-*.md
```

**All 4 files MUST exist.** If any file is missing:
1. Identify which reviewer failed to produce output
2. Check if the reviewer is still running, errored, or wrote to the wrong path
3. Do NOT proceed with consolidation until all 4 reports are present

## Deduplication Protocol

### Step 1: Read All Reports
Read all 4 reports from the paths listed above.

### Step 2: Merge and Deduplicate
1. **Collect all findings** across all 4 reports into a single list
2. **Identify duplicates** -- findings reported by multiple reviewers about the same issue
3. **Merge cross-referenced items** -- where one reviewer flagged something for another's domain
4. **Group by root cause** -- apply the root-cause grouping principle across ALL review types
5. **Document merge rationale** -- for EVERY merge (two or more findings combined into one root cause), state:
   - WHY these findings share a root cause (not just that they do)
   - What the common code path, pattern, or design flaw is
   - If merged findings span unrelated files or functions, provide extra justification

Use this format for each root-cause group:

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

## Bead Filing Instructions

File ONE bead per root cause (not per finding, not per review).

**Important**: Beads filed during session review are standalone. Do NOT assign them to a specific epic via `bd dep add --type parent-child`. They represent session-wide findings, not epic-specific work.

```bash
bd create --type=bug --priority=<combined-priority> --title="<root cause title>"
# Then update with full description including all affected surfaces
bd label add <id> <primary-review-type>
```

## Consolidated Summary Format

Write the consolidated summary to `.beads/agent-summaries/_session-50c2c6/review-reports/review-consolidated-20260219-120000.md` using this format:

```markdown
# Consolidated Review Summary

**Scope**: <list of all files reviewed>
**Reviews completed**: Clarity, Edge Cases, Correctness, Excellence
**Reports verified**: clarity-review.md check, edge-cases-review.md check, correctness-review.md check, excellence-review.md check
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

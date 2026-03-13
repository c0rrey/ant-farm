Consolidate the 2 Nitpicker reports into a unified summary.

Step 0: Read your consolidation brief from .beads/agent-summaries/_session-50c2c6/prompts/review-big-head-consolidation-r2.md
(Contains: both report paths, dedup protocol, bead filing instructions, output path.)

Your workflow:
1. Verify both report files exist (FAIL immediately if either missing)
2. Read both reports
3. Collect all findings into a single list
4. Deduplicate: merge findings about the same issue across reviewers
5. Group by root cause: one group per underlying problem, not per occurrence
6. For each merge, document WHY findings share a root cause
7. File ONE bead per root cause: `bd create --type=bug --priority=<P> --title="<title>"`
8. Write consolidated summary to .beads/agent-summaries/_session-50c2c6/review-reports/review-consolidated-20260220-120000.md

Your output MUST include (see brief for full format):
- Root cause groups with all affected surfaces and merge rationale
- Deduplication log (which findings merged, why)
- Bead IDs filed, with priority breakdown
- Overall verdict

---

# Big Head Consolidation Brief (Round 2)

**Round**: 2 (fix verification only)
**Consolidated Output Path**: .beads/agent-summaries/_session-50c2c6/review-reports/review-consolidated-20260220-120000.md

## Report Paths

This is a Round 2 review with 2 reviewers (not 4). Expect exactly these 2 reports:

1. **Edge Cases**: .beads/agent-summaries/_session-50c2c6/review-reports/edge-cases-review-20260220-120000.md
2. **Correctness**: .beads/agent-summaries/_session-50c2c6/review-reports/correctness-review-20260220-120000.md

## Step 0: Verify All Reports Exist (MANDATORY GATE)

Before reading any reports, verify both expected files exist:

```bash
ls .beads/agent-summaries/_session-50c2c6/review-reports/edge-cases-review-20260220-120000.md \
   .beads/agent-summaries/_session-50c2c6/review-reports/correctness-review-20260220-120000.md
```

**Both files MUST exist.** If either file is missing:
1. Identify which reviewer failed to produce output
2. Check if the reviewer is still running, errored, or wrote to the wrong path
3. Do NOT proceed with consolidation until both reports are present

## Deduplication Protocol

1. **Collect all findings** across both reports into a single list
2. **Identify duplicates** -- findings reported by both reviewers about the same issue
3. **Merge cross-referenced items** -- where one reviewer flagged something for the other's domain
4. **Group by root cause** -- apply the root-cause grouping principle across both review types
5. **Document merge rationale** -- for EVERY merge (two or more findings combined into one root cause), state:
   - WHY these findings share a root cause (not just that they do)
   - What the common code path, pattern, or design flaw is
   - If merged findings span unrelated files or functions, provide extra justification

### Root-Cause Grouping Format

For each group of related findings across both reviews:

```markdown
## Root-Cause Grouping (Big Head Consolidation)

### Root Cause <N>: <root cause title>
- **Root cause**: <what's systematically wrong>
- **Affected surfaces**:
  - file1:L10 -- <specific instance> (from edge-cases review)
  - file2:L25 -- <specific instance> (from correctness review)
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

Write the consolidated summary to the Consolidated Output Path above using this format:

```markdown
# Consolidated Review Summary (Round 2)

**Scope**: orchestration/RULES.md, orchestration/templates/checkpoints.md, orchestration/templates/queen-state.md, orchestration/templates/reviews.md
**Commit Range**: 002ee87..d9201c9 (3 fix commits)
**Reviews completed**: Edge Cases, Correctness (Round 2 -- fix verification)
**Reports verified**: edge-cases-review-20260220-120000.md, correctness-review-20260220-120000.md
**Total raw findings**: <N across both reviews>
**Root causes identified**: <N after dedup>
**Beads filed**: <N>

## Read Confirmation

**Both reports read and processed by Big Head consolidation:**

| Report Type | File | Status | Finding Count |
|-------------|------|--------|----------------|
| Edge Cases | edge-cases-review-20260220-120000.md | Read | <N> findings |
| Correctness | correctness-review-20260220-120000.md | Read | <N> findings |

**Total findings from all reports**: <N>

## Root Causes Filed

| Bead ID | Priority | Title | Contributing Reviews | Surfaces |
|---------|----------|-------|---------------------|----------|
| <id> | P<N> | <title> | correctness, edge-cases | <N> files |
| ... | ... | ... | ... | ... |

## Deduplication Log

Findings merged:
- <Finding X from correctness> + <Finding Y from edge-cases> -> Root Cause A
- ...

## Priority Breakdown
- P1 (blocking): <N> beads
- P2 (important): <N> beads
- P3 (polish): <N> beads

## Verdict
<PASS / PASS WITH ISSUES / NEEDS WORK>
<overall quality assessment>
```

# Report: Correctness Redux Review

**Scope**: orchestration/RULES.md, orchestration/templates/pantry.md, orchestration/templates/checkpoints.md, orchestration/templates/big-head-skeleton.md, orchestration/templates/dirt-pusher-skeleton.md
**Reviewer**: Correctness Redux Review (code-reviewer)

## Findings Catalog

### Finding 1: big-head-skeleton.md CONSOLIDATED_OUTPUT_PATH placeholder missing leading dot

- **File(s)**: `/Users/correy/projects/ant-farm/orchestration/templates/big-head-skeleton.md:14`
- **Severity**: P2
- **Category**: correctness
- **Description**: The `{CONSOLIDATED_OUTPUT_PATH}` placeholder definition reads `beads/agent-summaries/{epic-id}/review-reports/review-consolidated-<timestamp>.md` -- it is missing the leading dot (`.beads/...`). Every other reference to this path across all orchestration files uses `.beads/agent-summaries/...` (with a leading dot). A Queen filling in this placeholder would produce a path that does not match the canonical `.beads/` directory structure, causing the consolidated report to be written to a non-existent `beads/` directory at the repo root instead of the standard `.beads/` directory.
- **Acceptance criteria violated**: ant-farm-obd asked for "explicit Queen-facing instructions showing the TeamCreate -> SendMessage workflow." The wiring instructions were added, but the placeholder definition itself has a path typo.
- **Suggested fix**: Change line 14 from `` `beads/agent-summaries/{epic-id}/review-reports/review-consolidated-<timestamp>.md` `` to `` `.beads/agent-summaries/{epic-id}/review-reports/review-consolidated-<timestamp>.md` ``
- **Cross-reference**: This is in the Queen-facing instruction block, not the agent-facing template (which uses `{CONSOLIDATED_OUTPUT_PATH}` correctly). The error propagates at fill-time.

### Finding 2: big-head-skeleton.md uses old-style `{epic-id}` and `<timestamp>` instead of standardized `{EPIC_ID}` and `{timestamp}`

- **File(s)**: `/Users/correy/projects/ant-farm/orchestration/templates/big-head-skeleton.md:14`
- **Severity**: P2
- **Category**: correctness
- **Description**: ant-farm-ss6 standardized all task ID terminology across orchestration templates. The term definitions block was added to pantry.md, checkpoints.md, and dirt-pusher-skeleton.md -- but big-head-skeleton.md line 14 still uses `{epic-id}` (lowercase with hyphen) and `<timestamp>` (angle brackets) instead of the canonical `{EPIC_ID}` (uppercase) and `{timestamp}` (curly braces). This directly contradicts the standardization goal of ant-farm-ss6.
- **Acceptance criteria violated**: ant-farm-ss6 required "Standardize to one term across all orchestration files." big-head-skeleton.md was not fully updated.
- **Suggested fix**: (1) Add the canonical term definitions block to big-head-skeleton.md. (2) Change `{epic-id}` to `{EPIC_ID}` and `<timestamp>` to `{timestamp}` on line 14.
- **Cross-reference**: Relevant to the edge-cases and clarity reviewers -- ant-farm-ss6 coverage gap.

### Finding 3: RULES.md Queen Prohibitions still says "data files" without the "project" qualifier

- **File(s)**: `/Users/correy/projects/ant-farm/orchestration/RULES.md:6`
- **Severity**: P2
- **Category**: correctness
- **Description**: ant-farm-6jv fixed the Information Diet section (lines 80-85) to disambiguate "data files" by adding "project data files" and an explanatory paragraph. However, the Queen Prohibitions section at line 6 still reads "NEVER read source code, tests, data files, or config files" -- using the unqualified "data files" that was the original source of ambiguity. A fresh Queen reading the Prohibitions section first (as instructed by the heading "read FIRST") would encounter the same ambiguity that ant-farm-6jv was meant to fix, before reaching the clarification 74 lines later.
- **Acceptance criteria violated**: ant-farm-6jv required "Clarify: the prohibition is on project data files, not orchestration artifacts like data files and verdict tables." The Information Diet section was fixed, but the Prohibitions section was not.
- **Suggested fix**: Change line 6 from `- **NEVER** read source code, tests, data files, or config files -- agents do this` to `- **NEVER** read source code, tests, project data files, or config files -- agents do this`

### Finding 4: RULES.md Step 2 uses `{EPIC_ID}` as a literal shell variable in a mkdir command

- **File(s)**: `/Users/correy/projects/ant-farm/orchestration/RULES.md:29`
- **Severity**: P3
- **Category**: correctness
- **Description**: Step 2 says to run `mkdir -p .beads/agent-summaries/{EPIC_ID}/verification/pc/` where `{EPIC_ID}` is a placeholder the Queen must mentally substitute. This is consistent with how `{EPIC_ID}` is used elsewhere as a placeholder (e.g., checkpoints.md). However, contrast this with the Session Directory section (lines 113-115) which uses actual shell variables (`${SESSION_ID}`, `${SESSION_DIR}`). The mixed use of `{UPPERCASE}` as both shell-variable syntax and documentation-placeholder syntax within the same file could cause a Queen to try to use `${EPIC_ID}` as an actual shell variable (which was never set). The Epic Artifact Directories section (line 135) also uses `{EPIC_ID}` as placeholder, so at least the file is internally consistent on this point, but the dual convention within the same file is a minor source of confusion.
- **Suggested fix**: No code change required -- this is a documentation convention issue. The existing parenthetical "(one command per epic; use `_standalone` for tasks with no epic)" sufficiently clarifies that the Queen must substitute manually. Flagging for awareness only.

### Finding 5: checkpoints.md Checkpoint A section header renamed but internal cross-reference text not updated

- **File(s)**: `/Users/correy/projects/ant-farm/orchestration/templates/checkpoints.md:67`
- **Severity**: P3
- **Category**: correctness
- **Description**: The section header was renamed from "Checkpoint A" to "Colony Cartography Office (CCO)" (visible in the committed file at line 54). The prompt template text at line 67 references `See "Pest Control Overview" section above` -- this is correct. However, the old `pest-control-{TASK_SUFFIX}-checkpoint-a-{timestamp}.md` naming convention in the review brief (which is what brought me here as a reviewer) uses "checkpoint-a" in the filename while the committed checkpoints.md uses "cco" in filenames (line 100: `pc-{TASK_SUFFIX}-cco-{timestamp}.md`). This is not a bug in the files under review -- the naming is consistent within the committed files -- but it indicates the review brief itself was composed using outdated checkpoint names (A/B/C vs CCO/DMVDC/CCB). This is informational only.
- **Suggested fix**: No fix needed in the reviewed files. The review brief generator should use the current checkpoint naming convention.

### Finding 6: ant-farm-9oa acceptance criteria partially met -- task still IN_PROGRESS

- **File(s)**: `/Users/correy/projects/ant-farm/orchestration/templates/dirt-pusher-skeleton.md:15-16`
- **Severity**: P3
- **Category**: correctness
- **Description**: ant-farm-9oa required adding `{TASK_ID}` to the placeholder definitions in dirt-pusher-skeleton.md. This was done correctly -- `{TASK_ID}` and `{TASK_SUFFIX}` are now both defined in the Placeholders list (lines 15-16) and in the term definitions block (lines 8-11). However, `bd show ant-farm-9oa` shows the task is still `IN_PROGRESS` rather than `CLOSED`. The work appears complete in the committed code, so this is a process gap (task not closed after implementation), not a code correctness issue.
- **Suggested fix**: Close the task: `bd close ant-farm-9oa`

### Finding 7: ant-farm-tsw (P1 bug) -- fix is correct but prompts/ directory creation is redundant with Pantry

- **File(s)**: `/Users/correy/projects/ant-farm/orchestration/RULES.md:115`, `/Users/correy/projects/ant-farm/orchestration/templates/pantry.md:110`
- **Severity**: P3
- **Category**: correctness
- **Description**: ant-farm-tsw added `prompts` to the Step 0 brace expansion (`mkdir -p ${SESSION_DIR}/{task-metadata,previews,prompts}`). This correctly fixes the bug. However, pantry.md Section 2 Step 3 (line 110) still says "Create the prompts directory if needed: `{session-dir}/prompts/`" -- this is now redundant since Step 0 already creates it. The redundancy is harmless (`mkdir -p` is idempotent) but creates confusion about who owns directory creation.
- **Suggested fix**: Either remove the "Create the prompts directory if needed" line from pantry.md, or change it to a comment noting that Step 0 pre-creates it. Low priority since the behavior is correct either way.

## Preliminary Groupings

### Group A: Incomplete standardization of terminology (ant-farm-ss6 coverage gap)
- Finding 2 -- big-head-skeleton.md was not updated with standardized `{EPIC_ID}` terminology
- **Suggested combined fix**: Add term definitions block to big-head-skeleton.md and update `{epic-id}` -> `{EPIC_ID}`, `<timestamp>` -> `{timestamp}` in the placeholder definitions.

### Group B: Incomplete disambiguation of "data files" (ant-farm-6jv partial fix)
- Finding 3 -- Queen Prohibitions section not updated alongside Information Diet section
- **Suggested combined fix**: Add "project" qualifier to the Prohibitions section line 6, matching the Information Diet fix.

### Group C: big-head-skeleton.md path typo
- Finding 1 -- standalone (missing leading dot in `.beads/`)
- **Suggested combined fix**: Fix the path on line 14.

### Group D: Process/cleanup items
- Finding 4, Finding 5, Finding 6, Finding 7 -- standalone minor items
- No combined fix needed; each is independent.

## Summary Statistics
- Total findings: 7
- By severity: P1: 0, P2: 3, P3: 4
- Preliminary groups: 4

## Cross-Review Messages

### Sent
- None sent.

### Received
- From excellence-reviewer: "big-head-skeleton.md:14 missing leading dot in .beads/ path for CONSOLIDATED_OUTPUT_PATH placeholder" -- Action taken: Confirmed. Already cataloged as Finding 1 (P2). Independent corroboration strengthens confidence in the finding.

### Deferred Items
- None.

## Coverage Log

List every in-scope file with its review status. Files with no findings MUST still appear here -- omission is not acceptable.

| File | Status | Evidence |
|------|--------|----------|
| orchestration/RULES.md | Findings: #3, #4 | 206 lines examined. Verified all 10 tasks' acceptance criteria against the diffs touching this file. Checked Step 0, Step 1, Step 2, Step 3, Step 3b, Information Diet, Session Directory, Epic Artifact Directories sections for cross-file consistency. |
| orchestration/templates/pantry.md | Findings: #7 | 170 lines examined. Verified term definitions block added (ant-farm-ss6). Verified timestamp ownership change (ant-farm-af0). Verified cross-reference addition (ant-farm-yta). Checked Section 1 and Section 2 data file formats. |
| orchestration/templates/checkpoints.md | Findings: #5 | 469 lines examined. Verified term definitions block added (ant-farm-ss6). Verified commit range sourcing clarification (ant-farm-iih). Checked all 4 checkpoint sections (CCO, WWD, DMVDC, CCB) for consistent use of `{TASK_SUFFIX}`, `{TASK_ID}`, `{EPIC_ID}`. All artifact naming conventions verified consistent. |
| orchestration/templates/big-head-skeleton.md | Findings: #1, #2 | 71 lines examined. Verified TeamCreate + SendMessage wiring instructions added (ant-farm-obd). Checked placeholder list, agent-facing template, and example code blocks. |
| orchestration/templates/dirt-pusher-skeleton.md | Findings: #6 | 44 lines examined. Verified term definitions block added (ant-farm-ss6). Verified `{TASK_ID}` and `{TASK_SUFFIX}` added to placeholder list (ant-farm-9oa). Checked template section for consistent placeholder usage. |

## Overall Assessment
**Score**: 7/10
**Verdict**: PASS WITH ISSUES

Three P2 findings, all relating to incomplete propagation of fixes across files. The most impactful is Finding 1 (missing leading dot in `.beads/` path) which would cause Big Head's consolidated report to be written to the wrong directory. Findings 2 and 3 are consistency gaps where standardization changes were applied to most but not all relevant locations. No P1 blockers -- the core logic and data flow are correct, and the changes achieve their stated goals in the primary files they target.

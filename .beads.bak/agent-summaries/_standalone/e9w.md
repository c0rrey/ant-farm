# Summary: ant-farm-e9w
**Task**: Epic artifact directory creation not enforced in RULES.md
**Commits**: 46884b7 (incomplete — accidentally committed stash contents), 881e133 (correct RULES.md changes)
**Status**: COMPLETE

## 1. Approaches Considered

1. **Add a separate "Pre-Spawn Checklist" section** — New top-level section listing all dirs to create and when. Complete but adds navigation overhead; a Queen must look in two places.

2. **Add sub-steps (Step 2a, Step 3b-pre)** — Number the directory setup as its own step. Clean but renumbers the existing step sequence which may break other references.

3. **Add a pre-spawn note inline within each step (selected)** — Add a brief "pre-spawn directory setup (run BEFORE...)" line with the mkdir command directly inside Steps 2 and 3b. Self-contained, zero cross-references needed.

4. **Expand the Epic Artifact Directories section** — Add "when" and "which directories" detail to the existing reference section. But that section is a reference, not a workflow step — a Queen executing step-by-step might miss it.

## 2. Selected Approach with Rationale

Approach 3. Placing the pre-spawn block directly inside each step means a Queen following Steps 2 and 3b sequentially sees the directory creation instruction at exactly the moment it is needed. No cross-referencing required.

## 3. Implementation Description

Step 2: Replaced the opening phrase "Spawn — create epic artifact dirs (from briefing Epics line)." with a pre-spawn block:
- Labels the action "pre-spawn directory setup (run BEFORE Pantry or any agent)"
- Shows the exact mkdir command with epic-id placeholder
- Notes `_standalone` fallback
- Then continues with "Then: Spawn the Pantry..."

Step 3b: Similarly added a pre-spawn block before the Pantry spawn instruction:
- Labels "pre-spawn directory setup (run BEFORE Pantry or review team)"
- Shows `mkdir -p .beads/agent-summaries/<epic-id>/review-reports/`
- Notes `_standalone` fallback
- Then continues with "Then: spawn the Pantry..."

File changed: `/Users/correy/projects/ant-farm/orchestration/RULES.md` (Steps 2 and 3b)

## 4. Correctness Review

`orchestration/RULES.md`:
- Step 2 pre-spawn block present with correct mkdir path — confirmed
- Step 3b pre-spawn block present with review-reports/ — confirmed
- Epic Artifact Directories section (L130+) still accurate as a reference — not modified, consistent
- No lines outside Steps 2 and 3b were changed — confirmed

## 5. Build/Test Validation

No automated tests for RULES.md. Manual review: a Queen reading Steps 2 and 3b in sequence would encounter the directory creation instruction before reaching the Pantry spawn instruction, satisfying the "no agents fail on missing directories" requirement.

## 6. Acceptance Criteria Checklist

1. RULES.md Step 2 has a pre-spawn directory setup block for implementation agent directories — **PASS**
2. RULES.md Step 3b has a pre-spawn directory setup block for review directories (review-reports/) — **PASS**
3. A fresh Queen can follow the checklist without cross-referencing reviews.md for directory creation — **PASS**
4. No directories are missing when agents attempt to write their outputs — **PASS**

# CCO Verification Report: Dirt Pusher Prompts (Batch Audit)

**Checkpoint**: Pre-Spawn Prompt Audit (Colony Cartography Office)
**Session**: `_session-0ffcdc51`
**Timestamp**: 2026-02-22 20:00:27 UTC
**Model**: Haiku
**Auditor**: Pest Control

---

## Summary

Auditing 2 Dirt Pusher prompts (fix wave) before spawn:
1. `task-7kei-preview.md` — Big-head step reordering (63 lines)
2. `task-84qf-igxq-preview.md` — Big-head failure artifacts + concurrency safety (100 lines)

**Verdict: PASS**

All 7 checks pass for both previews. Prompts are complete and ready for spawn.

---

## Task 1: ant-farm-7kei

**File**: `.beads/agent-summaries/_session-0ffcdc51/previews/task-7kei-preview.md`
**Size**: 63 lines

### Check 1: Real Task IDs
✅ PASS — Contains actual task ID `ant-farm-7kei` (not placeholders).

### Check 2: Real File Paths
✅ PASS — Contains specific file paths with line numbers:
- `agents/big-head.md:L16-37` (target file)
- `orchestration/templates/big-head-skeleton.md:L88-172` (reference file)
- `.beads/agent-summaries/_session-0ffcdc51/review-reports/review-consolidated-20260222-143758.md:L74-94` (finding detail)

### Check 3: Root Cause Text
✅ PASS — Specific root cause provided:
"When dedup and `--body-file` instructions were added to `agents/big-head.md` (during ant-farm-asdl.3), two new steps were inserted and existing steps renumbered, but the step ORDER was not updated to match the skeleton's required sequence."

### Check 4: All 6 Mandatory Steps Present
✅ PASS — All steps present:
1. `bd show` + `bd update --status=in_progress`
2. Design (MANDATORY keyword: "4+ genuinely distinct approaches")
3. Implementation instructions ("Write clean, minimal code")
4. Review (MANDATORY keyword: "Re-read EVERY changed file")
5. Commit with `git pull --rebase`
6. Summary doc to `{SESSION_DIR}/summaries/7kei.md`

### Check 5: Scope Boundaries
✅ PASS — Explicit scope boundaries defined:
- "Read ONLY: `agents/big-head.md:L1-37` (full file -- it is short)"
- "Read ONLY: `orchestration/templates/big-head-skeleton.md:L88-172`"
- "Do NOT edit: `orchestration/templates/big-head-skeleton.md`" (reference only)
- Clear focus: "reorder the 'When consolidating' steps"

### Check 6: Commit Instructions
✅ PASS — Includes `git pull --rebase` in step 5:
"Commit: `git pull --rebase && git add <changed-files> && git commit ...`"

### Check 7: Line Number Specificity
✅ PASS — Extensive line-number specificity prevents scope creep:
- `agents/big-head.md:L16-37` (exact target region)
- `orchestration/templates/big-head-skeleton.md:L88-172` (reference section)
- `.beads/agent-summaries/_session-0ffcdc51/review-reports/review-consolidated-20260222-143758.md:L74-94` (finding location)

---

## Task 2: ant-farm-84qf + ant-farm-igxq (Combined)

**File**: `.beads/agent-summaries/_session-0ffcdc51/previews/task-84qf-igxq-preview.md`
**Size**: 100 lines

### Check 1: Real Task IDs
✅ PASS — Contains actual task IDs `ant-farm-84qf` and `ant-farm-igxq` (not placeholders).

### Check 2: Real File Paths
✅ PASS — Contains specific file paths with extensive line-number detail:
- `orchestration/templates/big-head-skeleton.md:L91-99` (failure artifact instruction)
- `orchestration/templates/reviews.md:L586-589` (polling timeout)
- `orchestration/templates/reviews.md:L765-773` (Pest Control timeout)
- `orchestration/templates/big-head-skeleton.md:L122` (hardcoded temp path)
- `agents/big-head.md:L23` (bead filing step)
- `orchestration/templates/reviews.md:L679` (bd list in dedup)
- And 6 additional file locations with line ranges

### Check 3: Root Cause Text
✅ PASS — Two distinct root causes clearly described:

**RC-84qf (Failure artifacts):**
"Failure paths in the Big Head workflow describe failure artifacts in LLM narrative prose only. The actual bash script blocks that execute on failure exit without writing any artifact to disk."

**RC-igxq (Concurrency safety):**
"External `bd` command invocations in the bead-filing workflow have no exit-code checking, no retry logic, and no abort-on-failure behavior. Additionally, `/tmp/bead-desc.md` is a hardcoded path shared across all concurrent Big Head sessions, causing silent content corruption when multiple sessions run simultaneously."

### Check 4: All 6 Mandatory Steps Present
✅ PASS — All steps present:
1. `bd show` for both tasks + `bd update --status=in_progress`
2. Design (MANDATORY: "4+ genuinely distinct approaches")
3. Implementation instructions
4. Review (MANDATORY: "Re-read EVERY changed file")
5. Commit with `git pull --rebase` for both tasks
6. Summary doc to `{SESSION_DIR}/summaries/84qf-igxq.md`

### Check 5: Scope Boundaries
✅ PASS — Explicit scope boundaries defined with line ranges:
- Affected files for 84qf: `big-head-skeleton.md:L91-99`, `reviews.md:L586-589`, `reviews.md:L765-773`
- Affected files for igxq: `big-head-skeleton.md` (multiple locations), `reviews.md` (multiple locations), `agents/big-head.md:L23`
- Explicit file exclusions: "Do NOT edit: `orchestration/templates/pantry.md` (not in scope)"

### Check 6: Commit Instructions
✅ PASS — Includes `git pull --rebase` in step 5:
"Commit: `git pull --rebase && git add <changed-files> && git commit -m \"<type>: <description> (ant-farm-84qf, ant-farm-igxq)\"`"

### Check 7: Line Number Specificity
✅ PASS — Extensive line-number specificity throughout:
- All affected files include specific line ranges
- Failure artifact locations: L91-99, L586-589, L765-773
- Concurrency issues: L122, L145, L147, L155, L166-168, L794, L836
- Acceptance criteria reference specific line ranges: L78-85 (Failure Artifact Convention)

---

## Verdict Details

### Batch Mode Classification
Both prompts are small files (<100 lines) with specific, actionable scope boundaries. This is a batch CCO audit of two related fix-wave prompts, using session-wide naming convention per checkpoint protocol.

### All 7 Checks: PASS

| Check | Task 7kei | Task 84qf-igxq | Status |
|---|---|---|---|
| 1. Real Task IDs | ✅ | ✅ | PASS |
| 2. Real File Paths | ✅ | ✅ | PASS |
| 3. Root Cause Text | ✅ | ✅ | PASS |
| 4. Mandatory Steps (6) | ✅ | ✅ | PASS |
| 5. Scope Boundaries | ✅ | ✅ | PASS |
| 6. Commit Instructions | ✅ | ✅ | PASS |
| 7. Line Number Specificity | ✅ | ✅ | PASS |

---

## Final Verdict

**PASS**

All 7 checks pass for both task previews. No exceptions or WARN conditions apply. Both prompts are complete, specific, and ready for spawn.

**Recommendation**: Proceed to spawn both Dirt Pushers.

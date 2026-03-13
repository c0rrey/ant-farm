# Pest Control -- CCO (Pre-Spawn Nitpickers Audit)

**Checkpoint**: CCO-review (Pre-Spawn Prompt Audit for Nitpickers)
**Session**: _session-405acc
**Audited previews**:
- `.beads/agent-summaries/_session-405acc/previews/review-clarity-preview.md`
- `.beads/agent-summaries/_session-405acc/previews/review-edge-cases-preview.md`
- `.beads/agent-summaries/_session-405acc/previews/review-correctness-preview.md`
- `.beads/agent-summaries/_session-405acc/previews/review-excellence-preview.md`
- `.beads/agent-summaries/_session-405acc/previews/review-big-head-preview.md`

---

## Check 1: File list matches git diff -- FAIL

**Commit range**: `bc84bd0..HEAD`

**Git diff --name-only output** (ground truth, 4 files):
1. `orchestration/templates/big-head-skeleton.md`
2. `orchestration/templates/checkpoints.md`
3. `orchestration/templates/pantry.md`
4. `orchestration/templates/reviews.md`

**Prompt file lists** (all 4 Nitpickers, 6 files):
1. `orchestration/templates/big-head-skeleton.md`
2. `orchestration/templates/checkpoints.md`
3. `orchestration/templates/dirt-pusher-skeleton.md`
4. `orchestration/templates/nitpicker-skeleton.md`
5. `orchestration/templates/pantry.md`
6. `orchestration/templates/reviews.md`

**Mismatch**:
- **Extra files in prompts** (not in git diff): `orchestration/templates/dirt-pusher-skeleton.md`, `orchestration/templates/nitpicker-skeleton.md`
- **Missing files from prompts**: none
- Verified with `git diff bc84bd0..HEAD -- orchestration/templates/dirt-pusher-skeleton.md orchestration/templates/nitpicker-skeleton.md` -- zero output, confirming no changes.

**Impact**: Reviewers will spend effort reviewing 2 files with zero changes. This wastes review capacity and may generate false findings about pre-existing issues unrelated to the session's work. Additionally, if reviewers report findings on unchanged files, Big Head will file beads for issues outside this session's scope.

## Check 2: Same file list across all 4 prompts -- PASS

All 4 Nitpicker prompts list the identical 6 files (same set, same order). Internally consistent.

## Check 3: Same commit range -- PASS

All 4 prompts reference commit range `bc84bd0..HEAD`. Consistent across all prompts.

## Check 4: Correct focus areas -- PASS

Each prompt has focus areas specific to its review type:
- **Clarity**: readability, documentation, consistency, naming, structure (5 areas, lines 44-48)
- **Edge Cases**: input validation, error handling, boundary conditions, file operations, concurrency, platform differences (6 areas, lines 44-50)
- **Correctness**: acceptance criteria, logic correctness, data integrity, regression risks, cross-file consistency, algorithm correctness (6 areas, lines 50-55). Also includes Task IDs (ant-farm-x4m, ant-farm-e9k, ant-farm-zeu) for acceptance criteria verification.
- **Excellence**: best practices, performance, security, maintainability, architecture, scalability, modern features (7 areas, lines 44-50)

Focus areas are distinct and domain-appropriate. No copy-paste duplication detected.

## Check 5: No bead filing instruction -- PASS

All 4 prompts contain explicit prohibition:
- Clarity: "Do NOT file beads (`bd create`) -- Big Head handles all bead filing." (line 21, repeated line 65)
- Edge Cases: "Do NOT file beads (`bd create`) -- Big Head handles all bead filing." (line 21, repeated line 64)
- Correctness: "Do NOT file beads (`bd create`) -- Big Head handles all bead filing." (line 21, repeated line 74)
- Excellence: "Do NOT file beads (`bd create`) -- Big Head handles all bead filing." (line 21, repeated line 67)

## Check 6: Report format reference -- PASS

Each prompt specifies the correct output path under `{SESSION_DIR}/review-reports/`:
- Clarity: `clarity-review-20260219-120000.md` (lines 4, 31, 63)
- Edge Cases: `edge-cases-review-20260219-120000.md` (lines 4, 31, 64)
- Correctness: `correctness-review-20260219-120000.md` (lines 4, 31, 72)
- Excellence: `excellence-review-20260219-120000.md` (lines 4, 31, 67)

Timestamp `20260219-120000` is consistent across all 4 prompts and the Big Head consolidation prompt.

## Check 7: Messaging guidelines -- PASS

All 4 prompts include DO/DO NOT messaging sections:
- Clarity: lines 69-79
- Edge Cases: lines 75-87
- Correctness: lines 89-97
- Excellence: lines 80-90

Each includes the three "DO message" scenarios and three "Do NOT message" scenarios.

## Big Head Prompt Assessment

The Big Head consolidation prompt:
- Correctly references all 4 report paths with matching timestamp
- Includes Step 0 mandatory gate for report existence verification
- Contains deduplication protocol with merge rationale requirements
- Specifies bead filing instructions (one bead per root cause, standalone, no epic assignment)
- Defines consolidated summary format with all required sections

No issues found with Big Head prompt.

---

## Verdict: FAIL

**Failing check**: Check 1 -- File list mismatch. The prompts include 2 files (`dirt-pusher-skeleton.md`, `nitpicker-skeleton.md`) that have zero changes in the commit range `bc84bd0..HEAD`. These files should be removed from the review scope before spawning.

**Passing checks**: 2, 3, 4, 5, 6, 7 (6 of 7 pass)

**Required remediation**: Remove `orchestration/templates/dirt-pusher-skeleton.md` and `orchestration/templates/nitpicker-skeleton.md` from all 4 Nitpicker prompts and re-run CCO. Alternatively, if there is a deliberate reason to include unchanged files (e.g., cross-file consistency review of related templates), document that rationale explicitly in the prompts.

# Consolidated Review Summary

**Scope**: orchestration/templates/big-head-skeleton.md, orchestration/templates/checkpoints.md, orchestration/templates/dirt-pusher-skeleton.md, orchestration/templates/nitpicker-skeleton.md, orchestration/templates/pantry.md, orchestration/templates/reviews.md
**Reviews completed**: Clarity, Edge Cases, Correctness, Excellence
**Reports verified**: clarity-review.md [x], edge-cases-review.md [x], correctness-review.md [x], excellence-review.md [x]
**Total raw findings**: 24 across all reviews
**Root causes identified**: 11 after deduplication
**Beads filed**: 11

## Read Confirmation

**All 4 reports read and processed by Big Head consolidation:**

| Report Type | File | Status | Finding Count |
|-------------|------|--------|---------------|
| Clarity | clarity-review-20260219-120000.md | Read | 6 findings |
| Edge Cases | edge-cases-review-20260219-120000.md | Read | 7 findings |
| Correctness | correctness-review-20260219-120000.md | Read | 4 findings |
| Excellence | excellence-review-20260219-120000.md | Read | 7 findings |

**Total findings from all reports**: 24

## Root-Cause Grouping (Big Head Consolidation)

### Root Cause 1: Polling loop in reviews.md Step 0a uses fragile wc -l line-counting with globs

- **Root cause**: The Step 0a polling loop chains 4 `ls` glob commands with `&&`, stores results in a misleadingly-named `MISSING_REPORTS` variable, and checks `wc -l -eq 4` to detect completion. This pattern has multiple defects: glob multi-match breaks the count, the variable name is inverted, no post-loop timeout detection exists, and shell state may not persist across agent Bash calls.
- **Affected surfaces**:
  - `/Users/correy/projects/ant-farm/orchestration/templates/reviews.md`:370-383 -- polling loop logic (from clarity, edge-cases, correctness, excellence reviews)
- **Combined priority**: P2 (highest across: clarity P3, edge-cases P2, correctness P2, excellence P2)
- **Fix**: Replace the `wc -l` counting approach with individual `[ -f path ]` checks per exact filename. Add post-loop timeout detection. Rename `MISSING_REPORTS` to `FOUND_REPORTS`. Add comment requiring single-invocation execution.
- **Merge rationale**: All 6 contributing findings (Clarity F2, Edge Cases F1, Edge Cases F2, Correctness F1, Excellence F1, Excellence F6) target the same bash code block at reviews.md:370-383. They describe different facets of the same flawed polling pattern: variable naming (Clarity F2), glob expansion (Edge Cases F1, Correctness F1, Excellence F1), missing post-loop check (Edge Cases F2), and shell persistence (Excellence F6). A single rewrite of this code block resolves all findings.
- **Acceptance criteria**: Polling loop uses exact file paths with `[ -f ]` checks. Post-loop code distinguishes timeout from success. Variable names match their semantics. Loop works correctly in a single Bash invocation.
- **Bead**: ant-farm-tek

### Root Cause 2: Nested markdown code fences in reviews.md error return template break rendering

- **Root cause**: The error return template at reviews.md:390-420 uses triple-backtick fences for both the outer code block and an inner "Re-spawn instruction" block. Standard markdown closes the outer fence at the inner backticks, causing lines 417-420 to render as regular text.
- **Affected surfaces**:
  - `/Users/correy/projects/ant-farm/orchestration/templates/reviews.md`:414-420 -- inner code fence prematurely closes outer fence (from clarity, edge-cases, excellence reviews)
- **Combined priority**: P2 (highest across: clarity P3, edge-cases P2, excellence P3)
- **Fix**: Use quadruple backticks for the outer fence, or indent the inner block with 4+ spaces, or use tildes for the inner fence.
- **Merge rationale**: Clarity F3, Edge Cases F7, and Excellence F2 all identify the same nested-fence collision at the same lines in reviews.md. They differ only in severity assessment (P2 vs P3) based on how literally an agent would parse the template. Same code, same bug, same fix.
- **Acceptance criteria**: The error return template renders correctly in standard markdown with no premature fence closure.
- **Bead**: ant-farm-tz0q

### Root Cause 3: Pantry failure artifact path collision across conditions for same task

- **Root cause**: All three Pantry failure conditions write to the same path (`task-{TASK_SUFFIX}-FAILED.md`), making the failure type distinguishable only by reading the artifact content, not the filename. Currently safe due to sequential waterfall checks, but fragile against future refactoring.
- **Affected surfaces**:
  - `/Users/correy/projects/ant-farm/orchestration/templates/pantry.md`:33 -- Condition 1 artifact path (from clarity, edge-cases, excellence reviews)
  - `/Users/correy/projects/ant-farm/orchestration/templates/pantry.md`:47 -- Condition 2 artifact path
  - `/Users/correy/projects/ant-farm/orchestration/templates/pantry.md`:58 -- Condition 3 artifact path
- **Combined priority**: P3 (all three reviewers agreed on P3)
- **Fix**: Add a comment documenting the sequential-check invariant. Optionally add condition type to filename.
- **Merge rationale**: Clarity F5, Edge Cases F3, and Excellence F3 all identify the same shared-path pattern across the same three conditions in pantry.md. The root cause is the single output path serving all failure types. All three findings describe identical concern (overwrite potential) at the same code locations.
- **Acceptance criteria**: A comment documents that conditions are evaluated sequentially and only the first triggers.
- **Bead**: ant-farm-sycy

### Root Cause 4: Pantry fail-fast says "Halt" but behavior is skip-to-next-task

- **Root cause**: The preamble at pantry.md:30 says "Halt and report" but the actual Condition 1-3 behavior is per-task skipping with continued processing. The word "Halt" implies stopping all work, which contradicts the skip-to-next-task semantics.
- **Affected surfaces**:
  - `/Users/correy/projects/ant-farm/orchestration/templates/pantry.md`:30-31 -- "Halt and report" preamble (from clarity, correctness reviews)
- **Combined priority**: P3 (both reviewers assigned P3)
- **Fix**: Change "Halt and report" to "Check and skip on failure" or "Validate before proceeding."
- **Merge rationale**: Clarity F6 and Correctness F3 both flag the same word ("Halt") on the same line (pantry.md:30-31) as misleading relative to the same actual behavior (skip-to-next-task). Identical root cause, identical fix.
- **Acceptance criteria**: The preamble wording accurately describes per-task skipping behavior.
- **Bead**: ant-farm-xdw3

### Root Cause 5: Big Head skeleton and reviews.md have divergent failure handling for missing reports

- **Root cause**: Big Head receives contradictory instructions from two templates: big-head-skeleton.md says "FAIL immediately" for missing reports, while reviews.md Step 0a (which the Pantry uses to compose the consolidation brief) specifies a 30-second polling loop before failing. Additionally, failure artifact paths differ between the two sources.
- **Affected surfaces**:
  - `/Users/correy/projects/ant-farm/orchestration/templates/big-head-skeleton.md`:57-66 -- immediate FAIL instruction (from correctness review)
  - `/Users/correy/projects/ant-farm/orchestration/templates/reviews.md`:354-424 -- polling loop with timeout (from correctness review)
- **Combined priority**: P2 (correctness reviewer assigned P2)
- **Fix**: Designate one template as authoritative. Update skeleton to reference the brief for remediation details, or add the polling protocol to the skeleton. Harmonize failure artifact paths.
- **Merge rationale**: Standalone finding from Correctness F2 -- no duplicates across reviews, but it references the same polling loop code as Root Cause 1. It is kept separate because the root cause here is a cross-template design contradiction, not a code defect in the loop itself.
- **Acceptance criteria**: Big Head receives a single consistent set of instructions for missing-report handling with one authoritative failure artifact path.
- **Bead**: ant-farm-crky

### Root Cause 6: Skeleton format spec hints do not match Pantry actual output sections

- **Root cause**: The format hints added to dirt-pusher-skeleton.md and nitpicker-skeleton.md by ant-farm-x4m are simplified summaries that omit sections the Pantry actually writes. Big Head skeleton has no format hint at all, inconsistent with the other two skeletons.
- **Affected surfaces**:
  - `/Users/correy/projects/ant-farm/orchestration/templates/dirt-pusher-skeleton.md`:30 -- omits "Summary Doc Sections" (from clarity review)
  - `/Users/correy/projects/ant-farm/orchestration/templates/nitpicker-skeleton.md`:19 -- sections don't match Pantry review brief (from clarity review)
  - `/Users/correy/projects/ant-farm/orchestration/templates/big-head-skeleton.md`:53 -- no format hint at all (from excellence review)
- **Combined priority**: P3 (both reviewers assigned P3)
- **Fix**: Update skeleton hints to match Pantry output, or add "(approximate)" qualifier. Add format hint to big-head-skeleton.md.
- **Merge rationale**: Clarity F4 and Excellence F7 both identify format spec inconsistencies between skeleton templates and the Pantry. Clarity F4 covers dirt-pusher and nitpicker skeletons having inaccurate hints; Excellence F7 covers big-head skeleton missing a hint entirely. Same pattern (skeleton-Pantry format mismatch), same design flaw (format specs added without verifying against actual Pantry output), one combined fix.
- **Acceptance criteria**: All three skeleton templates have format hints that accurately reflect the Pantry's actual output sections.
- **Bead**: ant-farm-0xqf

### Root Cause 7: Failure taxonomy (INFRASTRUCTURE vs SUBSTANCE) not defined in a shared location

- **Root cause**: The INFRASTRUCTURE FAILURE and SUBSTANCE FAILURE labels appear across multiple templates (pantry.md, big-head-skeleton.md, checkpoints.md, reviews.md) but are never formally defined in a single canonical location.
- **Affected surfaces**:
  - `/Users/correy/projects/ant-farm/orchestration/templates/pantry.md`:33, :45 -- both labels used (from clarity review)
  - `/Users/correy/projects/ant-farm/orchestration/templates/big-head-skeleton.md`:58 -- INFRASTRUCTURE FAILURE only
  - `/Users/correy/projects/ant-farm/orchestration/templates/checkpoints.md`:333 -- INFRASTRUCTURE FAILURE only
- **Combined priority**: P3 (clarity reviewer assigned P3)
- **Fix**: Add a taxonomy definition in a shared location and reference it from each template.
- **Merge rationale**: Standalone finding from Clarity F1. No duplicates across reviews, but thematically related to Root Cause 3 (failure artifact naming). Kept separate because the root cause is missing documentation of the taxonomy itself, not the artifact path pattern.
- **Acceptance criteria**: A single location defines both failure types with clear criteria for when each applies.
- **Bead**: ant-farm-k476

### Root Cause 8: Pantry partial verdict table placement is ambiguous -- per-failure or end-of-loop

- **Root cause**: The "On any failure above" block at pantry.md:68-74 appears after Condition 3 at the same indentation level. It is ambiguous whether the partial verdict table is returned once after all tasks or after each individual failure.
- **Affected surfaces**:
  - `/Users/correy/projects/ant-farm/orchestration/templates/pantry.md`:68-74 -- verdict table block (from correctness review)
- **Combined priority**: P3 (correctness reviewer assigned P3)
- **Fix**: Move the instruction to after the per-task loop ends and clarify "After processing all tasks, if any failures occurred, return a single partial verdict table."
- **Merge rationale**: Standalone finding from Correctness F4. No duplicates. Thematically related to Root Cause 4 (Pantry flow control language) but addresses a different code location and a structural placement issue rather than a wording issue.
- **Acceptance criteria**: The partial verdict table instruction is clearly positioned outside the per-task loop with explicit "run once" wording.
- **Bead**: ant-farm-oluh

### Root Cause 9: bd show failure guard only on DMVDC Check 2, missing from other bd show callsites

- **Root cause**: The ant-farm-zeu guard for `bd show` failure is placed only at checkpoints.md:332-337 (DMVDC Check 2). Other checkpoints that invoke `bd show` -- WWD (line 245) and CCB Check 2 (lines 490-492) -- lack equivalent guards.
- **Affected surfaces**:
  - `/Users/correy/projects/ant-farm/orchestration/templates/checkpoints.md`:245 -- WWD bd show without guard (from edge-cases, excellence reviews)
  - `/Users/correy/projects/ant-farm/orchestration/templates/checkpoints.md`:490-492 -- CCB Check 2 bd show without guard
- **Combined priority**: P3 (both reviewers assigned P3)
- **Fix**: Add similar guards to all bd show callsites, or create a shared "bd show failure handling" note in the Pest Control Overview section.
- **Merge rationale**: Edge Cases F5 and Excellence F5 both identify the same gap: the bd show guard was applied to one checkpoint but not to other checkpoints that use the same command. Same pattern (incomplete guard coverage), same code file, same class of missing guard.
- **Acceptance criteria**: All `bd show` callsites in checkpoints.md have failure guards or reference a shared failure handling protocol.
- **Bead**: ant-farm-zzi0

### Root Cause 10: Big Head failure artifact timestamp coexistence under re-spawn not documented

- **Root cause**: The Big Head failure artifact uses `{TIMESTAMP}` from the Queen. After a failure and re-spawn, both the old `-FAILED` file and new success file coexist (correct by design), but this behavior and the requirement for fresh timestamps on re-spawn are not documented.
- **Affected surfaces**:
  - `/Users/correy/projects/ant-farm/orchestration/templates/big-head-skeleton.md`:58 -- failure artifact path (from edge-cases, excellence reviews)
  - `/Users/correy/projects/ant-farm/orchestration/templates/big-head-skeleton.md`:20 -- wiring instructions
- **Combined priority**: P3 (both reviewers assigned P3, both confirmed no functional bug)
- **Fix**: No code change needed. Add a comment noting coexistence behavior and fresh-timestamp requirement on re-spawn.
- **Merge rationale**: Edge Cases F4 and Excellence F4 both examine the same timestamp pattern in big-head-skeleton.md:58 and reach the same conclusion: correct by design but undocumented. Both recommend documentation-only fixes.
- **Acceptance criteria**: A comment documents that failure and success artifacts may coexist and re-spawn requires a fresh TIMESTAMP.
- **Bead**: ant-farm-10ff

### Root Cause 11: Pantry empty file list guard does not validate that listed files exist on disk

- **Root cause**: The empty file list guard at pantry.md:217-228 checks for empty/whitespace input but does not verify that listed files exist on disk. If git state changes between list generation and Pantry execution, stale references could propagate to Nitpickers.
- **Affected surfaces**:
  - `/Users/correy/projects/ant-farm/orchestration/templates/pantry.md`:217-228 -- empty file list guard (from edge-cases review)
- **Combined priority**: P3 (edge-cases reviewer assigned P3, noted extremely low likelihood)
- **Fix**: Low priority. Add a documentation note that the Pantry trusts the Queen's file list and that file existence is verified by Nitpickers at review time.
- **Merge rationale**: Standalone finding from Edge Cases F6. No duplicates across reviews. The file existence validation is a distinct concern from the empty-list check, and no other reviewer raised it.
- **Acceptance criteria**: Documentation clarifies that file existence validation is deferred to Nitpickers.
- **Bead**: ant-farm-gf80

## Root Causes Filed

| Bead ID | Priority | Title | Contributing Reviews | Surfaces |
|---------|----------|-------|---------------------|----------|
| ant-farm-tek | P2 | Polling loop in reviews.md Step 0a uses fragile wc -l line-counting with globs | clarity, edge-cases, correctness, excellence | 1 file (reviews.md:370-383) |
| ant-farm-tz0q | P2 | Nested markdown code fences in reviews.md error return template break rendering | clarity, edge-cases, excellence | 1 file (reviews.md:414-420) |
| ant-farm-crky | P2 | Big Head skeleton and reviews.md have divergent failure handling for missing reports | correctness | 2 files (big-head-skeleton.md, reviews.md) |
| ant-farm-sycy | P3 | Pantry failure artifact path collision across conditions for same task | clarity, edge-cases, excellence | 1 file (pantry.md:33/47/58) |
| ant-farm-xdw3 | P3 | Pantry fail-fast says Halt but behavior is skip-to-next-task | clarity, correctness | 1 file (pantry.md:30-31) |
| ant-farm-0xqf | P3 | Skeleton format spec hints do not match Pantry actual output sections | clarity, excellence | 3 files (dirt-pusher-skeleton.md, nitpicker-skeleton.md, big-head-skeleton.md) |
| ant-farm-k476 | P3 | Failure taxonomy (INFRASTRUCTURE vs SUBSTANCE) not defined in a shared location | clarity | 3 files (pantry.md, big-head-skeleton.md, checkpoints.md) |
| ant-farm-oluh | P3 | Pantry partial verdict table placement ambiguous | correctness | 1 file (pantry.md:68-74) |
| ant-farm-zzi0 | P3 | bd show failure guard only on DMVDC Check 2, missing from other callsites | edge-cases, excellence | 1 file (checkpoints.md:245/490-492) |
| ant-farm-10ff | P3 | Big Head failure artifact timestamp coexistence under re-spawn not documented | edge-cases, excellence | 1 file (big-head-skeleton.md:58) |
| ant-farm-gf80 | P3 | Pantry empty file list guard does not validate file existence on disk | edge-cases | 1 file (pantry.md:217-228) |

## Deduplication Log

24 raw findings consolidated into 11 root causes. Mapping:

| Raw Finding | Root Cause | Merge Reason |
|-------------|-----------|--------------|
| Clarity F1 (failure label taxonomy) | RC7 (ant-farm-k476) | Standalone -- taxonomy definition gap |
| Clarity F2 (MISSING_REPORTS variable name) | RC1 (ant-farm-tek) | Same code block reviews.md:370-383, variable naming facet of polling loop defect |
| Clarity F3 (nested code fences) | RC2 (ant-farm-tz0q) | Same code block reviews.md:414-420 |
| Clarity F4 (skeleton format spec mismatch) | RC6 (ant-farm-0xqf) | Same pattern: skeleton hints vs Pantry output mismatch |
| Clarity F5 (failure artifact path collision) | RC3 (ant-farm-sycy) | Same shared-path pattern in pantry.md:33/47/58 |
| Clarity F6 (halt vs skip wording) | RC4 (ant-farm-xdw3) | Same word "Halt" at pantry.md:30-31 |
| Edge Cases F1 (glob multi-match in polling) | RC1 (ant-farm-tek) | Same code block reviews.md:370-383, glob expansion facet |
| Edge Cases F2 (no post-loop failure check) | RC1 (ant-farm-tek) | Same code block reviews.md:370-383, missing post-loop check |
| Edge Cases F3 (failure artifact collision) | RC3 (ant-farm-sycy) | Same shared-path pattern in pantry.md:33/47/58 |
| Edge Cases F4 (timestamp under re-spawn) | RC10 (ant-farm-10ff) | Same timestamp pattern in big-head-skeleton.md:58 |
| Edge Cases F5 (bd show guard coverage) | RC9 (ant-farm-zzi0) | Same incomplete guard coverage in checkpoints.md |
| Edge Cases F6 (stale file references) | RC11 (ant-farm-gf80) | Standalone -- file existence validation gap |
| Edge Cases F7 (nested code fences) | RC2 (ant-farm-tz0q) | Same code block reviews.md:414-420 |
| Correctness F1 (polling logic inversion) | RC1 (ant-farm-tek) | Same code block reviews.md:370-383, logic inversion facet |
| Correctness F2 (divergent failure handling) | RC5 (ant-farm-crky) | Standalone -- cross-template contradiction |
| Correctness F3 (halt vs skip wording) | RC4 (ant-farm-xdw3) | Same word "Halt" at pantry.md:30-31 |
| Correctness F4 (verdict table placement) | RC8 (ant-farm-oluh) | Standalone -- structural placement ambiguity |
| Excellence F1 (polling loop fragility) | RC1 (ant-farm-tek) | Same code block reviews.md:370-383, line-counting fragility |
| Excellence F2 (nested code fences) | RC2 (ant-farm-tz0q) | Same code block reviews.md:414-420 |
| Excellence F3 (failure artifact collision) | RC3 (ant-farm-sycy) | Same shared-path pattern in pantry.md:33/47/58 |
| Excellence F4 (timestamp coexistence) | RC10 (ant-farm-10ff) | Same timestamp pattern in big-head-skeleton.md:58 |
| Excellence F5 (bd show guard coverage) | RC9 (ant-farm-zzi0) | Same incomplete guard coverage in checkpoints.md |
| Excellence F6 (shell state persistence) | RC1 (ant-farm-tek) | Same code block reviews.md:370-383, execution environment facet |
| Excellence F7 (skeleton format hint missing) | RC6 (ant-farm-0xqf) | Same pattern: skeleton-Pantry format mismatch |

**Deduplication ratio**: 24 raw findings -> 11 root causes (54% dedup rate)

## Priority Breakdown

- **P1 (blocking)**: 0 beads
- **P2 (important)**: 3 beads (ant-farm-tek, ant-farm-tz0q, ant-farm-crky)
- **P3 (polish)**: 8 beads (ant-farm-sycy, ant-farm-xdw3, ant-farm-0xqf, ant-farm-k476, ant-farm-oluh, ant-farm-zzi0, ant-farm-10ff, ant-farm-gf80)

### P2 Root Cause Summary

1. **ant-farm-tek**: Polling loop in reviews.md Step 0a has multiple defects (inverted variable name, glob fragility, missing timeout detection, shell persistence concern). 6 contributing findings across all 4 reviews.
2. **ant-farm-tz0q**: Nested markdown code fences cause premature fence closure in error return template. 3 contributing findings across 3 reviews.
3. **ant-farm-crky**: Big Head receives contradictory instructions (immediate fail vs 30-second polling) from skeleton vs reviews.md. 1 finding from correctness review.

### P3 Pattern Analysis

The 8 P3 findings cluster into three themes:
- **Documentation gaps** (4 beads): Missing taxonomy definition, undocumented timestamp behavior, ambiguous verdict table placement, missing format hints
- **Naming/wording precision** (2 beads): "Halt" vs "skip", failure artifact path doesn't encode condition type
- **Incomplete guard coverage** (2 beads): bd show guard on one callsite, file existence not validated

## Verdict

**PASS WITH ISSUES**

The changes reviewed (ant-farm-zeu, ant-farm-e9k, ant-farm-x4m) add valuable defensive guards and failure handling to the orchestration pipeline. All acceptance criteria for the three tasks are met. The 3 P2 issues are concentrated in the new Step 0a remediation path in reviews.md (polling loop logic and nested fences) and a cross-template design contradiction between big-head-skeleton.md and reviews.md. These affect error-handling edge cases in agent templates, not the primary workflow. The 8 P3 issues are polish-level concerns around documentation, naming consistency, and guard coverage. No P1 blockers were found. The codebase is safe to ship with these issues tracked for follow-up.

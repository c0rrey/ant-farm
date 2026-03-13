# Consolidated Review Summary

**Scope**: orchestration/RULES.md, orchestration/templates/big-head-skeleton.md, orchestration/templates/checkpoints.md, orchestration/templates/nitpicker-skeleton.md, orchestration/templates/pantry.md, orchestration/templates/queen-state.md, orchestration/templates/reviews.md
**Reviews completed**: Clarity, Edge Cases, Correctness, Excellence
**Reports verified**: clarity-review.md [check], edge-cases-review.md [check], correctness-review.md [check], excellence-review.md [check]
**Total raw findings**: 37 across all reviews
**Root causes identified**: 18 after deduplication
**Beads filed**: 18

---

## Read Confirmation

**All 4 reports read and processed by Big Head consolidation:**

| Report Type | File | Status | Finding Count |
|-------------|------|--------|---------------|
| Clarity | clarity-review-20260219-120000.md | Read | 16 findings |
| Edge Cases | edge-cases-review-20260219-120000.md | Read | 8 findings |
| Correctness | correctness-review-20260219-120000.md | Read | 1 finding |
| Excellence | excellence-review-20260219-120000.md | Read | 12 findings |

**Total findings from all reports**: 37

---

## Root Causes Filed

| Bead ID | Priority | Title | Contributing Reviews | Surfaces |
|---------|----------|-------|---------------------|----------|
| ant-farm-60mh | P2 | Big Head Step 0 glob matching can silently consolidate stale reports from prior review rounds | edge-cases, edge-cases | reviews.md:411-424, reviews.md:452-485 |
| ant-farm-4l0t | P2 | PARTIAL verdict state missing from checkpoints.md Verdict Thresholds Summary | clarity | checkpoints.md:54-91, checkpoints.md:369, checkpoints.md:430, checkpoints.md:549 |
| ant-farm-rcdd | P2 | No hard cap on review rounds creates unbounded retry loop risk | edge-cases | reviews.md:143-144, RULES.md:117-121, queen-state.md:37 |
| ant-farm-w1dn | P3 | Development artifacts left in production templates | clarity | checkpoints.md:145, checkpoints.md:560-561 |
| ant-farm-j6jq | P3 | Shell code blocks lack production quality: magic numbers, inverted sentinel, buried constraints | excellence | reviews.md:447, reviews.md:452, reviews.md:449-450, reviews.md:469-473 |
| ant-farm-fkfw | P3 | Fragile grep-based Future Work epic discovery with no error handling | edge-cases, excellence | reviews.md:683, big-head-skeleton.md:93-98, reviews.md:681-692 |
| ant-farm-glzg | P3 | Placeholder syntax inconsistency: queen-state.md vs other templates | clarity, excellence | queen-state.md:1-47 |
| ant-farm-2r4j | P3 | Canonical term definitions copy-pasted across 3 templates without single source of truth | clarity | big-head-skeleton.md:8-13, checkpoints.md:4-10, pantry.md:6-11 |
| ant-farm-ppey | P3 | Incomplete failure paths in agent protocols | excellence | big-head-skeleton.md:89-92, reviews.md:643-651, nitpicker-skeleton.md:23, pantry.md:311-316 |
| ant-farm-jegj | P3 | Commit range and file list validation gaps | edge-cases | RULES.md:95, pantry.md:216-228 |
| ant-farm-bva6 | P3 | Cross-file navigation gaps: undeclared sub-step convention, missing path refs, no inline cross-references | clarity | RULES.md:89, reviews.md:10, reviews.md:707-734 |
| ant-farm-s7vu | P3 | Termination Rule wording ambiguity in reviews.md | correctness | reviews.md:141 |
| ant-farm-wk1a | P3 | Round 2+ scope instructions inconsistently presented | clarity | nitpicker-skeleton.md:21-22 |
| ant-farm-ch3m | P3 | Session state bootstrapping gap: queen-state.md creation not in Step 0 | excellence | RULES.md:177-192 |
| ant-farm-9nws | P3 | Retry count asymmetry between RULES.md and reviews.md undocumented | excellence | reviews.md:634-643, RULES.md:230-234 |
| ant-farm-ot9d | P3 | CCB Check 7 O(N) bead scan not scoped to session-created beads | excellence | checkpoints.md:543-548 |
| ant-farm-cozw | P3 | CCB reconciliation formula does not detect orphaned merge targets | edge-cases | checkpoints.md:501-505 |
| ant-farm-f3t0 | P3 | queen-state.md fix commit range has no crash-recovery reconstruction guidance | edge-cases | queen-state.md:36 |
| ant-farm-cfp8 | P3 | Documentation polish: minor formatting, redundancy, and structural inconsistencies | clarity | RULES.md:12, RULES.md:131-138, RULES.md:205, pantry.md:201, pantry.md:216-226, reviews.md:55-73, reviews.md:390 |

---

## Root Cause Groupings with Merge Rationale

### RC-1: ant-farm-60mh (P2) -- Stale glob matching in Big Head Step 0 and polling loop

- **Root cause**: File existence checks in Big Head's Step 0 (`ls ...-review-*.md`) and the polling loop use glob patterns that match any file with the review prefix, regardless of which round produced it. In multi-round sessions, old round-1 reports persist on disk and satisfy the glob, causing Big Head to consolidate stale data.
- **Affected surfaces**:
  - reviews.md:411-424 -- Step 0 `ls` check uses `*-review-*.md` glob (from edge-cases F2)
  - reviews.md:464-472 -- Polling loop glob matches stale files (from edge-cases F2)
  - reviews.md:483-485 -- Polling loop TIMED_OUT exit only echoes, no `exit 1` (from edge-cases F1)
- **Combined priority**: P2 (both contributing findings were P2)
- **Fix**: Replace all glob-based file checks with exact-timestamp path checks. The Queen generates a single timestamp per review cycle, so Big Head should receive exact file paths and use `[ -f "$EXACT_PATH" ]`. Also add `exit 1` after the TIMED_OUT echo to make the shell block itself signal failure.
- **Merge rationale**: Edge-cases F1 and F2 share the same code path (the Big Head polling loop in reviews.md:447-485). F1 is about the exit behavior when the loop times out; F2 is about the glob matching wrong files. Both are control-flow bugs in the same polling mechanism. The fix for F2 (exact paths) also eliminates the scenario where F1's weak exit signal matters on partial stale data.
- **Acceptance criteria**: (1) No `*-review-*.md` globs remain in Big Head Step 0 or polling loop; (2) TIMED_OUT path includes `exit 1`; (3) Round 2 session does not match round 1 report files.

### RC-2: ant-farm-4l0t (P2) -- PARTIAL verdict state missing from Verdict Thresholds Summary

- **Root cause**: The Verdict Thresholds Summary section in checkpoints.md (lines 54-91) defines PASS, WARN, and FAIL but omits PARTIAL, which is used in DMVDC and CCB sections. Pest Control agents read the summary first and will not expect PARTIAL when they encounter it in individual checkpoint sections.
- **Affected surfaces**:
  - checkpoints.md:54-91 -- Verdict Thresholds Summary table (from clarity F6)
  - checkpoints.md:369 -- DMVDC Dirt Pushers uses PARTIAL (from clarity F6)
  - checkpoints.md:430 -- DMVDC Nitpickers uses PARTIAL (from clarity F6)
  - checkpoints.md:549 -- CCB uses PARTIAL (from clarity F6)
- **Combined priority**: P2 (single source, clarity F6 rated P2)
- **Fix**: Add PARTIAL to the Common Verdict Definitions section (line 49) with definition: "PARTIAL (DMVDC and CCB only): Some checks failed. Agent can repair and resubmit, or consolidation can be amended. Does not escalate to user." Update the checkpoint-specific thresholds table (line 63) to include PARTIAL for DMVDC and CCB rows.
- **Merge rationale**: No merge -- single finding from one reviewer. Filed separately because the root cause is distinct (incomplete summary table) and the fix is a single edit to one section.
- **Acceptance criteria**: (1) PARTIAL appears in Common Verdict Definitions; (2) PARTIAL appears in checkpoint-specific thresholds table for DMVDC and CCB rows; (3) No other checkpoint types reference PARTIAL.

### RC-3: ant-farm-rcdd (P2) -- Unbounded review round loop

- **Root cause**: reviews.md states "There is no hard cap on rounds." RULES.md retry limits cover Dirt Pusher DMVDC/CCB failures, not review round cycles. A regression loop where each fix introduces new P1/P2 findings would run indefinitely.
- **Affected surfaces**:
  - reviews.md:143-144 -- Termination Rule states no hard cap (from edge-cases F3)
  - RULES.md:117-121 -- Step 3c has no round cap (from edge-cases F3)
  - queen-state.md:37 -- Tracks current round but no cap (from edge-cases F3)
- **Combined priority**: P2 (single source, edge-cases F3 rated P2)
- **Fix**: Add a recommended cap: "After round 4 with no convergence, escalate to user with full round history and ask whether to continue or abort." Document in reviews.md Termination Rule, RULES.md Step 3c, and queen-state.md Review Rounds section.
- **Merge rationale**: No merge -- single finding spanning 3 files but one root cause (missing cap on an iterative loop).
- **Acceptance criteria**: (1) A round cap or escalation trigger is documented in all 3 locations; (2) queen-state.md tracks the cap.

### RC-4: ant-farm-w1dn (P3) -- Development artifacts in production templates

- **Root cause**: Two development-era comments survived into production templates that agents read as instructions: "(NEW - prevents scope creep)" annotation on CCO Check 7, and "CRITICAL FIX" changelog note embedded inside a CCB code block.
- **Affected surfaces**:
  - checkpoints.md:145 -- "(NEW - prevents scope creep)" annotation (from clarity F7)
  - checkpoints.md:560-561 -- "CRITICAL FIX" note inside code block (from clarity F8)
- **Combined priority**: P3 (both P3)
- **Fix**: Remove "(NEW - prevents scope creep)" from line 145. Move "CRITICAL FIX" note outside the code block to a Design Notes section or remove entirely (rationale is in git history).
- **Merge rationale**: Both are the same pattern: development-era annotations that should have been removed before the templates were finalized. They share the same file (checkpoints.md) and the same underlying cause (incomplete cleanup pass). Agents reading these templates will see the annotations as instructions rather than changelog notes.
- **Acceptance criteria**: (1) No "(NEW ...)" annotations remain in checkpoints.md; (2) No "CRITICAL FIX" notes appear inside code blocks.

### RC-5: ant-farm-j6jq (P3) -- Shell code blocks lack production quality

- **Root cause**: Shell code blocks embedded in reviews.md are treated as prose rather than executable artifacts. Four specific issues: (a) the shell variable persistence constraint is buried in a comment inside a code block rather than elevated to visible prose; (b) TIMED_OUT=1 is a non-idiomatic sentinel (inverted boolean); (c) TIMEOUT=30 and POLL_INTERVAL=2 are undocumented magic numbers; (d) `<IF ROUND 1>` pseudo-XML markers could confuse implementers.
- **Affected surfaces**:
  - reviews.md:447 -- Shell persistence warning buried in comment (from excellence F1)
  - reviews.md:452 -- TIMED_OUT=1 inverted sentinel (from excellence F2)
  - reviews.md:449-450 -- TIMEOUT=30, POLL_INTERVAL=2 undocumented (from excellence F3)
  - reviews.md:469-473 -- `<IF ROUND 1>` pseudo-syntax (from excellence F5)
- **Combined priority**: P3 (all P3)
- **Fix**: (a) Add bold admonition above code block about single Bash invocation; (b) Rename TIMED_OUT to ALL_REPORTS_FOUND with standard boolean convention; (c) Add inline comments explaining timeout/interval rationale; (d) Rename pseudo-markers to `# PANTRY INSERTS BELOW ONLY FOR ROUND 1:`.
- **Merge rationale**: All 4 findings are in the same polling loop code block (reviews.md:447-485). The root cause is that this block was written as documentation prose rather than being reviewed as executable code. A single "shell code quality pass" on this block fixes all 4 issues.
- **Acceptance criteria**: (1) No magic numbers without comments; (2) Boolean sentinels use standard convention; (3) Critical constraints appear in prose above the code block; (4) Conditional markers use unambiguous English labels.

### RC-6: ant-farm-fkfw (P3) -- Fragile grep-based Future Work epic discovery

- **Root cause**: Both reviews.md and big-head-skeleton.md use `bd list --status=open | grep -i "future work"` to find the Future Work epic. This pattern is fragile in three ways: (a) `bd list` or `bd epic create` can fail with no recovery path, silently dropping P3 filings; (b) a typo in the epic title causes grep to return 0 results, silently creating a duplicate epic; (c) multiple matches cause the wrong epic to be selected.
- **Affected surfaces**:
  - reviews.md:683 -- grep pattern for Future Work epic (from excellence F6)
  - reviews.md:681-692 -- P3 auto-filing full section (from edge-cases F4)
  - big-head-skeleton.md:93-98 -- Same grep pattern duplicated (from excellence F6, edge-cases F4)
- **Combined priority**: P3 (edge-cases F4 and excellence F6 both P3)
- **Fix**: Replace grep-based lookup with an exact epic ID stored in the session state file. Add explicit failure handling: if `bd epic create` fails, record the error in the consolidated summary under "Auto-Filed P3s (Future Work)" as "FAILED: <error>". Add count guard: if 0 or 2+ results, log warning before proceeding.
- **Merge rationale**: Edge-cases F4 and excellence F6 both target the same `bd list | grep "future work"` pattern in the same two files. F4 covers the command-failure scenario; F6 covers the zero-match and multi-match scenarios. The root cause is the same fragile discovery mechanism. The fix (exact epic ID) eliminates all three failure modes.
- **Acceptance criteria**: (1) No `grep -i "future work"` patterns remain; (2) Epic ID is passed via session state; (3) bd command failures are recorded, not silently dropped.

### RC-7: ant-farm-glzg (P3) -- Placeholder syntax inconsistency

- **Root cause**: queen-state.md uses `<angle-bracket>` placeholders (e.g., `<timestamp>`, `<session-id>`) while all other templates use `{UPPERCASE_CURLY}` syntax. Additionally, queen-state.md mixes option lists (`pending/completed/failed`) with fill-in placeholders (`<N>`) without visual distinction. The Pantry's contamination check (pantry.md:57) flags `<angle-bracket text>` as contamination, creating false-positive risk.
- **Affected surfaces**:
  - queen-state.md:1-47 -- All placeholder usage (from clarity F12, excellence F8)
- **Combined priority**: P3 (both P3)
- **Fix**: Switch queen-state.md to `{UPPERCASE_CURLY}` placeholders. Use `[option1|option2]` bracket syntax for option lists. Add exclusion note or adopt consistent convention across all templates.
- **Merge rationale**: Clarity F12 and excellence F8 both identify the same file (queen-state.md) and the same issue (placeholder syntax differs from the project convention). F12 focuses on the option-list vs fill-in ambiguity; F8 focuses on the angle-bracket vs curly-brace mismatch and the contamination false-positive risk. Same file, same root cause (no style convention applied to this template).
- **Acceptance criteria**: (1) queen-state.md uses `{UPPERCASE_CURLY}` placeholders; (2) Option lists use `[a|b|c]` syntax; (3) No `<angle-bracket>` placeholders remain in queen-state.md.

### RC-8: ant-farm-2r4j (P3) -- Canonical term definitions without single source of truth

- **Root cause**: The term definitions block (`{TASK_ID}`, `{TASK_SUFFIX}`, `{SESSION_DIR}`, etc.) is copy-pasted across big-head-skeleton.md, checkpoints.md, and pantry.md with minor variations. Each claims to be "canonical" but the content differs (some include `{REVIEW_ROUND}`, some do not).
- **Affected surfaces**:
  - big-head-skeleton.md:8-13 -- Term defs including {REVIEW_ROUND} (from clarity F5)
  - checkpoints.md:4-10 -- Term defs without {REVIEW_ROUND} (from clarity F5)
  - pantry.md:6-11 -- Term defs without {REVIEW_ROUND} (from clarity F5)
- **Combined priority**: P3 (single finding)
- **Fix**: Add a reference to dependency-analysis.md in each file. Each local block should note "See dependency-analysis.md for full extraction rules; terms listed here are the subset used in this file."
- **Merge rationale**: No merge -- single finding from one reviewer.
- **Acceptance criteria**: (1) Each file's term block states which terms are file-local; (2) A pointer to the canonical definition source exists in each file.

### RC-9: ant-farm-ppey (P3) -- Incomplete failure paths in agent protocols

- **Root cause**: Agent templates document the happy path thoroughly but leave error branches underspecified. Three specific gaps: Big Head's timeout escalation says "escalate to Queen" but doesn't specify the mechanism; Nitpicker has no fallback if `{DATA_FILE_PATH}` is missing; Pantry Section 3 error handling is two bullet points with no definition of recoverable vs unrecoverable errors.
- **Affected surfaces**:
  - reviews.md:643-651 -- Big Head escalation mechanism unspecified (from excellence F7)
  - big-head-skeleton.md:89-92 -- Same escalation gap in skeleton (from excellence F7)
  - nitpicker-skeleton.md:23 -- No fallback for missing brief (from excellence F9)
  - pantry.md:311-316 -- Section 3 underspecified (from excellence F12)
- **Combined priority**: P3 (all P3)
- **Fix**: Add a mandatory "Failure Paths" subsection to each agent template: trigger condition, escalation mechanism, recipient, and artifact to write. Specifically: Big Head should use `SendMessage` to team-lead or write a `-BLOCKED.md` file; Nitpicker should STOP and return a BLOCKED message; Pantry should define recoverable vs unrecoverable errors with examples.
- **Merge rationale**: All three findings share the root cause of "failure paths receive less design attention than success paths." Each is in a different agent template but the pattern is identical: the happy path is multi-step and detailed, the error path is absent or a single sentence. A single design principle ("all agent templates must specify failure paths") fixes all three.
- **Acceptance criteria**: (1) Big Head escalation specifies SendMessage or file-based mechanism; (2) Nitpicker has a STOP-and-report path for missing briefs; (3) Pantry Section 3 defines recoverable vs unrecoverable with examples.

### RC-10: ant-farm-jegj (P3) -- Commit range and file list validation gaps

- **Root cause**: Neither RULES.md Step 3b nor the Pantry's empty-file-list guard validates that the commit range is valid and the resulting file list matches the actual git diff. An invalid commit range produces an empty or error-containing result; a stale file list from a prior run propagates incorrect data to reviewers.
- **Affected surfaces**:
  - RULES.md:95 -- Step 3b `git diff --name-only` with no validation (from edge-cases F8)
  - pantry.md:216-228 -- Empty file list guard doesn't cross-check git diff (from edge-cases F6)
- **Combined priority**: P3 (both P3)
- **Fix**: In RULES.md Step 3b, add: "Verify commit range by running `git log --oneline <range>` first." In pantry.md guard, add: "Run `git diff --name-only <range>` to cross-check Queen's file list; if they disagree, use git diff result."
- **Merge rationale**: Both findings are about the same data pipeline: the Queen produces a commit range (RULES.md Step 3b), which generates a file list, which the Pantry receives and guards (pantry.md). F8 is about the source (invalid range), F6 is about the consumer (no cross-check). The root cause is the same: no validation of the commit-range-to-file-list pipeline.
- **Acceptance criteria**: (1) Step 3b includes commit range validation; (2) Pantry guard includes git diff cross-check.

### RC-11: ant-farm-bva6 (P3) -- Cross-file navigation gaps

- **Root cause**: The orchestration documents lack declared navigation conventions and inline cross-references, forcing readers to already know the full document structure. Three specific gaps: RULES.md uses Step 3b/3c sub-step notation without declaring the convention; reviews.md Transition Gate refers to "the Queen's state file" without a path; reviews.md checklists reference procedures without linking to where they are defined.
- **Affected surfaces**:
  - RULES.md:89 -- Step 3b/3c sub-step convention undeclared (from clarity F2)
  - reviews.md:10 -- Transition Gate missing state file path (from clarity F13)
  - reviews.md:707-734 -- Checklists lack inline cross-references (from clarity F16)
- **Combined priority**: P3 (all P3)
- **Fix**: (1) Add a "Document Conventions" note at the top of RULES.md declaring the sub-step notation; (2) Change reviews.md:10 to include `({SESSION_DIR}/queen-state.md)`; (3) Add inline section references to checklist items.
- **Merge rationale**: All three findings stem from the same root cause: the documentation assumes readers already know the full structure. They share the pattern of "reference to something without saying where it is." The fix is the same principle applied in three places: add explicit pointers.
- **Acceptance criteria**: (1) Sub-step convention is declared; (2) State file path is inline in Transition Gate; (3) Checklist items have section cross-references.

### RC-12: ant-farm-s7vu (P3) -- Termination Rule wording ambiguity

- **Root cause**: reviews.md:141 says "Queen proceeds directly to RULES.md Step 4 (documentation)" -- the word "directly" can be read as "skip Handle P3 Issues." The more detailed Termination Check section (lines 750-759) correctly enumerates the order, but the summary is imprecise.
- **Affected surfaces**:
  - reviews.md:141 -- Termination Rule bullet 3 (from correctness F1)
- **Combined priority**: P3 (single finding)
- **Fix**: Change to "Queen proceeds to RULES.md Step 4 (documentation) -- Round 1: after Handle P3 Issues; Round 2+: directly (P3s already auto-filed by Big Head)".
- **Merge rationale**: No merge -- single finding from one reviewer.
- **Acceptance criteria**: (1) The word "directly" is qualified with round-specific context; (2) Round 1 path explicitly mentions Handle P3 Issues.

### RC-13: ant-farm-wk1a (P3) -- Round 2+ scope instructions inconsistently presented

- **Root cause**: nitpicker-skeleton.md embeds the round 2+ scope restriction inline after the field label (line 21-22), while reviews.md uses a blockquote for the same content. The skeleton does not match the visual treatment of the authoritative source.
- **Affected surfaces**:
  - nitpicker-skeleton.md:21-22 -- Round 2+ scope restriction inline (from clarity F9)
- **Combined priority**: P3 (single finding)
- **Fix**: Move the round 2+ instructions to a clearly marked blockquote block, matching the treatment in reviews.md.
- **Merge rationale**: No merge -- single finding from one reviewer.
- **Acceptance criteria**: (1) Round 2+ scope restriction in nitpicker-skeleton.md uses blockquote or bold block treatment.

### RC-14: ant-farm-ch3m (P3) -- Session state bootstrapping gap

- **Root cause**: RULES.md Step 0 creates subdirectories via `mkdir -p` but does not specify when or how to create the `queen-state.md` session state file from its template. The Template Lookup table lists it but does not say to instantiate it during Step 0.
- **Affected surfaces**:
  - RULES.md:177-192 -- Step 0 session directory setup (from excellence F10)
- **Combined priority**: P3 (single finding)
- **Fix**: Add to Step 0: "Create the Queen's session state file by copying `orchestration/templates/queen-state.md` to `{SESSION_DIR}/queen-state.md` and filling in Session ID and start timestamp."
- **Merge rationale**: No merge -- single finding from one reviewer.
- **Acceptance criteria**: (1) Step 0 includes explicit queen-state.md creation instruction.

### RC-15: ant-farm-9nws (P3) -- Retry count asymmetry undocumented

- **Root cause**: reviews.md specifies Big Head retries once on Pest Control timeout (2 total attempts), while RULES.md retry limits table shows "CCB fails -> 1 retry" for a different checkpoint. The asymmetry is not documented, so a reader of RULES.md may assume "1 retry" covers all retry scenarios.
- **Affected surfaces**:
  - reviews.md:634-643 -- Big Head 2-attempt protocol (from excellence F4)
  - RULES.md:230-234 -- Retry limits table (from excellence F4)
- **Combined priority**: P3 (single finding)
- **Fix**: Add footnote to RULES.md Retry Limits table: "Note: Big Head's SendMessage to Pest Control has its own 2-attempt protocol (see reviews.md Step 4)."
- **Merge rationale**: No merge -- single finding from one reviewer.
- **Acceptance criteria**: (1) RULES.md retry limits table cross-references reviews.md Big Head protocol.

### RC-16: ant-farm-ot9d (P3) -- CCB Check 7 O(N) bead scan

- **Root cause**: CCB Check 7 instructs Pest Control to run `bd list --status=open` and cross-reference against the consolidated summary. As the bead database grows, this is an unscoped O(N) scan.
- **Affected surfaces**:
  - checkpoints.md:543-548 -- CCB Check 7 (from excellence F11)
- **Combined priority**: P3 (single finding)
- **Fix**: Scope to session-created beads via `--created-after=<session-start>` or cross-reference only bead IDs in the consolidated summary.
- **Merge rationale**: No merge -- single finding from one reviewer.
- **Acceptance criteria**: (1) CCB Check 7 scopes bead scan to current session.

### RC-17: ant-farm-cozw (P3) -- CCB reconciliation formula gap

- **Root cause**: CCB Check 1 does not verify that every root cause listed in the dedup log as a merge target actually appears in the Root Causes Filed table. A dropped root-cause group creates a reconciliation gap that the mechanical count misses.
- **Affected surfaces**:
  - checkpoints.md:501-505 -- CCB Check 1 reconciliation (from edge-cases F5)
- **Combined priority**: P3 (single finding)
- **Fix**: Add clause: "Verify that every root cause listed in the dedup log as the merge target actually appears in the Root Causes Filed table. If a target root cause is absent, flag as NOT RECONCILED."
- **Merge rationale**: No merge -- single finding from one reviewer.
- **Acceptance criteria**: (1) CCB Check 1 includes merge-target presence verification.

### RC-18: ant-farm-f3t0 (P3) -- queen-state.md crash recovery gap

- **Root cause**: If a session crashes mid-review, the "Fix commit range" field in queen-state.md may be blank. A resumed Queen cannot reconstruct the correct round 2+ commit range because no fallback instruction is provided.
- **Affected surfaces**:
  - queen-state.md:36 -- Fix commit range field (from edge-cases F7)
- **Combined priority**: P3 (single finding)
- **Fix**: Add recovery hint: "If resuming a crashed session, reconstruct fix commit range via `git log --oneline <first-session-commit>..HEAD` and identify commits with '[fix]' suffixes."
- **Merge rationale**: No merge -- single finding from one reviewer.
- **Acceptance criteria**: (1) queen-state.md includes reconstruction guidance for fix commit range.

### RC-19: ant-farm-cfp8 (P3) -- Documentation polish: miscellaneous formatting and structural inconsistencies

- **Root cause**: Several documentation files have minor formatting, redundancy, or structural inconsistencies that do not affect functionality but reduce readability. These share the root cause of "no style guide applied during authoring" but are each in different files about different topics.
- **Affected surfaces**:
  - RULES.md:12 -- Ambiguous pronoun in path reference convention (from clarity F1)
  - RULES.md:131-138 -- Hard Gates table: prose in Artifact column (from clarity F3)
  - RULES.md:205 -- Anti-Patterns entry redundant with Queen Prohibitions (from clarity F4)
  - pantry.md:201 -- Section 2 input list: review round number buried at end (from clarity F10)
  - pantry.md:216-226 -- GUARD block: "SUBSTANCE FAILURE" terminology mismatch (from clarity F11)
  - reviews.md:55-73 -- Tilde vs backtick fence inconsistency (from clarity F14)
  - reviews.md:390 -- Big Head section hierarchy misleading (from clarity F15)
- **Combined priority**: P3 (all P3)
- **Fix**: Apply minor edits: (1) Rewrite RULES.md:12 for clarity; (2) Move Hard Gates prose to a note; (3) Add cross-ref to Anti-Patterns entry or remove it; (4) Reorder pantry input list; (5) Align GUARD terminology; (6) Add comment explaining tilde fences; (7) Add horizontal rule before Big Head section.
- **Merge rationale**: These 7 findings are all P3 documentation polish items from the clarity review. None shares a specific code path or design flaw with another, but they share the meta-root-cause of "no editorial style pass was applied." Filing them individually would create 7 trivial beads that are better addressed in a single cleanup pass. This is the one intentional over-merge in this consolidation, and it is justified because: (a) all are P3 with no functional impact; (b) all are "reword/reformat" fixes; (c) a single editorial pass across the 4 affected files is more efficient than 7 separate PRs.
- **Acceptance criteria**: All 7 specific items addressed per their individual suggested fixes.

---

## Deduplication Log

### Merged Findings

| Consolidated Bead | Merged Findings | Merge Reason |
|-------------------|-----------------|--------------|
| ant-farm-60mh (RC-1) | Edge-cases F1 + Edge-cases F2 | Same code path: Big Head polling loop (reviews.md:447-485). F1 is exit signal, F2 is glob matching. Both are control-flow bugs in the same mechanism. |
| ant-farm-w1dn (RC-4) | Clarity F7 + Clarity F8 | Same file (checkpoints.md), same pattern: development-era comments that survived into production templates. Single cleanup pass fixes both. |
| ant-farm-j6jq (RC-5) | Excellence F1 + F2 + F3 + F5 | Same code block (reviews.md:447-485 polling loop). All are shell code quality issues in the same embedded script. Single code-quality pass fixes all four. |
| ant-farm-fkfw (RC-6) | Edge-cases F4 + Excellence F6 | Same pattern in same two files: `bd list | grep "future work"`. F4 covers command failure; F6 covers match ambiguity. Same fix (exact epic ID) eliminates all failure modes. |
| ant-farm-glzg (RC-7) | Clarity F12 + Excellence F8 | Same file (queen-state.md), same issue: placeholder syntax differs from project convention. F12 is about option-list ambiguity; F8 is about contamination false-positive risk. Both fixed by adopting standard syntax. |
| ant-farm-ppey (RC-9) | Excellence F7 + F9 + F12 | Same pattern across 3 agent templates: failure paths underspecified vs detailed happy paths. Single design principle ("specify failure paths") fixes all. |
| ant-farm-jegj (RC-10) | Edge-cases F6 + Edge-cases F8 | Same data pipeline: commit range (RULES.md) -> file list (Pantry). F8 is source validation; F6 is consumer validation. Both are validation gaps in the same pipeline. |
| ant-farm-bva6 (RC-11) | Clarity F2 + F13 + F16 | Same pattern: references without explicit pointers. All three assume the reader knows the full document structure. Same fix: add explicit cross-references. |
| ant-farm-cfp8 (RC-19) | Clarity F1 + F3 + F4 + F10 + F11 + F14 + F15 | Meta-root-cause: no editorial style pass. All P3 documentation polish with no functional impact. Grouped to avoid 7 trivial individual beads. |

### Standalone Findings (No Merge)

| Consolidated Bead | Source Finding | Reason Not Merged |
|-------------------|---------------|-------------------|
| ant-farm-4l0t (RC-2) | Clarity F6 | Unique root cause: missing verdict state in summary table. No other finding covers this specific table omission. |
| ant-farm-rcdd (RC-3) | Edge-cases F3 | Unique root cause: unbounded iterative loop. No other finding covers round caps. |
| ant-farm-2r4j (RC-8) | Clarity F5 | Unique root cause: copy-pasted term definitions. No other finding covers cross-file definition drift. |
| ant-farm-s7vu (RC-12) | Correctness F1 | Unique root cause: specific wording ambiguity at reviews.md:141. No other finding covers this exact sentence. |
| ant-farm-wk1a (RC-13) | Clarity F9 | Unique root cause: visual treatment of round 2+ scope. No other finding covers nitpicker-skeleton formatting. |
| ant-farm-ch3m (RC-14) | Excellence F10 | Unique root cause: missing bootstrapping step. No other finding covers Step 0 state file creation. |
| ant-farm-9nws (RC-15) | Excellence F4 | Unique root cause: undocumented retry asymmetry. No other finding covers retry count cross-references. |
| ant-farm-ot9d (RC-16) | Excellence F11 | Unique root cause: unscoped bead scan. No other finding covers CCB Check 7 scalability. |
| ant-farm-cozw (RC-17) | Edge-cases F5 | Unique root cause: reconciliation formula gap. No other finding covers dropped merge targets. |
| ant-farm-f3t0 (RC-18) | Edge-cases F7 | Unique root cause: crash recovery for fix commit range. No other finding covers session resume. |

---

## Traceability Matrix

Every raw finding mapped to its consolidated bead:

| Review | Finding # | Description (abbreviated) | Consolidated Bead |
|--------|-----------|--------------------------|-------------------|
| Clarity | F1 | Ambiguous pronoun RULES.md:12 | ant-farm-cfp8 |
| Clarity | F2 | Step 3b/3c sub-step convention | ant-farm-bva6 |
| Clarity | F3 | Hard Gates table prose in Artifact column | ant-farm-cfp8 |
| Clarity | F4 | Anti-Patterns redundant with Prohibitions | ant-farm-cfp8 |
| Clarity | F5 | Term definitions copy-pasted | ant-farm-2r4j |
| Clarity | F6 | PARTIAL verdict missing from summary | ant-farm-4l0t |
| Clarity | F7 | "(NEW)" annotation in CCO Check 7 | ant-farm-w1dn |
| Clarity | F8 | "CRITICAL FIX" note in CCB code block | ant-farm-w1dn |
| Clarity | F9 | Round 2+ scope inline in nitpicker-skeleton | ant-farm-wk1a |
| Clarity | F10 | Section 2 dense input list | ant-farm-cfp8 |
| Clarity | F11 | GUARD block terminology mismatch | ant-farm-cfp8 |
| Clarity | F12 | queen-state.md placeholder inconsistency | ant-farm-glzg |
| Clarity | F13 | Transition Gate missing state file path | ant-farm-bva6 |
| Clarity | F14 | Tilde vs backtick fences | ant-farm-cfp8 |
| Clarity | F15 | Big Head section hierarchy | ant-farm-cfp8 |
| Clarity | F16 | Checklists lack inline cross-references | ant-farm-bva6 |
| Edge Cases | F1 | Polling loop exit without action | ant-farm-60mh |
| Edge Cases | F2 | Stale glob matching in Step 0 | ant-farm-60mh |
| Edge Cases | F3 | Unbounded review round loop | ant-farm-rcdd |
| Edge Cases | F4 | P3 auto-filing no error handling | ant-farm-fkfw |
| Edge Cases | F5 | CCB reconciliation formula gap | ant-farm-cozw |
| Edge Cases | F6 | Pantry guard doesn't cross-check git diff | ant-farm-jegj |
| Edge Cases | F7 | Fix commit range recovery gap | ant-farm-f3t0 |
| Edge Cases | F8 | RULES.md invalid commit range | ant-farm-jegj |
| Correctness | F1 | Termination Rule "directly" ambiguity | ant-farm-s7vu |
| Excellence | F1 | Shell persistence warning buried | ant-farm-j6jq |
| Excellence | F2 | TIMED_OUT inverted sentinel | ant-farm-j6jq |
| Excellence | F3 | Magic numbers undocumented | ant-farm-j6jq |
| Excellence | F4 | Retry count asymmetry | ant-farm-9nws |
| Excellence | F5 | `<IF ROUND 1>` pseudo-syntax | ant-farm-j6jq |
| Excellence | F6 | Fragile grep for Future Work epic | ant-farm-fkfw |
| Excellence | F7 | Big Head escalation unspecified | ant-farm-ppey |
| Excellence | F8 | queen-state.md placeholder syntax | ant-farm-glzg |
| Excellence | F9 | Nitpicker no fallback for missing brief | ant-farm-ppey |
| Excellence | F10 | queen-state.md creation not in Step 0 | ant-farm-ch3m |
| Excellence | F11 | CCB Check 7 O(N) scan | ant-farm-ot9d |
| Excellence | F12 | Pantry Section 3 underspecified | ant-farm-ppey |

**All 37 findings accounted for. 0 findings excluded.**

---

## Priority Breakdown

- **P1 (blocking)**: 0 beads
- **P2 (important)**: 3 beads
  - ant-farm-60mh: Stale glob matching in Big Head (multi-round hazard)
  - ant-farm-4l0t: PARTIAL verdict missing from summary table
  - ant-farm-rcdd: Unbounded review round loop
- **P3 (polish)**: 15 beads

Priority calibration note: 3 P2 findings is appropriate. The stale glob match (ant-farm-60mh) is the most operationally dangerous -- in any multi-round session it would cause silent wrong-round consolidation. The PARTIAL verdict gap (ant-farm-4l0t) could cause Pest Control to misclassify intermediate results. The unbounded loop (ant-farm-rcdd) is a resource consumption risk. All other findings are genuine P3 polish items with no immediate operational impact.

---

## Verdict

**PASS WITH ISSUES**

The orchestration templates are well-structured with clear ownership boundaries, correct round-aware logic across all 7 files, and all 11 acceptance criteria fully met (per the correctness review). The implementation is solid for first-run scenarios.

The three P2 findings all relate to multi-round session handling, which is the new critical path introduced by this implementation:
1. **Stale glob matching** (ant-farm-60mh) is the highest-risk item -- it would cause silent wrong-data consolidation in any session that reaches round 2.
2. **Missing PARTIAL verdict** (ant-farm-4l0t) could cause Pest Control to misinterpret checkpoint results.
3. **Unbounded review loop** (ant-farm-rcdd) has no safety cap for degenerate cases.

The 15 P3 findings are polish items: shell code quality, documentation formatting, cross-references, and failure path completeness. None would cause runtime failures.

**Recommendation**: Fix the 3 P2 issues before running multi-round sessions in production. The P3 items can be addressed in a subsequent cleanup pass.

# Consolidated Review Report

**Review round**: 1 (reduced: 2 of 4 reviewers)
**Timestamp**: 20260222-143758
**Consolidator**: Big Head

---

## Read Confirmation

| Report | File | Findings | Severity Breakdown |
|--------|------|----------|--------------------|
| Correctness | correctness-review-20260222-143758.md | 4 | P2: 1, P3: 3 |
| Edge Cases | edge-cases-review-20260222-143758.md | 9 | P2: 4, P3: 5 |
| Clarity | (not spawned) | -- | -- |
| Excellence | (not spawned) | -- | -- |
| **Total raw findings** | | **13** | **P2: 5, P3: 8** |

---

## Root Cause Groups

### RC-1: Failure artifact not written to disk on failure paths [P2]

**Root cause**: Failure paths in the Big Head workflow describe failure artifacts in LLM narrative prose only -- the actual bash script blocks that execute on failure exit without writing any artifact. This means downstream consumers (Queen, Pest Control) find no file at the expected output path.

**Affected surfaces**:
- `orchestration/templates/reviews.md:L586-589` -- polling timeout `exit 1` writes no artifact (Edge Cases F2)
- `orchestration/templates/big-head-skeleton.md:L91-99` -- failure artifact instruction uses `{CONSOLIDATED_OUTPUT_PATH}` placeholder in narrative prose, not in executable code (Edge Cases F5)
- `orchestration/templates/reviews.md:L765-773` -- Pest Control timeout escalation has no failure artifact write instruction at all (Edge Cases F6)

**Merge rationale**: All three findings share the same design flaw -- failure artifact creation is described as an LLM-level instruction rather than being embedded in the executable bash code blocks. The underlying pattern is: on failure, script exits but no written record is produced for downstream consumption. F2 (no artifact on polling timeout), F5 (placeholder in narrative not code), and F6 (no artifact on Pest Control timeout) are three instances of the same gap in the same workflow.

**Suggested fix**: For every failure path (polling timeout, Pest Control timeout), write the failure artifact inside the bash script block before `exit 1`, using a shell variable for the output path set at script start. Example:
```bash
cat > "$CONSOLIDATED_OUTPUT_PATH" << 'EOF'
# Big Head Consolidation -- BLOCKED
**Status**: FAILED -- [reason]
EOF
exit 1
```

**Cross-session dedup**:
- `ant-farm-ppey` (P3, open) covers "Incomplete failure paths in agent protocols: Big Head escalation" -- partial overlap but that bead is broader (covers Nitpicker and Pantry too) and is P3. This finding is more specific and targets the concrete bash-level implementation gap. File as new bead.
- `ant-farm-10ff` (P3, open) covers failure artifact timestamp coexistence -- different concern (naming, not absence). No overlap.

---

### RC-2: No error handling for bd commands in bead-filing workflow [P2]

**Root cause**: External `bd` command invocations in the bead-filing workflow have no exit-code checking, no retry logic, and no abort-on-failure behavior. In the multi-Queen production environment (documented lock contention), this leads to silent corruption or duplication.

**Affected surfaces**:
- `/tmp/bead-desc.md` hardcoded path -- concurrent Big Head sessions write to the same file, causing silent content corruption (Edge Cases F3; files: `agents/big-head.md:L23`, `orchestration/templates/reviews.md:L794`, `orchestration/templates/reviews.md:L836`)
- `bd list --status=open` for dedup check -- no exit-code check means lock failure silently produces empty output, so dedup is skipped and duplicates get filed (Edge Cases F4; files: `agents/big-head.md:L22`, `orchestration/templates/reviews.md:L679`)

**Merge rationale**: Both F3 and F4 stem from the same pattern: `bd` commands are invoked assuming success in a concurrency-hostile environment. F3 is about the write side (temp file collision during `bd create`), F4 is about the read side (`bd list` failure before filing). Same root cause: no concurrency safety in the bead-filing pipeline.

**Suggested fix**:
- F3: Use session-specific temp file names: `/tmp/bead-desc-{SESSION_SUFFIX}-$$.md`
- F4: Check exit code of `bd list` and abort filing if it fails:
  ```bash
  if ! bd list --status=open -n 0 > /tmp/open-beads.txt 2>&1; then
    echo "ERROR: bd list failed. Aborting bead filing."
    exit 1
  fi
  ```

**Cross-session dedup**:
- `ant-farm-p0m` (P3, open) covers "big-head.md bd create has no error handling for CLI failures" -- overlaps with F4's concern about `bd` command failures, but `ant-farm-p0m` is about `bd create` specifically, while F4 is about `bd list` and F3 is about temp file collision. The root cause is broader than `ant-farm-p0m`. File as new bead that subsumes the `bd` error handling gap.

---

### RC-3: agents/big-head.md step ordering contradicts big-head-skeleton.md [P2]

**Root cause**: When the dedup and `--body-file` instructions were added to `agents/big-head.md` (ant-farm-asdl.3), two new steps were inserted and existing steps renumbered, but the step ORDER was not updated to match the skeleton's required sequence. The result is that `big-head.md` says "file issues" (step 7) BEFORE "write consolidated report" (step 8), while the skeleton requires writing the report first, sending to Pest Control, and filing only after PASS verdict.

**Affected surfaces**:
- `agents/big-head.md:L22-24` -- steps 6 (dedup), 7 (file issues), 8 (write report) are in wrong order (Correctness F2)

**Merge rationale**: Single finding from one reviewer. No merge needed -- standalone root cause.

**Suggested fix**: Reorder `agents/big-head.md` "When consolidating" steps:
1. Read reports
2. Build findings inventory
3. Group by root cause
4. Merge into issues
5. Track severity conflicts
6. Deduplicate against existing beads
7. Write consolidated report
8. Send to Pest Control, await verdict, THEN file issues via `bd create --body-file` (PASS branch only)

**Cross-session dedup**: No existing bead matches this specific step-ordering issue. File as new bead.

---

### RC-4: Fragile numeric cross-references between template files [P3]

**Root cause**: Cross-file references use step numbers instead of step names, making them fragile to renumbering.

**Affected surfaces**:
- `orchestration/templates/pantry.md:L318` -- references "big-head-skeleton.md step 10" by number (Correctness F1)
- `orchestration/templates/big-head-skeleton.md:L120, L153` -- references "step 7" by number (Correctness F3, advisory/pre-existing)
- `orchestration/templates/reviews.md:L674` vs `orchestration/templates/big-head-skeleton.md` -- "Step 2.5" vs integer step 7 for same dedup step (Correctness F4)

**Merge rationale**: C1, C3, and C4 all describe the same pattern: numeric step references across files that break on renumbering. C3 is partially pre-existing (the epic ID capture gap is a separate sub-issue, not merged here). C4 is specifically about the reviews.md/skeleton naming inconsistency. All three stem from the same convention gap: no rule to use step names in cross-file references.

**Suggested fix**: Adopt a convention of referencing steps by name rather than number in cross-file references. For example: "see big-head-skeleton.md 'Await Pest Control verdict' step" instead of "step 10".

**Cross-session dedup**:
- `ant-farm-07ai` (P3, open) -- "Cross-file step numbering mismatch between reviews.md and big-head-skeleton.md" -- this is an EXACT MATCH for Correctness F4. Skip filing for F4.
- The broader fragile-numeric-reference issue (C1, C3) is not covered by `ant-farm-07ai` which is specifically about the mismatch, not about the fragility pattern. File a new bead for the fragile reference pattern, noting ant-farm-07ai as related.

---

### RC-5: Polling loop off-by-one timeout [P3]

**Root cause**: The polling loop in reviews.md can run up to 32 seconds wall-clock time while the comment says "30 seconds maximum".

**Affected surfaces**:
- `orchestration/templates/reviews.md:L565-584` -- loop condition allows one extra iteration (Edge Cases F1)

**Merge rationale**: Single finding, standalone.

**Suggested fix**: Adjust loop boundary or document the distinction between polling iterations and wall-clock time.

**Cross-session dedup**:
- `ant-farm-1pa0` (P3, open) -- "Big Head polling loop: single-invocation constraint under-documented and timeout may be too short" -- overlaps with this finding's concern about the polling loop timeout behavior. SKIP filing -- covered by existing bead.

---

### RC-6: Pantry reads dirt-pusher-skeleton.md without existence check [P3]

**Root cause**: Step 3 of Pantry Section 1 reads a template file with no fallback or fail-fast if the file is missing.

**Affected surfaces**:
- `orchestration/templates/pantry.md:L143` (Edge Cases F7)

**Merge rationale**: Single finding, standalone. The Pantry has fail-fast patterns for other conditions but not for template file existence.

**Suggested fix**: Add a file existence check before reading, consistent with existing Condition 1/2/3 fail-fast pattern.

**Cross-session dedup**: No existing bead matches. File as new bead.

---

### RC-7: [OUT-OF-SCOPE] tag has no enforcement in Big Head severity merging [P3]

**Root cause**: Round 2+ reviewer instructions define an `[OUT-OF-SCOPE]` tag, but Big Head treats all findings identically for dedup and root-cause grouping. Out-of-scope P3 findings can inflate a root cause group's priority if merged with in-scope findings.

**Affected surfaces**:
- `orchestration/templates/reviews.md:L199-208` (Edge Cases F8)

**Merge rationale**: Single finding, standalone. Conceptually distinct from other findings.

**Suggested fix**: Add instruction to Big Head: when merging findings, only use in-scope severity levels for priority calculation. OUT-OF-SCOPE findings contribute affected surfaces but not severity.

**Cross-session dedup**: No existing bead matches. File as new bead.

---

## Deduplication Log

| Raw Finding | Source | Consolidated RC | Merge Action |
|-------------|--------|-----------------|--------------|
| Correctness F1 (pantry.md fragile step ref) | Correctness | RC-4 | Merged -- same pattern as C3, C4: numeric cross-file references |
| Correctness F2 (big-head.md step order) | Correctness | RC-3 | Standalone -- unique root cause |
| Correctness F3 (skeleton step 7 refs + epic ID) | Correctness | RC-4 | Merged -- numeric cross-file references; epic ID sub-issue noted as pre-existing advisory |
| Correctness F4 (Step 2.5 vs integer 7) | Correctness | RC-4 | Merged -- same naming inconsistency pattern; SKIP FILING (covered by ant-farm-07ai) |
| Edge Cases F1 (polling off-by-one) | Edge Cases | RC-5 | Standalone; SKIP FILING (covered by ant-farm-1pa0) |
| Edge Cases F2 (polling exit no artifact) | Edge Cases | RC-1 | Merged -- failure artifact not in bash code |
| Edge Cases F3 (temp file collision) | Edge Cases | RC-2 | Merged -- bd command concurrency safety |
| Edge Cases F4 (bd list no error handling) | Edge Cases | RC-2 | Merged -- bd command concurrency safety |
| Edge Cases F5 (unfilled placeholder in failure prose) | Edge Cases | RC-1 | Merged -- failure artifact not in bash code |
| Edge Cases F6 (Pest Control timeout no artifact) | Edge Cases | RC-1 | Merged -- failure artifact not written on failure path |
| Edge Cases F7 (dirt-pusher-skeleton no check) | Edge Cases | RC-6 | Standalone |
| Edge Cases F8 (OUT-OF-SCOPE no enforcement) | Edge Cases | RC-7 | Standalone |
| Edge Cases F9 (P3 auto-filing ID capture gap) | Edge Cases | -- | Excluded: pre-existing, not introduced in current commit range (asdl.*). No bead filed. Cross-reference: flagged by both correctness reviewer (F3 advisory, epic ID sub-issue) and edge-cases reviewer (F9) as pre-existing. |

**Dedup summary**: 13 raw findings consolidated to 7 root cause groups. 2 groups (RC-5, partial RC-4) skipped for filing due to existing bead coverage. 1 finding (Edge Cases F9) excluded as pre-existing.

---

## Severity Conflicts

No severity conflicts detected. All merged findings within each root cause group had severities within 1 level of each other:
- RC-1: Edge Cases F2 (P2), F5 (P2), F6 (P3) -- max delta = 1 level, within threshold
- RC-2: Edge Cases F3 (P2), F4 (P2) -- same severity
- RC-4: Correctness F1 (P3), F3 (P3), F4 (P3) -- same severity

No cross-reviewer severity conflicts requiring calibration.

---

## Cross-Session Dedup Log

| Finding/RC | Existing Bead | Decision |
|------------|---------------|----------|
| RC-4 / Correctness F4 | ant-farm-07ai (P3) "Cross-file step numbering mismatch" | SKIP -- exact match |
| RC-5 / Edge Cases F1 | ant-farm-1pa0 (P3) "Polling loop timeout" | SKIP -- covered by existing bead |
| RC-2 / Edge Cases F4 | ant-farm-p0m (P3) "bd create no error handling" | FILE NEW -- ant-farm-p0m covers bd create only; RC-2 covers broader bd command concurrency (bd list + temp file collision) |
| RC-1 / Edge Cases F2,F5,F6 | ant-farm-ppey (P3) "Incomplete failure paths" | FILE NEW -- ant-farm-ppey is broader (3 agents); RC-1 is specific to bash-level artifact implementation |

---

## Beads Filed

DMVDC: PASS (both reports). CCB: PASS (after amendment). All beads filed.

| RC | Priority | Bead ID | Title |
|----|----------|---------|-------|
| RC-1 | P2 | ant-farm-84qf | Failure artifact writes missing from bash script blocks on Big Head failure paths |
| RC-2 | P2 | ant-farm-igxq | No concurrency safety in Big Head bead-filing workflow (temp file collision + bd list error handling) |
| RC-3 | P2 | ant-farm-7kei | agents/big-head.md step ordering places bead filing before Pest Control checkpoint |
| RC-4 | P3 | ant-farm-9d4e | Fragile numeric step references in cross-file template links |
| RC-6 | P3 | ant-farm-m47x | Pantry reads dirt-pusher-skeleton.md without file existence check |
| RC-7 | P3 | ant-farm-2sjc | [OUT-OF-SCOPE] tag has no enforcement in Big Head severity merging logic |

Skipped (existing coverage):
- RC-5 (polling off-by-one) -- covered by ant-farm-1pa0
- RC-4/F4 (Step 2.5 vs integer) -- covered by ant-farm-07ai

---

## Priority Breakdown

- P1: 0
- P2: 3 (RC-1: ant-farm-84qf, RC-2: ant-farm-igxq, RC-3: ant-farm-7kei)
- P3: 3 (RC-4: ant-farm-9d4e, RC-6: ant-farm-m47x, RC-7: ant-farm-2sjc)
- Skipped: 2 (existing coverage)
- Excluded (pre-existing): 1 (Edge Cases F9)
- Total beads filed: 6

---

## Overall Verdict

**Score**: 7/10
**Verdict**: PASS WITH ISSUES

Three P2 issues identified: (1) failure artifacts not written in executable code on failure paths, (2) no concurrency safety in the bead-filing pipeline, (3) agent definition step ordering contradicts the skeleton. None are P1 blockers -- the skeleton (which agents actually execute) has the correct ordering, and the concurrency issues require multi-Queen setups to trigger. Three P3 advisory findings for fragile references, missing file checks, and tag enforcement gaps. All acceptance criteria for ant-farm-asdl.1 through asdl.5 pass their stated criteria.

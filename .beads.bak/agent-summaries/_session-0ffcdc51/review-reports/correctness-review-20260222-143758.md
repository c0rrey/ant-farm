# Report: Correctness Review

**Scope**: agents/big-head.md, orchestration/templates/big-head-skeleton.md, orchestration/templates/pantry.md, orchestration/templates/reviews.md
**Reviewer**: Correctness reviewer (code-reviewer)
**Commit range**: 56c3795^..7359e9c
**Review round**: 1

---

## Findings Catalog

### Finding 1: pantry.md references "big-head-skeleton.md step 10" but the canonical bead-filing template is in step 10 only under the PASS branch sub-bullet

- **File(s)**: `orchestration/templates/pantry.md:318`
- **Severity**: P3
- **Category**: correctness
- **Description**: The pantry.md line added by ant-farm-asdl.4 reads: `"see big-head-skeleton.md step 10 for canonical example"`. Step 10 in the skeleton is the "Await Pest Control verdict" step, whose PASS branch contains the canonical `--body-file` template. The reference is technically accurate but requires the reader to navigate into a sub-bullet of a sub-bullet. If the step numbering in the skeleton ever changes (e.g., another step is inserted before step 10), this cross-reference will silently point to the wrong step. Currently step 10 is the correct step, so this is not a functional bug today — it is a fragile cross-reference. Severity P3 because the current content is correct; it becomes a misreference only if the skeleton is reorganized.
- **Suggested fix**: Change to a more stable reference: `"see big-head-skeleton.md 'Await Pest Control verdict' step (PASS branch) for canonical example"` — referencing the step by name rather than number.
- **Cross-reference**: None — this is a correctness concern, not clarity. The name-based reference is the fix.

---

### Finding 2: agents/big-head.md step ordering does not match the skeleton's step ordering — "Write consolidated report" (step 8 in big-head.md) comes after "File issues" (step 7 in big-head.md), but in the skeleton the summary is written BEFORE beads are filed

- **File(s)**: `agents/big-head.md:22-24`, `orchestration/templates/big-head-skeleton.md:106-116`
- **Severity**: P2
- **Category**: correctness
- **Description**: In `agents/big-head.md` (the agent definition), the "When consolidating" steps instruct:
  - Step 6: dedup against existing beads
  - Step 7: file issues via `bd create --body-file`
  - Step 8: write the consolidated report

  But in `big-head-skeleton.md` (the actual spawn prompt), the skeleton instructs:
  - Step 7: cross-session dedup
  - Step 8: write consolidated summary
  - Step 9: send to Pest Control and await verdict
  - Step 10: ONLY THEN file beads (after Pest Control PASS)

  The agent definition in `big-head.md` places "file issues" (step 7) BEFORE "write consolidated report" (step 8), which contradicts the skeleton. In the skeleton, the consolidated report must be written FIRST (step 8), sent to Pest Control (step 9), and beads are filed only after receiving a PASS verdict (step 10). An agent following `big-head.md` in isolation would file beads before the Pest Control checkpoint, bypassing the critical gate that prevents premature bead creation.

  The task ant-farm-asdl.3 added steps 6 and 7 to `big-head.md` and renumbered step 7→8, but did not reorder to match the skeleton's sequence. The acceptance criteria for ant-farm-asdl.3 only checked that dedup and --body-file references were present and steps were sequential — not that the ORDER matched the skeleton's validated-first-then-file sequence.

  This is a P2 because an agent following `big-head.md` alone would bypass Pest Control validation before filing beads. The skeleton is the authoritative spawn prompt and overrides the agent definition at runtime, so real Big Head instances follow the skeleton; but `big-head.md` is read during session planning and by humans reviewing the design, making this a correctness problem in the documentation that could mislead.
- **Suggested fix**: Reorder `big-head.md` steps to match the skeleton's sequence:
  1. Read reports
  2. Build findings inventory
  3. Group by root cause
  4. Merge into issues
  5. Track severity conflicts
  6. Deduplicate against existing beads (new from asdl.3)
  7. Write consolidated report
  8. Send to Pest Control and await verdict — THEN file issues via `bd create --body-file` (PASS branch)

  The current steps 7 ("File issues") and 8 ("Write consolidated report") must be reordered so filing comes AFTER report writing + Pest Control confirmation.

---

### Finding 3: big-head-skeleton.md step 10 references "step 7" for dedup decisions, but dedup is step 7 only in the new numbering — both forward and backward references must be checked

- **File(s)**: `orchestration/templates/big-head-skeleton.md:120`, `orchestration/templates/big-head-skeleton.md:153`
- **Severity**: P3
- **Category**: correctness
- **Description**: Step 10 (PASS branch) says "skip any marked as duplicates in step 7". Step 11 (P3 auto-filing) also says "skip any marked as duplicates in step 7". Both references are correct: step 7 is indeed the cross-session dedup step added by asdl.1. Verification check per acceptance criterion V5 of ant-farm-asdl.5: the references resolve correctly after renumbering. No issue here.

  However, the P3 auto-filing step (step 11) in `big-head-skeleton.md` references `<epic-id>` without specifying where the epic ID comes from. The step says "Find or create the epic" using `bd list | grep` or `bd epic create`, but does not show how to capture the epic ID from those commands for use in the subsequent `bd dep add` command. An agent would need to parse the output of `bd list` or `bd epic create` to extract the ID. This is incomplete operational guidance. Severity P3 — it does not break anything because an agent following these instructions would typically know to parse the ID, and this was pre-existing before the commit range.
- **Suggested fix**: Show explicit ID capture: `EPIC_ID=$(bd epic create ... | grep -oP 'ant-farm-\w+')` or equivalent, then use `$EPIC_ID` in `bd dep add`. This pre-exists the current changes, so it is advisory only.
- **Cross-reference**: This is pre-existing, not introduced in the asdl.* commits. Flag only for completeness.

---

### Finding 4: reviews.md "Step 2.5" is not numbered with a decimal in the skeleton, creating a naming inconsistency between the two files

- **File(s)**: `orchestration/templates/reviews.md:674`, `orchestration/templates/big-head-skeleton.md:106`
- **Severity**: P3
- **Category**: correctness
- **Description**: In `reviews.md`, the new dedup step is labeled "### Step 2.5: Deduplicate Against Existing Beads". In `big-head-skeleton.md`, the same step is "7. **Cross-session dedup**" (an integer step, not a decimal). The two files use different labeling conventions for the same logical step. This is a minor cross-file inconsistency — the dedup step is step 7 in the skeleton (which agents use) and "Step 2.5" in reviews.md (which the Queen reads). An agent following the skeleton will correctly do dedup as step 7; the Queen reading reviews.md will see it as "Step 2.5". These are different audiences, so the inconsistency is mild. No functional impact. Severity P3.
- **Suggested fix**: Either align the naming (call it "Step 7" in reviews.md Big Head Consolidation Protocol to match the skeleton, or add a note in reviews.md that this corresponds to step 7 in the skeleton), or document that reviews.md uses conceptual step numbers that differ from skeleton step numbers. Neither is a blocker.

---

## Acceptance Criteria Verification

### ant-farm-asdl.1: Add cross-session dedup step and description template to big-head-skeleton.md

- [x] No bare `bd create` command remains — every instance includes `--body-file`. Verified: `bd create --type=bug --priority=<P> --title="<title>" --body-file /tmp/bead-desc.md` (line 145) and `bd create --type=bug --priority=3 --title="<title>" --body-file /tmp/bead-desc.md` (line 166).
- [x] Description template in PASS branch contains all 5 sections: `## Root Cause`, `## Affected Surfaces`, `## Fix`, `## Changes Needed`, `## Acceptance Criteria` (lines 123-142).
- [x] Cross-session dedup step exists before write-summary step, containing `bd list --status=open` and `bd search` (step 7, lines 106-114).
- [x] Output requirements list includes "Cross-session dedup log" (line 177).
- [x] Step numbers are sequential: 1-11 with no gaps. Cross-references to "step 7" at lines 120 and 153 resolve correctly to the dedup step.

**Verdict**: ALL CRITERIA MET.

---

### ant-farm-asdl.2: Add cross-session dedup and description template to reviews.md Big Head Consolidation Protocol

- [x] "Step 2.5: Deduplicate Against Existing Beads" exists between Step 2 and Step 3, containing `bd list --status=open` (lines 674-689) and `bd search` (line 683).
- [x] No bare `bd create` commands in the bead filing section — all instances have `--body-file` (lines 813, 847).
- [x] Description template in bead filing section contains all 5 sections: Root Cause, Affected Surfaces, Fix, Changes Needed, Acceptance Criteria (lines 795-811).
- [x] P3 auto-filing section uses `--body-file` with Root Cause, Affected Surfaces, and Acceptance Criteria (lines 833-850).

**Verdict**: ALL CRITERIA MET.

---

### ant-farm-asdl.3: Update agents/big-head.md with dedup instruction and --body-file reference

- [x] `agents/big-head.md` contains a dedup instruction referencing `bd list --status=open` before the filing step (line 22, step 6).
- [x] `agents/big-head.md` references `--body-file` in the filing instruction (line 23, step 7).
- [x] Steps in "When consolidating:" list are sequentially numbered 1-8 (steps 1-8, verified).
- [x] Old step 7 ("Write the consolidated report") is renumbered to step 8 with content unchanged (line 24).

**Verdict**: ALL CRITERIA MET per the literal acceptance criteria. However, see Finding 2 above: the step ORDER in `big-head.md` is incorrect relative to the skeleton's required sequence (file-after-Pest-Control-PASS vs. file-before-writing-report).

---

### ant-farm-asdl.4: Update deprecated pantry.md Section 2 bead filing references

- [x] Lines 318-319 of pantry.md no longer contain a bare `bd create --title` command. Verified: replaced with prose referencing `--body-file` pattern.
- [x] Replacement text references `big-head-skeleton.md` as canonical source (line 318: "see big-head-skeleton.md step 10 for canonical example").
- [x] Replacement text mentions all 5 required description fields (line 319: "root cause with file:line refs, affected surfaces, fix, changes needed, acceptance criteria").
- [x] Replacement text includes the dedup instruction (line 320: "Before filing: run `bd list --status=open -n 0 --short` to check for existing duplicates").

**Verdict**: ALL CRITERIA MET per the literal acceptance criteria. See Finding 1 (fragile step number reference) as a P3 advisory.

---

### ant-farm-asdl.5: Verify all Big Head template changes are consistent and complete

- [x] V1 (no bare bd create): Passes — all `bd create` commands include `--body-file`.
- [x] V2 (dedup in both files): Passes — `bd list --status=open` appears in both `big-head-skeleton.md` and `reviews.md`.
- [x] V3 (5 description sections in skeleton): Passes — all 5 sections present.
- [x] V4 (build-review-prompts.sh extraction): Extracts content below `---` separator; all asdl.1 changes are below line 65 (separator is at line 65); compatible.
- [x] V5 (step numbering sequential): Steps 1-11 in skeleton, no gaps. Cross-references to "step 7" are correct.

**Verdict**: ALL CRITERIA MET per the acceptance criteria as written. Note that V5 only checked for sequential numbering and cross-references resolving — it did not check that the order in `big-head.md` matches the skeleton's required sequence (see Finding 2).

---

## Preliminary Groupings

### Group A: Step ordering mismatch between agent definition and spawn prompt (root cause: incomplete reorder during asdl.3 insertion)

- Finding 2 — `agents/big-head.md` step 7 ("File issues") placed before step 8 ("Write consolidated report"), contradicting the skeleton's sequence where filing happens only after Pest Control PASS.

**Suggested combined fix**: Reorder `agents/big-head.md` steps so filing happens after writing the report and receiving Pest Control verdict (matches the skeleton's steps 8→9→10 sequence).

### Group B: Fragile cross-references using step numbers instead of step names (root cause: numeric step references that do not survive renumbering)

- Finding 1 — `pantry.md:318` references "big-head-skeleton.md step 10" by number, which breaks if the skeleton is renumbered.
- Finding 3 (partial) — `big-head-skeleton.md:120` and `:153` reference "step 7" by number; currently correct but fragile.

**Suggested combined fix**: Use step names instead of numbers in cross-file references (e.g., "the cross-session dedup step" rather than "step 7").

### Group C: Minor cross-file naming inconsistency (cosmetic)

- Finding 4 — "Step 2.5" in reviews.md vs. integer step 7 in skeleton for the same dedup step.

---

## Summary Statistics

- Total findings: 4
- By severity: P1: 0, P2: 1, P3: 3
- Preliminary groups: 3

---

## Cross-Review Messages

### Sent

- To edge-cases-reviewer: "Pre-existing gap in skeleton step 11 — `bd dep add <epic-id>` has no variable capture example showing how the epic ID is extracted." — Action: flagged as pre-existing, not introduced in asdl.* commits; deferred ownership to edge-cases-reviewer.
- To edge-cases-reviewer: "Replied that reviews.md:L207-208 [OUT-OF-SCOPE] priority merging behavior is pre-existing and not covered by any asdl.* acceptance criteria; not in correctness scope for this review. Deferred ownership of that finding to edge-cases-reviewer."

### Received

- From edge-cases-reviewer: "Severity merging logic for [OUT-OF-SCOPE] findings in round 2+ (reviews.md:L199-208) may violate intended behavior — out-of-scope P3s could inflate combined priority when merged with in-scope findings. Checked whether any acceptance criteria address this." — Action taken: Verified reviews.md:L207-208 pre-dates asdl.* commits and is not covered by any of the 5 task acceptance criteria. Confirmed this is a pre-existing design gap; replied to edge-cases-reviewer to take ownership if they choose to report it.

### Deferred Items

None.

---

## Coverage Log

| File | Status | Evidence |
|------|--------|----------|
| `agents/big-head.md` | Findings: #2 (step order mismatch) | 37 lines, 8 steps in "When consolidating" block reviewed; step sequence checked against skeleton |
| `orchestration/templates/big-head-skeleton.md` | Findings: #3 (advisory — pre-existing epic ID capture gap, not introduced here) | Full file read; 179 lines; steps 1-11 verified sequential; all bd create commands checked; cross-references at L120, L153 verified |
| `orchestration/templates/pantry.md` | Findings: #1 (fragile step-number cross-reference) | Section 2 reviewed (deprecated); lines 313-322 checked against acceptance criteria; all 4 bullets verified |
| `orchestration/templates/reviews.md` | Findings: #4 (Step 2.5 vs. integer step naming) | Full file read; 988 lines; Big Head Consolidation Protocol section reviewed; Step 2.5 insertion (lines 674-689) verified; bead filing section (lines 791-850) verified; all bd create commands checked for --body-file |

---

## Overall Assessment

**Score**: 7.5/10
**Verdict**: PASS WITH ISSUES

All 5 acceptance criteria sets pass their stated criteria. The changes achieve their primary goals: cross-session dedup is now present in both skeleton and reviews.md, and `--body-file` is used consistently. One substantive correctness issue (P2): the step ordering in `agents/big-head.md` places bead filing before Pest Control checkpoint confirmation, contradicting the spawn prompt's validated sequence. This does not affect runtime behavior (the skeleton overrides the agent definition in practice), but is an incorrect documentation of the workflow that could mislead future editors or agents reading only the agent definition. Three P3 advisory findings (fragile step-number cross-references, naming inconsistency) do not block shipping.

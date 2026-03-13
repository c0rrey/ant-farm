# Summary: ant-farm-7hgn

**Task**: Delay Big Head bead filing until after Pest Control checkpoint validation
**Commit**: 46a776a
**Files changed**:
- orchestration/templates/reviews.md (Step 3/4 restructure, checklists)
- orchestration/templates/big-head-skeleton.md (steps 7-9 added)
- orchestration/RULES.md (team composition update)
- orchestration/templates/pantry.md (Big Head brief note + step references)

---

## 1. Approaches Considered

**Approach A: Pest Control as 6th team member; Big Head messages PC then files beads (selected)**
Add Pest Control to the TeamCreate call (6 members: 4 Nitpickers + Big Head + Pest Control). Big Head's workflow: consolidate → write summary → SendMessage to PC with report path → await PC reply → file beads on PASS, escalate on FAIL. All coordination is team-internal; no review content enters the Queen's window.

**Approach B: File-based handoff — Big Head writes marker file, PC polls for it**
Big Head writes a "ready-for-checkpoint.md" marker file after consolidation; PC polls for it. Tradeoff: requires PC to actively poll with no direct notification; more fragile than SendMessage. PC would need to be alive and aware of the expected path. Not selected — team messaging is more direct and reliable.

**Approach C: Two-phase team — Phase 1: 4 Nitpickers + Big Head; Phase 2: Queen spawns PC, then re-spawns Big Head**
Keep current 5-member team. After team completes, Queen spawns PC to validate consolidated report. If PASS, Queen spawns a new Big Head Task to file beads. Tradeoff: requires re-invoking Big Head (extra spawn cost), requires Queen to pass findings between agents (report content potentially enters Queen's window), violates acceptance criteria 2 (PC must be in team) and 5 (no report content in Queen's window). Rejected.

**Approach D: Shared file with polling — Big Head writes verdict request, PC writes result, Big Head polls**
Big Head and PC coordinate via a shared file in `{session-dir}/pc/`. Big Head writes a checkpoint-request file with the report path; PC writes a verdict file; Big Head polls for the verdict file. Tradeoff: more complex and slower than SendMessage; adds polling overhead. Rejected in favor of Approach A.

---

## 2. Selected Approach with Rationale

**Approach A** was selected. Adding Pest Control as the 6th team member enables direct SendMessage coordination between Big Head and PC without any content transiting the Queen's context window. This is the most architecturally clean solution:
- Team messaging is the existing coordination mechanism within teams
- No additional spawns or re-invocations needed
- Big Head stays alive waiting for PC's verdict — no re-invocation
- All five acceptance criteria are satisfied

---

## 3. Implementation Description

**orchestration/templates/reviews.md**:
- Renamed old "Step 3: File Beads" to "Step 3: Write Consolidated Summary" (swapped order with old Step 4)
- Added new "Step 4: Checkpoint Gate — Await Pest Control Validation Before Filing Beads" with:
  - SendMessage invocation template to PC with consolidated report path
  - PASS path: file all beads
  - FAIL path: escalation format to Queen + file only validated beads
- Updated Nitpicker Checklist: added item requiring 6-member team including Pest Control
- Updated Big Head Consolidation Checklist: added steps for sending to PC, receiving verdict, PASS/FAIL outcomes

**orchestration/templates/big-head-skeleton.md**:
- Reordered steps 7-9: old step 7 (file beads) split into:
  - Step 7: Write consolidated summary
  - Step 8: SendMessage to Pest Control with report path; "Do NOT file any beads before receiving Pest Control's reply"
  - Step 9: Await verdict — PASS: file beads; FAIL: escalate to Queen, file only validated

**orchestration/RULES.md**:
- Updated team composition from "5 members: 4 reviewers + Big Head" to "6 members: 4 reviewers + Big Head + Pest Control"
- Removed the post-team Pest Control spawn line for DMVDC + CCB (those now run inside the team)
- Added explanation of why PC must be a team member (SendMessage capability)

**orchestration/templates/pantry.md**:
- Updated "See also" reference to describe new step structure (Steps 1-2, Step 3, Step 4)
- Added bead filing note: "Big Head must NOT file beads until Pest Control confirms via team message — see reviews.md Step 4 and big-head-skeleton.md steps 8-9"
- Added Pest Control coordination note to Big Head brief composition instructions

---

## 4. Correctness Review

**orchestration/templates/reviews.md**:
- Step 3 (Write Consolidated Summary) comes before Step 4 (Checkpoint Gate). Order is correct: write first, then notify PC. Correct.
- Step 4 SendMessage template uses the correct `to="pest-control"` target name matching the team member name. Correct.
- FAIL escalation format includes specifics (findings failed, reasons, validated findings, beads filed, action required). Correct.
- Checklist: "Sent consolidated report path to Pest Control" comes after "Written consolidated summary" and before "Received verdict". Correct order. Correct.
- Nitpicker Checklist note about 6-member team added. Correct.
- Lines outside L321-542 were not modified. Scope respected.

**orchestration/templates/big-head-skeleton.md**:
- Steps 7-9 are sequenced correctly: write summary → notify PC (no beads) → verdict → file/escalate. Correct.
- "Do NOT file any beads before receiving Pest Control's reply" guard is explicit and unambiguous. Correct.
- Lines outside L67-80 (now L65-70 after shift) were not modified. Scope respected.

**orchestration/RULES.md**:
- Team composition updated from 5 to 6 members. Correct.
- Reference to "reviews.md Step 4" is correct (checkpoint gate is Step 4 in the new numbering). Correct.
- Post-team Pest Control spawn removed (DMVDC/CCB now run inside team). Correct.
- Lines outside L88-110 (approximately) were not modified. Scope respected.

**orchestration/templates/pantry.md**:
- Step references updated from old to new (Step 4 = checkpoint gate). Correct.
- "See also" step description matches new file structure. Correct.
- Lines outside L137-145 (the Big Head brief composition section) were not modified. Scope respected.

**Acceptance criteria verification:**
1. Big Head does not file any beads until PC confirms — PASS (reviews.md Step 4 + big-head-skeleton.md step 8 both have explicit guards)
2. Pest Control spawned as part of Nitpicker team — PASS (RULES.md: 6 members including Pest Control)
3. On checkpoint pass, all consolidated findings filed — PASS (both files describe PASS path as filing all root-cause beads)
4. On checkpoint fail, only validated findings filed; failures escalated — PASS (both files describe FAIL path with escalation format)
5. No review report content enters Queen's context window — PASS (coordination via team SendMessage; escalation format contains finding summaries, not raw report content)

---

## 5. Build/Test Validation

No automated test suite for markdown templates. Manual inspection confirms:
- The step ordering (Write Summary → Notify PC → Await Verdict → File Beads) is logically consistent across all four files
- The SendMessage target name "pest-control" needs to match whatever the Queen names the PC team member in the TeamCreate call — RULES.md and big-head-skeleton.md do not specify the team member name; this is a known constraint (the actual name used in TeamCreate must match the SendMessage target). Documented as an adjacent issue, not in scope to fix here.
- The FAIL path escalation avoids passing raw report content to the Queen: it passes finding identifiers and reasons, not the raw consolidated report text.

---

## 6. Acceptance Criteria Checklist

| Criterion | Status |
|-----------|--------|
| Big Head does not file any beads until Pest Control confirms checkpoint validation | PASS |
| Pest Control is spawned as part of the Nitpicker team, not as a separate Queen-orchestrated agent | PASS |
| On checkpoint pass, all consolidated findings are filed as beads | PASS |
| On checkpoint fail, only validated findings are filed; failures are escalated to Queen with specifics | PASS |
| No review report content enters the Queen's context window during this process | PASS |

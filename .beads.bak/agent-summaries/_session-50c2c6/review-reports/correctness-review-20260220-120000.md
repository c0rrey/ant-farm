# Report: Correctness Review (Round 2)

**Scope**: orchestration/RULES.md, orchestration/templates/checkpoints.md, orchestration/templates/queen-state.md, orchestration/templates/reviews.md
**Reviewer**: correctness / code-reviewer
**Round**: 2 (fix verification)

---

## Acceptance Criteria Verification

The three fix tasks (ant-farm-60mh, ant-farm-4l0t, ant-farm-rcdd) were retrieved via `bd show`. None had description or acceptance criteria stored in the database beyond their titles — they were filed with title only. The fix commit messages and the round-1 review findings they address serve as the source of truth for acceptance criteria.

### ant-farm-60mh — Big Head Step 0 glob matching can silently consolidate stale reports

Commit `002ee87`. Changes confined to `orchestration/templates/reviews.md`.

The fix replaced `ls ...-review-*.md` wildcard globs in Step 0 bash blocks (lines 412-424) and the polling loop (lines 456-476) with exact `[ -f "<session-dir>/review-reports/<type>-review-<timestamp>.md" ]` checks. It also added `exit 1` after the TIMEOUT echo at line 485.

- [x] Step 0 Round 1 bash block: uses `[ -f ... ]` with exact `<timestamp>` path — no wildcard. PASS.
- [x] Step 0 Round 2+ bash block: uses `[ -f ... ]` with exact `<timestamp>` path — no wildcard. PASS.
- [x] Polling loop variables: replaced `ls ...-*.md | head -1` pattern with `[ -f "<exact-path>" ]` checks. No wildcard glob remaining. PASS.
- [x] `exit 1` added after TIMEOUT echo (reviews.md:485). PASS.
- [x] The `head -1` comment that previously acknowledged multi-file matching is removed. PASS.
- [x] Pantry responsibility note (line 488) retained; text updated to say "exact file paths (with timestamp)." PASS.

**Regression check**: The `<timestamp>` placeholder in the template is still a template placeholder — the Pantry replaces it with the actual timestamp value when writing the Big Head brief. The comment at line 458 ("The Pantry replaces ... with the actual path before delivering this brief") makes the substitution responsibility explicit. The fix correctly shifts responsibility from the polling loop to the Pantry's brief-composition step without breaking the existing Pantry responsibility note. No regression.

**Verdict for ant-farm-60mh**: PASS.

### ant-farm-4l0t — PARTIAL verdict state missing from Verdict Thresholds Summary

Commit `023ee0f`. Changes confined to `orchestration/templates/checkpoints.md`.

The fix made three changes: (1) changed "All checkpoints use three verdict states" to "All checkpoints use the following verdict states" (line 50); (2) added a `**PARTIAL** (DMVDC and CCB only)` definition block at line 59; (3) updated the DMVDC rows in the Checkpoint-Specific Thresholds table from "WARN allows resubmission" to "PARTIAL allows resubmission" and the CCB row to "PARTIAL: fix and re-run."

- [x] "three verdict states" claim removed. PASS.
- [x] PARTIAL defined as a named verdict state. PASS.
- [x] DMVDC table rows now say "PARTIAL allows resubmission; FAIL escalates." PASS.
- [x] CCB table row now says "PARTIAL: fix and re-run; FAIL blocks user presentation." PASS.

**Incomplete fix — residual contradiction (Finding 1 below)**: The `**WARN**` definition block (lines 54-57) still includes `- DMVDC WARN: Partial failures detected. Agent can repair and resubmit.` and its header still reads `(checkpoints: CCO, WWD, DMVDC only)`. The fix added PARTIAL correctly but did not remove or update the DMVDC entry from the WARN block. An agent reading the WARN definition still sees DMVDC listed as a WARN checkpoint with resubmit behavior — directly contradicting the new PARTIAL definition and the updated table. The pre-existing finding (round 1 Finding 5 Problem A) described this as the core ambiguity; the fix addressed the table (Problem B) and added PARTIAL, but left the WARN block's DMVDC entry intact.

**Verdict for ant-farm-4l0t**: PARTIAL (incomplete — residual contradiction at checkpoints.md:54,57 not addressed).

### ant-farm-rcdd — No hard cap on review rounds creates unbounded retry loop risk

Commit `d9201c9`. Changes across three files: `orchestration/RULES.md`, `orchestration/templates/reviews.md`, `orchestration/templates/queen-state.md`.

The fix added escalation cap language in all three files:
- `reviews.md:144`: Escalation cap paragraph added to Termination Rule section.
- `RULES.md:122-126`: "Round cap — escalate after round 4" block added in Step 3c.
- `queen-state.md:35-36`: `Max rounds` and `Escalation cap` fields added to Review Rounds section.

- [x] All three files consistently state the cap triggers after round 4 (not round 3, not round 5). PASS.
- [x] All three files consistently say "do NOT start round 5" / "escalate to user." PASS.
- [x] queen-state.md provides tracking fields for the cap state. PASS.
- [x] reviews.md cap language is in the Termination Rule section where the loop logic lives. PASS.

**Placement issue — cap not reachable before round 5 spawns (Finding 2 below)**: In `RULES.md` Step 3c, the "Round cap" block is positioned as a sibling after the "If P1 or P2 issues found" decision block. The "fix now" branch reads: "Spawn fix tasks (see reviews.md), then re-run Step 3b with round N+1." This is an action directive — a Queen following it would proceed to spawn before continuing to read the Round cap block that follows. The cap block would only be encountered on re-entry to Step 3c after round N+1 completes, meaning the cap check happens one round late: a Queen enters round 5 before the cap text blocks it. The cap should either be integrated into the "fix now" branch (e.g., "if current round < 4, re-run Step 3b; else escalate") or placed before the "fix now" action rather than after the "defer" branch.

The `reviews.md` Escalation cap paragraph has the same structural issue — it appears at the end of the Termination Rule section rather than inside the "fix now" decision path.

**Verdict for ant-farm-rcdd**: PARTIAL (incomplete — cap placement allows round 5 to start before the cap fires).

---

## Findings Catalog

### Finding 1: WARN block still lists DMVDC as a WARN checkpoint after ant-farm-4l0t fix

- **File(s)**: `/Users/correy/projects/ant-farm/orchestration/templates/checkpoints.md:54,57`
- **Severity**: P2
- **Category**: correctness
- **Description**: The ant-farm-4l0t fix correctly added PARTIAL to the summary and updated the table, but did not remove DMVDC from the WARN definition block. `checkpoints.md:54` still reads `**WARN** (checkpoints: CCO, WWD, **DMVDC** only)` and `checkpoints.md:57` still reads `- DMVDC WARN: Partial failures detected. Agent can repair and resubmit.` This directly contradicts the new PARTIAL definition at line 59 and the updated table at lines 70-71. The fix addressed the table (Problem B from round-1 Finding 5) but left Problem A's core ambiguity in place: a Pest Control agent reading the WARN block will still see DMVDC listed as a WARN checkpoint, even though the correct verdict is PARTIAL. The fix is incomplete.
- **Suggested fix**: Remove `DMVDC` from the WARN header at line 54 (change to `(checkpoints: CCO, WWD only)`) and delete the `- DMVDC WARN: Partial failures detected. Agent can repair and resubmit.` line at line 57. The PARTIAL definition at line 59 now covers this case.
- **Cross-reference**: Directly traces to round-1 Finding 5, Problem A. The fix addressed Problem B (table) but not Problem A (WARN prose block).

### Finding 2: Round cap block in RULES.md Step 3c placed after the action it is meant to prevent

- **File(s)**: `/Users/correy/projects/ant-farm/orchestration/RULES.md:119,122-126`
- **Severity**: P2
- **Category**: correctness
- **Description**: The ant-farm-rcdd fix added the "Round cap — escalate after round 4" block in Step 3c, but positioned it as a sibling after the "If P1 or P2 issues found" block — specifically after the "defer" branch (line 121). The "fix now" action (line 119) reads "re-run Step 3b with round N+1" — a Queen following this path spawns the next round immediately. The Round cap block only appears after the defer branch, so a Queen acting on "fix now" in the same Step 3c pass never sees the cap before spawning. On re-entry to Step 3c after round 5 completes, the cap is seen — but by then round 5 has already started. The cap fires one round late, meaning the effective cap is round 5, not round 4 as stated.

  The same ordering issue exists in `reviews.md:144` where the Escalation cap paragraph sits at the end of the Termination Rule section, after the termination bullet points, rather than inside the loop logic.

- **Suggested fix**: In RULES.md Step 3c, restructure the "fix now" branch to check the round number before re-spawning:
  ```
  - **If "fix now"**:
    - If current round < 4: Spawn fix tasks, then re-run Step 3b with round N+1
      - Update session state: increment review round, record fix commit range
    - If current round = 4: Do NOT start round 5. Escalate to user with full round history.
  ```
  The separate "Round cap" sibling block can then be removed (the check is now inline). In reviews.md, move the Escalation cap note to appear inside the loop description rather than after it.
- **Cross-reference**: New finding introduced by ant-farm-rcdd fix. No cross-domain overlap.

---

## Preliminary Groupings

### Group A: Incomplete fix — WARN/PARTIAL contradiction partially unresolved
- Finding 1 (WARN block still lists DMVDC) — the ant-farm-4l0t fix addressed the summary table but not the WARN prose block
- **Suggested combined fix**: One additional edit to checkpoints.md:54-57 removes DMVDC from the WARN header and deletes the DMVDC WARN bullet. Two-line change.

### Group B: Standalone structural placement
- Finding 2 (round cap placed after the action it blocks) — structural ordering issue in RULES.md Step 3c and reviews.md Termination Rule. Standalone fix.

---

## Summary Statistics
- Total findings: 2
- By severity: P1: 0, P2: 2, P3: 0
- Preliminary groups: 2

---

## Cross-Review Messages

### Sent
- None sent.

### Received
- None received.

### Deferred Items
- None.

---

## Coverage Log

| File | Status | Evidence |
|------|--------|----------|
| orchestration/RULES.md | Findings: #2 | Step 3c (lines 109-126) read in full. Round cap block at lines 122-126 examined for placement correctness. Retry Limits table (lines 233-240) checked for round cap entry. Fix commit `d9201c9` diff verified. |
| orchestration/templates/checkpoints.md | Findings: #1 | Verdict Thresholds Summary (lines 44-93) read in full. WARN block (lines 54-57), new PARTIAL block (lines 59-60), and Checkpoint-Specific Thresholds table (lines 65-72) all examined. DMVDC verdict sections (lines 86-87, 369-370, 427-428) cross-checked for consistency. Fix commit `023ee0f` diff verified. |
| orchestration/templates/queen-state.md | Reviewed — no issues | Review Rounds section (lines 33-39) read in full. Max rounds (line 35) and Escalation cap (line 36) fields verified. Three-file consistency check with RULES.md and reviews.md performed. |
| orchestration/templates/reviews.md | Reviewed — no issues | Termination Rule section (lines 135-145) read in full. Escalation cap paragraph (line 144) verified present and consistent with RULES.md and queen-state.md. Step 0 bash blocks (lines 410-424) and polling loop (lines 443-486) read in full; exact-path checks and exit 1 verified. Fix commit `002ee87` diff verified. |

---

## Overall Assessment
**Score**: 6/10
**Verdict**: NEEDS WORK

Two P2 issues remain. Finding 1: the ant-farm-4l0t fix is incomplete — it correctly added PARTIAL and fixed the table, but left the WARN block's DMVDC entry intact at `checkpoints.md:54,57`, preserving the core contradiction that caused round-1 Finding 5. Finding 2: the ant-farm-rcdd fix adds a round cap that is structurally placed after the "fix now" action it is meant to prevent, meaning a Queen following the "fix now" path enters round 5 before the cap text is encountered.

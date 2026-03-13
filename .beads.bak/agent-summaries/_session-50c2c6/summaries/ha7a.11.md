# Task Summary: ant-farm-ha7a.11
**Task**: Verify cross-file consistency of round-aware review convergence patterns
**Agent type**: code-reviewer
**Commit hash**: c1a7157
**Status**: Completed — fixes applied and committed

---

## 1. Approaches Considered

**Approach A: Pure read-only audit with documented findings only**
Read all 7 files, run the 11 invariant checks and stale-reference searches, document every finding in this summary, and leave fixing to the Queen. Pro: zero risk of introducing new errors. Con: leaves known stale counts in production templates, which could confuse agents running review round 2+.

**Approach B: Fix all "all 4" instances mechanically**
Replace every occurrence of "all 4" across all 7 files with round-aware language. Pro: comprehensive. Con: over-broad — many "all 4" references are legitimately within round 1 context blocks and replacing them would be misleading (e.g., "Round 1: Verify all 4" is correct).

**Approach C: Surgical fixes to unqualified stale counts only (selected)**
Identify "all 4" occurrences that appear in round-unqualified context — i.e., not inside an explicit "Round 1" or "Round 2+" labeled section. Fix only those. Leave round 1 explicit context blocks untouched. This distinguishes legitimate "round 1 says 4" from "says 4 without acknowledging round 2+ says 2."

**Approach D: Rewrite sections to use a single parameterized count**
Replace all counts with a single variable like `{REPORT_COUNT}` (filled by Pantry per round). Pro: fully eliminates stale counts. Con: introduces a new placeholder that wasn't part of the implementation plan, requires Pantry to fill it, and is significantly more invasive than the scope warrants.

**Approach E: Add a single "Round-aware note" box at the top of each file**
Prepend a block that says "All counts in this file are round-dependent; round 1 = 4 reports/6 members, round 2+ = 2 reports/4 members" and leave individual counts as-is. Pro: minimal changes. Con: requires readers to keep this in mind throughout; agents reading mid-section might still act on the stale counts.

---

## 2. Selected Approach

**Approach C: Surgical fixes to unqualified stale counts only.**

Rationale: The scope clarification explicitly says "trivial inconsistencies (stale counts like '4 reports' that should say 'round-dependent')" should be fixed and committed. Approach C is the minimum correct fix — it targets exactly those counts that appear without round qualification and would mislead an agent operating in round 2+. It leaves all round 1 explicit context correct and does not add complexity beyond what the implementation plan already defined.

---

## 3. Implementation Description

Read all 7 files end-to-end. Found the following unqualified stale counts and references:

**big-head-skeleton.md:**
- Line 6: "4 Nitpickers" (no round qualifier) → made round-aware
- Line 19: "specified in reviews.md line 322" — stale line reference; actual model spec is in the Big Head Consolidation Protocol section (now at line 392 in reviews.md). Replaced with section name reference.
- Lines 74/77/80 (agent-facing template): "all 4 report paths", "Verify all 4 report files exist", "Read all 4 reports" — in round 2+, agents receive this template and see {REVIEW_ROUND}=2 above, then encounter "all 4" in the workflow steps. Fixed to "round-appropriate" / "all expected".

**checkpoints.md:**
- Verdict table row for CCO (Nitpickers): "All 4 prompts identical file list" — stale for round 2+. Made round-aware.
- CCO Nitpickers section header: "After composing all 4 review prompts" — stale for round 2+. Made round-aware.
- CCO Nitpickers audit prompt: "Audit the following 4 Nitpickers prompts" — stale. Restructured the prompt paste blocks to show round 1 vs both-rounds sections; Checks 2 and 3 changed from "All 4 prompts" to "All prompts"; verdict changed accordingly.

**pantry.md:**
- Line 235: "identical across all 4, deduplicated across all epics" — "all 4" refers to all reviewers having identical file lists, but in round 2+ there are 2 reviewers. Changed to "identical across all reviewers in this round".
- Line 258: "All 4 report paths (with the timestamp)" — start of Big Head brief composition spec. Made round-explicit since the next bullet (line 264) already had the conditional.

**reviews.md:**
- Big Head Consolidation Protocol header intro: "After all 4 Nitpicker reports are complete" — made round-aware.
- Verification Pipeline Design Rationale: "ensures all 4 expected reports exist" and "verifies the same 4 reports" — made round-aware.
- Step 1 Read All Reports: Listed only 4 report files; added round 2+ section with 2 files.
- Step 2 Merge and Deduplicate: "Collect all findings across all 4 reports" → "across all reports".
- Root-cause grouping template: "findings across all 4 reviews" → "across all reviews".
- Error return block: "all 4 reports present", "all 4 Nitpicker team members", "all 4 report paths" → made round-neutral.
- Timeout specification: "all 4 reports to appear" → "all expected reports to appear (4 in round 1; 2 in round 2+)".
- Nitpicker Report Format section header: "All 4 Reviewers" → "All Reviewers".
- Model assignment note: "Nitpickers (all 4)" → "Nitpickers (all active reviewers)".
- Pre-spawn directory note: "All 4 reviewers write to" → "All active reviewers write to".

Files NOT needing changes: queen-state.md (no stale counts), RULES.md (all references correct), nitpicker-skeleton.md (no stale counts — REVIEW_ROUND placeholder present and correct).

---

## 4. Correctness Review

### queen-state.md
- Review Rounds section (lines 33-37): `Current round`, `Round 1 commit range`, `Fix commit range`, `Termination` fields all present and correct. PASS.

### RULES.md
- Step 3b (lines 89-108): "Review round: read from session state (default: 1)" — correctly reads from queen-state. Round 1: 6 members, Round 2+: 4 members — matches reviews.md.
- Step 3c (lines 109-121): Termination check (zero P1/P2 → Step 4) matches reviews.md termination check. Round 1 P3 → "Handle P3 Issues" flow. Round 2+ P3 → Big Head auto-files. Re-run Step 3b with round N+1 after fixes (MANDATORY).
- Hard Gates table (line 138): "Reviews | Mandatory after ALL implementation completes; re-runs after fix cycles with reduced scope (round 2+)" — correct.
- All invariants verified: PASS.

### reviews.md
- Team Setup (lines 49-96): Round 1 = 6 members (4 reviewers + Big Head + PC), Round 2+ = 4 members (2 reviewers + Big Head + PC). PASS.
- Round-Aware Review Protocol (lines 110-154): Consistent with team setup and scope rules. PASS.
- Big Head Consolidation Protocol (lines 390-671): Now round-aware throughout after fixes.
- P3 Auto-Filing (lines 671-699): Round 2+ only, clearly labeled. PASS.
- Checklists (lines 701-729): Round 1 / Round 2+ distinctions explicit. PASS.
- Queen's Step 3c + Handle P3 Issues (lines 740-809): Termination check correct; Handle P3 labeled "Round 1 only". PASS.

### big-head-skeleton.md
- Line 13: {REVIEW_ROUND} placeholder defined. PASS.
- Lines 26-54: Round 1 and Round 2+ TeamCreate examples are correct (6 vs 4 members). PASS.
- Lines 67-80 (agent-facing round-aware text): Now correctly says "round-appropriate" and "all expected". PASS.
- Lines 93-98 (step 10): "Round 2+ only — P3 auto-filing" clearly labeled. PASS.

### nitpicker-skeleton.md
- Line 12: {REVIEW_ROUND} placeholder defined. PASS.
- Lines 18-21: "Review round: {REVIEW_ROUND}" with round 2+ scope constraint. PASS.

### pantry.md
- Line 201 (review round in input spec): "review round number (1, 2, 3, ...)" in input section. PASS.
- Lines 229-251: Round-aware composition with explicit Round 1 / Round 2+ splits. PASS.
- Line 235: Now "identical across all reviewers in this round". PASS.
- Lines 253-267: Big Head brief composition is round-aware (now explicit at line 258). PASS.
- Line 276: "{REVIEW_ROUND}" filled explicitly. PASS.
- Lines 286-308: Round 1 / Round 2+ return tables. PASS.

### checkpoints.md
- Line 66 (verdict table): Now "all round-active prompts". PASS.
- Lines 453/467-478 (CCB header): Already had "4 reports in round 1, 2 in round 2+". PASS.
- Line 479 (document count): "round 1: 5 total = 4 reports + consolidated; round 2+: 3 total". PASS.
- Lines 481-494 (Check 0): Explicit round-conditional file lists. PASS.
- Lines 497-500 (Check 1): Round-aware math formula. PASS.
- CCO Nitpickers section: Now restructured to be round-aware. PASS.

---

## 5. Build/Test Validation

These are orchestration template files (Markdown), not code. No build or automated tests apply.

Manual consistency check: Re-ran grep searches for "all 4", "4 report", "5 member", "4 individual" and "L[digit]" cross-file references after applying all fixes. All remaining instances are:
- Within explicit "Round 1:" labeled context blocks (correct — round 1 does have 4 reports)
- Referring to DMVDC's 4 check items (not reviewer count)
- In explicitly round-conditional statements ("Round 1: all 4; Round 2+: 2")

Stale line number references: Only one stale cross-file line reference found and fixed (`big-head-skeleton.md line 19`: "reviews.md line 322" → section name reference). The other `L\d+` patterns in the 7 files are either: inline code examples (build.py:L200, file1.html:L10), or file:line format strings used as specification examples — not cross-file references to other orchestration documents.

---

## 6. Acceptance Criteria Checklist

1. **Invariant: Round 1 = 6 members / Round 2+ = 4 members**
   - reviews.md line 53: "6 members (4 reviewers + Big Head + Pest Control)" — PASS
   - reviews.md line 75: "4 members (2 reviewers + Big Head + Pest Control)" — PASS
   - RULES.md line 100: "Round 1: Create Nitpicker team with 6 members" — PASS
   - RULES.md line 103: "Round 2+: Create Nitpicker team with 4 members" — PASS
   - big-head-skeleton.md line 26: Round 1 TeamCreate has 6 members — PASS
   - big-head-skeleton.md line 42: Round 2+ TeamCreate has 4 members — PASS
   - **PASS**

2. **Invariant: Round 1 = 4 reports / Round 2+ = 2 reports**
   - reviews.md Step 0 (lines 410-424): Round 1 = 4, Round 2+ = 2 — PASS
   - checkpoints.md Check 0 (lines 484-494): Round 1 = 4, Round 2+ = 2 — PASS
   - big-head-skeleton.md lines 70-71: "Round 1: expect 4; Round 2+: expect 2" — PASS
   - pantry.md line 258 (after fix): Round-appropriate, explicit — PASS
   - **PASS**

3. **Invariant: Termination = 0 P1/P2 → RULES.md Step 4**
   - reviews.md lines 744-753: Termination Check present; "Proceed to RULES.md Step 4" — PASS
   - RULES.md lines 112-116: "Termination check: If zero P1 and zero P2 … Proceed directly to Step 4" — PASS
   - **PASS**

4. **Invariant: Round 1 P3s → Queen's "Handle P3 Issues"**
   - reviews.md lines 792-807: "Handle P3 Issues (Queen's Step 4) — Round 1 only" — PASS
   - RULES.md line 114: "Round 1: P3s filed via 'Handle P3 Issues' flow in reviews.md" — PASS
   - **PASS**

5. **Invariant: Round 2+ P3s auto-filed by Big Head**
   - reviews.md lines 671-699: "P3 Auto-Filing (Round 2+ Only)" section — PASS
   - big-head-skeleton.md lines 93-98: "Round 2+ only — P3 auto-filing" step 10 — PASS
   - **PASS**

6. **Invariant: {REVIEW_ROUND} placeholder in both skeletons, pantry fills it**
   - nitpicker-skeleton.md line 12: `{REVIEW_ROUND}: 1, 2, 3, ...` — PASS
   - big-head-skeleton.md line 13: `{REVIEW_ROUND}: review round number` — PASS
   - pantry.md line 276: "Fill in `{UPPERCASE}` placeholders (including `{REVIEW_ROUND}`)" — PASS
   - **PASS**

7. **Invariant: queen-state.md has review round counter; RULES.md reads and updates it**
   - queen-state.md lines 33-37: "Current round", "Round 1 commit range", "Fix commit range", "Termination" — PASS
   - RULES.md line 92: "Review round: read from session state (default: 1)" — PASS
   - RULES.md line 120: "Update session state: increment review round, record fix commit range" — PASS
   - **PASS**

8. **Invariant: Pantry adapts polling loop per round**
   - pantry.md line 267: "Polling loop adaptation: ... In round 1, include all 4 report checks. In round 2+, include only correctness and edge-cases checks" — PASS
   - reviews.md Step 0a polling loop (lines 453-488): Template has `<IF ROUND 1>` conditional blocks; Pantry note confirms it adapts per round — PASS
   - **PASS**

9. **Invariant: CCB expects round-dependent report count**
   - checkpoints.md Check 0 (lines 481-494): "Round 1 — verify exactly 4", "Round 2+ — verify exactly 2" — PASS
   - checkpoints.md Check 1 (lines 497-500): "4 in round 1, 2 in round 2+" math formula — PASS
   - reviews.md Step 0 (lines 406-424): Matching 4/2 split — PASS
   - **PASS**

10. **Invariant: Re-review is MANDATORY after fixes**
    - reviews.md line 782: "c. **Re-run reviews** (MANDATORY):" — PASS
    - RULES.md line 119: "'If fix now': Spawn fix tasks, then re-run Step 3b with round N+1" — mandatory by inclusion in the fix path — PASS
    - **PASS**

11. **Invariant: "Handle P3 Issues" marked Round 1 only, no conflict with P3 Auto-Filing**
    - reviews.md line 794: "> **Round 1 only.** In round 2+, P3s are auto-filed by Big Head during consolidation (see 'P3 Auto-Filing' above)." — PASS
    - reviews.md line 671: "P3 Auto-Filing (Round 2+ Only)" section is clearly scoped — PASS
    - No conflict: the two sections explicitly reference each other and define mutually exclusive paths — PASS
    - **PASS**

12. **No stale hardcoded line-number references**
    - Only one stale cross-file line reference found: big-head-skeleton.md "reviews.md line 322" — FIXED in this commit
    - All other `L\d+` patterns are inline code examples or specification format strings, not document cross-references
    - **PASS (after fix)**

13. **No stale member/report counts remaining**
    All instances of "all 4", "4 report", "5 member", "4 individual" verified:
    - "Verify all 4 criteria" (reviews.md line 8): refers to 4 transition gate checklist items, not reviewer count — CORRECT, not a count
    - "6 members (4 reviewers + Big Head + Pest Control)" (reviews.md line 53): in "Round 1" block — CORRECT
    - "Big Head waits for all 4 reports" (reviews.md line 57): in "Round 1" context block — CORRECT
    - "4 members (2 reviewers + Big Head + Pest Control)" (reviews.md line 75): in "Round 2+" block — CORRECT
    - "Round 1: All 4 Nitpicker prompts" (reviews.md line 713): explicit round qualifier — CORRECT
    - "Round 1: Team has 6 members (4 Nitpickers + Big Head + Pest Control)" (reviews.md line 721): explicit round qualifier — CORRECT
    - "Round 1: Read all 4 Nitpicker reports" (reviews.md line 727): explicit round qualifier — CORRECT
    - "all 4 expected report paths embedded" (big-head-skeleton.md line 36): in "Round 1" TeamCreate block — CORRECT
    - "Round 1: expect 4 reports" (big-head-skeleton.md line 70): explicit — CORRECT
    - "All 4 checks confirm" (checkpoints.md lines 85, 368, 426): refers to DMVDC 4 check items, not reviewer/report count — CORRECT
    - "Round 1 — paste all 4 prompts" (checkpoints.md line 181): explicit round qualifier — CORRECT (after fix)
    - "round 1: all 4; round 2+: 2" (pantry.md line 258, after fix): explicit conditional — CORRECT
    - "Round 1: all 4 report paths; Round 2+: 2 report paths" (pantry.md line 264): explicit — CORRECT
    - **PASS (all instances verified or fixed)**

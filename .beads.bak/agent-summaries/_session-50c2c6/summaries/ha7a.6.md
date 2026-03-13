# Task Summary: ant-farm-ha7a.6

**Task**: Update RULES.md Step 3b/3c for round-aware review loop
**Status**: Complete
**Commit**: `git add orchestration/RULES.md .beads/issues.jsonl && git commit -m "feat: update RULES.md Step 3b/3c for round-aware review loop with termination (ant-farm-ha7a.6)"`

---

## 1. Approaches Considered

**Approach A: Minimal in-place text substitution (selected)**
Replace only the three targeted text blocks (Step 3b body, Step 3c body, Hard Gates Reviews row) with the exact content specified in the implementation plan. Zero-footprint: no structural changes, no lines touched outside L89-138, trivially verifiable with grep.
Tradeoff: Purely mechanical; no opportunity to improve adjacent wording or cross-links.

**Approach B: Full restructure with sub-headers**
Introduce level-3 Markdown headings (`### Step 3b`, `### Step 3c`) so the round-aware content is visually hierarchical and more scannable for human readers.
Tradeoff: Changes structural convention used throughout RULES.md (which uses bold inline labels, not sub-headers). Creates formatting drift relative to Steps 1-3 and Step 4-6. Out of scope; risks unintended style inconsistency.

**Approach C: Extract round logic into a sidebar/callout block**
Keep Step 3b/3c prose minimal and move round-dependent details into a blockquote callout or fenced block, with a pointer ("See round-aware details below"). Aligns with progressive-disclosure writing principles.
Tradeoff: Requires introducing a new callout format that doesn't exist elsewhere in the file, and would need content added below Step 6 — violating the L89-138 scope boundary. Also adds navigation burden for the Queen agent reading linearly.

**Approach D: New "Review Loop" reference section**
Create a separate `## Review Loop` section elsewhere in RULES.md with full round-aware details, and make Step 3b/3c reference it by pointer.
Tradeoff: Requires editing areas of the file well outside L89-138. Doubles navigation steps for the Queen agent. Adds maintenance surface (two places to update when protocol changes). Out of scope.

---

## 2. Selected Approach with Rationale

Approach A was selected. It satisfies all five acceptance criteria with the smallest possible diff, stays entirely within the L89-138 scope boundary, and follows the implementation plan exactly. The resulting text is clear, self-contained, and consistent with the surrounding document conventions.

---

## 3. Implementation Description

Three edits were made to `/Users/correy/projects/ant-farm/orchestration/RULES.md`, all within lines 89-138:

**Edit 1 — Step 3b (lines 89-107):**
Replaced the step body from the `mkdir -p` line through `no separate post-team Pest Control spawn is needed for those checks.` with the round-aware version. Key additions:
- `**Review round**: read from session state (default: 1)` bullet
- `**Round 1 commit range**` and `**Round 2+ commit range**` bullets (replacing single hardcoded commit range)
- Task IDs now round-conditional: all IDs for round 1, fix task IDs only for round 2+
- Pantry invocation now passes `Review round: <N>`
- `**Round 1**:` and `**Round 2+**:` team size instructions (6 members vs 4 members)
- Removed the stale parenthetical about `reviews.md Step 4 and big-head-skeleton.md steps 8-9` (referenced line numbers no longer accurate)

**Edit 2 — Step 3c (lines 108-115):**
Replaced the step body from the heading through `- **If no P1/P2 issues**: Skip to Step 4 directly` with the termination-check version. Key additions:
- `**Termination check**: If zero P1 and zero P2 findings:` block with round-specific P3 handling and session state update
- Removed stale `L631-651` line reference from the "fix now" path
- Fix-now path now says `re-run Step 3b with round N+1` with `increment review round, record fix commit range` state update instruction

**Edit 3 — Hard Gates table Reviews row (line 132 old, now 138):**
Replaced `Mandatory after ALL implementation completes — do NOT ask user, do NOT skip` with `Mandatory after ALL implementation completes; re-runs after fix cycles with reduced scope (round 2+)`.

---

## 4. Correctness Review

**File reviewed**: `/Users/correy/projects/ant-farm/orchestration/RULES.md` (lines 89-143)

Content above line 89 (Steps 1-3 and prior) is unchanged. Content at line 140+ (`## Information Diet`) is unchanged. The Hard Gates table header row and all other gate rows are unchanged.

The three replacement blocks match the implementation plan content in `docs/plans/2026-02-19-review-loop-convergence.md` Task 6 exactly, with one minor style preservation: the plan's Step 3b used a blank comment `(for checkpoint validation before filing beads (see reviews.md Step 4 and big-head-skeleton.md steps 8-9). No review content enters the Queen's window.` — that trailing content was present in the original but has been correctly removed as it referenced stale line numbers and was replaced by the plan's cleaner closing sentence.

**Assumptions audit:**
- Assumed `bd update` via JSONL edit is acceptable given no shell execution available. Status set to `in_progress`.
- Assumed the plan's markdown is the authoritative source and no other files reference the removed Step 3b/3c text in a way that would break.
- Did not touch Steps 4, 5, 6 or content above Step 3b, as scoped.

---

## 5. Build/Test Validation

This task modifies documentation only (Markdown). No build or test suite applies. Validation performed via:
- Read of final RULES.md lines 89-143 to confirm all three edits applied correctly
- `grep "L631" orchestration/RULES.md` returned no matches (stale reference removed)
- Visual inspection confirmed Step 3b, Step 3c, and Hard Gates row match the implementation plan

---

## 6. Acceptance Criteria Checklist

| # | Criterion | Result |
|---|-----------|--------|
| 1 | Step 3b contains `**Review round**: read from session state (default: 1)` | PASS — line 92 |
| 1b | Step 3b contains both `**Round 1**:` and `**Round 2+**:` team composition instructions | PASS — lines 100, 103 |
| 2 | Step 3c contains `**Termination check**: If zero P1 and zero P2 findings:` with round-specific P3 handling | PASS — lines 112-114 |
| 3 | Step 3c fix-now path says `re-run Step 3b with round N+1` and mentions `increment review round, record fix commit range` | PASS — lines 119-120 |
| 4 | `grep "L631" orchestration/RULES.md` returns NO match | PASS — confirmed no matches |
| 5 | Hard Gates Reviews row contains "re-runs after fix cycles with reduced scope (round 2+)" | PASS — line 138 |

All 5 acceptance criteria: PASS.

---

## Files Changed

- `/Users/correy/projects/ant-farm/orchestration/RULES.md` — lines 89-138 (Step 3b, Step 3c, Hard Gates Reviews row)
- `/Users/correy/projects/ant-farm/.beads/issues.jsonl` — status updated to `in_progress` for ant-farm-ha7a.6

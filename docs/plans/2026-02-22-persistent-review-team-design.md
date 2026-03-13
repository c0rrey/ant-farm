> **Note**: This document was written during the Beads era. CLI commands shown as `bd` have been replaced by `crumb` equivalents.

# Persistent Review Team with Fix Inner Loop

**Date**: 2026-02-22
**Status**: Approved

## Problem

Three pain points in the current review-fix-review loop:

1. **One-TeamCreate-per-session constraint** means round 2+ reviews fall back to sequential mode, losing parallelism and cross-pollination.
2. **Fix agents can't communicate with reviewers** who found the issues -- no channel for clarification on root causes or affected surfaces.
3. **Unnecessary overhead** from tearing down and recreating teams between review rounds.

## Solution

Keep the Nitpicker team alive across the entire review-fix-review loop. Spawn fix Dirt Pushers and fix Pest Control agents into the team. Fix agents iterate directly with PCs on DMVDC failures and can message reviewers for clarification.

## Key Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Big Head's role | Consolidation + bead filing + handoff to Queen (lean) | Avoids context pressure from orchestration duties |
| Same Big Head across rounds | Yes | Round 1 context is an asset for comparing findings |
| Reviewer re-tasking | Queen messages directly | Simple, Queen knows the commit range |
| Fix PCs per round | Fresh instances | Clean context matters for verification accuracy |
| Fix-cycle Scout | Auto-approved (for the user), with SSV gate | Speed + mechanical safety net |
| Pantry for fix briefs | Skip | Beads ARE the briefs; CCB validates quality |
| CCO for fix briefs | Skip | Bead content passed CCB; Scout strategy passed SSV |
| CCB model | Upgraded haiku -> sonnet | Checks 3 and 6 require judgment |
| Pre-fix correctness check | Lightweight spot-check (2 beads max) | Catches hallucinations without slowing the loop |
| Material spot-check failure | Respawn fresh Big Head, full bead review | Context degradation suspected; old BH can't self-correct |
| Step 1 Scout auto-approval | Separate issue (not in this design) | Different risk profile from fix-cycle auto-approval |

## Complete Flow

```
Step 3b: Queen creates team (6 members)
  |
  +-- Round 1: 4 Nitpickers review in parallel
  +-- Big Head consolidates, CCB (sonnet) validates
  |   +-- Check 3b spot-check: minor -> amend in place
  |   +-- Check 3b spot-check: material -> fresh Big Head, full review
  +-- Big Head files beads, sends list to Queen
  |
  +-- 0 P1/P2 -> converged -> team shutdown -> Step 4
  |
  +-- P1/P2 found (auto-fix <=5 root causes, or user says "fix now"):
  |   +-- Queen spawns Scout (outside team) for fix strategy
  |   +-- Queen spawns SSV PC (haiku) -- must PASS
  |   +-- Queen spawns into team:
  |   |   +-- N fix Dirt Pushers (sonnet)
  |   |   +-- fix-pc-wwd (haiku)
  |   |   +-- fix-pc-dmvdc (sonnet)
  |   |
  |   +-- Inner loop:
  |   |   DP commits -> messages fix-pc-wwd
  |   |   -> WWD PASS -> messages fix-pc-dmvdc
  |   |   -> DMVDC PASS -> DP idle
  |   |   -> DMVDC FAIL -> PC messages DP with specifics -> DP iterates
  |   |   -> Max 2 retries -> escalate to Queen
  |   |
  |   +-- All fix DPs verified
  |   +-- Queen builds round 2 prompts, runs CCO
  |   +-- Queen messages Correctness + Edge Cases with round 2 scope
  |   +-- Same Big Head consolidates round 2
  |   +-- Loop until 0 P1/P2 or round 4 cap
  |
  +-- Team shutdown -> Step 4
```

## Team Member Roster

### Initial Spawn (Step 3b, round 1): 6 members

| Member | Agent Type | Model | Status after round 1 |
|--------|-----------|-------|---------------------|
| Clarity reviewer | nitpicker | sonnet | Idle (done for session) |
| Edge Cases reviewer | nitpicker | sonnet | Idle -> re-tasked round 2 |
| Correctness reviewer | nitpicker | sonnet | Idle -> re-tasked round 2 |
| Drift reviewer | nitpicker | sonnet | Idle (done for session) |
| Big Head | big-head | opus | Idle -> re-activated each round |
| Pest Control (review) | pest-control | sonnet | Idle -> re-activated for CCB each round |

### Added After Fix Decision: up to N+2 members

| Member | Agent Type | Model | Lifecycle |
|--------|-----------|-------|-----------|
| fix-dp-1..N | dynamic (from Scout) | sonnet | Spawned per fix cycle, idle after DMVDC pass |
| fix-pc-wwd | pest-control | haiku | Fresh each round |
| fix-pc-dmvdc | pest-control | sonnet | Fresh each round |

Peak team size: 6 + 7 + 2 = 15 members (if max 7 fix DPs). Only N+2 are actively working during the fix phase -- the original 6 are idle. Idle members don't consume API tokens.

## Fix Inner Loop Protocol

### Trigger

Big Head sends bead list to Queen, Queen decides to fix (auto-fix round 1 with <=5 root causes, or user says "fix now").

### Steps

1. **Queen spawns Scout** (outside team) with bead IDs. Scout returns fix strategy to `{SESSION_DIR}/briefing-fix-r<N>.md`: wave composition, agent types, file assignments.

2. **Queen spawns SSV** (Pest Control, haiku, outside team) on the fix briefing. Same mechanical checks as Step 1b: file overlap within waves, file list match, intra-wave dependency ordering.
   - **SSV PASS**: Proceed. No user confirmation gate (auto-approved for the user).
   - **SSV FAIL**: Re-run Scout with violations. Max 1 retry, then escalate to user.

3. **Queen spawns fix agents into team** (single message): N fix DPs + fix-pc-wwd + fix-pc-dmvdc.

4. **WWD runs first**: After a fix DP commits, it messages `fix-pc-wwd` with commit hash and task ID. WWD PC does mechanical file check. Replies pass/fail.

5. **DMVDC runs second**: After WWD pass, DP messages `fix-pc-dmvdc`. DMVDC PC checks substance.
   - **PASS**: PC replies confirming. DP goes idle.
   - **FAIL**: PC replies with specifics (what's wrong, what's missing). DP iterates and re-commits. Back to step 4. Max 2 retries.
   - **Retry exhausted**: PC messages Queen with failure details. Queen escalates to user.

6. **All fix DPs verified**: Queen proceeds to round transition.

### Fix DP Prompt Structure

Fix DPs receive a lean prompt. The bead is the source of truth:

```
Fix the issue described in bead <bead-id>.
Read the full bead with: bd show <bead-id>
Agent type: <from Scout>
Session directory: <SESSION_DIR>
Write your summary to: <SESSION_DIR>/summaries/<bead-id>-fix.md
After committing, message fix-pc-wwd with your commit hash and task ID.
```

### Naming Convention

- `fix-dp-1`, `fix-dp-2`, ... (fix Dirt Pushers)
- `fix-pc-wwd` (WWD checker)
- `fix-pc-dmvdc` (DMVDC checker)
- Round 2+ fix cycle: `fix-dp-r2-1`, `fix-pc-wwd-r2`, `fix-pc-dmvdc-r2`

## Pantry & CCO: Skipped for Fix Briefs

**Pantry**: Skipped. Big Head's bead descriptions already contain root cause, affected surfaces, suggested fix, and acceptance criteria -- all composed from PC-validated review findings. The bead IS the fix brief.

**CCO**: Skipped. Bead content passed CCB validation. Scout strategy passed SSV. The combination of bead description + Scout agent-type assignment is sufficient.

## CCB Changes

### Model Upgrade: haiku -> sonnet

Checks 3 (bead quality) and 6 (dedup correctness) require judgment -- "is this root cause explanation substantive?" and "do these merged findings genuinely share a code path?" Sonnet handles this better than haiku. Since CCB is now the quality gate that determines whether beads are sufficient as fix briefs, the upgrade is justified.

### New Check 3b: Root Cause Spot-Check (Sampled)

Select up to 2 beads for deep validation (prioritize P1 beads, then highest-surface-count P2s):

For each sampled bead:
1. Read the source file(s) at the referenced file:line locations
2. Verify the root cause description matches what the code actually does
3. Assess whether the suggested fix is directionally correct (not "would it compile?" but "does it target the right code?")

Verdict per sampled bead:
- **CONFIRMED**: root cause and fix direction are consistent with the code
- **SUSPECT (minor)**: root cause exists but is vague/ambiguous. Flag for amendment, Big Head fixes in place, continue.
- **SUSPECT (material)**: root cause doesn't match code at referenced lines, OR suggested fix targets the wrong area. Triggers full bead review escalation.

### Material Spot-Check Escalation Path

When CCB finds a material SUSPECT:

1. **CCB verdict**: PARTIAL with flag `"context-degradation-suspected"`
2. **Queen shuts down old Big Head** (`shutdown_request`) -- its context is suspect
3. **Queen spawns fresh Big Head** (`big-head-r<N>`) into team with handoff:
   - CCB report path (showing which bead failed and why)
   - All bead IDs to review
   - Reviewer report paths
   - Round number
4. **Fresh Big Head reviews ALL beads**: reads code at every file:line reference, cross-references reviewer reports, amends or re-files incorrect beads
5. **Re-run CCB** (spot-check) on amended beads
6. **If still SUSPECT**: escalate to user. Two Big Head instances failing suggests a systemic issue.

## Round Transition Protocol

After all fix DPs pass DMVDC:

1. **Queen gathers fix metadata**: fix commit range (first fix commit..HEAD), changed files (`git diff --name-only`), fix task IDs

2. **Queen builds round 2 review prompts** (existing `build-review-prompts.sh`, round=2)

3. **Queen runs CCO** on round 2 prompts. Can use the review PC (original team member) or spawn external haiku PC.

4. **Queen messages Correctness and Edge Cases reviewers** with round 2 scope:
   - Fix commit range
   - Changed file list
   - Fix task IDs
   - Path to round 2 review brief
   - Output report path (new timestamp)

5. **Clarity and Drift reviewers**: left idle. Not messaged. Done for the session.

6. **Queen messages Big Head** with round 2 consolidation instructions:
   - Expected report count (2)
   - Report paths
   - Consolidated summary output path (new timestamp)

7. **Big Head consolidates round 2**, files any new beads, sends list to Queen.

8. **Convergence check**: 0 P1/P2 -> team shutdown -> Step 4. P1/P2 found -> back to fix cycle.

## Error Handling

| Scenario | Action |
|----------|--------|
| Fix DP stuck/crashes | Queen runs stuck-agent diagnostic (existing protocol), files bead for failed task, continues with remaining DPs. Round 2 reviewers catch the unfixed issue. |
| Fix PC crashes | Queen spawns replacement into team. DPs re-send verification requests. |
| Reviewer fails to produce round 2 report | Big Head's Step 0 polling catches it (30s timeout). Queen spawns fresh reviewer into team. |
| Big Head crashes mid-round | Queen spawns fresh Big Head with handoff doc (round number, report paths, bead IDs). |
| CCB spot-check material fail | Shut down old Big Head, spawn fresh, full bead review. See Material Spot-Check Escalation Path. |
| >50% fix DPs fail in a wave | Queen stops, escalates to user (existing wave failure threshold). |
| Round 4 with no convergence | Escalate to user with full round history (existing round cap). |

## Changes to Existing Files

| File | Change |
|------|--------|
| `orchestration/RULES.md` | Step 3b-3c rewritten for persistent team + fix inner loop; Model Assignments table: CCB haiku -> sonnet |
| `orchestration/templates/reviews.md` | Fix workflow updated for in-team fix DPs; Pantry/CCO skip documented; round transition via SendMessage |
| `orchestration/templates/checkpoints.md` | CCB model -> sonnet; new Check 3b (spot-check); material escalation path |
| `orchestration/templates/big-head-skeleton.md` | Add bead-list handoff message to Queen after filing |

## Related (Out of Scope)

- **Step 1 Scout auto-approval**: Separate issue. Different risk profile from fix-cycle auto-approval. File as its own bead.

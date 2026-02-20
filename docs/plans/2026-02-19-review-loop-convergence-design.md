# Review Loop Convergence

## Problem

The review pipeline has no convergence mechanism. Reviews scope to all session commits, so fix commits from round 1 become review surface for round 2. Four broad-scope reviewers (Clarity, Edge Cases, Correctness, Excellence) will always find something on any non-trivial change — especially Clarity and Excellence, whose focus areas (naming, readability, best practices, performance opportunities) are unbounded. The loop terminates only when reviewers return zero findings, which almost never happens.

The result: review → fix → review → fix cycles that burn tokens and time without converging. Session 405acc produced 11 root causes (3 P2, 8 P3). Session 54996f fixed those 3 P2s and immediately generated new P2s and P3s on the fix commits themselves.

## Design

### Round Structure

|  | Round 1 | Round 2+ |
|---|---|---|
| **Scope** | All session commits (`session-start..HEAD`) | Fix commits only (`fix-start..HEAD`) |
| **Reviewers** | 4 (Clarity, Edge Cases, Correctness, Excellence) | 2 (Correctness, Edge Cases) |
| **In-scope findings** | All severities reported | All severities reported |
| **Out-of-scope findings** | N/A (everything is in-scope) | Only runtime failure or silently wrong results |
| **P3 handling** | Presented to user via Big Head | Auto-filed to "Future Work" epic by Big Head, no user prompt |
| **Team size** | 6 (4 reviewers + Big Head + Pest Control) | 4 (2 reviewers + Big Head + Pest Control) |

### Termination Rule

The loop terminates when a review round produces zero P1 or P2 findings. At that point:

- Any P3s from the round are silently auto-filed to "Future Work" epic
- Queen proceeds directly to Step 4 (documentation)
- No user prompt needed

There is no hard cap on rounds. The reduced scope (fix commits only), reduced reviewer count (2 instead of 4), and higher bar for out-of-scope findings make convergence fast — likely 2 rounds max in practice.

### Out-of-Scope Finding Bar (Round 2+)

Reviewers in round 2+ may read full files for context but their mandate is narrowed. Out-of-scope findings (outside the fix commits) are only reportable if they would cause:

- **Runtime failure**: an agent, tool call, or workflow step would crash or error
- **Silently wrong results**: an agent would succeed but produce incorrect output (e.g., stale cross-references pointing the Queen to the wrong section, a variable name that causes an agent to call the wrong tool)

Not reportable out-of-scope:

- Naming conventions or style preferences
- Documentation gaps or missing comments
- Improvement opportunities (performance, scalability, modern features)
- Hypothetical edge cases that require unusual conditions to trigger

### Big Head P3 Routing (Round 2+)

Big Head's consolidation step gains routing logic in round 2+:

- **P1/P2 findings**: File beads, present to Queen for fix-or-defer decision (unchanged from round 1)
- **P3 findings**: Auto-file to "Future Work" epic:
  1. `bd create --type=bug --priority=3 --title="<title>"`
  2. Find or create the "Future Work" epic
  3. `bd dep add <bead-id> <future-work-epic-id> --type parent-child`
  4. Include in consolidated summary marked as "auto-filed, no action required"

The Queen does not see P3 findings in the fix-or-defer prompt. They appear only in the consolidated summary for the record.

### Round 2+ Reviewer Instructions

Correctness and Edge Cases reviewers receive modified instructions in round 2+:

> **Scope**: Review commits `<fix-start>..<HEAD>` only. You may read full files for context, but your mandate is: did these fixes land correctly and not break anything?
>
> **Out-of-scope findings**: If you notice something outside the fix commits that would cause a runtime failure, incorrect agent behavior, or silently wrong results (e.g., stale cross-references pointing to wrong sections), report it. Do NOT report naming conventions, style preferences, documentation gaps, or improvement opportunities outside the fix scope.

### Queen's Round Tracking

The Queen tracks the current review round number in the session state file. This determines:

- Which reviewer set to spawn (4 for round 1, 2 for round 2+)
- What scope to pass to the Pantry (all session commits vs fix commits only)
- Whether Big Head should auto-file P3s or present them

### Convergence Argument

Round 1 reviews all session work with 4 reviewers — maximum coverage, all severities surfaced. If P1/P2s are found and the user chooses "fix now," the fix commits become a much smaller diff. Round 2 reviews only that smaller diff with 2 focused reviewers and a higher bar for out-of-scope noise. The combination of narrower scope + fewer reviewers + suppressed P3s means the system converges when the fixes are correct. If a fix introduces a real bug, it gets caught and fixed — but polish items no longer restart the cycle.

## Files to Change

- **`orchestration/templates/reviews.md`**: Add "Round 2+ Protocol" section with scoped reviewer instructions, 2-reviewer team composition, out-of-scope bar definition, P3 auto-filing rule, and modified Big Head consolidation behavior
- **`orchestration/templates/big-head-skeleton.md`**: Add P3 routing logic for Future Work epic in round 2+
- **`orchestration/RULES.md`**: Update Step 3b to distinguish round 1 vs round 2+ (reviewer count, scope, team size), add termination rule, add round tracking to session state
- **`orchestration/templates/nitpicker-skeleton.md`**: Add round-aware scope instructions (round 2+ gets narrowed mandate)
- **`orchestration/templates/queen-state.md`** (if it exists): Add review round counter field

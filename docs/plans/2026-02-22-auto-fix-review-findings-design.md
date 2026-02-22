# Auto-Fix Review Findings

**Date**: 2026-02-22
**Status**: Approved
**Scope**: orchestration/RULES.md, orchestration/templates/reviews.md

## Problem

After Nitpicker reviews complete in Step 3c, the Queen always asks the user "Fix now or defer?" for P1/P2 findings. This creates an unnecessary blocking prompt when the answer is almost always "fix now" for round 1 findings.

## Design

Automatically fix P1/P2 findings after round 1, with differentiated treatment by severity.

### Decision Rules

| Condition | Action |
|-----------|--------|
| Round 1, P1+P2 root causes <= 5 | Auto-fix (no user prompt) |
| Round 1, P1+P2 root causes > 5 | Escalate to user (systemic issue) |
| Round 2+ | Existing behavior: ask user "fix now or defer?" |
| Round >= 4 (cap) | Existing behavior: escalate non-convergence |

### Notification

When auto-fix triggers, the Queen announces but does not wait:

> **Auto-fix**: Round 1 review found X P1 and Y P2 issues (Z root causes, within 5-threshold). Spawning fix tasks automatically.

When escalating due to >5 findings:

> **Escalation**: Round 1 review found Z root causes (>5 threshold). Manual decision required: fix now or defer?

### Fix Workflow Split by Severity

**P1 findings (build failures, security, data loss) -- TDD workflow:**

1. Create test-writing task per P1 root cause
2. Include a test specification block in the brief, extracted from the consolidated summary:
   - Failing case: specific scenario from the review finding (concrete input, expected vs actual)
   - Boundary condition: edge case derived from affected surfaces
   - Regression guard: happy path that must still pass
3. Spawn Dirt Pushers to write tests matching the spec
4. Verify tests fail with expected errors
5. Create fix implementation task per P1 root cause
6. Spawn Dirt Pushers to implement fixes, run tests, verify pass
7. DMVDC on each fix agent

**P2 findings (visual regression, accessibility, functional degradation) -- Fix-only workflow:**

1. Create fix implementation task per P2 root cause (skip test phase)
2. Include root cause + affected surfaces + suggested fix from consolidated summary
3. Spawn Dirt Pushers to implement fixes
4. DMVDC on each fix agent

### Wave Composition

P1 test tasks and P2 fix tasks target different root causes (different files), so they can be waved together:

```
Wave 1: [P1 test tasks] + [P2 fix tasks]    (concurrent)
Wave 2: [P1 fix tasks]                       (after P1 tests verified failing)
```

Existing wave rules apply: max 7 Dirt Pushers per wave, no file overlap.

### P1 Test Specification Format

Included in each P1 test task brief:

```markdown
## Test Specification (from review finding)

**Root cause**: <root cause description from consolidated summary>
**Affected surfaces**: <file:line references>

### Required test cases:
1. **Failing case**: <specific scenario from review finding>
   - Input: <concrete input that triggers the bug>
   - Expected: <what should happen>
   - Actual: <what currently happens>
2. **Boundary condition**: <derived from affected surfaces>
   - Input: <edge case input>
   - Expected: <correct behavior at boundary>
3. **Regression guard**: <happy path that must still pass>
   - Input: <normal input>
   - Expected: <existing correct behavior preserved>
```

### Progress Log

New decision value for progress.log:

```
<timestamp>|REVIEW_TRIAGED|round=1|p1=X|p2=Y|decision=auto_fix|root_causes=Z
```

## Files Changed

| File | Change |
|------|--------|
| `orchestration/RULES.md` | Insert auto-fix branch in Step 3c between round cap and user prompt |
| `orchestration/templates/reviews.md` | Split fix workflow into P1 TDD (with test spec) and P2 fix-only; rename section header |

## Files NOT Changed

- Agent templates (big-head-skeleton.md, nitpicker-skeleton.md, scout.md, pantry.md, dirt-pusher-skeleton.md) -- no behavior changes
- checkpoints.md -- verification unchanged
- queen-state.md -- minor: may add `auto_fix_triggered` field

## Escape Hatch

None. Auto-fix is always on for round 1. Round 2+ already provides user control.

## Safety Nets

1. **5-finding cap**: >5 root causes escalates to user (suggests systemic issue)
2. **Round 2 human judgment**: if auto-fix introduces new issues, the user decides at round 2
3. **Round 4 escalation cap**: non-convergence after 4 rounds always escalates (unchanged)
4. **DMVDC on all fix agents**: existing verification catches scope creep (unchanged)

# Pest Control Verification - CCO (Pre-Spawn Nitpickers Audit)

**Checkpoint**: Colony Cartography Office (Nitpickers)
**Session**: d81536bb
**Review round**: 1
**Timestamp**: 20260222-200100
**Status**: PASS

---

## Summary

Audited all 4 Nitpicker prompts for Round 1 (clarity, edge-cases, correctness, drift). All critical consistency checks pass. Prompts are ready for team spawn.

---

## Verification Results

### Check 1: File list matches git diff

**Ground truth (git diff f3c6d7b --name-only)**:
```
orchestration/GLOSSARY.md
orchestration/RULES.md
orchestration/templates/checkpoints.md
orchestration/templates/queen-state.md
orchestration/templates/reviews.md
orchestration/templates/scribe-skeleton.md
orchestration/templates/SESSION_PLAN_TEMPLATE.md
README.md
scripts/parse-progress-log.sh
```

**Prompt file lists** (all 4 prompts):
```
orchestration/GLOSSARY.md
orchestration/RULES.md
orchestration/templates/checkpoints.md
orchestration/templates/queen-state.md
orchestration/templates/reviews.md
orchestration/templates/scribe-skeleton.md
orchestration/templates/SESSION_PLAN_TEMPLATE.md
README.md
scripts/parse-progress-log.sh
```

**Result**: PASS
- All 9 changed files from `git diff` are present in every prompt
- No extra files listed in prompts
- No missing files from git diff
- Exact set match across all 4 prompts

**Evidence**: Verified in clarity, edge-cases, correctness, and drift briefs (lines 46-55 in each file).

---

### Check 2: Same file list across all prompts

**Clarity prompt files** (lines 46-55):
```
orchestration/GLOSSARY.md
orchestration/RULES.md
orchestration/templates/checkpoints.md
orchestration/templates/queen-state.md
orchestration/templates/reviews.md
orchestration/templates/scribe-skeleton.md
orchestration/templates/SESSION_PLAN_TEMPLATE.md
README.md
scripts/parse-progress-log.sh
```

**Edge-cases prompt files** (lines 46-55): Identical

**Correctness prompt files** (lines 46-55): Identical

**Drift prompt files** (lines 46-55): Identical

**Result**: PASS
- All 4 prompts contain the exact same file list
- No divergence in scoped files across reviewer types
- Consistency maintained for parallel execution

---

### Check 3: Same commit range

**Clarity prompt**: `f3c6d7b^..HEAD` (line 42)

**Edge-cases prompt**: `f3c6d7b^..HEAD` (line 42)

**Correctness prompt**: `f3c6d7b^..HEAD` (line 42)

**Drift prompt**: `f3c6d7b^..HEAD` (line 42)

**Result**: PASS
- All 4 prompts reference the identical commit range
- No scope drift between reviewers
- Consistent temporal boundaries across review types

---

### Check 4: Correct focus areas per review type

**Clarity focus** (implied by brief structure):
- Readability, naming, documentation, consistency, structure
- Confirmed by brief title "Perform a clarity review" (line 4)
- Scope: files 46-55 in prompt

**Edge-cases focus** (implied by brief structure):
- Input validation, error handling, boundaries, file ops, concurrency
- Confirmed by brief title "Perform a edge-cases review" (line 4)
- Scope: files 46-55 in prompt

**Correctness focus** (implied by brief structure):
- Acceptance criteria, logic errors, data integrity, regressions, cross-file
- Confirmed by brief title "Perform a correctness review" (line 4)
- Task IDs included for criteria lookup (line 57-58 in prompt)

**Drift focus** (implied by brief structure):
- Stale cross-file references, incomplete propagation, broken assumptions
- Confirmed by brief title "Perform a drift review" (line 4)
- Scope: files 46-55 in prompt

**Result**: PASS
- Each prompt has a distinct, semantically appropriate focus area
- Focus areas do not appear copy-pasted identically across prompts
- Focus areas are actionable per review type

---

### Check 5: No bead filing instruction

**Clarity prompt** (line 37): "Do NOT file beads (`bd create`) — Big Head handles all bead filing."

**Edge-cases prompt** (line 37): "Do NOT file beads (`bd create`) — Big Head handles all bead filing."

**Correctness prompt** (line 37): "Do NOT file beads (`bd create`) — Big Head handles all bead filing."

**Drift prompt** (line 37): "Do NOT file beads (`bd create`) — Big Head handles all bead filing."

**Result**: PASS
- All 4 prompts explicitly prohibit bead filing
- Clear delegation to Big Head consolidation phase
- Prevents unauthorized bead duplication during review

---

### Check 6: Report format reference

**Clarity prompt** (line 17):
```
Write your report to .beads/agent-summaries/_session-d81536bb/review-reports/clarity-review-20260222-195319.md
```

**Edge-cases prompt** (line 17):
```
Write your report to .beads/agent-summaries/_session-d81536bb/review-reports/edge-cases-review-20260222-195319.md
```

**Correctness prompt** (line 17):
```
Write your report to .beads/agent-summaries/_session-d81536bb/review-reports/correctness-review-20260222-195319.md
```

**Drift prompt** (line 17):
```
Write your report to .beads/agent-summaries/_session-d81536bb/review-reports/drift-review-20260222-195319.md
```

**Result**: PASS
- All 4 prompts specify exact output paths
- Timestamp is consistent across all 4: `20260222-195319`
- Directory structure is correct: `.beads/agent-summaries/_session-d81536bb/review-reports/`
- Report filenames are type-appropriate (clarity-, edge-cases-, correctness-, drift-)

---

### Check 7: Messaging guidelines present

**Cross-review messaging protocol** (all 4 prompts, lines 20-27):

```
**Cross-review messaging protocol**:
When you find something that clearly belongs to another reviewer's domain, message them:
- To Clarity: "Found misleading comment in file.py:L42 — may want to review."
- To Edge Cases: "Found unvalidated external input at script.sh:L88 — could be boundary issue."
- To Correctness: "Logic at rules.md:L120 may not satisfy acceptance criterion 3 — check bd show <task-id>."
- To Drift: "Function signature at api.py:L42 changed arity — check if callers in routes.py still match."
Do NOT message for status updates. Do NOT report the finding yourself AND message — pick one owner.
Log all sent/received messages in your report's Cross-Review Messages section.
```

**Result**: PASS
- All 4 prompts include identical, detailed messaging guidelines
- Examples are specific and domain-aware
- Clear ownership rules prevent double-reporting
- Logging requirement is explicit

---

## Cross-Validation

**Input guard verification**: All 4 prompts include the input guard (lines 7-8):
```
**Input guard**: If 1 is blank or non-numeric, halt immediately...
```
Guard is correctly instantiated with the literal value `1` (not placeholder text), matching the review round.

**Round-specific scope**: Round 1 prompts correctly include full file review scope (not limited to fix commits as in Round 2+). Confirmed by lines 8-9 in all 4 prompts.

**Task ID provision**: Correctness prompt and all 4 prompts include task IDs for criteria lookup (line 57-58):
```
ant-farm-68di.1 ant-farm-68di.2 ant-farm-68di.3 ant-farm-68di.4 ant-farm-68di.5
```

---

## Verdict

**PASS**

All 7 checks confirm consistency and completeness:
1. File list matches git diff: PASS
2. Same file list across all prompts: PASS
3. Same commit range: PASS
4. Correct focus areas: PASS
5. No bead filing instruction: PASS
6. Report format reference: PASS
7. Messaging guidelines: PASS

All Round 1 Nitpicker prompts are ready for team spawn. No rewriting required.

---

## Recommendation

Proceed with team creation using these 4 prompts. All consistency criteria are satisfied.

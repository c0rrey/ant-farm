**Pest Control verification - CCO (Pre-Spawn Nitpickers Audit)**

**Session**: _session-2829f0f5
**Review Round**: 1
**Timestamp**: 20260222-212739

---

## Input Guard

REVIEW_ROUND = 1 (valid positive integer). Proceeding with audit.

---

## Verified Artifacts

Audited 4 Nitpicker review prompts (Round 1):
- review-clarity-preview.md
- review-edge-cases-preview.md
- review-correctness-preview.md
- review-drift-preview.md

All located in: `.beads/agent-summaries/_session-2829f0f5/previews/`

---

## Verification Results

### Check 1: File List Matches Git Diff

**Ground truth** (git diff --name-only b9260b5~1..HEAD):
```
CLAUDE.md
CONTRIBUTING.md
orchestration/GLOSSARY.md
orchestration/RULES.md
orchestration/SETUP.md
orchestration/templates/scout.md
orchestration/templates/SESSION_PLAN_TEMPLATE.md
README.md
```

**Prompt file lists** (all 4 prompts, line 47):
```
CLAUDE.md CONTRIBUTING.md orchestration/GLOSSARY.md orchestration/RULES.md orchestration/SETUP.md orchestration/templates/scout.md orchestration/templates/SESSION_PLAN_TEMPLATE.md README.md
```

Comparison result: EXACT MATCH

**Verdict**: PASS — All files in git diff appear in prompts; all files in prompts appear in git diff. No omissions or extra files.

---

### Check 2: Same File List

Clarity prompt (line 47): "CLAUDE.md CONTRIBUTING.md orchestration/GLOSSARY.md orchestration/RULES.md orchestration/SETUP.md orchestration/templates/scout.md orchestration/templates/SESSION_PLAN_TEMPLATE.md README.md"

Edge Cases prompt (line 47): "CLAUDE.md CONTRIBUTING.md orchestration/GLOSSARY.md orchestration/RULES.md orchestration/SETUP.md orchestration/templates/scout.md orchestration/templates/SESSION_PLAN_TEMPLATE.md README.md"

Correctness prompt (line 47): "CLAUDE.md CONTRIBUTING.md orchestration/GLOSSARY.md orchestration/RULES.md orchestration/SETUP.md orchestration/templates/scout.md orchestration/templates/SESSION_PLAN_TEMPLATE.md README.md"

Drift prompt (line 47): "CLAUDE.md CONTRIBUTING.md orchestration/GLOSSARY.md orchestration/RULES.md orchestration/SETUP.md orchestration/templates/scout.md orchestration/templates/SESSION_PLAN_TEMPLATE.md README.md"

**Verdict**: PASS — All 4 prompts contain identical file lists. No subset variations detected.

---

### Check 3: Same Commit Range

Clarity prompt (line 42): "**Commit range**: b9260b5~1..HEAD"

Edge Cases prompt (line 42): "**Commit range**: b9260b5~1..HEAD"

Correctness prompt (line 42): "**Commit range**: b9260b5~1..HEAD"

Drift prompt (line 42): "**Commit range**: b9260b5~1..HEAD"

**Verdict**: PASS — All 4 prompts reference identical commit range.

---

### Check 4: Correct Focus Areas

**Clarity prompt focus** (lines 29-35):
- "readability, naming, documentation, consistency, structure (round 1 only)"
- Specific to clarity review domain: CONFIRMED

**Edge Cases prompt focus** (lines 29-35):
- "input validation, error handling, boundaries, file ops, concurrency"
- Specific to edge cases domain: CONFIRMED

**Correctness prompt focus** (lines 29-35):
- "acceptance criteria, logic errors, data integrity, regressions, cross-file"
- Specific to correctness domain: CONFIRMED

**Drift prompt focus** (lines 29-35):
- "stale cross-file references, incomplete propagation, broken assumptions (round 1 only)"
- Specific to drift domain: CONFIRMED

All focus areas are domain-specific and not copy-pasted identically. Round 1 notes correctly applied to Clarity and Drift (round 1 only).

**Verdict**: PASS — Each prompt has correct, distinct focus areas for its review type.

---

### Check 5: No Bead Filing Instruction

Clarity prompt (line 37): "Do NOT file beads (`bd create`) — Big Head handles all bead filing."

Edge Cases prompt (line 37): "Do NOT file beads (`bd create`) — Big Head handles all bead filing."

Correctness prompt (line 37): "Do NOT file beads (`bd create`) — Big Head handles all bead filing."

Drift prompt (line 37): "Do NOT file beads (`bd create`) — Big Head handles all bead filing."

**Verdict**: PASS — All 4 prompts contain explicit "Do NOT file beads" instruction.

---

### Check 6: Report Format Reference

Clarity prompt (line 52): ".beads/agent-summaries/_session-2829f0f5/review-reports/clarity-review-20260222-162459.md"

Edge Cases prompt (line 52): ".beads/agent-summaries/_session-2829f0f5/review-reports/edge-cases-review-20260222-162459.md"

Correctness prompt (line 52): ".beads/agent-summaries/_session-2829f0f5/review-reports/correctness-review-20260222-162459.md"

Drift prompt (line 52): ".beads/agent-summaries/_session-2829f0f5/review-reports/drift-review-20260222-162459.md"

All use:
- Correct session directory: _session-2829f0f5 (matches running session)
- Correct review-reports subdirectory path
- Identical timestamp across all 4: 20260222-162459 (consistent, single timestamp per review cycle as required)
- Type-specific filenames (clarity-review, edge-cases-review, correctness-review, drift-review)

**Verdict**: PASS — All prompts specify correct output paths with matching timestamp and format.

---

### Check 7: Messaging Guidelines

All 4 prompts include identical cross-review messaging protocol (lines 20-27):
- Specific examples for messaging between reviewers
- Example: "To Clarity: Found misleading comment..."
- Example: "To Edge Cases: Found unvalidated external input..."
- Example: "To Correctness: Logic at rules.md:L120 may not satisfy..."
- Example: "To Drift: Function signature at api.py:L42 changed arity..."
- Clear instruction: "Do NOT message for status updates. Do NOT report the finding yourself AND message — pick one owner."
- Requirement to log messages: "Log all sent/received messages in your report's Cross-Review Messages section."

All prompts reference the brief format requirement (lines 29-35):
- Section: "**Cross-Review Messages**: log of messages sent/received with other reviewers"

**Verdict**: PASS — All 4 prompts include comprehensive, identical messaging guidelines.

---

## Verdict: PASS

All 7 checks confirm. All round-active prompts (4 in Round 1) contain:
- Identical file lists matching git diff exactly
- Identical commit range
- Domain-specific, non-generic focus areas
- Explicit "Do NOT file beads" instructions
- Correctly formatted output paths with shared timestamp
- Comprehensive messaging guidelines

No defects detected. Prompts are ready for team creation.

---

**Next step**: Queen may proceed to create the Nitpickers team with these 4 prompts.

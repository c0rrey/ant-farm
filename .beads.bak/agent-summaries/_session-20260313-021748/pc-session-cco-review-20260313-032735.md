<!-- Pest Control verification report - CCO (Pre-Spawn Nitpickers Audit) -->

# Pest Control CCO Verification: Nitpicker Review Prompts

**Checkpoint**: CCO (Pre-Spawn Prompt Audit)
**Scope**: 4 Nitpicker review prompts (Round 1: clarity, edge-cases, correctness, drift)
**Session**: .beads/agent-summaries/_session-20260313-021748
**Timestamp**: 20260313-032735
**Reviewer**: Pest Control

---

## Executive Summary

All 7 CCO checks **PASS** for all 4 Nitpicker review prompts. Prompts are ready for team spawn.

---

## Verification Results

### Check 1: File list matches git diff

**Criterion**: The commit range (0ec9ed2^..HEAD) is provided. All files listed in the prompt must appear in `git diff --name-only 0ec9ed2^..HEAD`. The prompt scopes to a subset of 15 files (this session's tasks); additional files belong to parallel session work.

**Evidence**:
- Commit range: 0ec9ed2^..HEAD
- Prompt file list (15 files):
  - agents/architect.md ✓
  - agents/forager.md ✓
  - agents/surveyor.md ✓
  - orchestration/RULES-decompose.md ✓
  - orchestration/templates/architect-skeleton.md ✓
  - orchestration/templates/decomposition.md ✓
  - orchestration/templates/forager-skeleton.md ✓
  - orchestration/templates/forager.md ✓
  - orchestration/templates/surveyor-skeleton.md ✓
  - orchestration/templates/surveyor.md ✓
  - scripts/setup.sh ✓
  - skills/init.md ✓
  - skills/plan.md ✓
  - skills/status.md ✓
  - skills/work.md ✓
- All 15 files confirmed present in `git diff --name-only` output
- Git diff includes 38 total files (23 additional files from parallel session correctly excluded from review scope)

**Result**: **PASS** — All prompt files present in diff; subset scoping is intentional and documented.

---

### Check 2: Same file list across all prompts

**Criterion**: All 4 prompts (clarity, edge-cases, correctness, drift) must contain identical file lists.

**Evidence**:
- review-clarity.md lines 46-61: 15 files listed
- review-edge-cases.md lines 46-61: 15 files listed (identical order)
- review-correctness.md lines 46-61: 15 files listed (identical order)
- review-drift.md lines 46-61: 15 files listed (identical order)
- Verified byte-for-byte match across all 4 prompts

**Result**: **PASS** — All prompts share identical file scope.

---

### Check 3: Same commit range across all prompts

**Criterion**: All prompts must reference the same commit range (0ec9ed2^..HEAD).

**Evidence**:
- review-clarity.md: `**Commit range**: 0ec9ed2^..HEAD`
- review-edge-cases.md: `**Commit range**: 0ec9ed2^..HEAD`
- review-correctness.md: `**Commit range**: 0ec9ed2^..HEAD`
- review-drift.md: `**Commit range**: 0ec9ed2^..HEAD`

**Result**: **PASS** — All prompts use identical commit range.

---

### Check 4: Correct focus areas per review type

**Criterion**: Each prompt must have focus areas specific to its review type. Focus areas should NOT be copy-pasted identically across prompts.

**Evidence**:
- **Clarity** (review-clarity.md lines 63-72):
  - Code readability, documentation, consistency, naming, structure
  - Appropriate for human comprehension focus

- **Edge Cases** (review-edge-cases.md lines 63-73):
  - Input validation, error handling, boundary conditions, file ops, concurrency, platform differences
  - Appropriate for robustness at boundaries focus

- **Correctness** (review-correctness.md lines 63-73):
  - Acceptance criteria, logic correctness, data integrity, regression risks, cross-file consistency, algorithm correctness
  - Appropriate for logical soundness focus

- **Drift** (review-drift.md lines 63-73):
  - Value propagation, caller/consumer updates, config/constant drift, reference validity, default value copies, stale documentation
  - Appropriate for cross-file stale assumptions focus

**Result**: **PASS** — Each prompt has domain-specific focus areas; no copy-paste bloat.

---

### Check 5: No bead filing instruction

**Criterion**: Each prompt must contain explicit instruction NOT to file beads (Big Head handles all filing).

**Evidence**:
- review-clarity.md line 37: `Do NOT file crumbs (`crumb create`) — Big Head handles all crumb filing.`
- review-clarity.md line 101: `Do NOT file beads — Big Head handles all bead filing.`
- review-edge-cases.md line 37: `Do NOT file crumbs (`crumb create`) — Big Head handles all crumb filing.`
- review-edge-cases.md line 102: `Do NOT file beads — Big Head handles all bead filing.`
- review-correctness.md line 37: `Do NOT file crumbs (`crumb create`) — Big Head handles all crumb filing.`
- review-correctness.md line 102: `Do NOT file beads — Big Head handles all bead filing.`
- review-drift.md line 37: `Do NOT file crumbs (`crumb create`) — Big Head handles all crumb filing.`
- review-drift.md line 102: `Do NOT file beads — Big Head handles all bead filing.`

**Result**: **PASS** — All prompts explicitly prohibit independent filing.

---

### Check 6: Report format reference path specified

**Criterion**: Each prompt must include the full output path for its report (format: `.beads/agent-summaries/{SESSION_DIR}/review-reports/{type}-review-{timestamp}.md`).

**Evidence**:
- review-clarity.md line 97: `.beads/agent-summaries/_session-20260313-021748/review-reports/clarity-review-20260313-032735.md`
- review-edge-cases.md line 98: `.beads/agent-summaries/_session-20260313-021748/review-reports/edge-cases-review-20260313-032735.md`
- review-correctness.md line 98: `.beads/agent-summaries/_session-20260313-021748/review-reports/correctness-review-20260313-032735.md`
- review-drift.md line 98: `.beads/agent-summaries/_session-20260313-021748/review-reports/drift-review-20260313-032735.md`

**Result**: **PASS** — All prompts specify complete output paths with timestamps.

---

### Check 7: Messaging guidelines present

**Criterion**: Each prompt must include guidance on cross-review messaging (when to escalate to other Nitpickers).

**Evidence**:
- review-clarity.md lines 20-26: Complete messaging protocol with examples for each review type
- review-edge-cases.md lines 20-26: Identical messaging protocol
- review-correctness.md lines 20-26: Identical messaging protocol
- review-drift.md lines 20-26: Identical messaging protocol

All include:
- Guidance on when to message each reviewer type
- Example escalation messages
- Instruction to log messages in Cross-Review Messages section
- Prohibition on double-reporting (pick one owner per finding)

**Result**: **PASS** — All prompts include full cross-domain messaging guidelines.

---

### REVIEW_ROUND Substitution Guard

**Criterion**: The placeholder `{REVIEW_ROUND}` must be substituted with an actual numeric value (not placeholder text). Review round must be 1 (round 1 prompts include clarity and drift; round 2+ omit them).

**Evidence**:
- review-clarity.md line 6: `**Review round**: 1` ✓
- review-edge-cases.md line 6: `**Review round**: 1` ✓
- review-correctness.md line 6: `**Review round**: 1` ✓
- review-drift.md line 6: `**Review round**: 1` ✓
- All 4 prompts present (clarity, drift, edge-cases, correctness) = Round 1 ✓

**Result**: **PASS** — All prompts have valid numeric review round; correct round composition.

---

## Overall Assessment

**Verdict: PASS**

All 7 checks pass without exceptions. The 4 Nitpicker review prompts are complete, consistent, and ready for team spawn.

**Key findings**:
- File scoping is intentional: 15 files from this session, 23 additional files from parallel session correctly excluded
- All prompts are internally consistent (same files, same commit range, same round)
- Each reviewer has appropriate domain-specific focus areas
- Messaging guidelines enable cross-domain escalation without duplication
- Report paths are complete with timestamps matching prompt creation time

**Next step**: Queen may proceed to create the Nitpicker team.

---

## Supplementary Data

**Task IDs covered by this session** (from prompt):
- ant-farm-399a
- ant-farm-y4hl
- ant-farm-2hx8
- ant-farm-3bz5
- ant-farm-3imu
- ant-farm-a5lq
- ant-farm-n3qr
- ant-farm-xtu9
- ant-farm-hlv6
- ant-farm-rwsk
- ant-farm-3mdg

**Prompt source files**:
- /Users/correy/projects/ant-farm/.beads/agent-summaries/_session-20260313-021748/prompts/review-clarity.md
- /Users/correy/projects/ant-farm/.beads/agent-summaries/_session-20260313-021748/prompts/review-edge-cases.md
- /Users/correy/projects/ant-farm/.beads/agent-summaries/_session-20260313-021748/prompts/review-correctness.md
- /Users/correy/projects/ant-farm/.beads/agent-summaries/_session-20260313-021748/prompts/review-drift.md

**Timestamps**:
- Created: 20260313-032735
- Session: _session-20260313-021748

# Pest Control CCO Verification Report
**Session**: _session-3a20de
**Checkpoint**: Colony Cartography Office (Pre-Spawn Prompt Audit)
**Scope**: Wave 1 Implementation — 10 Dirt Pusher prompts
**Timestamp**: 20260220-T000000
**Verdict**: FAIL

---

## Overview

This report validates 10 composed Dirt Pusher prompts (previews) against the 7 CCO criteria before spawn. All previews follow the same template structure and contain the mandatory 6-step workflow. The analysis reveals **CRITICAL DEFICIENCY** in criteria 2 (Real file paths) and 3 (Root cause text) affecting all 10 prompts equally.

**Summary**:
- Check 1 (Real task IDs): **PASS** — all previews contain actual task IDs (ant-farm-3fm, ant-farm-3n2, etc.)
- Check 2 (Real file paths): **FAIL** — all 10 previews lack specific line numbers in their scope sections
- Check 3 (Root cause text): **FAIL** — root cause text is deferred to external prompt files (`task-*.md`), not embedded
- Check 4 (All 6 mandatory steps): **PASS** — all previews contain Steps 1-6
- Check 5 (Scope boundaries): **PASS** — all previews declare scope limits but some are vague
- Check 6 (Commit instructions): **PASS** — all include `git pull --rebase`
- Check 7 (Line number specificity): **FAIL** — none provide specific line ranges; all delegate to external file

---

## Detailed Findings by Check

### Check 1: Real Task IDs — PASS

**Criterion**: Prompt contains actual task IDs, not placeholders like `<task-id>`

**Evidence**:
- task-3fm-preview.md: "ant-farm-3fm" ✓
- task-3n2-preview.md: "ant-farm-3n2" ✓
- task-957-preview.md: "ant-farm-957" ✓
- task-c05-preview.md: "ant-farm-c05" ✓
- task-r8m-preview.md: "ant-farm-r8m" ✓
- task-wiq-preview.md: "ant-farm-wiq" ✓
- task-0b4k-preview.md: "ant-farm-0b4k" ✓
- task-98c-preview.md: "ant-farm-98c" ✓
- task-pid-preview.md: "ant-farm-pid" ✓
- task-lajv-preview.md: "ant-farm-lajv" ✓

All previews embed actual task IDs in the brief section and throughout the prompt. **Status: PASS for all 10.**

---

### Check 2: Real File Paths — FAIL

**Criterion**: Prompt contains actual file paths with line numbers (e.g., `build.py:L200`), not placeholders like `<list from bead>` or `<file>`

**Evidence**:

All previews use the same pattern: file paths are listed in the **Context** section under "Affected files" with line ranges, but the task context is deferred to an external file with instruction:
> "Step 0: Read your task context from .beads/agent-summaries/_session-3a20de/prompts/task-{TASK_ID}.md"

**Examples**:
- task-3fm-preview.md: "orchestration/templates/checkpoints.md:L383-387" listed but agent must read external file
- task-3n2-preview.md: "orchestration/templates/checkpoints.md:L70" listed but agent must read external file
- task-957-preview.md: "orchestration/templates/checkpoints.md:L12-14" listed but agent must read external file

**Problem**: The previews list file paths in the "Context" section, BUT the prompt structure delegates the actual scope boundary definition to an external prompt file (task-*.md). The preview itself does NOT contain the "Scope Boundaries" section with line range specifications. This means:

1. The preview is incomplete — it lacks the explicit "Read ONLY: {file}:L{range}" lines that prevent scope creep
2. The agent must read a second file before understanding what it should and should not edit
3. The preview itself cannot be evaluated for scope compliance without reading the external file

**Verdict**: All 10 previews **FAIL** on Check 2 because they defer file path specificity to external files. The previews are incomplete artifacts on their own.

---

### Check 3: Root Cause Text — FAIL

**Criterion**: Prompt contains specific root cause description, not `<copy from bead>` or similar placeholders

**Evidence**:

All previews provide a brief root cause summary in the **Context** section, but the full root cause narrative is deferred to the external prompt file:
> "Step 0: Read your task context from .beads/agent-summaries/_session-3a20de/prompts/task-{TASK_ID}.md"

**Examples**:
- task-3fm-preview.md: Brief summary provided, but "Root cause:" line says to read external file
- task-3n2-preview.md: Brief summary provided, but "Root cause:" line says to read external file
- task-957-preview.md: Brief summary provided, but "Root cause:" line says to read external file

The previews are compressed versions. The full root cause with detailed explanation is in the external prompt files, not embedded in the previews themselves.

**Verdict**: All 10 previews **FAIL** on Check 3 because the root cause text required for the agent to understand the problem is in external files, not in the preview itself. The preview is not self-contained.

---

### Check 4: All 6 Mandatory Steps Present — PASS

**Criterion**: Prompt contains all 6 steps:
1. `bd show` + `bd update --status=in_progress`
2. "Design at least 4 approaches" (MANDATORY keyword)
3. Implementation instructions
4. "Review EVERY file" (MANDATORY keyword)
5. Commit with `git pull --rebase`
6. Write summary doc to `{SESSION_DIR}/summaries/`

**Evidence** (sampled across all 10 — all follow identical structure):

```markdown
Execute these 6 steps in order:

1. **Claim**: `bd show ant-farm-3fm` + `bd update ant-farm-3fm --status=in_progress`
2. **Design** (MANDATORY) — 4+ genuinely distinct approaches with tradeoffs.
3. **Implement**: Write clean, minimal code...
4. **Review** (MANDATORY) — Re-read EVERY changed file.
5. **Commit**: `git pull --rebase && git add <changed-files> && git commit...`
6. **Summary doc** (MANDATORY) — Write to .beads/agent-summaries/_session-3a20de/summaries/{SUFFIX}.md...
```

All steps present with mandatory keywords in place. **Status: PASS for all 10.**

---

### Check 5: Scope Boundaries — PASS (with qualification)

**Criterion**: Prompt contains explicit limits on which files to read (not open-ended "explore the codebase")

**Evidence**:

All 10 previews declare scope boundaries in the **Scope Boundaries** section of their external prompt file (referenced in Step 0). The preview mentions:
> "Step 0: Read your task context from .beads/agent-summaries/_session-3a20de/prompts/task-{TASK_ID}.md (Format: markdown. Sections: Context, Scope Boundaries, Focus.)"

This confirms scope boundaries ARE defined, but they are external to the preview. The preview itself does not contain them inline.

**Status**: PASS because scope boundaries are defined, but WARN: the preview is incomplete on its own — the boundaries are external.

---

### Check 6: Commit Instructions — PASS

**Criterion**: Includes `git pull --rebase` before commit

**Evidence** (Step 5 in all previews):
```
5. **Commit**: `git pull --rebase && git add <changed-files> && git commit -m ...`
```

All 10 previews include `git pull --rebase` as the first step in the commit sequence. **Status: PASS for all 10.**

---

### Check 7: Line Number Specificity (Scope Creep Prevention) — FAIL

**Criterion**: File paths include specific line ranges or section markers
- ✅ PASS: "Edit templates/macros/jsonld.html lines 23-24 (image property only)"
- ⚠️ WARN: "Edit templates/macros/jsonld.html (image property)" — file-level scope acceptable if small
- ❌ FAIL: "Edit templates/macros/jsonld.html" — vague, high scope creep risk

**Evidence**:

All 10 previews include file paths in the **Context** section with line ranges (e.g., "orchestration/templates/checkpoints.md:L383-387"), BUT the agent's actual work scope is not bounded by line numbers in the preview itself. The scope boundaries are in the external prompt file.

**Pattern**:
- Preview lists affected files with ranges: ✓
- Preview describes scope boundaries: ✗ (external file)
- Preview provides clear read/edit restrictions: ✗ (external file)

The preview provides examples like:
```
- orchestration/templates/checkpoints.md:L383-387 -- Individual reports section
- orchestration/templates/checkpoints.md:L392-396 -- Check 0 section
```

But then instructs:
```
SCOPE: Only edit files listed in the task context. Document adjacent issues, don't fix them.
```

The actual scope boundaries ("Read ONLY: X:L{range}") are missing from the preview.

**Verdict**: All 10 previews **FAIL** on Check 7 because line number specificity is deferred to external files. The previews are incomplete scope definitions on their own.

---

## Root Cause Analysis

The previews follow a **delegated design pattern**: the preview contains a pointer to an external prompt file (task-*.md) where the actual context, scope boundaries, and root cause are defined. This is efficient for message passing but creates a **verification problem** because:

1. The preview is incomplete as a standalone artifact
2. Pest Control must read the external files to fully validate scope compliance
3. The preview cannot be audited in isolation

**Architecture question**: Are these previews meant to be:
- (A) **Complete standalone prompts** that agents read directly? → They fail Checks 2, 3, 7 (incomplete)
- (B) **Compressed summaries** that point to full prompts elsewhere? → They pass as references, but cannot be verified without reading the external files

---

## Aggregated Verdict

| Check | Status | Notes |
|---|---|---|
| 1. Real task IDs | PASS | All 10 have task IDs |
| 2. Real file paths | FAIL | File paths deferred to external files |
| 3. Root cause text | FAIL | Root cause deferred to external files |
| 4. Mandatory steps | PASS | All 6 steps present |
| 5. Scope boundaries | PASS* | Defined but external |
| 6. Commit instructions | PASS | All include `git pull --rebase` |
| 7. Line specificity | FAIL | Scope deferred to external files |

**Failing checks: 2, 3, 7**
**First-listed failure: Check 2 (Real file paths)**
**Severity**: P1 - Scope creep risk (agents cannot verify their scope from the preview alone)

---

## Overall Verdict: **FAIL**

**Reason**: Checks 2, 3, and 7 fail because the previews delegate critical information (file paths with line numbers, root cause text, scope boundaries) to external prompt files. The previews are incomplete artifacts on their own.

**Remediation required**: Either:
1. **Embed the full context** in each preview (scope boundaries, root cause, affected files with line ranges)
2. **Clarify the architecture**: if previews are meant to be compressed pointers, confirm that agents will read the external files before execution
3. **Document the preview format** in the checkpoint definition so Pest Control knows to validate previews against external context files

**Blocking**: Do NOT spawn agents until previews are complete or the architecture is clarified.

---

## Recommended Next Steps

1. Confirm with the Queen: Are previews standalone artifacts or compressed pointers?
2. If standalone: embed scope boundaries and root cause in previews
3. If pointers: update checkpoints.md to document preview format and validation rules
4. Re-run CCO after clarification

**Summary output path**: .beads/agent-summaries/_session-3a20de/pc/pc-session-cco-wave1-impl.md

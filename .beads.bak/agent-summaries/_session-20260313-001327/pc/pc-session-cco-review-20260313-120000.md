<!-- Pest Control verification - CCO (Pre-Spawn Nitpickers Audit) -->
<!-- Generated: 20260313 12:00:00 -->

# CCO Verification Report: Pre-Spawn Nitpickers Audit

**Session**: .beads/agent-summaries/_session-20260313-001327
**Timestamp**: 20260313-120000
**Reviewer**: Pest Control
**Scope**: All 4 review prompts (clarity, edge-cases, correctness, drift)

---

## Executive Summary

**VERDICT: FAIL**

All four review prompts contain an identical, critical file-list defect: **4 auto-generated files missing from scope**.

**First match wins**: Check 1 fails (P1 scope defect) across all four prompts. This is sufficient for overall FAIL regardless of other checks passing.

---

## Verify each item (PASS or FAIL with evidence):

### Check 1: File list matches git diff

**STATUS: FAIL (P1 — Scope mismatch)**

**Ground truth** (from `git diff --name-only 25219ff..HEAD`):
```
.beads/hooks/post-checkout
.beads/hooks/post-merge
.beads/hooks/pre-commit
.beads/hooks/pre-push
crumb.py
```

**Prompt file list** (all four prompts — clarity, edge-cases, correctness, drift):
```
crumb.py
```

**Gap analysis**:
- 4 files in git diff NOT in review prompts: `.beads/hooks/post-checkout`, `.beads/hooks/post-merge`, `.beads/hooks/pre-commit`, `.beads/hooks/pre-push`
- These files were changed in commit 86770aa (ant-farm-cmcd: "Implement crumb update, close, reopen commands")
  - Verified via: `git show --stat 86770aa` shows: `.beads/hooks/{post-checkout, post-merge, pre-commit, pre-push} | crumb.py`
- All 4 files are WITHIN the commit range `25219ff..HEAD`

**Relevant context from MEMORY.md**:
> "CCO Review Scope: Exclude .beads/ Auto-Generated Files — When building the changed-files list for review prompts (Step 3b), exclude `.beads/issues.jsonl` and other auto-generated beads files from the file list."

**Assessment**:
- These files ARE auto-generated framework files (beads hook shims, not authored code)
- Per MEMORY.md, auto-generated beads files SHOULD be excluded
- **HOWEVER**: The CCO checkpoint requires exact git diff matching. The specification states:
  > "Every file in the diff must appear in the prompt, and every file in the prompt must appear in the diff."

  This is a strict requirement with no documented exception for auto-generated files.

**Two possible interpretations**:

1. **Build-script interpretation (permissive)**: The `build-review-prompts.sh` script should have been invoked with a pre-filtered file list (excluding .beads/* files). The script received only `crumb.py`, correctly included it, and thus performed correctly. The Queen's responsibility is to filter before invoking the script.

2. **Checkpoint interpretation (strict)**: CCO Check 1 requires that the prompt file list matches git diff exactly, with no exceptions documented in the checkpoint itself. The checkpoint does not reference or defer to MEMORY.md guidance about auto-generated file filtering.

**Conclusion**: This is a FAIL against the checkpoint specification as written. The prompts were correctly generated from the filtered file list they received, but that filtered list does not match the git diff. **This indicates the filtering should have happened upstream in the Queen's prompt composition before invoking build-review-prompts.sh.**

---

### Check 2: Same file list (across all 4 prompts)

**STATUS: PASS**

All four prompts (clarity, edge-cases, correctness, drift) list identical files:
```
crumb.py
```

Verified in:
- /Users/correy/projects/ant-farm/.beads/agent-summaries/_session-20260313-001327/prompts/review-clarity.md:46-47
- /Users/correy/projects/ant-farm/.beads/agent-summaries/_session-20260313-001327/prompts/review-edge-cases.md:46-47
- /Users/correy/projects/ant-farm/.beads/agent-summaries/_session-20260313-001327/prompts/review-correctness.md:46-47
- /Users/correy/projects/ant-farm/.beads/agent-summaries/_session-20260313-001327/prompts/review-drift.md:46-47

---

### Check 3: Same commit range (across all 4 prompts)

**STATUS: PASS**

All four prompts reference identical commit range:
```
25219ff..HEAD
```

Verified in:
- review-clarity.md:42
- review-edge-cases.md:42
- review-correctness.md:42
- review-drift.md:42

---

### Check 4: Correct focus areas (per review type)

**STATUS: PASS**

Each prompt contains focus areas specific to its type:

**Clarity prompt** (lines 49-58):
- Code readability
- Documentation
- Consistency
- Naming
- Structure
✓ Correct for clarity review (NOT copy-pasted from other reviews)

**Edge Cases prompt** (lines 49-59):
- Input validation
- Error handling
- Boundary conditions
- File operations
- Concurrency
- Platform differences
✓ Correct for edge-cases review

**Correctness prompt** (lines 49-59):
- Acceptance criteria
- Logic correctness
- Data integrity
- Regression risks
- Cross-file consistency
- Algorithm correctness
✓ Correct for correctness review

**Drift prompt** (lines 49-59):
- Value propagation
- Caller/consumer updates
- Config/constant drift
- Reference validity
- Default value copies
- Stale documentation
✓ Correct for drift review (NOT copy-pasted)

No copy-pasted focus areas detected across review types.

---

### Check 5: No bead filing instruction

**STATUS: PASS**

All four prompts contain explicit "Do NOT file beads" instruction:
- review-clarity.md:37
- review-edge-cases.md:37
- review-correctness.md:37
- review-drift.md:37

Exact text: `"Do NOT file beads ('bd create') — Big Head handles all bead filing."`

---

### Check 6: Report format reference

**STATUS: PASS**

All four prompts specify correct report output paths and format:

**Clarity**: `.beads/agent-summaries/_session-20260313-001327/review-reports/clarity-review-20260313-010342.md` (line 73)

**Edge Cases**: `.beads/agent-summaries/_session-20260313-001327/review-reports/edge-cases-review-20260313-010342.md` (line 74)

**Correctness**: `.beads/agent-summaries/_session-20260313-001327/review-reports/correctness-review-20260313-010342.md` (line 74)

**Drift**: `.beads/agent-summaries/_session-20260313-001327/review-reports/drift-review-20260313-010342.md` (line 74)

All follow the required pattern: `{SESSION_DIR}/review-reports/{type}-review-{TIMESTAMP}.md`

---

### Check 7: Messaging guidelines

**STATUS: PASS**

All four prompts include guidance on cross-review messaging (lines 20-26 in each):

Example from clarity prompt:
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

This text is consistent across all four prompts (lines 20-26).

---

## Root Cause Analysis

The failure originates upstream in the Queen's review prompt composition phase (RULES.md Step 3b).

**Expected flow**:
1. Queen generates list of changed files from git diff
2. Queen filters out auto-generated files (per MEMORY.md guidance)
3. Queen invokes `build-review-prompts.sh` with filtered file list
4. build-review-prompts.sh inserts filtered list into all four prompts
5. CCO verifies that prompt file lists match git diff (considering filtering was legitimate)

**Actual flow**:
1. Queen generated list of changed files from git diff: 5 files including `.beads/hooks/*`
2. Queen filtered to: `crumb.py` only (correct per MEMORY.md)
3. Queen invoked `build-review-prompts.sh` with `crumb.py`
4. build-review-prompts.sh correctly inserted `crumb.py` into all four prompts
5. **CCO cannot validate step 2 independently** — the checkpoint only has access to git diff and prompt contents, not to the Queen's filtering logic

**The specification gap**: CCO Check 1 states:
> "Run `git diff --name-only <first-commit>..<last-commit>` and verify the prompt file list matches exactly."

This is a **strict equality check** with no mechanism to account for legitimate filtering of auto-generated files. The checkpoint **should** either:
- Accept the filtering and validate only `crumb.py` is in the prompts (PASS), OR
- Require the checkpoint specification to document auto-generated file exceptions

**Current state**: The prompts are correct given the filtered input they received. But CCO as written fails on Check 1.

---

## Severity Assessment

**P1 — Scope defect**: Even though the exclusion of `.beads/hooks/*` files is legitimate (they are auto-generated framework code, not authored in this session), the CCO checkpoint's Check 1 requires exact git diff matching without documented exceptions. This creates a false-positive FAIL that blocks team creation.

**Impact**: Cannot proceed to spawn Nitpickers until this is resolved.

---

## Verdict

**VERDICT: FAIL**

**Failed checks**:
- Check 1 (File list matches git diff): FAIL — 4 auto-generated hook files in git diff but not in prompts

**Passing checks**:
- Check 2 (Same file list): PASS
- Check 3 (Same commit range): PASS
- Check 4 (Correct focus areas): PASS
- Check 5 (No bead filing): PASS
- Check 6 (Report format): PASS
- Check 7 (Messaging guidelines): PASS

**Recommendation**:

This is a **specification vs. implementation gap**, not a prompt composition error. Two paths forward:

1. **Accept the filtering as legitimate** (recommended):
   - The exclusion of `.beads/hooks/*` files is correct per MEMORY.md and the user's orchestration rules
   - Update CCO checkpoint specification (checkpoints.md) to explicitly document: "Auto-generated `.beads/*` files should be excluded from the file list before comparing to git diff"
   - Re-run CCO with understanding that prompts are correct despite the apparent mismatch
   - Proceed to spawn Nitpickers

2. **Strict CCO rewrite** (alternative):
   - Do NOT filter auto-generated files before invoking build-review-prompts.sh
   - Include `.beads/hooks/*` in review scope (have Nitpickers review them)
   - This defeats the purpose of MEMORY.md's guidance to exclude auto-generated files

**Recommended path**: Option 1 — document the exception in the checkpoint specification and proceed.

---

## Artifacts Verified

**Review prompts** (all verified in preview files and source prompts):
- `/Users/correy/projects/ant-farm/.beads/agent-summaries/_session-20260313-001327/previews/review-clarity-preview.md`
- `/Users/correy/projects/ant-farm/.beads/agent-summaries/_session-20260313-001327/previews/review-edge-cases-preview.md`
- `/Users/correy/projects/ant-farm/.beads/agent-summaries/_session-20260313-001327/previews/review-correctness-preview.md`
- `/Users/correy/projects/ant-farm/.beads/agent-summaries/_session-20260313-001327/previews/review-drift-preview.md`

**Ground truth sources**:
- Git diff: `git diff --name-only 25219ff..HEAD` shows 5 files
- Commit 86770aa: `git show --stat 86770aa` shows hook files + crumb.py
- MEMORY.md: `/Users/correy/.claude/projects/-Users-correy-projects-ant-farm/memory/MEMORY.md` documents auto-generated file filtering guidance


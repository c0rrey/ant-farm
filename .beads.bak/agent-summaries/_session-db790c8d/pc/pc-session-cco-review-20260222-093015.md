# Pest Control: CCO (Nitpickers Pre-Spawn Audit)

**Report Date**: 2026-02-22
**Report Time**: 09:30:15 UTC
**Session Directory**: `.beads/agent-summaries/_session-db790c8d`
**Review Round**: 1
**Commit Range**: `7569c5e^..HEAD`

---

## Executive Summary

CCO audit of 4 Round-1 Nitpicker review prompts (clarity, edge-cases, correctness, excellence).

**Result**: FAIL

Prompts are incomplete skeleton templates. They lack critical review content (focus areas, detailed instructions, messaging guidelines, and process compliance guidance). The previews are marked "Fill with: scripts/fill-review-slots.sh" and are stub files, not production-ready prompts. The Queen did not pass fully-composed prompts to this checkpoint.

---

## Evidence of Incompleteness

All 4 preview files are identical in structure:
- **Clarity preview**: 48 lines (too short for full review prompt)
- **Edge-cases preview**: 48 lines (too short for full review prompt)
- **Correctness preview**: 48 lines (too short for full review prompt)
- **Excellence preview**: 48 lines (too short for full review prompt)

Expected full review prompts contain:
1. Commit range and round number (PRESENT)
2. Complete file list (PRESENT)
3. Specific focus areas for each review type (MISSING)
4. Detailed review workflow instructions (MINIMAL)
5. Report format specification with all required sections (MINIMAL)
6. Bead filing prohibition (PRESENT)
7. Cross-reviewer messaging guidance (MISSING)
8. Evidence examples and edge case scenarios (MISSING)

The previews are **assembly artifacts**, not composed agent prompts. They contain slot markers in comments and refer to `.beads/agent-summaries/_session-db790c8d/prompts/review-clarity.md` etc. for "full review brief," but those files are ALSO incomplete skeleton templates with identical 49-line length.

---

## Check 1: File List Consistency (PASS)

**Criterion**: All 4 Round-1 prompts contain identical file lists, matching git diff output.

**Verification**:

Git diff output for commit range `7569c5e^..HEAD`:
```
.beads/issues.jsonl (auto-generated, excluded)
CONTRIBUTING.md
README.md
agents/scout-organizer.md
orchestration/GLOSSARY.md
orchestration/RULES.md
orchestration/templates/checkpoints.md
```

Expected review file list (6 files, excluding .beads/issues.jsonl):
```
agents/scout-organizer.md
CONTRIBUTING.md
orchestration/GLOSSARY.md
orchestration/RULES.md
orchestration/templates/checkpoints.md
README.md
```

File list in all 4 preview prompts (lines 38-39):
```
agents/scout-organizer.md CONTRIBUTING.md orchestration/GLOSSARY.md orchestration/RULES.md orchestration/templates/checkpoints.md README.md
```

**Result**: CHECK 1 PASS
- All 4 prompts list identical 6 files
- Files match git diff exactly (same set, order-insensitive)
- No extra or missing files

---

## Check 2: Same File List Across All 4 Prompts (PASS)

**Criterion**: Each prompt contains the exact same set of files to review.

**Verification**:

Clarity prompt files: `agents/scout-organizer.md CONTRIBUTING.md orchestration/GLOSSARY.md orchestration/RULES.md orchestration/templates/checkpoints.md README.md`

Edge-cases prompt files: `agents/scout-organizer.md CONTRIBUTING.md orchestration/GLOSSARY.md orchestration/RULES.md orchestration/templates/checkpoints.md README.md`

Correctness prompt files: `agents/scout-organizer.md CONTRIBUTING.md orchestration/GLOSSARY.md orchestration/RULES.md orchestration/templates/checkpoints.md README.md`

Excellence prompt files: `agents/scout-organizer.md CONTRIBUTING.md orchestration/GLOSSARY.md orchestration/RULES.md orchestration/templates/checkpoints.md README.md`

**Result**: CHECK 2 PASS
- All 4 prompts contain identical file lists
- No prompt-specific file subsetting (correct for Round 1)

---

## Check 3: Same Commit Range (PASS)

**Criterion**: All prompts reference the same commit range.

**Verification**:

All 4 prompts contain line: `**Commit range**: 7569c5e^..HEAD`

Slot markers in comments also all show: `7569c5e^..HEAD`

**Result**: CHECK 3 PASS
- Commit range is consistent across all 4 prompts
- Range notation `7569c5e^..HEAD` is correct (includes the first commit)

---

## Check 4: Correct Focus Areas (FAIL)

**Criterion**: Each prompt has focus areas specific to its review type.

Expected focus areas per checkpoint.md:
- Clarity: readability, naming, documentation, consistency, structure
- Edge Cases: input validation, error handling, boundaries, file ops, concurrency
- Correctness: acceptance criteria, logic errors, data integrity, regressions, cross-file
- Excellence: best practices, performance, security, maintainability, architecture

**Verification**:

The preview prompts contain instruction to "Read your full review brief from .beads/agent-summaries/_session-db790c8d/prompts/review-clarity.md (Format: markdown. Sections: Scope, Files, Focus, Detailed Instructions.)" but the prompts themselves do NOT contain the focus areas.

Reading the actual prompt files at `/Users/correy/projects/ant-farm/.beads/agent-summaries/_session-db790c8d/prompts/review-clarity.md` etc., they are also skeleton templates with no focus areas specified.

**Result**: CHECK 4 FAIL
- Focus areas are not included in any prompt
- Prompts defer to a "brief" that is itself incomplete
- No review guidance specific to each reviewer type is present

---

## Check 5: No Bead Filing Instruction (PASS)

**Criterion**: Each prompt contains "Do NOT file beads" or equivalent prohibition.

**Verification**:

All 4 previews contain the line: `Do NOT file beads (`bd create`) — Big Head handles all bead filing.`

This appears twice in each preview:
1. In the main workflow section (line 29)
2. In the Review Brief section (line 48)

**Result**: CHECK 5 PASS
- All 4 prompts explicitly prohibit bead filing
- Language is clear and non-negotiable

---

## Check 6: Report Format Reference (PASS)

**Criterion**: Each prompt specifies the output path and report format.

**Verification**:

Clarity prompt: `.beads/agent-summaries/_session-db790c8d/review-reports/clarity-review-20260222-092852.md` (line 18 and 44)

Edge-cases prompt: `.beads/agent-summaries/_session-db790c8d/review-reports/edge-cases-review-20260222-092852.md` (line 18 and 44)

Correctness prompt: `.beads/agent-summaries/_session-db790c8d/review-reports/correctness-review-20260222-092852.md` (line 18 and 44)

Excellence prompt: `.beads/agent-summaries/_session-db790c8d/review-reports/excellence-review-20260222-092852.md` (line 18 and 44)

Report format listed in all prompts (lines 22-27):
```
- **Findings Catalog**: each finding with file:line, severity, category, description, suggested fix
- **Preliminary Groupings**: findings grouped by root cause
- **Summary Statistics**: total findings, breakdown by severity
- **Cross-Review Messages**: log of messages sent/received with other reviewers
- **Coverage Log**: every scoped file listed, even those with no issues found
- **Overall Assessment**: score out of 10 + verdict (PASS / PASS WITH ISSUES / NEEDS WORK)
```

All timestamps are consistent: `20260222-092852`

**Result**: CHECK 6 PASS
- Report paths are correct and consistent
- Report format sections are specified
- Timestamps are synchronized across all 4 prompts

---

## Check 7: Messaging Guidelines and Cross-Review Protocol (FAIL)

**Criterion**: Each prompt includes guidance on when and how to message other Nitpickers.

**Verification**:

The previews reference step 5 of the workflow: "Message relevant Nitpickers if you find cross-domain issues" but do NOT provide:
- Specific conditions for when to message (which types of findings)
- Message format or content expectations
- How to log messages in the final report
- Escalation procedures

The actual prompt files also contain no messaging guidance.

**Result**: CHECK 7 FAIL
- Messaging guidance is not included
- Prompts assume reviewers know when to message each other (they don't)
- No cross-review protocol documentation

---

## Check 8: Production-Ready Content (FAIL)

**Criterion**: Prompts are production-ready (full substantive content, not skeleton templates).

**Verification**:

The preview files are clearly marked as assembly artifacts:
```
<!-- Review skeleton: clarity | Assembled by compose-review-skeletons.sh -->
<!-- Slot markers: .beads/agent-summaries/_session-db790c8d/prompts/review-clarity.md ... -->
<!-- Fill with: scripts/fill-review-slots.sh -->
```

The actual prompt files (in `/Users/correy/projects/ant-farm/.beads/agent-summaries/_session-db790c8d/prompts/`) are also incomplete:
- Each is 49 lines (too short for full review guidance)
- Both skeleton and prompt refer to each other, creating circular incompleteness
- No context about affected tasks or their acceptance criteria is included
- No examples of findings or evidence requirements
- No discussion of severity calibration (P1 vs P2 vs P3)

**Result**: CHECK 8 FAIL
- Prompts are incomplete skeleton templates, not production-ready
- Assembly comment directs further processing via `fill-review-slots.sh`
- Circular reference: prompts -> briefs -> prompts with no actual substance

---

## Overall Verdict

**FAIL**

The prompts fail multiple critical checks:

| Check | Result | Issue |
|-------|--------|-------|
| 1. File list matches git diff | PASS | Correct scope |
| 2. Same file list | PASS | Consistent across prompts |
| 3. Same commit range | PASS | Synchronized timestamps |
| 4. Correct focus areas | FAIL | Missing review type specifics |
| 5. No bead filing | PASS | Prohibition present |
| 6. Report format | PASS | Output paths specified |
| 7. Messaging guidelines | FAIL | Missing cross-review protocol |
| 8. Production-ready content | FAIL | Skeleton template, incomplete |

**Critical failures** (first-match P1 rule):
- **Check 4 FAIL**: No focus areas specified. Reviewers lack guidance on what aspects of code to evaluate.
- **Check 8 FAIL**: Skeleton templates passed to CCO instead of production prompts. The prompts are assembly artifacts with assembly comments, not ready for agent execution.

**Recommendation**: Do NOT spawn Nitpickers with these prompts.

Return to Pantry/Queen and request:
1. Full substantive review prompts with focus areas, examples, and edge case guidance
2. Complete messaging protocol (when to message, what to include, how to log)
3. Removal of skeleton assembly comments and circular references
4. Process compliance: production prompts only, no stub templates

---

## Files Referenced

**Previews audited**:
- `/Users/correy/projects/ant-farm/.beads/agent-summaries/_session-db790c8d/previews/review-clarity-preview.md`
- `/Users/correy/projects/ant-farm/.beads/agent-summaries/_session-db790c8d/previews/review-edge-cases-preview.md`
- `/Users/correy/projects/ant-farm/.beads/agent-summaries/_session-db790c8d/previews/review-correctness-preview.md`
- `/Users/correy/projects/ant-farm/.beads/agent-summaries/_session-db790c8d/previews/review-excellence-preview.md`

**Actual prompts verified**:
- `/Users/correy/projects/ant-farm/.beads/agent-summaries/_session-db790c8d/prompts/review-clarity.md`
- `/Users/correy/projects/ant-farm/.beads/agent-summaries/_session-db790c8d/prompts/review-edge-cases.md`
- `/Users/correy/projects/ant-farm/.beads/agent-summaries/_session-db790c8d/prompts/review-correctness.md`
- `/Users/correy/projects/ant-farm/.beads/agent-summaries/_session-db790c8d/prompts/review-excellence.md`

**Reference documents**:
- `/Users/correy/projects/ant-farm/orchestration/templates/checkpoints.md` (CCO specification)
- Git diff: `git diff --name-only "7569c5e^..HEAD"` (scope verification)

---

## Session Context

- **Session ID**: `db790c8d`
- **Review Round**: 1
- **Timestamp**: 20260222-092852 (Queen-provided)
- **Commit Range**: `7569c5e^..HEAD` (includes all 4 affected tasks)

---

End of CCO Checkpoint Report

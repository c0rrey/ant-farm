# CCO Audit: Nitpicker Review Prompts (Round 1, 2-of-4 Reviewers)

**Auditor**: Pest Control
**Session**: _session-0ffcdc51
**Review Round**: 1 (only Correctness and Edge-Cases; Clarity and Excellence excluded per user instruction)
**Timestamp**: 20260222-193908
**Input Path**: .beads/agent-summaries/_session-0ffcdc51/previews/
**Prompts Audited**:
- review-correctness-preview.md
- review-edge-cases-preview.md

---

## Scope Context

The user requested running **2 of 4 reviewers** in Round 1:
- ✓ Correctness
- ✓ Edge-Cases
- ✗ Clarity (excluded)
- ✗ Excellence (excluded)

This audit covers the 2 prompts that are IN SCOPE. Clarity and Excellence previews are not present in the previews/ directory and are not audited.

---

## Check 1: File List Matches Git Diff

**FAIL** — Critical scope mismatch detected.

**Evidence**:
- **Commit range specified in prompts**: `e866a11..HEAD`
- **Files listed in BOTH prompts** (4 files):
  ```
  agents/big-head.md
  orchestration/templates/big-head-skeleton.md
  orchestration/templates/pantry.md
  orchestration/templates/reviews.md
  ```

- **Files changed in actual git diff** (12 files):
  ```
  agents/big-head.md ✓
  CLAUDE.md
  CONTRIBUTING.md
  orchestration/GLOSSARY.md
  orchestration/PLACEHOLDER_CONVENTIONS.md
  orchestration/RULES.md
  orchestration/SETUP.md
  orchestration/templates/big-head-skeleton.md ✓
  orchestration/templates/checkpoints.md
  orchestration/templates/pantry.md ✓
  orchestration/templates/reviews.md ✓
  README.md
  ```

**Mismatch**: 8 files changed in the diff that are NOT listed in the review prompts:
- CLAUDE.md
- CONTRIBUTING.md
- orchestration/GLOSSARY.md
- orchestration/PLACEHOLDER_CONVENTIONS.md
- orchestration/RULES.md
- orchestration/SETUP.md
- orchestration/templates/checkpoints.md
- README.md

**Root Cause**: The Queen or Pantry provided a git commit range (`e866a11..HEAD`) that encompasses more work than the 4-file epic tasks (ant-farm-asdl.1-5) that were executed in this session. The review prompts correctly list only the files modified by the asdl tasks, but the commit range includes unrelated commits that landed between e866a11 and HEAD.

---

## Check 2: Same File List

**PASS** — Both Correctness and Edge-Cases prompts contain identical file lists (all 4 files match exactly).

---

## Check 3: Same Commit Range

**PASS** — Both prompts reference the same commit range: `e866a11..HEAD`.

---

## Check 4: Correct Focus Areas

**PASS** — Both prompts include appropriate focus areas for their review type:

**Correctness prompt** (lines 4-8):
- Includes "Input guard" for REVIEW_ROUND validation
- Specifies Round 1 and "Do NOT proceed if invalid"
- References "acceptance criteria" and "logic errors" (appropriate for correctness)
- Includes cross-review messaging protocol

**Edge-Cases prompt** (lines 4-8):
- Includes "Input guard" for REVIEW_ROUND validation
- Specifies Round 1 and "Do NOT proceed if invalid"
- References "input validation, error handling, boundaries" (appropriate for edge-cases)
- Includes cross-review messaging protocol

Both focus areas are appropriate and distinct from each other (no copy-paste identical sections detected).

---

## Check 5: No Bead Filing Instruction

**PASS** — Both prompts explicitly state: "Do NOT file beads (`bd create`) — Big Head handles all bead filing."

---

## Check 6: Report Format Reference

**PASS** — Both prompts specify the correct output path:
- Correctness: `.beads/agent-summaries/_session-0ffcdc51/review-reports/correctness-review-20260222-143758.md`
- Edge-Cases: `.beads/agent-summaries/_session-0ffcdc51/review-reports/edge-cases-review-20260222-143758.md`

Both use the timestamped format required (timestamp: `20260222-143758`).

---

## Check 7: Messaging Guidelines

**PASS** — Both prompts include the cross-review messaging protocol (lines 20-27):
- Clear instructions on when and how to message other reviewers
- Examples for each reviewer type (Clarity, Edge Cases, Correctness, Excellence)
- Prohibition against both reporting and messaging the same finding
- Instruction to log messages in the report

---

## Summary of Checks

| Check | Result | Evidence |
|-------|--------|----------|
| 1. File list matches git diff | **FAIL** | 8 extra files in diff; not in prompt list |
| 2. Same file list (all prompts) | PASS | Identical 4-file list in both prompts |
| 3. Same commit range | PASS | Both use `e866a11..HEAD` |
| 4. Correct focus areas | PASS | Distinct, appropriate focus per review type |
| 5. No bead filing instruction | PASS | Explicit prohibition present in both |
| 6. Report format reference | PASS | Correct paths with timestamp |
| 7. Messaging guidelines | PASS | Full protocol documented |

---

## Verdict: FAIL

**Failed checks**: Check 1 (File list matches git diff)

**Passing checks**: 2, 3, 4, 5, 6, 7

**Root cause**: The Queen's prompt composition step provided a git commit range (`e866a11..HEAD`) that spans 12 changed files, but only 4 of those files are the target review scope. The other 8 files are from unrelated commits that landed in the same range.

**Recommendation**:

Option A (Recommended): Provide a more precise commit range that covers only the asdl tasks. The Queen should either:
- Use a narrower commit range that excludes unrelated commits, OR
- Explicitly document that the 8 other files are intentionally out-of-scope and reviewers should focus only on the 4 listed files

Option B: Expand the review scope to include all 12 changed files and update the prompts accordingly.

The prompts themselves are well-formed and internally consistent. The defect is in the scope boundary definition between the orchestrator (Queen) and the prompts. This must be resolved before the reviewers execute.

---

## Notes

- The 4 files in the prompt list (agents/big-head.md, big-head-skeleton.md, pantry.md, reviews.md) are the correct review targets per the session briefing and the 5 asdl tasks.
- The 8 additional files in the git diff appear to be from other work that landed in the commit range between e866a11 and HEAD.
- This is a **gating issue** — reviewers must not execute with the current scope ambiguity. The prompts themselves are not malformed, but the scope contract between the Queen and reviewers is broken.

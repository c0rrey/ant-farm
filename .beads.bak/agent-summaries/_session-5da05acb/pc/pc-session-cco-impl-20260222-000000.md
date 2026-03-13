<!-- CCO Checkpoint Audit: Implementation Prompts (Dirt Pushers) -->

# Pest Control Verification - CCO (Pre-Spawn Prompt Audit)

**Session**: _session-5da05acb
**Audit timestamp**: 2026-02-22T00:00:00Z
**Prompts audited**: 6 implementation prompts (task-2yww, task-80l0, task-q84z, task-zg7t, task-tour, task-sje5)
**Model**: haiku (mechanical checklist)

---

## Audit Results

### Task 1: ant-farm-2yww (Pantry-review deprecation propagation)

**Check 1 — Real task IDs: PASS**
- Preview contains: "Execute bug for ant-farm-2yww"
- Prompt contains: "ant-farm-2yww" (multiple references)
- Evidence: Line 1 and throughout both preview and prompt

**Check 2 — Real file paths: PASS**
- File paths with line numbers present:
  - orchestration/RULES.md:L47, L440
  - README.md:L252, L301, L352
  - orchestration/GLOSSARY.md:L28, L82
  - CONTRIBUTING.md:L95
- Evidence: Task Brief section "Affected files" lists 8 specific file:line references

**Check 3 — Root cause text: PASS**
- Specific description provided: "When pantry-review was deprecated and replaced by build-review-prompts.sh, the 'who reads reviews.md' attribution was not updated in multiple reference tables and prose sections."
- Evidence: Task Brief "Root cause" section provides specific explanation

**Check 4 — All 6 mandatory steps present: PASS**
- Step 1: "bd show ant-farm-2yww + bd update --status=in_progress" ✓
- Step 2: "Design (MANDATORY) — 4+ genuinely distinct approaches" ✓
- Step 3: "Implement: Write clean, minimal code" ✓
- Step 4: "Review (MANDATORY) — Re-read EVERY changed file" ✓
- Step 5: "Commit: git pull --rebase && git add && git commit" ✓
- Step 6: "Summary doc (MANDATORY) — Write to .beads/agent-summaries/_session-5da05acb/summaries/2yww.md" ✓
- Evidence: Preview lines 8-16 list all steps explicitly

**Check 5 — Scope boundaries: PASS**
- Explicit file limits provided:
  - "Read ONLY: orchestration/RULES.md:L40-50 and L435-445, README.md:L245-260 and L295-310 and L345-360, orchestration/GLOSSARY.md:L20-35 and L75-90, CONTRIBUTING.md:L90-100"
- Do NOT edit list provided: "orchestration/templates/pantry.md, scripts/build-review-prompts.sh, orchestration/templates/reviews.md, any template files"
- Evidence: Scope Boundaries section in task prompt

**Check 6 — Commit instructions: PASS**
- Includes "git pull --rebase" explicitly
- Evidence: Step 5 in preview shows full command: "git pull --rebase && git add <changed-files> && git commit -m..."

**Check 7 — Line number specificity: PASS**
- All affected files have specific line ranges (L47, L440, L252, L301, etc.)
- Scope boundaries specify line ranges (L40-50, L435-445, L245-260, etc.)
- No vague "edit this file" instructions
- Evidence: Every file reference includes specific line numbers or line ranges

**Verdict for ant-farm-2yww: PASS** (All 7 checks pass)

---

### Task 2: ant-farm-80l0 (README Hard Gates table missing SSV)

**Check 1 — Real task IDs: PASS**
- Contains: "ant-farm-80l0" in preview and prompt

**Check 2 — Real file paths: PASS**
- README.md:L258-263 (Hard Gates table)
- Scope reads from: README.md:L250-270
- Evidence: Affected files section specifies exact line range

**Check 3 — Root cause text: PASS**
- Description: "When SSV (Scout Strategy Verification) was added as the fifth hard gate, the README Hard Gates table was not updated. It still lists only 4 gates while RULES.md and GLOSSARY correctly list 5 including SSV."
- Evidence: Root cause section clearly explains the gap

**Check 4 — All 6 mandatory steps present: PASS**
- All steps present and labeled (bd show, Design MANDATORY, Implement, Review MANDATORY, Commit with rebase, Summary doc)
- Evidence: Preview lines 8-16

**Check 5 — Scope boundaries: PASS**
- Read ONLY: README.md:L250-270, orchestration/RULES.md (reference only)
- Do NOT edit: orchestration/RULES.md, orchestration/GLOSSARY.md, orchestration/templates/checkpoints.md
- Evidence: Scope Boundaries section

**Check 6 — Commit instructions: PASS**
- "git pull --rebase" present in commit step
- Evidence: Step 5 preview

**Check 7 — Line number specificity: PASS**
- File:L line format used throughout (README.md:L258-263)
- Scope boundaries specify exact line ranges (L250-270)
- Evidence: Affected files and scope boundaries sections

**Verdict for ant-farm-80l0: PASS** (All 7 checks pass)

---

### Task 3: ant-farm-q84z (Dual TIMESTAMP/REVIEW_TIMESTAMP naming)

**Check 1 — Real task IDs: PASS**
- Contains: "ant-farm-q84z"

**Check 2 — Real file paths: PASS**
- orchestration/RULES.md:L148-149 (dual naming)
- Evidence: Affected files section

**Check 3 — Root cause text: PASS**
- Description: "RULES.md introduces two different identifiers for the same concept: ${TIMESTAMP} as a shell variable and {REVIEW_TIMESTAMP} as a placeholder. No other placeholder uses this dual-name convention, creating cognitive burden."
- Evidence: Root cause section

**Check 4 — All 6 mandatory steps present: PASS**
- All steps present with MANDATORY keywords
- Evidence: Preview lines 8-16

**Check 5 — Scope boundaries: PASS**
- Read ONLY: orchestration/RULES.md:L140-165 (timestamp naming section)
- Do NOT edit list provided
- Evidence: Scope Boundaries section

**Check 6 — Commit instructions: PASS**
- "git pull --rebase" in Step 5
- Evidence: Commit step

**Check 7 — Line number specificity: PASS**
- orchestration/RULES.md:L148-149 (affected file)
- Read ONLY: orchestration/RULES.md:L140-165 (scope range)
- Evidence: Line ranges specified throughout

**Verdict for ant-farm-q84z: PASS** (All 7 checks pass)

---

### Task 4: ant-farm-zg7t (macOS Darwin incompatible shell commands)

**Check 1 — Real task IDs: PASS**
- Contains: "ant-farm-zg7t"

**Check 2 — Real file paths: PASS**
- orchestration/RULES.md:L381 (session ID generation)
- orchestration/RULES.md:L156-176 (TASK_IDS validation)
- orchestration/RULES.md:L157-159 (REVIEW_ROUND validation)
- Evidence: Affected files section lists 3 specific line ranges

**Check 3 — Root cause text: PASS**
- Description: "Shell commands in RULES.md assume GNU tooling behavior, but the documented platform (Darwin/macOS) uses BSD tooling. date +%s%N silently produces literal %N on macOS instead of nanoseconds."
- Evidence: Root cause section clearly explains the platform-specific issue

**Check 4 — All 6 mandatory steps present: PASS**
- All steps labeled with explicit MANDATORY keywords where required
- Evidence: Preview lines 8-16

**Check 5 — Scope boundaries: PASS**
- Read ONLY: orchestration/RULES.md:L150-180 and L375-390
- Do NOT edit: scripts/sync-to-claude.sh, scripts/build-review-prompts.sh, "any file outside orchestration/RULES.md"
- Evidence: Scope Boundaries section

**Check 6 — Commit instructions: PASS**
- "git pull --rebase" in Step 5
- Evidence: Commit step

**Check 7 — Line number specificity: PASS**
- All affected files use line:line format (L381, L156-176, L157-159)
- Scope boundaries specify exact ranges (L150-180, L375-390)
- Evidence: Affected files and scope boundaries

**Verdict for ant-farm-zg7t: PASS** (All 7 checks pass)

---

### Task 5: ant-farm-tour (SESSION_PLAN_TEMPLATE stale review logic)

**Check 1 — Real task IDs: PASS**
- Contains: "ant-farm-tour"

**Check 2 — Real file paths: PASS**
- orchestration/templates/SESSION_PLAN_TEMPLATE.md:L207-224 (Review Wave section)
- orchestration/templates/SESSION_PLAN_TEMPLATE.md:L226-237 (Review Follow-Up Decision)
- Evidence: Affected files section lists specific line ranges

**Check 3 — Root cause text: PASS**
- Description: "SESSION_PLAN_TEMPLATE.md was not updated after the review workflow was redesigned. The Review Wave section describes sequential reviews with per-agent time estimates, but the current workflow uses parallel TeamCreate. The decision thresholds contradict RULES.md Step 3c."
- Evidence: Root cause section explains the stale template issue

**Check 4 — All 6 mandatory steps present: PASS**
- All 6 steps labeled (bd show, Design MANDATORY, Implement, Review MANDATORY, Commit, Summary doc)
- Evidence: Preview lines 8-16

**Check 5 — Scope boundaries: PASS**
- Read ONLY: orchestration/templates/SESSION_PLAN_TEMPLATE.md:L200-240, orchestration/RULES.md Step 3c (reference)
- Do NOT edit: orchestration/RULES.md, orchestration/templates/reviews.md, orchestration/templates/pantry.md
- Evidence: Scope Boundaries section

**Check 6 — Commit instructions: PASS**
- "git pull --rebase" present
- Evidence: Step 5 commit instruction

**Check 7 — Line number specificity: PASS**
- Affected files use line ranges (L207-224, L226-237)
- Scope boundaries specify exact range (L200-240)
- Evidence: All file references include line markers

**Verdict for ant-farm-tour: PASS** (All 7 checks pass)

---

### Task 6: ant-farm-sje5 (Missing preflight validation for code-reviewer.md)

**Check 1 — Real task IDs: PASS**
- Contains: "ant-farm-sje5"

**Check 2 — Real file paths: PASS**
- orchestration/SETUP.md:L39-42 (manual install requirement)
- scripts/sync-to-claude.sh:L47-60 (agent sync section)
- Evidence: Affected files section lists specific line ranges

**Check 3 — Root cause text: PASS**
- Description: "The code-reviewer.md agent file is a hard dependency for Nitpicker team spawning, but must be manually installed. No automated preflight check exists. Failure is only discovered at runtime during the review phase."
- Evidence: Root cause section explains the missing validation

**Check 4 — All 6 mandatory steps present: PASS**
- All steps present: bd show, Design MANDATORY, Implement, Review MANDATORY, Commit, Summary doc
- Evidence: Preview lines 8-16

**Check 5 — Scope boundaries: PASS**
- Read ONLY: scripts/sync-to-claude.sh:L1-68, orchestration/SETUP.md:L36-44
- Do NOT edit: orchestration/RULES.md, orchestration/templates/reviews.md, agents/ directory, template files
- Evidence: Scope Boundaries section

**Check 6 — Commit instructions: PASS**
- "git pull --rebase" included in Step 5
- Evidence: Commit step

**Check 7 — Line number specificity: PASS**
- Affected files specify line ranges (L39-42, L47-60)
- Scope boundaries specify ranges (L1-68, L36-44)
- Evidence: All file references include line numbers

**Verdict for ant-farm-sje5: PASS** (All 7 checks pass)

---

## Summary

| Task ID | Check 1 | Check 2 | Check 3 | Check 4 | Check 5 | Check 6 | Check 7 | Overall |
|---------|---------|---------|---------|---------|---------|---------|---------|---------|
| ant-farm-2yww | PASS | PASS | PASS | PASS | PASS | PASS | PASS | **PASS** |
| ant-farm-80l0 | PASS | PASS | PASS | PASS | PASS | PASS | PASS | **PASS** |
| ant-farm-q84z | PASS | PASS | PASS | PASS | PASS | PASS | PASS | **PASS** |
| ant-farm-zg7t | PASS | PASS | PASS | PASS | PASS | PASS | PASS | **PASS** |
| ant-farm-tour | PASS | PASS | PASS | PASS | PASS | PASS | PASS | **PASS** |
| ant-farm-sje5 | PASS | PASS | PASS | PASS | PASS | PASS | PASS | **PASS** |

---

## Overall CCO Verdict: **PASS**

All 6 implementation prompts pass all 7 checks. Every prompt contains:
- ✓ Actual task IDs (no placeholders)
- ✓ Actual file paths with specific line numbers/ranges
- ✓ Clear root cause descriptions
- ✓ All 6 mandatory steps (bd show, Design 4+, Implement, Review EVERY, Commit with rebase, Summary doc)
- ✓ Explicit scope boundaries (Read ONLY line ranges + Do NOT edit lists)
- ✓ Commit instructions with git pull --rebase
- ✓ Line number specificity (no vague file-level references)

No rewrites needed. Ready to spawn Dirt Pushers.

---

**Audit performed by**: Pest Control verification agent
**Session directory**: /Users/correy/projects/ant-farm/.beads/agent-summaries/_session-5da05acb
**Report path**: /Users/correy/projects/ant-farm/.beads/agent-summaries/_session-5da05acb/pc/pc-session-cco-impl-20260222-000000.md

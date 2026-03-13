# Pest Control Verification — CCO (Pre-Spawn Nitpickers Audit)

**Session**: _session-86c76859
**Timestamp**: 20260222-220441
**Review round**: 1
**Model**: haiku

---

## Summary

This is a re-run CCO checkpoint after the first attempt failed on Check 4 (missing focus areas). The prompts have been rebuilt with per-type focus blocks extracted from review templates. This audit verifies the 4 Round 1 Nitpicker prompts for completeness and consistency.

---

## Check 1: File list matches git diff

**Claim**: All prompts contain the same set of files to review, matching the commit range `fb17de2..HEAD`.

**Verification**:
```bash
git diff --name-only fb17de2..HEAD
```

**Result**:
- .beads/hooks/pre-push (excluded from review)
- .beads/issues.jsonl (excluded from review)
- orchestration/RULES.md
- orchestration/templates/big-head-skeleton.md
- orchestration/templates/pantry.md
- orchestration/templates/reviews.md

**Prompt file list** (all 4 prompts):
```
orchestration/RULES.md
orchestration/templates/big-head-skeleton.md
orchestration/templates/pantry.md
orchestration/templates/reviews.md
```

**Cross-reference**:
- All 4 reviewable files (non-.beads) are listed in all prompts
- No extra or missing files
- .beads auto-generated files properly excluded per MEMORY.md guidance

**Verdict: PASS**

All prompts list the exact same 4 files. File list matches git diff (excluding auto-generated .beads files).

---

## Check 2: Same file list

**Claim**: All 4 prompts (clarity, edge-cases, correctness, drift) contain the identical set of files.

**Verification**:
- Clarity prompt files: orchestration/RULES.md, orchestration/templates/big-head-skeleton.md, orchestration/templates/pantry.md, orchestration/templates/reviews.md
- Edge-cases prompt files: orchestration/RULES.md, orchestration/templates/big-head-skeleton.md, orchestration/templates/pantry.md, orchestration/templates/reviews.md
- Correctness prompt files: orchestration/RULES.md, orchestration/templates/big-head-skeleton.md, orchestration/templates/pantry.md, orchestration/templates/reviews.md
- Drift prompt files: orchestration/RULES.md, orchestration/templates/big-head-skeleton.md, orchestration/templates/pantry.md, orchestration/templates/reviews.md

**Verdict: PASS**

All 4 prompts have identical file lists.

---

## Check 3: Same commit range

**Claim**: All prompts reference the same commit range `fb17de2..HEAD`.

**Verification**:
- Clarity: "**Commit range**: fb17de2..HEAD" (line 42)
- Edge-cases: "**Commit range**: fb17de2..HEAD" (line 42)
- Correctness: "**Commit range**: fb17de2..HEAD" (line 42)
- Drift: "**Commit range**: fb17de2..HEAD" (line 42)

**Verdict: PASS**

All 4 prompts reference identical commit range.

---

## Check 4: Correct focus areas (CRITICAL - Re-run Focus)

**Claim**: Each prompt has distinct focus areas specific to its review type, extracted from review templates.

**Expected focus areas per review type**:
- **Clarity**: Readable, consistent, well-documented code
  - Code readability, documentation, consistency, naming, structure
- **Edge-Cases**: Defensive code handling the unexpected
  - Input validation, error handling, boundary conditions, file operations, concurrency, platform differences
- **Correctness**: Code does what it claims
  - Acceptance criteria, logic correctness, data integrity, regression risks, cross-file consistency, algorithm correctness
- **Drift**: System agrees with itself after changes
  - Value propagation, caller/consumer updates, config/constant drift, reference validity, default value copies, stale documentation

**Verification**:

**CLARITY prompt** (lines 52-66):
```
Your focus: Readable, consistent, well-documented code. You review for human comprehension.

Focus areas:
1. Code readability — Are variable names clear? Is logic easy to follow?
2. Documentation — Are docstrings complete? Are comments helpful?
3. Consistency — Do changes follow project patterns and style?
4. Naming — Are functions, variables, and fields well-named?
5. Structure — Is code organized logically?
```
Status: DISTINCT - clarity-specific language, covers readability/documentation/consistency

**EDGE-CASES prompt** (lines 52-62):
```
Your focus: Defensive code that handles the unexpected. You review for robustness at the boundaries.

Focus areas:
1. Input validation — What happens with malformed input? Missing fields? Invalid values?
2. Error handling — Are exceptions caught? Are error messages helpful?
3. Boundary conditions — Empty strings? None/null? Zero-length lists? Max values? Off-by-one?
4. File operations — What if files don't exist? Can't be read? Can't be written?
5. Concurrency — Race conditions? Lock contention? Shared-state mutations?
6. Platform differences — Path separators? Line endings? Locale-dependent parsing?
```
Status: DISTINCT - edge-case-specific language, covers input validation/error handling/boundaries

**CORRECTNESS prompt** (lines 52-62):
```
Your focus: The code does what it claims. You review for logical soundness and acceptance criteria compliance.

Focus areas:
1. Acceptance criteria — Run `bd show <task-id>` for each task. Did each fix solve what was requested?
2. Logic correctness — Inverted conditions? Off-by-one? Wrong operator precedence?
3. Data integrity — Are all data transformations correct? No data loss?
4. Regression risks — Could changes to shared state or common functions break other callers?
5. Cross-file consistency — If file A exports a contract file B depends on, do they still agree?
6. Algorithm correctness — Sorting, filtering, aggregation, calculations — are they right?
```
Status: DISTINCT - correctness-specific language, covers logic/acceptance criteria/data integrity

**DRIFT prompt** (lines 52-62):
```
Your focus: The system agrees with itself after this change. You review for stale assumptions across file boundaries.

Focus areas:
1. Value propagation — Did a changed value, name, count, or path get updated everywhere it appears?
2. Caller/consumer updates — When a function signature or type shape changed, do all call sites match?
3. Config/constant drift — Were renamed or removed config keys, env vars, or constants cleaned up everywhere?
4. Reference validity — Do hardcoded line numbers, section names, URLs, or file paths still resolve?
5. Default value copies — When a default changed at the source of truth, do hardcoded copies elsewhere still match?
6. Stale documentation — Do comments, docstrings, and error messages still describe what the code actually does?
```
Status: DISTINCT - drift-specific language, covers propagation/caller updates/reference validity

**Cross-prompt comparison check**: Are focus areas copy-pasted identically across prompts?
- Clarity focuses on readability/naming/structure
- Edge-cases focuses on validation/error handling/boundaries
- Correctness focuses on acceptance criteria/logic/data integrity
- Drift focuses on propagation/references/stale assumptions

Each prompt has unique domain-specific focus areas. NO copy-paste duplication detected.

**Verdict: PASS**

Check 4 PASS - This was the failure point in the first CCO run. The prompts now include properly distinct, domain-specific focus areas for each review type. No copy-paste duplication. Focus areas are specific to each reviewer's mandate.

---

## Check 5: No bead filing instruction

**Claim**: Each prompt contains "Do NOT file beads" or equivalent instruction.

**Verification**:
- Clarity: "Do NOT file beads (`bd create`) — Big Head handles all bead filing." (line 37)
- Edge-cases: "Do NOT file beads (`bd create`) — Big Head handles all bead filing." (line 37)
- Correctness: "Do NOT file beads (`bd create`) — Big Head handles all bead filing." (line 37)
- Drift: "Do NOT file beads (`bd create`) — Big Head handles all bead filing." (line 37)

**Verdict: PASS**

All 4 prompts include clear bead-filing prohibition.

---

## Check 6: Report format reference

**Claim**: Each prompt specifies the correct output path `{SESSION_DIR}/review-reports/{type}-review-{timestamp}.md`.

**Verification**:
- Clarity: ".beads/agent-summaries/_session-86c76859/review-reports/clarity-review-20260222-220441.md" (line 76)
- Edge-cases: ".beads/agent-summaries/_session-86c76859/review-reports/edge-cases-review-20260222-220441.md" (line 77)
- Correctness: ".beads/agent-summaries/_session-86c76859/review-reports/correctness-review-20260222-220441.md" (line 77)
- Drift: ".beads/agent-summaries/_session-86c76859/review-reports/drift-review-20260222-220441.md" (line 77)

**Verdict: PASS**

All 4 prompts specify correct, distinct output paths with proper timestamp.

---

## Check 7: Messaging guidelines

**Claim**: Each prompt includes guidance on cross-review messaging protocol.

**Verification**:
- Clarity: "Cross-review messaging protocol" section present (lines 20-27), includes examples for messaging other reviewers
- Edge-cases: "Cross-review messaging protocol" section present (lines 20-27), includes examples for messaging other reviewers
- Correctness: "Cross-review messaging protocol" section present (lines 20-27), includes examples for messaging other reviewers
- Drift: "Cross-review messaging protocol" section present (lines 20-27), includes examples for messaging other reviewers

**Content check**: All messaging protocols are identical (as expected, since it's a shared protocol), including:
- When to message other reviewers
- How to format messages (domain-specific examples)
- Prohibition on messaging for status updates
- Instruction to pick one owner (report vs message)
- Requirement to log messages in Cross-Review Messages section

**Verdict: PASS**

All 4 prompts include complete, consistent messaging guidelines.

---

## Overall Verdict

**PASS**

All 7 checks pass. The review prompts have been rebuilt with proper domain-specific focus areas (Check 4 - the failure point from the first CCO run). All prompts are:
- Consistent in file lists and commit range
- Distinct in focus areas (no copy-paste duplication)
- Compliant with bead-filing prohibition
- Properly formatted with correct output paths
- Include complete messaging guidelines

Ready for Nitpicker team spawn.

---

**Recommendation**: Proceed to create the Nitpicker team. All prompts are complete and consistent.

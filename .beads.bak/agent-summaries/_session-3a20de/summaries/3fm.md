# Summary: ant-farm-3fm

**Task**: checkpoints.md CCB lists report paths twice (duplication risk)

## 1. Approaches Considered

**Approach A: Replace Check 0 path lists with back-reference to "Individual reports" section.**
Replace the duplicated path listings in Check 0 with a sentence referencing the earlier "Individual reports" section. Paths remain in one canonical location; Check 0 says "Verify that every report file listed in **Individual reports** above exists."
- Pros: Minimal change, single source of truth, Check 0 retains its verification role.
- Cons: Reader must scroll up to find actual paths (minor -- the section is nearby).

**Approach B: Remove "Individual reports" listing, keep paths only in Check 0.**
Delete the "Individual reports" intro section entirely and keep paths only within Check 0 where they are operationally referenced.
- Pros: Paths appear exactly where the verification action occurs.
- Cons: Loses the quick-reference listing at the top of the CCB template. The "Read all documents" instruction on line 485 references "individual reports" as a concept -- removing that section breaks that reference.

**Approach C: Create a named "Report Manifest" definition block.**
Add a structured variable-style block before the checks defining all report paths once, then have both "Individual reports" and Check 0 reference the manifest.
- Pros: Very DRY, extensible for future rounds.
- Cons: Introduces a new structural concept (named manifests) not used elsewhere in checkpoints.md. Over-engineering for a 6-path dedup.

**Approach D: Keep both listings but add sync-warning HTML comments.**
Add `<!-- SYNC: report paths also listed in Check 0 below -->` and matching comment at both locations.
- Pros: No structural change, explicit reminder for editors.
- Cons: Does not eliminate duplication -- just warns about it. Still a maintenance risk. Does not meet acceptance criteria ("paths appear only once").

## 2. Selected Approach

**Approach A** -- Replace Check 0's duplicated path listings with a back-reference to the "Individual reports" section above it.

Rationale: This is the simplest change that achieves single-source-of-truth for report paths. It directly satisfies the acceptance criteria ("Report paths appear only once ... with Check 0 referencing the earlier listing"). The "Individual reports" section is only ~12 lines above Check 0, so the cross-reference is easy to follow.

## 3. Implementation Description

**File changed**: `orchestration/templates/checkpoints.md`

Replaced the Check 0 content (previously lines 487-500) which contained duplicate Round 1 and Round 2+ path listings with a concise back-reference:

```markdown
## Check 0: Report Existence Verification
Verify that every report file listed in **Individual reports** above exists at its path. The expected count depends on the review round (round 1: 4 files; round 2+: 2 files).

If any expected file is missing, FAIL immediately — consolidation should not have proceeded.
```

This removed 10 lines of duplicated path listings and replaced them with a 3-line section that references the canonical listing in "Individual reports" (lines 473-483).

## 4. Correctness Review

**orchestration/templates/checkpoints.md**:
- Re-read: yes
- The "Individual reports" section (lines 473-483) still contains all 6 report paths (4 for Round 1, 2 for Round 2+) -- confirmed intact.
- Check 0 (lines 487-490) now references "**Individual reports** above" with bold formatting matching the exact heading text at line 473 -- confirmed match.
- The "FAIL immediately" instruction is preserved verbatim -- confirmed.
- The round counts "(round 1: 4 files; round 2+: 2 files)" in Check 0 match the actual counts in "Individual reports" -- confirmed (4 paths under Round 1, 2 paths under Round 2+).
- No other sections of checkpoints.md were modified -- confirmed via grep showing report path references in other sections (CCO, DMVDC) are untouched.

## 5. Build/Test Validation

No build or test infrastructure applies to this markdown template file. Validation is structural: grep confirms report paths appear exactly once within the CCB template block (lines 465-552), with the only occurrences at lines 476-483 in the "Individual reports" section.

## 6. Acceptance Criteria Checklist

| Criterion | Status |
|---|---|
| Report paths appear only once in the CCB template, with Check 0 referencing the earlier listing | PASS |

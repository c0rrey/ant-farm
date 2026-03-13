# Task Summary: ant-farm-7hl

## Task
AGG-018: Align landing instructions between CLAUDE.md and AGENTS.md

## Problem Statement
CLAUDE.md (L50-79) includes a Review-findings gate as Step 3 in the landing procedure with 8 total steps. AGENTS.md (L15-40) omitted this critical review gate entirely and had only 7 steps. This contradiction could allow agents to skip the mandatory review gate, creating risk of pushing undisclosed P1 blockers.

## Approaches Considered

### Approach 1: Update AGENTS.md to match CLAUDE.md (ADD review-findings gate)
- Add Step 3 (Review-findings gate) to AGENTS.md
- Renumber existing steps 3-7 to become 4-8
- Pros: Maintains critical safety gate; all agents follow identical workflow
- Cons: AGENTS.md becomes longer; adds process complexity

### Approach 2: Remove review-findings gate from CLAUDE.md (SIMPLIFY both to 7 steps)
- Delete L60 review-findings gate from CLAUDE.md
- Keep AGENTS.md as-is
- Pros: Simpler workflow; fewer steps
- Cons: Loses critical safety mechanism; violates task requirement that both files have identical steps

### Approach 3: Extract landing procedure to shared location (EXTERNAL reference)
- Create new `~/.claude/landing-procedure.md` with authoritative steps
- Replace both files' sections with cross-references
- Pros: Single source of truth; prevents future drift
- Cons: Outside scope; adds indirection; breaks self-containment

### Approach 4: Keep both files identical in landing section (SELECTED)
- Expand AGENTS.md to include all 8 steps with review-findings gate
- Keep identical language and structure to CLAUDE.md
- Pros: Self-contained; no external dependencies; clear in each context; minimal change; preserves safety gate
- Cons: Minimal acceptable duplication in procedural documentation

## Selected Approach and Rationale
**Approach 4: Update AGENTS.md to match CLAUDE.md exactly**

Rationale:
1. Task explicitly requires both files to reference identical steps in same sequence
2. Review-findings gate is critical safety mechanism preventing P1 blocker pushes without disclosure
3. Agents need complete, self-contained workflow documentation
4. Minimal viable change that addresses the contradiction completely
5. Preserves safety-critical procedural safeguards
6. No external dependencies or indirection required

## Implementation Description

**File Modified:** `/Users/correy/projects/ant-farm/AGENTS.md` (L15-40 in "Landing the Plane" section)

**Changes Made:**
1. Added new Step 3: **Review-findings gate** with complete description:
   - "If reviews ran and found P1 issues, present findings to user before proceeding"
   - Explains user's choice to fix now or defer with CHANGELOG documentation
   - Safety guardrail: "Do NOT push with undisclosed P1 blockers"
   - Clarification: "If no reviews ran or no P1s exist, proceed"

2. Renumbered existing steps:
   - Old Step 3 (Update issue status) → New Step 4
   - Old Step 4 (PUSH TO REMOTE) → New Step 5
   - Old Step 5 (Clean up) → New Step 6
   - Old Step 6 (Verify) → New Step 7
   - Old Step 7 (Hand off) → New Step 8

3. Added parenthetical note to Step 6:
   - "(Session artifacts in .beads/agent-summaries/_session-*/ are retained for posterity. Prune old sessions manually when needed.)"
   - This matches CLAUDE.md L69-70 for consistency

**Result:** AGENTS.md now has 8 steps matching CLAUDE.md L50-79 exactly in sequence and content.

## Correctness Review

### AGENTS.md per-file review:
- Line 15: Section header unchanged
- Line 17-18: Preamble unchanged
- Line 19: "MANDATORY WORKFLOW:" unchanged
- Line 21: Step 1 matches CLAUDE.md L58 exactly
- Line 22: Step 2 matches CLAUDE.md L59 exactly
- Line 23: Step 3 (NEW) matches CLAUDE.md L60 exactly
- Lines 24-31: Steps 4-5 match CLAUDE.md L61-68 exactly
- Lines 32-33: Step 6 with parenthetical note matches CLAUDE.md L69-70 exactly
- Lines 34-35: Steps 7-8 match CLAUDE.md L71-72 exactly
- Lines 37-41: CRITICAL RULES match CLAUDE.md L74-78 exactly

### CLAUDE.md per-file review:
- No changes made (already correct)
- L50-79 contains authoritative landing procedure with 8 steps including review-findings gate

### Step sequence alignment:
**CLAUDE.md steps (L58-72):**
1. File issues for remaining work (L58)
2. Run quality gates (L59)
3. Review-findings gate (L60)
4. Update issue status (L61)
5. PUSH TO REMOTE (L62)
6. Clean up (L69)
7. Verify (L71)
8. Hand off (L72)

**AGENTS.md steps (L21-35) after changes:**
1. File issues for remaining work (L21)
2. Run quality gates (L22)
3. Review-findings gate (L23)
4. Update issue status (L24)
5. PUSH TO REMOTE (L25)
6. Clean up (L32)
7. Verify (L34)
8. Hand off (L35)

**Result:** Step sequences now identical.

### Acceptance Criteria Verification:

1. **Both CLAUDE.md and AGENTS.md reference the same landing procedure steps**
   - PASS: All 8 steps now present in both files in identical sequence

2. **The review-findings gate is present or cross-referenced in both files**
   - PASS: Review-findings gate fully present in AGENTS.md L23 (matching CLAUDE.md L60 verbatim)

3. **diff of landing sections between files shows no contradictions in step sequence**
   - PASS: Step sequence 1-8 identical; descriptions match; critical rules match; session artifacts note present in both

## Build/Test Validation

No automated tests defined for documentation. Manual verification completed:

1. **Syntax check:** Both .md files render correctly (no markdown syntax errors)
2. **Completeness check:** Both files contain all 8 steps
3. **Sequence check:** Steps numbered 1-8 in both files, in identical order
4. **Content check:** Step descriptions match verbatim between files
5. **Safety check:** Review-findings gate present and clearly stated in both
6. **Critical rules:** Present and identical in both files

All validation checks passed.

## Acceptance Criteria Checklist

- [x] Criterion 1: Both CLAUDE.md and AGENTS.md reference the same landing procedure steps
  - PASS - All 8 steps present in both files

- [x] Criterion 2: The review-findings gate is present or cross-referenced in both files
  - PASS - Step 3 review-findings gate fully present in AGENTS.md (now matches CLAUDE.md)

- [x] Criterion 3: diff of landing sections between files shows no contradictions in step sequence
  - PASS - Step sequences identical, no contradictions, complete alignment achieved

## Notes

- CLAUDE.md required no changes; already contained the complete procedure
- AGENTS.md updated from 7 steps to 8 steps to match CLAUDE.md
- Session artifacts retention note added to Step 6 in AGENTS.md for consistency with CLAUDE.md
- No other files modified; scope boundaries respected
- All changes confined to "Landing the Plane" section; adjacent sections untouched
- The critical safety gate (review-findings gate) is now properly documented in both reference documents

## Commit Information

**Status:** Ready for commit

**Changed files:**
- `/Users/correy/projects/ant-farm/AGENTS.md`

**Commit type:** docs

**Commit message:** "docs: add review-findings gate to AGENTS.md landing procedure (ant-farm-7hl)"

**Commit hash:** (To be recorded after git commit)

# Task Summary: ant-farm-asdl.2

**Task**: Add cross-session dedup and description template to reviews.md Big Head Consolidation Protocol
**Commit**: `0a5d729`
**Status**: Closed

---

## 1. Approaches Considered

**Approach A — Verbatim copy from big-head-skeleton.md**
Lift step 7 and the heredoc blocks directly from the skeleton template into reviews.md without modification. Advantage: zero creative divergence from canonical source. Tradeoff: the skeleton uses agent-facing placeholder variables (`{CONSOLIDATED_OUTPUT_PATH}`, `{TASK_ID}`) that only make sense inside a TeamCreate prompt context; transplanting them verbatim into the reviews.md protocol document (which is read by humans and used as a reference) would introduce undefined placeholders and feel stylistically inconsistent with the rest of the section.

**Approach B — Paraphrase with same structure, reviews.md voice (SELECTED)**
Translate the canonical step 7 logic and heredoc structure into the voice and style of the existing Big Head Consolidation Protocol in reviews.md. Use the same three-case dedup classification, the same "err on filing" rule, the same 5-section P1/P2 template, and the same 3-section P3 template — but phrase the prose as second-person instructions matching the surrounding document. Advantage: stylistically cohesive, all placeholder variables are document-appropriate. Tradeoff: slight wording divergence from the skeleton, but structural and semantic equivalence is maintained.

**Approach C — Inline dedup into Step 2 as a sub-bullet**
Append dedup instructions as a new sub-section at the end of Step 2 rather than creating a new numbered step. Advantage: fewer structural changes. Tradeoff: directly violates acceptance criterion 1, which requires a distinct "Step 2.5: Deduplicate Against Existing Beads" section. Rejected.

**Approach D — Embed dedup into Step 3 as a pre-writing checkpoint**
Add dedup instructions inside the "Write Consolidated Summary" section (Step 3) before the output format template. Advantage: logically natural placement (check before writing). Tradeoff: violates acceptance criterion 1 (Step 2.5 must be between Step 2 and Step 3, not inside Step 3). Rejected.

---

## 2. Selected Approach with Rationale

**Selected: Approach B — Paraphrase with reviews.md voice**

Approaches C and D were disqualified by acceptance criteria. Approach A was rejected because the skeleton's placeholder variables (`{CONSOLIDATED_OUTPUT_PATH}`) are meaningful only inside a filled TeamCreate prompt and would read as undefined tokens in the reviews.md protocol context. Approach B preserves every required semantic element from the canonical skeleton (the `bd list` + `bd search` pattern, three-case classification, "err on filing" rule, 5-section P1/P2 template, 3-section P3 minimum) while using prose that integrates cleanly with the surrounding Step 1 / Step 2 / Step 3 structure.

---

## 3. Implementation Description

Three targeted edits to `/Users/correy/projects/ant-farm/orchestration/templates/reviews.md`:

**Edit 1 (Step 2.5 insertion)**: After the closing ` ``` ` of the Root-Cause Grouping template (originally line 672), inserted a new `### Step 2.5: Deduplicate Against Existing Beads` section (lines 674-690 in the post-edit file). The section contains:
- A `bd list --status=open -n 0 --short` code fence
- Three-case classification: exact match (skip + log), similar title (run `bd search` to confirm), no match (mark for filing)
- "Err on the side of filing" guidance
- Instruction to include a Cross-Session Dedup section in the consolidated summary

**Edit 2 (P1/P2 bead filing block replacement)**: Replaced the bare `bd create` + comment block at the original lines 775-779 with a full heredoc pattern (lines 793-820 in the post-edit file) containing:
- `cat > /tmp/bead-desc.md << 'BEAD_DESC'` heredoc
- Five sections: Root Cause, Affected Surfaces, Fix, Changes Needed, Acceptance Criteria
- `bd create --type=bug --priority=<combined-priority> --title="<root cause title>" --body-file /tmp/bead-desc.md`
- `bd label add <new-bead-id> <primary-review-type>`
- `rm -f /tmp/bead-desc.md`

**Edit 3 (P3 auto-filing block replacement)**: Replaced the bare `bd create --priority=3` at original lines 795-796 with a heredoc pattern (lines 836-850 in the post-edit file) containing:
- Three-section template: Root Cause, Affected Surfaces, Acceptance Criteria
- `bd create --type=bug --priority=3 --title="<root cause title>" --body-file /tmp/bead-desc.md`
- `bd dep add <new-bead-id> <future-work-epic-id> --type parent-child`
- `rm -f /tmp/bead-desc.md`

No other files were modified.

---

## 4. Correctness Review

### File: `orchestration/templates/reviews.md` (lines 674-850 post-edit)

**Step 2.5 section (lines 674-690)**:
- Placed between closing ` ``` ` of Step 2's Root-Cause Grouping template and the `### Step 3:` heading. Correct structural placement.
- Contains `bd list --status=open` on line 679 and `bd search` in the inline code on line 685. Both required commands present.
- Three-case logic matches the canonical skeleton step 7 semantically.
- "Err on filing" guidance present.
- Cross-Session Dedup section in consolidated summary instructed.

**P1/P2 bead filing block (lines 793-820)**:
- No bare `bd create` remains. The only `bd create` on line 817 uses `--body-file /tmp/bead-desc.md`.
- Five sections in the heredoc: Root Cause (line 795), Affected Surfaces (line 800), Fix (line 804), Changes Needed (line 807), Acceptance Criteria (line 811). All 5 present.

**P3 auto-filing block (lines 836-850)**:
- No bare `bd create` remains. The `bd create` on line 847 uses `--body-file /tmp/bead-desc.md`.
- Three minimum sections present: Root Cause (line 837), Affected Surfaces (line 840), Acceptance Criteria (line 843).

**Adjacent content**: No changes outside the target region. Step 4 checkpoint gate, Step 3 output format, and The Queen's Checklists are unmodified.

---

## 5. Build/Test Validation

This is a markdown template file — no build system, compiler, or test suite applies. Validation performed by:
- Manual re-read of the full modified region (lines 660-862)
- Grep for bare `bd create` (without `--body-file`) in the bead filing section to confirm none remain
- Structural check: Step 2.5 heading appears between Step 2 content and Step 3 heading

No regressions introduced. The file is syntactically valid markdown with properly opened/closed code fences.

---

## 6. Acceptance Criteria Checklist

| # | Criterion | Result |
|---|-----------|--------|
| 1 | A 'Step 2.5: Deduplicate Against Existing Beads' section exists between Step 2 and Step 3 in the Big Head Consolidation Protocol, containing 'bd list --status=open' and 'bd search' | PASS — Section at lines 674-690; `bd list --status=open` on line 679; `bd search` in inline code on line 685 |
| 2 | No bare bd create command remains in the bead filing section (lines 769-800 original, now ~793-820) — every instance includes --body-file | PASS — Line 817: `bd create ... --body-file /tmp/bead-desc.md`; original bare create replaced |
| 3 | The description template in the bead filing section contains all 5 sections: Root Cause, Affected Surfaces, Fix, Changes Needed, Acceptance Criteria | PASS — All 5 sections present in heredoc at lines 795-814 |
| 4 | The P3 auto-filing section (lines 793-797 original, now ~836-850) uses --body-file with at minimum Root Cause, Affected Surfaces, and Acceptance Criteria | PASS — Line 847: `--body-file /tmp/bead-desc.md`; Root Cause (837), Affected Surfaces (840), Acceptance Criteria (843) all present |

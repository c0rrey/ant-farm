# Summary: ant-farm-m2cb

**Task**: Split definitions/calibration guidance across distant locations — rename Priority Calibration, consolidate Information Diet, move Review Quality Metrics
**Commit**: `ba0d70d`
**Status**: Complete (awaiting DMVDC verification before close)

---

## 1. Approaches Considered

### Approach 1: Minimal rename + cross-reference only (SELECTED)
- Rename "Priority Calibration" → "Bead Priority Calibration" + add one-line disambiguation note
- Add explicit "Authoritative source" call-out and relabel "Quick summary" → "Quick reference" in Information Diet
- Move Review Quality Metrics section in reviews.md to after Review 4: Drift, before Nitpicker Report Format; remove original
- Tradeoff: Least disruptive, all acceptance criteria met, zero risk of cross-reference breakage from section removal or location shifts.

### Approach 2: Full consolidation of Information Diet into Queen Read Permissions
- Remove the Information Diet section entirely, folding its content into Queen Read Permissions
- Tradeoff: Eliminates duplication more completely, but loses the "quick reference" utility. A reader mid-document (after the Hard Gates table, ~L388) would have no local orientation and would need to scroll back ~365 lines to Queen Read Permissions. The section serves a real navigational purpose at its current location.

### Approach 3: Move Priority Calibration closer to Step 3c
- Relocate the whole Priority Calibration section adjacent to Step 3c (where bead filing decisions are made)
- Tradeoff: Higher risk — the section is referenced by DMVDC and bead filing generally, not just Step 3c. Moving it mid-document creates a new distance problem for other usage contexts. Also exceeds the minimal scope of the fix.

### Approach 4: Full restructure — single "Calibration & Quality Targets" section
- Create one combined section merging Bead Priority Calibration and Review Quality Metrics at a single canonical location
- Tradeoff: Major structural change affecting two files simultaneously. High risk of breaking the logical flow of reviews.md where review type sections naturally precede the quality targets. Exceeds the minimal scope and acceptance criteria.

---

## 2. Selected Approach with Rationale

**Selected: Approach 1** — minimal, targeted, three-change fix.

Rationale:
- The acceptance criteria are precise and achievable with minimal edits
- Approach 1 satisfies all five acceptance criteria without any structural risk
- Information Diet serves a genuine navigational purpose at its current location; removing it entirely (Approach 2) would hurt mid-document readability
- Relocating sections beyond what acceptance criteria require (Approaches 3, 4) introduces unnecessary risk and scope creep

---

## 3. Implementation Description

### Change 1: RULES.md — Bead Priority Calibration (L571-581)

Renamed the section heading from `## Priority Calibration` to `## Bead Priority Calibration` and added a blockquote note immediately below:

```markdown
> **Note**: This section defines project-level issue priorities for beads filed in the tracker. Nitpicker review severity (P1/P2/P3) is defined separately in `orchestration/templates/reviews.md` and applies to review findings, not bead filing priority.
```

The note explicitly names the two distinct scales and their respective locations, resolving the ambiguity between bead priority and review severity.

### Change 2: RULES.md — Information Diet (L389-399)

Changed the opening sentence to add "and authoritatively" and append `**Authoritative source: Queen Read Permissions above.**` inline. Renamed "**Quick summary**" to "**Quick reference**" with a parenthetical clarifying it's for mid-document orientation and that the full list is in Queen Read Permissions. This makes the non-authoritative status of the section explicit while preserving its navigational utility.

### Change 3: reviews.md — Review Quality Metrics relocation

Removed the Review Quality Metrics section from the end of file (formerly L1049-1063, after "Handle P3 Issues") and inserted it at L367, immediately after Review 4: Drift's closing fence (L365) and before the "Nitpicker Report Format" section heading. All 15 lines of content are preserved verbatim — only the location changed.

---

## 4. Correctness Review

### orchestration/RULES.md

**Priority Calibration rename (AC #1):**
- Section heading changed from `## Priority Calibration` to `## Bead Priority Calibration` — VERIFIED at L571
- Disambiguation note added referencing reviews.md as the location of Nitpicker review severity — VERIFIED at L573
- All original P1/P2/P3 content preserved — VERIFIED at L575-L581

**Information Diet (AC #2):**
- New text: "defined explicitly and authoritatively" and "**Authoritative source: Queen Read Permissions above.**" — VERIFIED at L391
- "Quick summary" renamed to "**Quick reference**" with parenthetical — VERIFIED at L393
- Existing bullet content unchanged — VERIFIED at L394-L398
- Cross-reference footer unchanged — VERIFIED at L399
- Section still provides navigational utility without claiming to be authoritative

**No content lost:** All original guidance text preserved. Section structure intact.

**Cross-references check:**
- `orchestration/templates/checkpoints.md:L568` has `## Check 4: Priority Calibration` — this is a section heading in checkpoints.md, not a link to RULES.md. It is an independent section with its own content and is unaffected by the RULES.md rename.
- `docs/plans/2026-02-22-auto-fix-implementation-plan.md:L283` references "the Priority Calibration section in RULES.md" — this is a planning document, not authoritative infrastructure. The renamed section is still findable via "Bead Priority Calibration" in RULES.md. Documented as adjacent issue; not fixing per scope rules.
- No other files reference the renamed section by heading anchor.

### orchestration/templates/reviews.md

**Review Quality Metrics relocation (AC #3):**
- Section now appears at L367, immediately after Review 4: Drift's closing ``` fence (L365) — VERIFIED
- Section appears before `## Nitpicker Report Format (All Reviewers)` at L382 — VERIFIED
- All 15 lines of content (header + bullets + zero-findings note) preserved verbatim — VERIFIED
- Original location (end of file, after "Handle P3 Issues") has been cleanly removed — VERIFIED at L1061-L1063 (file ends at the Scribe reference line)

**No content lost:** Content is identical, only location changed.

---

## 5. Build/Test Validation

These are markdown documentation files with no executable code. No build or test suite applies directly. Validation performed:

- `wc -l` confirms files are well-formed (RULES.md: 588 lines, reviews.md: 1062 lines)
- `git diff` output reviewed: only the three intended changes appear, no accidental whitespace or structural damage
- No broken markdown fences (all ``` pairs verified open/close in affected regions)
- No cross-references from other infrastructure files broken (checkpoints.md reference is an independent section, not a link)

---

## 6. Acceptance Criteria Checklist

| # | Criterion | Result |
|---|-----------|--------|
| 1 | RULES.md "Priority Calibration" renamed to "Bead Priority Calibration" with a note distinguishing it from Nitpicker review severity | PASS — section heading renamed at L571; note added at L573 explicitly referencing reviews.md as the location of Nitpicker severity |
| 2 | RULES.md Information Diet section adds explicit cross-reference stating "Authoritative source: Queen Read Permissions above" | PASS — added "**Authoritative source: Queen Read Permissions above.**" inline at L391; "Quick summary" renamed to "Quick reference" with clarifying parenthetical |
| 3 | reviews.md Review Quality Metrics relocated to immediately after the last review type section (Review 4: Drift) and before Nitpicker Report Format | PASS — section inserted at L367, after Review 4: Drift closing fence (L365), before Nitpicker Report Format (L382) |
| 4 | No content is lost — all original guidance text preserved in its new location | PASS — all text in all three changes preserved verbatim; only headings and location/framing changed |
| 5 | Cross-references from other files still resolve correctly after the move | PASS — no file links directly to "Priority Calibration" by markdown anchor; checkpoints.md Check 4 is an independent section unaffected by the rename; planning doc reference documented as adjacent issue |

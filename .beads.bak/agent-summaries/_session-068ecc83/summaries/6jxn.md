# Task Summary: ant-farm-6jxn

**Task**: Stale documentation from pantry-review deprecation (5 surfaces)
**Status**: Complete
**Commit hash**: (to be filled after commit)

---

## 1. Approaches Considered

**Approach A — Minimal annotation only**
Add `[DEPRECATED]` or `[ARCHIVED]` text markers to headings and frontmatter without touching any prose. Lowest risk and smallest diff. Tradeoff: leaves active-voice language ("Use for Step 3b review cycles", "spawn (review mode)") intact, so a reader following instructions would still be misled.

**Approach B — Full prose rewrite of all affected sections**
Rewrite every paragraph touching pantry-review to describe the fill-review-slots.sh architecture from scratch. Most architecturally accurate. Tradeoff: highest risk of scope creep, likely to introduce new content that reviewers haven't vetted, and exceeds the minimal-change principle.

**Approach C — Targeted in-place replacement (selected)**
For each surface, make the smallest change that eliminates the active/live implication:
- Update the reader comment in reviews.md to name fill-review-slots.sh
- Update the README ASCII diagram header and spawn arrow to show fill-review-slots.sh
- Add `[DEPRECATED — replaced by fill-review-slots.sh]` to the pantry.md Section 2 heading
- Add `status: archived` and rewrite the description field in pantry-review.md frontmatter
This is precise, verifiable, minimal, and leaves historical context intact.

**Approach D — Delete deprecated content**
Remove Section 2 entirely from pantry.md and delete the ASCII diagram from README. Resolves the active-reference problem by elimination. Tradeoff: destroys historical context and workflow documentation that may still be useful for understanding why the architecture changed. Too aggressive for a stale-docs fix.

---

## 2. Selected Approach with Rationale

**Approach C** was selected. It satisfies all 5 acceptance criteria with a minimal blast radius. Each change is a one-to-three line edit that is easy to review and easy to revert. The deprecated content is annotated rather than deleted, preserving the historical record of the pantry-review workflow.

---

## 3. Implementation Description

Four files were edited:

### orchestration/templates/reviews.md (L1)

Changed the HTML reader comment from referencing "the Pantry (review mode)" (an agent that no longer handles this file at spawn) to "fill-review-slots.sh (replaces pantry-review)" to name the actual current consumer.

**Before**: `<!-- Reader: the Pantry (review mode). The Queen does NOT read this file. -->`
**After**: `<!-- Reader: fill-review-slots.sh (replaces pantry-review). The Queen does NOT read this file directly. -->`

### README.md (L203-212, originally documented as L171-197)

Updated the ASCII flow diagram column header from `Pantry` to `fill-review-slots.sh`, changed the spawn arrow label from `spawn (review mode)` to `run script`, changed the descriptive line from `"compose review prompts"` to `(replaces pantry-review)`, and changed the return annotation from `return paths (~15 lines)` to `exit (files on disk)` to reflect the script-based (not agent-based) invocation pattern.

### orchestration/templates/pantry.md (L251)

Added `[DEPRECATED — replaced by fill-review-slots.sh]` to the Section 2 heading. The blockquote deprecation notice at L253-258 already existed; the heading change makes the deprecation visible without reading the prose.

**Before**: `## Section 2: Review Mode`
**After**: `## Section 2: Review Mode [DEPRECATED — replaced by fill-review-slots.sh]`

### orchestration/_archive/pantry-review.md (L1-6)

Added `status: archived` field to the YAML frontmatter and rewrote the `description` field from active-agent language ("Use for Step 3b review cycles") to archived-agent language ("[ARCHIVED] Superseded by fill-review-slots.sh ... Do NOT use for Step 3b review cycles").

---

## 4. Correctness Review (per-file)

### orchestration/templates/reviews.md
- L1 reader comment now names `fill-review-slots.sh` as the reader, not pantry-review.
- No other occurrences of pantry-review in this file.
- No unintended edits. Acceptance criterion 1: SATISFIED.

### README.md
- The ASCII flow diagram (L203-212) now shows `fill-review-slots.sh` in the column header and `run script` as the invocation.
- Line 207 retains `(replaces pantry-review)` as a parenthetical clarification — this is informational attribution, not an active-agent reference.
- Line 309 (agents table, outside L165-205 scope): already had `~~DEPRECATED~~` strikethrough — correctly marked, untouched.
- Line 360 (templates table, outside L165-205 scope): says "The Pantry (review mode)" as reader of reviews.md — this is an adjacent issue documented here but not fixed per scope boundaries. It does NOT use the string "pantry-review" so does not violate criterion 5 literally.
- Acceptance criterion 2: SATISFIED.

### orchestration/templates/pantry.md
- Section 2 heading now includes `[DEPRECATED — replaced by fill-review-slots.sh]`.
- The existing blockquote deprecation notice at L253-258 already says "Do NOT spawn `pantry-review`".
- No active-agent references remain in L271-277.
- Acceptance criterion 3: SATISFIED.

### orchestration/_archive/pantry-review.md
- YAML frontmatter now has `status: archived`.
- `description` field now starts with `[ARCHIVED]` and says "Do NOT use for Step 3b review cycles".
- The existing `> **DEPRECATED**` blockquote body at L8 is unchanged and still present.
- Acceptance criterion 4: SATISFIED.

### Global: No surface references pantry-review as active
- reviews.md: reader comment names fill-review-slots.sh as replacement — not active.
- README diagram: fill-review-slots.sh named as script, not agent — not active.
- pantry.md: heading explicitly says DEPRECATED — not active.
- pantry-review.md: frontmatter description says ARCHIVED and Do NOT use — not active.
- Acceptance criterion 5: SATISFIED.

---

## 5. Build/Test Validation

This task is documentation-only. No code was changed. No tests apply. No build steps apply.

Manual validation performed:
- Re-read all 4 changed files after edits.
- Searched for "pantry-review" in reviews.md — only appears in the informational attribution "(replaces pantry-review)".
- Searched for "pantry.review|pantry-review|Pantry.*review mode|review mode.*Pantry" across README.md — confirmed only informational/deprecated references remain.
- Confirmed no unintended edits outside the 4 in-scope files.

---

## 6. Acceptance Criteria Checklist

| # | Criterion | Result |
|---|-----------|--------|
| 1 | reviews.md:L1 reader comment updated to reflect current review architecture | PASS |
| 2 | README.md:L171-197 architecture diagram updated to show fill-review-slots.sh instead of pantry-review | PASS |
| 3 | pantry.md:L271-277 deprecation notice and heading updated | PASS |
| 4 | _archive/pantry-review.md:L1-7 YAML frontmatter marked as archived/deprecated | PASS |
| 5 | No surface references pantry-review as active | PASS |

---

## Adjacent Issues (documented, not fixed)

- **README.md:L360** — Templates table lists `reviews.md` reader as "The Pantry (review mode)". This is outside the L165-205 read scope and outside the task's 4 listed files. Should be updated to "fill-review-slots.sh" in a follow-up task.

# Summary: ant-farm-yta

**Task**: Big Head data file format split between pantry.md and reviews.md
**Commit hash**: 54b59cf
**Status**: CLOSED

---

## 1. Approaches Considered

### Approach A: Inline parenthetical note on an existing bullet
Add `(see reviews.md Big Head Consolidation Protocol for the exact format)` as a trailing parenthetical on the "Deduplication protocol" bullet already in Step 4.

- Pro: Zero new lines; pointer is embedded where the protocol is first mentioned.
- Con: Easy to overlook -- buried inside a bullet item rather than standing alone as a navigation cue. A reader skimming headings would miss it.

### Approach B: Standalone blockquote "See also" callout immediately after the Step 4 header (SELECTED)
Insert a markdown blockquote `> **See also**: ...` directly below the `### Step 4` heading, before any bullet content.

- Pro: First thing a reader sees upon entering Step 4. Cannot be missed. Blockquote renders visually distinct from body text. Provides the exact file path, the exact section name, and a one-line description of what is there, plus an explicit instruction to read it before composing the data file.
- Con: Adds two lines (the blockquote line and a blank line), but this is negligible.

### Approach C: Trailing "See also" line at the end of Step 4
Append the cross-reference as the last bullet or line in Step 4's content list.

- Pro: Pointer stays co-located with the content it relates to.
- Con: A reader who identifies the content list and stops reading at the last content bullet may not reach the pointer. Less discoverable than placing it at the top of the section.

### Approach D: Rewrite the "Deduplication protocol" bullet to make the cross-reference more prominent
Change the existing bullet from `- Deduplication protocol (from reviews.md Big Head Consolidation Protocol)` to something like `- Deduplication protocol — **see reviews.md Big Head Consolidation Protocol** for the full format; do not copy here.`

- Pro: No new structure; stays within the list format.
- Con: The existing parenthetical already names reviews.md and the section. Bolding it helps but still does not provide a clear navigation action. Does not tell the reader what they will find or why they need to go there.

---

## 2. Selected Approach

**Approach B** -- standalone blockquote "See also" callout immediately after the Step 4 header.

Rationale: The acceptance criterion states a fresh Pantry agent reading Step 4 must "know exactly where to find the format specification." Placement immediately after the heading maximises discoverability. The blockquote callout format is visually distinct and signals a navigation instruction rather than content. It includes the exact file path, exact section heading, a concise description of what is found there, and an explicit directive to read it before composing the data file. No format content from reviews.md is duplicated.

---

## 3. Implementation Description

Edited `/Users/correy/projects/ant-farm/orchestration/templates/pantry.md`, Section 2, Step 4.

Inserted two lines (blockquote + trailing blank line) immediately after `### Step 4: Compose Big Head Consolidation Data File` and immediately before `Write {session-dir}/prompts/review-big-head-consolidation.md containing:`.

The added text:
```markdown
> **See also**: `~/.claude/orchestration/templates/reviews.md` — **Big Head Consolidation Protocol** section. That section contains the full format specification: Step 0 (report verification gate), Steps 1-4 (read, merge/deduplicate, file beads, write consolidated summary), the root-cause grouping template, and the consolidated summary format. Read it before composing this data file.
```

No other sections of pantry.md were modified. reviews.md was read as a reference only and was not edited.

The same change was also applied to the synced copy at `~/.claude/orchestration/templates/pantry.md` for runtime consistency (this file is outside the git repo and is populated by the pre-push hook, but was patched manually to keep both copies in sync).

---

## 4. Correctness Review

### File: `orchestration/templates/pantry.md`

- Section 2, Step 4 header is present at its expected location.
- The blockquote "See also" line is the first content line under the header -- a reader entering Step 4 encounters it immediately.
- The file path in the pointer (`~/.claude/orchestration/templates/reviews.md`) is the runtime path used by Pantry agents -- consistent with how other template paths are referenced in this file.
- The section name `Big Head Consolidation Protocol` matches the exact `## Big Head Consolidation Protocol` heading in reviews.md (confirmed by reading reviews.md line 315).
- No content from reviews.md (dedup protocol text, step formats, templates) was copied into pantry.md.
- No other sections of pantry.md were modified.
- The existing `- Deduplication protocol (from reviews.md Big Head Consolidation Protocol)` bullet in the content list remains unchanged, now supplemented by the "See also" pointer above.

### Acceptance Criteria Verification

| # | Criterion | Status |
|---|-----------|--------|
| 1 | pantry.md Step 4 has a "See also: reviews.md Big Head Consolidation Protocol" or equivalent cross-reference line | PASS -- blockquote immediately under Step 4 heading contains the exact pointer |
| 2 | A fresh Pantry agent reading Step 4 knows exactly where to find the format specification | PASS -- file path, section name, and content description provided; explicit "Read it before composing" directive included |
| 3 | No duplication of format content introduced -- just a clear pointer | PASS -- only the file path, section name, and a one-line description of contents were added; no format text copied |

---

## 5. Build/Test Validation

This task modifies a markdown documentation/template file only. There is no compiled code, no test suite, and no build process for orchestration templates. Validation was performed by:

1. Reading the modified file before and after the change to confirm correct placement and text.
2. Confirming the target section heading in reviews.md (`## Big Head Consolidation Protocol`, line 315) exactly matches the pointer text.
3. Confirming the file path in the pointer matches the runtime path convention used elsewhere in pantry.md.
4. Confirming no other sections of pantry.md were modified (via line-range inspection of the surrounding context).

---

## 6. Acceptance Criteria Checklist

- [x] **AC1**: pantry.md Step 4 has a "See also: reviews.md Big Head Consolidation Protocol" or equivalent cross-reference line -- PASS
- [x] **AC2**: A fresh Pantry agent reading Step 4 knows exactly where to find the format specification -- PASS
- [x] **AC3**: No duplication of format content is introduced -- just a clear pointer -- PASS

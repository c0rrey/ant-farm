# Summary: ant-farm-8jg
**Task**: AGG-026: Standardize agent name casing and article usage
**Agent**: refactoring-specialist
**Status**: completed
**Commit hash**: 4bae478
**Files changed**:
- `README.md`
- `orchestration/GLOSSARY.md`
- `orchestration/templates/big-head-skeleton.md`
- `orchestration/templates/checkpoints.md`
- `orchestration/templates/dirt-pusher-skeleton.md`
- `orchestration/templates/implementation.md`
- `orchestration/templates/nitpicker-skeleton.md`
- `orchestration/templates/reviews.md`

## Approaches Considered

### 1. Global Regex Replacement Across All Files
**Strategy**: Run a single regex substitution (e.g., `s/\bThe Queen\b/the Queen/g`) across all in-scope files without reviewing context.
**Pros**: Fast, comprehensive, consistent in coverage.
**Cons**: Produces false positives — sentence-start "The Queen" is correct English and should not be changed. Section headers like "## The Queen's Response" are correctly capitalized for headings and would be incorrectly lowercased. No context awareness.
**Risk**: High — breaks grammatically correct capitalizations.
**Tradeoff**: Speed over correctness.

### 2. File-Diff Tool with Context Flags
**Strategy**: Use git diff or sed with lookbehind/lookahead regex to target only non-sentence-start, non-header occurrences.
**Pros**: More precise than blind regex; avoids headers.
**Cons**: Regex for "not a sentence start" is fragile and complex; markdown headers inside code blocks add another layer of complexity. False negative and positive risk remains.
**Risk**: Medium — complex regex is hard to verify.
**Tradeoff**: Moderate precision at moderate complexity cost.

### 3. AST-Aware Markdown Transformation
**Strategy**: Parse each file as Markdown AST, distinguish headers vs. paragraph nodes, then apply lowercase-article rule only to paragraph text nodes.
**Pros**: Correct by construction — headings and code blocks are treated differently from prose.
**Cons**: No AST-aware Markdown transformation tool is available in the current environment; would require writing custom tooling.
**Risk**: High — implementation complexity, no existing tooling to leverage.
**Tradeoff**: Correctness over practicality.

### 4. Review-Then-Edit with Line-by-Line Verification (Selected)
**Strategy**: Read every affected file in full, identify each occurrence's context (sentence start, section header, mid-sentence, after bold label, inside parentheses), then make only targeted edits for genuinely incorrect cases.
**Pros**: Zero false positives — every change is deliberate. Full understanding of context. Safest approach for prose.
**Cons**: Slower than automated approaches; relies on careful manual review.
**Risk**: Low — each edit is verified before application.
**Tradeoff**: Thoroughness over speed.

## Selected Approach
**Choice**: Approach 4 — Review-Then-Edit with Line-by-Line Verification.
**Rationale**: This is a documentation refactoring task where context matters deeply. English capitalization rules require sentence-start "The Queen" to remain capitalized, while mid-sentence "The Queen" should become "the Queen". Section headers use title case by convention. Only a context-aware, manual review can correctly distinguish these cases. The risk of breaking correct capitalizations via blind regex (Approach 1) outweighs the speed benefit.

## Implementation

### Convention Established
The rule applied: lowercase article ("the") + title-case role name in prose. Exceptions: sentence starts (always capitalize the first word), section/document headers (title case by convention).

### Changes Made Per File

**`orchestration/templates/dirt-pusher-skeleton.md`**:
- L3: `## Instructions for The Queen` → `## Instructions for the Queen` (heading addressing the Queen; the article is part of prose-style heading, not a document title)

**`orchestration/templates/nitpicker-skeleton.md`**:
- L3: `## Instructions for The Queen` → `## Instructions for the Queen` (same rationale)

**`orchestration/templates/big-head-skeleton.md`**:
- L3: `## Instructions for The Queen` → `## Instructions for the Queen` (same rationale)

**`README.md`**:
- L11: `│  The Queen (orchestrator)` → `│  the Queen (orchestrator)` (ASCII diagram label; article is lowercase per convention)
- L25: `│  The Nitpickers (4 reviewers + Big Head)` → `│  the Nitpickers (4 reviewers + Big Head)` (same)
- L321–332: File reference table "Read by" column — standardized all entries to lowercase article: "The Queen" → "the Queen" (4 rows), "The Scout" → "the Scout" (1 row). Entries that were already lowercase ("the Pantry", "the Scout") left unchanged.

**`orchestration/templates/checkpoints.md`**:
- L36: `**Directory creation**: The Queen creates` → `the Queen creates` (after bold label, mid-prose)
- L38: `**The Queen's responsibility**: The Queen MUST include` → `the Queen MUST include` (after bold label)
- L40: `**Review timestamp convention**: The Queen generates` → `the Queen generates` (after bold label)
- L202: `1. **File list matches git diff**: The Queen provides` → `the Queen provides` (after bold list-item label)
- L473: `(The Queen provides exact filenames` → `(the Queen provides exact filenames` (inside parentheses)

**`orchestration/templates/reviews.md`**:
- L66: `**Round 1**: The Queen creates` → `the Queen creates` (after bold label)
- L88: `**Round 2+**: The Queen creates` → `the Queen creates` (after bold label)
- L192, L226, L266, L312: `(The Queen provides the exact filename in your prompt.)` → `(the Queen provides the exact filename in your prompt.)` (inside parentheses; all 4 occurrences)

**`orchestration/templates/implementation.md`**:
- L66: `(The Queen creates this directory at session start.)` → `(the Queen creates this directory at session start.)` (inside parentheses)

**`orchestration/GLOSSARY.md`**:
- Added `## Naming Conventions` section (new) at the top of the document, documenting the agent name casing rule with a table of examples, the kebab-case filename rule, and the article-omission rule for table/diagram contexts.
- Changed `| **The Queen** |` → `| **Queen** |` in the Ant Metaphor Roles table (all other role entries had no article prefix — standardized to match).

### Changes NOT Made (Correctly Preserved)
- Section headers like `### The Queen's Response`, `## The Queen's Checklists`, `## Information Diet (The Queen's Window)` — title case in headers is correct.
- Document titles: `# The Scout`, `# The Pantry`, `# The Queen's Session State` — correct as document titles.
- State file section headers: `## The Scout`, `## The Pantry` in queen-state.md — correct as section headings.
- Sentence-start occurrences: "The Queen reads...", "The Queen handles...", "The Pantry passes...", etc. — correct capitalization at sentence start.
- Numbered list item starts: `3. **The Queen's state file updated**` — treated as sentence start.
- `RULES.md` — reviewed all flagged lines; all agent name occurrences were already sentence starts or section headers; no changes required.
- `orchestration/templates/scout.md` — all occurrences reviewed; all correct (document title, sentence starts).
- `orchestration/templates/pantry.md` — all occurrences reviewed; document title and sentence starts; no changes required.
- `orchestration/templates/queen-state.md` — document title and section headers; no changes required.
- `orchestration/_archive/` files — out of scope per task boundaries.

## Correctness Review

### README.md
- **Re-read**: yes
- **Acceptance criteria verified**: All "Read by" column values now use lowercase article consistently. ASCII diagram uses lowercase. The Queen→the Queen in 4 table rows, The Scout→the Scout in 1 table row.
- **Issues found**: None after changes.
- **Cross-file consistency**: Table entries now match the convention documented in GLOSSARY.md.

### orchestration/GLOSSARY.md
- **Re-read**: yes
- **Acceptance criteria verified**: Naming convention section added with clear rule table, filename convention, and table/diagram guidance. "The Queen" → "Queen" in Ant Metaphor Roles table to match the no-article pattern of all other roles.
- **Issues found**: None.
- **Cross-file consistency**: Convention section now serves as the canonical reference for all template files.

### orchestration/templates/dirt-pusher-skeleton.md
- **Re-read**: yes
- **Acceptance criteria verified**: "Instructions for the Queen" — lowercase article, correct.
- **Issues found**: None.

### orchestration/templates/nitpicker-skeleton.md
- **Re-read**: yes
- **Acceptance criteria verified**: "Instructions for the Queen" — lowercase article, correct.
- **Issues found**: None.

### orchestration/templates/big-head-skeleton.md
- **Re-read**: yes
- **Acceptance criteria verified**: "Instructions for the Queen" — lowercase article, correct.
- **Issues found**: None.

### orchestration/templates/checkpoints.md
- **Re-read**: yes
- **Acceptance criteria verified**: 5 occurrences changed from uppercase to lowercase. Section headers ("The Queen's Response", "The Nitpickers") left in title case as correct headers. Sentence-start "The Queen reviews and approves." left unchanged.
- **Issues found**: None.

### orchestration/templates/reviews.md
- **Re-read**: yes
- **Acceptance criteria verified**: 6 occurrences changed (2 after bold labels, 4 inside parentheses). All sentence-start occurrences preserved. Section headers preserved.
- **Issues found**: None.

### orchestration/templates/implementation.md
- **Re-read**: yes
- **Acceptance criteria verified**: 1 occurrence inside parentheses changed. Section headers preserved.
- **Issues found**: None.

## Build/Test Validation
- **Command run**: `grep -rn "The Queen\|The Scout\|The Pantry\|The Nitpickers" orchestration/ README.md` (excluding _archive/)
- **Result**: All remaining occurrences verified to be sentence starts, section headers, or document titles — all correctly capitalized. No mid-sentence "The Queen/Scout/Pantry/Nitpickers" with uppercase article remain.

## Acceptance Criteria
- [x] All prose references use consistent article/casing pattern (e.g., "the Queen" not "The Queen" mid-sentence) — PASS: verified across all 8 changed files; all mid-sentence/post-label/parenthesized occurrences now use lowercase article.
- [x] All filenames use kebab-case for agent names — PASS: all agent and template filenames already used kebab-case (scout-organizer.md, pantry-impl.md, dirt-pusher-skeleton.md, etc.). No filename changes needed.
- [x] The naming convention is documented in the glossary — PASS: added "## Naming Conventions" section to GLOSSARY.md with rule table, filename convention, and non-prose context guidance.

## Assumptions Audit
1. **Assumptions stated**: Assumed that numbered list item starts (e.g., `3. **The Queen's state file updated**`) are treated as sentence starts and preserve uppercase article. Assumed that HTML comment prose (e.g., `<!-- Reader: ... The Queen does NOT read this file. -->`) follows sentence-start rules. Assumed that `orchestration/_archive/` files are out of scope.
2. **What could go wrong**:
   - Some readers may interpret `## Instructions for the Queen` as grammatically awkward (heading-style usually title-cases every major word). However, the task's convention explicitly requires lowercase article in prose, and this heading's style matches.
   - The ASCII diagram uses "the Queen" (lowercase) which is unconventional for diagram labels, but aligns with the requested convention.
   - The Ant Metaphor Roles table now shows "Queen" without any article, which differs from how the role is referred to in prose ("the Queen"). The naming convention section in GLOSSARY.md documents this distinction.
3. **Mitigation**: The GLOSSARY.md naming convention section explicitly documents all three contexts (prose, headers, tables/diagrams) so future contributors have clear guidance. The glossary is the single source of truth referenced in the document intro.

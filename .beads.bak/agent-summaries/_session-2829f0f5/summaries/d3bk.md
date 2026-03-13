# Summary: ant-farm-d3bk

## Approaches Considered

1. **Add a parenthetical note after the script block** — Insert a note below the `bash` code block in Step 3b-ii explaining that `<changed-files>` and `<task-IDs>` accept an `@filepath` prefix for multiline values. Minimal change, non-intrusive to the code block, discoverable in normal reading order.

2. **Add inline comments in the bash code block** — Insert `# or @filepath` comments next to the `<changed-files>` and `<task-IDs>` arguments within the code block. Tradeoff: inline comments in a code block are unusual for a documentation context; they make the block harder to copy-paste.

3. **Add a "Note" callout before the script block** — Use a blockquote or bold "Note:" line before the bash block. Tradeoff: interrupts the reading flow; a post-block note is more natural for supplementary information.

4. **Update the argument placeholders in the bash block** — Change `"<changed-files>"` to something like `"<changed-files|@filepath>"`. Tradeoff: placeholder names become unwieldy; inconsistent with the rest of the document's convention for placeholder names.

## Selected Approach

**Add a parenthetical note after the script block** (Approach 1).

Rationale: The @file feature is supplementary information — useful to know but not needed to understand the primary invocation pattern. A post-block note is the appropriate place for such supplementary content. It is immediately discoverable after reading the script block, does not alter the code block (which should remain copy-pasteable), and matches the style of other notes in RULES.md.

## Implementation Description

Added three lines below the closing triple-backtick of the build-review-prompts.sh bash block in RULES.md Step 3b-ii:

```
Note: `<changed-files>` and `<task-IDs>` accept an `@filepath` prefix to read multiline
values from a file (e.g., `@/tmp/changed-files.txt`). Use this to avoid shell quoting
issues when the list contains many entries or paths with spaces.
```

This note is inserted between the closing backtick block and the "On exit 0" success/failure outcome lines.

The reference file for this feature is scripts/build-review-prompts.sh lines 23-26 (comment block) and lines 74-86 (resolve_arg function). The note accurately reflects what the script implements.

## Correctness Review

**orchestration/RULES.md Step 3b-ii:**
- @file prefix mentioned: yes
- Example path given (`@/tmp/changed-files.txt`): yes
- Both applicable arguments named (`<changed-files>` and `<task-IDs>`): yes
- Explanation of when to use it (multiline values, quoting issues): yes
- Existing script invocation block unchanged: yes
- On exit 0 / On non-zero outcome lines unchanged: yes

**Acceptance Criteria Verification:**
1. RULES.md mentions @file prefix for multiline arguments (optional note/parenthetical) — PASS

## Build/Test Validation

Documentation-only change. No build or test pipeline applies. The @file feature is verified by reading scripts/build-review-prompts.sh lines 74-86 (resolve_arg) and lines 23-26 (usage comment block), which confirm the implementation matches the documentation.

## Acceptance Criteria Checklist

1. RULES.md mentions @file prefix for multiline arguments (optional note/parenthetical) — **PASS**

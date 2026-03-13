# Task Summary: ant-farm-a2ot

**Task**: fix: CONTRIBUTING.md cross-file update checklist omits GLOSSARY.md
**Agent**: technical-writer
**Status**: complete

---

## 1. Approaches Considered

**Approach A — Append as item 4 after the existing three items (selected)**
Add `4. **\`orchestration/GLOSSARY.md\`** -- add the agent to the "Ant Metaphor Roles" table` as the next numbered item in the ordered list. Preserves the existing structure and formatting, is immediately readable, and matches the style of the existing three entries.

**Approach B — Insert alphabetically between existing items**
Insert GLOSSARY.md between README.md and RULES.md since "G" sorts before "R". This would require renumbering items 2 and 3, creating a larger diff for no practical navigational benefit in an ordered checklist.

**Approach C — Replace the entire checklist with a rewritten version**
Delete lines 39-41 and rewrite all four items from scratch. Achieves the same result but introduces unnecessary risk of altering wording, spacing, or emphasis on the existing three items that are known-good.

**Approach D — Add a "See also" note below the checklist**
Leave the numbered list unchanged and add a prose note below it pointing to GLOSSARY.md. This is less discoverable than a checklist item and does not integrate cleanly into the task-by-task workflow the checklist represents. Does not satisfy "checklist includes GLOSSARY.md" literally.

---

## 2. Selected Approach with Rationale

Approach A — append as item 4. The checklist uses a simple numbered list; appending item 4 requires no renumbering and matches the established style (bold backtick filename, double-dash, prose description). The description mirrors the level of detail in existing entries (what to do and where).

---

## 3. Implementation Description

One edit made to `CONTRIBUTING.md`:

Added a new line immediately after item 3 in the "Cross-file updates after adding an agent" ordered list:

```
4. **`orchestration/GLOSSARY.md`** -- add the agent to the "Ant Metaphor Roles" table (lines 77-85)
```

The line number reference (lines 77-85) was confirmed by reading `orchestration/GLOSSARY.md` lines 70-90, where the Ant Metaphor Roles table header appears at line 76 and the table body spans lines 78-86.

---

## 4. Correctness Review

**File: `CONTRIBUTING.md`**

- Lines 37-43 verified post-edit: the four-item checklist is present with correct numbering, formatting, and content.
- Item 4 reads: `4. **\`orchestration/GLOSSARY.md\`** -- add the agent to the "Ant Metaphor Roles" table (lines 77-85)`
- No adjacent lines were modified.
- GLOSSARY.md (reference only, not edited): Ant Metaphor Roles table confirmed at lines 76-86 of `orchestration/GLOSSARY.md`.
- Acceptance criterion 1 (checklist includes GLOSSARY.md Ant Metaphor Roles table): PASS

---

## 5. Build/Test Validation

This is a Markdown documentation file with no build or test pipeline. Validation consisted of:
- Re-reading CONTRIBUTING.md lines 37-44 post-edit to confirm the new item appears correctly and no surrounding content was disturbed.
- Confirming the GLOSSARY.md table reference is accurate by reading the actual file.

---

## 6. Acceptance Criteria Checklist

| # | Criterion | Result |
|---|-----------|--------|
| 1 | CONTRIBUTING.md checklist includes GLOSSARY.md Ant Metaphor Roles table | PASS |

---

**Commit hash**: (recorded after commit)

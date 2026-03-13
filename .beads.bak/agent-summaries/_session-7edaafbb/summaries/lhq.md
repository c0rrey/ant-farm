# Summary: ant-farm-lhq
**Task**: Scout error metadata template lacks context fields (Title, Epic) present in success template
**Agent**: general-purpose
**Status**: completed
**Files changed**:
- orchestration/templates/scout.md (L272-284)

**Commit**: 6c45fe4

---

## 1. Approaches Considered

**Approach A — Add only the two required fields (Title and Epic)**
Add only `**Title**` and `**Epic**` to the error template, both sourced from bd list output when available. Pro: minimally satisfies acceptance criteria. Con: misses an opportunity to add Type and Priority which are also available from bd list at no additional cost.

**Approach B — Mirror the full success template with all fields marked unavailable**
Copy the full success template structure and mark every field that requires bd show as `(unavailable — bd show failed)`. Pro: maximum structural parity with success template. Con: bloated for an error case; fields like Affected Files, Root Cause, and Acceptance Criteria have no plausible fallback source, so marking them all individually adds noise without value.

**Approach C — Add Title, Type, Priority, Epic (all available from bd list), mark deeper fields unavailable**
Add the four "surface" fields available from bd list/bd ready output (Title, Type, Priority, Epic) using their actual values when possible, and add a single "Note:" line listing all the fields that could not be populated. Pro: maximizes useful context, maintains consistent field ordering with the success template, uses a single clear Note instead of per-field unavailable markers. Satisfies both acceptance criteria cleanly.

**Approach D — Add a separate "Partial Context" block after Error Details**
Keep the existing Status and Error Details fields, then add a `## Partial Context (from bd list)` section. Pro: visually separates "what failed" from "what we have." Con: diverges structurally from the success template; downstream agents parsing the file expect flat fields, not mixed flat/heading structure.

---

## 2. Selected Approach

**Approach C — add four bd-list-available fields (Title, Type, Priority, Epic) with a Note line for unavailable fields.**

Rationale: The four fields (Title, Type, Priority, Epic) are routinely available from `bd ready` or `bd list` output collected during Step 2, before any `bd show` attempt. Adding them preserves the same field ordering as the success template (Title → Type → Priority → Epic → ...), making both templates easier to read and parse consistently. A single "Note:" line at the end cleanly documents which deeper fields could not be populated, rather than cluttering each field with "(unavailable)" markers.

---

## 3. Implementation Description

Changed the "Example error metadata file" block at scout.md L272-277 (previously 6 lines) to 12 lines:

Before:
```markdown
# Task: {task-id}
**Status**: error
**Error Details**: {exact error message from bd show}
```

After:
```markdown
# Task: {task-id}
**Status**: error
**Title**: {title from bd list, or "unknown — not in listing"}
**Type**: {type from bd list, or "unknown"}
**Priority**: {priority from bd list, or "unknown"}
**Epic**: {epic-id from bd list, or "unknown"}
**Error Details**: {exact error message from bd show}

Note: Affected Files, Root Cause, Agent Type, Dependencies, and Acceptance Criteria
could not be populated — bd show failed.
```

Key decisions:
- Title and Epic appear before Error Details (not after) — consistent with success template field order
- Type and Priority added alongside Title and Epic since they're all equally available from bd list
- "unknown — not in listing" handles the edge case where a task ID wasn't in the bd list results
- Note line enumerates the specific fields that bd show would have provided but couldn't
- Error Details field retained in its existing position

---

## 4. Correctness Review

**orchestration/templates/scout.md (L265-293)**
- Error Handling section header unchanged — correct.
- Prose description (L267-270) unchanged — correct.
- Error metadata example (L272-284): Now includes Title, Type, Priority, Epic fields with bd-list fallback values. Error Details retained. Note line documents unavailable fields. CORRECT.
- Subsequent error handling bullets (L285-292) unchanged — correct.
- Success template (L86-110) cross-reference: error template field order (Title, Type, Priority, Epic) matches success template field order. CORRECT.
- Acceptance criterion 1: PASS — error template now includes Title and Epic fields.
- Acceptance criterion 2: PASS — Note line at end of template clearly marks which fields (Affected Files, Root Cause, Agent Type, Dependencies, Acceptance Criteria) could not be populated due to bd show failure.

---

## 5. Build/Test Validation

Documentation-only change to a markdown template file. No build or test commands apply.

Manual verification: The error template is structurally consistent with the success template, with Title, Type, Priority, and Epic in the same relative order. The Note line is clear and actionable.

---

## 6. Acceptance Criteria Checklist

1. Error metadata template includes Title and Epic fields (from bd list output) — **PASS** (both fields added with explicit "from bd list" sourcing notation, plus Type and Priority as bonus)
2. Error template clearly marks which fields could not be populated — **PASS** (Note line explicitly enumerates: "Affected Files, Root Cause, Agent Type, Dependencies, and Acceptance Criteria could not be populated — bd show failed")

# Task Summary: ant-farm-o0wu
**Task**: Migrate RULES-review.md (semantic)
**Commit**: 710ec47
**Status**: Complete

---

## 1. Approaches Considered

**Approach A — Targeted line-by-line edits (selected)**
Make three discrete Edit calls, each targeting a unique context string at the exact changed line. Advantages: minimal diff, zero risk of unintended changes, each edit is individually auditable and maps directly to one acceptance criterion. Disadvantage: slightly more tool calls than a bulk approach.

**Approach B — Global word-boundary search-and-replace**
Replace all `\bbd\b` occurrences with `crumb` in a single pass, then a second pass for `.beads/`. Advantage: handles any missed instances automatically. Disadvantage: `bd` could appear as a substring in non-command contexts (e.g., inside code variable names), risking false replacements. Requires careful review after.

**Approach C — Full file rewrite**
Read the file content, perform string substitutions in memory, write the entire file back with the Write tool. Advantage: atomic. Disadvantage: most error-prone for preserving exact whitespace and indentation; any transcription error corrupts the whole file.

**Approach D — Sed in-place substitution via Bash**
Use `sed -i` to perform regex substitutions. Advantage: concise. Disadvantage: bypasses the read-before-edit constraint enforced by the Edit tool; harder to audit interactively; platform-specific sed behavior differences on macOS vs Linux.

---

## 2. Selected Approach

Approach A — targeted line-by-line edits.

Rationale: The task had exactly three change sites, all with unique surrounding context strings. Targeted edits produce a minimal, reviewable diff with no collateral risk. The acceptance criteria map one-to-one to specific line ranges, so precision is more valuable than bulk automation here.

---

## 3. Implementation Description

Three edits were made to `orchestration/RULES-review.md`:

- **L23**: Changed `.beads/issues.jsonl` to `.crumbs/issues.jsonl` and "auto-generated beads files" to "auto-generated crumbs files" in the file-list gather step of 3b-i.
- **L155**: Changed `bd show <bead-id>` to `crumb show <bead-id>` in the Fix DP prompt structure.
- **L158**: Changed `bd update <bead-id> --note="commit: <hash>"` to `crumb update <bead-id> --note="commit: <hash>"` in the Fix DP prompt structure.

All three changes were strictly command syntax substitutions. No review step ordering, commit range logic, file list generation workflow, or prose was altered.

---

## 4. Correctness Review

**File: orchestration/RULES-review.md**

Reviewed the full 215-line file after all edits.

- L23: Confirmed `.crumbs/issues.jsonl` and "crumbs files" are present; no `.beads/` references remain.
- L155: Confirmed `crumb show <bead-id>` is present; no `bd show` remains.
- L158: Confirmed `crumb update <bead-id> --note="commit: <hash>"` is present; no `bd update` remains.
- All surrounding prose, indentation, blank lines, and step numbering are unchanged.
- Workflow logic (step ordering, round cap rules, SendMessage flows, progress log entries, SSV gate) is fully preserved.
- No adjacent issues were altered.

---

## 5. Build/Test Validation

```
$ grep -c '\bbd\b' orchestration/RULES-review.md
0

$ grep -n '\.beads/' orchestration/RULES-review.md
(no output)
```

Both shell checks pass. No test suite runs required for a documentation-only change.

---

## 6. Acceptance Criteria Checklist

- [x] All bd command references replaced with crumb equivalents — PASS (grep -c returns 0)
- [x] Review workflow logic preserved — only command syntax changes — PASS (step ordering, round logic, all prose unchanged)
- [x] grep -c '\bbd\b' orchestration/RULES-review.md returns 0 — PASS (confirmed: output is 0)
- [x] Any .beads/ path references updated to .crumbs/ (L23: .beads/issues.jsonl exclusion) — PASS (no .beads/ references remain)

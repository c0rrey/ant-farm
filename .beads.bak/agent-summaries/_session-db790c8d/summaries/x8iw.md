# Summary: ant-farm-x8iw

**Task**: fix: Scout agent frontmatter declares model: sonnet, contradicting RULES.md model: opus
**Commit**: 7569c5e
**Date**: 2026-02-22

---

## 1. Approaches Considered

### Approach A: Manual targeted edits (selected)
Use the Edit tool for precise, line-level replacements in each of the three affected files. Each edit targets exactly the field that needs updating ("sonnet" → "opus") with enough surrounding context to be unambiguous. No risk of touching legitimately-sonnet values elsewhere (e.g., Dirt Pusher model, Pest Control DMVDC mode, Nitpicker rows).

**Tradeoffs**: Maximum precision and reviewability. Slightly more verbose than a one-liner shell command but each change is independently verifiable.

### Approach B: sed in-place substitution
Run `sed -i 's/| sonnet /| opus /g'` across the three files. Faster to type but the regex `| sonnet |` would match any table cell containing "sonnet" — a pattern that legitimately appears in the Pest Control row (`haiku (CCO, WWD, CCB), sonnet (DMVDC)`) and the Nitpicker row. The substitution would need context-aware anchoring to be safe.

**Tradeoffs**: Fast but fragile. Any imprecision in the regex risks corrupting legitimate "sonnet" references.

### Approach C: Global find-and-replace across the repo
Replace every occurrence of "sonnet" with "opus" in all `.md` files. Guaranteed to break: Dirt Pusher model assignment in RULES.md ("model: "sonnet" for all Dirt Pushers"), Pest Control DMVDC row ("sonnet (DMVDC)"), Nitpicker row ("sonnet"), and historical audit/session artifact content. Definitively wrong approach for this scope.

**Tradeoffs**: Maximally destructive. Not viable.

### Approach D: Patch file approach
Compose a unified diff manually and apply with `git apply`. Accurate and auditable, but more complex to write than direct Edit calls with no additional safety benefit for four targeted one-word changes. The Edit tool provides equivalent precision with less ceremony.

**Tradeoffs**: Unnecessary overhead for changes this small.

---

## 2. Selected Approach

**Approach A: Manual targeted edits.**

Rationale: Four discrete changes, each in a different field of a different file. The Edit tool with sufficient surrounding context anchors the replacement precisely. No risk of collateral damage to the Dirt Pusher "sonnet", Pest Control rows, or Nitpicker rows — all of which legitimately say "sonnet" and must not be changed.

---

## 3. Implementation Description

Three files were changed, four values updated:

1. **`agents/scout-organizer.md` L5** — Frontmatter `model: sonnet` → `model: opus`. This is the highest-severity fix: the frontmatter is the fallback model when the Queen omits the `model` parameter at spawn time.

2. **`orchestration/GLOSSARY.md` L80** — Scout row Model column: `sonnet` → `opus`.

3. **`orchestration/GLOSSARY.md` L81** — Pantry row Model column: `sonnet` → `opus`.

4. **`README.md` L75** — "a sonnet subagent" → "an opus subagent". Note: article changed from "a" to "an" to maintain grammatical correctness before a vowel sound.

No files outside the scope boundary were modified. `orchestration/RULES.md` was read as reference only and not edited (it was already correct at L294–L295).

---

## 4. Correctness Review

### agents/scout-organizer.md
- **Line 5**: `model: opus` — correct. Matches RULES.md L294: `| Scout | Task (scout-organizer) | opus |`.
- No other model references in this file.
- Frontmatter block is syntactically valid YAML. No other frontmatter fields affected.

### orchestration/GLOSSARY.md
- **Line 80 (Scout row)**: Model column now reads `opus`. Matches RULES.md L294.
- **Line 81 (Pantry row)**: Model column now reads `opus`. Matches RULES.md L295: `| Pantry (impl) | Task (pantry-impl) | opus |`.
- **Line 82 (Pest Control row)**: Unchanged. Still reads `haiku (CCO, WWD, CCB), sonnet (DMVDC)` — correct per RULES.md L297–L300.
- **Line 84 (Nitpicker row)**: Unchanged. Still reads `sonnet` — correct per RULES.md L301.
- Table structure intact; no columns misaligned.

### README.md
- **Line 75**: Now reads "an opus subagent" — correct. Article change from "a" to "an" is grammatically required before vowel sounds.
- No other Scout/Pantry model references in README.md.

### Acceptance Criteria verification
1. `agents/scout-organizer.md` frontmatter says `model: opus` — CONFIRMED at L5.
2. `orchestration/GLOSSARY.md` Scout row says `opus` — CONFIRMED at L80.
3. `orchestration/GLOSSARY.md` Pantry row says `opus` — CONFIRMED at L81.
4. `README.md` Scout description says "opus" not "sonnet" — CONFIRMED at L75.
5. Grep for `Scout.*sonnet|sonnet.*Scout|Pantry.*sonnet|sonnet.*Pantry` across `*.md`: remaining matches are exclusively in `.beads/agent-summaries/` session artifacts, `docs/audits/` audit reports (which correctly describe the pre-fix state), and `orchestration/RULES.md` L106 (Dirt Pusher model — legitimately sonnet). No matches in any editable source file.

---

## 5. Build/Test Validation

This task touches only documentation and frontmatter metadata fields. There are no compilation steps, no test suite exercised by model-name changes in markdown. The relevant validation is:

- **Grep check** (criterion 5): Passed. No remaining `Scout.*sonnet` or `Pantry.*sonnet` in editable source files.
- **Git diff review**: `git diff` output verified — exactly 4 lines changed (+4 / -4), all within scope boundary. No unintended changes.
- **Frontmatter YAML validity**: `model: opus` is valid YAML. No syntax errors.

---

## 6. Acceptance Criteria Checklist

| # | Criterion | Status |
|---|-----------|--------|
| 1 | `agents/scout-organizer.md` frontmatter says `model: opus` | PASS |
| 2 | `orchestration/GLOSSARY.md` Scout row says `opus` | PASS |
| 3 | `orchestration/GLOSSARY.md` Pantry row says `opus` | PASS |
| 4 | `README.md` Scout description says "opus" not "sonnet" | PASS |
| 5 | No other files reference Scout or Pantry as sonnet-tier agents (grep verification) | PASS |

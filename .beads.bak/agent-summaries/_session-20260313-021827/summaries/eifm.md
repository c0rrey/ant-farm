# Task Summary: ant-farm-eifm
**Task**: Migrate queen-state and session plan templates (mechanical)
**Commit**: 06c0011

---

## 1. Approaches Considered

**Approach A — Targeted Edit calls (selected)**
Apply the Edit tool once per occurrence. Each substitution is explicitly verified before and after. Changes are minimal, scoped to the exact lines identified by grep, and do not touch surrounding content.
Tradeoff: Requires more individual tool calls but produces a fully auditable change history.

**Approach B — Full file rewrite via Write tool**
Reconstruct entire file content in memory from the Read output, apply substitutions mentally, write the whole file back.
Tradeoff: Risk of subtle whitespace drift or accidental omission when reconstructing ~79 and ~353 line files by hand. Not suitable for mechanical accuracy requirements.

**Approach C — Grep-first enumeration, then targeted Edits**
Run Grep on both files before touching anything to enumerate all `bd`, `.beads/`, and `beads` occurrences. Then apply targeted Edit calls only for confirmed lines.
Tradeoff: Adds one round-trip per file but provides pre-edit confirmation of scope. This was the selected approach.

**Approach D — Shell sed commands**
Use `sed -i` with word-boundary patterns to perform all substitutions in one pass per file.
Tradeoff: The task brief prohibits using sed when a dedicated tool is available. Also, macOS BSD sed requires different escaping than GNU sed, making the commands fragile across environments.

---

## 2. Selected Approach

Approach C (Grep-first, then targeted Edit calls) was selected because:
- Grep output confirmed exact line numbers and surrounding context before any file was touched.
- Edit calls are minimal and verifiable against the known source text.
- No full-file reconstruction risk.
- The post-edit grep re-run directly validates the acceptance criterion (`\bbd\b` count = 0).

---

## 3. Implementation Description

**queen-state.md (2 edits):**
- Line 8: `.beads/agent-summaries/_session-<session-id>` replaced with `.crumbs/sessions/_session-<session-id>`
- Line 74: `` `bd` database (via Scout) ... lag behind bd; `` replaced with `` `crumb` database (via Scout) ... lag behind crumb; ``

**SESSION_PLAN_TEMPLATE.md (4 edits):**
- Line 271: `All beads tasks closed (bd close <ids>)` replaced with `All crumbs tasks closed (crumb close <ids>)`
- Lines 288 and 291: `- [ ] \`bd sync\` (sync beads with remote)` and `- [ ] Beads sync status clean (bd sync --status)` were removed entirely (no sync step needed with JSONL-based crumb)
- Line 297: `New beads filed (if any remain open)` replaced with `New crumbs filed (if any remain open)`

No other files were modified.

---

## 4. Correctness Review

**queen-state.md**
- Line 8 now reads: `**Session dir**: .crumbs/sessions/_session-<session-id>` — correct path, `_session-*` pattern preserved.
- Line 74 now reads: `` `crumb` database (via Scout) | Cache — may lag behind crumb; Scout re-syncs on next run `` — no `bd` present.
- Re-read of full file confirms no other `bd` or `.beads/` text present.

**SESSION_PLAN_TEMPLATE.md**
- Line 271: `All crumbs tasks closed (crumb close <ids>)` — correct substitution.
- Former lines 288 and 291 (bd sync references) are absent from the updated file.
- Line 295 (formerly 297): `New crumbs filed (if any remain open)` — correct.
- Re-read of the Landing the Plane section (lines 260-297) confirms the Git Operations block now contains only `git pull --rebase`, `git push`, and `git status` — no `bd sync` references remain.

---

## 5. Build/Test Validation

These are documentation-only template files. No build or test pipeline applies.

Post-edit validation performed:
- Grep tool run with pattern `\bbd\b` on both files returned 0 matches.
- Visual re-read of both files confirmed correct substitutions with no surrounding content disturbed.

---

## 6. Acceptance Criteria Checklist

| Criterion | Status |
|-----------|--------|
| queen-state.md: all `.beads/agent-summaries/` paths replaced with `.crumbs/sessions/` | PASS |
| SESSION_PLAN_TEMPLATE.md: `bd close` -> `crumb close`, `bd sync` references removed | PASS |
| `grep -c '\bbd\b'` on queen-state.md returns 0 | PASS |
| `grep -c '\bbd\b'` on SESSION_PLAN_TEMPLATE.md returns 0 | PASS |
| All 'beads' terminology updated to 'crumbs' | PASS |
| Session directory naming convention updated (`_session-*` pattern preserved) | PASS |

# Summary: ant-farm-0bez

**Task**: fix: GLOSSARY pre-push hook entry omits sync-to-claude.sh details
**Commit**: (see below)
**File changed**: `orchestration/GLOSSARY.md` (L58)

---

## 1. Approaches Considered

**Approach 1 — Minimal parenthetical expansion**
Append a parenthetical to the existing sentence listing the four missing behaviors inline. Tradeoff: produces a run-on sentence that is harder to read in a narrow table cell. The original sentence structure is also misleading (it names no script), so patching it in-place without restructuring perpetuates the structural problem.

**Approach 2 — Sentence replacement (selected)**
Replace the single vague sentence with three concise prose sentences that name the script and cover all four behaviors in the order they appear in the script. Consistent with the prose style of adjacent GLOSSARY rows. Table cell stays compact.

**Approach 3 — Inline shell code fragments**
Embed shell flag names like `--exclude='_archive/'` and `--no-delete` literally in the definition. Tradeoff: shell-level syntax is more detail than a conceptual glossary entry needs. Readers who want exact flags should read the script; the glossary entry should describe intent, not syntax.

**Approach 4 — Bulleted sub-list inside the table cell**
Enumerate the four behaviors as a markdown list. Tradeoff: makes the cell significantly taller than all other rows and breaks visual consistency across the Workflow Concepts table. Markdown list rendering inside table cells also varies across renderers.

---

## 2. Selected Approach

**Approach 2 — Sentence replacement.**

Rationale: Three tight sentences cover all four required behaviors without introducing shell syntax noise or breaking the table's visual consistency. The structure mirrors other multi-behavior entries in the same table (e.g., `summary doc`, `checkpoint`). The script is named explicitly so readers know where to look for implementation details.

---

## 3. Implementation Description

Replaced the single-sentence definition at `orchestration/GLOSSARY.md:L58` with a three-sentence definition:

- Sentence 1: Names the script (`sync-to-claude.sh`) and trigger (`git push`).
- Sentence 2: Covers the three rsync/copy operations — CLAUDE.md copy, agents sync, orchestration rsync — and states the `_archive/` exclusion and non-delete policy with its rationale.
- Sentence 3: Covers the selective script sync (only `build-review-prompts.sh`; developer tools excluded).

No other files were changed.

---

## 4. Correctness Review

**orchestration/GLOSSARY.md (L58)**

Checked against `scripts/sync-to-claude.sh:L23-44`:

| Claim in GLOSSARY | Source in script | Accurate? |
|-------------------|-----------------|-----------|
| Runs `scripts/sync-to-claude.sh` | Script filename and shebang | Yes |
| Copies `CLAUDE.md` to `~/.claude/CLAUDE.md` | L19-20: `cp "$REPO_ROOT/CLAUDE.md" ~/.claude/CLAUDE.md` | Yes |
| Syncs `agents/*.md` to `~/.claude/agents/` | L47-onwards agent sync block | Yes |
| Rsyncs `orchestration/` to `~/.claude/orchestration/` | L27: `rsync -av ... "$REPO_ROOT/orchestration/" ~/.claude/orchestration/` | Yes |
| Excludes `_archive/` | L27: `--exclude='_archive/'` | Yes |
| No `--delete` (non-delete policy) | L23-25: `--delete is intentionally omitted` comment + L27 flags | Yes |
| Only `build-review-prompts.sh` synced | L36: `for script in "$REPO_ROOT/scripts/build-review-prompts.sh"` | Yes |
| Developer tools not copied | L32-33: explicit comment excluding `sync-to-claude.sh`, `install-hooks.sh`, `scrub-pii.sh` | Yes |

Prose style is consistent with adjacent GLOSSARY rows. No markdown table formatting issues introduced.

---

## 5. Build/Test Validation

This task modifies documentation only (no code, no scripts). Build validation is not applicable. Manual check: the markdown table renders correctly with the new longer cell — no pipe characters embedded in the cell content that would break the table.

---

## 6. Acceptance Criteria Checklist

| Criterion | Status |
|-----------|--------|
| GLOSSARY pre-push hook entry mentions `_archive/` exclusion | PASS |
| GLOSSARY pre-push hook entry mentions selective script sync (only `build-review-prompts.sh`) | PASS |
| GLOSSARY pre-push hook entry mentions CLAUDE.md copy step | PASS |
| GLOSSARY pre-push hook entry mentions non-delete policy | PASS |

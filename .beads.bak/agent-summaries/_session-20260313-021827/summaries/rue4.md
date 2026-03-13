# Task Summary: ant-farm-rue4
**Task**: Migrate RULES.md (semantic)
**Commit**: 4147daf

## 1. Approaches Considered

**Approach A: Targeted surgical edits at identified lines**
Replace each identified occurrence individually, guided by the exact lines called out in the task brief (L16, L21, L55, L67, L93-94, L174, L215 area, L306, L309, L404, L437, L448, L507-508, L538, L594). Each edit is narrow, touching only the specific token or path that must change. Tradeoff: highest precision, lowest risk of side effects, but requires carefully tracking each location.

**Approach B: Global regex substitution pass**
Run a single automated replacement across the file for each pattern (`bd show` → `crumb show`, `.beads/agent-summaries/` → `.crumbs/sessions/`, etc.). Tradeoff: faster for mechanical substitutions, but risks missing context-sensitive cases (e.g., where `bd sync` appears in a bash block that needs full restructuring, not just a rename) and may hit unexpected matches in prose.

**Approach C: Section-by-section rewrite**
Rewrite each affected section wholesale, using RULES-review.md (already migrated) as the reference pattern for Steps 3b-3c, and deriving the transformations for all other sections independently. Tradeoff: preserves section-level coherence and allows catching adjacent issues, but risks inadvertent changes outside scope if the rewriter is not strictly disciplined.

**Approach D: Generate diff from a migrated reference and apply**
Diff RULES.md against RULES-review.md for the overlapping steps (3b-3c), extract the transformation patterns, then mechanically apply those patterns to the remaining sections. Tradeoff: systematic, but RULES-review.md only covers Steps 3b-3c; the rest of the file (Steps 0-2, 4-6, Session Directory, Hard Gates, Agent Types, Retry Limits) must still be handled independently.

## 2. Selected Approach

**Approach A (targeted surgical edits)** was selected. The task brief provides exact line numbers for every change required, making a targeted approach both safe and complete. The `bd sync` removal combined with the `exec-summary` copy addition at Step 6 required a structural rewrite of that bash block — a global substitution would not correctly handle this behavioral addition. Approach A accommodates these structural changes naturally.

RULES-review.md served as a validation reference (confirming `crumb show`/`crumb update` as the correct equivalents in the Fix DP prompt), but was not used as a mechanical diff source.

## 3. Implementation Description

Changes made to `orchestration/RULES.md`:

1. **Queen Prohibitions (L16, L21, L55)**: Replaced all three occurrences of `bd show`, `bd ready`, `bd list`, `bd blocked` prohibitions and the inline prose reference with `crumb` equivalents.

2. **Step 1 Scout prohibition (L93-94)**: Replaced the two-line prohibition block `Do NOT run 'bd show', 'bd ready', 'bd blocked', or any other 'bd' commands` with `crumb` equivalents.

3. **Crash recovery path (L67)**: Updated the example path from `.beads/agent-summaries/_session-<id>` to `.crumbs/sessions/_session-<id>`.

4. **Step 3b file list exclusion (L174)**: Updated `.beads/issues.jsonl` exclusion to `.crumbs/tasks.jsonl` (the correct crumb data file name).

5. **Step 6 landing-the-plane (L417-425)**: Removed `bd sync` from the bash block; updated the step description prose; added the exec-summary copy step (`cp "${SESSION_DIR}/exec-summary.md" ".crumbs/history/exec-summary-${SESSION_ID}.md"`) and its associated `git add` + `git commit` as a separate commit before `git pull --rebase && git push`.

6. **Hard Gates table (L439)**: Updated `bd close` to `crumb close`.

7. **Agent Types table (L450)**: Updated `bd CLI` to `crumb CLI` in Scout rationale.

8. **Fix DP prompt structure (L306, L309)**: Updated `bd show <bead-id>` to `crumb show <bead-id>` and `bd update <bead-id>` to `crumb update <bead-id>`.

9. **ESV prompt (L404)**: Updated `bd list` scope reference to `crumb list`.

10. **Session Directory section (L509)**: Updated `SESSION_DIR` assignment from `.beads/agent-summaries/_session-${SESSION_ID}` to `.crumbs/sessions/_session-${SESSION_ID}`.

11. **Session Directory prefix note (L540)**: Updated `agent-summaries/` reference to `.crumbs/sessions/`.

12. **Stuck-Agent Diagnostic (L596)**: Updated `.beads/agent-summaries/_session-*/` path to `.crumbs/sessions/_session-*/`.

Total: 1 file changed, 19 insertions(+), 17 deletions(-).

## 4. Correctness Review

**File reviewed**: `orchestration/RULES.md`

Scanned every changed location against the source file after editing:

- L16: `crumb show`, `crumb ready`, `crumb list`, `crumb blocked` — correct substitutions, no `bd` remains.
- L21: `crumb show` — correct.
- L55: `crumb show`, `crumb ready`, `crumb blocked`, `crumb list` — correct.
- L67: `.crumbs/sessions/_session-<id>` — correct path.
- L93-94: `crumb show`, `crumb ready`, `crumb blocked`, `crumb` — correct.
- L174: `.crumbs/tasks.jsonl` — correct (tasks.jsonl is the crumb data file, confirmed from skills/init.md and crumb CLI output).
- L417-425: Step 6 bash block includes `cp` + `git add` + `git commit` for exec-summary archiving; `bd sync` removed; `git pull --rebase` and `git push` retained. Step description prose updated to match new behavior.
- L439: `crumb close` — correct.
- L450: `crumb CLI` — correct.
- L306, L309: `crumb show <bead-id>`, `crumb update <bead-id> --note=` — correct; matches RULES-review.md L155-158.
- L404: `crumb list` — correct.
- L509: `.crumbs/sessions/_session-${SESSION_ID}` — correct.
- L540: `.crumbs/sessions/` — correct.
- L596: `.crumbs/sessions/_session-*/` — correct.

No workflow step ordering was changed. No hard gates were added or removed. No template lookup table entries were modified. No concurrency rules were altered. The exec-summary copy was added as two commits in Step 6 (CHANGELOG commit + exec-summary archive commit) which correctly separates documentation from artifact archiving.

**Assumptions audit**: No assumptions were made beyond what the task brief and the existing migrated reference (RULES-review.md, skills/init.md, crumb CLI help output) established. The `.crumbs/tasks.jsonl` filename was confirmed from `crumb doctor` and init skill context rather than assumed.

## 5. Build/Test Validation

```
grep -c '\bbd\b' orchestration/RULES.md
0
```
Result: 0 — acceptance criterion satisfied.

```
grep -n '\.beads/' orchestration/RULES.md
```
Result: no output — all `.beads/` paths migrated.

The file is a Markdown document with no executable components; no build or test suite applies.

## 6. Acceptance Criteria Checklist

- [x] **AC1: All bd command references replaced with crumb equivalents** — PASS. `grep -c '\bbd\b' orchestration/RULES.md` returns 0. Every `bd show`, `bd ready`, `bd list`, `bd blocked`, `bd update`, `bd close`, `bd sync` replaced with the appropriate `crumb` equivalent or removed (in the case of `bd sync`).

- [x] **AC2: Crash recovery paths updated from .beads/agent-summaries/ to .crumbs/sessions/ (L70, L301, L389)** — PASS. L67 (crash recovery example path) updated to `.crumbs/sessions/_session-<id>`. L509 (Session Directory definition) updated to `.crumbs/sessions/_session-${SESSION_ID}`. L540 (prefix note) updated to `.crumbs/sessions/`. L596 (stuck-agent diagnostic) updated to `.crumbs/sessions/_session-*/`.

- [x] **AC3: Landing-the-plane includes exec-summary copy step to .crumbs/history/** — PASS. Step 6 now includes `cp "${SESSION_DIR}/exec-summary.md" ".crumbs/history/exec-summary-${SESSION_ID}.md"` followed by `git add` and a separate `git commit` before `git pull --rebase && git push`.

- [x] **AC4: bd sync references removed from landing-the-plane workflow (L215)** — PASS. The `bd sync` line has been removed from the Step 6 bash block. The step description prose was also updated to no longer mention syncing.

- [x] **AC5: Session directory creation uses .crumbs/sessions/_session-{timestamp}/ pattern (L301)** — PASS. The Session Directory section now reads `SESSION_DIR=".crumbs/sessions/_session-${SESSION_ID}"`.

- [x] **AC6: grep -c '\bbd\b' orchestration/RULES.md returns 0 (excluding any _archive references)** — PASS. Confirmed: returns 0.

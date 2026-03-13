# Task Summary: ant-farm-gvd4

**Task**: Migrate dirt-pusher, nitpicker, scribe skeletons (mechanical)
**Status**: COMPLETE
**Commit**: b0dab79

## 1. Approaches Considered

**Approach A — Targeted line edits (lines flagged in task brief only)**
Edit only the exact lines called out in the task brief (L36, L44 in dirt-pusher; L39, L52 in nitpicker; L47, L53 in scribe). Fastest path, but risks missing additional occurrences on other lines and would fail acceptance criterion 4 (`grep -c '\bbd\b'` returns 0).

**Approach B — Global `replace_all` per distinct pattern**
Use `replace_all=true` in the Edit tool for each distinct pattern such as `bd show`, `bd update`, `bd close`, `bd create`, `beads`, `.beads/`. Fast, but requires carefully enumerating every pattern first; any missed pattern leaves a stale reference.

**Approach C — Rewrite each file from scratch**
Write the entire content of each file using the Write tool with all substitutions applied. Ensures completeness but introduces transcription risk: any inadvertent word change creates an unintended semantic modification, which violates the no-semantic-changes acceptance criterion.

**Approach D — Systematic per-occurrence Edit calls (selected)**
Grep each file to produce a complete inventory of every `bd`, `beads`, and `.beads/` occurrence, then issue one Edit call per unique string. Auditable, conservative, and easy to verify against the grep output. Eliminates transcription risk because only the targeted string changes.

## 2. Selected Approach with Rationale

Approach D was selected. The task is a pure string substitution with an explicit correctness gate (`grep -c '\bbd\b'` must return 0). Approach D provides the clearest audit trail: the grep inventory lists every occurrence to fix, the Edit calls address each one individually, and a final grep confirms zero remaining matches. Unlike Approach C, no line outside the targeted strings is touched, which satisfies the no-semantic-changes criterion.

## 3. Implementation Description

Pre-implementation grep across all three files produced a complete inventory of occurrences:

**dirt-pusher-skeleton.md (6 occurrences):**
- L11: `bead ID` in term definition
- L13: `.beads/agent-summaries/` in SESSION_DIR example
- L16: `bead type` in placeholder description
- L17: `bead ID` in TASK_ID placeholder description
- L36: `bd show` + `bd update` in Step 1 claim instruction
- L44: `bd close` in Step 6 close instruction

**nitpicker-skeleton.md (2 occurrences):**
- L39: `bd show <task-id>` in cross-review message example
- L52: `beads` + `bd create` in filing restriction note

**scribe-skeleton.md (5 occurrences):**
- L11: `.beads/agent-summaries/` in SESSION_DIR example
- L14: `bead IDs` in OPEN_BEAD_IDS term definition
- L21: `bead IDs` in OPEN_BEAD_IDS placeholder description
- L47: `Open beads` row label + `bd show <id>` in source table
- L53: `bd show` calls in fallback instruction
- L87: `{bead-id}` in Open Issues section example
- L100: `beads` in metrics counting rule

Each occurrence was replaced with its crumb equivalent using individual Edit calls. All `bd` commands became `crumb` commands; `bead`/`beads` became `crumb`/`crumbs`; `.beads/` became `.crumbs/`.

## 4. Correctness Review

**dirt-pusher-skeleton.md**
- L11: `crumb ID` — correct
- L13: `.crumbs/agent-summaries/_session-abc123` — correct
- L16: `crumb type` — correct
- L17: `crumb ID` — correct
- L36: `crumb show {TASK_ID}` + `crumb update {TASK_ID} --status=in_progress` — correct
- L44: `crumb close {TASK_ID}` — correct
- Semantic logic unchanged: 6-step workflow, all placeholders intact, all surrounding text untouched.

**nitpicker-skeleton.md**
- L39: `crumb show <task-id>` — correct
- L52: `crumbs` + `crumb create` — correct
- Semantic logic unchanged: review workflow, cross-review protocol, report format all intact.

**scribe-skeleton.md**
- L11: `.crumbs/agent-summaries/_session-abc123` — correct
- L14: `crumb IDs` — correct
- L21: `crumb IDs` — correct
- L47: `Open crumbs` + `crumb show <id>` — correct
- L53: `crumb show` calls — correct
- L87: `{crumb-id}` — correct
- L100: `crumbs` — correct
- Semantic logic unchanged: 4-step scribe workflow, all table structure, CHANGELOG format, and verification steps intact.

Final grep confirms: `grep -c '\bbd\b'` returns 0 for all three files.

## 5. Build/Test Validation

The three files are markdown templates with no executable components. Validation consisted of:
1. Pre-implementation grep to enumerate all occurrences — complete inventory confirmed.
2. Post-implementation `grep -c '\bbd\b'` on all three files — all returned 0.
3. Full re-read of each file after edits — no unintended changes found.

No build system or test runner applies to these template files.

## 6. Acceptance Criteria Checklist

- [x] **dirt-pusher-skeleton.md: all bd -> crumb command references updated** — PASS. Five distinct `bd` references replaced with crumb equivalents across L11, L13, L16, L17, L36, L44.
- [x] **nitpicker-skeleton.md: 3 bd references replaced with crumb equivalents (L39, L52, plus any others found)** — PASS. Two occurrences found and replaced (L39: `bd show`; L52: `beads`/`bd create`). No additional `bd` occurrences existed beyond those two lines.
- [x] **scribe-skeleton.md: bd show -> crumb show, 'beads' -> 'crumbs' terminology throughout** — PASS. All seven occurrences updated.
- [x] **grep -c '\bbd\b' on all three files returns 0** — PASS. Confirmed via post-implementation grep: dirt-pusher-skeleton.md:0, nitpicker-skeleton.md:0, scribe-skeleton.md:0.
- [x] **No semantic changes to skeleton prompt logic** — PASS. All workflow steps, placeholder structures, table formats, and instructional text preserved verbatim except for the targeted string substitutions.

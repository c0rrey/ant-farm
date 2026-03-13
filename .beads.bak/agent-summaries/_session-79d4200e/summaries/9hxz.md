# Task Summary: ant-farm-9hxz

**Task**: SETUP.md references wrong path for SESSION_PLAN_TEMPLATE.md
**Agent**: technical-writer
**Date**: 2026-02-22

---

## 1. Approaches Considered

**Approach A — Fix the `cp` command paths only (selected)**
Update both `cp orchestration/SESSION_PLAN_TEMPLATE.md .` lines to `cp orchestration/templates/SESSION_PLAN_TEMPLATE.md .`. The two "Project: SESSION_PLAN_TEMPLATE.md" label lines inside CLAUDE.md snippet blocks are user-facing names, not shell paths, and need no change.
Tradeoff: Surgical and minimal. Only corrects the lines that would fail if executed as shell commands.

**Approach B — Fix `cp` commands AND update label lines**
Also change the two `Project: SESSION_PLAN_TEMPLATE.md` label lines at L42 and L93 to include the full path.
Tradeoff: More exhaustive but alters CLAUDE.md snippets that users are intended to copy verbatim. The label is a conceptual pointer, not a shell path, so changing it introduces unnecessary noise in user-facing content.

**Approach C — Add a callout note at the top of SETUP.md**
Insert a note stating "SESSION_PLAN_TEMPLATE.md lives at `orchestration/templates/SESSION_PLAN_TEMPLATE.md`" without touching the existing lines.
Tradeoff: Additive rather than corrective. Leaves the wrong paths in place and burdens readers with reconciling conflicting information.

**Approach D — Move the template file to match existing references**
Relocate `orchestration/templates/SESSION_PLAN_TEMPLATE.md` to `orchestration/SESSION_PLAN_TEMPLATE.md` so SETUP.md references become correct without any edits.
Tradeoff: Changes the file system rather than documentation. Breaks the established `templates/` directory organization, violates scope (may require edits to files other than SETUP.md), and introduces higher risk of adjacent breakage.

---

## 2. Selected Approach

**Approach A** — Fix the two `cp` command lines in SETUP.md.

Rationale: The `cp` command lines are genuine path references that would fail at the shell if executed as written. They are the root cause cited in the task. The label lines are inside markdown code-block snippets meant to be pasted into a project's CLAUDE.md; they function as human-readable names, not filesystem paths. Changing only the failing shell paths satisfies the acceptance criteria with minimum scope.

---

## 3. Implementation Description

Edited `/Users/correy/projects/ant-farm/orchestration/SETUP.md` at two locations:

- **L61** (Quick Setup, Step 3): Changed
  `cp orchestration/SESSION_PLAN_TEMPLATE.md .`
  to
  `cp orchestration/templates/SESSION_PLAN_TEMPLATE.md .`

- **L121** (Full Setup, Step 1): Changed
  `cp orchestration/SESSION_PLAN_TEMPLATE.md .`
  to
  `cp orchestration/templates/SESSION_PLAN_TEMPLATE.md .`

No other files were modified.

---

## 4. Correctness Review

**File: `/Users/correy/projects/ant-farm/orchestration/SETUP.md`**

- L61: `cp orchestration/templates/SESSION_PLAN_TEMPLATE.md .` — correct. Matches actual file at `orchestration/templates/SESSION_PLAN_TEMPLATE.md` (confirmed by glob search).
- L121: `cp orchestration/templates/SESSION_PLAN_TEMPLATE.md .` — correct. Same file.
- L42: `Project: SESSION_PLAN_TEMPLATE.md` — intentional label inside CLAUDE.md snippet block. Not a shell path. Unchanged per design decision.
- L93: `Project: SESSION_PLAN_TEMPLATE.md` — same, intentional label. Unchanged.

Assumptions audit:
- Assumption: The label lines at L42 and L93 are user-facing CLAUDE.md snippet content, not shell paths. Verified: both appear inside fenced markdown code blocks showing CLAUDE.md content to be pasted by users. The surrounding prose confirms they are illustrative references, not commands.
- Assumption: No other files reference `orchestration/SESSION_PLAN_TEMPLATE.md` (the wrong path). Verified: grep search found only SETUP.md as the file with these references. The task scope boundary confirms only SETUP.md was to be edited.

---

## 5. Build/Test Validation

This task is a documentation-only change. There is no build or test suite applicable to markdown content. Manual verification performed:
- Glob confirmed actual file location: `orchestration/templates/SESSION_PLAN_TEMPLATE.md`.
- Full re-read of SETUP.md confirmed both `cp` commands now use the correct path.
- No broken markdown syntax introduced (verified by visual inspection of full file read).

---

## 6. Acceptance Criteria Checklist

| Criterion | Status |
|-----------|--------|
| SETUP.md references the correct path for SESSION_PLAN_TEMPLATE.md | PASS |

---

## Commit

```
fix: correct SESSION_PLAN_TEMPLATE.md path in SETUP.md cp commands (ant-farm-9hxz)
```

Changed file: `orchestration/SETUP.md`

Commit hash: (to be filled after `git commit` completes)

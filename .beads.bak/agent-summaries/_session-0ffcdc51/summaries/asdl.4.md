# Task Summary: ant-farm-asdl.4

**Task**: Update deprecated pantry.md Section 2 bead filing references
**Commit**: 4bb57ae
**Status**: Closed

---

## 1. Approaches Considered

**Approach A: Minimal inline reference only**
Replace both lines with a single pointer like "See big-head-skeleton.md step 10 for the canonical bd create --body-file pattern." Compact, but would fail AC #3 (no mention of 5 required fields) and AC #4 (no explicit dedup instruction). Rejected.

**Approach B: Exact plan text from ticklish-spinning-rose.md section 4 (SELECTED)**
Replace the two lines with the three specific bullets already drafted by the plan author: a reference to big-head-skeleton.md step 10, a list of the 5 required description fields, and the dedup pre-check command. Satisfies all four acceptance criteria precisely with minimal footprint. Selected.

**Approach C: Inline full bash code block**
Copy the entire cat/heredoc/bd create block from big-head-skeleton.md step 10 directly into pantry.md. Self-contained for readers but duplicates the canonical source, creates maintenance burden, and is overly verbose for a deprecated section. The task instruction says to reference, not duplicate. Rejected.

**Approach D: Deprecation-forward collapse**
Replace lines 318-319 with a single "DEPRECATED — see big-head-skeleton.md" note and remove all bullet content. Minimalist but explicitly violates AC #2, #3, and #4 by omitting the required references and instructions. Rejected.

---

## 2. Selected Approach with Rationale

**Approach B** — use the exact 3-bullet replacement from ticklish-spinning-rose.md section 4.

Rationale:
- The plan file is the authoritative spec written by the task author with all four acceptance criteria in mind.
- Three bullets replace two bullets: net +1 line is the minimum needed to satisfy all criteria.
- References big-head-skeleton.md by name and step number, pointing readers to the living canonical source rather than duplicating it.
- Names all 5 required fields on one line (root cause with file:line refs, affected surfaces, fix, changes needed, acceptance criteria).
- Includes the exact `bd list --status=open -n 0 --short` command for the dedup pre-check.
- Surrounding lines (deprecation notice, labels instruction, round 2+ note) are left completely untouched.

---

## 3. Implementation Description

**File changed**: `orchestration/templates/pantry.md`

**Lines before** (318-319):
```
- Command: `bd create --type=bug --priority=<combined-priority> --title="<root cause title>"`
- Then update with full description including all affected surfaces
```

**Lines after** (318-320, +1 line):
```
- Command: use `bd create --body-file` pattern (see big-head-skeleton.md step 10 for canonical example)
- Descriptions must include: root cause with file:line refs, affected surfaces, fix, changes needed, acceptance criteria
- Before filing: run `bd list --status=open -n 0 --short` to check for existing duplicates
```

No other files were modified. The deprecation notice and all surrounding content were left intact.

---

## 4. Correctness Review

### orchestration/templates/pantry.md (lines 313-322 post-change)

Re-read confirmed:
- Line 314: "File ONE bead per root cause" — unchanged
- Line 315: "Beads filed during session review are standalone" — unchanged
- Line 316: "Do NOT assign them to a specific epic" — unchanged
- Line 317: "They represent session-wide findings" — unchanged
- Line 318: now references `bd create --body-file` and big-head-skeleton.md step 10 — CORRECT
- Line 319: now lists all 5 required description fields by name — CORRECT
- Line 320: now includes `bd list --status=open -n 0 --short` dedup instruction — CORRECT
- Line 321: "Add labels: bd label add" — unchanged
- Line 322: "For round 2+: P3 findings may be auto-filed" — unchanged

No adjacent lines were inadvertently modified. The change is a clean 2-line replacement that expands to 3 lines.

**Assumptions audit**:
- Assumed "step 10" in the reference to big-head-skeleton.md is accurate: confirmed by reading big-head-skeleton.md, where the PASS bead-filing branch appears in step 10 of the Big Head workflow.
- Assumed the plan text in ticklish-spinning-rose.md section 4 is the authoritative replacement: confirmed by the task brief, which explicitly says "See plan at ~/.claude/plans/ticklish-spinning-rose.md section 4 for exact replacement text."
- No other files required review; scope was limited to pantry.md:L318-319.

---

## 5. Build/Test Validation

No code was changed (this is a markdown template file). No build or test suite applies.

Structural spot-check: verified that the surrounding Section 2 deprecation notice remains intact by reading lines 310-325 before and after the edit. The section header, deprecation label, and all other bullet points are unchanged.

Grep verification that bare `bd create --title` is gone from the changed section:

```
orchestration/templates/pantry.md:318: - Command: use `bd create --body-file` pattern (see big-head-skeleton.md step 10 for canonical example)
```

No bare `bd create --type=bug ... --title=` pattern remains on these lines.

---

## 6. Acceptance Criteria Checklist

- [x] **AC #1**: Lines 318-319 of pantry.md no longer contain a bare `bd create --title` command — PASS. The old command is replaced; only `bd create --body-file` is referenced.
- [x] **AC #2**: The replacement text references big-head-skeleton.md as the canonical source for the --body-file pattern — PASS. Line 318 says "(see big-head-skeleton.md step 10 for canonical example)".
- [x] **AC #3**: The replacement text mentions the 5 required description fields (Root Cause, Affected Surfaces, Fix, Changes Needed, Acceptance Criteria) — PASS. Line 319 lists all five: "root cause with file:line refs, affected surfaces, fix, changes needed, acceptance criteria".
- [x] **AC #4**: The replacement text includes the dedup instruction (bd list --status=open) — PASS. Line 320 says "run `bd list --status=open -n 0 --short` to check for existing duplicates".

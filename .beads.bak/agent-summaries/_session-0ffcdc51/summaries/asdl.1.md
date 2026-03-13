# Task Summary: ant-farm-asdl.1

**Task**: Add cross-session dedup step and description template to big-head-skeleton.md
**Status**: COMPLETE
**Commit**: 56c3795
**File changed**: `orchestration/templates/big-head-skeleton.md`

---

## 1. Approaches Considered

**Approach A — Inline prose instructions only**
Replace the bare `bd create` commands with prose descriptions of what Big Head should include (e.g., "write a description covering Root Cause, Affected Surfaces, Fix, Changes Needed, Acceptance Criteria"). Tradeoff: minimal file changes, but LLMs reliably follow concrete code block examples over prose. Prose-only instructions would reproduce the original problem where agents saw `bd create --type=bug ...` as the canonical pattern and ignored the surrounding text.

**Approach B — Inline code blocks, single shared temp file (`/tmp/bead-desc.md`)**
Add the full heredoc + `--body-file` pattern as a fenced code block in step 9 (PASS branch) and step 10 (P3 branch), both using `/tmp/bead-desc.md`. Both blocks include `rm -f /tmp/bead-desc.md` cleanup. Tradeoff: concise and directly mirrors the plan's canonical example. The single filename is safe because the two blocks are strictly sequential with cleanup after each.

**Approach C — Inline code blocks, distinct temp file names**
Same as B but use distinct names (`/tmp/bead-desc-p12.md` and `/tmp/bead-desc-p3.md`) to eliminate any theoretical collision if Big Head were ever run with concurrency. Tradeoff: slightly more verbose, marginal safety improvement for a non-concurrent single-agent flow. Adds cognitive overhead for readers comparing the two blocks.

**Approach D — External template file reference**
Add a new file `orchestration/templates/bead-description-template.md` and have Big Head read it at runtime. Tradeoff: clean separation of concerns, but adds a new file dependency, requires an extra file read at runtime, and undermines the design principle that `build-review-prompts.sh` injects the skeleton directly — everything Big Head needs should be in the single template it receives.

---

## 2. Selected Approach with Rationale

**Selected: Approach B** — Inline code blocks with a single shared temp file `/tmp/bead-desc.md`, following the plan at `~/.claude/plans/ticklish-spinning-rose.md` exactly.

Rationale:
- The plan is the canonical specification for this task. Deviating from it without a strong reason would introduce inconsistency between the plan and the implementation, making future audits harder.
- The single `/tmp/bead-desc.md` name is safe: both uses are sequential and each ends with `rm -f /tmp/bead-desc.md`, so there is no collision window.
- Inline code blocks give Big Head a concrete, copy-executable example, which is the highest-reliability instruction format for LLMs.
- All four changes (1a, 1b, 1c, 1d from the plan) are confined to `big-head-skeleton.md`, satisfying the scope boundary.

---

## 3. Implementation Description

Four changes were applied to `orchestration/templates/big-head-skeleton.md` in a single Edit operation:

**Change 1a — New cross-session dedup step (new step 7)**
Inserted between old step 6 ("document WHY findings share a root cause") and old step 7 ("write consolidated summary"). The new step instructs Big Head to run `bd list --status=open -n 0 --short`, then for each root cause group: exact-match titles → skip and log; similar titles → run `bd search "<key phrases>" --status open` to confirm; no match → mark for filing. Uncertainty bias is "err toward filing" to avoid missed filings.

**Change 1b — Replace bare `bd create` in PASS branch (now step 10)**
Replaced the single-line `bd create --type=bug --priority=<P> --title="<title>"` with a heredoc + `--body-file` code block. The template includes all 5 required sections: `## Root Cause`, `## Affected Surfaces`, `## Fix`, `## Changes Needed`, `## Acceptance Criteria`. Added explicit instruction that Root Cause "must be substantive analysis, NOT a restatement of the title." Added `bd label add` and `rm -f` cleanup. Added "(skip any marked as duplicates in step 7)" cross-reference.

**Change 1c — Replace bare `bd create` in P3 auto-filing (now step 11)**
Replaced the single-line P3 `bd create` with a shorter heredoc + `--body-file` block containing the minimum 3 sections: `## Root Cause`, `## Affected Surfaces`, `## Acceptance Criteria`. Added `rm -f` cleanup and "(skip any marked as duplicates in step 7)" cross-reference.

**Change 1d — Add "Cross-session dedup log" to output requirements**
Added a new bullet after "Deduplication log": "Cross-session dedup log: for each root cause, whether it was filed (new bead ID), skipped (matched existing bead ID), or merged with existing."

**Step renumbering**
Old step 7 → new step 8 (write consolidated summary)
Old step 8 → new step 9 (send report to Pest Control)
Old step 9 → new step 10 (await Pest Control verdict)
Old step 10 → new step 11 (P3 auto-filing)
All internal cross-references updated: "step 7" in PASS branch and P3 branch correctly reference the new dedup step (which is now step 7).

---

## 4. Correctness Review

### File: `orchestration/templates/big-head-skeleton.md`

**Re-read**: Full file re-read at line 1-180 after edits. Confirmed:

- Lines 1-65: Instruction block and template separator unchanged. No unintended modifications.
- Lines 66-100: Input guard, Step 0, Failure Artifact Convention unchanged.
- Lines 101-105: Steps 1-6 unchanged.
- Lines 106-114: New step 7 (cross-session dedup) — contains `bd list --status=open -n 0 --short` (L108) and `bd search "<key phrases>" --status open` (L112). Exact match / similar title / no match logic all present.
- Lines 115-150: Steps 8-10. Step 10 PASS branch contains full 5-section heredoc with `--body-file /tmp/bead-desc.md`. Label and cleanup present.
- Lines 151-172: Step 11 P3 auto-filing. 3-section heredoc with `--body-file /tmp/bead-desc.md`. Cleanup present.
- Lines 174-179: Output requirements. "Cross-session dedup log" bullet present at L177.

**Assumptions audit**:
- Assumed `bd search` accepts `--status open` flag. The plan uses this syntax so it is the intended pattern; if the flag differs in production, the plan itself would need correction.
- Assumed the plan's `/tmp/bead-desc.md` naming is intentional for both blocks. Sequential execution with cleanup makes this safe.
- Did not modify instruction block (lines 1-64) — only the agent-facing template below the `---` separator was changed, consistent with how `build-review-prompts.sh` extracts content.

**Adjacent issues noticed (not fixed, per scope)**:
- `orchestration/templates/reviews.md` still has bare `bd create` commands. This is tracked as ant-farm-asdl.2.
- `agents/big-head.md` line 22 still has the old step 6 description without dedup instruction. Tracked as ant-farm-asdl.3.
- `orchestration/templates/pantry.md` Section 2 has deprecated bead filing references. Tracked as ant-farm-asdl.4.

---

## 5. Build/Test Validation

No build system applies to Markdown template files. Manual validation performed:

```bash
# AC1: No bare bd create
grep -n 'bd create' orchestration/templates/big-head-skeleton.md
# Result: L145 and L166 — both include --body-file /tmp/bead-desc.md. PASS.

# AC2: All 5 template sections in PASS branch
grep -n '## Root Cause\|## Affected Surfaces\|## Fix\|## Changes Needed\|## Acceptance Criteria' big-head-skeleton.md
# Result: All 5 present at L123, L128, L132, L135, L139 (PASS branch). PASS.

# AC3: Dedup step contains bd list --status=open and bd search
grep -n 'bd list --status=open\|bd search' orchestration/templates/big-head-skeleton.md
# Result: L108 (bd list --status=open) and L112 (bd search). PASS.

# AC4: Output requirements include Cross-session dedup log
grep -n 'Cross-session dedup log' orchestration/templates/big-head-skeleton.md
# Result: L177. PASS.

# AC5: Sequential step numbering
grep -n '^[0-9]\+\.' orchestration/templates/big-head-skeleton.md
# Result: Steps 1-11, sequential, no gaps or duplicates. PASS.
```

---

## 6. Acceptance Criteria Checklist

| # | Criterion | Result |
|---|-----------|--------|
| 1 | No bare `bd create` command remains — every instance includes `--body-file` | PASS — L145 and L166 both include `--body-file /tmp/bead-desc.md` |
| 2 | Description template in PASS branch contains all 5 sections: `## Root Cause`, `## Affected Surfaces`, `## Fix`, `## Changes Needed`, `## Acceptance Criteria` | PASS — all 5 present at L123, L128, L132, L135, L139 |
| 3 | Cross-session dedup step exists before write-summary step, containing `bd list --status=open` and `bd search` | PASS — step 7 at L106-114; `bd list --status=open` at L108; `bd search` at L112 |
| 4 | Output requirements list includes "Cross-session dedup log" | PASS — L177 |
| 5 | Step numbers are sequential with no gaps or duplicates; all internal cross-references resolve correctly | PASS — steps 1-11 sequential; "step 7" cross-references at L120 and L153 correctly point to the dedup step |

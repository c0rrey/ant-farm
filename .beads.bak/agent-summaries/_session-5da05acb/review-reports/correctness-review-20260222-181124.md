# Correctness Review — Round 1

**Timestamp**: 20260222-181124
**Commit range**: aebd24d^..HEAD
**Commits reviewed**:
- `aebd24d` — fix: add preflight check for missing code-reviewer.md agent (ant-farm-sje5)
- `f95171e` — fix: update reader attributions from Pantry (review mode) to build-review-prompts.sh (ant-farm-2yww, ant-farm-80l0)
- `38ead0f` — fix: update SESSION_PLAN_TEMPLATE review sections to match parallel TeamCreate workflow (ant-farm-tour)

**Task IDs reviewed**: ant-farm-2yww, ant-farm-80l0, ant-farm-q84z, ant-farm-zg7t, ant-farm-tour, ant-farm-sje5

---

## Findings Catalog

### F1 — ant-farm-q84z: Acceptance criterion #1 not met — dual names persist after fix

**File**: `orchestration/PLACEHOLDER_CONVENTIONS.md:37,89,145`
**Severity**: P2
**Category**: Acceptance criteria compliance

**Description**: The ant-farm-q84z fix changed `RULES.md` line 146 to use `{TIMESTAMP}` as the prose placeholder name. However, `orchestration/PLACEHOLDER_CONVENTIONS.md` — the canonical source of truth for placeholder definitions — was not updated and continues to define `{REVIEW_TIMESTAMP}` as the Tier 1 canonical name (line 37) and `${TIMESTAMP}` as the shell variable that "holds the `{REVIEW_TIMESTAMP}` value" (line 89). The cross-reference table on line 145 still registers `RULES.md` as using `{REVIEW_TIMESTAMP}`, which is now factually wrong — RULES.md uses `{TIMESTAMP}`.

This leaves three names in play for the same concept:
- `{REVIEW_TIMESTAMP}` — still canonical per PLACEHOLDER_CONVENTIONS.md:37
- `{TIMESTAMP}` — used in RULES.md prose after the fix
- `${TIMESTAMP}` — shell variable (unchanged)

**Acceptance criterion violated**: "Only one name is used for the review timestamp concept (shell and prose use the same identifier)"

**Suggested fix**: Update `PLACEHOLDER_CONVENTIONS.md` to either (a) rename `{REVIEW_TIMESTAMP}` to `{TIMESTAMP}` throughout and update the cross-reference table row for RULES.md, or (b) revert RULES.md to use `{REVIEW_TIMESTAMP}` consistently. Either choice resolves the dual-name problem; the key is that PLACEHOLDER_CONVENTIONS.md and RULES.md must agree on the canonical name.

---

### F2 — ant-farm-2yww: README diagram still uses deprecated script name `fill-review-slots.sh`

**File**: `README.md:204`
**Severity**: P2
**Category**: Acceptance criteria compliance

**Description**: The ant-farm-2yww fix updated the `pantry-review` deprecation note (README:302) and the File Reference table (README:353) to correctly name `build-review-prompts.sh`. However, the ASCII diagram in the Step 3b workflow section (README:204) still reads:

```
Queen                       fill-review-slots.sh
```

`fill-review-slots.sh` is a defunct name that was superseded by `build-review-prompts.sh`. The commit `f95171e` updated one reference (`pantry-review` row) from `fill-review-slots.sh` to `build-review-prompts.sh`, but the diagram header was not touched.

The ant-farm-2yww description listed "No file in the repo attributes reviews.md readership to the Pantry" as the primary acceptance criterion, which is met. However, the bead also stated "Update all reader attributions to name `build-review-prompts.sh` as the replacement," and the diagram names a different, non-existent script.

**Suggested fix**: Change `README.md:204` from `fill-review-slots.sh` to `build-review-prompts.sh`.

---

## Findings That Passed (No Issues)

### ant-farm-sje5 — Preflight check for code-reviewer.md

`scripts/sync-to-claude.sh:64-67` — The warning is correctly emitted to stderr (`>&2`), names the exact file path (`~/.claude/agents/code-reviewer.md`), and explains the consequence ("Nitpicker team members will fail to spawn"). Both acceptance criteria are met.

### ant-farm-80l0 — README Hard Gates table SSV row

`README.md:260` — SSV row added with correct gate target ("Pantry spawn") and model ("haiku"). All 5 checkpoints (SSV, CCO, WWD, DMVDC, CCB) are now present in the table. Both acceptance criteria are met.

### ant-farm-zg7t — macOS-compatible shell commands

- `RULES.md:378` — `date +%s%N` replaced with `date +%s`. `date +%s` is macOS/BSD-compatible (returns seconds since epoch). Acceptance criterion met.
- `RULES.md:153` — `echo | grep` replaced with `[[ "${REVIEW_ROUND}" =~ ^[1-9][0-9]*$ ]]`. Bash-native regex. Criterion met.
- `RULES.md:169` — `tr | sed` pipeline replaced with `[[ -z "${TASK_IDS//[[:space:]]/}" ]]`. Matches the CHANGED_FILES pattern documented in the comment above. Criterion met.

Note: The acceptance criteria specified using `uuidgen` for session ID generation, but the actual fix used `date +%s` instead. Both are macOS-compatible. The criterion says "does not use `date +%s%N` or any GNU-only date format" — `date +%s` satisfies this. The criterion is met even though the implementation differed from the suggested fix.

### ant-farm-tour — SESSION_PLAN_TEMPLATE review sections

- `orchestration/templates/SESSION_PLAN_TEMPLATE.md:197` — Sequential review description replaced with "Review Wave (Parallel TeamCreate)" section. Criterion #1 met.
- `orchestration/templates/SESSION_PLAN_TEMPLATE.md:217-229` — Old raw-issue-count thresholds (<5/5-15/>15) replaced with root-cause-based triage that references RULES.md Step 3c and uses `<=5 root causes` threshold. No contradicting issue-count thresholds remain. Criteria #2 and #3 met.

### ant-farm-2yww — Reader attribution for reviews.md (partial)

Primary criteria met:
- `RULES.md:47` — Changed to "read by build-review-prompts.sh". Met.
- `RULES.md:440` — Changed to "read by build-review-prompts.sh". Met.
- `README.md:252` — Pantry attribution split; reviews.md now attributed to `build-review-prompts.sh`. Met.
- `README.md:353` — Changed to "`build-review-prompts.sh`". Met.
- `GLOSSARY.md:82` — Changed to "Reads implementation templates". Met.
- `CONTRIBUTING.md:95` — Pantry removed from "Read by" column for reviews.md. Met.

Criterion not fully met: see F2 above (README:204 diagram).

---

## Preliminary Groupings

### Group A: Incomplete fix scope (root cause: fix commits did not update all affected files)

- **F1** (P2): ant-farm-q84z fix updated RULES.md but not PLACEHOLDER_CONVENTIONS.md, leaving `{REVIEW_TIMESTAMP}` as the documented canonical name while RULES.md now uses `{TIMESTAMP}`. The cross-reference table in PLACEHOLDER_CONVENTIONS.md is also stale.
- **F2** (P2): ant-farm-2yww fix updated the pantry-review deprecation note and file reference table but missed the ASCII diagram at README:204 which still names the old `fill-review-slots.sh` script.

Both findings share the same root cause: the fix addressed the explicitly listed surfaces in the bead's "Changes Needed" section but missed additional occurrences of the same issue in adjacent files or sections.

---

## Summary Statistics

| Severity | Count |
|----------|-------|
| P1 | 0 |
| P2 | 2 |
| P3 | 0 |
| **Total** | **2** |

---

## Cross-Review Messages

**Sent to Drift reviewer**: "Stale cross-reference in `orchestration/PLACEHOLDER_CONVENTIONS.md:145` — table row for RULES.md says `{REVIEW_TIMESTAMP}` but RULES.md now uses `{TIMESTAMP}` after the ant-farm-q84z fix. Also `README.md:204` diagram still says `fill-review-slots.sh` instead of `build-review-prompts.sh`. Both are stale cross-file references — may want to review."

*(No messages received from other reviewers at time of writing.)*

---

## Coverage Log

| File | Status | Findings |
|------|--------|----------|
| `CONTRIBUTING.md` | Reviewed | No issues — ant-farm-2yww change (line 95) correctly removes Pantry from reviews.md reader attribution |
| `README.md` | Reviewed | F2 (P2) — diagram at line 204 still says `fill-review-slots.sh` |
| `orchestration/GLOSSARY.md` | Reviewed | No issues — Pantry description correctly updated to "Reads implementation templates" |
| `orchestration/RULES.md` | Reviewed | No issues — all three ant-farm-zg7t fixes verified; reviews.md attribution corrected; timestamp prose updated |
| `orchestration/templates/SESSION_PLAN_TEMPLATE.md` | Reviewed | No issues — sequential review replaced with parallel TeamCreate; decision thresholds replaced with RULES.md Step 3c reference |
| `scripts/sync-to-claude.sh` | Reviewed | No issues — preflight warning correct: stderr, correct path, correct consequence message |

**Out-of-scope file referenced for context** (not reviewed for findings):
- `orchestration/PLACEHOLDER_CONVENTIONS.md` — Not in the scoped file list, but consulted to evaluate F1. The stale cross-reference table and dual-name issue were discovered here. Reported to Drift reviewer rather than filed as a finding under this review (Drift owns stale cross-file references). The ant-farm-q84z acceptance criterion failure (F1) is filed as a Correctness finding because the in-scope fix in RULES.md left the acceptance criterion unmet — regardless of where the drift lives.

---

## Overall Assessment

**Score**: 7 / 10

**Verdict**: PASS WITH ISSUES

Both P2 findings represent acceptance criteria that were not fully met by the fix commits:

1. **F1** (ant-farm-q84z): The dual naming problem was partially solved — RULES.md now uses `{TIMESTAMP}` in prose, but the canonical source (`PLACEHOLDER_CONVENTIONS.md`) still registers `{REVIEW_TIMESTAMP}` as the official Tier 1 name, creating a new inconsistency rather than resolving the old one.

2. **F2** (ant-farm-2yww): The README ASCII diagram at line 204 still names the defunct `fill-review-slots.sh` script. The bead stated "Update all reader attributions to name `build-review-prompts.sh` as the replacement" and the diagram is a reader attribution context.

No P1 findings. Four of the six tasks (ant-farm-sje5, ant-farm-80l0, ant-farm-zg7t, ant-farm-tour) have their acceptance criteria fully satisfied. The two P2 gaps are both incomplete propagation of the fix to all affected surfaces — a pattern of partial completion rather than logic error.

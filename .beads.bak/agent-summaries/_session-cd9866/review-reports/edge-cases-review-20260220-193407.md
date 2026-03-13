# Report: Edge Cases Review (Round 2 — Fix Verification)

**Scope**: Fix commits 7ee2d0a..HEAD (5 commits)
**Files reviewed**: docs/installation-guide.md, orchestration/PLACEHOLDER_CONVENTIONS.md, orchestration/RULES.md, orchestration/templates/checkpoints.md, orchestration/templates/reviews.md, scripts/install-hooks.sh, scripts/scrub-pii.sh
**Reviewer**: Edge Cases — nitpicker (sonnet)
**Review round**: 2 (fix commits only)

---

## Findings Catalog

### Finding 1: Placeholder guard in reviews.md checks all 4 paths in round 2+, causing false-positive abort

- **File(s)**: `orchestration/templates/reviews.md:519-535`
- **Severity**: P2
- **Category**: edge-case
- **Description**: The placeholder substitution guard introduced by ant-farm-l3d5 iterates over all 4 review report paths (correctness, edge-cases, clarity, excellence) to detect unsubstituted template tokens. In round 2+, Pantry only substitutes the correctness and edge-cases paths; clarity and excellence paths are either (a) omitted from the for-loop by the Pantry, (b) left with `<session-dir>`/`<timestamp>` tokens, or (c) replaced with real paths. The Pantry responsibility note at line 572 says "the Pantry writes the concrete version of this polling loop" and "In round 2+, only the correctness and edge-cases checks are included (the `<IF ROUND 1>` block is omitted)." However, the `<IF ROUND 1>` markers (lines 553-556) are only placed inside the `while` loop body — NOT inside the guard's `for _path in` block (lines 520-524). If Pantry follows the note literally and only removes the `<IF ROUND 1>` section from the while loop body without also adapting the guard's path list, the guard's for-loop will encounter clarity/excellence paths still containing `<` or `>` tokens, trigger `PLACEHOLDER_ERROR=1`, and `exit 1` — falsely blocking Big Head from proceeding in every round 2+ session.
- **Suggested fix**: Add `<IF ROUND 1>` / `</IF ROUND 1>` markers around the clarity and excellence entries in the guard's for-loop (lines 523-524), so the same Pantry round-adaptation rule removes them consistently with the while loop:
  ```bash
  for _path in \
    "<session-dir>/review-reports/correctness-review-<timestamp>.md" \
    "<session-dir>/review-reports/edge-cases-review-<timestamp>.md" \
  # <IF ROUND 1>
    "<session-dir>/review-reports/clarity-review-<timestamp>.md" \
    "<session-dir>/review-reports/excellence-review-<timestamp>.md" \
  # </IF ROUND 1>
  ```
- **Cross-reference**: This is a correctness issue introduced by the ant-farm-l3d5 fix; messaging correctness reviewer.

---

## Preliminary Groupings

### Group A: Incomplete round-conditional annotation in placeholder guard

- Finding 1 — the guard code block and the while loop body use different conventions for round-specific paths. The `<IF ROUND 1>` markers were applied to the while loop but not the guard for-loop, creating an asymmetry that will cause false-positive failures in round 2+.
- **Shared root cause**: The ant-farm-l3d5 fix added the guard code without applying the same round-aware marker pattern used in the adjacent while loop.
- **Suggested combined fix**: Apply `<IF ROUND 1>` / `</IF ROUND 1>` markers to the clarity/excellence paths in the guard's for-loop.

---

## Summary Statistics

- Total findings: 1
- By severity: P1: 0, P2: 1, P3: 0
- Preliminary groups: 1

---

## Cross-Review Messages

### Sent

- To correctness: "Finding 1 in reviews.md:519-535 — placeholder guard may produce false-positive exit in round 2+ (incorrect logic introduced by ant-farm-l3d5 fix). This is a logic correctness issue worth verifying from your angle as well."

### Received

- None received at time of writing.

### Deferred Items

- None.

---

## Coverage Log

| File | Status | Evidence |
|------|--------|----------|
| `docs/installation-guide.md` | Reviewed — no issues | 407 lines; reviewed doc update at L47 describing new pre-commit hook behavior (ant-farm-4bna fix). Text accurately reflects the fix: "Blocks the commit with an error if `scrub-pii.sh` is not found or not executable (only when `issues.jsonl` is staged)." No edge cases in documentation content. |
| `orchestration/PLACEHOLDER_CONVENTIONS.md` | Reviewed — no issues | 236 lines; reviewed the two additions: `{REVIEW_TIMESTAMP}` entry at L36 and `${TIMESTAMP}` entry at L88 (ant-farm-88zh). Both are documentation-only entries. No executable code paths. Minor notation inconsistency (YYYYMMDD-HHmmss vs YYYYMMDD-HHMMSS) is a clarity issue, not an edge case. |
| `orchestration/RULES.md` | Reviewed — no issues | 424 lines; reviewed the Step 3b-i timestamp description expansion at L132-135 (ant-farm-88zh fix). Change is documentation/prose only — no executable paths introduced. No edge cases introduced. |
| `orchestration/templates/checkpoints.md` | Reviewed — no issues | 718 lines; reviewed: (1) CCO input guard expansion at L197-203 (ant-farm-l3d5 fix) — the guard now correctly catches literal `{REVIEW_ROUND}` text, blank, and non-numeric values; (2) WWD definition update at L264 (ant-farm-2gde fix) — inline definition is accurate and broader than the GLOSSARY.md entry it replaces. No edge cases. |
| `orchestration/templates/reviews.md` | Findings: #1 | 915 lines; reviewed the placeholder substitution guard added at L515-535 (ant-farm-l3d5 fix). Finding 1 describes the P2 edge case where the guard's for-loop checks all 4 paths without round-conditional markers, which will cause false-positive failures in round 2+. The polling loop body (L543-565) correctly uses `<IF ROUND 1>` markers but the guard at L520-524 does not. |
| `scripts/install-hooks.sh` | Reviewed — no issues | 99 lines; reviewed the fix moving the `scrub-pii.sh` existence check inside the staged-file guard (ant-farm-4bna). The pre-commit hook correctly uses `set -euo pipefail` so a non-zero exit from `scrub-pii.sh` (e.g., when remaining PII is found) will abort the commit via the `set -e` behavior. The fix ordering is correct: staged-file check → script existence check → script execution → re-stage. No edge cases introduced. |
| `scripts/scrub-pii.sh` | Reviewed — no issues | 61 lines; reviewed the regex scoping fix (ant-farm-yjrj). The `PII_FIELD_PATTERN` variable is used correctly in the `--check` path (L38). The post-scrub verification check at L54-55 hardcodes the same pattern inline rather than using `$PII_FIELD_PATTERN` — functionally identical (patterns match), and the check mode and scrub paths are consistent. The perl substitution regex correctly captures and preserves the surrounding field delimiters (`$1...$2`), so field values are replaced while keys and structural JSON are preserved. Tested: email addresses in `owner`/`created_by` are scrubbed; emails in other fields (titles, descriptions) are not touched. |

---

## Overall Assessment

**Score**: 8/10
**Verdict**: PASS WITH ISSUES

Five fixes landed correctly. Four of the five are clean with no new edge cases. One P2 issue exists in `orchestration/templates/reviews.md:519-535`: the placeholder guard introduced by ant-farm-l3d5 does not apply the `<IF ROUND 1>` marker convention to its path list, which will cause a false-positive exit in every round 2+ review session. The fix for this is low-risk (add two comment markers). No P1 issues were found.

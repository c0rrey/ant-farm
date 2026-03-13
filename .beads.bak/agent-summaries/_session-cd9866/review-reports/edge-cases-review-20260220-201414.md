# Report: Edge Cases Review

**Scope**: orchestration/templates/reviews.md (fix commits d4aa294..HEAD, ant-farm-12u9)
**Reviewer**: edge-cases | Nitpicker (Sonnet)
**Review round**: 3 (fix commits only)

---

## Findings Catalog

### Finding 1: Placeholder guard loop split is structurally correct but the `<IF ROUND 1>` comment is interpretive, not executable

- **File(s)**: `orchestration/templates/reviews.md:533-547`
- **Severity**: P3
- **Category**: edge-case
- **Description**: The fix splits the single 4-path placeholder guard loop into two loops: a base loop (correctness + edge-cases, always runs) and a `# <IF ROUND 1>` ... `# </IF ROUND 1>` guarded block (clarity + excellence). The markers are bash comments inside a fenced code block — they are read as prose by Big Head, who is instructed to interpret them when composing the actual polling script. This means the correctness of the round-scoping depends entirely on Big Head (an LLM) correctly omitting the `<IF ROUND 1>` block when composing the concrete script for round 2+.

  This is the pre-existing design (the `# <IF ROUND 1>` pattern also appears in the polling loop body at lines 566-569 with the same interpretive-only guarantee). The fix correctly mirrors the same pattern that already exists in the polling loop body, so the fix is structurally consistent with the surrounding template. However: if Big Head were to fail to strip the `<IF ROUND 1>` block in a round 2+ brief, the placeholder guard would falsely flag clarity and excellence paths as unsubstituted (since the Pantry did not fill them), causing Big Head to halt with PLACEHOLDER ERROR instead of proceeding.

  This is not introduced by the fix — the polling loop body at lines 566-569 has the same risk. The fix merely adds the same guard to the placeholder check section, maintaining parity. The boundary condition (round 2+ Big Head failing to strip the block) would cause a false PLACEHOLDER_ERROR halt rather than silent wrong behavior (data loss / incorrect results) — it fails loudly. Not a new P1/P2 risk.

- **Suggested fix**: No change needed for this round. If the `<IF ROUND 1>` pattern is ever strengthened to be executable (e.g., processed by a script rather than an LLM), the placeholder guard would benefit from the same upgrade. Track as future work.
- **Cross-reference**: No cross-domain issue.

---

## Preliminary Groupings

### Group A: Interpretive-only conditional blocks

- Finding 1 — standalone; describes the pre-existing `<IF ROUND 1>` interpretation pattern that the fix correctly mirrors. Not a regression introduced by this fix.

---

## Summary Statistics

- Total findings: 1
- By severity: P1: 0, P2: 0, P3: 1
- Preliminary groups: 1

---

## Cross-Review Messages

### Sent

None.

### Received

None.

### Deferred Items

None.

---

## Coverage Log

| File | Status | Evidence |
|------|--------|----------|
| `orchestration/templates/reviews.md` | Reviewed — 1 P3 finding | Full file read (924 lines); diff of d4aa294..HEAD examined; pre-fix version inspected via `git show`; `fill-review-slots.sh`, `compose-review-skeletons.sh`, `big-head-skeleton.md`, `nitpicker-skeleton.md`, and `pantry.md` read for system context |

---

## Overall Assessment

**Score**: 9.5/10
**Verdict**: PASS

The fix (commit f514707, ant-farm-12u9) correctly adds `<IF ROUND 1>` / `</IF ROUND 1>` markers around the clarity and excellence paths in the placeholder substitution guard, mirroring the identical pattern already used in the polling loop body (lines 566-569). The structural split into a base loop (round-agnostic) and a guarded block (round 1 only) is sound and consistent with the surrounding template design. No new edge-case risks are introduced: failure mode on the one identified edge case (Big Head failing to strip the block in round 2+) is a loud halt rather than silent wrong behavior, which is the safer failure mode. No P1 or P2 findings.

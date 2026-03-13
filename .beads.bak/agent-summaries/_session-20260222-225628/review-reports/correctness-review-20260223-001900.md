# Report: Correctness Review (Round 2)

**Scope**: Fix commits only — 9fcfc87..HEAD (commits: 4021909, a58c56f, 0463fa5, 06cf404, 365a0d9)
**Reviewer**: Correctness / nitpicker (sonnet)
**Review round**: 2 — scope limited to fix commits; out-of-scope findings only if they cause runtime failure or silently wrong results.

---

## Findings Catalog

### Finding 1: ant-farm-01a8 fix reintroduces the original problem at the acceptance-criterion level

- **File(s)**: `orchestration/templates/reviews.md:584`
- **Severity**: P2
- **Category**: correctness
- **Description**: Acceptance criterion 1 for ant-farm-01a8 states: "All four report paths are checked for unresolved placeholders unconditionally." Criterion 2 states: "A corrupt REVIEW_ROUND value still triggers an error but does not skip validation of other paths."

  The fix in commit 06cf404 made all four paths unconditional — that satisfied all three criteria. The follow-up commit 365a0d9 reverted to a conditional check (`if [ "$REVIEW_ROUND" -eq 1 ]; then`) for the clarity/drift paths. The commit message justifies the revert on a correctness ground (round-2+ briefs have unsubstituted angle-bracket placeholders for clarity/drift paths, so an unconditional check would always trigger a false PLACEHOLDER_ERROR in round 2+). That justification is technically correct.

  However, this revert means criterion 1 and 2 of ant-farm-01a8 are now **not met**: clarity/drift paths are not checked unconditionally, and a corrupt REVIEW_ROUND that somehow bypasses the `case` guard (e.g., from a different code path) would still skip validation of those paths.

  The comment in reviews.md:559-560 asserts "REVIEW_ROUND is guaranteed to be a valid integer here" because the `case` statement above catches corruption. This guarantee is correct given the current code flow. But the bead's acceptance criteria were written expecting unconditional validation — the fix intentionally deviates from them.

  **Impact**: The actual runtime behavior after 365a0d9 is correct (no false PLACEHOLDER_ERROR in round 2+). The issue is that the filed acceptance criteria are now formally unmet, which means CCB would fail Check 2 (Bead Existence Check) if it spot-checks the criteria text against the code.

- **Suggested fix**: Either (a) update the bead ant-farm-01a8 acceptance criteria to reflect the conditional check approach and the REVIEW_ROUND pre-validation invariant, or (b) leave as-is and document in the bead notes that criteria 1 and 2 are intentionally superseded by the follow-up commit rationale. This is a documentation/tracking issue, not a runtime issue.

---

### Finding 2: ant-farm-evk2 — RULES.md:L19 prohibition contradicts Step 3c termination check text

- **File(s)**: `orchestration/RULES.md:19`, `orchestration/RULES.md:300`
- **Severity**: P3
- **Category**: correctness
- **Description**: The Queen Prohibitions section (L19) says: "The **only** authorized shutdown trigger is the termination check in Step 3c (zero P1/P2 findings)." But RULES.md:300 (introduced in 0463fa5) says: "Shutdown is authorized at this point — but do NOT send `shutdown_request` yet. Proceed to Step 4 first; send `shutdown_request` to team members during session teardown (Step 6 cleanup)."

  The prohibition says shutdown happens at Step 3c termination check. The Step 3c text clarifies it should not be sent until Step 6. These are consistent in intent (don't send it prematurely) but the prohibition section's wording "the termination check in Step 3c" is the trigger event, while actual dispatch happens at Step 6. A Queen reading only L19 might send shutdown_request immediately upon termination check, contradicting L300's "do NOT send shutdown_request yet."

  This is a P3 clarity edge — not a runtime failure. The Step 3c text at L300 provides the correct instruction. The prohibition at L19 defines the gate (when authorization is granted), not when to actually send the message. A careful reader would synthesize both correctly, but the wording is slightly tension-inducing.

- **Suggested fix**: Revise L19 to read: "The **only** authorized shutdown trigger is convergence (zero P1/P2) at Step 3c; actual `shutdown_request` dispatch happens during session teardown at Step 6 cleanup." This aligns the prohibition wording with L300.

---

## Preliminary Groupings

### Group A: Acceptance criteria drift on ant-farm-01a8
- Finding 1 — standalone. The fix commit sequence (06cf404 → 365a0d9) resolved a real correctness issue (false PLACEHOLDER_ERROR in round 2+) but the revert technically violates the bead's acceptance criteria as written.

### Group B: Wording tension in evk2 shutdown prohibition
- Finding 2 — standalone. The two shutdown-related texts in RULES.md are consistent in intent but create slight reader ambiguity about when to send vs. when authorization is granted.

---

## Summary Statistics
- Total findings: 2
- By severity: P1: 0, P2: 1, P3: 1
- Preliminary groups: 2

---

## Acceptance Criteria Verification

### ant-farm-ql6s — PASS
- Criterion: `reviews.md:985` uses `team_name: "nitpicker-team"` ✓ (verified at reviews.md:1005)
- Criterion: No remaining occurrences of `"nitpickers"` as a team name value ✓ (grep confirms single occurrence at L1005, value = "nitpicker-team")
- Criterion: Fix agent spawn instructions reference the correct canonical team name ✓

### ant-farm-1pa0 — PASS
- Single-invocation constraint documented in big-head-skeleton.md:91 ✓
- Timeout increased from 30s to 60s with rationale in both big-head-skeleton.md:92 and reviews.md:540-542 ✓
- Error message text updated from "30 seconds" to "60 seconds" in both files ✓

### ant-farm-f7lg — PASS
- No references to `{session-dir}/briefs/` in reviews.md round-transition section ✓ (grep returns no matches)
- Edge Cases reviewer has explicit distinct output path `{session-dir}/review-reports/edge-cases-r<N+1>-<timestamp>.md` in reviews.md:1118 ✓
- RULES.md:403 provides `{SESSION_DIR}/review-reports/edge-cases-r<N+1>-<timestamp>.md` ✓
- RULES.md and reviews.md round-transition fields are consistent ✓

### ant-farm-5zs0 — PASS
- reviews.md:82 no longer instructs creating a new team for Round 2+ ✓ (now says "persistent — do NOT create a new team")
- reviews.md:934 (now mapped to the checklist line) no longer instructs creating a new team ✓ (updated to say "persistent team re-tasked via SendMessage")
- Both locations reference the persistent-team model and SendMessage re-tasking ✓

### ant-farm-fp74 — PASS
- `bd list` failure in big-head-skeleton.md writes failure artifact before exit 1 ✓ (L117-123)
- `bd list` failure sends SendMessage to Queen before exit 1 ✓ (L125)
- Both big-head-skeleton.md and reviews.md blocks updated consistently ✓ (reviews.md:707-718 mirrors the skeleton)

### ant-farm-01a8 — PARTIAL (see Finding 1)
- Criterion 3 (polling loop gated on REVIEW_ROUND for round-appropriate behavior) ✓
- Criteria 1 and 2 (unconditional 4-path check; corrupt REVIEW_ROUND does not skip path validation) — NOT MET as written, though the implementation is runtime-correct due to the pre-validation invariant. The revert in 365a0d9 restores conditional clarity/drift validation.

### ant-farm-1rof — PASS
- Missing session directory produces "Session directory not found" error before script runs ✓ (RULES.md:71-74)
- Existing exit-code handling for parse-progress-log.sh remains unchanged ✓ (step numbering adjusted but logic preserved)
- Error message includes the specific path that was not found ✓ (RULES.md:71 uses `<prior_SESSION_DIR>` variable)

### ant-farm-ccg8 — PASS
- ESV Check 2 handles the case where SESSION_START_COMMIT has no parent ✓ (checkpoints.md:791-795)
- Fallback command covers the correct commit range ✓ (`git log {SESSION_START_COMMIT}..{SESSION_END_COMMIT}` without `^`)
- Guard documented in the check instructions ✓ (prose description added)

### ant-farm-evk2 — PASS (with Finding 2 as P3 polish)
- Explicit "DO NOT send shutdown_request" prohibition added to Queen Prohibitions ✓ (RULES.md:19)
- Termination check (zero P1/P2) is the only authorized trigger ✓ (L19)
- "DO NOT send shutdown_request" added at Step 3c P1/P2 branch ✓ (RULES.md:302)
- Contradictory "Proceed directly to Step 4" line resolved by 0463fa5 ✓ (RULES.md:300)

---

## Cross-Review Messages

### Sent
- None

### Received
- None

### Deferred Items
- None

---

## Coverage Log

| File | Status | Evidence |
|------|--------|----------|
| `orchestration/RULES.md` | Findings: #2 | ~710 lines; reviewed crash recovery block (L65-82), Queen Prohibitions (L14-20), Step 3c shutdown instructions (L293-320), round-transition edge-cases path (L398-410) |
| `orchestration/templates/big-head-skeleton.md` | Reviewed — no P1/P2 issues in fix scope | ~232 lines; verified single-invocation constraint (L91-92), 60s timeout (L92), bd list failure artifact (L114-127) |
| `orchestration/templates/checkpoints.md` | Reviewed — no P1/P2 issues in fix scope | ~920 lines; verified ESV Check 2 root-commit guard (L788-800) |
| `orchestration/templates/reviews.md` | Findings: #1 | ~1156 lines; verified team_name fix (L1005), Round 2+ persistent-team text (L82), checklist (L934), edge-cases output path (L1118), bd list failure block (L707-718), placeholder guard structure (L555-608), timeout constants (L540-542) |

---

## Overall Assessment

**Score**: 8/10
**Verdict**: PASS WITH ISSUES

All P1 findings from round 1 are resolved and landed correctly. The fix for ant-farm-ql6s (wrong team name), ant-farm-f7lg (phantom briefs/ path + missing edge-cases output path), ant-farm-5zs0 (round 2+ persistent-team model), ant-farm-fp74 (bd list failure artifact), ant-farm-1rof (crash recovery dir check), ant-farm-ccg8 (ESV root-commit guard), and ant-farm-evk2 (shutdown prohibition) all verify clean against their acceptance criteria.

The one P2 finding (Finding 1) is a bead-tracking issue: the 365a0d9 follow-up commit was technically correct (preventing false PLACEHOLDER_ERROR in round 2+) but the revert formally unmet two of ant-farm-01a8's acceptance criteria as written. No runtime failure results. The finding warrants a bead update to bring the acceptance criteria text into alignment with the implemented solution.

The P3 finding (Finding 2) is a wording tension in RULES.md:19 vs. L300 around when shutdown authorization is granted vs. when shutdown_request should actually be dispatched. Both texts agree on the correct behavior; the prohibition wording is slightly imprecise.

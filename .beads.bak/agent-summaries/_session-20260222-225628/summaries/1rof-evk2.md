# Fix Summary: ant-farm-1rof + ant-farm-evk2

**Agent**: fix-dp-2
**File changed**: `orchestration/RULES.md`
**Commit**: a58c56f (initial), follow-up for L300-L301 contradiction fix

---

## ant-farm-1rof — Crash recovery missing session directory existence check

### Approaches considered

1. **Add bash existence check as a new numbered step (chosen)**: Insert `[ -d "<prior_SESSION_DIR>" ] || echo "Session directory not found: <prior_SESSION_DIR>"` as step 1 before calling `parse-progress-log.sh`. Clear, explicit, and renumbers the exit-code steps so the flow reads sequentially. Surfaces the specific missing path in the error message.

2. **Guard inside parse-progress-log.sh**: Add the existence check inside the script itself. Rejected — the script is a bash artifact, not a RULES.md change; the bead explicitly targets RULES.md:L64-75. A script change would also require a separate commit outside scope.

3. **Inline conditional wrapping the script call**: Use `[ -d ... ] && bash scripts/parse-progress-log.sh ...` on one line. Rejected — harder to read in the prose-style RULES.md format; does not surface a clear human-readable error message.

4. **Use set -e and a helper function**: Wrap the crash recovery block in error-trapping shell constructs. Rejected — RULES.md describes behavior for the Queen agent (a language model), not a shell script; shell error-trapping conventions don't map onto Queen context.

### Per-file correctness notes (RULES.md)

- L68-74: Existence check is unambiguous — bash one-liner with `|| echo` produces the exact "Session directory not found: `<path>`" message required by acceptance criteria.
- L75: `parse-progress-log.sh` call unchanged — existing exit-code handling preserved as required.
- L80-81: Exit 1 wording updated to note the path should be included — satisfies acceptance criterion 3.
- Renumbering from 4 steps to 5 is consistent; no steps were omitted or duplicated.

---

## ant-farm-evk2 — Explicit team-shutdown prohibition in RULES.md

### Approaches considered

1. **Add prohibition to Queen Prohibitions + Step 3c decision fork (chosen)**: Add a NEVER bullet to the authoritative prohibitions list (processed first by the Queen), and add explicit callouts at both branches of the Step 3c fork. Covers both the "where not to" (prohibitions) and "where to" (Step 3c fork) contexts.

2. **Queen Prohibitions only**: Add only to the prohibitions list, rely on the absence of shutdown authorization elsewhere. Rejected — the original bug occurred because the authorization point was ambiguous; absence-of-instruction is insufficient for a persistent-team model.

3. **Step 3c only, no prohibitions change**: Add callouts only at the decision fork. Rejected — the prohibitions section is read first and is the canonical rule source; omitting it there leaves the prohibition under-specified.

4. **Add to Anti-Patterns section**: Document "sending shutdown_request before Step 4" as an anti-pattern. Rejected — anti-patterns are lower-visibility than prohibitions; the bead explicitly requires the prohibition at Queen Prohibitions and Step 3c.

5. **Termination check: single unambiguous bullet (follow-up fix)**: The initial implementation produced two contradictory bullets (L300-L301). Collapsed to one bullet: "Shutdown is authorized at this point — but do NOT send shutdown_request yet. Proceed to Step 4 first; send shutdown_request to team members during session teardown." This resolves the contradiction flagged by DMVDC.

### Per-file correctness notes (RULES.md)

- L19 (Queen Prohibitions): NEVER bullet is consistent in style and specificity with adjacent prohibitions. Correctly states Step 3c termination check as the only authorized trigger.
- L300 (Step 3c termination check): Single bullet now unambiguously defers shutdown to Step 6 teardown while confirming authorization exists at this point.
- L302-303 (P1/P2 found branch): Standalone bold line prohibits shutdown_request when findings remain — keeps the team active for fix workflow.
- No unintended changes to surrounding workflow logic.

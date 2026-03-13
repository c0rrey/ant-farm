# Fix Summary: ant-farm-ql6s, ant-farm-1pa0, ant-farm-f7lg, ant-farm-5zs0, ant-farm-fp74, ant-farm-01a8

**Session**: _session-20260222-225628
**Commits**: 06cf404 (reviews.md, big-head-skeleton.md); 0463fa5 (RULES.md edge-cases path)
**Files changed**: orchestration/templates/reviews.md, orchestration/templates/big-head-skeleton.md, orchestration/RULES.md

---

## ant-farm-ql6s (P1): Wrong team name 'nitpickers' in Fix Workflow

**Root cause**: `reviews.md:985` used `team_name: "nitpickers"` instead of the canonical `"nitpicker-team"` established in `big-head-skeleton.md:30`.

**Approach considered**: Simple string replace. No alternatives needed — this was a single incorrect literal value with a single correct canonical value. Verified no other occurrences of `"nitpickers"` as a team name value remained.

**Fix**: Changed `team_name: "nitpickers"` → `team_name: "nitpicker-team"` at `reviews.md:985`.

**Correctness note**: Grep confirmed zero remaining occurrences of `"nitpickers"` as a team name in any orchestration file.

---

## ant-farm-1pa0 (P1): Polling loop single-invocation constraint under-documented, timeout too short

**Root cause**: The bash polling block in both `big-head-skeleton.md` (workflow instructions) and `reviews.md` (the embedded brief script) gave no warning that the entire `while` loop must run in a single Bash tool invocation. Shell state doesn't persist across turns, so multi-turn polling silently breaks. Additionally, 30 seconds was too short for slow reviewers under typical load.

**Approaches considered**:
1. Add prose warning only in big-head-skeleton.md instructions — rejected; the brief template (reviews.md) is what Big Head actually reads at runtime, so the warning belongs there too.
2. Add warning in both files + increase timeout — chosen.
3. Rearchitect polling to use a file-polling approach without `sleep` — out of scope; the existing shell approach is correct if executed in a single invocation.

**Fix**:
- Added "Single-invocation constraint" comment block in the brief script (reviews.md) explaining that the entire block must be one Bash tool call.
- Added corresponding prose note in big-head-skeleton.md workflow step 1.
- Increased `POLL_TIMEOUT_SECS` from 30 to 60 (30 iterations × 2s) with rationale comments in both files.
- Updated timeout references in failure artifact and error return format (30s → 60s).

**Correctness note (reviews.md)**: The comment block is positioned before the timing constants, so Big Head reads the constraint before the loop code. The timeout increase is backward-compatible — any correctly-functioning reviewer will still finish in under 60s.

**Correctness note (big-head-skeleton.md)**: Prose note added in the "On timeout" bullet, pointing out the single-invocation constraint before describing what to do on timeout.

---

## ant-farm-f7lg (P2): Phantom briefs/ path and missing edge-cases output path in round-transition spec

**Root cause**: `reviews.md:1091` referenced `{session-dir}/briefs/review-brief-<timestamp>.md` which does not exist in the canonical session layout. `reviews.md:1094` and `RULES.md:393` said "same fields as above" for the Edge Cases reviewer without specifying a distinct output path.

**Approaches considered**:
1. Replace `briefs/` path with a valid path — the field itself was vestigial (briefs are not re-sent during round transitions; the reviewer is simply re-scoped). Removed it entirely.
2. Expand "same fields as above" inline — chosen; explicitly listing all fields for each reviewer avoids ambiguity about which fields differ.

**Fix**:
- Removed the `Brief path:` field from the Correctness reviewer re-task block at `reviews.md:1091`.
- Expanded the Edge Cases re-task block at `reviews.md:1094` to list all fields explicitly, including distinct output path `{session-dir}/review-reports/edge-cases-r<N+1>-<timestamp>.md`.
- Updated `RULES.md:393` to expand "same fields" → explicit output path `{SESSION_DIR}/review-reports/edge-cases-r<N+1>-<timestamp>.md`.

**Correctness note (reviews.md)**: The round-transition block is now consistent: each reviewer has its own explicit output path. No `briefs/` reference remains.

**Correctness note (RULES.md)**: The RULES.md change was committed in an adjacent commit (0463fa5) by another agent due to git stash timing, but the content is identical to what was authored here.

---

## ant-farm-5zs0 (P2): Round 2+ spawn instructions contradict persistent-team model

**Root cause**: `reviews.md:82` and `reviews.md:934` still described creating a new Nitpicker team for round 2+, contradicting `RULES.md:226` which mandates re-tasking existing team members via SendMessage.

**Approaches considered**:
1. Delete the Round 2+ block at line 82 entirely — rejected; the block provides useful reference for what fields to include in re-task messages.
2. Rewrite as re-task instructions using the same fenced-block format — chosen.
3. Simply add a "do NOT create a new team" warning before the old block — insufficient; the old TeamCreate description would still be misleading.

**Fix**:
- Rewrote `reviews.md:82` block: replaced "the Queen creates the Nitpicker team with 4 members" with a clear statement that the team is persistent and reviewers are re-tasked via SendMessage. Retained field list for the re-task messages.
- Updated `reviews.md:934` checklist item: replaced "Round 2+: 4 members (2 Nitpickers + Big Head + Pest Control)" with explicit note that Round 2+ uses persistent team via SendMessage re-tasking.

**Correctness note**: Neither location now suggests TeamCreate for round 2+. The description matches RULES.md:226.

---

## ant-farm-fp74 (P2): Silent failure on bd list infrastructure error in cross-session dedup

**Root cause**: When `bd list --status=open` fails, both `big-head-skeleton.md` and `reviews.md` called `exit 1` without writing a failure artifact or notifying the Queen. Big Head went idle silently, triggering stuck-agent diagnostic with a long delay.

**Approaches considered**:
1. Retry `bd list` before aborting — rejected; the cross-session dedup protocol says "retry and wait" for lock contention, but the code path here is a definitive infrastructure failure (exit code non-zero), not a lock timeout.
2. Write failure artifact + SendMessage before exit — chosen; matches the established Failure Artifact Convention at big-head-skeleton.md:L77-L86.
3. Downgrade to a warning (continue without dedup) — rejected; the dedup step exists to prevent duplicate bead filing; skipping it silently on error defeats the purpose.

**Fix**:
- In both `big-head-skeleton.md` and `reviews.md`: added `cat > "{CONSOLIDATED_OUTPUT_PATH}"` failure artifact write using the standard format, followed by a `SendMessage(Queen)` call with structured error details, before the existing `exit 1`.

**Correctness note (big-head-skeleton.md)**: The failure artifact uses the same format defined in the Failure Artifact Convention section. `{CONSOLIDATED_OUTPUT_PATH}` is the shell variable (substituted at runtime), not a template placeholder.

**Correctness note (reviews.md)**: The duplicate block (Step 2.5) is updated consistently with big-head-skeleton.md.

---

## ant-farm-01a8 (P2): Placeholder guard incomplete for round-1 paths when REVIEW_ROUND is corrupt

**Root cause**: The placeholder guard in `reviews.md` placed clarity/drift path validation inside `if [ "$REVIEW_ROUND" -eq 1 ]`. A corrupt REVIEW_ROUND triggers the `case` statement exit before reaching path validation.

**First fix attempt (commit 06cf404)**: Moved all 4 paths into an unconditional loop. This was correct for the original bead but introduced a new failure mode: in round 2+, Pantry only substitutes correctness/edge-cases paths (clarity/drift are not in `ACTIVE_REVIEW_TYPES`). Unconditionally checking clarity/drift paths in round 2+ would always find unresolved angle-bracket placeholders and abort Big Head erroneously.

**Revised fix (this commit)**: Restored the conditional structure for clarity/drift, but added a comment explaining WHY: REVIEW_ROUND corruption is already caught and aborted by the `case "$REVIEW_ROUND"` block earlier in the script (line ~521), before path validation is reached. The guard comment now documents this invariant explicitly. Correctness/edge-cases paths are checked unconditionally; clarity/drift paths are checked only in round 1 (where Pantry actually substitutes them).

**Approaches considered**:
1. Check all 4 unconditionally — breaks round 2+ (false PLACEHOLDER_ERROR).
2. Keep original conditional structure, add comment explaining REVIEW_ROUND is pre-validated — chosen.
3. Use a separate REVIEW_ROUND integrity check before the path loop and then check all 4 — functionally equivalent to approach 2 but more verbose.

**Correctness note**: The `case "$REVIEW_ROUND" in *'{'*|*'}'*` block at line ~521 runs before the path validation loop and exits on unresolved `{{REVIEW_ROUND}}`. By the time path validation runs, REVIEW_ROUND is guaranteed to be a valid integer. The comment in the guard now documents this invariant.

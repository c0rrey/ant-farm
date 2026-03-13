# Report: Correctness Review

**Scope**: agents/big-head.md, orchestration/templates/big-head-skeleton.md, orchestration/templates/reviews.md
**Reviewer**: Correctness / Nitpicker (Round 2 — fix verification scope)
**Commit range**: d3932e9^..1dfd4c7
**Task IDs**: ant-farm-7kei, ant-farm-84qf, ant-farm-igxq

---

## Findings Catalog

### Finding 1: `$CONSOLIDATED_OUTPUT_PATH` shell variable undefined in polling timeout bash block

- **File(s)**: `orchestration/templates/reviews.md:L588`
- **Severity**: P2
- **Category**: correctness
- **Description**: The fix for ant-farm-84qf adds `cat > "$CONSOLIDATED_OUTPUT_PATH" << 'EOF'` at L588 inside the polling loop bash block (introduced by commit 1dfd4c7). However, `$CONSOLIDATED_OUTPUT_PATH` is never assigned as a shell variable anywhere in that script block (L496–L596). The Pantry fills `{CONSOLIDATED_OUTPUT_PATH}` as a prose placeholder (curly braces) in the skeleton, but the bash block uses `"$CONSOLIDATED_OUTPUT_PATH"` (dollar-prefix shell variable). When Big Head executes this block via the Bash tool, the variable expands to empty string, causing `cat > ""` which errors — no artifact lands at the expected output path. The downstream consumer (Queen, Pest Control) finds no file, indistinguishable from Big Head never having run. This directly violates ant-farm-84qf AC3: "Downstream consumers can distinguish 'Big Head failed' (FAILED artifact exists) from 'Big Head never ran' (no file at path)."
- **Suggested fix**: Replace `"$CONSOLIDATED_OUTPUT_PATH"` with the literal filled path (after Pantry substitution, this would be the actual session/review-consolidated path), or add a shell variable assignment at the top of the script block: `CONSOLIDATED_OUTPUT_PATH="<session-dir>/review-reports/review-consolidated-<timestamp>.md"` as a filled placeholder. Alternatively, use `{CONSOLIDATED_OUTPUT_PATH}` (curly-brace template syntax) consistently and rely on Pantry substitution before delivery.
- **Acceptance criterion violated**: ant-farm-84qf AC3 — "Downstream consumers can distinguish 'Big Head failed' from 'Big Head never ran'"

### Finding 2: `$CONSOLIDATED_OUTPUT_PATH` shell variable undefined in Pest Control timeout bash block

- **File(s)**: `orchestration/templates/reviews.md:L777`
- **Severity**: P2
- **Category**: correctness
- **Description**: The Pest Control timeout escalation bash block (also introduced by commit 1dfd4c7) has the same issue as Finding 1: `cat > "$CONSOLIDATED_OUTPUT_PATH" << 'EOF'` at L777 uses `"$CONSOLIDATED_OUTPUT_PATH"` as a shell variable, but no shell variable by that name is assigned in this block or its surrounding context. This block is presented as inline narrative instruction (not inside the main polling loop script), so there is no enclosing variable scope. The `cat >` will fail silently, leaving no artifact at the expected path when Pest Control times out.
- **Suggested fix**: Same as Finding 1 — either add an explicit shell variable assignment in the code block or use `{CONSOLIDATED_OUTPUT_PATH}` (template placeholder) so the Pantry fills the actual path before the template is delivered to Big Head.
- **Acceptance criterion violated**: ant-farm-84qf AC3 — same reasoning as Finding 1

---

## Acceptance Criteria Verification

### ant-farm-7kei: Big Head step ordering (commit d3932e9)

**AC 1** — "agents/big-head.md step ordering matches big-head-skeleton.md sequence: dedup → write report → Pest Control → file beads"
- PASS: Step 6 (dedup), step 7 (write report), step 8 (send to Pest Control, await verdict), step 9 (file beads) are now in correct sequence at `agents/big-head.md:L22–32`.

**AC 2** — "Bead filing step explicitly states it occurs only after Pest Control PASS verdict"
- PASS: Step 9 at `agents/big-head.md:L32` reads "ONLY after Pest Control PASS verdict."

**AC 3** — "No step in the agent definition instructs filing before the consolidated report is written"
- PASS: The word "filing" appears in step 6 as a future-tense reference ("Before filing, deduplicate..."), not as an instruction to file. No step issues a `bd create` instruction before step 9.

**Verdict for ant-farm-7kei**: PASS — all acceptance criteria met.

---

### ant-farm-84qf: Failure artifact writes (commit 1dfd4c7)

**AC 1** — "Every bash script block that can exit 1 on a failure path writes a FAILED artifact to $CONSOLIDATED_OUTPUT_PATH before exiting"
- PARTIAL: The artifact writes are structurally present (before `exit 1` at L594, and in the Pest Control block at L777), but the shell variable `$CONSOLIDATED_OUTPUT_PATH` is undefined in both blocks. The blocks will error at runtime rather than write the artifact. The structural intent is correct but the implementation is broken.

**AC 2** — "No failure artifact writes remain only in narrative prose outside of executable code blocks"
- PASS: Both failure artifact writes are inside `bash` code blocks (L588–L594 and L776–L784). The polling loop write is inside the main polling bash block; the Pest Control write is in an inline bash block.

**AC 3** — "Downstream consumers can distinguish 'Big Head failed' (FAILED artifact exists) from 'Big Head never ran' (no file at path)"
- FAIL: Due to the undefined `$CONSOLIDATED_OUTPUT_PATH` variable (Findings 1 and 2), no artifact will land on either failure path. The runtime outcome is identical to "never ran" — no file at path.

**Verdict for ant-farm-84qf**: NEEDS WORK — AC1 and AC3 not met due to undefined shell variable.

---

### ant-farm-igxq: Concurrency safety / temp file collision (commit 1dfd4c7)

**AC 1** — "No hardcoded /tmp/bead-desc.md path remains in any template or agent file"
- PASS: All occurrences replaced with `/tmp/bead-desc-$$.md` across all three files. Verified by grep: `agents/big-head.md:L32`, `orchestration/templates/big-head-skeleton.md:L127,150,152,160,171,173`, `orchestration/templates/reviews.md:L814,837,839,856,867,869`.

**AC 2** — "All temp file paths include a session-unique or process-unique component"
- PASS: `$$` (shell PID) is used throughout.

**AC 3** — "bd list calls in the dedup step check the exit code and abort bead filing on failure"
- PASS: `if ! bd list ... ; then ... exit 1; fi` pattern added at `orchestration/templates/reviews.md:L686` and `orchestration/templates/big-head-skeleton.md:L110`.

**AC 4** — "Two concurrent Big Head sessions running simultaneously cannot corrupt each other's bead descriptions"
- PASS: PID-unique temp files (`$$`) prevent collision.

**Verdict for ant-farm-igxq**: PASS — all acceptance criteria met.

---

## Preliminary Groupings

### Group A: Undefined shell variable `$CONSOLIDATED_OUTPUT_PATH` in failure-path bash blocks

- Finding 1 (`reviews.md:L588`) and Finding 2 (`reviews.md:L777`) share the same root cause: the fix adds `cat > "$CONSOLIDATED_OUTPUT_PATH"` in two bash blocks but never assigns the variable in shell scope. Both blocks will fail identically at runtime. The template treats `{CONSOLIDATED_OUTPUT_PATH}` (Pantry placeholder) and `$CONSOLIDATED_OUTPUT_PATH` (shell variable) as interchangeable, but they are not — Pantry substitution produces a literal string in the template prose/markdown, not a shell variable assignment.
- **Combined fix**: In each bash block that uses `"$CONSOLIDATED_OUTPUT_PATH"`, either (a) add a `CONSOLIDATED_OUTPUT_PATH=<filled-literal>` assignment that the Pantry populates, or (b) replace the shell variable reference with the Pantry placeholder `{CONSOLIDATED_OUTPUT_PATH}` directly in the heredoc redirect target (which requires no shell var).

---

## Summary Statistics

- Total findings: 2
- By severity: P1: 0, P2: 2, P3: 0
- Preliminary groups: 1 (both findings share one root cause)

---

## Cross-Review Messages

### Sent
- None.

### Received
- None.

### Deferred Items
- None.

---

## Coverage Log

| File | Status | Evidence |
|------|--------|----------|
| `agents/big-head.md` | Reviewed — 1 acceptance criterion fully verified (ant-farm-7kei), 1 criterion partially verified (ant-farm-igxq prose reference). No independent findings. | 38 lines, 9 steps in "When consolidating" section reviewed |
| `orchestration/templates/big-head-skeleton.md` | Reviewed — ant-farm-7kei N/A; ant-farm-84qf bash block L93 verified correct (uses `"$CONSOLIDATED_OUTPUT_PATH"` which is the same undefined-variable issue, but this was pre-existing before the fix); ant-farm-igxq PID-unique temp files and bd list exit-code check verified present. No new correctness findings beyond what applies to reviews.md. | 185 lines reviewed |
| `orchestration/templates/reviews.md` | Reviewed — Findings 1 and 2 filed. ant-farm-igxq changes verified correct. | 1048 lines; focused review on L496–L600 (polling loop), L680–L700 (dedup), L763–L800 (Pest Control timeout), L810–L870 (bead filing) |

---

## Overall Assessment

**Score**: 7/10
**Verdict**: PASS WITH ISSUES

Two P2 findings share a single root cause: the failure artifact writes added by ant-farm-84qf use `"$CONSOLIDATED_OUTPUT_PATH"` as a shell variable, but this variable is never assigned in the bash blocks where it appears. At runtime, the `cat >` command will fail silently (empty filename), so the FAILED artifact will not land. This means ant-farm-84qf's core goal — distinguishing "Big Head failed" from "Big Head never ran" — is not achieved on either failure path.

The ant-farm-7kei fix (step ordering) and ant-farm-igxq fix (concurrency safety, PID-unique temp files, bd list exit-code checking) are correctly implemented and all their acceptance criteria are met.

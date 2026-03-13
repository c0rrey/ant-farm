# Summary: ant-farm-84qf + ant-farm-igxq

**Task**: Fix failure artifact writes and concurrency safety in Big Head workflow templates
**Commit**: `1dfd4c7`
**Files changed**:
- `orchestration/templates/reviews.md`
- `orchestration/templates/big-head-skeleton.md`
- `agents/big-head.md`

---

## 1. Approaches Considered

### ant-farm-84qf (failure artifact writes)

**A. Shell variable + heredoc `cat` before every `exit 1`** *(selected)*
Add `cat > "$CONSOLIDATED_OUTPUT_PATH" << 'EOF' ... EOF` immediately before each `exit 1` in the bash script blocks. For the skeleton, convert the narrative-prose code block from a display fence to a `bash`-tagged executable block.
Tradeoffs: Minimal surface area change. Standard shell idiom. Clear to any LLM executing the template. Requires `$CONSOLIDATED_OUTPUT_PATH` to be set before the block (it already is, as a shell variable from the filled placeholder).

**B. Shell helper function `write_failure_artifact()`**
Define a reusable function at the top of each bash section and call it before each exit.
Tradeoffs: Adds indirection. Each bash block is a standalone template section, so the function would need to be repeated. Overkill for 2-3 failure paths.

**C. `trap 'write_failure_artifact' ERR` at script start**
Trap-based error handling automatically invokes the artifact writer on any nonzero exit.
Tradeoffs: Less explicit, can behave unexpectedly with subshells and pipeline errors. Not appropriate for LLM-executed templates where readability and predictability matter. Content of the artifact would be generic and not specific to the failure mode.

**D. Optimistic pre-write ("PENDING" artifact at script start)**
Write a PENDING artifact before entering the polling loop, overwrite with real output on success.
Tradeoffs: Requires cleanup logic on success, risks leaving stale PENDING artifacts if script is interrupted mid-success path. More complex state management.

### ant-farm-igxq (concurrency safety)

**Temp file uniqueness:**

**A. PID-based: `/tmp/bead-desc-$$.md`** *(selected)*
Shell PID (`$$`) is process-unique. Trivially supported in bash with no new dependencies.
Tradeoffs: PIDs theoretically recycle, but only after process death — safe for this use. Minimal change, matches the acceptance criteria example exactly.

**B. Session-suffix + PID: `/tmp/bead-desc-{SESSION_SUFFIX}-$$.md`**
Ties file to session context for stronger uniqueness.
Tradeoffs: Requires `{SESSION_SUFFIX}` to be a filled placeholder, adding a new Pantry dependency. Unnecessary complexity given PID alone is sufficient.

**C. `mktemp`: `BEAD_DESC_FILE=$(mktemp /tmp/bead-desc-XXXXXX.md)`**
OS-guaranteed unique via random suffix.
Tradeoffs: Requires introducing a variable for the path, which changes three lines per filing block (`cat > $BEAD_DESC_FILE`, `--body-file "$BEAD_DESC_FILE"`, `rm -f "$BEAD_DESC_FILE"`). More verbose without meaningful safety gain over PID.

**D. Timestamp + PID: `/tmp/bead-desc-$(date +%s)-$$.md`**
Extreme uniqueness via both time and process.
Tradeoffs: Verbose, harder to clean up stale files, overkill.

**bd list exit-code checking:**

**A. `if ! bd list ...; then echo ERROR; exit 1; fi`** *(selected)*
Explicit, readable inline check. Matches the suggested fix in the review report exactly.

**B. `bd list ... || { echo ERROR; exit 1; }`**
Shorter but slightly less readable in a multi-line template context.

**C. `set -e` at script start**
Automatic abort on any nonzero exit.
Tradeoffs: Too broad — would break on grep/other commands that legitimately return nonzero. Unsafe for these templates.

**D. Retry loop**
Retry 2-3 times before aborting, consistent with MEMORY.md lock contention guidance.
Tradeoffs: More resilient but adds complexity. Task spec and acceptance criteria specify abort-on-failure, not retry.

---

## 2. Selected Approach with Rationale

For both bugs, the guiding principle was minimum viable change that directly satisfies each acceptance criterion without touching non-failure-path logic.

- **ant-farm-84qf**: Approach A (heredoc cat before exit 1). The failure artifact content exactly matches the format defined in `big-head-skeleton.md:L78-85` (Status, Timestamp, Reason, Recovery). The skeleton's narrative prose block was converted to a `bash`-tagged executable block wrapping the same heredoc pattern, which is what the agent will actually execute.

- **ant-farm-igxq**: Approach A for both sub-problems. PID (`$$`) satisfies the uniqueness requirement with the smallest diff. The `if ! bd list ...` pattern exactly matches the suggested fix from the RC-2 finding and the task spec.

---

## 3. Implementation Description

### reviews.md changes

**Polling timeout failure path** (`reviews.md:L586-596` after fix):
Added `cat > "$CONSOLIDATED_OUTPUT_PATH" << 'EOF' ... EOF` block immediately before `exit 1` in the `if [ $REPORTS_FOUND -eq 0 ]` block. Content follows the standard failure artifact format: Status FAILED with reason, timestamp placeholder, and recovery instructions.

**Cross-session dedup bd list** (`reviews.md:Step 2.5`):
Replaced the bare `bd list --status=open -n 0 --short` with an `if !` check that redirects output to `/tmp/open-beads-$$.txt` and exits 1 on failure. Updated the surrounding prose to reference the temp file by name.

**Pest Control timeout escalation** (`reviews.md:L775-793` after fix):
Inserted a `bash`-tagged code block containing the `cat > "$CONSOLIDATED_OUTPUT_PATH"` heredoc before the existing prose escalation message. The artifact documents the Pest Control unavailability with appropriate Status/Timestamp/Reason/Recovery fields.

**Bead filing temp file paths** (`reviews.md:L794 and L836` after fix):
Changed `cat > /tmp/bead-desc.md` to `cat > /tmp/bead-desc-$$.md`, and updated both the `--body-file` argument and the `rm -f` cleanup line to match in both the PASS branch bead filing block and the P3 auto-filing block.

### big-head-skeleton.md changes

**Failure artifact instruction at L91-99**:
Converted the narrative prose display block (plain fenced code with markdown content) to an executable `bash`-tagged block containing the `cat > "$CONSOLIDATED_OUTPUT_PATH" << 'EOF' ... EOF` heredoc. Changed the surrounding prose from "write a failure artifact to..." to "write a failure artifact using this bash block:".

**Cross-session dedup bd list at L108**:
Replaced the bare `bd list --status=open -n 0 --short` with the same `if !` exit-code-checking pattern used in reviews.md. References `/tmp/open-beads-$$.txt` for output.

**PASS branch bead filing (L122/L145/L147)**:
Changed all three occurrences of `/tmp/bead-desc.md` to `/tmp/bead-desc-$$.md`.

**P3 auto-filing (L155/L166/L168)**:
Changed all three occurrences of `/tmp/bead-desc.md` to `/tmp/bead-desc-$$.md`.

### agents/big-head.md changes

Step 9 prose updated from "always write to a temp file" to "always write to a process-unique temp file (e.g., `/tmp/bead-desc-$$.md`) ... to avoid collision between concurrent Big Head sessions."

---

## 4. Correctness Review

### `orchestration/templates/reviews.md`

**Polling timeout block (AC1)**:
- `cat > "$CONSOLIDATED_OUTPUT_PATH" << 'EOF'` is now inside the `if [ $REPORTS_FOUND -eq 0 ]` block, before `exit 1`. PASS.
- Uses `$CONSOLIDATED_OUTPUT_PATH` shell variable (set from filled placeholder by Pantry/fill-review-slots.sh). Consistent with existing usage of the variable throughout the template. PASS.
- Artifact format: Status, Timestamp, Reason, Recovery — matches `big-head-skeleton.md:L78-85`. PASS.

**Dedup bd list exit-code check (AC8)**:
- `if ! bd list --status=open -n 0 --short > /tmp/open-beads-$$.txt 2>&1; then` — captures stdout+stderr, exits 1 on nonzero. PASS.
- Surrounding prose updated to reference `/tmp/open-beads-$$.txt`. PASS.

**Pest Control timeout escalation (AC2)**:
- Bash block with `cat > "$CONSOLIDATED_OUTPUT_PATH"` heredoc inserted before the prose escalation block. PASS.
- Format: Status, Timestamp, Reason, Recovery. PASS.
- The existing "Do NOT file any beads when escalating" instruction is preserved. PASS.

**Bead filing temp files (AC6)**:
- PASS branch: `cat > /tmp/bead-desc-$$.md`, `--body-file /tmp/bead-desc-$$.md`, `rm -f /tmp/bead-desc-$$.md`. PASS.
- P3 auto-filing: same pattern. PASS.
- Grep confirms no `/tmp/bead-desc.md` (without `$$`) remains in the file. PASS.

### `orchestration/templates/big-head-skeleton.md`

**Failure artifact instruction (AC3)**:
- Block is now `bash`-tagged and contains the executable heredoc. PASS.
- Instruction text changed from narrative prose ("write a failure artifact to...") to "write a failure artifact using this bash block:". PASS.

**Dedup bd list exit-code check (AC7)**:
- Same `if !` pattern as reviews.md. PASS.
- References `/tmp/open-beads-$$.txt`. PASS.

**Bead filing temp files (AC5)**:
- PASS branch bead filing (step 10): `cat > /tmp/bead-desc-$$.md`, `--body-file /tmp/bead-desc-$$.md`, `rm -f /tmp/bead-desc-$$.md`. PASS.
- P3 auto-filing (step 11): same pattern. PASS.
- Grep confirms no `/tmp/bead-desc.md` (without `$$`) remains. PASS.

### `agents/big-head.md`

**Temp file naming prose (AC9)**:
- Step 9 now reads: "always write to a process-unique temp file (e.g., `/tmp/bead-desc-$$.md`) and use `--body-file` to avoid collision between concurrent Big Head sessions." PASS.
- Step number not changed (ant-farm-7kei handles reordering). PASS.

### AC4 — All failure artifacts follow standard format

Standard format from `big-head-skeleton.md:L78-85`:
```
# [COMPONENT] — [FAILURE TYPE]
**Status**: FAILED — <one-line description>
**Timestamp**: <ISO 8601>
**Reason**: <what went wrong>
**Recovery**: <what to do next>
```

All three failure artifact writes use this format:
- `reviews.md` polling timeout: `# Big Head Consolidation — BLOCKED: Missing Nitpicker Reports`, Status/Timestamp/Reason/Recovery. PASS.
- `reviews.md` Pest Control timeout: `# Big Head Consolidation — BLOCKED: Pest Control Timeout`, Status/Timestamp/Reason/Recovery. PASS.
- `big-head-skeleton.md` timeout block: same format as reviews.md polling timeout. PASS.

---

## 5. Build/Test Validation

These are markdown template files — there is no compilation step, test suite, or linter applicable to the content changes.

Manual validation performed:
- Grep for `/tmp/bead-desc\.md` (without `$$`) across the repo: 0 matches in template/agent files (only in `.beads/issues.jsonl` which describes the bug, not the fix).
- Grep for bare `^bd list --status=open -n 0 --short` not preceded by `if !`: 0 matches in the templates directory.
- Visual re-read of all changed sections confirms correct indentation and heredoc syntax.

---

## 6. Acceptance Criteria Checklist

| # | Criterion | Status |
|---|-----------|--------|
| AC1 | `reviews.md` polling timeout bash block writes failure artifact to `$CONSOLIDATED_OUTPUT_PATH` before `exit 1` | PASS |
| AC2 | Pest Control timeout escalation path includes bash block writing failure artifact before escalating | PASS |
| AC3 | `big-head-skeleton.md:L91-99` failure artifact format is in executable bash (heredoc) not narrative prose | PASS |
| AC4 | All failure artifacts follow the standard format from `big-head-skeleton.md:L78-85` | PASS |
| AC5 | All `/tmp/bead-desc.md` refs in `big-head-skeleton.md` use `/tmp/bead-desc-$$.md` | PASS |
| AC6 | All `/tmp/bead-desc.md` refs in `reviews.md` use `/tmp/bead-desc-$$.md` | PASS |
| AC7 | `bd list` at `big-head-skeleton.md` cross-session dedup step includes exit-code check with abort-on-failure | PASS |
| AC8 | `bd list` at `reviews.md:Step 2.5` includes exit-code check with abort-on-failure | PASS |
| AC9 | `agents/big-head.md` step mentions unique naming pattern | PASS |

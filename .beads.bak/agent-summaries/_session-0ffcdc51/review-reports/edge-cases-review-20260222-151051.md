# Report: Edge Cases Review (Round 2 — Fix Verification)

**Scope**: Fix commits d3932e9 through 1dfd4c7
**Reviewer**: edge-cases | Nitpicker (Sonnet 4.6)
**Review round**: 2 — scope limited to fix commits; out-of-scope findings reported only if they cause runtime failure or silently wrong results

---

## Fix Commits Reviewed

| Commit | Summary |
|--------|---------|
| d3932e9 | fix: reorder big-head.md consolidation steps to gate bead filing behind Pest Control checkpoint (ant-farm-7kei) |
| 1dfd4c7 | fix: add failure artifact writes and concurrency safety to Big Head workflow (ant-farm-84qf, ant-farm-igxq) |

---

## Findings Catalog

### Finding 1: Pest Control timeout failure artifact overwrites the consolidated summary

- **File(s)**: `orchestration/templates/reviews.md:777`
- **Severity**: P2
- **Category**: edge-case
- **Description**: The new Pest Control timeout bash block (added in commit 1dfd4c7) writes a failure stub to `"$CONSOLIDATED_OUTPUT_PATH"` using `cat > "$CONSOLIDATED_OUTPUT_PATH"`. At the point this block executes, Big Head has already written the full consolidated summary to that same path in Step 3. Running this block overwrites — and permanently destroys — the consolidated findings Big Head spent the entire workflow producing. After the overwrite, the Queen receives only a sparse failure stub at that path; the root-cause groups, deduplication log, and priority breakdown are gone.

  The failure artifact convention (big-head-skeleton.md:77-86) is defined for cases where consolidation has NOT yet produced output. At Pest Control timeout, consolidation is complete and output already exists — the convention does not apply here, yet the fix mechanically applied the same pattern.

  Contrast with the polling-timeout bash block (reviews.md:588): that block correctly writes the failure artifact BEFORE any consolidated output exists, so overwriting is safe there.

- **Suggested fix**: Do not overwrite the already-written consolidated summary. Instead, write the Pest Control timeout failure artifact to a separate file (e.g., `review-consolidated-<timestamp>-pc-timeout.md`) so the consolidated findings survive. Update the escalation message to provide both paths: the consolidated summary path and the timeout failure path.

---

### Finding 2: `$CONSOLIDATED_OUTPUT_PATH` shell variable undefined in polling-timeout and Pest Control-timeout bash blocks (reviews.md)

- **File(s)**: `orchestration/templates/reviews.md:588`, `orchestration/templates/reviews.md:777`
- **Severity**: P2
- **Category**: edge-case
- **Description**: Both new bash blocks reference `"$CONSOLIDATED_OUTPUT_PATH"` as a shell variable, but this variable is never assigned anywhere in the polling-loop bash block that surrounds line 588, nor in any wrapper script. The value exists in the Big Head brief as a prose field ("**Consolidated output**: ...") that `build-review-prompts.sh` fills from `{{CONSOLIDATED_OUTPUT_PATH}}`, but the polling bash block at lines 496-596 does not set `CONSOLIDATED_OUTPUT_PATH=` before using it at line 588. If Big Head runs this block verbatim, `"$CONSOLIDATED_OUTPUT_PATH"` will expand to an empty string (or an unset-variable error with `set -u`), and the failure artifact will be written to a file named with an empty path, causing a shell error or writing to the wrong location.

  The same issue exists at line 777 — the Pest Control timeout block is presented in isolation (outside of any assignment block) and also uses `"$CONSOLIDATED_OUTPUT_PATH"` without prior assignment in scope.

  Note: `big-head-skeleton.md:93` uses the same `"$CONSOLIDATED_OUTPUT_PATH"` pattern, but in that file `{CONSOLIDATED_OUTPUT_PATH}` is a substitution placeholder that `build-review-prompts.sh` fills at line 297 (step 4). The conversion from `{UPPERCASE}` to `{{UPPERCASE}}` at line 270 and then `fill_slot` at line 297 means the bash code block in the skeleton receives a literal path substituted in. This substitution does NOT apply to `reviews.md`, which is documentation/instructions content copied verbatim into the Big Head brief, not the Big Head agent-facing template.

  The practical effect depends on whether Big Head is reading these bash blocks as documentation (and defines the variable itself before running) or copy-pastes them literally. Either way, the instructions are ambiguous — the variable is not defined within either bash block, and a developer or LLM following the blocks literally will produce a broken artifact write.

- **Suggested fix**: Add `CONSOLIDATED_OUTPUT_PATH="<session-dir>/review-reports/review-consolidated-<timestamp>.md"` as the first line inside each bash block, or document clearly (adjacent to each block) that Big Head must define this variable from the brief before running the block. The skeleton (big-head-skeleton.md) handles this correctly via template substitution; the reviews.md documentation blocks should match.

---

### Finding 3: `$CONSOLIDATED_OUTPUT_PATH` undefined in big-head-skeleton.md timeout bash block

- **File(s)**: `orchestration/templates/big-head-skeleton.md:93`
- **Severity**: P3
- **Category**: edge-case
- **Description**: The polling-timeout bash block in the skeleton uses `"$CONSOLIDATED_OUTPUT_PATH"` (line 93). `build-review-prompts.sh` fills `{{CONSOLIDATED_OUTPUT_PATH}}` as a placeholder in the skeleton body (line 297 of build-review-prompts.sh), but the conversion pass at line 270 converts `{CONSOLIDATED_OUTPUT_PATH}` → `{{CONSOLIDATED_OUTPUT_PATH}}`. The bash code uses `"$CONSOLIDATED_OUTPUT_PATH"` which is a shell variable reference, not a `{{...}}` placeholder, so `fill_slot` will NOT substitute it. The LLM receiving this block would need to define the shell variable before running the code.

  This is lower severity than Finding 2 because the skeleton's Consolidation Brief section (written by `build-review-prompts.sh` at lines 281-283) provides the literal consolidated output path, which the LLM can read and use to define the variable before running the block. The brief provides the information; the bash code just doesn't wire it up explicitly.

- **Suggested fix**: Either (a) use `{{CONSOLIDATED_OUTPUT_PATH}}` inside the bash block (which gets substituted to the literal path by `fill_slot`), or (b) add a line before the heredoc: `CONSOLIDATED_OUTPUT_PATH="{{CONSOLIDATED_OUTPUT_PATH}}"` so the shell variable is explicitly defined within the block.

---

## Preliminary Groupings

### Group A: Failure artifact bash blocks use undefined shell variable

**Findings**: 1 (partial), 2, 3

The root cause is that the new failure-artifact bash blocks in both `reviews.md` and `big-head-skeleton.md` reference `"$CONSOLIDATED_OUTPUT_PATH"` as a shell variable that is never assigned within the bash block itself. The variable originates as a template placeholder (`{CONSOLIDATED_OUTPUT_PATH}` / `{{CONSOLIDATED_OUTPUT_PATH}}`), but the bash code blocks use shell variable syntax (`$CONSOLIDATED_OUTPUT_PATH`) which bypasses the placeholder substitution mechanism. All three instances share the same underlying inconsistency: the template substitution system and the shell variable reference system are conflated.

- `big-head-skeleton.md:93` — bash block in timeout path (P3, skeleton gets some coverage via `fill_slot`)
- `reviews.md:588` — bash block in polling timeout path (P2, no substitution pathway)
- `reviews.md:777` — bash block in Pest Control timeout path (P2, no substitution pathway)

### Group B: Pest Control timeout block overwrites existing consolidated summary

**Finding**: 1

Standalone. The overwrite at `reviews.md:777` is a destructive side effect of applying the failure-artifact convention at the wrong stage of the workflow. The consolidated summary already exists when the Pest Control timeout triggers; writing to the same path destroys it. This is distinct from the undefined-variable issue (Group A) — even if the variable were defined, the overwrite would still be wrong.

---

## Summary Statistics

- Total findings: 3
- By severity: P1: 0, P2: 2, P3: 1
- Preliminary groups: 2

---

## Cross-Review Messages

### Sent

None sent. All findings are within edge-cases scope.

### Received

None received at time of report writing.

### Deferred Items

None.

---

## Coverage Log

| File | Status | Evidence |
|------|--------|----------|
| `agents/big-head.md` | Reviewed — no in-scope edge-case issues | 38 lines; step reordering (d3932e9) and PID-unique temp file wording (1dfd4c7) reviewed. Step ordering fix is correct. PID-unique prose addition is accurate. No edge-case issues introduced. |
| `orchestration/templates/big-head-skeleton.md` | Findings: #3 | 185 lines; failure artifact bash block at L93 uses `"$CONSOLIDATED_OUTPUT_PATH"` shell variable without prior assignment in the bash block. PID-unique path substitution (`$$.md`) reviewed and correct across all 3 bead-filing blocks (L124, L160, L168). bd list exit-code check reviewed and correct (L110-113). |
| `orchestration/templates/reviews.md` | Findings: #1, #2 | 1048 lines; reviewed fix-scope changes in full. Polling-timeout failure artifact (L586-596) adds the heredoc write but uses unassigned `$CONSOLIDATED_OUTPUT_PATH`. Pest Control timeout failure artifact (L776-784) overwrites the existing consolidated summary and uses unassigned `$CONSOLIDATED_OUTPUT_PATH`. PID-unique path substitution reviewed across all bead-filing blocks — correct. bd list exit-code check at L683-687 reviewed and correct. |

---

## Overall Assessment

**Score**: 7/10
**Verdict**: PASS WITH ISSUES

The fix commits correctly address the core issues they target: step reordering in `big-head.md` is sound, PID-unique temp file paths eliminate the original collision risk, and the `bd list` exit-code checks correctly abort on failure to prevent phantom dedup. Two P2 findings were introduced by the failure-artifact additions: (1) the Pest Control timeout block destructively overwrites the completed consolidated summary, and (2) both new bash blocks in `reviews.md` reference `"$CONSOLIDATED_OUTPUT_PATH"` as a shell variable that is never defined within the block. These are edge cases that fire only in timeout scenarios, but when they do fire, they produce misleading output (an empty-path write or an overwritten artifact) rather than a clean failure.

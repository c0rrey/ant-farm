# Report: Edge Cases Review

**Scope**: orchestration/_archive/pantry-review.md, orchestration/SETUP.md, orchestration/templates/pantry.md, orchestration/templates/reviews.md, orchestration/templates/scout.md, README.md, scripts/compose-review-skeletons.sh, scripts/parse-progress-log.sh
**Reviewer**: Edge Cases Review (code-reviewer / nitpicker)

## Findings Catalog

### Finding 1: Stale pantry-review agent in ~/.claude/agents/ now unguarded by Scout exclusion list

- **File(s)**: `orchestration/templates/scout.md:63`
- **Severity**: P2
- **Category**: edge-case
- **Description**: Commit ant-farm-oc9v removed `pantry-review` from the Scout's Dirt Pusher exclusion list. However, `~/.claude/agents/pantry-review.md` still exists on disk (it was removed from `agents/` in an earlier commit, 05ba029, but `sync-to-claude.sh` deliberately never deletes files from `~/.claude/agents/` — it only adds/updates). The Scout scans `~/.claude/agents/*.md` at runtime to build its agent catalog. Before this change, the exclusion list explicitly barred the Scout from recommending pantry-review as a Dirt Pusher agent; after this change, only the description-matching heuristic separates it from implementation candidates. If a future task description happens to match the (stale, non-DEPRECATED) description in `~/.claude/agents/pantry-review.md`, the Scout could recommend `pantry-review` as a Dirt Pusher for a task. The Queen would then spawn an orchestration agent as an implementation agent — a silent failure mode that produces no code and no commit.
- **Suggested fix**: Either (a) add `pantry-review` back to the exclusion list at `orchestration/templates/scout.md:63` until the stale `~/.claude/agents/pantry-review.md` is confirmed deleted, OR (b) document in `sync-to-claude.sh` that users must manually delete `~/.claude/agents/pantry-review.md` after pulling this commit. The safer fix is (a) — keep it in the exclusion list until manual cleanup is confirmed.
- **Cross-reference**: Related to the sync design gap (no `--delete` in rsync for agents). Not a new design gap, but newly exposed by removing the exclusion list entry.

### Finding 2: compose-review-skeletons.sh does not validate that SESSION_DIR exists before use

- **File(s)**: `scripts/compose-review-skeletons.sh:41-62`
- **Severity**: P3
- **Category**: edge-case
- **Description**: The script validates that the three source files (REVIEWS_MD, NITPICKER_SKELETON, BIG_HEAD_SKELETON) exist and are readable (lines 46-55), but does not check whether `SESSION_DIR` itself exists before attempting `mkdir -p "$SKELETON_DIR"`. While `mkdir -p` will create the path if needed (including `SESSION_DIR` if absent), a typo in `SESSION_DIR` passed by the caller would silently create a new directory tree in the wrong location instead of failing with a clear error. The comment update in this commit (lines 70-73) states that skeleton files are written to `{SESSION_DIR}/review-skeletons/` — if `SESSION_DIR` doesn't exist, the artifacts land silently in the wrong place. This matters because the Pantry's Section 1 Step 2.5 records these paths and returns them to the Queen; a path mismatch would cause a downstream failure during fill-review-slots.sh.
- **Suggested fix**: Add a check before line 61: `[ -d "$SESSION_DIR" ] || { echo "ERROR: SESSION_DIR not found: $SESSION_DIR" >&2; exit 1; }`. This gives a clear, immediate error rather than silently creating a rogue directory.

### Finding 3: extract_agent_section comment updated to state "exactly one delimiter" assumption but code still silently fails if assumption is violated

- **File(s)**: `scripts/compose-review-skeletons.sh:68-77`
- **Severity**: P3
- **Category**: edge-case
- **Description**: The updated comment (lines 70-73) documents that skeleton files are "expected to contain exactly one such delimiter." The awk at line 76 (`awk '/^---$/{count++; next} count>=1{print}'`) silently handles multiple delimiters by printing content after the first `---` (the second `---` would appear as literal output in the skeleton body). No validation enforces the "exactly one" expectation. If a skeleton file ever gains a second `---` (e.g., a maintainer adds a section break), the resulting skeleton file would contain `---` in the middle of its body without any error or warning. The comment documents the assumption but the code does not guard it.
- **Suggested fix**: After line 76, add a delimiter count check — if the count of `^---$` lines in the file is not exactly 1, emit a warning to stderr: `count=$(grep -c '^---$' "$file" || true); [ "$count" -eq 1 ] || echo "WARNING: $file contains $count '---' delimiter(s); expected exactly 1" >&2`. This matches the now-documented assumption with a runtime guard.
- **Concrete failure scenario (flagged by correctness-reviewer)**: If either skeleton file ever gained YAML frontmatter (which uses `---` as open/close delimiters), the awk would strip BOTH `---` lines and produce an empty `skeleton_body`. The resulting skeleton file would contain only the header comments and brief section, with no agent-facing instructions — causing every spawned Nitpicker to receive a prompt with no review instructions. No error would be raised. Currently safe (both files have exactly one `---` and no frontmatter), but the failure mode is silent and severe if the assumption ever breaks.

## Preliminary Groupings

### Group A: Stale agent state interacting with exclusion list removal (Finding 1)

- Finding 1 — standalone; root cause is the interaction between sync-without-delete policy and removal of the explicit exclusion list entry.
- **Suggested combined fix**: Re-add `pantry-review` to the exclusion list, or update sync documentation to require manual deletion.

### Group B: Missing precondition validation in scripts (Findings 2, 3)

- Finding 2 (no SESSION_DIR check) and Finding 3 (no delimiter count validation) share the root cause of missing input precondition guards in the shell scripts.
- Both scripts validate some inputs but not all.
- **Suggested combined fix**: Add defensive checks at the top of the relevant functions for all required preconditions, consistent with the pattern already established for source file validation.

## Summary Statistics

- Total findings: 3
- By severity: P1: 0, P2: 1, P3: 2
- Preliminary groups: 2

## Cross-Review Messages

### Sent

- None sent. All findings are squarely in the edge-cases domain (missing validation, unguarded assumptions, stale state interactions).

### Received

- From correctness-reviewer: "awk in `scripts/compose-review-skeletons.sh:74-78` silently strips ALL bare `---` lines — YAML frontmatter scenario would produce empty skeleton body with no error." — Action taken: confirmed the failure mode is real (silently empty output) and added a concrete scenario description to Finding 3. No new finding created; this is the same root cause as Finding 3.

### Deferred Items

- None.

## Coverage Log

| File | Status | Evidence |
|------|--------|----------|
| `orchestration/_archive/pantry-review.md` | Reviewed — no issues | YAML frontmatter updated with `status: archived` and DEPRECATED description; body unchanged. Frontmatter is valid YAML. |
| `orchestration/SETUP.md` | Reviewed — no issues | Code fence nesting fixed (outer ```` ```` ``` ```` wraps inner ` ``` `). No edge case concerns introduced. |
| `orchestration/templates/pantry.md` | Reviewed — no issues | Section 2 header updated to `[DEPRECATED — replaced by fill-review-slots.sh]`. The deprecated section body remains for reference use. No validation or input handling changes. |
| `orchestration/templates/reviews.md` | Reviewed — no issues | Two comment-only changes: HTML comment on line 1 updated to name `fill-review-slots.sh`; inline code comment reworded from `CONSTRAINT:` to `Report count constraint`. Neither change affects runtime behavior or error handling. |
| `orchestration/templates/scout.md` | Findings: #1 | `pantry-review` removed from Dirt Pusher exclusion list at line 63. See Finding 1. |
| `README.md` | Reviewed — no issues | ASCII diagram updated to replace Pantry with `fill-review-slots.sh` as the review slot-fill actor. Diagram alignment is correct (pipe characters land at consistent column positions). |
| `scripts/compose-review-skeletons.sh` | Findings: #2, #3 | Comment updated for `extract_agent_section` helper. No logic changes, but the documented assumption (exactly one `---` delimiter) is unguarded. SESSION_DIR existence not validated before mkdir. |
| `scripts/parse-progress-log.sh` | Reviewed — no issues | Two documentation-only changes: expanded inline comment about log ordering (lines 176-180) and shortened UNREACHABLE comment (line 208). Both changes accurately document existing behavior. The `[[ =~ ]]` regex at line 169 is compatible with bash 3.2 (confirmed on macOS Darwin 25.3.0). The map_set/map_get implementation uses temp files for POSIX compatibility; the `_key_file` function does not sanitize `step_key` but this is pre-existing and the comment at line 125-127 documents the safety assumption. |

## Overall Assessment

**Score**: 8/10
**Verdict**: PASS WITH ISSUES

The changes are documentation and comment updates with one functional change (removing `pantry-review` from the Scout exclusion list). The functional change introduces a P2 risk: if a user's `~/.claude/agents/` contains the stale `pantry-review.md` (which it likely does, because `sync-to-claude.sh` never deletes agent files), the Scout may recommend it as a Dirt Pusher after this commit. The two P3 findings are minor defensive gaps in pre-existing scripts that were not worsened by these commits. No data loss, crash, or hard-to-diagnose failures are introduced.

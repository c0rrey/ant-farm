# Task Summary: ant-farm-0cf
**Task**: Parallelize review prompt composition with implementation via bash scripts
**Commit**: 201ee96
**Status**: COMPLETE

---

## 1. Approaches Considered

### Approach A: envsubst-based slot filling
Use GNU `envsubst` to fill `${VAR}` style placeholders. Simple and declarative. Rejected because
`envsubst` is not available by default on macOS (requires GNU gettext via homebrew) and requires
callers to export each variable before invoking the script — fragile for multiline values like file
lists.

### Approach B: sed-based replacement with {{DOUBLE_BRACE}} markers (selected)
Use `{{SLOT_NAME}}` markers in skeleton files. Script 1 writes these markers; Script 2 uses awk-based
replacement (more robust than sed for multiline values). Works on all POSIX systems without additional
tooling. The double-brace convention avoids collision with shell parameter expansion (`$VAR`, `${VAR}`)
and markdown/template syntax (`{single}`).

### Approach C: Python template engine
Write Python scripts using `string.Template` or jinja2. More robust escaping and error messages.
Rejected because it introduces a Python version dependency and is architecturally heavier than needed
for mechanical string substitution. Shell scripts are more natural for the file-handling use case.

### Approach D: heredoc generation at creation time
Generate complete review prompt files at Pantry Section 1 time using bash heredocs — no slot markers,
no second script. Rejected because the key inputs (commit range, changed file list, task IDs) are
NOT available during Section 1. They're only known after dirt-pushers finish, which is the entire
point of the split design.

### Approach E: JSON manifest + jq assembly
Script 1 writes a JSON manifest of all review template fragments; Script 2 uses jq to assemble final
prompts. More structured than sed, but requires jq (not universally installed) and adds complexity
with no benefit for the simple string interpolation use case.

---

## 2. Selected Approach with Rationale

**Selected: Approach B** — sed/awk-based {{DOUBLE_BRACE}} slot markers.

Rationale:
- Universal availability: awk and sed are present on every POSIX system; no package installs needed
- Clear slot marker semantics: `{{SLOT_NAME}}` is visually distinct from shell vars (`$VAR`),
  markdown template vars (`{single}`), and bead IDs — no confusion about what needs filling
- Failure transparency: non-zero exit codes propagate to callers; errors go to stderr; stdout is
  clean return-table output the Queen can use directly
- Minimal LLM surface: once skeletons exist, slot-filling is pure text substitution — zero LLM
  round-trips, zero template reads absorbed into Queen's context

---

## 3. Implementation Description

### New files

**`scripts/compose-review-skeletons.sh`** (Script 1)
- Called by the Pantry during Section 1 Step 2.5
- Arguments: SESSION_DIR, REVIEWS_MD_PATH, NITPICKER_SKELETON_PATH, BIG_HEAD_SKELETON_PATH
- Reads the agent-facing section (below `---`) from nitpicker-skeleton.md and big-head-skeleton.md
- Converts single-brace `{WORD}` placeholders to `{{WORD}}` slot markers, then fills `{{REVIEW_TYPE}}`
  with the actual review type (since that's known statically)
- Writes 5 skeleton files to `{SESSION_DIR}/review-skeletons/`:
  skeleton-clarity.md, skeleton-edge-cases.md, skeleton-correctness.md, skeleton-excellence.md, skeleton-big-head.md
- Verifies all 5 output files are non-empty before exiting 0
- Errors to stderr + exit 1 on any failure

**`scripts/fill-review-slots.sh`** (Script 2)
- Called by the Queen at RULES.md Step 3b (replacing pantry-review spawn)
- Arguments: SESSION_DIR, COMMIT_RANGE, CHANGED_FILES, TASK_IDS, TIMESTAMP, REVIEW_ROUND
- Supports `@file` prefix for CHANGED_FILES and TASK_IDS to avoid shell quoting issues with newlines
- Round-aware: round 1 fills all 4 reviews; round 2+ fills only correctness + edge-cases
- Uses awk-based fill_slot() helper that writes replacement values to a temp file to avoid sed
  special-character escaping issues with path separators and newlines
- Writes to `{SESSION_DIR}/prompts/review-{type}.md` and `{SESSION_DIR}/previews/review-{type}-preview.md`
- Big Head brief written to `{SESSION_DIR}/prompts/review-big-head-consolidation.md`
- Prints a return table to stdout; Queen reads exit code only — never reads file contents
- Errors to stderr + exit 1 on any failure

### Modified files

**`orchestration/templates/pantry.md`**
- Added Step 2.5 between existing Steps 2 and 3 in Section 1
- Step 2.5 instructs Pantry to call compose-review-skeletons.sh and report skeleton paths in the return table
- Step 5 (Return File Paths) updated to include skeleton paths in the return table
- Section 2 (Review Mode) marked as DEPRECATED with a prominent blockquote note pointing to RULES.md Step 3b
- Section 2 content retained verbatim for reference

**`orchestration/RULES.md`**
- Step 3b rewritten: removed "spawn the Pantry (pantry-review)" instruction
- Replaced with: call fill-review-slots.sh bash script, then spawn Nitpicker team
- Timestamp generation instruction added (YYYYMMDD-HHmmss format)
- Agent Types table: pantry-review row marked as deprecated with strikethrough
- Model Assignments table: pantry-review row marked as deprecated

**`scripts/sync-to-claude.sh`**
- Added block to sync both scripts to `~/.claude/orchestration/scripts/` after the orchestration rsync
- Scripts are chmod +x'd at the destination

---

## 4. Correctness Review

### scripts/compose-review-skeletons.sh
- Argument count validation: checked (4 required)
- Source file existence and readability: both checked before proceeding
- Directory creation: mkdir -p with error handling
- Single-brace → double-brace conversion: `sed 's/{\([A-Z][A-Z_]*\)}/{{\1}}/g'` — correct POSIX BRE regex
- {{REVIEW_TYPE}} substitution after conversion: correct order (convert all first, then fill one)
- Output verification: checks all 5 files exist AND are non-empty (not just exit code)
- Error propagation: all failure paths use `echo "ERROR: ..." >&2; exit 1`
- set -euo pipefail: present at top

### scripts/fill-review-slots.sh
- Argument count validation: checked (6 required)
- @file argument resolution: resolve_arg() helper with file existence check
- REVIEW_ROUND integer validation: grep -qE '^[0-9]+$'
- Skeleton directory existence: checked before proceeding
- All 5 required skeletons: checked before proceeding
- Round-aware active review selection: round 1 = 4 types, round 2+ = 2 types
- fill_slot() awk approach: writes value to tmpfile, avoids sed metacharacter escaping
- Per-file prompts+previews loop: copies skeleton, fills each slot, verifies
- Big Head brief: expected report paths list is round-appropriate
- Output verification: checks all expected prompts + previews exist and are non-empty
- Return table: printed to stdout in Pantry-compatible format
- set -euo pipefail: present at top

### orchestration/templates/pantry.md
- Step 2.5 added after the task brief validation step: correct placement
- Script path uses `~/.claude/orchestration/scripts/` (runtime path): correct
- Template paths use `~/.claude/orchestration/templates/`: correct
- Failure format matches existing Pantry failure reporting convention: consistent
- Section 2 deprecation note: prominent blockquote at section top, content preserved below

### orchestration/RULES.md
- Step 3b: No longer mentions pantry-review spawn — fully replaced by script call
- Timestamp format specified: YYYYMMDD-HHmmss — consistent with existing format in reviews.md
- mkdir for review-reports retained after script call (correct ordering)
- Nitpicker team spawn instructions unchanged
- Agent Types and Model Assignments: deprecated rows use strikethrough markdown

### scripts/sync-to-claude.sh
- New sync block placed after the orchestration rsync: correct
- mkdir -p for destination: safe
- chmod +x applied at destination: correct
- Only the two new scripts are synced (not all scripts): correct (install-hooks.sh etc. are not orchestration scripts)

### Acceptance Criteria Verification

1. **Pantry Section 1 invocation produces both implementation prompts AND review skeletons**
   - Step 2.5 in pantry.md calls compose-review-skeletons.sh during Section 1 after task briefs
   - Skeletons written to session-dir/review-skeletons/ alongside the implementation prompts
   - VERIFIED: criteria met

2. **No second Pantry invocation is needed for review prompt composition**
   - RULES.md Step 3b now calls fill-review-slots.sh directly (bash, no LLM)
   - pantry-review spawn instruction removed from Step 3b
   - VERIFIED: criteria met

3. **Queen context window absorbs zero template content from review prompt composition**
   - fill-review-slots.sh reads skeleton files and writes output files — all disk I/O, no LLM
   - Queen calls the script as a bash command; script exits; Queen reads exit code only
   - No template file content passes through the Queen's context
   - VERIFIED: criteria met

4. **Review prompts produced by the scripts are identical in structure to current Pantry Section 2 output**
   - Script 1 extracts the agent-facing section from nitpicker-skeleton.md and big-head-skeleton.md
     (the same templates Pantry Section 2 used to read and fill)
   - Script 2 appends the same commit range, file list, task IDs, timestamp, report paths
   - Structure matches: review type header, workflow steps, report output path, "Do NOT file beads" note
   - VERIFIED: criteria met (structurally equivalent; content sourced from the same templates)

5. **Script failures surface as error messages to the Queen, not silent failures**
   - Both scripts use `set -euo pipefail`
   - All failure paths: `echo "ERROR: ..." >&2; exit 1`
   - RULES.md Step 3b: "On non-zero exit: surface the script's stderr as an error to the user — do NOT proceed"
   - pantry.md Step 2.5: "On failure (non-zero exit code): ... Report the error to the Queen in this format: REVIEW SKELETON ASSEMBLY FAILED: ..."
   - VERIFIED: criteria met

---

## 5. Build/Test Validation

Both scripts tested manually against real template files:

**compose-review-skeletons.sh — round trip test**:
- Invoked with actual reviews.md, nitpicker-skeleton.md, big-head-skeleton.md
- Produced all 5 skeleton files, all non-empty
- skeleton-clarity.md: {REVIEW_TYPE} resolved to "clarity"; other placeholders converted to {{DOUBLE_BRACE}}
- Exit 0 confirmed

**fill-review-slots.sh — round 1 test**:
- Invoked with: SESSION_DIR, commit range, 3-file list, 2 task IDs, timestamp, round=1
- Produced 4 prompts (clarity/edge-cases/correctness/excellence) + 4 previews + big-head brief
- Slot markers filled correctly: {{COMMIT_RANGE}} → "abc1234..HEAD", {{REVIEW_ROUND}} → "1", etc.
- Return table printed with correct paths
- Exit 0 confirmed

**fill-review-slots.sh — round 2 test**:
- Invoked with round=2
- Produced only 2 prompts (correctness + edge-cases) + 2 previews + big-head brief
- Big Head expected_report_paths contains only 2 entries (correctness, edge-cases)
- Exit 0 confirmed

**Error path tests**:
- Missing arguments: exit 1 + usage message to stderr
- Missing source file: exit 1 + "ERROR: Source file not found" to stderr

---

## 6. Acceptance Criteria Checklist

| # | Criterion | Status |
|---|-----------|--------|
| 1 | Pantry Section 1 invocation produces both implementation prompts AND review skeletons | PASS |
| 2 | No second Pantry invocation is needed for review prompt composition | PASS |
| 3 | Queen context window absorbs zero template content from review prompt composition | PASS |
| 4 | Review prompts produced by the scripts are identical in structure to current Pantry Section 2 output | PASS |
| 5 | Script failures surface as error messages to the Queen, not silent failures | PASS |

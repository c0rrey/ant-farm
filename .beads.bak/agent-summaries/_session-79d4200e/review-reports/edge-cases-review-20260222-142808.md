# Edge Cases Review Report

**Review type**: Edge Cases
**Review round**: 1
**Timestamp**: 20260222-142808
**Reviewer**: edge-cases-reviewer
**Commit range**: 94e350d^..HEAD

---

## Findings Catalog

### EC-01
**File**: `/Users/correy/projects/ant-farm/orchestration/RULES.md:369`
**Severity**: P2
**Category**: Stale reference / incorrect documentation
**Description**: The parenthetical "(see 3b-iii and 3b-ii respectively)" maps `review-skeletons/` to Step 3b-iii and `review-reports/` to Step 3b-ii. The pairing is backwards. `build-review-prompts.sh` (Step 3b-ii) creates `review-reports/` (line 112 of the script). The `mkdir -p "${SESSION_DIR}"/review-reports` command appears in Step 3b-iii — that's the second creation point for `review-reports/`, not for `review-skeletons/`. `review-skeletons/` is not created at Step 3b-iii at all.

A reader acting on this note would look for `review-reports/` at Step 3b-ii (correct accident) and `review-skeletons/` at Step 3b-iii (wrong — the `mkdir` there is for `review-reports/`). If someone tries to diagnose why `review-skeletons/` never exists, this note will misdirect them.

**Suggested fix**: Correct the note to: "`review-skeletons/` and `review-reports/` are created lazily during Step 3b (see 3b-ii and 3b-iii respectively)." Or, since `review-skeletons/` no longer exists (see EC-02), remove its mention entirely.

---

### EC-02
**File**: `/Users/correy/projects/ant-farm/orchestration/RULES.md:382`
**Severity**: P2
**Category**: Reference to non-existent artifact / dead directory
**Description**: The session directory listing includes `review-skeletons/` as a valid subdirectory: "review skeleton files written by `compose-review-skeletons.sh` (created at Step 3b-ii, not at Step 0)". Both the directory and the script are now gone. `compose-review-skeletons.sh` does not exist in `scripts/`. The replacement script, `build-review-prompts.sh`, does not create a `review-skeletons/` subdirectory — it writes directly to `prompts/` and `review-reports/`. Any operator or agent consulting this listing will expect a directory that never appears, and may interpret its absence as an error.

**Suggested fix**: Remove the `review-skeletons/` entry from the session directory listing and update the directory count (from 7 to 6).

---

### EC-03
**File**: `/Users/correy/projects/ant-farm/CONTRIBUTING.md:145-157`
**Severity**: P2
**Category**: Reference to non-existent scripts
**Description**: The "Script validation" section under "Testing Changes" provides example commands for two scripts that no longer exist: `./scripts/compose-review-skeletons.sh` and `./scripts/fill-review-slots.sh`. These were replaced by `build-review-prompts.sh`. A contributor following these instructions will get a "No such file or directory" error. Because this is in the "Testing Changes" section, it may cause a contributor to believe their environment is broken rather than that the documentation is stale.

```
# Test compose-review-skeletons.sh (Script 1):
./scripts/compose-review-skeletons.sh <SESSION_DIR> \
  ~/.claude/orchestration/templates/reviews.md \
  ...

# Test fill-review-slots.sh (Script 2):
./scripts/fill-review-slots.sh <SESSION_DIR> \
  "abc1234..HEAD" "file1.py\nfile2.py" "task-1 task-2" \
  ...
```

**Suggested fix**: Replace both example command blocks with the correct invocation of `build-review-prompts.sh`, matching the signature documented in RULES.md Step 3b-ii.

---

### EC-04
**File**: `/Users/correy/projects/ant-farm/CONTRIBUTING.md:94-97`
**Severity**: P2
**Category**: Reference to non-existent scripts in Template Inventory table
**Description**: The Template Inventory table lists `reviews.md` and the two skeleton files with "`compose-review-skeletons.sh`" as their reader. That script is gone. A contributor using this table to understand the template pipeline will trace a non-existent path.

```
| `reviews.md` | Pantry (review mode), `compose-review-skeletons.sh` | Review protocol, report format |
| `nitpicker-skeleton.md` | Queen, `compose-review-skeletons.sh` | Review agent spawn template |
| `big-head-skeleton.md` | Queen, `compose-review-skeletons.sh` | Consolidation agent spawn template |
```

**Suggested fix**: Replace `compose-review-skeletons.sh` with `build-review-prompts.sh` (or "Queen, `build-review-prompts.sh`") in all three rows.

---

### EC-05
**File**: `/Users/correy/projects/ant-farm/CONTRIBUTING.md:114-115`
**Severity**: P2
**Category**: Reference to non-existent script in "What to watch when editing templates"
**Description**: Two watchout items reference `compose-review-skeletons.sh` as the consumer of `reviews.md`, `nitpicker-skeleton.md`, and `big-head-skeleton.md`. The instructions tell contributors to "verify the script still parses them correctly" after edits, but the script does not exist.

```
- **`reviews.md`** defines review types and report format. Changes here must stay in sync with `compose-review-skeletons.sh` ...
- **`nitpicker-skeleton.md`** and **`big-head-skeleton.md`** are read by `compose-review-skeletons.sh` to produce skeleton files. ...
```

**Suggested fix**: Replace `compose-review-skeletons.sh` with `build-review-prompts.sh` in both bullet points.

---

### EC-06
**File**: `/Users/correy/projects/ant-farm/CONTRIBUTING.md:138`
**Severity**: P2
**Category**: Reference to non-existent directory in test verification step
**Description**: The manual validation step instructs contributors to verify: "Changed `reviews.md`? Verify the review skeletons in `{SESSION_DIR}/review-skeletons/` contain the expected content." The `review-skeletons/` directory is no longer created by the current pipeline. A contributor following this instruction will look for a directory that does not exist and may incorrectly conclude the test failed.

**Suggested fix**: Update to reflect what `build-review-prompts.sh` actually produces: verify the review prompts in `{SESSION_DIR}/prompts/` and previews in `{SESSION_DIR}/previews/`.

---

### EC-07
**File**: `/Users/correy/projects/ant-farm/CONTRIBUTING.md:170`
**Severity**: P2
**Category**: Syncing documentation references non-existent scripts
**Description**: The "What gets synced" section lists what `sync-to-claude.sh` copies, including: "`scripts/compose-review-skeletons.sh` and `scripts/fill-review-slots.sh` to `~/.claude/orchestration/scripts/`". These scripts don't exist and therefore cannot be synced. If `sync-to-claude.sh` attempts to copy them by name (cp not rsync with a glob), it may fail silently or with an error, depending on implementation. More critically, a user reading this thinks these scripts should be present at `~/.claude/orchestration/scripts/` — but they will not be.

**Suggested fix**: Replace with `scripts/build-review-prompts.sh` as the script that gets synced.

---

### EC-08
**File**: `/Users/correy/projects/ant-farm/CONTRIBUTING.md:219-231`
**Severity**: P2
**Category**: Cross-file dependency table references non-existent scripts
**Description**: The "reviews.md dependencies" and "Skeleton template dependencies" tables reference `compose-review-skeletons.sh` and `fill-review-slots.sh` in three rows:

```
| Review types or report format | `compose-review-skeletons.sh` (reads reviews.md to build skeletons) |
| `nitpicker-skeleton.md` structure | `compose-review-skeletons.sh` (parses this file) |
| `big-head-skeleton.md` structure | `compose-review-skeletons.sh` (parses this file) |
| Slot marker names (`{{...}}`) | `fill-review-slots.sh` (fills the markers) |
```

A contributor updating a skeleton or reviews.md would follow these cross-file dependency instructions and test against scripts that do not exist.

**Suggested fix**: Update all four rows to reference `build-review-prompts.sh`.

---

### EC-09
**File**: `/Users/correy/projects/ant-farm/orchestration/PLACEHOLDER_CONVENTIONS.md:14`
**Severity**: P3
**Category**: Stale script name in overview table
**Description**: The Tier 4 row lists "`fill-review-slots.sh`" as the script that fills `{{UPPERCASE}}` slots. The actual script is now `build-review-prompts.sh`.

```
| `{{UPPERCASE}}` | Review slot markers | `fill-review-slots.sh` | When shell script composes review prompts | ...
```

This is documentation for placeholder conventions, so a downstream failure from this stale reference is unlikely — but a contributor validating compliance would run the wrong script name.

**Suggested fix**: Replace `fill-review-slots.sh` with `build-review-prompts.sh` in the Tier 4 row.

---

### EC-10
**File**: `/Users/correy/projects/ant-farm/orchestration/PLACEHOLDER_CONVENTIONS.md:102-130`
**Severity**: P3
**Category**: Stale script name throughout Tier 4 section
**Description**: The Tier 4 section refers to `fill-review-slots.sh` in 5 places (lines 102, 108, 123, 129, and the code example). The code example shows `sed -i "s/{{REVIEW_ROUND}}/$REVIEW_ROUND/g" "$BRIEF_PATH"` with a comment saying this is what `fill-review-slots.sh` does — but this logic is now in `build-review-prompts.sh`.

**Suggested fix**: Update all 5 occurrences of `fill-review-slots.sh` in this section to `build-review-prompts.sh`. The code example comment and description should attribute the substitution to the correct script.

---

### EC-11
**File**: `/Users/correy/projects/ant-farm/orchestration/PLACEHOLDER_CONVENTIONS.md:197`
**Severity**: P3
**Category**: Stale script name in validation rules
**Description**: Pattern 5 description says: "These should only appear in review skeleton templates ... and are substituted exclusively by `fill-review-slots.sh` before prompt delivery." The actual script performing substitution is `build-review-prompts.sh`.

**Suggested fix**: Replace `fill-review-slots.sh` with `build-review-prompts.sh` in this pattern description.

---

### EC-12
**File**: `/Users/correy/projects/ant-farm/orchestration/PLACEHOLDER_CONVENTIONS.md:234` and `:244`
**Severity**: P3
**Category**: Stale script name in compliance summary
**Description**: The compliance summary in "Key Findings" (item 6) and "Why No Changes Needed" both attribute `{{REVIEW_ROUND}}` substitution to `fill-review-slots.sh`. This creates an accurate-seeming but wrong mental model for anyone auditing the system.

**Suggested fix**: Replace `fill-review-slots.sh` with `build-review-prompts.sh` at both locations.

---

### EC-13
**File**: `/Users/correy/projects/ant-farm/CONTRIBUTING.md:103`
**Severity**: P3
**Category**: Stale description of slot-filling mechanism
**Description**: The "Placeholder conventions" explanation says: "Review skeletons use `{{SLOT_NAME}}` (double braces) for values filled by `fill-review-slots.sh`." This is now incorrect — the filler is `build-review-prompts.sh`.

**Suggested fix**: Replace `fill-review-slots.sh` with `build-review-prompts.sh`.

---

### EC-14
**File**: `/Users/correy/projects/ant-farm/orchestration/RULES.md:376`
**Severity**: P3
**Category**: Stale directory count
**Description**: The session directory listing header says "7 subdirectories total" but `review-skeletons/` no longer exists. The actual count should be 6: `task-metadata/`, `previews/`, `prompts/`, `pc/`, `summaries/`, and `review-reports/`.

**Suggested fix**: Change "7 subdirectories total" to "6 subdirectories total" and remove `review-skeletons/` from the list.

---

## Preliminary Groupings

### Root Cause A: `compose-review-skeletons.sh` + `fill-review-slots.sh` replaced by `build-review-prompts.sh`, but CONTRIBUTING.md and PLACEHOLDER_CONVENTIONS.md not updated

Affects: EC-03, EC-04, EC-05, EC-06, EC-07, EC-08, EC-09, EC-10, EC-11, EC-12, EC-13

These findings all stem from the same underlying cause: the two-script pipeline (`compose-review-skeletons.sh` + `fill-review-slots.sh`) was consolidated into `build-review-prompts.sh`, but `CONTRIBUTING.md` and `PLACEHOLDER_CONVENTIONS.md` still reference the old scripts by name in multiple locations. This was a wide-surface migration that required updates across many files, and CONTRIBUTING.md/PLACEHOLDER_CONVENTIONS.md were partially missed.

### Root Cause B: `review-skeletons/` directory no longer created but still documented

Affects: EC-02, EC-06, EC-14

`build-review-prompts.sh` writes directly to `prompts/` and `review-reports/` — it does not create `review-skeletons/`. The intermediate skeleton files that `compose-review-skeletons.sh` produced no longer exist. RULES.md still lists `review-skeletons/` as a session subdirectory (including in the directory count and creation attribution).

### Root Cause C: Step cross-reference reversal in RULES.md note

Affects: EC-01

The parenthetical in RULES.md line 369 pairs `review-skeletons/` and `review-reports/` with steps 3b-iii and 3b-ii respectively — the reverse of the actual creation order. `review-reports/` is created at 3b-ii (by `build-review-prompts.sh`) and Step 3b-iii's explicit `mkdir -p` is also for `review-reports/`. This is a separate mistake from the stale directory reference.

---

## Summary Statistics

| Severity | Count |
|----------|-------|
| P1 | 0 |
| P2 | 8 |
| P3 | 6 |
| **Total** | **14** |

**Verdict**: PASS WITH ISSUES

The changes in this commit range are technically correct (RULES.md, checkpoints.md, GLOSSARY.md, SETUP.md, README.md, CLAUDE.md all received valid updates). The issues found are documentation staleness that was present before this commit range — specifically, CONTRIBUTING.md and PLACEHOLDER_CONVENTIONS.md were updated in this session to add new content (Tier 4 placeholder doc, TeamCreate constraint) but still contain extensive references to the now-deleted `compose-review-skeletons.sh` and `fill-review-slots.sh` scripts, and to the `review-skeletons/` directory that no longer exists. These are pre-existing but now more prominent because the new docs added in this session sit alongside the stale content.

No P1 issues found. The P2 findings represent incorrect instructions that a contributor would follow and fail, which is functionally misleading (wrong commands, wrong paths, wrong scripts), but they don't corrupt the runtime behavior of the orchestration system.

---

## Cross-Review Messages

None sent or received.

---

## Coverage Log

| File | Status | Notes |
|------|--------|-------|
| `CLAUDE.md` | Reviewed — no issues | Updated "Landing the Plane" section to add Steps 4-5 (documentation update and cross-reference verification). Changes are correct and internally consistent with RULES.md Step 4-6. No edge case concerns. |
| `CONTRIBUTING.md` | Issues found | EC-03, EC-04, EC-05, EC-06, EC-07, EC-08, EC-13 — stale script and directory references from pipeline replacement that was not propagated to this file. |
| `README.md` | Reviewed — no issues | Updated architecture diagram and DMVDC+CCB section to reflect Pest Control inside Nitpicker team. Flow diagram is consistent with RULES.md Step 3b-iv. No edge case concerns. |
| `orchestration/GLOSSARY.md` | Reviewed — no issues | Updated checkpoint count from 4 to 5 (SSV added) in definition, hard gate definition, CCO/CCB rows, and Pest Control role description. All four updates are consistent with each other and with checkpoints.md. |
| `orchestration/PLACEHOLDER_CONVENTIONS.md` | Issues found | EC-09, EC-10, EC-11, EC-12 — new Tier 4 section correctly documents the double-brace convention but attributes slot-filling to the now-deleted `fill-review-slots.sh` throughout, rather than to `build-review-prompts.sh`. |
| `orchestration/RULES.md` | Issues found | EC-01, EC-02, EC-14 — stale `review-skeletons/` directory listing and reversed step cross-reference in Session Directory section. Other changes (TeamCreate constraint, SSV model assignment, Step 4/5/6 expansion, session directory listing cleanup) are correct and well-formed. |
| `orchestration/SETUP.md` | Reviewed — no issues | Path fix for `SESSION_PLAN_TEMPLATE.md` cp commands (added `templates/` to path). Both occurrences updated. `docs/installation-guide.md` reference is valid (file exists). No edge case concerns. |
| `orchestration/templates/checkpoints.md` | Reviewed — no issues | Artifact naming section updated: Dirt Pusher CCO moved from task-specific to session-wide, historical naming note added, DMVDC Nitpicker artifact path corrected (`-dmvdc-` not `-dmvdc-review-`). TASK_SUFFIX description for Nitpicker DMVDC updated from abbreviated form (`review-clarity`, `review-edge`) to full form (`review-correctness`, `review-edge-cases`). All changes are internally consistent. No edge case concerns. |

---

## Overall Assessment

**Score**: 7/10

**Verdict**: PASS WITH ISSUES

The changes in this commit range are functionally correct — checkpoint, workflow, and structural documentation updates are accurate. The edge case concerns are documentation drift: `CONTRIBUTING.md` and `PLACEHOLDER_CONVENTIONS.md` still reference `compose-review-skeletons.sh`, `fill-review-slots.sh`, and `review-skeletons/` which no longer exist. A contributor following CONTRIBUTING.md's "Testing Changes" section would run commands that fail. The RULES.md session directory listing includes a subdirectory that is never created, with a step cross-reference that is reversed. These are meaningful P2 issues for a documentation-heavy orchestration framework where contributors rely on accurate instructions to test and extend the system.

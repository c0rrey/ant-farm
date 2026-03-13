# Task Summary: ant-farm-m5lg

**Task**: fix: review-skeletons/ and review-reports/ missing from Step 0 session directory setup
**Status**: Complete
**File changed**: `orchestration/RULES.md`

---

## 1. Approaches Considered

### Approach A: Add two bullet entries to the artifact list only
Add `review-skeletons/` and `review-reports/` as bullets in the "All session-scoped artifacts go here" list with a parenthetical noting lazy creation. Simple, but the existing list was only covering root-level files, not subdirectories — mixing the two in a flat list would be confusing.

### Approach B: Add a footnote below the mkdir command only
Add a note below the `mkdir -p` command explaining that review dirs are created lazily. Informs readers about timing but does not enumerate the review subdirectories anywhere, so the Session Directory section still lacks a complete directory inventory.

### Approach C: Update the mkdir command to include all 7 dirs
Change the `mkdir -p` command to add `review-skeletons` and `review-reports` to the brace expansion. Would mean they are eagerly created at Step 0, contradicting the actual behavior (they are lazy) and potentially confusing recovery workflows.

### Approach D: Add lazy-creation note near mkdir + separate subdirectory list with lazy markers (selected)
Add a note below the `mkdir -p` command explaining the lazy dirs, then restructure the artifact documentation to list all 7 subdirectories explicitly (with lazy creation noted for the 2 review dirs), followed by root-level file artifacts in a separate labeled group. This gives the most complete and accurate picture.

---

## 2. Selected Approach with Rationale

**Approach D** was selected because it satisfies all 3 acceptance criteria in a single coherent edit:
- Enumerates all 7 subdirectories
- Marks the 2 review dirs as lazy-created with step references
- The crash recovery note near the mkdir command informs readers that some dirs may not exist during recovery

---

## 3. Implementation Description

Two edits to `orchestration/RULES.md` (Session Directory section):

**Edit 1**: Added a note after the `mkdir -p` command:
```
Note: `review-skeletons/` and `review-reports/` are created lazily during Step 3b (see 3b-iii and 3b-ii respectively) — they do not exist until reviews run.
```

**Edit 2**: Restructured the artifact documentation block. The old block was a flat list of root-level files with no mention of subdirectories. The new block:
- Opens with "(7 subdirectories total; `review-skeletons/` and `review-reports/` are lazy-created)" in the header line
- Lists all 7 subdirectories with descriptions and lazy-creation notes for `review-skeletons/` and `review-reports/`
- Separates root-level files under "Root-level artifacts in `${SESSION_DIR}`"

This structure matches what actually exists in session directories as verified by checking the `_session-068ecc83` session (which ran full reviews) for the presence of both `review-skeletons/` and `review-reports/`.

---

## 4. Correctness Review

**File: `orchestration/RULES.md`**

- Line 353: Note explains lazy creation with correct step references (3b-iii creates `review-reports/` via `mkdir -p`; 3b-ii is where `compose-review-skeletons.sh` writes to `review-skeletons/`).
- Lines 360-367: All 7 subdirectories listed: `task-metadata/`, `previews/`, `prompts/`, `pc/`, `summaries/`, `review-skeletons/`, `review-reports/`.
- Lines 370-374: Root-level artifacts unchanged from previous task fix (9iyp).
- No other section of RULES.md was touched.
- Crash recovery section (lines 376-379) is unchanged; it only references `progress.log` and `resume-plan.md`, which are root-level files unaffected by review dir existence.

**Assumptions audit**:
- Assumed `compose-review-skeletons.sh` writes to `review-skeletons/` (confirmed: `_session-068ecc83/review-skeletons/` contains skeleton files).
- Assumed `review-reports/` is created at Step 3b-iii via `mkdir -p` (confirmed by RULES.md line 190: `mkdir -p "${SESSION_DIR}"/review-reports`).
- Confirmed all 5 pre-Step-0-created subdirectories match the `mkdir -p` command: `task-metadata`, `previews`, `prompts`, `pc`, `summaries`.

---

## 5. Build/Test Validation

No build artifacts affected. Documentation-only change. Manual verification:
- Confirmed `review-skeletons/` exists in `_session-068ecc83` (session that ran reviews).
- Confirmed `review-reports/` exists in `_session-068ecc83`.
- Confirmed neither directory exists in `_session-e76a488f` (session without reviews) — consistent with lazy creation.

---

## 6. Acceptance Criteria Checklist

1. **RULES.md Session Directory section documents all 7 subdirectories** — PASS. Lines 361-367 list all 7 with descriptions.
2. **Note clarifies lazy creation** — PASS. Both the note on line 353 and the entries on lines 366-367 specify "(created at Step 3b, not at Step 0)".
3. **Crash recovery documentation accounts for directories that may not yet exist** — PASS. The lazy-creation note on line 353 informs readers that review dirs may be absent, and the crash recovery section operates only on root-level files (`progress.log`, `resume-plan.md`) which are always present when relevant.

---

**Commit hash**: (recorded after commit)

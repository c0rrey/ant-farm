# Report: Correctness Review

**Scope**: orchestration/_archive/pantry-review.md, orchestration/SETUP.md, orchestration/templates/pantry.md, orchestration/templates/reviews.md, orchestration/templates/scout.md, README.md, scripts/compose-review-skeletons.sh, scripts/parse-progress-log.sh
**Reviewer**: Correctness Review / nitpicker (correctness specialization)
**Commit range**: dee544d~1..HEAD (3 commits)

---

## Findings Catalog

### Finding 1: Commit message undercounts changed surfaces (ant-farm-6jxn)

- **File(s)**: README.md (commit `dee544d` message)
- **Severity**: P3
- **Category**: correctness
- **Description**: The commit message for `dee544d` reads "update stale pantry-review references across **4** documentation surfaces (ant-farm-6jxn)" but the diff touches 5 change sites across 4 files: `reviews.md:1` (reader comment), `reviews.md:518` (CONSTRAINT comment rename), `README.md:201-215` (architecture diagram), `pantry.md:251` (heading rename), and `_archive/pantry-review.md:2-3` (YAML frontmatter). The bead title itself says "5 surfaces". The commit message number and bead title disagree. This does not affect functionality but creates a traceability inconsistency between the bead and the commit message. The count is wrong either in the message ("4") or in the bead title ("5").
- **Suggested fix**: If the intent was "4 files" (not surfaces), the message could read "across 4 files" or simply "across multiple documentation surfaces." No code change needed; the inconsistency is in the commit message only and cannot be retroactively fixed without rewriting git history.

---

### Finding 2: ant-farm-oc9v acceptance criterion "GLOSSARY.md and README.md updated" is ambiguously met

- **File(s)**: orchestration/GLOSSARY.md, README.md
- **Severity**: P3
- **Category**: correctness
- **Description**: The ant-farm-oc9v acceptance criteria include "GLOSSARY.md and README.md updated." The commit for `ant-farm-oc9v` (`823054a`) only touched `orchestration/templates/scout.md`. Neither `GLOSSARY.md` nor `README.md` was modified in that commit. However, inspection of the pre-existing state (before `dee544d~1`) shows that `GLOSSARY.md:28,81` already carried `~~pantry-review.md~~` (deprecated) strikethrough markers, and `README.md:309` already carried `~~...~~ **DEPRECATED**` language. Those surfaces were addressed in a prior session (before the current commit range). The acceptance criterion references work that was already done. This means the criterion was satisfied before this session's commits began — the oc9v bead was closed with a criterion that was implicitly pre-satisfied, not by any commit in this range. Criterion satisfaction cannot be traced to a commit in the claimed range, which may confuse future reviewers.
- **Suggested fix**: No code change needed. For future bead creation, acceptance criteria should reference only work the implementing commit must perform. Pre-existing satisfactions should be noted as "already satisfied" rather than listed as active criteria.

---

### Finding 3: ant-farm-oc9v bead description cites stale line numbers for README.md

- **File(s)**: README.md (referenced in bead description, not in code)
- **Severity**: P3
- **Category**: correctness
- **Description**: The bead description for `ant-farm-oc9v` cites "README.md:275 -- lists pantry-review as active agent." Inspection of `git show dee544d~1:README.md` shows line 275 is the hard-gates table (DMVDC row), which contains no `pantry-review` reference. The `pantry-review` row in README.md is at line 309, not 275. The bead was created with stale line numbers. The surface was already properly marked deprecated at line 309 prior to any commits in this range. This does not block any work — the criterion is satisfied — but the bead description was inaccurate when filed.
- **Suggested fix**: No code change possible (bead metadata). When filing beads, verify line numbers against current HEAD rather than prior review round artifacts.

---

### Finding 4: compose-review-skeletons.sh docstring says "first line" but awk skips ALL `---` delimiters

- **File(s)**: scripts/compose-review-skeletons.sh:69-78
- **Severity**: P3
- **Category**: correctness
- **Description**: The updated docstring for `extract_agent_section` reads: "Prints all lines after the first line containing only `---` (the delimiter line itself is excluded)." The awk pattern is `'/^---$/{count++; next} count>=1{print}'`. This pattern increments `count` on *every* `---` line it encounters. After the first `---`, `count=1` and printing begins. A second `---` line (if present) would also match, increment count to 2, and be excluded from output (due to `next`). The behavior is therefore: skip ALL bare `---` lines, not just the first. The docstring's phrase "the first line" is technically imprecise — it implies other `---` lines would be printed, which is false. Currently both `nitpicker-skeleton.md` and `big-head-skeleton.md` contain exactly one `---` delimiter, so the behavior matches the intent. But if a skeleton ever gains a second `---` (e.g., YAML frontmatter), both would be silently skipped, and the docstring would actively mislead the next maintainer. The comment was added in this commit and the imprecision was introduced by the change itself.
- **Suggested fix**: Change the docstring to: "Prints all lines after the first `---`-only delimiter line. Any subsequent bare `---` lines are also excluded from output (awk increments count on each match; count>=1 triggers printing while `next` still skips the matching line itself). Skeleton files are expected to contain exactly one such delimiter."

---

## Preliminary Groupings

### Group A: Bead metadata / traceability inconsistencies (Findings 1, 2, 3)

- Findings 1, 2, and 3 all stem from the same root cause: bead metadata (descriptions, acceptance criteria, line numbers) was not updated or validated against the actual code state before the session commenced. Finding 1 is a commit message vs bead title mismatch; Findings 2 and 3 are acceptance criteria and line numbers that reference stale state.
- **Suggested combined fix**: No code changes needed for any of these. Future process improvement: before closing a bead, verify that all acceptance criteria cite work actually done in the current commit range, and that referenced line numbers are accurate.

### Group B: Docstring precision after comment update (Finding 4)

- Finding 4 is standalone: a newly-added comment introduced an inaccuracy about awk behavior.
- **Suggested combined fix**: Update the docstring to accurately describe what all `---` lines (not just the first) are handled identically.

---

## Summary Statistics

- **Total findings**: 4
- **By severity**: P1: 0, P2: 0, P3: 4
- **Preliminary groups**: 2

---

## Cross-Review Messages

### Sent

- To edge-cases-reviewer: "The docstring inaccuracy in scripts/compose-review-skeletons.sh:69-78 could be a boundary/behavior gap if skeleton files ever gain a second `---` delimiter (YAML frontmatter). Worth a look from your angle for the hypothetical multi-delimiter case."

### Received

None received at time of report writing.

### Deferred Items

- Findings 1, 2, 3 (bead metadata inaccuracies): These are process/traceability issues, not code correctness issues. Deferring as P3 to the preliminary grouping. No code change is possible for commit messages or closed bead descriptions.

---

## Coverage Log

| File | Status | Evidence |
|------|--------|----------|
| `orchestration/_archive/pantry-review.md` | Reviewed — 0 code issues | YAML frontmatter `status: archived` added, `description` prefixed with `[ARCHIVED]`. Content is correct and consistent with deprecation. |
| `orchestration/SETUP.md` | Reviewed — 0 code issues | Code fence nesting fixed from 3-backtick to 4-backtick to correctly contain inner 3-backtick fences. Change is logically correct for Markdown rendering. |
| `orchestration/templates/pantry.md` | Reviewed — 0 code issues | Section 2 heading updated to `[DEPRECATED — replaced by fill-review-slots.sh]`. Consistent with body text. |
| `orchestration/templates/reviews.md` | Reviewed — 0 code issues | Reader comment updated at line 1; CONSTRAINT comment renamed to "Report count constraint" at line 518. Both changes are accurate. |
| `orchestration/templates/scout.md` | Reviewed — 0 code issues | `pantry-review` removed from the Dirt Pusher exclusion list. Correct: `pantry-review` is no longer a registered agent type. |
| `README.md` | Reviewed — 0 code issues | Architecture diagram updated to reflect `fill-review-slots.sh` replacing pantry (review mode). Updated labels and flow arrows are accurate. |
| `scripts/compose-review-skeletons.sh` | Findings: #4 | `extract_agent_section` docstring updated in this commit but contains a precision issue re: "first line" vs all `---` lines being skipped by awk. Functional behavior is correct for current single-delimiter templates. |
| `scripts/parse-progress-log.sh` | Reviewed — 0 code issues | Two comment updates: (1) added NOTE about SESSION_COMPLETE ordering in the log parsing loop, and (2) shortened "during normal execution" to "This branch can never be reached." Both are accurate. The SESSION_COMPLETE ordering note is factually correct — the early-exit guard at line 187 is authoritative regardless of log line position. |

---

## Overall Assessment

**Score**: 8.5/10
**Verdict**: PASS WITH ISSUES

All functional changes are correct. The pantry-review deprecation is consistently propagated across the 4 files in `dee544d`, the scout.md exclusion list correctly removes `pantry-review` in `823054a`, and the n0or polish changes (code fence nesting, docstring expansion, comment precision) are logically sound. Four P3 findings were identified, all of which are metadata/documentation precision issues rather than logic errors or acceptance criteria failures. The most actionable is Finding 4 (docstring imprecision in compose-review-skeletons.sh), which was introduced by the commit itself and could mislead a future maintainer if skeleton templates gain multiple `---` delimiters.

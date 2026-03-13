# Report: Edge Cases Review

**Scope**: orchestration/GLOSSARY.md, orchestration/RULES.md, orchestration/templates/checkpoints.md, orchestration/templates/queen-state.md, orchestration/templates/reviews.md, orchestration/templates/scribe-skeleton.md, orchestration/templates/SESSION_PLAN_TEMPLATE.md, README.md, scripts/parse-progress-log.sh
**Reviewer**: Edge Cases Review — Nitpicker (sonnet)

---

## Findings Catalog

### Finding 1: ESV prompt omits {OPEN_BEAD_IDS} — empty-list edge case not handled in Check 3

- **File(s)**: `orchestration/templates/checkpoints.md:L781`
- **Severity**: P2
- **Category**: edge-case
- **Description**: ESV Check 3 instructs Pest Control to "Run `bd list --status=open --after={SESSION_START_DATE}` to detect any open beads from this session that are NOT listed in the exec summary." However, the ESV spawn prompt in `RULES.md:L325` passes the open beads as a free-text variable `{IDS}` embedded in the prompt string. If `{OPEN_BEAD_IDS}` is an empty string (no open beads this session), Pest Control receives no guidance that "no beads are expected," and its Check 3 `bd list` call may surface open beads from previous sessions (depending on date scoping) or simply produce no discrepancies. The GUARD block only handles `bd show` failures per bead; there is no guard for the scenario where the exec summary's "Open Issues" section says "None this session." but `bd list` returns results. This is ambiguous: Pest Control has no explicit instruction for how to treat "exec summary says None, bd list returns beads" as either PASS or FAIL.
- **Suggested fix**: In the ESV prompt template (checkpoints.md), add an explicit branch: "If the exec summary's Open Issues section says 'None this session.', then `bd list` returning zero results is PASS. If it returns one or more results, each result must be traced — if any bead was filed after `{SESSION_START_DATE}` and is not listed in the exec summary, FAIL."

---

### Finding 2: ESV Check 2 commit range boundary is inclusive/exclusive ambiguous — double-counting risk

- **File(s)**: `orchestration/templates/checkpoints.md:L765`
- **Severity**: P2
- **Category**: edge-case
- **Description**: ESV Check 2 runs `git log --oneline {SESSION_START_COMMIT}..{SESSION_END_COMMIT}`. The `..` operator in git is exclusive of the left boundary — `SESSION_START_COMMIT` itself is NOT included. If `{SESSION_START_COMMIT}` is the very first commit of the session (i.e., the first implementation commit), it will be silently omitted from Check 2's coverage, and ESV will PASS even if that first commit is unaccounted for in the exec summary. This is a boundary-condition error: Scribe and ESV may both use the same commit range definition and both exclude the first commit, meaning the gap is never caught. The RULES.md Step 5c passes `{RANGE}` to ESV, but does not specify whether the range is `<first-commit>^..<last-commit>` or `<first-commit>..<last-commit>`.
- **Suggested fix**: In checkpoints.md ESV Check 2, specify that the range should be `{SESSION_START_COMMIT}^..{SESSION_END_COMMIT}` (with `^` to include the start commit), OR document explicitly that `{SESSION_START_COMMIT}` is the commit *before* the first session commit so the `..` range is correct. Also update RULES.md Step 5c to specify how `{RANGE}` is constructed.

---

### Finding 3: Scribe skeleton Step 3 — CHANGELOG prepend loses heading if file is empty

- **File(s)**: `orchestration/templates/scribe-skeleton.md:L148`
- **Severity**: P2
- **Category**: edge-case
- **Description**: The Scribe's Step 3 instruction says: "To prepend: read the current contents of `{CHANGELOG_PATH}`, then write a new file with your new entry at the top followed by the existing contents. Preserve the `# Changelog` heading at the top of the file if it exists — your new entry goes after the heading, not before it." If the CHANGELOG does not exist at all (e.g., a freshly forked project with no CHANGELOG.md yet), the Scribe's `Read` call on `{CHANGELOG_PATH}` will return an error or empty content. The instruction says "if it exists" about the heading, but does not address the file-not-exists case. An LLM reading this instruction may attempt to read a nonexistent file, receive an error, and either abort or write to the wrong path. No fallback is described.
- **Suggested fix**: Add: "If `{CHANGELOG_PATH}` does not exist, create it with `# Changelog\n\n` as the initial content, then prepend your entry after the heading." This covers the empty-repo edge case explicitly.

---

### Finding 4: parse-progress-log.sh — malformed log lines with valid timestamp but empty step_key pass the timestamp guard silently

- **File(s)**: `scripts/parse-progress-log.sh:L176`
- **Severity**: P3
- **Category**: edge-case
- **Description**: The log parsing loop reads `IFS='|' read -r timestamp step_key rest`. The first guard is `[ -z "$step_key" ] && continue`, which skips blank step_key. The second guard validates the timestamp format. However, if a log line has a valid timestamp but a step_key that is not in `STEP_KEYS[]` (e.g., a typo like `WAVE_SPWANED` or a future milestone not yet added), the `map_set "completed" "$step_key"` call writes an unrecognized key into the completed map. This does not affect the RESUME_STEP calculation (the loop only checks keys in `STEP_KEYS[]`), but it could cause a misleading "last completed" display in the resume plan if the loop iterates over `$key in "${STEP_KEYS[@]}"` and the unknown key is not found. In practice, `LAST_COMPLETED` is calculated by iterating `STEP_KEYS[]` and checking the completed map — only known keys are checked — so the impact is limited. However, no warning is emitted for unrecognized step_key values, which makes debugging corrupted logs harder.
- **Suggested fix**: After the timestamp check, add a warning when step_key is not in the known set: `echo "WARNING: Unrecognized step key '${step_key}' on line — will be ignored during resume calculation." >&2`. This preserves existing behavior while making silent unknowns visible.

---

### Finding 5: ESV spawn prompt in RULES.md omits SESSION_START_COMMIT and SESSION_END_COMMIT — runtime substitution gap

- **File(s)**: `orchestration/RULES.md:L320`
- **Severity**: P2
- **Category**: edge-case
- **Description**: The ESV spawn prompt in RULES.md Step 5c reads:
  ```
  prompt="ESV checkpoint. Session dir: {SESSION_DIR}. Commit range: {RANGE}.
          Verify exec-summary.md and CHANGELOG.md.
          Read orchestration/templates/checkpoints.md for full instructions."
  ```
  The checkpoints.md ESV template requires three Queen-supplied values: `{SESSION_START_COMMIT}`, `{SESSION_END_COMMIT}`, and `{SESSION_START_DATE}`. The RULES.md spawn prompt only provides `{RANGE}` (a range string) and `{SESSION_DIR}`. Pest Control must extract `SESSION_START_COMMIT`, `SESSION_END_COMMIT`, and `SESSION_START_DATE` from `{RANGE}` and context — but the ESV prompt template in checkpoints.md shows them as distinct fields. There is no explicit mapping: does `{RANGE}` = `SESSION_START_COMMIT..SESSION_END_COMMIT`? What is `SESSION_START_DATE`? If Pest Control reads checkpoints.md and sees three unsubstituted placeholders (`{SESSION_START_COMMIT}`, `{SESSION_END_COMMIT}`, `{SESSION_START_DATE}`), it may not correctly derive these from just `{RANGE}`.
- **Suggested fix**: Expand the RULES.md ESV spawn prompt to include all three values explicitly:
  ```
  prompt="ESV checkpoint. Session dir: {SESSION_DIR}.
          Session start commit: {FIRST_COMMIT}. Session end commit: HEAD.
          Session start date: {SESSION_DATE}.
          Verify exec-summary.md and CHANGELOG.md.
          Read orchestration/templates/checkpoints.md for full instructions."
  ```

---

### Finding 6: Scribe skeleton — no guard for missing or empty summaries/*.md files

- **File(s)**: `orchestration/templates/scribe-skeleton.md:L42`
- **Severity**: P3
- **Category**: edge-case
- **Description**: Step 1 instructs the Scribe to "Read each file" from `{SESSION_DIR}/summaries/*.md`. If no Dirt Pusher wrote a summary doc (e.g., all agents failed DMVDC and were escalated, or the session had zero implementation tasks), the glob expands to nothing and the Scribe receives empty agent summary data. The instruction says "Take notes as you go — you will synthesize them in Step 2," but does not specify what to write in "Work Completed" when no summaries exist. The exec summary template in Step 2 assumes at least some Work Completed bullet points. The fallback instruction "If a section has no content: Write a single line stating 'None this session.'" only applies to structured sections — it may not be clear to the Scribe whether zero agent summaries should result in "None this session." in Work Completed.
- **Suggested fix**: Add explicitly: "If `{SESSION_DIR}/summaries/*.md` is empty (no files match), note that no agent summaries are present and write 'None this session.' in the Work Completed section."

---

### Finding 7: reviews.md Big Head polling script — placeholder check loop uses literal angle-bracket strings, not actual filled paths

- **File(s)**: `orchestration/templates/reviews.md:L531`
- **Severity**: P2
- **Category**: edge-case
- **Description**: The placeholder substitution guard in the Big Head polling script checks paths like `"<session-dir>/review-reports/correctness-review-<timestamp>.md"` for angle brackets. This guard is correct only if `fill-review-slots.sh` substitutes these with real paths before delivering the brief. However, the guard itself uses `case "$_path" in *'<'*|*'>'*|*'{'*|*'}'*)` — if `fill-review-slots.sh` substitutes `{{REVIEW_ROUND}}` (the variable the template comments explicitly say it substitutes) but NOT the file path placeholders (because path substitution uses a different mechanism), the guard will catch the issue and exit. The guard works correctly in the failure case. The risk is the opposite: if the Pantry or fill-review-slots.sh substitutes paths but introduces a new placeholder syntax (e.g., `${SESSION_DIR}` instead of `<session-dir>`), the guard will not detect the problem because `$` and `{` in a shell-expanded string are not caught by the `*'{'*|*'}'*` check — they are expanded by bash before the case match. In that scenario, the unresolved `${SESSION_DIR}` becomes an empty path and `[ -f "" ]` silently fails, causing spurious timeout behavior.
- **Suggested fix**: The guard should also check for empty path strings explicitly: add `[ -z "$_path" ]` as a failure condition alongside the bracket checks, so an empty substitution result is caught and reported rather than silently failing the `-f` test.

---

### Finding 8: RULES.md Step 3b-i — CHANGED_FILES validation strips whitespace but allows single-character values

- **File(s)**: `orchestration/RULES.md:L165`
- **Severity**: P3
- **Category**: edge-case
- **Description**: The CHANGED_FILES validation uses `[[ -z "${CHANGED_FILES//[[:space:]]/}" ]]` to check non-emptiness after stripping whitespace. This correctly rejects all-whitespace inputs. However, a single character (e.g., `.`) would pass the check even though it is not a valid file path. In practice this is unlikely since `git diff --name-only` returns valid paths, but the validation comment says "must be non-empty (at least one changed file)" — a true path check would be more defensive.
- **Suggested fix**: This is genuinely low-risk in practice — `git diff --name-only` output is well-formed. Flag as P3/no-action-required for context only.

---

## Preliminary Groupings

### Group A: ESV Missing Input Specifications (Findings 1, 2, 5)

**Root cause**: The ESV checkpoint (added in this session) was specified with ambiguous or incomplete input definitions. Three distinct gaps share the same underlying issue: the ESV prompt template assumes Queen-supplied inputs (`SESSION_START_COMMIT`, `SESSION_END_COMMIT`, `SESSION_START_DATE`) that are not clearly mapped to what RULES.md Step 5c actually provides; the commit range boundary semantics (`..` vs `^..`) are unspecified; and the "no open beads" scenario is not explicitly handled.

- Finding 1 — Check 3 "Open Issues: None" vs `bd list` result ambiguity
- Finding 2 — Commit range `..` boundary excludes first commit
- Finding 5 — ESV spawn prompt omits `SESSION_START_COMMIT`, `SESSION_END_COMMIT`, `SESSION_START_DATE`

**Suggested combined fix**: Define a precise ESV input specification in RULES.md Step 5c, with explicit field names matching checkpoints.md's template placeholders, and add boundary semantics for the commit range.

---

### Group B: Scribe Skeleton Missing Edge Cases (Findings 3, 6)

**Root cause**: The Scribe skeleton template (new in this session) does not cover two empty-data scenarios: CHANGELOG.md not existing at all, and no agent summaries present. Both leave the Scribe without explicit instruction.

- Finding 3 — CHANGELOG file-not-exists case unaddressed
- Finding 6 — Empty `summaries/*.md` glob unaddressed

**Suggested combined fix**: Add a "missing data" section to the Scribe skeleton covering both cases with explicit fallback behavior.

---

### Group C: Script and Script-Adjacent Defensive Gaps (Findings 4, 7, 8)

**Root cause**: Three defensive gaps in operational scripts and script-like template code (parse-progress-log.sh and the Big Head polling script) where edge inputs either produce no warning or silently fail.

- Finding 4 — parse-progress-log.sh emits no warning for unrecognized step keys
- Finding 7 — Big Head polling script placeholder guard misses empty-string substitution case
- Finding 8 — CHANGED_FILES validation allows non-path single-character values

**Suggested combined fix**: Each is independent; address Finding 7 first (most likely to produce silent failures) then Finding 4.

---

## Summary Statistics
- Total findings: 8
- By severity: P1: 0, P2: 5 (Findings 1, 2, 3, 5, 7), P3: 3 (Findings 4, 6, 8)
- Preliminary groups: 3

---

## Cross-Review Messages

### Sent
- To Correctness: "Logic at orchestration/templates/checkpoints.md:L765 (ESV Check 2 commit range boundary `..` vs `^..`) may not satisfy acceptance criteria for ESV correctness — check if the intended range includes or excludes the first commit. This may be a correctness issue about whether the ESV range definition matches the Scribe's range."

### Received
- (none at time of report)

### Deferred Items
- "ESV Check 2 commit range boundary" — cross-reported to Correctness reviewer since the semantic question of whether the range is intentionally exclusive is also a correctness concern. Not reported here AND there — filing cross-review message only.

---

## Coverage Log

| File | Status | Evidence |
|------|--------|----------|
| `orchestration/GLOSSARY.md` | Reviewed — no issues | 90 lines, 8 term definitions, 3 role tables reviewed; ESV and Scribe entries consistent with checkpoints.md and RULES.md definitions; no missing validation, error handling, or boundary issues found |
| `orchestration/RULES.md` | Findings: #5, #8 | 556 lines examined; all workflow steps read; edge case gaps in ESV spawn prompt (Finding 5) and CHANGED_FILES validation corner (Finding 8) |
| `orchestration/templates/checkpoints.md` | Findings: #1, #2 | 893 lines examined; all 6 checkpoint sections read; ESV section (new, ~166 lines) reviewed for input handling; gaps in Check 3 empty-beads scenario (Finding 1) and commit range boundary (Finding 2) |
| `orchestration/templates/queen-state.md` | Reviewed — no issues | 79 lines, 5 tables, 1 source-of-truth section; Scribe and ESV rows added to Pest Control table and Scribe/ESV section; no edge case gaps found — fields are template placeholders that the Queen fills |
| `orchestration/templates/reviews.md` | Findings: #7 | 1050 lines examined; all sections read; Big Head polling script placeholder guard gap found (Finding 7) |
| `orchestration/templates/scribe-skeleton.md` | Findings: #3, #6 | 171 lines examined; all 4 steps read; two missing-data edge cases found (Findings 3 and 6) |
| `orchestration/templates/SESSION_PLAN_TEMPLATE.md` | Reviewed — no issues | 353 lines examined; template is user-facing planning aid, not operational code; Step 5b/Scribe references updated correctly; no edge case gaps applicable to this file type |
| `README.md` | Reviewed — no issues | 371 lines examined; all workflow descriptions, architecture diagram, and file reference table read; Scribe and ESV additions consistent with RULES.md; no edge case gaps in documentation |
| `scripts/parse-progress-log.sh` | Findings: #4 | 307 lines examined; all three main sections (argument validation, log parsing, resume plan writing) reviewed; unrecognized step key warning gap found (Finding 4); existing SCRIBE_COMPLETE and ESV_PASS entries correctly added and integrated |

---

## Overall Assessment
**Score**: 6.5/10
**Verdict**: PASS WITH ISSUES

Five P2 findings spanning the new ESV checkpoint (ambiguous input specification, commit range boundary, and empty-beads scenario) and the new Scribe skeleton (missing file-not-exists and empty-summaries fallbacks). These are not blocking issues — the system will function in the common case — but they represent gaps that will surface in edge conditions that are realistically encountered (new projects with no CHANGELOG, sessions with no open beads, first commit of a session being the session start). The P3 findings are low-risk in practice. No P1 findings.

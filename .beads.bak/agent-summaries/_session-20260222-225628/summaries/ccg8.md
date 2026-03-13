# Summary: ant-farm-ccg8 — Add repo root commit guard to ESV Check 2

**Commit**: `4021909`
**Files changed**:
- `orchestration/templates/checkpoints.md` (ESV Check 2, L789-L801 range)

---

## 1. Approaches Considered

**Approach A: Inline `|| true` suppression (discard)**
Append `|| true` to the `git log` command so a missing parent never produces a non-zero exit code. Zero structural change. Tradeoff: this swallows the error silently and produces no output when the root commit itself is SESSION_START_COMMIT, giving a false-empty log. The ESV agent would incorrectly pass Check 2 (zero commits to account for) while real session commits existed after the root commit.

**Approach B: `--ancestry-path` with `--reverse` flag (discard)**
Use `git log --ancestry-path --reverse {SESSION_START_COMMIT}..{SESSION_END_COMMIT}` which avoids the `^` parent entirely by relying on reachability from SESSION_START_COMMIT. Tradeoff: `--ancestry-path` filters to only commits that are directly on the ancestry path, which can omit side-branch merges that are also session commits. Semantically incorrect for the general case.

**Approach C: `git rev-list --count {SESSION_START_COMMIT}^ 2>/dev/null` pre-check then branch (considered)**
Run a count check first to determine parent existence, then branch. Functionally equivalent to the selected approach but `git rev-list --count` introduces an unnecessary extra object count when `git rev-parse` with `2>/dev/null` is the standard idiom for parent existence probing. More verbose than needed.

**Approach D: `git rev-parse {SESSION_START_COMMIT}^ 2>/dev/null` guard then branch (selected)**
Run `git rev-parse {SESSION_START_COMMIT}^ 2>/dev/null` as the probe. Exit code 0 means parent exists — use `^..` range as before. Non-zero exit code means root commit — fall back to `..` range with an explanatory note. This is the canonical git idiom for checking parent existence, minimal token cost, and the note ensures the ESV agent and any downstream reviewer understands the one-commit exclusion gap at the range boundary.

---

## 2. Selected Approach with Rationale

Approach D was selected because:
1. `git rev-parse <ref>^ 2>/dev/null` is the standard git idiom for probing parent existence — models trained on git documentation recognize it without ambiguity.
2. The fallback `{SESSION_START_COMMIT}..{SESSION_END_COMMIT}` is the correct git range when no parent exists; it is not a workaround but the proper form.
3. The inline note ("SESSION_START_COMMIT itself is not included in the git log output") documents the known coverage gap so the ESV agent does not misinterpret the fallback as a full-coverage range.
4. The guard is embedded inline within the numbered step, preserving the existing step-list format of Check 2 and requiring no new heading or section.
5. No changes to the non-root-commit path — zero regression risk for the common case.

---

## 3. Implementation Description

**`orchestration/templates/checkpoints.md`** — One change to ESV Check 2 (L789-L801):
- Step 1 of Check 2 replaced with a 3-bullet guard block:
  - Bullet 1: probe command `git rev-parse {SESSION_START_COMMIT}^ 2>/dev/null`
  - Bullet 2 (if-success): use `git log --oneline {SESSION_START_COMMIT}^..{SESSION_END_COMMIT}` with the existing range-boundary note preserved
  - Bullet 3 (if-fail): use `git log --oneline {SESSION_START_COMMIT}..{SESSION_END_COMMIT}` with a note documenting the root-commit exclusion
- Steps 2-4 and the PASS/FAIL conditions are unchanged.

---

## 4. Correctness Review

### orchestration/templates/checkpoints.md

Re-read lines 789-802 post-edit.

- **L789**: `## Check 2: Commit Coverage` — heading unchanged, correct.
- **L791**: `1. Before running the git log range command, guard against a root-commit edge case:` — step 1 correctly introduces the guard; no numbering gap with step 2 following at L796.
- **L792**: `- Run \`git rev-parse {SESSION_START_COMMIT}^ 2>/dev/null\`` — probe command correct. The `^` suffix on the placeholder references the parent commit; `2>/dev/null` redirects stderr so the ESV agent does not see a confusing git error message on failure.
- **L793**: `- **If the command succeeds** (exit code 0): run \`git log --oneline {SESSION_START_COMMIT}^..{SESSION_END_COMMIT}\`` — normal path preserved exactly as it was pre-edit. The `^..` range semantics note is carried through at L794.
- **L795**: `- **If the command fails** (exit code non-zero ...): run \`git log --oneline {SESSION_START_COMMIT}..{SESSION_END_COMMIT}\` instead, and note in your report: ...` — fallback path correct. The `..` form (without `^`) is valid for a root commit and returns all commits reachable from SESSION_END_COMMIT that are not reachable from SESSION_START_COMMIT, which is all commits after the root. The explanatory note is accurate: the root commit itself is not in the output.
- **L796-L798**: Steps 2-4 text unchanged — no regression.
- **L800-L801**: PASS/FAIL conditions unchanged — no regression.

**Adjacent observation (not fixed, out of scope)**: The root-commit fallback range `{SESSION_START_COMMIT}..{SESSION_END_COMMIT}` technically excludes SESSION_START_COMMIT from the output. In the root-commit scenario, SESSION_START_COMMIT was the repo's first commit before the session began, so excluding it is correct — session commits are those after SESSION_START_COMMIT. The note in L795 documents this accurately.

---

## 5. Build/Test Validation

These files are markdown prompt templates — no build system or automated tests exist. Validation performed by:
1. Re-reading the modified lines 789-802 in full after the edit.
2. Confirming the three-bullet guard structure renders correctly in context (no broken markdown, proper indentation under step 1).
3. Confirming steps 2-4 and PASS/FAIL conditions are byte-for-byte identical to pre-edit.

---

## 6. Acceptance Criteria Checklist

| # | Criterion | Status |
|---|-----------|--------|
| 1 | ESV Check 2 handles the case where SESSION_START_COMMIT has no parent | PASS — L791-L795: guard probes for parent existence and branches on exit code |
| 2 | The fallback command still covers the correct commit range | PASS — L795: fallback uses `{SESSION_START_COMMIT}..{SESSION_END_COMMIT}` with note documenting root-commit exclusion |
| 3 | The guard is documented in the check instructions | PASS — guard is inline within Check 2 step 1 with bolded if-success / if-fail conditions |

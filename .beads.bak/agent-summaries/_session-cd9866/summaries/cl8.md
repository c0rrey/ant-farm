# Summary: ant-farm-cl8
**Task**: scrub-pii.sh only matches quoted emails, misses unquoted occurrences

## 1. Approaches Considered

**A. Remove double-quote anchors from all three regex sites (selected)**
- Drop `"..."` wrapping from the `grep -qE` in --check mode, the perl substitution, and the post-scrub verification grep
- PII_PATTERN itself is already email-specific (requires `@` and a TLD), so false-positive risk is low
- Perl substitution becomes `s/PATTERN/ctc/g` (replaces the email address only, preserving surrounding JSON quotes)
- Tradeoff: could theoretically match an email-like string in a non-data field (e.g., in a URL template), but this is an acceptable tradeoff for comprehensive PII protection

**B. Two-pass detection in --check mode: quoted OR unquoted grep**
- Keep the existing quoted check, add a second `grep -qE "$PII_PATTERN"` and OR the results
- Tradeoff: redundant — the unquoted pattern is a strict superset of the quoted one; the quoted check is obsolete once the broader check exists. Would require maintaining two branches.

**C. Use word-boundary anchors (`\b`) in place of quote anchors**
- Pattern becomes `\b[PATTERN]\b` to avoid partial matches within longer tokens
- Tradeoff: standard grep (`-E`) does not support `\b`; would require `-P` (PCRE) which is not universally available on macOS grep (BSD grep). Adds a portability constraint without meaningful benefit since the email pattern itself is already anchored by `@` and TLD.

**D. Optional-quote regex: `"?PATTERN"?`**
- Matches emails optionally surrounded by double quotes
- Tradeoff: `"?` would also match an email at the end of a string that happens to start after a quote character — semantically it matches more than intended. Also the perl substitution would incorrectly consume the optional quote when present, altering JSON structure.

## 2. Selected Approach with Rationale

Approach A: remove double-quote anchors entirely.

- **Correct**: The `PII_PATTERN` variable already constrains matches to valid email-shaped strings. No quote anchors are needed for correctness; they were only narrowing detection incorrectly.
- **Consistent**: All three sites (check grep, perl scrub, verification grep) now use the same quoting-agnostic pattern, so check and scrub are in sync.
- **Preserves JSON structure**: The perl substitution `s/PATTERN/ctc/g` replaces only the email address token. If the email was in `"user@example.com"`, after scrub it becomes `"ctc"` — the surrounding quotes remain. This is correct JSON behavior.
- **Minimal diff**: Four lines changed, no logic restructuring.

## 3. Implementation Description

Three changes to `scripts/scrub-pii.sh`:

1. **L38 (--check mode grep)**: `grep -qE "\"$PII_PATTERN\""` changed to `grep -qE "$PII_PATTERN"` — drops the literal `\"` anchors, matching emails regardless of quoting context.

2. **L50 (perl scrub)**: `s/"(PATTERN)"/"ctc"/g` changed to `s/PATTERN/ctc/g` — removes quote anchors from both the match and the replacement, replacing only the email address itself.

3. **L52-53 (post-scrub verification)**: Both grep calls changed from `'"PATTERN"'` to `'PATTERN'` — post-scrub check now verifies no emails remain in any quoting context.

## 4. Correctness Review

**scripts/scrub-pii.sh**

- L35: `PII_PATTERN` unchanged — still `[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}`
- L38: `grep -qE "$PII_PATTERN"` — matches emails with or without surrounding quotes. PASS for AC1.
- L50: `s/[a-zA-Z0-9._%+\-]+\@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}/ctc/g` — replaces bare email token in any context. Preserves surrounding JSON quotes. PASS for AC2.
- L52: `grep -qE '[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}'` — verifies no emails in any quoting context. PASS for AC2.
- L53: Same pattern in `grep -cE` for count. PASS.

**Acceptance criteria verification**:
- AC1: --check mode at L38 now uses `grep -qE "$PII_PATTERN"` without quote anchors. Detects `"user@example.com"` and `user@example.com` and `(user@example.com)` equally. PASS.
- AC2: Perl scrub at L50 replaces email in any context. Post-scrub verification at L52-53 confirms no emails remain in any context. PASS.

**Assumptions audit**:
- Assumes `PII_PATTERN` is specific enough without quote anchors — validated: the `@` and TLD requirement (`\.[a-zA-Z]{2,}`) make false positives negligible in JSONL issue data.
- Assumes perl is available on the host (pre-existing assumption, no change).
- The scrub replaces email only (not quotes) — verified by test: `{"owner":"user@example.com"}` → `{"owner":"ctc"}`. JSON remains valid.

## 5. Build/Test Validation

Syntax check: `bash -n scripts/scrub-pii.sh` → OK

Functional tests (inline bash):
- Input `{"owner":"user@example.com"}` → `grep -qE "$PII_PATTERN"` → DETECTED: PASS
- Input `{"owner":user@example.com}` (unquoted) → `grep -qE "$PII_PATTERN"` → DETECTED: PASS
- Perl scrub on `{"owner":"user@example.com","note":plain@example.org}` → `{"owner":"ctc","note":ctc}` → no emails remain → PASS

## 6. Acceptance Criteria Checklist

| Criterion | Status |
|---|---|
| AC1: --check mode (L38) detects email addresses regardless of quoting context | PASS |
| AC2: Scrub operation (L50) and post-scrub verification (L52) handle both quoted and unquoted email patterns | PASS |

**Commit**: a958c09

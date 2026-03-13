# Fix Summary: ant-farm-aqlp

## Task
Fix the `sed` regex in `scripts/compose-review-skeletons.sh` that converts `{UPPERCASE}` tokens to `{{UPPERCASE}}` slot markers. Two problems: (1) the regex used `[A-Z][A-Z_]*` which matches 1+ chars, contradicting the comment's claim of "2+ chars"; (2) no canonical slot name list existed to document which tokens were expected to be converted.

## Commit
`dd9204c` — fix: tighten sed regex from * to + and document canonical slot names (ant-farm-aqlp)

## Files Changed
- `scripts/compose-review-skeletons.sh` — two sed substitution blocks modified (one in `write_nitpicker_skeleton`, one in `write_big_head_skeleton`)

## Design Decision
Four approaches were considered:

1. **Minimal regex fix only** — change `*` to `\+` at both sites. Fastest, but `\+` is a GNU sed extension not supported by BSD sed (macOS).
2. **Fix regex + update inline comments** (chosen) — use `sed -E` with ERE `+` quantifier (portable across BSD and GNU sed), and add canonical slot name lists in comments above each sed block.
3. **Define a CANONICAL_SLOTS variable at top of file** — single source of truth, but over-engineered for the scope of this fix.
4. **Replace sed with an explicit per-slot substitution loop** — eliminates pattern matching risk, but significantly out of scope.

Approach 2 was chosen because it satisfies all three acceptance criteria, is portable across macOS and Linux, touches only the two targeted sed blocks, and keeps changes minimal.

## Key Finding During Implementation
`\+` (BRE one-or-more quantifier) is a GNU sed extension and is NOT supported by BSD sed on macOS. Using `\+` caused the regex to silently match nothing — all tokens were left unconverted. The correct portable fix is `sed -E` (extended regular expressions) with a plain `+` quantifier. This was caught during manual testing before committing.

## Acceptance Criteria Verification
1. Regex at both sed sites uses `[A-Z][A-Z_]+` (2+ chars) — PASS. Line 109: `sed -E 's/\{([A-Z][A-Z_]+)\}/{{\1}}/g'`. Line 165: same pattern.
2. A comment listing canonical slot names appears above each sed block — PASS. Lines 106-108 list nitpicker slots; lines 162-164 list Big Head slots.
3. No other lines modified beyond these targeted changes — PASS. Only the two sed blocks were touched; all other file content is unchanged.

## Adjacent Issues Noted (Not Fixed)
- `scripts/parse-progress-log.sh` had unstaged changes at commit time (unrelated to this fix; not touched).
- The `ASSUMPTION` comment above each sed block remains valid but is not enforced programmatically. A future hardening task could consider switching from a pattern-based approach to an explicit per-slot substitution loop.

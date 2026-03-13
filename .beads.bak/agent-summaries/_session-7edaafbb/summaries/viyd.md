# Bug Fix Summary: ant-farm-viyd

## Issue
BSD grep (macOS) does not support `\s` in ERE mode (`-E`). The `PII_FIELD_PATTERN` variable in `scripts/scrub-pii.sh` used `\s` for whitespace matching, which silently failed to match on macOS. This caused post-scrub verification grep calls (lines 49, 65, 70) to always report "no PII found" even when email addresses remained, producing false-clean results.

## Root Cause
`\s` is a GNU grep extension not available in BSD grep. POSIX ERE has no `\s` shorthand; the portable equivalent is `[[:space:]]`.

## Fix Applied
**File**: `scripts/scrub-pii.sh`, line 46

**Before**:
```bash
PII_FIELD_PATTERN='"(owner|created_by)"\s*:\s*"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}"'
```

**After**:
```bash
PII_FIELD_PATTERN='"(owner|created_by)"[[:space:]]*:[[:space:]]*"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}"'
```

The grep calls on lines 49, 65, and 70 all consume `$PII_FIELD_PATTERN` by reference, so fixing the variable fixes all three call sites. The `\s` on line 63 is inside a Perl regex (`perl -i -pe`), where `\s` is fully supported on all platforms — that line was intentionally left unchanged.

## Commit
`d7702eb` — fix: replace grep \s with POSIX [[:space:]] for BSD compatibility (ant-farm-viyd)

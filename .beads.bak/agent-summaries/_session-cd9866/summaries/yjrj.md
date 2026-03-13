# Fix Summary: ant-farm-yjrj

## Issue
`scrub-pii.sh` applied its email regex globally across all content in `issues.jsonl`, meaning any email-like string in any field (titles, descriptions, URLs) would be silently redacted. The fix scopes all regex operations to only the `"owner"` and `"created_by"` JSON field values.

## Files Changed

### scripts/scrub-pii.sh

**`--check` mode grep** (line 38): Changed from bare email pattern `[a-zA-Z0-9._%+\-]+@...` to field-scoped pattern `"(owner|created_by)"\s*:\s*"<email>"` so it only flags PII in the two known PII-bearing fields.

**perl substitution** (line 52): Changed from global replacement `s/email/ctc/g` to a scoped substitution that captures the field prefix as group 1 and closing quote as group 2:
```perl
s/("(?:owner|created_by)"\s*:\s*")[a-zA-Z0-9._%+\-]+\@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}(")/$1ctc$2/g
```
This preserves the field name and surrounding JSON structure while replacing only the email value.

**Post-scrub verification grep** (lines 54-57): Updated to use the same field-scoped pattern, so the warning check is consistent with what was actually scrubbed.

**Pattern variable** (line 35): Renamed from `PII_PATTERN` to `PII_FIELD_PATTERN` and updated to the scoped form for use in `--check` mode.

## Commit
`9843978` — fix: scope PII scrub regex to owner/created_by fields only (ant-farm-yjrj)

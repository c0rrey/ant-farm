# Bug Fix Summary: ant-farm-bhgt

## Issue
`scripts/install-hooks.sh` lines 87-90 installed a pre-commit hook that performed a hard `exit 1` when `scrub-pii.sh` was not found or not executable. This blocked all future commits on any machine where `scrub-pii.sh` had not yet been created, even when `issues.jsonl` was not staged.

## Root Cause
The generated pre-commit hook used an unconditional hard failure (`exit 1`) when `scrub-pii.sh` was missing, with no provision for the script being added later. This is inconsistent with the pre-push hook, which treats a missing `sync-to-claude.sh` as a non-fatal warning.

## Fix Applied
Changed `/Users/correy/projects/ant-farm/scripts/install-hooks.sh` so the generated pre-commit hook replaces `exit 1` with a three-line warning block that:
- Emits `WARNING` (not `ERROR`) on stderr
- Describes the risk (PII may enter git history)
- Provides the remediation step (add the script and re-run install-hooks.sh)
- Allows the commit to proceed via the `else` branch when the script is present

The outer `install-hooks.sh` already had a warning at lines 107-109 for the missing script — the fix makes the generated hook itself consistent with that intent.

## Commit
`6f449b8` — fix: make pre-commit hook warn instead of fail when scrub-pii.sh is missing (ant-farm-bhgt)

## Files Changed
- `scripts/install-hooks.sh` — 8 insertions, 6 deletions (net +2 lines inside heredoc)

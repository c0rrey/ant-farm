# Fix Summary: ant-farm-4bna

## Issue
Pre-commit hook ordering bug — the hook checked for `scrub-pii.sh` existence/executability (lines 74-77) BEFORE the staged-file guard (line 80), causing ALL commits to be blocked whenever the script was absent, even when `issues.jsonl` was not staged.

## Files Changed

### scripts/install-hooks.sh
- Moved the `[[ ! -x "$SCRUB_SCRIPT" ]]` guard inside the `if git diff --cached --name-only | grep -q ...` block so the executable check only fires when `issues.jsonl` is actually staged.

### docs/installation-guide.md (line 47)
- Changed "Skips silently if `scrub-pii.sh` is not found or not executable" to "Blocks the commit with an error if `scrub-pii.sh` is not found or not executable (only when `issues.jsonl` is staged)" to accurately describe the blocking behavior.

## Commit
`04c96f5` — fix: move scrub-pii.sh check inside staged-file guard to prevent blocking all commits (ant-farm-4bna)

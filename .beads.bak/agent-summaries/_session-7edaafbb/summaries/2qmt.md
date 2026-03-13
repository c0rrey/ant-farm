# ant-farm-2qmt — Fix stale TIMED_OUT reference in big-head-skeleton.md

## Summary

Fixed a stale variable reference in `orchestration/templates/big-head-skeleton.md` line 91.

Commit 306a457 (ant-farm-j6jq) renamed the variable `TIMED_OUT` to `REPORTS_FOUND` in `reviews.md`, but the corresponding reference in `big-head-skeleton.md` was not updated, leaving a dangling/inconsistent variable name.

## Change

- **File**: `orchestration/templates/big-head-skeleton.md`
- **Line**: 91
- **Before**: `**On timeout (TIMED_OUT=1)**:`
- **After**: `**On timeout (REPORTS_FOUND=0)**:`

## Commit

`7813b8d` — fix: update stale TIMED_OUT reference to REPORTS_FOUND in big-head-skeleton.md (ant-farm-2qmt)

## Scope

Only `orchestration/templates/big-head-skeleton.md` was modified. No other files were touched.

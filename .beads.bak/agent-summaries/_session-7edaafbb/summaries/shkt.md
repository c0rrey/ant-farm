# Bug Fix Summary: ant-farm-shkt

## Issue
`orchestration/templates/reviews.md` line 502 contains `REVIEW_ROUND={{REVIEW_ROUND}}`. If `fill-review-slots.sh` is bypassed or fails, the unsubstituted `{{REVIEW_ROUND}}` token causes a confusing bash arithmetic error (e.g., when `[ "$REVIEW_ROUND" -eq 1 ]` is evaluated) instead of a clear placeholder-guard error.

## Fix Applied

Added a `case` guard immediately after the `REVIEW_ROUND=` assignment (now lines 503-511) that detects if the value still contains `{` or `}` characters and emits a clear diagnostic error, consistent in style with the existing file-path placeholder guards in the same block.

```bash
REVIEW_ROUND={{REVIEW_ROUND}}
case "$REVIEW_ROUND" in
  *'{'*|*'}'*)
    echo "PLACEHOLDER ERROR: REVIEW_ROUND was not substituted by fill-review-slots.sh (got: $REVIEW_ROUND)"
    echo "This brief was delivered with an unresolved {{REVIEW_ROUND}} placeholder."
    echo "Root cause: fill-review-slots.sh was bypassed or failed during prompt composition."
    echo "Do NOT proceed. Return this error to the Queen immediately."
    exit 1
    ;;
esac
```

## File Changed
- `orchestration/templates/reviews.md` — 9 lines inserted after line 502

## Commit
`8dafdd4` — fix: add placeholder guard for REVIEW_ROUND assignment in reviews.md polling loop (ant-farm-shkt)

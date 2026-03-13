# Fix: Skeleton Template Attribution Update (RC-3)

## Summary

Applied RC-3 (P3) fix: updated stale "Pantry (review mode)" attributions in both skeleton
templates to correctly attribute placeholder-filling to `build-review-prompts.sh`.

## Files Changed

- `orchestration/templates/nitpicker-skeleton.md`
- `orchestration/templates/big-head-skeleton.md`

## Changes Applied

### nitpicker-skeleton.md (lines 11-13)

- Line 11 — DATA_FILE_PATH: "from the Pantry (review mode) verdict table" -> "from build-review-prompts.sh output table"
- Line 12 — REPORT_OUTPUT_PATH: "from the Pantry verdict table" -> "from build-review-prompts.sh output table"
- Line 13 — REVIEW_ROUND: "filled by Pantry" -> "filled by build-review-prompts.sh"

### big-head-skeleton.md (lines 20, 58)

- Line 20 — DATA_FILE_PATH: "Big Head consolidation brief written by the Pantry (review mode)" -> "Big Head consolidation brief written by build-review-prompts.sh"
- Line 58 — "The Pantry writes all report paths" -> "build-review-prompts.sh writes all report paths"

## Commit

`fix: update skeleton template attributions from Pantry to build-review-prompts.sh (RC-3)`

## Verification

Both files re-read after edits. All five targeted strings confirmed replaced. No unintended
changes made. Scope limited strictly to the two skeleton template files as instructed.

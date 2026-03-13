# Summary: ant-farm-purh, ant-farm-yf5p, ant-farm-nq4f

**Commit**: 3bdee83
**File changed**: `orchestration/RULES.md`

## Fix 1 — ant-farm-purh (P2): Correct progress log filename in Step 3b

**Problem**: Step 3b progress log entry referenced `big-head-summary.md` as the consolidated report filename, but the actual file written by the review workflow is `review-consolidated-{timestamp}.md`.

**Change** (line 187):
```
before: report=${SESSION_DIR}/review-reports/big-head-summary.md
after:  report=${SESSION_DIR}/review-reports/review-consolidated-${TIMESTAMP}.md
```

## Fix 2 — ant-farm-yf5p (P2): Clarify TIMESTAMP origin in Step 3b-v

**Problem**: Step 3b-v used `${TIMESTAMP}` in the tmux send-keys command but provided no indication of where that variable was assigned, making the code block appear to reference an undefined variable.

**Change**: Added a comment at the top of the Step 3b-v bash block:
```bash
# TIMESTAMP was assigned at the start of Step 3b-i: TIMESTAMP=$(date +%Y%m%d-%H%M%S)
```

This cross-references Step 3b-i which already documents that the Queen generates ONE timestamp using `date +%Y%m%d-%H%M%S` format at the start of Step 3b.

## Fix 3 — ant-farm-nq4f (P2): Event-named progress log milestones

**Problem**: All 9 progress log entries used generic step-numbered keys (`step0`, `step1`, `step2`, `step3`, `step3b`, `step3c`, `step4`, `step5`, `step6`) with no per-agent granularity, making crash recovery ambiguous.

**Change**: Replaced all step-numbered keys with descriptive event-named milestones:

| Old key  | New key          | Step  |
|----------|------------------|-------|
| step0    | SESSION_INIT     | 0     |
| step1    | SCOUT_COMPLETE   | 1b    |
| step2    | WAVE_SPAWNED     | 2     |
| step3    | WAVE_VERIFIED    | 3     |
| step3b   | REVIEW_COMPLETE  | 3b    |
| step3c   | REVIEW_TRIAGED   | 3c    |
| step4    | DOCS_COMMITTED   | 4     |
| step5    | XREF_VERIFIED    | 5     |
| step6    | SESSION_COMPLETE | 6     |

The `wave=<N>` and `round=<N>` fields on wave/review entries already provide per-iteration granularity; the event names now allow `parse-progress-log.sh` to match milestones by semantic label rather than positional step number.

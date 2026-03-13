# Fix Summary: ant-farm-xybg

## Task
Re-add `pantry-review` to the Scout's orchestration agent exclusion list.

## Root Cause
The ant-farm-oc9v task removed `pantry-review` from the Scout's exclusion list at
`orchestration/templates/scout.md:63`. Because `sync-to-claude.sh` never deletes files
from `~/.claude/agents/`, a stale `pantry-review.md` agent file can persist on disk.
If present, the Scout would see it as a valid Dirt Pusher candidate and recommend it for
task assignment — a silent failure, since `pantry-review` is an orchestration agent that
does not implement tasks.

## Design Approaches Considered

1. **Direct string append (CHOSEN)** — Insert `pantry-review` between `pantry-impl` and
   `pest-control` in the existing comma-separated list on line 63. Minimal diff, preserves
   grouping of pantry agents together, exactly matches the fix brief specification.

2. **Alphabetical reorder** — Re-sort all exclusion agents alphabetically. Cleaner for
   long-term maintenance but changes more of the line than necessary and deviates from the
   fix brief.

3. **Separate pantry group comment** — Add a comment line grouping pantry agents. More
   descriptive but adds lines outside the scope boundary (edit only line 63).

4. **Rewrite exclusions section with structured formatting** — One agent per line, easier
   to read and diff. Improves readability but violates the scope boundary.

**Rationale for chosen approach**: The fix brief explicitly states the before/after text
for line 63. Direct string append satisfies both acceptance criteria with the smallest
possible diff.

## Files Changed

- `orchestration/templates/scout.md` — line 63 only

## Before / After

Before:
```
scout-organizer, pantry-impl, pest-control, nitpicker, big-head
```

After:
```
scout-organizer, pantry-impl, pantry-review, pest-control, nitpicker, big-head
```

## Acceptance Criteria Verification

1. `pantry-review` appears in the exclusion list at scout.md:63 — PASS
2. No other lines in scout.md are modified — PASS

## Assumptions Audit

- Assumed the file content at line 63 matched the "before" state in the fix brief exactly.
  Confirmed by reading the file before editing — the content matched.
- Assumed no concurrent changes to scout.md were in flight. Clean git status at session
  start confirmed this.
- No adjacent issues discovered during review.

## Commit Hash

<!-- To be filled after git commit -->
PENDING — run:
  git pull --rebase
  git add orchestration/templates/scout.md
  git commit -m "fix: re-add pantry-review to Scout exclusion list (ant-farm-xybg)"

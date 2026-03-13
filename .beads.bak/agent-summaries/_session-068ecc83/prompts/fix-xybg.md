# Fix Brief: ant-farm-xybg

## Context
Review finding RC-1 (P2): The ant-farm-oc9v task removed `pantry-review` from the Scout's exclusion list at `orchestration/templates/scout.md:63`. However, `sync-to-claude.sh` never deletes files from `~/.claude/agents/`. If the stale `pantry-review.md` agent file remains on disk, the Scout could recommend it as a Dirt Pusher, producing a silent failure.

## Fix
Re-add `pantry-review` to the exclusion list at `orchestration/templates/scout.md:63`. The current line reads:
```
scout-organizer, pantry-impl, pest-control, nitpicker, big-head
```
It should read:
```
scout-organizer, pantry-impl, pantry-review, pest-control, nitpicker, big-head
```

## Scope Boundaries
- **Edit ONLY**: `orchestration/templates/scout.md:63`
- **Do NOT edit**: Any other file

## Acceptance Criteria
1. `pantry-review` appears in the exclusion list at scout.md:63
2. No other lines in scout.md are modified

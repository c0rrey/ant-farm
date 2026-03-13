# ant-farm-sjyg Summary

## Issue
[BUG] SETUP.md troubleshooting block (lines 210-215) instructed the Queen to run `bd show <id>` directly, contradicting the Scout-delegation discipline enforced in RULES.md and CLAUDE.md.

## Fix
Rewrote line 211 of `orchestration/SETUP.md` to instruct spawning the Scout subagent for task metadata gathering instead of running `bd show` directly as Queen.

### Before
```
1. Gather all task metadata (bd show <id>)
```

### After
```
1. Spawn the Scout subagent to gather all task metadata (do NOT run bd show directly as Queen)
```

## Files Changed
- `orchestration/SETUP.md` — line 211 only

## Commit
`e9cd3dd` — fix: reword troubleshooting to delegate bd show to Scout instead of Queen (ant-farm-sjyg)

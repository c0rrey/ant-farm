# Task: ant-farm-tbis
**Status**: success
**Title**: Stale SESSION_DIR path in 6 files -- agent-summaries not updated to sessions
**Type**: bug
**Priority**: P2
**Epic**: none
**Agent Type**: general-purpose
**Dependencies**: {blocks: [], blockedBy: []}

## Affected Files
- `orchestration/reference/dependency-analysis.md:49-51` — stale SESSION_DIR example
- `orchestration/templates/dirt-pusher-skeleton.md:13` — stale SESSION_DIR example
- `orchestration/templates/scout.md:14` — stale SESSION_DIR example
- `orchestration/templates/scribe-skeleton.md:11` — stale SESSION_DIR example
- `CLAUDE.md:71` — stale session path in cleanup step
- `AGENTS.md:33` — stale session path in cleanup step

## Root Cause
Session artifact directory was renamed from `.crumbs/agent-summaries/_session-*` to `.crumbs/sessions/_session-*` but 6 files still reference the old path. Agents constructing SESSION_DIR from stale examples will write artifacts to a path the workflow does not read from.

## Expected Behavior
All files should reference `.crumbs/sessions/_session-*` consistently.

## Acceptance Criteria
1. `grep -r 'agent-summaries/_session' *.md orchestration/ docs/` returns no matches
2. All 6 files reference `.crumbs/sessions/_session-*` or `_session-<session-id>`
3. `~/.claude/CLAUDE.md` contains the updated path after running setup.sh

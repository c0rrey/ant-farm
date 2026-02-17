# The Queen's Session State
**Updated**: <timestamp>
**Session ID**: <session-id>
**Session dir**: .beads/agent-summaries/_session-<session-id>
**Session start**: <timestamp>
**Strategy**: <chosen execution strategy>

## The Scout
| Status | Briefing Path | Tasks Found | Blocked | Recommended Strategy |
|--------|---------------|-------------|---------|---------------------|
| pending/completed/failed | {path} | {N} | {M} | {name} |

## Agent Registry
| Agent Name | Task IDs | Files Assigned | Status | Commit Hash | Checkpoint B |
|------------|----------|----------------|--------|-------------|--------------|
| <name>     | <ids>    | <files>        | spawned/completed/errored | <hash> | PASS/PENDING/FAIL |

## The Pantry
| Wave | Status | Tasks | Verdict |
|------|--------|-------|---------|
| 1    | pending/completed/failed | <task-ids> | All PASS / <details> |

## Colony TSA
| Wave | Status | Verdict Summary |
|------|--------|-----------------|
| 1    | pending/completed/failed | All PASS / <details> |

## Checkpoint Status
| Checkpoint | Target | Result | Artifact Path |
|------------|--------|--------|---------------|
| C | consolidation | PASS/FAIL | <path> |

## Queue Position
- **Completed**: <N> of <total> tasks
- **In progress**: <list>
- **Remaining**: <list>
- **Retry budget**: <used>/<max 5>

## Error Log
- <timestamp>: <agent> — <error summary>

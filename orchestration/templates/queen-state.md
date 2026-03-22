# The Orchestrator's Session State

> **Timestamp format**: All timestamps in this file use ISO 8601 / RFC 3339: `YYYY-MM-DDTHH:MM:SSZ`
> (e.g., `2026-02-20T14:35:07Z`). Generate via `date -u +%Y-%m-%dT%H:%M:%SZ`.

**Updated**: {YYYY-MM-DDTHH:MM:SSZ}
**Session ID**: {session-id}
**Session dir**: .crumbs/sessions/_session-{session-id}
**Session start**: {YYYY-MM-DDTHH:MM:SSZ}
**Strategy**: {chosen-execution-strategy}

## The Recon Planner
| Status | Briefing Path | Tasks Found | Blocked | Recommended Strategy |
|--------|---------------|-------------|---------|---------------------|
| pending/completed/failed | {path} | {N} | {M} | {name} |

## Agent Registry
| Agent Name | Task IDs | Files Assigned | Status | Commit Hash | claims-vs-code |
|------------|----------|----------------|--------|-------------|----------------|
| {name}     | {ids}    | {files}        | spawned/completed/errored | {hash} | PASS/PENDING/FAIL |

## The Prompt Composer
| Wave | Status | Tasks | Verdict |
|------|--------|-------|---------|
| 1    | pending/completed/failed | {task-ids} | All PASS / {details} |

## Checkpoint Auditor

<!-- One row per RULES.md hard gate. Add rows for each wave (N=1,2,...) and review round (R=1,2,...). -->

| Step | Phase | Checkpoint | Status | Verdict |
|------|-------|------------|--------|---------|
| Step 2 | Wave N impl prompts | pre-spawn-check | pending/completed/failed | All PASS / {details} |
| Step 3 | Wave N per-agent | scope-verify | pending/completed/failed | All PASS / {details} |
| Step 3 | Wave N post | claims-vs-code | pending/completed/failed | All PASS / {details} |
| Step 3b | Round R review prompts | pre-spawn-check | pending/completed/failed | All PASS / {details} |
| Step 3b | Round R review post | claims-vs-code + review-integrity | pending/completed/failed | All PASS / {details} |
| Step 6 | Exec summary | session-complete | pending/completed/failed | PASS / FAIL / {details} |

## Review Rounds
- **Current round**: {1 | 2 | 3 | ...}
- **Max rounds**: 4 (escalate to user if P1/P2 still present after round 4)
- **Escalation cap**: {not triggered | triggered (round 4: X P1, Y P2 — awaiting user decision)}
- **Round 1 commit range**: {first-session-commit}..{last-impl-commit}
- **Fix commit range**: {first-fix-commit}..HEAD (set after fix cycle)
- **Termination**: {pending | terminated (round N: 0 P1/P2)}

## Session Scribe and Session-Complete (Step 5 / 6)
- **Session Scribe status**: {pending | spawned | completed | failed}
- **Session Scribe retry**: {0 | 1} (max 1 retry before escalation)
- **Exec summary path**: {SESSION_DIR}/exec-summary.md (or N/A)
- **Session-complete status**: {pending | spawned | PASS | FAIL}
- **Session-complete artifact**: {SESSION_DIR}/pc/pc-session-session-complete-{timestamp}.md (or N/A)
- **Session-complete escalated**: {no | yes — awaiting user decision}

## Queue Position
- **Completed**: {N} of {total} tasks
- **In progress**: {list}
- **Remaining**: {list}
- **Retry budget**: {used}/{max 5}

## Error Log
- {YYYY-MM-DDTHH:MM:SSZ}: {agent} — {error-summary}

## Source of Truth

When queen-state.md conflicts with other state sources, precedence is:

| State Domain | Authoritative Source | queen-state.md Role |
|--------------|---------------------|---------------------|
| Commits (hashes, ranges, authorship) | `git log` / `git diff` | Cache — refresh from git if stale |
| Artifact content (previews, reports, verdicts) | Artifact files on disk (`${SESSION_DIR}/...`) | Pointer — references paths, does not duplicate content |
| Session workflow state (current step, wave, review round, retry budget, queue position) | **queen-state.md** | Authoritative — this file is the single source of truth |
| Task status (open, closed, blocked) | `crumb` database (via Recon Planner) | Cache — may lag behind crumb; Recon Planner re-syncs on next run |

**Recovery rule**: If queen-state.md is lost or corrupted, rebuild workflow state from git log
(commit messages encode task IDs and step transitions) and artifact files (verdict tables encode
checkpoint pass/fail). Task status must be re-queried via a fresh Recon Planner spawn.

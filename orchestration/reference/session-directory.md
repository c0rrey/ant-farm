# Session Directory

At session start (Step 0), generate a session ID and create the session artifact directory:

    SESSION_ID="$(date +%Y%m%d-%H%M%S)-$(head -c4 /dev/urandom | xxd -p)"
    SESSION_DIR=".crumbs/sessions/_session-${SESSION_ID}"
    mkdir -p "${SESSION_DIR}"/{task-metadata,previews,prompts,pc,summaries,signals}
    crumb prune >/dev/null || true

Note: `review-reports/` is created lazily at Step 3b-iii — it does not exist until reviews run.

Store SESSION_DIR in your context. Pass it explicitly to every agent that needs to write artifacts:
Recon Planner receives it as "Session directory: <SESSION_DIR>".
Prompt Composer receives it as "Session directory: <SESSION_DIR>".
Checkpoint Auditor receives it as "Session directory: <SESSION_DIR>" (when writing checkpoint artifacts).

All session-scoped artifacts go here (7 subdirectories total; `review-reports/` is lazy-created):
- `task-metadata/` — per-task scope files written by Recon Planner
- `previews/` — combined prompt previews written by Prompt Composer
- `prompts/` — full task and review prompt files written by Prompt Composer
- `pc/` — Checkpoint Auditor checkpoint artifact files
- `summaries/` — Implementer summary docs
- `signals/` — sentinel files written by background subagents to signal completion
- `review-reports/` — Reviewer and Review Consolidator reports (created lazily at Step 3b-iii via `mkdir -p`, not at Step 0)

Root-level artifacts in `${SESSION_DIR}`:
- `orchestrator-state.md` — session state for context recovery
- `briefing.md` — written by Recon Planner (Step 1a); strategy summary read by Orchestrator after startup-check PASS before auto-proceeding to Step 2
- `session-summary.md` — written by Prompt Composer (optional); end-of-session narrative summary
- `exec-summary.md` — written by Session Scribe (Step 5); canonical session record covering work completed, review findings, open issues, and narrative observations; source for the CHANGELOG derivative
- `progress.log` — append-only milestone log; one pipe-delimited line per completed step; written by the Orchestrator at each workflow milestone; never read or overwritten during normal operation; recovery sessions read this once to determine the resume point
- `resume-plan.md` — written by `scripts/parse-progress-log.sh` on crash recovery; structured markdown resume plan presented to the user for approval before any action is taken

**Crash recovery script**: `scripts/parse-progress-log.sh <SESSION_DIR>`
- Exit 0: resume-plan.md written; present to user and await `resume` or `fresh start`
- Exit 1: error (missing log, unreadable); surface to user and await instruction
- Exit 2: session already completed (SESSION_COMPLETE logged); no resume-plan written; proceed with fresh start

The `_session-` prefix distinguishes session directories from other entries in `.crumbs/sessions/`.
This prevents collisions when multiple Orchestrators run in the same repo.

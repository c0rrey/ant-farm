# Session Directory

At session start (Step 0), generate a session ID and create the session artifact directory:

    SESSION_ID="$(date +%Y%m%d-%H%M%S)-$(head -c4 /dev/urandom | xxd -p)"
    SESSION_DIR=".crumbs/sessions/_session-${SESSION_ID}"
    mkdir -p "${SESSION_DIR}"/{task-metadata,previews,prompts,pc,summaries,signals}
    crumb prune >/dev/null || true

Note: `review-reports/` is created lazily at Step 3b-iii — it does not exist until reviews run.

Store SESSION_DIR in your context. Pass it explicitly to every agent that needs to write artifacts:
Scout receives it as "Session directory: <SESSION_DIR>".
Pantry receives it as "Session directory: <SESSION_DIR>".
Pest Control receives it as "Session directory: <SESSION_DIR>" (when writing checkpoint artifacts).

All session-scoped artifacts go here (7 subdirectories total; `review-reports/` is lazy-created):
- `task-metadata/` — per-task scope files written by Scout
- `previews/` — combined prompt previews written by Pantry
- `prompts/` — full task and review prompt files written by Pantry
- `pc/` — Pest Control checkpoint artifact files
- `summaries/` — Crumb Gatherer summary docs
- `signals/` — sentinel files written by background subagents to signal completion
- `review-reports/` — Nitpicker and Big Head reports (created lazily at Step 3b-iii via `mkdir -p`, not at Step 0)

Root-level artifacts in `${SESSION_DIR}`:
- `queen-state.md` — session state for context recovery
- `briefing.md` — written by Scout (Step 1a); strategy summary read by Queen after SSV PASS before auto-proceeding to Step 2
- `session-summary.md` — written by Pantry (optional); end-of-session narrative summary
- `exec-summary.md` — written by Scribe (Step 5); canonical session record covering work completed, review findings, open issues, and narrative observations; source for the CHANGELOG derivative
- `progress.log` — append-only milestone log; one pipe-delimited line per completed step; written by the Queen at each workflow milestone; never read or overwritten during normal operation; recovery sessions read this once to determine the resume point
- `resume-plan.md` — written by `scripts/parse-progress-log.sh` on crash recovery; structured markdown resume plan presented to the user for approval before any action is taken

**Crash recovery script**: `scripts/parse-progress-log.sh <SESSION_DIR>`
- Exit 0: resume-plan.md written; present to user and await `resume` or `fresh start`
- Exit 1: error (missing log, unreadable); surface to user and await instruction
- Exit 2: session already completed (SESSION_COMPLETE logged); no resume-plan written; proceed with fresh start

The `_session-` prefix distinguishes session directories from other entries in `.crumbs/sessions/`.
This prevents collisions when multiple Queens run in the same repo.

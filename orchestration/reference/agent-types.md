# Agent Types

| Agent | subagent_type | Rationale |
|-------|---------------|-----------|
| Recon Planner | `ant-farm-recon-planner` | Custom agent: agent-organizer + Bash for crumb CLI |
| Prompt Composer (impl) | `ant-farm-prompt-composer` | Custom agent: pre-spawn-check-aligned implementation prompt composer |
| Checkpoint Auditor | `ant-farm-checkpoint-auditor` | Custom agent: verification auditor, catches fabrication + scope creep |
| Implementers | from Prompt Composer verdict table | Specialist per task — Recon Planner recommends via dynamic agent discovery, Prompt Composer passes through |
| Reviewer — Clarity | `ant-farm-reviewer-clarity` | Custom agent: prose clarity, naming, and readability review |
| Reviewer — Edge Cases | `ant-farm-reviewer-edge-cases` | Custom agent: boundary conditions and untested scenarios review |
| Reviewer — Correctness | `ant-farm-reviewer-correctness` | Custom agent: logic correctness and algorithmic accuracy review |
| Reviewer — Drift | `ant-farm-reviewer-drift` | Custom agent: spec/design drift and requirement alignment review |
| Review Consolidator | `ant-farm-review-consolidator` | Custom agent: deduplication, root-cause grouping, issue filing |
| Session Scribe | `ant-farm-session-scribe` | Reads session artifacts, writes exec summary + CHANGELOG |
| PC — session-complete | `ant-farm-checkpoint-auditor` | Custom agent: mechanical exec-summary verification against session artifacts |

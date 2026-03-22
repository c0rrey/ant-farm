# Model Assignments

Every `Task` tool call the Orchestrator makes MUST include the `model` parameter from this table. Omitting `model` causes the agent to inherit the Orchestrator's opus model, wasting tokens on agents that don't need it.

| Agent | Spawn Method | Model | Notes |
|-------|-------------|-------|-------|
| Recon Planner | Task (`ant-farm-recon-planner`) | opus | Orchestration role |
| Prompt Composer (impl) | Task (`ant-farm-prompt-composer`) | opus | Prompt composition + review skeleton assembly (Script 1) |
| Implementers | Task (dynamic type) | sonnet | All implementers regardless of subagent_type |
| PC — startup-check | Task (`ant-farm-checkpoint-auditor`) | haiku | Set comparisons only — no judgment required |
| PC — pre-spawn-check | Task (`ant-farm-checkpoint-auditor`) | haiku | Mechanical checklist |
| PC — scope-verify | Task (`ant-farm-checkpoint-auditor`) | haiku | Mechanical file comparison |
| PC — claims-vs-code | Task (`ant-farm-checkpoint-auditor`) | sonnet | Judgment: claims vs actual code |
| PC — review-integrity | Task (`ant-farm-checkpoint-auditor`) | sonnet | Judgment: crumb quality and dedup correctness |
| Reviewers — Correctness, Edge Cases | TeamCreate member | opus | Higher-judgment reviews; set in review-consolidator-skeleton.md |
| Reviewers — Clarity, Drift | TeamCreate member | sonnet | Lower-judgment reviews; set in review-consolidator-skeleton.md |
| Review Consolidator | TeamCreate member | opus | Set in review-consolidator-skeleton.md (`{MODEL}`) |
| PC (team member) | TeamCreate member | sonnet | Runs claims-vs-code inside team; needs sonnet |
| Fix Implementers | Task (dynamic type) into team | sonnet | Same model as regular Implementers; spawned with `team_name: "reviewer-team"` |
| fix-pc-scope-verify | Task into team | haiku | Scope verify for fix implementers: lightweight scope check; spawned with `team_name: "reviewer-team"` |
| fix-pc-claims-vs-code | Task into team | sonnet | Claims-vs-code for fix implementers: substance check; spawned with `team_name: "reviewer-team"` |
| Session Scribe | Task (`ant-farm-session-scribe`) | sonnet | Reads session artifacts; writes exec-summary.md + CHANGELOG entry |
| PC — session-complete | Task (`ant-farm-checkpoint-auditor`) | haiku | Mechanical verification — 6 checks, no judgment required |

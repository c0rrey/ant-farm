# Model Assignments

Every `Task` tool call the Queen makes MUST include the `model` parameter from this table. Omitting `model` causes the agent to inherit the Queen's opus model, wasting tokens on agents that don't need it.

| Agent | Spawn Method | Model | Notes |
|-------|-------------|-------|-------|
| Scout | Task (`ant-farm-recon-planner`) | opus | Orchestration role |
| Pantry (impl) | Task (`ant-farm-prompt-composer`) | opus | Prompt composition + review skeleton assembly (Script 1) |
| Crumb Gatherers | Task (dynamic type) | sonnet | All crumb gatherers regardless of subagent_type |
| PC — SSV | Task (`ant-farm-checkpoint-auditor`) | haiku | Set comparisons only — no judgment required |
| PC — CCO | Task (`ant-farm-checkpoint-auditor`) | haiku | Mechanical checklist |
| PC — WWD | Task (`ant-farm-checkpoint-auditor`) | haiku | Mechanical file comparison |
| PC — CMVCC | Task (`ant-farm-checkpoint-auditor`) | sonnet | Judgment: claims vs actual code |
| PC — CCB | Task (`ant-farm-checkpoint-auditor`) | sonnet | Judgment: crumb quality and dedup correctness |
| Reviewers — Correctness, Edge Cases | TeamCreate member | opus | Higher-judgment reviews; set in review-consolidator-skeleton.md |
| Reviewers — Clarity, Drift | TeamCreate member | sonnet | Lower-judgment reviews; set in review-consolidator-skeleton.md |
| Review Consolidator | TeamCreate member | opus | Set in review-consolidator-skeleton.md (`{MODEL}`) |
| PC (team member) | TeamCreate member | sonnet | Runs CMVCC inside team; needs sonnet |
| Fix Crumb Gatherers | Task (dynamic type) into team | sonnet | Same model as regular Crumb Gatherers; spawned with `team_name: "reviewer-team"` |
| fix-pc-scope-verify | Task into team | haiku | Scope verify for fix CGs: lightweight scope check; spawned with `team_name: "reviewer-team"` |
| fix-pc-claims-vs-code | Task into team | sonnet | Claims-vs-code for fix CGs: substance check; spawned with `team_name: "reviewer-team"` |
| Session Scribe | Task (`ant-farm-session-scribe`) | sonnet | Reads session artifacts; writes exec-summary.md + CHANGELOG entry |
| PC — ESV | Task (`ant-farm-checkpoint-auditor`) | haiku | Mechanical verification — 6 checks, no judgment required |

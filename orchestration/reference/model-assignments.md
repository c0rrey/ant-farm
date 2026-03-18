# Model Assignments

Every `Task` tool call the Queen makes MUST include the `model` parameter from this table. Omitting `model` causes the agent to inherit the Queen's opus model, wasting tokens on agents that don't need it.

| Agent | Spawn Method | Model | Notes |
|-------|-------------|-------|-------|
| Scout | Task (`ant-farm-scout-organizer`) | opus | Orchestration role |
| Pantry (impl) | Task (`ant-farm-pantry-impl`) | opus | Prompt composition + review skeleton assembly (Script 1) |
| Crumb Gatherers | Task (dynamic type) | sonnet | All crumb gatherers regardless of subagent_type |
| PC — SSV | Task (`ant-farm-pest-control`) | haiku | Set comparisons only — no judgment required |
| PC — CCO | Task (`ant-farm-pest-control`) | haiku | Mechanical checklist |
| PC — WWD | Task (`ant-farm-pest-control`) | haiku | Mechanical file comparison |
| PC — CMVCC | Task (`ant-farm-pest-control`) | sonnet | Judgment: claims vs actual code |
| PC — CCB | Task (`ant-farm-pest-control`) | sonnet | Judgment: crumb quality and dedup correctness |
| Nitpickers — Correctness, Edge Cases | TeamCreate member | opus | Higher-judgment reviews; set in big-head-skeleton.md |
| Nitpickers — Clarity, Drift | TeamCreate member | sonnet | Lower-judgment reviews; set in big-head-skeleton.md |
| Big Head | TeamCreate member | opus | Set in big-head-skeleton.md (`{MODEL}`) |
| PC (team member) | TeamCreate member | sonnet | Runs CMVCC inside team; needs sonnet |
| Fix Crumb Gatherers | Task (dynamic type) into team | sonnet | Same model as regular Crumb Gatherers; spawned with `team_name: "nitpicker-team"` |
| fix-pc-wwd | Task into team | haiku | WWD for fix DPs: lightweight scope check; spawned with `team_name: "nitpicker-team"` |
| fix-pc-cmvcc | Task into team | sonnet | CMVCC for fix CGs: substance check; spawned with `team_name: "nitpicker-team"` |
| Scribe | Task (`ant-farm-technical-writer`) | sonnet | Reads session artifacts; writes exec-summary.md + CHANGELOG entry |
| PC — ESV | Task (`ant-farm-pest-control`) | haiku | Mechanical verification — 6 checks, no judgment required |

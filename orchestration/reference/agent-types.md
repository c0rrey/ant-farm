# Agent Types

| Agent | subagent_type | Rationale |
|-------|---------------|-----------|
| Scout | `ant-farm-scout-organizer` | Custom agent: agent-organizer + Bash for crumb CLI |
| Pantry (impl) | `ant-farm-pantry-impl` | Custom agent: CCO-aligned implementation prompt composer |
| Pest Control | `ant-farm-pest-control` | Custom agent: verification auditor, catches fabrication + scope creep |
| Dirt Pushers | from Pantry verdict table | Specialist per task — Scout recommends via dynamic agent discovery, Pantry passes through |
| Nitpicker — Clarity | `ant-farm-nitpicker-clarity` | Custom agent: prose clarity, naming, and readability review |
| Nitpicker — Edge Cases | `ant-farm-nitpicker-edge-cases` | Custom agent: boundary conditions and untested scenarios review |
| Nitpicker — Correctness | `ant-farm-nitpicker-correctness` | Custom agent: logic correctness and algorithmic accuracy review |
| Nitpicker — Drift | `ant-farm-nitpicker-drift` | Custom agent: spec/design drift and requirement alignment review |
| Big Head | `ant-farm-big-head` | Custom agent: deduplication, root-cause grouping, issue filing |
| Scribe | `ant-farm-technical-writer` | Reads session artifacts, writes exec summary + CHANGELOG |
| PC — ESV | `ant-farm-pest-control` | Custom agent: mechanical exec-summary verification against session artifacts |

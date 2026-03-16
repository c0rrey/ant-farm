# Term Definitions

Canonical term definitions for all orchestration templates. When a template uses these terms, it should point here instead of inlining definitions.

## Core Terms

- `{TASK_ID}` — full crumb ID including project prefix (e.g., `ant-farm-9oa`, `my-project-74g.1`)
- `{TASK_SUFFIX}` — suffix portion only; extracted by splitting on the LAST hyphen (e.g., `9oa` from `ant-farm-9oa`, or `74g1` from `my-project-74g.1`). For dot-notation IDs, the suffix includes the dot segment (e.g., `74g.1` from `my-project-74g.1`).
- `{SESSION_DIR}` — session artifact directory path (e.g., `.crumbs/sessions/_session-abc123`)

For extraction algorithm details and edge-case examples, see `orchestration/reference/dependency-analysis.md` (Term Definitions section).

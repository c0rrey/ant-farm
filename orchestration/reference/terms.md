# Term Definitions

Canonical term definitions for all orchestration templates. When a template uses these terms, it should point here instead of inlining definitions.

## Core Terms

- `{TASK_ID}` — full crumb ID including project prefix (e.g., `ant-farm-9oa`, `my-project-74g.1`)
- `{TASK_SUFFIX}` — suffix portion only; extracted by splitting on the LAST hyphen (e.g., `9oa` from `ant-farm-9oa`, or `74g1` from `my-project-74g.1`). For dot-notation IDs, the suffix includes the dot segment (e.g., `74g.1` from `my-project-74g.1`).
- `{SESSION_DIR}` — session artifact directory path (e.g., `.crumbs/sessions/_session-abc123`)

For extraction algorithm details and edge-case examples, see `orchestration/reference/dependency-analysis.md` (Term Definitions section).

## Failure Taxonomy

Two labels classify failure modes across orchestration templates:

- **INFRASTRUCTURE FAILURE** — The agent cannot proceed because a system-level dependency is missing or broken: a required file is absent or unreadable, a CLI tool returned an error, or a subprocess exited with a non-zero code for a non-content reason. Recovery typically requires re-running upstream tooling (e.g., re-spawning Scout) rather than fixing content.

- **SUBSTANCE FAILURE** — The agent has all required inputs but the content is invalid: required metadata sections are absent or empty, placeholder text was not substituted, or data fails a content-level validation rule. Recovery requires human review or correction of the underlying data.

**Decision rule**: If the problem would disappear by re-running the same upstream step without changing any content, it is an INFRASTRUCTURE FAILURE. If the problem requires someone to review or fix the content, it is a SUBSTANCE FAILURE.

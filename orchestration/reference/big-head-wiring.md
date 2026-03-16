# Big Head Wiring Instructions

Queen-facing instructions for spawning Big Head via TeamCreate.
Extracted from `orchestration/templates/big-head-skeleton.md` (formerly lines 1–71).

## Overview

Big Head is a **member of the Nitpicker team** (spawned via TeamCreate, NOT as a separate Task agent).
Do NOT use the Task tool for Big Head — it runs inside the same TeamCreate call as the Nitpickers (4 in round 1; 2 in round 2+).

## Term Definitions

Canonical across all orchestration templates:

- `{TASK_ID}` — full crumb ID including project prefix (e.g., `ant-farm-9oa`)
- `{TASK_SUFFIX}` — suffix portion only; extracted by splitting on the LAST hyphen (e.g., `9oa` from `ant-farm-9oa`, or `74g1` from `my-project-74g.1`)
- `{TIMESTAMP}` — UTC timestamp in `YYYYMMDD-HHmmss` format (e.g., `20260217-143000`)
- `{SESSION_DIR}` — session artifact directory (e.g., `.crumbs/sessions/_session-abc123`)
- `{REVIEW_ROUND}` — review round number (1, 2, 3, ...). Determines report count and P3 handling.

## Step Numbering Note

The steps in the big-head-skeleton.md (Steps 1–12) correspond to the Big Head Consolidation Protocol in `orchestration/templates/reviews.md`, which uses a different numbering scheme (Step 0/0a/1/2/2.5/3/4). See the **Step Numbering Cross-Reference** table in that section for the authoritative mapping. Quick reference: skeleton Step 1 = reviews.md Step 0 (prerequisite gate); skeleton Steps 9–10 = reviews.md Step 4 (Pest Control checkpoint + crumb filing).

## Wiring: TeamCreate + Direct Spawn Prompt

### Step 1 — Fill placeholders before building the TeamCreate call

Replace `{PLACEHOLDER}` values (uppercase) in the agent-facing template below:

- `{MODEL}`: Big Head model — see the **Big Head Consolidation Protocol** section of `orchestration/templates/reviews.md` for the authoritative model assignment. Do NOT hardcode a model name here; consult that section instead.
- `{DATA_FILE_PATH}`: Big Head consolidation brief written by build-review-prompts.sh
- `{CONSOLIDATED_OUTPUT_PATH}`: `{SESSION_DIR}/review-reports/review-consolidated-{TIMESTAMP}.md`

> **Re-spawn and artifact coexistence**: If Big Head fails (timeout, missing reports, or Pest Control
> unavailable), re-spawn it with a **fresh `{TIMESTAMP}` value** — do NOT reuse the original timestamp.
> A fresh timestamp produces a new `{CONSOLIDATED_OUTPUT_PATH}`, so the old `-FAILED` artifact and the
> new success artifact coexist in `review-reports/` by design. This is expected behavior, not an error.
> The Queen should verify results against the artifact with the most recent timestamp.

### Step 2 — Create the Nitpicker team

Pass the filled-in template text (everything below the `---` separator in `big-head-skeleton.md`) as Big Head's `prompt`. Include all expected Nitpicker report paths directly in Big Head's spawn prompt so it can begin consolidation as soon as the reports are ready. Pest Control must be a team member so Big Head can SendMessage to it directly for checkpoint validation (see Step 4 in reviews.md).

**Round 1**: Big Head is the 5th member; Pest Control is the 6th.

```
TeamCreate(
  name="nitpicker-team",
  members=[
    { "name": "clarity-reviewer",      "subagent_type": "ant-farm-nitpicker-clarity",     "prompt": "<filled nitpicker template with REVIEW_TYPE=clarity>", "model": "sonnet" },
    { "name": "edge-cases-reviewer",   "subagent_type": "ant-farm-nitpicker-edge-cases",   "prompt": "<filled nitpicker template with REVIEW_TYPE=edge-cases>", "model": "sonnet" },
    { "name": "correctness-reviewer",  "subagent_type": "ant-farm-nitpicker-correctness",  "prompt": "<filled nitpicker template with REVIEW_TYPE=correctness>", "model": "sonnet" },
    { "name": "drift-reviewer",        "subagent_type": "ant-farm-nitpicker-drift",         "prompt": "<filled nitpicker template with REVIEW_TYPE=drift>", "model": "sonnet" },
    { "name": "ant-farm-big-head",     "prompt": "<filled big-head template with all 4 expected report paths embedded>", "model": "{MODEL}" },
    { "name": "ant-farm-pest-control", "prompt": "<pest-control prompt>", "model": "sonnet" }
  ]
)
```

**Round 2+**: Big Head is the 3rd member; Pest Control is the 4th. Only Correctness and Edge Cases reviewers are spawned.

```
TeamCreate(
  name="nitpicker-team",
  members=[
    { "name": "correctness-reviewer",  "subagent_type": "ant-farm-nitpicker-correctness",  "prompt": "<filled nitpicker template with REVIEW_TYPE=correctness>", "model": "sonnet" },
    { "name": "edge-cases-reviewer",   "subagent_type": "ant-farm-nitpicker-edge-cases",   "prompt": "<filled nitpicker template with REVIEW_TYPE=edge-cases>", "model": "sonnet" },
    { "name": "ant-farm-big-head",     "prompt": "<filled big-head template with 2 expected report paths embedded>", "model": "{MODEL}" },
    { "name": "ant-farm-pest-control", "prompt": "<pest-control prompt>", "model": "sonnet" }
  ]
)
```

### Step 3 — Report paths are included automatically

`build-review-prompts.sh` writes all expected report paths into `{DATA_FILE_PATH}` (the consolidation brief) automatically via `fill_slot`. Big Head's spawn prompt already includes `{DATA_FILE_PATH}`, so Big Head discovers all report paths from the brief without any manual embedding or follow-up SendMessage.

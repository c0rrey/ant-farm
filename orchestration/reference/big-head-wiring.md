# Big Head Wiring Instructions

Queen-facing instructions for spawning Big Head via TeamCreate.
Extracted from `orchestration/templates/big-head-skeleton.md` (formerly lines 1–71).

## Overview

Big Head is a **member of the Nitpicker team** (spawned via TeamCreate, NOT as a separate Task agent).
Do NOT use the Task tool for Big Head — it runs inside the same TeamCreate call as the Nitpickers (typically 4 in round 1, 2 in round 2+; exact count from consolidation brief's `expected_paths`).

## Term Definitions

Canonical across all orchestration templates:

- `{TASK_ID}` — full crumb ID including project prefix (e.g., `ant-farm-9oa`)
- `{TASK_SUFFIX}` — suffix portion only; extracted by splitting on the LAST hyphen (e.g., `9oa` from `ant-farm-9oa`, or `74g1` from `my-project-74g.1`)
- `{TIMESTAMP}` — UTC timestamp in `YYYYMMDD-HHmmss` format (e.g., `20260217-143000`)
- `{SESSION_DIR}` — session artifact directory (e.g., `.crumbs/sessions/_session-abc123`)
- `{REVIEW_ROUND}` — review round number (1, 2, 3, ...). Determines which review types are active and P3 handling. Report count is determined by the consolidation brief's `expected_paths` list, not by a fixed number.

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

**Round 1**: Big Head is the 5th member in the base case (6 total); Pest Control is always the last member. The consolidation brief's `expected_paths` list is authoritative for how many report paths Big Head must wait for.

**Dynamic member list**: The Queen reads the return table from `build-review-prompts.sh` to determine which reviewer slots were filled and how many split instances were produced. Do NOT use a fixed 6-member list. Instead, build the `members` array from the return table:
- Base case (no splits): 4 reviewers (`clarity-reviewer`, `edge-cases-reviewer`, `correctness-reviewer`, `drift-reviewer`)
- Split Clarity: replace `clarity-reviewer` with `clarity-1`, `clarity-2` (and `clarity-3` if 3-way split); each gets its own filled nitpicker template with `REVIEW_TYPE=clarity`
- Split Drift: replace `drift-reviewer` with `drift-1`, `drift-2`, etc.
- Big Head and Pest Control are always appended last (Big Head second-to-last, Pest Control last)

**Split instance naming convention**: `{review-type}-{N}` where `N` starts at 1 (e.g., `clarity-1`, `clarity-2`, `drift-1`, `drift-2`). SendMessage targeting must use these exact names — broadcast is prohibited because it would re-task idle split instances in round 2+.

Base case (no splits) — 6 members:

```
TeamCreate(
  name="nitpicker-team",
  members=[
    { "name": "clarity-reviewer",      "subagent_type": "ant-farm-nitpicker-clarity",     "prompt": "<filled nitpicker template with REVIEW_TYPE=clarity>", "model": "sonnet" },
    { "name": "edge-cases-reviewer",   "subagent_type": "ant-farm-nitpicker-edge-cases",   "prompt": "<filled nitpicker template with REVIEW_TYPE=edge-cases>", "model": "opus" },
    { "name": "correctness-reviewer",  "subagent_type": "ant-farm-nitpicker-correctness",  "prompt": "<filled nitpicker template with REVIEW_TYPE=correctness>", "model": "opus" },
    { "name": "drift-reviewer",        "subagent_type": "ant-farm-nitpicker-drift",         "prompt": "<filled nitpicker template with REVIEW_TYPE=drift>", "model": "sonnet" },
    { "name": "ant-farm-big-head",     "prompt": "<filled big-head template — report count from consolidation brief's expected_paths>", "model": "{MODEL}" },
    { "name": "ant-farm-pest-control", "prompt": "<pest-control prompt>", "model": "sonnet" }
  ]
)
```

Split instance example (2 Clarity + 2 Drift splits) — 8 members:

```
TeamCreate(
  name="nitpicker-team",
  members=[
    { "name": "clarity-1",             "subagent_type": "ant-farm-nitpicker-clarity",     "prompt": "<filled nitpicker template with REVIEW_TYPE=clarity, file subset A>", "model": "sonnet" },
    { "name": "clarity-2",             "subagent_type": "ant-farm-nitpicker-clarity",     "prompt": "<filled nitpicker template with REVIEW_TYPE=clarity, file subset B>", "model": "sonnet" },
    { "name": "edge-cases-reviewer",   "subagent_type": "ant-farm-nitpicker-edge-cases",   "prompt": "<filled nitpicker template with REVIEW_TYPE=edge-cases>", "model": "opus" },
    { "name": "correctness-reviewer",  "subagent_type": "ant-farm-nitpicker-correctness",  "prompt": "<filled nitpicker template with REVIEW_TYPE=correctness>", "model": "opus" },
    { "name": "drift-1",               "subagent_type": "ant-farm-nitpicker-drift",         "prompt": "<filled nitpicker template with REVIEW_TYPE=drift, file subset A>", "model": "sonnet" },
    { "name": "drift-2",               "subagent_type": "ant-farm-nitpicker-drift",         "prompt": "<filled nitpicker template with REVIEW_TYPE=drift, file subset B>", "model": "sonnet" },
    { "name": "ant-farm-big-head",     "prompt": "<filled big-head template — report count from consolidation brief's expected_paths>", "model": "{MODEL}" },
    { "name": "ant-farm-pest-control", "prompt": "<pest-control prompt>", "model": "sonnet" }
  ]
)
```

**Round 2+**: Only Correctness and Edge Cases reviewers are re-tasked; the consolidation brief's `expected_paths` is authoritative for the 2 expected report paths. Pest Control is always the last member of the persistent team.

**Split instance idle semantics**: In round 2+, split Clarity instances (`clarity-1`, `clarity-2`, etc.) and split Drift instances (`drift-1`, `drift-2`, etc.) remain idle — exactly like the base-case `clarity-reviewer` and `drift-reviewer`. They are NOT re-tasked via SendMessage. Round 2+ SendMessage targets only `correctness-reviewer`, `edge-cases-reviewer`, `ant-farm-big-head`, and `ant-farm-pest-control` by name. Never use broadcast in round 2+.

Round 2+ re-task targets (named-member SendMessage only — no broadcast):

```
TeamCreate(
  name="nitpicker-team",
  members=[
    { "name": "correctness-reviewer",  "subagent_type": "ant-farm-nitpicker-correctness",  "prompt": "<filled nitpicker template with REVIEW_TYPE=correctness>", "model": "opus" },
    { "name": "edge-cases-reviewer",   "subagent_type": "ant-farm-nitpicker-edge-cases",   "prompt": "<filled nitpicker template with REVIEW_TYPE=edge-cases>", "model": "opus" },
    { "name": "ant-farm-big-head",     "prompt": "<filled big-head template — report count from consolidation brief's expected_paths>", "model": "{MODEL}" },
    { "name": "ant-farm-pest-control", "prompt": "<pest-control prompt>", "model": "sonnet" }
  ]
)
```

> Note: The Round 2+ TeamCreate block above shows the initial spawn composition only. The team is persistent — do NOT re-issue TeamCreate. Round 2+ uses SendMessage to re-task `correctness-reviewer` and `edge-cases-reviewer` (and Big Head and Pest Control) by their exact member names. Any split instances present in the team (e.g., `clarity-1`, `drift-2`) stay idle and receive no messages.

### Step 3 — Report paths are included automatically

`build-review-prompts.sh` writes all expected report paths into `{DATA_FILE_PATH}` (the consolidation brief) automatically via `fill_slot`. Big Head's spawn prompt already includes `{DATA_FILE_PATH}`, so Big Head discovers all report paths from the brief without any manual embedding or follow-up SendMessage.

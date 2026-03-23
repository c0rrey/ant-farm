---
description: This skill should be used when the user invokes "/ant-farm-plan", provides a spec file path or inline specification text to decompose, says "plan this", "decompose this spec", "break this into tasks", or asks to turn a requirement or idea into crumbs. Accepts a file path, inline text, or --prd <file> flag, classifies input as structured vs freeform (or PRD import), and routes to the RULES-decompose.md decomposition workflow.
---

> **Tool invocation note**: Where this skill instructs the Orchestrator to call crumb operations directly
> (e.g., `crumb create`), prefer the MCP tool equivalents (`crumb_list`, `crumb_show`,
> `crumb_update`, `crumb_create`, `crumb_query`, `crumb_doctor`). If the MCP server is unavailable, fall
> back to the equivalent `crumb <command>` CLI call via Bash.

# /ant-farm-plan — Decomposition Skill

This skill governs the `/ant-farm-plan` slash command. It accepts a spec file path or inline specification text, detects the input type, classifies the input as structured or freeform (or PRD import), creates a timestamped `DECOMPOSE_DIR` under `.crumbs/sessions/`, and routes to `orchestration/RULES-decompose.md` for execution.

There are three input modes:

| Mode | Invocation | Spec Writer | Notes |
|------|-----------|----------|-------|
| Freeform | `/ant-farm-plan <idea text>` | Yes | Spec Writer asks clarifying questions and writes spec.md |
| Structured spec | `/ant-farm-plan path/to/spec.md` | No | Spec written verbatim; user may optionally run Researchers |
| PRD import | `/ant-farm-plan --prd path/to/prd.md` | No | PRD extracted into spec.md format; user confirms before Researchers |

Use `--prd` when you have an existing Product Requirements Document you want decomposed directly. The Spec Writer is skipped; the PRD Importer agent reads the file, extracts requirements into spec.md format, and asks you to confirm before spawning Researchers. Use standard invocation (freeform or structured spec) when you are starting from scratch or from a lightweight outline.

## Trigger Conditions

Activate this skill when the user:
- Invokes `/ant-farm-plan` (with or without an argument)
- Invokes `/ant-farm-plan --prd <file>` to import a PRD file directly
- Provides a file path to a spec document as an argument to `/ant-farm-plan`
- Provides inline specification text as an argument to `/ant-farm-plan`
- Says "plan this", "decompose this spec", "break this into tasks", "turn this into crumbs", or similar

## Step 0 — Pre-flight Error Handling

Before doing anything else, check for fatal conditions. Surface clear error messages and stop if any are true.

### Error: .crumbs/ not initialized

```bash
[ -f .crumbs/tasks.jsonl ] && [ -f .crumbs/config.json ] && echo "INITIALIZED" || echo "NOT_INITIALIZED"
```

If `NOT_INITIALIZED`:

> **Error**: `.crumbs/` is not initialized in this project. Run `/ant-farm-init` first to scaffold the task system, then return to `/ant-farm-plan`.

Stop. Do not proceed.

### Flag detection: --prd

If the invocation is `/ant-farm-plan --prd <file>`:

1. Extract `<file>` as `PRD_PATH`.
2. Validate the file exists and is readable:

```bash
[ -f "<PRD_PATH>" ] && echo "PRD_EXISTS" || echo "PRD_NOT_FOUND"
```

If `PRD_NOT_FOUND`:

> **Error**: PRD file not found: `<PRD_PATH>`. Check the path and try again.
>
> Usage: `/ant-farm-plan --prd path/to/prd.md`

Stop. Do not proceed.

3. Check the file is non-empty:

```bash
[ -s "<PRD_PATH>" ] && echo "PRD_NON_EMPTY" || echo "PRD_EMPTY"
```

If `PRD_EMPTY`:

> **Error**: PRD file is empty: `<PRD_PATH>`. Provide a file with content.

Stop. Do not proceed.

4. Set `INPUT_CLASS=PRD`, `INPUT_SOURCE="prd:<PRD_PATH>"`, and `PRD_PATH` in context. Skip Steps 1 and 2. Proceed directly to Step 3 (Create DECOMPOSE_DIR), then Step 4 (Route to RULES-decompose.md) — passing `INPUT_CLASS=PRD` and `PRD_PATH` to the decomposition workflow.

### Error: Empty input

If the user invoked `/ant-farm-plan` with no argument and no inline text (and no `--prd` flag):

> **Error**: No input provided. Usage:
>
> - `/ant-farm-plan path/to/spec.md` — decompose a spec file
> - `/ant-farm-plan <inline text>` — decompose inline specification text
> - `/ant-farm-plan --prd path/to/prd.md` — import a PRD file and skip the Spec Writer
>
> Provide a file path, paste your spec text directly, or use `--prd` to import a PRD.

Stop. Do not proceed.

## Step 1 — Detect Input Type

Examine the argument provided to `/ant-farm-plan`.

### File path detection

The argument is treated as a **file path** if it meets any of the following:
- Starts with `/`, `./`, or `../`
- Ends with a recognized doc extension: `.md`, `.txt`, `.rst`, `.yaml`, `.yml`, `.json`
- Does not contain whitespace and resolves to an existing file

```bash
[ -f "<ARGUMENT>" ] && echo "FILE_EXISTS" || echo "NOT_A_FILE"
```

If the argument looks like a file path but the file does not exist:

> **Error**: File not found: `<ARGUMENT>`. Check the path and try again, or pass the spec text inline.

Stop. Do not proceed.

If the file exists, read its contents:

```bash
cat "<ARGUMENT>"
```

Store the contents as `INPUT_TEXT`. Store the source path as `INPUT_SOURCE` (e.g., `"file:<ARGUMENT>"`).

### Inline text detection

If the argument does not match the file path heuristic above, treat the entire argument as **inline text**. Store it directly as `INPUT_TEXT`. Store `INPUT_SOURCE` as `"inline"`.

If `INPUT_TEXT` is empty or whitespace-only after reading:

> **Error**: Input is empty. The file `<ARGUMENT>` exists but contains no content, or no text was provided inline.

Stop. Do not proceed.

## Step 2 — Classify Input

Analyze `INPUT_TEXT` to determine whether it is a **structured spec** or a **freeform idea**. This classification affects the decomposition strategy in `RULES-decompose.md`.

### Structured spec heuristic

Score +1 for each of the following signals present in `INPUT_TEXT`:

| Signal | Detection |
|---|---|
| Markdown headings | One or more lines matching `^#{1,4}\s+\S` |
| Bullet or numbered lists | Three or more lines matching `^\s*[-*+]\s` or `^\s*\d+\.\s` |
| Acceptance criteria section | Case-insensitive match for "acceptance criteria", "AC:", or "- [ ]" |
| Requirements language | Case-insensitive match for "must", "should", "shall", "requirements", "constraints" |
| Numbered sections | Two or more lines matching `^\d+\.\s+[A-Z]` (numbered section headers) |
| Technical specificity | Presence of code fences (` ``` `), inline code (`` `..` ``), or CLI commands |

**Threshold**: Score 3 or more → classify as `STRUCTURED`. Score 2 or fewer → classify as `FREEFORM`.

Store the classification as `INPUT_CLASS` (`STRUCTURED` or `FREEFORM`) and the score as `CLASS_SCORE`.

Surface the classification to the user:

> **Input classified**: `[STRUCTURED | FREEFORM]` (score: `CLASS_SCORE`/6)
>
> Source: `INPUT_SOURCE`

## Step 3 — Create DECOMPOSE_DIR

Generate a decomposition session ID and create the working directory:

```bash
DECOMPOSE_ID=$(date +%Y%m%d-%H%M%S)
DECOMPOSE_DIR=".crumbs/sessions/_decompose-${DECOMPOSE_ID}"
mkdir -p "${DECOMPOSE_DIR}"
```

Write a manifest file to capture input metadata:

```bash
jq -n \
  --arg decompose_id "${DECOMPOSE_ID}" \
  --arg input_source "<INPUT_SOURCE>" \
  --arg input_class "<INPUT_CLASS>" \
  --arg class_score "<CLASS_SCORE>" \
  --arg created_at "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
  '{decompose_id: $decompose_id, input_source: $input_source, input_class: $input_class, class_score: $class_score, created_at: $created_at}' \
  > "${DECOMPOSE_DIR}/manifest.json"
```

Write `INPUT_TEXT` to `${DECOMPOSE_DIR}/input.txt` for use by the decomposition workflow:

```bash
printf '%s\n' "${INPUT_TEXT}" > "${DECOMPOSE_DIR}/input.txt"
```

Store `DECOMPOSE_DIR` in context. Pass it explicitly to the decomposition workflow.

## Step 4 — Route to RULES-decompose.md

Read `orchestration/RULES-decompose.md` and follow its workflow from Step 1 onward, passing:
- `DECOMPOSE_DIR` — the session directory created in Step 3
- `INPUT_CLASS` — `STRUCTURED`, `FREEFORM`, or `PRD`
- `INPUT_TEXT` — the raw spec content (empty string when `INPUT_CLASS=PRD`; the workflow uses `PRD_PATH` instead)
- `PRD_PATH` — the validated PRD file path (only when `INPUT_CLASS=PRD`; omit otherwise)

The decomposition workflow in `RULES-decompose.md` is responsible for:
- Parsing the spec into epics, tasks, and dependencies
- Applying the appropriate decomposition strategy based on `INPUT_CLASS`
- Writing crumbs to `.crumbs/tasks.jsonl` via `crumb create`
- Producing a decomposition summary

## Error Reference

| Condition | Behavior |
|---|---|
| `.crumbs/` not initialized | Hard stop — instruct user to run `/ant-farm-init` |
| `--prd <file>` given but file not found | Hard stop — show path; suggest checking the path |
| `--prd <file>` given but file is empty | Hard stop — report empty PRD file |
| No argument provided | Hard stop — show usage message including `--prd` option |
| Argument looks like file path but file not found | Hard stop — show path and suggest inline alternative |
| File found but empty | Hard stop — report empty file |
| Inline text is whitespace-only | Hard stop — report empty input |
| `RULES-decompose.md` not found | Hard stop — report missing file: `orchestration/RULES-decompose.md does not exist. This file must be created before /ant-farm-plan can execute decomposition.` |
| `mkdir` fails for DECOMPOSE_DIR | Hard stop — report permissions error on `.crumbs/sessions/` |
| `crumb` CLI not available | Hard stop — instruct user to run `/ant-farm-init` to install the `crumb` CLI |

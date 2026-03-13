---
name: ant-farm-plan
description: This skill should be used when the user invokes "/ant-farm:plan", provides a spec file path or inline specification text to decompose, says "plan this", "decompose this spec", "break this into tasks", or asks to turn a requirement or idea into crumbs. Accepts a file path or inline text, classifies input as structured vs freeform, and routes to the RULES-decompose.md decomposition workflow.
version: 1.0.0
---

# /ant-farm:plan — Decomposition Skill

This skill governs the `/ant-farm:plan` slash command. It accepts a spec file path or inline specification text, detects the input type, classifies the input as structured or freeform, creates a timestamped `DECOMPOSE_DIR` under `.crumbs/sessions/`, and routes to `orchestration/RULES-decompose.md` for execution.

## Trigger Conditions

Activate this skill when the user:
- Invokes `/ant-farm:plan` (with or without an argument)
- Provides a file path to a spec document as an argument to `/ant-farm:plan`
- Provides inline specification text as an argument to `/ant-farm:plan`
- Says "plan this", "decompose this spec", "break this into tasks", "turn this into crumbs", or similar

## Step 0 — Pre-flight Error Handling

Before doing anything else, check for fatal conditions. Surface clear error messages and stop if any are true.

### Error: .crumbs/ not initialized

```bash
[ -f .crumbs/tasks.jsonl ] && [ -f .crumbs/config.json ] && echo "INITIALIZED" || echo "NOT_INITIALIZED"
```

If `NOT_INITIALIZED`:

> **Error**: `.crumbs/` is not initialized in this project. Run `/ant-farm:init` first to scaffold the task system, then return to `/ant-farm:plan`.

Stop. Do not proceed.

### Error: Empty input

If the user invoked `/ant-farm:plan` with no argument and no inline text:

> **Error**: No input provided. Usage:
>
> - `/ant-farm:plan path/to/spec.md` — decompose a spec file
> - `/ant-farm:plan <inline text>` — decompose inline specification text
>
> Provide a file path or paste your spec text directly as the argument.

Stop. Do not proceed.

## Step 1 — Detect Input Type

Examine the argument provided to `/ant-farm:plan`.

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
cat > "${DECOMPOSE_DIR}/manifest.json" <<EOF
{
  "decompose_id": "${DECOMPOSE_ID}",
  "input_source": "<INPUT_SOURCE>",
  "input_class": "<INPUT_CLASS>",
  "class_score": <CLASS_SCORE>,
  "created_at": "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
}
EOF
```

Write `INPUT_TEXT` to `${DECOMPOSE_DIR}/input.txt` for use by the decomposition workflow:

```bash
cat > "${DECOMPOSE_DIR}/input.txt" <<'SPEC_EOF'
<INPUT_TEXT>
SPEC_EOF
```

Store `DECOMPOSE_DIR` in context. Pass it explicitly to the decomposition workflow.

## Step 4 — Route to RULES-decompose.md

Read `orchestration/RULES-decompose.md` and follow its workflow from Step 1 onward, passing:
- `DECOMPOSE_DIR` — the session directory created in Step 3
- `INPUT_CLASS` — `STRUCTURED` or `FREEFORM`
- `INPUT_TEXT` — the raw spec content

The decomposition workflow in `RULES-decompose.md` is responsible for:
- Parsing the spec into epics, tasks, and dependencies
- Applying the appropriate decomposition strategy based on `INPUT_CLASS`
- Writing crumbs to `.crumbs/tasks.jsonl` via `crumb create`
- Producing a decomposition summary

## Error Reference

| Condition | Behavior |
|---|---|
| `.crumbs/` not initialized | Hard stop — instruct user to run `/ant-farm:init` |
| No argument provided | Hard stop — show usage message |
| Argument looks like file path but file not found | Hard stop — show path and suggest inline alternative |
| File found but empty | Hard stop — report empty file |
| Inline text is whitespace-only | Hard stop — report empty input |
| `RULES-decompose.md` not found | Hard stop — report missing file: `orchestration/RULES-decompose.md does not exist. This file must be created before /ant-farm:plan can execute decomposition.` |
| `mkdir` fails for DECOMPOSE_DIR | Hard stop — report permissions error on `.crumbs/sessions/` |
| `crumb` CLI not available | Hard stop — instruct user to run `/ant-farm:init` to install the `crumb` CLI |

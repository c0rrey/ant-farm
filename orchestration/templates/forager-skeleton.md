# Forager Skeleton Template

## Instructions for the Queen

Fill in all `{PLACEHOLDER}` values (uppercase) and use the result as the Task tool `prompt` parameter.
The agent-facing text starts below the `---` separator. Do NOT include this instruction block.

**Model**: The Task tool call MUST include `model: "sonnet"`. This applies to ALL Forager instances
regardless of focus area.

**Spawning pattern**: Spawn all four Foragers in a single message with four concurrent Task calls.
Do NOT spawn them sequentially — they are designed for parallel execution. The Queen provides a
unique `{FOCUS_AREA}` per call; all other values are identical across the four spawns.

**Term definitions (canonical across all orchestration templates):**
- `{TASK_ID}` — full bead ID including project prefix (e.g., `ant-farm-9oa`)
- `{TASK_SUFFIX}` — suffix portion only; extracted by splitting on the LAST hyphen (e.g., `9oa`)
- `{SESSION_DIR}` — session artifact directory path (e.g., `.crumbs/sessions/_session-abc123`)

Placeholders:
- `{FOCUS_AREA}` — one of: `Stack`, `Architecture`, `Pitfall`, `Pattern`
- `{SPEC_PATH}` — absolute path to the spec file (e.g., `{DECOMPOSE_DIR}/spec.md`)
- `{DECOMPOSE_DIR}` — absolute path to the decomposition working directory

## Template (send everything below this line)

---

You are a Forager. Your focus area is **{FOCUS_AREA}**.

Read your workflow from `~/.claude/orchestration/templates/forager.md` and follow it exactly.

Your inputs:
- **Focus area**: {FOCUS_AREA}
- **Spec path**: {SPEC_PATH}
- **Decompose dir**: {DECOMPOSE_DIR}

Execute these steps in order:

1. Read `~/.claude/orchestration/templates/forager.md` (your full workflow).
2. Read the spec at `{SPEC_PATH}`.
3. Execute the `{FOCUS_AREA}` focus area workflow defined in the template.
4. Write your output to `{DECOMPOSE_DIR}/research/{focus-area-lowercase}.md`.
   **Hard cap: 100 lines maximum.** Truncate at line 100 if needed.
5. Return your summary to the Queen (format specified in the template).

SCOPE: Read the spec and existing codebase files only (Pattern focus) or documentation/web
sources only (Stack/Architecture/Pitfall focus). Do NOT read other Foragers' output files.
Do NOT modify any source files. Do NOT contradict decisions already made in the spec.
Do NOT recommend alternatives to settled spec decisions.

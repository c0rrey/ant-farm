# Pest Control -- Checkpoint A (Pre-Spawn Prompt Audit)

**Task ID**: ant-farm-ss6
**Preview**: `.beads/agent-summaries/_session-ae4401/previews/task-ss6-preview.md`
**Task context**: `.beads/agent-summaries/_session-ae4401/prompts/task-ss6.md`
**Timestamp**: 2026-02-17 12:08:51

---

## Check 1: Real Task IDs
**PASS**

The preview uses the actual task ID `ant-farm-ss6` in all four required locations:
- `bd show ant-farm-ss6` (line 8)
- `bd update ant-farm-ss6 --status=in_progress` (line 8)
- Commit message template `(ant-farm-ss6)` (line 12)
- `bd close ant-farm-ss6` (line 19)

No placeholders like `<task-id>` or `{id}` found in the preview.

---

## Check 2: Real File Paths
**PASS**

The preview delegates file listing to the task context file (`task-ss6.md`), which contains four real file paths:
- `~/.claude/orchestration/templates/dirt-pusher-skeleton.md`
- `~/.claude/orchestration/templates/pantry.md`
- `~/.claude/orchestration/templates/checkpoints.md`
- `~/.claude/orchestration/RULES.md`

No placeholder paths like `<list from bead>` or `<file>` found. Each file path is accompanied by specific search patterns (e.g., "search for all occurrences of `TASK_ID`, `task-id`, `task-id-suffix`").

---

## Check 3: Root Cause Text
**PASS**

The task context contains a specific, detailed root cause (task-ss6.md lines 23):
> "dirt-pusher-skeleton.md uses `{TASK_ID}` (uppercase placeholder for full ID like `hs_website-74g.1`), pantry.md uses `{task-id-suffix}` (lowercase, meaning just the suffix like `74g.1` or `ss6`), and checkpoints.md uses both `<task-id>` and `{task-id}` interchangeably without clarifying whether they mean the full ID or the suffix."

This is a concrete description naming three specific files, three specific notation styles, and the ambiguity they create. Not a placeholder.

---

## Check 4: All 6 Mandatory Steps Present
**PASS**

| Step | Required | Found | Evidence |
|------|----------|-------|----------|
| 1 | `bd show` + `bd update --status=in_progress` | Yes | Line 8: `bd show ant-farm-ss6` + `bd update ant-farm-ss6 --status=in_progress` |
| 2 | "Design at least 4 approaches" (MANDATORY) | Yes | Line 9: "4+ genuinely distinct approaches with tradeoffs" with "(MANDATORY)" keyword |
| 3 | Implementation instructions | Yes | Line 10: "Write clean, minimal code satisfying acceptance criteria" |
| 4 | "Review EVERY file" (MANDATORY) | Yes | Line 11: "Re-read EVERY changed file. Verify acceptance criteria. Assumptions audit." with "(MANDATORY)" keyword |
| 5 | Commit with `git pull --rebase` | Yes | Line 12: `git pull --rebase && git add <changed-files> && git commit` |
| 6 | Write summary doc to `.beads/agent-summaries/<epic-id>/` | Yes | Lines 13-14: "Write to .beads/agent-summaries/_standalone/ss6.md with all required sections" |

All 6 steps present with required keywords.

---

## Check 5: Scope Boundaries
**PASS**

The preview contains explicit scope constraints at line 17: "SCOPE: Only edit files listed in the task context."

The task context reinforces this with three separate scope mechanisms:
1. **Read ONLY list**: Four specific files enumerated (task-ss6.md lines 35-38)
2. **Do NOT edit list**: Eight specific exclusions enumerated (task-ss6.md lines 41-48)
3. **Focus section**: Explicit "Do NOT" list with four constraints including "Fix other issues you notice," "Make while you're here improvements," "Combine this task with related work," and "Change functional behavior" (task-ss6.md lines 53-57)

Not open-ended "explore the codebase."

---

## Check 6: Commit Instructions
**PASS**

Line 12 of the preview contains: `git pull --rebase && git add <changed-files> && git commit -m "<type>: <description> (ant-farm-ss6)"`

The `git pull --rebase` appears before `git add` and `git commit` in the correct order.

---

## Check 7: Line Number Specificity
**WARN** (acceptable)

The task context provides file-level scope with specific search patterns but no line numbers:
- `dirt-pusher-skeleton.md` -- "search for all occurrences of `TASK_ID`, `task-id`, `task-id-suffix`"
- `pantry.md` -- "search for all occurrences of `task-id-suffix`, `task-id`, `TASK_ID`"
- `checkpoints.md` -- "search for all occurrences of `task-id`, `task-id-suffix`, `TASK_ID`"
- `RULES.md` -- "search for `task-id`, `task-id-suffix`, `TASK_ID`"

The task context explicitly explains WHY line numbers are not provided (task-ss6.md line 14): "Do NOT rely on specific line numbers provided below -- they are approximate. Instead, search for the patterns described." This is because Wave 1 agents modified these files, making prior line numbers unreliable.

Per the rubric, file-level scope with section/pattern markers is WARN-level ("acceptable if small file"). This is acceptable here because:
1. The task is a terminology standardization requiring full-file search-and-replace
2. Line numbers would be actively misleading due to Wave 1 modifications
3. Specific search patterns are provided to constrain the scope within each file

---

## Verdict: PASS

All 7 checks pass (6 PASS, 1 WARN-acceptable). The preview and task context contain real task IDs, real file paths with search patterns, a specific root cause, all 6 mandatory steps with required keywords, explicit scope boundaries, correct commit instructions, and acceptable file-level scope with pattern markers.

No defects found. Safe to spawn.

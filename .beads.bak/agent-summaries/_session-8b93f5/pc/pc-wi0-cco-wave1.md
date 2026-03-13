# Pest Control -- CCO (Pre-Spawn Prompt Audit)

**Task**: ant-farm-wi0
**Preview file**: `.beads/agent-summaries/_session-8b93f5/previews/task-wi0-preview.md`
**Checkpoint**: Colony Cartography Office (CCO) -- Dirt Pusher

---

## Check 1: Real Task IDs
**PASS**

The prompt contains the actual task ID `ant-farm-wi0` in multiple locations:
- Line 1: "Execute task for ant-farm-wi0."
- Line 8: `bd show ant-farm-wi0` + `bd update ant-farm-wi0 --status=in_progress`
- Line 12: commit message suffix `(ant-farm-wi0)`
- Line 16: `bd close ant-farm-wi0`
- Line 23: "# Task Brief: ant-farm-wi0"

No placeholders like `<task-id>` or `{TASK_ID}` used where a concrete ID is expected.

---

## Check 2: Real File Paths
**PASS**

The prompt lists concrete file paths with line numbers in the "Affected files" section (lines 29-33):
- `orchestration/templates/scout.md:L78` -- verified: line 78 contains `{task-id-suffix}` in a write path template
- `orchestration/templates/scout.md:L81` -- verified: line 81 contains `{full-task-id}` in a markdown heading template
- `orchestration/templates/scout.md:L254` -- verified: line 254 contains `{full-task-id}` in an error metadata example
- `orchestration/PLACEHOLDER_CONVENTIONS.md:L63` -- verified: line 63 contains `{task-id-suffix}` listed as a Tier 2 example

All four file:line references were cross-checked against the actual files on disk. Each line contains exactly the content described in the prompt.

No placeholders like `<list from bead>` or `<file>` found.

---

## Check 3: Root Cause Text
**PASS**

Lines 34-35 contain a specific, multi-sentence root cause description:
> "The same concepts use different variable names across files: `{task-id-suffix}` vs `{TASK_SUFFIX}`, `{full-task-id}` vs `{TASK_ID}`, and the terms 'task ID' vs 'bead ID' are used interchangeably. The PLACEHOLDER_CONVENTIONS.md glossary defines canonical Tier 1 names [...] but scout.md still uses non-canonical Tier 2 synonyms [...]"

This is specific to the actual codebase state, names concrete files and variable names, and explains the causal mechanism (glossary defines canonical names, but scout.md drifted). Not a placeholder.

---

## Check 4: All 6 Mandatory Steps Present
**PASS**

All six steps are present (lines 8-16):

| Step | Required content | Present? | Evidence |
|------|-----------------|----------|----------|
| Step 1 | `bd show` + `bd update --status=in_progress` | Yes | Line 8: `bd show ant-farm-wi0` + `bd update ant-farm-wi0 --status=in_progress` |
| Step 2 | "4+" or "Design at least 4 approaches" (MANDATORY keyword) | Yes | Line 9: "**Design** (MANDATORY): 4+ genuinely distinct approaches" |
| Step 3 | Implementation instructions | Yes | Line 10: "**Implement**: Write clean, minimal code satisfying acceptance criteria." |
| Step 4 | "Re-read EVERY" or per-file correctness review (MANDATORY keyword) | Yes | Line 11: "**Review** (MANDATORY): Re-read EVERY changed file." |
| Step 5 | Commit with `git pull --rebase` | Yes | Line 12: `git pull --rebase && git add <changed-files> && git commit` |
| Step 6 | Write summary doc to `{SESSION_DIR}/summaries/` | Yes | Line 14: "Write to .beads/agent-summaries/_session-8b93f5/summaries/wi0.md" |

---

## Check 5: Scope Boundaries
**PASS**

Lines 42-58 contain explicit, bounded scope instructions:

**Read ONLY list** (lines 42-48): Six specific files with line-range restrictions:
- `orchestration/templates/scout.md` (full file, focus on L78, L81, L254)
- `orchestration/PLACEHOLDER_CONVENTIONS.md` (full file, focus on L63 and glossary sections)
- `orchestration/templates/pantry.md:L1-10`
- `orchestration/templates/dirt-pusher-skeleton.md:L8-16`
- `orchestration/templates/checkpoints.md:L4-10`
- `orchestration/templates/big-head-skeleton.md:L8-12`

**Do NOT edit list** (lines 50-58): Eight explicit exclusions with rationale for each.

**Focus section** (lines 60-63): Narrows the task further with "ONLY" keyword and two explicit prohibitions against adjacent work.

This is not open-ended "explore the codebase." The scope is tightly bounded.

---

## Check 6: Commit Instructions
**PASS**

Line 12 includes `git pull --rebase` as part of the commit command chain:
```
git pull --rebase && git add <changed-files> && git commit -m "<type>: <description> (ant-farm-wi0)"
```

---

## Check 7: Line Number Specificity
**PASS**

All affected files include specific line numbers or line ranges:

| File path | Line specificity | Rating |
|-----------|-----------------|--------|
| `orchestration/templates/scout.md:L78` | Specific line | PASS |
| `orchestration/templates/scout.md:L81` | Specific line | PASS |
| `orchestration/templates/scout.md:L254` | Specific line | PASS |
| `orchestration/PLACEHOLDER_CONVENTIONS.md:L63` | Specific line | PASS |

The Scope Boundaries "Read ONLY" section also specifies line ranges for reference files (e.g., `pantry.md:L1-10`, `dirt-pusher-skeleton.md:L8-16`, `checkpoints.md:L4-10`, `big-head-skeleton.md:L8-12`).

For the two editable files (`scout.md` and `PLACEHOLDER_CONVENTIONS.md`), the prompt says "full file, focus on L78, L81, L254" and "full file, focus on L63 and glossary sections" respectively. The affected lines are enumerated with specific line numbers and each annotation describes exactly what needs changing (e.g., "uses `{task-id-suffix}` instead of canonical `{TASK_SUFFIX}`").

---

## Verdict

**PASS** -- All 7 checks pass. The prompt contains real task IDs, verified file paths with accurate line numbers, a specific root cause, all 6 mandatory steps with required keywords, explicit scope boundaries, `git pull --rebase` in commit instructions, and line-level specificity for all affected files. Ready to spawn.

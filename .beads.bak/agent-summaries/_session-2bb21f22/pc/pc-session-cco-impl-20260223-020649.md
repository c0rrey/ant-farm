# CCO Audit Report - Wave 1 Implementation Prompts

**Checkpoint**: Colony Cartography Office (CCO) - Pre-Spawn Prompt Audit
**Session**: _session-2bb21f22
**Wave**: 1
**Tasks**: ant-farm-fomy (1 task, 1 agent)
**Timestamp**: 2026-02-23T02:06:49Z
**Model**: haiku

---

## Audit Status

**CRITICAL ISSUE DETECTED**

The preview directory `/Users/correy/projects/ant-farm/.beads/agent-summaries/_session-2bb21f22/previews/` is **empty**. According to orchestration/RULES.md:
- Step 2 requires Pantry to create combined prompt previews in `{SESSION_DIR}/previews/`
- CCO should audit these preview files BEFORE agents are spawned
- No preview files were found at the expected location

**Impact**: CCO audit cannot proceed as designed. The artifact to audit does not exist at the correct location.

---

## Artifact Discovery

I located a task brief at:
`/Users/correy/projects/ant-farm/.beads/agent-summaries/_session-2bb21f22/prompts/task-fomy.md`

This file exists in the `prompts/` directory but corresponds to what should be a **preview file** in the `previews/` directory.

**Status of located artifact**: The file appears to be a **task metadata brief** rather than a **fully composed agent instruction prompt**. The distinction is critical for CCO:

- **Task metadata brief**: Input to Pantry; summarizes task scope, files, criteria (what Pantry uses to compose)
- **Composed agent prompt**: Output from Pantry; full instruction set with 6 mandatory steps, ready for spawn

The file at `task-fomy.md` is the metadata brief (task-metadata version also exists at `/Users/correy/projects/ant-farm/.beads/agent-summaries/_session-2bb21f22/task-metadata/fomy.md`). It is NOT a composed agent prompt ready for spawn.

---

## CCO Verdict

**FAIL: MISSING ARTIFACTS**

**Reason**: Preview files do not exist in the required location. Pantry must be spawned to create:
1. `/Users/correy/projects/ant-farm/.beads/agent-summaries/_session-2bb21f22/previews/task-fomy-preview.md` (or similar) - composed agent prompt preview
2. `/Users/correy/projects/ant-farm/.beads/agent-summaries/_session-2bb21f22/prompts/task-fomy.md` - fully composed agent prompt with all 6 mandatory steps

**Current state**:
- ✅ task-metadata/fomy.md exists (input to Pantry)
- ✅ prompts/task-fomy.md exists (but this is a brief, not a composed prompt)
- ❌ previews/ directory is empty (no preview files)
- ❌ No fully composed agent prompt with 6 mandatory steps detected

---

## Remediation

The Queen must:

1. **Spawn Pantry** (if not already spawned) per orchestration/RULES.md Step 2:
   - Template: `orchestration/templates/pantry.md`
   - Input: Task metadata files in `task-metadata/` (Scout has already written these)
   - Output: Combined prompt previews in `previews/` + full prompts in `prompts/`

2. **Re-run CCO** after Pantry completes and writes preview files to the correct location

---

## Finding Details

| Check | Status | Evidence |
|-------|--------|----------|
| Real task IDs (Check 1) | UNTESTABLE | Artifact is metadata brief, not composed prompt |
| Real file paths (Check 2) | UNTESTABLE | Artifact is metadata brief, not composed prompt |
| Root cause text (Check 3) | UNTESTABLE | Artifact is metadata brief, not composed prompt |
| Mandatory 6 steps (Check 4) | UNTESTABLE | Artifact is metadata brief, not composed prompt |
| Scope boundaries (Check 5) | UNTESTABLE | Artifact is metadata brief, not composed prompt |
| Commit instructions (Check 6) | UNTESTABLE | Artifact is metadata brief, not composed prompt |
| Line specificity (Check 7) | UNTESTABLE | Artifact is metadata brief, not composed prompt |

---

## Notes for Queen

The workflow is:
1. Scout writes task-metadata/{TASK_SUFFIX}.md ✅ COMPLETE
2. Pantry reads task-metadata and writes prompts/task-{TASK_SUFFIX}.md + previews/task-{TASK_SUFFIX}-preview.md ❌ NOT STARTED
3. CCO audits previews/task-{TASK_SUFFIX}-preview.md ⏸️ BLOCKED on step 2
4. Agents are spawned using prompts/task-{TASK_SUFFIX}.md

Progress log shows Scout completed at 2026-02-23T02:04:37Z. Pantry has not yet been spawned (no corresponding progress log entry).

**Next action**: Spawn Pantry per RULES.md Step 2, then re-run CCO.

---

**CCO Verdict**: **FAIL** — Missing artifact (empty preview directory)
**Blocks spawn?**: Yes — CCO must PASS before agents are spawned
**Resubmission path**: Pantry must run → CCO re-runs on generated previews

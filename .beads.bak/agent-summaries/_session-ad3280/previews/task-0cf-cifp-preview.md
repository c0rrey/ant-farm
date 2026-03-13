Execute feature for ant-farm-0cf, then task for ant-farm-cifp (BATCHED — sequential execution, same agent).

Step 0: Read your task context from .beads/agent-summaries/_session-ad3280/prompts/task-0cf.md
Then read .beads/agent-summaries/_session-ad3280/prompts/task-cifp.md
(Contains: affected files, root cause, acceptance criteria, scope boundaries for both tasks.)

Execute these 6 steps in order FOR EACH TASK (ant-farm-0cf first, then ant-farm-cifp):

1. **Claim**: `bd show <task-id>` + `bd update <task-id> --status=in_progress`
2. **Design** (MANDATORY): 4+ genuinely distinct approaches with tradeoffs. Document choice before coding.
3. **Implement**: Write clean, minimal code satisfying acceptance criteria.
4. **Review** (MANDATORY): Re-read EVERY changed file. Verify acceptance criteria. Assumptions audit.
5. **Commit**: `git pull --rebase && git add <changed-files> && git commit -m "<type>: <description> (<task-id>)"`
   Use conventional commit type (fix/feat/refactor/etc). Record commit hash in summary doc.
6. **Summary doc** (MANDATORY): Write to .beads/agent-summaries/_session-ad3280/summaries/<task-suffix>.md with all required sections
   (see data file for section list). Only after the summary doc is successfully written:
   `bd close <task-id>`

Complete ALL 6 steps for ant-farm-0cf (summary: .beads/agent-summaries/_session-ad3280/summaries/0cf.md) BEFORE starting ant-farm-cifp (summary: .beads/agent-summaries/_session-ad3280/summaries/cifp.md).

After all tasks in this batch:
- Run `git pull --rebase` to stack commits cleanly
- Close all tasks: `bd close ant-farm-0cf ant-farm-cifp`

SCOPE: Only edit files listed in each task's data file. Document adjacent issues, don't fix them.
Do NOT push to remote. Do NOT modify CHANGELOG/README/CLAUDE.md.

---

# Task Brief: ant-farm-0cf
**Task**: Parallelize review prompt composition with implementation via bash scripts
**Agent Type**: devops-engineer
**Summary output path**: .beads/agent-summaries/_session-ad3280/summaries/0cf.md

## Context
- **Affected files**:
  - `orchestration/templates/pantry.md:L104-180` — Section 2 (Review Mode): to be deprecated in favor of bash script assembly
  - `orchestration/RULES.md:L48-62` — Step 3b (Review): update to call slot-filling script instead of spawning review Pantry
  - `scripts/compose-review-skeletons.sh` — New file: assembles 4 review data files + Big Head consolidation file with slot markers
  - `scripts/fill-review-slots.sh` — New file: fills slot markers with commit range, changed files, task IDs, timestamp
- **Root cause**: Review prompt composition (Pantry Section 2) currently runs as a separate LLM subagent invocation after implementation finishes, adding unnecessary latency. The review prompts are formulaic — they follow rigid templates with variable slots for commit range, changed files, and task IDs. This work is mechanical text assembly, not compositional reasoning, yet it consumes a full LLM round-trip.
- **Expected behavior**: Split review prompt composition into two bash scripts called at different workflow stages. Script 1 (skeleton assembly) is called by Pantry during Section 1. Script 2 (slot filling) is called by the Queen after dirt-pushers finish. Queen context window absorbs zero template content from review prompt composition.
- **Acceptance criteria**:
  1. Pantry Section 1 invocation produces both implementation prompts AND review skeletons
  2. No second Pantry invocation is needed for review prompt composition
  3. Queen context window absorbs zero template content from review prompt composition
  4. Review prompts produced by the scripts are identical in structure to current Pantry Section 2 output
  5. Script failures surface as error messages to the Queen, not silent failures

## Scope Boundaries
Read ONLY:
- `orchestration/templates/pantry.md:L1-180` (full file, focus on Section 2: L104-180)
- `orchestration/RULES.md:L48-62` (Step 3b review section)
- `orchestration/templates/reviews.md:L1-548` (review prompt templates to replicate in scripts)
- `orchestration/templates/nitpicker-skeleton.md` (skeleton format for review previews)
- `~/.claude/orchestration/templates/big-head-skeleton.md` (skeleton format for Big Head)

Do NOT edit:
- `orchestration/templates/reviews.md` (source of truth for review content, read-only reference)
- `orchestration/templates/implementation.md` (unrelated to review composition)
- `orchestration/templates/scout.md` (unrelated)
- `orchestration/templates/checkpoints.md` (unrelated)
- `~/.claude/agents/*.md` (agent definitions are out of scope)

## Focus
Your task is ONLY to parallelize review prompt composition by creating two bash scripts and updating pantry.md + RULES.md to use them.
Do NOT fix adjacent issues you notice.
Do NOT change the content/structure of review prompts — only move their assembly from LLM to bash.

## Summary Doc Sections (all required)
1. Approaches Considered (4+ genuinely distinct)
2. Selected Approach with rationale
3. Implementation description
4. Correctness Review (per-file, with acceptance criteria verification)
5. Build/Test Validation
6. Acceptance Criteria checklist (each criterion + PASS/FAIL)

---

# Task Brief: ant-farm-cifp
**Task**: Add explicit scope fencing to Nitpicker agent definitions per review type
**Agent Type**: technical-writer
**Summary output path**: .beads/agent-summaries/_session-ad3280/summaries/cifp.md

## Context
- **Affected files**:
  - `~/.claude/agents/nitpicker.md:L1-25` — Add per-type specialization blocks with scope fences, heuristics, and severity calibration
  - `orchestration/templates/reviews.md:L86-243` — May need to reference new scope boundaries for consistency (Review 1-4 sections)
  - `orchestration/templates/pantry.md:L119-135` — Review data files section; may need a REVIEW_TYPE marker if using conditional blocks
- **Root cause**: All four Nitpicker reviewers (clarity, edge-cases, correctness, excellence) share a single agent MD file (`~/.claude/agents/nitpicker.md:L1-25`) with no review-type-specific identity. Differentiation comes entirely from the Pantry-composed data files. Each reviewer has no baked-in understanding of what is NOT its responsibility, leading to duplicate findings across reviewers that Big Head must deduplicate after the fact.
- **Expected behavior**: Add per-review-type specialization blocks to the Nitpicker agent definition(s). For each review type, define explicit 'NOT your responsibility' list referencing other three review types, type-specific heuristics, and type-specific severity calibration. Option (b) — single agent MD file with conditional sections keyed to a REVIEW_TYPE variable — is preferred for maintainability.
- **Acceptance criteria**:
  1. Each Nitpicker reviewer has explicit 'not my job' boundaries that reference the other three review types by name
  2. Type-specific severity calibration is defined (what constitutes P1/P2/P3 for each type)
  3. Big Head deduplication load is reduced — fewer cross-type duplicate findings at source
  4. Shared concerns (report format, output structure, messaging guidelines) remain in one place, not duplicated across 4 files

## Scope Boundaries
Read ONLY:
- `~/.claude/agents/nitpicker.md:L1-25` (current agent definition)
- `orchestration/templates/reviews.md:L86-243` (Review 1-4 focus areas and scope)
- `orchestration/templates/pantry.md:L104-155` (Section 2 review data file composition)
- `~/.claude/agents/big-head.md:L1-31` (understand how Big Head deduplicates, for context)

Do NOT edit:
- `~/.claude/agents/big-head.md` (separate task ant-farm-7k1 owns this)
- `orchestration/templates/implementation.md` (unrelated)
- `orchestration/templates/scout.md` (unrelated)
- `orchestration/templates/checkpoints.md` (unrelated)
- `orchestration/RULES.md` (separate task ant-farm-0cf may touch this)

## Focus
Your task is ONLY to add per-review-type scope fences, heuristics, and severity calibration to the Nitpicker agent definition(s).
Do NOT fix adjacent issues you notice.
Do NOT change Big Head's consolidation logic.
Do NOT restructure the review protocol in reviews.md beyond referencing scope boundaries.

## Summary Doc Sections (all required)
1. Approaches Considered (4+ genuinely distinct)
2. Selected Approach with rationale
3. Implementation description
4. Correctness Review (per-file, with acceptance criteria verification)
5. Build/Test Validation
6. Acceptance Criteria checklist (each criterion + PASS/FAIL)

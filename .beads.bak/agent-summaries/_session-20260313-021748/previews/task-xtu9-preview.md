Execute task for ant-farm-xtu9.

Step 0: Read your task context from .beads/agent-summaries/_session-20260313-021748/prompts/task-xtu9.md
(Format: markdown. Sections: Context, Scope Boundaries, Focus.)

Execute these 6 steps in order:

1. **Claim**: `crumb show ant-farm-xtu9` + `crumb update ant-farm-xtu9 --status=in_progress`
2. **Design** (MANDATORY) — 4+ genuinely distinct approaches with tradeoffs. Document choice before coding.
3. **Implement**: Write clean, minimal code satisfying acceptance criteria.
4. **Review** (MANDATORY) — Re-read EVERY changed file. Verify acceptance criteria. Assumptions audit.
5. **Commit**: `git pull --rebase && git add <changed-files> && git commit -m "<type>: <description> (ant-farm-xtu9)"`
   Use conventional commit type (fix/feat/refactor/etc). Record commit hash in summary doc.
6. **Summary doc** (MANDATORY) — Write to .beads/agent-summaries/_session-20260313-021748/summaries/xtu9.md with all required sections
   (see task brief for section list). Only after the summary doc is successfully written:
   `crumb close ant-farm-xtu9`

SCOPE: Only edit files listed in the task context. Document adjacent issues, don't fix them.
Do NOT push to remote. Do NOT modify CHANGELOG/README/CLAUDE.md.

---

# Task Brief: ant-farm-xtu9
**Task**: Design and write Architect agent (definition + template + skeleton)
**Agent Type**: prompt-engineer
**Summary output path**: .beads/agent-summaries/_session-20260313-021748/summaries/xtu9.md

## Context
- **Affected files**:
  - agents/architect.md (new file) -- agent definition with frontmatter: name, description, model: opus, tools
  - orchestration/templates/decomposition.md (new file) -- detailed workflow template for spec decomposition
  - orchestration/templates/architect-skeleton.md (new file) -- prompt skeleton for Architect agent
- **Root cause**: N/A -- new feature. Architect agent needed for spec decomposition into trails and crumbs.
- **Expected behavior**: Three files created: agent definition, workflow template, and prompt skeleton for the Architect agent that reads spec.md + research briefs + codebase, creates trails/crumbs via CLI, wires dependencies, assigns scope.
- **Acceptance criteria**:
  1. agents/architect.md exists with correct frontmatter (name, description, model: opus, tools list)
  2. orchestration/templates/decomposition.md contains full decomposition workflow with crumb CLI commands
  3. orchestration/templates/architect-skeleton.md contains prompt template with input file placeholders
  4. Prompt specifies 100% spec coverage requirement (every requirement maps to >=1 crumb acceptance criterion)
  5. Scope budget (5-8 files per crumb) explicitly stated and enforced
  6. Prompt includes explicit prohibitions: no code writing, no orphan crumbs, no circular deps, no vague scope, no unverifiable criteria
  7. Brownfield vs greenfield handling documented
  8. decomposition-brief.md output format specified

## Scope Boundaries
Read ONLY:
- orchestration/templates/pantry.md (reference for template/skeleton patterns)
- orchestration/templates/implementation.md (reference for dirt-pusher workflow that Architect feeds into)
- orchestration/templates/dirt-pusher-skeleton.md (reference for skeleton format conventions)
- orchestration/templates/scout.md (reference for existing agent template patterns)
- agents/ directory (reference for existing agent definition format)
- orchestration/templates/architect-skeleton.md (if partially exists from dependencies)
- Any spec.md or research brief files referenced in existing orchestration docs

Do NOT edit:
- orchestration/templates/pantry.md
- orchestration/templates/implementation.md
- orchestration/templates/dirt-pusher-skeleton.md
- orchestration/templates/scout.md
- orchestration/RULES.md
- CLAUDE.md
- CHANGELOG.md
- README.md
- Any existing agent definitions in agents/

## Focus
Your task is ONLY to design and write the Architect agent definition, decomposition workflow template, and architect prompt skeleton.
Do NOT fix adjacent issues you notice.

## Summary Doc Sections (all required)
1. Approaches Considered (4+ genuinely distinct)
2. Selected Approach with rationale
3. Implementation description
4. Correctness Review (per-file, with acceptance criteria verification)
5. Build/Test Validation
6. Acceptance Criteria checklist (each criterion + PASS/FAIL)

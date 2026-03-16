<!-- Reader: the Pantry (implementation mode). Condensed extract of implementation.md. -->
# Dirt Pusher Workflow — Pantry Reference

## The 6-Step Workflow

Every dirt pusher executes these steps in order. Task briefs you compose must instruct agents to follow them exactly:

1. **Claim** — `crumb show <id>` + `crumb update <id> --status=in_progress`
2. **Design (MANDATORY)** — 4+ genuinely distinct approaches with pros/cons; document choice before coding
3. **Implement** — write clean, minimal code satisfying acceptance criteria
4. **Correctness Review (MANDATORY)** — re-read every changed file; verify acceptance criteria; assumptions audit (3 specific failure scenarios + mitigations)
5. **Commit** — `git pull --rebase && git add <files> && git commit -m "<type>: <description> (<task-id>)"`; record commit hash in summary doc; if rebase resolved conflicts, repeat Step 4
6. **Summary Doc (MANDATORY)** — write to `{session-dir}/summaries/{task-id}.md`

## Mandatory Summary Doc Sections

Task briefs must reference all of these sections:

1. Approaches Considered (4+ genuinely distinct)
2. Selected Approach with rationale
3. Implementation description
4. Correctness Review (per-file, with acceptance criteria verification)
5. Build/Test Validation
6. Acceptance Criteria checklist (each criterion + PASS/FAIL)

## Why Steps 2, 4, and 6 Are MANDATORY

- **Step 2 (Design)**: Prevents agents from jumping to the first solution. Distinct approaches must differ in algorithm, data structure, or architectural pattern — not just cosmetic variations.
- **Step 4 (Correctness Review)**: Catching issues before commit is cheaper than review-round fixes. The assumptions audit (3 specific failure scenarios) is required — generic risks do not count.
- **Step 6 (Summary Doc)**: Incomplete summaries are rejected. Big Head and Pest Control depend on the summary for traceability.

## Scope Boundary Principle

Agents must ONLY edit files listed in their task brief. Adjacent issues found during implementation must be documented in the summary doc under "Adjacent Issues Found" — not fixed.

## Information Diet Principle

Crumbs contain pre-digested context (root cause, affected surfaces, expected behavior, fix description, acceptance criteria). Task briefs must extract and provide this context directly — do NOT tell agents to "discover the problem" or "explore the codebase."

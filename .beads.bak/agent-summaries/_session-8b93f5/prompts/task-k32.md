# Task Brief: ant-farm-k32
**Task**: MANDATORY keyword formatting inconsistent across templates
**Agent Type**: refactoring-specialist
**Summary output path**: .beads/agent-summaries/_session-8b93f5/summaries/k32.md

## Context
- **Affected files**:
  - `orchestration/templates/implementation.md:L6` — uses `**MANDATORY**` (bold, within sentence: "MANDATORY: Every spawned Dirt Pusher MUST receive ALL sections below")
  - `orchestration/templates/implementation.md:L28` — uses `(MANDATORY -- do not skip)` in step header
  - `orchestration/templates/implementation.md:L44` — uses `(MANDATORY -- do not skip)` in step header
  - `orchestration/templates/implementation.md:L53` — uses `(MANDATORY):` after bold "Assumptions audit"
  - `orchestration/templates/implementation.md:L60` — uses `**MANDATORY**:` at start of bullet
  - `orchestration/templates/implementation.md:L61` — uses `**MANDATORY -- Conditional Re-Review**:` in bold
  - `orchestration/templates/implementation.md:L64` — uses `(MANDATORY -- do not skip)` in step header
  - `orchestration/templates/implementation.md:L169-173` — uses `(MANDATORY)` in checklist items
  - `orchestration/templates/dirt-pusher-skeleton.md:L35` — uses `(MANDATORY):` after bold "Design"
  - `orchestration/templates/dirt-pusher-skeleton.md:L37` — uses `(MANDATORY):` after bold "Review"
  - `orchestration/templates/dirt-pusher-skeleton.md:L40` — uses `(MANDATORY):` after bold "Summary doc"
  - `orchestration/templates/checkpoints.md:L139` — uses `(MANDATORY keyword present)` as a verification check description
  - `orchestration/templates/checkpoints.md:L141` — uses `(MANDATORY keyword present)` as a verification check description
  - `orchestration/templates/reviews.md:L178, L212, L252, L298` — uses `## Report (MANDATORY)` as section headers
  - `orchestration/templates/reviews.md:L406` — uses `### Step 0: Verify All Reports Exist (MANDATORY GATE)` as section header
  - `orchestration/templates/reviews.md:L789` — uses `(MANDATORY):` in sentence
  - `orchestration/templates/SESSION_PLAN_TEMPLATE.md:L304` — uses `(**MANDATORY** - not done until pushed!)` in checklist
- **Root cause**: implementation.md uses plain `MANDATORY` and `(MANDATORY -- do not skip)`, dirt-pusher-skeleton uses `(MANDATORY)` inline, checkpoints uses `(MANDATORY keyword present)` as a check description, reviews uses `(MANDATORY)` and `(MANDATORY GATE)`. No consistent formatting style exists across templates.
- **Expected behavior**: All templates use one consistent formatting style for the MANDATORY keyword.
- **Acceptance criteria**:
  1. All templates use the same formatting style for the MANDATORY keyword
  2. The chosen style is documented (or implied by uniform usage)
  3. No template uses a different form of MANDATORY formatting without explanation

## Scope Boundaries
Read ONLY:
- `orchestration/templates/implementation.md:L1-175` (full file)
- `orchestration/templates/dirt-pusher-skeleton.md:L1-46` (full file)
- `orchestration/templates/checkpoints.md:L135-145` (MANDATORY keyword check lines)
- `orchestration/templates/reviews.md:L175-185, L210-215, L250-255, L295-300, L400-410, L785-795` (MANDATORY occurrences)
- `orchestration/templates/SESSION_PLAN_TEMPLATE.md:L300-310` (MANDATORY occurrence)

Do NOT edit:
- `orchestration/RULES.md` (no MANDATORY keyword usage)
- `orchestration/templates/scout.md` (no MANDATORY keyword usage)
- `orchestration/templates/pantry.md` (no MANDATORY keyword usage)
- `CLAUDE.md`, `README.md` (off-limits per process rules)

## Focus
Your task is ONLY to standardize the MANDATORY keyword formatting to one consistent style across all template files that use it.
Do NOT fix adjacent issues you notice.

## Summary Doc Sections (all required)
1. Approaches Considered (4+ genuinely distinct)
2. Selected Approach with rationale
3. Implementation description
4. Correctness Review (per-file, with acceptance criteria verification)
5. Build/Test Validation
6. Acceptance Criteria checklist (each criterion + PASS/FAIL)

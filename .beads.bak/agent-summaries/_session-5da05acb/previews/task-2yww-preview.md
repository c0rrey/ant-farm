Execute bug for ant-farm-2yww.

Step 0: Read your task context from .beads/agent-summaries/_session-5da05acb/prompts/task-2yww.md
(Format: markdown. Sections: Context, Scope Boundaries, Focus.)

Execute these 6 steps in order:

1. **Claim**: `bd show ant-farm-2yww` + `bd update ant-farm-2yww --status=in_progress`
2. **Design** (MANDATORY) — 4+ genuinely distinct approaches with tradeoffs. Document choice before coding.
3. **Implement**: Write clean, minimal code satisfying acceptance criteria.
4. **Review** (MANDATORY) — Re-read EVERY changed file. Verify acceptance criteria. Assumptions audit.
5. **Commit**: `git pull --rebase && git add <changed-files> && git commit -m "<type>: <description> (ant-farm-2yww)"`
   Use conventional commit type (fix/feat/refactor/etc). Record commit hash in summary doc.
6. **Summary doc** (MANDATORY) — Write to .beads/agent-summaries/_session-5da05acb/summaries/2yww.md with all required sections
   (see task brief for section list). Only after the summary doc is successfully written:
   `bd close ant-farm-2yww`

SCOPE: Only edit files listed in the task context. Document adjacent issues, don't fix them.
Do NOT push to remote. Do NOT modify CHANGELOG/README/CLAUDE.md.

---

# Task Brief: ant-farm-2yww
**Task**: Pantry-review deprecation not fully propagated to reader attributions
**Agent Type**: technical-writer
**Summary output path**: .beads/agent-summaries/_session-5da05acb/summaries/2yww.md

## Context
- **Affected files**:
  - orchestration/RULES.md:L47 — FORBIDDEN reads list says Pantry reads reviews.md
  - orchestration/RULES.md:L440 — Template Lookup says "read by the Pantry"
  - README.md:L252 — Information diet prose says Pantry reads reviews.md
  - README.md:L301 — Deprecated pantry-review row lacks cross-ref to replacement
  - README.md:L352 — File reference table says "The Pantry (review mode)"
  - orchestration/GLOSSARY.md:L28 — pantry-review.md listed without removal status
  - orchestration/GLOSSARY.md:L82 — Pantry role mixes active/deprecated file
  - CONTRIBUTING.md:L95 — Template inventory "Read by" mentions deprecated Pantry review mode
- **Root cause**: When pantry-review was deprecated and replaced by build-review-prompts.sh, the "who reads reviews.md" attribution was not updated in multiple reference tables and prose sections.
- **Expected behavior**: All reader attributions should name build-review-prompts.sh as the replacement. GLOSSARY Pantry role should say "Reads implementation templates" only.
- **Acceptance criteria**:
  1. No file in the repo attributes reviews.md readership to the Pantry
  2. GLOSSARY Pantry role description says "Reads implementation templates" (not "or review templates")
  3. README file reference table names build-review-prompts.sh as the reader of reviews.md

## Scope Boundaries
Read ONLY: orchestration/RULES.md:L40-50 and L435-445, README.md:L245-260 and L295-310 and L345-360, orchestration/GLOSSARY.md:L20-35 and L75-90, CONTRIBUTING.md:L90-100
Do NOT edit: orchestration/templates/pantry.md, scripts/build-review-prompts.sh, orchestration/templates/reviews.md, any template files

## Focus
Your task is ONLY to update reader attributions from "Pantry (review mode)" to "build-review-prompts.sh" in reference tables and prose sections.
Do NOT fix adjacent issues you notice.

## Summary Doc Sections (all required)
1. Approaches Considered (4+ genuinely distinct)
2. Selected Approach with rationale
3. Implementation description
4. Correctness Review (per-file, with acceptance criteria verification)
5. Build/Test Validation
6. Acceptance Criteria checklist (each criterion + PASS/FAIL)

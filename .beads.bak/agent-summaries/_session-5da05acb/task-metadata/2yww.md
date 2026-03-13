# Task: ant-farm-2yww
**Status**: success
**Title**: Pantry-review deprecation not fully propagated to reader attributions
**Type**: bug
**Priority**: P2
**Epic**: none
**Agent Type**: technical-writer
**Dependencies**: {blocks: [], blockedBy: []}

## Affected Files
- orchestration/RULES.md:47 — FORBIDDEN reads list says Pantry reads reviews.md
- orchestration/RULES.md:440 — Template Lookup says "read by the Pantry"
- README.md:252 — Information diet prose says Pantry reads reviews.md
- README.md:301 — Deprecated pantry-review row lacks cross-ref to replacement
- README.md:352 — File reference table says "The Pantry (review mode)"
- orchestration/GLOSSARY.md:28 — pantry-review.md listed without removal status
- orchestration/GLOSSARY.md:82 — Pantry role mixes active/deprecated file
- CONTRIBUTING.md:95 — Template inventory "Read by" mentions deprecated Pantry review mode

## Root Cause
When pantry-review was deprecated and replaced by build-review-prompts.sh, the "who reads reviews.md" attribution was not updated in multiple reference tables and prose sections.

## Expected Behavior
All reader attributions should name build-review-prompts.sh as the replacement. GLOSSARY Pantry role should say "Reads implementation templates" only.

## Acceptance Criteria
1. No file in the repo attributes reviews.md readership to the Pantry
2. GLOSSARY Pantry role description says "Reads implementation templates" (not "or review templates")
3. README file reference table names build-review-prompts.sh as the reader of reviews.md

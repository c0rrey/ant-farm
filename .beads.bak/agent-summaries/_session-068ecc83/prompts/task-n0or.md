# Task Brief: ant-farm-n0or
**Task**: Session 7edaafbb R1: miscellaneous P3 polish findings (7 items)
**Agent Type**: technical-writer
**Summary output path**: .beads/agent-summaries/_session-068ecc83/summaries/n0or.md

## Context
- **Affected files**:
  - orchestration/SETUP.md:L36-56 -- nested markdown code fence mismatch (RC-15c)
  - scripts/parse-progress-log.sh:L203-206 -- UNREACHABLE comment ambiguous about "normal execution" qualifier (RC-15a)
  - scripts/parse-progress-log.sh:L164-176 -- corrupt ordering causes false SESSION_COMPLETE (RC-15d, downgraded to P3)
  - orchestration/templates/reviews.md:L513-515 -- CONSTRAINT comment header inconsistent style (RC-15b)
  - scripts/compose-review-skeletons.sh:L68-74 -- extract_agent_section docstring update (from RC-1 Clarity-4 residual)
- **Root cause**: Collection of standalone P3 findings from round 1 review that do not share a root cause with any other consolidated finding. Each is a minor documentation/comment precision issue: (a) UNREACHABLE comment uses ambiguous "normal execution" qualifier, (b) CONSTRAINT comment header uses inconsistent style vs. other constraint comments, (c) nested code fences in SETUP.md are mismatched, (d) corrupt ordering comment needs clarification, (e) extract_agent_section docstring may need update.
- **Expected behavior**: Comments and documentation should accurately describe the behavior of the code they annotate.
- **Acceptance criteria**:
  1. SETUP.md:L36-56 nested code fence mismatch resolved
  2. parse-progress-log.sh:L203-206 UNREACHABLE comment clarified
  3. reviews.md:L513-515 CONSTRAINT comment style made consistent
  4. parse-progress-log.sh:L164-176 comment about corrupt ordering clarified (no code change needed, P3 doc fix)
  5. compose-review-skeletons.sh:L68-74 extract_agent_section docstring updated if not already addressed by RC-1 fix

## Scope Boundaries
Read ONLY:
- orchestration/SETUP.md:L30-60
- scripts/parse-progress-log.sh:L155-210
- orchestration/templates/reviews.md:L508-525
- scripts/compose-review-skeletons.sh:L65-80

Do NOT edit:
- Any file outside the 5 listed above
- README.md (managed by ant-farm-6jxn and ant-farm-oc9v)
- orchestration/RULES.md (managed by ant-farm-oc9v)
- orchestration/GLOSSARY.md (managed by ant-farm-oc9v)
- orchestration/templates/pantry.md (managed by ant-farm-6jxn)

## Focus
Your task is ONLY to fix 5 minor documentation/comment precision issues across SETUP.md, parse-progress-log.sh, reviews.md, and compose-review-skeletons.sh. These are all P3 polish items -- comment clarifications and doc formatting fixes. No functional code changes needed.
Do NOT fix adjacent issues you notice.

## Summary Doc Sections (all required)
1. Approaches Considered (4+ genuinely distinct)
2. Selected Approach with rationale
3. Implementation description
4. Correctness Review (per-file, with acceptance criteria verification)
5. Build/Test Validation
6. Acceptance Criteria checklist (each criterion + PASS/FAIL)

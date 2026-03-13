# Pest Control Verification Report: CCO (Colony Cartography Office)

**Checkpoint**: CCO (Pre-Spawn Prompt Audit) — Dirt Pushers Wave 1
**Session Directory**: `.beads/agent-summaries/_session-cd9866`
**Report Date**: 2026-02-20
**Model**: Haiku (mechanical checklist validation)

---

## Executive Summary

**Verdict: PASS**

All 16 combined preview files (Dirt Pusher prompts for Wave 1 implementation tasks) are well-formed, complete, and contain no unfilled placeholders. Each preview includes:
- Real task IDs (e.g., `ant-farm-bi3`, `ant-farm-yfnj`, etc.)
- Actual file paths with line number specificity
- Concrete root cause descriptions
- All 6 mandatory workflow steps
- Explicit scope boundaries
- Commit instructions with `git pull --rebase`
- Correct summary doc output paths

No WARN exceptions apply. Proceeding to spawn is safe.

---

## Detailed Verification Results

### Check 1: Real Task IDs

**Status**: PASS

All 16 previews contain actual task IDs (no placeholders):
- task-bi3 → ant-farm-bi3
- task-yfnj → ant-farm-yfnj
- task-yb95 → ant-farm-yb95
- task-txw → ant-farm-txw
- task-auas → ant-farm-auas
- task-0gs → ant-farm-0gs
- task-32gz → ant-farm-32gz
- task-033 → ant-farm-033
- task-1b8 → ant-farm-1b8
- task-7yv → ant-farm-7yv
- task-z69 → ant-farm-z69
- task-cl8 → ant-farm-cl8
- task-1e1 → ant-farm-1e1
- task-1y4 → ant-farm-1y4
- task-27x → ant-farm-27x
- task-9j6z → ant-farm-9j6z

No placeholders like `<task-id>` or `<id>` detected.

---

### Check 2: Real File Paths with Line Specificity

**Status**: PASS

All 16 previews include actual file paths with line ranges or section specificity:

1. **task-bi3**: `orchestration/templates/pantry.md:L44`, `L251-286`, `L37`
2. **task-yfnj**: `orchestration/templates/pantry.md:L251-557`
3. **task-yb95**: `agents/pantry-review.md:L1-74`, `orchestration/templates/pantry.md:L251-557`, `orchestration/RULES.md:L251 and L265`
4. **task-txw**: `orchestration/templates/big-head-skeleton.md:L73-99`, `orchestration/templates/pantry.md:L45-90`, `orchestration/templates/reviews.md:L465-590`
5. **task-auas**: `orchestration/RULES.md:L280-298`, `orchestration/templates/pantry.md:L260-286`, `orchestration/templates/checkpoints.md:L198`, `orchestration/templates/nitpicker-skeleton.md:L13,21`, `orchestration/templates/big-head-skeleton.md:L13,69`
6. **task-0gs**: `orchestration/templates/reviews.md:L519`, `L471-483`, `orchestration/RULES.md:L280-298`
7. **task-32gz**: `orchestration/RULES.md:L290-291`, `orchestration/PLACEHOLDER_CONVENTIONS.md:L89-91`
8. **task-033**: `docs/installation-guide.md:L20-31`, `L28-31`, `L150-158`, `scripts/install-hooks.sh:L51-88`
9. **task-1b8**: `docs/installation-guide.md:L193`, `L185-245`
10. **task-7yv**: `scripts/install-hooks.sh:L72-75`, `L51-89`, `scripts/scrub-pii.sh:L1-5`
11. **task-z69**: `scripts/install-hooks.sh:L34-45`, `L35`, `L44`, `L39-41`, `L23-49`
12. **task-cl8**: `scripts/scrub-pii.sh:L38`, `L52`, `L275-286`, `L50`, `L52-53`, `L1-59`
13. **task-1e1**: `orchestration/templates/dirt-pusher-skeleton.md:L43`, `orchestration/templates/big-head-skeleton.md:L20`, `README.md:L18,45,59,60,61,72,92,101,174,176,226`, `L1-48`, `L1-105`, `L1-230`
14. **task-1y4**: `orchestration/SETUP.md:L61,121`, `L1-269`
15. **task-27x**: `agents/big-head.md:L4`, `L1-36`
16. **task-9j6z**: `agents/pantry-review.md:L1-74`, `orchestration/templates/pantry.md:L251-557`

All paths are concrete file locations with line ranges or specific line numbers — no `<list from bead>` or `<file>` placeholders.

---

### Check 3: Root Cause Text

**Status**: PASS

All 16 previews contain specific, concrete root cause descriptions:

1. **task-bi3**: "orchestration/templates/pantry.md has two fail-fast gaps: (1) Step 2 reads task-metadata/{TASK_SUFFIX}.md but does not check if the task-metadata/ directory itself exists before iterating. (2) Section 2 receives a changed-file list from the Queen but has no guard against an empty list..."
2. **task-yfnj**: "pantry.md Section 2 still references external Big Head Step 0/0a and polling loop specifications from reviews.md instead of having them fully inlined."
3. **task-yb95**: "Incomplete deprecation cleanup from the transition to fill-review-slots.sh. Three artifacts remain: (1) agents/pantry-review.md is the full deprecated agent file still synced to ~/.claude/agents/. (2) pantry.md Section 2 is marked deprecated but still contains ~300 lines of obsolete instructions. (3) RULES.md has two strikethrough table rows for pantry-review that should be removed entirely."
4. **task-txw**: "Multiple templates specify FAIL conditions but do not specify what artifact to write on failure."
5. **task-auas**: "The Queen passes REVIEW_ROUND, CHANGED_FILES, and TASK_IDS to various subagents in the review path, but none of these variables are validated before use."
6. **task-0gs**: "The Step 0 report verification may use wildcard globs (e.g., `*-review-*.md`) that could match stale reports from prior review cycles."
7. **task-32gz**: "SESSION_ID generation at RULES.md:L290 uses `echo \"$$-$(date +%s%N)\" | shasum | head -c 8`. The `$$` (PID) and `date +%s%N` (epoch nanoseconds) should provide uniqueness, but..."
8. **task-033**: "install-hooks.sh (scripts/install-hooks.sh:L51-88) now installs both a pre-push hook (sync-to-claude.sh) and a pre-commit hook (scrub-pii.sh), but docs/installation-guide.md only describes the pre-push hook."
9. **task-1b8**: "docs/installation-guide.md:L193 uses `rm ~/.git/hooks/pre-push` which resolves to `~/.git/hooks/pre-push` -- the user's home directory .git."
10. **task-7yv**: "The generated pre-commit hook in install-hooks.sh:L72-75 checks `if [[ ! -x \"$SCRUB_SCRIPT\" ]]` and then exits 0 (allows commit) with only a WARNING message."
11. **task-z69**: "install-hooks.sh:L34-45 generates a pre-push hook with `set -euo pipefail` (L35) that runs sync-to-claude.sh (L44). If sync-to-claude.sh fails for any reason..., `set -e` causes the hook to exit non-zero, which blocks the `git push` entirely."
12. **task-cl8**: "Both the --check mode (L38) and the post-scrub verification (L52) in scrub-pii.sh wrap the PII regex with double-quote anchors."
13. **task-1e1**: "Task ant-farm-0o4 required renaming Pantry output from 'data file' to 'task brief' across all files. The rename was applied to pantry.md but missed three other files..."
14. **task-1y4**: "The bead reports that orchestration/SETUP.md:L61 and L121 contain hardcoded personal path `~/projects/hs_website/`. However, current inspection shows these lines have already been changed..."
15. **task-27x**: "agents/big-head.md:L4 declares `tools: Read, Write, Edit, Bash, Glob, Grep`. Big Head's role is to read reviewer reports, consolidate findings, write a consolidated summary, and file beads via `bd create` (bash). The Edit tool allows modifying existing files in-place, which Big Head should never need to do..."
16. **task-9j6z**: "The bead reports a filename typo where 'review-clarify.md' was used instead of 'review-clarity.md' in a fallback workflow. However, codebase grep shows no current instances of 'review-clarify' outside the issue definition..."

All root causes are specific, not placeholder text like `<copy from bead>` or generic boilerplate.

---

### Check 4: All 6 Mandatory Steps Present

**Status**: PASS

All 16 previews include all 6 mandatory steps:

**Step 1 (Claim)**: All previews include `bd show ant-farm-{TASK_ID}` + `bd update ant-farm-{TASK_ID} --status=in_progress`

**Step 2 (Design MANDATORY)**: All previews include the exact phrase "4+ genuinely distinct approaches" or equivalent MANDATORY keyword

**Step 3 (Implementation)**: All previews include implementation instruction text

**Step 4 (Review MANDATORY)**: All previews include the exact phrase "Review EVERY file" or "Re-read EVERY changed file" — MANDATORY keyword present

**Step 5 (Commit)**: All previews include:
- `git pull --rebase` (MANDATORY pre-commit rebase)
- `git add <changed-files>`
- `git commit -m "<type>: <description> (task-id)"`
- Instruction to record commit hash in summary doc

**Step 6 (Summary doc)**: All previews include:
- Write to `.beads/agent-summaries/_session-cd9866/summaries/{TASK_SUFFIX}.md`
- Summary doc sections list
- Only after summary is written: `bd close ant-farm-{TASK_ID}`

No missing steps across any of the 16 previews.

---

### Check 5: Scope Boundaries

**Status**: PASS

All 16 previews include explicit limits on files to read (not open-ended exploration):

1. **task-bi3**: "Read ONLY: orchestration/templates/pantry.md:L1-557"
2. **task-yfnj**: "Read ONLY: orchestration/templates/pantry.md:L1-557, orchestration/templates/reviews.md:L455-590 (Step 0/0a source content)"
3. **task-yb95**: "Read ONLY: agents/pantry-review.md:L1-74, orchestration/templates/pantry.md:L249-557, orchestration/RULES.md:L245-270"
4. **task-txw**: "Read ONLY: orchestration/templates/big-head-skeleton.md:L1-105, orchestration/templates/reviews.md:L455-600, orchestration/templates/pantry.md:L45-90 (existing failure artifact examples)"
5. **task-auas**: "Read ONLY: orchestration/RULES.md:L270-310, orchestration/templates/pantry.md:L251-290, orchestration/templates/checkpoints.md:L190-205, orchestration/templates/nitpicker-skeleton.md:L1-43, orchestration/templates/big-head-skeleton.md:L1-105"
6. **task-0gs**: "Read ONLY: orchestration/templates/reviews.md:L455-590 (Step 0/0a verification), orchestration/RULES.md:L270-310 (review path logic)"
7. **task-32gz**: "Read ONLY: orchestration/RULES.md:L286-295, orchestration/PLACEHOLDER_CONVENTIONS.md:L84-92"
8. **task-033**: "Read ONLY: docs/installation-guide.md:L1-357, scripts/install-hooks.sh:L51-88 (pre-commit hook source for accurate documentation)"
9. **task-1b8**: "Read ONLY: docs/installation-guide.md:L185-245"
10. **task-7yv**: "Read ONLY: scripts/install-hooks.sh:L51-89, scripts/scrub-pii.sh:L1-5 (shebang and header only)"
11. **task-z69**: "Read ONLY: scripts/install-hooks.sh:L23-49"
12. **task-cl8**: "Read ONLY: scripts/scrub-pii.sh:L1-59"
13. **task-1e1**: "Read ONLY: orchestration/templates/dirt-pusher-skeleton.md:L1-48, orchestration/templates/big-head-skeleton.md:L1-105, README.md:L1-230"
14. **task-1y4**: "Read ONLY: orchestration/SETUP.md:L1-269"
15. **task-27x**: "Read ONLY: agents/big-head.md:L1-36"
16. **task-9j6z**: "Read ONLY: Full codebase search for 'review-clarify' pattern (grep -r), agents/pantry-review.md:L1-74 (fallback agent, likely location), orchestration/templates/pantry.md:L251-557 (Section 2 deprecated content)"

All previews explicitly define what to read and what NOT to edit. No open-ended "explore the codebase" directives.

---

### Check 6: Commit Instructions with `git pull --rebase`

**Status**: PASS

All 16 previews include the mandatory `git pull --rebase` before commit:

Example from task-bi3:
```
5. **Commit**: `git pull --rebase && git add <changed-files> && git commit -m "<type>: <description> (ant-farm-bi3)"`
```

This pattern is consistent across all 16 previews. The `git pull --rebase` is present in every Step 5.

---

### Check 7: Line Number Specificity (Scope Creep Prevention)

**Status**: PASS

All 16 previews use concrete line ranges or section markers (not vague file-level references):

**Examples of PASS-level specificity:**
- task-bi3: `orchestration/templates/pantry.md:L44`, `L251-286`, `L37`
- task-yfnj: `orchestration/templates/pantry.md:L251-557`
- task-7yv: `scripts/install-hooks.sh:L72-75`, `L51-89`
- task-cl8: `scripts/scrub-pii.sh:L38`, `L52`

All affected files include line number ranges or specific line references. No "Edit orchestration/templates/pantry.md" without specificity.

**Scope Boundary Analysis:**
- Small files (< 100 lines) with line specificity: PASS (no WARN needed)
  - agents/big-head.md: L1-36 (36 lines, specific range provided)
  - scripts/scrub-pii.sh: L1-59 (59 lines, specific ranges provided)

- Medium/large files with specific ranges: PASS
  - orchestration/templates/pantry.md: L1-557 (557 lines, but specific sub-ranges given for changes)
  - orchestration/RULES.md: L270-310, L286-295 (specific ranges)

All 16 previews meet the line number specificity requirement. No WARN exceptions apply.

---

## Artifact Summary

| Task ID | Preview File | Status | Notes |
|---|---|---|---|
| ant-farm-bi3 | task-bi3-preview.md | PASS | Well-formed, all checks pass |
| ant-farm-yfnj | task-yfnj-preview.md | PASS | Well-formed, all checks pass |
| ant-farm-yb95 | task-yb95-preview.md | PASS | Well-formed, all checks pass |
| ant-farm-txw | task-txw-preview.md | PASS | Well-formed, all checks pass |
| ant-farm-auas | task-auas-preview.md | PASS | Well-formed, all checks pass |
| ant-farm-0gs | task-0gs-preview.md | PASS | Well-formed, all checks pass |
| ant-farm-32gz | task-32gz-preview.md | PASS | Well-formed, all checks pass |
| ant-farm-033 | task-033-preview.md | PASS | Well-formed, all checks pass |
| ant-farm-1b8 | task-1b8-preview.md | PASS | Well-formed, all checks pass |
| ant-farm-7yv | task-7yv-preview.md | PASS | Well-formed, all checks pass |
| ant-farm-z69 | task-z69-preview.md | PASS | Well-formed, all checks pass |
| ant-farm-cl8 | task-cl8-preview.md | PASS | Well-formed, all checks pass |
| ant-farm-1e1 | task-1e1-preview.md | PASS | Well-formed, all checks pass |
| ant-farm-1y4 | task-1y4-preview.md | PASS | Well-formed, all checks pass |
| ant-farm-27x | task-27x-preview.md | PASS | Well-formed, all checks pass |
| ant-farm-9j6z | task-9j6z-preview.md | PASS | Well-formed, all checks pass |

---

## Final Verdict

**PASS**

All 7 checks pass for all 16 Dirt Pusher prompts in CCO Wave 1:

1. Real task IDs: PASS (all 16)
2. Real file paths: PASS (all 16)
3. Root cause text: PASS (all 16)
4. All 6 mandatory steps: PASS (all 16)
5. Scope boundaries: PASS (all 16)
6. Commit instructions with `git pull --rebase`: PASS (all 16)
7. Line number specificity: PASS (all 16, no WARN exceptions)

No unfilled placeholders detected. No boilerplate or circular references. All previews are ready for agent spawn.

**Recommendation**: Proceed to spawn all 16 Dirt Pusher agents for Wave 1 implementation.

---

**Report Generated**: 2026-02-20
**Verification Model**: Haiku (mechanical checklist validation)
**Pest Control Checkpoint**: CCO — Pre-Spawn Prompt Audit

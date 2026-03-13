# Pest Control -- CCO Pre-Spawn Prompt Audit (Implementation Wave 1)

**Checkpoint**: Colony Cartography Office (CCO)
**Scope**: 7 Dirt Pusher previews for session _session-8ae30b, Wave 1
**Date**: 2026-02-20

---

## Audit Summary

| Task | Check 1: Real IDs | Check 2: Real Paths | Check 3: Root Cause | Check 4: 6 Steps | Check 5: Scope | Check 6: git pull --rebase | Check 7: Line Specificity | Verdict |
|------|-------------------|---------------------|---------------------|-------------------|----------------|---------------------------|--------------------------|---------|
| 7qp  | PASS | PASS | PASS | PASS | PASS | PASS | PASS | **PASS** |
| s2g  | PASS | PASS | PASS | PASS | PASS | PASS | PASS | **PASS** |
| 3mk  | PASS | PASS | PASS | PASS | PASS | PASS | WARN | **PASS** |
| 7ob  | PASS | PASS | PASS | PASS | PASS | PASS | PASS | **PASS** |
| mx0  | PASS | PASS | PASS | PASS | PASS | PASS | PASS | **PASS** |
| 7hl  | PASS | PASS | PASS | PASS | PASS | PASS | PASS | **PASS** |
| jae  | PASS | PASS | PASS | PASS | PASS | PASS | WARN | **PASS** |

**Overall Verdict: PASS** -- All 7 previews pass all mandatory checks. Two WARNs on line specificity noted but not blocking.

---

## Per-Preview Detail

### task-7qp (ant-farm-7qp): Timestamp ownership conflict

**Check 1 - Real task IDs**: PASS
- Task ID `ant-farm-7qp` appears 5 times in the preview (bd show, bd update, bd close, commit message, summary doc path).

**Check 2 - Real file paths**: PASS
- `~/.claude/orchestration/templates/pantry.md:L106,L115` -- verified: L106 contains "review timestamp (YYYYMMDD-HHMMSS format)" in Section 2 input spec, L115 says "Use the review timestamp provided by the Queen"
- `~/.claude/agents/pantry-review.md:L38-40` -- verified: L38-40 says "Generate ONE timestamp"
- `~/.claude/orchestration/templates/reviews.md:L247` -- referenced for timestamp ownership
- `~/.claude/orchestration/RULES.md:L48-62` -- verified: Step 3b content, does not explicitly instruct Queen to generate timestamp

**Check 3 - Root cause text**: PASS
- Specific: "Three files give contradictory instructions about who generates the review timestamp. pantry.md says use the Queen's timestamp, pantry-review.md says generate one, reviews.md says the Queen generates it, but RULES.md Step 3b does not instruct the Queen to do so."

**Check 4 - All 6 mandatory steps**: PASS
- Step 1: `bd show ant-farm-7qp` + `bd update ant-farm-7qp --status=in_progress` -- present
- Step 2: "4+ genuinely distinct approaches" -- MANDATORY keyword present ("Design (MANDATORY)")
- Step 3: "Write clean, minimal code satisfying acceptance criteria" -- present
- Step 4: "Re-read EVERY changed file" -- MANDATORY keyword present ("Review (MANDATORY)")
- Step 5: `git pull --rebase && git add <changed-files> && git commit` -- present
- Step 6: Write summary doc to `.beads/agent-summaries/_session-8ae30b/summaries/7qp.md` -- present

**Check 5 - Scope boundaries**: PASS
- Explicit "Read ONLY" list of 4 files
- Explicit "Do NOT edit" list covering out-of-scope sections
- "Do NOT fix adjacent issues you notice" instruction present

**Check 6 - Commit instructions**: PASS
- `git pull --rebase` explicitly present in Step 5

**Check 7 - Line number specificity**: PASS
- `pantry.md:L106,L115` -- specific lines
- `pantry-review.md:L38-40` -- specific range
- `reviews.md:L247` -- specific line
- `RULES.md:L48-62` -- specific range
- Scope boundaries further narrow: "focus on L106-115", "focus on L38-40", "focus on L247", "focus on L48-62 Step 3b"

---

### task-s2g (ant-farm-s2g): Circular reference in Pantry Big Head instructions

**Check 1 - Real task IDs**: PASS
- Task ID `ant-farm-s2g` appears 5 times (bd show, bd update, bd close, commit, summary path).

**Check 2 - Real file paths**: PASS
- `~/.claude/orchestration/templates/pantry.md:L137-145` -- verified: Section 2 Step 4 "Compose Big Head Consolidation Data File" with "See also" directive at L139
- `~/.claude/orchestration/templates/reviews.md:L320-469` -- referenced Big Head Consolidation Protocol section

**Check 3 - Root cause text**: PASS
- Specific: "pantry.md Section 2 Step 4 (L139) contains a 'See also' directive telling the Pantry to read reviews.md Big Head Consolidation Protocol before composing the Big Head data file. But pantry.md Section 2 IS the review mode instructions, so the Pantry is already reading pantry.md, which says 'read reviews.md', which may reference pantry.md."

**Check 4 - All 6 mandatory steps**: PASS
- All 6 steps present with correct structure and MANDATORY keywords.

**Check 5 - Scope boundaries**: PASS
- "Read ONLY" restricted to pantry.md and reviews.md
- "Do NOT edit" lists: pantry.md Section 1, Section 3; reviews.md Reviews 1-4 and Nitpicker Report Format; any other files

**Check 6 - Commit instructions**: PASS
- `git pull --rebase` present in Step 5

**Check 7 - Line number specificity**: PASS
- `pantry.md:L137-145` -- specific range
- `reviews.md:L320-469` -- specific range
- Scope further narrows: "focus on L137-145, Section 2 Step 4" and "focus on L320-469, Big Head Consolidation Protocol"

---

### task-3mk (ant-farm-3mk): TeamCreate fallback path

**Check 1 - Real task IDs**: PASS
- Task ID `ant-farm-3mk` appears 5 times.

**Check 2 - Real file paths**: PASS
- `~/.claude/orchestration/templates/reviews.md:L33-35` -- verified: L33 contains "TeamCreate (NOT the Task tool)" and L35 contains "CRITICAL: Reviews MUST use Agent Teams"

**Check 3 - Root cause text**: PASS
- Specific: "reviews.md mandates TeamCreate for the Nitpicker review workflow (L33 and L35) but does not specify what to do if the runtime environment cannot create teams or messaging fails. Claude Code supports only one TeamCreate per session (documented in MEMORY.md)..."

**Check 4 - All 6 mandatory steps**: PASS
- All 6 steps present with MANDATORY keywords.

**Check 5 - Scope boundaries**: PASS
- "Read ONLY" restricted to `reviews.md` with focus on L30-72
- "Do NOT edit" lists 5 specific sections of reviews.md (Transition Gate, Reviews 1-4, Nitpicker Report Format, Big Head Consolidation, After Consolidation)

**Check 6 - Commit instructions**: PASS
- `git pull --rebase` present in Step 5

**Check 7 - Line number specificity**: WARN
- Affected file: `reviews.md:L33-35` -- specific range, good
- Read scope: "focus on L30-72 Agent Teams Protocol section" -- acceptable, this is a targeted section
- However, the "Do NOT edit" boundaries use line ranges (L1-28, L86-243, L245-318, L320-469, L471-533) which define where NOT to go but do not give a precise line range for what TO add. The task is to ADD a new fallback section, so the insertion point is implicitly "within L30-72" -- acceptable for an additive task.

---

### task-7ob (ant-farm-7ob): RULES.md pantry.md section references

**Check 1 - Real task IDs**: PASS
- Task ID `ant-farm-7ob` appears 5 times.

**Check 2 - Real file paths**: PASS
- `~/.claude/orchestration/RULES.md:L33-34` -- verified: L33 says "Spawn the Pantry (`pantry-impl`) for data files + combined previews" and L34 says "templates/pantry.md"
- `~/.claude/orchestration/RULES.md:L55` -- verified: L55 says "spawn the Pantry (`pantry-review`) for review prompts"

**Check 3 - Root cause text**: PASS
- Specific: "pantry-impl.md references 'pantry.md, Section 1' and pantry-review.md references 'pantry.md, Section 2', but RULES.md Steps 2 and 3b just say 'templates/pantry.md' (L34) and 'the Pantry (pantry-review)' (L55) without section numbers."

**Check 4 - All 6 mandatory steps**: PASS
- All 6 steps present with MANDATORY keywords.

**Check 5 - Scope boundaries**: PASS
- "Read ONLY" restricted to RULES.md (L33-34, L48-62) and pantry.md (L12, L104 for headings)
- "Do NOT edit" lists RULES.md Steps 0,1,3,4,5,6 and several sections; pantry.md read only

**Check 6 - Commit instructions**: PASS
- `git pull --rebase` present in Step 5

**Check 7 - Line number specificity**: PASS
- `RULES.md:L33-34` -- specific range
- `RULES.md:L55` -- specific line (note: the preview says "L55" in root cause, and scope says "L48-62 Step 3b")
- `pantry.md` L12 and L104 -- specific lines for section headings
- Edit scope further restricted: "RULES.md Steps 0, 1, 3, 4, 5, 6" excluded, meaning only Steps 2 and 3b editable

---

### task-mx0 (ant-farm-mx0): Redundant prompts/ directory creation

**Check 1 - Real task IDs**: PASS
- Task ID `ant-farm-mx0` appears 5 times.

**Check 2 - Real file paths**: PASS
- `~/.claude/orchestration/RULES.md:L122` -- verified: `mkdir -p ${SESSION_DIR}/{task-metadata,previews,prompts,pc,summaries}`
- `~/.claude/orchestration/templates/pantry.md:L119` -- verified: "Create the prompts directory if needed: `{session-dir}/prompts/`"

**Check 3 - Root cause text**: PASS
- Specific: "RULES.md Step 0 (L122) creates the prompts/ directory via brace expansion in mkdir. pantry.md Review Mode Step 3 (L119) also says 'Create the prompts directory if needed.' The redundancy is harmless (mkdir -p is idempotent) but creates confusion about who owns directory creation."

**Check 4 - All 6 mandatory steps**: PASS
- All 6 steps present with MANDATORY keywords.

**Check 5 - Scope boundaries**: PASS
- "Read ONLY" restricted to pantry.md (L119) and RULES.md (L122)
- "Do NOT edit" RULES.md, pantry.md Section 1, Section 3, any other files

**Check 6 - Commit instructions**: PASS
- `git pull --rebase` present in Step 5

**Check 7 - Line number specificity**: PASS
- `RULES.md:L122` -- specific line
- `pantry.md:L119` -- specific line
- Scope further narrows: "focus on L119, Review Mode Step 3" and "focus on L122, Session Directory section"

---

### task-7hl (ant-farm-7hl): Align landing instructions CLAUDE.md vs AGENTS.md

**Check 1 - Real task IDs**: PASS
- Task ID `ant-farm-7hl` appears 5 times.

**Check 2 - Real file paths**: PASS
- `~/.claude/CLAUDE.md:L50-79` -- Landing the Plane section
- `/Users/correy/projects/ant-farm/AGENTS.md:L15-40` -- Landing the Plane section
- Both files confirmed to exist on disk

**Check 3 - Root cause text**: PASS
- Specific: "CLAUDE.md includes a Review-findings gate as Step 3 (L60: 'If reviews ran and found P1 issues, present findings to user before proceeding') and has 8 landing steps. AGENTS.md omits this review gate entirely and has only 7 steps..."

**Check 4 - All 6 mandatory steps**: PASS
- All 6 steps present with MANDATORY keywords.

**Check 5 - Scope boundaries**: PASS
- "Read ONLY" restricted to CLAUDE.md (L50-79) and AGENTS.md (L15-40)
- "Do NOT edit" lists CLAUDE.md sections above Landing the Plane and AGENTS.md Quick Reference

**Check 6 - Commit instructions**: PASS
- `git pull --rebase` present in Step 5

**Check 7 - Line number specificity**: PASS
- `CLAUDE.md:L50-79` -- specific range
- `AGENTS.md:L15-40` -- specific range
- Scope narrows: "focus on L50-79, Landing the Plane section" and "focus on L15-40, Landing the Plane section"

---

### task-jae (ant-farm-jae): Dangling cross-reference in checkpoints.md

**Check 1 - Real task IDs**: PASS
- Task ID `ant-farm-jae` appears 5 times.

**Check 2 - Real file paths**: PASS
- `~/.claude/orchestration/templates/checkpoints.md:L55,L230` -- referenced with "Pest Control Overview" cross-references
- File confirmed to exist; L55 verified to contain "See 'Pest Control Overview' section above"

**Check 3 - Root cause text**: PASS
- Specific: "The task metadata reports three locations in checkpoints.md referencing a section titled 'Pest Control: The Verification Subagent' that does not exist. The closest match is 'Pest Control Overview' (L9). NOTE: The current file content at L67, L243, L300 does not contain this exact string."
- Notably, the root cause is honest about uncertainty: "The agent must verify the current state of the file -- the dangling references may have been partially fixed or the line numbers may have shifted."

**Check 4 - All 6 mandatory steps**: PASS
- All 6 steps present with MANDATORY keywords.

**Check 5 - Scope boundaries**: PASS
- "Read ONLY" restricted to checkpoints.md with instruction to grep for remaining references
- "Do NOT edit" lists: checkpoint verification logic, Pest Control Overview content (L9-37) beyond heading rename

**Check 6 - Commit instructions**: PASS
- `git pull --rebase` present in Step 5

**Check 7 - Line number specificity**: WARN
- Affected file references `checkpoints.md:L55,L230` -- specific lines provided
- However, the scope says "full file -- grep for 'Verification Subagent'" which is necessarily open-ended because the task is to find and fix ALL dangling references wherever they occur. The preview compensates by listing known locations (L55, L230, L67, L243, L300) and instructing grep verification.
- This is acceptable for a search-and-fix task where the exact locations are uncertain.

---

## Cross-Preview Conflict Analysis

Checked for file overlap conflicts between the 7 tasks:

| File | Tasks that touch it |
|------|-------------------|
| `pantry.md` | 7qp (L106,L115), s2g (L137-145), mx0 (L119) |
| `reviews.md` | 7qp (L247), s2g (L320-469), 3mk (L33-35) |
| `RULES.md` | 7qp (L48-62), 7ob (L33-34, L55) |
| `checkpoints.md` | jae (L55, L230) |
| `CLAUDE.md` | 7hl (L50-79) |
| `AGENTS.md` | 7hl (L15-40) |
| `pantry-review.md` | 7qp (L38-40) |

**Potential conflicts**:
- **pantry.md**: 7qp touches L106-115, s2g touches L137-145, mx0 touches L119. The ranges L106-115 (7qp) and L119 (mx0) are close but non-overlapping (4 lines apart). s2g's L137-145 is well separated. If 7qp or mx0 adds or removes lines before L119/L137, it could shift line numbers for later tasks. This is a concurrency risk but the ranges are currently non-overlapping. **LOW RISK** -- tasks target distinct sections.
- **reviews.md**: 7qp touches L247, s2g touches L320-469, 3mk touches L33-35. All three ranges are well separated. **NO CONFLICT**.
- **RULES.md**: 7qp touches L48-62, 7ob touches L33-34 and L55. L55 falls within 7qp's range (L48-62). **MEDIUM RISK** -- 7qp may modify the Step 3b area where 7ob also needs to add section references. However, 7qp's focus is on timestamp generation instruction while 7ob's focus is on pantry.md section number references -- they target different aspects of the same lines.

**Recommendation**: Tasks 7qp and 7ob both touch RULES.md Step 3b (L48-62). If spawned in the same wave, the second to commit may hit a merge conflict or overwrite the first's changes. The Queen should be aware of this overlap. The previews themselves are correctly scoped, so this is a scheduling concern, not a prompt defect.

---

## Verdict

**OVERALL: PASS**

All 7 previews pass all 7 CCO checks. Two non-blocking WARNs on line specificity for tasks 3mk and jae are acceptable given the nature of those tasks (additive section and grep-based search respectively). One scheduling advisory noted for the RULES.md overlap between tasks 7qp and 7ob.

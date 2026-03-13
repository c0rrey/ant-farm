<!-- Pest Control: Colony Cartography Office (CCO) Pre-Spawn Audit -->
# CCO Verification Report: Wave 3 Dirt Pushers

**Session**: `_session-8b93f5`
**Timestamp**: 2026-02-20-001200
**Auditor**: Pest Control (Haiku)
**Checkpoint**: CCO (Pre-Spawn Prompt Audit)

---

## Tasks Audited

- ant-farm-8jg: Standardize agent name casing and article usage
- ant-farm-81y: Add inline acronym expansions to architecture diagram
- ant-farm-x0m: Wave concept definition and cross-reference

---

## Verification Results

### Task 8jg: Standardize agent name casing and article usage

| Criterion | Status | Evidence |
|-----------|--------|----------|
| 1. Real task IDs | PASS | Contains `ant-farm-8jg` (not placeholders) |
| 2. Real file paths | PASS | Lists specific files with line numbers: `RULES.md:L16,L21,L25,L31,L37,L51,L60,L70-71,L74,L91,L98,L100-101,L103-106,L109,L113,L140,L146,L148,L167,L175-177,L205,L210-212,L214,L223-224,L226,L228,L230,L242,L257` |
| 3. Root cause text | PASS | "Agent names are capitalized and articled inconsistently across the codebase: 'the Queen' / 'Queen' / 'The Queen', 'the Nitpickers' / 'Nitpicker team', 'Big Head' (always title case)." |
| 4. All 6 mandatory steps | PASS | Step 1: `bd show`/`bd update`; Step 2: "Design (MANDATORY): 4+ genuinely distinct approaches"; Step 3: "Implement"; Step 4: "Review (MANDATORY): Re-read EVERY changed file"; Step 5: "Commit" with `git pull --rebase`; Step 6: Summary doc to `.beads/agent-summaries/_session-8b93f5/summaries/8jg.md` |
| 5. Scope boundaries | PASS | Explicit "Read ONLY:" list with 11 files, "Do NOT edit:" list with 4 categories |
| 6. Commit instructions | PASS | Includes `git pull --rebase && git add <changed-files> && git commit...` |
| 7. Line number specificity | PASS | All file references include specific line numbers or ranges (e.g., `L16,L21,L25`), not vague file-level scopes |

**Task 8jg Verdict**: **PASS**

---

### Task 81y: Add inline acronym expansions to architecture diagram

| Criterion | Status | Evidence |
|-----------|--------|----------|
| 1. Real task IDs | PASS | Contains `ant-farm-81y` (not placeholders) |
| 2. Real file paths | PASS | Specific file reference: `README.md:L9-27` with explanation that first expansions appear later at L61, L105, L106, L165 |
| 3. Root cause text | PASS | "The README architecture diagram uses CCO, WWD, DMVDC, and CCB without inline expansions. Full names appear much later in the document (38-145 lines after first use)." |
| 4. All 6 mandatory steps | PASS | Step 1: `bd show`/`bd update`; Step 2: "Design (MANDATORY): 4+ genuinely distinct approaches"; Step 3: "Implement"; Step 4: "Review (MANDATORY): Re-read EVERY changed file"; Step 5: "Commit" with `git pull --rebase`; Step 6: Summary doc to `.beads/agent-summaries/_session-8b93f5/summaries/81y.md` |
| 5. Scope boundaries | PASS | Explicit "Read ONLY: `README.md:L1-70`" and "Do NOT edit:" list covering sections after L70 and other directories |
| 6. Commit instructions | PASS | Includes `git pull --rebase && git add <changed-files> && git commit...` |
| 7. Line number specificity | PASS | File reference includes line ranges: `L9-27`, `L1-70` (not vague file-level scope) |

**Task 81y Verdict**: **PASS**

---

### Task x0m: Wave concept used in RULES.md but never defined

| Criterion | Status | Evidence |
|-----------|--------|----------|
| 1. Real task IDs | PASS | Contains `ant-farm-x0m` (not placeholders) |
| 2. Real file paths | PASS | Specific file references with line numbers: `orchestration/RULES.md:L37,L80,L83-84,L141,L177` and `orchestration/templates/checkpoints.md:L237,L243,L270,L292` |
| 3. Root cause text | PASS | "RULES.md Hard Gates table references 'Next agent in wave' (L141) and checkpoints.md says 'BEFORE spawning next agent in same wave' (L237). The concept of a wave (a batch of agents spawned in parallel, where Wave N completes before Wave N+1 begins) is never defined anywhere in the codebase." |
| 4. All 6 mandatory steps | PASS | Step 1: `bd show`/`bd update`; Step 2: "Design (MANDATORY): 4+ genuinely distinct approaches"; Step 3: "Implement"; Step 4: "Review (MANDATORY): Re-read EVERY changed file"; Step 5: "Commit" with `git pull --rebase`; Step 6: Summary doc to `.beads/agent-summaries/_session-8b93f5/summaries/x0m.md` |
| 5. Scope boundaries | PASS | Explicit "Read ONLY:" with specific line ranges for RULES.md and checkpoints.md, "Do NOT edit:" list with 8 categories |
| 6. Commit instructions | PASS | Includes `git pull --rebase && git add <changed-files> && git commit...` |
| 7. Line number specificity | PASS | File references include specific line numbers (L37, L80, L83-84, L141, L177, L237, L243, L270, L292) — not vague file-level scope |

**Task x0m Verdict**: **PASS**

---

## Summary

| Task | Verdict | Mandatory Steps | Scope | Real Assets |
|------|---------|-----------------|-------|------------|
| ant-farm-8jg | PASS | All 6 present | Well-bounded | Task ID, file paths, root cause |
| ant-farm-81y | PASS | All 6 present | Well-bounded | Task ID, file paths, root cause |
| ant-farm-x0m | PASS | All 6 present | Well-bounded | Task ID, file paths, root cause |

---

## Overall Verdict

**PASS — All 3 prompts pass CCO audit**

All three Dirt Pusher prompts are ready for spawn:
- Each contains real task IDs (not placeholders)
- Each contains real file paths with specific line numbers (not vague file-level scope)
- Each contains specific root cause text (not generic copy-paste placeholders)
- Each includes all 6 mandatory execution steps
- Each has explicit scope boundaries (Read ONLY / Do NOT edit)
- Each includes `git pull --rebase` in commit instructions
- Each has high line-number specificity preventing scope creep

No prompt gaps detected. Ready to proceed with agent spawn.

# Pest Control Verification: CCO (Pre-Spawn Prompt Audit)
**Wave 3 Implementation Tasks**

**Session directory**: `.beads/agent-summaries/_session-3a20de`
**Verification timestamp**: 2026-02-20T16:45:00Z
**Audited tasks**: 2 (ant-farm-hz4t, ant-farm-b219)

---

## Task 1: ant-farm-hz4t
**Task name**: Add instrumented dummy reviewer via tmux for context usage measurement
**Agent type**: ai-engineer
**Prompt source**: `.beads/agent-summaries/_session-3a20de/prompts/task-hz4t.md`

### Verification Results

| Check | Criterion | Result | Evidence |
|-------|-----------|--------|----------|
| 1 | Real task IDs | PASS | `ant-farm-hz4t` present in task brief header (line 1) |
| 2 | Real file paths with line numbers | PASS | All file references include line ranges: `orchestration/RULES.md:L101-129`, `orchestration/templates/pantry.md:L249-530`, `docs/plans/2026-02-19-meta-orchestration-plan.md` (lines 8-9, 26) |
| 3 | Root cause text (not placeholder) | PASS | "No empirical data on how much context window reviewers consume during a review cycle..." (line 11) — specific, not a placeholder |
| 4 | All 6 mandatory steps present | PASS | All steps present with keywords: Step 1: `bd show` + `bd update` (line 8); Step 2: "Design (MANDATORY) — 4+ genuinely distinct approaches" (line 9); Step 3: Implement (line 10); Step 4: "Review (MANDATORY) — Re-read EVERY changed file" (line 11); Step 5: `git pull --rebase` (line 12); Step 6: Summary doc write to `summaries/hz4t.md` (line 14) |
| 5 | Scope boundaries explicit | PASS | Lines 20-33 define explicit "Read ONLY" and "Do NOT edit" sections with specific file ranges and directories |
| 6 | Commit instructions with git pull --rebase | PASS | Line 12 includes `git pull --rebase` before git add/commit |
| 7 | Line number specificity (prevents scope creep) | PASS | All affected files include specific line ranges (e.g., `L101-129`, `L249-530`); no vague file-level scope |

**Task 1 Verdict**: **PASS** — All 7 checks pass. Prompt is ready for spawn.

---

## Task 2: ant-farm-b219
**Task name**: Automated Queen crash recovery from progress log
**Agent type**: technical-writer
**Prompt source**: `.beads/agent-summaries/_session-3a20de/prompts/task-b219.md`

### Verification Results

| Check | Criterion | Result | Evidence |
|-------|-----------|--------|----------|
| 1 | Real task IDs | PASS | `ant-farm-b219` present in task brief header (line 1) |
| 2 | Real file paths with line numbers | PASS | File references include line ranges where applicable: `orchestration/RULES.md:L55-74`, `orchestration/RULES.md:L226-243` (lines 8-9); `scripts/parse-progress-log.sh` is new file (no range needed) (line 10) |
| 3 | Root cause text (not placeholder) | PASS | "Even with a progress log, crash recovery is manual. The user or next Queen must read the log, interpret the state, and decide what to resume..." (line 12) — specific root cause, not a placeholder |
| 4 | All 6 mandatory steps present | PASS | All steps present with keywords: Step 1: `bd show` + `bd update` (line 8); Step 2: "Design (MANDATORY) — 4+ genuinely distinct approaches" (line 9); Step 3: Implement (line 10); Step 4: "Review (MANDATORY) — Re-read EVERY changed file" (line 11); Step 5: `git pull --rebase` (line 12); Step 6: Summary doc write to `summaries/b219.md` (line 14) |
| 5 | Scope boundaries explicit | PASS | Lines 20-30 define explicit "Read ONLY" and "Do NOT edit" sections with specific file ranges and directory constraints |
| 6 | Commit instructions with git pull --rebase | PASS | Line 12 includes `git pull --rebase` before git add/commit |
| 7 | Line number specificity (prevents scope creep) | PASS | All editable files include specific line ranges (e.g., `L55-74`, `L226-243`); `scripts/parse-progress-log.sh` is a new file with clear creation scope |

**Task 2 Verdict**: **PASS** — All 7 checks pass. Prompt is ready for spawn.

---

## Summary

| Task | Task Name | Verdict | Notes |
|------|-----------|---------|-------|
| ant-farm-hz4t | Dummy reviewer tmux instrumentation | **PASS** | All 7 checks pass; scope well-bounded; no ambiguities |
| ant-farm-b219 | Crash recovery from progress log | **PASS** | All 7 checks pass; new script creation clearly scoped; no file conflicts |

---

## Overall Verdict: **PASS**

Both Wave 3 implementation prompts have been verified and meet all CCO criteria:
- All real task IDs present
- All file paths include line-number specificity
- Root causes are concrete, not placeholder text
- All 6 mandatory workflow steps present and explicit
- Scope boundaries are well-defined (read/edit restrictions, file ranges)
- Commit workflow includes `git pull --rebase`
- No ambiguity or scope creep risk detected

**Recommendation**: Proceed to spawn both agents.

---

**Pest Control signature**: `.beads/agent-summaries/_session-3a20de/pc/pc-session-cco-wave3-impl.md`

# Pest Control -- Checkpoint B (Substance Verification)

**Task ID**: ant-farm-ss6
**Commit**: 03f6299
**Summary doc**: `.beads/agent-summaries/_standalone/ss6.md`
**Timestamp**: 2026-02-17T17:25:58Z

---

## Check 1: Git Diff Verification

**Method**: Ran `git show --stat 03f6299` and `git diff a8305f1..03f6299 --name-only` to identify all changed files.

**Files in git diff:**
1. `orchestration/RULES.md`
2. `orchestration/templates/checkpoints.md`
3. `orchestration/templates/dirt-pusher-skeleton.md`
4. `orchestration/templates/pantry.md`

**Files claimed in summary doc:**
1. `orchestration/RULES.md`
2. `orchestration/templates/checkpoints.md`
3. `orchestration/templates/dirt-pusher-skeleton.md`
4. `orchestration/templates/pantry.md`

**Diff stats**: 73 insertions, 54 deletions across 4 files.

- All 4 claimed files are present in the diff. **CONFIRMED.**
- No files in the diff are missing from the summary. **CONFIRMED.**
- No files in the summary are absent from the diff. **CONFIRMED.**

**Verdict: PASS**

---

## Check 2: Acceptance Criteria Spot-Check

The bead description for ant-farm-ss6 states: "dirt-pusher-skeleton.md uses <task-id>, pantry.md uses {task-id-suffix}, checkpoints.md uses both interchangeably. A fresh agent cannot tell if it should use the full ID (hs_website-74g.1) or just the suffix (74g.1). Standardize to one term across all orchestration files."

The summary doc lists 4 acceptance criteria. I selected the two most critical.

### AC 2: All three primary files use the chosen terms consistently -- no mixed terminology

**Verification method**: Ran `grep` for all old-format patterns (`{task-id}`, `{task-id-suffix}`, `<task-id>`, `{epic-id}`, `<epic-id>`, `<epic>`) against each file at commit 03f6299.

- `orchestration/templates/dirt-pusher-skeleton.md`: Zero matches for any old-format term. **CONFIRMED.**
- `orchestration/templates/pantry.md`: Zero matches for any old-format term. **CONFIRMED.**
- `orchestration/templates/checkpoints.md`: Zero matches except one intentional negative example on line 78 (`NOT placeholders like \`<task-id>\` or \`<id>\``), which is a teaching example for Pest Control CCO Check 1. The summary doc explicitly documents this exception at line 88: "Preserved intentional negative example: `<task-id>` on CCO check 1." **CONFIRMED -- intentional preservation, not a gap.**
- `orchestration/RULES.md`: Zero matches for any old-format term. **CONFIRMED.**

**Verdict: PASS**

### AC 4: A fresh agent reading any single template knows the format without cross-referencing

**Verification method**: Read the first 10-15 lines of each file at commit 03f6299 to confirm term definitions block presence.

- `checkpoints.md` lines 4-7: Contains "Term definitions (canonical across all orchestration templates):" block with all three terms (`{TASK_ID}`, `{TASK_SUFFIX}`, `{EPIC_ID}`) defined with examples. **CONFIRMED.**
- `dirt-pusher-skeleton.md` lines 8-11: Contains identical term definitions block. **CONFIRMED.**
- `pantry.md` lines 5-8: Contains identical term definitions block. **CONFIRMED.**
- `RULES.md`: Does NOT contain a term definitions block, but uses `{EPIC_ID}` consistently. The summary doc explains (line 170): "Term definitions are in each individual template file (not RULES.md), satisfying the self-contained criterion." RULES.md is read by the Queen, not by agents, so self-containment for agents is still satisfied. **CONFIRMED -- reasonable design decision.**

**Verdict: PASS**

---

## Check 3: Approaches Substance Check

The summary doc lists 5 approaches (A through E).

| Approach | Strategy | Distinct? |
|----------|----------|-----------|
| A | Uppercase-pair (`{TASK_ID}` / `{TASK_SUFFIX}`) with inline definitions in each file | Yes -- defines new canonical vocabulary + inline definitions |
| B | Keep existing `{task-id-suffix}` lowercase, add definitions only | Yes -- minimal-change strategy, annotates rather than replaces |
| C | Single term `{TASK_ID}` everywhere, drop suffix concept entirely | Yes -- fundamentally different (one term vs. two), forces agents to parse IDs |
| D | Glossary in RULES.md, all templates point to it | Yes -- centralized reference vs. inline definitions; explicit cross-file dependency |
| E | Verbose `{TASK_ID_SUFFIX}` / `{EPIC_ID_SUFFIX}` naming | Yes -- self-descriptive naming variant; different naming convention than A |

All 5 approaches represent genuinely distinct design strategies with different tradeoffs. Approaches B and D are defensive alternatives (minimal change vs. centralized reference). Approach C eliminates a concept entirely. Approach E is a naming convention variant. No cosmetic duplicates detected.

**Verdict: PASS**

---

## Check 4: Correctness Review Evidence

I selected `pantry.md` for spot-checking.

**Summary doc claims (Section 4, pantry.md):**
- "Term definitions block is present and correct"
- "Task-metadata read path: `{TASK_SUFFIX}` -- correct (file is named by suffix)"
- "Data file write path: `task-{TASK_SUFFIX}.md` -- correct"
- "Template output block: `{TASK_ID}` in header (correct -- Task Brief shows full ID for agent reference), `{EPIC_ID}` and `{TASK_SUFFIX}` in paths -- correct"
- "Review mode paths: `{EPIC_ID}/review-reports/...` -- correct"
- "No mixed terminology remains"

**Verification against actual file content at commit 03f6299:**

1. Term definitions block -- Present at lines 5-8. Content matches the canonical three-term format. **CONFIRMED.**
2. Task-metadata read path -- Line `1. Read \`{session-dir}/task-metadata/{TASK_SUFFIX}.md\`` uses `{TASK_SUFFIX}`. **CONFIRMED.**
3. Data file write path -- Line `3. Write a data file to \`{session-dir}/prompts/task-{TASK_SUFFIX}.md\`` uses `{TASK_SUFFIX}`. **CONFIRMED.**
4. Template output block -- `# Task Brief: {TASK_ID}` uses full ID (correct for display). `**Summary output path**: .beads/agent-summaries/{EPIC_ID}/{TASK_SUFFIX}.md` uses both terms correctly. **CONFIRMED.**
5. Review mode paths -- `Report output path: \`.beads/agent-summaries/{EPIC_ID}/review-reports/{type}-review-{timestamp}.md\`` uses `{EPIC_ID}`. Consolidated path: `.beads/agent-summaries/{EPIC_ID}/review-reports/review-consolidated-{timestamp}.md` uses `{EPIC_ID}`. **CONFIRMED.**
6. No mixed terminology -- `grep` for old-format terms returned zero matches. **CONFIRMED.**

The correctness notes are specific to actual file content (referencing specific path expressions and their locations), not generic boilerplate.

**Verdict: PASS**

---

## Overall Verdict: PASS

All 4 checks confirm substance. The git diff matches the summary doc's claims exactly, the acceptance criteria are genuinely satisfied (verified via grep and file reads), the approaches are distinct strategies, and the correctness review contains file-specific evidence that matches ground truth.

| Check | Result | Evidence |
|-------|--------|----------|
| 1. Git Diff Verification | PASS | 4 files in diff match 4 files in summary exactly; no omissions or extras |
| 2. Acceptance Criteria Spot-Check | PASS | Old-format terms eliminated (grep verified); term definitions blocks present in all 3 template files |
| 3. Approaches Substance Check | PASS | 5 genuinely distinct strategies with different tradeoffs |
| 4. Correctness Review Evidence | PASS | pantry.md notes are specific and accurate against committed file content |

<!-- Pest Control CCO Pre-Spawn Audit Report -->
# CCO Verification Report: Wave 1 Task Previews

**Session:** _session-20260313-021827
**Checkpoint:** CCO (Pre-Spawn Prompt Audit)
**Auditor:** Pest Control
**Timestamp:** 2026-03-13 02:24:41

---

## Summary

All 7 Wave 1 task previews pass the CCO mechanical checklist. All previews contain:
- Actual task IDs (not placeholders)
- Real file paths with line numbers
- Specific root cause descriptions
- All 6 mandatory workflow steps with required keywords
- Explicit scope boundaries
- Commit instructions with `git pull --rebase`
- Line number specificity for all affected files

---

## CCO Checklist Results

### Task ant-farm-6gg6: Migrate Scout and implementation templates

**File:** task-6gg6-preview.md

| Check | Criterion | Evidence | Result |
|-------|-----------|----------|--------|
| 1 | Real task IDs | "ant-farm-6gg6" present in task brief and steps | PASS |
| 2 | Real file paths with line numbers | scout.md:L34-46,L83,L138,L267-285; implementation.md:L25-26,L47,L71,L115,L168,L194,L197 | PASS |
| 3 | Specific root cause | "Scout and implementation templates contain bd command references that need mechanical substitution to crumb equivalents." | PASS |
| 4 | All 6 mandatory steps | Step 1: bd show/update; Step 2: Design (MANDATORY); Step 3: Implement; Step 4: Review (MANDATORY); Step 5: Commit with git pull --rebase; Step 6: Summary doc + bd close | PASS |
| 5 | Scope boundaries | "Read ONLY: orchestration/templates/scout.md (full file), orchestration/templates/implementation.md (full file)" | PASS |
| 6 | Commit instructions | `git pull --rebase && git add <changed-files> && git commit -m "<type>: <description> (ant-farm-6gg6)"` | PASS |
| 7 | Line number specificity | All files have specific line ranges (L34-46, L83, L138, L267-285, etc.) | PASS |

**Verdict: PASS**

---

### Task ant-farm-eifm: Migrate queen-state and session plan templates

**File:** task-eifm-preview.md

| Check | Criterion | Evidence | Result |
|-------|-----------|----------|--------|
| 1 | Real task IDs | "ant-farm-eifm" present | PASS |
| 2 | Real file paths with line numbers | queen-state.md:L8,L74; SESSION_PLAN_TEMPLATE.md:L271,L288,L291 | PASS |
| 3 | Specific root cause | "Queen-state and session plan templates contain bd command references and .beads/ paths needing mechanical substitution." | PASS |
| 4 | All 6 mandatory steps | Steps 1-6 all present with MANDATORY keywords in Steps 2 and 4 | PASS |
| 5 | Scope boundaries | "Read ONLY: orchestration/templates/queen-state.md (full file), orchestration/templates/SESSION_PLAN_TEMPLATE.md (full file)" | PASS |
| 6 | Commit instructions | Includes `git pull --rebase` in step 5 | PASS |
| 7 | Line number specificity | All files have specific line numbers (L8, L74, L271, L288, L291) | PASS |

**Verdict: PASS**

---

### Task ant-farm-gvd4: Migrate dirt-pusher, nitpicker, scribe skeletons

**File:** task-gvd4-preview.md

| Check | Criterion | Evidence | Result |
|-------|-----------|----------|--------|
| 1 | Real task IDs | "ant-farm-gvd4" present | PASS |
| 2 | Real file paths with line numbers | dirt-pusher-skeleton.md:L36,L44; nitpicker-skeleton.md:L39,L52; scribe-skeleton.md:L47,L53 | PASS |
| 3 | Specific root cause | "Skeleton templates contain bd command references needing mechanical substitution." | PASS |
| 4 | All 6 mandatory steps | Steps 1-6 all present with MANDATORY keywords | PASS |
| 5 | Scope boundaries | "Read ONLY: orchestration/templates/dirt-pusher-skeleton.md (full file), orchestration/templates/nitpicker-skeleton.md (full file), orchestration/templates/scribe-skeleton.md (full file)" | PASS |
| 6 | Commit instructions | Includes `git pull --rebase` | PASS |
| 7 | Line number specificity | All files have specific line numbers (L36, L44, L39, L52, L47, L53) | PASS |

**Verdict: PASS**

---

### Task ant-farm-k03k: Migrate reference and setup documentation

**File:** task-k03k-preview.md

| Check | Criterion | Evidence | Result |
|-------|-----------|----------|--------|
| 1 | Real task IDs | "ant-farm-k03k" present | PASS |
| 2 | Real file paths with line numbers | dependency-analysis.md:L59-60,L195; SETUP.md:L87,L93,L226 | PASS |
| 3 | Specific root cause | "Reference and setup documentation contain bd references needing mechanical substitution." | PASS |
| 4 | All 6 mandatory steps | Steps 1-6 all present with MANDATORY keywords | PASS |
| 5 | Scope boundaries | "Read ONLY: orchestration/reference/dependency-analysis.md (full file), orchestration/SETUP.md (full file)" | PASS |
| 6 | Commit instructions | Includes `git pull --rebase` | PASS |
| 7 | Line number specificity | All files have specific line numbers (L59-60, L195, L87, L93, L226) | PASS |

**Verdict: PASS**

---

### Task ant-farm-mmo3: Migrate agent definitions

**File:** task-mmo3-preview.md

| Check | Criterion | Evidence | Result |
|-------|-----------|----------|--------|
| 1 | Real task IDs | "ant-farm-mmo3" present | PASS |
| 2 | Real file paths with line numbers | ~/.claude/agents/scout-organizer.md:L3,L25,L33,L35; ~/.claude/agents/nitpicker.md:L107,L124,L172 | PASS |
| 3 | Specific root cause | "Agent definition files contain bd command references needing mechanical substitution." | PASS |
| 4 | All 6 mandatory steps | Steps 1-6 all present with MANDATORY keywords | PASS |
| 5 | Scope boundaries | "Read ONLY: ~/.claude/agents/scout-organizer.md (full file), ~/.claude/agents/nitpicker.md (full file)" | PASS |
| 6 | Commit instructions | Includes `git pull --rebase` | PASS |
| 7 | Line number specificity | All files have specific line numbers (L3, L25, L33, L35, L107, L124, L172) | PASS |

**Verdict: PASS**

---

### Task ant-farm-vjhe: Migrate project documentation

**File:** task-vjhe-preview.md

| Check | Criterion | Evidence | Result |
|-------|-----------|----------|--------|
| 1 | Real task IDs | "ant-farm-vjhe" present | PASS |
| 2 | Real file paths with line numbers | README.md:L29,L78-79,L128,L249,L322-336; AGENTS.md:L3,L8-12,L28; CONTRIBUTING.md:L132; docs/installation-guide.md:L41 | PASS |
| 3 | Specific root cause | "Project documentation contains bd references and beads terminology needing mechanical substitution." | PASS |
| 4 | All 6 mandatory steps | Steps 1-6 all present with MANDATORY keywords | PASS |
| 5 | Scope boundaries | "Read ONLY: README.md (full file), AGENTS.md (full file), CONTRIBUTING.md (full file), docs/installation-guide.md (full file)" | PASS |
| 6 | Commit instructions | Includes `git pull --rebase` | PASS |
| 7 | Line number specificity | All files have specific line numbers or ranges (L29, L78-79, L128, L249, L322-336, L3, L8-12, L28, L132, L41) | PASS |

**Verdict: PASS**

---

### Task ant-farm-6d3f: Migrate build-review-prompts.sh

**File:** task-6d3f-preview.md

| Check | Criterion | Evidence | Result |
|-------|-----------|----------|--------|
| 1 | Real task IDs | "ant-farm-6d3f" present | PASS |
| 2 | Real file paths with line numbers | scripts/build-review-prompts.sh:L247 | PASS |
| 3 | Specific root cause | "Shell script contains bd command references requiring semantic migration to crumb equivalents." | PASS |
| 4 | All 6 mandatory steps | Steps 1-6 all present with MANDATORY keywords | PASS |
| 5 | Scope boundaries | "Read ONLY: scripts/build-review-prompts.sh (full file)" | PASS |
| 6 | Commit instructions | Includes `git pull --rebase` | PASS |
| 7 | Line number specificity | File has specific line number (L247); also includes syntax check requirement in acceptance criteria | PASS |

**Verdict: PASS**

---

## Overall Verdict

**PASS**

All 7 Wave 1 task previews meet the CCO mechanical checklist criteria. Every preview contains:
- Real task IDs (no placeholders)
- Real file paths with specific line numbers or ranges
- Detailed root cause descriptions
- All 6 mandatory workflow steps with required keywords
- Explicit scope boundaries limiting agent access
- Proper commit instructions including `git pull --rebase`
- Line number specificity preventing scope creep

All previews are ready for Dirt Pusher spawn.

---

**Report Location:** /Users/correy/projects/ant-farm/.beads/agent-summaries/_session-20260313-021827/pc/pc-session-cco-impl-20260313-022441.md

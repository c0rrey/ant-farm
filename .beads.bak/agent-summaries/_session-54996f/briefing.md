# Session Briefing

## Task Inventory
| ID | Epic | Title | Priority | Type | Agent | Files | Risk |
|----|------|-------|----------|------|-------|-------|------|
| ant-farm-tek | _standalone | Polling loop in reviews.md Step 0a uses fragile wc -l line-counting | P2 | bug | prompt-engineer | reviews.md:370-383 | HIGH |
| ant-farm-tz0q | _standalone | Nested markdown code fences in reviews.md error return template | P2 | bug | technical-writer | reviews.md:390-420 | HIGH |
| ant-farm-crky | _standalone | Big Head skeleton and reviews.md have divergent failure handling | P2 | bug | prompt-engineer | reviews.md:354-424, big-head-skeleton.md:57-66 | HIGH |
| ant-farm-7hgn | ant-farm-753 | Delay Big Head bead filing until after Pest Control checkpoint validation | P2 | task | prompt-engineer | reviews.md, big-head-skeleton.md, RULES.md, pantry.md | HIGH |

**Ready**: 4 tasks | **Blocked**: 0 tasks

## File Modification Matrix
| File | Tasks | Risk |
|------|-------|------|
| orchestration/templates/reviews.md | ant-farm-tek, ant-farm-tz0q, ant-farm-crky, ant-farm-7hgn | HIGH |
| orchestration/templates/big-head-skeleton.md | ant-farm-crky, ant-farm-7hgn | HIGH |
| orchestration/RULES.md | ant-farm-7hgn | LOW |
| orchestration/templates/pantry.md | ant-farm-7hgn | LOW |

## Dependency Chains
- No explicit bd dependency chains between the 4 tasks (all are unblocked)
- Logical ordering constraint: ant-farm-crky (divergent failure handling) should ideally be resolved before ant-farm-7hgn (which adds Pest Control gate), since both modify big-head-skeleton.md and reviews.md failure-handling sections. Resolving the contradiction first gives 7hgn a clean baseline.
- ant-farm-tek and ant-farm-tz0q both target reviews.md Step 0a error handling area (lines 354-424) — high overlap with ant-farm-crky which covers the same region.

## Proposed Strategies

### Strategy A: Serial Single-Agent Execution (Recommended)
**Wave 1** (1 agent): ant-farm-tek, ant-farm-tz0q, ant-farm-crky, ant-farm-7hgn — all four tasks assigned to one prompt-engineer agent, executed sequentially in logical order (tek → tz0q → crky → 7hgn)
**Rationale**: reviews.md is touched by all 4 tasks, with ant-farm-tek (lines 370-383), ant-farm-tz0q (lines 390-420), and ant-farm-crky (lines 354-424) all targeting the same Step 0a error handling block. This is a classic Pattern 1 (Same File, Same Section) HIGH conflict scenario. A single agent processes all tasks in one pass, with no merge conflicts or rebasing needed. The logical order (fix the fragile wc -l first, fix fence nesting second, reconcile divergent behavior third, then add PC gate) means each task builds on a clean prior state.
**Risk**: LOW — single agent eliminates all merge conflicts; sequential ordering prevents logical contradictions between fixes

### Strategy B: Parallel with Two Agents (Wave-Based)
**Wave 1** (2 agents):
- Agent 1: ant-farm-tek + ant-farm-tz0q (both target reviews.md lines 370-420, near Step 0a)
- Agent 2: ant-farm-7hgn only (targets reviews.md consolidation protocol, RULES.md, pantry.md)
**Wave 2** (1 agent): ant-farm-crky (reconcile after both Wave 1 agents complete, since it touches both sets of files)
**Risk**: MEDIUM — Agent 1 and Agent 2 both write to reviews.md simultaneously (different sections, but same file). Requires rebase before commit. ant-farm-crky in Wave 2 touches sections modified by both Wave 1 agents, requiring careful rebase. Risk of logical inconsistency if Wave 1 fixes diverge from the reconciliation needed by crky.

### Strategy C: Full Parallel (4 Agents)
**Wave 1** (4 agents): ant-farm-tek, ant-farm-tz0q, ant-farm-crky, ant-farm-7hgn simultaneously
**Risk**: HIGH — 4 agents all writing to reviews.md. ant-farm-tek (lines 370-383), ant-farm-tz0q (lines 390-420), and ant-farm-crky (lines 354-424) have near-total section overlap. Very high merge conflict probability. Known failure mode from Epic 74g: agents scramble each other's work. Not recommended.

## Metadata
- Epics: ant-farm-753, _standalone
- Task metadata files: /Users/correy/projects/ant-farm/.beads/agent-summaries/_session-54996f/task-metadata/ (4 files)
- Session dir: /Users/correy/projects/ant-farm/.beads/agent-summaries/_session-54996f/

# Session Briefing

## Task Inventory
| ID | Epic | Title | Priority | Type | Agent | Files | Risk |
|----|------|-------|----------|------|-------|-------|------|
| ant-farm-0b4k | ant-farm-753 | Add append-only progress log for Queen crash recovery | P1 | feature | technical-writer | RULES.md | HIGH |
| ant-farm-pid | ant-farm-753 | AGG-038: Clarify wildcard artifact path matching in reviews.md | P1 | task | technical-writer | reviews.md | LOW |
| ant-farm-3n2 | ant-farm-753 | AGG-040: Clarify DMVDC sampling formula | P2 | task | technical-writer | checkpoints.md | HIGH |
| ant-farm-957 | ant-farm-753 | AGG-041: Clarify code-reviewer role in checkpoints.md | P2 | task | technical-writer | checkpoints.md | HIGH |
| ant-farm-lajv | ant-farm-753 | Research tmux + iTerm2 control mode integration | P2 | task | data-researcher | meta-orchestration-plan.md | LOW |
| ant-farm-s0ak | ant-farm-753 | Add pre-flight Scout strategy verification checkpoint | P2 | feature | prompt-engineer | checkpoints.md, RULES.md | HIGH |
| ant-farm-3fm | ant-farm-753 | CCB lists report paths twice (duplication risk) | P3 | bug | technical-writer | checkpoints.md | HIGH |
| ant-farm-98c | ant-farm-753 | Retry counter interaction unspecified | P3 | bug | technical-writer | RULES.md | HIGH |
| ant-farm-c05 | ant-farm-753 | Checkpoint A.5 scope validation limitation | P3 | bug | technical-writer | checkpoints.md | HIGH |
| ant-farm-r8m | ant-farm-753 | {checkpoint} placeholder not defined | P3 | bug | technical-writer | checkpoints.md | HIGH |
| ant-farm-wiq | ant-farm-753 | CCO FAIL verdict format has no example | P3 | task | technical-writer | checkpoints.md | HIGH |
| ant-farm-5q3 | ant-farm-753 | AGG-039: Add complete error recovery procedures | P1 | task | technical-writer | RULES.md | HIGH |
| ant-farm-hz4t | ant-farm-753 | Add instrumented dummy reviewer via tmux | P2 | task | ai-engineer | RULES.md, pantry.md | HIGH |
| ant-farm-b219 | ant-farm-753 | Automated Queen crash recovery from progress log | P3 | feature | technical-writer | RULES.md, scripts/ | HIGH |

**Total**: 14 tasks | **Wave 1 (ready)**: 11 tasks | **Later waves (blocked)**: 3 tasks

## File Modification Matrix
| File | Tasks | Risk |
|------|-------|------|
| orchestration/templates/checkpoints.md | ant-farm-3fm, ant-farm-3n2, ant-farm-957, ant-farm-c05, ant-farm-r8m, ant-farm-s0ak, ant-farm-wiq | HIGH (7 tasks!) |
| orchestration/RULES.md | ant-farm-0b4k, ant-farm-98c, ant-farm-s0ak, ant-farm-5q3 (blocked), ant-farm-hz4t (blocked), ant-farm-b219 (blocked) | HIGH (6 tasks across waves) |
| orchestration/templates/reviews.md | ant-farm-pid | LOW (1 task) |
| orchestration/templates/pantry.md | ant-farm-hz4t (blocked) | LOW (1 task) |
| docs/plans/2026-02-19-meta-orchestration-plan.md | ant-farm-lajv | LOW (1 task) |

## Dependency Chains
- ant-farm-98c --> ant-farm-5q3 (retry counter clarity needed before adding error recovery procedures)
- ant-farm-0b4k --> ant-farm-b219 (progress log format needed before automated recovery)
- ant-farm-lajv --> ant-farm-hz4t (tmux research needed before dummy reviewer implementation)

## Proposed Strategies

### Strategy A: Batch by File -- Serial Checkpoints + Parallel RULES (Recommended)

The dominant constraint is that 7 tasks touch checkpoints.md and 6 tasks touch RULES.md. Parallel edits to the same file will cause merge conflicts. The safest approach batches all same-file tasks to a single agent.

**Wave 1** (3 agents):
- Agent 1 (technical-writer): ant-farm-3fm, ant-farm-3n2, ant-farm-957, ant-farm-c05, ant-farm-r8m, ant-farm-wiq -- all checkpoints.md-only tasks (6 tasks batched to 1 agent)
- Agent 2 (technical-writer): ant-farm-0b4k, ant-farm-98c -- RULES.md tasks that are ready and have no checkpoints.md overlap (2 tasks)
- Agent 3 (technical-writer): ant-farm-pid -- reviews.md only (1 task)
- Note: ant-farm-lajv is ready but deferred to Wave 1b (see below) since it is a research task with no file conflicts

**Wave 1b** (2 agents, can start immediately in parallel with Wave 1):
- Agent 4 (data-researcher): ant-farm-lajv -- tmux research, independent file (1 task)
- Agent 5 (prompt-engineer): ant-farm-s0ak -- touches both checkpoints.md AND RULES.md, so must run AFTER Agent 1 and Agent 2 complete (1 task)
- Note: ant-farm-s0ak actually cannot start until Agents 1 and 2 finish due to file overlaps

**Revised Wave 1** (4 agents):
- Agent 1 (technical-writer): ant-farm-3fm, ant-farm-3n2, ant-farm-957, ant-farm-c05, ant-farm-r8m, ant-farm-wiq (checkpoints.md batch, 6 tasks)
- Agent 2 (technical-writer): ant-farm-0b4k, ant-farm-98c (RULES.md batch, 2 tasks)
- Agent 3 (technical-writer): ant-farm-pid (reviews.md, 1 task)
- Agent 4 (data-researcher): ant-farm-lajv (research, 1 task)

**Wave 2** (2 agents, after Wave 1 completes):
- Agent 5 (prompt-engineer): ant-farm-s0ak (checkpoints.md + RULES.md, 1 task) -- needs both files stable
- Agent 6 (technical-writer): ant-farm-5q3 (RULES.md, 1 task) -- blocked by ant-farm-98c from Wave 1

**Wave 3** (2 agents, after Wave 2 completes):
- Agent 7 (ai-engineer): ant-farm-hz4t (RULES.md + pantry.md, 1 task) -- blocked by ant-farm-lajv from Wave 1
- Agent 8 (technical-writer): ant-farm-b219 (RULES.md + scripts/, 1 task) -- blocked by ant-farm-0b4k from Wave 1

Note: ant-farm-hz4t could theoretically start in Wave 2 (its blocker ant-farm-lajv is in Wave 1), but it touches RULES.md which is also modified by ant-farm-5q3 and ant-farm-s0ak in Wave 2. Deferring to Wave 3 avoids RULES.md conflicts.

**Rationale**: Maximizes safety by batching all checkpoints.md edits into one agent (6 tasks) and all early RULES.md edits into another (2 tasks). The 7-task checkpoints.md collision is the highest risk in this session -- batching eliminates it entirely. Wave 2 handles cross-file tasks (s0ak) and dependency-unblocked tasks (5q3). Wave 3 handles remaining blocked tasks after RULES.md stabilizes.

**Risk**: MEDIUM overall. Agent 1 has a heavy 6-task batch which increases per-agent failure risk, but eliminates the HIGH merge conflict risk. If Agent 1 fails, 6 tasks need re-run.

### Strategy B: Maximum Parallel -- Rebase Between Tasks

Run all 11 ready tasks as individual agents (up to 7 concurrent, rest queued). Each agent does `git pull --rebase` before committing. Higher throughput but significant merge conflict risk on checkpoints.md (7 concurrent editors).

**Wave 1** (7 agents):
- ant-farm-0b4k (technical-writer) -- RULES.md
- ant-farm-3fm (technical-writer) -- checkpoints.md
- ant-farm-3n2 (technical-writer) -- checkpoints.md
- ant-farm-957 (technical-writer) -- checkpoints.md
- ant-farm-98c (technical-writer) -- RULES.md
- ant-farm-pid (technical-writer) -- reviews.md
- ant-farm-lajv (data-researcher) -- meta-orchestration-plan.md

**Wave 1 overflow** (4 agents, start as Wave 1 slots free):
- ant-farm-c05 (technical-writer) -- checkpoints.md
- ant-farm-r8m (technical-writer) -- checkpoints.md
- ant-farm-s0ak (prompt-engineer) -- checkpoints.md + RULES.md
- ant-farm-wiq (technical-writer) -- checkpoints.md

**Wave 2** (3 agents):
- ant-farm-5q3 (technical-writer) -- RULES.md
- ant-farm-hz4t (ai-engineer) -- RULES.md + pantry.md
- ant-farm-b219 (technical-writer) -- RULES.md

**Rationale**: Fastest if all rebases succeed. But 7 tasks on checkpoints.md with rebase is a known HIGH-risk pattern (reference: Epic 74g failure mode from dependency-analysis.md).

**Risk**: HIGH. 7 concurrent checkpoints.md editors will almost certainly produce merge conflicts. Multiple agents may do redundant work or scramble each other's changes.

### Strategy C: Two-Agent Deep Batch

Minimize agent count to 2, each handling one primary file.

**Wave 1** (2 agents):
- Agent 1 (technical-writer): ALL checkpoints.md tasks + reviews.md task: ant-farm-3fm, ant-farm-3n2, ant-farm-957, ant-farm-c05, ant-farm-r8m, ant-farm-wiq, ant-farm-pid (7 tasks)
- Agent 2 (technical-writer): ALL RULES.md tasks + research: ant-farm-0b4k, ant-farm-98c, ant-farm-lajv (3 tasks)

**Wave 2** (2 agents):
- Agent 3 (prompt-engineer): ant-farm-s0ak (checkpoints.md + RULES.md, 1 task)
- Agent 4 (technical-writer): ant-farm-5q3 (RULES.md, 1 task)

**Wave 3** (2 agents):
- Agent 5 (ai-engineer): ant-farm-hz4t (RULES.md + pantry.md, 1 task)
- Agent 6 (technical-writer): ant-farm-b219 (RULES.md + scripts/, 1 task)

**Rationale**: Simplest coordination. Fewest agents means lowest merge conflict risk. But ant-farm-lajv is a research task (web search, docs reading) while ant-farm-0b4k/98c are documentation edits -- grouping them is awkward. And Agent 1 has 7 tasks which pushes the "max 7 tasks/agent" limit.

**Risk**: LOW for conflicts. MEDIUM for per-agent overload (7 tasks on Agent 1, mixed task types on Agent 2).

## Coverage Verification
- Inventory: 14 total tasks (11 ready + 3 blocked)
- Strategy A: 14 assigned across 3 waves -- PASS
- Strategy B: 14 assigned across 2 waves -- PASS
- Strategy C: 14 assigned across 3 waves -- PASS

## Metadata
- Epics: ant-farm-753
- Task metadata files: .beads/agent-summaries/_session-3a20de/task-metadata/ (14 files)
- Session dir: .beads/agent-summaries/_session-3a20de

# Session Briefing (Fix Cycle -- Round 1 P1/P2 Findings)

## Context
This is a **FIX-CYCLE** briefing. All 8 beads are P1/P2 findings from round 1 review. All are prompt-engineer type (orchestration template edits).

## Task Inventory
| ID | Epic | Title | Priority | Type | Agent | Files | Risk |
|----|------|-------|----------|------|-------|-------|------|
| ant-farm-ql6s | none | Wrong team name 'nitpickers' in reviews.md Fix Workflow | P1 | bug | prompt-engineer | reviews.md:985 | HIGH (shared file) |
| ant-farm-1pa0 | ant-farm-qp1j | Big Head polling loop: single-invocation under-documented, timeout too short | P1 | bug | prompt-engineer | big-head-skeleton.md:88-105, reviews.md:538-642 | HIGH (shared file) |
| ant-farm-f7lg | none | Phantom briefs/ path and missing edge-cases output path | P2 | bug | prompt-engineer | reviews.md:1091-1094, RULES.md:393 | HIGH (shared file) |
| ant-farm-5zs0 | none | Round 2+ spawn instructions contradict persistent-team model | P2 | bug | prompt-engineer | reviews.md:82,934 | HIGH (shared file) |
| ant-farm-fp74 | none | Silent failure on bd list in Big Head cross-session dedup | P2 | bug | prompt-engineer | big-head-skeleton.md:113-117, reviews.md:720-724 | HIGH (shared file) |
| ant-farm-01a8 | none | Placeholder guard incomplete when REVIEW_ROUND corrupt | P2 | bug | prompt-engineer | reviews.md:554-593 | HIGH (shared file) |
| ant-farm-1rof | none | Crash recovery missing session directory existence check | P2 | bug | prompt-engineer | RULES.md:64-75 | LOW |
| ant-farm-ccg8 | none | ESV Check 2 git log no guard for repo root commit | P2 | bug | prompt-engineer | checkpoints.md:791-795 | LOW |

**Total**: 8 tasks | **Wave 1 (ready)**: 8 tasks | **Later waves (blocked)**: 0 tasks

## File Modification Matrix
| File | Tasks | Line Ranges | Risk |
|------|-------|-------------|------|
| orchestration/templates/reviews.md | ql6s, 1pa0, 5zs0, 01a8, fp74, f7lg | L82, L538-642, L554-593, L720-724, L934, L985, L1091-1094 | HIGH (6 tasks) |
| orchestration/templates/big-head-skeleton.md | 1pa0, fp74 | L88-105, L113-117 | MEDIUM (2 tasks, adjacent ~8 lines apart) |
| orchestration/RULES.md | f7lg, 1rof | L64-75, L393 | LOW (2 tasks, 320 lines apart) |
| orchestration/templates/checkpoints.md | ccg8 | L791-795 | LOW (1 task) |

### Conflict Detail
- **reviews.md** is touched by 6 of 8 tasks. Although all line ranges are well-separated (minimum ~130 line gap between distinct tasks), the decision matrix flags 3+ tasks on the same file as HIGH risk. Batching is strongly recommended.
- **big-head-skeleton.md** has 2 tasks in adjacent sections (L88-105 and L113-117 are only ~8 lines apart). MEDIUM risk -- serialization or batching recommended.
- **RULES.md** has 2 tasks 320 lines apart. LOW risk -- parallel with rebase is safe.
- **checkpoints.md** has 1 task. No conflict.
- **Cross-file overlap**: ant-farm-1pa0 touches BOTH reviews.md and big-head-skeleton.md. ant-farm-fp74 also touches BOTH. ant-farm-f7lg touches BOTH reviews.md and RULES.md. Batching these cross-file tasks with the reviews.md batch eliminates all cross-file conflicts.

## Dependency Chains
- No inter-task dependencies exist among these 8 beads
- All 8 are ready (unblocked)
- ant-farm-1pa0 is a child of epic ant-farm-qp1j but has no blockers

## Proposed Strategies

### Strategy A: Batched by File Ownership (Recommended)
**Wave 1** (3 agents):
- **Agent 1 (reviews.md mega-batch)**: ant-farm-ql6s, ant-farm-1pa0, ant-farm-5zs0, ant-farm-01a8, ant-farm-fp74, ant-farm-f7lg (prompt-engineer) -- all 6 tasks touching reviews.md; Agent 1 also handles big-head-skeleton.md edits (1pa0, fp74) and RULES.md:393 edit (f7lg) since these tasks cross file boundaries
- **Agent 2**: ant-farm-1rof (prompt-engineer) -- RULES.md:64-75 only
- **Agent 3**: ant-farm-ccg8 (prompt-engineer) -- checkpoints.md:791-795 only

**Rationale**: Batching all reviews.md tasks into a single agent eliminates the HIGH-risk 6-task file conflict entirely. Agent 1 also handles both big-head-skeleton.md tasks (1pa0 and fp74), preventing the MEDIUM-risk adjacent-section conflict. The cross-file tasks (f7lg touches RULES.md:393, 1pa0/fp74 touch big-head-skeleton.md) are all absorbed by Agent 1, so no agent-to-agent file conflicts exist. Agent 2 (RULES.md:64-75) and Agent 1 (RULES.md:393) do touch the same file, but 320 lines apart -- rebase handles this trivially.

**Risk**: LOW overall after batching. Agent 1 has 6 tasks but all are small, targeted edits with specific line numbers. No merge conflict risk since reviews.md and big-head-skeleton.md are each owned by exactly one agent. The only shared file across agents is RULES.md (Agent 1 at L393, Agent 2 at L64-75), which is LOW risk.

### Strategy B: Maximally Safe Single Batch
**Wave 1** (2 agents):
- **Agent 1**: ant-farm-ql6s, ant-farm-1pa0, ant-farm-5zs0, ant-farm-01a8, ant-farm-fp74, ant-farm-f7lg, ant-farm-1rof (prompt-engineer) -- 7 tasks, all files except checkpoints.md
- **Agent 2**: ant-farm-ccg8 (prompt-engineer) -- checkpoints.md only

**Rationale**: Eliminates ALL file conflicts by putting every task touching a shared file into one agent. Only checkpoints.md (single task, no conflicts) runs separately. Zero merge conflict risk.

**Risk**: LOW. Agent 1 has 7 tasks (at the max limit). All are small edits. Slowest wall-clock time but maximum safety.

### Strategy C: Parallel with Rebase (Fastest)
**Wave 1** (5 agents):
- **Agent 1 (reviews.md-only)**: ant-farm-ql6s, ant-farm-5zs0, ant-farm-01a8 (prompt-engineer) -- reviews.md L82, L554-593, L934, L985
- **Agent 2 (cross-file pair)**: ant-farm-1pa0, ant-farm-fp74 (prompt-engineer) -- big-head-skeleton.md L88-117, reviews.md L538-642 & L720-724
- **Agent 3 (cross-file single)**: ant-farm-f7lg (prompt-engineer) -- reviews.md L1091-1094, RULES.md L393
- **Agent 4**: ant-farm-1rof (prompt-engineer) -- RULES.md L64-75
- **Agent 5**: ant-farm-ccg8 (prompt-engineer) -- checkpoints.md L791-795

Execution order: Agents 4+5 run freely. Agent 1 commits first on reviews.md, then Agents 2+3 rebase and commit.

**Rationale**: Maximum parallelism. Splits reviews.md work across 3 agents with sequential commit ordering to manage conflicts.

**Risk**: MEDIUM. Three agents editing reviews.md requires careful commit ordering and rebase. In a fix cycle where reliability matters more than speed, this introduces unnecessary merge risk. **Not recommended.**

## Coverage Verification
- Inventory: 8 total tasks (8 ready + 0 blocked)
- Strategy A: 8 assigned across 1 wave -- PASS
- Strategy B: 8 assigned across 1 wave -- PASS
- Strategy C: 8 assigned across 1 wave -- PASS

## Metadata
- Epics: ant-farm-qp1j, none (7 tasks have no epic parent)
- Task metadata files: .beads/agent-summaries/_session-20260222-225628/task-metadata/ (8 files)
- Session dir: .beads/agent-summaries/_session-20260222-225628

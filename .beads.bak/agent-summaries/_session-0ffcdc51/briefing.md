# Session Briefing

## Task Inventory
| ID | Epic | Title | Priority | Type | Agent | Files | Risk |
|----|------|-------|----------|------|-------|-------|------|
| ant-farm-asdl.1 | ant-farm-asdl | Add cross-session dedup step and description template to big-head-skeleton.md | P1 | task | prompt-engineer | orchestration/templates/big-head-skeleton.md | LOW |
| ant-farm-asdl.2 | ant-farm-asdl | Add cross-session dedup and description template to reviews.md Big Head Consolidation Protocol | P2 | task | prompt-engineer | orchestration/templates/reviews.md | LOW |
| ant-farm-asdl.3 | ant-farm-asdl | Update agents/big-head.md with dedup instruction and --body-file reference | P2 | task | prompt-engineer | agents/big-head.md | LOW |
| ant-farm-asdl.4 | ant-farm-asdl | Update deprecated pantry.md Section 2 bead filing references | P3 | task | prompt-engineer | orchestration/templates/pantry.md | LOW |
| ant-farm-asdl.5 | ant-farm-asdl | Verify all Big Head template changes are consistent and complete | P2 | task | code-reviewer | all 4 files + scripts/build-review-prompts.sh | LOW |

**Total**: 5 tasks | **Wave 1 (ready)**: 1 task | **Later waves (blocked)**: 4 tasks

## File Modification Matrix
| File | Tasks | Risk |
|------|-------|------|
| orchestration/templates/big-head-skeleton.md | asdl.1 (write), asdl.5 (read/verify) | LOW |
| orchestration/templates/reviews.md | asdl.2 (write), asdl.5 (read/verify) | LOW |
| agents/big-head.md | asdl.3 (write), asdl.5 (read/verify) | LOW |
| orchestration/templates/pantry.md | asdl.4 (write), asdl.5 (read/verify) | LOW |
| scripts/build-review-prompts.sh | asdl.5 (read only) | LOW |

No file conflicts exist among implementation tasks -- each task writes to a unique file. The only shared access is asdl.5 reading all files for verification after implementation completes.

## Dependency Chains
- ant-farm-asdl.1 -> ant-farm-asdl.2 -> ant-farm-asdl.5 (skeleton establishes canonical pattern, reviews.md mirrors it, verification confirms)
- ant-farm-asdl.1 -> ant-farm-asdl.3 -> ant-farm-asdl.5 (skeleton establishes pattern, agent definition references it, verification confirms)
- ant-farm-asdl.1 -> ant-farm-asdl.4 -> ant-farm-asdl.5 (skeleton establishes pattern, pantry references it, verification confirms)

**Key constraint**: asdl.1 is the sole Wave 1 task because it establishes the canonical patterns that .2, .3, and .4 must match. asdl.5 depends on ALL four implementation tasks completing first.

## Proposed Strategies

### Strategy A: Three-Wave Sequential (Recommended)
**Wave 1** (1 agent): ant-farm-asdl.1 (prompt-engineer)
**Wave 2** (3 agents): ant-farm-asdl.2 (prompt-engineer), ant-farm-asdl.3 (prompt-engineer), ant-farm-asdl.4 (prompt-engineer)
**Wave 3** (1 agent): ant-farm-asdl.5 (code-reviewer)
**Rationale**: Respects all dependency chains. Wave 1 establishes the canonical pattern in the skeleton. Wave 2 tasks each touch independent files and can safely run in parallel once .1 completes. Wave 3 verification runs after all writes complete. No file conflicts in any wave. This is the natural execution order dictated by the dependency graph.
**Risk**: LOW -- each wave touches independent files, and the dependency gates prevent inconsistency.

### Strategy B: Two-Wave Aggressive
**Wave 1** (4 agents): ant-farm-asdl.1 (prompt-engineer), ant-farm-asdl.2 (prompt-engineer), ant-farm-asdl.3 (prompt-engineer), ant-farm-asdl.4 (prompt-engineer)
**Wave 2** (1 agent): ant-farm-asdl.5 (code-reviewer)
**Rationale**: Since the plan file (~/.claude/plans/ticklish-spinning-rose.md) contains exact replacement text for ALL tasks, tasks .2-.4 could theoretically execute in parallel with .1 by referencing the plan directly rather than reading .1's output. Each task touches a different file so there are no merge conflicts.
**Risk**: MEDIUM -- .2-.4 are supposed to "match the canonical pattern established in big-head-skeleton.md" but the plan already specifies exact text, so there's no real data dependency on runtime output from .1. However, if .1 deviates from the plan (e.g., adjusts step numbering), .2-.4 could have stale cross-references.

### Strategy C: Single-Agent Serial
**Wave 1** (1 agent): ant-farm-asdl.1 (prompt-engineer), ant-farm-asdl.2 (prompt-engineer), ant-farm-asdl.3 (prompt-engineer), ant-farm-asdl.4 (prompt-engineer), ant-farm-asdl.5 (code-reviewer) -- all sequentially in one agent
**Rationale**: One agent handles all tasks in dependency order. Zero coordination overhead, guaranteed consistency since the same agent context sees all changes.
**Risk**: LOW -- no conflicts possible. But slower: serial execution of 5 tasks in one agent context.

## Coverage Verification
- Inventory: 5 total tasks (1 ready + 4 blocked)
- Strategy A: 5 assigned across 3 waves -- PASS
- Strategy B: 5 assigned across 2 waves -- PASS
- Strategy C: 5 assigned across 1 wave -- PASS

## Metadata
- Epics: ant-farm-asdl
- Task metadata files: .beads/agent-summaries/_session-0ffcdc51/task-metadata/ (5 files)
- Session dir: .beads/agent-summaries/_session-0ffcdc51

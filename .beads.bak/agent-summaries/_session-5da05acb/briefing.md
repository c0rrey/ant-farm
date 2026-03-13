# Session Briefing

## Task Inventory
| ID | Epic | Title | Priority | Type | Agent | Files | Risk |
|----|------|-------|----------|------|-------|-------|------|
| ant-farm-2yww | none | Pantry-review deprecation not fully propagated to reader attributions | P2 | bug | technical-writer | RULES.md, README.md, GLOSSARY.md, CONTRIBUTING.md | HIGH |
| ant-farm-80l0 | none | README Hard Gates table missing SSV checkpoint | P2 | bug | technical-writer | README.md | MED |
| ant-farm-tour | none | SESSION_PLAN_TEMPLATE stale review decision logic contradicts RULES.md | P2 | bug | technical-writer | SESSION_PLAN_TEMPLATE.md | LOW |
| ant-farm-q84z | none | Dual TIMESTAMP/REVIEW_TIMESTAMP naming convention creates cognitive burden | P2 | bug | technical-writer | RULES.md | HIGH |
| ant-farm-zg7t | none | macOS (Darwin) incompatible shell commands in RULES.md | P2 | bug | devops-engineer | RULES.md | HIGH |
| ant-farm-sje5 | none | Missing preflight validation for required code-reviewer.md agent | P2 | bug | devops-engineer | sync-to-claude.sh, SETUP.md | LOW |

**Total**: 6 tasks | **Wave 1 (ready)**: 6 tasks | **Later waves (blocked)**: 0 tasks

## File Modification Matrix
| File | Tasks | Risk |
|------|-------|------|
| orchestration/RULES.md | ant-farm-2yww (L47,440), ant-farm-q84z (L148-149), ant-farm-zg7t (L157-176,381) | HIGH |
| README.md | ant-farm-2yww (L252,301,352), ant-farm-80l0 (L258-263) | MED |
| orchestration/GLOSSARY.md | ant-farm-2yww (L28,82) | LOW |
| CONTRIBUTING.md | ant-farm-2yww (L95) | LOW |
| orchestration/templates/SESSION_PLAN_TEMPLATE.md | ant-farm-tour (L207-237) | LOW |
| scripts/sync-to-claude.sh | ant-farm-sje5 | LOW |
| orchestration/SETUP.md | ant-farm-sje5 (L39-42) | LOW |

## Dependency Chains
- No explicit dependency chains -- all 6 tasks are independent and unblocked.
- Implicit conflict chain: ant-farm-2yww, ant-farm-q84z, and ant-farm-zg7t all modify orchestration/RULES.md (different sections).
- Implicit conflict: ant-farm-2yww and ant-farm-80l0 both modify README.md (sections within ~6 lines of each other).

## Proposed Strategies

### Strategy A: Conflict-Batched (Recommended)
**Wave 1** (4 agents):
- Agent 1 (technical-writer): ant-farm-2yww + ant-farm-80l0 -- batches all README.md work together and handles RULES.md lines 47, 440 plus GLOSSARY.md and CONTRIBUTING.md
- Agent 2 (technical-writer): ant-farm-q84z + ant-farm-zg7t -- batches remaining RULES.md work (lines 148-176, 381); both are shell/naming fixes in RULES.md
- Agent 3 (technical-writer): ant-farm-tour -- independent file (SESSION_PLAN_TEMPLATE.md), no conflicts
- Agent 4 (devops-engineer): ant-farm-sje5 -- independent files (sync-to-claude.sh, SETUP.md), no conflicts

**Rationale**: Batching eliminates all file conflicts. Agent 1 owns all README.md changes (2yww + 80l0) and 2yww's RULES.md lines (47, 440). Agent 2 owns the remaining RULES.md lines (148-176, 381). No two agents touch the same file. This is the safest strategy with zero merge conflict risk while still running 4 agents in parallel.

**Risk**: LOW -- no file overlaps between agents. Agent 1 has the most work (8 file locations across 4 files for 2yww + 1 location for 80l0), but the changes are all simple text substitutions.

### Strategy B: Maximum Parallel (6 agents with rebase)
**Wave 1** (6 agents):
- ant-farm-2yww (technical-writer)
- ant-farm-80l0 (technical-writer)
- ant-farm-tour (technical-writer)
- ant-farm-q84z (technical-writer)
- ant-farm-zg7t (devops-engineer)
- ant-farm-sje5 (devops-engineer)

All agents use git pull --rebase before commit.

**Rationale**: Maximum parallelism, fastest wall-clock time. Relies on rebase to resolve conflicts.

**Risk**: HIGH -- 3 agents on RULES.md and 2 agents on README.md. RULES.md conflicts are in different sections (lines 47/440 vs 148-149 vs 157-176/381) so rebase may succeed, but 3-way conflicts are possible. README.md lines 252 and 258-263 are close enough that context overlap could cause merge failures.

### Strategy C: Two-Wave Conservative
**Wave 1** (4 agents):
- Agent 1 (technical-writer): ant-farm-2yww -- the "big" task touching 4 files including RULES.md and README.md
- Agent 2 (technical-writer): ant-farm-tour -- independent file
- Agent 3 (devops-engineer): ant-farm-sje5 -- independent files
- Agent 4 (devops-engineer): ant-farm-zg7t -- RULES.md (lines 157-176, 381 only)

**Wave 2** (2 agents, after wave 1 completes):
- Agent 5 (technical-writer): ant-farm-q84z -- RULES.md lines 148-149 (waits for 2yww and zg7t to finish)
- Agent 6 (technical-writer): ant-farm-80l0 -- README.md lines 258-263 (waits for 2yww to finish)

**Rationale**: Serializes the highest-risk conflicts by deferring q84z and 80l0 to wave 2. Wave 1 still has RULES.md conflict between 2yww (L47,440) and zg7t (L157-176,381), but these sections are far apart.

**Risk**: MEDIUM -- Wave 1 has a RULES.md overlap (2yww vs zg7t) but sections are 100+ lines apart. Wave 2 runs clean after wave 1 commits. Slower than Strategy A due to two waves.

## Coverage Verification
- Inventory: 6 total tasks (6 ready + 0 blocked)
- Strategy A: 6 assigned across 1 wave -- PASS
- Strategy B: 6 assigned across 1 wave -- PASS
- Strategy C: 6 assigned across 2 waves -- PASS

## Metadata
- Epics: none
- Task metadata files: .beads/agent-summaries/_session-5da05acb/task-metadata/ (6 files)
- Session dir: .beads/agent-summaries/_session-5da05acb

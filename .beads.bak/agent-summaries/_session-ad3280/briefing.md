# Session Briefing

## Task Inventory
| ID | Epic | Title | Priority | Type | Agent | Files | Risk |
|----|------|-------|----------|------|-------|-------|------|
| ant-farm-0cf | ant-farm-21d | Parallelize review prompt composition with implementation via bash scripts | P1 | feature | devops-engineer | pantry.md, RULES.md, scripts/*.sh (new) | MED |
| ant-farm-7k1 | ant-farm-6k0 | AGG-009: Add severity conflict handling guidance to big-head.md | P2 | task | technical-writer | ~/.claude/agents/big-head.md | LOW |
| ant-farm-cifp | ant-farm-6k0 | Add explicit scope fencing to Nitpicker agent definitions per review type | P2 | task | technical-writer | ~/.claude/agents/nitpicker.md, reviews.md, pantry.md | MED |
| ant-farm-w7p | ant-farm-6k0 | (BUG) Improve Scout agent type tie-breaking with deeper catalog reads and explicit fallback | P2 | bug | technical-writer | orchestration/templates/scout.md | LOW |

**Ready**: 4 tasks | **Blocked**: 1 task (ant-farm-nly — blocked by ant-farm-5dt: pantry.md Review Mode does not generate Big Head preview file for CCO audit [P3 open])

## File Modification Matrix
| File | Tasks | Risk |
|------|-------|------|
| orchestration/templates/pantry.md | ant-farm-0cf, ant-farm-cifp | MED |
| orchestration/RULES.md | ant-farm-0cf | LOW |
| scripts/compose-review-skeletons.sh (new) | ant-farm-0cf | LOW |
| scripts/fill-review-slots.sh (new) | ant-farm-0cf | LOW |
| ~/.claude/agents/big-head.md | ant-farm-7k1 | LOW |
| ~/.claude/agents/nitpicker.md | ant-farm-cifp | LOW |
| orchestration/templates/reviews.md | ant-farm-cifp | LOW |
| orchestration/templates/scout.md | ant-farm-w7p | LOW |

## Dependency Chains
- ant-farm-5dt → ant-farm-nly (ant-farm-nly blocked: Big Head preview file must exist before consolidation file prominence fix makes sense)
- No dependency chains among the 4 ready tasks

## Proposed Strategies

### Strategy A: Full Parallel (Recommended)
**Wave 1** (4 agents): ant-farm-0cf, ant-farm-7k1, ant-farm-cifp, ant-farm-w7p
**Rationale**: The only shared file is pantry.md, touched by ant-farm-0cf (Step 1.5 insertion near top + Section 2 deprecation) and ant-farm-cifp (REVIEW_TYPE marker in data file templates — a different section). These are different sections of pantry.md and both agents should `git pull --rebase` before committing. All other files are independent. The conflict risk is MEDIUM at worst, acceptable for a 2-second rebase on a markdown file. All 4 tasks fit comfortably under the 7-agent ceiling. P1 task (ant-farm-0cf) and P2 tasks run together since there are no blocking relationships.
**Risk**: LOW-MEDIUM overall. If both agents modify pantry.md's Step 5/Section 2 area simultaneously, a rebase conflict is possible but easily resolved since both changes are additive text insertions in distinct locations.

### Strategy B: Serial by Epic
**Wave 1** (2 agents): ant-farm-7k1, ant-farm-w7p (epic ant-farm-6k0 independent tasks — no pantry.md touches)
**Wave 2** (2 agents): ant-farm-0cf, ant-farm-cifp (both touch pantry.md — serialize within wave via agent batching, or allow parallel with rebase)
**Rationale**: Eliminates all pantry.md conflict risk by running the two pantry.md-touching tasks after the independent ones complete. Adds one extra wave of latency (~30-40 min).
**Risk**: LOW. Zero conflict risk at cost of sequential execution.

### Strategy C: Batch pantry.md tasks to single agent
**Wave 1** (3 agents): ant-farm-7k1, ant-farm-w7p, ant-farm-0cf+ant-farm-cifp (batched)
**Wave 1 agent 3 handles**: ant-farm-0cf then ant-farm-cifp in sequence on pantry.md
**Rationale**: Eliminates pantry.md conflict entirely by giving one agent ownership of all pantry.md changes. Slightly longer single agent task but clean.
**Risk**: LOW. One agent serializes pantry.md; other files remain fully parallel.

## Metadata
- Epics: ant-farm-21d, ant-farm-6k0
- Task metadata files: .beads/agent-summaries/_session-ad3280/task-metadata/ (4 files)
- Session dir: .beads/agent-summaries/_session-ad3280/

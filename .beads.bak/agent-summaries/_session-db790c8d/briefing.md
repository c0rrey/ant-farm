# Session Briefing

## Task Inventory
| ID | Epic | Title | Priority | Type | Agent | Files | Risk |
|----|------|-------|----------|------|-------|-------|------|
| ant-farm-x8iw | none | Scout agent frontmatter declares model: sonnet, contradicting RULES.md model: opus | P1 | bug | general-purpose | agents/scout-organizer.md, orchestration/GLOSSARY.md, README.md | LOW |
| ant-farm-h94m | none | checkpoints.md describes PC spawning code-reviewer but pest-control agent lacks Task tool | P1 | bug | technical-writer | orchestration/templates/checkpoints.md, agents/pest-control.md, orchestration/RULES.md | HIGH |
| ant-farm-wg2i | none | installed pre-push hook is fatal on sync failure, contradicting install-hooks.sh non-fatal design | P1 | bug | devops-engineer | .git/hooks/pre-push, CONTRIBUTING.md | LOW |
| ant-farm-zuae | none | WWD checkpoint skipped entirely in production session despite being documented as mandatory gate | P1 | bug | technical-writer | orchestration/RULES.md, orchestration/templates/checkpoints.md | HIGH |

**Total**: 4 tasks | **Wave 1 (ready)**: 4 tasks | **Later waves (blocked)**: 0 tasks

## File Modification Matrix
| File | Tasks | Risk |
|------|-------|------|
| orchestration/templates/checkpoints.md | ant-farm-h94m, ant-farm-zuae | HIGH |
| orchestration/RULES.md | ant-farm-h94m (conditional), ant-farm-zuae | MEDIUM |
| agents/scout-organizer.md | ant-farm-x8iw | LOW |
| orchestration/GLOSSARY.md | ant-farm-x8iw | LOW |
| README.md | ant-farm-x8iw | LOW |
| .git/hooks/pre-push | ant-farm-wg2i | LOW |
| CONTRIBUTING.md | ant-farm-wg2i | LOW |
| agents/pest-control.md | ant-farm-h94m | LOW |

### Conflict Detail: checkpoints.md (HIGH)
- **ant-farm-h94m** modifies: Pest Control Overview (lines 13-24), "Agent type (spawned by Pest Control): code-reviewer" fields at lines 17, 113, 191, **266**, 339, 413, 504, 614
- **ant-farm-zuae** modifies: WWD "When" field at line **264**, WWD section starting at line 262
- **Overlap zone**: Lines 262-266 in the WWD section -- h94m removes "Agent type" at line 266, zuae rewrites the "When" field at line 264. Both tasks edit the same ~5-line block. Direct merge conflict likely.

### Conflict Detail: RULES.md (MEDIUM)
- **ant-farm-h94m**: May touch Agent Types table (only if Option B chosen -- aligning reality to docs). If Option A (recommended -- align docs to reality), h94m does NOT modify RULES.md.
- **ant-farm-zuae**: Modifies Step 3 (lines 118-119), Hard Gates table (lines 259-260), adds progress.log WWD milestone
- **Risk assessment**: If h94m takes Option A (recommended), no overlap. If Option B, the Agent Types table is in a different section from zuae's changes -- manageable via rebase.

## Dependency Chains
- No explicit `bd` dependencies between any of the 4 tasks.
- **Implicit conflict dependency**: ant-farm-h94m and ant-farm-zuae both modify checkpoints.md (same section). Should be serialized or batched.

## Proposed Strategies

### Strategy A: Serialize Conflicting Pair (Recommended)
**Wave 1** (3 agents): ant-farm-x8iw (general-purpose), ant-farm-wg2i (devops-engineer), ant-farm-h94m (technical-writer)
**Wave 2** (1 agent): ant-farm-zuae (technical-writer)
**Rationale**: h94m and zuae both modify checkpoints.md lines 262-266 (WWD section). Running h94m first in Wave 1 resolves the spawn architecture language. zuae then modifies the updated WWD section in Wave 2, building on h94m's changes without merge conflicts. x8iw and wg2i are fully independent -- no file overlaps with any other task.
**Risk**: LOW overall. Wave 2 has only 1 task, so no conflict possible. Wave 1 tasks have zero file overlaps.

### Strategy B: Batch Conflicting Pair to Single Agent
**Wave 1** (3 agents): ant-farm-x8iw (general-purpose), ant-farm-wg2i (devops-engineer), ant-farm-h94m + ant-farm-zuae (technical-writer, batched)
**Rationale**: Batching h94m and zuae to a single technical-writer agent eliminates all conflict risk. The agent handles both checkpoints.md and RULES.md changes in a single pass, ensuring internal consistency. x8iw and wg2i run in parallel with no overlaps.
**Risk**: LOW. No file conflicts at all. Slight risk of agent overload (2 tasks with substantial doc rewrites), but both tasks are well-scoped P1 bugs with clear acceptance criteria.

### Strategy C: Full Parallel with Rebase
**Wave 1** (4 agents): ant-farm-x8iw (general-purpose), ant-farm-wg2i (devops-engineer), ant-farm-h94m (technical-writer), ant-farm-zuae (technical-writer)
**Rationale**: Maximum parallelism. All 4 agents run simultaneously. h94m and zuae both touch checkpoints.md but in adjacent (not identical) lines -- rebase may succeed automatically.
**Risk**: MEDIUM. Lines 264 and 266 are only 2 lines apart in the WWD section. Git rebase will likely see this as a conflict requiring manual resolution. Not recommended unless speed is critical.

## Coverage Verification
- Inventory: 4 total tasks (4 ready + 0 blocked)
- Strategy A: 4 assigned across 2 waves -- PASS
- Strategy B: 4 assigned across 1 wave -- PASS
- Strategy C: 4 assigned across 1 wave -- PASS

## Metadata
- Epics: none
- Task metadata files: .beads/agent-summaries/_session-db790c8d/task-metadata/ (4 files)
- Session dir: .beads/agent-summaries/_session-db790c8d

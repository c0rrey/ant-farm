# Session Briefing

## FIX-CYCLE: P1/P2 Review Findings (RETRY -- zero task-level file overlaps per wave)

## Task Inventory
| ID | Epic | Title | Priority | Type | Agent | Files | Risk |
|----|------|-------|----------|------|-------|-------|------|
| ant-farm-5ujg | none | crumb sync referenced in AGENTS.md but does not exist | P1 | bug | general-purpose | AGENTS.md | HIGH |
| ant-farm-rlne | none | Pantry placeholder contamination detection ambiguous | P1 | bug | general-purpose | orchestration/templates/pantry.md | LOW |
| ant-farm-rgg3 | none | build-review-prompts.sh FOCUS_AREAS_FILE missing readable check | P1 | bug | general-purpose | scripts/build-review-prompts.sh | HIGH |
| ant-farm-tbis | none | Stale SESSION_DIR path in 6 files | P2 | bug | general-purpose | AGENTS.md, CLAUDE.md, +4 templates | HIGH |
| ant-farm-9ahp | none | setup.sh does not copy CLAUDE.md to ~/.claude/CLAUDE.md | P2 | bug | general-purpose | scripts/setup.sh | LOW |
| ant-farm-5ohl | none | build-review-prompts.sh resolve_arg exit code swallowed | P2 | bug | general-purpose | scripts/build-review-prompts.sh | HIGH |
| ant-farm-qv4a | none | Temp file leak on error paths in fill_slot and big-head dedup | P2 | bug | general-purpose | scripts/build-review-prompts.sh, big-head-skeleton.md | HIGH |
| ant-farm-52ka | none | CODEBASE_ROOT template literal without substitution guidance | P2 | bug | general-purpose | orchestration/RULES-decompose.md | LOW |
| ant-farm-5fq0 | none | Dolt mode switch has no rollback on error | P2 | bug | general-purpose | orchestration/templates/decomposition.md | LOW |
| ant-farm-7fc3 | none | Big-head-skeleton polling timeout hardcoded | P2 | bug | general-purpose | orchestration/templates/big-head-skeleton.md | MED |
| ant-farm-nmpw | none | Scout error tasks in wave plan produce invalid conflict analysis | P2 | bug | general-purpose | orchestration/templates/scout.md | MED |
| ant-farm-z305 | none | work.md task count check includes trails | P2 | bug | general-purpose | skills/work.md | LOW |
| ant-farm-c47w | none | CLI tool naming inconsistency crumb vs bd | P2 | bug | general-purpose | AGENTS.md, CLAUDE.md, RULES.md | HIGH |

**Total**: 13 tasks | **Wave 1 (ready)**: 13 tasks | **Later waves (blocked)**: 0 tasks

## File Modification Matrix
| File | Tasks | Risk |
|------|-------|------|
| `AGENTS.md` | 5ujg, tbis, c47w | HIGH (3 tasks) |
| `scripts/build-review-prompts.sh` | rgg3, 5ohl, qv4a | HIGH (3 tasks) |
| `CLAUDE.md` | tbis, c47w | MED (2 tasks, different sections) |
| `orchestration/templates/scout.md` | tbis, nmpw | MED (2 tasks, different sections: L14 vs L83-110) |
| `orchestration/templates/big-head-skeleton.md` | qv4a, 7fc3 | MED (2 tasks, different sections: L114-127 vs L91-106) |
| `orchestration/templates/pantry.md` | rlne | LOW |
| `orchestration/reference/dependency-analysis.md` | tbis | LOW |
| `orchestration/templates/dirt-pusher-skeleton.md` | tbis | LOW |
| `orchestration/templates/scribe-skeleton.md` | tbis | LOW |
| `orchestration/RULES-decompose.md` | 52ka | LOW |
| `orchestration/templates/decomposition.md` | 5fq0 | LOW |
| `orchestration/RULES.md` | c47w | LOW |
| `scripts/setup.sh` | 9ahp | LOW |
| `skills/work.md` | z305 | LOW |

## Dependency Chains
- No explicit dependency chains between these 13 tasks.
- File conflicts create implicit ordering: AGENTS.md (3 tasks must serialize across 3 waves), build-review-prompts.sh (3 tasks must serialize across 3 waves), CLAUDE.md (2 tasks across 2 waves), scout.md (2 tasks across 2 waves), big-head-skeleton.md (2 tasks across 2 waves).

## Proposed Strategies

### Strategy A: Three-Wave Serialization by File Conflict (Recommended)

Separate all file-conflicting tasks into distinct waves so that NO file appears in more than one task within any wave. This guarantees zero task-level file overlaps per wave.

**Wave 1** (7 agents, 7 tasks -- zero file overlaps):
1. ant-farm-5ujg (general-purpose) -- AGENTS.md
2. ant-farm-rgg3 (general-purpose) -- scripts/build-review-prompts.sh
3. ant-farm-rlne (general-purpose) -- orchestration/templates/pantry.md
4. ant-farm-9ahp (general-purpose) -- scripts/setup.sh
5. ant-farm-52ka (general-purpose) -- orchestration/RULES-decompose.md
6. ant-farm-5fq0 (general-purpose) -- orchestration/templates/decomposition.md
7. ant-farm-nmpw (general-purpose) -- orchestration/templates/scout.md

**File overlap check -- Wave 1**: Each task touches a unique file. ZERO overlaps.

**Wave 2** (4 agents, 4 tasks -- zero file overlaps):
1. ant-farm-tbis (general-purpose) -- AGENTS.md, CLAUDE.md, orchestration/templates/scout.md, orchestration/reference/dependency-analysis.md, orchestration/templates/dirt-pusher-skeleton.md, orchestration/templates/scribe-skeleton.md
2. ant-farm-5ohl (general-purpose) -- scripts/build-review-prompts.sh
3. ant-farm-7fc3 (general-purpose) -- orchestration/templates/big-head-skeleton.md
4. ant-farm-z305 (general-purpose) -- skills/work.md

**File overlap check -- Wave 2**: tbis touches AGENTS.md (5ujg done in W1), CLAUDE.md (unique in W2), scout.md (nmpw done in W1). 5ohl touches build-review-prompts.sh (rgg3 done in W1). 7fc3 touches big-head-skeleton.md (unique in W2). z305 touches work.md (unique). ZERO overlaps within Wave 2.

**Wave 3** (2 agents, 2 tasks -- zero file overlaps):
1. ant-farm-c47w (general-purpose) -- AGENTS.md, CLAUDE.md, orchestration/RULES.md
2. ant-farm-qv4a (general-purpose) -- scripts/build-review-prompts.sh, orchestration/templates/big-head-skeleton.md

**File overlap check -- Wave 3**: c47w touches AGENTS.md (5ujg W1, tbis W2 -- done), CLAUDE.md (tbis W2 -- done), RULES.md (unique). qv4a touches build-review-prompts.sh (rgg3 W1, 5ohl W2 -- done), big-head-skeleton.md (7fc3 W2 -- done). ZERO overlaps within Wave 3.

**Dependency gates**: Wave 2 starts after Wave 1 completes. Wave 3 starts after Wave 2 completes.
**Rationale**: The two 3-way conflict clusters (AGENTS.md and build-review-prompts.sh) force at least 3 waves. This arrangement maximizes Wave 1 parallelism (7 tasks), then handles the second conflicting task per file in Wave 2 (4 tasks), and the third in Wave 3 (2 tasks). Every wave has strictly zero task-level file overlaps.
**Risk**: LOW. Zero file overlaps within any wave. Each wave commits cleanly before the next starts.

### Strategy B: Two-Wave with P1 Priority and Batched Conflicts

Run all P1 tasks plus conflict-free P2 tasks in Wave 1. Batch remaining file-conflicting P2 tasks into single agents in Wave 2 to avoid file overlaps.

**Wave 1** (7 agents, 7 tasks -- zero file overlaps):
1. ant-farm-5ujg (general-purpose) -- AGENTS.md
2. ant-farm-rlne (general-purpose) -- orchestration/templates/pantry.md
3. ant-farm-rgg3 (general-purpose) -- scripts/build-review-prompts.sh
4. ant-farm-9ahp (general-purpose) -- scripts/setup.sh
5. ant-farm-52ka (general-purpose) -- orchestration/RULES-decompose.md
6. ant-farm-5fq0 (general-purpose) -- orchestration/templates/decomposition.md
7. ant-farm-nmpw (general-purpose) -- orchestration/templates/scout.md

**File overlap check -- Wave 1**: Each task touches a unique file. ZERO overlaps.

**Wave 2** (4 agents, 6 tasks -- zero file overlaps via batching):
1. ant-farm-tbis + ant-farm-c47w (general-purpose) -- AGENTS.md, CLAUDE.md, RULES.md, scout.md, +3 templates [BATCHED: both touch AGENTS.md and CLAUDE.md, single agent serializes edits]
2. ant-farm-5ohl + ant-farm-qv4a (general-purpose) -- scripts/build-review-prompts.sh, big-head-skeleton.md [BATCHED: both touch build-review-prompts.sh, single agent serializes edits]
3. ant-farm-7fc3 (general-purpose) -- orchestration/templates/big-head-skeleton.md
4. ant-farm-z305 (general-purpose) -- skills/work.md

**File overlap check -- Wave 2**: Agent 1 handles tbis+c47w sequentially (no inter-agent conflict on AGENTS.md/CLAUDE.md). Agent 2 handles 5ohl+qv4a sequentially (no inter-agent conflict on build-review-prompts.sh). However: Agent 2 (qv4a) touches big-head-skeleton.md AND Agent 3 (7fc3) touches big-head-skeleton.md -- this IS a task-level file overlap on big-head-skeleton.md even though they are different sections (L114-127 vs L91-106).

**NOTE**: This strategy has 1 task-level file overlap (big-head-skeleton.md in Wave 2 between qv4a and 7fc3). If the SSV checker flags this, Strategy A is the safe alternative.

**Dependency gates**: Wave 2 starts after Wave 1 completes.
**Rationale**: Fewer waves (2 vs 3) means faster total execution. Batching eliminates most conflicts. One remaining MEDIUM-risk overlap on big-head-skeleton.md (well-separated sections, rebase-safe).
**Risk**: MEDIUM. One task-level file overlap on big-head-skeleton.md in Wave 2.

### Strategy C: Three-Wave Priority-Ordered

Separate by priority tier first, then by file conflicts.

**Wave 1** (3 agents, 3 tasks -- P1 only, zero file overlaps):
1. ant-farm-5ujg (general-purpose) -- AGENTS.md
2. ant-farm-rlne (general-purpose) -- orchestration/templates/pantry.md
3. ant-farm-rgg3 (general-purpose) -- scripts/build-review-prompts.sh

**File overlap check -- Wave 1**: Each task touches a unique file. ZERO overlaps.

**Wave 2** (7 agents, 7 tasks -- P2 first batch, zero file overlaps):
1. ant-farm-tbis (general-purpose) -- AGENTS.md, CLAUDE.md, scout.md, +3 templates
2. ant-farm-5ohl (general-purpose) -- scripts/build-review-prompts.sh
3. ant-farm-9ahp (general-purpose) -- scripts/setup.sh
4. ant-farm-52ka (general-purpose) -- orchestration/RULES-decompose.md
5. ant-farm-5fq0 (general-purpose) -- orchestration/templates/decomposition.md
6. ant-farm-nmpw (general-purpose) -- orchestration/templates/scout.md
7. ant-farm-z305 (general-purpose) -- skills/work.md

**File overlap check -- Wave 2**: tbis touches scout.md AND nmpw touches scout.md -- this IS a task-level file overlap.

**NOTE**: This strategy has 1 task-level file overlap (scout.md in Wave 2 between tbis and nmpw). Moving nmpw to Wave 3 would fix it but creates a 4-wave plan. If the SSV checker flags this, Strategy A is the safe alternative.

**Wave 3** (3 agents, 3 tasks -- P2 remainder, zero file overlaps):
1. ant-farm-c47w (general-purpose) -- AGENTS.md, CLAUDE.md, RULES.md
2. ant-farm-qv4a (general-purpose) -- scripts/build-review-prompts.sh, big-head-skeleton.md
3. ant-farm-7fc3 (general-purpose) -- orchestration/templates/big-head-skeleton.md

**File overlap check -- Wave 3**: qv4a touches big-head-skeleton.md AND 7fc3 touches big-head-skeleton.md -- this IS a task-level file overlap.

**NOTE**: This strategy has 2 task-level file overlaps across Waves 2 and 3. Strategy A remains the only fully clean option.

**Dependency gates**: Wave 2 after Wave 1. Wave 3 after Wave 2.
**Rationale**: Priority-first ordering ensures P1 fixes land earliest. But the file conflict constraints make it harder to achieve zero overlaps with only priority-based grouping.
**Risk**: MEDIUM. Two task-level file overlaps (scout.md in W2, big-head-skeleton.md in W3).

## Coverage Verification
- Inventory: 13 total tasks (13 ready + 0 blocked)
- Strategy A: 13 assigned across 3 waves (7 + 4 + 2) -- PASS
- Strategy B: 13 assigned across 2 waves (7 + 6) -- PASS
- Strategy C: 13 assigned across 3 waves (3 + 7 + 3) -- PASS

## Metadata
- Epics: none
- Task metadata files: .beads/agent-summaries/_session-20260313-021827/task-metadata/ (13 files)
- Session dir: .beads/agent-summaries/_session-20260313-021827

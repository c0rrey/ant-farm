# Session Briefing

## Task Inventory

### Ready (5 tasks)
| ID | Epic | Title | Priority | Type | Agent | Files | Risk |
|----|------|-------|----------|------|-------|-------|------|
| ant-farm-wi0 | ant-farm-amk | AGG-022: Standardize variable naming across templates | P1 | task | refactoring-specialist | orchestration/templates/*.md, RULES.md, PLACEHOLDER_CONVENTIONS.md | HIGH |
| ant-farm-jxf | ant-farm-amk | AGG-025: Create canonical glossary for key terms | P2 | task | technical-writer | README.md or new orchestration/GLOSSARY.md | LOW |
| ant-farm-4vg | ant-farm-amk | AGG-027: Standardize review type naming (display vs short names) | P2 | task | technical-writer | orchestration/templates/reviews.md, nitpicker-skeleton.md, implementation.md | MED |
| ant-farm-s57 | ant-farm-amk | AGG-028: Standardize timestamp format string across templates | P3 | task | technical-writer | orchestration/templates/checkpoints.md, big-head-skeleton.md | MED |
| ant-farm-k32 | ant-farm-amk | MANDATORY keyword formatting inconsistent across templates | P3 | task | refactoring-specialist | orchestration/templates/implementation.md, dirt-pusher-skeleton.md, checkpoints.md | MED |

### Blocked (4 tasks — within epic)
| ID | Epic | Title | Priority | Type | Agent | Blocker | Files | Risk |
|----|------|-------|----------|------|-------|---------|-------|------|
| ant-farm-8jg | ant-farm-amk | AGG-026: Standardize agent name casing and article usage | P2 | task | refactoring-specialist | ant-farm-jxf | orchestration/templates/*.md, RULES.md, README.md | MED |
| ant-farm-81y | ant-farm-amk | AGG-029: Add inline acronym expansions to architecture diagram | P3 | task | technical-writer | ant-farm-jxf | README.md | LOW |
| ant-farm-x0m | ant-farm-amk | Wave concept used in RULES.md but never defined | P3 | task | technical-writer | ant-farm-jxf | RULES.md, checkpoints.md, GLOSSARY.md | LOW |
| ant-farm-cn0 | ant-farm-amk | Timestamp format YYYYMMDD-HHMMSS repeated 5+ times | P3 | task | technical-writer | ant-farm-s57 | orchestration/templates/checkpoints.md, pantry.md | MED |

### External Tasks Unblocked by This Epic (not worked in this session)
| ID | Epic | Title | Priority | Blocked By (in-epic) | Note |
|----|------|-------|----------|----------------------|------|
| ant-farm-1jo | ant-farm-azg | AGG-045: Specify wave parallelism and concurrency rules | P2 | ant-farm-x0m | fully unblocked once x0m done |
| ant-farm-5q3 | ant-farm-753 | AGG-039: Add complete error recovery procedures | P1 | ant-farm-x0m | ALSO blocked by ant-farm-98c (external P3 bug) — completing x0m alone will NOT fully unblock this task |
| ant-farm-7qp | ant-farm-7hh | AGG-010: Resolve timestamp ownership conflict (P1 bug) | P1 | ant-farm-s57 | fully unblocked once s57 done |
| ant-farm-pid | ant-farm-753 | AGG-038: Clarify wildcard artifact path matching | P1 | ant-farm-s57 | fully unblocked once s57 done |

**Ready**: 5 tasks | **Blocked (in-epic)**: 4 tasks

## File Modification Matrix
| File | Tasks | Risk |
|------|-------|------|
| orchestration/templates/checkpoints.md | ant-farm-wi0, ant-farm-s57, ant-farm-k32, ant-farm-cn0 | HIGH (4 tasks) |
| orchestration/templates/implementation.md | ant-farm-wi0, ant-farm-4vg, ant-farm-k32 | HIGH (3 tasks) |
| orchestration/RULES.md | ant-farm-wi0, ant-farm-8jg, ant-farm-x0m | HIGH (3 tasks) |
| orchestration/templates/*.md (all templates, broad) | ant-farm-wi0, ant-farm-8jg | HIGH |
| README.md | ant-farm-jxf, ant-farm-81y, ant-farm-8jg | MED (3 tasks, different sections) |
| orchestration/templates/pantry.md | ant-farm-wi0, ant-farm-cn0 | MED |
| orchestration/templates/reviews.md | ant-farm-wi0, ant-farm-4vg | MED |
| orchestration/templates/big-head-skeleton.md | ant-farm-wi0, ant-farm-s57 | MED |
| orchestration/templates/dirt-pusher-skeleton.md | ant-farm-wi0, ant-farm-k32 | MED |
| orchestration/templates/nitpicker-skeleton.md | ant-farm-wi0, ant-farm-4vg | MED |
| orchestration/GLOSSARY.md (new) | ant-farm-jxf (creates), ant-farm-x0m (adds wave def), ant-farm-8jg (adds naming convention) | MED |
| orchestration/PLACEHOLDER_CONVENTIONS.md | ant-farm-wi0 | LOW |

## Dependency Chains

### Within-epic
- ant-farm-jxf → ant-farm-8jg (glossary must exist before standardizing agent name casing/articles)
- ant-farm-jxf → ant-farm-81y (glossary must exist before adding acronym expansions to README diagram)
- ant-farm-jxf → ant-farm-x0m (glossary must exist before adding "wave" definition to it)
- ant-farm-s57 → ant-farm-cn0 (timestamp format must be canonical before deduplicating repeated definitions)

### Cross-epic (external tasks unblocked by this work)
- ant-farm-x0m → ant-farm-1jo (wave definition needed before specifying wave parallelism rules in ant-farm-azg epic)
- ant-farm-x0m → ant-farm-5q3 (wave definition needed for error recovery procedures — BUT ant-farm-5q3 also blocked by external ant-farm-98c P3 bug; x0m completion alone does not fully unblock it)
- ant-farm-s57 → ant-farm-7qp (timestamp format canonical before resolving timestamp ownership conflict in ant-farm-7hh epic)
- ant-farm-s57 → ant-farm-pid (timestamp format canonical before clarifying wildcard artifact path matching in ant-farm-753 epic)

## Proposed Strategies

### Strategy A: Serialize wi0, Then Two Parallel Fans (Recommended)

**Wave 1** (1 agent): ant-farm-wi0
- Broad variable-name rename across ALL template files. Isolated in its own wave to eliminate merge conflicts for every subsequent task.

**Wave 2** (4 agents): ant-farm-jxf, ant-farm-4vg, ant-farm-s57, ant-farm-k32
- ant-farm-jxf: Creates new GLOSSARY.md — no conflict (new file)
- ant-farm-4vg: reviews.md + nitpicker-skeleton.md + implementation.md (review type names section)
- ant-farm-s57: checkpoints.md (timestamp section) + big-head-skeleton.md
- ant-farm-k32: implementation.md (MANDATORY section) + dirt-pusher-skeleton.md + checkpoints.md (MANDATORY section)
- Conflicts to manage: s57 and k32 both touch checkpoints.md (different sections); 4vg and k32 both touch implementation.md (different sections). Both pairs use `git pull --rebase` before commit.

**Wave 3** (3 agents): ant-farm-8jg, ant-farm-81y, ant-farm-x0m
- All three depend on ant-farm-jxf (Wave 2). All can run in parallel once jxf commits.
- ant-farm-8jg: Prose casing across all templates + RULES.md
- ant-farm-81y: README.md diagram section only (isolated)
- ant-farm-x0m: GLOSSARY.md (adds wave def) + RULES.md cross-reference + checkpoints.md cross-reference
- Conflict: 8jg and x0m both touch RULES.md (different sections — casing vs wave definition). Rebase discipline required.

**Wave 4** (1 agent): ant-farm-cn0
- Depends on ant-farm-s57 (Wave 2). Deduplicates the now-canonical timestamp format in checkpoints.md and pantry.md.

**Summary**: 4 waves, max 4 concurrent agents, all 9 tasks covered.
**Rationale**: wi0's broad variable rename is the single highest-conflict operation in the epic — isolating it in Wave 1 makes every subsequent wave's file conflicts manageable rather than catastrophic. Wave 2 is the most parallel-safe of the remaining tasks, with only two cross-task file conflicts (checkpoints.md, implementation.md) in clearly separate sections. Wave 3 fans out the three jxf-dependent tasks, and Wave 4 is a lightweight DRY cleanup.
**Risk**: MEDIUM. The only real conflict zones are in Wave 2 (two pairs sharing files in different sections) and Wave 3 (8jg + x0m sharing RULES.md in different sections). All manageable with rebase discipline.

---

### Strategy B: Priority-Gated Waves (Slowest, Lowest Risk)

**Wave 1** (1 agent): ant-farm-wi0 (P1)
**Wave 2** (2 agents): ant-farm-jxf, ant-farm-4vg (P2 tasks that have no blockers)
**Wave 3** (3 agents): ant-farm-8jg, ant-farm-81y, ant-farm-x0m (P2/P3 tasks unblocked by jxf in Wave 2; run in parallel alongside each other)
**Wave 4** (2 agents): ant-farm-s57, ant-farm-k32 (P3 tasks with no blockers — could run in Wave 2, but strict priority ordering keeps them here)
**Wave 5** (1 agent): ant-farm-cn0 (P3, unblocked by s57 in Wave 4)

**Rationale**: Strict priority ordering and minimum file contention per wave.
**Risk**: LOW per-wave. But requires 5 sequential waves; slowest option. Waves 2 and 3 could be merged (jxf, 4vg, s57, k32 all have no blockers) which is essentially Strategy A.

---

### Strategy C: Aggressive Parallel (Fastest, Highest Risk)

**Wave 1** (5 agents): ant-farm-wi0, ant-farm-jxf, ant-farm-4vg, ant-farm-s57, ant-farm-k32
**Wave 2** (4 agents): ant-farm-8jg, ant-farm-81y, ant-farm-x0m, ant-farm-cn0

**Rationale**: All 9 tasks in 2 waves. Wave 2 starts as soon as jxf and s57 are committed (does not need to wait for all of Wave 1 to finish).
**Risk**: HIGH. ant-farm-wi0 renames variables across every template file while ant-farm-4vg, ant-farm-s57, and ant-farm-k32 are simultaneously making targeted edits to those same files. Near-certain merge conflicts. Not recommended.

---

## Summary Recommendation

Use **Strategy A** (4 waves). It correctly sequences the one high-blast-radius task (wi0) before any targeted edits, fans out the four independent tasks in Wave 2, then resolves all dependency-gated tasks in Waves 3 and 4.

**Side effect**: Completing this epic fully unblocks 2 external P1 tasks (ant-farm-7qp, ant-farm-pid) and 1 external P2 task (ant-farm-1jo). ant-farm-5q3 (external P1) will remain blocked due to its second dependency on ant-farm-98c (external P3 bug in ant-farm-753 epic) — not addressable in this session.

## Metadata
- Epics: ant-farm-amk
- Task metadata files: .beads/agent-summaries/_session-8b93f5/task-metadata/ (9 files: wi0, jxf, 4vg, s57, k32, 8jg, 81y, x0m, cn0)
- Session dir: .beads/agent-summaries/_session-8b93f5

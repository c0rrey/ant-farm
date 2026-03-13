# Session Briefing

## Task Inventory
| ID | Epic | Title | Priority | Type | Agent | Files | Risk |
|----|------|-------|----------|------|-------|-------|------|
| ant-farm-033 | none | Installation guide omits pre-commit PII scrub hook documentation | P2 | bug | technical-writer | docs/installation-guide.md | MED |
| ant-farm-0gs | none | Step 0 wildcard glob may match stale reports from prior review cycles | P2 | bug | general-purpose | orchestration/templates/reviews.md, orchestration/RULES.md | HIGH |
| ant-farm-1b8 | none | Installation guide uninstall uses wrong path ~/.git/ instead of .git/ | P2 | bug | technical-writer | docs/installation-guide.md | MED |
| ant-farm-1e1 | none | Incomplete 'data file' to 'task brief' rename from ant-farm-0o4 | P2 | bug | technical-writer | dirt-pusher-skeleton.md, big-head-skeleton.md, README.md | MED |
| ant-farm-1y4 | none | SETUP.md hardcoded personal path blocks new adopters | P2 | bug | technical-writer | orchestration/SETUP.md | LOW |
| ant-farm-27x | none | big-head.md includes Edit tool unnecessarily | P2 | bug | general-purpose | agents/big-head.md | LOW |
| ant-farm-32gz | none | SESSION_ID collision: same-second Queens produce identical session directory | P2 | bug | general-purpose | orchestration/RULES.md, PLACEHOLDER_CONVENTIONS.md | HIGH |
| ant-farm-7yv | none | Pre-commit hook silently allows PII when scrub script not executable | P2 | bug | devops-engineer | scripts/install-hooks.sh, scripts/scrub-pii.sh | MED |
| ant-farm-9j6z | none | Filename typo: review-clarify.md should be review-clarity.md | P2 | bug | general-purpose | unknown (needs investigation) | LOW |
| ant-farm-auas | none | Missing input validation guards on Queen-owned review path | P2 | bug | general-purpose | orchestration/RULES.md, pantry.md, checkpoints.md, nitpicker-skeleton.md, big-head-skeleton.md | HIGH |
| ant-farm-bi3 | none | Pantry template lacks fail-fast for missing task-metadata dir and empty file list | P2 | bug | prompt-engineer | orchestration/templates/pantry.md | HIGH |
| ant-farm-cl8 | none | scrub-pii.sh only matches quoted emails, misses unquoted | P2 | bug | devops-engineer | scripts/scrub-pii.sh | LOW |
| ant-farm-txw | none | Templates lack failure artifact specification for error paths | P2 | bug | prompt-engineer | big-head-skeleton.md, pantry.md, reviews.md | HIGH |
| ant-farm-yb95 | none | Incomplete deprecation cleanup: pantry-review, Section 2, RULES.md | P2 | bug | general-purpose | agents/pantry-review.md, pantry.md, orchestration/RULES.md | HIGH |
| ant-farm-yfnj | none | pantry.md Section 2 circular reference fix incomplete | P2 | bug | prompt-engineer | orchestration/templates/pantry.md | HIGH |
| ant-farm-z3j | none | Checkpoint thresholds undefined: small file, sampling N<3, CCB unbounded | P2 | bug | prompt-engineer | orchestration/templates/checkpoints.md | MED |
| ant-farm-z69 | none | Pre-push hook blocks all git pushes when sync-to-claude.sh fails | P2 | bug | devops-engineer | scripts/install-hooks.sh | MED |

**Total**: 17 tasks | **Wave 1 (ready)**: 17 tasks | **Later waves (blocked)**: 0 tasks

## File Modification Matrix
| File | Tasks | Risk |
|------|-------|------|
| orchestration/templates/pantry.md | ant-farm-bi3, ant-farm-yfnj, ant-farm-yb95, ant-farm-txw, ant-farm-auas | HIGH (5 tasks!) |
| orchestration/RULES.md | ant-farm-0gs, ant-farm-32gz, ant-farm-yb95, ant-farm-auas | HIGH (4 tasks) |
| docs/installation-guide.md | ant-farm-033, ant-farm-1b8 | MED |
| scripts/install-hooks.sh | ant-farm-7yv, ant-farm-z69 | MED |
| orchestration/templates/big-head-skeleton.md | ant-farm-1e1, ant-farm-txw, ant-farm-auas | MED |
| orchestration/templates/reviews.md | ant-farm-0gs, ant-farm-txw | MED |
| orchestration/templates/checkpoints.md | ant-farm-z3j, ant-farm-auas | MED |
| orchestration/templates/nitpicker-skeleton.md | ant-farm-auas | LOW |
| orchestration/templates/dirt-pusher-skeleton.md | ant-farm-1e1 | LOW |
| README.md | ant-farm-1e1 | LOW |
| orchestration/SETUP.md | ant-farm-1y4 | LOW |
| agents/big-head.md | ant-farm-27x | LOW |
| agents/pantry-review.md | ant-farm-yb95 | LOW |
| scripts/scrub-pii.sh | ant-farm-7yv, ant-farm-cl8 | MED |
| orchestration/PLACEHOLDER_CONVENTIONS.md | ant-farm-32gz | LOW |

## Dependency Chains
- No explicit bd dependency chains exist. All 17 tasks are independent.
- However, semantic dependencies exist via shared files (see conflict clusters below).

**Conflict Clusters (shared-file groupings):**
1. **Pantry/orchestration mega-cluster**: ant-farm-bi3, ant-farm-yfnj, ant-farm-yb95, ant-farm-txw, ant-farm-auas, ant-farm-0gs, ant-farm-32gz all touch pantry.md and/or RULES.md and/or related template files. These 7 tasks form a dense conflict graph.
2. **Docs cluster**: ant-farm-033, ant-farm-1b8 (installation-guide.md)
3. **Hook scripts cluster**: ant-farm-7yv, ant-farm-z69 (install-hooks.sh), ant-farm-cl8 (scrub-pii.sh overlaps with 7yv)
4. **Independent tasks**: ant-farm-1e1, ant-farm-1y4, ant-farm-27x, ant-farm-9j6z, ant-farm-z3j

## Proposed Strategies

### Strategy A: Conflict-Batched Serial Waves (Recommended)
Batch high-conflict tasks into single agents to avoid merge conflicts. Use 2 waves to stay within the 7-agent limit.

**Wave 1** (7 agents):
- Agent 1 (general-purpose): ant-farm-bi3, ant-farm-yfnj, ant-farm-yb95, ant-farm-txw, ant-farm-auas -- Pantry/RULES mega-cluster. One agent handles all 5 tasks touching pantry.md, RULES.md, big-head-skeleton.md, reviews.md, checkpoints.md to avoid all conflicts.
- Agent 2 (general-purpose): ant-farm-0gs, ant-farm-32gz -- Both touch RULES.md (plus reviews.md and PLACEHOLDER_CONVENTIONS.md respectively). Batched to avoid RULES.md conflict with Agent 1.
- Agent 3 (technical-writer): ant-farm-033, ant-farm-1b8 -- Both touch installation-guide.md.
- Agent 4 (devops-engineer): ant-farm-7yv, ant-farm-z69, ant-farm-cl8 -- All touch scripts/ (install-hooks.sh and scrub-pii.sh). 7yv and cl8 share scrub-pii.sh.
- Agent 5 (technical-writer): ant-farm-1e1 -- Touches dirt-pusher-skeleton.md, big-head-skeleton.md, README.md. Note: big-head-skeleton.md overlaps with Agent 1, but 1e1 is a simple rename (different section) and Agent 1's changes are structural -- MEDIUM risk, manageable with rebase.
- Agent 6 (technical-writer): ant-farm-1y4 -- SETUP.md only, no conflicts.
- Agent 7 (general-purpose): ant-farm-27x, ant-farm-9j6z -- Small independent fixes (big-head.md tool list, review-clarify typo investigation).

**Wave 2**: ant-farm-z3j (prompt-engineer) -- checkpoints.md. Deferred because Agent 1 (auas) also touches checkpoints.md. Runs after Wave 1 completes to avoid conflict.

**Rationale**: The pantry.md/RULES.md mega-cluster is the dominant conflict. Batching those 5 tasks to one agent eliminates the highest-risk conflicts. The remaining RULES.md tasks (0gs, 32gz) go to a second agent that runs in parallel but only overlaps on RULES.md sections different from Agent 1. z3j is deferred to Wave 2 because checkpoints.md is shared with auas.
**Risk**: MEDIUM overall. Agent 1 has heavy workload (5 tasks) but they are all documentation/template edits. The big-head-skeleton.md overlap between Agents 1 and 5 is low-risk (different sections). Wave 2 is just 1 task.

### Strategy B: Maximum Parallelism with Rebase
Maximize parallel agents, accept merge conflict risk, use git pull --rebase between commits.

**Wave 1** (7 agents):
- Agent 1 (prompt-engineer): ant-farm-bi3, ant-farm-yfnj -- pantry.md Section 2 tasks (tightly coupled)
- Agent 2 (general-purpose): ant-farm-yb95 -- deprecation cleanup (pantry.md Section 2, RULES.md, pantry-review.md)
- Agent 3 (general-purpose): ant-farm-auas, ant-farm-txw -- validation guards + failure artifacts (overlap on pantry.md, big-head-skeleton.md, RULES.md)
- Agent 4 (general-purpose): ant-farm-0gs, ant-farm-32gz -- RULES.md + reviews.md tasks
- Agent 5 (technical-writer): ant-farm-033, ant-farm-1b8 -- installation-guide.md
- Agent 6 (devops-engineer): ant-farm-7yv, ant-farm-z69, ant-farm-cl8 -- scripts/
- Agent 7 (technical-writer): ant-farm-1e1, ant-farm-1y4, ant-farm-27x -- docs/rename tasks + SETUP.md + big-head.md

**Wave 2** (2 agents):
- Agent 8 (prompt-engineer): ant-farm-z3j -- checkpoints.md
- Agent 9 (general-purpose): ant-farm-9j6z -- typo investigation

**Rationale**: More parallelism in Wave 1, but Agents 1, 2, and 3 all touch pantry.md creating HIGH conflict risk. Rebase strategy required.
**Risk**: HIGH. Three agents touching pantry.md simultaneously will likely cause merge conflicts. RULES.md also has 3 agents (2, 3, 4). Not recommended.

### Strategy C: Two Equal Waves
Split tasks into two balanced waves of ~7, separating all file conflicts across waves.

**Wave 1** (7 agents):
- Agent 1 (prompt-engineer): ant-farm-bi3, ant-farm-yfnj -- pantry.md core fixes
- Agent 2 (technical-writer): ant-farm-033, ant-farm-1b8 -- installation-guide.md
- Agent 3 (devops-engineer): ant-farm-7yv, ant-farm-z69 -- install-hooks.sh
- Agent 4 (devops-engineer): ant-farm-cl8 -- scrub-pii.sh
- Agent 5 (technical-writer): ant-farm-1e1 -- data file rename
- Agent 6 (technical-writer): ant-farm-1y4 -- SETUP.md
- Agent 7 (general-purpose): ant-farm-27x, ant-farm-9j6z -- small independent fixes

**Wave 2** (5 agents):
- Agent 8 (general-purpose): ant-farm-yb95 -- deprecation cleanup (pantry.md, RULES.md, pantry-review.md)
- Agent 9 (general-purpose): ant-farm-auas -- validation guards (RULES.md, pantry.md, checkpoints.md, etc.)
- Agent 10 (prompt-engineer): ant-farm-txw -- failure artifacts (big-head-skeleton.md, pantry.md, reviews.md)
- Agent 11 (general-purpose): ant-farm-0gs, ant-farm-32gz -- RULES.md + reviews.md
- Agent 12 (prompt-engineer): ant-farm-z3j -- checkpoints.md

**Rationale**: Cleanly separates the pantry.md mega-cluster across waves. Wave 1 handles the core pantry fixes (bi3, yfnj); Wave 2 handles the structural cleanup (yb95, auas, txw) after Wave 1's changes are committed. Avoids all HIGH-risk overlaps.
**Risk**: MEDIUM. Wave 2 still has 3 agents touching pantry.md (yb95, auas, txw), but they touch different sections. reviews.md and RULES.md overlaps in Wave 2 are manageable with rebase. Slower total execution due to 2 full waves.

## Coverage Verification
- Inventory: 17 total tasks (17 ready + 0 blocked)
- Strategy A: 17 assigned across 2 waves -- PASS
- Strategy B: 17 assigned across 2 waves -- PASS
- Strategy C: 17 assigned across 2 waves -- PASS

## Metadata
- Epics: none (no tasks have epic parents)
- Task metadata files: .beads/agent-summaries/_session-cd9866/task-metadata/ (17 files)
- Session dir: .beads/agent-summaries/_session-cd9866

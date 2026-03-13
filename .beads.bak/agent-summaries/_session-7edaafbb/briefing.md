# Session Briefing

## Task Inventory
| ID | Epic | Title | Priority | Type | Agent | Files | Risk |
|----|------|-------|----------|------|-------|-------|------|
| ant-farm-40z | none | rsync --delete silently removes custom user files | P2 | bug | devops-engineer | sync-to-claude.sh | HIGH |
| ant-farm-a66 | none | SETUP.md references hardcoded path | P2 | bug | general-purpose | SETUP.md | MED |
| ant-farm-kwp | none | SETUP.md test checklist says Queen runs bd show | P2 | bug | general-purpose | SETUP.md | MED |
| ant-farm-lhq | none | Scout error metadata template lacks context fields | P2 | bug | general-purpose | scout.md | LOW |
| ant-farm-39zq | none | fill-review-slots.sh fill_slot spawns separate awk per slot | P3 | bug | devops-engineer | fill-review-slots.sh | HIGH |
| ant-farm-i2zd | none | fill-review-slots.sh temp files not cleaned up on abnormal exit | P3 | bug | devops-engineer | fill-review-slots.sh | HIGH |
| ant-farm-lc97 | none | fill-review-slots.sh resolve_arg accepts empty file content | P3 | bug | devops-engineer | fill-review-slots.sh | HIGH |
| ant-farm-ti6g | none | fill-review-slots.sh accepts review round 0 | P3 | bug | devops-engineer | fill-review-slots.sh | HIGH |
| ant-farm-w2i1 | none | Fragile comment-delimited conditionals and missing placeholder validation | P3 | bug | devops-engineer | fill-review-slots.sh, reviews.md | HIGH |
| ant-farm-o058 | none | compose-review-skeletons.sh extract_agent_section includes frontmatter | P3 | bug | devops-engineer | compose-review-skeletons.sh | MED |
| ant-farm-yn1r | none | compose-review-skeletons.sh sed regex too broad | P3 | bug | devops-engineer | compose-review-skeletons.sh | MED |
| ant-farm-npfx | none | parse-progress-log.sh hardening gaps | P3 | bug | devops-engineer | parse-progress-log.sh | LOW |
| ant-farm-9wk8 | none | Undocumented magic value ctc in scrub-pii.sh | P3 | bug | devops-engineer | scrub-pii.sh | HIGH |
| ant-farm-ns95 | none | scrub-pii.sh email regex limited coverage | P3 | bug | devops-engineer | scrub-pii.sh | HIGH |
| ant-farm-9vq | none | scrub-pii.sh grep pattern duplicated inline | P3 | bug | devops-engineer | scrub-pii.sh | HIGH |
| ant-farm-50m | none | scrub-pii.sh assumes perl installed | P3 | bug | devops-engineer | scrub-pii.sh | HIGH |
| ant-farm-wtp | none | scrub-pii.sh no re-stage in standalone mode | P3 | bug | devops-engineer | scrub-pii.sh | HIGH |
| ant-farm-a1rf | none | Bash scripting edge cases under set -euo pipefail | P3 | bug | devops-engineer | scrub-pii.sh, RULES.md, install-hooks.sh | HIGH |
| ant-farm-g29r | none | sync-to-claude.sh silently skips missing scripts | P3 | bug | devops-engineer | sync-to-claude.sh | HIGH |
| ant-farm-szcy | none | sync-to-claude.sh script selection has no comment | P3 | bug | devops-engineer | sync-to-claude.sh | HIGH |
| ant-farm-3r9 | none | sync-to-claude.sh backup timestamp collision risk | P3 | bug | devops-engineer | sync-to-claude.sh | HIGH |
| ant-farm-rja | none | sync-to-claude.sh agent glob fails silently | P3 | bug | devops-engineer | sync-to-claude.sh | HIGH |
| ant-farm-3mg | none | install-hooks.sh missing chmod for sync-to-claude.sh | P3 | bug | devops-engineer | install-hooks.sh | HIGH |
| ant-farm-4fx | none | install-hooks.sh backup uses fixed filename | P3 | bug | devops-engineer | install-hooks.sh | HIGH |
| ant-farm-4g7 | none | install-hooks.sh hook lacks descriptive error | P3 | bug | devops-engineer | install-hooks.sh | HIGH |
| ant-farm-dv9g | none | Pre-push hook sync failure non-fatal without comment | P3 | bug | devops-engineer | install-hooks.sh | HIGH |
| ant-farm-e1u6 | none | No tmux guard for dummy reviewer spawn | P3 | bug | devops-engineer | RULES.md | MED |
| ant-farm-qoig | none | RULES.md tmux dependency without availability check | P3 | bug | devops-engineer | RULES.md | MED |
| ant-farm-352c.1 | ant-farm-352c | Strengthen IF ROUND 1 markers to executable | P3 | bug | devops-engineer | reviews.md | MED |
| ant-farm-j6jq | none | Shell code blocks in reviews.md lack production quality | P3 | bug | devops-engineer | reviews.md | MED |

**Total**: 30 tasks | **Wave 1 (ready)**: 30 tasks | **Later waves (blocked)**: 0 tasks

## File Modification Matrix
| File | Tasks | Risk |
|------|-------|------|
| scripts/fill-review-slots.sh | ant-farm-39zq, ant-farm-i2zd, ant-farm-lc97, ant-farm-ti6g, ant-farm-w2i1 | HIGH |
| scripts/scrub-pii.sh | ant-farm-9wk8, ant-farm-ns95, ant-farm-9vq, ant-farm-50m, ant-farm-wtp, ant-farm-a1rf | HIGH |
| scripts/sync-to-claude.sh | ant-farm-40z, ant-farm-g29r, ant-farm-szcy, ant-farm-3r9, ant-farm-rja | HIGH |
| scripts/install-hooks.sh | ant-farm-3mg, ant-farm-4fx, ant-farm-4g7, ant-farm-dv9g, ant-farm-a1rf | HIGH |
| orchestration/templates/reviews.md | ant-farm-352c.1, ant-farm-w2i1, ant-farm-j6jq | MED |
| orchestration/RULES.md | ant-farm-e1u6, ant-farm-qoig, ant-farm-a1rf | MED |
| scripts/compose-review-skeletons.sh | ant-farm-o058, ant-farm-yn1r | MED |
| SETUP.md | ant-farm-a66, ant-farm-kwp | MED |
| scripts/parse-progress-log.sh | ant-farm-npfx | LOW |
| orchestration/templates/scout.md | ant-farm-lhq | LOW |

## Dependency Chains
- No explicit bd dependency chains exist. All 30 tasks are unblocked.
- ant-farm-a1rf is a cross-cutting task touching scrub-pii.sh, install-hooks.sh, and RULES.md. It MUST run in a separate wave from all single-file agents on those files.
- ant-farm-w2i1 is a cross-cutting task touching fill-review-slots.sh and reviews.md. It MUST run in a separate wave from single-file agents on those files.

## Proposed Strategies

### Strategy A: File-Grouped 2-Wave with Cross-Cut Isolation (Recommended)
Wave 1 handles all single-file tasks (no overlaps possible). Wave 2 handles both cross-cutting tasks plus the remaining reviews.md-only tasks (grouped with w2i1 to avoid a third wave).

**Wave 1** (7 agents):
1. **fill-review-slots.sh agent** (devops-engineer): ant-farm-39zq, ant-farm-i2zd, ant-farm-lc97, ant-farm-ti6g (4 tasks)
2. **scrub-pii.sh agent** (devops-engineer): ant-farm-9wk8, ant-farm-ns95, ant-farm-9vq, ant-farm-50m, ant-farm-wtp (5 tasks)
3. **sync-to-claude.sh agent** (devops-engineer): ant-farm-40z, ant-farm-g29r, ant-farm-szcy, ant-farm-3r9, ant-farm-rja (5 tasks)
4. **install-hooks.sh agent** (devops-engineer): ant-farm-3mg, ant-farm-4fx, ant-farm-4g7, ant-farm-dv9g (4 tasks)
5. **compose-review-skeletons.sh + parse-progress-log.sh agent** (devops-engineer): ant-farm-o058, ant-farm-yn1r, ant-farm-npfx (3 tasks)
6. **RULES.md agent** (devops-engineer): ant-farm-e1u6, ant-farm-qoig (2 tasks)
7. **docs agent** (general-purpose): ant-farm-a66, ant-farm-kwp, ant-farm-lhq (3 tasks -- SETUP.md x2, scout.md x1)

**Wave 2** (2 agents, after Wave 1 completes):
1. **reviews.md + fill-review-slots.sh cross-cut agent** (devops-engineer): ant-farm-352c.1, ant-farm-w2i1, ant-farm-j6jq (3 tasks -- w2i1 touches fill-review-slots.sh and reviews.md; 352c.1 and j6jq are reviews.md-only; all batched to one agent since they share reviews.md)
2. **a1rf cross-cut agent** (devops-engineer): ant-farm-a1rf (1 task -- touches scrub-pii.sh, install-hooks.sh, RULES.md; all three files are now stable from Wave 1)

**File overlap verification (Wave 1)**: Each file appears in exactly one agent assignment. fill-review-slots.sh in agent 1 only. scrub-pii.sh in agent 2 only. sync-to-claude.sh in agent 3 only. install-hooks.sh in agent 4 only. compose-review-skeletons.sh and parse-progress-log.sh in agent 5 only. RULES.md in agent 6 only. SETUP.md and scout.md in agent 7 only. Zero overlaps.

**File overlap verification (Wave 2)**: Agent 1 touches reviews.md and fill-review-slots.sh. Agent 2 touches scrub-pii.sh, install-hooks.sh, RULES.md. No shared files between Wave 2 agents. Zero overlaps.

**Dependency gate**: Wave 2 starts only after all Wave 1 agents complete. This ensures w2i1 sees stable fill-review-slots.sh (from Wave 1 agent 1) and a1rf sees stable scrub-pii.sh (agent 2), install-hooks.sh (agent 4), and RULES.md (agent 6).

**Rationale**: Recommended because Wave 1 processes 26 of 30 tasks in full parallel with zero conflict risk. Wave 2 is small (4 tasks, 2 agents) and fast. Total elapsed time is only marginally longer than a single wave, but conflict risk is zero.

**Risk**: LOW. Zero file overlaps in both waves. No merge conflicts possible.

### Strategy B: Strict 2-Wave with Maximum Isolation
Same as Strategy A but splits Wave 2 further so each cross-cutting task gets its own agent, and reviews.md-only tasks are also isolated.

**Wave 1** (7 agents):
1. **fill-review-slots.sh agent** (devops-engineer): ant-farm-39zq, ant-farm-i2zd, ant-farm-lc97, ant-farm-ti6g (4 tasks)
2. **scrub-pii.sh agent** (devops-engineer): ant-farm-9wk8, ant-farm-ns95, ant-farm-9vq, ant-farm-50m, ant-farm-wtp (5 tasks)
3. **sync-to-claude.sh agent** (devops-engineer): ant-farm-40z, ant-farm-g29r, ant-farm-szcy, ant-farm-3r9, ant-farm-rja (5 tasks)
4. **install-hooks.sh agent** (devops-engineer): ant-farm-3mg, ant-farm-4fx, ant-farm-4g7, ant-farm-dv9g (4 tasks)
5. **compose-review-skeletons.sh + parse-progress-log.sh agent** (devops-engineer): ant-farm-o058, ant-farm-yn1r, ant-farm-npfx (3 tasks)
6. **RULES.md agent** (devops-engineer): ant-farm-e1u6, ant-farm-qoig (2 tasks)
7. **docs agent** (general-purpose): ant-farm-a66, ant-farm-kwp, ant-farm-lhq (3 tasks -- SETUP.md x2, scout.md x1)

**Wave 2** (3 agents, after Wave 1 completes):
1. **reviews.md-only agent** (devops-engineer): ant-farm-352c.1, ant-farm-j6jq (2 tasks -- reviews.md only)
2. **w2i1 cross-cut agent** (devops-engineer): ant-farm-w2i1 (1 task -- touches fill-review-slots.sh and reviews.md)
3. **a1rf cross-cut agent** (devops-engineer): ant-farm-a1rf (1 task -- touches scrub-pii.sh, install-hooks.sh, RULES.md)

**IMPORTANT**: Wave 2 agents 1 and 2 BOTH touch reviews.md. This is an overlap. To fix: merge them into one agent.

**Corrected Wave 2** (2 agents, after Wave 1 completes):
1. **reviews.md + fill-review-slots.sh agent** (devops-engineer): ant-farm-352c.1, ant-farm-w2i1, ant-farm-j6jq (3 tasks)
2. **a1rf cross-cut agent** (devops-engineer): ant-farm-a1rf (1 task)

**Note**: After correction, this is identical to Strategy A. Including it to demonstrate that further splitting Wave 2 is not possible without introducing file overlaps. Strategy A's grouping is the minimum-conflict configuration.

**Risk**: LOW. Identical to Strategy A after correction.

### Strategy C: Priority-First 3-Wave
P2 tasks land first in Wave 1, P3 single-file tasks in Wave 2, cross-cutting P3 tasks in Wave 3.

**Wave 1** (3 agents -- P2 only):
1. **sync-to-claude.sh P2 agent** (devops-engineer): ant-farm-40z (1 task)
2. **SETUP.md agent** (general-purpose): ant-farm-a66, ant-farm-kwp (2 tasks)
3. **scout.md agent** (general-purpose): ant-farm-lhq (1 task)

**Wave 2** (7 agents -- P3 single-file only, after Wave 1 completes):
1. **fill-review-slots.sh agent** (devops-engineer): ant-farm-39zq, ant-farm-i2zd, ant-farm-lc97, ant-farm-ti6g (4 tasks)
2. **scrub-pii.sh agent** (devops-engineer): ant-farm-9wk8, ant-farm-ns95, ant-farm-9vq, ant-farm-50m, ant-farm-wtp (5 tasks)
3. **sync-to-claude.sh P3 agent** (devops-engineer): ant-farm-g29r, ant-farm-szcy, ant-farm-3r9, ant-farm-rja (4 tasks)
4. **install-hooks.sh agent** (devops-engineer): ant-farm-3mg, ant-farm-4fx, ant-farm-4g7, ant-farm-dv9g (4 tasks)
5. **compose-review-skeletons.sh + parse-progress-log.sh agent** (devops-engineer): ant-farm-o058, ant-farm-yn1r, ant-farm-npfx (3 tasks)
6. **RULES.md agent** (devops-engineer): ant-farm-e1u6, ant-farm-qoig (2 tasks)
7. **reviews.md-only agent** (devops-engineer): ant-farm-352c.1, ant-farm-j6jq (2 tasks)

**Wave 3** (2 agents, after Wave 2 completes):
1. **w2i1 + reviews.md cross-cut agent** (devops-engineer): ant-farm-w2i1 (1 task -- touches fill-review-slots.sh and reviews.md, both stable from Wave 2)
2. **a1rf cross-cut agent** (devops-engineer): ant-farm-a1rf (1 task -- touches scrub-pii.sh, install-hooks.sh, RULES.md, all stable from Wave 2)

**File overlap verification (Wave 1)**: sync-to-claude.sh, SETUP.md, scout.md -- all unique per agent. Zero overlaps.
**File overlap verification (Wave 2)**: fill-review-slots.sh, scrub-pii.sh, sync-to-claude.sh, install-hooks.sh, compose-review-skeletons.sh, parse-progress-log.sh, RULES.md, reviews.md -- all unique per agent. Zero overlaps.
**File overlap verification (Wave 3)**: Agent 1 touches fill-review-slots.sh + reviews.md. Agent 2 touches scrub-pii.sh + install-hooks.sh + RULES.md. No shared files. Zero overlaps.

**Rationale**: P2 tasks committed earliest. Zero conflicts across all waves. But 3 waves with underutilized Wave 1 (3 agents) significantly increases total elapsed time.

**Risk**: LOW. Zero file overlaps in all three waves. No merge conflicts possible.

## Coverage Verification
- Inventory: 30 total tasks (30 ready + 0 blocked)
- Strategy A: 30 assigned across 2 waves (26 Wave 1 + 4 Wave 2) -- PASS
- Strategy B: 30 assigned across 2 waves (26 Wave 1 + 4 Wave 2) -- PASS (identical to A after correction)
- Strategy C: 30 assigned across 3 waves (4 Wave 1 + 24 Wave 2 + 2 Wave 3) -- PASS

## Metadata
- Epics: ant-farm-352c (1 task: ant-farm-352c.1), none (29 tasks)
- Task metadata files: .beads/agent-summaries/_session-7edaafbb/task-metadata/ (30 files)
- Session dir: .beads/agent-summaries/_session-7edaafbb

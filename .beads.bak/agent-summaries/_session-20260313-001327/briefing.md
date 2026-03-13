# Session Briefing (Fix Cycle)

## Task Inventory
| ID | Epic | Title | Priority | Type | Agent | Files | Risk |
|----|------|-------|----------|------|-------|-------|------|
| ant-farm-ru51 | none | cmd_list filters and _auto_close miss dual-storage fields | P2 | bug | python-pro | crumb.py:425-430,520,523 | MED |
| ant-farm-bzhs | none | _convert_beads_record inverts blocks dependency direction | P2 | bug | python-pro | crumb.py:1483-1484 | MED |
| ant-farm-35a5 | none | Missing try/except OSError on file open/touch ops | P2 | bug | python-pro | crumb.py:181,222,258-260 | LOW |
| ant-farm-l1en | none | Missing type validation on --from-json and int() conversions | P2 | bug | python-pro | crumb.py:645-649,679,1148,1433,1646-1647 | MED |
| ant-farm-ch0z | none | TOCTOU race in cmd_doctor --fix: read without FileLock | P2 | bug | python-pro | crumb.py:1714-1816 | LOW |

**Total**: 5 tasks | **Wave 1 (ready)**: 5 tasks | **Later waves (blocked)**: 0 tasks

## File Modification Matrix
| File | Tasks | Line Ranges | Risk |
|------|-------|-------------|------|
| crumb.py | ALL 5 tasks | See below | HIGH (5 tasks, 1 file) |

**Detailed line ranges (no direct overlaps, but same-function proximity):**
- L181, L222, L258-260: 35a5 (utility functions at top of file)
- L425-430, L520, L523: ru51 (cmd_list + auto-close mid-file)
- L645-649, L679: l1en (cmd_create)
- L1148: l1en (cmd_trail_create)
- L1433: l1en (import ID assignment in _convert_beads_record)
- L1483-1484: bzhs (dependency processing in _convert_beads_record) -- 50 lines from l1en's L1433
- L1646-1647: l1en (post-import counter update)
- L1714-1816: ch0z (cmd_doctor restructure)

**Key overlap**: l1en (L1433) and bzhs (L1483-1484) both modify `_convert_beads_record`. Different sections (~50 lines apart), but merge conflicts are possible if line shifts occur.

## Dependency Chains
- No explicit `bd` dependencies between these 5 tasks
- Implicit ordering concern: l1en and bzhs both touch `_convert_beads_record` function

## Proposed Strategies

### Strategy A: Serial Single-Agent (Recommended)
**Wave 1** (1 agent): ant-farm-35a5, ant-farm-ru51, ant-farm-l1en, ant-farm-bzhs, ant-farm-ch0z (all python-pro)
**Rationale**: All 5 tasks modify the same file. A single agent eliminates all merge conflict risk. The fixes are small and targeted (adding try/except wrappers, dual-lookup patterns, isinstance checks, reordering lock scope). A single competent agent can execute all 5 in sequence faster than coordinating merges across agents. This is the safest approach for a fix cycle where all bugs are in one file. Recommended fix order: 35a5 first (top of file, utility functions), ru51 second (mid-file), l1en third (scattered but includes _convert_beads_record L1433), bzhs fourth (same function, L1483 -- immediately after l1en's nearby edit), ch0z last (bottom of file, largest restructure).
**Risk**: LOW (no merge conflicts possible)

### Strategy B: Two-Agent Split (Upper/Lower File Halves)
**Wave 1** (2 agents):
- Agent 1 (python-pro): ant-farm-35a5 (L181-260), ant-farm-ru51 (L425-523) -- upper half of crumb.py
- Agent 2 (python-pro): ant-farm-l1en (L645-1647), ant-farm-bzhs (L1483-1484), ant-farm-ch0z (L1714-1816) -- lower half

**Rationale**: Splits file roughly in half. Agent 1 touches L181-523, Agent 2 touches L645-1816. No line range overlap between agents. The l1en+bzhs proximity risk is contained within a single agent.
**Risk**: MEDIUM (same file, but non-overlapping regions >100 lines apart; git rebase should handle cleanly, but line shifts from Agent 1's edits could cause merge noise in Agent 2's ranges)

### Strategy C: Maximum Parallel (5 Agents)
**Wave 1** (5 agents): one agent per task, all python-pro
**Rationale**: Maximum speed. Each fix is small and localized.
**Risk**: HIGH (5 agents on same file; even though line ranges don't overlap, the rebase/merge overhead and risk of line-shift conflicts makes this fragile for a fix cycle. Known failure mode from Epic 74g.)

## Coverage Verification
- Inventory: 5 total tasks (5 ready + 0 blocked)
- Strategy A: 5 assigned across 1 wave -- PASS
- Strategy B: 5 assigned across 1 wave -- PASS
- Strategy C: 5 assigned across 1 wave -- PASS

## Metadata
- Epics: none
- Task metadata files: .beads/agent-summaries/_session-20260313-001327/task-metadata/ (5 files)
- Session dir: .beads/agent-summaries/_session-20260313-001327

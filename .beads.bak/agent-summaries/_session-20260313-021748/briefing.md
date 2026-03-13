# Session Briefing

## Fix Cycle — Big Head Review Findings

## Task Inventory
| ID | Epic | Title | Priority | Type | Agent | Files | Risk |
|----|------|-------|----------|------|-------|-------|------|
| ant-farm-gvvk | none | Dual-lookup missing in cmd_list and _auto_close | P1 | bug | python-pro | crumb.py:425-430,520,523 | HIGH |
| ant-farm-i9nt | none | Inverted blocks dependency in _convert_beads_record | P1 | bug | python-pro | crumb.py:1483-1484 | HIGH |
| ant-farm-7bn5 | none | Input type validation — json.loads and int() guards | P1 | bug | python-pro | crumb.py:645-649,679,1148,1433,1646-1647 | HIGH |
| ant-farm-z43j | none | cmd_doctor FileLock race — read outside lock scope | P1 | bug | python-pro | crumb.py:1714,1816 | HIGH |
| ant-farm-m7hn | none | Missing OSError handling in open()/touch() calls | P2 | bug | python-pro | crumb.py:181,222,258-260 | HIGH |
| ant-farm-v45n | none | Config schema mismatch — counters vs next_crumb_id | P2 | bug | general-purpose | skills/init.md:107-115 | LOW |
| ant-farm-prjj | none | Contradictory follow-exactly-except in work.md | P2 | bug | general-purpose | skills/work.md:115-128 | MED |
| ant-farm-jc98 | none | Missing config.json check in work.md init guard | P2 | bug | general-purpose | skills/work.md:24-26 | MED |
| ant-farm-li6e | none | Shell robustness gaps in setup.sh | P2 | bug | general-purpose | scripts/setup.sh:67,100,149 | LOW |
| ant-farm-3iye | none | Heredoc/JSON injection in plan.md | P2 | bug | general-purpose | skills/plan.md:119-145 | LOW |
| ant-farm-bcv4 | none | Silent failures — placeholder guard + line cap | P2 | bug | general-purpose | orchestration/RULES-decompose.md:127,250 | LOW |
| ant-farm-k1z2 | none | Empty feature request validation in surveyor.md | P2 | bug | general-purpose | orchestration/templates/surveyor.md:367-375 | LOW |

**Total**: 12 tasks | **Wave 1 (ready)**: 12 tasks | **Later waves (blocked)**: 0 tasks

## File Modification Matrix
| File | Tasks | Risk |
|------|-------|------|
| crumb.py | ant-farm-gvvk (L425-530), ant-farm-i9nt (L1483-1484), ant-farm-7bn5 (L645-679+L1148,1433,1646), ant-farm-z43j (L1714-1816), ant-farm-m7hn (L181-260) | HIGH (5 tasks, non-overlapping sections) |
| skills/work.md | ant-farm-prjj (L115-128), ant-farm-jc98 (L24-26) | MED (2 tasks, different sections) |
| skills/init.md | ant-farm-v45n (L107-115) | LOW (1 task) |
| skills/plan.md | ant-farm-3iye (L119-145) | LOW (1 task) |
| scripts/setup.sh | ant-farm-li6e (L67,100,149) | LOW (1 task) |
| orchestration/RULES-decompose.md | ant-farm-bcv4 (L127,250) | LOW (1 task) |
| orchestration/templates/surveyor.md | ant-farm-k1z2 (L367-375) | LOW (1 task) |

## crumb.py Section Analysis

The 5 crumb.py tasks touch well-separated regions:
- **ant-farm-m7hn**: L181-260 (read_tasks, iter_jsonl, FileLock -- early utility functions)
- **ant-farm-gvvk**: L425-530 (_auto_close_trail, cmd_list filters -- mid-file)
- **ant-farm-7bn5**: L645-679 + L1148,1433,1646 (cmd_create validation + scattered int() guards)
- **ant-farm-i9nt**: L1483-1484 (_convert_beads_record -- import section)
- **ant-farm-z43j**: L1714-1816 (cmd_doctor lock restructure -- late file)

The sections are non-overlapping but ant-farm-7bn5 has scattered edits spanning the full file. If parallel agents add/remove lines, 7bn5's later edits (L1148, L1433, L1646) could conflict with i9nt (L1483) and z43j (L1714) due to line-number drift.

## Dependency Chains
- No explicit dependency chains among these 12 tasks.
- Implicit file-level coupling: 5 tasks on crumb.py, 2 tasks on skills/work.md.

## Proposed Strategies

### Strategy A: Batch crumb.py to One Agent, Parallel the Rest (Recommended)
**Wave 1** (7 agents):
- Agent 1 (python-pro): ant-farm-gvvk, ant-farm-i9nt, ant-farm-7bn5, ant-farm-z43j, ant-farm-m7hn -- all 5 crumb.py tasks batched
- Agent 2 (general-purpose): ant-farm-prjj, ant-farm-jc98 -- both skills/work.md tasks batched
- Agent 3 (general-purpose): ant-farm-v45n -- skills/init.md
- Agent 4 (general-purpose): ant-farm-li6e -- scripts/setup.sh
- Agent 5 (general-purpose): ant-farm-3iye -- skills/plan.md
- Agent 6 (general-purpose): ant-farm-bcv4 -- orchestration/RULES-decompose.md
- Agent 7 (general-purpose): ant-farm-k1z2 -- orchestration/templates/surveyor.md

**Rationale**: Batching all crumb.py tasks to one python-pro agent eliminates the HIGH merge conflict risk entirely. The 5 tasks touch non-overlapping sections so one agent can handle them sequentially. The work.md pair is batched for the same reason. All remaining tasks touch independent files. This completes everything in a single wave with zero conflict risk.
**Risk**: LOW. The crumb.py agent has the heaviest load (5 tasks) but edits are localized to separate sections. No merge conflicts possible.

### Strategy B: Split crumb.py Early/Late, Parallel with Rebase
**Wave 1** (7 agents):
- Agent 1 (python-pro): ant-farm-m7hn, ant-farm-gvvk -- early crumb.py (L181-530)
- Agent 2 (python-pro): ant-farm-i9nt, ant-farm-z43j, ant-farm-7bn5 -- mid-to-late crumb.py (L645+)
- Agent 3 (general-purpose): ant-farm-prjj, ant-farm-jc98 -- skills/work.md
- Agent 4 (general-purpose): ant-farm-v45n -- skills/init.md
- Agent 5 (general-purpose): ant-farm-li6e -- scripts/setup.sh
- Agent 6 (general-purpose): ant-farm-3iye -- skills/plan.md
- Agent 7 (general-purpose): ant-farm-bcv4, ant-farm-k1z2 -- orchestration docs batched

**Rationale**: Splits crumb.py workload for faster execution. Agent 1 handles early-file edits (L181-530), Agent 2 handles L645+. Requires git pull --rebase between commits.
**Risk**: MEDIUM. ant-farm-7bn5 has scattered edits spanning L645-1646. If Agent 1 adds/removes lines, Agent 2's later edits may shift. Rebase should resolve automatically but manual intervention possible.

### Strategy C: Priority-First Waves
**Wave 1** (4 agents -- P1 crumb.py + independent P2s):
- Agent 1 (python-pro): ant-farm-gvvk, ant-farm-i9nt, ant-farm-7bn5, ant-farm-z43j -- P1 crumb.py batch
- Agent 2 (general-purpose): ant-farm-v45n -- skills/init.md
- Agent 3 (general-purpose): ant-farm-li6e -- scripts/setup.sh
- Agent 4 (general-purpose): ant-farm-3iye -- skills/plan.md

**Wave 2** (4 agents -- remaining P2s):
- Agent 1 (python-pro): ant-farm-m7hn -- crumb.py P2 (safe after P1 batch committed)
- Agent 2 (general-purpose): ant-farm-prjj, ant-farm-jc98 -- skills/work.md
- Agent 3 (general-purpose): ant-farm-bcv4 -- orchestration/RULES-decompose.md
- Agent 4 (general-purpose): ant-farm-k1z2 -- orchestration/templates/surveyor.md

**Rationale**: Prioritizes P1 fixes. Wave 2 P2 tasks run after P1 crumb.py changes are committed, eliminating conflict for the remaining P2 crumb.py task. Independent P2 tasks start in Wave 1 since they have no file overlap.
**Risk**: LOW but slower. Two waves add latency without reducing real risk since P2 tasks touch different sections anyway.

## Coverage Verification
- Inventory: 12 total tasks (12 ready + 0 blocked)
- Strategy A: 12 assigned across 1 wave -- PASS
- Strategy B: 12 assigned across 1 wave -- PASS
- Strategy C: 12 assigned across 2 waves -- PASS

## Metadata
- Epics: none
- Task metadata files: .beads/agent-summaries/_session-20260313-021748/task-metadata/ (12 files)
- Session dir: .beads/agent-summaries/_session-20260313-021748

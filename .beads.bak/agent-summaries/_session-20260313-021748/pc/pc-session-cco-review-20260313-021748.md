# CCO Verification Report (Nitpicker Pre-Spawn Audit)

**Timestamp**: 20260313-021748
**Review round**: 1
**Session**: _session-20260313-021748

## Summary

FAIL - Critical scope mismatch detected between git diff and review prompt file lists.

The review prompts specify 15 files (matching the 11-task Pantry session plan), but the commit range `0ec9ed2^..HEAD` includes 37 files from 24 commits (11 scheduled + 13 unscheduled support/doc tasks).

## Detailed Findings

### Check 1: File List Matches Git Diff

**Status**: FAIL

**Evidence**:
- Commit range: `0ec9ed2^..HEAD`
- Files listed in review prompts: 15 files
- Files actually changed in git diff: 37 files
- Task mismatch: 11 scheduled tasks + 13 unscheduled support/doc tasks
- File mismatch: 15 expected files + 22 undocumented files

### Breakdown: Scheduled vs Unscheduled Tasks

**11 Scheduled tasks (in Pantry session plan):**
```
ant-farm-399a (Surveyor)        → agents/surveyor.md, orchestration/templates/surveyor.md, orchestration/templates/surveyor-skeleton.md
ant-farm-y4hl (Forager)         → agents/forager.md, orchestration/templates/forager.md, orchestration/templates/forager-skeleton.md
ant-farm-2hx8 (/work skill)     → skills/work.md
ant-farm-3bz5 (setup.sh)        → scripts/setup.sh
ant-farm-3imu (/init skill)     → skills/init.md
ant-farm-a5lq (/plan skill)     → skills/plan.md
ant-farm-n3qr (/status skill)   → skills/status.md
ant-farm-xtu9 (Architect)       → agents/architect.md, orchestration/templates/decomposition.md, orchestration/templates/architect-skeleton.md
ant-farm-hlv6 (decomposition)   → orchestration/templates/decomposition.md
ant-farm-rwsk (RULES-decompose) → orchestration/RULES-decompose.md
ant-farm-3mdg (Planner)         → orchestration/RULES-decompose.md
```
**Result**: 15 files (matches review prompt list)

**13 Unscheduled support/doc tasks (NOT in Pantry plan, but committed):**
```
ant-farm-6d3f   → scripts/build-review-prompts.sh (migrate bd→crumb in build script)
ant-farm-6gg6   → orchestration/templates/scout.md, orchestration/templates/implementation.md (migrate bd→crumb)
ant-farm-a50b   → orchestration/templates/big-head-skeleton.md (migrate bd→crumb)
ant-farm-ax38   → CLAUDE.md (migrate bd→crumb)
ant-farm-eifm   → orchestration/templates/queen-state.md, orchestration/templates/SESSION_PLAN_TEMPLATE.md (migrate bd→crumb)
ant-farm-epmv   → orchestration/templates/pantry.md (migrate bd→crumb)
ant-farm-gvd4   → orchestration/templates/dirt-pusher-skeleton.md, orchestration/templates/nitpicker-skeleton.md, orchestration/templates/scribe-skeleton.md (migrate bd→crumb)
ant-farm-h2gu   → orchestration/templates/checkpoints.md (migrate bd→crumb)
ant-farm-k03k   → orchestration/reference/dependency-analysis.md, orchestration/SETUP.md (migrate bd→crumb)
ant-farm-mmo3   → agents/nitpicker.md, agents/scout-organizer.md (replace bd references)
ant-farm-n56q   → orchestration/templates/reviews.md (migrate bd→crumb)
ant-farm-o0wu   → orchestration/RULES-review.md (migrate bd→crumb)
ant-farm-vjhe   → AGENTS.md, CONTRIBUTING.md, README.md, docs/installation-guide.md (migrate bd→crumb)
```
**Result**: 22 additional files (NOT in review prompt list)

### Files Specified in Review Prompts (15 total)

```
agents/architect.md
agents/forager.md
agents/surveyor.md
orchestration/RULES-decompose.md
orchestration/templates/architect-skeleton.md
orchestration/templates/decomposition.md
orchestration/templates/forager-skeleton.md
orchestration/templates/forager.md
orchestration/templates/surveyor-skeleton.md
orchestration/templates/surveyor.md
scripts/setup.sh
skills/init.md
skills/plan.md
skills/status.md
skills/work.md
```

### Files Changed in Git Diff but MISSING from Review Scope (22 total)

**Project documentation (5):**
- AGENTS.md
- CLAUDE.md
- CONTRIBUTING.md
- README.md
- docs/installation-guide.md

**Orchestration reference (1):**
- orchestration/reference/dependency-analysis.md

**Orchestration config & setup (2):**
- orchestration/RULES-review.md
- orchestration/SETUP.md

**Orchestration templates (10):**
- orchestration/templates/SESSION_PLAN_TEMPLATE.md
- orchestration/templates/big-head-skeleton.md
- orchestration/templates/checkpoints.md
- orchestration/templates/dirt-pusher-skeleton.md
- orchestration/templates/implementation.md
- orchestration/templates/nitpicker-skeleton.md
- orchestration/templates/pantry.md
- orchestration/templates/queen-state.md
- orchestration/templates/reviews.md
- orchestration/templates/scout.md
- orchestration/templates/scribe-skeleton.md

**Agent definitions (2):**
- agents/nitpicker.md
- agents/scout-organizer.md

**Support scripts (1):**
- scripts/build-review-prompts.sh

### Impact Assessment

**Scope gap**: 59% of changed files excluded from review

**Critical files not reviewed:**
- orchestration/templates/checkpoints.md — Core verification checkpoint definitions
- orchestration/templates/pantry.md — Prompt composition orchestrator
- orchestration/templates/reviews.md — Review execution framework
- orchestration/templates/big-head-skeleton.md — Consolidation orchestrator
- agents/nitpicker.md — New agent definition
- agents/scout-organizer.md — New agent definition
- orchestration/RULES-review.md — Review workflow rules
- build-review-prompts.sh — Script that generated these review prompts

**Implications**:
- Clarity review will NOT examine major orchestration templates and new agent definitions
- Edge Cases review will NOT examine defensive code in skeleton templates or reference docs
- Correctness review will NOT verify acceptance criteria for 13 unscheduled support tasks
- Drift review will NOT catch cross-file inconsistencies in orchestration framework

### Check 2: Same File List Across All Prompts

**Status**: PASS

All 4 review prompts (clarity, edge-cases, correctness, drift) contain identical file lists (15 files each).

### Check 3: Same Commit Range Across All Prompts

**Status**: PASS

All 4 review prompts specify `0ec9ed2^..HEAD`.

### Check 4: Correct Focus Areas

**Status**: PASS

Each prompt has domain-appropriate focus areas (not copy-pasted).

### Check 5: No Bead Filing Instruction

**Status**: PASS

All 4 prompts contain "Do NOT file crumbs (`crumb create`) — Big Head handles all crumb filing."

### Check 6: Report Format Reference

**Status**: PASS

All 4 prompts specify correct output paths with consistent timestamp `20260313-032735`.

### Check 7: Messaging Guidelines

**Status**: PASS

All 4 prompts include cross-review messaging protocol with examples.

## Verdict

**FAIL**

**Failing checks**:
1. Check 1 (File list matches git diff): **FAIL** — 22 changed files not included in review scope (59% of actual changes from 13 unscheduled tasks)

**Passing checks**: 2, 3, 4, 5, 6, 7

## Root Cause Analysis

**Primary cause**: Pantry composed review prompts for the 11 scheduled primary tasks only, generating a file list of 15 files. However, the commit range `0ec9ed2^..HEAD` includes 13 additional support/documentation tasks (migrating bd→crumb CLI references) that were committed in the same branch but were NOT scheduled in the Pantry session plan.

**Secondary issue**: These 13 support tasks modified critical orchestration infrastructure (checkpoints.md, pantry.md, reviews.md, big-head-skeleton.md, etc.) and new agent definitions (nitpicker.md, scout-organizer.md). They should be reviewed but are not included in the current briefs.

**Question for Queen**:
- Were these 13 support tasks intentionally deferred from the Pantry plan and committed separately by a different agent/process?
- Or are they unintended scope creep that should have been captured in the initial task decomposition?

## Recommendation

**Before spawning Nitpickers, the Queen must resolve the scope mismatch:**

**Option A: Narrow review scope (if support tasks are out of scope for this review cycle)**
- Rewrite the commit range to be `0ec9ed2^..{commit-before-first-support-task}`
- Verify this matches the 11 scheduled tasks
- This excludes the 13 support tasks and their 22 file changes
- Pro: Matches original Pantry plan; Con: Support tasks go unreviewed in this round

**Option B: Expand review scope (if support tasks should be reviewed now)**
- Re-run Pantry with expanded task list including the 13 support tasks
- Generate new review prompts with complete file list (37 files, 24 tasks)
- Deploy new prompts to Nitpickers before spawn
- Pro: Comprehensive review of all changes; Con: Requires Pantry re-run

**Option C: Run two review cycles (if support tasks are from a separate initiative)**
- Spawn Nitpickers now with 15-file scope for the 11 primary tasks
- File a separate review cycle for the 13 support tasks afterward
- Pro: Clear separation of concerns; Con: Fragmented review and double work

Do NOT spawn Nitpickers until the Queen chooses an option and updates the commit range or file list accordingly.

## Evidence

**Review prompt files audited:**
- /Users/correy/projects/ant-farm/.beads/agent-summaries/_session-20260313-021748/prompts/review-clarity.md
- /Users/correy/projects/ant-farm/.beads/agent-summaries/_session-20260313-021748/prompts/review-edge-cases.md
- /Users/correy/projects/ant-farm/.beads/agent-summaries/_session-20260313-021748/prompts/review-correctness.md
- /Users/correy/projects/ant-farm/.beads/agent-summaries/_session-20260313-021748/prompts/review-drift.md

**Session context:**
- /Users/correy/projects/ant-farm/.beads/agent-summaries/_session-20260313-021748/session-summary.md

**Git verification:**
- Commit range: 0ec9ed2^..HEAD (24 commits, 37 files)
- Session plan: 11 tasks, 15 files

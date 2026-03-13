# Summary: ant-farm-ygmj.4 — Update RULES.md for persistent team and fix inner loop

**Commit**: 9fcfc87
**Task**: refactor: update RULES.md for persistent team and fix inner loop (ant-farm-ygmj.4)

## 1. Approaches Considered

### Approach A: Surgical Line-Number Targeting
Replace only the exact byte ranges given in the task brief (L157-305, L416-435, L533-548). Use the known line offsets to target edits precisely. Advantage: minimal; Risk: line numbers can shift if predecessor commits changed the file — edits would land in the wrong context.

### Approach B: Content-Anchored Find-and-Replace (Selected)
Use prose anchors — the section headers (`**Step 3b:**`, `## Model Assignments`, `## Retry Limits`) plus the full current block text — as the old_string in Edit calls. This is robust to minor line drift. Three independent Edit operations, one per scope region. Selected because it combines precision with robustness.

### Approach C: Full-File Rewrite
Read the file, produce a complete rewritten version in a Write call. Advantage: allows holistic consistency review while authoring. Disadvantage: violates the task's "only edit listed sections" scope constraint; introduces high risk of accidentally changing unscoped sections; large diff makes review harder.

### Approach D: Inline Incremental Patch
Make many small targeted Edit calls, one per logical change (e.g., separate edits for team persistence paragraph, naming conventions, each new progress log entry). Advantage: each edit is a minimal diff. Disadvantage: higher number of round-trips, and small edits interleaved in a large block risk mis-targeting if surrounding context is ambiguous.

## 2. Selected Approach with Rationale

Approach B (Content-Anchored Find-and-Replace with Three Edit Calls) was selected.

Rationale:
- Three scoped regions map cleanly to three Edit calls: (1) Steps 3b+3c together since they form a cohesive unit, (2) Model Assignments table, (3) Retry Limits table.
- Using full block text as old_string guarantees exact matching regardless of line-number drift from predecessor commits.
- Keeps the diff bounded and reviewable: each Edit touches only one logical section.
- Does not require re-writing the entire file, preserving the task's "only edit listed sections" scope constraint.

## 3. Implementation Description

**Three Edit operations:**

**Edit 1 — Steps 3b and 3c (L157-407 in final file)**:
- Added "Team persistence" paragraph at the top of Step 3b explaining the team is NOT torn down after round 1, with one-TeamCreate-per-session rationale.
- Added "Team roster progression" bullet list documenting initial 6 members, post-fix state (+N fix DPs + 2 fix PCs), peak of 15, and round 2+ idle/re-tasked states.
- Updated 3b-i file list note to exclude `.beads/issues.jsonl` and auto-generated beads files.
- Updated 3b-iv header and bullets to clarify round 1 only spawns the team; round 2+ re-tasks via SendMessage.
- Updated OneTeamCreate constraint paragraph to reference fix agents spawning with `team_name: "nitpicker-team"`.
- Updated progress log label from "after Nitpicker team completes" to "after Nitpicker team completes round 1".
- Updated Step 3c opening to reference Big Head's bead-list SendMessage handoff (big-head-skeleton.md step 12).
- Replaced "see reviews.md Fix Workflow" references with inline "Fix Workflow" section directly in RULES.md Step 3c.
- Added Fix Workflow subsection with four steps:
  - 3c-i: Fix-cycle Scout (outside team, auto-approved, SSV gate, FIX_SCOUT_COMPLETE progress log)
  - 3c-ii: Spawn fix agents into team (N fix DPs sonnet, fix-pc-wwd haiku, fix-pc-dmvdc sonnet; minimal DP prompt structure; FIX_AGENTS_SPAWNED log)
  - 3c-iii: Fix inner loop ASCII flow diagram with retry limits (FIX_DMVDC_COMPLETE log)
  - 3c-iv: Round transition via SendMessage to Correctness, Edge Cases, Big Head; Clarity/Drift idle (ROUND_TRANSITION log)
- Removed obsolete "TDD workflow" and "fix-only workflow" references from auto-fix bullet.

**Edit 2 — Model Assignments table (L519-540 in final file)**:
- Updated "Fix Dirt Pushers" row to note `team_name: "nitpicker-team"` parameter.
- Added new row: `fix-pc-wwd | Task into team | haiku | WWD for fix DPs`.
- Added new row: `fix-pc-dmvdc | Task into team | sonnet | DMVDC for fix DPs`.
- Preserved existing CCB row with `sonnet` (already set by ygmj.1).

**Edit 3 — Retry Limits table (L638-654 in final file)**:
- Added five new rows after "SSV FAIL -> re-Scout cycle":
  - Fix DP stuck/crash: 0 retries, stuck-agent diagnostic + escalate
  - Fix PC crash: 1 retry, spawn replacement into team
  - Reviewer failure round 2+: 1 retry, spawn fresh reviewer into team
  - Big Head crash: 1 retry, spawn fresh with handoff brief
  - CCB material spot-check fail: 1 retry, shut down + fresh Big Head + re-run CCB

## 4. Correctness Review (per-file)

**orchestration/RULES.md** — re-read all three edited sections:

- Step 3b team persistence paragraph: correctly states "NOT torn down after round 1 consolidation", references round 4 cap and convergence as shutdown triggers, cites one-TeamCreate constraint. PASS.
- Team roster progression: correctly lists initial 6, post-fix N+2 active, peak 15, round 2+ idle state. Naming conventions (fix-dp-1..N, fix-pc-wwd, fix-pc-dmvdc, round suffixes fix-dp-r2-1, fix-pc-wwd-r2, fix-pc-dmvdc-r2) match reviews.md exactly. PASS.
- 3b-iv round 2+ note: correctly says "do NOT spawn a new team — re-task via SendMessage". PASS.
- TeamCreate constraint paragraph: updated to mention fix PCs messaging fix DPs as example; references `team_name: "nitpicker-team"`. PASS.
- Step 3c Fix Workflow: auto-approval documented with explicit "no user confirmation gate" wording. SSV gate documented as mechanical safety net. PASS.
- Fix inner loop diagram matches reviews.md verbatim for the core flow path. PASS.
- Round transition: documents re-tasking Correctness, Edge Cases, and Big Head via SendMessage; Clarity/Drift explicitly left idle. PASS.
- Progress log entries: four new milestones added (FIX_SCOUT_COMPLETE, FIX_AGENTS_SPAWNED, FIX_DMVDC_COMPLETE, ROUND_TRANSITION). All use same pipe-delimited format as existing entries. PASS.
- Model Assignments: fix-pc-wwd haiku, fix-pc-dmvdc sonnet, Fix Dirt Pushers sonnet with team_name note. CCB sonnet preserved from ygmj.1. PASS.
- Retry Limits: all five new rows present. Fix DP has 0 retries (consistent with stuck-agent policy), fix PC has 1, reviewer has 1, Big Head has 1, CCB material fail has 1. PASS.
- Unscoped sections (Steps 0-2, Step 4-6, Concurrency Rules, Hard Gates, Anti-Patterns, Session Directory, Wave Failure Threshold, Bead Priority Calibration, Context Preservation Targets): unchanged. PASS.

**Consistency with predecessor work:**
- ygmj.1 (CCB sonnet): CCB row in Model Assignments preserved as `sonnet`. PASS.
- ygmj.2 (bead-list handoff step 12): Step 3c opening references "big-head-skeleton.md step 12" explicitly. Fix-cycle Scout reads bead list from Big Head's SendMessage handoff. PASS.
- ygmj.3 (fix workflow in reviews.md): Fix inner loop diagram in RULES.md matches the flow documented in reviews.md. Auto-approval and SSV gate language is consistent. Fix team naming conventions match. PASS.

## 5. Build/Test Validation

This task modifies only orchestration documentation (RULES.md). No code, tests, or build artifacts are involved. Validation is doc-internal: structural consistency of the markdown, no broken references, no placeholder leakage.

Manual checks performed:
- `wc -l orchestration/RULES.md` → 700 lines (increased from ~590, consistent with additions)
- File ends with final context preservation targets section — no truncation
- All three edited sections confirmed present via line-range reads
- `git diff` reviewed: only the three target sections changed; all other sections untouched
- Predecessor commits confirmed: `git stash && git pull --rebase` incorporated ygmj.1/2/3 work before editing

## 6. Acceptance Criteria Checklist

- [x] **Step 3b explicitly states team persists across the full loop (no teardown after round 1)**
  PASS: "Team persistence" paragraph at L159-164 states "The team is NOT torn down after round 1 consolidation."

- [x] **Step 3c documents: Big Head handoff -> Scout (outside team) -> SSV -> fix agents spawn into team -> inner loop -> round transition**
  PASS: Steps 3c-i through 3c-iv document exactly this sequence in order.

- [x] **Fix-cycle Scout is documented as auto-approved for the user with SSV gate as mechanical safety net**
  PASS: L327-332 — "Auto-approval: The fix-cycle Scout's strategy is auto-approved — no user confirmation gate." + "SSV gate: SSV runs as a mechanical safety net."

- [x] **Model Assignments table updated: CCB sonnet, fix-pc-wwd haiku, fix-pc-dmvdc sonnet, fix DPs sonnet**
  PASS: CCB sonnet (ygmj.1 preserved), Fix Dirt Pushers sonnet, fix-pc-wwd haiku, fix-pc-dmvdc sonnet all present at L532-538.

- [x] **Error handling covers fix DP stuck/crash, fix PC crash, reviewer failure, Big Head crash, CCB material fail**
  PASS: Five new rows in Retry Limits table at L648-652.

- [x] **Team naming conventions documented (fix-dp-N, fix-pc-wwd, fix-pc-dmvdc with round suffixes)**
  PASS: L168 — "names: fix-dp-1..N, fix-pc-wwd, fix-pc-dmvdc; round suffixes for round 2+: fix-dp-r2-1, fix-pc-wwd-r2, fix-pc-dmvdc-r2"

- [x] **Progress log format includes new milestones for fix cycle steps**
  PASS: FIX_SCOUT_COMPLETE (L334), FIX_AGENTS_SPAWNED (L358), FIX_DMVDC_COMPLETE (L385), ROUND_TRANSITION (L400) all added.

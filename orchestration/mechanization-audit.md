# Mechanization Audit: RULES.md Enforcement Instructions

**Date**: 2026-03-24
**Crumb**: AF-489
**Scope**: `orchestration/RULES.md` (all enforcement instructions mapped to mechanized gates)
**Verification date**: 2026-03-24 (AF-491 — post-RULES.md cleanup)
**Verification legend**: `PASS` — documentation claim matches actual code behavior; `FAIL` — documentation claim is inaccurate or overstated relative to what the code actually enforces
**Status legend**:
- `MECHANIZED` — a hook, CLI tool, or checkpoint fully enforces this rule without relying on the Orchestrator's prompt text
- `PARTIALLY_MECHANIZED` — enforcement exists in code but does not cover all cases, or relies on a parameter the Orchestrator must supply correctly
- `PROMPT_ONLY` — no code enforcement; the rule exists only as prose in RULES.md or a checkpoint template

**Action legend**:
- `KEPT` — keep the RULES.md instruction as-is (defense-in-depth or prompt-only coverage)
- `SIMPLIFIED` — reduce or restructure the prose because the mechanic covers the core enforcement
- `REMOVED` — delete the instruction because the mechanic fully covers it and the prose adds confusion or redundancy

---

**Note**: RULES.md line references in this document are against the pre-simplification version (510 lines, commit 367d36b). AF-490 simplified RULES.md to 357 lines; current line numbers will differ. Search by instruction name rather than line number to navigate RULES.md.

## Quick Index

| # | Instruction | RULES.md lines | Status | Action | Verification |
|---|-------------|---------------|--------|--------|-------------|
| 1 | Startup-check gate (predecessor gate blocks agent spawn) | L170–186, L332–342 | MECHANIZED | SIMPLIFIED | PASS |
| 2 | Pre-spawn-check gate (prompt audit before agent spawn) | L192–207, L332–342 | MECHANIZED | SIMPLIFIED | PASS |
| 3 | Scope-verify gate (post-commit file scope check) | L209–236, L332–342 | MECHANIZED | SIMPLIFIED | PASS |
| 4 | Claims-vs-code gate (substance verification) | L231–236, L332–342 | MECHANIZED | SIMPLIFIED | PASS |
| 5 | Position check (spawn matches expected next_step) | L109–155 | MECHANIZED | SIMPLIFIED | PASS |
| 6 | Retry tracking (per-type limits + global cap) | L443–461 | MECHANIZED | SIMPLIFIED | PASS |
| 7 | Wave failure threshold (>50% failure blocks next wave) | L475–489 | MECHANIZED | SIMPLIFIED | PASS |
| 8 | Scope enforcement (file write advisory / enforcing block) | (implementation.md L142–163) | MECHANIZED | KEPT | PASS |
| 9 | Cycle detection in dependency graph | L332–342 (startup-check) | MECHANIZED | KEPT | PASS |
| 10 | Granularity constraint (crumb/file count per trail) | L332–342 (startup-check Check 1b) | PARTIALLY_MECHANIZED | KEPT | PASS |
| 11 | Banned phrases in AC | (crumb.py validate-spec) | PARTIALLY_MECHANIZED | KEPT | PASS |
| 12 | TDD ordering (tests before implementation) | (crumb.py validate-tdd) | PARTIALLY_MECHANIZED | KEPT | PASS |
| 13 | Security scanner (dangerous patterns in writes/bash) | (hook: ant-farm-security-scanner.js) | MECHANIZED | KEPT | PASS |
| 14 | Context monitor (warn at 35%/25% remaining) | L503–510 | MECHANIZED | SIMPLIFIED | PASS |
| 15 | Pause instruction (inform user at critical context) | L503–510 | MECHANIZED | SIMPLIFIED | PASS |
| 16 | JSON output for agents (machine-readable verdict) | (pre-spawn-check, claims-vs-code templates) | PROMPT_ONLY | KEPT | PASS |
| 17 | Conflict matrix (file overlap between waves) | L353–360 (Concurrency Rules) | PARTIALLY_MECHANIZED | KEPT | PASS |
| 18 | Stuck-agent detection (>10 min without commit) | L463–473 | PARTIALLY_MECHANIZED | SIMPLIFIED | PASS |
| 19 | Spec coverage (`validate-coverage`) | (crumb.py validate-coverage) | PARTIALLY_MECHANIZED | KEPT | PASS |
| 20 | Review-integrity gate (reviewer report audit) | L332–342 | MECHANIZED | SIMPLIFIED | PASS |
| 21 | Session-complete gate (exec summary + CHANGELOG audit) | L289–308, L332–342 | MECHANIZED | SIMPLIFIED | PASS |
| 22 | Orchestrator read restrictions (FORBIDDEN file list) | L56–65 | PROMPT_ONLY | KEPT | PASS |
| 23 | Orchestrator prohibition (no crumb commands directly) | L23–33 | PROMPT_ONLY | KEPT | PASS |
| 24 | Wave pipelining (wave N+1 Prompt Composer concurrent) | L198–206 | PROMPT_ONLY | KEPT | PASS |
| 25 | Agent task cap (≤3 tasks per agent per wave) | L355–356 | PARTIALLY_MECHANIZED | KEPT | PASS |

*Quick Index row numbers (#1–#25) are sequential and don't correspond to section labels (P0-1, P1-1, etc.). Search for the instruction name to navigate to its detailed section.*

---

## P0 Gates

### P0-1: Startup-Check Gate (Gate Enforcement — Root Gate)

**RULES.md lines**: L170–186 (Step 1b description), L332–342 (Hard Gates table)
**Mechanization**: `MECHANIZED`
**Action**: `SIMPLIFIED`

**What the rule says**: The startup-check must PASS before the Prompt Composer (and all downstream steps) can be spawned. On FAIL, re-run Recon Planner with specific violations. One retry max.

**What is mechanized**: `ant-farm-gate-enforcer.js` (PreToolUse hook on `Task`) reads `gate-status.json` from the session directory and blocks any Task spawn if the `startup-check` gate has not recorded a PASS verdict. The gate is fully enforced at the system level — the Orchestrator cannot bypass it without setting `bypass_gates: true` in config.json.

**Residual prompt value**: The RULES.md description of retry behavior (max 1 retry → escalate to user) is NOT covered by the hook; the hook only blocks or allows. The retry logic and escalation path remain as Orchestrator instructions. This portion is PROMPT_ONLY and must be KEPT.

**Recommended simplification**: Keep one sentence stating "startup-check is mechanically enforced by the gate-enforcer hook." Trim the retry count and escalation instructions to a single bullet — they remain valid Orchestrator guidance but don't need to restate what the hook does.

**Defense-in-depth consideration**: Both layers are intentional. The hook blocks at the runtime level (catches cases where the Orchestrator ignores the prose); the prose tells the Orchestrator how to respond when the hook fires. KEPT for prose, SIMPLIFIED for the hook-description portion.

---

### P0-2: Pre-Spawn-Check Gate (Prompt Audit)

**RULES.md lines**: L192–207 (Step 2 description), L332–342 (Hard Gates table)
**Template**: `orchestration/templates/checkpoints/pre-spawn-check.md`
**Mechanization**: `MECHANIZED`
**Action**: `SIMPLIFIED`

**What the rule says**: After composing agent prompts, run pre-spawn-check (Checkpoint Auditor, haiku) before spawning. Only after all pre-spawn-check PASS: spawn agents.

**What is mechanized**:
1. `ant-farm-gate-enforcer.js` records the `pre-spawn-check` gate state in `gate-status.json`. Agent spawns are blocked if `pre-spawn-check` has not passed.
2. `pre-spawn-check.md` defines 7 specific audit checks (real task IDs, real file paths, root cause text, all 7 mandatory steps present, scope boundaries, commit instructions, line specificity). The WARN/FAIL verdict thresholds are explicit and unambiguous.

**Residual prompt value**: The Orchestrator must actively spawn the Checkpoint Auditor with the correct file paths — the hook can only block, not spawn. The spawn instruction is PROMPT_ONLY and must be KEPT.

**Recommended simplification**: The RULES.md prose can drop the checklist of what pre-spawn-check verifies (it lives in the template). Keep the spawn instruction and the gate block reference.

---

### P0-3: Scope-Verify Gate (Post-Commit Scope Check)

**RULES.md lines**: L209–229 (Step 3 detail), L332–342 (Hard Gates table)
**Template**: `orchestration/templates/checkpoints/scope-verify.md`
**Mechanization**: `MECHANIZED`
**Action**: `SIMPLIFIED`

**What the rule says**: After each agent (serial mode) or all agents (batch mode) commit, run scope-verify before claims-vs-code. FAIL blocks queue progression.

**What is mechanized**:
1. `ant-farm-gate-enforcer.js` checks `scope-verify` gate status before allowing claims-vs-code spawns.
2. `scope-verify.md` defines PASS/WARN/FAIL verdict thresholds with explicit blocking behavior per verdict.
3. The mode selection rule (serial vs. batch) is mechanically derived from whether agents were spawned in a single message — a factual question, not a judgment call.

**Residual prompt value**: The Orchestrator must know the mode (serial/batch) and spawn the Checkpoint Auditor accordingly. The N=1 boundary condition and partial-wave-commit edge cases are Orchestrator instructions with no mechanic. KEPT.

**Recommended simplification**: Collapse the serial/batch prose to a brief rule and pointer to scope-verify.md. Remove the repetition of PASS/FAIL/WARN behaviors (they live in the template).

---

### P0-4: Gate Enforcement (General Hard Gates Table)

**RULES.md lines**: L330–342 (Hard Gates table)
**Mechanization**: `MECHANIZED`
**Action**: `SIMPLIFIED`

**What the rule says**: Lists all gates, what they block, and the artifact each gate produces.

**What is mechanized**: `ant-farm-gate-enforcer.js` enforces the gate chain defined in `gate-manager.js` (GATE_CHAIN constant: startup-check → pre-spawn-check → scope-verify → claims-vs-code → review-integrity → session-complete). The code reflects the same ordering as the table.

**Residual prompt value**: The table serves as a human-readable quick reference and documents artifact paths — valuable for the Orchestrator when diagnosing failures. KEPT as a reference, but the blocking semantics themselves are mechanized.

**Recommended simplification**: Add a note to the table: "Gate ordering is enforced by ant-farm-gate-enforcer.js." No prose changes needed in the table rows.

---

### P0-5: Position Check (Spawn Matches Expected Next Step)

**RULES.md lines**: L109–155 (Position Check section, global rule)
**Mechanization**: `MECHANIZED`
**Action**: `SIMPLIFIED`

**What the rule says**: Before every major phase transition, read `progress.log` to verify the next action matches the expected `next_step=` value. Mismatch → STOP.

**What is mechanized**: `ant-farm-gate-enforcer.js` calls `getExpectedNextStep(sessionDir)` from `progress-reader.js` on every Task spawn. If the spawn's prompt text does not include the expected step label, the hook blocks the spawn and writes a `position-check FAIL` verdict to `gate-status.json`. The known-steps list is hardcoded in the hook.

**Residual prompt value**: The `next_step` value convention table (L135–155) lists all valid values — this is reference material the Orchestrator uses when writing progress log entries. The hook reads these values but does not define them. The table must be KEPT.

**Recommended simplification**: Add a note to the Position Check section: "The position check is also enforced mechanically by ant-farm-gate-enforcer.js — mismatch blocks the spawn." Trim the manual-check prose ("run this command before every phase transition") to acknowledge the hook handles it.

---

### P0-6: Retry Tracking

**RULES.md lines**: L443–461 (Retry Limits table), L363–365 (Wave Management)
**Mechanization**: `MECHANIZED`
**Action**: `SIMPLIFIED`

**What the rule says**: Per-type retry limits (claims-vs-code: 2, review-integrity: 1, stuck: 0, startup-check fail: 1, Recon Planner: 1, etc.) with a global cap of 5. Track in Orchestrator's state file.

**What is mechanized**: `retry-tracker.js` implements per-type limits (`checkpoint: 2`, `agent_error: 1`, `stuck: 0`) and a global session cap of 5 in `retries.json`. `ant-farm-gate-enforcer.js` calls `canRetry()` before every Task spawn — re-spawns are blocked when limits are exhausted.

**Gap**: The hook's `RETRY_FAILURE_TYPE` is `'checkpoint'` (applies to gate-enforced re-spawns). Some RULES.md retry limits are for specific situations (startup-check FAIL → re-Recon Planner: 1) that do not map to the generic checkpoint type. These remain PROMPT_ONLY Orchestrator instructions.

**Residual prompt value**: The full Retry Limits table with human-readable scenarios (what to do, escalation paths) is PROMPT_ONLY for those cases not covered by the hook. The mechanic covers the structural cap; the table covers escalation behavior. KEPT.

**Recommended simplification**: Add a footnote to the table: "Global retry cap and per-type limits are enforced by retry-tracker.js. Retries blocked by the hook show a 'Retry limit exceeded' reason in the PreToolUse response." Trim the instruction to "Track retry count in Orchestrator state file" since retries.json handles this mechanically.

---

### P0-7: Cycle Detection in Dependency Graph

**RULES.md lines**: L332–342 (startup-check gate blocks downstream; cycle detection is in startup-check.md Check 3 implicitly via `crumb conflict-matrix`)
**Mechanization**: `MECHANIZED` (crumb.py `_detect_cycles`, `crumb doctor`)
**Action**: `KEPT`

**What the rule says**: Implicitly — via startup-check, the Recon Planner strategy must be free of intra-wave dependency violations (Check 3 in startup-check.md).

**What is mechanized**: `crumb.py` implements `_detect_cycles()` using `graphlib.TopologicalSorter`. `crumb doctor` runs cycle detection on the full task graph and breaks cycles with `_break_cycle_edges()`. The startup-check Checkpoint Auditor is directed to run `crumb conflict-matrix` as a cross-reference.

**Residual prompt value**: RULES.md does not describe cycle detection explicitly — this is covered in startup-check.md and crumb.py. The gate entry in the Hard Gates table adequately covers this. No RULES.md prose needs to be added or removed.

---

### P0-8: Banned Phrases in Acceptance Criteria

**RULES.md lines**: (Not in RULES.md directly; enforced via `crumb validate-spec`)
**Mechanization**: `PARTIALLY_MECHANIZED`
**Action**: `KEPT`

**What the rule says**: Acceptance criteria should not contain vague phrases like "works correctly" or "as expected." `crumb validate-spec <spec-file>` scans AC lines for banned phrases configured in `.crumbs/config.json`.

**What is mechanized**: `crumb.py validate-spec` (cmd_validate_spec) reads `banned_phrases` from config (defaults: "works correctly", "as expected"), compiles word-boundary regexes, and scans lines matching `AC-\d+\.\d+:`. Outputs PASS/FAIL with line-by-line matches.

**Gap**: No hook or gate triggers validate-spec automatically. It is available as a Recon Planner or Prompt Composer call but has no mandatory invocation point in RULES.md or startup-check.

**Why KEPT**: The mechanism exists and should be wired in. RULES.md does not currently instruct the Orchestrator to invoke validate-spec. This is both an audit finding and a justification for retaining a placeholder in the workflow until a follow-up crumb wires it in.

---

## P1 Gates

### P1-1: TDD Ordering (Tests Before Implementation)

**RULES.md lines**: (Implementation details in `implementation.md` Step 2.5; not in RULES.md directly)
**Mechanization**: `PARTIALLY_MECHANIZED`
**Action**: `KEPT`

**What the rule says**: Implementers must write failing tests before implementation code. `crumb validate-tdd <commit-hash>` verifies ordering. If `tdd: false`, skip check.

**What is mechanized**: `crumb.py validate-tdd` (cmd_validate_tdd) inspects a commit range, classifies files into `test_files` and `impl_files`, and identifies `ordering_violations`. The `tdd: false` flag is stored per-crumb. `claims-vs-code.md` Check 5 instructs the Checkpoint Auditor to run this command.

**Gap**: The check runs post-hoc (after commit) in claims-vs-code, not pre-emptively. No hook prevents an agent from writing implementation before tests. Enforcement is detective, not preventive.

**Why KEPT**: The post-hoc check in claims-vs-code is the correct enforcement point — the crumb track record and ordering_violations output give an unambiguous PASS/FAIL. Defense-in-depth: `implementation.md` also instructs agents directly. Both layers address different failure modes (agent defiance vs. process drift).

---

### P1-2: Security Scanner (Dangerous Patterns)

**RULES.md lines**: (No direct RULES.md instruction; security scanning is a hook)
**Mechanization**: `MECHANIZED`
**Action**: `KEPT`

**What is mechanized**: `ant-farm-security-scanner.js` (PreToolUse hook on Write, Edit, Bash) scans content for dangerous patterns from `security-scanner.js`. Enforcing mode blocks (`continue: false`); advisory mode warns. Exceptions via `security_exceptions` in `.ant-farm-scope.json`.

**RULES.md coverage**: RULES.md does not instruct the Orchestrator to run security checks explicitly — the hook operates transparently. No RULES.md change needed.

**Why KEPT**: The hook is the enforcement mechanism. No prose to add or remove from RULES.md.

---

### P1-3: Context Monitor (Warn at 35%/25% Remaining)

**RULES.md lines**: L503–510 (Context Preservation Targets)
**Mechanization**: `MECHANIZED`
**Action**: `SIMPLIFIED`

**What the rule says**: Finish with >50% context remaining; context monitor hook will warn at 35% and 25%.

**What is mechanized**: `ant-farm-context-monitor.js` (PostToolUse hook) fires at configurable thresholds (default 35%/25%) with WARNING/CRITICAL advisories injected into the model's context. Debounce prevents spam (5-tool-use window). At CRITICAL, the advisory explicitly instructs the Orchestrator to tell the user to run `/ant-farm-pause`.

**Residual prompt value**: The prose target (">50% remaining") gives the Orchestrator a planning goal — the hook only warns when already below threshold. The aspiration is PROMPT_ONLY. KEPT.

**Recommended simplification**: The sentence "The context monitor hook will warn you at 35% and 25% remaining" can be trimmed to a parenthetical — the hook fires regardless of what RULES.md says.

---

### P1-4: Pause Instruction (Inform User at Critical Context)

**RULES.md lines**: L503–510 (Context Preservation Targets; implied)
**Mechanization**: `MECHANIZED`
**Action**: `SIMPLIFIED`

**What is mechanized**: The CRITICAL advisory from `ant-farm-context-monitor.js` explicitly states: "Inform the user they should run /ant-farm-pause to preserve progress and start a new session." No separate RULES.md instruction is needed.

**Residual prompt value**: RULES.md currently only mentions the thresholds, not the pause action. The hook handles the pause instruction. No RULES.md change needed beyond noting the mechanic.

---

### P1-5: JSON Output for Agents (Machine-Readable Verdicts)

**RULES.md lines**: (Defined in checkpoint templates, not RULES.md directly)
**Mechanization**: `PROMPT_ONLY`
**Action**: `KEPT`

**What the rule says**: Checkpoint Auditor verdicts must follow a structured format (PASS/FAIL/PARTIAL with evidence). Report paths are specified per checkpoint.

**What is mechanized**: Nothing. The format is enforced only by the checkpoint template prose. No hook validates output format.

**Why KEPT**: This is a critical convention. Lack of mechanization means it's entirely reliant on the Checkpoint Auditor following its template. Defense-in-depth: the ESV and review-integrity gates verify downstream artifacts.

---

## P2 Gates

### P2-1: Conflict Matrix (File Overlap Between Waves)

**RULES.md lines**: L353–360 (Concurrency Rules: "No two agents edit the same file")
**Mechanization**: `PARTIALLY_MECHANIZED`
**Action**: `KEPT`

**What the rule says**: No two agents edit the same file — queue conflicting tasks sequentially.

**What is mechanized**:
1. `crumb.py conflict-matrix` (cmd_conflict_matrix) identifies overlapping files between open/in-progress crumbs and outputs risk tiers and wave grouping suggestions.
2. `startup-check.md` Check 1 directs the Checkpoint Auditor to verify no unresolved file overlaps exist within a wave.

**Gap**: The mechanic identifies conflicts in the briefing phase but cannot prevent the Orchestrator from spawning conflicting agents anyway — the gate blocks on overall startup-check FAIL, not specifically on conflict type. Scope-verify catches actual scope creep after the fact.

**Why KEPT**: The two-layer approach (pre-flight conflict-matrix + post-commit scope-verify) is intentional defense-in-depth. The RULES.md concurrency rule provides the conceptual frame; the tooling provides the check.

---

### P2-2: Wave Failure Threshold (>50% Failure Blocks Next Wave)

**RULES.md lines**: L475–489 (Wave Failure Threshold section)
**Mechanization**: `MECHANIZED`
**Action**: `SIMPLIFIED`

**What the rule says**: If >50% of agents in a single wave fail (after retries), stop new spawns, collect failure summaries, notify the user, and await instruction.

**What is mechanized**: `ant-farm-gate-enforcer.js` extracts the wave number from the spawn prompt and calls `getWaveStatus(sessionDir, prevWave)` from `wave-tracker.js`. If `prevWaveStatus.failureRate > waveFailureThreshold` (default 0.5), the spawn is blocked with "Wave failure threshold exceeded" reason. Threshold configurable via `config.json`.

**Residual prompt value**: The mechanic blocks the spawn; the prose defines what the Orchestrator should do (collect summaries, notify user, await instruction). The response workflow is PROMPT_ONLY. KEPT.

**Recommended simplification**: Add a note: "Wave failure threshold blocking is mechanically enforced by ant-farm-gate-enforcer.js." The four-step response procedure (stop, collect, notify, await) remains as Orchestrator guidance.

---

### P2-3: Stuck-Agent Detection (>10 Min Without Commit)

**RULES.md lines**: L463–473 (Stuck-Agent Diagnostic Procedure)
**Mechanization**: `PARTIALLY_MECHANIZED`
**Action**: `SIMPLIFIED`

**What the rule says**: When an agent has been active for >10 minutes without a commit, follow a diagnostic procedure before escalating. *(Updated from "15 turns" to wall-clock time in AF-490.)*

**What is mechanized**: `ant-farm-gate-enforcer.js` implements `checkStuckAgents()` which reads agent spawn timestamps from `agents.json` and emits WARNING (≥10 min, configurable) and CRITICAL (≥15 min, configurable) advisories. The advisory is injected into the Orchestrator's context via the PreToolUse response.

**Gap**: ~~The mechanic uses wall-clock time (minutes since spawn), not turn count (15 turns). "15 turns" in RULES.md is a proxy for elapsed time that the hook implements as minutes. The semantic match is approximate, not exact.~~ *(Resolved in AF-490: RULES.md now uses wall-clock time, matching the hook.)*

**Residual prompt value**: The 5-step diagnostic procedure (read task brief, check partial summaries, check git log, check last output, escalate) is PROMPT_ONLY — the hook flags but does not diagnose. KEPT.

**Recommended simplification**: ~~Update RULES.md to reference wall-clock time~~ *(Done in AF-490.)*

---

### P2-4: Spec Coverage (`validate-coverage`)

**RULES.md lines**: (Not explicitly in RULES.md — in crumb CLI help and orchestration tooling)
**Mechanization**: `PARTIALLY_MECHANIZED`
**Action**: `KEPT`

**What is mechanized**: `crumb.py validate-coverage` (cmd_validate_coverage) scans open crumbs for requirement (REQ) references and checks coverage against a spec file. This is available as a Recon Planner or Checkpoint Auditor tool call.

**Gap**: RULES.md does not instruct the Orchestrator to run validate-coverage at any specific step. The tool exists but has no defined trigger point in the main workflow.

**Why KEPT**: The tool is available but its use is discretionary. This is an audit finding: the mechanic is built but not wired into the workflow gates. Recommend a follow-up crumb to add a `validate-coverage` call to startup-check or Step 1b.

---

## Additional Enforcement Instructions (Prompt-Only)

### Additional-1: Orchestrator Read Restrictions (FORBIDDEN File List)

**RULES.md lines**: L56–65
**Mechanization**: `PROMPT_ONLY`
**Action**: `KEPT`

**What the rule says**: The Orchestrator must never read certain files (agent instruction files, checkpoint definitions, source code). These are delegated to subagents.

**Why PROMPT_ONLY**: No hook enforces Orchestrator read restrictions. The Orchestrator's tool calls are not filtered by file type.

**Why KEPT**: Essential for preventing context bloat and maintaining the information hierarchy. The Orchestrator's compliance is the only enforcement mechanism. Critical to retain.

---

### Additional-2: Orchestrator Prohibition (No Direct Crumb Commands)

**RULES.md lines**: L23–33
**Mechanization**: `PROMPT_ONLY`
**Action**: `KEPT`

**What the rule says**: The Orchestrator must not run `crumb show`, `crumb ready`, `crumb list`, `crumb blocked` — these go through the Recon Planner.

**Why PROMPT_ONLY**: No hook prevents the Orchestrator from calling crumb CLI commands or MCP tools directly. The prohibition exists only as a CLAUDE.md/RULES.md instruction.

**Historical note**: This prohibition was moved from RULES.md mid-turn content to CLAUDE.md (system prompt) to prevent parallel dispatch races (see MEMORY.md). RULES.md retains the instruction for completeness but CLAUDE.md is the authoritative enforcement point.

**Why KEPT**: Defense-in-depth. The CLAUDE.md system prompt is the primary gate; RULES.md is secondary. Both are PROMPT_ONLY but operate at different precedence levels.

---

### Additional-3: Wave Pipelining (Wave N+1 Prompt Composer Concurrent)

**RULES.md lines**: L198–206 (Step 2 wave pipelining)
**Mechanization**: `PROMPT_ONLY`
**Action**: `KEPT`

**What the rule says**: When spawning wave N Implementers, include the wave N+1 Prompt Composer in the SAME message so they launch concurrently.

**Why PROMPT_ONLY**: No hook enforces message batching. The Orchestrator can spawn agents one message at a time without consequence from the gate system.

**Why KEPT**: Performance optimization with no mechanical enforcement. The benefit (20-30% session time reduction) is real and worth retaining in RULES.md as Orchestrator guidance.

---

### Additional-4: Agent Task Cap (≤3 Tasks Per Agent Per Wave)

**RULES.md lines**: L355–356 (Concurrency Rules)
**Mechanization**: `PARTIALLY_MECHANIZED`
**Action**: `KEPT`

**What is mechanized**: `startup-check.md` Check 1b directs the Checkpoint Auditor to verify no agent has more than 3 tasks per wave. startup-check FAIL blocks downstream work.

**Gap**: The check runs pre-flight (before spawning) but does not prevent mid-session task rebalancing that could push an agent over the cap. The gate covers the briefing-time assignment, not runtime additions.

**Why KEPT**: The pre-flight check catches the common case. The prose in RULES.md provides the rationale (scope creep, context bloat, quality), which complements the mechanical count check.

---

## Summary Statistics

| Status | Count | Instructions |
|--------|-------|-------------|
| MECHANIZED | 14 | startup-check gate, pre-spawn-check gate, scope-verify gate, claims-vs-code gate, position check, retry tracking, wave failure threshold, scope enforcement, cycle detection, security scanner, context monitor, pause instruction, review-integrity gate, session-complete gate |
| PARTIALLY_MECHANIZED | 7 | granularity constraint, banned phrases, TDD ordering, conflict matrix, stuck-agent detection, spec coverage, agent task cap |
| PROMPT_ONLY | 4 | JSON output format, orchestrator read restrictions, orchestrator prohibition, wave pipelining |

**P0 gates**: 8 mapped (startup-check gate, pre-spawn-check gate, scope-verify gate, gate enforcement, position check, retry tracking, cycle detection, banned phrases) — all covered above
**P1 gates**: 5 mapped (TDD, security, context monitor, pause, JSON output) — all covered above
**P2 gates**: 4 mapped (conflict matrix, wave failure, stuck-agent, spec coverage) — all covered above

---

## Instructions That Should Be KEPT as Defense-in-Depth

The following instructions are mechanized but should remain in RULES.md because the mechanical layer and the prose layer address different failure modes:

| Instruction | Why Defense-in-Depth |
|-------------|---------------------|
| Startup-check gate prose | Hook blocks; prose defines retry and escalation behavior the hook cannot supply |
| Pre-spawn-check gate prose | Hook blocks; prose tells Orchestrator when and how to spawn the Checkpoint Auditor |
| Scope-verify gate prose | Hook records; prose defines serial vs. batch mode selection and edge cases |
| Claims-vs-code gate prose | Hook records; prose defines resume-agent workflow and retry escalation |
| Position check next_step table | Hook enforces the check; table defines valid values the Orchestrator must write |
| Retry limits table | Hook enforces counts; table defines per-scenario escalation behavior |
| Context monitor thresholds | Hook fires the warning; prose sets the planning target (>50% remaining) |
| Wave failure threshold | Hook blocks spawn; prose defines Orchestrator response (collect summaries, notify, await) |
| Conflict matrix rule | crumb conflict-matrix identifies; startup-check gates on it; prose provides the design intent |
| Orchestrator prohibitions | No hook enforces; CLAUDE.md is primary; RULES.md is secondary defense |
| Scope enforcement | scope-advisor hook fires advisory/block; implementation.md scope boundary section provides agent-facing instruction |

---

## Adjacent Issues (Do Not Fix Here)

1. **validate-coverage has no defined trigger**: `crumb validate-coverage` exists but RULES.md does not specify when the Orchestrator or Recon Planner should invoke it. Recommend adding to startup-check or Recon Planner workflow.

2. **~~"15 turns" vs. wall-clock time mismatch~~** *(RESOLVED in AF-490)*: RULES.md was updated to ">10 min without commit", aligning with the hook's wall-clock implementation.

3. **review-integrity gate is in the Hard Gates table but not in the main step narrative**: Step 3b delegates to RULES-review.md but the Hard Gates table references review-integrity. A reader of RULES.md alone cannot locate where this gate is invoked.

4. **session-complete gate**: Fully mechanized but the escalation paths (on second FAIL, present to user) are PROMPT_ONLY. These should remain in RULES.md.

---

## Documentation Verification (AC-17.4)

**Scope**: Post-RULES.md cleanup (AF-490). Verified 2026-03-24 by AF-491.
**Sources of truth**: `hooks/ant-farm-gate-enforcer.js`, `hooks/lib/gate-manager.js`, `hooks/ant-farm-security-scanner.js`, `hooks/ant-farm-scope-advisor.js`, `hooks/ant-farm-context-monitor.js`, `scripts/gate-manager.js` (lib), `scripts/retry-tracker.js`, `scripts/wave-tracker.js`, `scripts/progress-reader.js`

### Claim Verification Table

| File | Location | Claim | Verdict | Notes |
|------|----------|-------|---------|-------|
| `README.md` | L5 | "mechanical verification gates" | PASS | gate-enforcer.js is a real PreToolUse hook that mechanically blocks Task spawns |
| `README.md` | L12 | "Six verification checkpoints block progression" | FAIL → FIXED | Correct count is seven (startup-check, pre-spawn-check, scope-verify, claims-vs-code, review-integrity, session-complete, decomposition-check); README.md L61 and Hard Gates table (L75-83) both list seven. Fixed to "Seven" in AF-491. |
| `README.md` | L61 | "mechanically block progression" | PASS | Accurate: Checkpoint Auditor + gate-enforcer.js hook together constitute a mechanized system. startup-check is the direct PreToolUse hook enforcement; other gates enforce through the Checkpoint Auditor writing gate-status.json verdicts |
| `README.md` | L201 | "Strategy approval is mechanical, not conversational" | PASS | gate-enforcer.js blocks all Task spawns until startup-check PASS is recorded in gate-status.json; no human approval required |
| `CONTRIBUTING.md` | L72 | `RULES.md` Hard Gates table cross-reference instruction | PASS | Accurate: when adding a checkpoint, RULES.md Hard Gates table is a correct update target |
| `CONTRIBUTING.md` | L74 | `README.md` Hard Gates table cross-reference instruction | PASS | Accurate: when adding a checkpoint, README.md Hard Gates table is a correct update target |
| `CONTRIBUTING.md` | L220 | checkpoint verdict thresholds → `RULES.md` Hard Gates table dependency | PASS | Accurate: Hard Gates table describes blocking behavior that stems from checkpoint verdict thresholds |
| `AGENTS.md` | L1-23 | No enforcement mechanism claims present | PASS | AGENTS.md contains only task management references and session completion cross-reference. No stale enforcement claims introduced by AF-490. |
| `orchestration/GLOSSARY.md` | L23 | "hard gate" — "A checkpoint that must return PASS before the system proceeds to the next phase. All seven checkpoints ... are hard gates." | PASS | Correct count (7) and accurate definition. GATE_CHAIN in gate-manager.js lists 6 execution gates; decomposition-check is a planning-workflow gate not in GATE_CHAIN but documented as a hard gate in RULES.md and GLOSSARY.md. Both are accurate at their respective scopes. |
| `orchestration/GLOSSARY.md` | L29 | `checkpoint` definition — "mandatory verification gate that blocks the next phase" | PASS | Accurate: checkpoints are enforced by Checkpoint Auditor + gate-enforcer.js hook |
| `orchestration/GLOSSARY.md` | L43-51 | Checkpoint Names table — startup-check "Strategy mechanical correctness" | PASS | Accurate: "mechanical correctness" refers to structural/formulaic correctness (wave groupings, file conflicts, dependency violations) — not a claim about machine enforcement. The phrase correctly describes the check's purpose. |
| `orchestration/templates/checkpoints/startup-check.md` | L8 | "misses mechanical errors like file/task mismatches, agent overloading, or intra-wave dependency violations" | PASS | "Mechanical errors" = formulaic, structural errors. Accurate usage — describes the category of defect caught, not the enforcement method. |
| `orchestration/templates/checkpoints/startup-check.md` | L15 | "verify the Recon Planner's execution strategy for mechanical correctness" | PASS | Accurate: the four checks (file overlaps, task cap, file list match, dependency violations) are deterministic mechanical checks with no judgment required. |
| `orchestration/templates/checkpoints/startup-check.md` | L120 | "The startup-check validates mechanical correctness (no file conflicts, no dependency violations); a PASS is sufficient to begin implementation without waiting for user approval." | PASS | Accurate: gate-enforcer.js enforces that startup-check PASS is recorded before allowing downstream spawns. No human approval gate exists in the hook. |

### Summary

- **Total claims verified**: 14
- **PASS**: 13
- **FAIL (corrected)**: 1 — README.md L12 "Six verification checkpoints" corrected to "Seven verification checkpoints"
- **No inaccurate "mechanically enforced" claims** found in CONTRIBUTING.md, AGENTS.md, GLOSSARY.md, or startup-check.md. All uses of "mechanical" in these files refer to deterministic/formulaic checks (accurate) rather than overclaiming hook-level enforcement for prompt-only gates.

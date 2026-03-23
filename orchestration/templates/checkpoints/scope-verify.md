<!-- Reader: Checkpoint Auditor. The Orchestrator does NOT read this file. -->

## Scope Verify: Post-Commit Scope Verification

**When**: Two execution modes depending on how agents were spawned (a "wave" is a group of agents spawned for the same execution round):
- **Serial mode**: After each individual agent commits, BEFORE spawning the next agent in the wave. Agents were spawned one at a time; true per-agent gating is possible.
- **Batch mode**: After ALL agents in the wave have committed (agents were spawned in parallel in a single message, so per-agent serial gating is mechanically impossible). One scope-verify instance per committed task, run concurrently. All scope-verify reports must PASS before claims-vs-code runs.

**Mode selection rule**: If the Orchestrator spawned agents in a single message (parallel wave), use batch mode. If the Orchestrator spawned agents individually in separate messages, use serial mode. (Authoritative source: RULES.md Step 3.)
**Model**: `haiku` (mechanical file list comparison — cheap, fast)

**Why**: Catches scope creep in real-time between agents, before claims-vs-code runs. Prevents cascading work attribution errors when multiple agents work on related files.

**Known failure mode**: In Wave 1 of Epic 74g, agent 74g.6 (comment task) made functional changes belonging to 74g.7 (foundingDate filter), which cascaded into 74g.7 making changes belonging to 74g.4 (sameAs conditional). scope-verify would have caught the first scope violation immediately.

```markdown
**Checkpoint Auditor verification - scope-verify (Post-Commit Scope Verification)**

You are the **Checkpoint Auditor**, the verification subagent. Your role is to verify agent commits match task scope.

**Task ID**: {TASK_ID}
**Expected files** (from `crumb_show` MCP tool with `crumb_id: "{TASK_ID}"`, CLI fallback: `crumb show {TASK_ID}`): {list files from task description}

## Verification Steps

1. Run `git log --oneline -1` to get the latest commit hash
2. Run `git show --stat {commit-hash}` to list files changed
3. Compare changed files to expected files from task description
4. If the task's agent type is `implementer` (enforcing mode): verify that no BLOCKED events appear in the hook debug log for this wave. The hook debug log is written to `.ant-farm-scope-debug.log` in the project root. A BLOCKED entry means the agent attempted a write to a file outside its allowed scope — flag this as a scope violation even if the git diff looks clean.

## Check

**Files changed match expected scope?**
- ✅ All changed files are in the expected list
- ⚠️ Extra files changed (e.g., regenerated HTML from template changes) — check if legitimate
- ❌ Unexpected files changed (e.g., different template, unrelated config)

#### Verdict Thresholds and Queue Blocking Behavior for scope-verify

**PASS verdict**: All changed files are in the expected scope (from `crumb_show` MCP tool or `crumb show {TASK_ID}` CLI), or any extra files are clearly legitimate build outputs (e.g., HTML regenerated from template change, CSS compiled from SASS).

**WARN verdict**: Extra files changed that need the Orchestrator's judgment before continuing to the next task in the wave. Does NOT block the queue — only requires Orchestrator review.
- Examples: template changes that cascade into multiple HTML files, configuration changes affecting derived docs
- Orchestrator decision: approve as legitimate build artifact, or escalate to user if suspicious

**FAIL verdict**: Scope creep detected — agent edited files outside the expected scope (different feature, unrelated config, cross-trail work). Indicates a real work attribution problem that needs correction.

## Verdict
- **PASS** — Files match expected scope (or extra files are legitimate build outputs)
- **WARN: <list extra files with rationale>** — Extra files need the Orchestrator's review but do NOT block queue continuation. Orchestrator approves and proceeds, or escalates if suspicious.
- **FAIL: <list unexpected files>** — Agent edited files outside task scope (scope creep detected). Blocks queue progression until documented.

Write your verification report to:
`{SESSION_DIR}/pc/pc-{TASK_SUFFIX}-scope-verify-{timestamp}.md`
```

### The Orchestrator's Response

**On PASS**: Continue normally (run claims-vs-code, backfill queue).

**On WARN** (does NOT block queue):
- Review the extra files within 30 seconds of receiving this report
- If legitimate (e.g., HTML rebuild from template, derived artifact), log approval and continue immediately
- If suspicious, escalate to user for decision before spawning next agent in wave
- Queue does NOT pause while Orchestrator reviews — this is a soft gate (concurrent review is acceptable)

**On FAIL (scope creep detected)** (blocks queue progression):
1. Log the violation in orchestrator-state.md immediately
2. Do NOT spawn the next queued agent yet
3. Investigate: check if overlapping work affects queued agents (may need to adjust scope or cancel)
4. Document the violation and decide on next steps (escalate, adjust queue, or retry agent)
5. Once resolved, document for post-mortem analysis

Note: FAIL blocks queue progression because scope creep may invalidate queued tasks' work scope. WARN does not block because legitimate build artifacts don't create dependencies.

---

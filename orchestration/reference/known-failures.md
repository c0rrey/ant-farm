# Known Failure Modes

## Epic 3: Skipped Design and Review Steps

**What happened**: Implementers bypassed Step 2 (Design 4+ approaches) and Step 4 (Per-File Correctness Review). Unreviewed, undesigned work shipped with unknown quality.

**Root cause**: Steps were marked "MANDATORY" in templates but nothing verified compliance. No checkpoints existed to enforce adherence.

**Fix applied**: Hard gate enforcement — Crumbs Moved vs Crumbs Claimed now verifies approach substance and review evidence before allowing task closure.

**When to apply**: Every quality review session. Verify agents completed all 6 mandatory steps before closing tasks.

---

## Epic 74g: Work Scrambling (Same-File Parallelism)

**What happened**: Three agents worked on the same file in parallel without line-level boundaries. Agent 74g.6 removed a filter that was task 74g.7's work. Agent 74g.7 found it done, made a different change. Agent 74g.4 made yet another. All functional work completed but attribution scrambled and summaries misleading.

**Root causes**:
- No file-level locking for same-file tasks
- Agents fixed adjacent issues they noticed ("while I'm here" fixes)
- No real-time scope verification between commits
- Colony Cartography Office verified prompts but not line-level specificity

**Fixes applied**:
1. **Wandering Worker Detection** (Post-Commit Scope Verification) — Lightweight check after each commit verifies files changed match expected scope, catching scope creep before next agent spawns
2. **Enhanced pre-spawn-check** — Now requires line number specificity (e.g., "lines 23-24" not "file.py")
3. **Anti-Scope-Creep Template** — Aggressive boundary language with explicit "Adjacent Issues Found" section
4. **Conflict Risk Assessment** — Pre-flight file modification matrix with LOW/MEDIUM/HIGH risk tiers and serialization strategies

**When to apply** (every multi-agent session):
- Always use anti-scope-creep template for Implementers
- Always run scope-verify after each commit
- Always assess file conflict risk before spawning (create modification matrix)
- Serialize tasks when 3+ agents touch the same file (HIGH risk tier)

---

## Template for Future Failures

| Field | Content |
|-------|---------|
| What happened | Concise narrative of the failure |
| Root cause | Why it occurred (system gap, missing step, assumption) |
| Fix applied | Process change or gate added to prevent recurrence |
| When to apply | Which phases/sessions need the fix |

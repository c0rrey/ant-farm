# Summary: ant-farm-fomy — Auto-approve Scout strategy in Step 1

**Commit**: `8af72c3`
**File changed**: `orchestration/RULES.md` (Step 1b, lines 90-111)

---

## 1. Approaches Considered

### Approach A: Always auto-approve after SSV PASS (selected)
Remove the user approval gate entirely. After SSV PASS, the Queen proceeds directly to Step 2 with no pause.

Tradeoffs:
- Pro: Maximum latency reduction. Consistent behavior regardless of session size.
- Pro: SSV already provides the substantive mechanical safety check; user approval on top of a SSV PASS adds no verification value.
- Pro: Aligns with the precedent established by ant-farm-ygmj (fix-cycle Scout auto-approve).
- Con: No user veto point before agents spawn. A strategically wrong but structurally valid strategy would execute.

### Approach B: Complexity threshold (auto-approve <= N tasks, prompt > N)
Auto-approve small sessions; pause for user confirmation on large ones.

Tradeoffs:
- Pro: Gives user a veto for high-task-count sessions where mistakes are more expensive.
- Con: Threshold value is arbitrary. Task count alone is not a reliable risk signal — a 15-task SSV PASS is just as structurally sound as a 3-task one. Adds Queen logic to parse briefing.md task count. Inconsistent UX.

### Approach C: Silent informational display without blocking
Show the strategy as an informational message, then proceed without waiting for a response.

Tradeoffs:
- Pro: Preserves user visibility while eliminating the blocking wait.
- Con: Marginal improvement over full auto-approve. The display still consumes tokens and adds cognitive overhead for users who do not need to review it. Interruption window is effectively zero.

### Approach D: Opt-in user gate via environment variable
Default auto-approve; set `REQUIRE_STRATEGY_APPROVAL=1` to re-enable the prompt.

Tradeoffs:
- Pro: Maximum flexibility for users who want control.
- Con: RULES.md cannot enforce env var conventions. Adds operational complexity (users must know the variable exists). Over-engineered for a documentation change. No mechanism to actually check the env var in a Claude Code orchestration context.

---

## 2. Selected Approach with Rationale

**Approach A — Always auto-approve after SSV PASS.**

The SSV mechanical check verifies the three failure modes that cause agent conflicts: file overlap within waves, file list match against beads, and intra-wave dependency ordering. A strategy that passes these checks is structurally safe to execute. The user approval gate was redundant — it provided a veto point but no additional verification capability.

The complexity threshold (Approach B) was explicitly evaluated and rejected. Task count is not a useful risk proxy: SSV correctness does not degrade with session size. Maintaining an arbitrary threshold constant in RULES.md would create a maintenance burden with no clear safety benefit.

The ant-farm-ygmj precedent (auto-approve fix-cycle Scout strategies) was the direct motivation. This change extends that pattern to the main orchestration loop.

---

## 3. Implementation Description

Modified `orchestration/RULES.md` Step 1b (lines 90-111):

1. Removed "before presenting to user" from the SSV gate description (line 91) — the framing implied user presentation was always the next step.

2. Replaced the **On SSV PASS** instruction:
   - Old: "Present the recommended strategy to the user for approval."
   - New: "Proceed directly to Step 2. Do NOT wait for user approval. SSV is the mechanical safety gate — a passing strategy is structurally sound and ready to execute. No complexity threshold applies; auto-approve regardless of task count."

3. Added a **Risk analysis** block (lines 103-109) documenting: what SSV verifies, the remaining risk (scope error), the Scout's mitigation for that risk, the complexity threshold evaluation and rejection decision, and the additional safety nets still in effect (Dirt Pusher summaries, DMVDC, WWD).

4. Updated the progress log comment (line 111) from "after SSV PASS and user approves strategy" to "after SSV PASS" — accurately reflecting that user approval no longer occurs. The shell command itself is unchanged; `tasks_approved=<N>` refers to the task count in the strategy, not a user approval action.

No other sections of RULES.md were modified.

---

## 4. Correctness Review

### orchestration/RULES.md (Step 1b section only)

- **AC1 — No user approval after SSV PASS**: Line 97 explicitly reads "Proceed directly to Step 2. Do NOT wait for user approval." The old "Present the recommended strategy to the user for approval" language is completely removed. PASS.
- **AC2 — Risk analysis documented**: Lines 103-109 contain an explicit risk analysis block. It covers: what SSV verifies (file overlap, file list integrity, dependency ordering), the remaining risk (scope error), the Scout's mitigation (derives scope from user's message), and additional safety nets (Steps 3 and 4 verification). PASS.
- **AC3 — Complexity threshold decision documented**: Line 107-108 explicitly states "A complexity threshold was evaluated and rejected: task count alone is not a useful risk signal; a 15-task session that passes SSV is structurally sound." PASS.

Adjacent issues noticed but not fixed (per scope boundary):
- The `tasks_approved=<N>` placeholder in the progress log shell command is slightly misleading (it could be read as "N tasks the user approved") but is out of scope. Filed no new issue as the semantic meaning — task count in the strategy — is clear from context.

---

## 5. Build/Test Validation

This task modifies documentation only (RULES.md). There are no build artifacts, tests, or scripts to run. The file is valid Markdown and the diff was inspected character-by-character during the review step. No linting failures.

---

## 6. Acceptance Criteria Checklist

| Criterion | Status |
|---|---|
| RULES.md Step 1b no longer requires user approval after SSV PASS | PASS |
| Risk analysis documented: what could go wrong, what safety nets exist | PASS |
| Decision on complexity threshold documented (always auto-approve vs threshold-based) | PASS |

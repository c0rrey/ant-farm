# Task Summary: ant-farm-trfb

**Task**: fix: one-TeamCreate-per-session constraint undocumented in operator-facing docs
**Status**: Complete
**Files changed**: `orchestration/RULES.md`, `CONTRIBUTING.md`

---

## 1. Approaches Considered

### Approach A: Note in RULES.md Step 3b-iv + note in CONTRIBUTING.md "Adding a New Agent"
Add a constraint callout directly below the Step 3b-iv team membership rules, and add a subsection in CONTRIBUTING.md's "Adding a New Agent" section. Most discoverable placement — operators hit Step 3b-iv when spawning teams, and framework extenders hit "Adding a New Agent" when extending the framework.

### Approach B: New "Runtime Constraints" section in RULES.md + note in SETUP.md
Add a top-level constraints section to RULES.md and mention the limit in SETUP.md. More prominent in RULES.md but harder to find during active work (operators don't scan for constraint sections mid-session). SETUP.md is less relevant because it covers initial project wiring, not agent extension.

### Approach C: Note in RULES.md Concurrency Rules section + note in CONTRIBUTING.md
Place the constraint in the existing Concurrency Rules section since TeamCreate is a concurrency concern. Reasonable placement but less discoverable than Step 3b-iv — the constraint only matters when spawning a team, which is Step 3b-iv context.

### Approach D: Note in RULES.md Hard Gates table + note in CONTRIBUTING.md
Add a row to the Hard Gates table for the TeamCreate constraint. Hard Gates is for checkpoint gates, not structural constraints — mixing these categories would clutter the table.

---

## 2. Selected Approach with Rationale

**Approach A** was selected because:
- Step 3b-iv is the exact decision point where the constraint matters — an operator reading "how do I add an agent to the team?" immediately encounters the constraint.
- CONTRIBUTING.md's "Adding a New Agent" section is where framework extenders look when designing new agent roles — the constraint directly affects whether a new agent can be a separate Task spawn or must be a team member.

---

## 3. Implementation Description

**Edit 1 — `orchestration/RULES.md`, Step 3b-iv (after the existing team member list)**:
Added a "Constraint: one TeamCreate per session" paragraph explaining:
- Claude Code supports only one `TeamCreate` per session
- The Nitpicker team uses this slot
- Agents needing intra-team messaging (SendMessage) must be team members, not separate Task spawns
- Instruction not to add a second TeamCreate anywhere in the workflow

**Edit 2 — `CONTRIBUTING.md`, "Adding a New Agent" section (new subsection)**:
Added "### One-TeamCreate-per-session constraint" subsection after "Cross-file updates after adding an agent" explaining:
- Only one TeamCreate per session is supported
- Nitpicker review team uses this slot for the entire session
- Implication for new agents: if the agent needs SendMessage reception, it must be a team member
- Agents not requiring intra-team messaging can be regular Task spawns

---

## 4. Correctness Review

**File: `orchestration/RULES.md`**

- Lines 201-207: Constraint note is placed after the existing team membership rules (lines 196-199), which is the natural read continuation. It does not replace or contradict existing content.
- The note correctly references the PC/Big Head SendMessage pattern that motivates the constraint (consistent with lines 196-197).
- No other section of RULES.md was modified.

**File: `CONTRIBUTING.md`**

- Lines 43-49: New subsection placed after "Cross-file updates after adding an agent" (line 37) and before "Adding a New Checkpoint" (line 51). This is the correct scoping — it appears within the "Adding a New Agent" section.
- Language accurately reflects the discovered constraint: one TeamCreate per session, Nitpicker team uses it, new agents requiring SendMessage must be team members.
- No other section of CONTRIBUTING.md was modified.

**Assumptions audit**:
- Confirmed from MEMORY.md: "Claude Code does not support Queen → Subagent → Sub-subagent" and "One Team Per Session — Claude Code only supports one TeamCreate per session."
- Confirmed PC receives SendMessage from Big Head (RULES.md line 197: "Pest Control MUST be a team member so Big Head can SendMessage to it").
- Scope note: task said "CONTRIBUTING.md or SETUP.md" — chose CONTRIBUTING.md because it covers framework extension (adding agents), which is the primary audience for this constraint.

---

## 5. Build/Test Validation

No build artifacts affected. Documentation-only change. Manual verification:
- RULES.md Step 3b-iv content before the edit: correctly preserved (lines 193-199 unchanged).
- CONTRIBUTING.md "Adding a New Agent" section structure: new subsection fits between "Cross-file updates" and "Adding a New Checkpoint" without disrupting the section flow.

---

## 6. Acceptance Criteria Checklist

1. **RULES.md documents the one-TeamCreate-per-session constraint** — PASS. Lines 201-207.
2. **Note explains the architectural implication (PC must be team member, not separate spawn)** — PASS. Lines 203-206 explain the implication; line 197 already explains PC's required membership.
3. **CONTRIBUTING.md or SETUP.md mentions the constraint for framework extenders** — PASS. CONTRIBUTING.md lines 43-49 cover this with a dedicated subsection in "Adding a New Agent".

---

**Commit hash**: (recorded after commit)

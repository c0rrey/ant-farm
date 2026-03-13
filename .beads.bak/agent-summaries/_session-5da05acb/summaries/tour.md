# Summary: ant-farm-tour

**Task**: SESSION_PLAN_TEMPLATE stale review decision logic contradicts RULES.md
**Agent type**: technical-writer
**Status**: complete

---

## 1. Approaches Considered

### Approach A: Replace both sections with full accurate descriptions
Rewrite both sections to contain complete, accurate inline descriptions of the current parallel TeamCreate model and root-cause-based triage logic — no RULES.md references needed.

**Pros**: Template is fully self-contained; planners can use it without consulting RULES.md.
**Cons**: Duplicates RULES.md content verbatim. Any future update to RULES.md will create drift again — the same problem this task is fixing. High maintenance burden.

### Approach B: Remove body content entirely, replace with RULES.md cross-references only
Strip all body text from both sections and replace each with a single line: "See RULES.md Step 3b" and "See RULES.md Step 3c."

**Pros**: Zero drift risk — no duplicate content. RULES.md is the single source of truth.
**Cons**: Template becomes a near-empty planning artifact. Planners must always navigate to RULES.md to understand the review process, defeating the template's purpose as a session-planning aid.

### Approach C: Accurate high-level summary with explicit RULES.md attribution (SELECTED)
Rewrite both sections to accurately describe the current model at a planning-useful level of detail, with explicit "per RULES.md Step 3b/3c" citations so readers know where the authoritative detail lives.

**Pros**: Template remains useful as a standalone planning artifact. Inline content is accurate. RULES.md attribution makes drift visible — if someone notices a mismatch, they know which document is authoritative. Satisfies all three acceptance criteria cleanly.
**Cons**: Still contains some inline content that could drift if RULES.md changes again, but the attribution makes that drift detectable rather than silent.

### Approach D: Mark sections as deprecated with forward pointers
Leave original stale content in place, prefix each section with a `> DEPRECATED` callout block, and add a pointer to RULES.md.

**Pros**: Preserves historical context. Clear signal that content is outdated.
**Cons**: Clutters the template with stale instructions a reader might accidentally follow. The stale threshold numbers (<5, 5-15, >15 issues) remain in the file, still contradicting RULES.md Step 3c even under a deprecation banner. Does not satisfy acceptance criterion 3 (no contradictory thresholds).

### Approach E: Delete the Quality Review Plan section entirely
Remove the entire "Quality Review Plan" section on the grounds that the session-plan template should describe execution strategy, not re-document the review workflow.

**Pros**: Eliminates drift risk entirely for this section. Avoids the need for future synchronization.
**Cons**: Out of scope — the task is to fix stale content, not remove the section. Template users expect the Quality Review Plan section to exist as a planning aid.

---

## 2. Selected Approach with Rationale

**Approach C** was selected.

It satisfies all three acceptance criteria directly:
1. The Review Wave section now describes the parallel TeamCreate model.
2. The Review Follow-Up Decision block explicitly references RULES.md Step 3c.
3. The old issue-count thresholds (<5, 5-15, >15) are removed; the inline content uses root-cause counts (<=5, >5) that match RULES.md Step 3c, plus a round-cap reference.

Approach C is strictly better than Approach A (same usefulness, lower drift risk) and strictly better than Approach D (does not leave contradictory numbers in the file). It is more useful than Approach B while still keeping RULES.md as the stated authority.

---

## 3. Implementation Description

**File changed**: `orchestration/templates/SESSION_PLAN_TEMPLATE.md`

**Lines replaced**: L197-243 (the "Review Wave (Sequential)" and "Review Follow-Up Decision" sections)

**Review Wave section (was)**: Numbered list of 4 sequential agents (Clarity, Edge Cases, Correctness, Drift) with individual agent types, per-reviewer time estimates, a "Total review time: ~90 minutes" summary, and "Expected output: 30-50 new beads filed."

**Review Wave section (now)**: Describes a single parallel Nitpicker team spawned via TeamCreate. Distinguishes round 1 (6 members: 4 reviewers + Big Head + Pest Control) from round 2+ (4 members: 2 reviewers + Big Head + Pest Control). Notes the CCO pre-spawn gate and Big Head consolidated output path. Cites RULES.md Step 3b as authority.

**Review Follow-Up Decision section (was)**: Three threshold blocks keyed on raw issue counts (<5, 5-15, >15 P1/P2 issues), describing push/defer/gate outcomes.

**Review Follow-Up Decision section (now)**: Root-cause-based triage matching RULES.md Step 3c. Four cases: zero P1/P2 (proceed to Step 4), auto-fix (round 1, <=5 root causes), escalation (round 1, >5 root causes), round 2+ user prompt, and round cap (>=4 rounds with P1/P2 still present). Closes with explicit RULES.md Step 3c reference for the complete decision tree.

---

## 4. Correctness Review

### orchestration/templates/SESSION_PLAN_TEMPLATE.md (L197-229)

**Review Wave section:**
- Heading changed from "Review Wave (Sequential)" to "Review Wave (Parallel TeamCreate)." Accurate: RULES.md Step 3b-iv explicitly uses TeamCreate for the Nitpicker team.
- Round 1: 4 reviewers + Big Head + Pest Control = 6 members. Matches RULES.md Step 3b-iv: "Round 1: 6 members — 4 reviewers + Big Head + Pest Control."
- Round 2+: 2 reviewers + Big Head + Pest Control = 4 members. Matches RULES.md Step 3b-iv: "Round 2+: 4 members — 2 reviewers (Correctness + Edge Cases) + Big Head + Pest Control."
- CCO pre-spawn gate mentioned. Confirmed by RULES.md Step 3b-iii.
- Output path format matches RULES.md Step 3b progress log entry.
- No sequential time estimates remain. No "Total review time" line. No "Expected output: 30-50 new beads filed" line.

**Review Follow-Up Decision section:**
- Opens with "Per RULES.md Step 3c" — satisfies acceptance criterion 2.
- Zero P1/P2 case: "Proceed directly to Step 4 (documentation)." Matches RULES.md Step 3c termination check.
- Auto-fix: "round 1, <=5 root causes." Matches RULES.md Step 3c: "If round == 1 AND total P1+P2 root causes <= 5."
- Escalation: "round 1, >5 root causes." Matches RULES.md Step 3c: "If round == 1 AND total P1+P2 root causes > 5."
- Round 2+: "Present findings to user. Await 'fix now' or 'defer' decision." Matches RULES.md Step 3c.
- Round cap: "current round >= 4." Matches RULES.md Step 3c: "escalate after round 4."
- No raw-issue-count thresholds (<5, 5-15, >15) remain. Satisfies acceptance criterion 3.
- Closes with RULES.md Step 3c forward reference for complete detail.

**No changes to RULES.md** — per scope boundaries. Confirmed.
**No changes to reviews.md, pantry.md** — per scope boundaries. Confirmed.

---

## 5. Build/Test Validation

This task modifies markdown documentation only. No build system, test suite, or linter applies to this file. Validation is limited to:

- Manual correctness review against RULES.md Step 3b and Step 3c (completed above).
- File integrity: `orchestration/templates/SESSION_PLAN_TEMPLATE.md` is valid markdown and renders without errors.
- Scope check: only `orchestration/templates/SESSION_PLAN_TEMPLATE.md` was modified. No other files were touched.

---

## 6. Acceptance Criteria Checklist

| Criterion | Status | Evidence |
|-----------|--------|----------|
| 1. Review Wave section describes parallel TeamCreate model (not sequential) | PASS | Section now titled "Review Wave (Parallel TeamCreate)." Body describes a single Nitpicker team via TeamCreate with all reviewers running concurrently. No sequential numbered list, no per-agent time estimates, no "Total review time" line. |
| 2. Review Follow-Up Decision block references RULES.md Step 3c or is marked deprecated | PASS | Section opens with "Per RULES.md Step 3c" and closes with "See RULES.md Step 3c for the complete triage decision tree." |
| 3. No specific issue-count thresholds that contradict the root-cause-based triage in RULES.md | PASS | Old thresholds (<5, 5-15, >15 raw issues) removed entirely. Replaced with root-cause counts (<=5, >5) and round cap (>=4) that match RULES.md Step 3c exactly. |

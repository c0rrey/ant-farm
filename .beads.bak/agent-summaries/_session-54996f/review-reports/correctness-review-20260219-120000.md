# Report: Correctness Redux Review

**Scope**: orchestration/templates/reviews.md, orchestration/templates/big-head-skeleton.md, orchestration/templates/pantry.md, orchestration/RULES.md
**Reviewer**: Correctness Redux Review (code-reviewer)

## Findings Catalog

### Finding 1: Team member count inconsistency -- reviews.md Team Setup still says "5 members"

- **File(s)**: `/Users/correy/projects/ant-farm/orchestration/templates/reviews.md:53`, `/Users/correy/projects/ant-farm/orchestration/templates/reviews.md:56`
- **Severity**: P2
- **Category**: correctness
- **Description**: The Team Setup section (lines 53 and 56) states "The Queen creates the Nitpicker team with **5 members** (4 reviewers + Big Head)" and "Create a team with these 5 members." However, ant-farm-7hgn's acceptance criterion #2 requires "Pest Control is spawned as part of the Nitpicker team, not as a separate Queen-orchestrated agent," making the correct count 6 members. The Nitpicker Checklist on line 573 was correctly updated to say 6 members, and RULES.md Step 3b was correctly updated to say 6 members. But lines 53 and 56 were missed during the ant-farm-7hgn commit (46a776a), creating a contradiction within the same file. A Queen following the Team Setup section would create only 5 members, omitting Pest Control and breaking Big Head's SendMessage to Pest Control at step 8.
- **Suggested fix**: Change line 53 to "The Queen creates the Nitpicker team with **6 members** (4 reviewers + Big Head + Pest Control):" and line 56 to "Create a team with these 6 members." Add a 6th numbered member entry for Pest Control in the example block (lines 66-70).
- **Cross-reference**: Related to Finding 2 (same root cause -- incomplete propagation of 6-member team change).
- **Acceptance criterion violated**: ant-farm-7hgn AC #2: "Pest Control is spawned as part of the Nitpicker team, not as a separate Queen-orchestrated agent"

### Finding 2: big-head-skeleton.md TeamCreate example omits Pest Control as 6th team member

- **File(s)**: `/Users/correy/projects/ant-farm/orchestration/templates/big-head-skeleton.md:23`, `/Users/correy/projects/ant-farm/orchestration/templates/big-head-skeleton.md:27-38`
- **Severity**: P2
- **Category**: correctness
- **Description**: The TeamCreate example in big-head-skeleton.md (lines 23, 27-38) says "Big Head is the 5th member" and shows only 5 members in the `members` array. It does not include Pest Control. This contradicts the updated RULES.md (line 98: "6 members") and reviews.md Nitpicker Checklist (line 573: "6 members"). Since the Queen reads big-head-skeleton.md once per review cycle (per Queen Read Permissions), this example is a primary reference for constructing the TeamCreate call. If the Queen follows this example literally, Pest Control will not be in the team, and Big Head's step 8 (`SendMessage` to Pest Control) will fail because the recipient is not a team member.
- **Suggested fix**: Update line 23 to "Big Head is the 5th member. Pest Control is the 6th." Add a 6th entry to the members array: `{ "name": "pest-control", "prompt": "<pest-control prompt>", "model": "sonnet" }`.
- **Cross-reference**: Related to Finding 1 (same root cause -- incomplete propagation of 6-member team change).
- **Acceptance criterion violated**: ant-farm-7hgn AC #2: "Pest Control is spawned as part of the Nitpicker team, not as a separate Queen-orchestrated agent"

### Finding 3: Big Head step 8 SendMessage uses display name "Pest Control" instead of team member name "pest-control"

- **File(s)**: `/Users/correy/projects/ant-farm/orchestration/templates/big-head-skeleton.md:66`
- **Severity**: P3
- **Category**: correctness
- **Description**: Line 66 of big-head-skeleton.md instructs Big Head to "Send consolidated report path to Pest Control (SendMessage)". The SendMessage tool requires the recipient's team member name (e.g., `pest-control`), not a display name. The current text uses "Pest Control" as a natural-language label in the instruction text, which is acceptable since the agent will interpret it -- but the instruction doesn't specify the exact member name to use in the `recipient` field. This is a minor ambiguity rather than a hard bug, since an agent reading this will likely derive the kebab-case name from context. However, the reviews.md Step 4 example (line 530) shows `to="pest-control"` with the correct kebab-case name, creating a minor inconsistency in precision between the two references.
- **Suggested fix**: Change line 66 to include the exact member name: `Send consolidated report path to pest-control (SendMessage): "Consolidated report ready at..."` or add `(team member name: "pest-control")` as a parenthetical.
- **Cross-reference**: N/A -- standalone polish issue.

### Finding 4: reviews.md Step 4 SendMessage example uses positional args instead of named params

- **File(s)**: `/Users/correy/projects/ant-farm/orchestration/templates/reviews.md:529-532`
- **Severity**: P3
- **Category**: correctness
- **Description**: The SendMessage notification example at lines 529-532 shows `SendMessage(to="pest-control", message="...")`. However, the actual SendMessage tool uses `recipient` and `content` as parameter names, not `to` and `message`. This is a template example (not executed code), so the agent will interpret intent rather than copy-paste the exact call. But the skeleton template (big-head-skeleton.md line 66) uses natural language instead, creating two different pseudo-API conventions for the same operation. Neither matches the actual tool schema exactly.
- **Suggested fix**: Update the example to use the actual parameter names: `SendMessage(type="message", recipient="pest-control", content="...", summary="...")` to match the real tool interface.
- **Cross-reference**: N/A -- standalone polish issue.

### Finding 5: Stale line reference in RULES.md Step 3c points to wrong section after content shift

- **File(s)**: `/Users/correy/projects/ant-farm/orchestration/RULES.md:113`
- **Severity**: P2
- **Category**: correctness
- **Description**: RULES.md line 113 references "orchestration/templates/reviews.md L485-514 (test-writing + fix workflow)" for the "fix now" path. After the ant-farm-7hgn commit (46a776a) inserted the Step 4 checkpoint gate (38 new lines) before the consolidated summary template, lines 485-514 now contain the consolidated summary template (Beads filed count, Read Confirmation table, Root Causes Filed, Deduplication Log, Priority Breakdown). The actual test-writing + fix workflow ("If user chooses 'fix now' -- Queen spawns fix tasks") is now at approximately lines 609-629. A Queen following this reference would read the wrong section entirely -- a consolidated summary format spec instead of the fix workflow instructions.
- **Suggested fix**: Update RULES.md line 113 to reference the correct line range: `L609-629` (or better, reference by section heading "Queen's Step 3c: User Triage on P1/P2 Issues" to avoid future line-drift issues).
- **Cross-reference**: Flagged by clarity-reviewer; verified and added here as a correctness finding since it causes incorrect behavior (Queen reads wrong section).
- **Acceptance criterion context**: Not a direct AC violation for any single task, but a regression introduced by the ant-farm-7hgn commit shifting content without updating the cross-reference.

## Preliminary Groupings

### Group A: Incomplete propagation of 6-member team composition

- Finding 1, Finding 2 -- same underlying issue
- **Root cause**: When ant-farm-7hgn added Pest Control as a team member, the change was propagated to RULES.md Step 3b, reviews.md Nitpicker Checklist, and Big Head Consolidation Checklist -- but the reviews.md Team Setup section (lines 53-71) and big-head-skeleton.md TeamCreate example (lines 23-38) were not updated. These are the two primary references the Queen uses when constructing the actual TeamCreate call.
- **Suggested combined fix**: Update both files to reflect 6 members and include Pest Control in all team composition examples and descriptions.

### Group B: SendMessage pseudo-API inconsistency

- Finding 3, Finding 4 -- same underlying issue
- **Root cause**: The SendMessage instructions across templates use different conventions (natural language vs pseudo-API with wrong parameter names) rather than consistent, correct parameter names.
- **Suggested combined fix**: Standardize all SendMessage examples to use the actual tool parameter names (`type`, `recipient`, `content`, `summary`).

### Group C: Stale cross-reference after content insertion

- Finding 5 -- standalone
- **Root cause**: The ant-farm-7hgn commit inserted ~38 new lines (Step 4 checkpoint gate) into reviews.md before the consolidated summary section, shifting all subsequent content downward, but RULES.md line 113 still references the pre-shift line numbers.

## Summary Statistics
- Total findings: 5
- By severity: P1: 0, P2: 3, P3: 2
- Preliminary groups: 3

## Cross-Review Messages

### Sent
- To edge-cases-reviewer: "Confirmed team count inconsistency already captured as Findings 1 and 2" -- Action: Acknowledged overlap, no action needed from edge-cases reviewer on correctness angle.
- To clarity-reviewer: "Confirmed finding 1, added stale line ref as Finding 5" -- Action: Acknowledged team count overlap; confirmed stale line reference verified and added.
- To excellence-reviewer: "Confirmed 5-member config breaks SendMessage pipeline" -- Action: Confirmed runtime impact analysis; noted reviews.md:33 as additional surface under same root cause.

### Received
- From edge-cases-reviewer: "Team member count inconsistency in reviews.md lines 53/56 vs 573 and RULES.md 98" -- Action taken: Already captured as Finding 1 (P2); confirmed coverage.
- From clarity-reviewer: "Team count mismatch (same as above) + stale line reference in RULES.md:113 pointing to L485-514 instead of L609-629" -- Action taken: Team count already captured; stale line reference verified and added as Finding 5 (P2).
- From excellence-reviewer: "Team member count contradiction in reviews.md lines 33/53/56 and big-head-skeleton.md lines 28-37; asked for runtime impact verification" -- Action taken: Already captured as Findings 1 and 2 (P2); confirmed that 5-member team would break Big Head's SendMessage to Pest Control, stalling the entire consolidation pipeline. Noted reviews.md:33 as additional affected surface under Group A.

### Deferred Items
- None.

## Coverage Log

List every in-scope file with its review status. Files with no findings MUST still appear here -- omission is not acceptable.

| File | Status | Evidence |
|------|--------|----------|
| `/Users/correy/projects/ant-farm/orchestration/templates/reviews.md` | Findings: #1, #4 | 667 lines, full file read; Team Setup section (L49-73), polling loop (L364-397), error return (L399-438), Step 4 checkpoint gate (L523-559), checklists (L561-586) examined against acceptance criteria |
| `/Users/correy/projects/ant-farm/orchestration/templates/big-head-skeleton.md` | Findings: #2, #3 | 77 lines, full file read; Queen instructions (L1-48), agent-facing template (L50-77) examined; TeamCreate example (L27-38) cross-referenced with RULES.md and reviews.md |
| `/Users/correy/projects/ant-farm/orchestration/templates/pantry.md` | Reviewed -- no issues | 289 lines, full file read; Section 2 Step 4 (L244-255) correctly updated with Pest Control coordination note and bead filing gate reference |
| `/Users/correy/projects/ant-farm/orchestration/RULES.md` | Findings: #5 | 248 lines, full file read; Step 3b (L89-106) correctly updated to 6 members with Pest Control rationale; Hard Gates table (L123-132) unchanged and consistent; Step 3c (L113) stale line reference found |

## Overall Assessment
**Score**: 6/10
**Verdict**: PASS WITH ISSUES
<!-- Verdict Rubric:
  PASS           = 0 P1 findings AND 0 P2 findings
  PASS WITH ISSUES = 0 P1 findings AND any P2 or P3 findings
  NEEDS WORK     = any P1 finding present

  Score formula: Start at 10, subtract 3 per P1, 1 per P2, 0.5 per P3 (floor at 0)
  10 - 0(P1) - 3(P2) - 2*0.5(P3) = 10 - 3 - 1 = 6
-->
The core logic changes (polling loop fix, tilde fence fix, authority designation, checkpoint gate) are all correctly implemented. However, the 6-member team composition was incompletely propagated: the two primary Queen-facing references (reviews.md Team Setup and big-head-skeleton.md TeamCreate example) still show 5 members without Pest Control, which would cause Big Head's SendMessage to Pest Control to fail at runtime. Additionally, the content insertion from ant-farm-7hgn shifted line numbers in reviews.md without updating the cross-reference in RULES.md Step 3c (line 113), which now points the Queen to the consolidated summary template instead of the fix workflow. The P3 findings are minor polish on SendMessage parameter naming conventions.

# Report: Edge Cases Review

**Scope**: orchestration/templates/reviews.md, orchestration/templates/big-head-skeleton.md, orchestration/templates/pantry.md, orchestration/RULES.md
**Reviewer**: Edge Cases Review (code-reviewer)

## Findings Catalog

### Finding 1: Team member count inconsistency -- reviews.md says 5 members but checklist says 6

- **File(s)**: /Users/correy/projects/ant-farm/orchestration/templates/reviews.md:53, /Users/correy/projects/ant-farm/orchestration/templates/reviews.md:56, /Users/correy/projects/ant-farm/orchestration/templates/reviews.md:573
- **Severity**: P2
- **Category**: edge-case
- **Description**: The Team Setup section at line 53 states "The Queen creates the Nitpicker team with **5 members** (4 reviewers + Big Head)" and line 56 says "Create a team with these 5 members." However, the Nitpicker Checklist at line 573 (added by commit 46a776a) now says "Team has 6 members: 4 Nitpickers + Big Head + Pest Control." The team setup example block at lines 55-71 only lists 5 members (no Pest Control member in the example). RULES.md line 98 also says 6 members. This means the Team Setup section was not updated to match the new 6-member team architecture. An agent reading the Team Setup section top-to-bottom would create a 5-member team without Pest Control, breaking the Big Head -> Pest Control SendMessage flow that the new Step 4 checkpoint gate depends on.
- **Suggested fix**: Update line 53 to "6 members (4 reviewers + Big Head + Pest Control)" and line 56 to "Create a team with these 6 members." Add a 6th entry to the example member list for Pest Control. Also update the intro paragraph at line 33 to mention Pest Control as a team member.
- **Cross-reference**: Correctness reviewer should verify acceptance criteria for ant-farm-7hgn -- this may be an incomplete implementation of the Pest Control team membership requirement.

### Finding 2: Polling loop uses unsubstituted `<session-dir>` placeholder in bash code

- **File(s)**: /Users/correy/projects/ant-farm/orchestration/templates/reviews.md:379-382
- **Severity**: P3
- **Category**: edge-case
- **Description**: The polling loop bash code uses `<session-dir>` as a literal placeholder in the `ls` commands (e.g., `ls <session-dir>/review-reports/clarity-review-*.md`). This is consistent with the rest of the template -- these are instructional placeholders meant for Big Head to substitute at runtime. However, there is no explicit instruction in the polling loop section telling Big Head to replace `<session-dir>` with the actual session directory path before execution. The Step 0 section at line 342 uses the same pattern, so the convention is established. This is low-risk because Big Head reads the full consolidation brief which includes actual paths, and the brief is declared authoritative. Noting for completeness.
- **Suggested fix**: No action required -- the convention is consistent and the brief contains concrete paths. If desired, a single-line note like "Replace `<session-dir>` with the actual session directory path" could be added before the code block for extra clarity.

### Finding 3: No timeout or error handling for Pest Control response in Step 4

- **File(s)**: /Users/correy/projects/ant-farm/orchestration/templates/reviews.md:525-535
- **Severity**: P2
- **Category**: edge-case
- **Description**: Step 4 instructs Big Head to "Wait for Pest Control reply" after sending the SendMessage, but specifies no timeout or fallback. If Pest Control crashes, gets stuck, or fails to reply, Big Head will wait indefinitely. The missing-report handling in Step 0a has an explicit 30-second timeout and error return protocol, but Step 4 has no equivalent. Since Big Head and Pest Control are team members, if Pest Control's agent process dies, Big Head may hang forever waiting for a message that never arrives.
- **Suggested fix**: Add a timeout specification for the Pest Control reply (e.g., 60 seconds) and an error return protocol similar to Step 0a. On timeout, Big Head should escalate to the Queen with a message like "Pest Control did not respond within timeout. Consolidated report is at <path>. Queen must decide: re-spawn Pest Control, or proceed without checkpoint validation."

### Finding 4: No timeout for Pest Control response in big-head-skeleton.md step 9

- **File(s)**: /Users/correy/projects/ant-farm/orchestration/templates/big-head-skeleton.md:68-70
- **Severity**: P2
- **Category**: edge-case
- **Description**: The skeleton template step 9 says "Await Pest Control verdict" with branching on PASS/FAIL, but provides no guidance on what to do if Pest Control never replies. This mirrors Finding 3 -- the skeleton and the authoritative reviews.md both lack a timeout for this interaction. Since the skeleton defers to the brief for Step 0a handling, the brief should also be authoritative for Step 4 timeout behavior, but neither document addresses it.
- **Suggested fix**: Same as Finding 3 -- add timeout handling in reviews.md Step 4 (the authoritative source), and optionally add a brief note in the skeleton step 9 deferring to the brief for timeout behavior.

### Finding 5: SendMessage example uses pseudocode syntax, not actual tool call format

- **File(s)**: /Users/correy/projects/ant-farm/orchestration/templates/reviews.md:528-532
- **Severity**: P3
- **Category**: edge-case
- **Description**: The SendMessage example in Step 4 uses a pseudocode format: `SendMessage(to="pest-control", message="...")`. The actual Claude Code SendMessage tool uses parameters like `recipient` and `content`, not `to` and `message`. If Big Head follows this literally, the tool call would fail. However, LLMs typically understand the intent and translate to the correct parameter names, making this a low-risk cosmetic issue.
- **Suggested fix**: Update the pseudocode to use the actual parameter names (`recipient` instead of `to`, `content` instead of `message`) for precision. Or add a note that this is pseudocode showing the intent.

### Finding 6: Big Head escalation format on FAIL uses plain fenced code block without language specifier

- **File(s)**: /Users/correy/projects/ant-farm/orchestration/templates/reviews.md:540-547
- **Severity**: P3
- **Category**: edge-case
- **Description**: The escalation format template block at lines 540-547 is inside a plain fenced code block (triple backtick with no language). This is nested inside a markdown document that itself uses fenced code blocks. While the tilde-fence fix from commit cba88a6 addressed a similar nesting issue in the re-spawn instruction at lines 427-429, this escalation block could face the same premature-closure problem if a downstream consumer embeds it in another fenced block context. Currently, the outer context uses triple backticks at line 540, and the inner content has no nested fences, so there is no immediate breakage. Low risk.
- **Suggested fix**: No immediate action needed. If future edits add nested fenced blocks inside this escalation template, consider switching to tilde fences for consistency with the fix applied at lines 427-429.

## Preliminary Groupings

### Group A: Missing timeout for Pest Control reply

- Finding 3, Finding 4 -- both describe the same gap: no timeout or error-return protocol when Big Head awaits Pest Control's checkpoint verdict. Finding 3 is in reviews.md (the authoritative source), Finding 4 is in big-head-skeleton.md (which defers to the brief).
- **Suggested combined fix**: Add a timeout specification and error-return protocol to reviews.md Step 4 (the authoritative location). Optionally add a cross-reference in big-head-skeleton.md step 9 noting that timeout behavior is defined in the brief.

### Group B: Team member count not updated in Team Setup section

- Finding 1 -- standalone. The checklist and RULES.md were updated to 6 members but the Team Setup prose and example were not.

### Group C: Low-risk template polish

- Finding 2, Finding 5, Finding 6 -- cosmetic issues in template formatting and placeholder conventions. None affect runtime behavior under normal conditions.

## Summary Statistics

- Total findings: 6
- By severity: P1: 0, P2: 3, P3: 3
- Preliminary groups: 3

## Cross-Review Messages

### Sent

- To correctness-reviewer: "reviews.md Team Setup section (lines 53, 56) still says 5 members, but Nitpicker Checklist (line 573) and RULES.md (line 98) say 6 members. This may be an incomplete implementation of the Pest Control team membership requirement from ant-farm-7hgn. Please check against the acceptance criteria." -- Action: Asked correctness reviewer to verify acceptance criteria compliance for the team count change.

### Received

- (None received at time of report writing.)

### Deferred Items

- (None.)

## Coverage Log

| File | Status | Evidence |
|------|--------|----------|
| /Users/correy/projects/ant-farm/orchestration/templates/reviews.md | Findings: #1, #2, #3, #5, #6 | 660 lines examined; polling loop, Step 4 checkpoint gate, team setup, checklists, escalation format reviewed |
| /Users/correy/projects/ant-farm/orchestration/templates/big-head-skeleton.md | Findings: #4 | 77 lines examined; skeleton workflow steps 1-9, placeholder wiring instructions reviewed |
| /Users/correy/projects/ant-farm/orchestration/templates/pantry.md | Reviewed -- no issues | 289 lines, 3 sections (impl mode, review mode, error handling) examined; Step 4 cross-reference update and bead filing note verified as consistent with reviews.md changes |
| /Users/correy/projects/ant-farm/orchestration/RULES.md | Reviewed -- no issues | 248 lines examined; Step 3b updated to 6 members with Pest Control rationale, consistent with reviews.md checklist; no edge-case issues found in changed lines |

## Overall Assessment

**Score**: 7/10
**Verdict**: PASS WITH ISSUES

Three P2 findings identified: a team member count inconsistency between the Team Setup section and the updated checklist/RULES.md (Finding 1), and a missing timeout protocol for the Pest Control checkpoint reply (Findings 3 and 4). The count inconsistency is the most likely to cause an actual runtime failure -- an agent following the Team Setup example would create a 5-member team without Pest Control, breaking the new bead-filing checkpoint gate. The missing timeout is a latent hang risk if Pest Control fails silently. The P3 findings are cosmetic.

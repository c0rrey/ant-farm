# Report: Excellence Review

**Scope**: orchestration/RULES.md, orchestration/templates/big-head-skeleton.md, orchestration/templates/checkpoints.md, orchestration/templates/nitpicker-skeleton.md, orchestration/templates/pantry.md, orchestration/templates/queen-state.md, orchestration/templates/reviews.md
**Reviewer**: excellence / code-reviewer

---

## Findings Catalog

### Finding 1: Shell variable persistence warning is doc-only, not enforced

- **File(s)**: orchestration/templates/reviews.md:447
- **Severity**: P3
- **Category**: excellence
- **Description**: The polling loop comment `# IMPORTANT: This entire block must execute in a single Bash invocation. # Shell state (variables) does not persist across separate Bash tool calls.` is correct and critical, but it appears only in a comment inside a code block. If a future author copies this pattern and forgets the constraint, the silent failure will be hard to debug. The comment could be elevated to a surrounding prose warning (outside the code block) to make it more visible during document scanning.
- **Suggested fix**: Add a bold admonition above the code block: `**IMPORTANT**: Execute this entire polling loop in a single Bash invocation. Shell variables do not persist across separate Bash tool calls.`
- **Cross-reference**: Potentially relevant to edge-cases reviewer (runtime failure if the loop is split).

---

### Finding 2: Sentinel variable TIMED_OUT initialised to 1 (non-zero) — misleading default

- **File(s)**: orchestration/templates/reviews.md:452
- **Severity**: P3
- **Category**: excellence
- **Description**: The polling loop initialises `TIMED_OUT=1` (timed out by default) and sets it to `0` only on success. While functionally correct, this is a non-idiomatic shell pattern that reads as "we timed out before we even started." The conventional idiom is to initialise to `0` (success default) and flip to `1` on failure. The current inversion means every future reader must mentally invert the boolean, increasing cognitive load.
- **Suggested fix**: Rename to `ALL_REPORTS_FOUND=0` and set to `1` on success, then check `if [ $ALL_REPORTS_FOUND -eq 0 ]` for the error path. This aligns with standard shell conventions.
- **Cross-reference**: None.

---

### Finding 3: Magic number 2 (POLL_INTERVAL) and 30 (TIMEOUT) undocumented

- **File(s)**: orchestration/templates/reviews.md:449-450
- **Severity**: P3
- **Category**: excellence
- **Description**: `TIMEOUT=30` and `POLL_INTERVAL=2` are bare magic numbers with no explanation of why these specific values were chosen. If network latency or model startup time changes (e.g., a slow model takes 45s to produce output), these limits will fail silently. Documenting the rationale (e.g., "30s accounts for typical model startup + report generation time") helps future maintainers make informed adjustments.
- **Suggested fix**: Add inline comments: `TIMEOUT=30     # seconds: allow for model startup + report generation` and `POLL_INTERVAL=2  # seconds: balance responsiveness against busy-wait overhead`.
- **Cross-reference**: None.

---

### Finding 4: Retry limit of 1 in Big Head escalation path is inconsistent with RULES.md

- **File(s)**: orchestration/templates/reviews.md:634-643, orchestration/RULES.md:230-234
- **Severity**: P3
- **Category**: excellence
- **Description**: `reviews.md` specifies Big Head retries once on Pest Control timeout (send + one retry = 2 attempts). RULES.md specifies `CCB fails → 1 retry`. These are different checkpoints (Big Head SendMessage timeout vs. CCB FAIL), but the asymmetry is not documented. If a reader looks at RULES.md retry limits they may conclude "1 retry" covers everything and miss the double-attempt in reviews.md. A cross-reference note in RULES.md Retry Limits table would help.
- **Suggested fix**: Add a footnote to the RULES.md Retry Limits table: "Note: Big Head's SendMessage to Pest Control has its own 2-attempt protocol (see reviews.md Step 4)."
- **Cross-reference**: None.

---

### Finding 5: `<IF ROUND 1>` pseudo-comment is not valid shell and may confuse implementers

- **File(s)**: orchestration/templates/reviews.md:469-473
- **Severity**: P3
- **Category**: excellence
- **Description**: The polling loop template contains `# <IF ROUND 1>` / `# </IF ROUND 1>` comments as round-conditional markers. These are pseudo-templating syntax embedded in a shell code block. Because Pantry is supposed to adapt this code per round, leaving the markers in as guidance is intentional — but a reader could mistake them for valid shell comments and copy them verbatim, producing a script with dangling XML-like comments that, while harmless, are confusing. The prose below the block (`Pantry responsibility: ...`) explains this, but the markers themselves could use a clearer naming convention.
- **Suggested fix**: Rename to `# PANTRY INSERTS BELOW ONLY FOR ROUND 1:` and `# END PANTRY ROUND 1 BLOCK` to make the templating instruction unambiguous.
- **Cross-reference**: None.

---

### Finding 6: `bd list --status=open | grep -i "future work"` is fragile pattern

- **File(s)**: orchestration/templates/reviews.md:683, orchestration/templates/big-head-skeleton.md:94
- **Severity**: P3
- **Category**: excellence
- **Description**: Both files show `bd list --status=open | grep -i "future work"` as the method for finding the Future Work epic. This is fragile: if the epic title contains a typo ("Futire Work"), has extra whitespace, or if `bd list` output format changes, the grep silently returns empty and the fallback `bd epic create` creates a duplicate epic. There is no deduplication guard (e.g., checking if 0 or 2+ results are returned).
- **Suggested fix**: Add an explicit count guard: `COUNT=$(bd list --status=open | grep -ci "future work"); if [ $COUNT -gt 1 ]; then echo "WARNING: multiple Future Work epics found"; fi`. Or, prefer `bd epic list` if that command provides cleaner output.
- **Cross-reference**: Relevant to edge-cases reviewer (duplicate epic creation).

---

### Finding 7: Big Head timeout escalation does not specify where to send the escalation message

- **File(s)**: orchestration/templates/reviews.md:643-651, orchestration/templates/big-head-skeleton.md:89-92
- **Severity**: P3
- **Category**: excellence
- **Description**: When Pest Control is unavailable after 2 attempts, the protocol says "escalate to the Queen immediately" but does not specify the mechanism. Big Head is a team member — it cannot directly message the Queen. Presumably this escalation should go via `SendMessage` to the team lead or via the standard output, but neither file specifies this. A reader implementing Big Head must guess.
- **Suggested fix**: Add to the timeout escalation section: "Send escalation via `SendMessage` to the team-lead, or write the error to `{CONSOLIDATED_OUTPUT_PATH}-BLOCKED.md` and return it as your final output so the Queen sees it when reading the team's output."
- **Cross-reference**: None.

---

### Finding 8: `queen-state.md` uses `<angle-bracket>` placeholder syntax inconsistently

- **File(s)**: orchestration/templates/queen-state.md:1-47 (all lines)
- **Severity**: P3
- **Category**: excellence
- **Description**: `queen-state.md` uses `<angle-bracket text>` for placeholder values (e.g., `<timestamp>`, `<session-id>`, `<name>`). The Pantry's contamination check (pantry.md:57) explicitly flags `<angle-bracket text>` as contamination markers that should not survive into composed artifacts. If the Queen copies this template verbatim into a session state file (as intended), the file will have unfilled placeholders, and any future automated check for `<angle-bracket>` patterns will generate false-positive contamination alerts.
- **Suggested fix**: Either (a) document at the top of queen-state.md that these brackets are template placeholders, not contamination, and exclude this file from automated placeholder checks, or (b) switch to `{UPPERCASE_CURLY}` placeholders to match the convention used in other templates (pantry.md, reviews.md, etc.).
- **Cross-reference**: Potentially relevant to clarity reviewer (consistency finding).

---

### Finding 9: `nitpicker-skeleton.md` has no fallback if `{DATA_FILE_PATH}` is missing or empty

- **File(s)**: orchestration/templates/nitpicker-skeleton.md:23
- **Severity**: P3
- **Category**: excellence
- **Description**: The Nitpicker is instructed to "Read your full review brief from {DATA_FILE_PATH}" with no failure path specified. If the Pantry fails to write the brief, or the path is wrong, the Nitpicker will either error or proceed without context — in either case, the Queen receives no signal. The Pantry does have a fail-fast check (pantry.md:30-42), but the Nitpicker itself has no recovery logic.
- **Suggested fix**: Add a step: "If the brief file does not exist or is empty, STOP immediately and return: `BLOCKED: Brief file not found at {DATA_FILE_PATH}. Cannot proceed without review context.`"
- **Cross-reference**: None.

---

### Finding 10: RULES.md `Session Directory` section lists `queen-state.md` as a session artifact but does not create it in the `mkdir` command

- **File(s)**: orchestration/RULES.md:177-192
- **Severity**: P3
- **Category**: excellence
- **Description**: The `mkdir -p` command at Step 0 creates subdirectories `{task-metadata,previews,prompts,pc,summaries}`. The subsequent prose lists `queen-state.md` and `HANDOFF-*.md` as artifacts that go in the session directory root, but there is no template instantiation step specified for `queen-state.md`. A new Queen reading RULES.md would know they need the state file but not know when or how to create it. The Template Lookup table (line 224) does list `queen-state.md` but does not say to create it during Step 0.
- **Suggested fix**: Add to Step 0: "Create the Queen's session state file by copying `orchestration/templates/queen-state.md` to `{SESSION_DIR}/queen-state.md` and filling in Session ID and start timestamp."
- **Cross-reference**: None.

---

### Finding 11: `checkpoints.md` CCB Check 7 uses `bd list --status=open` to find unauthorized beads — this is O(N) over all open beads

- **File(s)**: orchestration/templates/checkpoints.md:543-548
- **Severity**: P3
- **Category**: excellence
- **Description**: CCB Check 7 instructs Pest Control to run `bd list --status=open` and cross-reference against the consolidated summary. As the bead database grows, this is an O(N) scan across all open beads regardless of age or scope. For a large project with hundreds of open beads, this becomes slow and produces noisy output that must be manually filtered. The check could be scoped to beads created since the session started.
- **Suggested fix**: Filter by creation date: `bd list --status=open --created-after=<session-start-timestamp>` (if the `bd` CLI supports it), or cross-reference only the bead IDs that appear in the consolidated summary rather than scanning all open beads.
- **Cross-reference**: None.

---

### Finding 12: `pantry.md` Section 3 is brief and asymmetric with Section 1 and 2

- **File(s)**: orchestration/templates/pantry.md:311-316
- **Severity**: P3
- **Category**: excellence
- **Description**: Section 3 (Error Handling) has only two bullet points, while Sections 1 and 2 have detailed multi-step protocols. The error handling is underspecified: "On any unrecoverable error: return a partial file path table" does not define what constitutes an "unrecoverable error" vs. a recoverable one, nor does it specify what the Queen should do with the partial table. This asymmetry makes the error path easy to miss during implementation.
- **Suggested fix**: Expand Section 3 with at least: (a) examples of recoverable vs. unrecoverable errors, (b) a sentence specifying that the Queen should re-run Pantry for failed tasks only (not the full batch), and (c) a note that partial progress is preserved per the "write each brief immediately" rule above.
- **Cross-reference**: None.

---

## Preliminary Groupings

### Group A: Inconsistent placeholder syntax creating confusion and false-positive risk
- Finding 8 — `queen-state.md` uses `<angle-bracket>` placeholders, other templates use `{UPPERCASE_CURLY}`
- **Root cause**: No documented placeholder syntax convention applied consistently across all templates
- **Suggested combined fix**: Adopt `{UPPERCASE_CURLY}` syntax universally; add a brief "Placeholder Conventions" note at the top of RULES.md or in a shared reference file.

### Group B: Shell script robustness in embedded code templates
- Finding 1 — critical constraint buried in comment
- Finding 2 — non-idiomatic sentinel variable
- Finding 3 — magic numbers without rationale
- Finding 5 — pseudo-syntax `<IF ROUND 1>` markers
- **Root cause**: Shell code blocks in documentation are treated as prose rather than as executable code artifacts, so best practices (comments, naming, documentation) are not applied consistently.
- **Suggested combined fix**: Establish a "Shell Code Block Review Checklist" for orchestration templates: (a) no magic numbers without comments, (b) idiomatic boolean sentinels, (c) constraints elevated to prose, (d) conditional markers use unambiguous naming.

### Group C: Incomplete failure paths in agent protocols
- Finding 7 — Big Head escalation mechanism unspecified
- Finding 9 — Nitpicker has no fallback for missing brief
- Finding 12 — Pantry Section 3 underspecified
- **Root cause**: Failure paths receive less design attention than success paths; each agent template documents the happy path thoroughly but leaves error branches underspecified.
- **Suggested combined fix**: Add a mandatory "Failure Paths" subsection to each agent template, mirroring the level of detail given to the success path. Minimum: trigger condition, escalation mechanism, recipient, and artifact to write.

### Group D: Cross-file consistency / stale cross-references
- Finding 4 — retry count asymmetry between RULES.md and reviews.md
- Finding 6 — fragile grep pattern duplicated in two files
- **Root cause**: Patterns implemented in reviews.md are independently maintained in big-head-skeleton.md, with no single source of truth. Changes in one file may not propagate to the other.
- **Suggested combined fix**: For the grep pattern, define the "Future Work" epic discovery pattern once (in reviews.md) and reference it from big-head-skeleton.md. For retry counts, add cross-reference notes so they stay in sync.

### Group E: Session state bootstrapping gap
- Finding 10 — queen-state.md creation not included in Step 0
- **Root cause**: RULES.md Step 0 defines directory setup but not state file initialisation, leaving an implied step undocumented.
- **Suggested combined fix**: Add explicit state file creation to Step 0.

### Group F: Scalability concern
- Finding 11 — O(N) bead scan in CCB Check 7
- **Root cause**: Checkpoint design assumes a small bead database; no session-scoping applied to expensive list operations.
- **Suggested combined fix**: Scope the CCB bead scan to session-created beads only.

---

## Summary Statistics
- Total findings: 12
- By severity: P1: 0, P2: 0, P3: 12
- Preliminary groups: 6

---

## Cross-Review Messages

### Sent
- To clarity-reviewer: "Finding 8 (queen-state.md placeholder syntax inconsistency) may overlap with your consistency domain — I'm flagging it as P3 excellence; worth noting if you see it too." — Action: Flagged for potential deduplication.
- To edge-cases-reviewer: "Finding 6 (fragile grep for Future Work epic) could produce a duplicate-epic edge case — flagging in case you haven't already covered it." — Action: Flagged for potential deduplication.

### Received
- None at time of writing.

### Deferred Items
- None — all findings fall within excellence scope.

---

## Coverage Log

| File | Status | Evidence |
|------|--------|----------|
| orchestration/RULES.md | Findings: #4, #10 | 254 lines, 12 sections examined: Queen Prohibitions, Read Permissions, Workflow Steps 0-6, Hard Gates, Information Diet, Agent Types, Concurrency Rules, Session Directory, Anti-Patterns, Template Lookup, Retry Limits, Priority Calibration, Context Preservation Targets |
| orchestration/templates/big-head-skeleton.md | Findings: #6, #7 | 105 lines, 4 sections: Instructions for Queen, Wiring/TeamCreate, Template (agent-facing), Steps 0-10 in agent-facing text |
| orchestration/templates/checkpoints.md | Findings: #11 | 571 lines, 5 checkpoint types reviewed: CCO (Dirt Pushers + Nitpickers), WWD, DMVDC (Dirt Pushers + Nitpickers), CCB — all verdict thresholds, check definitions, and Queen response sections examined |
| orchestration/templates/nitpicker-skeleton.md | Findings: #9 | 42 lines, 2 sections: Instructions for Queen (placeholder definitions), Template (agent-facing text) — all 5 workflow steps and 6 report section requirements examined |
| orchestration/templates/pantry.md | Findings: #12 | 316 lines, 3 sections: Implementation Mode (Steps 1-5), Review Mode (Steps 1-6), Error Handling — all fail-fast checks, task brief format, session summary format, and return tables examined |
| orchestration/templates/queen-state.md | Findings: #8 | 47 lines, 8 sections: session metadata, Scout table, Agent Registry, Pantry table, Pest Control table, Review Rounds, Queue Position, Error Log — all placeholders examined |
| orchestration/templates/reviews.md | Findings: #1, #2, #3, #4, #5, #6, #7 | 830 lines, all major sections reviewed: Transition Gate Checklist, Agent Teams Protocol, Round-Aware Protocol, 4 review types, Nitpicker Report Format, Big Head Consolidation Protocol (Steps 0-4, P3 Auto-Filing), Queen's Checklists, After Consolidation, Step 3c User Triage, Handle P3 Issues, Review Quality Metrics |

---

## Overall Assessment
**Score**: 8.5/10
**Verdict**: PASS WITH ISSUES

The orchestration templates are well-structured, thorough, and demonstrate strong architectural thinking. All 12 findings are P3 polish items. The primary excellence opportunities are: elevating the shell script quality in embedded code blocks (consistent idioms, documented magic numbers, unambiguous conditional markers), standardising placeholder syntax across all templates (queen-state.md is the outlier), and adding explicit failure-path subsections to agent templates to match the detail level of the success paths. No blocking issues found.

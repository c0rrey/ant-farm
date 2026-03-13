# Report: Excellence Review

**Scope**: AGENTS.md, agents/pantry-review.md, orchestration/RULES.md, orchestration/templates/pantry.md, orchestration/templates/reviews.md
**Reviewer**: Excellence Review (code-reviewer)

## Findings Catalog

### Finding 1: Deprecated Section 2 retained in pantry.md — dead weight in an active instruction file

- **File(s)**: `/Users/correy/projects/ant-farm/orchestration/templates/pantry.md:251-447`
- **Severity**: P3
- **Category**: excellence
- **Description**: Section 2 ("Review Mode") spans nearly 200 lines and opens with a prominent DEPRECATED notice (`> **DEPRECATED**: Section 2 (Review Mode) is superseded...`). The section is retained "for reference only" but the Pantry agent is actively instructed to follow its workflow steps. Any agent reading this file will encounter the section, must parse the deprecation notice, and must decide to skip it — adding cognitive load with no upside. Deprecated content in an actively-used instruction file is a maintainability liability: it will accumulate drift as Section 1 evolves, and future maintainers will face uncertainty about whether partial sub-sections still apply.
- **Suggested fix**: Move deprecated Section 2 to `orchestration/_archive/pantry-section2-review-mode.md` with a header noting when and why it was superseded, and replace the block in pantry.md with a single-line pointer: `# Section 2: REMOVED — see _archive/pantry-section2-review-mode.md`. This keeps the file lean and authoritative.
- **Cross-reference**: Overlaps with clarity domain (dead code clarity). Not deferring; the excellence angle is maintainability cost of retaining deprecated content in an actively-read agent file.

---

### Finding 2: CCO Self-Validation checklist items are binary pass/fail with no guidance on remediation

- **File(s)**: `/Users/correy/projects/ant-farm/agents/pantry-review.md:57-71`
- **Severity**: P3
- **Category**: excellence
- **Description**: The Self-Validation Checklist at the bottom of pantry-review.md has 10 items written as `- [ ] ...` with no indication of what the agent should do if a check fails — other than the trailing line "fix the file before returning." This is vague. An agent failing check 3 ("Commit range is identical across all 4 review files") doesn't know whether to re-read templates, re-compose all 4 files from scratch, or patch only the differing file. Contrast this with the much more explicit failure handling in pantry.md Section 1 Steps 2 fail-fast conditions, where each failure condition maps to a specific artifact path and a recovery instruction. The quality bar is inconsistent between these two files.
- **Suggested fix**: For each checklist item, add a parenthetical or inline note for the common remediation. Example: `- [ ] Commit range is identical across all 4 review files (if not: re-read commit-range from Queen's input and patch the differing files)`. This brings pantry-review.md up to the same quality bar as pantry.md Section 1.
- **Cross-reference**: None.

---

### Finding 3: `pantry-review.md` agent instructions reference "Queen's input" without specifying the delivery mechanism

- **File(s)**: `/Users/correy/projects/ant-farm/agents/pantry-review.md:12-14`
- **Severity**: P3
- **Category**: excellence
- **Description**: The file states "Your workflow is defined in the orchestration template the Queen points you to (pantry.md, Section 2)." But the file also notes Section 2 is deprecated and superseded by `fill-review-slots.sh`. If the pantry-review agent is no longer supposed to be invoked for a second pass (per RULES.md Step 3b and pantry.md Section 2 deprecation notice), the agent file still exists in `agents/` which means it is still registered and can still be accidentally spawned. The description field says "Use for Step 3b review cycles" — which contradicts the deprecation. An agent type that is registered but should not be used is a footgun. Either the agent type should be de-registered (file removed from `agents/`) or its description must be updated to say "DEPRECATED — do not spawn."
- **Suggested fix**: Update `agents/pantry-review.md` description to `DEPRECATED — do not spawn. Replaced by fill-review-slots.sh (see RULES.md Step 3b).` Alternatively, delete the agent file and update RULES.md Agent Types table to remove the deprecated strikethrough entry. The strikethrough-in-table approach in RULES.md is fragile — it depends on readers noticing and parsing markdown strikethrough, which is easy to miss.
- **Cross-reference**: Correctness reviewer should verify whether the RULES.md Agent Types table and Model Assignments table accurately reflect the deprecated/removed status (they use strikethrough formatting, not deletion).

---

### Finding 4: RULES.md Agent Types table uses strikethrough for deprecated entries — not machine-readable

- **File(s)**: `/Users/correy/projects/ant-farm/orchestration/RULES.md:180-182` and `/Users/correy/projects/ant-farm/orchestration/RULES.md:193-195`
- **Severity**: P3
- **Category**: excellence
- **Description**: Both the Agent Types and Model Assignments tables mark deprecated Pantry (review) entries using `~~strikethrough~~`. Strikethrough is a visual convention for human readers, not a machine-enforceable signal. An agent reading RULES.md to learn what agent types are available still sees `pantry-review` in the table — it just appears with strikethrough. If an agent processes tables by extracting rows, it may still act on the deprecated entry. A more architecturally robust pattern is to remove deprecated rows from the canonical tables and reference the archive location in a footnote.
- **Suggested fix**: Remove the `~~pantry-review~~` rows from both tables. Add a footnote or comment below each table: `<!-- Pantry (review) was deprecated in commit XXXX. Replaced by fill-review-slots.sh. See _archive/pantry-section2-review-mode.md for historical reference. -->`. This eliminates the ambiguity without losing history.
- **Cross-reference**: Linked to Finding 3. Same root cause: deprecated functionality not cleanly removed.

---

### Finding 5: `reviews.md` polling loop template uses comment-delimited conditional blocks (`<IF ROUND 1>`) — fragile templating convention

- **File(s)**: `/Users/correy/projects/ant-farm/orchestration/templates/reviews.md:528-532`
- **Severity**: P3
- **Category**: excellence
- **Description**: The Big Head polling loop uses `# <IF ROUND 1>` / `# </IF ROUND 1>` comment-style conditional markers. These are not standard shell conditional syntax — they are human-readable annotations that the Pantry is expected to interpret and transform when composing the Big Head brief. This is a fragile templating convention: (1) it requires the Pantry to reliably identify and strip/expand these blocks during composition; (2) there is no validation that the expansion was done correctly; (3) a future maintainer adding a Round 3+ conditional would need to invent a new comment convention. The note at line 548 confirms the Pantry is expected to adapt this block, but the adaptation logic is buried in prose rather than enforced by a structured template mechanism.
- **Suggested fix**: Consider using a named-section approach or providing two concrete, complete versions of the polling block (one for round 1, one for round 2+) and instructing the Pantry to pick the appropriate version rather than transform a conditional template. This eliminates the fragile comment-stripping step. If the comment convention must be retained, add an explicit validation step: "After expanding `<IF ROUND 1>` blocks, re-read the generated file and confirm no `<IF` or `</IF>` comment markers remain."
- **Cross-reference**: Edge-cases reviewer may want to check whether the Pantry's prompt for fill-review-slots.sh correctly handles round 2+ polling block generation.

---

### Finding 6: `reviews.md` Big Head Step 0 polling loop runs sleep in a Bash tool invocation — potential context/timeout issue

- **File(s)**: `/Users/correy/projects/ant-farm/orchestration/templates/reviews.md:506-540`
- **Severity**: P3
- **Category**: excellence
- **Description**: The polling loop includes `sleep $POLL_INTERVAL` (2-second intervals) within a loop that may run up to 30 seconds total. The comment at the top of the block correctly notes "This entire block must execute in a single Bash invocation." However, a 30-second sleep in a Bash tool call may hit the agent's bash timeout depending on platform configuration. More importantly, the polling approach (sleep + re-check) is appropriate only if another process can actually write the missing file while this sleep is running — which in a sequential agent context (not a parallel process) won't happen. The timeout/sleep approach is borrowed from multi-process coordination but doesn't map cleanly to an agent that is the only process running.
- **Suggested fix**: Add a brief note in the template explaining when the polling is useful (multi-agent team where reviewers are running concurrently) vs when it won't help (sequential fallback mode). This helps the Pantry and future maintainers understand the design intent and avoid generating the polling block in contexts where it adds latency with no benefit.
- **Cross-reference**: None.

---

### Finding 7: `AGENTS.md` and `CLAUDE.md` contain identical content — maintenance split hazard

- **File(s)**: `/Users/correy/projects/ant-farm/AGENTS.md:1-42`
- **Severity**: P3
- **Category**: excellence
- **Description**: `AGENTS.md` is identical in content to the project's `CLAUDE.md` (per the session context). Maintaining two files with identical content means any update requires remembering to update both. The comment in MEMORY.md confirms "CLAUDE.md — System prompt instructions (synced to ~/.claude/ via pre-push hook)" but makes no mention of AGENTS.md. If AGENTS.md is intended for non-Claude environments (e.g., Cursor, OpenAI agents), that purpose is undocumented. If it's just a copy, it's redundant and will drift.
- **Suggested fix**: Either (a) add a comment at the top of AGENTS.md explaining what environment it targets and how it's synced/updated, or (b) replace AGENTS.md with a symlink or script-generated copy if the content must stay in sync, or (c) delete AGENTS.md if it has no distinct consumer. At minimum, add a one-line header: `<!-- This file mirrors CLAUDE.md for non-Claude agent environments. Keep in sync manually or via pre-push hook. -->`.
- **Cross-reference**: None. This is a documentation/maintainability finding, not a correctness issue.

---

### Finding 8: No explicit lint/validation step for `fill-review-slots.sh` output in RULES.md Step 3b

- **File(s)**: `/Users/correy/projects/ant-farm/orchestration/RULES.md:106-114`
- **Severity**: P3
- **Category**: excellence
- **Description**: Step 3b-ii calls `fill-review-slots.sh` and notes "On exit 0: prompts/previews written." But the downstream CCO gate (Step 3b-iii) is the only validation. If the script exits 0 but produces malformed output (e.g., unfilled `{UPPERCASE}` placeholders due to a quoting bug in the script call), the Queen proceeds to CCO, which may or may not catch the malformation depending on what CCO checks. The pantry-review.md Self-Validation Checklist has an explicit "zero unfilled placeholders" check, but that was for the old Pantry-based flow. No equivalent explicit check exists for the new script-based flow before the CCO gate.
- **Suggested fix**: After the script exits 0, add a quick grep to verify no `{UPPERCASE}` placeholders remain in the generated preview files: `grep -rn '{[A-Z_]*}' "${SESSION_DIR}/previews/" && echo "UNFILLED PLACEHOLDERS" || echo "Clean"`. This makes the validation explicit and cheap, and catches the class of errors that would otherwise only surface at CCO review.
- **Cross-reference**: Edge-cases reviewer may want to verify what happens when `fill-review-slots.sh` exits 0 but writes empty files or partial output.

---

## Preliminary Groupings

### Group A: Deprecated content retained in active files
- Finding 1 (pantry.md Section 2 deprecated block)
- Finding 3 (pantry-review.md agent file still registered, description contradicts deprecation)
- Finding 4 (RULES.md strikethrough rows in canonical tables)

**Root cause**: Deprecation was done in-place (adding notices/strikethrough) rather than removing the deprecated artifacts. All three are the same pattern: deprecated functionality visually flagged but structurally still present, creating confusion for agents and maintainers.

**Suggested combined fix**: Archive Section 2 of pantry.md, delete or clearly mark agents/pantry-review.md as DEPRECATED-DO-NOT-SPAWN, and remove strikethrough rows from RULES.md tables (with archive footnotes).

---

### Group B: Brittle template conventions requiring Pantry interpretation
- Finding 5 (comment-delimited `<IF ROUND 1>` conditional in reviews.md polling loop)
- Finding 8 (no explicit placeholder validation after fill-review-slots.sh)

**Root cause**: The templating system relies on agents correctly interpreting informal conventions (comment-style conditionals, implicit placeholder validation) rather than enforcing them mechanically. Both findings represent places where the system assumes correct agent interpretation without a validation backstop.

**Suggested combined fix**: Add explicit validation steps after any template transformation — whether by the Pantry or via fill-review-slots.sh. Make template conditionals unambiguous (provide concrete round-1 and round-2+ versions rather than conditional markup).

---

### Group C: Standalone findings
- Finding 2 (pantry-review.md checklist lacks remediation guidance) — standalone
- Finding 6 (polling loop sleep in sequential context) — standalone
- Finding 7 (AGENTS.md / CLAUDE.md duplication) — standalone

---

## Summary Statistics
- Total findings: 8
- By severity: P1: 0, P2: 0, P3: 8
- Preliminary groups: 3
- Note: Findings 3 and 4 (pantry-review deprecation) were flagged to correctness-reviewer. Correctness reviewer elevated the combined issue to P2 (correctness Finding 10) covering out-of-scope files GLOSSARY.md and README.md. Big Head should merge excellence Findings 3+4 with correctness Finding 10 into one root-cause group.

---

## Cross-Review Messages

### Sent
- To correctness-reviewer: "Finding 3 and Finding 4 touch RULES.md Agent Types and Model Assignments tables — please verify whether the deprecated pantry-review rows cause any correctness issue in how agents parse or act on those tables. The strikethrough rows may be visible to agents as live entries." -- Action: correctness reviewer to check table parse fidelity for deprecated rows.

### Received
- From correctness-reviewer: "Elevated to P2 in correctness report (Finding 10). GLOSSARY.md:81 describes pantry-review as an active agent form with no deprecation marker; README.md:275 lists it live in the agent capabilities table; agents/pantry-review.md:3 gives a positive present-tense spawn instruction. A Queen consulting GLOSSARY.md before or alongside RULES.md has two sources saying live vs one saying deprecated. Strikethrough is not rendered as a warning to a model skimming a table; it reads as raw markdown and may not be parsed as a prohibition. Fix spans four locations: agents/pantry-review.md description, GLOSSARY.md:81, README.md:275, and the agent file body." -- Action taken: Updated Findings 3 and 4 notes (see below) to acknowledge the broader cross-file scope. Severity remains P3 in this report for the in-scope files; the correctness reviewer owns the P2 elevation covering GLOSSARY.md and README.md.

### Deferred Items
- "Polling loop sleep behavior in sequential context" (Finding 6) -- Could have edge-case dimension (what if sleep causes bash timeout?). Flagged but deferred to edge-cases reviewer for deeper analysis if they encounter it.
- "pantry-review deprecation correctness risk" (Findings 3, 4) -- Elevated to P2 by correctness-reviewer; the P2 elevation covers out-of-scope files (GLOSSARY.md, README.md). My in-scope findings (agents/pantry-review.md, RULES.md) remain P3 from the excellence domain perspective; Big Head should merge with correctness Finding 10 into a single root-cause group.

---

## Coverage Log

| File | Status | Evidence |
|------|--------|----------|
| AGENTS.md | Reviewed — 1 issue (Finding 7) | 42 lines, landing-the-plane workflow section, Quick Reference section — examined for duplication, maintainability, documentation gaps |
| agents/pantry-review.md | Reviewed — 2 issues (Finding 2, Finding 3) | 72 lines, YAML front matter, Quality Requirements, Self-Validation Checklist — examined for consistency, architecture fit, deprecated state |
| orchestration/RULES.md | Reviewed — 2 issues (Finding 4, Finding 8) | 296 lines, all sections including Queen Prohibitions, workflow steps, hard gates, agent tables, concurrency rules, session directory, anti-patterns, template lookup, retry limits, priority calibration, context preservation — examined throughout |
| orchestration/templates/pantry.md | Reviewed — 2 issues (Finding 1, Finding 3 upstream) | 454 lines, Sections 1–3 including all Steps — examined for deprecated content, template quality, architecture fit |
| orchestration/templates/reviews.md | Reviewed — 2 issues (Finding 5, Finding 6) | 890 lines, full file including transition gate, team setup, round-aware protocol, all review types, Big Head protocol, polling loop, bead filing, P3 auto-filing, queen checklists — examined throughout |

---

## Overall Assessment
**Score**: 8.0/10
**Verdict**: PASS WITH ISSUES

All 8 findings are P3 (polish/maintainability). No correctness or blocking issues found in the excellence domain. The primary improvement area is incomplete deprecation cleanup — deprecated content remains structurally present in active files, creating cognitive load and future drift risk. The templating conventions for round-conditional blocks could also be more explicit. The core orchestration logic, workflows, and quality gates are well-designed and internally consistent.

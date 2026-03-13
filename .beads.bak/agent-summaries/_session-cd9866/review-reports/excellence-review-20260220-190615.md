# Report: Excellence Review

**Scope**: 14 files changed in commit range f9ad7d9..HEAD
**Reviewer**: Excellence Review | nitpicker (sonnet)

---

## Findings Catalog

### Finding 1: Pre-commit hook silently swallows sync failures with wrong exit behavior
- **File(s)**: `scripts/install-hooks.sh:44-46`
- **Severity**: P2
- **Category**: excellence
- **Description**: The pre-push hook installed by `install-hooks.sh` treats a sync failure as a WARNING but still exits 0 (allowing the push to proceed). The comment says "push continuing without sync" — this means a failed sync is invisible to the developer. The `set -euo pipefail` at the top of the hook script would cause the hook to exit 1 on any unhandled failure, but the sync failure is explicitly suppressed with the `if !` block. This is an intentional design choice, but the tradeoff is undocumented and users may be surprised when pushes succeed despite failed syncs.
- **Suggested fix**: Either (a) add a comment in `install-hooks.sh` explaining why sync failures are non-fatal for push, or (b) exit 1 to make sync failures blocking. The current behavior is a silent degraded state — the docs say "after push, agents are updated" but that may not be true.
- **Cross-reference**: Clarity reviewer may want to note the missing rationale comment.

### Finding 2: `scrub-pii.sh` regex does not target only JSON field values
- **File(s)**: `scripts/scrub-pii.sh:35,50`
- **Severity**: P2
- **Category**: excellence
- **Description**: The PII pattern `[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}` is applied globally with `perl -i -pe` across ALL content in `issues.jsonl`. It does not scope replacement to specific JSON fields (`"owner"` and `"created_by"` as stated in the header comment on line 7). This means any email pattern appearing in a task title, description, or any other JSON field would also be replaced. The inverse is also true: if the email-like string is a legitimate domain or identifier (e.g., `user@example.com` in a URL within a description), it would be silently scrubbed without warning.
- **Suggested fix**: Scope the perl regex to target only the known PII-bearing JSON keys, e.g.:
  ```perl
  perl -i -pe 's/("owner"|"created_by"):\s*"[^"]*\K[a-zA-Z0-9._%+\-]+\@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}/ctc/g'
  ```
  This limits replacement to values of the `owner` and `created_by` fields specifically.

### Finding 3: `install-hooks.sh` installs a pre-commit hook that hard-errors when `scrub-pii.sh` is missing
- **File(s)**: `scripts/install-hooks.sh:74-77`
- **Severity**: P2
- **Category**: excellence
- **Description**: The installed pre-commit hook exits 1 (blocking all commits) when `scrub-pii.sh` is not found or not executable. This is a hard dependency — if the script is deleted, renamed, or has permissions reset (e.g., after a fresh clone without `chmod`), ALL commits are blocked until the script is restored. The installation guide recommends removing the hook as a cleanup step, but that still leaves the hard failure mode active for users who forget. There is no graceful degradation — the hook does not skip if the file is missing.
- **Suggested fix**: Add a comment in the installed hook documenting this hard dependency. Optionally, treat a missing `scrub-pii.sh` as a WARN (issue a warning but allow commit to continue) and separately document this in `docs/installation-guide.md` under Troubleshooting. The current behavior that blocks commits for a missing script is arguably too aggressive for an internal tooling script.
- **DEFERRED**: edge-cases-reviewer has already reported this as their Finding 1 (P2) with a more precise fix: the executable check at line 74-77 runs unconditionally before the staged-file guard at line 80, so the block affects ALL commits, not just issues.jsonl commits. Defer to their report — do NOT consolidate from this finding.

### Finding 4: `scrub-pii.sh` post-scrub verification uses inconsistent variable
- **File(s)**: `scripts/scrub-pii.sh:52-55`
- **Severity**: P3
- **Category**: excellence
- **Description**: The post-scrub verification at line 52 runs `grep -qE` to check if PII remains, then at line 53 runs `grep -cE` to count remaining occurrences. This runs the same grep twice on potentially large files. The second grep is inside the `if` block that only executes if the first grep found matches, but this is still a minor inefficiency. More importantly, line 53 stores the count in `REMAINING` but this variable is only used in the echo message — the exit code would be 1 regardless. A single grep with both `-q` and output capture would be cleaner.
- **Suggested fix**: Combine into one grep call with output capture, or use `REMAINING=$(grep -cE ... || true)` and test `[ "$REMAINING" -gt 0 ]`. Minor inefficiency, not a correctness issue.

### Finding 5: `orchestration/PLACEHOLDER_CONVENTIONS.md` Enforcement Strategy references optional grep validation that is never enforced
- **File(s)**: `orchestration/PLACEHOLDER_CONVENTIONS.md:203-207`
- **Severity**: P3
- **Category**: excellence
- **Description**: The "Enforcement Strategy" section (lines 203-207) lists "Run grep patterns as part of pre-push validation (optional, via git hook or CI)" as step 3. This is labeled optional and has never been implemented. The pre-push hook (installed by `install-hooks.sh`) only calls `sync-to-claude.sh` — it does NOT run any placeholder validation. The "Compliance Status: All Files Pass" section declares all files compliant, but there is no automated enforcement to catch future regressions. If a developer adds a new template with incorrect placeholder casing, nothing will catch it at commit/push time.
- **Suggested fix**: Either implement the grep validation in the pre-push hook, or update the enforcement strategy to remove the "(optional, via git hook)" language and make explicit that compliance is manual. The current wording creates a false impression of automated enforcement.

### Finding 6: `orchestration/templates/reviews.md` documents a deprecated Pantry spawn flow in README diagram
- **File(s)**: `README.md:174-197`
- **Severity**: P2
- **Category**: excellence
- **Description**: The README diagram in the "Step 3b: Quality review" section (lines 174-197) shows the Queen spawning Pantry in "review mode" — `"compose review prompts"` — and Pantry reading `reviews.md` to write 4 review briefs. However, `orchestration/templates/pantry.md` Section 2 has been marked DEPRECATED: "Section 2 is superseded by `scripts/fill-review-slots.sh`." The README diagram has not been updated to reflect this architectural change. Users reading the README will have an incorrect mental model of the review workflow.
- **Suggested fix**: Update the README Step 3b diagram to show the Queen calling `fill-review-slots.sh` directly, replacing the Pantry-review-mode spawn. Also update the "File reference" table at the bottom of README to mark `pantry-review` as deprecated (currently it notes DEPRECATED in the custom agents table but the workflow diagram still shows it).

### Finding 7: `orchestration/RULES.md` Step 3b-iv round composition comment inconsistency
- **File(s)**: `orchestration/RULES.md:171-177`
- **Severity**: P3
- **Category**: excellence
- **Description**: Step 3b-iv in `RULES.md` says "Round 1: 6 members — 4 reviewers + Big Head + Pest Control" and "Round 2+: 4 members — 2 reviewers (Correctness + Edge Cases) + Big Head + Pest Control." The `big-head-skeleton.md` file shows the same counts correctly. However, `reviews.md` Agent Teams Protocol section (line 66) says "the Queen creates the Nitpicker team with **6 members**" for round 1 and later "4 members" for round 2+. These are consistent. The minor issue is the phrasing "Correctness + Edge Cases" in RULES.md vs `reviews.md` which says "2 reviewers (Correctness, Edge Cases only — Clarity and Excellence are dropped)" — no contradiction, but "dropped" is not reflected in RULES.md's phrasing of "(Correctness + Edge Cases)". Minor wording inconsistency, not a correctness issue.
- **Suggested fix**: Align RULES.md Step 3b-iv phrasing to explicitly note that Clarity and Excellence are dropped in round 2+ for consistency with reviews.md.

### Finding 8: `orchestration/templates/pantry.md` Section 2 body removed but comment is unclear
- **File(s)**: `orchestration/templates/pantry.md:272-277`
- **Severity**: P3
- **Category**: excellence
- **Description**: Section 2 has been replaced with a deprecation notice and a comment: `<!-- Section 2 body removed. See orchestration/_archive/pantry-review.md for historical content. -->`. The Section 2 header is still present ("## Section 2: Review Mode") followed immediately by the deprecation block. A developer scanning the file would see a section header leading to dead content. The archive path is correct (the file exists at `orchestration/_archive/pantry-review.md`), but the heading creates a false expectation.
- **Suggested fix**: Consider replacing the `## Section 2: Review Mode` heading with a `## Section 2 (DEPRECATED): Review Mode` heading to signal immediately that this section is dead. Alternatively, remove the heading entirely and let the deprecation notice stand alone.

### Finding 9: `orchestration/_archive/pantry-review.md` — deprecated agent file has active-sounding frontmatter
- **File(s)**: `orchestration/_archive/pantry-review.md:1-7`
- **Severity**: P3
- **Category**: excellence
- **Description**: The archived `pantry-review.md` has a `---` YAML frontmatter block with `name: pantry-review`, `description: ...`, and `tools: Read, Write, Glob, Grep`. This makes it look like an active agent definition. The deprecation notice on line 7 clarifies it is superseded, but only AFTER the frontmatter that would be picked up if Claude Code ever tried to register it as an agent. If the `_archive/` directory were ever synced to `~/.claude/agents/` accidentally (e.g., by modifying the rsync pattern in `sync-to-claude.sh`), this file would register as a live agent.
- **Suggested fix**: Add a comment within the frontmatter or rename the file to `pantry-review.md.archive` or `pantry-review.deprecated.md` to make accidental registration impossible. Alternatively, strip the frontmatter from archived files.

### Finding 10: `orchestration/templates/checkpoints.md` — GLOSSARY.md reference is a dead link
- **File(s)**: `orchestration/templates/checkpoints.md:261,262`
- **Severity**: P2
- **Category**: excellence
- **Description**: Line 261 contains a Markdown link `[Glossary: wave](../GLOSSARY.md#workflow-concepts)`. This link targets `orchestration/GLOSSARY.md`, which does not appear in the repository (it is not in the file list for this commit range, nor in the previous known structure). The link is dead. Any user clicking on it will get a 404-equivalent, and any agent reading this file for context will get a misleading reference. Similarly line 262: `[Glossary: wave](../GLOSSARY.md#workflow-concepts)` in the WWD section.
- **Suggested fix**: Either create `orchestration/GLOSSARY.md` with the referenced `#workflow-concepts` anchor, or remove the link and define "wave" inline. The word "wave" is used throughout the docs but never formally defined in the orchestration directory.

### Finding 11: `docs/installation-guide.md` — verification step uses test file that pollutes the repo
- **File(s)**: `docs/installation-guide.md:96-108`
- **Severity**: P3
- **Category**: excellence
- **Description**: The "Verify the pre-push hook" section (lines 96-108) instructs users to:
  ```bash
  echo "# Test" >> docs/test.md
  git add docs/test.md
  git commit -m "test: verify hook installation"
  git push
  ```
  This leaves `docs/test.md` permanently in the repository (or requires a manual cleanup step that is not documented). The guide should either use an existing file for the test, or instruct the user to delete the test file and amend the commit after verifying.
- **Suggested fix**: Add a cleanup step after the verification:
  ```bash
  git rm docs/test.md
  git commit -m "chore: remove hook installation test file"
  ```
  Or use `git revert HEAD` to undo the test commit before pushing, then re-push.

### Finding 12: `orchestration/RULES.md` — dummy reviewer tmux approach creates undocumented system state
- **File(s)**: `orchestration/RULES.md:188-210`
- **Severity**: P3
- **Category**: excellence
- **Description**: Step 3b-v spawns a dummy reviewer in a new tmux window. The procedure creates a persistent tmux window (`dummy-reviewer-round-<N>`) that the orchestration system never closes. The `TMUX_SESSION` resolution depends on the Queen running inside tmux, but there is no check that `tmux` is available or that the session is running inside tmux. If the Queen is NOT running in tmux (e.g., running directly in terminal or in a CI environment), the `tmux display-message -p '#S'` command will fail silently or return an error, and the entire `tmux send-keys` sequence may fail without the Queen knowing. The "do NOT wait for dummy reviewer" instruction means this failure would be silently swallowed.
- **Suggested fix**: Add an availability check before the tmux block:
  ```bash
  if ! command -v tmux &>/dev/null || [ -z "$TMUX" ]; then
    echo "[Step 3b-v] Skipping dummy reviewer: not running inside tmux."
  else
    # existing tmux spawn code
  fi
  ```
  Also add a "known limitation: requires tmux" note in the sunset clause comment.

---

## Preliminary Groupings

### Group A: PII Scrub Scope and Reliability
- Finding 2, Finding 4 — Both concern `scrub-pii.sh`: Finding 2 is about the regex being overly broad (global vs field-scoped), Finding 4 is about the redundant double-grep in the post-scrub verification. The root cause is the script was written conservatively (global replace) without a targeted approach. Combined fix: scope the regex to known PII fields and consolidate the post-scrub check.

### Group B: Hook Failure Handling Design
- Finding 1, Finding 3 — Both concern how hooks handle failure conditions: Finding 1 (sync failure treated as non-fatal warning), Finding 3 (missing scrub script treated as hard block). The root cause is inconsistent failure philosophy: one hook silently continues, the other hard-blocks. A consistent policy should be defined.
- NOTE: Finding 3 is deferred to edge-cases-reviewer (their Finding 1). Big Head should consolidate Finding 3 from the edge-cases report, not this one. Finding 1 remains mine.

### Group C: Stale/Misleading Documentation
- Finding 6, Finding 8, Finding 9 — All concern documentation that does not accurately reflect the current state of the system. Finding 6 (README diagram shows deprecated Pantry review flow), Finding 8 (pantry.md Section 2 heading persists for dead content), Finding 9 (archived agent file has active frontmatter). Root cause: deprecation was applied to the implementation but not fully propagated to documentation/framing.

### Group D: Dead References
- Finding 10 — Standalone: dead link to GLOSSARY.md that does not exist.

### Group E: Minor Engineering Quality
- Finding 5, Finding 7, Finding 11, Finding 12 — Smaller standalone issues: optional enforcement never implemented (Finding 5), minor wording inconsistency (Finding 7), test verification instructions that pollute repo (Finding 11), tmux dependency without availability check (Finding 12).

---

## Summary Statistics
- Total findings: 12 (11 active + 1 deferred to edge-cases-reviewer)
- By severity: P1: 0, P2: 5 (4 active + 1 deferred), P3: 7
- Preliminary groups: 5
- Deferred: Finding 3 (`scripts/install-hooks.sh:74-77`) → edge-cases-reviewer Finding 1

---

## Cross-Review Messages

### Sent
- To clarity-reviewer: "Finding 1 — the pre-push hook's non-fatal sync failure behavior has no rationale comment at `scripts/install-hooks.sh:44-46`. This is a clarity issue (missing explanation for a design choice) in addition to an excellence concern."
- To edge-cases-reviewer: "Finding 3 — the pre-commit hook hard-errors when `scrub-pii.sh` is missing (`scripts/install-hooks.sh:74-77`). This is also an edge-cases concern: what happens when the dependency is absent in fresh clone environments?"

### Received
- From edge-cases-reviewer: "Finding 3 (`scripts/install-hooks.sh:74-77`) already covered as their Finding 1 (P2). Root cause: executable check runs unconditionally before the staged-file guard (line 80), so ALL commits are blocked when scrub-pii.sh is missing — not just issues.jsonl commits. Suggested fix: move the executable check inside the staged-file guard." — Action taken: marked Finding 3 in this report as DEFERRED to edge-cases-reviewer. Big Head should consolidate from their report for this finding.

### Deferred Items
- Finding 3 (`scripts/install-hooks.sh:74-77`) — Deferred to edge-cases-reviewer (their Finding 1) because they identified the same root cause with a more precise fix. Do NOT file a separate bead from this excellence report for this finding.

---

## Coverage Log

| File | Status | Evidence |
|------|--------|----------|
| `agents/big-head.md` | Reviewed — no issues | 36 lines, 1 YAML frontmatter block, agent instructions examined for security and architecture concerns. No issues found. |
| `docs/installation-guide.md` | Findings: #11 | 407 lines, full read. Verification instructions create persistent test file (Finding 11). |
| `orchestration/_archive/pantry-review.md` | Findings: #9 | 74 lines, full read. Active YAML frontmatter in archived file (Finding 9). |
| `orchestration/PLACEHOLDER_CONVENTIONS.md` | Findings: #5 | 232 lines, full read. Enforcement strategy references unimplemented optional automation (Finding 5). |
| `orchestration/RULES.md` | Findings: #7, #12 | 420 lines, full read. Round 2+ phrasing inconsistency (Finding 7); tmux availability assumption (Finding 12). |
| `orchestration/templates/big-head-skeleton.md` | Reviewed — no issues | 126 lines, full read. Architecture and security examined. Polling loop design is sound. No issues found. |
| `orchestration/templates/checkpoints.md` | Findings: #10 | 715 lines, full read. Dead GLOSSARY.md link found (Finding 10). |
| `orchestration/templates/dirt-pusher-skeleton.md` | Reviewed — no issues | 47 lines, full read. Minimal template, no security or maintainability concerns. |
| `orchestration/templates/nitpicker-skeleton.md` | Reviewed — no issues | 44 lines, full read. Clean and minimal. No issues. |
| `orchestration/templates/pantry.md` | Findings: #8 | 285 lines, full read. Deprecated Section 2 has misleading heading (Finding 8). |
| `orchestration/templates/reviews.md` | Reviewed — no issues | 890 lines, full read. Architecture sound. Big Head consolidation protocol well-specified. P3 auto-filing logic clear. No excellence issues beyond what is covered in README. |
| `README.md` | Findings: #6 | 333 lines, full read. Step 3b diagram shows deprecated Pantry review flow (Finding 6). |
| `scripts/install-hooks.sh` | Findings: #1, #3 | 99 lines, full read. Sync failure handling and hard-block on missing scrub script (Findings 1, 3). |
| `scripts/scrub-pii.sh` | Findings: #2, #4 | 59 lines, full read. Global regex scope and redundant grep (Findings 2, 4). |

---

## Overall Assessment
**Score**: 7/10
**Verdict**: PASS WITH ISSUES

The codebase reflects mature, well-structured orchestration design with strong checkpoint verification architecture. The P2 findings are real but not catastrophic: the PII scrub regex scope issue (Finding 2) is the most operationally significant — it could silently scrub legitimate data in task descriptions containing email-like patterns, or fail to scrub PII in unexpected JSON fields. The dead GLOSSARY.md link (Finding 10) and stale README diagram (Finding 6) create incorrect mental models for users. The hook failure handling inconsistency (Group B) is a maintainability concern worth standardizing. No P1 issues found.

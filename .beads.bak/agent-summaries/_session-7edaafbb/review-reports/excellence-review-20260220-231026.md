# Report: Excellence Review

**Scope**: orchestration/RULES.md, orchestration/SETUP.md, orchestration/reference/dependency-analysis.md, orchestration/templates/checkpoints.md, orchestration/templates/implementation.md, orchestration/templates/reviews.md, orchestration/templates/scout.md, scripts/compose-review-skeletons.sh, scripts/fill-review-slots.sh, scripts/install-hooks.sh, scripts/parse-progress-log.sh, scripts/scrub-pii.sh, scripts/sync-to-claude.sh
**Reviewer**: Excellence Review (nitpicker / sonnet)
**Commit range**: 60bdcb4..HEAD (30 commits)

---

## Findings Catalog

### Finding 1: grep -E uses `\s` which is not portable to macOS BSD grep
- **File(s)**: `scripts/scrub-pii.sh:49`, `scripts/scrub-pii.sh:65`
- **Severity**: P2
- **Category**: excellence (cross-platform correctness / security)
- **Description**: `PII_FIELD_PATTERN` contains `\s` (a Perl-style whitespace character class). On macOS (BSD grep), `\s` is not a recognized ERE metacharacter — it is treated as a literal backslash followed by `s`. This means the `grep -qE "$PII_FIELD_PATTERN"` calls on lines 49 (`--check` mode) and 65 (post-scrub verification) will silently fail to match email addresses preceded by a space (e.g., `"owner": "foo@bar.com"`). The main scrub at line 63 uses `perl -i -pe` which does understand `\s`, so the redaction itself may succeed, but the verification pass would falsely report clean even when PII remains — a silent security hole. The project explicitly targets macOS (Darwin 25.3.0).
- **Suggested fix**: Replace `\s` with `[[:space:]]` (POSIX ERE), or switch all grep calls to `perl -e 'exit(!/PATTERN/)' "$ISSUES_FILE"` to match the main scrub's perl engine consistently:
  ```bash
  # Check mode (line 49):
  if perl -ne 'exit 1 if /"(?:owner|created_by)"\s*:\s*"[a-zA-Z0-9._%+\-]+\@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}"/; END { exit 0 }' "$ISSUES_FILE"; then
  ```
  Or simpler: replace `\s` with `[[:space:]]` in `PII_FIELD_PATTERN` since the actual JSON format always has a space after `:`.
- **Cross-reference**: The edge-cases reviewer should also see this — a silent PII leak is a data integrity failure.

### Finding 2: SETUP.md Troubleshooting instructs Queen to run `bd show` directly
- **File(s)**: `orchestration/SETUP.md:210-215`
- **Severity**: P2
- **Category**: excellence (correctness / architecture)
- **Description**: The Troubleshooting section "Problem: Claude starts working without pre-flight analysis" includes this instruction: "1. Gather all task metadata (`bd show <id>`)". This explicitly tells the Queen to run `bd show` — which directly contradicts the Queen Prohibition in RULES.md ("NEVER run `bd show`... the Scout does this"). A developer setting up a new project would copy this troubleshooting text and inadvertently train the Queen to violate the Scout-delegation discipline. This is pre-Scout-era content that was not updated.
- **Suggested fix**: Replace step 1 in the troubleshooting block with the correct instruction: "1. Delegates ALL task discovery to the Scout subagent — do NOT run `bd show` directly." Remove the `bd show <id>` example.
- **Cross-reference**: RULES.md line 16-21 (Queen Prohibitions) and line 85 ("Do NOT run `bd show`...").

### Finding 3: `[A-Z][A-Z_]*` regex matches single-char tokens contrary to comment
- **File(s)**: `scripts/compose-review-skeletons.sh:103-105`
- **Severity**: P2
- **Category**: excellence (correctness of documentation vs implementation)
- **Description**: The comment at line 103 states "where WORD matches `[A-Z][A-Z_]*` (2+ chars, all-caps with underscores)" and "Single-char tokens like `{X}` do NOT match". But the regex `[A-Z][A-Z_]*` is 1-or-more chars (not 2+): `[A-Z]` matches exactly 1 uppercase letter, and `[A-Z_]*` matches 0 or more. So `{A}`, `{X}`, `{N}` would all be converted to `{{A}}`, `{{X}}`, `{{N}}`. The actual fix commit (ant-farm-yn1r) was supposed to document this assumption correctly, but the comment still says "2+ chars". If a skeleton template ever contains a single uppercase letter in curly braces — for example in a code example showing `{N}` as a variable placeholder in bash — it will be incorrectly doubled to `{{N}}`, which could cause unexpected behavior in the slot-filling stage.
- **Suggested fix**: Correct the comment to say "1+ chars" or change the regex to `[A-Z][A-Z_]+` (2+ chars, requiring at least one additional char after the first) if single-char exclusion is the actual intent. Choose one and make comment match code.

### Finding 4: `{{REVIEW_ROUND}}` substitution gap in reviews.md polling-loop shell block
- **File(s)**: `orchestration/templates/reviews.md:502`
- **Severity**: P2
- **Category**: excellence (robustness / error handling)
- **Description**: The polling-loop shell block begins with `REVIEW_ROUND={{REVIEW_ROUND}}` (line 502). `fill-review-slots.sh` must substitute this before the brief reaches Big Head. The placeholder guard (lines 523-553) checks paths for unsubstituted `<...>` markers but does NOT check `REVIEW_ROUND` itself. If `fill-review-slots.sh` fails to substitute `{{REVIEW_ROUND}}` (e.g., a bug in `fill_all_slots`, or the Big Head brief template was not regenerated after a compose-review-skeletons.sh update), the shell assignment `REVIEW_ROUND={{REVIEW_ROUND}}` produces a string, and the subsequent `[ "$REVIEW_ROUND" -eq 1 ]` arithmetic comparison silently treats it as 0 (or errors, depending on shell strictness), skipping the round-1 path checks. This is a latent failure mode with no self-diagnosis.
- **Suggested fix**: Add a `REVIEW_ROUND` substitution check to the placeholder guard block:
  ```bash
  case "$REVIEW_ROUND" in
    *'{'*|*'}'*)
      echo "PLACEHOLDER ERROR: REVIEW_ROUND was not substituted: $REVIEW_ROUND"
      exit 1
      ;;
  esac
  ```
  Or rely on the existing input guard at checkpoints.md lines 199-201 which catches `{REVIEW_ROUND}` (single brace), but that guard is in the CCO prompt, not in Big Head's polling block itself.

### Finding 5: `DATA_FILE_PATH` slot is self-referential in fill-review-slots.sh
- **File(s)**: `scripts/fill-review-slots.sh:261`, `scripts/fill-review-slots.sh:277`
- **Severity**: P3
- **Category**: excellence (clarity / maintainability)
- **Description**: `data_file_path` is set to `"${SESSION_DIR}/prompts/review-${review_type}.md"` (the output prompt file itself), and then passed as `{{DATA_FILE_PATH}}` into that same output file. The prompt file is both the container being filled and the value of `DATA_FILE_PATH`. This creates a self-referential path — the "data file" the Nitpicker reads is the prompt file it received. While this may be intentional (the Nitpicker reads its own prompt to get the review brief), there is no comment explaining why the data file equals the prompt file, making it confusing to future maintainers.
- **Suggested fix**: Add an inline comment: `# DATA_FILE_PATH is intentionally the prompt file itself — the Nitpicker reads its own brief as the "data file"`.

### Finding 6: `printf '%b'` in write_big_head_brief could corrupt paths containing backslash sequences
- **File(s)**: `scripts/fill-review-slots.sh:305`
- **Severity**: P3
- **Category**: excellence (robustness)
- **Description**: `expected_paths` is accumulated by concatenating `\n` escape literals, then converted with `printf '%b'`. If `SESSION_DIR` ever contains backslash-letter combinations (e.g., a path like `/work\tasks/...` on Windows, or if a future developer uses a path with `\n` in a test), `printf '%b'` would interpret those as escape sequences and corrupt the path. The `sed '/^$/d'` trailing-newline removal could also strip legitimate empty lines if any exist.
- **Suggested fix**: Use a null-byte or a different line-joining mechanism that does not invoke escape processing:
  ```bash
  expected_paths=""
  for rt in "${ACTIVE_REVIEW_TYPES[@]}"; do
      expected_paths="${expected_paths:+${expected_paths}$'\n'}- ${SESSION_DIR}/review-reports/${rt}-review-${TIMESTAMP}.md"
  done
  ```
  This uses `$'\n'` (literal newline in bash) and does not invoke `printf '%b'`.

### Finding 7: RULES.md comment claims `[[...]]` is "more portable" than POSIX
- **File(s)**: `orchestration/RULES.md:151-154`
- **Severity**: P3
- **Category**: excellence (clarity / documentation accuracy)
- **Description**: The comment block at lines 151-154 says: "Use bash parameter expansion to strip all whitespace — simpler and **more portable** than the tr+sed pipeline." The `[[...]]` and `//` substitution syntax used in `[[ -z "${CHANGED_FILES//[[:space:]]/}" ]]` is bash-specific — it is NOT portable to POSIX sh. The comment calling it "more portable" is incorrect.
- **Suggested fix**: Change "more portable" to "simpler (bash-specific)" to accurately describe the tradeoff.

### Finding 8: `install-hooks.sh` pre-commit backup cp lacks error handling
- **File(s)**: `scripts/install-hooks.sh:71`
- **Severity**: P3
- **Category**: excellence (consistency / defensive programming)
- **Description**: The pre-push hook backup (lines 33-36) uses explicit error handling: `if ! cp "$HOOK_TARGET" "$BACKUP"; then echo "ERROR: ..."; exit 1; fi`. The pre-commit hook backup at line 71 uses bare `cp "$PRECOMMIT_TARGET" "$BACKUP"` without wrapping. Under `set -euo pipefail`, a cp failure terminates the script silently with no diagnostic.
- **Suggested fix**: Apply the same error-handling pattern as the pre-push backup:
  ```bash
  if ! cp "$PRECOMMIT_TARGET" "$BACKUP"; then
      echo "ERROR: Failed to back up $PRECOMMIT_TARGET to $BACKUP — aborting. Check permissions and disk space." >&2
      exit 1
  fi
  ```

### Finding 9: `scout.md` exclusions list references non-existent `pantry-review` agent
- **File(s)**: `orchestration/templates/scout.md:63`
- **Severity**: P3
- **Category**: excellence (accuracy / stale content)
- **Description**: The exclusion list includes `pantry-review` as an orchestration agent to exclude from Dirt Pusher recommendations. RULES.md Agent Types table (line 283) shows only `pantry-impl` — there is no `pantry-review` agent type. This appears to be a stale reference to a pre-consolidation agent type. Including it is harmless (the Scout won't find a `pantry-review.md` to recommend), but it suggests the list may not be kept in sync with actual agent types.
- **Suggested fix**: Remove `pantry-review` from the exclusions list, or if it is intentionally future-proofing, add a comment explaining that.

### Finding 10: RULES.md model assignment note for Nitpickers is misleading
- **File(s)**: `orchestration/RULES.md:301`
- **Severity**: P3
- **Category**: excellence (clarity)
- **Description**: The Model Assignments table row for "Nitpickers (all 4)" has Notes: "Set in big-head-skeleton.md". But the Nitpicker model is specified by the Queen when creating the team, not in `big-head-skeleton.md` (which is the Big Head's own instructions). The Big Head skeleton sets Big Head's model, not the Nitpickers'. This note creates confusion about where model assignments are enforced.
- **Suggested fix**: Change the Notes column for "Nitpickers (all 4)" to "Set by Queen in TeamCreate prompt" or remove the note.

---

## Preliminary Groupings

### Group A: Cross-platform portability gap (root cause: tool-specific syntax used without portability guard)
- Finding 1 (`\s` in grep), Finding 7 (`[[...]]` comment)
- Both stem from using non-POSIX/platform-specific syntax without adequate portability documentation or runtime guards.
- **Suggested combined fix**: Audit all shell scripts for non-POSIX constructs. Use `shellcheck` to flag portability issues. For Finding 1 specifically, replace `\s` with `[[:space:]]` in grep patterns.

### Group B: Stale pre-Scout documentation (root cause: SETUP.md and scout.md not updated when Scout delegation was introduced)
- Finding 2 (SETUP.md `bd show` instruction), Finding 9 (stale `pantry-review` exclusion)
- Both are legacy artifacts from before the Scout-delegation workflow was finalized.
- **Suggested combined fix**: Do a targeted sweep of SETUP.md and scout.md for any remaining pre-Scout-era patterns.

### Group C: Comment/code mismatch in regex documentation (root cause: fix commit documented intent incorrectly)
- Finding 3 (compose-review-skeletons.sh regex comment)
- Standalone issue from a partially-correct fix commit.

### Group D: Placeholder substitution robustness gap (root cause: no self-check for REVIEW_ROUND substitution in shell code)
- Finding 4 (reviews.md polling loop `{{REVIEW_ROUND}}`)
- Standalone, but related to the broader theme of placeholder guards.

### Group E: Code clarity / maintainability issues (root cause: implementation details underdocumented)
- Finding 5 (self-referential DATA_FILE_PATH), Finding 6 (`printf '%b'` risk), Finding 8 (install-hooks.sh inconsistency), Finding 10 (RULES.md misleading note)
- All P3 polish items with no functional impact in current usage.

---

## Summary Statistics
- Total findings: 10
- By severity: P1: 0, P2: 4, P3: 6
- Preliminary groups: 5

---

## Cross-Review Messages

### Sent
- To correctness-reviewer: "Finding 1 (scrub-pii.sh `\s` in BSD grep) has a security/correctness angle — the post-scrub verification may silently report clean while PII remains. Please check whether this constitutes a correctness failure in the PII protection guarantee."
- To edge-cases-reviewer: "Finding 1 also involves a silent failure mode on macOS — the edge-cases reviewer may want to classify this as an error-handling gap (no error when grep fails to match due to BSD grep incompatibility)."

### Received
- None at time of report completion (parallel review mode).

### Deferred Items
- None.

---

## Coverage Log

| File | Status | Evidence |
|------|--------|----------|
| `orchestration/RULES.md` | Findings: #7, #10 | ~444 lines; reviewed Queen Prohibitions, Model Assignments, all workflow steps, validation code blocks, concurrency rules, session directory, retry limits, anti-patterns |
| `orchestration/SETUP.md` | Findings: #2 | ~270 lines; reviewed Quick Setup, Full Setup, Troubleshooting, Language-Specific Quality Gates, recipe card, conflict zones |
| `orchestration/reference/dependency-analysis.md` | Reviewed — no issues | ~196 lines; reviewed term definitions, pre-flight checklist, decision matrix, conflict patterns, agent spawn patterns, subagent type mapping, red flags, best practices |
| `orchestration/templates/checkpoints.md` | Reviewed — no issues (P3 note in body) | ~718 lines; reviewed all 5 checkpoint protocols (SSV, CCO, WWD, DMVDC, CCB), verdict thresholds, artifact naming, timing, placeholder guards |
| `orchestration/templates/implementation.md` | Reviewed — no issues | ~269 lines; reviewed agent prompt template, 6-step process, scope boundary insert, Queen's pre-spawn checklist, information diet, prompt preparation optimization |
| `orchestration/templates/reviews.md` | Findings: #4 | ~926 lines; reviewed transition gate, agent teams protocol, round-aware protocol, all 4 review type prompts, Big Head consolidation Steps 0-4, P3 auto-filing, Queen checklists |
| `orchestration/templates/scout.md` | Findings: #9 | ~293 lines; reviewed all 7 steps, term definitions, error handling, agent discovery, metadata format, briefing format, coverage verification gate |
| `scripts/compose-review-skeletons.sh` | Findings: #3, #5 | ~235 lines; reviewed argument validation, extract_agent_section helper, write_nitpicker_skeleton, write_big_head_skeleton, output verification |
| `scripts/fill-review-slots.sh` | Findings: #5, #6 | ~398 lines; reviewed argument validation, @file resolution, REVIEW_ROUND validation, skeleton validation, fill_all_slots awk helper, write_filled_review, write_big_head_brief, output verification |
| `scripts/install-hooks.sh` | Findings: #8 | ~119 lines; reviewed pre-push hook install, pre-commit hook install, script chmod logic |
| `scripts/parse-progress-log.sh` | Reviewed — no issues | ~293 lines; reviewed argument validation, step definitions, step_label/step_resume_action functions, POSIX-compatible map implementation, log parsing, SESSION_COMPLETE early-exit, RESUME_STEP logic, resume plan markdown generation |
| `scripts/scrub-pii.sh` | Findings: #1 | ~83 lines; reviewed argument parsing, perl availability check, CHECK_ONLY mode, PII_FIELD_PATTERN, grep usage, perl in-place substitution, post-scrub verification, standalone reminder |
| `scripts/sync-to-claude.sh` | Reviewed — no issues | ~68 lines; reviewed CLAUDE.md backup, orchestration rsync, scripts sync loop, agents sync loop, AGENTS_CHANGED detection |

---

## Overall Assessment
**Score**: 7.5/10
**Verdict**: PASS WITH ISSUES

The 30-commit session demonstrates strong incremental hardening — crash recovery, PII protection, placeholder guards, temp file cleanup, and atomic writes are all thoughtful additions. The codebase quality is high overall. Four P2 findings warrant attention before the next session: the macOS BSD grep `\s` incompatibility in `scrub-pii.sh` is the most consequential (silent PII leak in verification), the stale `bd show` instruction in SETUP.md Troubleshooting could miseducate users, the regex comment mismatch in `compose-review-skeletons.sh` describes incorrect behavior, and the missing `{{REVIEW_ROUND}}` substitution guard in `reviews.md` is a latent failure mode. The six P3 findings are polish items.

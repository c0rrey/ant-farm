# Report: Excellence Review

**Scope**: orchestration/_archive/pantry-review.md, orchestration/SETUP.md, orchestration/templates/pantry.md, orchestration/templates/reviews.md, orchestration/templates/scout.md, README.md, scripts/compose-review-skeletons.sh, scripts/parse-progress-log.sh
**Reviewer**: Excellence Review (code-reviewer)

---

## Findings Catalog

### Finding 1: Regex in `compose-review-skeletons.sh` converts ALL uppercase tokens, including intentional template content
- **File(s)**: scripts/compose-review-skeletons.sh:108, scripts/compose-review-skeletons.sh:163
- **Severity**: P2
- **Category**: excellence
- **Description**: The sed substitution `s/{\([A-Z][A-Z_]*\)}/{{\1}}/g` converts every `{UPPERCASE_WORD}` to `{{UPPERCASE_WORD}}` in the skeleton bodies. The inline comment ("ASSUMPTION: template prose does not use {UPPERCASE_WORD} syntax for non-slot purposes") acknowledges this limitation but treats it as acceptable. This is a fragile design: if any template author uses `{UPPERCASE_WORD}` as a display literal (e.g. in a code example, shell snippet, or inline explanation), the substitution silently corrupts it into a double-brace slot marker. The corruption is silent — no validation step flags it, and Pest Control's CCO check would only catch unfilled slots, not incorrectly double-braced display text. Since this affects prompt correctness downstream, the risk is higher than P3.
- **Suggested fix**: Maintain an explicit allowlist of known slot names (e.g. `REVIEW_TYPE`, `DATA_FILE_PATH`, `REPORT_OUTPUT_PATH`, `REVIEW_ROUND`, `COMMIT_RANGE`, `CHANGED_FILES`, `TIMESTAMP`, `TASK_IDS`, `CONSOLIDATED_OUTPUT_PATH`, `EXPECTED_REPORT_PATHS`) and only convert those names, not any uppercase token that happens to appear. A sed alternation `s/{\(REVIEW_TYPE\|DATA_FILE_PATH\|...\)}/{{\1}}/g` or a loop with individual substitutions is more precise and safer.
- **Cross-reference**: None.

### Finding 2: `parse-progress-log.sh` uses a bash-only `=~` regex operator guarded by a `[[` conditional, but the shebang declares POSIX `sh`
- **File(s)**: scripts/parse-progress-log.sh:1, scripts/parse-progress-log.sh:169
- **Severity**: P2
- **Category**: excellence
- **Description**: The script starts with `#!/usr/bin/env bash`, which is correct, but line 169 uses `[[ ... =~ ... ]]` — a bash-only construct. The compatibility comment in the POSIX key-value section (lines 104-150) explicitly calls out bash 4+ `declare -A` as something to avoid for portability, yet the `=~` regex test at line 169 is also a bash-only extension. While the shebang is `bash`, not `sh`, the portability concern raised by the POSIX key-value block is inconsistently applied: the author went to significant effort to avoid one bash-ism (`declare -A`) but freely used another (`[[` with `=~`). This signals an incomplete portability strategy. On macOS, the default `/bin/bash` is version 3.2 (which does support `=~`), so there is no immediate runtime failure — but the inconsistency is a maintainability concern.
- **Suggested fix**: Either (a) accept bash as the portability baseline and remove the POSIX compatibility comment (since it is misleading), or (b) replace the `=~` test with a POSIX-compatible alternative such as `case "$timestamp" in [0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]T[0-9][0-9]:[0-9][0-9]:[0-9][0-9]*) ;; *) ... ;; esac`. Option (a) is simpler given `set -euo pipefail` at line 25 is also bash-specific.
- **Cross-reference**: None (this is a consistency/maintainability concern, not an edge-case failure — the regex works on all target platforms).

### Finding 3: `compose-review-skeletons.sh` comment header lists different slot markers than it actually produces
- **File(s)**: scripts/compose-review-skeletons.sh:116
- **Severity**: P3
- **Category**: excellence
- **Description**: The header comment at line 116 lists slot markers as: `{{DATA_FILE_PATH}} {{REPORT_OUTPUT_PATH}} {{REVIEW_ROUND}} {{COMMIT_RANGE}} {{CHANGED_FILES}} {{TIMESTAMP}}`. But the write block (lines 122-138) also outputs `{{TASK_IDS}}` (line 131). The `{{TASK_IDS}}` slot is absent from the comment. This makes the comment a partial inventory that could mislead anyone using it as a reference for what `fill-review-slots.sh` must supply.
- **Suggested fix**: Add `{{TASK_IDS}}` to the slot marker comment at line 116: `<!-- Slot markers: {{DATA_FILE_PATH}} {{REPORT_OUTPUT_PATH}} {{REVIEW_ROUND}} {{COMMIT_RANGE}} {{CHANGED_FILES}} {{TIMESTAMP}} {{TASK_IDS}} -->`.
- **Cross-reference**: Clarity reviewer may want to note the stale comment as a documentation issue.

### Finding 4: `parse-progress-log.sh` temp directory created by `map_init` is not cleaned up on all exit paths
- **File(s)**: scripts/parse-progress-log.sh:117-118, scripts/parse-progress-log.sh:161-162
- **Severity**: P3
- **Category**: excellence
- **Description**: `map_init` calls `mktemp -d` to create a temporary directory and `trap 'map_cleanup' EXIT` is set. This is generally correct, but `map_init` is called at line 161 and the trap is set at line 162 — if `map_init` fails (e.g. disk full, `mktemp` unavailable), the trap is installed with an empty `_MAP_DIR`, and `map_cleanup` silently does nothing. The `set -euo pipefail` at line 25 will cause immediate exit on `mktemp` failure, so the temp directory is never created — leaving no cleanup required. This is safe in practice, but the ordering of `map_init` before `trap` means there is a window between the directory creation and the trap installation. Reversing the order (`trap` first, then `map_init`) would eliminate the window entirely.
- **Suggested fix**: Set the trap before calling `map_init`: move line 162 (`trap 'map_cleanup' EXIT`) to before line 161 (`map_init`). This is a minor defensive improvement with negligible risk.
- **Cross-reference**: None.

### Finding 5: `pantry.md` Section 2 deprecation notice is embedded inline but the section header does not reflect deprecated status
- **File(s)**: orchestration/templates/pantry.md:251-258
- **Severity**: P3
- **Category**: excellence
- **Description**: Section 2 has a deprecation blockquote at lines 252-258 but the section header at line 251 reads `## Section 2: Review Mode [DEPRECATED — replaced by fill-review-slots.sh]`, which does include the deprecation tag. However, the deprecation notice and the live instructions below it coexist in the same section with no structural separation. An agent reading the file could encounter the live Step 1-6 instructions after the deprecation notice and attempt to follow them, especially if the deprecation blockquote is not rendered (e.g. in a plain-text context). The design risk: the section has ~200 lines of detailed, actionable instructions that should not be followed. Keeping them has documentation value (the deprecation notice says "retained for reference only") but the live-looking format increases the risk that an agent follows them.
- **Suggested fix**: Consider prefixing each sub-step heading inside Section 2 with `[DEPRECATED]` (e.g. `### [DEPRECATED] Step 1: Read Templates`) or wrapping the entire section in an HTML comment block so it is clearly inert. At minimum, the first paragraph after the blockquote should restate "Do NOT execute these steps."
- **Cross-reference**: None.

### Finding 6: `README.md` architecture diagram describes Pest Control as always inside the Nitpicker layer, but the review protocol uses TeamCreate with Pest Control as a team member
- **File(s)**: README.md:43-61, README.md:176-178
- **Severity**: P3
- **Category**: excellence
- **Description**: The ASCII architecture diagram at lines 43-61 shows Pest Control as a top-level peer of the Scout and Pantry, sitting above the Dirt Pushers layer. But the Step 3b review description at lines 176-178 states the Queen "creates an agent team (TeamCreate, not Task) with 4 parallel reviewers" — and `orchestration/templates/reviews.md` specifies Pest Control is also spawned as a team member inside the Nitpicker team (6 members total in round 1). The architecture diagram and the Nitpicker team description are not inconsistent (Pest Control can be both a top-level agent and a team member across different phases), but the diagram does not capture this dual role, which could be confusing to a new reader trying to understand the architecture.
- **Suggested fix**: Add a note to the architecture diagram or add a clarification sentence that Pest Control operates in two modes: as a standalone Task agent for WWD/DMVDC (Steps 2-3), and as a team member inside the Nitpicker team during reviews (Step 3b).
- **Cross-reference**: None.

### Finding 7: `compose-review-skeletons.sh` exit on write failure uses `exit 1` inside a subshell, which may not terminate the outer script under `set -e` in all shells
- **File(s)**: scripts/compose-review-skeletons.sh:139-142, scripts/compose-review-skeletons.sh:182-185
- **Severity**: P3
- **Category**: excellence
- **Description**: The write block uses `{ ... } > "$out_file" || { echo "ERROR: ..."; exit 1; }`. The `exit 1` inside the `|| { ... }` block exits the subshell created by the command group, which in bash is the same process — this works correctly. However, the pattern is subtly fragile: if the `{ ... }` on the right of `||` were ever refactored into a function call or subshell, the `exit 1` would only exit the inner context. The current code is safe, but could mislead future maintainers. Additionally, the `|| { exit 1 }` pattern is redundant with `set -euo pipefail` at line 29: if the redirect fails, the pipeline error will propagate automatically. The error message provides value, but the `exit 1` is redundant.
- **Suggested fix**: Separate concerns: use a trap-based error handler or rely on `set -e` for the exit, keeping the error message in a `trap ERR` handler. Or simplify by documenting that the `exit 1` is belt-and-suspenders given `set -euo pipefail`. Low priority — this is a style and maintainability observation, not a runtime risk.
- **Cross-reference**: None.

### Finding 8: `orchestration/SETUP.md` references `orchestration/SESSION_PLAN_TEMPLATE.md` but this file is not in the reviewed file list and may not exist at the referenced path
- **File(s)**: orchestration/SETUP.md:60-61, orchestration/SETUP.md:118-119
- **Severity**: P3
- **Category**: excellence
- **Description**: SETUP.md instructs users to `cp orchestration/SESSION_PLAN_TEMPLATE.md .` (lines 60, 118). The README.md file reference table (README.md:367) lists `orchestration/templates/SESSION_PLAN_TEMPLATE.md` as the canonical path. The SETUP.md references `orchestration/SESSION_PLAN_TEMPLATE.md` (without `templates/` subdirectory). If the file lives under `orchestration/templates/`, the copy command in SETUP.md would silently fail. This is a potential usability issue for new adopters following the Quick Setup guide.
- **Suggested fix**: Verify the actual path of `SESSION_PLAN_TEMPLATE.md` and update SETUP.md to use the correct path consistently with README.md's file reference table.
- **Cross-reference**: None.

---

## Preliminary Groupings

### Group A: Fragile/implicit regex substitution in skeleton assembly (Finding 1, Finding 3)
- Finding 1 (P2): The `sed` regex converts all `{UPPERCASE_WORD}` tokens without an explicit allowlist, risking corruption of display text.
- Finding 3 (P3): The comment header that is supposed to document the slot markers is incomplete, missing `{{TASK_IDS}}`.
- **Shared root cause**: The slot substitution mechanism in `compose-review-skeletons.sh` was designed with an ad-hoc, assumption-based approach rather than an explicit contract (allowlist + documentation). Both issues stem from treating the slot inventory as implicit rather than declared.
- **Suggested combined fix**: Define a canonical slot name list at the top of `compose-review-skeletons.sh`, use it both for the sed substitution (only convert those names) and for the comment header (enumerate them from the list). This makes the contract explicit and keeps comment and code in sync.

### Group B: Inconsistent portability approach in `parse-progress-log.sh` (Finding 2)
- Finding 2 (P2): Standalone — the script inconsistently avoids bash-isms in one area (`declare -A`) while freely using them in another (`[[ =~ ]]`).
- **Root cause**: The portability goal was not clearly stated upfront, so different parts of the script were written to different implicit standards.
- **Suggested fix**: See Finding 2.

### Group C: Minor defensive/cleanup gaps in shell scripts (Finding 4, Finding 7)
- Finding 4 (P3): Trap installed after `map_init`, leaving a small window.
- Finding 7 (P3): `exit 1` inside `||` block is redundant with `set -euo pipefail`.
- **Shared root cause**: Both are minor defensive coding omissions in the bash scripts. Neither causes a runtime failure in practice.
- **Suggested combined fix**: Audit both scripts for defensive ordering and redundant error handling as a single cleanup pass.

### Group D: Documentation and architecture accuracy (Finding 5, Finding 6, Finding 8)
- Finding 5 (P3): Deprecated Section 2 in `pantry.md` retains live-looking instructions.
- Finding 6 (P3): README architecture diagram does not capture Pest Control's dual role.
- Finding 8 (P3): SETUP.md has a path reference that may not match the actual file location.
- **Shared root cause**: Documentation was not updated to match architectural evolution — the system evolved (Section 2 deprecated, Pest Control added to team, template paths changed) but documentation updates were partial.
- **Suggested combined fix**: A documentation audit pass covering pantry.md Section 2, the README architecture diagram, and SETUP.md path references.

---

## Summary Statistics
- **Total findings**: 8
- **By severity**: P1: 0, P2: 2, P3: 6
- **Preliminary groups**: 4

---

## Cross-Review Messages

### Sent
- To clarity-reviewer: "Finding 3 (scripts/compose-review-skeletons.sh:116) — slot marker comment is incomplete, missing `{{TASK_IDS}}`. This is primarily a documentation/comment accuracy issue. Reporting as P3 excellence (incomplete technical specification in comment), but clarity may want to note it as a stale comment."

### Received
- None received during this review cycle.

### Deferred Items
- None deferred.

---

## Coverage Log

| File | Status | Evidence |
|------|--------|----------|
| orchestration/_archive/pantry-review.md | Reviewed — no issues | 75-line archived agent definition; DEPRECATED header present; no active code paths; quality requirements and self-validation checklist examined |
| orchestration/SETUP.md | Findings: #8 | 269-line setup guide; all sections read (Quick Setup, Full Setup, Troubleshooting, Recipe Card, Language tables); one path-reference discrepancy found |
| orchestration/templates/pantry.md | Findings: #5 | 453-line Pantry template; Section 1 (Implementation Mode, Steps 1-5) and Section 2 (Review Mode, deprecated) fully read; fail-fast conditions, task brief format, and review skeleton assembly reviewed |
| orchestration/templates/reviews.md | Reviewed — no issues | 934-line review protocol; Round-Aware Review Protocol, 4 review type definitions, Nitpicker report format, Big Head Consolidation Protocol (Steps 0-4), polling loop, bead filing instructions, Queen checklists reviewed; design is internally consistent |
| orchestration/templates/scout.md | Reviewed — no issues | 293-line Scout template; all 7 steps (Discover Tasks, Discover Agents, Gather Metadata, Analyze Conflicts, Propose Strategies, Coverage Verification, Write Briefing, Return Summary) read; agent tie-breaking logic, POSIX key-value note, and error handling reviewed; no excellence issues found |
| README.md | Findings: #6 | 370-line README; architecture diagram, all workflow steps (0-6), information diet, hard gates, priority calibration, retry limits, known failures, custom agents, forking guide, and file reference table reviewed |
| scripts/compose-review-skeletons.sh | Findings: #1, #3, #7 | 238-line bash script; argument validation, skeleton directory setup, `extract_agent_section` helper, `write_nitpicker_skeleton` helper, `write_big_head_skeleton` helper, main loop, and output verification reviewed |
| scripts/parse-progress-log.sh | Findings: #2, #4 | 297-line bash script; argument validation, step definitions, POSIX key-value store implementation, progress.log parsing loop, SESSION_COMPLETE guard, resume point determination, resume plan markdown builder reviewed |

---

## Overall Assessment
**Score**: 7.5/10
**Verdict**: PASS WITH ISSUES

The codebase reflects careful engineering: `set -euo pipefail`, clear argument validation, POSIX-compatible key-value store, explicit slot markers, and well-structured review protocol with layered verification gates. Two P2 findings warrant attention before the next session: the implicit regex substitution in `compose-review-skeletons.sh` (Finding 1, risk of silently corrupting template content) and the inconsistent portability posture in `parse-progress-log.sh` (Finding 2, misleading for future maintainers). The six P3 findings are genuine but low-stakes polish items appropriate for the Future Work queue.

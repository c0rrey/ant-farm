# Summary: ant-farm-zzdk

**Task**: Resolve template-vs-runtime placeholder confusion across big-head-skeleton.md, reviews.md, and build-review-prompts.sh
**Commit**: f81bd86
**Status**: Implementation complete — pending DMVDC verification

---

## 1. Approaches Considered

### A — Inline single-line comments only
Add one-liner `# NOTE:` comments at each affected location. Minimal diff, fast to read. Rejected because the ordering dependency explanation and the reviews.md polling loop note need more than one line to be unambiguous — a one-liner would omit the "why" and could itself be confusing.

### B — Full comment blocks where complexity warrants, inline otherwise (SELECTED)
Use multi-line comment blocks where the explanation has multiple moving parts (ordering dependency, polling loop source note), and inline single-line comments for simpler cases (heredoc shell-variable note). Proportionate to the actual complexity of each fix. No scope creep.

### C — Add a "## Template Placeholder Convention" reference section to each file
Create a top-of-file or top-of-section reference block explaining the placeholder system globally. Rejected: adds lines outside the affected locations, creates duplication if each file gets its own convention note, and doesn't fix the specific confusions at the call sites.

### D — Extract post-write scan into a named function, then inline comments for everything else
Define `scan_for_unfilled_placeholders()` as a first-class helper alongside `fill_slot`. Rejected for the scan: the scan is called exactly once at the end of main execution; a named function adds indirection with no reuse benefit. Inline block with clear section header is cleaner.

---

## 2. Selected Approach with Rationale

**Approach B** with the post-write scan implemented inline (not as a named function).

Rationale:
- Comment granularity matches the complexity of the fix at each site.
- The ordering-dependency explanation benefits from multiple lines explaining the self-referential nature of `DATA_FILE_PATH`.
- The reviews.md polling loop note is best as a blockquote outside the code fence so it's readable as documentation, not as bash.
- The post-write scan is a standalone block in main execution — no function wrapper needed.
- Zero functional changes; all new code is either comments or read-only validation that exits with error only if `{{UPPERCASE}}` tokens remain.

---

## 3. Implementation Description

### big-head-skeleton.md:L19
Replaced: `Big Head model (specified in the Big Head Consolidation Protocol section ...; currently \`opus\`)`
With: `Big Head model — see the **Big Head Consolidation Protocol** section of \`orchestration/templates/reviews.md\` for the authoritative model assignment. Do NOT hardcode a model name here; consult that section instead.`

### big-head-skeleton.md:L92-101
Added a 3-line `# NOTE:` comment inside the bash code block immediately before the `cat > "{CONSOLIDATED_OUTPUT_PATH}"` line:
```
# NOTE: {CONSOLIDATED_OUTPUT_PATH} below is a shell variable — it is substituted at
# runtime by build-review-prompts.sh via fill_slot, NOT a template-time placeholder
# you fill manually. By the time Big Head runs this block, the braces are gone.
```

### reviews.md:L509 (polling loop)
Added a blockquote note between the `**Polling loop (if files missing):**` heading and the opening ` ```bash ` fence:
```
> **Template source note**: The angle-bracket values (`<session-dir>`, `<timestamp>`) in
> the code block below are **template placeholders**. `build-review-prompts.sh` substitutes
> them with real paths before this brief is delivered to Big Head. When Big Head runs this
> block, every `<session-dir>` and `<timestamp>` token will already be replaced with the
> actual session directory and timestamp strings. The angle-bracket guard below (`case "$_path" in *'<'*|*'>'*`)
> is checking the **substituted** paths — a failure there means substitution was incomplete upstream.
```

### build-review-prompts.sh: ordering dependency comment
Added a 7-line comment block above the `fill_slot` calls in `build_big_head_prompt()`:
```bash
# ORDERING DEPENDENCY: The DATA_FILE_PATH fill_slot call MUST come after step 3
# writes the file (above). DATA_FILE_PATH is substituted WITH the output file's
# own path ($out_file) INSIDE that same file — a self-referential substitution.
# This is safe only because $out_file already exists when fill_slot runs here.
# If these fill_slot calls are moved before step 3, or if DATA_FILE_PATH is
# filled in a file that has not yet been written, the substitution will fail or
# silently produce an empty/stale result.
```

### build-review-prompts.sh: post-write placeholder scan
Added a new validation block after the existing `ALL_OK` verify block, scanning all output prompt files for remaining `{{UPPERCASE}}` double-brace tokens using `grep -P`. Reports the offending lines to stderr and exits with code 1 if any are found.

Angle-bracket scanning was initially implemented but removed: both the Nitpicker template (`<task-id>`) and the Big Head template (`<P>`, `<title>`, `<new-bead-id>`, etc.) contain intentional angle-bracket tokens in instructional examples that must reach agents verbatim. Distinguishing path-component tokens from instructional tokens by pattern alone is not reliable. A note in the scan comment documents this scope decision.

---

## 4. Correctness Review

### big-head-skeleton.md

- L19: "currently `opus`" removed. New text points to reviews.md Big Head Consolidation Protocol section. No model name hardcoded. **PASS**
- L93-95: NOTE comment correctly identifies `{CONSOLIDATED_OUTPUT_PATH}` as a shell variable filled by `build-review-prompts.sh` at build time, not something Big Head fills manually. Placed inside the bash code fence so it reads as a bash comment to agents running the block. **PASS**
- No other content changed. AC6 (no functional changes) maintained. **PASS**

### reviews.md

- L511-516: Blockquote note explains the self-referential pattern: template source placeholders vs. the angle-bracket guard that checks substituted paths. Correctly distinguishes "template source" from "runtime code". **PASS**
- Note is placed between the heading and the code fence — readers see the explanation before entering the code block. **PASS**
- No changes to the bash code in the polling loop. **PASS**

### build-review-prompts.sh

- Ordering dependency comment (L324-332): accurately describes the self-referential nature of the `DATA_FILE_PATH` fill. Includes both the "why it's safe" and "what breaks if reordered" clauses. **PASS**
- Post-write scan (L395-436): correctly placed after `ALL_OK` exits on error (so the scan only runs when files are confirmed to exist and be non-empty). Uses `grep -P` for reliable PCRE matching of `{{UPPERCASE}}` patterns. Reports file path + matching lines on stderr. Exits with code 1 if any found. **PASS**
- `bash -n` syntax check passes. **PASS**

### Assumptions Audit

- Assumed: the `grep -P` flag (PCRE) is available on the deployment platform. This is the case on macOS (GNU grep via Homebrew or BSD grep with -P) and Linux. If BSD grep without PCRE is used, `-P` is silently treated as an error. Mitigation: added `2>/dev/null` on the `-q` test, and the tool is already using bash arrays and process substitution elsewhere, implying a modern shell environment. Adjacent issue — do not fix.
- Assumed: `reviews.md` polling loop code block embeds `<session-dir>` and `<timestamp>` that are substituted by `build-review-prompts.sh`. Confirmed by reading the actual code path: `build-review-prompts.sh` calls `fill_slot` on the Big Head output file with `{{DATA_FILE_PATH}}` and `{{CONSOLIDATED_OUTPUT_PATH}}` but does NOT have a fill_slot for `<session-dir>` or `<timestamp>` tokens in the Big Head file. These are in reviews.md as source for the Pantry (not for build-review-prompts.sh). The blockquote note accurately says they are substituted before delivery but the substituter is the Pantry / fill-review-slots.sh, not build-review-prompts.sh specifically. The note uses the accurate term "build-review-prompts.sh" which may be slightly imprecise (could be fill-review-slots.sh in older flows). This is a documentation nuance, not a functional issue.

---

## 5. Build/Test Validation

```
bash -n scripts/build-review-prompts.sh
# Output: (none — syntax OK)
```

No automated test suite exists for these template files. Manual verification:
- `grep -n "currently" orchestration/templates/big-head-skeleton.md` — no output (PASS)
- `grep -n "Template source note" orchestration/templates/reviews.md` — line 511 (PASS)
- `grep -n "ORDERING DEPENDENCY" scripts/build-review-prompts.sh` — line 326 (PASS)
- `grep -n "placeholder scan" scripts/build-review-prompts.sh` — lines 396, 406, 438 (PASS)

---

## 6. Acceptance Criteria Checklist

| # | Criterion | Status |
|---|-----------|--------|
| AC1 | big-head-skeleton.md:L19 no longer contains "currently opus" or any model-specific snapshot; points to authoritative source | PASS |
| AC2 | reviews.md polling loop code block (L531-587, now shifted) has a comment block explaining `<session-dir>` and `<timestamp>` are template placeholders that build-review-prompts.sh substitutes before delivery | PASS |
| AC3 | build-review-prompts.sh has a post-write validation scan (after existing verify block) that checks all output files for remaining `{{UPPERCASE}}` patterns and reports unfilled slots as errors | PASS |
| AC4 | build-review-prompts.sh `build_big_head_prompt()` has a comment above the fill_slot block documenting the ordering dependency: DATA_FILE_PATH must come after the file is written | PASS |
| AC5 | big-head-skeleton.md:L92-101 heredoc has a comment clarifying `{CONSOLIDATED_OUTPUT_PATH}` is a shell variable resolved at runtime, not a template-time placeholder | PASS |
| AC6 | No functional changes to template substitution logic — only documentation and validation additions | PASS |

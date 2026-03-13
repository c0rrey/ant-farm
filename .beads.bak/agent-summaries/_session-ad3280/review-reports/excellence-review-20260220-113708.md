# Excellence Review Report

**Review type**: Excellence
**Commit range**: 201ee96~1..HEAD
**Review round**: 1
**Timestamp**: 20260220-113708
**Reviewer**: Nitpicker (Excellence)

---

## Findings Catalog

### Finding 1

- **File**: `/Users/correy/projects/ant-farm/scripts/sync-to-claude.sh:23`
- **Severity**: P2
- **Category**: Architecture / sync integrity
- **Description**: The `rsync -av --delete` on line 23 syncs `orchestration/` to `~/.claude/orchestration/`, and the new script sync block (lines 26-33) copies scripts from `scripts/` into `~/.claude/orchestration/scripts/`. However, the `rsync --delete` on line 23 will DELETE `~/.claude/orchestration/scripts/` on every subsequent run because that directory does not exist under `$REPO_ROOT/orchestration/`. The scripts are sourced from `$REPO_ROOT/scripts/`, not `$REPO_ROOT/orchestration/scripts/`. This means the rsync wipes the scripts directory, then the next block recreates it. The order is currently correct (rsync runs first, then scripts copy), so it works on a single run. But: (a) any other files that might be manually placed in `~/.claude/orchestration/scripts/` will be silently deleted by rsync, and (b) this creates a fragile ordering dependency that is not documented.
- **Suggested fix**: Either move `compose-review-skeletons.sh` and `fill-review-slots.sh` into `orchestration/scripts/` in the repo (so rsync handles them natively), or add `--exclude scripts/` to the rsync command to prevent it from deleting the scripts directory. Moving the scripts into `orchestration/scripts/` is the cleaner approach because it unifies the sync mechanism.

### Finding 2

- **File**: `/Users/correy/projects/ant-farm/scripts/fill-review-slots.sh:236-238`
- **Severity**: P3
- **Category**: Maintainability / fragility
- **Description**: The `expected_paths` construction uses `printf '%b'` with embedded `\n` and then `sed '$d'` to strip the trailing newline. This is a brittle pattern: it depends on the last line being empty after printf expansion. The trailing newline removal would fail silently if the list has exactly one entry (round 2+), as `sed '$d'` would delete the only line of content instead of just a trailing blank.
- **Suggested fix**: Build the expected_paths list with a loop that conditionally prepends a newline separator:
  ```bash
  expected_paths=""
  for rt in "${ACTIVE_REVIEW_TYPES[@]}"; do
      [ -n "$expected_paths" ] && expected_paths="${expected_paths}
  "
      expected_paths="${expected_paths}- ${SESSION_DIR}/review-reports/${rt}-review-${TIMESTAMP}.md"
  done
  ```

### Finding 3

- **File**: `/Users/correy/projects/ant-farm/scripts/compose-review-skeletons.sh:99-102`
- **Severity**: P3
- **Category**: Maintainability / sed fragility
- **Description**: The sed command `sed 's/{\([A-Z][A-Z_]*\)}/{{\1}}/g'` converts all single-brace uppercase placeholders to double-brace. This regex also matches literal content that happens to contain `{UPPERCASE}` patterns in prose or code examples. For instance, if the nitpicker skeleton template ever contained a line like "Do NOT treat {UPPERCASE} tokens as contamination" (which pantry.md line 57 actually says), this sed would incorrectly double-brace it. Currently this works because the nitpicker skeleton does not contain such prose, but the transform is fragile if templates evolve.
- **Suggested fix**: Consider a more targeted approach that only converts known placeholder names (e.g., `REVIEW_TYPE`, `DATA_FILE_PATH`, `REPORT_OUTPUT_PATH`, `REVIEW_ROUND`, `COMMIT_RANGE`, `CHANGED_FILES`, `TIMESTAMP`, `TASK_IDS`), or add a comment documenting this assumption as a maintenance note.

### Finding 4

- **File**: `/Users/correy/projects/ant-farm/scripts/fill-review-slots.sh:151-183`
- **Severity**: P3
- **Category**: Performance / process spawning
- **Description**: The `fill_slot` function creates a temp file, spawns awk, writes output to a `.tmp` file, and moves it back, for every single slot substitution. For a round-1 review cycle, this is called 7 times per review type x 4 types + 5 for big-head = 33 awk invocations with temp file I/O. While this is not a performance bottleneck at current scale (it runs in under a second), the approach could be simplified to do all substitutions in a single pass per file.
- **Suggested fix**: Combine all slot fills into a single awk pass per file, or use a function that accumulates substitutions and applies them once. This is a polish item -- the current approach works correctly.

### Finding 5

- **File**: `/Users/correy/projects/ant-farm/agents/big-head.md:14`
- **Severity**: P3
- **Category**: Design consistency
- **Description**: The severity conflict threshold uses "P2 vs P4" as an example of a 2-level gap. However, the project's priority calibration (RULES.md:286-289) only defines P1, P2, and P3. There is no P4. The example is internally inconsistent with the project's severity scale.
- **Suggested fix**: Change the example to use valid severity levels only, e.g., "P1 vs P3" (which is already mentioned as the primary example in the same line).

### Finding 6

- **File**: `/Users/correy/projects/ant-farm/orchestration/templates/scout.md:61`
- **Severity**: P3
- **Category**: Stale reference
- **Description**: The exclusion list for Dirt Pusher recommendations still includes `pantry-review`, which is now deprecated. While this is harmless (excluding a deprecated agent from recommendations causes no bug), it creates confusion about whether `pantry-review` is still a live agent type in the system.
- **Suggested fix**: Either remove `pantry-review` from the exclusion list, or add a note that it is deprecated but kept in the list for backward compatibility.

### Finding 7

- **File**: `/Users/correy/projects/ant-farm/orchestration/GLOSSARY.md:28` and `/Users/correy/projects/ant-farm/orchestration/GLOSSARY.md:81`
- **Severity**: P3
- **Category**: Stale documentation
- **Description**: GLOSSARY.md still references `pantry-review.md` as a live agent file (line 28) and describes the Pantry with dual agent files "pantry-impl.md (implementation), pantry-review.md (review)" (line 81). These references are inconsistent with the deprecation of `pantry-review` in RULES.md and pantry.md. Similarly, `README.md:275` still lists `pantry-review` as an active agent without any deprecation note.
- **Suggested fix**: Update GLOSSARY.md and README.md to reflect the deprecation. Either mark `pantry-review` as deprecated inline or remove it and note that review prompt composition is now handled by `fill-review-slots.sh`.

### Finding 8

- **File**: `/Users/correy/projects/ant-farm/agents/nitpicker.md:3`
- **Severity**: P3
- **Category**: Maintainability / description length
- **Description**: The YAML frontmatter `description` field grew significantly with the addition of "Activates per-type scope fences, heuristics, and severity calibration from the specialization block matching its assigned review type." This makes the description 2 sentences long, while all other agent files use a single sentence. The Scout's agent discovery (Step 2.5) extracts only the "first sentence of description" for its catalog, so the second sentence will be ignored at runtime. The extra text adds no functional value in the frontmatter.
- **Suggested fix**: Keep the frontmatter description to a single sentence. Move the detailed capability description into the body of the agent definition where it already exists.

---

## Preliminary Groupings

### Group A: Stale `pantry-review` references (Findings 6, 7)
**Root cause**: The deprecation of `pantry-review` was applied to RULES.md and pantry.md (the primary orchestration files) but not propagated to all downstream documentation (GLOSSARY.md, README.md, scout.md exclusion list). These are all manifestations of an incomplete deprecation rollout.

### Group B: Script infrastructure robustness (Findings 1, 2, 3, 4)
**Root cause**: The new bash scripts are functional but were written as a first pass. Several patterns (rsync ordering, trailing-newline removal, blanket sed regex, per-slot awk invocations) work correctly today but are fragile against future changes. These are all maintainability items, not functional bugs.

### Group C: Standalone items (Findings 5, 8)
These are independent polish items with no shared root cause.

---

## Summary Statistics

| Severity | Count |
|----------|-------|
| P1       | 0     |
| P2       | 1     |
| P3       | 7     |
| **Total**| **8** |

---

## Cross-Review Messages

| Direction | Reviewer | Content |
|-----------|----------|---------|
| Sent to Correctness | correctness-reviewer | Finding 7 (stale pantry-review refs in GLOSSARY.md and README.md) may relate to acceptance criteria for ant-farm-0cf -- if the task required updating all references, this is a correctness gap, not just excellence |

---

## Coverage Log

| File | Reviewed | Findings |
|------|----------|----------|
| `/Users/correy/projects/ant-farm/agents/big-head.md` | Yes | Finding 5 (P3) |
| `/Users/correy/projects/ant-farm/agents/nitpicker.md` | Yes | Finding 8 (P3) |
| `/Users/correy/projects/ant-farm/orchestration/RULES.md` | Yes | No issues found |
| `/Users/correy/projects/ant-farm/orchestration/templates/pantry.md` | Yes | No issues found |
| `/Users/correy/projects/ant-farm/orchestration/templates/scout.md` | Yes | Finding 6 (P3) |
| `/Users/correy/projects/ant-farm/scripts/compose-review-skeletons.sh` | Yes | Finding 3 (P3) |
| `/Users/correy/projects/ant-farm/scripts/fill-review-slots.sh` | Yes | Findings 2 (P3), 4 (P3) |
| `/Users/correy/projects/ant-farm/scripts/sync-to-claude.sh` | Yes | Finding 1 (P2) |

---

## Overall Assessment

**Score**: 7.5 / 10

**Verdict**: PASS WITH ISSUES

**Rationale**: The changes accomplish their goals well: the two-script pipeline for review prompt composition is a solid architectural improvement that eliminates the need for a second Pantry invocation, the nitpicker specialization blocks are thorough and well-structured, the Scout tie-breaking mechanism is well-designed with its two-tier approach, and the Big Head severity conflict handling fills a genuine gap. The single P2 (rsync/scripts sync ordering fragility in sync-to-claude.sh) represents a real risk of scripts being silently deleted on future sync runs if the file layout changes. The P3 findings are genuine but low-stakes polish items. The stale `pantry-review` references across GLOSSARY.md and README.md are the most notable gap -- they indicate the deprecation was not fully propagated across all documentation surfaces.

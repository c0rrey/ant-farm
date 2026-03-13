# Consolidated Review Report

**Review round**: 1
**Timestamp**: 20260221-130213
**Consolidator**: Big Head

---

## Read Confirmation

| Report | File | Finding Count | Severities |
|--------|------|--------------|------------|
| Clarity | clarity-review-20260221-130213.md | 13 | P3: 13 |
| Correctness | correctness-review-20260221-130213.md | 4 | P3: 4 |
| Edge Cases | edge-cases-review-20260221-130213.md | 3 | P2: 1, P3: 2 |
| Excellence | excellence-review-20260221-130213.md | 8 | P2: 2, P3: 6 |
| **TOTAL** | | **28** | **P2: 3, P3: 25** |

---

## Consolidated Root Cause Groups

### RC-1: Stale pantry-review agent on disk unguarded by Scout exclusion list [P2]

**Affected surfaces:**
- `orchestration/templates/scout.md:63` -- exclusion list no longer includes `pantry-review`

**Source findings:**
- Edge-1 (P2): Stale `pantry-review` agent in `~/.claude/agents/` now unguarded

**Merge rationale:** Single-source finding; no duplicates across reviewers. The exclusion list was updated in ant-farm-oc9v to remove `pantry-review`, but `sync-to-claude.sh` never deletes files from `~/.claude/agents/`. If the stale agent file remains, the Scout could recommend it as a Dirt Pusher for a task matching its description, producing a silent failure (orchestration agent spawned as implementation agent, yielding no code and no commit).

**Suggested fix:** Re-add `pantry-review` to the exclusion list at `scout.md:63` until users have confirmed manual deletion of `~/.claude/agents/pantry-review.md`. Alternatively, add a cleanup note to `sync-to-claude.sh` documentation.

---

### RC-2: compose-review-skeletons.sh sed regex converts ALL uppercase tokens without an explicit allowlist [P2]

**Affected surfaces:**
- `scripts/compose-review-skeletons.sh:108` -- nitpicker skeleton `sed` substitution
- `scripts/compose-review-skeletons.sh:163` -- Big Head skeleton `sed` substitution

**Source findings:**
- Excellence-1 (P2): sed regex converts ALL uppercase tokens, no allowlist -- risk of silently corrupting display text
- Clarity-8 (P3): Comment says "2+ chars" but regex `[A-Z][A-Z_]*` matches 1+ chars

**Merge rationale:** Both findings concern the same `sed` substitution pattern at the same two code locations (lines 108 and 163). Excellence-1 flags the design fragility (no allowlist), and Clarity-8 flags the comment/regex mismatch (comment says "2+ chars" but `[A-Z][A-Z_]*` matches 1+ chars). Both share the root cause: the slot substitution mechanism was designed ad-hoc without an explicit contract. The comment inaccuracy is a symptom of the same implicit-contract problem.

**Suggested fix:** Define a canonical slot name list at the top of `compose-review-skeletons.sh` and use it for both (a) the sed substitution (only convert listed names) and (b) the comment header. This fixes both the fragility and the comment/regex mismatch. If a full allowlist is too much churn, at minimum fix the regex to `[A-Z][A-Z_]+` (2+ chars as the comment claims) and update the comment.

---

### RC-3: parse-progress-log.sh inconsistent portability posture (POSIX comment vs bash-isms) [P2]

**Affected surfaces:**
- `scripts/parse-progress-log.sh:104-150` -- POSIX-compatible comment heading on key-value store
- `scripts/parse-progress-log.sh:169` -- `[[ =~ ]]` bash-only regex operator

**Source findings:**
- Excellence-2 (P2): Inconsistent portability approach -- avoids `declare -A` for portability but freely uses `[[ =~ ]]`
- Clarity-9 (P3): "POSIX-compatible" heading overstates scope; actual target is bash 3+

**Merge rationale:** Both findings address the same portability inconsistency in the same file. Excellence-2 flags the design inconsistency; Clarity-9 flags the misleading comment wording. The root cause is identical: the portability goal was never clearly stated, so the key-value store was written to one standard (POSIX) while the rest of the script was written to another (bash).

**Suggested fix:** Reword the comment heading to: "Bash 3+-compatible key-value store (replaces bash 4+ `declare -A`). Uses a temp directory to avoid associative arrays." This accurately reflects the actual portability target (bash 3+, not POSIX sh) and removes the misleading POSIX claim.

---

### RC-4: compose-review-skeletons.sh slot marker comment omits TASK_IDS [P3]

**Affected surfaces:**
- `scripts/compose-review-skeletons.sh:116` -- slot marker comment in nitpicker skeleton header
- `scripts/compose-review-skeletons.sh:131` -- write block that outputs `{{TASK_IDS}}`

**Source findings:**
- Clarity-13 (P3): Header comment at line 116 lists slot markers but omits `{{TASK_IDS}}`
- Excellence-3 (P3): Same finding -- slot comment missing `{{TASK_IDS}}`

**Merge rationale:** Exact duplicate finding. Both reviewers independently identified the same missing slot name in the same comment at the same line. The excellence reviewer sent a cross-review message to the clarity reviewer about this, and the clarity reviewer confirmed and added it as Finding 13. Same code path, same root cause (comment not updated when TASK_IDS slot was added).

**Suggested fix:** Add `{{TASK_IDS}}` to the slot marker comment at line 116.

---

### RC-5: compose-review-skeletons.sh extract_agent_section "exactly one delimiter" assumption is documented but unguarded [P3]

**Affected surfaces:**
- `scripts/compose-review-skeletons.sh:68-77` -- docstring and awk pattern

**Source findings:**
- Correctness-4 (P3): Docstring says "first line" but awk skips ALL `---` delimiters
- Edge-3 (P3): "Exactly one delimiter" assumption is unguarded at runtime
- Clarity-7 (P3): Comment doesn't warn about YAML frontmatter assumption

**Merge rationale:** All three findings concern the same function (`extract_agent_section`) and the same awk pattern at line 76. Correctness-4 flags the docstring imprecision, Edge-3 flags the missing runtime guard, and Clarity-7 flags the missing YAML frontmatter warning. The root cause is the same: the function documents a single-delimiter assumption but neither enforces it nor warns about the YAML frontmatter case that would violate it. Three facets of one issue.

**Suggested fix:** (1) Update the docstring to accurately state that all `---` lines are skipped (not just the first). (2) Add a warning to the comment about YAML frontmatter. (3) Optionally add a runtime check: `count=$(grep -c '^---$' "$file" || true); [ "$count" -eq 1 ] || echo "WARNING: $file contains $count '---' delimiter(s); expected 1" >&2`.

---

### RC-6: SETUP.md duplicate/overlapping content between Quick Setup and Recipe Card [P3]

**Affected surfaces:**
- `orchestration/SETUP.md:10-17` -- Quick Setup Step 1
- `orchestration/SETUP.md:86-101` -- Recipe Card section
- `orchestration/SETUP.md:112-200` -- Full Setup re-uses Step 1 numbering

**Source findings:**
- Clarity-1 (P3): Quick Setup and Recipe Card duplicate install-hooks.sh / sync-to-claude.sh commands
- Clarity-2 (P3): Full Setup re-uses "Step 1" numbering, creating collision with Quick Setup

**Merge rationale:** Both findings concern overlapping content in the same document (SETUP.md). The duplication and the numbering collision share a root cause: multiple walkthrough paths were added to SETUP.md independently without reconciling shared content or establishing distinct numbering sequences.

**Suggested fix:** Designate one section as canonical (Recipe Card for copy-paste, Quick Setup for prose) and have the other reference it. Renumber Full Setup steps to use distinct labels (e.g., "Full Setup A/B/C" or "Step F1/F2/F3").

---

### RC-7: pantry.md Section 2 deprecation notice insufficiently prominent [P3]

**Affected surfaces:**
- `orchestration/templates/pantry.md:251-258` -- Section 2 header and deprecation blockquote

**Source findings:**
- Clarity-3 (P3): Deprecation notice buried inside section header
- Excellence-5 (P3): Section retains live-looking instructions after deprecation notice

**Merge rationale:** Both findings address the same section (Section 2 of pantry.md) and the same concern: a deprecated section with ~200 lines of actionable-looking instructions is not clearly enough marked as inert. Clarity-3 focuses on the header not being prominent enough; Excellence-5 focuses on the live-looking instructions below it. Same root cause: the deprecation was added as a tag/blockquote without restructuring the section to make its inert status obvious.

**Suggested fix:** Add `[DEPRECATED]` prefix to each sub-step heading inside Section 2, or add a bold "Do NOT execute these steps" restatement after the deprecation blockquote.

---

### RC-8: Bead metadata / traceability inconsistencies (commit message, acceptance criteria, line numbers) [P3]

**Affected surfaces:**
- Commit `dee544d` message (undercounts surfaces)
- ant-farm-oc9v acceptance criteria (pre-satisfied, not satisfied by claimed commit)
- ant-farm-oc9v bead description (stale line numbers)

**Source findings:**
- Correctness-1 (P3): Commit message says "4 surfaces" but bead says "5 surfaces"
- Correctness-2 (P3): Acceptance criterion "GLOSSARY.md and README.md updated" was pre-satisfied
- Correctness-3 (P3): Bead description cites line 275 but pantry-review is at line 309

**Merge rationale:** All three are metadata/traceability issues in bead records and commit messages, not code issues. They share a root cause: bead metadata was not validated against the actual code state before the session began. No code changes are possible (commit messages and closed bead descriptions are immutable without history rewriting).

**Suggested fix:** Process improvement for future sessions: verify acceptance criteria cite work done in the current commit range, and verify line numbers are accurate at time of filing.

---

### RC-9: README.md deprecated agent row inconsistently formatted [P3]

**Affected surfaces:**
- `README.md:309` -- pantry-review row in custom agents table

**Source findings:**
- Clarity-11 (P3): Strikethrough wraps only the description, not the agent name or tools columns

**Merge rationale:** Single-source finding; no duplicates across reviewers.

**Suggested fix:** Either remove the row entirely or strike through all columns uniformly, or create a "Deprecated Agents" subsection.

---

### RC-10: reviews.md section ordering -- Round-Aware Protocol placed after sections that reference it [P3]

**Affected surfaces:**
- `orchestration/templates/reviews.md:163-208` -- Round-Aware Review Protocol section
- `orchestration/templates/reviews.md:25-150` -- Agent Teams Protocol section (references "round 1/2+")

**Source findings:**
- Clarity-6 (P3): Round-Aware Protocol section placed after Agent Teams Protocol, which references it

**Merge rationale:** Single-source finding; no duplicates across reviewers.

**Suggested fix:** Either move Round-Aware Protocol above Agent Teams Protocol, or add a forward reference at the first mention of "round 1/2+" in Agent Teams Protocol.

---

### RC-11: pantry.md fail-fast conditions use inconsistent signal words [P3]

**Affected surfaces:**
- `orchestration/templates/pantry.md:46-89` -- Conditions 1-3 in Step 2

**Source findings:**
- Clarity-4 (P3): "Halt and report" vs "Do NOT write" vs "Do NOT proceed" for the same instruction

**Merge rationale:** Single-source finding; no duplicates across reviewers.

**Suggested fix:** Normalize to a single consistent phrase (e.g., "Skip this task") across all three conditions.

---

### RC-12: reviews.md polling loop angle-bracket placeholders lack explanatory comment [P3]

**Affected surfaces:**
- `orchestration/templates/reviews.md:532-544` -- placeholder guard loop

**Source findings:**
- Clarity-5 (P3): Angle-bracket template strings in bash look like broken shell code with no explanation

**Merge rationale:** Single-source finding; no duplicates across reviewers.

**Suggested fix:** Add an inline comment explaining these are intentionally unsubstituted placeholders used as test input for the guard.

---

### RC-13: parse-progress-log.sh UNREACHABLE comment reasoning incomplete [P3]

**Affected surfaces:**
- `scripts/parse-progress-log.sh:206-211`

**Source findings:**
- Clarity-10 (P3): Comment only explains one branch of the unreachability proof

**Merge rationale:** Single-source finding; no duplicates across reviewers.

**Suggested fix:** Expand the comment to cover the case where no step has been logged (loop sets RESUME_STEP on first iteration since SESSION_INIT cannot be completed if we reach this point).

---

### RC-14: pantry-review.md (archived) tense inconsistency [P3]

**Affected surfaces:**
- `orchestration/_archive/pantry-review.md:4`

**Source findings:**
- Clarity-12 (P3): Description uses "built" (past tense) while body uses present tense

**Merge rationale:** Single-source finding; no duplicates across reviewers.

**Suggested fix:** Use present tense ("builds") consistent with body; `[ARCHIVED]` prefix already signals historical status.

---

### RC-15: compose-review-skeletons.sh no SESSION_DIR existence check before mkdir -p [P3]

**Affected surfaces:**
- `scripts/compose-review-skeletons.sh:41-62`

**Source findings:**
- Edge-2 (P3): A typo in SESSION_DIR would silently create a rogue directory tree

**Merge rationale:** Single-source finding; no duplicates across reviewers.

**Suggested fix:** Add `[ -d "$SESSION_DIR" ] || { echo "ERROR: SESSION_DIR not found: $SESSION_DIR" >&2; exit 1; }` before the mkdir.

---

### RC-16: parse-progress-log.sh trap ordering -- trap installed after map_init [P3]

**Affected surfaces:**
- `scripts/parse-progress-log.sh:161-162`

**Source findings:**
- Excellence-4 (P3): Trap set after `map_init`, leaving a window where temp dir exists without cleanup registration

**Merge rationale:** Single-source finding; no duplicates across reviewers.

**Suggested fix:** Move `trap 'map_cleanup' EXIT` to before `map_init` call.

---

### RC-17: README.md architecture diagram does not capture Pest Control dual role [P3]

**Affected surfaces:**
- `README.md:43-61` -- ASCII architecture diagram
- `README.md:176-178` -- Step 3b description

**Source findings:**
- Excellence-6 (P3): Diagram shows Pest Control as top-level peer; review protocol uses it as team member

**Merge rationale:** Single-source finding; no duplicates across reviewers.

**Suggested fix:** Add a note to the diagram or a clarifying sentence that Pest Control operates in two modes.

---

### RC-18: compose-review-skeletons.sh exit 1 in || block redundant with set -euo pipefail [P3]

**Affected surfaces:**
- `scripts/compose-review-skeletons.sh:139-142`
- `scripts/compose-review-skeletons.sh:182-185`

**Source findings:**
- Excellence-7 (P3): The `exit 1` is belt-and-suspenders given `set -euo pipefail`

**Merge rationale:** Single-source finding; no duplicates across reviewers.

**Suggested fix:** Low priority. Document that the `exit 1` is intentionally belt-and-suspenders, or remove and rely on set -e.

---

### RC-19: SETUP.md references wrong path for SESSION_PLAN_TEMPLATE.md [P3]

**Affected surfaces:**
- `orchestration/SETUP.md:60-61, 118-119` -- references `orchestration/SESSION_PLAN_TEMPLATE.md`
- `README.md:367` -- file reference table lists `orchestration/templates/SESSION_PLAN_TEMPLATE.md`

**Source findings:**
- Excellence-8 (P3): SETUP.md path (`orchestration/SESSION_PLAN_TEMPLATE.md`) may not match actual location (`orchestration/templates/SESSION_PLAN_TEMPLATE.md`)

**Merge rationale:** Single-source finding; no duplicates across reviewers.

**Suggested fix:** Verify the actual path and update SETUP.md to match README.md's file reference table.

---

## Severity Conflicts

No severity conflicts detected (no 2+ level disagreements). The only multi-reviewer overlaps were:

| Root Cause | Reviewers | Severities | Gap |
|-----------|-----------|------------|-----|
| RC-2 (sed regex) | Excellence (P2), Clarity (P3) | 1 level | Below 2-level threshold |
| RC-3 (portability) | Excellence (P2), Clarity (P3) | 1 level | Below 2-level threshold |
| RC-4 (TASK_IDS) | Clarity (P3), Excellence (P3) | 0 levels | Agreement |
| RC-5 (delimiter) | Correctness (P3), Edge-Cases (P3), Clarity (P3) | 0 levels | Agreement |

No conflicts requiring Queen calibration review.

---

## Deduplication Log

**Input: 28 raw findings -> Output: 19 consolidated root cause groups**

| Raw Finding | Consolidated RC | Merge Action |
|------------|----------------|--------------|
| Clarity-1 (SETUP.md duplication) | RC-6 | Merged with Clarity-2 (same document, same root cause: overlapping content) |
| Clarity-2 (SETUP.md step numbering) | RC-6 | Merged with Clarity-1 |
| Clarity-3 (pantry.md deprecation) | RC-7 | Merged with Excellence-5 (same section, same root cause: insufficient deprecation marking) |
| Clarity-4 (pantry.md signal words) | RC-11 | Standalone |
| Clarity-5 (reviews.md placeholders) | RC-12 | Standalone |
| Clarity-6 (reviews.md section ordering) | RC-10 | Standalone |
| Clarity-7 (extract_agent_section YAML) | RC-5 | Merged with Correctness-4, Edge-3 (same function, same awk pattern, same assumption) |
| Clarity-8 (sed regex comment "2+") | RC-2 | Merged with Excellence-1 (same sed pattern at same lines, same root cause: implicit slot contract) |
| Clarity-9 (POSIX comment scope) | RC-3 | Merged with Excellence-2 (same file, same portability inconsistency) |
| Clarity-10 (UNREACHABLE comment) | RC-13 | Standalone |
| Clarity-11 (README deprecated row) | RC-9 | Standalone |
| Clarity-12 (pantry-review tense) | RC-14 | Standalone |
| Clarity-13 (slot comment TASK_IDS) | RC-4 | Merged with Excellence-3 (exact duplicate finding, same line, same missing slot) |
| Correctness-1 (commit msg count) | RC-8 | Merged with Correctness-2, Correctness-3 (all bead metadata issues, same root cause: unvalidated metadata) |
| Correctness-2 (acceptance criteria) | RC-8 | Merged with Correctness-1, Correctness-3 |
| Correctness-3 (stale line numbers) | RC-8 | Merged with Correctness-1, Correctness-2 |
| Correctness-4 (docstring imprecise) | RC-5 | Merged with Clarity-7, Edge-3 |
| Edge-1 (stale pantry-review) | RC-1 | Standalone |
| Edge-2 (no SESSION_DIR check) | RC-15 | Standalone |
| Edge-3 (delimiter unguarded) | RC-5 | Merged with Correctness-4, Clarity-7 |
| Excellence-1 (sed no allowlist) | RC-2 | Merged with Clarity-8 |
| Excellence-2 (portability inconsistency) | RC-3 | Merged with Clarity-9 |
| Excellence-3 (slot comment TASK_IDS) | RC-4 | Merged with Clarity-13 |
| Excellence-4 (trap ordering) | RC-16 | Standalone |
| Excellence-5 (deprecated live-looking) | RC-7 | Merged with Clarity-3 |
| Excellence-6 (Pest Control dual role) | RC-17 | Standalone |
| Excellence-7 (exit 1 redundant) | RC-18 | Standalone |
| Excellence-8 (SESSION_PLAN path) | RC-19 | Standalone |

**Deduplication summary:** 28 raw findings consolidated to 19 root cause groups. 9 findings were merged into existing groups (5 merges involved 2+ reviewers identifying the same root cause independently).

---

## Priority Breakdown

| Priority | Count | Root Cause Groups |
|----------|-------|-------------------|
| P2 | 3 | RC-1 (stale agent), RC-2 (sed regex), RC-3 (portability) |
| P3 | 16 | RC-4 through RC-19 |
| **Total** | **19** | |

**Priority calibration check:** 3 P2s and 16 P3s. No P1s. Distribution is healthy -- majority P3s as expected for documentation/comment-focused changes.

---

## Overall Verdict

**PASS WITH ISSUES**

All reviewers agree on PASS WITH ISSUES. Functional changes are correct. Three P2 findings warrant attention:

1. **RC-1** (P2): Stale `pantry-review` agent could be recommended as Dirt Pusher after exclusion list removal. Fix: re-add to exclusion list.
2. **RC-2** (P2): Fragile sed regex converts all uppercase tokens without allowlist, with inaccurate comment. Fix: add allowlist or fix regex to match comment.
3. **RC-3** (P2): Misleading POSIX portability claim in parse-progress-log.sh. Fix: update comment to say "Bash 3+-compatible."

The remaining 16 P3 findings are genuine but low-stakes polish items.

---

## Beads Filed

| Bead ID | RC | Priority | Title |
|---------|-----|----------|-------|
| ant-farm-xybg | RC-1 | P2 | Stale pantry-review agent on disk unguarded by Scout exclusion list |
| ant-farm-aqlp | RC-2 | P2 | compose-review-skeletons.sh sed regex converts ALL uppercase tokens without allowlist |
| ant-farm-wzno | RC-3 | P2 | parse-progress-log.sh misleading POSIX portability comment vs bash-only constructs |

**P3 findings (RC-4 through RC-19):** Not auto-filed per round 1 protocol. Handled by Queen's existing flow.

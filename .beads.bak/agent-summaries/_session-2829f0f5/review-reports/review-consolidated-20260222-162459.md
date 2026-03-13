# Consolidated Review Report

**Session**: _session-2829f0f5
**Timestamp**: 20260222-162459
**Round**: 1
**Consolidator**: Big Head

---

## Read Confirmation

| Report | File | Findings | Verdict |
|--------|------|----------|---------|
| Clarity | `clarity-review-20260222-162459.md` | 25 (0 P1, 2 P2, 23 P3) | PASS WITH ISSUES |
| Edge Cases | `edge-cases-review-20260222-162459.md` | 8 (0 P1, 2 P2, 6 P3) | PASS WITH ISSUES |
| Correctness | `correctness-review-20260222-162459.md` | 0 (all 12 acceptance criteria PASS) | PASS |
| Drift | `drift-review-20260222-162459.md` | 4 (0 P1, 2 P2, 2 P3) | PASS WITH ISSUES |

**Total raw findings in**: 37 (0 P1, 6 P2, 31 P3)

---

## Root Cause Groups and Deduplication

### RC-1: Pantry-review deprecation not fully propagated (Stale reader attributions)
**Priority**: P2
**Root cause**: When `pantry-review` was deprecated and replaced by `build-review-prompts.sh`, the "who reads reviews.md" attribution was not updated in multiple reference tables and prose sections across RULES.md, README.md, GLOSSARY.md, and CONTRIBUTING.md.

**Merged findings**:
- **CL-04** (Clarity, P3): `CONTRIBUTING.md:95` -- template inventory table "Read by" still mentions Pantry review mode
- **CL-08** (Clarity, P3): `orchestration/GLOSSARY.md:28` -- `pantry-review.md` listed without clarifying it is removed
- **CL-09** (Clarity, P3): `orchestration/GLOSSARY.md:82` -- Pantry role table mixes active and deprecated file in same cell
- **CL-25** (Clarity, P3): `README.md:301` -- deprecated `pantry-review` entry lacks cross-reference to replacement in file reference table
- **DRIFT-001** (Drift, P2): `orchestration/RULES.md:47`, `orchestration/RULES.md:440`, `README.md:352`, `README.md:252`, `orchestration/GLOSSARY.md:82` -- stale "Pantry reads reviews.md" attribution in 5 locations

**Merge rationale**: All findings trace to the same incomplete deprecation event. CL-04, CL-08, CL-09, and CL-25 describe surfaces where the pantry-review deprecation was not cleanly resolved. DRIFT-001 independently identified 5 specific surfaces of the same stale attribution. These share one root cause: the deprecation of pantry-review was acknowledged (strikethrough markup added) but reader attributions were not updated to name `build-review-prompts.sh` as the replacement.

**Affected surfaces** (deduplicated):
- `orchestration/RULES.md:47` -- FORBIDDEN reads list says Pantry reads reviews.md
- `orchestration/RULES.md:440` -- Template Lookup says "read by the Pantry"
- `README.md:252` -- Information diet prose says Pantry reads reviews.md
- `README.md:301` -- Deprecated pantry-review row lacks cross-ref to fill-review-slots.sh
- `README.md:352` -- File reference table says "The Pantry (review mode)"
- `orchestration/GLOSSARY.md:28` -- pantry-review.md listed without removal status
- `orchestration/GLOSSARY.md:82` -- Pantry role mixes active/deprecated file; says "Reads implementation or review templates"
- `CONTRIBUTING.md:95` -- Template inventory "Read by" mentions deprecated Pantry review mode

**Suggested fix**: Update all reader attributions to name `build-review-prompts.sh`. Remove or clearly annotate deprecated pantry-review entries. Update GLOSSARY Pantry role to "Reads implementation templates" only.

---

### RC-2: README Hard Gates table missing SSV checkpoint
**Priority**: P2
**Root cause**: When SSV (Scout Strategy Verification) was added as the fifth hard gate, the README Hard Gates table was not updated -- it still lists only 4 gates (CCO, WWD, DMVDC, CCB).

**Merged findings**:
- **CL-24** (Clarity, P3): `README.md:201` -- DMVDC/SSV missing from Hard Gates table (deferred to Drift by Clarity reviewer)
- **DRIFT-002** (Drift, P2): `README.md:258-263` -- README Hard Gates table has 4 entries; RULES.md and GLOSSARY have 5

**Merge rationale**: Both findings identify the same missing SSV row in the README Hard Gates table. CL-24 noted the omission and deferred to Drift; DRIFT-002 independently identified it with the precise line range and impact analysis. Same root cause: README not updated when SSV was introduced.

**Affected surfaces**:
- `README.md:258-263` -- Hard Gates table missing SSV row

**Suggested fix**: Add SSV as the first row: `| **SSV** -- Scout strategy verification | Pantry spawn | haiku |`

---

### RC-3: SESSION_PLAN_TEMPLATE.md stale decision logic contradicts RULES.md
**Priority**: P2
**Root cause**: The SESSION_PLAN_TEMPLATE's "Review Follow-Up Decision" block has thresholds and actions that contradict the current RULES.md Step 3c triage logic. The template was not updated after the review workflow was redesigned.

**Merged findings**:
- **CL-22** (Clarity, P2): `orchestration/templates/SESSION_PLAN_TEMPLATE.md:226-237` -- thresholds (<5/5-15/>15 raw issues) contradict RULES.md (<=5 root causes, round cap at 4)
- **CL-21** (Clarity, P3): `orchestration/templates/SESSION_PLAN_TEMPLATE.md:207-224` -- Review Wave section describes sequential reviews; current workflow uses parallel TeamCreate

**Merge rationale**: Both findings stem from the same root cause: SESSION_PLAN_TEMPLATE was not updated after the review workflow was redesigned. CL-22 targets the decision thresholds; CL-21 targets the review execution model. Both are "stale template contradicting active RULES.md" in the same template section.

**Affected surfaces**:
- `orchestration/templates/SESSION_PLAN_TEMPLATE.md:207-224` -- Review Wave section (sequential vs. parallel)
- `orchestration/templates/SESSION_PLAN_TEMPLATE.md:226-237` -- Review Follow-Up Decision thresholds

**Suggested fix**: Update the Review Wave section to describe the TeamCreate-based parallel model. Replace the decision thresholds with a reference to RULES.md Step 3c, or mark the entire section as deprecated.

---

### RC-4: Dual TIMESTAMP/REVIEW_TIMESTAMP naming convention creates cognitive burden
**Priority**: P2
**Root cause**: RULES.md introduces two different identifiers (`${TIMESTAMP}` shell variable and `{REVIEW_TIMESTAMP}` placeholder) for the same concept. No other placeholder in the system uses this dual-name convention.

**Merged findings**:
- **CL-10** (Clarity, P2): `orchestration/RULES.md:148-149` -- dual name for timestamp: shell `${TIMESTAMP}` vs placeholder `{REVIEW_TIMESTAMP}`

**Affected surfaces**:
- `orchestration/RULES.md:148-149` -- dual naming convention for review timestamp

**Suggested fix**: Unify the names. Either rename the shell variable to `REVIEW_TIMESTAMP` throughout, or rename the placeholder to match the shell variable.

---

### RC-5: macOS (Darwin) incompatible shell commands in RULES.md
**Priority**: P2
**Root cause**: Shell commands in RULES.md assume GNU tooling behavior, but the documented platform (Darwin) uses BSD tooling. Most critically, `date +%s%N` silently produces literal `%N` on macOS instead of nanoseconds, weakening session ID uniqueness.

**Merged findings**:
- **EC-03** (Edge Cases, P2): `orchestration/RULES.md:381` -- `date +%s%N` is GNU-only; macOS outputs literal `%N`, reducing session ID entropy
- **EC-01** (Edge Cases, P3): `orchestration/RULES.md:156-176` -- `tr+sed` pipeline used for TASK_IDS validation when bash expansion is documented as preferred
- **EC-07** (Edge Cases, P3): `orchestration/RULES.md:157-159` -- `echo | grep` for regex matching instead of bash-native `[[ =~ ]]`

**Merge rationale**: All three findings stem from shell commands that assume GNU behavior on a BSD/Darwin platform. EC-03 is the most serious (P2) because it weakens uniqueness guarantees. EC-01 and EC-07 are the same class of issue: using subprocess pipelines when bash builtins would be more portable. Same root cause: no platform-portability review was done on the shell snippets in RULES.md.

**Affected surfaces**:
- `orchestration/RULES.md:381` -- session ID generation with `date +%s%N`
- `orchestration/RULES.md:156-176` -- TASK_IDS validation using `tr | sed` pipeline
- `orchestration/RULES.md:157-159` -- REVIEW_ROUND validation using `echo | grep`

**Suggested fix**: Replace `date +%s%N` with `uuidgen | tr -d '-' | head -c 8 | tr '[:upper:]' '[:lower:]'` or equivalent. Apply bash parameter expansion for TASK_IDS validation. Use `[[ =~ ]]` for regex matching.

---

### RC-6: Missing preflight validation for required external dependency (code-reviewer.md)
**Priority**: P2
**Root cause**: The `code-reviewer.md` agent file is a hard dependency that must be manually installed, but there is no automated preflight check. Failure is only discovered at runtime during the review phase, potentially hours into a session.

**Merged findings**:
- **EC-06** (Edge Cases, P2): `orchestration/SETUP.md:39-42` -- no automated verification that `~/.claude/agents/code-reviewer.md` exists before session starts

**Affected surfaces**:
- `orchestration/SETUP.md:39-42` -- manual install requirement with no validation

**Suggested fix**: Add a preflight check to Quick Setup or `sync-to-claude.sh`:
```bash
[ -f ~/.claude/agents/code-reviewer.md ] || echo "WARNING: code-reviewer.md missing"
```

---

### RC-7: Placeholder notation inconsistency across documentation
**Priority**: P3
**Root cause**: Multiple placeholder conventions coexist (`${VAR}`, `{PLACEHOLDER}`, `{{SLOT_NAME}}`, `{timestamp}`, `<angle-bracket>`) without clear differentiation rules. The RULES.md Hard Gates table uses `{timestamp}` (informal prose notation) which could be confused with actual template placeholders.

**Merged findings**:
- **CL-13** (Clarity, P3): `orchestration/RULES.md:303-309` -- `{timestamp}` lowercase in table uses ambiguous brace notation
- **CL-05** (Clarity, P3): `CONTRIBUTING.md:114` -- "Check 4" should be labeled "CCO Check 4" consistently
- **CL-06** (Clarity, P3): `CONTRIBUTING.md:115-116` -- inconsistent formatting of file references vs checkpoint names

**Merge rationale**: CL-13, CL-05, and CL-06 all stem from the same root cause: no unified naming/notation convention has been enforced across cross-references and placeholders. CL-05 and CL-06 are about inconsistent labeling of checkpoints and file references in the same file; CL-13 is about ambiguous placeholder notation. All trace to the lack of a style guide for these cross-reference patterns.

**Affected surfaces**:
- `orchestration/RULES.md:303-309` -- `{timestamp}` ambiguous notation
- `CONTRIBUTING.md:114` -- "Check 4" missing "CCO" prefix
- `CONTRIBUTING.md:115-116` -- mixed formatting for file refs vs checkpoint names

**Suggested fix**: Replace `{timestamp}` with `<timestamp>` in prose contexts. Standardize checkpoint labels to include the checkpoint name prefix (e.g., "CCO Check 4"). Apply consistent formatting for file references.

---

### RC-8: SESSION_PLAN_TEMPLATE.md example values not clearly marked as examples
**Priority**: P3
**Root cause**: Template example content (time estimates, pseudocode) is not clearly distinguished from fill-in-the-blank placeholders, creating a risk that users copy verbatim values or misunderstand the API.

**Merged findings**:
- **CL-20** (Clarity, P3): `orchestration/templates/SESSION_PLAN_TEMPLATE.md:74` -- specific time estimates filled in as examples without "example" label
- **CL-23** (Clarity, P3): `orchestration/templates/SESSION_PLAN_TEMPLATE.md:153-164` -- Python pseudocode with `background=True` contradicts CLAUDE.md prohibition
- **CL-19** (Clarity, P3): `orchestration/templates/SESSION_PLAN_TEMPLATE.md:45-46` -- emoji usage inconsistent with rest of orchestration docs

**Merge rationale**: All three are issues within SESSION_PLAN_TEMPLATE.md where the template content does not clearly distinguish example/illustrative content from operational placeholders. CL-20 has time estimates that look like real values, CL-23 has pseudocode that misrepresents the actual API and includes a banned parameter, and CL-19 uses a visual convention (emoji) inconsistent with the rest of the system. Same root cause: template authoring did not consistently mark example vs. operational content.

**Affected surfaces**:
- `orchestration/templates/SESSION_PLAN_TEMPLATE.md:45-46` -- emoji severity indicators
- `orchestration/templates/SESSION_PLAN_TEMPLATE.md:74` -- time estimate examples
- `orchestration/templates/SESSION_PLAN_TEMPLATE.md:153-164` -- pseudocode with banned `background=True`

**Suggested fix**: Replace time estimates with `___ min` placeholders. Add a note that pseudocode is conceptual and `background=True` must not be used. Replace emoji with plain-text labels (HIGH/MED/LOW).

---

### RC-9: Documentation self-contradictions in SETUP.md
**Priority**: P3
**Root cause**: SETUP.md contains forward references to content that does not exist and contradictory descriptions of file locations.

**Merged findings**:
- **CL-14** (Clarity, P3): `orchestration/SETUP.md:5` -- promises "backup, and uninstall documentation" that doesn't exist
- **CL-15** (Clarity, P3): `orchestration/SETUP.md:36` -- "original repository's `~/.claude/agents/`" is contradictory (not a repo path)

**Merge rationale**: Both findings are self-contradictions within SETUP.md where the text promises or references something that does not match reality. Same root cause: SETUP.md prose was not validated against actual content and filesystem structure.

**Affected surfaces**:
- `orchestration/SETUP.md:5` -- missing backup/uninstall sections
- `orchestration/SETUP.md:36` -- contradictory "repository" reference to a per-machine path

**Suggested fix**: Remove "backup, and uninstall" from the intro sentence. Rewrite the code-reviewer path description to say "on the machine where the system was first configured, at `~/.claude/agents/code-reviewer.md`".

---

### RC-10: Hardcoded line references drift as files grow
**Priority**: P3
**Root cause**: Cross-file references use hardcoded line numbers that become stale as target files are edited.

**Merged findings**:
- **DRIFT-003** (Drift, P3): `CONTRIBUTING.md:42` -- line range "77-85" for GLOSSARY Ant Metaphor Roles table is now off (table ends at line 87)
- **DRIFT-004** (Drift, P3): `orchestration/GLOSSARY.md:58` -- pre-push hook description omits `scripts/` rsync exclusion

**Merge rationale**: Both are minor cross-file reference drift. DRIFT-003 is a stale line number hint; DRIFT-004 is an incomplete description of sync behavior. Both stem from the same root cause: incremental edits to target files invalidated cross-references in other files.

**Affected surfaces**:
- `CONTRIBUTING.md:42` -- stale line range "77-85" for GLOSSARY table
- `orchestration/GLOSSARY.md:58` -- missing `scripts/` from rsync exclusion description

**Suggested fix**: Update CONTRIBUTING.md line range or remove hardcoded line numbers. Add `scripts/` to the GLOSSARY rsync exclusion description.

---

### RC-11: Missing guards on critical setup paths
**Priority**: P3
**Root cause**: Failures in setup/initialization are either silent or discovered only after significant downstream work has been done.

**Merged findings**:
- **EC-04** (Edge Cases, P3): `orchestration/RULES.md:383` -- no guard on empty SESSION_DIR before `mkdir -p`
- **EC-08** (Edge Cases, P3): `orchestration/RULES.md:88-98` -- no retry limit for SSV->Scout->SSV loop

**Merge rationale**: Both findings involve missing defensive guards in the setup/initialization path. EC-04 could create directories at filesystem root if SESSION_DIR is empty. EC-08 could loop indefinitely if SSV keeps failing. Same root cause: insufficient fail-fast guards before downstream work begins.

**Affected surfaces**:
- `orchestration/RULES.md:383` -- mkdir without SESSION_DIR guard
- `orchestration/RULES.md:88-98` -- SSV retry loop without count limit

**Suggested fix**: Add `[[ -z "${SESSION_DIR}" ]] && exit 1` guard. Add SSV retry limit to the Retry Limits table (e.g., "SSV fails after Scout revision: 1").

---

### RC-12: Minor style and organization inconsistencies (organic evolution)
**Priority**: P3
**Root cause**: Documentation evolved organically without a consistent style guide. Multiple minor formatting, labeling, and organizational inconsistencies exist across files.

**Merged findings**:
- **CL-01** (Clarity, P3): `CLAUDE.md:38` -- mixed bold+caps vs caps-only in prohibition list
- **CL-02** (Clarity, P3): `CLAUDE.md:56` -- near-duplicate sentence with different casing
- **CL-03** (Clarity, P3): `CONTRIBUTING.md:44` -- One-TeamCreate constraint buried in agent-specific subsection
- **CL-07** (Clarity, P3): `CONTRIBUTING.md:165` -- comment claims simpler approach used but adjacent code uses "old" approach
- **CL-11** (Clarity, P3): `orchestration/RULES.md:197` -- round 1 team unnamed; round 2+ named
- **CL-12** (Clarity, P3): `orchestration/RULES.md:212-246` -- sunset clause buried at end of step
- **CL-16** (Clarity, P3): `orchestration/SETUP.md:63` -- checkbox format for non-interactive content
- **CL-17** (Clarity, P3): `orchestration/templates/scout.md:11-13` -- inconsistent depth of inline definitions
- **CL-18** (Clarity, P3): `orchestration/templates/scout.md:119-121` -- letter-based sub-step labels unique to this step
- **EC-02** (Edge Cases, P3): `orchestration/RULES.md:227-237` -- tmux send-keys failure path undocumented (low impact, sunset clause)
- **EC-05** (Edge Cases, P3): `orchestration/templates/scout.md:266-289` -- bd show failure fallback references bd list output that may not exist in all modes

**Merge rationale**: These 11 findings are individually minor style, organization, or documentation precision issues. None share a specific code path or pattern with each other -- they are grouped here because they all stem from the same meta-cause: organic doc evolution without style guide enforcement. Each is a small polish item. Filing them as one composite issue prevents 11 separate P3 beads while preserving the full list of affected surfaces.

**Affected surfaces**: See individual finding descriptions above for file:line locations.

**Suggested fix**: Address as part of a documentation style guide enforcement pass. Individual fixes are described in the original reviewer reports.

---

## Severity Conflicts

No severity conflicts exist. No root cause group had reviewers disagreeing by 2+ levels. The only overlaps between reviewers were:
- RC-1: Clarity assessed surfaces at P3; Drift assessed the root cause at P2. This is a 1-level difference (within tolerance), and the root cause grouping correctly elevates to P2.
- RC-2: Clarity assessed at P3 (and deferred to Drift); Drift assessed at P2. Again a 1-level difference, within tolerance.

---

## Deduplication Log

| Raw Finding | Source | Root Cause Group | Rationale |
|-------------|--------|-----------------|-----------|
| CL-01 | Clarity | RC-12 | Minor style inconsistency |
| CL-02 | Clarity | RC-12 | Minor style inconsistency |
| CL-03 | Clarity | RC-12 | Organizational issue |
| CL-04 | Clarity | RC-1 | Pantry deprecation not propagated |
| CL-05 | Clarity | RC-7 | Naming/notation inconsistency |
| CL-06 | Clarity | RC-7 | Cross-reference formatting inconsistency |
| CL-07 | Clarity | RC-12 | Code/comment mismatch |
| CL-08 | Clarity | RC-1 | Pantry deprecation not propagated |
| CL-09 | Clarity | RC-1 | Pantry deprecation not propagated |
| CL-10 | Clarity | RC-4 | Dual timestamp naming |
| CL-11 | Clarity | RC-12 | Minor style inconsistency |
| CL-12 | Clarity | RC-12 | Organizational issue |
| CL-13 | Clarity | RC-7 | Placeholder notation ambiguity |
| CL-14 | Clarity | RC-9 | SETUP.md self-contradiction |
| CL-15 | Clarity | RC-9 | SETUP.md self-contradiction |
| CL-16 | Clarity | RC-12 | Minor style inconsistency |
| CL-17 | Clarity | RC-12 | Minor style inconsistency |
| CL-18 | Clarity | RC-12 | Minor style inconsistency |
| CL-19 | Clarity | RC-8 | Template example vs. operational content |
| CL-20 | Clarity | RC-8 | Template example vs. operational content |
| CL-21 | Clarity | RC-3 | Stale template contradicting RULES.md |
| CL-22 | Clarity | RC-3 | Stale template contradicting RULES.md |
| CL-23 | Clarity | RC-8 | Template example vs. operational content |
| CL-24 | Clarity | RC-2 | README missing SSV checkpoint |
| CL-25 | Clarity | RC-1 | Pantry deprecation not propagated |
| EC-01 | Edge Cases | RC-5 | macOS shell incompatibility |
| EC-02 | Edge Cases | RC-12 | Minor doc precision issue |
| EC-03 | Edge Cases | RC-5 | macOS shell incompatibility |
| EC-04 | Edge Cases | RC-11 | Missing setup guard |
| EC-05 | Edge Cases | RC-12 | Minor doc precision issue |
| EC-06 | Edge Cases | RC-6 | Missing preflight validation |
| EC-07 | Edge Cases | RC-5 | macOS shell incompatibility |
| EC-08 | Edge Cases | RC-11 | Missing setup guard |
| F-001 | Correctness | (excluded) | Not a defect -- scoping check, explicitly "no action required" |
| DRIFT-001 | Drift | RC-1 | Pantry deprecation not propagated |
| DRIFT-002 | Drift | RC-2 | README missing SSV checkpoint |
| DRIFT-003 | Drift | RC-10 | Hardcoded line reference drift |
| DRIFT-004 | Drift | RC-10 | Hardcoded line reference drift |

**Raw findings in**: 37 (25 Clarity + 8 Edge Cases + 0 Correctness defects + 4 Drift)
**Findings excluded**: 1 (F-001: not a defect)
**Findings consolidated**: 36 -> 12 root cause groups

---

## Cross-Session Dedup Log

Checked all 12 root cause groups against existing open beads (`bd list --status=open -n 0`):

| RC | Title | Existing Bead Match | Action |
|----|-------|-------------------|--------|
| RC-1 | Pantry-review deprecation not fully propagated | No exact match. `ant-farm-bo7d` and `ant-farm-gl11` cover "pantry.md Section 2 deprecation notice" but are scoped to pantry.md, not the cross-file reader attribution surfaces. `ant-farm-e66h`/`ant-farm-onmp` cover pantry.md signal words. These are different surfaces. | FILE NEW |
| RC-2 | README Hard Gates table missing SSV | `ant-farm-aozr` exists: "README Hard Gates table stale for WWD". Similar but covers WWD, not SSV. Different checkpoint. | FILE NEW |
| RC-3 | SESSION_PLAN_TEMPLATE stale decision logic | `ant-farm-pxsk` exists: "SESSION_PLAN_TEMPLATE stale hardcoded values (model name, token budget, emoji)". Different surfaces -- pxsk covers model name/token budget/emoji, RC-3 covers review decision thresholds and review wave model. | FILE NEW |
| RC-4 | Dual TIMESTAMP/REVIEW_TIMESTAMP naming | No match found in existing beads. | FILE NEW |
| RC-5 | macOS shell incompatibility in RULES.md | `ant-farm-8y39` exists: "RULES.md: mixed [[ and [ bracket styles in validation block". Related (shell style) but different root cause (bracket styles vs. GNU/BSD portability). | FILE NEW |
| RC-6 | Missing preflight for code-reviewer.md | No match found. | FILE NEW |
| RC-7 | Placeholder notation inconsistency | `ant-farm-0zws` (epic: Placeholder Conventions Cleanup) exists with many children. RC-7's CL-13 (placeholder in prose) partially overlaps. However, CL-05 and CL-06 (checkpoint labeling) are not placeholder issues per se. | FILE NEW (broader scope than existing placeholder epic children) |
| RC-8 | SESSION_PLAN_TEMPLATE example values unmarked | `ant-farm-pxsk` partially overlaps (emoji is in both). But RC-8 covers time estimates and pseudocode too. | FILE NEW |
| RC-9 | SETUP.md self-contradictions | `ant-farm-h41z` exists: "SETUP.md references wrong path for SESSION_PLAN_TEMPLATE.md". Different surface. `ant-farm-q3o6`/`ant-farm-y719`: "SETUP.md duplicate/overlapping content". Different issue. | FILE NEW |
| RC-10 | Hardcoded line references drift | `ant-farm-9d4e` exists: "Fragile numeric step references in cross-file template links". After review, ant-farm-9d4e covers step number references in templates (pantry.md, big-head-skeleton.md); RC-10 covers hardcoded file line-number ranges in cross-file references (CONTRIBUTING.md -> GLOSSARY.md) and incomplete sync descriptions. Different surfaces and different fix patterns. | FILE NEW |
| RC-11 | Missing guards on setup paths | No exact match. `ant-farm-ch3m` covers "Session state bootstrapping gap" but is about queen-state.md, not SESSION_DIR guard or SSV retry limit. | FILE NEW |
| RC-12 | Minor style and organization inconsistencies | No single bead covers this composite. Various individual beads cover specific style issues in specific files, but none cover this cross-cutting composite. | FILE NEW |

**To file**: RC-1 through RC-12 (12 new beads)
**Skipped**: none

---

## Priority Breakdown

| Priority | Count | Root Cause Groups |
|----------|-------|-------------------|
| P2 | 6 | RC-1, RC-2, RC-3, RC-4, RC-5, RC-6 |
| P3 | 6 | RC-7, RC-8, RC-9, RC-10, RC-11, RC-12 |
| **Total** | **12** | 12 to file |

---

## Priority Calibration Note

6 of 12 root causes are P2. This is higher than the typical "most findings should be P3" baseline, but is justified:
- RC-1 and RC-2 are stale documentation that would actively mislead operators
- RC-3 has wrong decision thresholds that could cause a developer to skip required fix cycles
- RC-4 creates ongoing cognitive burden for every workflow participant
- RC-5 has a silent failure on the documented platform (macOS) that weakens uniqueness guarantees
- RC-6 has a failure mode that wastes hours of session time before discovery

None of these warrant P1 (no runtime crashes, data loss, or security issues). The P2 assessment reflects "would actively mislead an operator or cause significant rework."

---

## Bead Filing Log

All 12 beads filed after Pest Control CCB PARTIAL verdict and Queen authorization.

| RC | Bead ID | Priority | Label | Title |
|----|---------|----------|-------|-------|
| RC-1 | ant-farm-2yww | P2 | drift | Pantry-review deprecation not fully propagated to reader attributions |
| RC-2 | ant-farm-80l0 | P2 | drift | README Hard Gates table missing SSV checkpoint |
| RC-3 | ant-farm-tour | P2 | clarity | SESSION_PLAN_TEMPLATE stale review decision logic contradicts RULES.md |
| RC-4 | ant-farm-q84z | P2 | clarity | Dual TIMESTAMP/REVIEW_TIMESTAMP naming convention creates cognitive burden |
| RC-5 | ant-farm-zg7t | P2 | edge-cases | macOS (Darwin) incompatible shell commands in RULES.md |
| RC-6 | ant-farm-sje5 | P2 | edge-cases | Missing preflight validation for required code-reviewer.md agent |
| RC-7 | ant-farm-8awb | P3 | clarity | Placeholder notation and cross-reference labeling inconsistency |
| RC-8 | ant-farm-8qgy | P3 | clarity | SESSION_PLAN_TEMPLATE example values not clearly marked as examples |
| RC-9 | ant-farm-dxia | P3 | clarity | SETUP.md self-contradictions: missing sections and contradictory path description |
| RC-10 | ant-farm-4qjl | P3 | drift | Hardcoded line references and incomplete sync descriptions drift |
| RC-11 | ant-farm-jnjs | P3 | edge-cases | Missing guards on critical setup paths: SESSION_DIR and SSV retry |
| RC-12 | ant-farm-nuc1 | P3 | clarity | Minor style and organization inconsistencies across documentation (composite) |

**Summary**: 12 beads filed (6 P2, 6 P3). 0 skipped.

---

## Overall Verdict

**PASS WITH ISSUES**

- 0 P1 findings
- 6 P2 root causes (documentation drift, platform incompatibility, missing preflight)
- 6 P3 root causes (style, organization, minor drift, setup guards)
- All 12 acceptance criteria from the correctness review PASS
- The codebase is functionally correct; all findings are in documentation and shell snippet portability
- 12 beads filed with full traceability from raw findings to root cause groups to bead IDs

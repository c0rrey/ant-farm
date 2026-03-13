# Final Triage Report — Ant-Farm Bead Audit

**Date generated**: 2026-02-22
**Session**: _session-39adef65 (audit epic ant-farm-v2h1)
**Scope**: All 176 beads in the system (168 non-epic + 8 epics)

---

## Executive Summary

| Category | Count |
|---|---|
| Epics (noted, not triaged) | 8 |
| STILL_VALID (open, needs work) | 113 |
| ALREADY_FIXED (close) | 16 |
| DUPLICATE_SUSPECT (close these beads) | 36 |
| IRRELEVANT (close as not applicable) | 3 |
| **Non-epic reviewed beads (batches A-I)** | **168** |
| **+ Epics from pass0-epics-skip.json** | **8** |
| **Grand total** | **176** |

**Math verification**: Each of the 168 non-epic beads received exactly one verdict. 113 + 16 + 36 + 3 = 168. Plus 8 epics = 176. Consistent.

**Key counts**:
- 8 epics noted from pass0-epics-skip.json
- 16 exact duplicate pairs identified in pass0-exact-dupes.json (32 beads, both sides appeared in batch outputs)
- 168 non-epic beads reviewed across batches A through I
- 176 total beads accounted for (168 + 8 epics)

**Reconciliation note**: No bead ID is missing from this report. All 168 non-epic batch entries are listed in the sections below, with each receiving one of: STILL_VALID, ALREADY_FIXED, DUPLICATE_SUSPECT, or IRRELEVANT.

---

## Pass 0: Exact Duplicate Pairs

The following 16 pairs were identified in pass0-exact-dupes.json as having identical titles. Each pair was reviewed in the batch outputs. Recommendation: close the "close" bead in each pair and retain the "keep" bead for resolution.

| Keep (canonical) | Close (duplicate) | Title | Underlying Status |
|---|---|---|---|
| ant-farm-0jn7 | ant-farm-zv46 | README.md architecture diagram does not capture Pest Control dual role | STILL_VALID (in keep bead) |
| ant-farm-32r8 | ant-farm-i9y5 | Bead metadata / traceability inconsistencies (commit msg, acceptance criteria, line numbers) | STILL_VALID (in keep bead — see Batch I) |
| ant-farm-w6lr | ant-farm-456u | parse-progress-log.sh trap ordering -- trap installed after map_init | STILL_VALID (in keep bead) |
| ant-farm-4lcv | ant-farm-c1n2 | README.md deprecated agent row inconsistently formatted | STILL_VALID (in keep bead) |
| ant-farm-n0dw | ant-farm-4ome | reviews.md polling loop angle-bracket placeholders lack explanatory comment | STILL_VALID (in keep bead) |
| ant-farm-wlo4 | ant-farm-4u4s | pantry-review.md (archived) tense inconsistency | DUPLICATE_SUSPECT — see notes |
| ant-farm-58f1 | ant-farm-hpgz | compose-review-skeletons.sh slot marker comment omits TASK_IDS | ALREADY_FIXED in merged script |
| ant-farm-66gl | ant-farm-bkco | Future Work | ant-farm-66gl is the epic; ant-farm-bkco is IRRELEVANT (per Batch I) |
| ant-farm-9hxz | ant-farm-h41z | SETUP.md references wrong path for SESSION_PLAN_TEMPLATE.md | STILL_VALID (in keep bead) |
| ant-farm-gl11 | ant-farm-bo7d | pantry.md Section 2 deprecation notice insufficiently prominent | STILL_VALID (in keep bead) |
| ant-farm-c606 | ant-farm-wqkm | compose-review-skeletons.sh no SESSION_DIR existence check before mkdir -p | STILL_VALID — migrated to build-review-prompts.sh |
| ant-farm-dsaa | ant-farm-o7ji | parse-progress-log.sh UNREACHABLE comment reasoning incomplete | Both DUPLICATE_SUSPECT; underlying ALREADY_FIXED (see 9p4i) |
| ant-farm-e66h | ant-farm-onmp | pantry.md fail-fast conditions use inconsistent signal words | STILL_VALID (in keep bead) |
| ant-farm-z1qp | ant-farm-ees2 | compose-review-skeletons.sh exit 1 in || block redundant with set -euo pipefail | STILL_VALID — migrated to build-review-prompts.sh |
| ant-farm-w1w8 | ant-farm-ek7x | reviews.md section ordering -- Round-Aware Protocol placed after sections that reference it | STILL_VALID (in keep bead) |
| ant-farm-q3o6 | ant-farm-y719 | SETUP.md duplicate/overlapping content between Quick Setup and Recipe Card | STILL_VALID (in keep bead) |

**Note on wlo4/4u4s pair**: The batch analysis concluded this underlying issue may be IRRELEVANT since pantry-review.md is archived, but kept as DUPLICATE_SUSPECT pending team decision. Both beads are low-value targets.

**Note on dsaa/o7ji pair**: Both are duplicates of each other AND both are substantively resolved by the current parse-progress-log.sh UNREACHABLE comment. Recommend closing all three (dsaa, o7ji, and the canonical 9p4i is ALREADY_FIXED).

---

## Pass 0: Epics (Noted, Not Triaged)

These 8 epic IDs were skipped during Pass 1 review. They serve as containers for child tasks and are not bugs/features themselves.

| Epic ID | Title |
|---|---|
| ant-farm-0zws | Placeholder Conventions Cleanup |
| ant-farm-2em7 | Documentation & Setup |
| ant-farm-5eul | Orchestration Workflow Polish |
| ant-farm-66gl | Future Work |
| ant-farm-908t | Audit Findings: Orchestration Documentation Drift |
| ant-farm-apws | Pantry & Scout Template Polish |
| ant-farm-aqgd | Shell Script Fixes |
| ant-farm-qp1j | Review Pipeline Polish |

---

## ALREADY_FIXED (16 beads — close these)

These beads describe issues that have been resolved. No action needed on the code; only close the bead.

| Bead ID | Title | Evidence Summary |
|---|---|---|
| ant-farm-r4qj | RULES.md Step 3b-i timestamp format lacks explicit shell variable assignment example | Fixed by commit 5dba086; TIMESTAMP=$(date +%Y%m%d-%H%M%S) now present at RULES.md line 151 |
| ant-farm-t6f | PLACEHOLDER_CONVENTIONS.md not cross-referenced from RULES.md or any template | Fixed by commit d4aa294; RULES.md lines 147-148 now cross-reference PLACEHOLDER_CONVENTIONS.md |
| ant-farm-164n | Dual placeholder conventions for round-conditional blocks | pantry.md no longer uses structural placeholder markers; fixed by commit 1b0037e |
| ant-farm-t7sd | pantry.md references undefined 'two-script approach' | Fixed by commit 1b0037e; now reads 'superseded by `scripts/build-review-prompts.sh`' |
| ant-farm-zvl | Pantry review mode has no fail-fast for empty changed-file list | Fixed by commit 6b26beb; GUARD block present at pantry.md lines 238-250 |
| ant-farm-5n8h | compose-review-skeletons.sh: sed regex comment says 2+ chars but matches 1+ | Resolved by script merger (commit 1b0037e); old script eliminated, new awk approach has no such comment |
| ant-farm-ew0 | big-head-skeleton.md cross-references reviews.md line 322 but model is at line 323 | Fixed; big-head-skeleton.md now uses section name instead of line number |
| ant-farm-igem | compose-review-skeletons.sh: document single-delimiter assumption for future skeleton files | Resolved by script merger (commit 1b0037e); old script eliminated |
| ant-farm-ot9d | CCB Check 7 O(N) bead scan not scoped to session-created beads | Fixed; checkpoints.md line 574 now uses `--after={SESSION_START_DATE}` parameter |
| ant-farm-1yl | PLACEHOLDER_CONVENTIONS.md shell example uses unquoted SESSION_DIR variable | Fixed; both SESSION_DIR usages are correctly double-quoted in current file |
| ant-farm-3a0 | PLACEHOLDER_CONVENTIONS.md Tier 2 {session-dir} vs Tier 1 {SESSION_DIR} naming ambiguity | Fixed; Tier 2 section now explicitly defines the relationship between both forms |
| ant-farm-zyxs | New documents (GLOSSARY, PLACEHOLDER_CONVENTIONS, SESSION_PLAN) missing from README File Reference | Fixed by commit 07ec281b; all three documents listed in README File Reference |
| ant-farm-0t31 | fill-review-slots.sh: fill_all_slots block comment describes wrong map format | Resolved by script merger (commit 1b0037e); fill-review-slots.sh eliminated |
| ant-farm-2585 | fill-review-slots.sh: undocumented assumptions in fill_all_slots (tabs in paths, printf %b) | Resolved by script merger (commit 1b0037e); fill-review-slots.sh eliminated |
| ant-farm-9p4i | parse-progress-log.sh: dead branch comment could be more precise | Fixed; lines 210-212 now contain precise two-part reasoning for the UNREACHABLE branch |
| ant-farm-yzj | SETUP.md nested code fences break standard markdown rendering | Fixed; outer fence uses 4 backticks correctly when inner content has 3 backticks |

**Bead list** (16 total): r4qj, t6f, 164n, t7sd, zvl, 5n8h, ew0, igem, ot9d, 1yl, 3a0, zyxs, 0t31, 2585, 9p4i, yzj.

---

## IRRELEVANT (3 beads — close as not applicable)

These beads describe issues that are no longer applicable.

| Bead ID | Title | Reason |
|---|---|---|
| ant-farm-t1ex | pantry-review.md self-validation checklist lacks remediation guidance per item | File is archived and frozen; agents must not follow it. No operational benefit to fixing. |
| ant-farm-bkco | Future Work | This is an epic container (meta-issue), not an actionable bead. Tracked under ant-farm-66gl (identical title, same purpose). |
| ant-farm-xvmn | Explore tmux-based agent spawning for real-time observability | Feature exploration marked P4; existing tmux usage in RULES.md already handles the narrow dummy-reviewer case. This is future research, not a current gap requiring action. |

---

## DUPLICATE_SUSPECT (36 beads — close duplicates, keep canonicals)

These beads have identical or near-identical titles. The recommended action is to close the listed bead and keep the canonical version.

### Exact title duplicates from Pass 0 (close the "close" column bead)

| Close This | Keep This | Title |
|---|---|---|
| ant-farm-zv46 | ant-farm-0jn7 | README.md architecture diagram does not capture Pest Control dual role |
| ant-farm-i9y5 | ant-farm-32r8 | Bead metadata / traceability inconsistencies |
| ant-farm-456u | ant-farm-w6lr | parse-progress-log.sh trap ordering |
| ant-farm-c1n2 | ant-farm-4lcv | README.md deprecated agent row inconsistently formatted |
| ant-farm-4ome | ant-farm-n0dw | reviews.md polling loop angle-bracket placeholders |
| ant-farm-4u4s | ant-farm-wlo4 | pantry-review.md (archived) tense inconsistency |
| ant-farm-hpgz | ant-farm-58f1 | compose-review-skeletons.sh slot marker comment omits TASK_IDS |
| ant-farm-h41z | ant-farm-9hxz | SETUP.md references wrong path for SESSION_PLAN_TEMPLATE.md |
| ant-farm-bo7d | ant-farm-gl11 | pantry.md Section 2 deprecation notice insufficiently prominent |
| ant-farm-wqkm | ant-farm-c606 | compose-review-skeletons.sh no SESSION_DIR existence check |
| ant-farm-o7ji | ant-farm-dsaa | parse-progress-log.sh UNREACHABLE comment reasoning incomplete |
| ant-farm-onmp | ant-farm-e66h | pantry.md fail-fast conditions use inconsistent signal words |
| ant-farm-ees2 | ant-farm-z1qp | compose-review-skeletons.sh exit 1 in || block redundant |
| ant-farm-ek7x | ant-farm-w1w8 | reviews.md section ordering -- Round-Aware Protocol placed after sections that reference it |
| ant-farm-y719 | ant-farm-q3o6 | SETUP.md duplicate/overlapping content between Quick Setup and Recipe Card |
| ant-farm-dsaa | ant-farm-o7ji | parse-progress-log.sh UNREACHABLE comment (NOTE: dsaa and o7ji are each other's duplicates; close both; underlying fixed by 9p4i) |

### Additional duplicates identified during Pass 1

| Close This | Keep This | Title / Note |
|---|---|---|
| ant-farm-a4s | ant-farm-28fl | Angle-bracket placeholder convention not documented (sub-issue of 28fl) |
| ant-farm-w6m | ant-farm-28fl | PLACEHOLDER_CONVENTIONS.md does not document angle-bracket syntax (sub-issue of 28fl) |
| ant-farm-t0n | ant-farm-nx31 | PLACEHOLDER_CONVENTIONS.md enforcement strategy mixes completed and aspirational items (near-duplicate of nx31) |
| ant-farm-56ue | ant-farm-nnf7 | extract_agent_section "exactly one delimiter" assumption unguarded (56ue is older; keep 56ue, close nnf7) |
| ant-farm-nnf7 | ant-farm-56ue | (see above — close nnf7) |
| ant-farm-e5o | ant-farm-bnyn | Installation guide verification test leaves docs/test.md committed (e5o is older but bnyn has more precise line refs; team to decide; both describe same root cause) |

**Note on 56ue/nnf7**: ant-farm-56ue was created 2026-02-21, ant-farm-nnf7 on 2026-02-22. Recommend keeping ant-farm-56ue (older) and closing ant-farm-nnf7.

**Note on e5o/bnyn**: ant-farm-e5o was created 2026-02-18 (older, canonical), ant-farm-bnyn was created 2026-02-21 (newer, more precise). Recommend keeping ant-farm-e5o and closing ant-farm-bnyn, but noting that bnyn has the correct line references.

---

## STILL_VALID (113 beads — organized by epic)

These beads remain open and require work. Organized by the epic they are assigned to for easy scanning. P2 items are marked.

Note: Some beads are cross-assigned to multiple epics; those appear in both relevant sections with "(also listed under...)" notation but are counted as one bead each.

### Epic: ant-farm-908t — Audit Findings: Orchestration Documentation Drift

| Bead ID | Title | Priority | Notes |
|---|---|---|---|
| ant-farm-0bez | fix: GLOSSARY pre-push hook entry omits sync-to-claude.sh details | P3 | GLOSSARY.md cosmetic gap |
| ant-farm-geou | fix: document artifact naming convention transition point for historical sessions | **P2** | checkpoints.md missing historical naming transition note; causes confusion auditing old sessions |
| ant-farm-ng0e | fix: DMVDC Nitpicker artifact naming in checkpoints.md does not match actual filenames | **P2** | Real query failures result from mismatch; checkpoints.md:475 |
| ant-farm-sd12 | fix: remove archived pantry-review from scout.md exclusion list | P3 | scout.md:63 references archived pantry-review |

### Epic: ant-farm-apws — Pantry & Scout Template Polish

| Bead ID | Title | Priority | Notes |
|---|---|---|---|
| ant-farm-3ysr | Pantry guard edge cases: whitespace handling and contamination detection carve-out | P3 | Low confidence; tab/space whitespace edge case |
| ant-farm-4ki0 | TOCTOU race: Pantry fail-fast metadata check may read partially-written Scout file | P3 | Theoretical; near-zero operational probability |
| ant-farm-6e1 | Pantry 'report to Queen immediately' misleading for Task subagent model | P3 | pantry.md line 45 wording issue |
| ant-farm-gf80 | Pantry empty file list guard does not validate that listed files exist on disk | P3 | One-line clarifying note needed |
| ant-farm-gl11 | pantry.md Section 2 deprecation notice insufficiently prominent | P3 | 189 lines of deprecated content follow sparse notice |
| ant-farm-oluh | Pantry partial verdict table placement ambiguous -- per-failure or end-of-loop | P3 | pantry.md lines 83-89 restructuring needed |
| ant-farm-ppey | Incomplete failure paths in agent protocols: Big Head escalation, Nitpicker missing brief, Pantry error handling | P3 | Medium confidence; multi-surface bead |
| ant-farm-qql | Pantry fail-fast check uses redundant 'missing, does not exist' phrasing | P3 | Medium confidence; minor phrasing cleanup |
| ant-farm-sycy | Pantry failure artifact path collision across conditions for same task | P3 | All three conditions write to same path; low probability collision |
| ant-farm-wlo4 | pantry-review.md (archived) tense inconsistency | P3 | May be IRRELEVANT since file is archived; team to decide |
| ant-farm-xdw3 | Pantry fail-fast says Halt but behavior is skip-to-next-task | P3 | pantry.md line 45 wording contradiction |
| ant-farm-e66h | pantry.md fail-fast conditions use inconsistent signal words (canonical) | P3 | Signal word inconsistency: Halt / Do not proceed / skip |

### Epic: ant-farm-aqgd — Shell Script Fixes

| Bead ID | Title | Priority | Notes |
|---|---|---|---|
| ant-farm-5365 | fix: scrub-pii.sh and pre-commit hook not described in SETUP.md or README.md | P3 | Documentation gap; install-hooks.sh header has info but SETUP.md/README do not |
| ant-farm-71ye | install-hooks.sh: pre-commit backup cp lacks error handling (asymmetric with pre-push) | P3 | Cosmetic asymmetry; set -euo pipefail provides safety net |
| ant-farm-w2gj | scrub-pii.sh: perl \\s* vs grep [[:space:]]* pattern divergence (cosmetic) | P3 | Cosmetic; both patterns match same input |
| ant-farm-w6lr | parse-progress-log.sh trap ordering -- trap installed after map_init (canonical) | P3 | trap registered after map_init at lines 165-166 |
| ant-farm-c606 | compose-review-skeletons.sh no SESSION_DIR existence check before mkdir -p (canonical — gap migrated to build-review-prompts.sh) | P3 | Gap present in build-review-prompts.sh lines 104-115 |
| ant-farm-z1qp | compose-review-skeletons.sh exit 1 in || block redundant with set -euo pipefail (canonical — gap migrated to build-review-prompts.sh) | P3 | Pattern at build-review-prompts.sh lines 105, 109, 113 |

### Epic: ant-farm-qp1j — Review Pipeline Polish

| Bead ID | Title | Priority | Notes |
|---|---|---|---|
| ant-farm-0bez | (also listed under ant-farm-908t — cross-assigned) | — | — |
| ant-farm-0kwo | nitpicker.md frontmatter description too long; second sentence ignored by Scout | P3 | agents/nitpicker.md:3 |
| ant-farm-0xqf | Skeleton format spec hints do not match Pantry actual output sections | P3 | dirt-pusher-skeleton.md, nitpicker-skeleton.md hints vs pantry output |
| ant-farm-10ff | Big Head failure artifact timestamp coexistence under re-spawn not documented | P3 | big-head-skeleton.md; no comment about artifact coexistence after retry |
| ant-farm-1pa0 | Big Head polling loop: single-invocation constraint under-documented and timeout may be too short | P3 | Medium confidence; constraint is inside code block, not surrounding prose |
| ant-farm-1s5k | nitpicker.md NOT YOUR RESPONSIBILITY blocks use inconsistent scope vocabulary | P3 | agents/nitpicker.md:52-56 |
| ant-farm-2r4j | Canonical term definitions copy-pasted across 3 templates with no single source of truth | P3 | dirt-pusher-skeleton.md, big-head-skeleton.md, pantry.md, checkpoints.md |
| ant-farm-3jiq | reviews.md After Consolidation section stranded in file the Queen cannot read | P3 | reviews.md line 1 says Queen does not read it; line 847 says Queen owns this step |
| ant-farm-58f1 | compose-review-skeletons.sh slot marker comment omits TASK_IDS (canonical — see note) | P3 | Underlying issue ALREADY_FIXED by 1b0037e in merged script; however this bead is the canonical of the hpgz/58f1 duplicate pair. Close hpgz as duplicate, then close 58f1 as ALREADY_FIXED. |
| ant-farm-5xo7 | Minor formatting inconsistencies in checkpoints.md, scout.md, big-head-skeleton.md | P3 | Medium confidence; big-head-skeleton.md portion may be fixed |
| ant-farm-6i1 | PLACEHOLDER_CONVENTIONS.md audit claims All Files Pass despite partial nitpicker-skeleton.md | P3 | Medium confidence; related to ant-farm-lbcy |
| ant-farm-93n | big-head.md agent definition lacks cross-reference to reviews.md protocol | P3 | agents/big-head.md has no cross-reference to reviews.md |
| ant-farm-fkfw | Fragile grep-based Future Work epic discovery with no error handling or dedup guard | P3 | reviews.md:788 and big-head-skeleton.md:115 |
| ant-farm-hm05 | Placeholder/term definition block maintenance gaps in templates | P3 | Medium confidence; checkpoints.md SESSION_START_DATE gap still needs verification |
| ant-farm-jss | Read Confirmation finding counts can be copied rather than independently verified | P3 | reviews.md:687-699; no independent count requirement |
| ant-farm-k476 | Failure taxonomy (INFRASTRUCTURE vs SUBSTANCE) not defined in a shared location | P3 | Terms used in pantry.md but defined nowhere central |
| ant-farm-lbcy | fix: double-brace placeholder tier {{SLOT}} absent from PLACEHOLDER_CONVENTIONS.md | **P2** | False PASS in audit table; reviews.md actively uses {{REVIEW_ROUND}} and others |
| ant-farm-ldha | big-head.md references nonexistent P4 severity level | P3 | agents/big-head.md line 14 uses P4 example; project only defines P1/P2/P3 |
| ant-farm-mv6b | SendMessage pseudo-API examples use incorrect parameter names | P3 | reviews.md lines 729-744 use to=/message= instead of recipient=/content= |
| ant-farm-n0dw | reviews.md polling loop angle-bracket placeholders lack explanatory comment (canonical) | P3 | Polling loop lines 532-575 use angle-bracket placeholders without explanatory comment |
| ant-farm-o2zl | Mixed placeholder conventions and minor template polish in reviews.md | P3 | reviews.md line 845 uses {session-dir} while all others use <session-dir> |
| ant-farm-ogyk | reviews.md: REVIEW_ROUND guard relies on LLM interpreting exit code (defense-in-depth note) | P3 | reviews.md lines 502-511; defense-in-depth note absent |
| ant-farm-oi3 | Correctness Redux instructs Nitpickers to run bd show with undocumented tool dependency | P3 | reviews.md lines 312-313; bd tool availability undocumented |
| ant-farm-omwi | dirt-pusher-skeleton.md has policy text embedded in placeholder list | P3 | {AGENT_TYPE} placeholder entry contains multi-line policy prose |
| ant-farm-p0m | big-head.md bd create has no error handling for CLI failures mid-consolidation | P3 | agents/big-head.md step 6; no recovery path for bd create failures |
| ant-farm-ppey | (also listed under ant-farm-apws) | — | — |
| ant-farm-qzj | Read Confirmation table placement and duplication in consolidated summary format | P3 | pantry.md hardcodes 4 report types; wrong for round 2+ |
| ant-farm-retj | nitpicker.md cross-review messaging section placed after per-type blocks | P3 | agents/nitpicker.md (not nitpicker-skeleton.md); placement may still be wrong |
| ant-farm-ut66 | reviews.md: minor comment precision issues in polling loop | P3 | Medium confidence; sparse bead description |
| ant-farm-uu8u | MANDATORY GATE style inconsistency in reviews.md | P3 | reviews.md:459 has only one explicit MANDATORY GATE label |
| ant-farm-w1w8 | reviews.md section ordering -- Round-Aware Protocol placed after sections that reference it (canonical) | P3 | Agent Teams Protocol at line 25 references Round 2+ before Round-Aware Protocol section at line 163 |
| ant-farm-wk1a | Round 2+ scope instructions inconsistently presented between nitpicker-skeleton and reviews.md | P3 | Formal quoted block vs inline conditional sentence |
| ant-farm-x31 | Verification Pipeline Rationale has redundant 'Why both?' paragraph | P3 | Medium confidence; paragraph adds design rationale |
| ant-farm-xyly | Template-to-agent communication gaps: unactionable escalation path and unfilled placeholder | P3 | Medium confidence; title-only bead |

### Epic: ant-farm-5eul — Orchestration Workflow Polish

| Bead ID | Title | Priority | Notes |
|---|---|---|---|
| ant-farm-1r2o | AGENTS.md and CLAUDE.md contain identical content with no sync mechanism documented | P3 | sync-to-claude.sh has no awareness of AGENTS.md |
| ant-farm-bva6 | Cross-file navigation gaps: undeclared sub-step convention, missing path refs, no inline cross-references in checklists | P3 | Medium confidence; title-only bead |
| ant-farm-cfp8 | Documentation polish: minor formatting, redundancy, and structural inconsistencies across orchestration templates | P3 | Low confidence; title-only catch-all bead |
| ant-farm-cqfv | Fallback workflow missing round-awareness for round 2+ | P3 | reviews.md Fallback section (lines 105-149) lacks round 2+ branching |
| ant-farm-f3t0 | queen-state.md fix commit range has no crash-recovery reconstruction guidance | P3 | queen-state.md recovery rule does not address fix commit range reconstruction |
| ant-farm-s7l8 | queen-state.md escalation cap field missing post-decision terminal state | P3 | queen-state.md line 42 has no terminal state after user decides |
| ant-farm-s7vu | Termination Rule wording ambiguity: 'directly' may imply skipping Round 1 P3 handling | P3 | Medium confidence; 'directly' in reviews.md:194 and RULES.md:245 |
| ant-farm-w1dn | Development artifacts left in production templates (NEW annotation, CRITICAL FIX note) | P3 | checkpoints.md lines 155 and 592 |
| ant-farm-x31 | (also listed under ant-farm-qp1j) | — | — |
| ant-farm-xyly | (also listed under ant-farm-qp1j) | — | — |
| ant-farm-z8lq | Review task ID scoping includes out-of-range commits | P3 | RULES.md Step 3b-i; tasks whose fix commits pre-date session first commit should be excluded |

### Epic: ant-farm-0zws — Placeholder Conventions Cleanup

| Bead ID | Title | Priority | Notes |
|---|---|---|---|
| ant-farm-28fl | PLACEHOLDER_CONVENTIONS enforcement incomplete and angle-bracket syntax undocumented | P3 | Covers enforcement gaps AND angle-bracket docs (broadest in this cluster) |
| ant-farm-3yw | PLACEHOLDER_CONVENTIONS.md Compliance Status section is verbose and redundant with audit table | P3 | 45-line section repeats 16-line audit table information |
| ant-farm-d1u | PLACEHOLDER_CONVENTIONS.md audit table line numbers will become stale without commit reference | P3 | No date, version hash, or update instructions in audit table |
| ant-farm-glzg | Placeholder syntax inconsistency: queen-state.md uses angle-brackets while other templates use curly-braces | P3 | queen-state.md mixes angle-bracket and curly-brace syntaxes |
| ant-farm-hpi | Scout {MODE} placeholder parsing convention undocumented for compound modes | P3 | No definition of valid values or compound mode syntax (e.g., 'READY+REVIEW') |
| ant-farm-lc3a | PLACEHOLDER_CONVENTIONS.md audit table lacks update guidance | P3 | No instructions for when to add rows or update line references |
| ant-farm-nx31 | PLACEHOLDER_CONVENTIONS.md enforcement strategy references unimplemented automation | P3 | Items 3 and 4 of enforcement strategy are unimplemented |
| ant-farm-yh4 | PLACEHOLDER_CONVENTIONS.md validation regex Pattern 4 has false negatives for mixed casing | P3 | {myVar} and {mixedCase} patterns evade detection |

### Epic: ant-farm-2em7 — Documentation & Setup

| Bead ID | Title | Priority | Notes |
|---|---|---|---|
| ant-farm-28aq | fix: MEMORY.md references deleted _session-3be37d without noting its absence is expected | P3 | MEMORY.md outside repo; user must edit manually |
| ant-farm-4hj | README fork instructions step 4 lacks actual hook install command | P3 | README.md 'Forking this repo' Step 4 shows comment instead of commands |
| ant-farm-9hxz | SETUP.md references wrong path for SESSION_PLAN_TEMPLATE.md (canonical) | P3 | SETUP.md lines 61 and 121 have wrong path; should be orchestration/templates/ |
| ant-farm-bnyn | Installation guide verification test leaves docs/test.md committed permanently (canonical — close e5o as duplicate) | P3 | docs/installation-guide.md lines 96-104; no cleanup step |
| ant-farm-dwfe | fix: MEMORY.md custom agent minimum file requirements TBD caveat may be stale | P3 | MEMORY.md outside repo; CONTRIBUTING.md warning also missing |
| ant-farm-maml | README.md Dirt Pushers mislabeled as review subagents | P3 | README.md line 41; Dirt Pushers are implementation-only agents |
| ant-farm-pxsk | SESSION_PLAN_TEMPLATE stale hardcoded values (model name, token budget, emoji) | P3 | Boss-Bot term, 200K token budget, and emoji notation stale |
| ant-farm-q3o6 | SETUP.md duplicate/overlapping content between Quick Setup and Recipe Card (canonical) | P3 | SETUP.md lines 38-55 and 87-101 have nearly identical content |
| ant-farm-rhfl | fix: MEMORY.md Project Structure still lists colony-tsa.md as being eliminated | P3 | MEMORY.md outside repo; Project Structure entry contradicts Completed section |
| ant-farm-vvm | SETUP.md Prerequisites section duplicates Quick Setup commands | P3 | SETUP.md lines 9-14 and 24-28 have identical code blocks |

### Epic: ant-farm-apws / ant-farm-qp1j (cross-listed) — Scout Template Polish

| Bead ID | Title | Priority | Notes |
|---|---|---|---|
| ant-farm-a86 | Scout briefing format lacks optional Errors section placement | P3 | scout.md Step 6 template has no Errors section placement guidance |
| ant-farm-cev | Scout ready mode gaps: Step 4 references bd blocked not run, assumption undocumented | P3 | scout.md Step 4:138 references unavailable bd blocked output in ready mode |
| ant-farm-dz4 | dependency-analysis.md says parallel bd show but scout.md uses sequential write-each-immediately | P3 | Contradictory guidance between two files Scout reads |
| ant-farm-hrt | Scout Step 2.5 silently skips agent files with invalid frontmatter | P3 | scout.md:57 says skip with no log/warn instruction |
| ant-farm-jqw | scout.md Step 3 does not explicitly say to continue iteration after bd show failure | P3 | Error handling only at document end; Step 3 prose gap |
| ant-farm-laq | Scout metadata write-each-immediately has no truncation/atomicity check downstream | P3 | No integrity check before downstream Pantry consumption |
| ant-farm-mbbp | Scout Step 5.5 coverage verification missing wave capacity validation | P3 | scout.md Step 5.5 does not check 7-agent max per wave |
| ant-farm-t8cg | scout.md PICK ONE bracket syntax resembles regex/BNF notation | P3 | scout.md lines 121 and 154-155 use [type-a | type-b] bracket notation |

### Epic: ant-farm-5eul / checkpoints (cross-listed) — Checkpoint Gaps

| Bead ID | Title | Priority | Notes |
|---|---|---|---|
| ant-farm-69c6 | Dual-maintenance surface: Pest Control tool list in two files | P3 | checkpoints.md:L17 and README.md:L307 each list independently |
| ant-farm-cozw | CCB reconciliation formula does not detect orphaned merge targets in dedup log | P3 | Medium confidence; edge-case gap in Check 1 counting |
| ant-farm-ve6 | Verification Pipeline no defined precedence when Big Head and CCB checks disagree | P3 | No tie-breaking rule between Big Head and CCB in checkpoints.md |
| ant-farm-zzi0 | bd show failure guard only on DMVDC Check 2, missing from other bd show callsites | P3 | WWD lines 277/294 and CCB Check 2 line 539 lack GUARD blocks |

### Epic: ant-farm-908t (RULES.md cluster)

| Bead ID | Title | Priority | Notes |
|---|---|---|---|
| ant-farm-07ai | Cross-file step numbering mismatch between reviews.md and big-head-skeleton.md | P3 | No mapping note between the two step schemes anywhere in codebase |
| ant-farm-0c28 | WWD mode selection rule missing from checkpoints.md | P3 | checkpoints.md describes modes but omits selection rule |
| ant-farm-19r3 | fix: SESSION_PLAN_TEMPLATE.md uses stale Boss-Bot term and Claude Sonnet 4.5 model | P3 | SESSION_PLAN_TEMPLATE.md lines 8 and 340 still have Boss-Bot |
| ant-farm-70ti | fix: GLOSSARY says 4 checkpoints but framework has 5 (SSV omitted) | **P2** | GLOSSARY.md states 4 checkpoints four times; SSV never mentioned; authoritative doc wrong |
| ant-farm-8y39 | RULES.md: mixed [[ and [ bracket styles in validation block | P3 | RULES.md lines 156-176 mix bash [[ and POSIX [ |
| ant-farm-9dp7 | fix: minor bd prohibition wording drift between CLAUDE.md and RULES.md | P3 | Cosmetic; functionally identical |
| ant-farm-9iyp | fix: remove 3 dead artifact entries from RULES.md Session Directory list | **P2** | briefing.md absent from list despite being referenced at RULES.md:86 and 99 |
| ant-farm-9nws | Retry count asymmetry between RULES.md (1 retry) and reviews.md (2-attempt) undocumented | P3 | Medium confidence; no cross-reference or reconciliation note |
| ant-farm-9s2a | fix: dummy reviewer prompt created but output report never materializes | P3 | RULES.md lines 233-234; sunset clause but no note on non-materializing output |
| ant-farm-a2ot | fix: CONTRIBUTING.md cross-file update checklist omits GLOSSARY.md | P3 | GLOSSARY.md Ant Metaphor Roles table not in CONTRIBUTING.md checklist |
| ant-farm-a87o | fix: CCO artifact naming uses session-wide format in practice but checkpoints.md specifies per-task | **P2** | Spec mismatch misleads future Pest Control agents following checkpoints.md literally |
| ant-farm-aozr | README Hard Gates table stale for WWD | P3 | README.md line 269 still shows old 'Next agent in wave' for WWD Blocks column |
| ant-farm-b89w | [HALF-BAKED] Group co-located tasks into single Dirt Pusher assignments | P3 | Feature request requiring changes across 6+ components; not a documentation fix |
| ant-farm-ch3m | Session state bootstrapping gap: queen-state.md creation not specified in RULES.md Step 0 | P3 | Step 0 does not mention when/how to create queen-state.md |
| ant-farm-d3bk | fix: fill-review-slots.sh @file argument notation undocumented in RULES.md | P3 | @file feature preserved in build-review-prompts.sh; RULES.md still does not document it |
| ant-farm-eq77 | fix: docs don't clarify code-reviewer is a custom agent outside the repo | P3 | code-reviewer not in RULES.md Agent Types table; no doc about ~/.claude/agents/ |
| ant-farm-f0x | Sentinel-file completion protocol for background subagents | P3 | Feature request; CLAUDE.md blanket prohibition is intentional design decision |
| ant-farm-f1xn | fix: CLAUDE.md Landing the Plane annotation says Step 6 but content spans Steps 4-6 with gaps | **P2** | False annotation causes Queen to skip CHANGELOG documentation commit (RULES.md Step 4) |
| ant-farm-hf9a | Batch mode boundary conditions underdocumented | P3 | Partial wave commits and N=1 wave edge cases not addressed |
| ant-farm-irix | Priority calibration examples use web-UI vocabulary in orchestration context | P3 | RULES.md Priority Calibration section uses web-frontend terms |
| ant-farm-jegj | Commit range and file list validation gaps in RULES.md Step 3b and Pantry guard | P3 | Medium confidence; additional validation gaps beyond what 14f13d7 added |
| ant-farm-kzz6 | Documentation polish: terminology, wording, and examples across review files | P3 | Groups 9 documentation items; sub-item (2) step numbering still present |
| ant-farm-m5lg | fix: review-skeletons/ and review-reports/ missing from Step 0 session directory setup | **P2** | Undocumented lazy-created directories; briefing.md and session-summary.md also missing from list |
| ant-farm-mk03 | RULES.md Model Assignments note misleading about Nitpicker model config location | P3 | 'Set in big-head-skeleton.md' directs reader to wrong place |
| ant-farm-nnmm | RULES.md Step 3 prose polish: milestone placement and variable naming | P3 | WAVE_WWD_PASS milestone placement; TIMESTAMP vs REVIEW_TIMESTAMP naming |
| ant-farm-t3k0 | Standalone documentation polish items (4 sub-issues) | P3 | RULES.md:88 SSV not expanded at first use; other items in CONTRIBUTING.md/GLOSSARY.md |
| ~~ant-farm-t6f~~ | ~~(ALREADY_FIXED — see ALREADY_FIXED section above; not a STILL_VALID item)~~ | — | Close bead; fixed by commit d4aa294 |
| ant-farm-trfb | fix: one-TeamCreate-per-session constraint undocumented in operator-facing docs | **P2** | RULES.md documents 6-member team but not the architectural constraint; runtime failure risk for new operators |
| ant-farm-tvun | PLACEHOLDER_CONVENTIONS.md example missing pc and summaries subdirs | P3 | PLACEHOLDER_CONVENTIONS.md:94 mkdir differs from RULES.md:351 |
| ant-farm-x9eu | fix: README shows 5-member Nitpicker team but RULES.md requires 6 (Pest Control inside team) | **P2** | Functional breakage for new adopters: 5-member team prevents Big Head SendMessage to PC |
| ant-farm-x9yx | fix: SSV checkpoint missing from RULES.md Model Assignments table | **P2** | SSV-unaware Queen omits model parameter, inherits opus; wastes tokens on haiku-appropriate task |
| ant-farm-xyas | RULES.md round 2+ composition phrasing inconsistency with reviews.md | P3 | RULES.md:195 does not state which reviewers are dropped in round 2+ |
| ant-farm-32r8 | Bead metadata / traceability inconsistencies (commit msg, acceptance criteria, line numbers) (canonical) | P3 | Title-only canonical bead; close ant-farm-i9y5 |
| ant-farm-4lcv | README.md deprecated agent row inconsistently formatted (canonical) | P3 | README.md line 309 mixed formatting |
| ant-farm-0jn7 | README.md architecture diagram does not capture Pest Control dual role (canonical) | P3 | ASCII diagram does not show dual-phase role |

---

## Priority Re-Calibration Suggestions

The following beads were flagged by batch reviewers as potentially under-prioritized:

| Bead ID | Current Priority | Suggested Priority | Reason |
|---|---|---|---|
| ant-farm-70ti | P3 | **P2** | GLOSSARY.md is stated authoritative source; SSV omission means readers miss a hard gate entirely |
| ant-farm-9iyp | P3 | **P2** | briefing.md referenced at RULES.md:86/99 but absent from artifact list; navigation gap in frequently consulted section |
| ant-farm-f1xn | P3 | **P2** | False Step 6 annotation causes Queens to skip CHANGELOG documentation commit (RULES.md Step 4) |
| ant-farm-x9eu | P3 | **P2** | Functional breakage for new adopters who follow README to build 5-member team |
| ant-farm-x9yx | P3 | **P2** | Missing SSV row in Model Assignments table causes opus usage for a haiku task |
| ant-farm-trfb | P3 | **P2** | one-TeamCreate constraint invisible to operators; runtime failure with no warning |
| ant-farm-a87o | P3 | **P2** | CCO artifact naming spec mismatch misleads Pest Control agents following checkpoints.md |
| ant-farm-m5lg | P3 | **P2** | Session Directory artifact list is incomplete reference; review-skeletons/ lazy creation undocumented |
| ant-farm-geou | P3 | **P2** | Historical session artifact naming confusion has real operational impact during audits |
| ant-farm-ng0e | P3 | **P2** | Real query failures result from documented-vs-actual artifact naming mismatch |
| ant-farm-lbcy | P3 | **P2** | Audit table gives false PASS for reviews.md; {{SLOT}} tier is actively used but undefined |
| ant-farm-9hxz | P3 | P2 (candidate) | Broken copy command in SETUP.md fails for new adopters |

---

## Completeness Verification

### Bead count by source

| Source | Expected | Counted |
|---|---|---|
| Pass 0 duplicate pairs (both sides, 16 pairs) | 32 | 32 |
| Pass 0 epics | 8 | 8 |
| Batch A | ~33 | 33 |
| Batch B | ~22 | 22 |
| Batch C | ~34 | 34 |
| Batch D | ~6 | 6 |
| Batch E | ~16 | 16 |
| Batch F | ~8 | 8 |
| Batch G | ~10 | 10 |
| Batch H | ~15 | 15 |
| Batch I | ~24 | 24 |
| **Total** | **176** | **176** |

### Verdict count verification

The 168 non-epic bead entries from the 9 batches received these verdicts:

| Verdict | Bead count |
|---|---|
| STILL_VALID | 113 |
| ALREADY_FIXED | 16 |
| DUPLICATE_SUSPECT | 36 |
| IRRELEVANT | 3 |
| **Non-epic batch total** | **168** |
| **+ Epics** | **8** |
| **Grand total** | **176** |

**Reconciliation**: 113 + 16 + 36 + 3 = 168 non-epic beads. Plus 8 epics = 176. All 176 unique bead IDs in the system are accounted for in this report. No bead ID is missing.

---

## Human Review Required

The following items need a human decision before automated action:

1. **ant-farm-wlo4 / ant-farm-4u4s** (pantry-review.md tense): Decide whether to fix or mark IRRELEVANT since file is archived.

2. **ant-farm-bnyn / ant-farm-e5o** (installation guide test file): e5o is older canonical, bnyn has more accurate line references. Decide which to keep as canonical.

3. **ant-farm-dsaa / ant-farm-o7ji**: Both are duplicates of each other AND both are substantively ALREADY_FIXED. Recommend closing all three including ant-farm-9p4i. However 9p4i is marked ALREADY_FIXED separately — confirm whether dsaa and o7ji should be closed as ALREADY_FIXED (not DUPLICATE_SUSPECT) since the underlying issue is fixed.

4. **Priority re-calibrations**: 12 beads listed above have reviewer-suggested P2 upgrades. User should confirm which to officially re-prioritize.

5. **ant-farm-66gl vs ant-farm-bkco** (Future Work epic): Both have identical title. ant-farm-bkco is marked IRRELEVANT in this report. Confirm this is the correct disposition.

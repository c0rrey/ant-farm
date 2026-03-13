# Summary: ant-farm-veht — Add TDV checkpoint definition to checkpoints.md

## 1. Approaches Considered

**Approach A: Minimal flat structure**
Write TDV as a single flat section similar to WWD — all checks inline, no sub-headings, no property table. Compact and easy to scan, but loses visual separation between structural checks and heuristic warnings. Would not match the richer structure of SSV and ESV, and does not satisfy the property table acceptance criterion.

**Approach B: SSV-mirrored structure with numbered checks**
Follow SSV's exact pattern: `**When**`/`**Model**`/`**Why**` header trio, a fenced Pest Control prompt block, and a Queen's Response section. Checks as `## Check N:` headings inside the block. This is structurally sound and consistent with the most prominent checkpoints. Does not inherently include a property table.

**Approach C: ESV-mirrored structure (most complete)**
ESV is the most recently added checkpoint and the most detailed. Mirror ESV's level of depth: per-check PASS/FAIL conditions, a backtick-formatted verdicts block with example FAIL output, and explicit Queen's Response steps. This format gives Pest Control the clearest operational guidance and has the best parity with the newest checkpoint.

**Approach D: Property-table-first hybrid**
Lead with a markdown property table (name, run by, model, when, blocks, max retries, checks) before the fenced code block, since AC7 explicitly requires this. Then follow the SSV/ESV structural pattern for the rest. The property table is not present in any existing checkpoint, making it additive rather than inconsistent.

## 2. Selected Approach

**Approach C + D hybrid**: Use ESV-mirrored structure (Approach C) for maximum consistency with the newest and most detailed checkpoint, and prepend the explicit property table (Approach D) required by AC7. The property table is placed between the header rationale and the fenced code block — visible at a glance without disrupting the flow of the operational prompt.

Rationale: ESV established the current standard for checkpoint detail level (per-check PASS/FAIL conditions, example FAIL verdict, numbered Queen's Response steps). TDV is more complex than SSV (5 structural checks + 3 heuristics vs 3 checks) so the richer format is appropriate. The property table satisfies AC7 and provides a quick-reference summary for the Queen without requiring a full read of the prompt block.

## 3. Implementation Description

Appended 191 lines to `orchestration/templates/checkpoints.md` after the existing ESV section (line 922 onward). The new TDV section consists of:

- **Header block**: `**When**`, `**Model**`, `**Why**`, `**Why haiku**` — matching the SSV/ESV pattern
- **Property table**: 7-row markdown table with name, run by, model, when, blocks, max retries, checks
- **Fenced Pest Control prompt** containing:
  - Check 1 (Coverage): spec requirements → crumb acceptance criteria mapping
  - Check 2 (Completeness): 6 required fields per crumb with bd show-based verification
  - Check 3 (Dependency Validity): circular chain detection + ID existence check with infrastructure failure guard
  - Check 4 (Scope Coherence): provisional wave computation algorithm (DAG topological sort) + file conflict check
  - Check 5 (Trail Integrity): parent linkage verification
  - Heuristic Warnings section with 3 non-blocking checks (AC quality, chain depth, directory overlap)
  - Verdict block with example FAIL output
  - Artifact output path: `{SESSION_DIR}/pc/pc-session-tdv-{timestamp}.md`
- **Queen's Response**: PASS path (proceed to handoff, note warnings) and FAIL path (log, do not proceed, resume Architect, max 2 retries, escalate to user on second failure)

No existing content was modified. The existing ESV section ends at line 922 and remains unchanged.

## 4. Correctness Review

### orchestration/templates/checkpoints.md (lines 922-1113)

Re-read: yes

**Format consistency**: The TDV section opens with a level-2 heading (`##`) matching all other checkpoint headings. The `**When**`, `**Model**`, `**Why**` header pattern matches SSV and ESV exactly. The fenced code block uses the same ` ```markdown ` opening. The Queen's Response subsection uses the same `### The Queen's Response` heading with `**On PASS**` / `**On FAIL**` structure.

**Check numbering**: 5 structural checks numbered Check 1 through Check 5. Each has explicit `**PASS condition**` and `**FAIL condition**` lines — matching ESV's per-check format.

**Heuristic warnings**: Placed inside the fenced prompt block, separated by a horizontal rule from the structural checks. Labeled "Non-Blocking" in the section heading. Each warning uses "WARN —" prefix in its report template — consistent with how other checkpoints document WARN verdicts.

**Infrastructure failure guard**: Check 3 includes the standard guard pattern (record, skip, continue, mark [SKIPPED], threshold failure) matching the guard patterns in SSV (Check 2) and ESV (Check 3).

**Provisional wave algorithm**: Documented as a numbered algorithm inside Check 4 with a concrete example (`Crumbs A, B → Wave 1, C → Wave 2, D → Wave 3`). This satisfies AC6 without introducing notation not used elsewhere in the file.

**Artifact path**: Uses session-wide naming convention `pc-session-tdv-{timestamp}.md` — correct, since TDV is a session-wide (not per-task) checkpoint. Matches the naming pattern for SSV, CCO-impl, CCO-review, CCB, ESV.

**Retry logic**: Queen's Response On FAIL step 5 explicitly states "If TDV fails a second time, escalate to user... do NOT attempt a third Architect retry automatically." Property table row "Max retries: 2 (Architect retries); escalate to user after second failure." Both satisfy AC5.

**Adjacent issue noted (not fixed)**: The Pest Control Overview section (L13-51) lists responsibilities and the Verdict Thresholds Summary (L54-114) list all checkpoints by name. Neither mentions TDV. These sections are within the L1-870 read-only scope boundary and were not modified. A follow-up task should update those sections to include TDV for completeness.

## 5. Build/Test Validation

No compiled code changed. The file is a markdown template read by Pest Control at runtime. Structural validation:

- Markdown heading hierarchy: `##` for section, `###` for subsections inside and outside the fenced block — consistent with existing checkpoints.
- No broken backtick fences: the fenced block opens with ` ```markdown ` at line 946 and closes with ` ``` ` at line 1096.
- No unclosed bold markers, tables, or blockquotes.
- Line count: 191 lines added, 0 lines removed.

## 6. Acceptance Criteria Checklist

| # | Criterion | Status |
|---|---|---|
| 1 | TDV checkpoint added to checkpoints.md with same format as existing checkpoints | PASS |
| 2 | All 5 structural checks documented with pass/fail criteria | PASS |
| 3 | 3 heuristic warnings documented as warnings (not blockers) | PASS |
| 4 | Verdict definitions: TDV PASS -> handoff, TDV FAIL -> Architect retry with gap list | PASS |
| 5 | Max 2 retries documented with escalation to user after limit | PASS |
| 6 | Provisional wave computation algorithm documented (for scope coherence check) | PASS |
| 7 | TDV property table included: name, run by, model, when, blocks, max retries, checks | PASS |

**Commit**: b8bbdb4
**File changed**: `orchestration/templates/checkpoints.md` (+191 lines, lines 923-1113)

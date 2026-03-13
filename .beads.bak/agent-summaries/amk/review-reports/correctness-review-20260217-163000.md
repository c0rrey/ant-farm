# Report: Correctness Redux Review

**Scope**: orchestration/PLACEHOLDER_CONVENTIONS.md
**Reviewer**: Correctness Redux Review (code-reviewer)

## Findings Catalog

### Finding 1: Audit table line number references may become stale

- **File(s)**: /Users/correy/projects/ant-farm/orchestration/PLACEHOLDER_CONVENTIONS.md:103-118
- **Severity**: P3
- **Category**: correctness
- **Description**: The file-by-file audit table (lines 103-118) includes specific line number references for where placeholders appear in each file (e.g., "`{SESSION_DIR}` (L10,62,66,129,175,178)"). These line numbers are accurate as of the audit but will become stale as the referenced files are edited. For example, the scout.md changes in commits ed041b2 and 55c8401 added lines that shifted content down, meaning some of these line references may already be inaccurate. The audit table is a snapshot, not a living reference, but it presents itself as authoritative ("File-by-File Audit (Completed)") without noting the snapshot date.
- **Suggested fix**: Add a date or commit hash to the audit header (e.g., "File-by-File Audit (as of commit 1f656e7, 2026-02-17)") so readers know the line numbers are point-in-time. Alternatively, remove line-number specificity from the table and keep only file-level pass/fail status, since the grep patterns in the Validation Rules section (lines 122-152) provide the live verification mechanism.

### Finding 2: PLACEHOLDER_CONVENTIONS.md not referenced from RULES.md or any template

- **File(s)**: /Users/correy/projects/ant-farm/orchestration/PLACEHOLDER_CONVENTIONS.md:207-211
- **Severity**: P3
- **Category**: correctness
- **Description**: The Enforcement Strategy section (lines 207-211) lists "Document pattern in RULES.md 'Information Diet' section referencing this document" as step 4, but this cross-reference has not been added to RULES.md. A grep for "PLACEHOLDER" or "placeholder" in RULES.md returns no matches. The document exists as a canonical reference but is not linked from the workflow entry points where template authors would encounter it. AC2 states "All templates use consistent casing matching the documented convention" -- while this is true (the audit confirmed compliance), the convention is not discoverable from the templates themselves.
- **Suggested fix**: Add a one-line reference in RULES.md or in the relevant template files pointing to `orchestration/PLACEHOLDER_CONVENTIONS.md` as the canonical placeholder reference. This completes the enforcement strategy's step 4.

## Preliminary Groupings

### Group A: Documentation completeness
- Finding 1, Finding 2 -- both relate to the document's integration into the broader orchestration documentation system.
- **Suggested combined fix**: Add a commit hash/date to the audit table header and add a cross-reference from RULES.md to PLACEHOLDER_CONVENTIONS.md.

**Acceptance criteria verification for p33:**

- **AC1** (A canonical document defines the placeholder convention with clear uppercase vs lowercase rules): **MET**. PLACEHOLDER_CONVENTIONS.md defines a 3-tier system: Tier 1 (`{UPPERCASE}`) for Queen-substituted context, Tier 2 (`{lowercase-kebab}`) for agent-derived/runtime values, and Tier 3 (`${SHELL_VAR}`) for shell variables. Each tier has clear definitions, characteristics, and examples (lines 1-96). The term definition block template (lines 40-47) provides a copy-paste block for templates.
- **AC2** (All templates use consistent casing matching the documented convention): **MET**. The file-by-file audit table (lines 103-118) lists every orchestration file and confirms PASS status for all. Running the mixed-casing validation grep pattern (Pattern 4, lines 148-152) against `orchestration/` confirms no violations outside the convention document itself (which uses example terms like `{UPPERCASE}` in prose).
- **AC3** (`grep` across `orchestration/` for placeholder patterns shows no violations of the convention): **MET**. The validation rules section (lines 122-152) provides 4 grep patterns for detecting each tier and invalid mixed casing. Running Pattern 4 (mixed casing detection) confirms no violations in actual template files. All matches from the self-referential convention document are expected.

## Summary Statistics
- Total findings: 2
- By severity: P1: 0, P2: 0, P3: 2
- Preliminary groups: 1

## Cross-Review Messages

### Sent
- None

### Received
- None

### Deferred Items
- None

## Coverage Log

| File | Status | Evidence |
|------|--------|----------|
| /Users/correy/projects/ant-farm/orchestration/PLACEHOLDER_CONVENTIONS.md | Findings: #1, #2 | 237 lines examined across all sections: overview table, 3 tier definitions with examples, file-by-file audit table (19 files listed), 4 validation grep patterns, compliance status with per-file analysis, enforcement strategy, benefits, and exceptions/special cases |

## Overall Assessment
**Score**: 9/10
**Verdict**: PASS WITH ISSUES
<!-- Verdict Rubric:
  PASS           = 0 P1 findings AND 0 P2 findings
  PASS WITH ISSUES = 0 P1 findings AND any P2 or P3 findings
  NEEDS WORK     = any P1 finding present

  Score formula: Start at 10, subtract 3 per P1, 1 per P2, 0.5 per P3 (floor at 0)
  10 - 0.5(P3) - 0.5(P3) = 9
-->
All three acceptance criteria for task p33 are met. The placeholder conventions document is thorough, the 3-tier system is clearly defined, and the audit confirms all templates comply. The two P3 findings are minor documentation integration issues: the audit table's line numbers will become stale over time, and the document is not yet cross-referenced from RULES.md as specified in its own enforcement strategy.

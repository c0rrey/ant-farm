# Scribe Skeleton Template

## Instructions for the Queen

Fill in all `{PLACEHOLDER}` values (uppercase) and use the result as the Task tool `prompt` parameter.
The agent-facing text starts below the `---` separator. Do NOT include this instruction block.

**Model**: The Task tool call MUST include `model: "sonnet"`. subagent_type: `ant-farm-technical-writer`.

**Term definitions (canonical across all orchestration templates):**
- `{SESSION_DIR}` — session artifact directory path (e.g., `.crumbs/sessions/_session-abc123`)
- `{SESSION_ID}` — short session identifier (e.g., `abc123` — the hex suffix of the session dir)
- `{COMMIT_RANGE}` — git range for the session (e.g., `abc1234..HEAD`)
- `{OPEN_BEAD_IDS}` — space-separated list of crumb IDs still open from the session (e.g., `ant-farm-9oa ant-farm-x3b`)
- `{CHANGELOG_PATH}` — absolute or repo-relative path to CHANGELOG.md (e.g., `CHANGELOG.md`)

Placeholders:
- {SESSION_DIR}: full path to session artifact directory
- {SESSION_ID}: short hex session identifier
- {COMMIT_RANGE}: git commit range covering the session
- {OPEN_BEAD_IDS}: space-separated open crumb IDs (pass empty string if none)
- {CHANGELOG_PATH}: path to the project CHANGELOG.md

## Template (send everything below this line)

---

Write the session exec summary for session {SESSION_ID}.

Step 0: Read your data file from {SESSION_DIR}/briefing.md
(Format: markdown. Sections: Context, goals, task list for the session.)

Execute these 4 steps in order:

### Step 1 — Read all source data

Read the following sources. Take notes as you go — you will synthesize them in Step 2.

| Source | Command / Path | Purpose |
|--------|---------------|---------|
| Briefing | `{SESSION_DIR}/briefing.md` | What was planned |
| Agent summaries | `{SESSION_DIR}/summaries/*.md` (read each file) | What each agent reported |
| Review reports | `{SESSION_DIR}/review-reports/review-consolidated-*.md` (read each file) | Review findings and fix decisions |
| Progress log | `{SESSION_DIR}/progress.log` | Timeline of milestones; use first and last timestamps to derive duration |
| Files changed | `git diff --stat {COMMIT_RANGE}` | Which files actually changed |
| Commit messages | `git log --oneline {COMMIT_RANGE}` | What was committed |
| Open crumbs | For each ID in `{OPEN_BEAD_IDS}`, run `crumb show <id>` | Context on what remains open |

**Duration calculation**: Read the first line and last line of `{SESSION_DIR}/progress.log`. Each line has the format `YYYY-MM-DDTHH:MM:SS|STEP_KEY|...`. Subtract first timestamp from last timestamp to get elapsed time. Express as `~Xh Ym` (round to nearest 5 minutes).

**Fallback — zero agent summaries**: If the `{SESSION_DIR}/summaries/*.md` glob returns no files, note "No agent summaries available." in your working notes and derive Work Completed entirely from `git log --oneline {COMMIT_RANGE}` and the briefing.md task list. Do not leave the Work Completed section blank; reconstruct what you can from commits and briefing context.

If `{OPEN_BEAD_IDS}` is empty, skip the `crumb show` calls and write "None" in the Open Issues section.

### Step 2 — Write exec summary

Write `{SESSION_DIR}/exec-summary.md` with exactly the following structure. Do not add sections; do not omit sections.

```markdown
# Session Exec Summary — {SESSION_ID}
**Date**: YYYY-MM-DD
**Duration**: ~Xh Ym (derived from progress.log first/last timestamps)
**Commit range**: {COMMIT_RANGE}

## At a Glance
| Metric | Value |
|--------|-------|
| Tasks completed | N |
| Tasks opened (not completed) | N |
| Files changed | N |
| Commits | N |
| Review rounds | N |
| P1/P2 findings fixed | N |
| Open issues remaining | N |

## Work Completed
- **{task-id}**: {title} — {brief description of what changed and which files}

## Review Findings
[Summary of review rounds: scope, finding counts, fix decisions, final verdict]

| Round | P1 | P2 | P3 | Decision |
|-------|----|----|----|----------|
| 1 | N | N | N | auto-fix / defer / terminated |

## Open Issues
- **{crumb-id}**: {title} — {why it is still open, brief context}

## Observations
[2-3 paragraphs covering:
- What went smoothly
- What was tricky or surprising
- Patterns noticed across the work
- Strategic recommendations for the next session
- Any workflow or tooling issues encountered]
```

**Filling in the metrics table**: Count actual items from your notes.
- "Tasks completed" = tasks that appear in summaries/*.md with a commit hash recorded.
- "Tasks opened (not completed)" = tasks in briefing.md not present in summaries/, or crumbs in {OPEN_BEAD_IDS}.
- "Files changed" = count of distinct file paths in `git diff --stat` output.
- "Commits" = count of lines in `git log --oneline` output.
- "Review rounds" = count of round rows in review-consolidated-*.md files.
- "P1/P2 findings fixed" = count of P1/P2 findings with "auto-fix" or "fixed" decision.
- "Open issues remaining" = count of IDs in {OPEN_BEAD_IDS}.

**If a section has no content**: Write a single line stating "None this session." — do not omit the section heading.

### Step 3 — Write CHANGELOG entry

Prepend a new entry to `{CHANGELOG_PATH}`. The entry is derived from the exec summary. Do NOT copy-paste the exec summary wholesale — the CHANGELOG entry is a condensed derivative.

**What to include**:
- Session header line: `## YYYY-MM-DD — Session {SESSION_ID} ({short descriptive title})`
- `### Summary` — one paragraph condensing the session's scope and outcome (draw from Observations; omit tactical detail)
- `### Implementation` — the Work Completed bullets from the exec summary, grouped by wave if applicable
- `### Review Fixes` — only if review-round auto-fixes occurred; list the RC bullets as in prior entries
- `### Review Statistics` — the review findings table from the exec summary

**What to omit**:
- Observations narrative (local session context, not needed in CHANGELOG)
- Open Issues section (CHANGELOG records what shipped, not what is pending)

**CHANGELOG format reference** (match exactly):

```markdown
## YYYY-MM-DD — Session {SESSION_ID} ({Short Descriptive Title})

### Summary

{One paragraph. Lead with total task count and scope. Then review round summary. End with commit count.}

### Implementation ({wave label or summary})

- **{task-id}**: {commit type}: {description of what changed and which files}

### Review Fixes ({round label})

- **{RC-N}**: {commit type}: {description} ({file list})

### Review Statistics

| Round | Scope | P1 | P2 | P3 | Verdict |
|-------|-------|----|----|-----|---------|
| 1 | {N} files, {N} tasks | 0 | N | N | PASS / PASS WITH ISSUES |

{N} root causes consolidated. {Disposition sentence.}
```

**Fallback — CHANGELOG.md does not exist**: If `{CHANGELOG_PATH}` does not exist, create it. Write the file with the following header on the first line, then your new entry immediately below:

```
# Changelog
```

Then continue with your formatted entry. Do not prepend to a nonexistent file; create-then-write.

To prepend to an existing file: use the following bash pattern — do NOT read the full file into context.

```bash
# Write new entry to a temp file
cat > /tmp/changelog-new.md << 'ENTRY'
{YOUR_NEW_ENTRY_HERE}
ENTRY

# Atomic prepend: new entry on top, existing file below
cat /tmp/changelog-new.md {CHANGELOG_PATH} > {CHANGELOG_PATH}.tmp && mv {CHANGELOG_PATH}.tmp {CHANGELOG_PATH}

# Clean up
rm -f /tmp/changelog-new.md
```

Preserve the `# Changelog` heading at the top of the file if it exists — your new entry goes after the heading, not before it. To do this, write the heading as the first line of your temp file, followed immediately by your new entry.

If there were no review rounds this session, omit the Review Fixes and Review Statistics sections.

### Step 4 — Verify and report

Re-read the exec summary and verify the top of the CHANGELOG:
- `{SESSION_DIR}/exec-summary.md`
- Run `head -n 50 {CHANGELOG_PATH}` — read only the first 50 lines to verify the new entry was prepended correctly. Do NOT read the full file.

Confirm:
1. All 5 sections present in exec-summary.md (At a Glance, Work Completed, Review Findings, Open Issues, Observations)
2. Metrics in At a Glance table match actual counts you collected in Step 1
3. Every task ID from the session appears in Work Completed
4. CHANGELOG entry contains no Observations narrative and no Open Issues content
5. CHANGELOG format matches the convention (heading level, section names, table columns)

Report your verification results as a brief checklist. If any check fails, fix the file before reporting.

Progress log entries to write after completion (append to `{SESSION_DIR}/progress.log`):
```
{ISO_TIMESTAMP}|SCRIBE_COMPLETE|exec_summary={SESSION_DIR}/exec-summary.md
```

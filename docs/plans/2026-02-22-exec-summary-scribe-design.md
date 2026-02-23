# Design: Session Exec Summary Agent ("Scribe")

**Date**: 2026-02-22
**Status**: Approved (brainstorming)

## Problem

Session work is captured across many scattered artifacts: agent summaries, review reports, progress logs, CHANGELOG entries, and open beads. There's no single canonical document that tells a human or future AI session "here's what happened, what shipped, what's left, and what to watch out for." The CHANGELOG captures what shipped but not the narrative — what was tricky, what patterns emerged, or strategic context for the next session.

## Design Decisions

1. **Audience**: Human operator + future AI sessions (dual-purpose)
2. **Storage**: `{SESSION_DIR}/exec-summary.md` — local session artifact, not git-synced
3. **Relationship to CHANGELOG**: Exec summary is the canonical record; CHANGELOG is a committed derivative written by the same agent
4. **Timing**: Runs before push (Step 5b) so the CHANGELOG derivative gets included in the final commit
5. **Format**: Hybrid — structured summary table at top, narrative observations at bottom
6. **Gate**: ESV (Exec Summary Verification) is a hard gate — must PASS before push

## Workflow Position

### Current Flow
```
Step 4: Documentation (CHANGELOG, README, CLAUDE.md)
Step 5: Verify (cross-refs, task closure)
Step 6: Land the plane (pull, sync, push)
```

### New Flow
```
Step 4: Documentation (README, CLAUDE.md — NO CHANGELOG)
Step 5: Verify (cross-refs, task closure)
Step 5b: Scribe — exec summary agent
Step 5c: ESV — Pest Control verification (hard gate)
Step 6: Land the plane (Queen commits Scribe output, pull, sync, push)
```

CHANGELOG authoring moves from the Queen (Step 4) to the Scribe (Step 5b). The Queen still updates README and CLAUDE.md at Step 4 when needed.

## Scribe Agent Specification

### Agent Configuration
- **subagent_type**: `technical-writer`
- **model**: `sonnet`
- **Custom agent** — technical-writer with Bash added (Read, Write, Edit, Bash, Glob, Grep)

### Inputs (passed by Queen)

1. **Session directory path** — Scribe reads all artifacts from it
2. **Commit range** — `<first-session-commit>..<HEAD>`
3. **Open bead IDs** — beads opened or touched during the session that remain open
4. **CHANGELOG.md path** — so the Scribe knows where to write the derivative

### What the Scribe Reads

| Source | Purpose |
|--------|---------|
| `{SESSION_DIR}/briefing.md` | What was planned |
| `{SESSION_DIR}/summaries/*.md` | What each agent reported |
| `{SESSION_DIR}/review-reports/review-consolidated-*.md` | Review findings and fix decisions |
| `{SESSION_DIR}/progress.log` | Timeline of milestones, duration |
| `git diff --stat <commit-range>` | What files actually changed |
| `git log --oneline <commit-range>` | Commit messages |
| `bd show <open-bead-ids>` | Context on what's still open |

### Outputs

#### 1. Exec Summary (`{SESSION_DIR}/exec-summary.md`)

```markdown
# Session Exec Summary — {SESSION_ID}
**Date**: YYYY-MM-DD
**Duration**: ~Xh Ym (derived from progress.log first/last timestamps)
**Commit range**: abc1234..def5678

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
[one bullet per completed task]

## Review Findings
[Summary of review rounds: scope, finding counts, fix decisions, final verdict]

| Round | P1 | P2 | P3 | Decision |
|-------|----|----|----|----------|
| 1 | N | N | N | auto-fix / defer / terminated |

## Open Issues
- **{bead-id}**: {title} — {why it's still open, brief context}
[one bullet per open bead from the session]

## Observations
[2-3 paragraphs of narrative:
- What went smoothly in this session
- What was tricky or surprising
- Patterns noticed across the work
- Strategic recommendations for the next session
- Any workflow/tooling issues encountered]
```

#### 2. CHANGELOG Entry (prepended to `CHANGELOG.md`)

Derived from the exec summary. Includes:
- Session ID and date header
- Summary line (condensed from Observations)
- Work Completed section (as-is)
- Review statistics table
- Omits: Observations narrative, Open Issues (those are local context)

Format matches the existing CHANGELOG convention already established in the project.

## ESV Checkpoint (Exec Summary Verification)

### Agent Configuration
- **subagent_type**: `pest-control`
- **model**: `haiku`
- **Gate type**: Hard gate — blocks push until PASS

### Checks

| # | Check | Inputs | Pass Condition |
|---|-------|--------|----------------|
| 1 | Task coverage | briefing.md / progress.log task IDs vs exec-summary.md | Every session task ID appears in exec summary |
| 2 | Commit coverage | `git log --oneline <range>` vs exec-summary.md | Every commit hash is accounted for |
| 3 | Open bead accuracy | exec-summary.md "Open Issues" vs `bd show` | Listed beads are actually open; no unlisted open beads from session |
| 4 | CHANGELOG derivation fidelity | exec-summary.md vs CHANGELOG.md | Every task ID and commit in exec summary also appears in CHANGELOG |
| 5 | Section completeness | exec-summary.md | All 5 required sections present (At a Glance, Work Completed, Review Findings, Open Issues, Observations) |
| 6 | Metric consistency | exec-summary.md internal cross-check | Counts in "At a Glance" table match actual item counts in body sections |

### Failure Handling
- **On ESV FAIL**: Re-spawn Scribe with specific violations from ESV report (max 1 retry)
- **On second ESV FAIL**: Escalate to user — present the failed checks and ask whether to fix manually or push as-is

### Artifact
Written to `{SESSION_DIR}/pc/pc-session-esv-{timestamp}.md`

## Hard Gate Table Update

Add to RULES.md Hard Gates table:

| Gate | Blocks | Artifact |
|------|--------|----------|
| ESV PASS | Git push (Step 6) | `{SESSION_DIR}/pc/pc-session-esv-{timestamp}.md` |

## Retry Limits Update

Add to RULES.md Retry Limits table:

| Situation | Max Retries | After Limit |
|-----------|-------------|-------------|
| Scribe fails ESV | 1 | Escalate to user with ESV report |

## Changes to Existing Steps

### Step 4 (Documentation)
- Remove CHANGELOG writing from this step
- Keep README and CLAUDE.md updates here

### Step 5b (NEW — Scribe)
Queen spawns:
```
Task(
  subagent_type="technical-writer",
  model="sonnet",
  prompt="Write session exec summary. Session dir: {SESSION_DIR}. Commit range: {RANGE}. Open beads: {IDS}. [+ template instructions]"
)
```

### Step 5c (NEW — ESV)
Queen spawns:
```
Task(
  subagent_type="pest-control",
  model="haiku",
  prompt="ESV checkpoint. Session dir: {SESSION_DIR}. Commit range: {RANGE}. Verify exec-summary.md and CHANGELOG.md. [+ checkpoint instructions]"
)
```

### Step 6 (Land the Plane)
- Queen commits the Scribe's CHANGELOG.md changes before pushing
- `git add CHANGELOG.md && git commit -m "docs: add session {SESSION_ID} changelog entry"`
- Then proceeds with existing: pull --rebase, bd sync, push

### Progress Log
Add two new entries:
```
{timestamp}|SCRIBE_COMPLETE|exec_summary={SESSION_DIR}/exec-summary.md
{timestamp}|ESV_PASS|artifact={SESSION_DIR}/pc/pc-session-esv-{timestamp}.md
```

## What This Does NOT Change

- Session artifacts remain not git-synced (exec summary stays in session dir)
- Review workflow is untouched
- Agent spawning, verification, and implementation steps are untouched
- The Scribe has no gate role over implementation — it's retrospective only
- If both Scribe and retry fail, Queen can still push (after user approval) with a manually-written CHANGELOG

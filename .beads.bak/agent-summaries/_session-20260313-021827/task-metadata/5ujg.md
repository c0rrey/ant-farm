# Task: ant-farm-5ujg
**Status**: success
**Title**: crumb sync referenced in AGENTS.md but does not exist in crumb.py
**Type**: bug
**Priority**: P1
**Epic**: none
**Agent Type**: general-purpose
**Dependencies**: {blocks: [], blockedBy: []}

## Affected Files
- `AGENTS.md:12` — quick reference table lists `crumb sync`
- `AGENTS.md:28` — landing-the-plane push block includes `crumb sync`

## Root Cause
`crumb sync` is referenced in AGENTS.md at two locations but no `sync` subcommand exists in crumb.py. Added during bd-to-crumb migration but never implemented. Agents following AGENTS.md session completion instructions will encounter a command-not-found error.

## Expected Behavior
AGENTS.md should not reference non-existent commands. Push block should match CLAUDE.md.

## Acceptance Criteria
1. `crumb sync` does not appear anywhere in AGENTS.md
2. AGENTS.md push block matches CLAUDE.md push block (git pull --rebase, git push, git status)
3. `grep -r 'crumb sync' *.md` returns no matches in user-facing docs

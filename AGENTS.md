# Agent Instructions

This project uses **crumb** for issue tracking. Run `crumb doctor` to get started.

## Quick Reference

```bash
crumb ready              # Find available work
crumb show <id>          # View issue details
crumb update <id> --status in_progress  # Claim work
crumb close <id>         # Complete work
```

## Landing the Plane (Session Completion)

**When ending a work session**, you MUST complete ALL steps below. Work is NOT complete until `git push` succeeds.

**MANDATORY WORKFLOW:**

1. **File issues for remaining work** - Create issues for anything that needs follow-up
2. **Run quality gates** (if code changed) - Tests, linters, builds
3. **Review-findings gate** — If reviews ran and found P1 issues, present findings to user before proceeding. User decides: fix now, or document deferred P1s in CHANGELOG and push. Do NOT push with undisclosed P1 blockers. If no reviews ran or no P1s exist, proceed.
4. **Update issue status** - Close finished work, update in-progress items
5. **PUSH TO REMOTE** - This is MANDATORY:
   ```bash
   git pull --rebase
   git push
   git status  # MUST show "up to date with origin"
   ```
6. **Clean up** - Clear stashes, prune remote branches
   (Session artifacts in .crumbs/sessions/_session-*/ are retained for posterity. Prune old sessions manually when needed.)
7. **Verify** - All changes committed AND pushed
8. **Hand off** - Provide context for next session

**CRITICAL RULES:**
- Work is NOT complete until `git push` succeeds
- NEVER stop before pushing - that leaves work stranded locally
- NEVER say "ready to push when you are" - YOU must push
- If push fails, resolve and retry until it succeeds


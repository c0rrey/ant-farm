# Handoff: Deferred Reviews for Session db790c8d

## What happened

Session db790c8d completed 4 P1 bug fixes across 2 waves. All passed WWD + DMVDC verification. Reviews (Step 3b) were blocked because review prompt templates lacked per-type focus areas and messaging guidance — a gap introduced when review prompts moved to bash-script generation.

A separate agent is implementing the template fix (plan at `~/.claude/plans/wobbly-scribbling-map.md`). Once that fix lands, reviews can run on this session's work.

## Review inputs (ready to use)

| Field | Value |
|-------|-------|
| Session dir | `.beads/agent-summaries/_session-db790c8d` |
| Commit range | `7569c5e^..HEAD` (adjust HEAD to the last implementation commit if new commits exist — last impl commit is `c78875b`) |
| Changed files | `agents/scout-organizer.md CONTRIBUTING.md orchestration/GLOSSARY.md orchestration/RULES.md orchestration/templates/checkpoints.md README.md` |
| Task IDs | `ant-farm-x8iw ant-farm-h94m ant-farm-wg2i ant-farm-zuae` |
| Review round | `1` |

## Commits to review

| Commit | Task | Summary |
|--------|------|---------|
| `7569c5e` | ant-farm-x8iw | Fix Scout/Pantry model references (sonnet → opus) in frontmatter, GLOSSARY, README |
| `17a6e03` | ant-farm-h94m | Remove false "PC spawns code-reviewer" architecture from checkpoints.md |
| `4a30d6a` | ant-farm-wg2i | Regenerate pre-push hook (non-fatal sync), fix CONTRIBUTING.md rsync docs |
| `c78875b` | ant-farm-zuae | Document WWD batch vs serial execution modes in RULES.md + checkpoints.md |

## Steps to run reviews

**Prerequisite**: The template fix from `wobbly-scribbling-map.md` must be committed and the updated files synced to `~/.claude/orchestration/templates/` and `~/.claude/agents/`.

1. **Regenerate review skeletons** (old skeletons lack focus blocks):
   ```bash
   bash scripts/compose-review-skeletons.sh \
     ".beads/agent-summaries/_session-db790c8d" \
     "$HOME/.claude/orchestration/templates/reviews.md" \
     "$HOME/.claude/orchestration/templates/nitpicker-skeleton.md" \
     "$HOME/.claude/orchestration/templates/big-head-skeleton.md" \
     "$HOME/.claude/orchestration/templates/review-focus-areas.md"
   ```

2. **Fill review slots**:
   ```bash
   TIMESTAMP=$(date +%Y%m%d-%H%M%S)
   bash scripts/fill-review-slots.sh \
     ".beads/agent-summaries/_session-db790c8d" \
     "7569c5e^..c78875b" \
     "agents/scout-organizer.md CONTRIBUTING.md orchestration/GLOSSARY.md orchestration/RULES.md orchestration/templates/checkpoints.md README.md" \
     "ant-farm-x8iw ant-farm-h94m ant-farm-wg2i ant-farm-zuae" \
     "${TIMESTAMP}" \
     "1"
   ```

3. **CCO gate** on review previews, then **spawn Nitpicker team** per RULES.md Step 3b-iii/iv.

## Notes

- Exclude `.beads/issues.jsonl` from changed files — auto-generated beads metadata, not reviewable code (see memory note).
- The commit range uses `7569c5e^..c78875b` (pinned end) rather than `..HEAD` to avoid picking up the template fix commits or other post-session work.
- Review skeletons from the original session exist at `.beads/agent-summaries/_session-db790c8d/review-skeletons/` but must be regenerated (step 1 above) to include focus blocks.

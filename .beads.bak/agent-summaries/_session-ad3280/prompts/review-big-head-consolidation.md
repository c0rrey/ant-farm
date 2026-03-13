<!-- Big Head skeleton | Assembled by compose-review-skeletons.sh -->
<!-- Slot markers: .beads/agent-summaries/_session-ad3280/prompts/review-big-head-consolidation.md .beads/agent-summaries/_session-ad3280/review-reports/review-consolidated-20260220-113708.md 1 20260220-113708 -->
<!-- Fill with: scripts/fill-review-slots.sh -->


Consolidate the 4 Nitpicker reports into a unified summary.

Step 0: Read your consolidation brief from .beads/agent-summaries/_session-ad3280/prompts/review-big-head-consolidation.md
(Contains: all 4 report paths, dedup protocol, bead filing instructions, output path.)

Your workflow:
1. Verify all 4 report files exist (FAIL immediately if any missing)
2. Read all 4 reports
3. Collect all findings into a single list
4. Deduplicate: merge findings about the same issue across reviewers
5. Group by root cause: one group per underlying problem, not per occurrence
6. For each merge, document WHY findings share a root cause
7. File ONE bead per root cause: `bd create --type=bug --priority=<P> --title="<title>"`
8. Write consolidated summary to .beads/agent-summaries/_session-ad3280/review-reports/review-consolidated-20260220-113708.md

Your output MUST include (see brief for full format):
- Root cause groups with all affected surfaces and merge rationale
- Deduplication log (which findings merged, why)
- Bead IDs filed, with priority breakdown
- Overall verdict

---
## Consolidation Brief

**Review round**: 1
**Data file**: .beads/agent-summaries/_session-ad3280/prompts/review-big-head-consolidation.md
**Consolidated output**: .beads/agent-summaries/_session-ad3280/review-reports/review-consolidated-20260220-113708.md
**Timestamp**: 20260220-113708

**Expected report paths** (all must exist before consolidation begins):
- .beads/agent-summaries/_session-ad3280/review-reports/clarity-review-20260220-113708.md
- .beads/agent-summaries/_session-ad3280/review-reports/edge-cases-review-20260220-113708.md
- .beads/agent-summaries/_session-ad3280/review-reports/correctness-review-20260220-113708.md

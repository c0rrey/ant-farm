<!-- Big Head skeleton | Assembled by compose-review-skeletons.sh -->
<!-- Slot markers: .beads/agent-summaries/_session-db790c8d/prompts/review-big-head-consolidation.md .beads/agent-summaries/_session-db790c8d/review-reports/review-consolidated-20260222-103344.md 2 20260222-103344 -->
<!-- Fill with: scripts/fill-review-slots.sh -->


Consolidate the Nitpicker reports into a unified summary.

**Review round**: 2
- Round 1: expect 4 reports (clarity, edge-cases, correctness, excellence)
- Round 2+: expect 2 reports (correctness, edge-cases only)

Step 0: Read your consolidation brief from .beads/agent-summaries/_session-db790c8d/prompts/review-big-head-consolidation.md
(Contains: round-appropriate report paths, dedup protocol, bead filing instructions, output path.)

Your workflow:
1. Verify all expected report files exist (4 for round 1; 2 for round 2+) — follow the missing-report handling protocol in your consolidation brief (Step 0a)
   - The brief is authoritative for this step: it specifies the polling timeout, error return format, and failure conditions
   - Do NOT proceed to read reports or perform consolidation until the brief's Step 0a protocol completes successfully
2. Read all expected reports
3. Collect all findings into a single list
4. Deduplicate: merge findings about the same issue across reviewers
5. Group by root cause: one group per underlying problem, not per occurrence
6. For each merge, document WHY findings share a root cause
7. Write consolidated summary to .beads/agent-summaries/_session-db790c8d/review-reports/review-consolidated-20260222-103344.md
8. Send consolidated report path to Pest Control (SendMessage): "Consolidated report ready at .beads/agent-summaries/_session-db790c8d/review-reports/review-consolidated-20260222-103344.md. Please run DMVDC and CCB checkpoints and reply with verdict."
   - Do NOT file any beads before receiving Pest Control's reply
9. Await Pest Control verdict — follow the timeout/retry protocol in reviews.md Step 4:
   - Wait up to 60 seconds; retry once if no response; escalate to Queen after 120s total with no reply
   - **PASS**: File ONE bead per root cause: `bd create --type=bug --priority=<P> --title="<title>"`
   - **FAIL**: Escalate to Queen with specifics (which findings failed, why); file beads ONLY for validated findings
   - **TIMEOUT/UNAVAILABLE**: Escalate to Queen with consolidated report path; do NOT file beads
10. **Round 2+ only — P3 auto-filing**: After filing P1/P2 beads, auto-file P3 findings to "Future Work" epic:
    - Find or create the epic: `bd list --status=open | grep -i "future work"` or `bd epic create --title="Future Work" --description="Low-priority polish and improvements from review sessions"`
    - For each P3: `bd create --type=bug --priority=3 --title="<title>"` then `bd dep add <id> <epic-id> --type parent-child`
    - Mark P3s as "auto-filed, no action required" in the consolidated summary
    - Do NOT include P3 findings in the fix-or-defer prompt to the Queen
    - In round 1, skip this step — P3s are handled by the Queen's existing flow

Your output MUST include (see brief for full format):
- Root cause groups with all affected surfaces and merge rationale
- Deduplication log (which findings merged, why)
- Bead IDs filed, with priority breakdown
- Overall verdict

---
## Consolidation Brief

**Review round**: 2
**Data file**: .beads/agent-summaries/_session-db790c8d/prompts/review-big-head-consolidation.md
**Consolidated output**: .beads/agent-summaries/_session-db790c8d/review-reports/review-consolidated-20260222-103344.md
**Timestamp**: 20260222-103344

**Expected report paths** (all must exist before consolidation begins):
- .beads/agent-summaries/_session-db790c8d/review-reports/correctness-review-20260222-103344.md
- .beads/agent-summaries/_session-db790c8d/review-reports/edge-cases-review-20260222-103344.md

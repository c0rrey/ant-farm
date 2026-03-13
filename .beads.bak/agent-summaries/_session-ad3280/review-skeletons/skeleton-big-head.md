<!-- Big Head skeleton | Assembled by compose-review-skeletons.sh -->
<!-- Slot markers: {{DATA_FILE_PATH}} {{CONSOLIDATED_OUTPUT_PATH}} {{REVIEW_ROUND}} {{TIMESTAMP}} -->
<!-- Fill with: scripts/fill-review-slots.sh -->


Consolidate the 4 Nitpicker reports into a unified summary.

Step 0: Read your consolidation brief from {{DATA_FILE_PATH}}
(Contains: all 4 report paths, dedup protocol, bead filing instructions, output path.)

Your workflow:
1. Verify all 4 report files exist (FAIL immediately if any missing)
2. Read all 4 reports
3. Collect all findings into a single list
4. Deduplicate: merge findings about the same issue across reviewers
5. Group by root cause: one group per underlying problem, not per occurrence
6. For each merge, document WHY findings share a root cause
7. File ONE bead per root cause: `bd create --type=bug --priority=<P> --title="<title>"`
8. Write consolidated summary to {{CONSOLIDATED_OUTPUT_PATH}}

Your output MUST include (see brief for full format):
- Root cause groups with all affected surfaces and merge rationale
- Deduplication log (which findings merged, why)
- Bead IDs filed, with priority breakdown
- Overall verdict

---
## Consolidation Brief

**Review round**: {{REVIEW_ROUND}}
**Data file**: {{DATA_FILE_PATH}}
**Consolidated output**: {{CONSOLIDATED_OUTPUT_PATH}}
**Timestamp**: {{TIMESTAMP}}

**Expected report paths** (all must exist before consolidation begins):
{{EXPECTED_REPORT_PATHS}}

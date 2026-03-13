# Pest Control -- CCO (Pre-Spawn Nitpickers Audit)

**Session**: `_session-ad3280`
**Timestamp**: 20260220-163950
**Auditor**: Pest Control (Opus 4.6)

## Previews Audited

| Review Type | Preview Path |
|---|---|
| clarity | `.beads/agent-summaries/_session-ad3280/previews/review-clarity-preview.md` |
| edge-cases | `.beads/agent-summaries/_session-ad3280/previews/review-edge-cases-preview.md` |
| correctness | `.beads/agent-summaries/_session-ad3280/previews/review-correctness-preview.md` |
| excellence | `.beads/agent-summaries/_session-ad3280/previews/review-excellence-preview.md` |

---

## Check 1: File list matches git diff -- PASS

**Ground truth** (`git diff --name-only 201ee96~1..HEAD`):
```
agents/big-head.md
agents/nitpicker.md
orchestration/RULES.md
orchestration/templates/pantry.md
orchestration/templates/scout.md
scripts/compose-review-skeletons.sh
scripts/fill-review-slots.sh
scripts/sync-to-claude.sh
```

**All 4 previews list** (line 35, space-separated):
```
agents/big-head.md agents/nitpicker.md orchestration/RULES.md orchestration/templates/pantry.md orchestration/templates/scout.md scripts/compose-review-skeletons.sh scripts/fill-review-slots.sh scripts/sync-to-claude.sh
```

Exact match. 8 files in both. No missing, no extra.

---

## Check 2: Same file list -- PASS

All 4 previews contain identical file lists on line 35. Verified by direct text comparison of all 4 files.

---

## Check 3: Same commit range -- PASS

All 4 previews reference **`201ee96~1..HEAD`** (line 30). Consistent across all prompts.

Commit range covers 4 commits:
```
779ead3 fix: improve Scout agent type tie-breaking (ant-farm-w7p)
cf2ceb1 refactor: add severity conflict handling guidance (ant-farm-7k1)
7feb9c8 feat: add per-review-type scope fences (ant-farm-cifp)
201ee96 feat: parallelize review prompt composition (ant-farm-0cf)
```

---

## Check 4: Correct focus areas -- FAIL (structural)

**Finding**: None of the 4 preview prompts contain review-type-specific focus areas. The body text in all 4 is identical -- it is Big Head consolidation language, not Nitpicker review instructions.

**Evidence** -- lines 6-19 in ALL 4 previews are identical:
```
Consolidate the 4 Nitpicker reports into a unified summary.

Step 0: Read your consolidation brief from .beads/agent-summaries/_session-ad3280/prompts/review-{type}.md
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
```

This is the Big Head consolidation workflow, NOT the Nitpicker review workflow. The correct Nitpicker skeleton body (from `orchestration/templates/nitpicker-skeleton.md` lines 19-42) should read:
```
Perform a {REVIEW_TYPE} review of the completed work.
...
```

**Root cause**: The `compose-review-skeletons.sh` `extract_agent_section()` function extracted the wrong template body into the Nitpicker skeletons. The skeleton files in `.beads/agent-summaries/_session-ad3280/review-skeletons/skeleton-clarity.md` (etc.) already contain the Big Head body, so this happened during skeleton composition, before slot filling.

**Mitigating factor**: The Nitpicker agent definition (`agents/nitpicker.md`) contains the full review-type-specific specialization blocks (lines 35-158), including focus areas, severity calibration, heuristics, and NOT YOUR RESPONSIBILITY lists. The agent reads this at spawn time regardless of the prompt content. However, the prompt body actively instructs the agent to "Consolidate reports" and "File ONE bead per root cause" which directly contradicts the agent definition's "Do NOT file issues -- only Big Head files issues."

**Impact**: Conflicting instructions between the prompt body (consolidation) and the agent definition (review). The Nitpicker may follow the prompt's consolidation instructions instead of its agent definition's review instructions.

---

## Check 5: No bead filing instruction -- PASS (with caveat)

All 4 previews contain "Do NOT file beads -- Big Head handles all bead filing." on line 44.

**Caveat**: Line 18 of ALL 4 previews also says `7. File ONE bead per root cause: bd create --type=bug --priority=<P> --title="<title>"` -- this is a direct instruction TO file beads, contradicting the prohibition on line 44. This is a consequence of the Check 4 failure (wrong body text). Technically the explicit prohibition exists, so this check passes, but the conflicting instruction is a risk.

---

## Check 6: Report format reference -- PASS

Each preview specifies the correct, unique output path on line 40:

| Review Type | Output Path |
|---|---|
| clarity | `.beads/agent-summaries/_session-ad3280/review-reports/clarity-review-20260220-113708.md` |
| edge-cases | `.beads/agent-summaries/_session-ad3280/review-reports/edge-cases-review-20260220-113708.md` |
| correctness | `.beads/agent-summaries/_session-ad3280/review-reports/correctness-review-20260220-113708.md` |
| excellence | `.beads/agent-summaries/_session-ad3280/review-reports/excellence-review-20260220-113708.md` |

All use the same timestamp `20260220-113708`. Paths follow the convention `{SESSION_DIR}/review-reports/{type}-review-{timestamp}.md`.

---

## Check 7: Messaging guidelines -- FAIL (structural)

**Finding**: None of the 4 preview prompts contain messaging guidelines. The Nitpicker agent definition (`agents/nitpicker.md`, lines 162-170) contains the messaging guidance:

```
Message a teammate Nitpicker when you find something that clearly belongs to their domain:
- To Clarity: "Found misleading comment in file.py:L42 -- may want to review."
- To Edge Cases: "Found unvalidated external input at script.sh:L88 -- could be boundary issue."
...
Do NOT message for status updates. Do NOT report the finding yourself AND message -- pick one.
```

These guidelines are in the agent definition but NOT in the preview/prompt content. The CCO criterion requires "Each prompt includes guidance on when to message other Nitpickers."

**Mitigating factor**: Same as Check 4 -- the agent definition provides this at runtime.

---

## Additional Finding: Unfilled Slot Marker

All 4 previews contain the raw slot marker `{{CONSOLIDATED_OUTPUT_PATH}}` on line 19. This is a Big Head slot that `fill-review-slots.sh` only fills for the Big Head skeleton (line 248 of the script), not for Nitpicker skeletons. This is a direct symptom of the wrong body text being injected (Check 4).

**Evidence** (grep output):
```
review-clarity-preview.md:19:8. Write consolidated summary to {{CONSOLIDATED_OUTPUT_PATH}}
review-edge-cases-preview.md:19:8. Write consolidated summary to {{CONSOLIDATED_OUTPUT_PATH}}
review-correctness-preview.md:19:8. Write consolidated summary to {{CONSOLIDATED_OUTPUT_PATH}}
review-excellence-preview.md:19:8. Write consolidated summary to {{CONSOLIDATED_OUTPUT_PATH}}
```

---

## Verdict Summary

| Check | Result | Notes |
|---|---|---|
| 1. File list matches git diff | **PASS** | Exact 8-file match |
| 2. Same file list | **PASS** | Identical across all 4 |
| 3. Same commit range | **PASS** | `201ee96~1..HEAD` in all 4 |
| 4. Correct focus areas | **FAIL** | All 4 have Big Head body, no review-type focus areas in prompt |
| 5. No bead filing instruction | **PASS** | Present on line 44 (contradicted by line 18) |
| 6. Report format reference | **PASS** | Correct unique paths with shared timestamp |
| 7. Messaging guidelines | **FAIL** | Not present in prompt content |

## Overall Verdict: FAIL

**Failed checks**: 4 (focus areas) and 7 (messaging guidelines).

**Root cause**: The Nitpicker skeleton composition (`compose-review-skeletons.sh`) injected the Big Head consolidation body text into all 4 Nitpicker skeletons instead of the Nitpicker review body. This caused:
1. Wrong instructions in the prompt body (consolidation instead of review)
2. Missing review-type-specific focus areas
3. Missing messaging guidelines
4. An unfilled `{{CONSOLIDATED_OUTPUT_PATH}}` slot marker
5. A contradictory bead-filing instruction (line 18) vs. prohibition (line 44)

**Risk assessment**: The Nitpicker agent definition (`agents/nitpicker.md`) contains the correct review methodology, focus areas, and messaging guidelines. At runtime, the agent will receive BOTH its definition AND the prompt. The conflicting "Consolidate the 4 Nitpicker reports" instruction could confuse the agent into attempting consolidation instead of performing a review. The "File ONE bead per root cause" instruction could cause unauthorized bead filing despite the later prohibition.

**Recommendation**: Do NOT spawn the Nitpickers until the skeleton composition is fixed. The `compose-review-skeletons.sh` `extract_agent_section()` function needs investigation -- it appears to have extracted the Big Head body instead of the Nitpicker body for all 4 Nitpicker skeletons.

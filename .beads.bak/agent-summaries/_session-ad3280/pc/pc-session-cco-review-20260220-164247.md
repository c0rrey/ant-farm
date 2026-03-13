# Pest Control - CCO (Pre-Spawn Nitpickers Audit)

**Timestamp**: 20260220-164247
**Audited previews**:
- `.beads/agent-summaries/_session-ad3280/previews/review-clarity-preview.md`
- `.beads/agent-summaries/_session-ad3280/previews/review-edge-cases-preview.md`
- `.beads/agent-summaries/_session-ad3280/previews/review-correctness-preview.md`
- `.beads/agent-summaries/_session-ad3280/previews/review-excellence-preview.md`

**Corresponding prompt files** (verified identical to previews via `fill-review-slots.sh` line 213: `cp "$out_prompt" "$out_preview"`):
- `.beads/agent-summaries/_session-ad3280/prompts/review-clarity.md`
- `.beads/agent-summaries/_session-ad3280/prompts/review-edge-cases.md`
- `.beads/agent-summaries/_session-ad3280/prompts/review-correctness.md`
- `.beads/agent-summaries/_session-ad3280/prompts/review-excellence.md`

---

## Check 1: File list matches git diff -- PASS

**Commit range in all 4 prompts**: `201ee96~1..HEAD`

**Actual `git diff --name-only 201ee96~1..HEAD` output** (8 files):
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

**File list in all 4 prompts** (line 36 in each):
```
agents/big-head.md agents/nitpicker.md orchestration/RULES.md orchestration/templates/pantry.md orchestration/templates/scout.md scripts/compose-review-skeletons.sh scripts/fill-review-slots.sh scripts/sync-to-claude.sh
```

All 8 files present in git diff appear in prompts. No extra files in prompts. **Exact match.**

---

## Check 2: Same file list -- PASS

All 4 prompts contain the identical file list string on their line 36:
```
agents/big-head.md agents/nitpicker.md orchestration/RULES.md orchestration/templates/pantry.md orchestration/templates/scout.md scripts/compose-review-skeletons.sh scripts/fill-review-slots.sh scripts/sync-to-claude.sh
```

No subsets, no differences between prompts.

---

## Check 3: Same commit range -- PASS

All 4 prompts specify: `**Commit range**: 201ee96~1..HEAD` (line 31 in each).

Cross-checked against commits in range:
- `201ee96` feat: parallelize review prompt composition via bash scripts (ant-farm-0cf)
- `7feb9c8` feat: add per-review-type scope fences to nitpicker agent definition (ant-farm-cifp)
- `cf2ceb1` refactor: add severity conflict handling guidance to big-head.md (ant-farm-7k1)
- `779ead3` fix: improve Scout agent type tie-breaking with deep catalog reads and explicit fallback (ant-farm-w7p)

The `~1` suffix on the first commit correctly includes that commit in the range.

---

## Check 4: Correct focus areas -- PASS

**Architecture note**: The previews/prompts are team member task descriptions that say "Perform a {type} review" and instruct the Nitpicker to read its brief from the prompt path. The actual review-type-specific focus areas, scope fences, severity calibration, and heuristics live in the `nitpicker` agent definition (`agents/nitpicker.md`), which is loaded as the agent's system prompt when the team is created with agent type `nitpicker`.

**Verified in `agents/nitpicker.md`** -- each type has a distinct, dedicated specialization block:

| Review Type | Specialization Block | Scope Fences (NOT YOUR RESPONSIBILITY) | Severity Calibration | Heuristics |
|---|---|---|---|---|
| **Clarity** | Lines 41-67 | Edge Cases, Correctness, Excellence explicitly excluded | P1=misleading names/comments, P2=requires significant effort, P3=could be clearer | Read names aloud, check docstrings vs impl, intra-file drift |
| **Edge Cases** | Lines 70-98 | Clarity, Correctness, Excellence explicitly excluded | P1=data loss/crashes, P2=incorrect but recoverable, P3=unlikely condition | Trace external inputs, bare except, file ops, off-by-one |
| **Correctness** | Lines 101-129 | Clarity, Edge Cases, Excellence explicitly excluded | P1=wrong output on common inputs or AC unmet, P2=occasional wrong output, P3=unusual conditions | bd show for AC, trace return values, inverted logic, grep callers |
| **Excellence** | Lines 132-159 | Clarity, Edge Cases, Correctness explicitly excluded | P1=exploitable security vuln, P2=perf at scale or maintenance burden, P3=best-practice miss | User-controlled values, repeated code, function length/nesting |

Focus areas are genuinely distinct across all 4 types. NOT copy-pasted.

**Key distinction from the preview bodies**: The 4 preview files themselves have identical bodies (same template structure: workflow steps, required report sections). This is correct by design -- the preview is the task assignment, and the specialization comes from the agent definition. The first sentence of each preview differentiates which block to activate:
- clarity-preview: "Perform a clarity review"
- edge-cases-preview: "Perform a edge-cases review"
- correctness-preview: "Perform a correctness review"
- excellence-preview: "Perform a excellence review"

The Nitpicker agent workflow step 2 says: "Identify your review type from the first sentence of your prompt" -- so the dispatch mechanism is present.

---

## Check 5: No bead filing instruction -- PASS

All 4 prompts contain the prohibition in two places:
1. Line 26: `Do NOT file beads (\`bd create\`) -- Big Head handles all bead filing.`
2. Line 45: `Do NOT file beads -- Big Head handles all bead filing.`

Additionally, the `nitpicker.md` agent definition (line 28) reinforces: `Do NOT file issues -- only Big Head files issues.`

---

## Check 6: Report format reference -- PASS

Each prompt specifies the correct output path with the shared timestamp `20260220-113708`:

| Review Type | Report Output Path (line 41) |
|---|---|
| Clarity | `.beads/agent-summaries/_session-ad3280/review-reports/clarity-review-20260220-113708.md` |
| Edge Cases | `.beads/agent-summaries/_session-ad3280/review-reports/edge-cases-review-20260220-113708.md` |
| Correctness | `.beads/agent-summaries/_session-ad3280/review-reports/correctness-review-20260220-113708.md` |
| Excellence | `.beads/agent-summaries/_session-ad3280/review-reports/excellence-review-20260220-113708.md` |

All 4 use the same timestamp (20260220-113708) as required by the review timestamp convention. Path format matches `{SESSION_DIR}/review-reports/{type}-review-{timestamp}.md`.

---

## Check 7: Messaging guidelines -- PASS

All 4 prompts include step 5 in the workflow (line 17): `Message relevant Nitpickers if you find cross-domain issues`

Additionally, the `nitpicker.md` agent definition includes a full "Cross-Review Messaging" section (lines 162-170) with:
- Explicit examples of when to message each review type
- Direction to pick one (message OR report, not both)
- Prohibition on status-update messages

---

## Additional Check: Not Big Head Consolidation Body -- PASS

**User specifically requested verification that each Nitpicker has its own review-type-specific body, NOT the Big Head consolidation body.**

Evidence:
- Each preview says "Perform a {type} review" (not "consolidate" or "deduplicate")
- Each preview's workflow is: read files, catalog findings, group by root cause, write report, message Nitpickers
- Big Head's workflow (from `agents/big-head.md`) is entirely different: read 4 reports, build findings inventory, group by root cause, merge, file issues via `bd create`
- The Big Head brief is a separate file: `.beads/agent-summaries/_session-ad3280/prompts/review-big-head-consolidation.md` (not audited here, but confirmed distinct)

---

## Additional Check: No Unfilled Slot Markers -- PASS

Grep for `{{[A-Z_]+}}` across all preview and prompt files returned zero matches. All slot markers were successfully filled by `fill-review-slots.sh`.

---

## Additional Check: Self-Referential Brief Path -- INFO (not a failure)

Each preview instructs: `Step 0: Read your full review brief from .beads/agent-summaries/_session-ad3280/prompts/review-{type}.md`

This path points to the prompt file itself (identical content to the preview). Since the preview IS the combined format (skeleton body + review brief), the Nitpicker reading that path will get the same content it was already spawned with. This is a no-op read but not harmful -- the agent will simply re-read what it already has. This is an artifact of the `fill-review-slots.sh` architecture where `DATA_FILE_PATH` is set to the prompt's own path (line 195: `local data_file_path="${SESSION_DIR}/prompts/review-${review_type}.md"`).

---

## Verdict: PASS

All 7 required checks pass. No failures detected.

| Check | Result |
|---|---|
| 1. File list matches git diff | PASS |
| 2. Same file list across all 4 | PASS |
| 3. Same commit range across all 4 | PASS |
| 4. Correct focus areas per type | PASS |
| 5. No bead filing instruction | PASS |
| 6. Report format reference | PASS |
| 7. Messaging guidelines | PASS |
| Bonus: Not Big Head body | PASS |
| Bonus: No unfilled slots | PASS |

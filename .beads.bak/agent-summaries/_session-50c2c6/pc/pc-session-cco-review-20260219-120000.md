# Pest Control -- CCO (Pre-Spawn Nitpickers Audit)

**Checkpoint**: CCO-review (Nitpickers pre-spawn prompt audit)
**Session**: _session-50c2c6
**Timestamp**: 20260219-120000
**Audited previews**:
1. `.beads/agent-summaries/_session-50c2c6/previews/review-clarity-preview.md`
2. `.beads/agent-summaries/_session-50c2c6/previews/review-edge-cases-preview.md`
3. `.beads/agent-summaries/_session-50c2c6/previews/review-correctness-preview.md`
4. `.beads/agent-summaries/_session-50c2c6/previews/review-excellence-preview.md`
5. `.beads/agent-summaries/_session-50c2c6/previews/review-big-head-preview.md`

**Referenced prompt briefs** (inlined into previews):
- `.beads/agent-summaries/_session-50c2c6/prompts/review-clarity.md`
- `.beads/agent-summaries/_session-50c2c6/prompts/review-edge-cases.md`
- `.beads/agent-summaries/_session-50c2c6/prompts/review-correctness.md`
- `.beads/agent-summaries/_session-50c2c6/prompts/review-excellence.md`
- `.beads/agent-summaries/_session-50c2c6/prompts/review-big-head-consolidation.md`

---

## Check 1: File list matches git diff -- PASS

**Method**: Ran `git diff --name-only ea25412..c1a7157` and compared against the file lists in all 4 Nitpicker previews.

**Git diff output** (7 files):
```
orchestration/RULES.md
orchestration/templates/big-head-skeleton.md
orchestration/templates/checkpoints.md
orchestration/templates/nitpicker-skeleton.md
orchestration/templates/pantry.md
orchestration/templates/queen-state.md
orchestration/templates/reviews.md
```

**All 4 Nitpicker previews list** (identical across all 4):
```
- orchestration/RULES.md
- orchestration/templates/big-head-skeleton.md
- orchestration/templates/checkpoints.md
- orchestration/templates/nitpicker-skeleton.md
- orchestration/templates/pantry.md
- orchestration/templates/queen-state.md
- orchestration/templates/reviews.md
```

**Verdict**: Exact match. 7 files in diff, 7 files in each prompt. No missing files, no extra files.

---

## Check 2: Same file list -- PASS

All 4 Nitpicker previews contain the identical 7-file list (verified by line-for-line comparison of the "Files to review" sections in each preview at lines 38-44 for clarity, lines 38-44 for edge-cases, lines 38-44 for correctness, lines 38-44 for excellence). No prompt uses a different subset.

---

## Check 3: Same commit range -- PASS

All 4 Nitpicker previews reference the same commit range:
- Clarity preview line 34: `**Commit range**: ea25412..c1a7157 (11 commits)`
- Edge-cases preview line 34: `**Commit range**: ea25412..c1a7157 (11 commits)`
- Correctness preview line 34: `**Commit range**: ea25412..c1a7157 (11 commits)`
- Excellence preview line 34: `**Commit range**: ea25412..c1a7157 (11 commits)`

All reference `ea25412..c1a7157 (11 commits)`. Identical.

---

## Check 4: Correct focus areas -- PASS

Each prompt has focus areas specific to its review type. They are NOT copy-pasted identically.

**Clarity** (preview lines 48-52):
1. Code readability
2. Documentation
3. Consistency
4. Naming
5. Structure

**Edge Cases** (preview lines 48-54):
1. Input validation
2. Error handling
3. Boundary conditions
4. File operations
5. Concurrency
6. Platform differences

**Correctness** (preview lines 63-68):
1. Acceptance criteria verification
2. Logic correctness
3. Data integrity
4. Regression risks
5. Cross-file consistency
6. Algorithm correctness

**Excellence** (preview lines 48-55):
1. Best practices
2. Performance
3. Security
4. Maintainability
5. Architecture
6. Scalability
7. Modern features

All focus areas are appropriate to their review type. No copy-paste detected across prompts.

Additionally, the correctness preview (lines 46-58) includes a "Task IDs for Acceptance Criteria Verification" section listing 11 task IDs (ant-farm-ha7a.1 through ant-farm-ha7a.11), which is unique to the correctness reviewer and appropriate for AC verification. This is a quality differentiator.

---

## Check 5: No bead filing instruction -- PASS

Each of the 4 Nitpicker previews contains an explicit prohibition on bead filing:

- **Clarity preview** line 21: `Do NOT file beads (\`bd create\`) -- Big Head handles all bead filing.`
  Also repeated at line 65 in the instructions section: `Do NOT file beads -- Big Head handles all bead filing.`
- **Edge-cases preview** line 21: `Do NOT file beads (\`bd create\`) -- Big Head handles all bead filing.`
  Also repeated at line 65.
- **Correctness preview** line 21: `Do NOT file beads (\`bd create\`) -- Big Head handles all bead filing.`
  Also repeated at line 83.
- **Excellence preview** line 21: `Do NOT file beads (\`bd create\`) -- Big Head handles all bead filing.`
  Also repeated at line 69.

All 4 prompts contain the prohibition, each stated twice (once in the preamble workflow, once in the brief instructions section).

---

## Check 6: Report format reference -- PASS

Each prompt specifies the correct output path using the session directory and shared timestamp:

- **Clarity**: `{SESSION_DIR}/review-reports/clarity-review-20260219-120000.md` (preview line 10 and line 63)
- **Edge-cases**: `{SESSION_DIR}/review-reports/edge-cases-review-20260219-120000.md` (preview line 10 and line 64)
- **Correctness**: `{SESSION_DIR}/review-reports/correctness-review-20260219-120000.md` (preview line 10 and line 81)
- **Excellence**: `{SESSION_DIR}/review-reports/excellence-review-20260219-120000.md` (preview line 10 and line 67)

All use the same timestamp `20260219-120000`. All paths follow the `{SESSION_DIR}/review-reports/{type}-review-{timestamp}.md` convention.

The Big Head consolidation preview also correctly references all 4 report paths at lines 32-35, plus its own output path at line 28: `.beads/agent-summaries/_session-50c2c6/review-reports/review-consolidated-20260219-120000.md`.

---

## Check 7: Messaging guidelines -- PASS

Each of the 4 Nitpicker previews contains a "Messaging Guidelines" section with both "DO message" and "Do NOT message" sub-sections:

- **Clarity preview** lines 72-80: 3 "DO" reasons, 3 "Do NOT" reasons
- **Edge-cases preview** lines 72-80: 3 "DO" reasons, 3 "Do NOT" reasons
- **Correctness preview** lines 98-108: 3 "DO" reasons, 3 "Do NOT" reasons
- **Excellence preview** lines 76-84: 3 "DO" reasons, 3 "Do NOT" reasons

Content is appropriate to each review type (e.g., clarity mentions "you spot a potential edge case or correctness bug"; edge-cases mentions "you spot a clarity issue or correctness bug"; correctness mentions "you spot a clarity issue or edge case"; excellence mentions "you spot a clarity issue or correctness bug"). The cross-domain references are tailored per reviewer, not identically copy-pasted.

---

## Big Head Consolidation Preview: Supplementary Check

The Big Head preview was also audited for consistency with the Nitpicker prompts:

- **Report paths**: All 4 report paths at lines 32-35 match the output paths specified in the 4 Nitpicker prompts. CONFIRMED.
- **Timestamp consistency**: Uses `20260219-120000` throughout. CONFIRMED.
- **Deduplication protocol**: Present with explicit merge rationale requirements (lines 59-60). CONFIRMED.
- **Bead filing instructions**: Present (lines 86-96), including the prohibition on epic assignment via `bd dep add --type parent-child`. CONFIRMED.
- **Step 0 gate**: Mandatory report existence verification before proceeding (lines 37-51). CONFIRMED.
- **Consolidated summary format**: Output path specified as `.beads/agent-summaries/_session-50c2c6/review-reports/review-consolidated-20260219-120000.md`. CONFIRMED.

---

## Verdict: PASS

All 7 checks pass for all 4 Nitpicker prompts. The Big Head consolidation prompt is also consistent with the Nitpicker prompts. No defects detected.

| Check | Result |
|-------|--------|
| 1. File list matches git diff | PASS |
| 2. Same file list across prompts | PASS |
| 3. Same commit range | PASS |
| 4. Correct focus areas | PASS |
| 5. No bead filing instruction | PASS |
| 6. Report format reference | PASS |
| 7. Messaging guidelines | PASS |

**Overall**: PASS -- All prompts are complete, consistent, and ready for team spawn.

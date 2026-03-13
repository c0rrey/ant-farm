# Pest Control -- CCO (Pre-Spawn Nitpickers Audit) v2

**Checkpoint**: CCO-review (Pre-Spawn Prompt Audit for Nitpickers + Big Head)
**Session**: _session-405acc
**Commit range**: 0ebf20e..HEAD (3 commits: bc84bd0, 7c94f28, 6b26beb)
**Audited previews**:
- review-clarity-preview.md
- review-edge-cases-preview.md
- review-correctness-preview.md
- review-excellence-preview.md
- review-big-head-preview.md

---

## Check 1: File list matches git diff -- PASS

**Ground truth** (`git diff --name-only 0ebf20e..HEAD`):
1. orchestration/templates/big-head-skeleton.md
2. orchestration/templates/checkpoints.md
3. orchestration/templates/dirt-pusher-skeleton.md
4. orchestration/templates/nitpicker-skeleton.md
5. orchestration/templates/pantry.md
6. orchestration/templates/reviews.md

**Verification**: All 4 Nitpicker prompts list exactly these 6 files in their "Files to Review" sections. No extra files, no missing files.

| Prompt | Files listed | Match? |
|--------|-------------|--------|
| Clarity (lines 35-41) | 6/6 | YES |
| Edge Cases (lines 39-44) | 6/6 | YES |
| Correctness (lines 35-41) | 6/6 | YES |
| Excellence (lines 35-41) | 6/6 | YES |

**Result**: PASS

---

## Check 2: Same file list across all 4 prompts -- PASS

All 4 prompts contain identical file lists. No prompt uses a subset or superset.

**Result**: PASS

---

## Check 3: Same commit range across all 4 prompts -- PASS

| Prompt | Commit range | Line |
|--------|-------------|------|
| Clarity | 0ebf20e..HEAD | line 29 |
| Edge Cases | 0ebf20e..HEAD | line 29 |
| Correctness | 0ebf20e..HEAD | line 29 |
| Excellence | 0ebf20e..HEAD | line 29 |

**Result**: PASS

---

## Check 4: Correct focus areas -- PASS

Each prompt has distinct, domain-appropriate focus areas. They are NOT copy-pasted identically.

- **Clarity**: readability, documentation, consistency, naming, structure (5 areas)
- **Edge Cases**: input validation, error handling, boundary conditions, file operations, concurrency, platform differences (6 areas)
- **Correctness**: acceptance criteria verification, logic correctness, data integrity, regression risks, cross-file consistency, algorithm correctness (6 areas) -- additionally includes Task IDs (ant-farm-x4m, ant-farm-e9k, ant-farm-zeu) for acceptance criteria verification
- **Excellence**: best practices, performance, security, maintainability, architecture, scalability, modern features (7 areas)

No two prompts share the same focus areas. Each is appropriate for its review type.

**Result**: PASS

---

## Check 5: No bead filing instruction -- PASS

Each prompt contains "Do NOT file beads" prohibition, appearing twice per prompt (once in the header workflow section, once in the body instructions).

| Prompt | Header prohibition | Body prohibition |
|--------|-------------------|-----------------|
| Clarity | line 21 | line 65-66 |
| Edge Cases | line 21 | line 64 |
| Correctness | line 21 | line 75 |
| Excellence | line 21 | line 69 |

All use the exact wording: `Do NOT file beads (`bd create`) -- Big Head handles all bead filing.`

**Result**: PASS

---

## Check 6: Report format reference -- PASS

Each prompt specifies a unique, correctly-formatted output path with consistent timestamp (20260219-120000).

| Prompt | Output path |
|--------|------------|
| Clarity | `.beads/agent-summaries/_session-405acc/review-reports/clarity-review-20260219-120000.md` (lines 31, 63) |
| Edge Cases | `.beads/agent-summaries/_session-405acc/review-reports/edge-cases-review-20260219-120000.md` (lines 31, 64) |
| Correctness | `.beads/agent-summaries/_session-405acc/review-reports/correctness-review-20260219-120000.md` (lines 31, 72) |
| Excellence | `.beads/agent-summaries/_session-405acc/review-reports/excellence-review-20260219-120000.md` (lines 31, 67) |

All timestamps are synchronized (20260219-120000), matching the convention that the Queen generates a single timestamp per review cycle.

**Result**: PASS

---

## Check 7: Messaging guidelines -- PASS

All 4 prompts include a "Messaging Guidelines" section with DO/DON'T subsections.

| Prompt | Messaging section | DO items | DON'T items |
|--------|------------------|----------|-------------|
| Clarity | lines 69-79 | 3 | 3 |
| Edge Cases | lines 75-88 | 3 | 3 |
| Correctness | lines 88-98 | 3 | 3 |
| Excellence | lines 80-90 | 3 | 3 |

Guidelines are process-level (not domain-specific), so identical content across prompts is appropriate here.

**Result**: PASS

---

## Supplementary: Big Head Prompt Audit

The Big Head prompt is not a Nitpicker and is not subject to the 7-check framework, but was audited for structural integrity:

- **Report path references**: All 4 report paths listed (lines 32-35) with consistent timestamp 20260219-120000. PASS.
- **Step 0 mandatory gate**: Includes file existence verification before consolidation proceeds (lines 37-52). PASS.
- **Deduplication protocol**: Includes 5-step merge process with root-cause grouping format (lines 54-91). PASS.
- **Bead filing instructions**: Includes standalone bead creation with explicit note NOT to assign to epics (lines 93-103). PASS.
- **Consolidated output path**: `.beads/agent-summaries/_session-405acc/review-reports/review-consolidated-20260219-120000.md` (line 27). Timestamp matches all Nitpicker timestamps. PASS.
- **Output format template**: Full consolidated summary format included (lines 105-151). PASS.

---

## Overall Verdict: PASS

All 7 checks pass for all 4 Nitpicker prompts. Big Head prompt passes supplementary structural audit.

| Check | Result |
|-------|--------|
| 1. File list matches git diff | PASS |
| 2. Same file list | PASS |
| 3. Same commit range | PASS |
| 4. Correct focus areas | PASS |
| 5. No bead filing instruction | PASS |
| 6. Report format reference | PASS |
| 7. Messaging guidelines | PASS |
| Supplementary: Big Head | PASS |

**Verdict: PASS -- All prompts are correctly composed and ready for spawn.**

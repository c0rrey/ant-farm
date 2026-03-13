# Pest Control Verification - CCO (Pre-Spawn Nitpickers Audit)

**Checkpoint**: CCO-review
**Timestamp**: 2026-02-20T01:23:48Z
**Session**: _session-54996f
**Auditor**: Pest Control

---

## Check 1: File list matches git diff

**Verdict**: PASS

`git diff --name-only bf6e38b~1..HEAD` returns:
- orchestration/RULES.md
- orchestration/templates/big-head-skeleton.md
- orchestration/templates/pantry.md
- orchestration/templates/reviews.md

All 4 prompts list exactly these 4 files. No missing files, no extra files.

## Check 2: Same file list across all 4 prompts

**Verdict**: PASS

All 4 prompt data files (review-clarity.md, review-edge-cases.md, review-correctness.md, review-excellence.md) contain the identical "Files to review" section with the same 4 files. Each explicitly states "(identical across all 4 reviews)".

## Check 3: Same commit range across all 4 prompts

**Verdict**: PASS

All 4 prompts specify: `bf6e38b~1..HEAD (4 commits: bf6e38b, cba88a6, 0884df0, 46a776a)`. Verified against `git log --oneline bf6e38b~1..HEAD` which returns the same 4 commits.

## Check 4: Correct focus areas (distinct per review type)

**Verdict**: PASS

Focus areas are genuinely distinct and domain-appropriate:
- **Clarity**: Code readability, Documentation, Consistency, Naming, Structure (5 areas)
- **Edge Cases**: Input validation, Error handling, Boundary conditions, File operations, Concurrency, Platform differences (6 areas)
- **Correctness**: Acceptance criteria verification, Logic correctness, Data integrity, Regression risks, Cross-file consistency, Algorithm correctness (6 areas) + Task IDs section with ant-farm-tek, ant-farm-tz0q, ant-farm-crky, ant-farm-7hgn
- **Excellence**: Best practices, Performance, Security, Maintainability, Architecture, Scalability, Modern features (7 areas)

No copy-paste across prompts. Each review type has unique, relevant focus areas.

## Check 5: No bead filing instruction

**Verdict**: PASS

All 4 prompts contain: "Do NOT file beads -- Big Head handles all bead filing."
- review-clarity.md line 33
- review-edge-cases.md line 32
- review-correctness.md line 44
- review-excellence.md line 35

All 4 preview files also include: `Do NOT file beads (\`bd create\`) -- Big Head handles all bead filing.`

## Check 6: Report format reference (output paths)

**Verdict**: PASS

All 4 prompts specify explicit output paths using the pattern `{SESSION_DIR}/review-reports/{type}-review-{timestamp}.md` with consistent timestamp 20260219-120000:
- clarity-review-20260219-120000.md
- edge-cases-review-20260219-120000.md
- correctness-review-20260219-120000.md
- excellence-review-20260219-120000.md

Big Head consolidation brief references all 4 paths and uses the same timestamp for consolidated output.

## Check 7: Messaging guidelines

**Verdict**: PASS

All 4 prompts contain a "Messaging Guidelines" section with:
- "SHOULD message when" -- with domain-specific cross-references (e.g., clarity says "you spot a potential edge case")
- "Should NOT message" -- consistent across all 4 (no status updates, no general observations, no questions for Big Head)

---

## Additional Verifications

### Preview vs Prompt data file consistency: PASS
Each preview file contains the standard preamble (workflow steps, report format requirements) plus the full review brief from the corresponding prompt data file. Content matches exactly between preview and prompt data files.

### Big Head consolidation prompt: PASS
Correctly references all 4 report paths with matching timestamp, includes Step 0 gate (verify all reports exist with polling loop and error return), deduplication protocol, Step 4 checkpoint gate (await Pest Control validation before filing beads), and bead filing instructions. Scope in consolidated summary template matches git diff file list.

---

## Overall Verdict

**PASS** -- All 7 checks pass for all 4 prompts. Big Head consolidation prompt is also well-formed. No issues detected.

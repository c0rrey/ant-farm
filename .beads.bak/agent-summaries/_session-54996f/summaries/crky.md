# Summary: ant-farm-crky

**Task**: Reconcile divergent failure handling between big-head-skeleton.md and reviews.md
**Commit**: 0884df0
**Files changed**:
- orchestration/templates/big-head-skeleton.md (lines 57-66, now 57-59)
- orchestration/templates/reviews.md (lines 354-356, new authority callout added)

---

## 1. Approaches Considered

**Approach A: Make reviews.md authoritative; skeleton defers to the brief (selected)**
Update skeleton step 1 to say "follow the missing-report handling protocol in your consolidation brief (Step 0a)." Remove the contradicting fail-immediately and file-artifact instructions from the skeleton. Add an authority declaration to reviews.md Step 0a. The data file (composed by Pantry from reviews.md) becomes the single runtime source of truth. The skeleton is the spawn-time envelope; the brief is the runtime document.

**Approach B: Make skeleton authoritative; strip polling from reviews.md**
Keep the "FAIL immediately" approach in the skeleton. Simplify reviews.md Step 0a to remove the polling loop. Tradeoff: loses the polling grace period intentionally added to handle slow Nitpicker agents. The polling behavior was a deliberate design choice; removing it degrades resilience.

**Approach C: Add full polling protocol to skeleton directly**
Copy the polling loop and error return template from reviews.md into the skeleton, then remove reviews.md Step 0a. Tradeoff: creates a single authoritative source but duplicates significant content and makes future maintenance require syncing two locations. The very duplication problem we are fixing becomes worse.

**Approach D: Cross-reference with bidirectional authority declaration**
Add "the brief is authoritative" in the skeleton AND add "skeleton defers here" in reviews.md. Keep both descriptions but make the authority relationship explicit and bidirectional. Tradeoff: both descriptions still exist, so a future editor could drift them again. Less minimal than Approach A.

---

## 2. Selected Approach with Rationale

**Approach A** was selected. The brief (composed from reviews.md by Pantry) is what Big Head reads at runtime. The skeleton is only the spawn-time wrapper. Making the brief authoritative aligns with the system's existing authority chain. Removing the conflicting instructions from the skeleton eliminates the contradiction at source rather than adding override logic.

On failure artifact paths: reviews.md returns an inline structured error (no file artifact). The skeleton previously wrote to `review-consolidated-{TIMESTAMP}-FAILED.md`. By removing the skeleton's artifact instructions, the inline error return in reviews.md becomes the sole format — paths are now consistent (one format: inline error).

---

## 3. Implementation Description

**big-head-skeleton.md**: Replaced lines 57-66 (the "FAIL immediately" block with file artifact writing instructions) with 3 lines that defer to the consolidation brief:
- Step 1 now reads: "follow the missing-report handling protocol in your consolidation brief (Step 0a)"
- Added: "The brief is authoritative for this step: it specifies the polling timeout, error return format, and failure conditions"
- Retained: "Do NOT proceed to read reports or perform consolidation until the brief's Step 0a protocol completes successfully"

**reviews.md**: Added an authority callout blockquote immediately after the `### Step 0a` heading:
- "> **Authoritative source**: This section is the authoritative protocol for missing-report handling. The big-head-skeleton.md step 1 defers to this brief. If any apparent conflict exists between the skeleton and this brief, follow this brief."

---

## 4. Correctness Review

**File: orchestration/templates/big-head-skeleton.md (lines 57-59)**
- The skeleton no longer contradicts reviews.md: it defers explicitly to the brief for all missing-report handling. Correct.
- No file artifact path is specified in the skeleton. Failure artifact format is determined entirely by reviews.md (inline error). Consistent. Correct.
- "Do NOT proceed" gate is preserved. Big Head still blocks on this step until success. Correct.
- Lines outside L47-80 were not modified. Scope respected.

**File: orchestration/templates/reviews.md (lines 354-358)**
- The authority callout is placed as a blockquote directly under the heading, before any procedural content. Big Head reads it first. Correct.
- The callout explicitly names big-head-skeleton.md and states the brief wins. No ambiguity. Correct.
- Lines outside L354-424 were not modified (authority callout inserted within scope). Scope respected.

**Acceptance criteria verification:**
1. One template designated authoritative — PASS (reviews.md Step 0a is explicitly marked authoritative)
2. Other template references authoritative one rather than contradicting — PASS (skeleton step 1 defers to "your consolidation brief (Step 0a)")
3. Failure artifact paths consistent — PASS (skeleton no longer specifies a file artifact; reviews.md inline error is sole format)
4. Big Head has unambiguous instructions — PASS (skeleton defers, reviews.md is authoritative, no need to resolve contradictions)

---

## 5. Build/Test Validation

No automated test suite for markdown templates. Manual inspection confirms:
- The skeleton's step 1 no longer contains any instructions that conflict with reviews.md
- The authority callout in reviews.md is the first content an agent reads in Step 0a, ensuring the authority relationship is established before any procedural instructions
- The failure artifact path inconsistency is resolved: only one format exists (inline error return from reviews.md)

---

## 6. Acceptance Criteria Checklist

| Criterion | Status |
|-----------|--------|
| One template designated authoritative for missing-report handling | PASS |
| Other template references authoritative one rather than contradicting | PASS |
| Failure artifact paths consistent between both templates | PASS |
| Big Head has unambiguous instructions with no need to resolve contradictions | PASS |

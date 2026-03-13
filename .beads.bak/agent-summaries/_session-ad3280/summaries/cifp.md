# Task Summary: ant-farm-cifp
**Task**: Add explicit scope fencing to Nitpicker agent definitions per review type
**Commit**: 7feb9c8
**Status**: COMPLETE

---

## 1. Approaches Considered

### Approach A: Four separate agent files
Create `nitpicker-clarity.md`, `nitpicker-edge-cases.md`, `nitpicker-correctness.md`,
`nitpicker-excellence.md`. Maximum specialization and isolation. Rejected because it duplicates
all shared boilerplate (core principles, workflow, report format, messaging rules) across 4 files.
Any change to shared rules requires 4 edits. Directly violates acceptance criterion 4.

### Approach B: Single agent file with per-type specialization blocks (selected)
Extend `nitpicker.md` with a `## Per-Review-Type Specialization` section containing four clearly
delimited blocks. The agent identifies its review type from its spawn prompt (which already begins
with "Perform a clarity review" / "Perform an edge-cases review" etc. — set by the nitpicker
skeleton). Shared sections remain at the top; specialization blocks below a `---` separator.
Satisfies all four acceptance criteria.

### Approach C: Separate scope reference document
Create `nitpicker-scope-reference.md` and instruct the agent to read the section matching its type.
Avoids modifying the agent file, but requires an extra file read per review and buries the scope
fences in an auxiliary document rather than baking them into the agent's identity. Weaker than B
for calibrating the agent at spawn time.

### Approach D: Skeleton injection (no agent file changes)
Extend `nitpicker-skeleton.md` to inject a fully-filled specialization block into each spawn prompt
at review time. No agent file changes. Rejected because it moves the specialization out of the
persistent agent definition back into the spawn-time composition layer — the same problem the task
is trying to solve. Each spawn call would need to carry ~60 lines of specialization content that
could instead be in the agent definition.

### Approach E: HTML comment conditional blocks
Add all four specialization blocks inline with `<!-- REVIEW_TYPE: clarity -->` HTML comment
delimiters and instruct the agent to scan for its type. Same functional result as Approach B but
relies on HTML comment parsing, which is less explicit and harder for the agent to follow reliably
compared to named markdown section headers. Approach B's `### CLARITY REVIEWER` headers are clearer.

---

## 2. Selected Approach with Rationale

**Selected: Approach B** — single agent file with four per-type specialization blocks.

Rationale:
- Single file: shared concerns (core principles, coverage rules, messaging) are defined once
- Type activation is natural: the agent's spawn prompt already begins with "Perform a {type} review"
  (set by the nitpicker skeleton + fill-review-slots.sh) — the agent reads its type from that first sentence
- NOT YOUR RESPONSIBILITY lists: baked into the agent definition, not delegated to data files, so
  scope fences apply even if the data file is incomplete
- Severity calibration: concrete P1/P2/P3 examples per type reduce calibration drift over time
- Heuristics: review-type-specific search strategies reduce the chance of reviewers checking each
  other's territory by accident

---

## 3. Implementation Description

### File changed: agents/nitpicker.md (also synced to ~/.claude/agents/nitpicker.md)

**Structural additions** to the original 25-line agent definition:

1. **`## Core Principles (all types)`** — original content preserved, labelled as universal
2. **`## Workflow (all types)`** — original 5-step workflow expanded with steps to identify
   review type and activate specialization block before reading files
3. **`## Shared Rules (all types)`** — original prohibitions (no filing, no fixing, severity bias)
   preserved; added rule to message other reviewer instead of self-reporting cross-domain findings
4. **`## Per-Review-Type Specialization`** — new section with four blocks:

   **CLARITY REVIEWER block**:
   - Mandate: human comprehension, readability, consistency
   - What you look for: 5 concrete patterns (naming, misleading comments, style drift, structure, magic values)
   - NOT YOUR RESPONSIBILITY: edge-cases, correctness, excellence each listed by name with their domains
   - Severity calibration: P1 = misleading name that causes bugs; P2 = effortful to understand; P3 = default
   - Heuristics: 4 actionable search strategies

   **EDGE CASES REVIEWER block**:
   - Mandate: robustness at the boundaries
   - What you look for: 6 patterns (input validation, error handling, boundary conditions, I/O, race conditions, platform)
   - NOT YOUR RESPONSIBILITY: clarity, correctness, excellence each listed with their domains
   - Severity calibration: P1 = data loss/crash; P2 = incorrect observable behavior; P3 = unlikely/easy-to-diagnose
   - Heuristics: 4 actionable strategies including tracing external inputs

   **CORRECTNESS REVIEWER block**:
   - Mandate: logical soundness, acceptance criteria compliance, no regressions
   - What you look for: 6 patterns (logic errors, acceptance criteria, regression risks, cross-file consistency, algorithm, data fidelity)
   - NOT YOUR RESPONSIBILITY: clarity, edge-cases, excellence listed with their domains
   - Severity calibration: P1 = wrong output in common case OR unmet acceptance criterion; P2 = occasional wrong output; P3 = theoretical/cosmetic
   - Heuristics: 4 strategies including explicit `bd show <task-id>` instruction for acceptance criteria

   **EXCELLENCE REVIEWER block**:
   - Mandate: security, performance, maintainability, architecture
   - What you look for: 6 patterns (performance, security, maintainability, missing tests, architecture mismatches, modern features)
   - NOT YOUR RESPONSIBILITY: clarity, edge-cases, correctness listed with their domains — with specific guard against re-reporting as "maintainability" or "security"
   - Severity calibration: P1 = realistic exploit path; P2 = noticeable degradation at scale; P3 = best-practice miss (default)
   - Heuristics: 4 strategies including anti-pattern for hypothetical security risks

5. **`## Cross-Review Messaging`** — moved and expanded from the workflow section, with concrete
   example messages for handing off to each reviewer type

**Description field update**: The agent's frontmatter description now explicitly mentions
per-type specialization block activation.

---

## 4. Correctness Review

### agents/nitpicker.md

- REVIEW_TYPE identification step: Step 2 of workflow instructs agent to identify its type from the
  first sentence of its prompt. This is reliable because the nitpicker-skeleton fills `{REVIEW_TYPE}`
  into "Perform a {review_type} review" — after the ant-farm-0cf changes this becomes the
  `{{REVIEW_TYPE}}` slot filled by compose-review-skeletons.sh (statically) at skeleton creation time.
  The review type is always in the first sentence. CORRECT.

- NOT YOUR RESPONSIBILITY cross-references: each block lists all three other types by name with
  their specific domains. No two blocks claim the same territory. CORRECT.

- Severity calibration completeness: all four types have P1/P2/P3 defined with concrete examples.
  No gaps. CORRECT.

- Shared content: Core Principles, Workflow, Shared Rules, Cross-Review Messaging all appear once
  in the shared sections above the Per-Review-Type Specialization divider. CORRECT.

- No duplication: report format, coverage log requirements, "Do NOT file issues" prohibition, and
  messaging guidelines are NOT repeated inside the specialization blocks. CORRECT.

### Acceptance Criteria Verification

1. **Each Nitpicker reviewer has explicit 'not my job' boundaries that reference the other three review types by name**
   - Clarity NOT YOUR RESPONSIBILITY: "Edge Cases reviewer", "Correctness reviewer", "Excellence reviewer" — named
   - Edge Cases NOT YOUR RESPONSIBILITY: "Clarity reviewer", "Correctness reviewer", "Excellence reviewer" — named
   - Correctness NOT YOUR RESPONSIBILITY: "Clarity reviewer", "Edge Cases reviewer", "Excellence reviewer" — named
   - Excellence NOT YOUR RESPONSIBILITY: "Clarity reviewer", "Edge Cases reviewer", "Correctness reviewer" — named
   - PASS

2. **Type-specific severity calibration is defined (what constitutes P1/P2/P3 for each type)**
   - Clarity: P1 = misleading name causing bugs; P2 = effortful to understand; P3 = default (could be clearer)
   - Edge Cases: P1 = data loss/crash; P2 = incorrect recoverable behavior; P3 = unlikely/easy-to-diagnose
   - Correctness: P1 = wrong output in common case OR unmet acceptance criterion; P2 = occasional wrong output; P3 = theoretical/cosmetic
   - Excellence: P1 = realistic exploit path; P2 = noticeable degradation or significant maintenance burden; P3 = best-practice miss (default)
   - PASS

3. **Big Head deduplication load is reduced — fewer cross-type duplicate findings at source**
   - Each NOT YOUR RESPONSIBILITY list explicitly redirects cross-domain findings to the owning reviewer
   - The Cross-Review Messaging section provides concrete handoff patterns (message instead of self-report)
   - The "Do NOT report the finding yourself AND message — pick one" rule prevents double-counting
   - This is a behavioral change baked into the agent definition that reduces source-level overlap
   - PASS (acceptance criteria is about reducing load, not eliminating it — the mechanism is in place)

4. **Shared concerns (report format, output structure, messaging guidelines) remain in one place, not duplicated across 4 files**
   - The implementation is a single file with shared sections at the top
   - Report format, coverage log, "Do NOT file issues", "Do NOT fix code", severity bias rule, messaging guidelines — all appear once in shared sections
   - The four specialization blocks contain ONLY type-specific content: mandate, what-to-look-for, NOT-YOUR-RESPONSIBILITY, severity calibration, heuristics
   - PASS

---

## 5. Build/Test Validation

**Manual review**: Read the completed nitpicker.md against each acceptance criterion.

**Cross-domain boundary check**: Traced each NOT YOUR RESPONSIBILITY entry to verify it maps to a
"What you look for" entry in the named reviewer's specialization block:
- Clarity → "Edge Cases owns: missing input validation" maps to Edge Cases "What you look for: Missing input validation" — VERIFIED
- Clarity → "Correctness owns: logic bugs" maps to Correctness "What you look for: Logic errors" — VERIFIED
- Edge Cases → "Correctness owns: happy-path logic" maps to Correctness mandate "code does what it claims" — VERIFIED
- Correctness → "Edge Cases owns: invalid inputs" maps to Edge Cases mandate "robustness at the boundaries" — VERIFIED
- Excellence → "Clarity owns: naming/comments/style" with guard "do not re-report style issues as maintainability" — VERIFIED
- Excellence → "Edge Cases owns: input validation" with guard "do not re-report as security unless active exploit path" — VERIFIED

**Severity overlap check**: P1/P2/P3 definitions across the four types do not contradict each other.
A "P3 by excellence" finding (a loop that could be a list comprehension) would not be P1 or P2 by
any other type's calibration. A "P1 by correctness" finding (acceptance criterion unmet) would not
be P3 by any other type. Calibrations are consistent at the boundary. VERIFIED.

**No regression to shared content**: Original core principles and prohibitions ("Every finding must
have a file:line reference", "Do NOT file issues", "When in doubt about severity, go lower") are
preserved verbatim in the shared sections. VERIFIED.

---

## 6. Acceptance Criteria Checklist

| # | Criterion | Status |
|---|-----------|--------|
| 1 | Each Nitpicker reviewer has explicit 'not my job' boundaries that reference the other three review types by name | PASS |
| 2 | Type-specific severity calibration is defined (what constitutes P1/P2/P3 for each type) | PASS |
| 3 | Big Head deduplication load is reduced — fewer cross-type duplicate findings at source | PASS |
| 4 | Shared concerns (report format, output structure, messaging guidelines) remain in one place, not duplicated across 4 files | PASS |

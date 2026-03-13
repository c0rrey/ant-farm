# Task Summary: ant-farm-ygmj.3

**Task**: Rewrite fix workflow for in-team agents
**Commit**: f686f88
**File changed**: orchestration/templates/reviews.md (L983-L1112 rewritten; L1114-1133 unchanged)

---

## 1. Approaches Considered

**Approach A: Minimal Patch (Surgical Edits)**
Keep existing P1/P2/Wave/Re-Run structure; replace only lines referencing standalone Task agents with team-spawn language; insert new subsections for inner loop, naming, Pantry/CCO skip.
- Pro: Low diff volume; low risk of disturbing surrounding context
- Con: Old section structure (TDD test-writing wave, P1/P2 split with test-spec block) was not designed for the in-team model; layering new concepts onto an incompatible skeleton creates an inconsistent, harder-to-read result

**Approach B: Full Section Replacement with Narrative Flow**
Replace L983-L1050 completely; preserve Handle P3 Issues; order content as: overview -> Scout -> Pantry/CCO skip -> naming -> fix DP prompt -> inner loop -> wave composition -> round transition -> re-run reviews.
- Pro: Coherent new structure; directly addresses root cause (old architecture does not map to new)
- Con: Higher diff volume; requires more careful review to avoid breaking surrounding context

**Approach C: Subsection Insertion with Deprecation Markers**
Keep all existing Fix Workflow text; insert new subsections labeled "NEW" or "DEPRECATED" for old content.
- Pro: Preserves full history in-file; easy rollback reference
- Con: Not production quality; mixing deprecated and new content creates confusion for agents reading the document

**Approach D: Promote Fix Workflow to H2 Top-Level Section**
Move Fix Workflow to a new `## Fix Workflow` heading; rewrite under that new structure; leave a pointer line at L983.
- Pro: Better document organization; signals architectural importance
- Con: Task scope is L983-1070 only; changing heading level affects RULES.md references and violates scope boundaries

**Approach E: Atomic Replacement with Protocol-First Layout**
Replace L983-L1050 in full; use protocol-first ordering (Scout auto-approval and Pantry/CCO skip context first, then naming, prompt structure, inner loop, wave, round transition, re-run); keep Handle P3 Issues unchanged.
- Pro: Most complete and unambiguous; all 7 acceptance criteria map directly to named subsections; protocol ordering matches how an agent reads/uses the document
- Con: Same diff volume as Approach B; no meaningful downside vs B

---

## 2. Selected Approach

**Approach E (Atomic Replacement with Protocol-First Layout)**

Rationale: The current Fix Workflow was architecturally incompatible with the in-team design — it described standalone Task agents, TDD test-writing waves, and Big Head-composed briefs. None of these map to the new design. A full replacement was the only way to produce a coherent result. Protocol-first ordering was chosen because Scout auto-approval and Pantry/CCO skip are prerequisites to understanding why fix agents work differently from the original design — they must appear before the naming and prompt structure subsections.

---

## 3. Implementation Description

Replaced orchestration/templates/reviews.md L983-L1050 ("Fix Workflow" through "Re-Run Reviews") with new content organized into seven subsections:

1. **Fix-Cycle Scout and Auto-Approval** — documents auto-approval (no user confirmation gate) with SSV mechanical safety net (PASS/FAIL branches, max 1 retry on SSV FAIL)
2. **Pantry and CCO Skip Rationale** — explains why beads validated by CCB + Scout strategy validated by SSV make Pantry and CCO redundant for fix briefs
3. **Fix Team Member Naming** — table with fix-dp-N, fix-pc-wwd, fix-pc-dmvdc names plus round suffix convention (-r2, -r3) to avoid name collisions in persistent team
4. **Fix DP Prompt Structure** — lean code-block prompt with bead ID as source of truth, bd show command, SendMessage to fix-pc-wwd after commit
5. **Fix Inner Loop Protocol** — ASCII flow diagram showing DP -> fix-pc-wwd -> fix-pc-dmvdc -> iterate path; max 2 retries; escalation to Queen on retry limit; model assignments (Haiku for WWD, Sonnet for DMVDC)
6. **Wave Composition** — simplified single-wave (P1 + P2 concurrent, no separate test-writing wave); fix-pc-wwd and fix-pc-dmvdc spawned once per round, not per DP
7. **Round Transition via SendMessage** — four-step SendMessage sequence re-tasking correctness, edge-cases, and big-head reviewers with round N+1 scope; Clarity/Drift left idle after round 1
8. **Re-Run Reviews (MANDATORY)** — CCB outcome branches: zero P1/P2 ends loop, P1/P2 remain returns to user prompt

Handle P3 Issues (L1114-1133 in new numbering) was not modified.

---

## 4. Correctness Review

**File**: orchestration/templates/reviews.md

Verified:
- L975-982 (context before Fix Workflow): unchanged; "Fix Workflow below" reference still accurate
- L983-985 (new Fix Workflow opening): correctly identifies persistent team, Task tool with `team_name: "nitpickers"`, and SendMessage
- L987-995 (Scout auto-approval): auto-approval stated clearly; SSV gate documented with PASS/FAIL branches and max 1 retry
- L997-1004 (Pantry/CCO skip): both rationales complete; bead-as-brief rationale cites CCB; CCO rationale cites CCB + SSV
- L1006-1016 (naming table): all three roles present; round 1 and round 2+ names correct; round suffix explanation present
- L1018-1037 (fix DP prompt structure): lean prompt with bead ID, bd show, commit recording, SendMessage to fix-pc-wwd, go idle
- L1039-1066 (inner loop): ASCII diagram covers PASS/FAIL for both WWD and DMVDC; retry limit stated as max 2 total; Queen escalation path on retry limit; model assignments (Haiku/Sonnet) documented
- L1068-1080 (wave composition): max 7 DPs per wave; file overlap prohibition; fix-pc-wwd and fix-pc-dmvdc spawned once per round; P1+P2 in single wave noted; references dependency-analysis.md
- L1082-1104 (round transition): SendMessage to correctness, edge-cases, big-head; all required fields listed (round, commit range, changed files, task IDs, brief path, output path); Clarity/Drift idle rationale present
- L1106-1112 (re-run reviews): CCB PASS + zero P1/P2 terminates; CCB PASS + P1/P2 remain returns to user prompt
- L1114-1133 (Handle P3): unchanged and intact

No adjacent issues modified. No out-of-scope files touched.

---

## 5. Build/Test Validation

This is a documentation-only change (markdown template file). No build or test commands apply.

Structural validation performed:
- Markdown heading hierarchy consistent (###, #### levels match surrounding file)
- Code blocks properly fenced (triple backtick)
- Table syntax valid (three-column, header separator row present)
- File ends with a newline after L1133

---

## 6. Acceptance Criteria Checklist

- [x] **AC1**: Fix workflow section describes fix DPs and fix PCs spawning into the persistent team via Task with team_name parameter
  - L985: "using the Task tool with `team_name: \"nitpickers\"`"; L1008: "spawn into the Nitpicker team" — PASS

- [x] **AC2**: Fix inner loop protocol documented: DP -> fix-pc-wwd -> fix-pc-dmvdc -> iterate on fail (with max 2 retries)
  - L1039-1066: ASCII diagram shows full DP -> fix-pc-wwd -> fix-pc-dmvdc flow; L1062: "maximum of 2 retries total" — PASS

- [x] **AC3**: Pantry/CCO skip rationale documented with clear explanation of why beads + CCB + SSV are sufficient
  - L997-1004: "Fix briefs do not go through Pantry or CCO" with separate rationale for each; CCB and SSV cited — PASS

- [x] **AC4**: Round transition protocol uses SendMessage to re-task Correctness and Edge Cases reviewers
  - L1082-1104: "Round Transition via SendMessage" with numbered steps sending to `correctness`, `edge-cases`, and `big-head` — PASS

- [x] **AC5**: Fix-cycle Scout documented as auto-approved with SSV gate
  - L987-995: "Auto-approval: The fix-cycle Scout strategy is auto-approved"; SSV PASS/FAIL branches documented — PASS

- [x] **AC6**: Fix DP prompt structure shown (lean prompt, bead as source of truth, message fix-pc-wwd after commit)
  - L1018-1037: code block with bead ID, `bd show <bead-id>`, `bd update <bead-id> --note="commit: <hash>"`, `SendMessage to fix-pc-wwd` — PASS

- [x] **AC7**: Naming convention for fix team members documented (fix-dp-N, fix-pc-wwd, fix-pc-dmvdc, round suffixes)
  - L1006-1016: table with fix-dp-1/fix-dp-r2-1, fix-pc-wwd/fix-pc-wwd-r2, fix-pc-dmvdc/fix-pc-dmvdc-r2; round suffix explanation — PASS

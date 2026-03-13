# Summary: ant-farm-asdl.3
**Task**: Update agents/big-head.md with dedup instruction and --body-file reference
**Status**: CLOSED
**Commit**: ad364ca
**Files changed**: agents/big-head.md

---

## 1. Approaches Considered

**Approach A — Minimal terse prose (one-line steps)**
Add very concise one-line steps with no command examples, consistent with the general prose tone of the file. Pros: smallest diff, consistent style. Cons: mirrors the problem being fixed — prose without concrete commands is what agents ignore in practice (per the root cause analysis).

**Approach B — Full bash code blocks in agent definition**
Mirror big-head-skeleton.md exactly, embedding multi-line heredoc examples directly in the agent definition. Pros: maximally concrete, highest chance of compliance. Cons: over-engineered for a 36-line agent definition file; the skeleton is the runtime prompt, so duplicating it verbatim adds maintenance burden without additional benefit.

**Approach C — Reference to skeleton as authoritative source**
Replace steps with pointers: "See big-head-skeleton.md step 10 for canonical example." Pros: DRY, no duplication. Cons: agents/big-head.md is a persistent agent definition, not a runtime prompt. An agent reading its own definition cannot follow an external file reference. Must be self-contained.

**Approach D (SELECTED) — Directive prose with inline command examples**
Each step includes the concrete command inline using backtick formatting, consistent with the existing file style (step 5 uses backtick-wrapped commands inline). Step 6 names `bd list --status=open -n 0 --short` explicitly; step 7 names `bd create --body-file` explicitly and adds a "Never use inline -d" prohibition. Matches the exact text specified in the plan file (ticklish-spinning-rose.md, section 3a).

**Approach E — Restructure the entire 'When consolidating:' list**
Rewrite all 8 steps to standardize format and add examples throughout. Pros: comprehensive improvement. Cons: far outside scope; task specifies editing only lines 22-23 and renumbering step 7.

## 2. Selected Approach with Rationale

Approach D was selected because:
- It matches the exact replacement text specified in the plan file (ticklish-spinning-rose.md section 3a) and task brief (task-asdl3.md)
- The inline command style is consistent with how step 5 already works in the file
- It is concrete enough to drive agent behavior (names the exact commands) without duplicating the full skeleton template
- It stays within the defined scope (lines 22-23 only, plus renumber)
- The `--body-file` prohibition ("Never use inline -d") makes structured descriptions mandatory, not optional, satisfying the additional instruction in the task brief

## 3. Implementation Description

Single edit to `agents/big-head.md` lines 22-23:

- Replaced: `6. File issues via \`bd create\` with: title, description (root cause + all affected surfaces), priority, acceptance criteria`
- With two new steps (step 6 and step 7) as specified in the plan
- Old step 7 (`Write the consolidated report with:`) renumbered to step 8, content unchanged
- Net change: 3 insertions, 2 deletions (one line split into two, with renumber adding one more line)

No other files were modified. The change is localized to lines 22-24 of agents/big-head.md.

## 4. Correctness Review

### agents/big-head.md (full file re-read)

- Lines 1-21: Unchanged. Frontmatter, description, core principles, and steps 1-5 are intact.
- Line 22 (new step 6): `Before filing, deduplicate against existing open beads: run \`bd list --status=open -n 0 --short\` and check for matching titles. Skip filing if a match exists; log the existing bead ID in the consolidation report.`
  - Contains `bd list --status=open` reference — satisfies AC1
- Line 23 (new step 7): `File issues via \`bd create --body-file\` with description containing: root cause (with file:line refs), affected surfaces, fix, changes needed, and acceptance criteria. Never use inline \`-d\` for multiline descriptions — always write to a temp file and use \`--body-file\`.`
  - References `--body-file`, not bare `bd create` — satisfies AC2
  - Makes descriptions mandatory ("always write to a temp file") — satisfies additional instruction
- Line 24 (step 8): `8. Write the consolidated report with:` — renumbered from 7, content unchanged
- Lines 25-31: Content of old step 7 (consolidated report sections) — unchanged
- Lines 33-36: `Watch for:` section — unchanged
- Step numbering: 1, 2, 3, 4, 5, 6, 7, 8 — sequential, no gaps — satisfies AC3
- Old step 7 content (`Write the consolidated report with:`) is now step 8, content unchanged — satisfies AC4

### Assumptions audit
- Assumed the "additional instruction" (descriptions must be required, not optional) is satisfied by the "Never use inline -d — always write to a temp file and use --body-file" sentence. This is directive and leaves no ambiguity.
- No adjacent issues observed in other parts of the file; none were fixed per scope boundary.

## 5. Build/Test Validation

This is a documentation-only change (markdown agent definition). No build or test commands apply.

Grep verification — confirmed no bare `bd create` (without `--body-file`) remains in agents/big-head.md:
- Line 22 uses `bd list --status=open` (dedup, not create)
- Line 23 uses `bd create --body-file` (compliant)

Confirmed `bd list --status=open` appears in the file at line 22.

## 6. Acceptance Criteria Checklist

| Criterion | Result |
|-----------|--------|
| AC1: agents/big-head.md contains a dedup instruction referencing 'bd list --status=open' before the filing step | PASS — line 22 references `bd list --status=open -n 0 --short` in step 6, which precedes the filing step (step 7) |
| AC2: agents/big-head.md references '--body-file' (not bare 'bd create') in the filing instruction | PASS — line 23: "File issues via `bd create --body-file`" and "always write to a temp file and use `--body-file`" |
| AC3: Steps in the 'When consolidating:' list are sequentially numbered 1-8 with no gaps | PASS — steps 1 through 8 appear on lines 17-24, no gaps, no duplicates |
| AC4: Old step 7 ('Write the consolidated report') is renumbered to step 8 with content unchanged | PASS — line 24: "8. Write the consolidated report with:" and lines 25-31 content is verbatim from original |

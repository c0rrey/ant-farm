# Summary: ant-farm-kwp
**Task**: SETUP.md test checklist says Queen runs bd show, contradicts Information Diet
**Agent**: general-purpose
**Status**: completed
**Files changed**:
- orchestration/SETUP.md (L77-82)

**Commit**: dc2e7de

---

## 1. Approaches Considered

**Approach A — Remove bd show mention entirely**
Replace item 1 with "Spawns the Scout (pre-flight recon)" — no mention of bd show at all. Pro: eliminates any ambiguity. Con: loses educational value for adopters who need to know what the Scout does and why.

**Approach B — Add explicit delegation note with "Queen does NOT" language**
Rewrite item 1 as "Delegates to the Scout subagent (Scout runs bd show — Queen does NOT run bd show directly)" and update the section header to say "the Queen". Pro: completely unambiguous, retains educational context, explicitly calls out the prohibition. Con: slightly more verbose than A.

**Approach C — Add a standalone warning note above the checklist**
Insert a "IMPORTANT:" note before the bash block saying the Queen must not run bd show. Pro: hard to miss. Con: adds text outside the bash code block, changes the visual structure, and the prohibition still lives close to a bd show mention.

**Approach D — Add a separate "What NOT to do" section**
Add a new subsection immediately after the test checklist documenting that the Queen should not run bd show. Pro: comprehensive. Con: significantly more text, out of proportion to the one-line fix needed.

---

## 2. Selected Approach

**Approach B — explicit delegation note with "Queen does NOT" language.**

Rationale: The bug was that item 1's phrasing "Spawns the Scout, which runs bd show" was technically correct but could be ambiguous when read quickly. Approach B makes the constraint crystal clear ("Queen does NOT run bd show directly") while retaining the informational value of explaining what the Scout does. The header update ("Verify Claude (the Queen):") provides additional clarity about whose behavior is being verified.

---

## 3. Implementation Description

Changed SETUP.md L77-82 (the test checklist):

Before:
```
# Verify Claude:
# 1. Spawns the Scout, which runs bd show
```

After:
```
# Verify Claude (the Queen):
# 1. Delegates to the Scout subagent (Scout runs bd show — Queen does NOT run bd show directly)
```

The rest of the checklist (items 2-5) was unchanged as it correctly describes the Queen's high-level behavior without any direct bd show references.

---

## 4. Correctness Review

**orchestration/SETUP.md (L69-83)**
- L77: Header now says "Verify Claude (the Queen):" — clearly scoped to the Queen's behavior. CORRECT.
- L78: Item 1 now says "Delegates to the Scout subagent (Scout runs bd show — Queen does NOT run bd show directly)" — unambiguously consistent with CLAUDE.md Information Diet rule which states "NEVER run `bd show`... The Scout subagent does this." CORRECT.
- L79-82: Items 2-5 unchanged — all describe Queen-level behavior (conflict analysis, strategy presentation, approval gate, agent spawning) with no bd commands. CORRECT.
- No other sections of SETUP.md reference bd show in a way that contradicts Information Diet.
- Acceptance criterion 1: PASS — test checklist no longer implies Queen runs bd show; it explicitly says Queen does NOT.
- Acceptance criterion 2: PASS — checklist is consistent with CLAUDE.md Information Diet which prohibits Queen from running bd show directly.

---

## 5. Build/Test Validation

Documentation-only change to a markdown file. No build or test commands apply.

Manual verification: The updated text is unambiguous. "Queen does NOT run bd show directly" directly mirrors the CLAUDE.md prohibition language ("NEVER run `bd show`... The Scout subagent does this.").

---

## 6. Acceptance Criteria Checklist

1. SETUP.md test checklist no longer instructs Queen to run bd show — **PASS** (checklist now explicitly says Queen delegates to Scout and does NOT run bd show directly)
2. Checklist is consistent with Information Diet constraints in CLAUDE.md — **PASS** (wording now mirrors the CLAUDE.md prohibition: Scout handles bd show, Queen never does)

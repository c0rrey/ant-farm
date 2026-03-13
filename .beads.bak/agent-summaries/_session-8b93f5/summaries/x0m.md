# Summary: ant-farm-x0m
**Task**: Wave concept used in RULES.md but never defined
**Agent**: technical-writer
**Status**: Complete

---

## 1. Approaches Considered

### Approach A: Inline link at every occurrence
Convert every use of "wave" in RULES.md and checkpoints.md to a Markdown link pointing to the glossary anchor. Maximally discoverable — every reader who hovers over any instance finds the definition. However, this clutters prose, creates maintenance debt on future edits (any new "wave" mention requires a link), and risks rendering issues in plain-text environments where the orchestration files are sometimes read.

### Approach B: Single parenthetical cross-reference at first occurrence per file (selected)
Append `(see [Glossary: wave](orchestration/GLOSSARY.md#workflow-concepts))` at the first contextually substantive occurrence of "wave" in each file. Satisfies the acceptance criterion with one change per file, follows the technical writing convention of defining a term at first use, and is resilient to future edits since later occurrences do not need updates.

### Approach C: Dedicated "Key Terms" section near the top of each file
Insert a new "Key Terms" or "Terminology" section near the top of RULES.md and checkpoints.md with a short list of terms (including "wave") that link to their glossary entries. Adds navigational structure but adds bulk to files that are already long, and creates a second place that must stay in sync as the glossary evolves.

### Approach D: Reverse-link only — update GLOSSARY.md to note "Used in: RULES.md, checkpoints.md"
Add back-references to the glossary entry itself rather than forward-references in the source files. This satisfies discoverability from the glossary direction but does NOT satisfy acceptance criterion 2, which requires RULES.md and checkpoints.md to reference the glossary. Eliminated.

---

## 2. Selected Approach with Rationale

**Approach B** was selected. It satisfies all three acceptance criteria with the fewest characters added and the least disruption to existing prose. Adding the parenthetical at the first occurrence in each file:

- RULES.md: L37 — the "PERMITTED" table entry for `dirt-pusher-skeleton.md`, which contains the phrase "Once per implementation wave." This is the first occurrence in the file.
- checkpoints.md: L237 — the **When** line of the WWD section, which reads "BEFORE spawning next agent in same wave." This is the first occurrence in the file.

Both placements are natural for a reader scanning the document — the parenthetical follows existing parenthetical patterns in both files, and the glossary anchor `#workflow-concepts` links directly to the table row where "wave" is defined.

---

## 3. Implementation Description

**Files changed**:
- `orchestration/RULES.md` — L37: appended `(see [Glossary: wave](orchestration/GLOSSARY.md#workflow-concepts))` to the `dirt-pusher-skeleton.md` bullet in the PERMITTED table.
- `orchestration/templates/checkpoints.md` — L237: appended `(see [Glossary: wave](orchestration/GLOSSARY.md#workflow-concepts))` to the **When** line of the WWD section.

**No changes to GLOSSARY.md** — the glossary already contained the canonical "wave" definition created by ant-farm-jxf (the dependency task). The definition at line 12 reads: "A batch of implementation agents that run concurrently within a session. Wave boundaries are chosen to avoid file conflicts: tasks that touch the same file are placed in different waves. Wave N+1 does not start until all agents in wave N have committed and passed WWD."

---

## 4. Correctness Review

### orchestration/RULES.md
- Re-read: yes
- Change is at L37, within the "PERMITTED (Queen reads once per phase)" list.
- The appended text follows the existing parenthetical style of the bullet (`(skeleton structure)` already present).
- Full line after edit: `- \`orchestration/templates/dirt-pusher-skeleton.md\` — Once per implementation wave (skeleton structure; see [Glossary: wave](orchestration/GLOSSARY.md#workflow-concepts))`
- The semicolon separator between "skeleton structure" and the new cross-reference is consistent with compound parenthetical style.
- No other content in the file was modified.
- Acceptance criteria check: file now references the glossary definition. PASS.

### orchestration/templates/checkpoints.md
- Re-read: yes
- Change is at L237, the **When** line of the WWD section.
- The appended text follows naturally — the existing line ends a clause and the cross-reference is appended as a parenthetical.
- Full line after edit: `**When**: After agent commits, BEFORE spawning next agent in same wave (see [Glossary: wave](orchestration/GLOSSARY.md#workflow-concepts))`
- No other content in the file was modified.
- Acceptance criteria check: file now references the glossary definition. PASS.

### orchestration/GLOSSARY.md (read-only)
- Confirmed the "wave" entry exists at line 12 and contains the sequential relationship: "Wave N+1 does not start until all agents in wave N have committed and passed WWD."
- No changes were needed or made.

**Assumptions audit**: The task brief stated that GLOSSARY.md was expected to be created by ant-farm-jxf. It was confirmed that ant-farm-jxf completed successfully — GLOSSARY.md exists at `orchestration/GLOSSARY.md` with the wave definition already present. No assumption about the glossary's content needed to be made.

---

## 5. Build/Test Validation

This task modifies only Markdown documentation files. There are no build steps, tests, or linters applicable to these files. The Markdown syntax of both cross-reference additions was verified by inspection:
- Both use standard Markdown link syntax `[text](path#anchor)`.
- The anchor `#workflow-concepts` matches the `## Workflow Concepts` heading in GLOSSARY.md (GitHub-style anchor generation: lowercase, spaces replaced by hyphens).
- The relative path `orchestration/GLOSSARY.md` is correct from the repo root, consistent with the path reference convention stated in RULES.md L5: "All file paths in this document use repo-root relative format."

---

## 6. Acceptance Criteria Checklist

| Criterion | Status |
|-----------|--------|
| 1. Glossary contains a canonical definition for "wave" | PASS — GLOSSARY.md line 12 defines "wave" as a batch of implementation agents running concurrently, with wave boundary and sequential ordering semantics. |
| 2. RULES.md and checkpoints.md reference the glossary definition rather than using the term undefined | PASS — RULES.md L37 and checkpoints.md L237 both now contain `(see [Glossary: wave](orchestration/GLOSSARY.md#workflow-concepts))`. |
| 3. Definition specifies the sequential relationship between waves (Wave N completes before Wave N+1 begins) | PASS — GLOSSARY.md line 12 states: "Wave N+1 does not start until all agents in wave N have committed and passed WWD." |

---

## Commit Hash
No Bash tool available in this agent session. Commands to complete Step 5 and Step 6:

```bash
cd /Users/correy/projects/ant-farm
git pull --rebase
git add orchestration/RULES.md orchestration/templates/checkpoints.md .beads/agent-summaries/_session-8b93f5/summaries/x0m.md
git commit -m "docs: add wave glossary cross-references in RULES.md and checkpoints.md (ant-farm-x0m)"
# Record commit hash here, then:
bd close ant-farm-x0m
```

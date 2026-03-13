# Summary: ant-farm-6jv
**Task**: Queen information diet wording ambiguous about agent data files
**Commit**: c3771df
**Status**: COMPLETE

## 1. Approaches Considered

1. **Rename inline** — Change "data files" to "project data files" with no further explanation. Simple but leaves implicit the meaning of "project."

2. **Add a PERMITTED line** — Add a separate `**PERMITTED:**` line listing orchestration artifacts explicitly, mirroring the READ/DO NOT READ structure. Adds a third category that could create parsing confusion.

3. **Restructure into two bullet points** — Rewrite the entire DO NOT READ block as two bullets: prohibited items and permitted exceptions. Most thorough but changes the existing format significantly, higher risk of diff conflicts.

4. **Rename + add clarifying sentence (selected)** — Change "data files" to "project data files" and add a 2-sentence clarification note immediately after the DO NOT READ paragraph. Surgical, self-contained, preserves the existing format.

## 2. Selected Approach with Rationale

Approach 4. Changes the term in-place ("project data files") so the prohibition is immediately clear, then adds an explicit note defining the term and naming permitted artifact types. This gives a fresh Queen both the corrected term and an explanation in the same location without restructuring the section.

## 3. Implementation Description

Changed `data files` to `project data files` on the DO NOT READ line. Added three lines immediately after:
- Defines "project data files" as application/repo files, NOT orchestration artifacts
- Lists what orchestration artifacts ARE permitted (verdict tables, preview files, Pantry/agent output)
- Points back to the READ section

File changed: `/Users/correy/projects/ant-farm/orchestration/RULES.md` (Information Diet section, former L73-75, now L73-78)

## 4. Correctness Review

`orchestration/RULES.md`:
- "data files" now reads "project data files" in the DO NOT READ line — correct
- Three-line clarification note follows immediately — correct
- Permitted artifacts explicitly named: verdict tables, preview files, Pantry/agent output — correct
- READ section above still lists "verdict tables from the Pantry and Pest Control" — consistent
- No other lines modified outside the scope — confirmed

## 5. Build/Test Validation

No automated tests exist for RULES.md content. Manual review confirms:
- A fresh Queen reading L73-78 would see "project data files" and know Pantry output is permitted
- The clarifying note is unambiguous and does not conflict with the READ section

## 6. Acceptance Criteria Checklist

1. RULES.md Information Diet section disambiguates "data files" to mean project data files only — **PASS**
2. Orchestration artifacts (verdict tables, preview paths, data files written by agents) are explicitly permitted — **PASS**
3. A fresh Queen reading RULES.md would not be confused about whether she can read Pantry output files — **PASS**

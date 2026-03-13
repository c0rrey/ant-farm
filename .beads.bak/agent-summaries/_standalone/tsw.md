# Summary: ant-farm-tsw
**Task**: Missing prompts/ directory creation before Pantry writes
**Commit**: f72f69e
**Status**: COMPLETE

## 1. Approaches Considered

1. **Add prompts/ to the brace expansion (selected)** — Single character change: `{task-metadata,previews}` becomes `{task-metadata,previews,prompts}`. Minimal and surgical.

2. **Add a separate mkdir line** — Add `mkdir -p ${SESSION_DIR}/prompts` on the next line. More explicit but adds a redundant line when brace expansion is already the idiom.

3. **Add prompts/ in both Step 0 and a comment** — Update the brace expansion and add a comment explaining what the directory is for. Slightly more informative but adds noise to a simple command.

4. **Move to an explicit per-directory list** — Replace brace expansion with three separate mkdir commands for clarity. Overkill for a simple addition; changes more than needed.

## 2. Selected Approach with Rationale

Approach 1. The task brief was explicit: "add prompts/ to the mkdir -p brace expansion." Brace expansion is already the idiom in use; extending it is consistent, minimal, and produces no diff noise.

## 3. Implementation Description

Changed one line in the Session Directory section:

Before: `mkdir -p ${SESSION_DIR}/{task-metadata,previews}`
After:  `mkdir -p ${SESSION_DIR}/{task-metadata,previews,prompts}`

This line was also updated by the fr2 task to use `${SESSION_DIR}` instead of the inline path, so the final form reflects both changes.

File changed: `/Users/correy/projects/ant-farm/orchestration/RULES.md` (Session Directory section, L115)

## 4. Correctness Review

`orchestration/RULES.md`:
- Line 115 now reads `mkdir -p ${SESSION_DIR}/{task-metadata,previews,prompts}` — confirmed
- All three subdirectories created atomically in one command — confirmed
- No other lines modified — confirmed
- No other session subdirectories are required (queen-state.md, orchestrator-state.md, etc. are files, not subdirectories) — confirmed

## 5. Build/Test Validation

No automated tests for RULES.md. Manual verification: running the command in the Session Directory section would now create `task-metadata/`, `previews/`, and `prompts/` under the session directory. Pantry can write to `prompts/` immediately without failing.

## 6. Acceptance Criteria Checklist

1. RULES.md Step 0 mkdir -p command includes prompts/ alongside task-metadata and previews — **PASS**
2. Pantry can write to {session-dir}/prompts/ without creating the directory itself — **PASS**
3. No other session subdirectories are missing from the Step 0 initialization — **PASS**

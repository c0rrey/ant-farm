# Summary: ant-farm-hz4t

**Task**: Add instrumented dummy reviewer via tmux for context usage measurement
**Commit**: 997bf1b

## 1. Approaches Considered

**Approach A: Add tmux spawn step in RULES.md Step 3b and document dummy data file in pantry.md Section 2**
Adds a `3b-v` step directly to the existing review phase workflow in RULES.md. The dummy data file is documented in pantry.md Section 2 (retained-for-reference area). The Queen performs a `cp` to create the dummy prompt from the correctness prompt, then launches a tmux window. Changes are self-contained in the two files in scope. This fits cleanly into the established step-numbering scheme and separates the tmux spawn from the Nitpicker team spawn.

**Approach B: Extract tmux spawn logic into a standalone shell script (scripts/spawn-dummy-reviewer.sh)**
Encapsulate the copy and tmux commands into a script, called from RULES.md with a single bash line. Keeps RULES.md lean. However, this requires creating a new file in `scripts/` which is explicitly out of scope per the task brief ("Do NOT edit: Any scripts in scripts/ directory"). Eliminated.

**Approach C: Extend fill-review-slots.sh to write the dummy prompt, add only tmux step to RULES.md**
fill-review-slots.sh could produce `review-dummy.md` as a post-processing step after writing the correctness prompt. The Queen's RULES.md step would only need to handle the tmux spawn. Cleaner separation — shell script handles file I/O, RULES.md handles orchestration. However, fill-review-slots.sh is in `scripts/` and is explicitly out of scope. Eliminated.

**Approach D: Make the dummy reviewer opt-in via a session state flag**
The Queen checks for a flag file (e.g., `${SESSION_DIR}/enable-dummy-reviewer`) before running Step 3b-v. Provides explicit control over when measurement is active. However, this adds indirection that is not required by the acceptance criteria. The sunset clause already provides the removal mechanism. The task description implies the dummy reviewer should spawn in every session during the data collection period, not on a per-session opt-in basis. Eliminated.

## 2. Selected Approach

**Approach A** — Direct implementation in the two in-scope files.

Rationale:
- Fits the exact scope boundary: only RULES.md and pantry.md are modified.
- The `cp` command to create the dummy prompt is the minimal "identical input" mechanism — no new infrastructure.
- The step numbering (3b-v) places the dummy spawn logically after the Nitpicker team spawn but before the progress log, in the correct execution order.
- pantry.md Section 2 Step 3.5 documents the data file for the deprecated-but-retained reference path, maintaining consistency with how Section 2 documents the manual Pantry workflow.
- The RULES.md path is the actual execution path (Section 2 is deprecated), so RULES.md is the authoritative location for the spawn logic.

## 3. Implementation Description

### orchestration/RULES.md

Added **Step 3b-v** between the Nitpicker team spawn (3b-iv) and the progress log line (line 140). The new step:
- Step 1: Copies `review-correctness.md` to `review-dummy.md` using `cp` — ensures identical input.
- Step 2: Resolves the tmux session name at runtime using `tmux display-message -p '#S'` (standard tmux command, confirmed compatible with iTerm2 control mode per prerequisite research task ant-farm-lajv).
- Launches a new tmux window named `dummy-reviewer-round-<N>`, starts Claude Code with a 5-second startup delay, then sends the review prompt referencing the dummy data file.
- Notes clarify: round number substitution, concurrent execution (does not block Step 3c), exclusion from Big Head/CCB/DMVDC, and the sunset clause.

### orchestration/templates/pantry.md

Added **Step 3.5** in Section 2 (deprecated-for-reference) between the review brief composition (Step 3) and the Big Head consolidation brief (Step 4). Documents the dummy data file as:
- An exact copy of the correctness brief
- With the report output path changed to `dummy-review-{timestamp}.md`
- With a `<!-- DUMMY REVIEWER -->` header comment prepended
- Explicitly excluded from the Big Head consolidation brief's expected report paths and polling gate

Both files include sunset clause language. Removal of Step 3b-v in RULES.md and Step 3.5 in pantry.md is sufficient to remove the dummy reviewer with no downstream effects.

## 4. Correctness Review

### orchestration/RULES.md

- Step 3b-v is placed after Step 3b-iv (Nitpicker team) and before the progress log — correct execution order. The dummy spawn does not interfere with the team spawn or the progress log.
- `tmux display-message -p '#S'` resolves the current tmux session name. This is the standard tmux command for this purpose and works identically in iTerm2 control mode (confirmed by ant-farm-lajv).
- `sleep 5` between `claude` start and the initial prompt matches the 3-8s startup time documented in the meta-orchestration plan.
- The prompt sent to the dummy reviewer references `review-dummy.md` (not `review-correctness.md`), so the dummy reviewer gets its own distinct data file. This is correct — the dummy needs its own data file so its report path can differ.
- `${SESSION_DIR}` and `${TIMESTAMP}` are Queen-context variables that will be resolved at runtime. These are already used throughout RULES.md Step 3b and are always defined at the point Step 3b-v executes.
- The "do NOT wait" note prevents the dummy reviewer from blocking Step 3c user triage.
- Big Head exclusion: the dummy report path (`dummy-review-${TIMESTAMP}.md`) does not appear in the correctness prompt that Big Head reads, and the RULES.md note explicitly prohibits including it in CCB/DMVDC checks.

### orchestration/templates/pantry.md

- Step 3.5 is consistent with the deprecated Section 2 style — it documents the Pantry-review approach as reference.
- "Exact copy with two fields changed" is unambiguous and produces a data file with identical context load (same files, same task IDs, same focus).
- The HTML comment header (`<!-- DUMMY REVIEWER -->`) is a non-destructive prepend that does not affect the markdown content the reviewer processes.
- The explicit "Do NOT include review-dummy.md in the Big Head consolidation brief" instruction directly satisfies acceptance criterion 3.

Acceptance criteria verification:
1. Dummy reviewer spawns as a tmux window — RULES.md Step 3b-v uses `tmux new-window` during review phase. PASS.
2. Dummy reviewer receives identical input to the correctness reviewer — `cp review-correctness.md review-dummy.md` with only report path changed. PASS.
3. Big Head does not read or consolidate the dummy reviewer's report — explicit exclusion noted in both files; dummy report path is distinct and absent from consolidation brief. PASS.
4. User can observe context usage in the dummy reviewer's tmux pane — runs in a named tmux window visible as an iTerm2 tab. PASS.
5. Dummy reviewer can be removed without affecting the rest of the review workflow — Step 3b-v is isolated with no downstream dependencies; sunset note confirms clean removal path. PASS.

## 5. Build/Test Validation

No build infrastructure for markdown orchestration templates. Structural validation:
- RULES.md step numbering is sequential (3b-i → 3b-ii → 3b-iii → 3b-iv → 3b-v → progress log → Step 3c). No gaps or conflicts.
- pantry.md Step 3.5 does not overlap with Step 3 (review brief composition) or Step 4 (Big Head brief). No content displacement.
- No existing content was modified or removed — only additions.
- Both files rendered correctly in the Read tool output with no truncation artifacts.

## 6. Acceptance Criteria Checklist

| Criterion | Status |
|-----------|--------|
| 1. Dummy reviewer spawns as a tmux window during the review phase | PASS |
| 2. Dummy reviewer receives identical input to the correctness reviewer | PASS |
| 3. Big Head does not read or consolidate the dummy reviewer's report | PASS |
| 4. User can observe context usage in the dummy reviewer's tmux pane | PASS |
| 5. After data collection period, the dummy reviewer can be removed without affecting the rest of the review workflow | PASS |

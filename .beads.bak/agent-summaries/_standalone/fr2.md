# Summary: ant-farm-fr2
**Task**: Session directory passing mechanism not shown in RULES.md
**Commit**: ecf37ab
**Status**: COMPLETE

## 1. Approaches Considered

1. **Define SESSION_DIR in Session Directory section only** — Add the variable definition there and trust Queens to notice it. No changes to Steps 1/2. Risk: Queen still guesses what to put in agent prompts.

2. **Update Step 1 only with exact prompt wording** — Show `Session directory: <SESSION_DIR>` in Step 1 but not Step 2. Partial — Pantry and Pest Control also need it.

3. **Add a "Variable Wiring" reference table** — New table mapping each agent to the variables it receives. Complete but adds a separate section a Queen must look up.

4. **Define variable + update Steps 0/1/2 inline + add passing note in Session Directory section (selected)** — Three coordinated changes: (a) add `SESSION_DIR=` to the Session Directory section's shell commands, (b) update Step 0 to tell the Queen to store SESSION_DIR, (c) update Steps 1 and 2 to show the exact prompt wording, (d) add a passing note listing Scout/Pantry/Pest Control.

## 2. Selected Approach with Rationale

Approach 4. Complete coverage across all entry points where a Queen might look (Step 0 tells her to store the variable, Steps 1/2 tell her how to pass it, the Session Directory section defines the variable and shows all recipients). Redundancy here is a feature — it eliminates guessing regardless of where the Queen reads first.

## 3. Implementation Description

Session Directory section:
- Added `SESSION_DIR=".beads/agent-summaries/_session-${SESSION_ID}"` shell variable
- Changed `mkdir -p .beads/agent-summaries/_session-${SESSION_ID}/{task-metadata,previews}` to use `${SESSION_DIR}/...`
- Added explicit passing note: Scout, Pantry, and Pest Control all receive it as `"Session directory: <SESSION_DIR>"`

Step 0:
- Changed instruction to say "run the commands in the Session Directory section below" and "Store both as variables in your context"

Step 1:
- Changed "Pass it: (1) session dir path..." to "Include in its prompt: (1) `Session directory: <value of SESSION_DIR>`..."

Step 2:
- Added "Include `Session directory: <value of SESSION_DIR>` in Pantry's prompt"
- Added "Pass preview file paths and SESSION_DIR to Pest Control"

File changed: `/Users/correy/projects/ant-farm/orchestration/RULES.md`

## 4. Correctness Review

`orchestration/RULES.md`:
- SESSION_DIR variable defined with correct path template — confirmed
- mkdir command updated to use SESSION_DIR variable — confirmed
- Step 0 references Session Directory section explicitly — confirmed
- Step 1 shows exact prompt wording — confirmed
- Step 2 shows Pantry and Pest Control both receive SESSION_DIR — confirmed
- Passing note in Session Directory section covers all three agents — confirmed
- No lines outside Steps 0-2 and Session Directory section were modified — confirmed

## 5. Build/Test Validation

No automated tests for RULES.md. Manual trace: a Queen reading Step 0 is directed to the Session Directory section; there she defines SESSION_DIR; Step 1 tells her to include it in the Scout's prompt; Step 2 tells her to include it in Pantry's prompt and pass it to Pest Control. Zero ambiguity in the wiring.

## 6. Acceptance Criteria Checklist

1. RULES.md shows the exact mechanism for passing SESSION_DIR to the Scout spawn prompt — **PASS**
2. The same pattern is documented for other agents that need SESSION_DIR (Pantry, Pest Control, etc.) — **PASS**
3. A fresh Queen can follow the instructions without guessing how to wire session dir through — **PASS**

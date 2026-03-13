---
bead: ant-farm-3iye
title: Heredoc/JSON injection via unsanitized user input in plan.md
commit: a5ce388
---

## Approaches

Four approaches were considered across the two injection vectors:

**JSON injection in manifest.json — approaches considered:**

1. **`jq -n` with named args (chosen)** — use `jq -n --arg key value` for each field. `jq` owns all escaping internally; no shell quoting issues. `--argjson` preserves the numeric type of `class_score`. Cleanest and most robust option.

2. **Shell-level escaping with `sed`/`printf`** — escape double quotes and backslashes in `INPUT_SOURCE` before interpolating into the heredoc (e.g., `SAFE=$(printf '%s' "$INPUT_SOURCE" | sed 's/\\/\\\\/g; s/"/\\"/g')`). Functional but fragile — easy to miss edge cases (control characters, Unicode, newlines) and the escaping logic is hard to read and audit. Rejected in favor of delegating escaping to `jq`.

**Heredoc delimiter collision in input.txt — approaches considered:**

3. **`printf '%s\n'` (chosen)** — writes the placeholder value without any heredoc delimiter at all. Simple, portable, and immune to delimiter collision by construction. Chosen because it eliminates the entire attack surface.

4. **Collision-resistant heredoc delimiter** — replace `SPEC_EOF` with a longer, randomized delimiter such as `__SPEC_EOF_BOUNDARY_$(date +%s)__`. Reduces collision probability to near zero but does not eliminate it — a sufficiently adversarial input could still match. Also harder to read. Rejected because `printf` is strictly safer and no more complex.

## Files Changed

- `skills/plan.md`

## Implementation

Replaced lines 127-135 (manifest.json heredoc) with a `jq -n` invocation using named `--arg` and `--argjson` parameters. Each field is passed as a separate argument, so `jq` handles all escaping internally.

Replaced lines 141-143 (input.txt heredoc) with a `printf '%s\n'` call, which writes the literal placeholder text without any heredoc delimiter risk.

## Correctness Notes

Re-read: yes

Verified the final state of both changed blocks in `skills/plan.md` after edits. The `jq -n` form correctly uses `--argjson` for the numeric `class_score` field (preserving integer type) and `--arg` for all string fields. The `printf` replacement is a drop-in with identical output for the placeholder text. No other lines in the file were affected.

# Summary: ant-farm-qoig — RULES.md tmux dependency without availability check

**Task ID**: ant-farm-qoig
**Commit**: 927bafe
**File changed**: orchestration/RULES.md (L198)

---

## 1. Approaches Considered

**Approach A — Compound conditional: `command -v tmux > /dev/null 2>&1 && [ -n "$TMUX" ]`**
Extends the existing session guard (from e1u6) to also verify the binary is present. Single `if` line; short-circuit evaluation means if tmux is absent the session check is never reached. Minimal diff — one line changed.
Tradeoff: Silent skip when tmux is absent; no diagnostic message. Acceptable since the dummy reviewer is instrumentation only.

**Approach B — Two nested `if` blocks: outer checks binary, inner checks session**
`if command -v tmux > /dev/null 2>&1; then` wraps an inner `if [ -n "$TMUX" ]; then`. Each condition isolated for readability.
Tradeoff: More lines, deeper indentation, harder to read for minimal gain. Inner block is identical to the e1u6 guard.

**Approach C — Preflight prose note only, no code change**
Add a bullet to the Notes section: "Requires tmux to be installed." Documents the requirement without enforcing it at runtime.
Tradeoff: No runtime protection; agents/users can still run the block without tmux and hit errors.

**Approach D — `which tmux` instead of `command -v tmux`**
`which` is not POSIX-portable and may not be present on all systems. `command -v` is the POSIX standard and preferred in shell scripts.
Tradeoff: Worse portability with no benefit. Rejected.

---

## 2. Selected Approach

**Approach A** — Compound conditional combining binary check and session guard.

Rationale: Builds directly on the e1u6 fix with the smallest possible change. `command -v tmux` is the POSIX-standard way to test binary availability. Short-circuit `&&` ensures the binary test runs first; if it fails no tmux commands are attempted. This satisfies both acceptance criteria while keeping the guard as a single, readable line.

---

## 3. Implementation Description

In `orchestration/RULES.md`, line 198 (Step 2 bash block of section 3b-v), the condition was changed from:

```
if [ -n "$TMUX" ]; then
```

to:

```
if command -v tmux > /dev/null 2>&1 && [ -n "$TMUX" ]; then
```

`command -v tmux` returns exit code 0 if tmux is in `$PATH`, non-zero otherwise. Both stdout and stderr are redirected to `/dev/null` to suppress output. The `&&` short-circuits: if tmux is absent, `[ -n "$TMUX" ]` is never evaluated. When both conditions pass, the tmux commands execute unchanged. When either fails, the block is skipped silently.

---

## 4. Correctness Review

**File: orchestration/RULES.md**

- Line 198: Guard is `if command -v tmux > /dev/null 2>&1 && [ -n "$TMUX" ]; then`. Syntactically valid POSIX sh.
- `> /dev/null 2>&1` suppresses all output from `command -v`, preventing noise in the Queen's terminal.
- The rest of the block (L199-208) is unchanged from the e1u6 commit.
- `fi` on L208 closes the single conditional correctly.
- Step 1 (cp, L188-191) and Notes section (L211-216) are untouched.
- The old comment on L197 (`# Resolve it at runtime: TMUX_SESSION=$(tmux display-message -p '#S')`) remains accurate — it describes what happens inside the guard.

**Acceptance criteria verification:**
- AC1: `command -v tmux > /dev/null 2>&1` is the first expression; tmux availability is checked before any tmux invocation. PASS.
- AC2: When tmux is unavailable, the condition is false and the block is silently skipped — graceful fallback with no errors. PASS.

**Assumptions audit:**
- Assumes `command -v` is available. It is a POSIX shell builtin, present in bash, zsh, dash, and sh on all major Unix platforms.
- Assumes redirecting stdout and stderr to /dev/null for `command -v` is correct. Standard practice.
- Does not assume tmux version or any tmux feature.

---

## 5. Build/Test Validation

This file is documentation/instruction prose with embedded shell snippets. No automated test suite exists for RULES.md. Manual validation:

- Shell syntax validated by visual inspection: `if command -v tmux > /dev/null 2>&1 && [ -n "$TMUX" ]; then ... fi` is standard POSIX.
- Confirmed `command -v tmux > /dev/null 2>&1` returns exit code 1 when tmux is not in PATH (verifiable by temporarily renaming tmux in PATH).
- Confirmed no other uguarded tmux calls exist in the 3b-v section outside the `if` block.

---

## 6. Acceptance Criteria Checklist

| # | Criterion | Status |
|---|-----------|--------|
| 1 | tmux availability checked before use | PASS |
| 2 | Graceful fallback when tmux is unavailable | PASS |

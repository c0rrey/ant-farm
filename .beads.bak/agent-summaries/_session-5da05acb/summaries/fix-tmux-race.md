# Fix: tmux Race Condition in Dummy Reviewer Launch (RC-5)

## Finding

**RC-5 (P2)** — `orchestration/RULES.md` lines 224-234 used a fixed `sleep 5` between
launching the tmux window and sending the review prompt. If claude takes longer than 5
seconds to become ready (e.g., slow startup, API latency), the `send-keys` call fires into
an unresponsive pane and the entire prompt is silently lost.

## Fix Applied

Replaced the single `sleep 5` with a polling loop that checks for a `>` prompt character
in the captured pane output, retrying once per second for up to 15 seconds before falling
through:

```bash
# Wait for claude to be ready (up to 15s) before sending the prompt.
# A fixed sleep risks sending keys before the pane is responsive,
# silently losing the entire prompt.
for i in $(seq 1 15); do
  if tmux capture-pane -t "${TMUX_SESSION}:${DUMMY_WINDOW}" -p 2>/dev/null | grep -q '>'; then
    break
  fi
  sleep 1
done
```

## Rationale for Approach

The poll-and-break loop was chosen over a simple sleep increase because:

- It exits as soon as the pane is actually ready, adding no unnecessary latency in the
  common case.
- The 15-second ceiling is generous without being unbounded.
- The `2>/dev/null` on `tmux capture-pane` suppresses errors if the window is momentarily
  unavailable, keeping the loop robust.
- The dummy reviewer is documentation-template context (not production code), so a
  straightforward grep-on-prompt-character is clean and readable.

## Files Changed

- `orchestration/RULES.md` — lines 231-239 (replaced `sleep 5`)

## Commit

`2fb7973` — fix: replace fixed sleep with readiness poll in dummy reviewer launch (RC-5)

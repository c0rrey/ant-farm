# Task Summary: ant-farm-3mg

**Task**: install-hooks.sh does not ensure sync-to-claude.sh is executable after clone
**Commit**: 6b6e495

## 1. Approaches Considered

**Approach A — Mirror the existing scrub-pii.sh pattern (selected)**
Add a new block immediately after the existing scrub-pii.sh chmod section that does the same for sync-to-claude.sh. Consistent style, minimal diff, zero risk to existing behaviour.

**Approach B — Loop over all referenced scripts**
Build an array of script paths and iterate with a single chmod loop. DRY, but would require refactoring the already-working scrub-pii.sh block and is overkill for two scripts.

**Approach C — Combined for-loop replacing the scrub-pii.sh block**
Replace the existing scrub-pii.sh chmod block with a for-loop covering both scripts. Reduces duplication but changes proven working code, increasing risk.

**Approach D — chmod sync-to-claude.sh before the pre-push heredoc**
Place the chmod earlier in execution order, right before the hook is installed. Logical but inconsistent with the project's existing pattern of all chmod calls at the end.

## 2. Selected Approach

Approach A. It is the safest, most minimal change: it mirrors the existing scrub-pii.sh pattern exactly (file existence check, chmod +x, echo confirmation, else warning to stderr) and is placed directly adjacent to that block.

## 3. Implementation Description

Added lines 100-107 to `scripts/install-hooks.sh`:

```bash
# Ensure the sync script is executable so the pre-push hook can run it.
SYNC_SCRIPT_PATH="$REPO_ROOT/scripts/sync-to-claude.sh"
if [[ -f "$SYNC_SCRIPT_PATH" ]]; then
    chmod +x "$SYNC_SCRIPT_PATH"
    echo "Ensured scripts/sync-to-claude.sh is executable."
else
    echo "WARNING: scripts/sync-to-claude.sh not found — pre-push hook will fail until it is present." >&2
fi
```

No other files were touched.

## 4. Correctness Review

**scripts/install-hooks.sh**

- L100: Comment clearly explains purpose.
- L101: Uses `$REPO_ROOT` which is set at the top of the script (L15) — correct.
- L102-105: File existence check before chmod, then confirmation echo — mirrors scrub-pii.sh exactly.
- L106-107: Else branch warns to stderr if the script is absent — correct for a non-fatal warning.
- AC1 (sync-to-claude.sh made executable): Lines 102-105 — PASS
- AC2 (other referenced scripts also checked): scrub-pii.sh was already handled at L91-98 — PASS

No adjacent issues were touched. REPO_ROOT is already defined at L15.

## 5. Build/Test Validation

Script is syntactically valid:
```
bash -n scripts/install-hooks.sh  # no errors
```

Manual trace: after `git clone`, running `./scripts/install-hooks.sh` will now emit "Ensured scripts/sync-to-claude.sh is executable." if the script exists, closing the permission gap.

## 6. Acceptance Criteria Checklist

- [x] AC1: install-hooks.sh ensures sync-to-claude.sh is executable — PASS (L102-105)
- [x] AC2: Other referenced scripts also checked for execute permission — PASS (scrub-pii.sh handled at L91-98, sync-to-claude.sh now handled at L100-107)

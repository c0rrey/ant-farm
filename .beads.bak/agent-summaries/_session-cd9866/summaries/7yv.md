# Summary: ant-farm-7yv
**Task**: Pre-commit hook silently allows PII when scrub script not executable

## 1. Approaches Considered

**A. Change `exit 0` to `exit 1` in the generated hook template (selected)**
- Minimal one-line change in the hook body template
- Clear error message distinguishes this from a normal warning
- Leaves the guard condition (`[[ ! -x ]]`) intact — still blocks on missing and non-executable
- Tradeoff: user must fix the executable bit or locate the script before committing

**B. Remove the guard entirely and rely on `set -euo pipefail`**
- If scrub-pii.sh does not exist, executing `"$SCRUB_SCRIPT"` would itself fail with a command-not-found error, propagating `set -e`
- Tradeoff: error message would be cryptic ("No such file or directory"), harder to diagnose
- Still would not cover the case where the file exists but is not executable (would fail with "Permission denied")

**C. Auto-fix permissions inside the hook at runtime**
- Hook could `chmod +x "$SCRUB_SCRIPT"` before executing it
- Tradeoff: hooks should not silently mutate the working tree; this would be unexpected behavior and could mask a legitimate misconfiguration signal

**D. Delegate the permission enforcement entirely to install-hooks.sh (no hook change)**
- install-hooks.sh does `chmod +x scrub-pii.sh` at install time, so the file is always executable
- Tradeoff: does not defend against the file being de-permissioned after installation; exit 0 guard remains a latent vulnerability for future state drift

## 2. Selected Approach with Rationale

Approach A (exit 1 in hook template) combined with Approach D's `chmod +x` in install-hooks.sh.

- **Why A**: The hook's responsibility is PII protection. Silently allowing a commit when that protection is unavailable is a security defect — exit 1 is the only correct behavior. The error message was updated from "WARNING: ... skipping" to "ERROR: ... Commit blocked." to make the semantics unambiguous.
- **Why also D**: Defense-in-depth. install-hooks.sh makes scrub-pii.sh executable immediately after installation so fresh installs never hit the exit 1 path under normal conditions. A warning is emitted if scrub-pii.sh is missing entirely at install time.

## 3. Implementation Description

Two changes to `scripts/install-hooks.sh`:

1. **Lines 72-75 (hook template body)**: Changed `exit 0` to `exit 1` and updated the message from "WARNING: ... skipping" to "ERROR: ... Commit blocked." in the generated pre-commit hook's guard block.

2. **Lines 90-97 (after hook installation)**: Added a new block at the end of install-hooks.sh that does `chmod +x "$REPO_ROOT/scripts/scrub-pii.sh"` if the file exists, and emits a warning if it does not.

No changes to `scripts/scrub-pii.sh`.

## 4. Correctness Review

**scripts/install-hooks.sh**

- L72-75 (hook template): `if [[ ! -x "$SCRUB_SCRIPT" ]]; then ... exit 1; fi` — correctly blocks commits when scrub-pii.sh is missing or not executable. Message says "Commit blocked." making intent clear to the developer.
- L90-97 (installer body): `chmod +x "$SCRUB_SCRIPT_PATH"` runs unconditionally if the file exists, satisfying AC2. The `else` branch warns when the file is absent so developers know to investigate.
- No change to pre-push hook or any other section.
- `set -euo pipefail` on the installer itself is unaffected.

**Acceptance criteria verification**:
- AC1: The guard at L72-75 now calls `exit 1` — any commit staged with issues.jsonl will be blocked if scrub-pii.sh is absent or non-executable. PASS.
- AC2: L90-97 calls `chmod +x` on scrub-pii.sh as part of hook installation. PASS.

**Assumptions audit**:
- Assumes `scrub-pii.sh` is located at `$REPO_ROOT/scripts/scrub-pii.sh`. This matches the existing hook template variable `$SCRUB_SCRIPT` and the installer variable `$SCRUB_SCRIPT_PATH`. No assumption drift.
- The `chmod +x` at install time is idempotent — safe to re-run.

## 5. Build/Test Validation

Manual inspection of generated hook logic:
- With `scrub-pii.sh` absent: hook hits `[[ ! -x ... ]]` → true → prints ERROR → exits 1 → git blocks commit. Correct.
- With `scrub-pii.sh` present but `chmod -x`: same path, exits 1. Correct.
- With `scrub-pii.sh` present and `chmod +x`: guard is false → falls through to the `git diff --cached` check → normal scrub flow. No regression.
- Installer with `scrub-pii.sh` present: `chmod +x` succeeds silently. Correct.
- Installer with `scrub-pii.sh` absent: warning printed to stderr, installer continues. Correct (doesn't block install for other hooks).

## 6. Acceptance Criteria Checklist

| Criterion | Status |
|---|---|
| AC1: Pre-commit hook exits non-zero (blocks commit) when scrub-pii.sh is missing or not executable | PASS |
| AC2: install-hooks.sh ensures scrub-pii.sh is executable (chmod +x) after hook installation | PASS |

**Commit**: 769369c

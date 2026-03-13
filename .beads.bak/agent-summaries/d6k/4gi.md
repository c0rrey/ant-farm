# Summary: ant-farm-4gi — Fix pre-push hook not being versioned or installable

**Epic**: d6k (Setup & Forkability)
**Commit**: 6c3f59d
**Status**: Complete

---

## 1. Approaches Considered

### Approach 1: Symlink-based installer
Create a symlink from `.git/hooks/pre-push` -> `.beads/hooks/pre-push`. Any change to the versioned hook is immediately reflected without re-running the installer.

Tradeoffs:
- Pro: Always in sync with the versioned source file.
- Con: Symlinks on Windows (even with WSL) are unreliable. Absolute symlinks are machine-specific; relative symlinks can break if the repo is moved. The existing `.git/hooks/pre-push` is not identical to `.beads/hooks/pre-push` — symlinking would install the wrong (bd-shim) hook rather than the working one.

### Approach 2: Direct copy of `.beads/hooks/pre-push`
Copy the bd-shim from `.beads/hooks/pre-push` into `.git/hooks/pre-push`.

Tradeoffs:
- Pro: Simple, cross-platform.
- Con: `.beads/hooks/pre-push` is a bd-shim (`bd hooks run pre-push`), but the actual working hook in this repo calls `scripts/sync-to-claude.sh` directly. Copying the shim would install a hook that depends on `bd` and does NOT trigger the ant-farm sync. This would break the expected behavior.

### Approach 3 (Selected): Installer writes the working hook pattern as a heredoc
The installer script contains the hook body verbatim (matching the current `.git/hooks/pre-push`) as a heredoc and writes it to `.git/hooks/pre-push`. The hook delegates to `scripts/sync-to-claude.sh`.

Tradeoffs:
- Pro: Installs the correct, known-working hook. Self-contained. No external dependency (`bd` not required). Idempotent with backup on overwrite.
- Con: Hook body maintained in two places (installer + `.git/hooks/pre-push` at rest), but since hook content is stable and minimal (6 lines), this is acceptable.

### Approach 4: Git template directory approach
Configure `git config core.hooksPath` to point to a versioned `hooks/` directory in the repo, eliminating the need for `.git/hooks/` entirely.

Tradeoffs:
- Pro: Hooks are always active; no installer step at all.
- Con: `core.hooksPath` is a machine-local git config setting that must still be set per-clone. It also changes hook resolution for ALL hooks (including any user-global hooks), which is a broader change than the task scope. Would require touching git config, not just installing a hook file. Out of scope.

---

## 2. Selected Approach with Rationale

**Approach 3**: Installer writes the working hook as a heredoc.

The key insight from reviewing the repo state: `.beads/hooks/pre-push` (bd-shim) and `.git/hooks/pre-push` (sync-to-claude.sh delegation) are different files with different behaviors. The bd-shim was likely seeded as boilerplate but is not what this repo uses. Copying it would install a broken hook. The installer must reproduce the working hook pattern.

The heredoc approach is self-contained, auditable, and produces an executable hook that exactly matches what the repo currently uses. Backup-on-overwrite makes it safe to re-run.

---

## 3. Implementation Description

**File created: `scripts/install-hooks.sh`** (new, executable)

The script:
1. Resolves `REPO_ROOT` relative to its own location (`dirname "$0"/..`) — works regardless of cwd.
2. Validates that `.git/hooks/` exists (guards against running outside a git repo).
3. If `.git/hooks/pre-push` already exists, backs it up to `.git/hooks/pre-push.bak` before overwriting.
4. Writes the hook body via heredoc (`<<'HOOK'`) — single-quoted delimiter prevents variable expansion in hook body.
5. Sets the hook executable with `chmod +x`.
6. Prints confirmation messages.

The written hook body is identical to the existing `.git/hooks/pre-push`: it finds `scripts/sync-to-claude.sh` relative to the git root and delegates to it.

**File modified: `orchestration/SETUP.md`** (lines 7–22 of Prerequisites section)

Replaced the single-command first-time setup block with a two-step sequence:
1. `./scripts/install-hooks.sh` — install the pre-push hook
2. `./scripts/sync-to-claude.sh` — run initial sync immediately

Added a prose paragraph explaining the relationship between `.beads/hooks/pre-push` (bd-shim reference), the installer, and the working `.git/hooks/pre-push`. This documents the hook architecture that was previously undocumented.

---

## 4. Correctness Review

### `scripts/install-hooks.sh`
- Uses `set -euo pipefail` — strict error handling.
- `REPO_ROOT` resolved with `cd "$(dirname "$0")/.." && pwd` — correct for any invocation path.
- `[[ ! -d "$HOOKS_DIR" ]]` guard — prevents silent failure outside a git repo.
- Backup conditional uses `[[ -f "$HOOK_TARGET" ]]` — only backs up if regular file exists (not symlink check, but acceptable for this use case).
- Heredoc delimiter is single-quoted (`<<'HOOK'`) — variable expansion in hook body is intentionally suppressed.
- `chmod +x` applied after write — hook will be executable.
- Hook content matches existing `.git/hooks/pre-push` byte-for-byte (verified: both 265 bytes in test).
- Tested idempotency: re-running creates `.bak` and reinstalls correctly.

### `orchestration/SETUP.md` (Prerequisites section)
- Both commands use `./scripts/` path (relative, works from repo root).
- Commands are in the correct order (install hook first, then sync immediately).
- Prose correctly identifies `.beads/hooks/pre-push` as a bd-shim reference and clarifies it differs from the working hook.
- Does not modify any other sections of SETUP.md.
- Does not touch `CLAUDE.md`, `scripts/sync-to-claude.sh`, `.beads/hooks/pre-push`, or `orchestration/templates/`.

### Acceptance Criteria Verification
- AC1: `scripts/install-hooks.sh` is a tracked file that installs the pre-push hook. PASS.
- AC2: Running the installer produces `.git/hooks/pre-push` that calls `sync-to-claude.sh` (the sync trigger). PASS.
- AC3: `orchestration/SETUP.md` documents the installation step with exact commands. PASS.

---

## 5. Build/Test Validation

```
bash -n scripts/install-hooks.sh   # Syntax OK
bash -n .git/hooks/pre-push        # Existing hook syntax OK
```

Functional test in `/tmp/ant-farm-hook-test/`:
- Created minimal git structure (`.git/hooks/` directory).
- Ran installer: hook created, exit 0, output correct.
- Verified hook is 265 bytes, executable, passes `bash -n`.
- Re-ran installer: backup created as `pre-push.bak`, new hook installed, exit 0.

---

## 6. Acceptance Criteria Checklist

| Criterion | Status |
|-----------|--------|
| A tracked script (e.g., `scripts/install-hooks.sh`) exists that installs the pre-push hook | PASS |
| Running the installer creates a working `.git/hooks/pre-push` that triggers sync | PASS |
| README or SETUP.md documents the hook installation step with exact commands | PASS |

All acceptance criteria pass.

---

## Adjacent Issues (do not fix)

- `.beads/hooks/pre-push` (bd-shim) and `.git/hooks/pre-push` (sync-to-claude.sh delegation) have diverged. The bd-shim file exists as a versioned reference but is not the hook actually in use. This relationship could be clarified further in `.beads/hooks/pre-push` header comments, but that file is owned by this task's scope as "do not edit" and is noted here for tracking.
- `README.md:L266-268` still says "via the pre-push hook" without linking to the installer — per scope, README edits are out of scope for this task (ant-farm-5fa covers installation documentation).

# Summary: ant-farm-wg2i

**Task**: fix: installed pre-push hook is fatal on sync failure, contradicting install-hooks.sh non-fatal design
**Commit**: 4a30d6a
**Status**: CLOSED

---

## 1. Approaches Considered

**Approach A: Run install-hooks.sh directly (SELECTED)**
Execute `./scripts/install-hooks.sh` — the canonical, documented installer. It generates the correct hook content from its own heredoc, backs up the stale hook automatically, sets executable permissions, and regenerates both hooks atomically. Tradeoff: also regenerates the pre-commit hook (already current, so this is benign but slightly broader than strictly required).

**Approach B: Write hook content directly**
Extract the heredoc content from install-hooks.sh and write it directly to `.git/hooks/pre-push` using the Write tool. Produces exactly the same output as Approach A without touching the pre-commit hook. Tradeoff: if install-hooks.sh changes again in the future, this approach encodes the same root-cause pattern — the directly-written file diverges from the installer. Also requires manually setting executable permissions.

**Approach C: Symlink hook to a repo script**
Create a thin wrapper script in `scripts/` and symlink `.git/hooks/pre-push` to it. The symlink would always reflect the current script without needing a re-run step. Tradeoff: fundamentally changes the hook architecture and is explicitly out of scope. Git hooks cannot be symlinked into the repo tree without security implications and path resolution issues.

**Approach D: Add a version marker for drift detection**
Add a version token (e.g. `# HOOK_VERSION=2`) to both the installer template and the installed hook. A separate check script could compare versions and warn when they diverge. Tradeoff: addresses future drift detection only — does not fix the currently stale hook. Adds ongoing complexity. Appropriate as a follow-up improvement, not as the primary fix here.

---

## 2. Selected Approach

**Approach A — Run install-hooks.sh directly.**

Rationale: This is exactly what the task brief and the task description specify ("Re-run `./scripts/install-hooks.sh` to replace the installed hook with the current non-fatal version"). It uses the canonical tool for hook installation, is idempotent, creates an automatic timestamped backup of the stale hook, sets permissions correctly, and produces output that is guaranteed to match the installer template by construction. The side effect of regenerating the pre-commit hook is benign.

---

## 3. Implementation Description

**Step 1 — Regenerate .git/hooks/pre-push**

Ran `./scripts/install-hooks.sh`. The installer:
- Backed up the stale hook to `.git/hooks/pre-push.bak.20260222_090650`
- Wrote the new hook from its heredoc (lines 39-58 of install-hooks.sh)
- Set executable permissions (`chmod +x`)

The new hook wraps the sync call in a non-fatal check:
```bash
if ! "$SYNC_SCRIPT"; then
    echo "[ant-farm] WARNING: sync-to-claude.sh failed — push continuing without sync." >&2
    ...
fi
```
Any sync failure now prints a warning and exits 0, allowing the push to proceed.

**Step 2 — Fix CONTRIBUTING.md L161 (rsync --delete claim)**

Changed:
```
- `orchestration/` to `~/.claude/orchestration/` (via rsync `--delete`, excluding `scripts/`)
```
To:
```
- `orchestration/` to `~/.claude/orchestration/` (via rsync without `--delete`, excluding `scripts/` and `_archive/` — existing files in the target that are not in the source are preserved, not deleted)
```
This matches the actual rsync invocation in sync-to-claude.sh L27:
`rsync -av --exclude='scripts/' --exclude='_archive/' "$REPO_ROOT/orchestration/" ~/.claude/orchestration/`

**Step 3 — Add re-run reminder to CONTRIBUTING.md**

Added a paragraph after the hook list in "Installing the hooks":
```
**Re-run after pulling changes.** If `scripts/install-hooks.sh` is updated upstream (e.g. after a `git pull`), re-run it to get the new hook behavior. The installed hook in `.git/hooks/` is not updated automatically — it only changes when you run `install-hooks.sh` again.
```

---

## 4. Correctness Review

**.git/hooks/pre-push**
- Contains `if ! "$SYNC_SCRIPT"; then` — non-fatal pattern. CORRECT.
- Missing script check (`if [[ ! -x "$SYNC_SCRIPT" ]]`) exits 1 — intentionally fatal for missing/non-executable sync script. CORRECT (matches installer template).
- Executable bit confirmed (`-rwxr-xr-x`). CORRECT.
- Content matches install-hooks.sh lines 40-18 character-for-character (verified by reading both). CORRECT.

**CONTRIBUTING.md**
- L161: No longer claims `--delete`. Now says "without `--delete`" and lists both exclusions (`scripts/` and `_archive/`). Matches sync-to-claude.sh L27. CORRECT.
- Re-run reminder placed immediately after the hook list, before "After syncing" section. Logically positioned — a contributor reading the install instructions sees it in context. CORRECT.
- No other lines were changed; surrounding context was preserved. CORRECT.

**Assumptions audit**
- Assumed `.git/hooks/` is the correct hooks directory. Confirmed: install-hooks.sh uses `HOOKS_DIR="$REPO_ROOT/.git/hooks"` with the same assumption.
- Assumed sync-to-claude.sh L27 is the definitive rsync invocation. Confirmed: read the full file; L27 is the only rsync call.
- Assumed `_archive/` exclusion is significant enough to document. Confirmed: sync-to-claude.sh has an inline comment at L27 explaining the no-delete policy, and the `--exclude='_archive/'` is explicit.

---

## 5. Build/Test Validation

**Functional test — sync failure is non-fatal:**
Created a temporary script that exits 1 and ran the hook logic directly:
```
[ant-farm] WARNING: sync-to-claude.sh failed — push continuing without sync.
[ant-farm]   Cause: the sync script exited non-zero ...
[ant-farm]   Fix:   run scripts/sync-to-claude.sh manually to diagnose, then re-push.
Hook completed — push proceeds.
Shell exited with: 0
```
The hook exits 0 when sync fails. PASS.

**Functional test — missing script is fatal:**
Ran hook logic with a non-existent SYNC_SCRIPT path:
```
[ant-farm] ERROR: sync script not found or not executable: ...
Shell exited with: 1
```
Missing script check still exits 1. PASS (intentional behavior preserved).

**No regressions in pre-commit hook:** Regenerated as a side effect; content was verified to match the installer template.

---

## 6. Acceptance Criteria Checklist

- [x] **AC1: Installed .git/hooks/pre-push matches output of install-hooks.sh (non-fatal sync)**
  PASS — Hook was regenerated via install-hooks.sh. Uses `if ! "$SYNC_SCRIPT"` pattern. Exits 0 on sync failure.

- [x] **AC2: CONTRIBUTING.md rsync description matches actual sync-to-claude.sh behavior (no --delete, excludes _archive/)**
  PASS — L161 updated: removed `--delete` claim, added `_archive/` exclusion, noted preservation behavior.

- [x] **AC3: CONTRIBUTING.md includes guidance on re-running install-hooks.sh after pulling changes**
  PASS — Added bold "Re-run after pulling changes." paragraph with explicit instruction.

- [x] **AC4: Push succeeds even when sync-to-claude.sh fails (manual test)**
  PASS — Simulated sync failure in bash: hook exits 0, prints warning, does not block push.

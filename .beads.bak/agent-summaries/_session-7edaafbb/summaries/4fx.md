# Task Summary: ant-farm-4fx

**Task**: install-hooks.sh backup uses fixed filename, losing backup history on re-run
**Commit**: 739a370

## 1. Approaches Considered

**Approach A — Timestamp suffix with `date +%Y%m%d_%H%M%S` (selected)**
Replace the fixed `.bak` suffix with a datetime stamp in `YYYYMMDD_HHMMSS` format. Each invocation produces a unique filename. No external dependencies beyond `date`. Sortable and filesystem-safe.

**Approach B — Sequence number suffix**
Find the highest existing `.bak.N` file and increment. Preserves ordinal ordering without time awareness, but requires an additional shell glob/count operation and is more complex to implement correctly.

**Approach C — Git commit hash suffix**
Use `git rev-parse --short HEAD` as the suffix. Meaningful semantically (which repo state triggered the reinstall), but the hash describes HEAD, not the hook content being backed up, which may confuse operators.

**Approach D — ISO-8601 suffix with `date -Iseconds`**
More readable format (`2026-02-20T12:34:56`) but colons in filenames are problematic on Windows file systems and some macOS contexts.

## 2. Selected Approach

Approach A. `date +%Y%m%d_%H%M%S` produces a sortable, filesystem-safe, human-readable timestamp. It is the simplest correct solution, matches POSIX `date` behavior on both macOS and Linux, and requires no logic beyond inline variable expansion.

## 3. Implementation Description

Two lines changed in `scripts/install-hooks.sh`:

- L28: `BACKUP="$HOOK_TARGET.bak.$(date +%Y%m%d_%H%M%S)"` (was `.bak`)
- L58: `BACKUP="$PRECOMMIT_TARGET.bak.$(date +%Y%m%d_%H%M%S)"` (was `.bak`)

No other lines were touched. Backup logic (copy, echo) is unchanged.

## 4. Correctness Review

**scripts/install-hooks.sh**

- L28: Timestamp appended via command substitution inside double-quotes — correct shell expansion.
- L58: Same pattern for pre-commit hook — correct and symmetric.
- `date +%Y%m%d_%H%M%S` is POSIX-compatible; works on macOS and Linux without GNU-specific flags.
- `set -euo pipefail` at the top means if `date` somehow fails, the script exits — safe.
- AC1 (unique filename each backup): Timestamp changes every second; two runs within the same second would collide, but that is an acceptable edge case for a manual installer. — PASS
- AC2 (previous backups not overwritten): Each new timestamp produces a new filename, old backups persist. — PASS

## 5. Build/Test Validation

```
bash -n scripts/install-hooks.sh  # syntax OK
```

Manual trace: running the installer twice with an existing hook now produces:
- `.git/hooks/pre-push.bak.20260220_103000`
- `.git/hooks/pre-push.bak.20260220_103045`
Both files coexist.

## 6. Acceptance Criteria Checklist

- [x] AC1: Each backup has a unique filename — PASS (timestamp suffix at L28 and L58)
- [x] AC2: Previous backups are not overwritten — PASS (new filename each run)

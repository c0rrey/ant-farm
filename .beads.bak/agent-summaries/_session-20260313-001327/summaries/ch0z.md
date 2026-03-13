---
bead: ant-farm-ch0z
title: TOCTOU race in cmd_doctor --fix: reads tasks.jsonl without holding FileLock
commit: 96347af
---

## Files Changed

- `crumb.py` — moved `FileLock` acquisition in `cmd_doctor` to wrap the entire read+validate+write sequence; removed the inner `FileLock` that previously guarded only the write phase

## Implementation

The original code had two separate phases:

1. **Unlocked read** (L1714): `read_tasks()` called outside any lock, followed by the raw `open()` pass for malformed-line detection — also unlocked.
2. **Locked write** (L1816): `with FileLock(): write_tasks(...)` guarded only the final write.

Between phases 1 and 2, another process could append new crumbs (via `crumb create`) or update existing ones. When the doctor wrote its snapshot under lock, those interleaved changes were silently discarded.

The fix: introduce a single `with FileLock():` block at L1785 that wraps all three phases — Pass 1 (raw `open()` for malformed-line detection), the lookup-structure build and semantic checks (Pass 2), and the `write_tasks()` call. The `--fix` print statements and the error/warning report section remain outside the lock — they only read the `errors`, `warnings`, and `fixes_applied` lists that were populated during the locked phase, so holding the lock during reporting is unnecessary.

The inner `with FileLock():` that previously wrapped only `write_tasks()` was removed. `write_tasks()` is now called directly inside the outer lock at L1892.

## Approaches Considered

1. **Acquire lock only when `--fix` is passed**: Guard the read+write with `FileLock` only if `args.fix` is true, leaving the read-only path unlocked. Rejected because read-only doctor runs are also subject to TOCTOU — a concurrent write between the `open()` and the duplicate-ID check could produce false duplicate errors or miss newly created records. The lock should always be held for consistency.

2. **Use `read_tasks()` inside the lock instead of a raw `open()`**: Replace the raw `open()` + `json.loads` loop with a call to `read_tasks()`, adding separate malformed-line detection via a second `open()`. This would simplify the code but require two reads. The existing single-pass approach (raw `open()` that both detects malformed lines and accumulates valid records) is more efficient and already correct — it just needed to move inside the lock.

3. **Acquire a read lock (shared flock) for the read phase, upgrade to exclusive for write**: Use `fcntl.LOCK_SH` during read and `fcntl.LOCK_EX` for write. This would allow concurrent readers. Rejected because `FileLock` only implements `LOCK_EX`, upgrading from shared to exclusive requires releasing and re-acquiring the lock (introducing a new TOCTOU window), and crumb.py has no use case for concurrent reads that would benefit from this complexity.

4. **Re-read tasks.jsonl under lock before writing, then merge**: Keep the unlocked read for detection, then re-read inside the lock before writing to pick up any concurrent changes, and merge the doctor's fixes onto the freshly-read snapshot. Rejected because merging is complex (must correlate records by ID, handle concurrent additions/deletions) and the simpler correct fix — hold the lock for the full sequence — eliminates the race entirely without any merge logic.

5. **Use an atomic rename pattern for the doctor's write, without a lock**: Write to a temp file and `os.rename()` atomically. Rejected because `write_tasks()` already uses this pattern internally, but it doesn't prevent another writer from doing the same concurrently — both writes succeed and one silently wins. Only a file lock provides mutual exclusion.

## Per-File Correctness Notes

### crumb.py

- **Lock scope (L1785-L1894)**: The `with FileLock():` block ends after the `if fixes_applied` write block at L1894, before the `# --- Report ---` section at L1896. The `errors`, `warnings`, and `fixes_applied` lists are defined before the lock at L1781-L1783 and populated inside it, so they remain accessible after the lock is released. No data escapes the lock boundary through mutable shared state.
- **`die()` inside the lock (L1801-L1802)**: If `open()` raises `OSError`, `die()` calls `sys.exit()`. Python's `with` statement guarantees `FileLock.__exit__` is called on any exception including `SystemExit` (because `SystemExit` is a `BaseException`). `FileLock.__exit__` calls `self._lock_file.close()` which releases the `flock`. The lock is not leaked on early exit.
- **Removed inner `FileLock` (was L1891-L1892)**: The original `with FileLock():` around `write_tasks()` is removed. `write_tasks()` is called directly at L1892 inside the outer lock. Since `FileLock` uses `fcntl.LOCK_EX` (exclusive), re-entering it from the same process would deadlock on Linux (flock is per-open-file-description, not per-process on all platforms). Removing the inner lock eliminates this hazard.
- **`fixes_applied` print inside lock (L1893-L1894)**: The `print(f"fixed: {msg}")` calls moved inside the lock. This is a minor behavioral change (output appears while lock is held) but is correct — the messages are generated from `fixes_applied` which is populated during the locked phase, and printing them under lock ensures they appear before the lock is released and another process can observe the written state.
- **Read-only path (`--fix` not set)**: When `args.fix` is false, no write occurs; the lock is still held for the duration of Pass 1 and Pass 2. This is the correct trade-off — the lock is brief (file read + in-memory validation) and ensures the doctor's snapshot is consistent.

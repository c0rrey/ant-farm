#!/usr/bin/env python3
# ant-farm crumb CLI
"""crumb.py — Lightweight JSONL task tracker CLI for ant-farm.

Single-file Python CLI, stdlib only, minimum Python 3.8.
Manages tasks and trails in .crumbs/tasks.jsonl with flock-based
concurrency safety and atomic writes.

Usage:
    crumb list [--open] [--closed] [--in-progress] [--parent ID]
               [--priority P0-P4] [--type TYPE] [--agent-type TYPE]
               [--discovered] [--after DATE] [--limit N]
               [--sort FIELD] [--short]
    crumb show <ID>
    crumb create --title "..." [--from-json '...']
    crumb update <ID> [--status STATUS] [--note "..."] [FIELD=VALUE ...]
    crumb close <ID> [<ID> ...]
    crumb reopen <ID>
    crumb ready [--limit N] [--sort FIELD]
    crumb blocked
    crumb link <ID> [--parent ID] [--blocked-by ID]
                    [--remove-blocked-by ID] [--discovered-from ID]
    crumb search "QUERY"
    crumb trail list
    crumb trail show <ID>
    crumb trail create --title "..."
    crumb trail close <ID>
    crumb tree [ID]
    crumb import <FILE> [--from-beads]
    crumb doctor
    crumb init [--prefix PREFIX]
    crumb prune [--days N] [--dry-run]
"""

from __future__ import annotations

import argparse
import fcntl
import json
import os
import re
import shutil
import sys
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterator, List, Optional, Tuple

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

TASKS_FILE = "tasks.jsonl"
CONFIG_FILE = "config.json"
LOCK_FILE = "tasks.lock"
CRUMBS_DIR_NAME = ".crumbs"

DEFAULT_CONFIG: Dict[str, Any] = {
    "prefix": "AF",
    "default_priority": "P2",
    "next_crumb_id": 1,
    "next_trail_id": 1,
}

VALID_STATUSES = ("open", "in_progress", "closed")
VALID_PRIORITIES = ("P0", "P1", "P2", "P3", "P4")
VALID_TYPES = ("task", "bug", "feature", "trail")

# ---------------------------------------------------------------------------
# Prune constants
# ---------------------------------------------------------------------------

DEFAULT_RETENTION_DAYS: int = 14
ACTIVE_GUARD_MINUTES: int = 60
SESSION_DIR_PREFIXES: Tuple[str, ...] = ("_session-", "_decompose-", "_review-")
SESSION_TS_FORMAT: str = "%Y%m%d-%H%M%S"


# ---------------------------------------------------------------------------
# Error helpers
# ---------------------------------------------------------------------------


def die(message: str, code: int = 1) -> None:
    """Print error to stderr and exit with given code.

    Args:
        message: Human-readable error description (printed with "error: " prefix).
        code: Process exit code; defaults to 1.

    Raises:
        SystemExit: Always — this function never returns normally.
    """
    print(f"error: {message}", file=sys.stderr)
    sys.exit(code)


# ---------------------------------------------------------------------------
# Directory discovery — walks up from cwd like git finds .git/
# ---------------------------------------------------------------------------


def find_crumbs_dir() -> Path:
    """Walk up from cwd to filesystem root; return first .crumbs/ found.

    Returns:
        Absolute path to the .crumbs/ directory.

    Raises:
        SystemExit: If no .crumbs/ directory is found in any ancestor.
    """
    current = Path.cwd().resolve()
    while True:
        candidate = current / CRUMBS_DIR_NAME
        if candidate.is_dir():
            return candidate
        parent = current.parent
        if parent == current:
            # Reached filesystem root without finding .crumbs/
            die(
                f"no {CRUMBS_DIR_NAME}/ directory found in {Path.cwd()} or any parent. "
                "Run /ant-farm-init first."
            )
        current = parent


def crumbs_dir() -> Path:
    """Return the .crumbs/ directory, exiting if not found.

    Returns:
        Absolute path to the .crumbs/ directory.

    Raises:
        SystemExit: If no .crumbs/ directory is found in any ancestor.
    """
    return find_crumbs_dir()


def tasks_path() -> Path:
    """Return path to tasks.jsonl, exiting if .crumbs/ not found.

    Returns:
        Absolute path to .crumbs/tasks.jsonl.

    Raises:
        SystemExit: If no .crumbs/ directory is found in any ancestor.
    """
    return crumbs_dir() / TASKS_FILE


def config_path() -> Path:
    """Return path to config.json, exiting if .crumbs/ not found.

    Returns:
        Absolute path to .crumbs/config.json.

    Raises:
        SystemExit: If no .crumbs/ directory is found in any ancestor.
    """
    return crumbs_dir() / CONFIG_FILE


def lock_path() -> Path:
    """Return path to tasks.lock, exiting if .crumbs/ not found.

    Returns:
        Absolute path to .crumbs/tasks.lock.

    Raises:
        SystemExit: If no .crumbs/ directory is found in any ancestor.
    """
    return crumbs_dir() / LOCK_FILE


# ---------------------------------------------------------------------------
# Config read / write
# ---------------------------------------------------------------------------


def read_config() -> Dict[str, Any]:
    """Read config.json, returning defaults merged with stored values.

    Returns:
        Dict with keys: prefix, default_priority, next_crumb_id, next_trail_id.

    Raises:
        SystemExit: If config.json exists but cannot be read or contains
            invalid JSON, or if a counter field is not an integer.
    """
    path = config_path()
    if not path.exists():
        return dict(DEFAULT_CONFIG)
    try:
        with open(path, "r", encoding="utf-8") as fh:
            stored = json.load(fh)
    except (json.JSONDecodeError, OSError) as exc:
        die(f"cannot read config.json: {exc}")
    config = dict(DEFAULT_CONFIG)
    config.update(stored)
    for field in ("next_crumb_id", "next_trail_id"):
        try:
            config[field] = int(config[field])
        except (ValueError, TypeError):
            die(f"config field '{field}' must be an integer, got: {config[field]!r}")
    return config


def write_config(config: Dict[str, Any]) -> None:
    """Atomically write config.json.

    Args:
        config: Dict to serialise.

    Raises:
        SystemExit: If the config file cannot be written (OS error).
    """
    path = config_path()
    tmp_path = path.with_suffix(".json.tmp")
    try:
        with open(tmp_path, "w", encoding="utf-8") as fh:
            json.dump(config, fh, indent=2)
            fh.write("\n")
        try:
            os.rename(str(tmp_path), str(path))
        except OSError:
            tmp_path.unlink(missing_ok=True)
            raise
    except OSError as exc:
        die(f"cannot write config.json: {exc}")


# ---------------------------------------------------------------------------
# JSONL read / write utilities
# ---------------------------------------------------------------------------


def read_tasks(path: Path) -> List[Dict[str, Any]]:
    """Read all records from a JSONL file.

    Args:
        path: Path to the JSONL file.

    Returns:
        List of parsed dicts, one per non-empty line.

    Raises:
        SystemExit: If the file cannot be opened (OS error). Malformed
            JSON lines emit a warning to stderr and are skipped, not raised.
    """
    records: List[Dict[str, Any]] = []
    try:
        fh_ctx = open(path, "r", encoding="utf-8")
    except OSError as exc:
        die(f"cannot read {path}: {exc}")
    with fh_ctx as fh:
        for lineno, line in enumerate(fh, start=1):
            line = line.rstrip("\n")
            if not line:
                continue
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError as exc:
                print(
                    f"warning: skipping malformed JSON on line {lineno}: {exc}",
                    file=sys.stderr,
                )
    return records


def write_tasks(path: Path, records: List[Dict[str, Any]]) -> None:
    """Atomically write records to a JSONL file via temp-then-rename.

    Args:
        path: Destination JSONL path.
        records: List of dicts to serialise, one per line.

    Raises:
        SystemExit: If the temporary file cannot be written or renamed
            (OS error).
    """
    tmp_path = path.with_suffix(".jsonl.tmp")
    try:
        with open(tmp_path, "w", encoding="utf-8") as fh:
            for record in records:
                fh.write(json.dumps(record, separators=(",", ":")) + "\n")
        try:
            os.rename(str(tmp_path), str(path))
        except OSError:
            tmp_path.unlink(missing_ok=True)
            raise
    except OSError as exc:
        die(f"cannot write {path.name}: {exc}")



# ---------------------------------------------------------------------------
# File locking — exclusive flock on tasks.lock
# ---------------------------------------------------------------------------


_LOCK_TIMEOUT_SECS: int = 10
_LOCK_RETRY_INTERVAL: float = 0.05


class FileLock:
    """Context manager that holds an exclusive flock on tasks.lock.

    Platform restriction: uses ``fcntl.flock``, which is Unix-only (Linux,
    macOS). Windows is not supported; attempting to use this on Windows will
    raise ``AttributeError`` at import time (``fcntl`` is not available).

    Acquires the lock with ``LOCK_NB`` (non-blocking) and retries for up to
    ``_LOCK_TIMEOUT_SECS`` seconds so the process never blocks indefinitely.

    Usage::

        with FileLock():
            # read, modify, write tasks.jsonl safely
    """

    def __init__(self) -> None:
        """Initialise with no open lock file handle."""
        self._lock_file: Optional[Any] = None

    def __enter__(self) -> "FileLock":
        """Acquire the exclusive flock on tasks.lock.

        Retries with ``LOCK_NB`` until the lock is acquired or the timeout
        expires (default: ``_LOCK_TIMEOUT_SECS`` seconds).

        Returns:
            self, allowing use as a context manager.

        Raises:
            SystemExit: If the lock file cannot be created/opened, or if the
                lock cannot be acquired within ``_LOCK_TIMEOUT_SECS`` seconds.
        """
        path = lock_path()
        try:
            path.touch()
            self._lock_file = open(path, "w", encoding="utf-8")
        except OSError as exc:
            die(f"cannot acquire lock: {exc}")
        deadline = time.monotonic() + _LOCK_TIMEOUT_SECS
        while True:
            try:
                fcntl.flock(self._lock_file, fcntl.LOCK_EX | fcntl.LOCK_NB)
                break
            except BlockingIOError:
                if time.monotonic() >= deadline:
                    self._lock_file.close()
                    self._lock_file = None
                    die(
                        f"cannot acquire lock: timed out after "
                        f"{_LOCK_TIMEOUT_SECS}s — another crumb process may "
                        f"be running"
                    )
                time.sleep(_LOCK_RETRY_INTERVAL)
        return self

    def __exit__(self, *_: Any) -> None:
        """Release the flock by closing the lock file handle.

        Closing the file descriptor releases the flock held on it.
        Safe to call even if __enter__ was never reached (guard on None).
        """
        if self._lock_file is not None:
            # flock is released automatically on close
            self._lock_file.close()
            self._lock_file = None


# ---------------------------------------------------------------------------
# Startup: clean up stale .tmp files
# ---------------------------------------------------------------------------


def cleanup_stale_tmp_files() -> None:
    """Remove any leftover .tmp files from a previous crashed write.

    Called at startup before any command runs. Silent — does not print
    unless an unexpected error occurs.
    """
    # Walk up from cwd silently (do not use die() / find_crumbs_dir() here
    # to avoid printing errors during startup before help is displayed).
    current = Path.cwd().resolve()
    crumbs: Optional[Path] = None
    while True:
        candidate = current / CRUMBS_DIR_NAME
        if candidate.is_dir():
            crumbs = candidate
            break
        parent = current.parent
        if parent == current:
            break  # Reached filesystem root — no .crumbs/ found
        current = parent

    if crumbs is None:
        return

    for tmp_file in crumbs.glob("*.tmp"):
        try:
            tmp_file.unlink()
        except OSError:
            pass  # Best-effort; ignore errors during cleanup


# ---------------------------------------------------------------------------
# Timestamp helpers
# ---------------------------------------------------------------------------


def now_iso() -> str:
    """Return current UTC time as an ISO 8601 string with Z suffix.

    Returns:
        UTC timestamp formatted as 'YYYY-MM-DDTHH:MM:SSZ'.
    """
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


# ---------------------------------------------------------------------------
# tasks.jsonl existence guard
# ---------------------------------------------------------------------------


def require_tasks_jsonl() -> Path:
    """Return path to tasks.jsonl, exiting with error if not found.

    Returns:
        Path to existing tasks.jsonl.

    Raises:
        SystemExit: If .crumbs/tasks.jsonl does not exist.
    """
    path = tasks_path()
    if not path.exists():
        die("no .crumbs/tasks.jsonl found. Run /ant-farm-init first.")
    return path


# ---------------------------------------------------------------------------
# Private helper utilities — used by subcommand handlers below
# ---------------------------------------------------------------------------


def _find_crumb(tasks: List[Dict[str, Any]], crumb_id: str) -> Optional[Dict[str, Any]]:
    """Return the first record matching crumb_id, or None.

    Args:
        tasks: List of task dicts from tasks.jsonl.
        crumb_id: The ID string to look up (case-sensitive).

    Returns:
        Matching dict or None if not found.
    """
    for task in tasks:
        if task.get("id") == crumb_id:
            return task
    return None


def _priority_sort_key(priority: str) -> int:
    """Return an integer sort key for a priority string (P0 sorts first).

    Args:
        priority: Priority string such as 'P0', 'P1', ..., 'P4'.

    Returns:
        Integer in range 0-4; unknown values sort last (5).
    """
    try:
        return int(priority[1]) if len(priority) == 2 and priority[0] == "P" else 5
    except (ValueError, IndexError):
        return 5


def _status_sort_key(status: str) -> int:
    """Return an integer sort key for a status string.

    Args:
        status: Status string such as 'open', 'in_progress', 'closed'.

    Returns:
        Integer sort key; unknown values sort last.
    """
    order = {"open": 0, "in_progress": 1, "closed": 2}
    return order.get(status, 3)


def _get_trail_children(
    tasks: List[Dict[str, Any]], trail_id: str
) -> List[Dict[str, Any]]:
    """Return all non-trail records whose links.parent equals trail_id.

    Args:
        tasks: Full task list from tasks.jsonl.
        trail_id: The trail ID to match against.

    Returns:
        List of child crumb dicts (excludes the trail record itself).
    """
    children = []
    for t in tasks:
        if t.get("type") == "trail":
            continue
        links = t.get("links") or {}
        if isinstance(links, dict) and links.get("parent") == trail_id:
            children.append(t)
    return children


def _auto_close_trail_if_complete(
    tasks: List[Dict[str, Any]], path: Path, closed_crumb_id: str
) -> None:
    """Auto-close a trail when the last open child is closed.

    Called from cmd_close (inside FileLock) after write_tasks. Looks up
    the closed crumb's parent trail (via links.parent). If all children
    of that trail are now closed, closes the trail and calls write_tasks
    again.

    Args:
        tasks: Already-modified task list (crumb already marked closed).
        path: Path to tasks.jsonl for the second write_tasks call.
        closed_crumb_id: The ID of the crumb that was just closed.
    """
    crumb = _find_crumb(tasks, closed_crumb_id)
    if crumb is None:
        return

    links = crumb.get("links") or {}
    if not isinstance(links, dict):
        links = {}
    parent_id = links.get("parent")
    if not parent_id:
        return

    trail = _find_crumb(tasks, parent_id)
    if trail is None or trail.get("type") != "trail":
        return
    if trail.get("status") == "closed":
        return  # Already closed; nothing to do

    children = _get_trail_children(tasks, parent_id)
    if not children:
        return  # No children tracked yet; don't auto-close empty trail

    all_closed = all(c.get("status") == "closed" for c in children)
    if all_closed:
        now = now_iso()
        trail["status"] = "closed"
        trail["closed_at"] = now
        trail["updated_at"] = now
        write_tasks(path, tasks)
        print(f"auto-closed trail {parent_id} (all children closed)")


def _auto_reopen_trail_if_needed(
    tasks: List[Dict[str, Any]], path: Path, trail_id: str, crumb_status: str
) -> None:
    """Auto-reopen a trail when a new open crumb is linked to it as parent.

    Called from cmd_link (inside FileLock) after write_tasks. If the trail
    is closed and the newly-linked crumb is not closed, reopens the trail.

    Args:
        tasks: Already-modified task list.
        path: Path to tasks.jsonl for the second write_tasks call.
        trail_id: The trail to potentially reopen.
        crumb_status: Current status of the crumb that was just linked.
    """
    if crumb_status == "closed":
        return  # Linking a closed crumb; trail stays closed

    trail = _find_crumb(tasks, trail_id)
    if trail is None or trail.get("type") != "trail":
        return
    if trail.get("status") != "closed":
        return  # Trail is not closed; nothing to do

    now = now_iso()
    trail["status"] = "open"
    trail.pop("closed_at", None)
    trail["updated_at"] = now
    write_tasks(path, tasks)
    print(f"auto-reopened trail {trail_id} (new open child linked)")


def _parse_session_dir_timestamp(name: str) -> Optional[datetime]:
    """Extract and parse the YYYYMMDD-HHMMSS timestamp from a session directory name.

    Checks whether *name* starts with one of the known session directory
    prefixes (``_session-``, ``_decompose-``, ``_review-``), strips the
    prefix, and attempts to parse the remainder as a ``%Y%m%d-%H%M%S``
    timestamp.  Returns ``None`` for names that do not match any known
    prefix or whose timestamp portion is not parseable.

    Args:
        name: Directory base name (not a full path).

    Returns:
        Parsed :class:`datetime` (naive, local) or ``None``.
    """
    matched_prefix: Optional[str] = None
    for prefix in SESSION_DIR_PREFIXES:
        if name.startswith(prefix):
            matched_prefix = prefix
            break
    if matched_prefix is None:
        return None

    ts_str = name[len(matched_prefix):]
    # Accept only the first 15 characters (YYYYMMDD-HHMMSS) so that
    # extra suffixes (e.g., _session-20260101-120000-extra) are still
    # parseable from the leading timestamp portion.
    ts_candidate = ts_str[:15]
    try:
        return datetime.strptime(ts_candidate, SESSION_TS_FORMAT)
    except ValueError:
        return None


def _is_active_session(dir_path: Path, now_ts: float) -> bool:
    """Return True if *dir_path* was modified within the active-guard window.

    Uses ``os.stat(dir_path).st_mtime`` so that ongoing writes to the
    session directory extend the guard window.  A fresh ``stat`` call is
    made here (not cached) to mitigate TOCTOU between the age check and
    the actual ``shutil.rmtree``.

    Args:
        dir_path: Absolute path to the session directory.
        now_ts: Current time as a POSIX timestamp (``time.time()``).

    Returns:
        ``True`` if the directory's mtime is within
        :data:`ACTIVE_GUARD_MINUTES` minutes of *now_ts*.
    """
    try:
        mtime = os.stat(dir_path).st_mtime
    except OSError:
        # If stat fails the directory may have vanished; treat as not active.
        return False
    return (now_ts - mtime) < (ACTIVE_GUARD_MINUTES * 60)


def cmd_list(args: argparse.Namespace) -> None:
    """List crumbs with optional filters, sort, and limit.

    Reads tasks.jsonl, applies composable filter flags, sorts, limits,
    and prints one line per crumb (short mode) or a summary table.

    Args:
        args: Parsed arguments from the list subparser.
    """
    path = require_tasks_jsonl()
    tasks = read_tasks(path)

    # Exclude trails from list output (type == 'trail' is the trail sentinel)
    results = [t for t in tasks if t.get("type") != "trail"]

    # --- status filters (compose: OR within status group) ---
    status_filters: List[str] = []
    if args.filter_open:
        status_filters.append("open")
    if args.filter_closed:
        status_filters.append("closed")
    if args.filter_in_progress:
        status_filters.append("in_progress")
    if status_filters:
        results = [t for t in results if t.get("status") in status_filters]

    # --- other filters ---
    if args.priority:
        results = [t for t in results if t.get("priority") == args.priority]

    if args.filter_type:
        results = [t for t in results if t.get("type") == args.filter_type]

    if args.agent_type:
        results = [
            t for t in results
            if (t.get("scope") or {}).get("agent_type") == args.agent_type
            or t.get("agent_type") == args.agent_type  # flat fallback
        ]

    if args.parent:
        results = [
            t for t in results
            if (t.get("links") or {}).get("parent") == args.parent
        ]

    if args.discovered:
        results = [
            t for t in results
            if (t.get("links") or {}).get("discovered_from")
        ]

    if args.after:
        # Compare ISO 8601 strings lexicographically; prepend date if needed
        after_str = args.after
        results = [
            t
            for t in results
            if (t.get("created_at") or "") > after_str
        ]

    # --- sort ---
    sort_field = args.sort  # 'priority' | 'created_at' | 'status'
    if sort_field == "priority":
        results.sort(key=lambda t: _priority_sort_key(t.get("priority", "P4")))
    elif sort_field == "status":
        results.sort(key=lambda t: _status_sort_key(t.get("status", "")))
    else:
        # Default: created_at ascending
        results.sort(key=lambda t: t.get("created_at") or "")

    # --- limit ---
    if args.limit is not None and args.limit > 0:
        results = results[: args.limit]

    if not results:
        print("no crumbs found")
        return

    # --- output ---
    if args.short:
        for t in results:
            tid = t.get("id", "?")
            title = t.get("title", "")
            status = t.get("status", "")
            priority = t.get("priority", "")
            print(f"{tid:<12} {priority:<4} {status:<12} {title}")
    else:
        for t in results:
            tid = t.get("id", "?")
            title = t.get("title", "")
            status = t.get("status", "")
            priority = t.get("priority", "")
            crumb_type = t.get("type", "")
            created_at = t.get("created_at", "")
            print(f"{tid:<12} {priority:<4} {status:<12} {crumb_type:<10} {created_at[:10]}  {title}")


def cmd_show(args: argparse.Namespace) -> None:
    """Show all fields for a crumb or trail.

    Args:
        args: Parsed arguments; args.id is the crumb ID to display.
    """
    path = require_tasks_jsonl()
    tasks = read_tasks(path)

    crumb = _find_crumb(tasks, args.id)
    if crumb is None:
        die(f"crumb '{args.id}' not found")

    # Print all known fields with labels
    fields = [
        ("id", "ID"),
        ("type", "Type"),
        ("title", "Title"),
        ("status", "Status"),
        ("priority", "Priority"),
        ("agent_type", "Agent Type"),
        ("description", "Description"),
        ("acceptance_criteria", "Acceptance Criteria"),
        ("scope", "Scope"),
        ("parent", "Parent"),
        ("discovered_from", "Discovered From"),
        ("blocked_by", "Blocked By"),
        ("links", "Links"),
        ("notes", "Notes"),
        ("created_at", "Created At"),
        ("updated_at", "Updated At"),
        ("closed_at", "Closed At"),
    ]

    for key, label in fields:
        value = crumb.get(key)
        if value is None or value == "" or value == [] or value == {}:
            continue
        if isinstance(value, list):
            print(f"{label}:")
            for item in value:
                print(f"  - {item}")
        else:
            print(f"{label}: {value}")

    # Print any extra keys not in the known list
    known_keys = {k for k, _ in fields}
    for key, value in crumb.items():
        if key not in known_keys and value not in (None, "", [], {}):
            label = key.replace("_", " ").title()
            print(f"{label}: {value}")


def cmd_create(args: argparse.Namespace) -> None:
    """Create a new crumb and append it to tasks.jsonl.

    Accepts either --title with optional flags, --from-json with a
    JSON object containing explicit fields, or --from-file with a path
    to a JSON file. Auto-assigns an ID from config if not provided in
    the JSON payload.

    Args:
        args: Parsed arguments from the create subparser.
    """
    with FileLock():
        path = tasks_path()
        # tasks.jsonl may not exist yet; create it on first write
        if path.exists():
            tasks = read_tasks(path)
        else:
            tasks = []

        # --- build the new record ---
        config = read_config()
        prefix = config["prefix"]

        if args.from_json and args.from_file:
            die("--from-json and --from-file are mutually exclusive")

        if args.from_json:
            try:
                payload: Dict[str, Any] = json.loads(args.from_json)
            except json.JSONDecodeError as exc:
                die(f"invalid JSON in --from-json: {exc}")
            if not isinstance(payload, dict):
                die("--from-json must be a JSON object, not a list or scalar")

            # Merge explicit --title / --priority / --type / --description
            # CLI flags override JSON payload fields
            if args.title:
                payload["title"] = args.title
            if args.priority:
                payload["priority"] = args.priority
            if args.crumb_type:
                payload["type"] = args.crumb_type
            if args.description:
                payload["description"] = args.description
        elif args.from_file:
            file_path = Path(args.from_file)
            if not file_path.exists():
                die(f"--from-file path does not exist: {args.from_file}")
            if file_path.is_dir():
                die(f"--from-file path is a directory, not a file: {args.from_file}")
            try:
                payload = json.loads(file_path.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError) as exc:
                die(f"cannot read --from-file: {exc}")
            if not isinstance(payload, dict):
                die("--from-file must contain a JSON object, not a list or scalar")

            # Merge explicit --title / --priority / --type / --description
            # CLI flags override JSON payload fields
            if args.title:
                payload["title"] = args.title
            if args.priority:
                payload["priority"] = args.priority
            if args.crumb_type:
                payload["type"] = args.crumb_type
            if args.description:
                payload["description"] = args.description
        else:
            if not args.title:
                die("--title is required unless --from-json or --from-file is provided")
            payload = {"title": args.title}
            if args.priority:
                payload["priority"] = args.priority
            if args.crumb_type:
                payload["type"] = args.crumb_type
            if args.description:
                payload["description"] = args.description

        # Reject trail creation via crumb create; use 'crumb trail create' instead
        if payload.get("type") == "trail":
            die("use 'crumb trail create' to create trails")

        # --- assign ID ---
        if "id" in payload and payload["id"]:
            crumb_id = str(payload["id"])
            # Duplicate detection
            if _find_crumb(tasks, crumb_id) is not None:
                die(f"crumb '{crumb_id}' already exists")
            # Advance counter past this explicit numeric ID so subsequent
            # auto-ID calls don't wastefully hit the duplicate check loop.
            prefix_dash = f"{prefix}-"
            if crumb_id.startswith(prefix_dash):
                suffix = crumb_id[len(prefix_dash):]
                try:
                    explicit_num = int(suffix)
                    if explicit_num >= int(config.get("next_crumb_id", 1)):
                        config["next_crumb_id"] = explicit_num + 1
                        write_config(config)
                except ValueError:
                    pass  # non-numeric suffix (e.g. T-prefixed trail): leave counter alone
        else:
            next_id = int(config.get("next_crumb_id", 1))
            crumb_id = f"{prefix}-{next_id}"
            # Advance counter even if this ID somehow already exists
            while _find_crumb(tasks, crumb_id) is not None:
                next_id += 1
                crumb_id = f"{prefix}-{next_id}"
            config["next_crumb_id"] = next_id + 1
            write_config(config)

        # --- apply defaults ---
        now = now_iso()
        record: Dict[str, Any] = {
            "id": crumb_id,
            "type": payload.get("type", "task"),
            "title": payload.get("title", ""),
            "status": payload.get("status", "open"),
            "priority": payload.get("priority", config.get("default_priority", "P2")),
            "created_at": payload.get("created_at", now),
            "updated_at": payload.get("updated_at", now),
        }
        # Carry over any additional fields from payload
        for key, value in payload.items():
            if key not in record:
                record[key] = value

        # --- validate ---
        if record["status"] not in VALID_STATUSES:
            die(f"invalid status '{record['status']}'; must be one of {VALID_STATUSES}")
        if record["priority"] not in VALID_PRIORITIES:
            die(f"invalid priority '{record['priority']}'; must be one of {VALID_PRIORITIES}")
        if record["type"] not in VALID_TYPES:
            die(f"invalid type '{record['type']}'; must be one of {VALID_TYPES}")

        tasks.append(record)

        # Ensure the parent directory exists (handles first-time init)
        path.parent.mkdir(parents=True, exist_ok=True)
        write_tasks(path, tasks)

    print(f"created {crumb_id}")


def cmd_update(args: argparse.Namespace) -> None:
    """Update crumb fields or append a note.

    Handles --status, --title, --priority, --description, and --note.
    Attempting to set status to a value that requires a special transition
    (e.g. closed -> in_progress) exits 1 with guidance.

    Args:
        args: Parsed arguments; args.id is the target crumb ID.
    """
    with FileLock():
        path = require_tasks_jsonl()
        tasks = read_tasks(path)

        crumb = _find_crumb(tasks, args.id)
        if crumb is None:
            die(f"crumb '{args.id}' not found")

        changed = False

        # --- status transition guard ---
        if args.status is not None:
            current_status = crumb.get("status", "open")
            if current_status == "closed":
                die(
                    f"cannot transition from 'closed' to '{args.status}'. "
                    f"Use 'crumb reopen {args.id}' to reopen first."
                )
            if current_status == "in_progress" and args.status == "open":
                print(
                    f"warning: unclaiming '{args.id}' (transitioning from "
                    f"in_progress to open)",
                    file=sys.stderr,
                )
            if crumb.get("status") != args.status:
                crumb["status"] = args.status
                changed = True

        # --- scalar field updates ---
        if args.title is not None:
            if crumb.get("title") != args.title:
                crumb["title"] = args.title
                changed = True

        if args.priority is not None:
            if crumb.get("priority") != args.priority:
                crumb["priority"] = args.priority
                changed = True

        if args.description is not None:
            if crumb.get("description") != args.description:
                crumb["description"] = args.description
                changed = True

        # --- partial JSON merge ---
        if getattr(args, "from_json", None) is not None:
            try:
                extra: Dict[str, Any] = json.loads(args.from_json)
            except json.JSONDecodeError as exc:
                die(f"invalid JSON in --from-json: {exc}")
            if not isinstance(extra, dict):
                die("--from-json must be a JSON object, not a list or scalar")
            # Merge fields; skip protected keys that have dedicated flags or
            # guarded transitions.  "status" must go through --status (which
            # enforces the closed→open gate).  "closed_at" is managed by
            # close/reopen and must not be set directly.
            protected = {"id", "created_at", "status", "closed_at"}
            for key, value in extra.items():
                if key in protected:
                    continue
                if isinstance(value, dict) and isinstance(crumb.get(key), dict):
                    crumb[key].update(value)
                else:
                    crumb[key] = value
            changed = True

        # --- note append ---
        if args.note is not None:
            timestamp = now_iso()
            note_entry = f"{timestamp}: {args.note}"
            notes: List[Any] = crumb.get("notes") or []
            if not isinstance(notes, list):
                notes = [notes]
            notes.append(note_entry)
            crumb["notes"] = notes
            changed = True

        if not changed:
            print(f"no changes to {args.id}")
            return

        crumb["updated_at"] = now_iso()
        write_tasks(path, tasks)

    print(f"updated {args.id}")


def cmd_close(args: argparse.Namespace) -> None:
    """Close one or more crumbs, stamping closed_at on each.

    Already-closed crumbs are silently skipped (idempotent). Each ID
    is resolved independently; an unknown ID exits 1 immediately.

    Args:
        args: Parsed arguments; args.ids is the list of crumb IDs to close.
    """
    with FileLock():
        path = require_tasks_jsonl()
        tasks = read_tasks(path)

        # Pre-validate all IDs exist before mutating any
        for crumb_id in args.ids:
            if _find_crumb(tasks, crumb_id) is None:
                die(f"crumb '{crumb_id}' not found")

        closed: List[str] = []
        skipped: List[str] = []

        for crumb_id in args.ids:
            crumb = _find_crumb(tasks, crumb_id)

            if crumb.get("status") == "closed":
                skipped.append(crumb_id)
                continue

            now = now_iso()
            crumb["status"] = "closed"
            crumb["closed_at"] = now
            crumb["updated_at"] = now
            closed.append(crumb_id)

        if closed:
            write_tasks(path, tasks)
            # Auto-close any parent trail whose last open child just closed
            for crumb_id in closed:
                _auto_close_trail_if_complete(tasks, path, crumb_id)

    for crumb_id in closed:
        print(f"closed {crumb_id}")
    for crumb_id in skipped:
        print(f"{crumb_id} already closed")


def cmd_reopen(args: argparse.Namespace) -> None:
    """Reopen a closed crumb, restoring status to open and clearing closed_at.

    Args:
        args: Parsed arguments; args.id is the target crumb ID.
    """
    with FileLock():
        path = require_tasks_jsonl()
        tasks = read_tasks(path)

        crumb = _find_crumb(tasks, args.id)
        if crumb is None:
            die(f"crumb '{args.id}' not found")

        if crumb.get("status") != "closed":
            current = crumb.get("status", "open")
            die(f"crumb '{args.id}' is not closed (current status: '{current}')")

        now = now_iso()
        crumb["status"] = "open"
        crumb.pop("closed_at", None)
        crumb["updated_at"] = now
        write_tasks(path, tasks)

    print(f"reopened {args.id}")


def _get_blocked_by(crumb: Dict[str, Any]) -> List[str]:
    """Return the blocked_by list for a crumb, checking both top-level and links.

    The blocked_by list may live at crumb["blocked_by"] (direct field) or
    crumb["links"]["blocked_by"] (set by cmd_link). Both locations are
    checked and merged to handle records created via --from-json or link.

    Args:
        crumb: A crumb record dict.

    Returns:
        List of blocker ID strings (may be empty).
    """
    top_level: List[str] = crumb.get("blocked_by") or []
    if not isinstance(top_level, list):
        top_level = [top_level] if top_level else []

    links_raw = crumb.get("links") or {}
    links_dict: Dict[str, Any] = links_raw if isinstance(links_raw, dict) else {}
    links_level: List[str] = links_dict.get("blocked_by") or []
    if not isinstance(links_level, list):
        links_level = [links_level] if links_level else []

    # Merge both locations, deduplicated, preserving order
    merged: List[str] = []
    for bid in top_level + links_level:
        if bid not in merged:
            merged.append(bid)
    return merged


def _is_crumb_blocked(
    crumb: Dict[str, Any], id_to_record: Dict[str, Dict[str, Any]]
) -> bool:
    """Return True if crumb has at least one unresolved blocker.

    A blocker is unresolved when its ID exists in id_to_record AND its
    status is not 'closed'. Blockers that reference non-existent IDs are
    treated as resolved (returns False contribution).

    Args:
        crumb: The crumb to evaluate.
        id_to_record: Mapping of ID string to record dict for all tasks.

    Returns:
        True if at least one blocker is unresolved; False otherwise.
    """
    for bid in _get_blocked_by(crumb):
        blocker = id_to_record.get(bid)
        if blocker is not None and blocker.get("status") != "closed":
            return True
    return False


def cmd_ready(args: argparse.Namespace) -> None:
    """List open crumbs with no unresolved blockers.

    A crumb is ready when its status is 'open' AND every entry in its
    blocked_by list either does not exist or refers to a closed crumb.
    Supports --limit and --sort flags matching cmd_list behaviour.

    Args:
        args: Parsed arguments; args.limit and args.sort are optional.
    """
    path = require_tasks_jsonl()
    tasks = read_tasks(path)

    # Build fast lookup dict for blocker resolution
    id_to_record: Dict[str, Dict[str, Any]] = {
        t["id"]: t for t in tasks if "id" in t
    }

    # Only status=="open" crumbs are included; in_progress crumbs are
    # intentionally excluded — they've already been claimed by an agent.
    results = [
        t
        for t in tasks
        if t.get("status") == "open"
        and t.get("type") != "trail"
        and not _is_crumb_blocked(t, id_to_record)
    ]

    # --- sort ---
    sort_field = getattr(args, "sort", "created_at")
    if sort_field == "priority":
        results.sort(key=lambda t: _priority_sort_key(t.get("priority", "P4")))
    elif sort_field == "status":
        results.sort(key=lambda t: _status_sort_key(t.get("status", "")))
    else:
        results.sort(key=lambda t: t.get("created_at") or "")

    # --- limit ---
    limit = getattr(args, "limit", None)
    if limit is not None and limit > 0:
        results = results[:limit]

    for t in results:
        tid = t.get("id", "?")
        title = t.get("title", "")
        status = t.get("status", "")
        priority = t.get("priority", "")
        print(f"{tid:<12} {priority:<4} {status:<12} {title}")


def cmd_blocked(args: argparse.Namespace) -> None:
    """List open crumbs with at least one unresolved blocker.

    A crumb is blocked when its status is 'open' AND at least one entry in
    its blocked_by list refers to an existing crumb whose status is not
    'closed'. Blockers referencing non-existent IDs are ignored.

    Args:
        args: Parsed arguments (no flags for blocked currently).
    """
    path = require_tasks_jsonl()
    tasks = read_tasks(path)

    # Build fast lookup dict for blocker resolution
    id_to_record: Dict[str, Dict[str, Any]] = {
        t["id"]: t for t in tasks if "id" in t
    }

    # Only status=="open" crumbs are included; in_progress crumbs are
    # intentionally excluded — they've already been claimed by an agent.
    results = [
        t
        for t in tasks
        if t.get("status") == "open"
        and t.get("type") != "trail"
        and _is_crumb_blocked(t, id_to_record)
    ]

    results.sort(key=lambda t: t.get("created_at") or "")

    for t in results:
        tid = t.get("id", "?")
        title = t.get("title", "")
        status = t.get("status", "")
        priority = t.get("priority", "")
        print(f"{tid:<12} {priority:<4} {status:<12} {title}")


def cmd_link(args: argparse.Namespace) -> None:
    """Manage crumb links: parent, blocked_by, and discovered_from.

    Multiple flags can be combined in a single invocation. Dangling
    references are allowed — the doctor command validates referential
    integrity.

    Args:
        args: Parsed arguments; args.id is the target crumb ID.
            args.link_parent: Set the parent trail link.
            args.blocked_by: Append to the blocked_by array.
            args.remove_blocked_by: Remove from the blocked_by array.
            args.discovered_from: Set the discovered_from provenance.
    """
    with FileLock():
        path = require_tasks_jsonl()
        tasks = read_tasks(path)

        crumb = _find_crumb(tasks, args.id)
        if crumb is None:
            die(f"crumb '{args.id}' not found")

        # Ensure the links sub-dict exists
        links: Dict[str, Any] = crumb.get("links") or {}
        if not isinstance(links, dict):
            links = {}

        changed = False

        # --- --parent: set or replace the parent trail link ---
        if args.link_parent is not None:
            if links.get("parent") != args.link_parent:
                links["parent"] = args.link_parent
                changed = True

        # --- --blocked-by: append without duplicates ---
        if args.blocked_by is not None:
            blocked: List[str] = links.get("blocked_by") or []
            if not isinstance(blocked, list):
                blocked = [blocked]
            if args.blocked_by not in blocked:
                blocked.append(args.blocked_by)
                links["blocked_by"] = blocked
                changed = True

        # --- --remove-blocked-by: remove from blocked_by array ---
        if args.remove_blocked_by is not None:
            blocked_existing: List[str] = links.get("blocked_by") or []
            if not isinstance(blocked_existing, list):
                blocked_existing = [blocked_existing]
            if args.remove_blocked_by in blocked_existing:
                blocked_existing = [
                    bid for bid in blocked_existing if bid != args.remove_blocked_by
                ]
                links["blocked_by"] = blocked_existing
                changed = True

        # --- --discovered-from: set or replace the provenance link ---
        if args.discovered_from is not None:
            if links.get("discovered_from") != args.discovered_from:
                links["discovered_from"] = args.discovered_from
                changed = True

        if not changed:
            print(f"no link changes to {args.id}")
            return

        crumb["links"] = links
        crumb["updated_at"] = now_iso()
        write_tasks(path, tasks)
        # Auto-reopen any closed parent trail when a new open crumb links to it
        if args.link_parent is not None:
            _auto_reopen_trail_if_needed(
                tasks, path, args.link_parent, crumb.get("status", "open")
            )

    print(f"updated links for {args.id}")


def cmd_search(args: argparse.Namespace) -> None:
    """Case-insensitive full-text search across crumb and trail titles and descriptions.

    Matches the query string against each record's title and description fields
    using str.lower() comparison. Prints one line per matching record using
    the same format as cmd_list. Empty results produce no output and exit 0.

    Args:
        args: Parsed arguments; args.query is the search string.
    """
    path = require_tasks_jsonl()
    tasks = read_tasks(path)

    query_lower = args.query.lower()

    results = [
        t
        for t in tasks
        if query_lower in (t.get("title") or "").lower()
        or query_lower in (t.get("description") or "").lower()
    ]

    for t in results:
        tid = t.get("id", "?")
        title = t.get("title", "")
        status = t.get("status", "")
        priority = t.get("priority", "")
        print(f"{tid:<12} {priority:<4} {status:<12} {title}")


def cmd_trail(args: argparse.Namespace) -> None:
    """Trail subcommands: list, show, create, close.

    Dispatches on args.trail_command. Trails are tasks.jsonl records
    with type='trail' and T-prefixed IDs (e.g., AF-T1).

    Args:
        args: Parsed arguments; args.trail_command is the sub-subcommand.
    """
    trail_cmd = getattr(args, "trail_command", None)

    if trail_cmd == "create":
        _cmd_trail_create(args)
    elif trail_cmd == "show":
        _cmd_trail_show(args)
    elif trail_cmd == "list":
        _cmd_trail_list(args)
    elif trail_cmd == "close":
        _cmd_trail_close(args)
    else:
        die("usage: crumb trail <list|show|create|close>")


def _cmd_trail_create(args: argparse.Namespace) -> None:
    """Create a new trail record with an AF-T{n} auto-ID.

    Reads next_trail_id from config.json, builds the trail record,
    appends it to tasks.jsonl, and increments the counter.

    Args:
        args: Parsed arguments; args.title is required.
    """
    with FileLock():
        path = tasks_path()
        if path.exists():
            tasks = read_tasks(path)
        else:
            tasks = []

        config = read_config()
        prefix = config["prefix"]
        next_trail_id = int(config.get("next_trail_id", 1))
        trail_id = f"{prefix}-T{next_trail_id}"
        # Ensure no collision (defensive)
        while _find_crumb(tasks, trail_id) is not None:
            next_trail_id += 1
            trail_id = f"{prefix}-T{next_trail_id}"
        config["next_trail_id"] = next_trail_id + 1
        write_config(config)

        now = now_iso()
        record: Dict[str, Any] = {
            "id": trail_id,
            "type": "trail",
            "title": args.title,
            "status": "open",
            "priority": args.priority or config.get("default_priority", "P2"),
            "created_at": now,
            "updated_at": now,
        }
        if args.description:
            record["description"] = args.description
        if args.acceptance_criteria:
            record["acceptance_criteria"] = args.acceptance_criteria

        path.parent.mkdir(parents=True, exist_ok=True)
        tasks.append(record)
        write_tasks(path, tasks)

    print(f"created {trail_id}")


def _cmd_trail_show(args: argparse.Namespace) -> None:
    """Show trail fields and its child crumbs.

    Args:
        args: Parsed arguments; args.id is the trail ID.
    """
    path = require_tasks_jsonl()
    tasks = read_tasks(path)

    trail = _find_crumb(tasks, args.id)
    if trail is None:
        die(f"trail '{args.id}' not found")
    if trail.get("type") != "trail":
        die(f"'{args.id}' is not a trail")

    # Print trail fields
    fields = [
        ("id", "ID"),
        ("type", "Type"),
        ("title", "Title"),
        ("status", "Status"),
        ("priority", "Priority"),
        ("description", "Description"),
        ("acceptance_criteria", "Acceptance Criteria"),
        ("created_at", "Created At"),
        ("updated_at", "Updated At"),
        ("closed_at", "Closed At"),
    ]
    for key, label in fields:
        value = trail.get(key)
        if value is None or value == "" or value == [] or value == {}:
            continue
        if isinstance(value, list):
            print(f"{label}:")
            for item in value:
                print(f"  - {item}")
        else:
            print(f"{label}: {value}")

    # Print child crumbs
    children = _get_trail_children(tasks, args.id)
    total = len(children)
    closed_count = sum(1 for c in children if c.get("status") == "closed")
    print(f"\nChildren ({closed_count}/{total} closed):")
    if not children:
        print("  (none)")
    else:
        for child in children:
            cid = child.get("id", "?")
            title = child.get("title", "")
            status = child.get("status", "")
            priority = child.get("priority", "")
            print(f"  {cid:<12} {priority:<4} {status:<12} {title}")


def _cmd_trail_list(args: argparse.Namespace) -> None:
    """List all trails with completion counts (X/Y closed).

    Args:
        args: Parsed arguments (no additional flags for trail list).
    """
    path = require_tasks_jsonl()
    tasks = read_tasks(path)

    trails = [t for t in tasks if t.get("type") == "trail"]
    if not trails:
        print("no trails found")
        return

    for trail in trails:
        trail_id = trail.get("id", "?")
        title = trail.get("title", "")
        status = trail.get("status", "")
        priority = trail.get("priority", "")
        children = _get_trail_children(tasks, trail_id)
        total = len(children)
        closed_count = sum(1 for c in children if c.get("status") == "closed")
        completion = f"{closed_count}/{total} closed"
        print(f"{trail_id:<12} {priority:<4} {status:<12} {completion:<16} {title}")


def _cmd_trail_close(args: argparse.Namespace) -> None:
    """Close a trail, rejecting if any children are still open.

    Exits 1 with stderr listing open children if any exist.

    Args:
        args: Parsed arguments; args.id is the trail ID.
    """
    with FileLock():
        path = require_tasks_jsonl()
        tasks = read_tasks(path)

        trail = _find_crumb(tasks, args.id)
        if trail is None:
            die(f"trail '{args.id}' not found")
        if trail.get("type") != "trail":
            die(f"'{args.id}' is not a trail")

        if trail.get("status") == "closed":
            print(f"{args.id} already closed")
            return

        children = _get_trail_children(tasks, args.id)
        open_children = [
            c for c in children if c.get("status") != "closed"
        ]
        if open_children:
            lines = [f"cannot close trail '{args.id}': {len(open_children)} open child(ren):"]
            for child in open_children:
                cid = child.get("id", "?")
                title = child.get("title", "")
                status = child.get("status", "")
                lines.append(f"  {cid}  {status}  {title}")
            die("\n".join(lines))

        now = now_iso()
        trail["status"] = "closed"
        trail["closed_at"] = now
        trail["updated_at"] = now
        write_tasks(path, tasks)

    print(f"closed {args.id}")


def cmd_tree(args: argparse.Namespace) -> None:
    """Display trail/crumb hierarchy as an indented tree.

    Without an ID argument: shows all trails followed by their child crumbs
    (indented by 2 spaces), then orphan crumbs (no parent trail) at the end.
    With an ID argument: shows only the specified trail and its children;
    exits 1 if the ID is not found or is not a trail.

    Args:
        args: Parsed arguments; args.id is the optional trail ID to scope to.
    """
    path = require_tasks_jsonl()
    tasks = read_tasks(path)

    trail_id_filter: Optional[str] = getattr(args, "id", None)

    if trail_id_filter is not None:
        # Scoped to a single trail
        trail = _find_crumb(tasks, trail_id_filter)
        if trail is None:
            die(f"trail '{trail_id_filter}' not found")
        if trail.get("type") != "trail":
            die(f"'{trail_id_filter}' is not a trail")

        tid = trail.get("id", "?")
        title = trail.get("title", "")
        status = trail.get("status", "")
        priority = trail.get("priority", "")
        print(f"{tid:<12} {priority:<4} {status:<12} {title}")

        children = _get_trail_children(tasks, trail_id_filter)
        for child in children:
            cid = child.get("id", "?")
            ctitle = child.get("title", "")
            cstatus = child.get("status", "")
            cpriority = child.get("priority", "")
            print(f"  {cid:<10} {cpriority:<4} {cstatus:<12} {ctitle}")
        return

    # Full tree: all trails with children, then orphans
    trails = [t for t in tasks if t.get("type") == "trail"]
    # Build set of IDs claimed by trails (children are those with links.parent)
    all_trail_ids = {t.get("id") for t in trails if t.get("id")}

    # Collect all non-trail records and find orphans
    non_trails = [t for t in tasks if t.get("type") != "trail"]

    # Build a set of non-trail IDs that have a valid parent link
    child_ids: set = set()

    for trail in trails:
        tid = trail.get("id", "?")
        title = trail.get("title", "")
        status = trail.get("status", "")
        priority = trail.get("priority", "")
        print(f"{tid:<12} {priority:<4} {status:<12} {title}")

        children = _get_trail_children(tasks, tid)
        for child in children:
            cid = child.get("id", "?")
            ctitle = child.get("title", "")
            cstatus = child.get("status", "")
            cpriority = child.get("priority", "")
            print(f"  {cid:<10} {cpriority:<4} {cstatus:<12} {ctitle}")
            child_ids.add(cid)

    # Print orphan crumbs (non-trail, no valid parent link)
    orphans = [
        t for t in non_trails
        if t.get("id") not in child_ids
    ]
    if orphans:
        print("(orphans)")
        for t in orphans:
            tid = t.get("id", "?")
            title = t.get("title", "")
            status = t.get("status", "")
            priority = t.get("priority", "")
            print(f"  {tid:<10} {priority:<4} {status:<12} {title}")


_BEADS_PRIORITY_MAP: Dict[int, str] = {
    0: "P0",
    1: "P1",
    2: "P2",
    3: "P3",
    4: "P4",
}

_BEADS_STATUS_MAP: Dict[str, str] = {
    "open": "open",
    "in_progress": "in_progress",
    "closed": "closed",
}


def _convert_beads_record(
    beads_rec: Dict[str, Any],
    epic_id_map: Dict[str, str],
    config: Dict[str, Any],
) -> Dict[str, Any]:
    """Convert a single Beads issue record to crumb format.

    Args:
        beads_rec: A single record from Beads issues.jsonl.
        epic_id_map: Maps Beads epic IDs to their generated trail IDs.
        config: Current config dict (may be mutated to advance next_trail_id).

    Returns:
        A crumb-format record dict.
    """
    beads_id: str = beads_rec.get("id", "")
    issue_type: str = beads_rec.get("issue_type", "task")
    is_epic = issue_type == "epic"

    # --- type mapping ---
    # Beads epics become crumb trails; task/bug/feature map directly;
    # any unrecognised Beads type falls back to "task".
    if is_epic:
        crumb_type = "trail"
    elif issue_type in ("task", "bug", "feature"):
        crumb_type = issue_type
    else:
        crumb_type = "task"

    # --- ID assignment ---
    # Epics get new T-prefixed trail IDs (AF-T1, AF-T2, …) from the running
    # counter in config.  The mapping from old Beads epic ID → new trail ID
    # is stored in epic_id_map so that child records can resolve their parent
    # link in the post-pass (_resolve_beads_epic_refs).
    # Non-epic records keep their existing Beads IDs unchanged.
    if is_epic:
        prefix = config["prefix"]
        next_tid = int(config.get("next_trail_id", 1))
        trail_id = f"{prefix}-T{next_tid}"
        config["next_trail_id"] = next_tid + 1  # advance counter (mutates config in-place)
        epic_id_map[beads_id] = trail_id  # register mapping for post-pass
        crumb_id = trail_id
    else:
        crumb_id = beads_id

    # --- priority mapping ---
    # Beads stores priority as an integer (0 = highest) or as a P-string.
    # Convert integer to P-string via lookup table; pass through valid P-strings
    # unchanged; default to config's default_priority if neither applies.
    raw_priority = beads_rec.get("priority")
    if isinstance(raw_priority, int) and raw_priority in _BEADS_PRIORITY_MAP:
        priority = _BEADS_PRIORITY_MAP[raw_priority]
    elif isinstance(raw_priority, str) and raw_priority in VALID_PRIORITIES:
        priority = raw_priority  # already in crumb format
    else:
        priority = config.get("default_priority", "P2")  # unknown — use project default

    # --- status mapping ---
    # Beads and crumb share the same status vocabulary, so this is a passthrough
    # with a safe default of "open" for any unrecognised value.
    raw_status = beads_rec.get("status", "open")
    status = _BEADS_STATUS_MAP.get(raw_status, "open")

    now = now_iso()
    record: Dict[str, Any] = {
        "id": crumb_id,
        "type": crumb_type,
        "title": beads_rec.get("title", ""),
        "status": status,
        "priority": priority,
        # Preserve original timestamps; fall back to current time if absent
        "created_at": beads_rec.get("created_at", now),
        "updated_at": beads_rec.get("updated_at", now),
    }

    # Optional fields: only include in output record if present in source
    if beads_rec.get("description"):
        record["description"] = beads_rec["description"]
    if beads_rec.get("closed_at"):
        record["closed_at"] = beads_rec["closed_at"]

    # --- dependency mapping (first pass: parent-child only) ---
    # Scan each Beads dependency entry.  "parent-child" deps set links.parent.
    # "blocks" deps are intentionally deferred to _apply_blocks_deps because
    # target records may not have been converted yet at this point in the loop.
    deps: List[Dict[str, Any]] = beads_rec.get("dependencies") or []
    if isinstance(deps, list) and deps:
        parent_id: Optional[str] = None
        for dep in deps:
            if not isinstance(dep, dict):
                continue
            dep_type = dep.get("type", "")
            depends_on = dep.get("depends_on_id", "")
            if dep_type == "parent-child" and depends_on:
                # This record is a child of depends_on (epic/trail).
                # If multiple parent-child deps exist, last one wins (intentional).
                parent_id = dep.get("depends_on_id", "")
            # "blocks" deps are handled by _apply_blocks_deps post-pass

        links: Dict[str, Any] = {}
        if parent_id:
            # Store raw Beads parent ID here; _resolve_beads_epic_refs will
            # rewrite it to the generated trail ID if parent was an epic.
            links["parent"] = parent_id
        if links:
            record["links"] = links

    return record


def _resolve_beads_epic_refs(
    records: List[Dict[str, Any]], epic_id_map: Dict[str, str]
) -> None:
    """Update links in records to replace Beads epic IDs with trail IDs.

    Called after all records are converted so epic_id_map is fully populated.
    Mutates records in-place.

    Args:
        records: List of converted crumb records.
        epic_id_map: Maps Beads epic ID → generated trail ID.
    """
    for record in records:
        links = record.get("links")
        if not isinstance(links, dict):
            continue  # no links to rewrite on this record

        # Rewrite links.parent: if the stored value is a Beads epic ID,
        # replace it with the generated trail ID (e.g. "BD-42" → "AF-T3").
        # IDs that are already crumb IDs (non-epics) are not in epic_id_map
        # and pass through unchanged.
        parent = links.get("parent")
        if parent and parent in epic_id_map:
            links["parent"] = epic_id_map[parent]

        # Rewrite each entry in links.blocked_by the same way.
        # epic_id_map.get(bid, bid) returns the mapped trail ID if the
        # blocker was an epic, or the original ID otherwise.
        blocked_by: List[str] = links.get("blocked_by") or []
        if isinstance(blocked_by, list) and blocked_by:
            links["blocked_by"] = [
                epic_id_map.get(bid, bid) for bid in blocked_by
            ]


def _apply_blocks_deps(
    raw_beads: List[Dict[str, Any]],
    records: List[Dict[str, Any]],
    epic_id_map: Dict[str, str],
) -> None:
    """Apply blocks-type dependencies to the correct target records.

    A Beads dep {issue_id: A, depends_on_id: B, type: "blocks"} means
    "A blocks B", so B's links.blocked_by should contain A (not A's).
    Mutates records in-place.

    Args:
        raw_beads: Original Beads records (used to read dependency lists).
        records: List of converted crumb records to mutate.
        epic_id_map: Maps Beads epic ID → generated trail ID.
    """
    # Build a fast O(1) lookup from crumb ID → converted record so we can
    # mutate target records directly when we find a "blocks" relationship.
    record_index: Dict[str, Dict[str, Any]] = {
        r["id"]: r for r in records if r.get("id")
    }

    # Build a translation table from every Beads ID to its crumb ID.
    # For epics this uses the generated trail ID from epic_id_map;
    # for all other records the Beads ID and crumb ID are identical.
    beads_id_to_crumb_id: Dict[str, str] = {}
    for beads_rec in raw_beads:
        beads_id = beads_rec.get("id", "")
        if beads_id in epic_id_map:
            beads_id_to_crumb_id[beads_id] = epic_id_map[beads_id]  # epic → trail ID
        else:
            beads_id_to_crumb_id[beads_id] = beads_id  # non-epic: ID unchanged

    # Walk every raw Beads record and look for "blocks" dependencies.
    # Beads semantics: dep {issue_id: A, depends_on_id: B, type: "blocks"}
    # means "A blocks B", so we append A's crumb ID to B's blocked_by list.
    for beads_rec in raw_beads:
        source_beads_id = beads_rec.get("id", "")
        # Translate the blocking issue's Beads ID to its crumb ID
        source_crumb_id = beads_id_to_crumb_id.get(source_beads_id, source_beads_id)
        deps: List[Dict[str, Any]] = beads_rec.get("dependencies") or []
        if not isinstance(deps, list):
            continue
        for dep in deps:
            if not isinstance(dep, dict):
                continue
            if dep.get("type") != "blocks":
                continue  # skip parent-child and any other dep types
            target_beads_id = dep.get("depends_on_id", "")
            if not target_beads_id:
                continue  # malformed dep entry; skip
            # Translate the blocked issue's Beads ID to its crumb ID
            target_crumb_id = beads_id_to_crumb_id.get(target_beads_id, target_beads_id)
            target_record = record_index.get(target_crumb_id)
            if target_record is None:
                print(
                    f"warning: blocks dep from '{source_crumb_id}' targets "
                    f"'{target_crumb_id}' which is not in the converted set — skipping",
                    file=sys.stderr,
                )
                continue  # target not in converted set (e.g. skipped as duplicate)
            # Append source to target's blocked_by list (no duplicates)
            links = target_record.setdefault("links", {})
            blocked_by: List[str] = links.setdefault("blocked_by", [])
            if source_crumb_id not in blocked_by:
                blocked_by.append(source_crumb_id)


def cmd_import(args: argparse.Namespace) -> None:
    """Import crumbs from a JSONL file, with optional Beads format migration.

    Plain mode: reads the file line-by-line, skips malformed JSON (with
    warning), skips duplicate IDs (with warning), appends valid entries to
    tasks.jsonl. Updates config counters after import.

    Beads mode (--from-beads): converts Beads issues.jsonl format to crumb
    format. Priority integers map to P0-P4. Type 'epic' becomes 'trail'
    with a T-prefixed ID. Dependencies are mapped to links.parent /
    links.blocked_by.

    Args:
        args: Parsed arguments; args.file is the input path,
              args.from_beads enables Beads migration mode.
    """
    import_path = Path(args.file)
    if not import_path.exists():
        die(f"file not found: {import_path}")
    if import_path.is_dir():
        die(f"path is a directory, not a file: {import_path}")

    with FileLock():
        path = tasks_path()
        if path.exists():
            existing_tasks = read_tasks(path)
        else:
            existing_tasks = []
            path.parent.mkdir(parents=True, exist_ok=True)

        existing_ids: set = {t.get("id") for t in existing_tasks if t.get("id")}
        config = read_config()

        imported_count = 0
        skipped_malformed = 0
        skipped_duplicate = 0

        if getattr(args, "from_beads", False):
            # --- Beads migration mode ---
            # Two-pass: first collect all records, then resolve epic refs
            raw_beads: List[Dict[str, Any]] = []
            try:
                with open(import_path, "r", encoding="utf-8") as fh:
                    for lineno, line in enumerate(fh, start=1):
                        line = line.rstrip("\n")
                        if not line:
                            continue
                        try:
                            raw_beads.append(json.loads(line))
                        except json.JSONDecodeError as exc:
                            print(
                                f"warning: skipping malformed JSON on line {lineno}: {exc}",
                                file=sys.stderr,
                            )
                            skipped_malformed += 1
            except OSError as exc:
                die(f"cannot read {import_path}: {exc}")

            # Sort epics first so epic_id_map is populated before children
            epic_id_map: Dict[str, str] = {}
            epics = [r for r in raw_beads if r.get("issue_type") == "epic"]
            non_epics = [r for r in raw_beads if r.get("issue_type") != "epic"]

            converted: List[Dict[str, Any]] = []
            for beads_rec in epics + non_epics:
                record = _convert_beads_record(beads_rec, epic_id_map, config)
                crumb_id = record.get("id", "")
                if crumb_id in existing_ids:
                    print(
                        f"warning: skipping duplicate ID '{crumb_id}'",
                        file=sys.stderr,
                    )
                    skipped_duplicate += 1
                    continue
                existing_ids.add(crumb_id)
                converted.append(record)

            # Resolve epic ID references after all records are converted
            _resolve_beads_epic_refs(converted, epic_id_map)
            # Apply blocks deps in reverse: A blocks B → B.blocked_by = [A]
            _apply_blocks_deps(raw_beads, converted, epic_id_map)

            existing_tasks.extend(converted)
            imported_count = len(converted)

        else:
            # --- Plain JSONL import mode ---
            try:
                with open(import_path, "r", encoding="utf-8") as fh:
                    for lineno, line in enumerate(fh, start=1):
                        line = line.rstrip("\n")
                        if not line:
                            continue
                        try:
                            record: Dict[str, Any] = json.loads(line)
                        except json.JSONDecodeError as exc:
                            print(
                                f"warning: skipping malformed JSON on line {lineno}: {exc}",
                                file=sys.stderr,
                            )
                            skipped_malformed += 1
                            continue

                        crumb_id = record.get("id", "")
                        if not crumb_id:
                            print(
                                f"warning: skipping record on line {lineno}: missing 'id' field",
                                file=sys.stderr,
                            )
                            skipped_malformed += 1
                            continue

                        if crumb_id in existing_ids:
                            print(
                                f"warning: skipping duplicate ID '{crumb_id}' on line {lineno}",
                                file=sys.stderr,
                            )
                            skipped_duplicate += 1
                            continue

                        existing_ids.add(crumb_id)
                        existing_tasks.append(record)
                        imported_count += 1
            except OSError as exc:
                die(f"cannot read {import_path}: {exc}")

        # --- Update config counters to exceed highest imported numeric ID ---
        # Clamp to 0 so corrupt config values (e.g. 0 or missing) cannot
        # produce a negative starting point.
        max_crumb_num = max(0, int(config.get("next_crumb_id", 1)) - 1)
        max_trail_num = max(0, int(config.get("next_trail_id", 1)) - 1)
        prefix = config["prefix"]
        prefix_dash = f"{prefix}-"
        prefix_trail = f"{prefix}-T"

        for task in existing_tasks:
            tid = task.get("id", "")
            if not tid:
                continue
            if tid.startswith(prefix_trail):
                try:
                    num = int(tid[len(prefix_trail):])
                    if num > max_trail_num:
                        max_trail_num = num
                except ValueError:
                    pass
            elif tid.startswith(prefix_dash):
                suffix = tid[len(prefix_dash):]
                try:
                    num = int(suffix)
                    if num > max_crumb_num:
                        max_crumb_num = num
                except ValueError:
                    pass

        config["next_crumb_id"] = max_crumb_num + 1
        config["next_trail_id"] = max_trail_num + 1

        if imported_count > 0:
            write_tasks(path, existing_tasks)
        # Always write config: counters are updated above regardless of
        # imported_count, and must be persisted even when all records were
        # duplicates or the file contained only malformed lines.
        write_config(config)

    print(
        f"imported {imported_count} record(s)"
        + (f", skipped {skipped_malformed} malformed" if skipped_malformed else "")
        + (f", skipped {skipped_duplicate} duplicate(s)" if skipped_duplicate else "")
    )


def cmd_doctor(args: argparse.Namespace) -> None:
    """Validate tasks.jsonl integrity and optionally repair issues.

    Checks performed:
    - Malformed JSON lines (reported with line numbers)
    - Duplicate IDs (error)
    - Dangling parent links (pointing to non-existent or non-trail IDs — error)
    - Dangling blocked_by references (pointing to non-existent IDs — warning)
    - Orphan crumbs (non-trail records with no parent — warning)

    With --fix, removes dangling blocked_by references atomically.
    Note: --fix is an implementation extension not documented in the
    design spec; the spec says "optionally auto-repairs" without naming
    the flag.

    Exit code: 0 if no errors (warnings alone do not set exit code 1);
               1 if any errors are found.

    Args:
        args: Parsed arguments; args.fix enables auto-repair.
    """
    path = require_tasks_jsonl()

    errors: List[str] = []
    warnings: List[str] = []
    fixes_applied: List[str] = []

    with FileLock():
        # --- Pass 1: raw line-by-line read for malformed JSON detection ---
        valid_records: List[Dict[str, Any]] = []
        malformed_lines: List[int] = []
        try:
            with open(path, "r", encoding="utf-8") as fh:
                for lineno, raw_line in enumerate(fh, start=1):
                    line = raw_line.rstrip("\n")
                    if not line:
                        continue
                    try:
                        record = json.loads(line)
                        valid_records.append(record)
                    except json.JSONDecodeError as exc:
                        malformed_lines.append(lineno)
                        errors.append(f"line {lineno}: malformed JSON — {exc}")
        except OSError as exc:
            die(f"cannot read tasks.jsonl: {exc}")

        # --- Build lookup structures from valid records ---
        seen_ids: Dict[str, int] = {}  # id -> first occurrence index
        id_to_record: Dict[str, Dict[str, Any]] = {}

        for idx, record in enumerate(valid_records):
            rec_id = record.get("id")
            if not rec_id:
                continue
            if rec_id in seen_ids:
                errors.append(
                    f"duplicate ID '{rec_id}' (first at record {seen_ids[rec_id] + 1}, "
                    f"again at record {idx + 1})"
                )
            else:
                seen_ids[rec_id] = idx
                id_to_record[rec_id] = record

        # Build set of all trail IDs for parent validation
        trail_ids: set = {
            rid for rid, rec in id_to_record.items() if rec.get("type") == "trail"
        }

        # --- Pass 2: semantic checks on valid records ---
        for record in valid_records:
            rec_id = record.get("id", "<unknown>")
            rec_type = record.get("type", "")

            # Skip trails for orphan and parent checks (trails have no parent)
            if rec_type != "trail":
                # Resolve parent exclusively from links.parent (canonical field)
                links_raw = record.get("links") or {}
                parent_id = (
                    links_raw.get("parent") or ""
                    if isinstance(links_raw, dict)
                    else ""
                )

                if parent_id:
                    # Dangling parent: parent ID doesn't exist or isn't a trail
                    if parent_id not in id_to_record:
                        errors.append(
                            f"'{rec_id}': dangling parent link — '{parent_id}' does not exist"
                        )
                    elif parent_id not in trail_ids:
                        errors.append(
                            f"'{rec_id}': dangling parent link — '{parent_id}' is not a trail"
                        )
                else:
                    # No parent: orphan crumb
                    warnings.append(f"'{rec_id}': orphan crumb — no parent trail")

                # Dangling blocked_by references
                blocked_by_ids = _get_blocked_by(record)
                dangling_blockers = [
                    bid for bid in blocked_by_ids if bid not in id_to_record
                ]
                for bid in dangling_blockers:
                    warnings.append(
                        f"'{rec_id}': dangling blocked_by reference — '{bid}' does not exist"
                    )

                # --- --fix: remove dangling blocked_by from this record ---
                if getattr(args, "fix", False) and dangling_blockers:
                    dangling_set = set(dangling_blockers)
                    # Remove from top-level blocked_by
                    top_blocked: List[str] = record.get("blocked_by") or []
                    if isinstance(top_blocked, list):
                        cleaned_top = [b for b in top_blocked if b not in dangling_set]
                        if len(cleaned_top) != len(top_blocked):
                            record["blocked_by"] = cleaned_top
                            fixes_applied.append(
                                f"'{rec_id}': removed dangling blocked_by {dangling_set} from top-level"
                            )
                    # Remove from links.blocked_by
                    if isinstance(record.get("links"), dict):
                        links_blocked: List[str] = record["links"].get("blocked_by") or []
                        if isinstance(links_blocked, list):
                            cleaned_links = [b for b in links_blocked if b not in dangling_set]
                            if len(cleaned_links) != len(links_blocked):
                                record["links"]["blocked_by"] = cleaned_links
                                fixes_applied.append(
                                    f"'{rec_id}': removed dangling blocked_by {dangling_set} from links"
                                )

        # --- Apply --fix writes ---
        if getattr(args, "fix", False) and fixes_applied:
            write_tasks(path, valid_records)
            for msg in fixes_applied:
                print(f"fixed: {msg}")
            if malformed_lines:
                print(
                    f"note: {len(malformed_lines)} malformed line(s) were removed "
                    f"from tasks.jsonl (lines: {malformed_lines})",
                    file=sys.stderr,
                )

    # --- Report ---
    for msg in errors:
        print(f"error: {msg}", file=sys.stderr)
    for msg in warnings:
        print(f"warning: {msg}", file=sys.stderr)

    if not errors and not warnings:
        print("No issues found")
        return

    if errors:
        sys.exit(1)


# ---------------------------------------------------------------------------
# Init subcommand — bootstrap .crumbs/ directory structure
# ---------------------------------------------------------------------------


def cmd_init(args: argparse.Namespace) -> None:
    """Bootstrap the .crumbs/ directory structure in the current directory.

    Creates the following files if they do not already exist:
      - ``.crumbs/``            — the directory itself
      - ``.crumbs/config.json`` — prefix and counter settings
      - ``.crumbs/tasks.jsonl`` — empty task store
    Also appends ``.crumbs/`` to the project ``.gitignore`` when the entry
    is not already present.

    If ``.crumbs/`` already exists this command is a no-op and exits 0 so
    it is safe to run multiple times (idempotent).

    Args:
        args: Parsed arguments.  ``args.prefix`` is the ID prefix string
            (e.g. ``"AF"``).  Defaults to ``"AF"`` when not supplied.
    """
    cwd = Path.cwd().resolve()
    crumbs = cwd / CRUMBS_DIR_NAME

    if crumbs.is_dir():
        print(f"{CRUMBS_DIR_NAME}/ already exists at {crumbs} — nothing to do.")
        return

    prefix: str = args.prefix if args.prefix else DEFAULT_CONFIG["prefix"]

    # Create .crumbs/ directory
    try:
        crumbs.mkdir(parents=False, exist_ok=False)
    except OSError as exc:
        die(f"cannot create {CRUMBS_DIR_NAME}/: {exc}")

    # Write config.json
    config: Dict[str, Any] = dict(DEFAULT_CONFIG)
    config["prefix"] = prefix
    config_file = crumbs / CONFIG_FILE
    try:
        with open(config_file, "w", encoding="utf-8") as fh:
            json.dump(config, fh, indent=2)
            fh.write("\n")
    except OSError as exc:
        die(f"cannot write {CONFIG_FILE}: {exc}")

    # Create empty tasks.jsonl
    tasks_file = crumbs / TASKS_FILE
    try:
        tasks_file.touch()
    except OSError as exc:
        die(f"cannot create {TASKS_FILE}: {exc}")

    # Add .crumbs/sessions/ to .gitignore if not already present
    gitignore = cwd / ".gitignore"
    gitignore_entry = f"{CRUMBS_DIR_NAME}/sessions/"
    try:
        existing_entries: List[str] = []
        if gitignore.exists():
            with open(gitignore, "r", encoding="utf-8") as fh:
                existing_entries = fh.read().splitlines()
        if gitignore_entry not in existing_entries:
            with open(gitignore, "a", encoding="utf-8") as fh:
                # Ensure there is a newline before our entry when the file is
                # non-empty and does not already end with one.
                if existing_entries and existing_entries[-1] != "":
                    fh.write("\n")
                fh.write(f"{gitignore_entry}\n")
            print(f"Added '{gitignore_entry}' to .gitignore")
        else:
            print(f"'.gitignore' already contains '{gitignore_entry}' — skipped")
    except OSError as exc:
        # .gitignore update is best-effort; warn but do not abort
        print(f"warning: could not update .gitignore: {exc}", file=sys.stderr)

    print(
        f"Initialised {CRUMBS_DIR_NAME}/ in {cwd}\n"
        f"  config.json  — prefix={prefix!r}\n"
        f"  tasks.jsonl  — empty task store"
    )


# ---------------------------------------------------------------------------
# render-template subcommand — single-pass {{SLOT}} expansion
# ---------------------------------------------------------------------------

#: Pattern matching a slot placeholder, e.g. ``{{COMMIT_RANGE}}``.
#: Slot names must start with an uppercase ASCII letter and contain only
#: uppercase letters, digits, and underscores — matching the convention used
#: in the orchestration templates and the shell ``fill_slot`` helper.
_SLOT_RE: re.Pattern[str] = re.compile(r"\{\{([A-Z][A-Z0-9_]*)\}\}")


def render_template(template: str, slots: Dict[str, str]) -> str:
    """Expand ``{{SLOT_NAME}}`` placeholders in *template* with values from *slots*.

    Performs a single-pass, left-to-right substitution using ``re.sub``.
    Each slot placeholder in the template is replaced with the corresponding
    string value from *slots*.  Replacement values are treated as plain text:
    if a value itself contains ``{{OTHER}}``, that inner placeholder is NOT
    expanded (single-pass guarantee).

    Validation rules (checked before any substitution takes place):
    - Every slot name found in the template must have a corresponding entry in
      *slots* — missing slots raise :class:`SystemExit` (via :func:`die`).
    - Every key in *slots* must appear at least once in the template — extra
      slots that are never used raise :class:`SystemExit` (via :func:`die`).

    Slots inside fenced code blocks (````` ``` ```) are expanded identically to
    slots anywhere else in the template — there is no block-level exclusion.

    Args:
        template: Raw template text containing zero or more ``{{SLOT_NAME}}``
            placeholders.
        slots: Mapping of slot name to replacement value.  Keys must be
            uppercase strings matching ``[A-Z][A-Z0-9_]*``.

    Returns:
        The rendered string with all placeholders replaced.

    Raises:
        SystemExit: If a template slot is missing from *slots*, or if *slots*
            contains a key that does not appear in the template.
    """
    # Collect every distinct slot name present in the template.
    template_slots: List[str] = list(dict.fromkeys(_SLOT_RE.findall(template)))

    # Validate: every template slot must have a provided value.
    for name in template_slots:
        if name not in slots:
            die(f"missing slot: {name}")

    # Validate: every provided slot must appear in the template.
    for name in slots:
        if name not in template_slots:
            die(f"extra slot: {name}")

    # Single-pass substitution.  re.sub makes one left-to-right scan; the
    # replacement callback returns a literal string (not re-parsed), so a
    # value containing ``{{ANYTHING}}`` is emitted verbatim without further
    # expansion.
    def _replace(match: re.Match[str]) -> str:
        return slots[match.group(1)]

    return _SLOT_RE.sub(_replace, template)


def cmd_render_template(args: argparse.Namespace) -> None:
    """Render a template file by expanding ``{{SLOT_NAME}}`` placeholders.

    Reads the template file at *args.template*, parses ``--slot KEY=VALUE``
    arguments into a slot mapping, validates that all template slots are
    provided and no extra slots are given, then writes the rendered output to
    stdout.

    Args:
        args: Parsed arguments.
            ``args.template`` (str): Path to the template file.
            ``args.slot`` (List[str] | None): Zero or more ``KEY=VALUE``
                strings from repeated ``--slot`` flags.

    Raises:
        SystemExit: If the template file does not exist, a slot is missing
            or extra, or a ``--slot`` value is malformed (no ``=`` separator).
    """
    template_path = Path(args.template)
    if not template_path.is_file():
        die(f"template not found: {args.template}")

    template_text = template_path.read_text(encoding="utf-8")

    # Parse --slot KEY=VALUE pairs into a dict.
    slots: Dict[str, str] = {}
    for item in args.slot or []:
        if "=" not in item:
            die(f"invalid --slot value (expected KEY=VALUE): {item!r}")
        key, _, value = item.partition("=")
        slots[key] = value

    rendered = render_template(template_text, slots)
    sys.stdout.write(rendered)


# ---------------------------------------------------------------------------
# Prune subcommand — remove old session directories
# ---------------------------------------------------------------------------


def cmd_prune(args: argparse.Namespace) -> None:
    """Delete session directories under .crumbs/sessions/ older than --days.

    Enumerates ``.crumbs/sessions/`` children, filters to those matching a
    known session prefix (``_session-``, ``_decompose-``, ``_review-``),
    parses the name-embedded ``YYYYMMDD-HHMMSS`` timestamp to compute age,
    and deletes directories exceeding the retention threshold.  The age
    comparison is inclusive: a directory exactly ``--days`` days old *is*
    pruned (``age_days >= days``, not ``>``).  Directories modified within
    the last 60 minutes are never deleted regardless of age.

    With ``--dry-run`` the would-be pruned and would-be retained lists are
    printed without any deletion taking place.

    Args:
        args: Parsed arguments.
            ``args.days`` (int): Retention threshold in days (default 14).
            ``args.dry_run`` (bool): When True, list candidates but do not delete.

    Raises:
        SystemExit: If ``--days`` is negative, or on unrecoverable errors.
    """
    days: int = args.days
    if days < 0:
        die(f"--days must be 0 or greater, got {days}")

    crumbs_dir = find_crumbs_dir()
    sessions_dir = crumbs_dir / "sessions"

    if not sessions_dir.is_dir():
        print("nothing to prune (no sessions directory)")
        return

    now = datetime.now()
    now_ts = time.time()

    to_prune: List[Tuple[Path, int]] = []   # (dir_path, age_days)
    to_retain: List[Tuple[Path, str]] = []  # (dir_path, reason)

    try:
        entries = sorted(sessions_dir.iterdir())
    except OSError as exc:
        die(f"error: cannot read sessions directory: {sessions_dir}: {exc}")

    for entry in entries:
        if not entry.is_dir():
            continue

        # Only consider directories matching known prefixes
        parsed_ts = _parse_session_dir_timestamp(entry.name)
        if parsed_ts is None:
            if any(entry.name.startswith(p) for p in SESSION_DIR_PREFIXES):
                # Recognised prefix but unparseable timestamp — warn and skip
                print(
                    f"warning: skipping {entry.name}: timestamp not parseable",
                    file=sys.stderr,
                )
            # Directories with no recognised prefix are silently skipped
            continue

        age_days = (now - parsed_ts).days

        if age_days < days:
            to_retain.append((entry, f"age {age_days}d < {days}d threshold"))
            continue

        # Re-stat immediately before deletion decision (TOCTOU mitigation)
        if _is_active_session(entry, now_ts):
            print(
                f"warning: skipping {entry.name}: active session (mtime within "
                f"{ACTIVE_GUARD_MINUTES} minutes)",
                file=sys.stderr,
            )
            to_retain.append((entry, "active session"))
            continue

        to_prune.append((entry, age_days))

    if args.dry_run:
        if to_prune:
            print(f"would prune {len(to_prune)} director{'y' if len(to_prune) == 1 else 'ies'}:")
            for dir_path, age_days in to_prune:
                print(f"  {dir_path.name}  ({age_days}d old)")
        else:
            print("would prune: nothing")
        if to_retain:
            print(f"would retain {len(to_retain)} director{'y' if len(to_retain) == 1 else 'ies'}:")
            for dir_path, reason in to_retain:
                print(f"  {dir_path.name}  ({reason})")
        else:
            print("would retain: nothing")
        return

    if not to_prune:
        print(f"nothing to prune (0 directories exceed {days} days)")
        return

    pruned_names: List[str] = []
    for dir_path, _age in to_prune:
        try:
            shutil.rmtree(dir_path)
            pruned_names.append(dir_path.name)
        except FileNotFoundError:
            # Already deleted concurrently — count it as pruned
            pruned_names.append(dir_path.name)
        except OSError as exc:
            print(
                f"warning: could not remove {dir_path.name}: {exc}",
                file=sys.stderr,
            )

    if pruned_names:
        names_str = ", ".join(pruned_names)
        print(f"pruned {len(pruned_names)} director{'y' if len(pruned_names) == 1 else 'ies'}: {names_str}")
    else:
        print(f"nothing to prune (0 directories exceed {days} days)")


# ---------------------------------------------------------------------------
# Argument parser
# ---------------------------------------------------------------------------


def build_parser() -> argparse.ArgumentParser:
    """Build and return the top-level argument parser with all subcommands.

    Returns:
        Configured ArgumentParser ready to parse sys.argv[1:].
    """
    parser = argparse.ArgumentParser(
        prog="crumb",
        description="Lightweight JSONL task tracker for ant-farm.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Subcommands:\n"
            "  list        List crumbs (excludes trails by default)\n"
            "  show        Show full detail for a crumb or trail\n"
            "  create      Create a new crumb\n"
            "  update      Update crumb fields or append a note\n"
            "  close       Close one or more crumbs\n"
            "  reopen      Reopen a closed crumb\n"
            "  ready       List open crumbs with no unresolved blockers\n"
            "  blocked     List open crumbs with at least one unresolved blocker\n"
            "  link        Manage crumb links (parent, blocked-by, discovered-from)\n"
            "  search      Full-text search titles and descriptions\n"
            "  trail       Trail subcommands (list, show, create, close)\n"
            "  tree        Show trail/crumb hierarchy\n"
            "  import      Bulk import from JSONL or migrate from Beads\n"
            "  doctor      Validate tasks.jsonl integrity\n"
            "  init        Bootstrap .crumbs/ directory structure\n"
            "  render-template  Expand {{SLOT_NAME}} placeholders in a template file\n"
        ),
    )
    parser.set_defaults(func=None)

    sub = parser.add_subparsers(dest="command", metavar="<subcommand>")

    # --- list ---
    p_list = sub.add_parser("list", help="List crumbs")
    p_list.add_argument("--open", action="store_true", dest="filter_open")
    p_list.add_argument("--closed", action="store_true", dest="filter_closed")
    p_list.add_argument("--in-progress", action="store_true", dest="filter_in_progress")
    p_list.add_argument("--parent", metavar="ID")
    p_list.add_argument("--priority", choices=VALID_PRIORITIES)
    p_list.add_argument("--type", dest="filter_type", choices=["task", "bug", "feature"])
    p_list.add_argument("--agent-type", dest="agent_type")
    p_list.add_argument("--discovered", action="store_true")
    p_list.add_argument("--after", metavar="DATE")
    p_list.add_argument("--limit", type=int, metavar="N")
    p_list.add_argument(
        "--sort",
        choices=["priority", "created_at", "status"],
        default="created_at",
    )
    p_list.add_argument("--short", action="store_true")
    p_list.set_defaults(func=cmd_list)

    # --- show ---
    p_show = sub.add_parser("show", help="Show full detail for a crumb or trail")
    p_show.add_argument("id", metavar="ID")
    p_show.set_defaults(func=cmd_show)

    # --- create ---
    p_create = sub.add_parser("create", help="Create a new crumb")
    p_create.add_argument("--title", metavar="TITLE")
    p_create.add_argument("--from-json", dest="from_json", metavar="JSON")
    p_create.add_argument("--from-file", dest="from_file", metavar="PATH")
    p_create.add_argument("--priority", choices=VALID_PRIORITIES)
    p_create.add_argument("--type", dest="crumb_type", choices=["task", "bug", "feature"])
    p_create.add_argument("--description", metavar="TEXT")
    p_create.set_defaults(func=cmd_create)

    # --- update ---
    p_update = sub.add_parser("update", help="Update crumb fields or append a note")
    p_update.add_argument("id", metavar="ID")
    p_update.add_argument("--status", choices=VALID_STATUSES)
    p_update.add_argument("--note", metavar="TEXT")
    p_update.add_argument("--title", metavar="TITLE")
    p_update.add_argument("--priority", choices=VALID_PRIORITIES)
    p_update.add_argument("--description", metavar="TEXT")
    p_update.add_argument("--from-json", dest="from_json", metavar="JSON",
                          help="Merge a JSON object into the crumb (partial update)")
    p_update.set_defaults(func=cmd_update)

    # --- close ---
    p_close = sub.add_parser("close", help="Close one or more crumbs")
    p_close.add_argument("ids", nargs="+", metavar="ID")
    p_close.set_defaults(func=cmd_close)

    # --- reopen ---
    p_reopen = sub.add_parser("reopen", help="Reopen a closed crumb")
    p_reopen.add_argument("id", metavar="ID")
    p_reopen.set_defaults(func=cmd_reopen)

    # --- ready ---
    p_ready = sub.add_parser("ready", help="List ready crumbs (no unresolved blockers)")
    p_ready.add_argument("--limit", type=int, metavar="N")
    p_ready.add_argument(
        "--sort",
        choices=["priority", "created_at", "status"],
        default="created_at",
    )
    p_ready.set_defaults(func=cmd_ready)

    # --- blocked ---
    p_blocked = sub.add_parser("blocked", help="List blocked crumbs")
    p_blocked.set_defaults(func=cmd_blocked)

    # --- link ---
    p_link = sub.add_parser("link", help="Manage crumb links")
    p_link.add_argument("id", metavar="ID")
    p_link.add_argument("--parent", metavar="ID", dest="link_parent")
    p_link.add_argument("--blocked-by", metavar="ID", dest="blocked_by")
    p_link.add_argument("--remove-blocked-by", metavar="ID", dest="remove_blocked_by")
    p_link.add_argument("--discovered-from", metavar="ID", dest="discovered_from")
    p_link.set_defaults(func=cmd_link)

    # --- search ---
    p_search = sub.add_parser("search", help="Full-text search titles and descriptions")
    p_search.add_argument("query", metavar="QUERY")
    p_search.set_defaults(func=cmd_search)

    # --- trail ---
    p_trail = sub.add_parser("trail", help="Trail subcommands")
    trail_sub = p_trail.add_subparsers(dest="trail_command", metavar="<trail-subcommand>")

    p_trail_list = trail_sub.add_parser("list", help="List trails with completion counts")
    p_trail_list.set_defaults(func=cmd_trail, trail_command="list")

    p_trail_show = trail_sub.add_parser("show", help="Show trail detail and child crumbs")
    p_trail_show.add_argument("id", metavar="ID")
    p_trail_show.set_defaults(func=cmd_trail, trail_command="show")

    p_trail_create = trail_sub.add_parser("create", help="Create a trail")
    p_trail_create.add_argument("--title", required=True, metavar="TITLE")
    p_trail_create.add_argument("--description", metavar="TEXT")
    p_trail_create.add_argument("--priority", choices=VALID_PRIORITIES)
    p_trail_create.add_argument(
        "--acceptance-criteria", dest="acceptance_criteria", metavar="TEXT", action="append"
    )
    p_trail_create.set_defaults(func=cmd_trail, trail_command="create")

    p_trail_close = trail_sub.add_parser("close", help="Close a trail")
    p_trail_close.add_argument("id", metavar="ID")
    p_trail_close.set_defaults(func=cmd_trail, trail_command="close")

    p_trail.set_defaults(func=cmd_trail)

    # --- tree ---
    p_tree = sub.add_parser("tree", help="Show trail/crumb hierarchy")
    p_tree.add_argument("id", nargs="?", metavar="ID")
    p_tree.set_defaults(func=cmd_tree)

    # --- import ---
    p_import = sub.add_parser("import", help="Bulk import from JSONL or migrate from Beads")
    p_import.add_argument("file", metavar="FILE")
    p_import.add_argument(
        "--from-beads",
        action="store_true",
        dest="from_beads",
        help="Migrate Beads issues.jsonl format",
    )
    p_import.set_defaults(func=cmd_import)

    # --- doctor ---
    p_doctor = sub.add_parser("doctor", help="Validate tasks.jsonl integrity")
    p_doctor.add_argument(
        "--fix",
        action="store_true",
        help="Remove dangling blocked_by references automatically",
    )
    p_doctor.set_defaults(func=cmd_doctor)

    # --- init ---
    p_init = sub.add_parser(
        "init",
        help="Bootstrap .crumbs/ directory structure in the current directory",
    )
    p_init.add_argument(
        "--prefix",
        metavar="PREFIX",
        default=None,
        help=(
            "ID prefix for new crumbs (e.g. 'AF'). "
            f"Defaults to '{DEFAULT_CONFIG['prefix']}' when omitted."
        ),
    )
    p_init.set_defaults(func=cmd_init)

    # --- render-template ---
    p_render_template = sub.add_parser(
        "render-template",
        help="Render a template file by expanding {{SLOT_NAME}} placeholders",
    )
    p_render_template.add_argument(
        "template",
        metavar="TEMPLATE",
        help="Path to the template file (must exist and be readable)",
    )
    p_render_template.add_argument(
        "--slot",
        metavar="KEY=VALUE",
        action="append",
        dest="slot",
        help="Slot assignment; repeat for multiple slots (e.g. --slot FOO=bar --slot BAZ=qux)",
    )
    p_render_template.set_defaults(func=cmd_render_template)

    # --- prune ---
    p_prune = sub.add_parser(
        "prune",
        help="Delete old session directories under .crumbs/sessions/",
    )
    p_prune.add_argument(
        "--days",
        type=int,
        default=DEFAULT_RETENTION_DAYS,
        metavar="N",
        help=(
            "Delete session directories whose name-embedded timestamp is older "
            f"than N days (default: {DEFAULT_RETENTION_DAYS}). "
            "Use 0 to delete all except active sessions."
        ),
    )
    p_prune.add_argument(
        "--dry-run",
        action="store_true",
        dest="dry_run",
        help="List would-prune and would-retain directories without deleting.",
    )
    p_prune.set_defaults(func=cmd_prune)

    return parser


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def main() -> None:
    """Parse arguments and dispatch to the appropriate subcommand handler.

    Entry point for the ``crumb`` CLI. Cleans up stale .tmp files at startup,
    builds the argument parser, and calls the subcommand function stored in
    ``args.func``. If no subcommand is given, prints help and exits 0.

    Raises:
        SystemExit: On invalid arguments (argparse), missing .crumbs/, or
            any subcommand that calls die().
    """
    cleanup_stale_tmp_files()

    parser = build_parser()
    args = parser.parse_args()

    if args.func is None:
        # No subcommand given — print help and exit 0
        parser.print_help()
        sys.exit(0)

    args.func(args)


if __name__ == "__main__":
    main()

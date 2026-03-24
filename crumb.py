#!/usr/bin/env python3
# ant-farm crumb CLI
"""crumb.py — Lightweight JSONL task tracker CLI for ant-farm.

Single-file Python CLI, stdlib only, minimum Python 3.8.
Manages tasks and trails in .crumbs/tasks.jsonl with flock-based
concurrency safety and atomic writes.  Run ``crumb --help`` for usage.
"""

from __future__ import annotations

import argparse

try:
    import fcntl
except ImportError:
    fcntl = None  # type: ignore[assignment]  # Windows — FileLock.die()s at use

try:
    from graphlib import TopologicalSorter, CycleError as _CycleError
    _GRAPHLIB_AVAILABLE = True
except ImportError:  # Python < 3.9
    _GRAPHLIB_AVAILABLE = False
    _CycleError = None  # type: ignore[assignment,misc]

import json
import os
import re
import shutil
import subprocess
import sys

import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

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
    "min_crumbs_per_trail": 3,
    "max_crumbs_per_trail": 8,
    "max_files_per_crumb": 8,
    "context_warning_threshold": 35,
    "context_critical_threshold": 25,
    "wave_failure_threshold": 0.5,
    "stuck_agent_timeout_minutes": 10,
    "stuck_agent_escalation_minutes": 15,
    "banned_phrases": [
        "works correctly",
        "as expected",
        "appropriate",
        "well-structured",
        "properly handles",
        "handles gracefully",
        "user-friendly",
        "performant",
        "intuitive",
        "robust",
        "seamless",
    ],
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
    """Print error to stderr and exit."""
    print(f"error: {message}", file=sys.stderr)
    sys.exit(code)


# ---------------------------------------------------------------------------
# Directory discovery — walks up from cwd like git finds .git/
# ---------------------------------------------------------------------------


def find_crumbs_dir() -> Path:
    """Walk up from cwd to filesystem root; return first .crumbs/ found."""
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


def tasks_path() -> Path:
    """Return path to .crumbs/tasks.jsonl."""
    return find_crumbs_dir() / TASKS_FILE


def config_path() -> Path:
    """Return path to .crumbs/config.json."""
    return find_crumbs_dir() / CONFIG_FILE


def lock_path() -> Path:
    """Return path to .crumbs/tasks.lock."""
    return find_crumbs_dir() / LOCK_FILE


# ---------------------------------------------------------------------------
# Config read / write
# ---------------------------------------------------------------------------


def read_config() -> Dict[str, Any]:
    """Read config.json, returning defaults merged with stored values."""
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
    """Atomically write config.json via temp-then-rename."""
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
    """Read all records from a JSONL file. Malformed lines are skipped with a warning."""
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
    """Atomically write records to a JSONL file via temp-then-rename."""
    tmp_path = path.with_suffix(".jsonl.tmp")
    try:
        try:
            with open(tmp_path, "w", encoding="utf-8") as fh:
                for record in records:
                    fh.write(json.dumps(record, separators=(",", ":")) + "\n")
            os.rename(str(tmp_path), str(path))
        except Exception:
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
    """Context manager holding an exclusive flock on tasks.lock (Unix-only).

    Retries with LOCK_NB for up to _LOCK_TIMEOUT_SECS seconds.
    """

    def __init__(self) -> None:
        self._lock_file: Optional[Any] = None

    def __enter__(self) -> "FileLock":
        if fcntl is None:
            die("file locking requires fcntl (Unix-only); Windows is not supported")
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
            except OSError as exc:
                self._lock_file.close()
                self._lock_file = None
                die(f"cannot acquire lock: {exc}")
        return self

    def __exit__(self, *_: Any) -> None:
        if self._lock_file is not None:
            # flock is released automatically on close
            self._lock_file.close()
            self._lock_file = None


# ---------------------------------------------------------------------------
# Startup: clean up stale .tmp files
# ---------------------------------------------------------------------------


_STALE_TMP_AGE_SECS: float = 5.0


def cleanup_stale_tmp_files() -> None:
    """Remove leftover .tmp files from a previous crashed write."""
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

    now = time.time()
    for tmp_file in crumbs.glob("*.tmp"):
        try:
            # Skip recently-modified files — they may belong to a
            # concurrent write_tasks call that has not yet renamed them.
            if now - tmp_file.stat().st_mtime < _STALE_TMP_AGE_SECS:
                continue
            tmp_file.unlink()
        except OSError as exc:
            print(
                f"warning: could not remove stale temp file {tmp_file}: {exc}",
                file=sys.stderr,
            )


# ---------------------------------------------------------------------------
# Timestamp helpers
# ---------------------------------------------------------------------------


def now_iso() -> str:
    """Return current UTC time as ISO 8601 with Z suffix."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


# ---------------------------------------------------------------------------
# tasks.jsonl existence guard
# ---------------------------------------------------------------------------


def require_tasks_jsonl() -> Path:
    """Return path to tasks.jsonl, dying if not found."""
    path = tasks_path()
    if not path.exists():
        die("no .crumbs/tasks.jsonl found. Run /ant-farm-init first.")
    return path


# ---------------------------------------------------------------------------
# Private helper utilities — used by subcommand handlers below
# ---------------------------------------------------------------------------


def _find_crumb(tasks: List[Dict[str, Any]], crumb_id: str) -> Optional[Dict[str, Any]]:
    """Return the first record matching crumb_id, or None."""
    for task in tasks:
        if task.get("id") == crumb_id:
            return task
    return None


def _priority_sort_key(priority: str) -> int:
    """Return an integer sort key for a priority string (P0=0, unknown=5)."""
    try:
        return int(priority[1]) if len(priority) == 2 and priority[0] == "P" else 5
    except (ValueError, IndexError):
        return 5


def _status_sort_key(status: str) -> int:
    """Return an integer sort key for a status string."""
    order = {"open": 0, "in_progress": 1, "closed": 2}
    return order.get(status, 3)


def _require_crumb(
    tasks: List[Dict[str, Any]], crumb_id: str, label: str = "crumb"
) -> Dict[str, Any]:
    """Find a crumb by ID, dying with an error message if not found."""
    crumb = _find_crumb(tasks, crumb_id)
    if crumb is None:
        die(f"{label} '{crumb_id}' not found")
    return crumb


def _sort_crumbs(results: List[Dict[str, Any]], sort_field: str) -> None:
    """Sort results in-place by the given field (priority, status, or created_at)."""
    if sort_field == "priority":
        results.sort(key=lambda t: _priority_sort_key(t.get("priority", "P4")))
    elif sort_field == "status":
        results.sort(key=lambda t: _status_sort_key(t.get("status", "")))
    else:
        results.sort(key=lambda t: t.get("created_at") or "")


def _format_row(crumb: Dict[str, Any], indent: int = 0) -> str:
    """Format a crumb as a single display row."""
    tid = crumb.get("id", "?")
    title = crumb.get("title", "")
    status = crumb.get("status", "")
    priority = crumb.get("priority", "")
    pad = " " * indent
    id_width = 10 if indent else 12
    return f"{pad}{tid:<{id_width}} {priority:<4} {status:<12} {title}"


def _print_fields(record: Dict[str, Any], fields: List[Tuple[str, str]],
                  show_extras: bool = False) -> None:
    """Print label-value pairs for a record, skipping empty values."""
    for key, label in fields:
        value = record.get(key)
        if value is None or value == "" or value == [] or value == {}:
            continue
        if isinstance(value, list):
            print(f"{label}:")
            for item in value:
                print(f"  - {item}")
        else:
            print(f"{label}: {value}")
    if show_extras:
        known_keys = {k for k, _ in fields}
        for key, value in record.items():
            if key not in known_keys and value not in (None, "", [], {}):
                label = key.replace("_", " ").title()
                print(f"{label}: {value}")


def _add_json_flag(parser: argparse.ArgumentParser) -> None:
    """Add the standard --json output flag to a subcommand parser."""
    parser.add_argument(
        "--json",
        action="store_true",
        dest="json_output",
        help="Output JSON instead of human-readable text.",
    )


def _get_trail_children(
    tasks: List[Dict[str, Any]], trail_id: str
) -> List[Dict[str, Any]]:
    """Return all non-trail records whose links.parent equals trail_id."""
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
    """Auto-close a trail when its last open child is closed."""
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
    """Auto-reopen a closed trail when a new non-closed crumb is linked to it."""
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
    """Parse YYYYMMDD-HHMMSS timestamp from a session directory name, or None."""
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
    """Return True if dir_path's mtime is within ACTIVE_GUARD_MINUTES."""
    try:
        mtime = os.stat(dir_path).st_mtime
    except OSError:
        # If stat fails the directory may have vanished; treat as not active.
        return False
    return (now_ts - mtime) < (ACTIVE_GUARD_MINUTES * 60)


def _crumb_to_json_obj(crumb: Dict[str, Any]) -> Dict[str, Any]:
    """Serialize a crumb to a JSON-safe dict with all required fields as keys.

    Required fields are always present (None if absent). Extra keys are appended.

    See docs/json-schema.md for the full field reference, per-command output
    shapes, and copy-pasteable examples.
    """
    required_fields: List[str] = [
        "id", "title", "type", "status", "priority",
        "description", "acceptance_criteria", "scope", "links", "notes",
    ]
    obj: Dict[str, Any] = {field: crumb.get(field) for field in required_fields}
    # Append any extra keys stored on the record (created_at, updated_at, etc.)
    for key, value in crumb.items():
        if key not in obj:
            obj[key] = value
    return obj


def cmd_list(args: argparse.Namespace) -> None:
    """List crumbs with optional filters, sort, and limit."""
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
        # Validate YYYY-MM-DD format: regex enforces zero-padded digits,
        # strptime rejects invalid calendar dates like 2026-02-30.
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", args.after):
            die(f"invalid --after date '{args.after}': expected YYYY-MM-DD format")
        try:
            datetime.strptime(args.after, "%Y-%m-%d")
        except ValueError:
            die(f"invalid --after date '{args.after}': not a valid calendar date")
        # Compare ISO 8601 strings lexicographically (created_at is stored as full ISO 8601)
        after_str = args.after
        results = [
            t
            for t in results
            if (t.get("created_at") or "") > after_str
        ]

    _sort_crumbs(results, args.sort)
    if args.limit is not None and args.limit > 0:
        results = results[: args.limit]

    # --- JSON output branch (before human-readable guard) ---
    if args.json_output:
        print(json.dumps([_crumb_to_json_obj(t) for t in results], indent=2))
        return

    if not results:
        print("no crumbs found")
        return

    # --- output ---
    if args.short:
        for t in results:
            print(_format_row(t))
    else:
        for t in results:
            tid = t.get("id", "?")
            priority = t.get("priority", "")
            status = t.get("status", "")
            crumb_type = t.get("type", "")
            created_at = t.get("created_at", "")
            title = t.get("title", "")
            print(f"{tid:<12} {priority:<4} {status:<12} {crumb_type:<10} {created_at[:10]}  {title}")


def cmd_show(args: argparse.Namespace) -> None:
    """Show all fields for a crumb or trail."""
    path = require_tasks_jsonl()
    tasks = read_tasks(path)
    crumb = _require_crumb(tasks, args.id)

    if args.json_output:
        print(json.dumps(_crumb_to_json_obj(crumb), indent=2))
        return

    fields = [
        ("id", "ID"), ("type", "Type"), ("title", "Title"),
        ("status", "Status"), ("priority", "Priority"),
        ("agent_type", "Agent Type"), ("description", "Description"),
        ("acceptance_criteria", "Acceptance Criteria"), ("scope", "Scope"),
        ("parent", "Parent"), ("discovered_from", "Discovered From"),
        ("blocked_by", "Blocked By"), ("links", "Links"), ("notes", "Notes"),
        ("created_at", "Created At"), ("updated_at", "Updated At"),
        ("closed_at", "Closed At"),
    ]
    _print_fields(crumb, fields, show_extras=True)


def cmd_create(args: argparse.Namespace) -> None:
    """Create a new crumb and append it to tasks.jsonl."""
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
        else:
            if not args.title:
                die("--title is required unless --from-json or --from-file is provided")
            payload = {"title": args.title}

        # Merge explicit CLI flags over payload — applies to all input modes.
        # For --title-only the args.title override is idempotent; for
        # --from-json / --from-file it lets CLI flags win over JSON fields.
        if args.title:
            payload["title"] = args.title
        if args.priority:
            payload["priority"] = args.priority
        if args.crumb_type:
            payload["type"] = args.crumb_type
        if args.description:
            payload["description"] = args.description
        if getattr(args, "tdd", None) is not None:
            payload["tdd"] = args.tdd

        # Reject empty or whitespace-only titles
        if not payload.get("title", "").strip():
            die("title must not be empty")

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
            # NOTE (maintainers): next_crumb_id is the only counter validated here.
            # If new config counter fields are added (e.g. next_trail_id variants),
            # they must be explicitly advanced in this branch or IDs will collide.
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
            "tdd": payload.get("tdd", True),
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

    # --- JSON output branch ---
    if getattr(args, "json_output", False):
        print(json.dumps(_crumb_to_json_obj(record), indent=2))
        return

    print(f"created {crumb_id}")


def cmd_update(args: argparse.Namespace) -> None:
    """Update crumb fields or append a note."""
    with FileLock():
        path = require_tasks_jsonl()
        tasks = read_tasks(path)

        crumb = _require_crumb(tasks, args.id)
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

        if getattr(args, "tdd", None) is not None:
            if crumb.get("tdd") != args.tdd:
                crumb["tdd"] = args.tdd
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
            # guarded transitions.  "id" and "created_at" are immutable
            # identifiers set once at creation time.  "status" must go through
            # --status (which enforces the closed->open gate).  "closed_at" is
            # managed by close/reopen and must not be set directly.
            protected = {"id", "created_at", "status", "closed_at"}
            for key, value in extra.items():
                if key in protected:
                    continue
                if isinstance(value, dict) and isinstance(crumb.get(key), dict):
                    # Deep-merge: only flag changed when the incoming dict
                    # adds or overwrites at least one key with a different value.
                    existing_sub: Dict[str, Any] = crumb[key]
                    for sub_key, sub_val in value.items():
                        if existing_sub.get(sub_key) != sub_val:
                            existing_sub[sub_key] = sub_val
                            changed = True
                else:
                    if isinstance(crumb.get(key), dict) and not isinstance(value, dict):
                        print(
                            f"Warning: field '{key}' was a dict but is being replaced by a scalar value from --from-json",
                            file=sys.stderr,
                        )
                    if crumb.get(key) != value:
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
            if getattr(args, "json_output", False):
                print(json.dumps({"success": False, "message": "no changes"}, indent=2))
            else:
                print(f"no changes to {args.id}")
            return

        crumb["updated_at"] = now_iso()
        write_tasks(path, tasks)

    # --- JSON output branch ---
    if getattr(args, "json_output", False):
        obj = {"success": True}
        obj.update(_crumb_to_json_obj(crumb))
        print(json.dumps(obj, indent=2))
        return

    print(f"updated {args.id}")


def cmd_close(args: argparse.Namespace) -> None:
    """Close one or more crumbs. Already-closed crumbs are skipped."""
    with FileLock():
        path = require_tasks_jsonl()
        tasks = read_tasks(path)

        # Pre-validate all IDs exist before mutating any
        for crumb_id in args.ids:
            if _find_crumb(tasks, crumb_id) is None:
                die(f"crumb '{crumb_id}' not found")

        closed: List[str] = []
        closed_crumbs: List[Dict[str, Any]] = []
        skipped: List[str] = []

        for crumb_id in args.ids:
            crumb = _find_crumb(tasks, crumb_id)
            # Invariant: pre-validation loop above (under same FileLock)
            # guarantees every ID exists — _find_crumb cannot return None here.
            if crumb is None:
                die(f"internal error: '{crumb_id}' pre-validated but not found in mutation loop")

            if crumb.get("status") == "closed":
                skipped.append(crumb_id)
                continue

            now = now_iso()
            crumb["status"] = "closed"
            crumb["closed_at"] = now
            crumb["updated_at"] = now
            closed.append(crumb_id)
            closed_crumbs.append(crumb)

        if closed:
            write_tasks(path, tasks)
            # Auto-close any parent trail whose last open child just closed
            for crumb_id in closed:
                _auto_close_trail_if_complete(tasks, path, crumb_id)

    # --- JSON output branch ---
    if getattr(args, "json_output", False):
        if len(closed_crumbs) == 1 and len(args.ids) == 1:
            print(json.dumps(_crumb_to_json_obj(closed_crumbs[0]), indent=2))
        else:
            print(json.dumps([_crumb_to_json_obj(c) for c in closed_crumbs], indent=2))
        return

    for crumb_id in closed:
        print(f"closed {crumb_id}")
    for crumb_id in skipped:
        print(f"{crumb_id} already closed")


def cmd_reopen(args: argparse.Namespace) -> None:
    """Reopen a closed crumb."""
    with FileLock():
        path = require_tasks_jsonl()
        tasks = read_tasks(path)

        crumb = _require_crumb(tasks, args.id)
        if crumb.get("status") != "closed":
            current = crumb.get("status", "open")
            die(f"crumb '{args.id}' is not closed (current status: '{current}')")

        now = now_iso()
        crumb["status"] = "open"
        crumb.pop("closed_at", None)
        crumb["updated_at"] = now
        write_tasks(path, tasks)

    # --- JSON output branch ---
    if getattr(args, "json_output", False):
        print(json.dumps(_crumb_to_json_obj(crumb), indent=2))
        return

    print(f"reopened {args.id}")


def _get_blocked_by(crumb: Dict[str, Any]) -> List[str]:
    """Return merged blocked_by list from both top-level and links fields."""
    top_level: List[str] = crumb.get("blocked_by") or []
    if not isinstance(top_level, list):
        top_level = [top_level] if top_level else []

    links_raw = crumb.get("links") or {}
    links_dict: Dict[str, Any] = links_raw if isinstance(links_raw, dict) else {}
    links_blocked_by: List[str] = links_dict.get("blocked_by") or []
    if not isinstance(links_blocked_by, list):
        links_blocked_by = [links_blocked_by] if links_blocked_by else []

    # Merge both locations, deduplicated, preserving order
    merged: List[str] = []
    for bid in top_level + links_blocked_by:
        if bid not in merged:
            merged.append(bid)
    return merged


def _detect_cycles(id_to_record: Dict[str, Dict[str, Any]]) -> List[List[str]]:
    """Detect cycles in the blocked_by dependency graph.

    Uses ``graphlib.TopologicalSorter`` (Python 3.9+) to find cycles. For
    each cycle discovered, removes its nodes from the working graph and repeats
    until no cycles remain, ensuring all cycles in disconnected subgraphs are
    found.

    Self-referential cycles (A blocked_by A) are detected in a pre-pass before
    the topological sort, since graphlib does not always surface them as a
    distinct CycleError path.

    Args:
        id_to_record: Mapping of crumb ID to its full record dict.

    Returns:
        List of cycles, where each cycle is an ordered list of IDs forming the
        cycle path (e.g., ``["AF-1", "AF-2", "AF-3", "AF-1"]`` — last element
        repeats the first to close the loop). Returns an empty list when
        graphlib is unavailable (Python < 3.9).
    """
    if not _GRAPHLIB_AVAILABLE:
        return []

    cycles: List[List[str]] = []

    # Pre-pass: detect self-referential cycles (A blocked_by A).
    # graphlib may or may not surface these cleanly, so handle explicitly.
    self_refs: Set[str] = set()
    for rec_id, record in id_to_record.items():
        blockers = _get_blocked_by(record)
        if rec_id in blockers:
            cycles.append([rec_id, rec_id])
            self_refs.add(rec_id)

    # Build adjacency: node -> set of predecessors (nodes it depends on /
    # is blocked by). graphlib uses "predecessors" = nodes that must come first.
    # blocked_by means "I depend on these", i.e. they are my predecessors.
    remaining: Dict[str, Set[str]] = {}
    for rec_id, record in id_to_record.items():
        if rec_id in self_refs:
            continue  # already reported; skip to avoid confusing the sorter
        blockers = [b for b in _get_blocked_by(record) if b in id_to_record and b not in self_refs]
        remaining[rec_id] = set(blockers)

    # Iteratively run TopologicalSorter, peel off one cycle per iteration.
    # This surfaces all cycles across disconnected subgraphs.
    max_iterations = len(remaining) + 1  # safety cap
    for _ in range(max_iterations):
        if not remaining:
            break
        ts = TopologicalSorter(remaining)
        try:
            ts.prepare()
            break  # no cycle found — remaining graph is acyclic
        except _CycleError as exc:  # type: ignore[misc]
            # exc.args[1] is a tuple of IDs forming the cycle path
            raw_cycle: Tuple[str, ...] = exc.args[1] if len(exc.args) > 1 else ()
            if raw_cycle:
                # graphlib already returns a closed path: [A, B, C, A].
                # Use as-is; no need to append raw_cycle[0] again.
                cycle_path = list(raw_cycle)
                cycles.append(cycle_path)
                # Remove the first node in the cycle to break it, then retry
                # to find any remaining cycles.
                pivot = raw_cycle[0]
                remaining.pop(pivot, None)
                # Also remove any references to pivot from other nodes so the
                # graph stays self-consistent.
                for deps in remaining.values():
                    deps.discard(pivot)
            else:
                break  # degenerate CycleError with no path info — stop

    return cycles


def _break_cycle_edges(
    cycles: List[List[str]],
    id_to_record: Dict[str, Dict[str, Any]],
) -> List[Tuple[str, str]]:
    """Remove the closing blocked_by edge from each cycle, mutating id_to_record in place.

    For a cycle path ``[A, B, C, A]`` returned by graphlib, each consecutive pair
    ``(X, Y)`` encodes a dependency edge where Y is blocked by X (X must complete
    before Y).  The closing edge is ``(C, A)``, meaning A is blocked by C.  This
    function removes C from A's ``blocked_by`` (in both the top-level field and
    ``links.blocked_by``) so the cycle is broken with minimal collateral damage.

    Self-referential cycles ``[X, X]`` remove X from its own ``blocked_by``.

    Only edges that actually exist in the record are removed; if the edge is
    missing (e.g., already cleaned by a prior iteration) it is silently skipped.

    Args:
        cycles: List of cycle paths as returned by ``_detect_cycles``.  Each
            path is a closed list where ``path[0] == path[-1]``.
        id_to_record: Mapping of crumb ID to record dict.  **Mutated in place.**

    Returns:
        List of ``(blocked_id, blocker_id)`` tuples describing each edge removed:
        ``blocker_id`` was removed from ``blocked_id``'s ``blocked_by`` field.
        Duplicate closing edges across multiple reported cycles are deduplicated.
    """
    removed: List[Tuple[str, str]] = []
    seen_edges: Set[Tuple[str, str]] = set()

    for cycle_path in cycles:
        if len(cycle_path) < 2:
            continue
        # In the cycle path [A, B, C, A], each consecutive pair (X, Y) encodes
        # a dependency edge meaning Y is blocked by X (X must complete before Y).
        # The closing edge is represented by (cycle_path[-2], cycle_path[0]):
        #   cycle_path[0] is blocked by cycle_path[-2].
        # To break the cycle we remove cycle_path[-2] from cycle_path[0]'s blocked_by.
        #
        # For a self-referential cycle [X, X]:
        #   cycle_path[-2] == cycle_path[0] == X — remove X from X's blocked_by.
        blocker_id = cycle_path[-2]   # the predecessor to remove
        blocked_id = cycle_path[0]    # the record whose blocked_by we edit
        edge = (blocker_id, blocked_id)
        if edge in seen_edges:
            continue  # already handled this edge
        seen_edges.add(edge)

        record = id_to_record.get(blocked_id)
        if record is None:
            continue

        edge_removed = False

        # Remove from top-level blocked_by
        top_blocked: List[str] = record.get("blocked_by") or []
        if isinstance(top_blocked, list) and blocker_id in top_blocked:
            record["blocked_by"] = [b for b in top_blocked if b != blocker_id]
            edge_removed = True

        # Remove from links.blocked_by
        links_raw = record.get("links")
        if isinstance(links_raw, dict):
            links_blocked: List[str] = links_raw.get("blocked_by") or []
            if isinstance(links_blocked, list) and blocker_id in links_blocked:
                links_raw["blocked_by"] = [b for b in links_blocked if b != blocker_id]
                edge_removed = True

        if edge_removed:
            removed.append((blocked_id, blocker_id))

    return removed


def _is_crumb_blocked(
    crumb: Dict[str, Any], id_to_record: Dict[str, Dict[str, Any]]
) -> bool:
    """Return True if crumb has at least one unresolved (non-closed) blocker."""
    for bid in _get_blocked_by(crumb):
        blocker = id_to_record.get(bid)
        if blocker is not None and blocker.get("status") != "closed":
            return True
    return False


def cmd_ready(args: argparse.Namespace) -> None:
    """List open crumbs with no unresolved blockers."""
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

    _sort_crumbs(results, getattr(args, "sort", "created_at"))
    limit = getattr(args, "limit", None)
    if limit is not None and limit > 0:
        results = results[:limit]

    # --- JSON output branch ---
    if getattr(args, "json_output", False):
        print(json.dumps([_crumb_to_json_obj(t) for t in results], indent=2))
        return

    for t in results:
        print(_format_row(t))


def cmd_blocked(args: argparse.Namespace) -> None:
    """List open crumbs with at least one unresolved blocker."""
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

    _sort_crumbs(results, "created_at")

    # --- JSON output branch ---
    if getattr(args, "json_output", False):
        output: List[Dict[str, Any]] = []
        for t in results:
            obj = _crumb_to_json_obj(t)
            blockers: List[Dict[str, Any]] = []
            for bid in _get_blocked_by(t):
                blocker = id_to_record.get(bid)
                blockers.append({
                    "id": bid,
                    "status": blocker.get("status") if blocker else None,
                })
            obj["blockers"] = blockers
            output.append(obj)
        print(json.dumps(output, indent=2))
        return

    for t in results:
        print(_format_row(t))


def cmd_link(args: argparse.Namespace) -> None:
    """Manage crumb links: parent, blocked_by, and discovered_from."""
    with FileLock():
        path = require_tasks_jsonl()
        tasks = read_tasks(path)

        crumb = _require_crumb(tasks, args.id)

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

    # --- JSON output branch ---
    if getattr(args, "json_output", False):
        print(json.dumps(_crumb_to_json_obj(crumb), indent=2))
        return

    print(f"updated links for {args.id}")


def cmd_search(args: argparse.Namespace) -> None:
    """Case-insensitive full-text search across titles and descriptions."""
    path = require_tasks_jsonl()
    tasks = read_tasks(path)

    query_lower = args.query.lower()

    results = [
        t
        for t in tasks
        if query_lower in (t.get("title") or "").lower()
        or query_lower in (t.get("description") or "").lower()
    ]

    # --- JSON output branch ---
    if getattr(args, "json_output", False):
        print(json.dumps([_crumb_to_json_obj(t) for t in results], indent=2))
        return

    for t in results:
        print(_format_row(t))


def cmd_trail(args: argparse.Namespace) -> None:
    """Dispatch trail subcommands: list, show, create, close."""
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
    """Create a new trail with an auto-assigned T-prefixed ID."""
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

    # --- JSON output branch ---
    if getattr(args, "json_output", False):
        print(json.dumps(_crumb_to_json_obj(record), indent=2))
        return

    print(f"created {trail_id}")


def _cmd_trail_show(args: argparse.Namespace) -> None:
    """Show trail fields and its child crumbs."""
    path = require_tasks_jsonl()
    tasks = read_tasks(path)

    trail = _require_crumb(tasks, args.id, label="trail")
    if trail.get("type") != "trail":
        die(f"'{args.id}' is not a trail")

    # --- JSON output branch ---
    if getattr(args, "json_output", False):
        obj = _crumb_to_json_obj(trail)
        obj["children"] = [_crumb_to_json_obj(c) for c in _get_trail_children(tasks, args.id)]
        print(json.dumps(obj, indent=2))
        return

    fields = [
        ("id", "ID"), ("type", "Type"), ("title", "Title"),
        ("status", "Status"), ("priority", "Priority"),
        ("description", "Description"),
        ("acceptance_criteria", "Acceptance Criteria"),
        ("created_at", "Created At"), ("updated_at", "Updated At"),
        ("closed_at", "Closed At"),
    ]
    _print_fields(trail, fields)

    # Print child crumbs
    children = _get_trail_children(tasks, args.id)
    total = len(children)
    closed_count = sum(1 for c in children if c.get("status") == "closed")
    print(f"\nChildren ({closed_count}/{total} closed):")
    if not children:
        print("  (none)")
    else:
        for child in children:
            print(_format_row(child, indent=2))


def _cmd_trail_list(args: argparse.Namespace) -> None:
    """List all trails with completion counts."""
    path = require_tasks_jsonl()
    tasks = read_tasks(path)

    trails = [t for t in tasks if t.get("type") == "trail"]

    # --- JSON output branch ---
    if getattr(args, "json_output", False):
        print(json.dumps([_crumb_to_json_obj(t) for t in trails], indent=2))
        return

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
    """Close a trail, rejecting if any children are still open."""
    with FileLock():
        path = require_tasks_jsonl()
        tasks = read_tasks(path)

        trail = _require_crumb(tasks, args.id, label="trail")
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


# ---------------------------------------------------------------------------
# validate-trail helpers
# ---------------------------------------------------------------------------


def _count_crumb_files(crumb: Dict[str, Any]) -> int:
    """Return the number of files referenced in a crumb's scope.files array.

    Falls back to 0 when the field is absent or malformed.

    Args:
        crumb: A task record dict.

    Returns:
        Integer file count.
    """
    scope = crumb.get("scope")
    if isinstance(scope, dict):
        files = scope.get("files")
        if isinstance(files, list):
            return len(files)
    return 0


def _validate_single_trail(
    tasks: List[Dict[str, Any]],
    trail_id: str,
    min_crumbs: int,
    max_crumbs: int,
    max_files: int,
) -> Dict[str, Any]:
    """Validate granularity constraints for one trail.

    Checks:
    - open/in_progress child crumb count is within [min_crumbs, max_crumbs]
    - no child crumb references more than max_files files in scope.files

    Args:
        tasks: All task records.
        trail_id: ID of the trail to validate.
        min_crumbs: Minimum required open/in-progress crumb count.
        max_crumbs: Maximum allowed open/in-progress crumb count.
        max_files: Maximum allowed files per crumb.

    Returns:
        Dict with keys:
            trail_id (str), crumb_count (int), status (str: PASS/WARN/FAIL),
            violations (list of dicts with 'type', 'message', and optional 'crumb_id').
    """
    children = _get_trail_children(tasks, trail_id)
    active_children = [
        c for c in children if c.get("status") in ("open", "in_progress")
    ]
    crumb_count = len(active_children)

    violations: List[Dict[str, Any]] = []
    has_fail = False
    has_warn = False

    # --- crumb count checks (FAIL) ---
    if crumb_count < min_crumbs:
        violations.append({
            "type": "FAIL",
            "message": (
                f"trail has {crumb_count} open/in-progress crumb(s); "
                f"minimum is {min_crumbs}"
            ),
        })
        has_fail = True
    elif crumb_count > max_crumbs:
        violations.append({
            "type": "FAIL",
            "message": (
                f"trail has {crumb_count} open/in-progress crumb(s); "
                f"maximum is {max_crumbs}"
            ),
        })
        has_fail = True

    # --- per-crumb file count checks (WARN) ---
    for child in children:
        file_count = _count_crumb_files(child)
        if file_count > max_files:
            violations.append({
                "type": "WARN",
                "crumb_id": child.get("id", "?"),
                "message": (
                    f"crumb {child.get('id', '?')} references {file_count} file(s); "
                    f"maximum is {max_files}"
                ),
            })
            has_warn = True

    if has_fail:
        status = "FAIL"
    elif has_warn:
        status = "WARN"
    else:
        status = "PASS"

    return {
        "trail_id": trail_id,
        "crumb_count": crumb_count,
        "status": status,
        "violations": violations,
    }


def cmd_validate_trail(args: argparse.Namespace) -> None:
    """Validate trail granularity constraints.

    Checks open/in-progress crumb count and per-crumb file count against
    configurable thresholds. Supports --all (validate every trail), --json
    (structured output), and --strict (exit 1 on any FAIL).

    Args:
        args: Parsed CLI arguments.
    """
    path = require_tasks_jsonl()
    tasks = read_tasks(path)
    config = read_config()

    min_crumbs = int(config.get("min_crumbs_per_trail", 3))
    max_crumbs = int(config.get("max_crumbs_per_trail", 8))
    max_files = int(config.get("max_files_per_crumb", 8))

    validate_all: bool = getattr(args, "all_trails", False)
    json_output: bool = getattr(args, "json_output", False)
    strict: bool = getattr(args, "strict", False)
    trail_id: Optional[str] = getattr(args, "id", None)

    if validate_all:
        trails = [t for t in tasks if t.get("type") == "trail"]
        if not trails:
            if json_output:
                print(json.dumps([], indent=2))
            else:
                print("no trails found")
            return

        results = [
            _validate_single_trail(
                tasks, t["id"], min_crumbs, max_crumbs, max_files
            )
            for t in trails
        ]
    else:
        if trail_id is None:
            die("usage: crumb validate-trail <trail-id> | --all")
        trail = _require_crumb(tasks, trail_id, label="trail")
        if trail.get("type") != "trail":
            die(f"'{trail_id}' is not a trail")
        results = [
            _validate_single_trail(
                tasks, trail_id, min_crumbs, max_crumbs, max_files
            )
        ]

    if json_output:
        print(json.dumps(results if validate_all else results[0], indent=2))
    else:
        if validate_all:
            # Summary table header
            print(f"{'Trail':<14} {'Crumbs':>7}  {'Status':<6}  Violations")
            print("-" * 60)
            for r in results:
                vcount = len(r["violations"])
                print(
                    f"{r['trail_id']:<14} {r['crumb_count']:>7}  "
                    f"{r['status']:<6}  {vcount} violation(s)"
                )
            all_statuses = [r["status"] for r in results]
            fail_count = all_statuses.count("FAIL")
            warn_count = all_statuses.count("WARN")
            pass_count = all_statuses.count("PASS")
            print(
                f"\n{len(results)} trail(s): "
                f"{pass_count} PASS, {warn_count} WARN, {fail_count} FAIL"
            )
        else:
            r = results[0]
            print(f"trail: {r['trail_id']}")
            print(f"crumb count (open/in-progress): {r['crumb_count']}")
            print(f"status: {r['status']}")
            if r["violations"]:
                print("violations:")
                for v in r["violations"]:
                    print(f"  [{v['type']}] {v['message']}")
            else:
                print("no violations")

    if strict:
        any_fail = any(r["status"] == "FAIL" for r in results)
        if any_fail:
            sys.exit(1)


def cmd_tree(args: argparse.Namespace) -> None:
    """Display trail/crumb hierarchy as an indented tree."""
    path = require_tasks_jsonl()
    tasks = read_tasks(path)

    trail_id_filter: Optional[str] = getattr(args, "id", None)

    if trail_id_filter is not None:
        trail = _require_crumb(tasks, trail_id_filter, label="trail")
        if trail.get("type") != "trail":
            die(f"'{trail_id_filter}' is not a trail")

        # --- JSON output branch (single trail) ---
        if getattr(args, "json_output", False):
            obj = _crumb_to_json_obj(trail)
            obj["children"] = [_crumb_to_json_obj(c) for c in _get_trail_children(tasks, trail_id_filter)]
            print(json.dumps(obj, indent=2))
            return

        print(_format_row(trail))
        for child in _get_trail_children(tasks, trail_id_filter):
            print(_format_row(child, indent=2))
        return

    # Full tree: all trails with children, then orphans
    trails = [t for t in tasks if t.get("type") == "trail"]
    non_trails = [t for t in tasks if t.get("type") != "trail"]
    child_ids: Set[str] = set()

    # --- JSON output branch (full tree) ---
    if getattr(args, "json_output", False):
        trail_objs: List[Dict[str, Any]] = []
        json_child_ids: Set[str] = set()
        for trail in trails:
            obj = _crumb_to_json_obj(trail)
            children = _get_trail_children(tasks, trail.get("id", "?"))
            obj["children"] = [_crumb_to_json_obj(c) for c in children]
            for c in children:
                json_child_ids.add(c.get("id", "?"))
            trail_objs.append(obj)
        orphans_json = [
            _crumb_to_json_obj(t)
            for t in non_trails
            if t.get("id") not in json_child_ids
        ]
        print(json.dumps({"trails": trail_objs, "orphans": orphans_json}, indent=2))
        return

    for trail in trails:
        print(_format_row(trail))
        for child in _get_trail_children(tasks, trail.get("id", "?")):
            print(_format_row(child, indent=2))
            child_ids.add(child.get("id", "?"))

    orphans = [t for t in non_trails if t.get("id") not in child_ids]
    if orphans:
        print("(orphans)")
        for t in orphans:
            print(_format_row(t, indent=2))


def cmd_import(args: argparse.Namespace) -> None:
    """Import crumbs from a JSONL file.

    Reads line-by-line, skips malformed JSON and duplicate IDs (with
    warnings), appends valid entries to tasks.jsonl, and updates config
    counters after import.
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

        existing_ids: Set[str] = {t.get("id") for t in existing_tasks if t.get("id")}
        config = read_config()

        imported_count = 0
        skipped_malformed = 0
        skipped_duplicate = 0

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

    # --- JSON output branch ---
    if getattr(args, "json_output", False):
        print(json.dumps({
            "imported_count": imported_count,
            "skipped_malformed": skipped_malformed,
            "skipped_duplicate": skipped_duplicate,
        }, indent=2))
        return

    print(
        f"imported {imported_count} record(s)"
        + (f", skipped {skipped_malformed} malformed" if skipped_malformed else "")
        + (f", skipped {skipped_duplicate} duplicate(s)" if skipped_duplicate else "")
    )


def cmd_doctor(args: argparse.Namespace) -> None:
    """Validate tasks.jsonl integrity and optionally repair issues.

    Checks: malformed JSON, duplicate IDs, dangling parent/blocked_by
    links, orphan crumbs, and circular dependency cycles in blocked_by
    fields. With --fix, removes dangling blocked_by refs and breaks
    detected cycles by removing the closing edge of each cycle.
    Exit 1 on errors; warnings alone exit 0.
    """
    path = require_tasks_jsonl()

    errors: List[str] = []
    warnings: List[str] = []
    fixes_applied: List[str] = []
    cycle_fixes_applied: List[str] = []
    cycles: List[List[str]] = []

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
        trail_ids: Set[str] = {
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

        # --- Pass 3: cycle detection in blocked_by dependency graph ---
        cycles = _detect_cycles(id_to_record)
        for cycle_path in cycles:
            path_str = " -> ".join(cycle_path)
            errors.append(f"cycle detected: {path_str}")

        # --- Pass 4 (--fix): break detected cycles ---
        if getattr(args, "fix", False) and cycles:
            broken_edges = _break_cycle_edges(cycles, id_to_record)
            for from_id, to_id in broken_edges:
                msg = f"'{from_id}': removed cycle-closing blocked_by edge to '{to_id}'"
                cycle_fixes_applied.append(msg)
                fixes_applied.append(msg)

        # --- Apply --fix writes ---
        if getattr(args, "fix", False) and fixes_applied:
            write_tasks(path, valid_records)
            if not getattr(args, "json_output", False):
                for msg in fixes_applied:
                    print(f"fixed: {msg}")
            if malformed_lines and not getattr(args, "json_output", False):
                print(
                    f"note: {len(malformed_lines)} malformed line(s) were removed "
                    f"from tasks.jsonl (lines: {malformed_lines})",
                    file=sys.stderr,
                )

    # --- Report ---
    if getattr(args, "json_output", False):
        report = {
            "ok": len(errors) == 0,
            "error_count": len(errors),
            "warning_count": len(warnings),
            "errors": errors,
            "warnings": warnings,
            "fixes_applied": fixes_applied,
            "cycle_fixes_applied": cycle_fixes_applied,
            "cycles": cycles,
        }
        print(json.dumps(report, indent=2))
        if errors:
            sys.exit(1)
        return

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
    """Bootstrap .crumbs/ directory with config.json and tasks.jsonl. Idempotent."""
    cwd = Path.cwd().resolve()
    crumbs = cwd / CRUMBS_DIR_NAME
    json_output: bool = getattr(args, "json_output", False)

    if crumbs.is_dir():
        if json_output:
            print(json.dumps({"path": str(crumbs), "status": "already_exists"}, indent=2))
        else:
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
            if not json_output:
                print(f"Added '{gitignore_entry}' to .gitignore")
        else:
            if not json_output:
                print(f"'.gitignore' already contains '{gitignore_entry}' — skipped")
    except OSError as exc:
        # .gitignore update is best-effort; warn but do not abort
        print(f"warning: could not update .gitignore: {exc}", file=sys.stderr)

    # --- JSON output branch ---
    if json_output:
        print(json.dumps({"path": str(crumbs), "status": "initialized"}, indent=2))
        return

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
#: in the orchestration templates and the ``crumb render-template`` subcommand.
_SLOT_RE: re.Pattern[str] = re.compile(r"\{\{([A-Z][A-Z0-9_]*)\}\}")


def render_template(template: str, slots: Dict[str, str]) -> str:
    """Single-pass {{SLOT_NAME}} expansion. Dies on missing or extra slots."""
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
    """Render a template file by expanding {{SLOT_NAME}} placeholders."""
    template_path = Path(args.template)
    if not template_path.is_file():
        die(f"template not found: {args.template}")

    try:
        template_text = template_path.read_text(encoding="utf-8")
    except OSError as exc:
        die(f"cannot read template: {exc}")

    # Parse --slot KEY=VALUE pairs into a dict.
    slots: Dict[str, str] = {}
    for item in args.slot or []:
        if "=" not in item:
            die(f"invalid --slot value (expected KEY=VALUE): {item!r}")
        key, _, value = item.partition("=")
        slots[key] = value

    rendered = render_template(template_text, slots)

    # --- JSON output branch ---
    if getattr(args, "json_output", False):
        print(json.dumps({"content": rendered}, indent=2))
        return

    sys.stdout.write(rendered)


# ---------------------------------------------------------------------------
# validate-spec subcommand — scan AC lines for banned phrases
# ---------------------------------------------------------------------------

#: Pattern matching acceptance-criteria lines, e.g. "AC-1.2: some text".
_AC_LINE_RE: re.Pattern[str] = re.compile(r"AC-\d+\.\d+:")


def cmd_validate_spec(args: argparse.Namespace) -> None:
    """Scan a spec file's acceptance criteria lines for banned phrases.

    Reads ``banned_phrases`` from config.json (with defaults from
    ``DEFAULT_CONFIG``).  Each line matching ``AC-\\d+\\.\\d+:`` is tested
    against every banned phrase using case-insensitive word-boundary regex so
    that partial matches inside longer words are not reported (e.g.
    ``inappropriate`` does **not** trigger the phrase ``appropriate``).

    Exits 1 when any matches are found; exits 0 when the spec is clean.

    Args:
        args: Parsed CLI arguments.  Expected attributes:

            - ``spec_file`` (str): Path to the spec markdown file.
            - ``json_output`` (bool): Emit JSON instead of human-readable text.
    """
    spec_path = Path(args.spec_file)
    if not spec_path.exists():
        die(f"spec file not found: {spec_path}")

    config = read_config()
    banned_phrases: List[str] = config.get("banned_phrases", [])
    if not isinstance(banned_phrases, list):
        die("config field 'banned_phrases' must be a list")

    # Pre-compile one pattern per phrase for word-boundary, case-insensitive matching.
    phrase_patterns: List[Tuple[str, re.Pattern[str]]] = [
        (phrase, re.compile(r"\b" + re.escape(phrase) + r"\b", re.IGNORECASE))
        for phrase in banned_phrases
        if isinstance(phrase, str) and phrase
    ]

    try:
        lines = spec_path.read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        die(f"cannot read spec file: {exc}")

    matches: List[Dict[str, Any]] = []
    for lineno, line in enumerate(lines, start=1):
        if not _AC_LINE_RE.search(line):
            continue
        for phrase, pattern in phrase_patterns:
            if pattern.search(line):
                matches.append(
                    {
                        "line": lineno,
                        "phrase": phrase,
                        "text": line.strip(),
                    }
                )

    json_output: bool = getattr(args, "json_output", False)
    clean = len(matches) == 0

    if json_output:
        print(json.dumps({"clean": clean, "matches": matches}, indent=2))
    else:
        if clean:
            print("validate-spec: PASS — no banned phrases found")
        else:
            print(f"validate-spec: FAIL — {len(matches)} banned phrase(s) found")
            for m in matches:
                print(f"  line {m['line']}: [{m['phrase']}] {m['text']}")

    if not clean:
        sys.exit(1)


# ---------------------------------------------------------------------------
# validate-tdd subcommand — verify test-first ordering in a commit range
# ---------------------------------------------------------------------------

#: Patterns that identify test files.
_TEST_FILE_PATTERNS: List[re.Pattern[str]] = [
    re.compile(r".*_test\.[^/]+$"),     # *_test.*
    re.compile(r"(?:^|/)test_[^/]+$"),  # test_*.*
    re.compile(r".*\.spec\.[^/]+$"),    # *.spec.*
    re.compile(r".*\.test\.[^/]+$"),    # *.test.*
]


def _is_test_file(path: str) -> bool:
    """Return True when *path* matches any known test-file pattern."""
    for pat in _TEST_FILE_PATTERNS:
        if pat.search(path):
            return True
    return False


def _git_run(args: List[str], cwd: str) -> subprocess.CompletedProcess:
    """Run a git command and return the CompletedProcess."""
    return subprocess.run(
        ["git", *args],
        capture_output=True,
        text=True,
        cwd=cwd,
    )


def _parse_commit_range(commit_range: str) -> Tuple[Optional[str], Optional[str]]:
    """Split 'A..B' into (A, B). Returns (None, commit_range) for bare hashes."""
    if ".." in commit_range:
        parts = commit_range.split("..", 1)
        return parts[0], parts[1]
    return None, commit_range


def cmd_validate_tdd(args: argparse.Namespace) -> None:
    """Verify test-first ordering in a commit range.

    Uses ``git log --diff-filter=A --name-only`` to collect files added in
    each commit, then classifies them as test files (matching known patterns)
    or implementation files.  A violation occurs when an implementation file
    is added in an earlier commit than any test file that shares the same
    directory root.  Warns when merge commits are detected in the range.

    Args:
        args: Parsed CLI arguments.  Expected attributes:

            - ``commit_range`` (str): Git commit range (e.g. ``HEAD~3..HEAD``).
            - ``crumb_id`` (Optional[str]): Crumb ID to check for ``tdd:
              false``.
            - ``json_output`` (bool): Emit JSON instead of human-readable text.
    """
    commit_range: str = args.commit_range
    crumb_id: Optional[str] = getattr(args, "crumb_id", None)
    json_output: bool = getattr(args, "json_output", False)

    # Honour tdd: false if a crumb ID is provided.
    if crumb_id:
        try:
            path = require_tasks_jsonl()
            tasks = read_tasks(path)
            crumb = _require_crumb(tasks, crumb_id)
            if crumb.get("tdd") is False:
                if json_output:
                    print(json.dumps({"skipped": True, "reason": "tdd: false", "crumb_id": crumb_id}, indent=2))
                else:
                    print(f"validate-tdd: SKIP — tdd: false for {crumb_id}")
                return
        except SystemExit:
            # _require_crumb / require_tasks_jsonl calls die() which exits;
            # propagate the exit rather than swallowing it.
            raise

    cwd = os.getcwd()

    # Detect merge commits in the range.
    merge_check = _git_run(
        ["log", "--merges", "--oneline", commit_range],
        cwd=cwd,
    )
    merge_commits: List[str] = [
        line.strip() for line in merge_check.stdout.splitlines() if line.strip()
    ]
    has_merges = bool(merge_commits)

    # Collect added files per commit (ordered oldest-first via --reverse).
    log_result = _git_run(
        [
            "log",
            "--reverse",
            "--diff-filter=A",
            "--name-only",
            "--format=%H",
            commit_range,
        ],
        cwd=cwd,
    )

    if log_result.returncode != 0:
        err = log_result.stderr.strip()
        die(f"git log failed: {err or '(no stderr)'}")

    # Parse output: alternating commit hash lines and file-name lines.
    # ``--format=%H`` emits a blank line before the file list for each commit.
    commits_ordered: List[str] = []      # commit hashes in reverse order (oldest first)
    commit_files: Dict[str, List[str]] = {}  # hash -> list of added files
    current_commit: Optional[str] = None

    for raw_line in log_result.stdout.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        # A full-length hex string (40 chars) is a commit hash.
        if re.fullmatch(r"[0-9a-f]{40}", line):
            current_commit = line
            commits_ordered.append(line)
            commit_files[current_commit] = []
        elif current_commit is not None:
            commit_files[current_commit].append(line)

    # Classify files and build ordered lists.
    test_files: List[Dict[str, str]] = []
    impl_files: List[Dict[str, str]] = []
    ordering_violations: List[Dict[str, str]] = []

    # Map from file path to the index of the commit that first added it.
    file_commit_index: Dict[str, int] = {}
    for idx, chash in enumerate(commits_ordered):
        for fpath in commit_files.get(chash, []):
            if fpath not in file_commit_index:
                file_commit_index[fpath] = idx
            entry = {"file": fpath, "commit": chash}
            if _is_test_file(fpath):
                test_files.append(entry)
            else:
                impl_files.append(entry)

    # Detect ordering violations: impl file added before the earliest test file.
    # We check at the directory-root level: for each impl file, check whether
    # ANY test file was added at the same commit index or earlier.
    if test_files and impl_files:
        min_test_idx = min(file_commit_index[e["file"]] for e in test_files)
        for entry in impl_files:
            impl_idx = file_commit_index[entry["file"]]
            if impl_idx < min_test_idx:
                ordering_violations.append(
                    {
                        "impl_file": entry["file"],
                        "impl_commit": entry["commit"],
                        "message": (
                            f"{entry['file']} added before any test file "
                            f"(commit {entry['commit'][:8]})"
                        ),
                    }
                )
    elif impl_files and not test_files:
        # Implementation files present but no test files added at all.
        for entry in impl_files:
            ordering_violations.append(
                {
                    "impl_file": entry["file"],
                    "impl_commit": entry["commit"],
                    "message": f"{entry['file']} added with no test files in range",
                }
            )

    verdict = "PASS" if not ordering_violations else "FAIL"

    if json_output:
        result: Dict[str, Any] = {
            "verdict": verdict,
            "commit_range": commit_range,
            "test_files": test_files,
            "impl_files": impl_files,
            "ordering_violations": ordering_violations,
        }
        if has_merges:
            result["merge_warning"] = (
                f"{len(merge_commits)} merge commit(s) detected; "
                "--diff-filter=A results may be incomplete"
            )
            result["merge_commits"] = merge_commits
        print(json.dumps(result, indent=2))
    else:
        if has_merges:
            print(
                f"warning: {len(merge_commits)} merge commit(s) detected in range; "
                "--diff-filter=A results may be incomplete",
                file=sys.stderr,
            )
        print(f"validate-tdd: {verdict}")
        print(f"  commit range : {commit_range}")
        print(f"  test files   : {len(test_files)}")
        print(f"  impl files   : {len(impl_files)}")
        if ordering_violations:
            print("  violations:")
            for v in ordering_violations:
                print(f"    {v['message']}")
        else:
            print("  no ordering violations")

    if verdict == "FAIL":
        sys.exit(1)


# ---------------------------------------------------------------------------
# Prune subcommand — remove old session directories
# ---------------------------------------------------------------------------


def cmd_prune(args: argparse.Namespace) -> None:
    """Delete session directories under .crumbs/sessions/ older than --days.

    Active sessions (mtime within ACTIVE_GUARD_MINUTES) are never deleted.
    """
    # Timezone note: age uses naive local-time datetimes on both sides,
    # so cross-timezone pruning may be off by up to one day.
    days: int = args.days
    if days < 0:
        die(f"--days must be 0 or greater, got {days}")

    crumbs_path = find_crumbs_dir()
    sessions_dir = crumbs_path / "sessions"

    if not sessions_dir.is_dir():
        if getattr(args, "json_output", False):
            print(json.dumps({"dry_run": args.dry_run, "pruned": [], "retained": []}, indent=2))
        else:
            print("nothing to prune (no sessions directory)")
        return

    # Naive local-time datetime; see timezone note in docstring.
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

    json_output: bool = getattr(args, "json_output", False)

    if args.dry_run:
        # --- JSON output branch (dry-run) ---
        if json_output:
            print(json.dumps({
                "dry_run": True,
                "pruned": [p.name for p, _ in to_prune],
                "retained": [p.name for p, _ in to_retain],
            }, indent=2))
            return

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
        # --- JSON output branch (nothing to prune) ---
        if json_output:
            print(json.dumps({
                "dry_run": False,
                "pruned": [],
                "retained": [p.name for p, _ in to_retain],
            }, indent=2))
            return
        print(f"nothing to prune (0 directories exceed {days} days)")
        return

    pruned_names: List[str] = []
    for dir_path, _age in to_prune:
        # Re-check active-session guard immediately before deletion (TOCTOU
        # mitigation: directory may have become active since enumeration).
        if _is_active_session(dir_path, time.time()):
            print(
                f"warning: skipping {dir_path.name}: became active since "
                f"enumeration (mtime within {ACTIVE_GUARD_MINUTES} minutes)",
                file=sys.stderr,
            )
            continue
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

    # --- JSON output branch (after deletion) ---
    if json_output:
        print(json.dumps({
            "dry_run": False,
            "pruned": pruned_names,
            "retained": [p.name for p, _ in to_retain],
        }, indent=2))
        return

    if pruned_names:
        names_str = ", ".join(pruned_names)
        print(f"pruned {len(pruned_names)} director{'y' if len(pruned_names) == 1 else 'ies'}: {names_str}")
    else:
        print(f"nothing to prune (0 directories exceed {days} days)")


# ---------------------------------------------------------------------------
# Session retry commands
# ---------------------------------------------------------------------------

#: Filename written by hooks/lib/retry-tracker.js inside the session directory.
_RETRIES_FILE = "retries.json"

# ---------------------------------------------------------------------------
# Session status commands
# ---------------------------------------------------------------------------

#: Progress log filename written by ant-farm hooks inside the session directory.
_PROGRESS_LOG_FILE = "progress.log"


def _parse_progress_log(session_dir: Path) -> Dict[str, Any]:
    """Parse progress.log in *session_dir* and return session position metadata.

    Reads the progress log line-by-line.  Each non-empty line uses the pipe-
    delimited format::

        TIMESTAMP|EVENT_TYPE|field=value|field=value|...

    Returns a dict with keys:

    * ``last_step`` — the EVENT_TYPE from the final non-empty line, or ``None``.
    * ``position``  — a human-readable label for the last step, or ``None``.
    * ``next_step`` — the value of the last ``next_step=`` KV field found across
                      all lines, or ``None`` when no such field exists.

    The dict values are all ``None`` when progress.log is absent, empty, or
    contains no parseable lines.

    Args:
        session_dir: Absolute path to the session directory.

    Returns:
        Dict with keys ``last_step``, ``position``, and ``next_step``.
    """
    progress_path = session_dir / _PROGRESS_LOG_FILE
    result: Dict[str, Any] = {"last_step": None, "position": None, "next_step": None}

    if not progress_path.exists():
        return result

    try:
        text = progress_path.read_text(encoding="utf-8")
    except OSError:
        return result

    lines = [ln for ln in text.splitlines() if ln.strip()]
    if not lines:
        return result

    # Extract EVENT_TYPE from the last non-empty line.
    last_line = lines[-1]
    parts = last_line.split("|")
    if len(parts) >= 2:
        result["last_step"] = parts[1].strip() or None

    # Compute a human-readable position label from last_step.
    _STEP_LABELS: Dict[str, str] = {
        "SESSION_INIT": "1/6 session-init",
        "SCOUT_COMPLETE": "2/6 scout-complete",
        "WAVE_SPAWNED": "3/6 wave-spawned",
        "WAVE_WWD_PASS": "3/6 wave-wwd-pass",
        "WAVE_VERIFIED": "3/6 wave-verified",
        "REVIEW_COMPLETE": "4/6 review-complete",
        "REVIEW_TRIAGED": "4/6 review-triaged",
        "DOCS_COMMITTED": "5/6 docs-committed",
        "XREF_VERIFIED": "5/6 xref-verified",
        "SCRIBE_COMPLETE": "5/6 scribe-complete",
        "ESV_PASS": "6/6 esv-pass",
        "SESSION_COMPLETE_PASS": "6/6 session-complete-pass",
        "SESSION_COMPLETE": "6/6 session-complete",
    }
    if result["last_step"] is not None:
        result["position"] = _STEP_LABELS.get(result["last_step"])

    # Find the last next_step= KV field across all lines.
    last_next_step = None
    for line in lines:
        fields = line.split("|")
        for field in fields[2:]:
            kv = field.strip()
            if kv.startswith("next_step="):
                value = kv[len("next_step="):]
                if value:
                    last_next_step = value
                break  # Only one next_step= per line expected.
    result["next_step"] = last_next_step

    return result


def cmd_session_status(args: argparse.Namespace) -> None:
    """Show current session position from progress.log.

    Reads progress.log from the given session directory and prints a summary
    of the current position, last completed step, and expected next step.
    Supports --json for machine-readable output.

    Args:
        args: Parsed CLI arguments.  Expects ``args.session_dir`` (str) and
              ``args.json_output`` (bool).
    """
    session_dir = Path(args.session_dir).expanduser().resolve()
    progress_path = session_dir / _PROGRESS_LOG_FILE

    if not progress_path.exists():
        if args.json_output:
            print(json.dumps({"position": None, "last_step": None, "next_step": None}))
        else:
            print("position: unknown (no progress.log found)")
        return

    data = _parse_progress_log(session_dir)

    if args.json_output:
        print(json.dumps({
            "position": data["position"],
            "last_step": data["last_step"],
            "next_step": data["next_step"],
        }))
    else:
        position_str = data["position"] if data["position"] is not None else "unknown"
        last_step_str = data["last_step"] if data["last_step"] is not None else "none"
        next_step_str = data["next_step"] if data["next_step"] is not None else "none"
        print(f"position: {position_str}")
        print(f"last step: {last_step_str}")
        print(f"next step: {next_step_str}")


def cmd_session_retries(args: argparse.Namespace) -> None:
    """Show retry counts for a session directory.

    Reads retries.json from the given session directory and prints a summary
    of retry events grouped by failure_type, plus the global total.  Supports
    --json for machine-readable output.

    Args:
        args: Parsed CLI arguments.  Expects ``args.session_dir`` (str) and
              ``args.json_output`` (bool).
    """
    session_dir = Path(args.session_dir).expanduser().resolve()
    retries_path = session_dir / _RETRIES_FILE

    if not retries_path.exists():
        if args.json_output:
            print(json.dumps({"total": 0, "by_type": {}, "events": []}))
        else:
            print("total: 0 (no retries.json found)")
        return

    try:
        with open(retries_path, "r", encoding="utf-8") as fh:
            events = json.load(fh)
    except (json.JSONDecodeError, OSError) as exc:
        die(f"cannot read retries.json: {exc}")

    if not isinstance(events, list):
        die("retries.json is malformed: expected a JSON array")

    by_type: Dict[str, int] = {}
    for event in events:
        ft = event.get("failure_type", "unknown")
        by_type[ft] = by_type.get(ft, 0) + 1

    total = len(events)

    if args.json_output:
        print(json.dumps({"total": total, "by_type": by_type, "events": events}, indent=2))
    else:
        print(f"total: {total}")
        if by_type:
            print("by type:")
            for ft, count in sorted(by_type.items()):
                print(f"  {ft}: {count}")
        else:
            print("no retry events recorded")


def cmd_session_reset_retries(args: argparse.Namespace) -> None:
    """Clear the retry log for a session directory.

    Overwrites retries.json in the given session directory with an empty JSON
    array, atomically (tmp-then-rename).  Prints a confirmation message.

    Args:
        args: Parsed CLI arguments.  Expects ``args.session_dir`` (str).
    """
    session_dir = Path(args.session_dir).expanduser().resolve()
    retries_path = session_dir / _RETRIES_FILE
    tmp_path = retries_path.with_suffix(".json.tmp")

    try:
        with open(tmp_path, "w", encoding="utf-8") as fh:
            json.dump([], fh)
            fh.write("\n")
        try:
            os.rename(str(tmp_path), str(retries_path))
        except OSError:
            tmp_path.unlink(missing_ok=True)
            raise
    except OSError as exc:
        die(f"cannot write retries.json: {exc}")

    print(f"retries reset for session: {session_dir}")


# ---------------------------------------------------------------------------
# Session agents command
# ---------------------------------------------------------------------------

#: Filename for the agent spawn accumulation file inside a session directory.
_AGENTS_FILE = "agents.json"


def cmd_session_agents(args: argparse.Namespace) -> None:
    """Show agents spawned in a session with status and elapsed time.

    Reads agents.json from the given session directory and prints a summary
    of each spawned agent including task_id, spawned_at timestamp, status,
    and elapsed time since spawn.  Supports --json for machine-readable output.

    JSON output includes an ``elapsed_minutes`` field computed at read time.

    Args:
        args: Parsed CLI arguments.  Expects ``args.session_dir`` (str) and
              ``args.json_output`` (bool).
    """
    session_dir = Path(args.session_dir).expanduser().resolve()
    agents_path = session_dir / _AGENTS_FILE

    if not agents_path.exists():
        if args.json_output:
            print(json.dumps([]))
        else:
            print("no agents recorded (agents.json not found)")
        return

    try:
        with open(agents_path, "r", encoding="utf-8") as fh:
            agents = json.load(fh)
    except (json.JSONDecodeError, OSError) as exc:
        die(f"cannot read agents.json: {exc}")

    if not isinstance(agents, list):
        die("agents.json is malformed: expected a JSON array")

    now = datetime.now(timezone.utc)

    agent_objects: List[Dict[str, Any]] = []
    for agent in agents:
        task_id = agent.get("task_id", "unknown")
        spawned_at_str = agent.get("spawned_at", "")
        status = agent.get("status", "spawned")

        # Compute elapsed time from spawn timestamp.
        elapsed_minutes: float = 0.0
        try:
            # Parse ISO 8601 UTC timestamp; strip trailing Z and attach UTC tzinfo.
            spawned_dt = datetime.fromisoformat(spawned_at_str.rstrip("Z")).replace(tzinfo=timezone.utc)
            elapsed_minutes = (now - spawned_dt).total_seconds() / 60.0
        except (ValueError, AttributeError):
            elapsed_minutes = 0.0

        agent_objects.append({
            "task_id": task_id,
            "spawned_at": spawned_at_str,
            "status": status,
            "elapsed_minutes": round(elapsed_minutes, 1),
        })

    if args.json_output:
        print(json.dumps(agent_objects, indent=2))
        return

    if not agent_objects:
        print("no agents recorded")
        return

    for obj in agent_objects:
        elapsed = obj["elapsed_minutes"]
        if elapsed >= 60:
            elapsed_str = f"{elapsed / 60:.1f}hr elapsed"
        else:
            elapsed_str = f"{elapsed:.0f}min elapsed"
        print(f"{obj['task_id']}  status={obj['status']}  spawned_at={obj['spawned_at']}  {elapsed_str}")


# ---------------------------------------------------------------------------
# Session list command
# ---------------------------------------------------------------------------

#: Filename written by /ant-farm-pause to record graceful-pause state.
_HANDOFF_FILE = "handoff.json"


def _classify_session(session_dir: Path) -> str:
    """Determine status for a session directory.

    Classification rules (in priority order):

    1. ``completed`` — ``progress.log`` contains a ``SESSION_COMPLETE`` event.
    2. ``paused``    — ``handoff.json`` exists (graceful pause via /ant-farm-pause).
    3. ``crashed``   — neither of the above (session stopped without clean handoff).

    Args:
        session_dir: Absolute path to the session directory.

    Returns:
        One of ``"completed"``, ``"paused"``, or ``"crashed"``.
    """
    progress_path = session_dir / _PROGRESS_LOG_FILE
    handoff_path = session_dir / _HANDOFF_FILE

    if progress_path.exists():
        try:
            text = progress_path.read_text(encoding="utf-8")
            for line in text.splitlines():
                parts = line.split("|")
                if len(parts) >= 2 and parts[1].strip() == "SESSION_COMPLETE":
                    return "completed"
        except OSError:
            pass

    if handoff_path.exists():
        return "paused"

    return "crashed"


def _session_last_activity(session_dir: Path) -> str:
    """Return the last-activity timestamp for a session directory as an ISO 8601 string.

    Uses the directory's mtime as a proxy for last activity.  Falls back to
    ``"unknown"`` if ``os.stat`` fails.

    Args:
        session_dir: Absolute path to the session directory.

    Returns:
        ISO 8601 datetime string (UTC, no microseconds) or ``"unknown"``.
    """
    try:
        mtime = os.stat(session_dir).st_mtime
        return datetime.utcfromtimestamp(mtime).strftime("%Y-%m-%dT%H:%M:%SZ")
    except OSError:
        return "unknown"


def cmd_session_list(args: argparse.Namespace) -> None:
    """List session directories under .crumbs/sessions/ with status and timestamp.

    Enumerates all directories under ``.crumbs/sessions/`` whose names match a
    known session prefix (``SESSION_DIR_PREFIXES``).  For each session directory,
    determines its status:

    * ``completed`` — ``progress.log`` contains a ``SESSION_COMPLETE`` event.
    * ``paused``    — ``handoff.json`` exists (graceful pause via /ant-farm-pause).
    * ``crashed``   — neither of the above.

    Supports ``--json`` for machine-readable output with fields ``id``,
    ``status``, ``last_activity``, and ``path``.

    Args:
        args: Parsed CLI arguments.  Expects ``args.json_output`` (bool).
    """
    crumbs_path = find_crumbs_dir()
    sessions_dir = crumbs_path / "sessions"

    if not sessions_dir.is_dir():
        if args.json_output:
            print(json.dumps([]))
        return

    try:
        entries = sorted(sessions_dir.iterdir())
    except OSError as exc:
        die(f"error: cannot read sessions directory: {sessions_dir}: {exc}")

    session_objects: List[Dict[str, Any]] = []
    for entry in entries:
        if not entry.is_dir():
            continue
        # Only include directories matching known session prefixes.
        if not any(entry.name.startswith(p) for p in SESSION_DIR_PREFIXES):
            continue
        # Skip entries whose timestamps are not parseable — be lenient but quiet.
        if _parse_session_dir_timestamp(entry.name) is None:
            continue

        status = _classify_session(entry)
        last_activity = _session_last_activity(entry)

        session_objects.append({
            "id": entry.name,
            "status": status,
            "last_activity": last_activity,
            "path": str(entry),
        })

    if args.json_output:
        print(json.dumps(session_objects, indent=2))
        return

    if not session_objects:
        return

    for obj in session_objects:
        print(f"{obj['id']}  status={obj['status']}  last_activity={obj['last_activity']}")


def _extract_base_file(file_entry: str) -> str:
    """Return the base filename from a scope.files entry, stripping :L<range> suffixes.

    Examples:
        ``"crumb.py:L100-200"``  → ``"crumb.py"``
        ``"crumb.py"``           → ``"crumb.py"``

    Args:
        file_entry: A string from scope.files, optionally with a line-range annotation.

    Returns:
        The file path without any ``:L<range>`` suffix.
    """
    # Strip :L<digits>-<digits> or :L<digits> suffixes
    return re.sub(r":L\d+(-\d+)?$", "", file_entry)


def _has_section_annotation(entry: str) -> bool:
    """Return True if a scope.files entry has a line-range section annotation.

    Args:
        entry: A raw scope.files string, e.g. ``"crumb.py:L100-200"``.

    Returns:
        True when the entry contains a ``:L<range>`` suffix.
    """
    return bool(re.search(r":L\d+(-\d+)?$", entry))


def _classify_risk(crumb_ids: List[str], file_entries: List[str]) -> str:
    """Determine the risk tier for a set of crumbs that reference the same base file.

    Risk tiers:
    - HIGH   — 3+ crumbs reference the same base file, OR 2+ crumbs reference the
               exact same annotated section (e.g. ``file.py:L10-20``).
    - MEDIUM — exactly 2 crumbs reference the same bare file (no section annotation
               on either entry).
    - LOW    — exactly 2 crumbs reference the same base file but with different
               explicit section annotations (different line ranges noted).

    Args:
        crumb_ids: List of crumb IDs sharing this file (deduplicated, ordered).
        file_entries: List of raw scope.files entries (including section annotations)
            that map to the same base file, in the same order as ``crumb_ids``.

    Returns:
        ``"HIGH"``, ``"MEDIUM"``, or ``"LOW"``.
    """
    if len(crumb_ids) >= 3:
        return "HIGH"
    # HIGH when two entries share the exact same explicit section annotation
    annotated = [e for e in file_entries if _has_section_annotation(e)]
    if len(annotated) != len(set(annotated)):
        return "HIGH"
    # LOW when all entries carry explicit (but distinct) section annotations
    if len(annotated) == len(file_entries) and len(file_entries) >= 2:
        return "LOW"
    # MEDIUM: same bare file, 2 crumbs, mixed or no section annotations
    return "MEDIUM"


def _greedy_wave_plan(
    conflicts: List[Dict[str, Any]], all_crumb_ids: List[str]
) -> List[List[str]]:
    """Assign crumbs to waves using greedy graph-coloring to minimize intra-wave conflicts.

    Builds a conflict graph where crumbs sharing a HIGH-risk file are connected
    by an edge.  Then applies greedy coloring: each crumb is assigned to the
    lowest-numbered wave that does not already contain a conflicting crumb.
    LOW and MEDIUM conflicts are tolerated within a wave (they can be resolved
    via rebase-before-commit).

    Args:
        conflicts: List of conflict dicts with ``"crumbs"`` and ``"risk"`` fields,
            as produced by ``cmd_conflict_matrix``.
        all_crumb_ids: Ordered list of every active crumb ID (determines iteration order).

    Returns:
        A list of waves, where each wave is a list of crumb IDs.  Wave 1 is index 0.
        Crumbs with no conflicts are placed in Wave 1.
    """
    # Build adjacency set: only HIGH-risk conflicts trigger wave separation
    neighbors: Dict[str, set] = {cid: set() for cid in all_crumb_ids}
    for conflict in conflicts:
        if conflict.get("risk") != "HIGH":
            continue
        crumbs = conflict["crumbs"]
        for i, a in enumerate(crumbs):
            for b in crumbs[i + 1 :]:
                if a in neighbors:
                    neighbors[a].add(b)
                if b in neighbors:
                    neighbors[b].add(a)

    # Greedy coloring: assign lowest available wave index to each crumb
    assignment: Dict[str, int] = {}  # crumb_id -> 0-based wave index
    for cid in all_crumb_ids:
        used_by_neighbors = {assignment[nb] for nb in neighbors[cid] if nb in assignment}
        wave_idx = 0
        while wave_idx in used_by_neighbors:
            wave_idx += 1
        assignment[cid] = wave_idx

    # Build wave lists from assignments
    if not assignment:
        return []
    max_wave = max(assignment.values())
    waves: List[List[str]] = [[] for _ in range(max_wave + 1)]
    for cid in all_crumb_ids:
        waves[assignment[cid]].append(cid)
    return waves


def cmd_conflict_matrix(args: argparse.Namespace) -> None:
    """Read open/in-progress crumbs and report file overlap conflicts with risk tiers.

    Reads all non-closed crumbs from tasks.jsonl, extracts ``scope.files`` arrays,
    builds a file-to-crumbs overlap map, assigns risk tiers (MEDIUM/HIGH), and
    outputs either a human-readable table or ``--json`` structured output.

    When ``args.wave_plan`` is True, runs greedy graph-coloring to suggest wave
    groupings that minimise intra-wave file conflicts.  With ``--json``, returns a
    structured object with ``matrix``, ``risk_tiers``, and ``wave_plan`` fields
    instead of the flat conflict array.

    Risk tiers:
    - HIGH   — 3+ crumbs share the same base file, or 2+ crumbs cite the exact
               same file:section entry.
    - MEDIUM — exactly 2 crumbs share the same base file (different sections).

    When no overlaps are detected, prints ``No file conflicts detected`` and exits 0.

    Args:
        args: Parsed CLI arguments.  Expects ``args.json_output`` (bool) and
            ``args.wave_plan`` (bool).
    """
    path = require_tasks_jsonl()
    tasks = read_tasks(path)

    # Only open and in_progress crumbs participate in conflict analysis
    active_statuses = {"open", "in_progress"}
    active = [t for t in tasks if t.get("status") in active_statuses]

    # Build: base_file -> list of (crumb_id, raw_entry) tuples
    file_to_entries: Dict[str, List[tuple]] = {}
    for crumb in active:
        scope = crumb.get("scope")
        if not isinstance(scope, dict):
            continue
        files = scope.get("files")
        if not isinstance(files, list):
            continue
        crumb_id = crumb.get("id", "?")
        for entry in files:
            if not isinstance(entry, str):
                continue
            base = _extract_base_file(entry)
            if base not in file_to_entries:
                file_to_entries[base] = []
            file_to_entries[base].append((crumb_id, entry))

    # Collect conflicts: files referenced by 2+ distinct crumbs
    conflicts: List[Dict[str, Any]] = []
    for base_file, entries in sorted(file_to_entries.items()):
        crumb_ids = [cid for cid, _ in entries]
        raw_entries = [raw for _, raw in entries]
        unique_crumb_ids = list(dict.fromkeys(crumb_ids))  # preserve order, dedupe
        if len(unique_crumb_ids) < 2:
            continue
        risk = _classify_risk(unique_crumb_ids, raw_entries)
        conflicts.append({
            "file": base_file,
            "crumbs": unique_crumb_ids,
            "risk": risk,
        })

    # Collect ordered list of all active crumb IDs with scope.files (for wave-plan)
    seen_ids: Set[str] = set()
    all_active_ids: List[str] = []
    for crumb in active:
        scope = crumb.get("scope")
        if not isinstance(scope, dict):
            continue
        if not isinstance(scope.get("files"), list):
            continue
        cid = crumb.get("id", "?")
        if cid not in seen_ids:
            seen_ids.add(cid)
            all_active_ids.append(cid)

    wave_plan = getattr(args, "wave_plan", False)

    if args.json_output:
        if wave_plan:
            waves = _greedy_wave_plan(conflicts, all_active_ids)
            risk_tiers = {
                entry["file"]: entry["risk"] for entry in conflicts
            }
            print(json.dumps({
                "matrix": conflicts,
                "risk_tiers": risk_tiers,
                "wave_plan": waves,
            }, indent=2))
        else:
            print(json.dumps(conflicts, indent=2))
        return

    if wave_plan:
        waves = _greedy_wave_plan(conflicts, all_active_ids)
        if not waves:
            print("No active crumbs with scope.files found")
            return
        print("Suggested wave plan (greedy graph-coloring by file conflicts):")
        print()
        for i, wave in enumerate(waves, start=1):
            print(f"Wave {i}: {', '.join(wave)}")
        return

    if not conflicts:
        print("No file conflicts detected")
        return

    # Human-readable table output
    print(f"{'FILE':<50} {'CRUMBS':<30} RISK")
    print("-" * 90)
    for entry in conflicts:
        file_str = entry["file"]
        crumbs_str = ", ".join(entry["crumbs"])
        risk_str = entry["risk"]
        print(f"{file_str:<50} {crumbs_str:<30} {risk_str}")


#: Pattern that matches REQ-N: headings in a spec file.
#: Matches lines like "## REQ-1: Description" or "### REQ-42: ..." (any heading level).
_REQ_HEADING_RE: re.Pattern[str] = re.compile(
    r"^#{1,6}\s+(REQ-\d+)\s*:", re.MULTILINE
)


def _extract_req_ids(spec_text: str) -> List[str]:
    """Return a list of unique REQ-N identifiers from a spec file, in order of appearance.

    Matches headings of the form ``## REQ-1:``, ``### REQ-42:``, etc. (any heading level).

    Args:
        spec_text: Full text of the spec markdown file.

    Returns:
        Ordered list of unique REQ IDs (e.g. ``["REQ-1", "REQ-2"]``).
    """
    seen: Dict[str, None] = {}
    for match in _REQ_HEADING_RE.finditer(spec_text):
        req_id = match.group(1)
        seen[req_id] = None
    return list(seen.keys())


def cmd_validate_coverage(args: argparse.Namespace) -> None:
    """Validate that every REQ-N heading in a spec is covered by at least one crumb.

    Reads the spec file at ``args.spec_file``, extracts all ``REQ-N:`` headings,
    then reads all open/in-progress crumbs from tasks.jsonl and maps their
    ``requirements`` arrays to the extracted REQ IDs.

    Output:
    - **covered**: REQs with at least one open/in-progress crumb listing them.
    - **uncovered**: REQs with no covering crumb.
    - **unmapped**: Crumb IDs that have no ``requirements`` field (migration warning).

    Exit codes:
    - ``0`` — all REQs are covered (or the spec has no REQs).
    - ``1`` — one or more REQs are uncovered, or the spec file is not found.

    Args:
        args: Parsed CLI arguments.  Expected attributes:

            - ``spec_file`` (str): Path to the spec markdown file.
            - ``json_output`` (bool): Emit JSON instead of human-readable text.
    """
    spec_path = Path(args.spec_file)
    if not spec_path.exists():
        die(f"spec file not found: {spec_path}")

    try:
        spec_text = spec_path.read_text(encoding="utf-8")
    except OSError as exc:
        die(f"cannot read spec file: {exc}")

    req_ids = _extract_req_ids(spec_text)

    path = require_tasks_jsonl()
    tasks = read_tasks(path)

    active_statuses = {"open", "in_progress"}
    active = [t for t in tasks if t.get("status") in active_statuses]

    # Build: req_id -> list of covering crumb IDs
    coverage: Dict[str, List[str]] = {req: [] for req in req_ids}
    unmapped: List[str] = []

    for crumb in active:
        crumb_id = crumb.get("id", "?")
        reqs = crumb.get("requirements")
        if reqs is None:
            unmapped.append(crumb_id)
            continue
        if not isinstance(reqs, list):
            unmapped.append(crumb_id)
            continue
        for req in reqs:
            if isinstance(req, str) and req in coverage:
                coverage[req].append(crumb_id)

    covered: List[Dict[str, Any]] = []
    uncovered: List[str] = []
    for req_id in req_ids:
        covering = coverage[req_id]
        if covering:
            covered.append({"req": req_id, "crumbs": covering})
        else:
            uncovered.append(req_id)

    fully_covered = len(uncovered) == 0

    if args.json_output:
        print(json.dumps({
            "covered": covered,
            "uncovered": uncovered,
            "unmapped": unmapped,
        }, indent=2))
        if not fully_covered:
            sys.exit(1)
        return

    # Human-readable output
    if covered:
        print(f"Covered ({len(covered)}):")
        for entry in covered:
            crumbs_str = ", ".join(entry["crumbs"])
            print(f"  {entry['req']:<10} covered by: {crumbs_str}")

    if uncovered:
        print(f"Uncovered ({len(uncovered)}):")
        for req_id in uncovered:
            print(f"  {req_id}")

    if unmapped:
        print(f"Warning: {len(unmapped)} crumb(s) have no requirements field: "
              f"{', '.join(unmapped)}")

    if not req_ids:
        print("No REQ headings found in spec — nothing to validate.")

    if not fully_covered:
        sys.exit(1)


# ---------------------------------------------------------------------------
# Argument parser
# ---------------------------------------------------------------------------


def build_parser() -> argparse.ArgumentParser:
    """Build and return the top-level argument parser with all subcommands."""
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
            "  validate-trail  Validate trail granularity constraints\n"
            "  tree        Show trail/crumb hierarchy\n"
            "  import      Bulk import from JSONL\n"
            "  doctor      Validate tasks.jsonl integrity\n"
            "  init        Bootstrap .crumbs/ directory structure\n"
            "  prune       Delete old session directories under .crumbs/sessions/\n"
            "  render-template  Expand {{SLOT_NAME}} placeholders in a template file\n"
            "  session-retries  Show retry counts for a session directory\n"
            "  session-reset-retries  Clear the retry log for a session directory\n"
            "  session-status   Show current position, last step, and next step for a session\n"
            "  session-list     List all session directories with status and last activity\n"
            "  validate-tdd     Verify test-first ordering in a commit range\n"
            "  conflict-matrix  Report file overlap conflicts between open crumbs\n"
            "  validate-coverage  Validate REQ coverage across open crumbs\n"
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
    _add_json_flag(p_list)
    p_list.set_defaults(func=cmd_list)

    # --- show ---
    p_show = sub.add_parser("show", help="Show full detail for a crumb or trail")
    p_show.add_argument("id", metavar="ID")
    _add_json_flag(p_show)
    p_show.set_defaults(func=cmd_show)

    # --- create ---
    p_create = sub.add_parser("create", help="Create a new crumb")
    p_create.add_argument("--title", metavar="TITLE")
    p_create.add_argument("--from-json", dest="from_json", metavar="JSON")
    p_create.add_argument("--from-file", dest="from_file", metavar="PATH")
    p_create.add_argument("--priority", choices=VALID_PRIORITIES)
    p_create.add_argument("--type", dest="crumb_type", choices=["task", "bug", "feature"])
    p_create.add_argument("--description", metavar="TEXT")
    tdd_group = p_create.add_mutually_exclusive_group()
    tdd_group.add_argument("--tdd", dest="tdd", action="store_true", default=None,
                           help="Enable TDD for this crumb (default)")
    tdd_group.add_argument("--no-tdd", dest="tdd", action="store_false",
                           help="Disable TDD for this crumb")
    p_create.set_defaults(tdd=None)
    _add_json_flag(p_create)
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
    tdd_update_group = p_update.add_mutually_exclusive_group()
    tdd_update_group.add_argument("--tdd", dest="tdd", action="store_true", default=None,
                                  help="Enable TDD for this crumb")
    tdd_update_group.add_argument("--no-tdd", dest="tdd", action="store_false",
                                  help="Disable TDD for this crumb")
    p_update.set_defaults(tdd=None)
    _add_json_flag(p_update)
    p_update.set_defaults(func=cmd_update)

    # --- close ---
    p_close = sub.add_parser("close", help="Close one or more crumbs")
    p_close.add_argument("ids", nargs="+", metavar="ID")
    _add_json_flag(p_close)
    p_close.set_defaults(func=cmd_close)

    # --- reopen ---
    p_reopen = sub.add_parser("reopen", help="Reopen a closed crumb")
    p_reopen.add_argument("id", metavar="ID")
    _add_json_flag(p_reopen)
    p_reopen.set_defaults(func=cmd_reopen)

    # --- ready ---
    p_ready = sub.add_parser("ready", help="List ready crumbs (no unresolved blockers)")
    p_ready.add_argument("--limit", type=int, metavar="N")
    p_ready.add_argument(
        "--sort",
        choices=["priority", "created_at", "status"],
        default="created_at",
    )
    _add_json_flag(p_ready)
    p_ready.set_defaults(func=cmd_ready)

    # --- blocked ---
    p_blocked = sub.add_parser("blocked", help="List blocked crumbs")
    _add_json_flag(p_blocked)
    p_blocked.set_defaults(func=cmd_blocked)

    # --- link ---
    p_link = sub.add_parser("link", help="Manage crumb links")
    p_link.add_argument("id", metavar="ID")
    p_link.add_argument("--parent", metavar="ID", dest="link_parent")
    p_link.add_argument("--blocked-by", metavar="ID", dest="blocked_by")
    p_link.add_argument("--remove-blocked-by", metavar="ID", dest="remove_blocked_by")
    p_link.add_argument("--discovered-from", metavar="ID", dest="discovered_from")
    _add_json_flag(p_link)
    p_link.set_defaults(func=cmd_link)

    # --- search ---
    p_search = sub.add_parser("search", help="Full-text search titles and descriptions")
    p_search.add_argument("query", metavar="QUERY")
    _add_json_flag(p_search)
    p_search.set_defaults(func=cmd_search)

    # --- trail ---
    p_trail = sub.add_parser("trail", help="Trail subcommands")
    trail_sub = p_trail.add_subparsers(dest="trail_command", metavar="<trail-subcommand>")

    p_trail_list = trail_sub.add_parser("list", help="List trails with completion counts")
    _add_json_flag(p_trail_list)
    p_trail_list.set_defaults(func=cmd_trail, trail_command="list")

    p_trail_show = trail_sub.add_parser("show", help="Show trail detail and child crumbs")
    p_trail_show.add_argument("id", metavar="ID")
    _add_json_flag(p_trail_show)
    p_trail_show.set_defaults(func=cmd_trail, trail_command="show")

    p_trail_create = trail_sub.add_parser("create", help="Create a trail")
    p_trail_create.add_argument("--title", required=True, metavar="TITLE")
    p_trail_create.add_argument("--description", metavar="TEXT")
    p_trail_create.add_argument("--priority", choices=VALID_PRIORITIES)
    p_trail_create.add_argument(
        "--acceptance-criteria", dest="acceptance_criteria", metavar="TEXT", action="append"
    )
    _add_json_flag(p_trail_create)
    p_trail_create.set_defaults(func=cmd_trail, trail_command="create")

    p_trail_close = trail_sub.add_parser("close", help="Close a trail")
    p_trail_close.add_argument("id", metavar="ID")
    p_trail_close.set_defaults(func=cmd_trail, trail_command="close")

    p_trail.set_defaults(func=cmd_trail)

    # --- validate-trail ---
    p_validate_trail = sub.add_parser(
        "validate-trail",
        help="Validate trail granularity constraints (crumb count, file count per crumb)",
    )
    p_validate_trail.add_argument(
        "id",
        nargs="?",
        metavar="ID",
        help="Trail ID to validate (omit when using --all)",
    )
    p_validate_trail.add_argument(
        "--all",
        action="store_true",
        dest="all_trails",
        help="Validate every trail in tasks.jsonl",
    )
    p_validate_trail.add_argument(
        "--strict",
        action="store_true",
        help="Exit code 1 when any trail has FAIL status",
    )
    _add_json_flag(p_validate_trail)
    p_validate_trail.set_defaults(func=cmd_validate_trail)

    # --- validate-spec ---
    p_validate_spec = sub.add_parser(
        "validate-spec",
        help="Scan a spec file's acceptance criteria for banned phrases",
    )
    p_validate_spec.add_argument(
        "spec_file",
        metavar="FILE",
        help="Path to the spec markdown file to validate",
    )
    _add_json_flag(p_validate_spec)
    p_validate_spec.set_defaults(func=cmd_validate_spec)

    # --- validate-tdd ---
    p_validate_tdd = sub.add_parser(
        "validate-tdd",
        help="Verify test-first ordering in a commit range",
    )
    p_validate_tdd.add_argument(
        "commit_range",
        metavar="COMMIT_RANGE",
        help="Git commit range to inspect (e.g. HEAD~3..HEAD or a single ref)",
    )
    p_validate_tdd.add_argument(
        "--crumb-id",
        dest="crumb_id",
        metavar="ID",
        default=None,
        help="Crumb ID to check for tdd: false (skips check when disabled)",
    )
    _add_json_flag(p_validate_tdd)
    p_validate_tdd.set_defaults(func=cmd_validate_tdd)

    # --- tree ---
    p_tree = sub.add_parser("tree", help="Show trail/crumb hierarchy")
    p_tree.add_argument("id", nargs="?", metavar="ID")
    _add_json_flag(p_tree)
    p_tree.set_defaults(func=cmd_tree)

    # --- import ---
    p_import = sub.add_parser("import", help="Bulk import from JSONL")
    p_import.add_argument("file", metavar="FILE")
    _add_json_flag(p_import)
    p_import.set_defaults(func=cmd_import)

    # --- doctor ---
    p_doctor = sub.add_parser("doctor", help="Validate tasks.jsonl integrity")
    p_doctor.add_argument(
        "--fix",
        action="store_true",
        help="Remove dangling blocked_by references automatically",
    )
    _add_json_flag(p_doctor)
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
    _add_json_flag(p_init)
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
    _add_json_flag(p_render_template)
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
    _add_json_flag(p_prune)
    p_prune.set_defaults(func=cmd_prune)

    # --- session-retries ---
    p_session_retries = sub.add_parser(
        "session-retries",
        help="Show retry counts for a session directory",
    )
    p_session_retries.add_argument(
        "session_dir",
        metavar="SESSION_DIR",
        help="Path to the session directory containing retries.json",
    )
    _add_json_flag(p_session_retries)
    p_session_retries.set_defaults(func=cmd_session_retries)

    # --- session-reset-retries ---
    p_session_reset_retries = sub.add_parser(
        "session-reset-retries",
        help="Clear the retry log for a session directory",
    )
    p_session_reset_retries.add_argument(
        "session_dir",
        metavar="SESSION_DIR",
        help="Path to the session directory containing retries.json",
    )
    p_session_reset_retries.set_defaults(func=cmd_session_reset_retries)

    # --- session-agents ---
    p_session_agents = sub.add_parser(
        "session-agents",
        help="Show agents spawned in a session with status and elapsed time",
    )
    p_session_agents.add_argument(
        "session_dir",
        metavar="SESSION_DIR",
        help="Path to the session directory containing agents.json",
    )
    _add_json_flag(p_session_agents)
    p_session_agents.set_defaults(func=cmd_session_agents)

    # --- session-status ---
    p_session_status = sub.add_parser(
        "session-status",
        help="Show current position, last step, and expected next step for a session",
    )
    p_session_status.add_argument(
        "session_dir",
        metavar="SESSION_DIR",
        help="Path to the session directory containing progress.log",
    )
    _add_json_flag(p_session_status)
    p_session_status.set_defaults(func=cmd_session_status)

    # --- session-list ---
    p_session_list = sub.add_parser(
        "session-list",
        help="List all session directories under .crumbs/sessions/ with status and last activity",
    )
    _add_json_flag(p_session_list)
    p_session_list.set_defaults(func=cmd_session_list)

    # --- conflict-matrix ---
    p_conflict_matrix = sub.add_parser(
        "conflict-matrix",
        help="Report file overlap conflicts between open/in-progress crumbs",
    )
    _add_json_flag(p_conflict_matrix)
    p_conflict_matrix.add_argument(
        "--wave-plan",
        dest="wave_plan",
        action="store_true",
        default=False,
        help="Output suggested wave groupings using greedy graph-coloring to minimize intra-wave file conflicts",
    )
    p_conflict_matrix.set_defaults(func=cmd_conflict_matrix)

    # --- validate-coverage ---
    p_validate_coverage = sub.add_parser(
        "validate-coverage",
        help="Validate that every REQ-N heading in a spec is covered by open crumbs",
    )
    p_validate_coverage.add_argument(
        "spec_file",
        metavar="SPEC_FILE",
        help="Path to the spec markdown file containing REQ-N: headings",
    )
    _add_json_flag(p_validate_coverage)
    p_validate_coverage.set_defaults(func=cmd_validate_coverage)

    return parser


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def main() -> None:
    """Parse arguments and dispatch to the appropriate subcommand handler."""
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

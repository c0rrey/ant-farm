#!/usr/bin/env python3
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
"""

from __future__ import annotations

import argparse
import fcntl
import json
import os
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterator, List, Optional

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
# Error helpers
# ---------------------------------------------------------------------------


def die(message: str, code: int = 1) -> None:
    """Print error to stderr and exit with given code."""
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
                "Run /ant-farm:init first."
            )
        current = parent


def crumbs_dir() -> Path:
    """Return the .crumbs/ directory, exiting if not found."""
    return find_crumbs_dir()


def tasks_path() -> Path:
    """Return path to tasks.jsonl, exiting if .crumbs/ not found."""
    return crumbs_dir() / TASKS_FILE


def config_path() -> Path:
    """Return path to config.json, exiting if .crumbs/ not found."""
    return crumbs_dir() / CONFIG_FILE


def lock_path() -> Path:
    """Return path to tasks.lock, exiting if .crumbs/ not found."""
    return crumbs_dir() / LOCK_FILE


# ---------------------------------------------------------------------------
# Config read / write
# ---------------------------------------------------------------------------


def read_config() -> Dict[str, Any]:
    """Read config.json, returning defaults merged with stored values.

    Returns:
        Dict with keys: prefix, default_priority, next_crumb_id, next_trail_id.
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
    return config


def write_config(config: Dict[str, Any]) -> None:
    """Atomically write config.json.

    Args:
        config: Dict to serialise.
    """
    path = config_path()
    tmp_path = path.with_suffix(".json.tmp")
    try:
        with open(tmp_path, "w", encoding="utf-8") as fh:
            json.dump(config, fh, indent=2)
            fh.write("\n")
        os.rename(str(tmp_path), str(path))
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
    """
    records: List[Dict[str, Any]] = []
    with open(path, "r", encoding="utf-8") as fh:
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
    """
    tmp_path = path.with_suffix(".jsonl.tmp")
    try:
        with open(tmp_path, "w", encoding="utf-8") as fh:
            for record in records:
                fh.write(json.dumps(record, separators=(",", ":")) + "\n")
        os.rename(str(tmp_path), str(path))
    except OSError as exc:
        die(f"cannot write {path.name}: {exc}")


def iter_jsonl(path: Path) -> Iterator[Dict[str, Any]]:
    """Yield parsed records from a JSONL file, skipping malformed lines.

    Args:
        path: Path to the JSONL file.

    Yields:
        Parsed dict records.
    """
    with open(path, "r", encoding="utf-8") as fh:
        for lineno, line in enumerate(fh, start=1):
            line = line.rstrip("\n")
            if not line:
                continue
            try:
                yield json.loads(line)
            except json.JSONDecodeError as exc:
                print(
                    f"warning: skipping malformed JSON on line {lineno}: {exc}",
                    file=sys.stderr,
                )


# ---------------------------------------------------------------------------
# File locking — exclusive flock on tasks.lock
# ---------------------------------------------------------------------------


class FileLock:
    """Context manager that holds an exclusive flock on tasks.lock.

    Blocks until the lock is acquired. The lock is released on __exit__.

    Usage::

        with FileLock():
            # read, modify, write tasks.jsonl safely
    """

    def __init__(self) -> None:
        self._lock_file: Optional[Any] = None

    def __enter__(self) -> "FileLock":
        path = lock_path()
        # Ensure the lock file exists
        path.touch()
        self._lock_file = open(path, "w", encoding="utf-8")
        fcntl.flock(self._lock_file, fcntl.LOCK_EX)
        return self

    def __exit__(self, *_: Any) -> None:
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
    """Return current UTC time as an ISO 8601 string with Z suffix."""
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
        die("no .crumbs/tasks.jsonl found. Run /ant-farm:init first.")
    return path


# ---------------------------------------------------------------------------
# Subcommand stubs — placeholders for downstream tasks
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
        results = [t for t in results if t.get("agent_type") == args.agent_type]

    if args.parent:
        results = [t for t in results if t.get("parent") == args.parent]

    if args.discovered:
        results = [t for t in results if t.get("discovered_from")]

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

    Accepts either --title with optional flags, or --from-json with a
    JSON object containing explicit fields. Auto-assigns an ID from
    config if not provided in the JSON payload.

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

        if args.from_json:
            try:
                payload: Dict[str, Any] = json.loads(args.from_json)
            except json.JSONDecodeError as exc:
                die(f"invalid JSON in --from-json: {exc}")

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
                die("--title is required unless --from-json is provided")
            payload = {"title": args.title}
            if args.priority:
                payload["priority"] = args.priority
            if args.crumb_type:
                payload["type"] = args.crumb_type
            if args.description:
                payload["description"] = args.description

        # --- assign ID ---
        if "id" in payload and payload["id"]:
            crumb_id = str(payload["id"])
            # Duplicate detection
            if _find_crumb(tasks, crumb_id) is not None:
                die(f"crumb '{crumb_id}' already exists")
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
            if current_status == "closed" and args.status != "open":
                die(
                    f"cannot transition from 'closed' to '{args.status}'. "
                    f"Use 'crumb reopen {args.id}' to reopen first."
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

        closed: List[str] = []
        skipped: List[str] = []

        for crumb_id in args.ids:
            crumb = _find_crumb(tasks, crumb_id)
            if crumb is None:
                die(f"crumb '{crumb_id}' not found")

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


def cmd_ready(args: argparse.Namespace) -> None:
    """List ready crumbs (no unresolved blockers). Implemented downstream."""
    die("crumb ready not yet implemented")


def cmd_blocked(args: argparse.Namespace) -> None:
    """List blocked crumbs. Implemented downstream."""
    die("crumb blocked not yet implemented")


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

    print(f"updated links for {args.id}")


def cmd_search(args: argparse.Namespace) -> None:
    """Full-text search crumbs. Implemented downstream."""
    die("crumb search not yet implemented")


def cmd_trail(args: argparse.Namespace) -> None:
    """Trail subcommands. Implemented downstream."""
    die("crumb trail not yet implemented")


def cmd_tree(args: argparse.Namespace) -> None:
    """Show crumb hierarchy. Implemented downstream."""
    die("crumb tree not yet implemented")


def cmd_import(args: argparse.Namespace) -> None:
    """Import crumbs from a JSONL file. Implemented downstream."""
    die("crumb import not yet implemented")


def cmd_doctor(args: argparse.Namespace) -> None:
    """Validate tasks.jsonl integrity. Implemented downstream."""
    die("crumb doctor not yet implemented")


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
    p_doctor.set_defaults(func=cmd_doctor)

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

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


def cmd_list(args: argparse.Namespace) -> None:
    """List crumbs. Implemented by ant-farm-l7pk."""
    die("crumb list not yet implemented")


def cmd_show(args: argparse.Namespace) -> None:
    """Show a crumb or trail. Implemented by ant-farm-l7pk."""
    die("crumb show not yet implemented")


def cmd_create(args: argparse.Namespace) -> None:
    """Create a crumb. Implemented by ant-farm-l7pk."""
    die("crumb create not yet implemented")


def cmd_update(args: argparse.Namespace) -> None:
    """Update a crumb. Implemented downstream."""
    die("crumb update not yet implemented")


def cmd_close(args: argparse.Namespace) -> None:
    """Close one or more crumbs. Implemented downstream."""
    die("crumb close not yet implemented")


def cmd_reopen(args: argparse.Namespace) -> None:
    """Reopen a closed crumb. Implemented downstream."""
    die("crumb reopen not yet implemented")


def cmd_ready(args: argparse.Namespace) -> None:
    """List ready crumbs (no unresolved blockers). Implemented downstream."""
    die("crumb ready not yet implemented")


def cmd_blocked(args: argparse.Namespace) -> None:
    """List blocked crumbs. Implemented downstream."""
    die("crumb blocked not yet implemented")


def cmd_link(args: argparse.Namespace) -> None:
    """Manage crumb links. Implemented downstream."""
    die("crumb link not yet implemented")


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

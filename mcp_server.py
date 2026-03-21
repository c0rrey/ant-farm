#!/usr/bin/env python3
"""MCP server wrapping crumb.py task-tracker functions.

Exposes six tools that map directly to crumb CLI commands:

  crumb_list    — list tasks with optional filters
  crumb_show    — show all fields for a single crumb
  crumb_update  — update crumb fields or append a note
  crumb_query   — full-text search across titles and descriptions
  crumb_create  — create a new crumb
  crumb_doctor  — validate tasks.jsonl integrity

All tools return structured JSON matching the ``crumb <command> --json``
CLI output schema.  Blocking ``fcntl.flock`` calls are run in a thread
executor (via ``asyncio.to_thread``) to prevent event-loop stalling.
Atomic temp+rename writes in crumb.py guarantee tasks.jsonl remains
consistent even if the server process terminates unexpectedly.

Requires Python >=3.10 and the ``mcp`` package (``pip install mcp``).

Usage (stdio transport, for Claude Code MCP integration)::

    python3 mcp_server.py

    # Or via MCP stdio launcher
    mcp run mcp_server.py
"""

from __future__ import annotations

import argparse
import asyncio
import contextlib
import io
import json
import threading
from typing import Any, Optional

from mcp.server.fastmcp import FastMCP

# ---------------------------------------------------------------------------
# Import crumb functions
# ---------------------------------------------------------------------------

# crumb.py is a single-file CLI living in the same directory.  We import
# its public symbols directly to avoid subprocess overhead and to reuse
# its FileLock / atomic-write machinery without modification.
import crumb as _crumb

# ---------------------------------------------------------------------------
# MCP server instance
# ---------------------------------------------------------------------------

mcp = FastMCP(
    "crumb",
    instructions=(
        "Task tracker tools for the ant-farm project. "
        "Use crumb_list to browse tasks, crumb_show to inspect a single task, "
        "crumb_update to change status/fields, crumb_create to add new tasks, "
        "crumb_query to search, and crumb_doctor to validate integrity."
    ),
)

# ---------------------------------------------------------------------------
# Thread-safe stdout capture helper
# ---------------------------------------------------------------------------

# ``contextlib.redirect_stdout`` modifies ``sys.stdout`` globally, which is
# not thread-safe: concurrent calls would interleave their output into each
# other's buffer.  This lock serialises stdout-capture sections so that only
# one thread redirects stdout at a time.  The crumb ``FileLock`` already
# serialises file writes; this lock only adds mutual exclusion around the
# stdout redirect itself (which is very brief).
_stdout_lock = threading.Lock()


def _run_cmd_json(fn: Any, args: argparse.Namespace) -> Any:
    """Call a crumb command function and return its parsed JSON output.

    Redirects stdout so the JSON printed by the ``--json`` output branch is
    captured rather than written to the process stdout.  The redirect is
    protected by ``_stdout_lock`` so concurrent thread-pool calls do not
    interleave their output into each other's capture buffers.

    Each call is executed synchronously in the calling thread — callers are
    responsible for dispatching to a thread executor when ``fn`` involves
    blocking I/O (i.e., any command that acquires ``FileLock``).

    Args:
        fn: A crumb ``cmd_*`` function (e.g. ``crumb.cmd_list``).
        args: Pre-built ``argparse.Namespace`` with ``json_output=True``.

    Returns:
        The Python object produced by ``json.loads`` of the captured output.

    Raises:
        ValueError: If the captured stdout is empty or not valid JSON.
        SystemExit: Re-raised if the crumb function exits non-zero (e.g.
            crumb_list when no .crumbs/ directory is found).
    """
    buf = io.StringIO()
    with _stdout_lock:
        with contextlib.redirect_stdout(buf):
            fn(args)
    raw = buf.getvalue().strip()
    if not raw:
        raise ValueError(
            f"Command '{getattr(fn, '__name__', fn)}' produced no output — "
            "expected JSON but stdout was empty."
        )
    return json.loads(raw)


# ---------------------------------------------------------------------------
# Tool: crumb_list
# ---------------------------------------------------------------------------


@mcp.tool(
    description=(
        "List crumbs (tasks/bugs/features) with optional filters. "
        "Returns a JSON array of crumb objects."
    )
)
async def crumb_list(
    status: Optional[str] = None,
    priority: Optional[str] = None,
    crumb_type: Optional[str] = None,
    parent: Optional[str] = None,
    agent_type: Optional[str] = None,
    limit: Optional[int] = None,
    sort: str = "created_at",
    discovered: bool = False,
    after: Optional[str] = None,
) -> list[dict[str, Any]]:
    """List crumbs with optional filters.

    Args:
        status: Filter by status: "open", "closed", or "in_progress".
            Omit for all statuses.
        priority: Filter by priority: "P0", "P1", "P2", "P3", or "P4".
        crumb_type: Filter by type: "task", "bug", or "feature".
        parent: Filter by parent trail ID (e.g. "AF-T1").
        agent_type: Filter by agent_type in scope.
        limit: Maximum number of results to return.
        sort: Sort field — "priority", "status", or "created_at" (default).
        discovered: If true, only return crumbs with a discovered_from link.
        after: ISO 8601 date string; return only crumbs created after this date.

    Returns:
        List of crumb objects, each matching the crumb --json schema.
    """
    args = argparse.Namespace(
        filter_open=(status == "open"),
        filter_closed=(status == "closed"),
        filter_in_progress=(status == "in_progress"),
        priority=priority,
        filter_type=crumb_type,
        agent_type=agent_type,
        parent=parent,
        discovered=discovered,
        after=after,
        sort=sort,
        limit=limit,
        short=False,
        json_output=True,
    )
    return await asyncio.to_thread(_run_cmd_json, _crumb.cmd_list, args)


# ---------------------------------------------------------------------------
# Tool: crumb_show
# ---------------------------------------------------------------------------


@mcp.tool(
    description=(
        "Show all fields for a single crumb. "
        "Returns a single JSON object with the full crumb record."
    )
)
async def crumb_show(crumb_id: str) -> dict[str, Any]:
    """Show all fields for a single crumb or trail.

    Args:
        crumb_id: The crumb ID to look up (e.g. "AF-123" or "AF-T1").

    Returns:
        Full crumb object matching the crumb --json schema.

    Raises:
        RuntimeError: If the crumb ID is not found.
    """
    args = argparse.Namespace(id=crumb_id, json_output=True)
    try:
        return await asyncio.to_thread(_run_cmd_json, _crumb.cmd_show, args)
    except SystemExit as exc:
        raise RuntimeError(f"crumb '{crumb_id}' not found") from exc


# ---------------------------------------------------------------------------
# Tool: crumb_update
# ---------------------------------------------------------------------------


@mcp.tool(
    description=(
        "Update crumb fields or append a note. "
        "Returns the updated crumb as JSON with a 'success' field."
    )
)
async def crumb_update(
    crumb_id: str,
    status: Optional[str] = None,
    title: Optional[str] = None,
    priority: Optional[str] = None,
    description: Optional[str] = None,
    note: Optional[str] = None,
) -> dict[str, Any]:
    """Update crumb fields or append a note.

    Args:
        crumb_id: The crumb ID to update (e.g. "AF-123").
        status: New status: "open" or "in_progress". To close a crumb, use
            ``crumb close <id>`` via the CLI (no MCP tool for close exists).
        title: New title string.
        priority: New priority: "P0", "P1", "P2", "P3", or "P4".
        description: New description string.
        note: Text to append as a timestamped note.

    Returns:
        Dict with "success": true and the full updated crumb, or
        {"success": false, "message": "no changes"} when nothing changed.

    Raises:
        RuntimeError: If the crumb ID is not found or the transition is invalid.
    """
    args = argparse.Namespace(
        id=crumb_id,
        status=status,
        title=title,
        priority=priority,
        description=description,
        note=note,
        from_json=None,
        json_output=True,
    )
    try:
        return await asyncio.to_thread(_run_cmd_json, _crumb.cmd_update, args)
    except SystemExit as exc:
        raise RuntimeError(f"crumb_update failed for '{crumb_id}'") from exc


# ---------------------------------------------------------------------------
# Tool: crumb_query (search)
# ---------------------------------------------------------------------------


@mcp.tool(
    description=(
        "Full-text search across crumb titles and descriptions. "
        "Returns a JSON array of matching crumb objects."
    )
)
async def crumb_query(query: str) -> list[dict[str, Any]]:
    """Search crumbs by title or description text.

    Case-insensitive substring match across all crumb titles and descriptions.

    Args:
        query: Search string (case-insensitive substring match).

    Returns:
        List of crumb objects whose title or description contains the query.
    """
    args = argparse.Namespace(query=query, json_output=True)
    return await asyncio.to_thread(_run_cmd_json, _crumb.cmd_search, args)


# ---------------------------------------------------------------------------
# Tool: crumb_create
# ---------------------------------------------------------------------------


@mcp.tool(
    description=(
        "Create a new crumb. "
        "Returns the newly created crumb as a JSON object."
    )
)
async def crumb_create(
    title: str,
    priority: Optional[str] = None,
    crumb_type: Optional[str] = None,
    description: Optional[str] = None,
    from_json: Optional[str] = None,
) -> dict[str, Any]:
    """Create a new crumb and return it.

    Args:
        title: Required title for the new crumb.
        priority: Priority level: "P0", "P1", "P2", "P3", or "P4".
            Defaults to project default (typically "P2").
        crumb_type: Type: "task", "bug", or "feature". Defaults to "task".
        description: Optional description text.
        from_json: Optional JSON string with additional fields to set on
            the new crumb (e.g. '{"scope": {"files": ["foo.py"]}}').

    Returns:
        The newly created crumb object matching the crumb --json schema.

    Raises:
        RuntimeError: If creation fails (e.g. invalid priority or type).
    """
    args = argparse.Namespace(
        title=title,
        priority=priority,
        crumb_type=crumb_type,
        description=description,
        from_json=from_json,
        from_file=None,
        json_output=True,
    )
    try:
        return await asyncio.to_thread(_run_cmd_json, _crumb.cmd_create, args)
    except SystemExit as exc:
        raise RuntimeError("crumb_create failed") from exc


# ---------------------------------------------------------------------------
# Tool: crumb_doctor
# ---------------------------------------------------------------------------


@mcp.tool(
    description=(
        "Validate tasks.jsonl integrity. "
        "Returns a JSON diagnostic report with errors, warnings, and fix results."
    )
)
async def crumb_doctor(fix: bool = False) -> dict[str, Any]:
    """Validate tasks.jsonl integrity and optionally repair issues.

    Checks for: malformed JSON lines, duplicate IDs, dangling parent links,
    dangling blocked_by references, and orphan crumbs.

    Args:
        fix: If true, automatically remove dangling blocked_by references.

    Returns:
        Diagnostic report with fields:
            ok (bool): True when error_count is 0.
            error_count (int): Number of errors found.
            warning_count (int): Number of warnings found.
            errors (list[str]): Error descriptions.
            warnings (list[str]): Warning descriptions.
            fixes_applied (list[str]): Descriptions of repairs made (if fix=True).
    """
    args = argparse.Namespace(fix=fix, json_output=True)

    def _run_doctor() -> Any:
        # crumb_doctor exits with code 1 when errors are found; catch that
        # and still return the report (caller inspects via 'ok': false).
        buf = io.StringIO()
        try:
            with _stdout_lock:
                with contextlib.redirect_stdout(buf):
                    _crumb.cmd_doctor(args)
        except SystemExit as exc:
            # Exit code 1 means doctor found errors but still printed its
            # JSON report — suppress it so the caller can inspect the report.
            # Any other exit code (e.g. missing .crumbs/ dir) is unexpected
            # infrastructure failure and must propagate.
            if exc.code != 1:
                raise
        raw = buf.getvalue().strip()
        if not raw:
            raise ValueError(
                "cmd_doctor produced no JSON output -- "
                "tasks.jsonl may be missing or .crumbs/ directory not found."
            )
        return json.loads(raw)

    return await asyncio.to_thread(_run_doctor)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def main() -> None:
    """Run the MCP server using stdio transport.

    Suitable for use as a Claude Code MCP server or any MCP-compatible client
    that communicates via stdin/stdout.
    """
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()

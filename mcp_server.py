#!/usr/bin/env python3
"""MCP server wrapping crumb.py task-tracker functions.

Exposes thirteen tools that map directly to crumb CLI commands:

  crumb_list         — list tasks with optional filters
  crumb_show         — show all fields for a single crumb
  crumb_update       — update crumb fields or append a note
  crumb_query        — full-text search across titles and descriptions
  crumb_create       — create a new crumb
  crumb_doctor       — validate tasks.jsonl integrity
  crumb_trail_list   — list all trails with status/progress
  crumb_trail_show   — show trail details with children array
  crumb_trail_close  — close a trail (rejects if open children exist)
  crumb_close        — close one or more crumbs
  crumb_ready        — list unblocked open crumbs
  crumb_blocked      — list blocked crumbs with blocker details
  crumb_link         — add/remove links between crumbs

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
        "crumb_query to search, crumb_doctor to validate integrity, "
        "crumb_trail_list/crumb_trail_show/crumb_trail_close for trail management, "
        "crumb_close to close tasks, crumb_ready for unblocked tasks, "
        "crumb_blocked for blocked tasks, and crumb_link to manage links."
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
# Tool: crumb_trail_list
# ---------------------------------------------------------------------------


@mcp.tool(
    description=(
        "List all trails with their status and child-completion progress. "
        "Returns a JSON array of trail objects, each with a 'children_total' "
        "and 'children_closed' count."
    )
)
async def crumb_trail_list() -> list[dict[str, Any]]:
    """List all trails with status and child-completion progress.

    Returns:
        List of trail objects. Each object is the full trail record from
        ``_crumb_to_json_obj`` augmented with:
            children_total (int): Total number of child crumbs.
            children_closed (int): Number of closed child crumbs.
    """

    def _run() -> list[dict[str, Any]]:
        path = _crumb.require_tasks_jsonl()
        tasks = _crumb.read_tasks(path)
        trails = [t for t in tasks if t.get("type") == "trail"]
        result = []
        for trail in trails:
            trail_id = trail.get("id", "")
            children = _crumb._get_trail_children(tasks, trail_id)
            obj = _crumb._crumb_to_json_obj(trail)
            obj["children_total"] = len(children)
            obj["children_closed"] = sum(
                1 for c in children if c.get("status") == "closed"
            )
            result.append(obj)
        return result

    return await asyncio.to_thread(_run)


# ---------------------------------------------------------------------------
# Tool: crumb_trail_show
# ---------------------------------------------------------------------------


@mcp.tool(
    description=(
        "Show a trail's full details including its children array. "
        "Returns a JSON object with the trail record and a 'children' list."
    )
)
async def crumb_trail_show(trail_id: str) -> dict[str, Any]:
    """Show a trail's fields and its child crumbs.

    Args:
        trail_id: The trail ID to look up (e.g. "AF-T1").

    Returns:
        Dict containing all trail fields from ``_crumb_to_json_obj`` plus:
            children (list[dict]): Full JSON objects for each child crumb.
            children_total (int): Total child count.
            children_closed (int): Closed child count.

    Raises:
        RuntimeError: If the trail ID is not found or is not a trail type.
    """

    def _run() -> dict[str, Any]:
        path = _crumb.require_tasks_jsonl()
        tasks = _crumb.read_tasks(path)
        trail = _crumb._find_crumb(tasks, trail_id)
        if trail is None:
            raise RuntimeError(f"trail '{trail_id}' not found")
        if trail.get("type") != "trail":
            raise RuntimeError(f"'{trail_id}' is not a trail")
        children = _crumb._get_trail_children(tasks, trail_id)
        obj = _crumb._crumb_to_json_obj(trail)
        obj["children"] = [_crumb._crumb_to_json_obj(c) for c in children]
        obj["children_total"] = len(children)
        obj["children_closed"] = sum(
            1 for c in children if c.get("status") == "closed"
        )
        return obj

    try:
        return await asyncio.to_thread(_run)
    except RuntimeError:
        raise
    except SystemExit as exc:
        raise RuntimeError(f"trail '{trail_id}' not found") from exc


# ---------------------------------------------------------------------------
# Tool: crumb_trail_close
# ---------------------------------------------------------------------------


@mcp.tool(
    description=(
        "Close a trail. Rejects with an error if the trail has open children. "
        "Returns a JSON object with 'success' and the updated trail record."
    )
)
async def crumb_trail_close(trail_id: str) -> dict[str, Any]:
    """Close a trail, rejecting if any children are still open.

    Args:
        trail_id: The trail ID to close (e.g. "AF-T1").

    Returns:
        Dict with:
            success (bool): True when the trail was closed.
            message (str): "already closed" if it was already closed.
            Plus the full trail object fields if closed or already-closed.

    Raises:
        RuntimeError: If the trail has open children or the ID is not found.
    """

    def _run() -> dict[str, Any]:
        with _crumb.FileLock():
            path = _crumb.require_tasks_jsonl()
            tasks = _crumb.read_tasks(path)

            trail = _crumb._find_crumb(tasks, trail_id)
            if trail is None:
                raise RuntimeError(f"trail '{trail_id}' not found")
            if trail.get("type") != "trail":
                raise RuntimeError(f"'{trail_id}' is not a trail")

            if trail.get("status") == "closed":
                obj = _crumb._crumb_to_json_obj(trail)
                obj["success"] = False
                obj["message"] = "already closed"
                return obj

            children = _crumb._get_trail_children(tasks, trail_id)
            open_children = [c for c in children if c.get("status") != "closed"]
            if open_children:
                raise RuntimeError(
                    f"cannot close trail '{trail_id}': "
                    f"{len(open_children)} open child(ren): "
                    + ", ".join(c.get("id", "?") for c in open_children)
                )

            now = _crumb.now_iso()
            trail["status"] = "closed"
            trail["closed_at"] = now
            trail["updated_at"] = now
            _crumb.write_tasks(path, tasks)

        obj = _crumb._crumb_to_json_obj(trail)
        obj["success"] = True
        return obj

    try:
        return await asyncio.to_thread(_run)
    except RuntimeError:
        raise


# ---------------------------------------------------------------------------
# Tool: crumb_close
# ---------------------------------------------------------------------------


@mcp.tool(
    description=(
        "Close one or more crumbs. Already-closed crumbs are skipped. "
        "Returns a JSON object listing which IDs were closed and which skipped."
    )
)
async def crumb_close(ids: list[str]) -> dict[str, Any]:
    """Close one or more crumbs by ID.

    Args:
        ids: List of crumb IDs to close (e.g. ["AF-1", "AF-2"]).

    Returns:
        Dict with:
            closed (list[str]): IDs that were newly closed.
            skipped (list[str]): IDs that were already closed.
            tasks (list[dict]): Full JSON objects for every affected crumb
                (closed + skipped), in the order provided.

    Raises:
        RuntimeError: If any provided ID does not exist.
    """

    def _run() -> dict[str, Any]:
        with _crumb.FileLock():
            path = _crumb.require_tasks_jsonl()
            tasks = _crumb.read_tasks(path)

            # Pre-validate all IDs exist before mutating anything
            for crumb_id in ids:
                if _crumb._find_crumb(tasks, crumb_id) is None:
                    raise RuntimeError(f"crumb '{crumb_id}' not found")

            closed: list[str] = []
            skipped: list[str] = []

            for crumb_id in ids:
                crumb = _crumb._find_crumb(tasks, crumb_id)
                if crumb is None:
                    raise RuntimeError(
                        f"internal error: '{crumb_id}' pre-validated but not found"
                    )
                if crumb.get("status") == "closed":
                    skipped.append(crumb_id)
                    continue
                now = _crumb.now_iso()
                crumb["status"] = "closed"
                crumb["closed_at"] = now
                crumb["updated_at"] = now
                closed.append(crumb_id)

            if closed:
                _crumb.write_tasks(path, tasks)
                for crumb_id in closed:
                    _crumb._auto_close_trail_if_complete(tasks, path, crumb_id)

        # Re-read tasks to get the post-write state for the returned objects
        path = _crumb.require_tasks_jsonl()
        tasks = _crumb.read_tasks(path)
        all_ids = closed + skipped
        affected = [
            _crumb._crumb_to_json_obj(t)
            for t in tasks
            if t.get("id") in all_ids
        ]
        return {"closed": closed, "skipped": skipped, "tasks": affected}

    return await asyncio.to_thread(_run)


# ---------------------------------------------------------------------------
# Tool: crumb_ready
# ---------------------------------------------------------------------------


@mcp.tool(
    description=(
        "List open crumbs with no unresolved blockers (ready to work on). "
        "Returns a JSON array of crumb objects, sorted by priority."
    )
)
async def crumb_ready(
    limit: Optional[int] = None,
    sort: str = "created_at",
) -> list[dict[str, Any]]:
    """List open crumbs that have no unresolved blockers.

    Only ``status == 'open'`` crumbs are included; ``in_progress`` crumbs
    are intentionally excluded — they have already been claimed by an agent.
    Trail records are also excluded.

    Args:
        limit: Maximum number of results to return. Omit for all.
        sort: Sort field — "priority", "status", or "created_at" (default).

    Returns:
        List of crumb objects matching the ``_crumb_to_json_obj`` schema,
        each representing an unblocked open crumb.
    """

    def _run() -> list[dict[str, Any]]:
        path = _crumb.require_tasks_jsonl()
        tasks = _crumb.read_tasks(path)

        id_to_record: dict[str, dict[str, Any]] = {
            t["id"]: t for t in tasks if "id" in t
        }

        results = [
            t
            for t in tasks
            if t.get("status") == "open"
            and t.get("type") != "trail"
            and not _crumb._is_crumb_blocked(t, id_to_record)
        ]

        _crumb._sort_crumbs(results, sort)
        if limit is not None and limit > 0:
            results = results[:limit]

        return [_crumb._crumb_to_json_obj(t) for t in results]

    return await asyncio.to_thread(_run)


# ---------------------------------------------------------------------------
# Tool: crumb_blocked
# ---------------------------------------------------------------------------


@mcp.tool(
    description=(
        "List open crumbs that have at least one unresolved blocker. "
        "Returns a JSON array of crumb objects, each augmented with a "
        "'blockers' field listing the blocking crumb IDs."
    )
)
async def crumb_blocked() -> list[dict[str, Any]]:
    """List open crumbs with at least one unresolved blocker.

    Only ``status == 'open'`` crumbs are included; ``in_progress`` crumbs
    are intentionally excluded.  Trail records are also excluded.

    Returns:
        List of crumb objects matching the ``_crumb_to_json_obj`` schema,
        each augmented with a ``blockers`` field (list[str]) containing the
        IDs of unresolved blocking crumbs.
    """

    def _run() -> list[dict[str, Any]]:
        path = _crumb.require_tasks_jsonl()
        tasks = _crumb.read_tasks(path)

        id_to_record: dict[str, dict[str, Any]] = {
            t["id"]: t for t in tasks if "id" in t
        }

        results = [
            t
            for t in tasks
            if t.get("status") == "open"
            and t.get("type") != "trail"
            and _crumb._is_crumb_blocked(t, id_to_record)
        ]

        _crumb._sort_crumbs(results, "created_at")

        output = []
        for t in results:
            obj = _crumb._crumb_to_json_obj(t)
            # Add a 'blockers' field listing only the unresolved blocker IDs
            all_blocker_ids = _crumb._get_blocked_by(t)
            unresolved = [
                bid
                for bid in all_blocker_ids
                if (rec := id_to_record.get(bid)) is not None
                and rec.get("status") != "closed"
            ]
            obj["blockers"] = unresolved
            output.append(obj)
        return output

    return await asyncio.to_thread(_run)


# ---------------------------------------------------------------------------
# Tool: crumb_link
# ---------------------------------------------------------------------------


@mcp.tool(
    description=(
        "Add or remove links between crumbs: set parent trail, "
        "add/remove a blocked_by reference, or set a discovered_from provenance. "
        "Returns the updated crumb as a JSON object with a 'success' field."
    )
)
async def crumb_link(
    crumb_id: str,
    parent: Optional[str] = None,
    blocked_by: Optional[str] = None,
    remove_blocked_by: Optional[str] = None,
    discovered_from: Optional[str] = None,
) -> dict[str, Any]:
    """Manage links between crumbs.

    At least one link parameter must be provided.

    Args:
        crumb_id: The crumb ID to update (e.g. "AF-1").
        parent: Trail ID to set as the parent (e.g. "AF-T1").
        blocked_by: Crumb ID to add as a blocker (e.g. "AF-2").
        remove_blocked_by: Crumb ID to remove from blocked_by list.
        discovered_from: Provenance reference to set on the crumb.

    Returns:
        Dict with:
            success (bool): True when links were updated; False when nothing
                changed (no-op call).
            message (str): "no link changes" when success is False.
            Plus all full crumb fields from ``_crumb_to_json_obj``.

    Raises:
        RuntimeError: If the crumb ID is not found.
    """
    args = argparse.Namespace(
        id=crumb_id,
        link_parent=parent,
        blocked_by=blocked_by,
        remove_blocked_by=remove_blocked_by,
        discovered_from=discovered_from,
        json_output=True,
    )

    def _run() -> dict[str, Any]:
        with _crumb.FileLock():
            path = _crumb.require_tasks_jsonl()
            tasks = _crumb.read_tasks(path)

            crumb = _crumb._find_crumb(tasks, crumb_id)
            if crumb is None:
                raise RuntimeError(f"crumb '{crumb_id}' not found")

            links: dict[str, Any] = crumb.get("links") or {}
            if not isinstance(links, dict):
                links = {}

            changed = False

            if args.link_parent is not None:
                if links.get("parent") != args.link_parent:
                    links["parent"] = args.link_parent
                    changed = True

            if args.blocked_by is not None:
                blocked: list[str] = links.get("blocked_by") or []
                if not isinstance(blocked, list):
                    blocked = [blocked]
                if args.blocked_by not in blocked:
                    blocked.append(args.blocked_by)
                    links["blocked_by"] = blocked
                    changed = True

            if args.remove_blocked_by is not None:
                blocked_existing: list[str] = links.get("blocked_by") or []
                if not isinstance(blocked_existing, list):
                    blocked_existing = [blocked_existing]
                if args.remove_blocked_by in blocked_existing:
                    blocked_existing = [
                        bid
                        for bid in blocked_existing
                        if bid != args.remove_blocked_by
                    ]
                    links["blocked_by"] = blocked_existing
                    changed = True

            if args.discovered_from is not None:
                if links.get("discovered_from") != args.discovered_from:
                    links["discovered_from"] = args.discovered_from
                    changed = True

            if not changed:
                obj = _crumb._crumb_to_json_obj(crumb)
                obj["success"] = False
                obj["message"] = "no link changes"
                return obj

            crumb["links"] = links
            crumb["updated_at"] = _crumb.now_iso()
            _crumb.write_tasks(path, tasks)

            if args.link_parent is not None:
                _crumb._auto_reopen_trail_if_needed(
                    tasks, path, args.link_parent, crumb.get("status", "open")
                )

        obj = _crumb._crumb_to_json_obj(crumb)
        obj["success"] = True
        return obj

    try:
        return await asyncio.to_thread(_run)
    except RuntimeError:
        raise


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

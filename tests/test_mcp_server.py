"""Tests for mcp_server.py — MCP server wrapping crumb.py functions.

Tests are organized into:
  TestMcpServerRegistration  — server instantiation and tool registration
  TestCrumbList              — crumb_list tool
  TestCrumbShow              — crumb_show tool
  TestCrumbUpdate            — crumb_update tool
  TestCrumbQuery             — crumb_query tool
  TestCrumbCreate            — crumb_create tool
  TestCrumbDoctor            — crumb_doctor tool
  TestRunCmdJsonHelper       — internal _run_cmd_json helper
  TestConcurrency            — concurrent calls do not corrupt tasks.jsonl
  TestCrumbTrailList         — crumb_trail_list tool
  TestCrumbTrailShow         — crumb_trail_show tool
  TestCrumbTrailClose        — crumb_trail_close tool
  TestCrumbClose             — crumb_close tool
  TestCrumbReady             — crumb_ready tool
  TestCrumbBlocked           — crumb_blocked tool
  TestCrumbLink              — crumb_link tool

All tests use the ``crumbs_env`` fixture from conftest.py which patches
``crumb.find_crumbs_dir`` to an isolated tmp directory.

Async tools are tested with ``asyncio.run()`` so no pytest-asyncio plugin
is required.
"""

from __future__ import annotations

import argparse
import asyncio
import json
from pathlib import Path
from typing import Any

import pytest

import crumb as _crumb
import mcp_server
from mcp_server import (
    _run_cmd_json,
    crumb_blocked,
    crumb_close,
    crumb_create,
    crumb_doctor,
    crumb_link,
    crumb_list,
    crumb_query,
    crumb_ready,
    crumb_show,
    crumb_trail_close,
    crumb_trail_list,
    crumb_trail_show,
    crumb_update,
    mcp,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _seed_task(
    crumbs_dir: Path,
    crumb_id: str = "AF-1",
    title: str = "Test task",
    status: str = "open",
    priority: str = "P2",
    crumb_type: str = "task",
    description: str | None = None,
    links: dict[str, Any] | None = None,
) -> None:
    """Write a single task record to tasks.jsonl.

    Args:
        crumbs_dir: Path to the isolated .crumbs/ directory.
        crumb_id: ID to assign.
        title: Task title.
        status: Task status.
        priority: Task priority.
        crumb_type: Task type ("task", "bug", "feature").
        description: Optional description text.
        links: Optional links dict.
    """
    record: dict[str, Any] = {
        "id": crumb_id,
        "type": crumb_type,
        "title": title,
        "status": status,
        "priority": priority,
        "created_at": "2026-01-01T00:00:00Z",
        "updated_at": "2026-01-01T00:00:00Z",
    }
    if description is not None:
        record["description"] = description
    if links is not None:
        record["links"] = links
    tasks_path = crumbs_dir / "tasks.jsonl"
    existing = tasks_path.read_text(encoding="utf-8")
    tasks_path.write_text(
        existing + json.dumps(record, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )


def _seed_trail(crumbs_dir: Path, trail_id: str = "AF-T1", title: str = "Test trail") -> None:
    """Write a trail record to tasks.jsonl.

    Args:
        crumbs_dir: Path to the isolated .crumbs/ directory.
        trail_id: Trail ID (e.g. "AF-T1").
        title: Trail title.
    """
    record: dict[str, Any] = {
        "id": trail_id,
        "type": "trail",
        "title": title,
        "status": "open",
        "priority": "P2",
        "created_at": "2026-01-01T00:00:00Z",
        "updated_at": "2026-01-01T00:00:00Z",
    }
    tasks_path = crumbs_dir / "tasks.jsonl"
    existing = tasks_path.read_text(encoding="utf-8")
    tasks_path.write_text(
        existing + json.dumps(record, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )


# ---------------------------------------------------------------------------
# TestMcpServerRegistration
# ---------------------------------------------------------------------------


class TestMcpServerRegistration:
    """Verify the MCP server instance and tool registration."""

    def test_mcp_instance_created(self) -> None:
        """FastMCP instance exists and has the expected name."""
        assert mcp is not None
        assert mcp.name == "crumb"

    def test_expected_tools_registered(self) -> None:
        """Exactly the expected tools are registered on the MCP server."""
        tools_result = asyncio.run(mcp.list_tools())
        registered_names = {t.name for t in tools_result}
        expected = {
            "crumb_list",
            "crumb_show",
            "crumb_update",
            "crumb_query",
            "crumb_create",
            "crumb_doctor",
            "crumb_trail_list",
            "crumb_trail_show",
            "crumb_trail_close",
            "crumb_close",
            "crumb_ready",
            "crumb_blocked",
            "crumb_link",
        }
        assert expected == registered_names

    def test_original_six_tools_still_registered(self) -> None:
        """The original 6 tools remain registered unchanged."""
        tools_result = asyncio.run(mcp.list_tools())
        registered_names = {t.name for t in tools_result}
        original = {
            "crumb_list",
            "crumb_show",
            "crumb_update",
            "crumb_query",
            "crumb_create",
            "crumb_doctor",
        }
        assert original.issubset(registered_names)

    def test_all_tools_have_descriptions(self) -> None:
        """Every registered tool has a non-empty description."""
        tools_result = asyncio.run(mcp.list_tools())
        for tool in tools_result:
            assert tool.description, f"Tool '{tool.name}' has no description"

    def test_crumb_list_schema_has_expected_params(self) -> None:
        """crumb_list tool schema exposes status and limit parameters."""
        tools_result = asyncio.run(mcp.list_tools())
        tool = next(t for t in tools_result if t.name == "crumb_list")
        params = tool.inputSchema.get("properties", {})
        assert "status" in params
        assert "limit" in params


# ---------------------------------------------------------------------------
# TestRunCmdJsonHelper
# ---------------------------------------------------------------------------


class TestRunCmdJsonHelper:
    """Unit tests for the _run_cmd_json helper function."""

    def test_captures_json_list_output(self, crumbs_env: Path) -> None:
        """Returns parsed list when cmd_list emits a JSON array."""
        _seed_task(crumbs_env)
        args = argparse.Namespace(
            filter_open=False,
            filter_closed=False,
            filter_in_progress=False,
            priority=None,
            filter_type=None,
            agent_type=None,
            parent=None,
            discovered=False,
            after=None,
            sort="created_at",
            limit=None,
            short=False,
            json_output=True,
        )
        result = _run_cmd_json(_crumb.cmd_list, args)
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0]["id"] == "AF-1"

    def test_captures_json_dict_output(self, crumbs_env: Path) -> None:
        """Returns parsed dict when cmd_show emits a JSON object."""
        _seed_task(crumbs_env, crumb_id="AF-1", title="My task")
        args = argparse.Namespace(id="AF-1", json_output=True)
        result = _run_cmd_json(_crumb.cmd_show, args)
        assert isinstance(result, dict)
        assert result["id"] == "AF-1"

    def test_raises_on_invalid_json(self, crumbs_env: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """Raises ValueError if the command emits non-JSON to stdout."""
        def bad_cmd(args: argparse.Namespace) -> None:
            import sys
            print("not json", file=sys.stdout)

        with pytest.raises((ValueError, json.JSONDecodeError)):
            _run_cmd_json(bad_cmd, argparse.Namespace())

    def test_raises_value_error_on_empty_stdout(self, crumbs_env: Path) -> None:
        """Raises ValueError with a descriptive message when the command emits no output."""
        def silent_cmd(args: argparse.Namespace) -> None:
            pass  # produces no stdout

        with pytest.raises(ValueError, match="no output"):
            _run_cmd_json(silent_cmd, argparse.Namespace())

    def test_system_exit_propagates_on_non_json_path(self, crumbs_env: Path) -> None:
        """SystemExit raised by the command re-propagates out of _run_cmd_json."""
        def exiting_cmd(args: argparse.Namespace) -> None:
            raise SystemExit(2)

        with pytest.raises(SystemExit) as exc_info:
            _run_cmd_json(exiting_cmd, argparse.Namespace())
        assert exc_info.value.code == 2


# ---------------------------------------------------------------------------
# TestCrumbList
# ---------------------------------------------------------------------------


class TestCrumbList:
    """Tests for the crumb_list MCP tool."""

    def test_returns_all_tasks(self, crumbs_env: Path) -> None:
        """Returns all non-trail tasks when no filters applied."""
        _seed_task(crumbs_env, "AF-1", "Task one")
        _seed_task(crumbs_env, "AF-2", "Task two", status="in_progress")
        _seed_trail(crumbs_env)  # Trails should be excluded

        result = asyncio.run(crumb_list())
        assert isinstance(result, list)
        ids = {r["id"] for r in result}
        assert "AF-1" in ids
        assert "AF-2" in ids
        assert "AF-T1" not in ids  # Trails excluded

    def test_filter_by_open_status(self, crumbs_env: Path) -> None:
        """Only open tasks returned when status='open'."""
        _seed_task(crumbs_env, "AF-1", "Open task", status="open")
        _seed_task(crumbs_env, "AF-2", "In-progress task", status="in_progress")

        result = asyncio.run(crumb_list(status="open"))
        ids = {r["id"] for r in result}
        assert "AF-1" in ids
        assert "AF-2" not in ids

    def test_filter_by_priority(self, crumbs_env: Path) -> None:
        """Only P0 tasks returned when priority='P0'."""
        _seed_task(crumbs_env, "AF-1", "P0 task", priority="P0")
        _seed_task(crumbs_env, "AF-2", "P2 task", priority="P2")

        result = asyncio.run(crumb_list(priority="P0"))
        assert len(result) == 1
        assert result[0]["id"] == "AF-1"

    def test_limit_parameter(self, crumbs_env: Path) -> None:
        """Respects limit parameter."""
        for i in range(1, 6):
            _seed_task(crumbs_env, f"AF-{i}", f"Task {i}")

        result = asyncio.run(crumb_list(limit=3))
        assert len(result) == 3

    def test_empty_result_returns_empty_list(self, crumbs_env: Path) -> None:
        """Returns empty list when no tasks match filter."""
        result = asyncio.run(crumb_list(status="closed"))
        assert result == []

    def test_json_schema_fields_present(self, crumbs_env: Path) -> None:
        """Each result has required schema fields from _crumb_to_json_obj."""
        _seed_task(crumbs_env)
        result = asyncio.run(crumb_list())
        assert len(result) == 1
        required_fields = {"id", "title", "type", "status", "priority"}
        assert required_fields.issubset(set(result[0].keys()))

    def test_filter_by_type(self, crumbs_env: Path) -> None:
        """Only bug-type tasks returned when crumb_type='bug'."""
        _seed_task(crumbs_env, "AF-1", "A task", crumb_type="task")
        _seed_task(crumbs_env, "AF-2", "A bug", crumb_type="bug")

        result = asyncio.run(crumb_list(crumb_type="bug"))
        assert len(result) == 1
        assert result[0]["id"] == "AF-2"


# ---------------------------------------------------------------------------
# TestCrumbShow
# ---------------------------------------------------------------------------


class TestCrumbShow:
    """Tests for the crumb_show MCP tool."""

    def test_returns_full_crumb_object(self, crumbs_env: Path) -> None:
        """Returns dict with all required fields for a known ID."""
        _seed_task(crumbs_env, "AF-1", "Show me")

        result = asyncio.run(crumb_show("AF-1"))
        assert isinstance(result, dict)
        assert result["id"] == "AF-1"
        assert result["title"] == "Show me"
        assert result["status"] == "open"

    def test_raises_for_unknown_id(self, crumbs_env: Path) -> None:
        """Raises RuntimeError when crumb ID does not exist."""
        with pytest.raises(RuntimeError, match="crumb_show failed.*exit code"):
            asyncio.run(crumb_show("AF-9999"))

    def test_shows_trail_record(self, crumbs_env: Path) -> None:
        """Can show a trail record by its T-prefixed ID."""
        _seed_trail(crumbs_env, "AF-T1", "Test trail")

        result = asyncio.run(crumb_show("AF-T1"))
        assert result["id"] == "AF-T1"
        assert result["type"] == "trail"

    def test_includes_all_schema_fields(self, crumbs_env: Path) -> None:
        """Result includes all required JSON schema fields (including null ones)."""
        _seed_task(crumbs_env, "AF-1", "Full schema task")

        result = asyncio.run(crumb_show("AF-1"))
        # _crumb_to_json_obj always emits these keys (possibly null)
        for field in ("id", "title", "type", "status", "priority", "description",
                      "acceptance_criteria", "scope", "links", "notes"):
            assert field in result, f"Missing field '{field}' in crumb_show result"


# ---------------------------------------------------------------------------
# TestCrumbUpdate
# ---------------------------------------------------------------------------


class TestCrumbUpdate:
    """Tests for the crumb_update MCP tool."""

    def test_update_status(self, crumbs_env: Path) -> None:
        """Successfully transitions a task from open to in_progress."""
        _seed_task(crumbs_env, "AF-1", "Claimable task")

        result = asyncio.run(crumb_update("AF-1", status="in_progress"))
        assert result["success"] is True
        assert result["status"] == "in_progress"

    def test_update_title(self, crumbs_env: Path) -> None:
        """Successfully updates a task title."""
        _seed_task(crumbs_env, "AF-1", "Old title")

        result = asyncio.run(crumb_update("AF-1", title="New title"))
        assert result["success"] is True
        assert result["title"] == "New title"

    def test_update_priority(self, crumbs_env: Path) -> None:
        """Successfully updates a task priority."""
        _seed_task(crumbs_env, "AF-1", "A task", priority="P2")

        result = asyncio.run(crumb_update("AF-1", priority="P0"))
        assert result["success"] is True
        assert result["priority"] == "P0"

    def test_append_note(self, crumbs_env: Path) -> None:
        """Appends a timestamped note to the crumb."""
        _seed_task(crumbs_env, "AF-1", "Noted task")

        result = asyncio.run(crumb_update("AF-1", note="This is a note"))
        assert result["success"] is True
        notes = result.get("notes") or []
        assert any("This is a note" in str(n) for n in notes)

    def test_no_change_returns_success_false(self, crumbs_env: Path) -> None:
        """Returns success=false when no field values changed."""
        _seed_task(crumbs_env, "AF-1", "Unchanged task")

        result = asyncio.run(crumb_update("AF-1"))
        assert result["success"] is False
        assert "no changes" in result.get("message", "")

    def test_raises_for_unknown_id(self, crumbs_env: Path) -> None:
        """Raises RuntimeError when crumb ID does not exist."""
        with pytest.raises(RuntimeError):
            asyncio.run(crumb_update("AF-9999", status="in_progress"))

    def test_raises_on_closed_transition(self, crumbs_env: Path) -> None:
        """Raises RuntimeError when attempting to update a closed crumb."""
        _seed_task(crumbs_env, "AF-1", "Closed task", status="closed")

        with pytest.raises(RuntimeError):
            asyncio.run(crumb_update("AF-1", status="in_progress"))

    def test_persists_to_disk(self, crumbs_env: Path) -> None:
        """Updated status is written to tasks.jsonl and readable back."""
        _seed_task(crumbs_env, "AF-1", "Persist test")

        asyncio.run(crumb_update("AF-1", status="in_progress"))

        # Read back directly from disk to verify persistence
        tasks_path = crumbs_env / "tasks.jsonl"
        tasks = _crumb.read_tasks(tasks_path)
        task = next(t for t in tasks if t["id"] == "AF-1")
        assert task["status"] == "in_progress"


# ---------------------------------------------------------------------------
# TestCrumbQuery
# ---------------------------------------------------------------------------


class TestCrumbQuery:
    """Tests for the crumb_query MCP tool."""

    def test_matches_title(self, crumbs_env: Path) -> None:
        """Finds tasks whose title contains the query string."""
        _seed_task(crumbs_env, "AF-1", "Fix the login bug")
        _seed_task(crumbs_env, "AF-2", "Update database schema")

        result = asyncio.run(crumb_query("login"))
        ids = {r["id"] for r in result}
        assert "AF-1" in ids
        assert "AF-2" not in ids

    def test_matches_description(self, crumbs_env: Path) -> None:
        """Finds tasks whose description contains the query string."""
        _seed_task(crumbs_env, "AF-1", "Generic task", description="Involves frobnicator widget")
        _seed_task(crumbs_env, "AF-2", "Another task")

        result = asyncio.run(crumb_query("frobnicator"))
        assert len(result) == 1
        assert result[0]["id"] == "AF-1"

    def test_case_insensitive(self, crumbs_env: Path) -> None:
        """Query matching is case-insensitive."""
        _seed_task(crumbs_env, "AF-1", "MCP Integration Test")

        result_lower = asyncio.run(crumb_query("mcp integration"))
        result_upper = asyncio.run(crumb_query("MCP INTEGRATION"))
        assert len(result_lower) == 1
        assert len(result_upper) == 1

    def test_no_match_returns_empty_list(self, crumbs_env: Path) -> None:
        """Returns empty list when no tasks match the query."""
        _seed_task(crumbs_env, "AF-1", "Completely unrelated task")

        result = asyncio.run(crumb_query("xyzzy_nonexistent_1234"))
        assert result == []

    def test_matches_trails_too(self, crumbs_env: Path) -> None:
        """Query also matches trail records (cmd_search is not filtered)."""
        _seed_trail(crumbs_env, "AF-T1", "Trail for frobnicator feature")

        result = asyncio.run(crumb_query("frobnicator"))
        assert any(r["id"] == "AF-T1" for r in result)


# ---------------------------------------------------------------------------
# TestCrumbCreate
# ---------------------------------------------------------------------------


class TestCrumbCreate:
    """Tests for the crumb_create MCP tool."""

    def test_creates_task_with_title(self, crumbs_env: Path) -> None:
        """Creates a new task and returns its JSON object."""
        result = asyncio.run(crumb_create(title="New feature task"))

        assert isinstance(result, dict)
        assert result["title"] == "New feature task"
        assert result["status"] == "open"
        assert result["id"].startswith("AF-")

    def test_assigns_sequential_id(self, crumbs_env: Path) -> None:
        """Auto-assigns IDs starting from AF-1."""
        r1 = asyncio.run(crumb_create(title="First task"))
        r2 = asyncio.run(crumb_create(title="Second task"))

        assert r1["id"] == "AF-1"
        assert r2["id"] == "AF-2"

    def test_respects_priority(self, crumbs_env: Path) -> None:
        """Assigns specified priority to the new crumb."""
        result = asyncio.run(crumb_create(title="P0 task", priority="P0"))
        assert result["priority"] == "P0"

    def test_respects_type(self, crumbs_env: Path) -> None:
        """Assigns specified type to the new crumb."""
        result = asyncio.run(crumb_create(title="A bug", crumb_type="bug"))
        assert result["type"] == "bug"

    def test_persists_to_disk(self, crumbs_env: Path) -> None:
        """Created task appears in tasks.jsonl after creation."""
        asyncio.run(crumb_create(title="Disk persist task"))

        tasks_path = crumbs_env / "tasks.jsonl"
        tasks = _crumb.read_tasks(tasks_path)
        assert any(t["title"] == "Disk persist task" for t in tasks)

    def test_from_json_payload(self, crumbs_env: Path) -> None:
        """Creates a crumb with extra fields from from_json."""
        payload = json.dumps({"scope": {"files": ["mcp_server.py"]}})
        result = asyncio.run(crumb_create(title="With scope", from_json=payload))
        assert result["scope"] == {"files": ["mcp_server.py"]}

    def test_raises_on_invalid_priority(self, crumbs_env: Path) -> None:
        """Raises RuntimeError when an invalid priority is specified."""
        with pytest.raises(RuntimeError):
            asyncio.run(crumb_create(title="Bad priority", priority="P9"))

    def test_raises_on_invalid_type(self, crumbs_env: Path) -> None:
        """Raises RuntimeError when an invalid type is specified."""
        with pytest.raises(RuntimeError):
            asyncio.run(crumb_create(title="Bad type", crumb_type="invalid"))

    def test_result_has_required_schema_fields(self, crumbs_env: Path) -> None:
        """Created crumb result has all required JSON schema fields."""
        result = asyncio.run(crumb_create(title="Schema check"))
        for field in ("id", "title", "type", "status", "priority",
                      "description", "acceptance_criteria", "scope", "links", "notes"):
            assert field in result


# ---------------------------------------------------------------------------
# TestCrumbDoctor
# ---------------------------------------------------------------------------


class TestCrumbDoctor:
    """Tests for the crumb_doctor MCP tool."""

    def test_clean_file_returns_ok_true(self, crumbs_env: Path) -> None:
        """Returns ok=true when tasks.jsonl has no integrity issues."""
        _seed_trail(crumbs_env, "AF-T1")
        _seed_task(crumbs_env, "AF-1", "Clean task", links={"parent": "AF-T1"})

        result = asyncio.run(crumb_doctor())
        assert isinstance(result, dict)
        assert result["ok"] is True
        assert result["error_count"] == 0

    def test_orphan_produces_warning(self, crumbs_env: Path) -> None:
        """Orphan crumbs (no parent) appear as warnings, not errors."""
        _seed_task(crumbs_env, "AF-1", "Orphan task")

        result = asyncio.run(crumb_doctor())
        assert result["warning_count"] > 0
        assert any("orphan" in w for w in result["warnings"])

    def test_dangling_parent_produces_error(self, crumbs_env: Path) -> None:
        """Dangling parent link appears as an error and ok=false."""
        _seed_task(crumbs_env, "AF-1", "Dangling parent task",
                   links={"parent": "AF-T999"})

        result = asyncio.run(crumb_doctor())
        assert result["ok"] is False
        assert result["error_count"] > 0

    def test_fix_removes_dangling_blocked_by(self, crumbs_env: Path) -> None:
        """With fix=True, removes dangling blocked_by references."""
        _seed_trail(crumbs_env, "AF-T1")
        _seed_task(crumbs_env, "AF-1", "Blocked task",
                   links={"parent": "AF-T1", "blocked_by": ["AF-9999"]})

        result = asyncio.run(crumb_doctor(fix=True))
        assert len(result["fixes_applied"]) > 0

    def test_result_schema_fields(self, crumbs_env: Path) -> None:
        """Result always contains all expected schema fields."""
        result = asyncio.run(crumb_doctor())
        for field in ("ok", "error_count", "warning_count", "errors",
                      "warnings", "fixes_applied"):
            assert field in result, f"Missing field '{field}' in crumb_doctor result"

    def test_ok_false_still_returns_report(self, crumbs_env: Path) -> None:
        """Returns a complete report even when doctor exits with errors (ok=false)."""
        _seed_task(crumbs_env, "AF-1", "Dangling task",
                   links={"parent": "AF-T999"})

        # Should not raise even though crumb_doctor would sys.exit(1)
        result = asyncio.run(crumb_doctor())
        assert result["ok"] is False
        assert isinstance(result["errors"], list)

    def test_unexpected_system_exit_propagates(
        self, crumbs_env: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """SystemExit with code != 1 propagates out of crumb_doctor."""
        import crumb as _crumb_mod

        def _failing_cmd_doctor(args: argparse.Namespace) -> None:
            # Simulate an infrastructure failure (e.g. missing .crumbs/ dir)
            # by raising SystemExit with a code other than 1.
            raise SystemExit(2)

        monkeypatch.setattr(_crumb_mod, "cmd_doctor", _failing_cmd_doctor)

        with pytest.raises(SystemExit) as exc_info:
            asyncio.run(crumb_doctor())
        assert exc_info.value.code == 2

    def test_exit_code_1_does_not_propagate(
        self, crumbs_env: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """SystemExit with code 1 is suppressed; the JSON report is returned."""
        import crumb as _crumb_mod

        def _exit_1_cmd_doctor(args: argparse.Namespace) -> None:
            # Simulate doctor finding errors: print a valid report then exit 1.
            import json as _json
            report = {
                "ok": False,
                "error_count": 1,
                "warning_count": 0,
                "errors": ["synthetic error"],
                "warnings": [],
                "fixes_applied": [],
            }
            print(_json.dumps(report))
            raise SystemExit(1)

        monkeypatch.setattr(_crumb_mod, "cmd_doctor", _exit_1_cmd_doctor)
        # monkeypatch the module-level reference used by mcp_server
        monkeypatch.setattr(mcp_server._crumb, "cmd_doctor", _exit_1_cmd_doctor)

        result = asyncio.run(crumb_doctor())
        assert result["ok"] is False
        assert result["error_count"] == 1

    def test_empty_output_raises_value_error(
        self, crumbs_env: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """_run_doctor raises ValueError (not JSONDecodeError) when cmd_doctor produces no output."""
        import crumb as _crumb_mod

        def _silent_cmd_doctor(args: argparse.Namespace) -> None:
            # Simulate cmd_doctor calling die() before printing any JSON.
            pass

        monkeypatch.setattr(_crumb_mod, "cmd_doctor", _silent_cmd_doctor)
        monkeypatch.setattr(mcp_server._crumb, "cmd_doctor", _silent_cmd_doctor)

        with pytest.raises(ValueError, match="tasks.jsonl"):
            asyncio.run(crumb_doctor())


# ---------------------------------------------------------------------------
# TestConcurrency
# ---------------------------------------------------------------------------


class TestConcurrency:
    """Verify that concurrent MCP tool calls do not corrupt tasks.jsonl."""

    def test_concurrent_creates_no_corruption(self, crumbs_env: Path) -> None:
        """Multiple concurrent crumb_create calls produce unique IDs with no data loss."""

        async def _run_concurrent_creates() -> list[dict[str, Any]]:
            tasks = [
                crumb_create(title=f"Concurrent task {i}")
                for i in range(5)
            ]
            return list(await asyncio.gather(*tasks))

        results = asyncio.run(_run_concurrent_creates())

        # All 5 creations succeeded
        assert len(results) == 5

        # All IDs are unique
        ids = [r["id"] for r in results]
        assert len(set(ids)) == 5, f"Duplicate IDs detected: {ids}"

        # tasks.jsonl on disk has exactly 5 records
        tasks_path = crumbs_env / "tasks.jsonl"
        disk_tasks = _crumb.read_tasks(tasks_path)
        assert len(disk_tasks) == 5

    def test_concurrent_updates_no_corruption(self, crumbs_env: Path) -> None:
        """Multiple concurrent crumb_update calls on different tasks produce no data loss."""
        for i in range(1, 4):
            _seed_task(crumbs_env, f"AF-{i}", f"Task {i}")

        async def _run_concurrent_updates() -> list[dict[str, Any]]:
            tasks = [
                crumb_update(f"AF-{i}", status="in_progress")
                for i in range(1, 4)
            ]
            return list(await asyncio.gather(*tasks))

        results = asyncio.run(_run_concurrent_updates())
        assert all(r["success"] is True for r in results)

        # Verify all three tasks updated on disk
        tasks_path = crumbs_env / "tasks.jsonl"
        disk_tasks = _crumb.read_tasks(tasks_path)
        for task in disk_tasks:
            if task["id"] in {"AF-1", "AF-2", "AF-3"}:
                assert task["status"] == "in_progress", (
                    f"Task {task['id']} not updated: {task['status']}"
                )

    def test_concurrent_creates_and_reads(self, crumbs_env: Path) -> None:
        """Concurrent creates and reads do not raise exceptions or corrupt data."""
        _seed_task(crumbs_env, "AF-1", "Seed task")

        async def _run_mixed() -> None:
            await asyncio.gather(
                crumb_create(title="Concurrent create A"),
                crumb_list(),
                crumb_create(title="Concurrent create B"),
                crumb_show("AF-1"),
            )

        # Should complete without raising exceptions
        asyncio.run(_run_mixed())

        # Verify disk integrity
        tasks_path = crumbs_env / "tasks.jsonl"
        disk_tasks = _crumb.read_tasks(tasks_path)
        assert len(disk_tasks) == 3  # AF-1 + A + B


# ---------------------------------------------------------------------------
# TestCrumbTrailList
# ---------------------------------------------------------------------------


class TestCrumbTrailList:
    """Tests for the crumb_trail_list MCP tool."""

    def test_returns_all_trails(self, crumbs_env: Path) -> None:
        """Returns a list containing all trail records."""
        _seed_trail(crumbs_env, "AF-T1", "First trail")
        _seed_trail(crumbs_env, "AF-T2", "Second trail")

        result = asyncio.run(crumb_trail_list())
        assert isinstance(result, list)
        ids = {r["id"] for r in result}
        assert "AF-T1" in ids
        assert "AF-T2" in ids

    def test_excludes_non_trail_tasks(self, crumbs_env: Path) -> None:
        """Regular tasks are not included in the trail list."""
        _seed_trail(crumbs_env, "AF-T1", "A trail")
        _seed_task(crumbs_env, "AF-1", "A task")

        result = asyncio.run(crumb_trail_list())
        ids = {r["id"] for r in result}
        assert "AF-T1" in ids
        assert "AF-1" not in ids

    def test_includes_children_counts(self, crumbs_env: Path) -> None:
        """Each trail object includes children_total and children_closed counts."""
        _seed_trail(crumbs_env, "AF-T1", "Trail with children")
        _seed_task(crumbs_env, "AF-1", "Open child", links={"parent": "AF-T1"})
        _seed_task(
            crumbs_env, "AF-2", "Closed child", status="closed",
            links={"parent": "AF-T1"}
        )

        result = asyncio.run(crumb_trail_list())
        trail = next(r for r in result if r["id"] == "AF-T1")
        assert trail["children_total"] == 2
        assert trail["children_closed"] == 1

    def test_empty_list_when_no_trails(self, crumbs_env: Path) -> None:
        """Returns empty list when no trails exist."""
        _seed_task(crumbs_env, "AF-1", "Just a task")

        result = asyncio.run(crumb_trail_list())
        assert result == []

    def test_trail_schema_fields_present(self, crumbs_env: Path) -> None:
        """Each trail object has the required schema fields."""
        _seed_trail(crumbs_env, "AF-T1", "Schema trail")

        result = asyncio.run(crumb_trail_list())
        assert len(result) == 1
        trail = result[0]
        for field in ("id", "title", "type", "status", "priority",
                      "children_total", "children_closed"):
            assert field in trail, f"Missing field '{field}' in crumb_trail_list result"


# ---------------------------------------------------------------------------
# TestCrumbTrailShow
# ---------------------------------------------------------------------------


class TestCrumbTrailShow:
    """Tests for the crumb_trail_show MCP tool."""

    def test_returns_trail_with_children_array(self, crumbs_env: Path) -> None:
        """Returns trail object with populated children array."""
        _seed_trail(crumbs_env, "AF-T1", "Parent trail")
        _seed_task(crumbs_env, "AF-1", "Child task", links={"parent": "AF-T1"})

        result = asyncio.run(crumb_trail_show("AF-T1"))
        assert isinstance(result, dict)
        assert result["id"] == "AF-T1"
        assert isinstance(result["children"], list)
        assert len(result["children"]) == 1
        assert result["children"][0]["id"] == "AF-1"

    def test_children_array_empty_when_no_children(self, crumbs_env: Path) -> None:
        """Returns empty children array when trail has no child crumbs."""
        _seed_trail(crumbs_env, "AF-T1", "Childless trail")

        result = asyncio.run(crumb_trail_show("AF-T1"))
        assert result["children"] == []
        assert result["children_total"] == 0
        assert result["children_closed"] == 0

    def test_children_counts_correct(self, crumbs_env: Path) -> None:
        """children_total and children_closed counts are accurate."""
        _seed_trail(crumbs_env, "AF-T1", "Count trail")
        _seed_task(crumbs_env, "AF-1", "Open child", links={"parent": "AF-T1"})
        _seed_task(
            crumbs_env, "AF-2", "Closed child", status="closed",
            links={"parent": "AF-T1"}
        )
        _seed_task(crumbs_env, "AF-3", "Another open", links={"parent": "AF-T1"})

        result = asyncio.run(crumb_trail_show("AF-T1"))
        assert result["children_total"] == 3
        assert result["children_closed"] == 1

    def test_raises_for_unknown_trail_id(self, crumbs_env: Path) -> None:
        """Raises RuntimeError when trail ID does not exist."""
        with pytest.raises(RuntimeError, match="not found"):
            asyncio.run(crumb_trail_show("AF-T9999"))

    def test_raises_for_non_trail_id(self, crumbs_env: Path) -> None:
        """Raises RuntimeError when the ID points to a task, not a trail."""
        _seed_task(crumbs_env, "AF-1", "A task, not a trail")

        with pytest.raises(RuntimeError, match="not a trail"):
            asyncio.run(crumb_trail_show("AF-1"))

    def test_trail_schema_fields_present(self, crumbs_env: Path) -> None:
        """Result includes all required trail schema fields."""
        _seed_trail(crumbs_env, "AF-T1", "Full schema trail")

        result = asyncio.run(crumb_trail_show("AF-T1"))
        for field in ("id", "title", "type", "status", "priority",
                      "children", "children_total", "children_closed"):
            assert field in result, f"Missing field '{field}' in crumb_trail_show result"


# ---------------------------------------------------------------------------
# TestCrumbTrailClose
# ---------------------------------------------------------------------------


class TestCrumbTrailClose:
    """Tests for the crumb_trail_close MCP tool."""

    def test_closes_trail_with_all_children_closed(self, crumbs_env: Path) -> None:
        """Closes a trail when all children are already closed."""
        _seed_trail(crumbs_env, "AF-T1", "Closeable trail")
        _seed_task(
            crumbs_env, "AF-1", "Done child", status="closed",
            links={"parent": "AF-T1"}
        )

        result = asyncio.run(crumb_trail_close("AF-T1"))
        assert result["success"] is True
        assert result["status"] == "closed"

    def test_closes_childless_trail(self, crumbs_env: Path) -> None:
        """Closes a trail that has no children."""
        _seed_trail(crumbs_env, "AF-T1", "Empty trail")

        result = asyncio.run(crumb_trail_close("AF-T1"))
        assert result["success"] is True
        assert result["status"] == "closed"

    def test_raises_when_open_children_exist(self, crumbs_env: Path) -> None:
        """Raises RuntimeError when trail has open children."""
        _seed_trail(crumbs_env, "AF-T1", "Blocked trail")
        _seed_task(crumbs_env, "AF-1", "Open child", links={"parent": "AF-T1"})

        with pytest.raises(RuntimeError, match="open child"):
            asyncio.run(crumb_trail_close("AF-T1"))

    def test_already_closed_returns_success_false(self, crumbs_env: Path) -> None:
        """Returns success=False and message='already closed' for closed trails."""
        _seed_trail(crumbs_env, "AF-T1", "Already closed trail")
        # Manually mark it closed
        tasks_path = crumbs_env / "tasks.jsonl"
        records = _crumb.read_tasks(tasks_path)
        for r in records:
            if r.get("id") == "AF-T1":
                r["status"] = "closed"
        _crumb.write_tasks(tasks_path, records)

        result = asyncio.run(crumb_trail_close("AF-T1"))
        assert result["success"] is False
        assert result["message"] == "already closed"

    def test_raises_for_unknown_trail_id(self, crumbs_env: Path) -> None:
        """Raises RuntimeError when trail ID does not exist."""
        with pytest.raises(RuntimeError, match="not found"):
            asyncio.run(crumb_trail_close("AF-T9999"))

    def test_persists_closed_status_to_disk(self, crumbs_env: Path) -> None:
        """Closed trail status is written to tasks.jsonl."""
        _seed_trail(crumbs_env, "AF-T1", "Persist trail")

        asyncio.run(crumb_trail_close("AF-T1"))

        tasks_path = crumbs_env / "tasks.jsonl"
        tasks = _crumb.read_tasks(tasks_path)
        trail = next(t for t in tasks if t["id"] == "AF-T1")
        assert trail["status"] == "closed"


# ---------------------------------------------------------------------------
# TestCrumbClose
# ---------------------------------------------------------------------------


class TestCrumbClose:
    """Tests for the crumb_close MCP tool."""

    def test_closes_single_crumb(self, crumbs_env: Path) -> None:
        """Returns success with the closed ID in the 'closed' list."""
        _seed_task(crumbs_env, "AF-1", "Task to close")

        result = asyncio.run(crumb_close(["AF-1"]))
        assert isinstance(result, dict)
        assert "AF-1" in result["closed"]
        assert result["skipped"] == []

    def test_closes_multiple_crumbs(self, crumbs_env: Path) -> None:
        """Can close multiple crumbs in one call."""
        _seed_task(crumbs_env, "AF-1", "First")
        _seed_task(crumbs_env, "AF-2", "Second")

        result = asyncio.run(crumb_close(["AF-1", "AF-2"]))
        assert set(result["closed"]) == {"AF-1", "AF-2"}
        assert result["skipped"] == []

    def test_skips_already_closed_crumbs(self, crumbs_env: Path) -> None:
        """Already-closed crumbs appear in 'skipped', not 'closed'."""
        _seed_task(crumbs_env, "AF-1", "Open task")
        _seed_task(crumbs_env, "AF-2", "Closed task", status="closed")

        result = asyncio.run(crumb_close(["AF-1", "AF-2"]))
        assert "AF-1" in result["closed"]
        assert "AF-2" in result["skipped"]

    def test_raises_for_unknown_id(self, crumbs_env: Path) -> None:
        """Raises RuntimeError when any provided ID does not exist."""
        with pytest.raises(RuntimeError, match="not found"):
            asyncio.run(crumb_close(["AF-9999"]))

    def test_tasks_field_contains_affected_records(self, crumbs_env: Path) -> None:
        """The 'tasks' field contains full crumb objects for all affected IDs."""
        _seed_task(crumbs_env, "AF-1", "Closeable")

        result = asyncio.run(crumb_close(["AF-1"]))
        assert isinstance(result["tasks"], list)
        assert len(result["tasks"]) == 1
        task = result["tasks"][0]
        assert task["id"] == "AF-1"
        assert task["status"] == "closed"

    def test_persists_closed_status_to_disk(self, crumbs_env: Path) -> None:
        """Closed status is written to tasks.jsonl."""
        _seed_task(crumbs_env, "AF-1", "Disk check")

        asyncio.run(crumb_close(["AF-1"]))

        tasks_path = crumbs_env / "tasks.jsonl"
        disk_tasks = _crumb.read_tasks(tasks_path)
        task = next(t for t in disk_tasks if t["id"] == "AF-1")
        assert task["status"] == "closed"


# ---------------------------------------------------------------------------
# TestCrumbReady
# ---------------------------------------------------------------------------


class TestCrumbReady:
    """Tests for the crumb_ready MCP tool."""

    def test_returns_unblocked_open_crumbs(self, crumbs_env: Path) -> None:
        """Returns open crumbs that have no unresolved blockers."""
        _seed_task(crumbs_env, "AF-1", "Ready task")
        _seed_task(crumbs_env, "AF-2", "Another ready task")

        result = asyncio.run(crumb_ready())
        assert isinstance(result, list)
        ids = {r["id"] for r in result}
        assert "AF-1" in ids
        assert "AF-2" in ids

    def test_excludes_blocked_crumbs(self, crumbs_env: Path) -> None:
        """Crumbs blocked by an open blocker are not in ready list."""
        _seed_task(crumbs_env, "AF-1", "Blocker task")
        _seed_task(
            crumbs_env, "AF-2", "Blocked task",
            links={"blocked_by": ["AF-1"]}
        )

        result = asyncio.run(crumb_ready())
        ids = {r["id"] for r in result}
        assert "AF-1" in ids   # Blocker itself is ready
        assert "AF-2" not in ids  # Blocked task excluded

    def test_excludes_in_progress_crumbs(self, crumbs_env: Path) -> None:
        """In-progress crumbs are not returned (already claimed)."""
        _seed_task(crumbs_env, "AF-1", "In-progress task", status="in_progress")
        _seed_task(crumbs_env, "AF-2", "Open task")

        result = asyncio.run(crumb_ready())
        ids = {r["id"] for r in result}
        assert "AF-1" not in ids
        assert "AF-2" in ids

    def test_excludes_trails(self, crumbs_env: Path) -> None:
        """Trail records are never included in the ready list."""
        _seed_trail(crumbs_env, "AF-T1", "A trail")
        _seed_task(crumbs_env, "AF-1", "A task")

        result = asyncio.run(crumb_ready())
        ids = {r["id"] for r in result}
        assert "AF-T1" not in ids

    def test_respects_limit(self, crumbs_env: Path) -> None:
        """Respects the limit parameter."""
        for i in range(1, 6):
            _seed_task(crumbs_env, f"AF-{i}", f"Task {i}")

        result = asyncio.run(crumb_ready(limit=2))
        assert len(result) == 2

    def test_resolved_blocker_makes_crumb_ready(self, crumbs_env: Path) -> None:
        """A crumb whose blocker is closed is included in the ready list."""
        _seed_task(crumbs_env, "AF-1", "Closed blocker", status="closed")
        _seed_task(
            crumbs_env, "AF-2", "Previously blocked",
            links={"blocked_by": ["AF-1"]}
        )

        result = asyncio.run(crumb_ready())
        ids = {r["id"] for r in result}
        assert "AF-2" in ids

    def test_empty_when_no_unblocked_open_tasks(self, crumbs_env: Path) -> None:
        """Returns empty list when all open tasks are blocked."""
        _seed_task(crumbs_env, "AF-1", "Blocker", status="in_progress")
        _seed_task(
            crumbs_env, "AF-2", "Blocked",
            links={"blocked_by": ["AF-1"]}
        )

        result = asyncio.run(crumb_ready())
        # AF-1 is in_progress (excluded), AF-2 is blocked by AF-1 (in_progress is not closed)
        ids = {r["id"] for r in result}
        assert "AF-2" not in ids


# ---------------------------------------------------------------------------
# TestCrumbBlocked
# ---------------------------------------------------------------------------


class TestCrumbBlocked:
    """Tests for the crumb_blocked MCP tool."""

    def test_returns_blocked_crumbs(self, crumbs_env: Path) -> None:
        """Returns open crumbs with unresolved blockers."""
        _seed_task(crumbs_env, "AF-1", "Blocker task")
        _seed_task(
            crumbs_env, "AF-2", "Blocked task",
            links={"blocked_by": ["AF-1"]}
        )

        result = asyncio.run(crumb_blocked())
        assert isinstance(result, list)
        ids = {r["id"] for r in result}
        assert "AF-2" in ids
        assert "AF-1" not in ids

    def test_includes_blockers_field(self, crumbs_env: Path) -> None:
        """Each blocked crumb has a 'blockers' field listing unresolved blocker IDs."""
        _seed_task(crumbs_env, "AF-1", "First blocker")
        _seed_task(crumbs_env, "AF-2", "Second blocker")
        _seed_task(
            crumbs_env, "AF-3", "Multi-blocked",
            links={"blocked_by": ["AF-1", "AF-2"]}
        )

        result = asyncio.run(crumb_blocked())
        blocked_task = next(r for r in result if r["id"] == "AF-3")
        assert set(blocked_task["blockers"]) == {"AF-1", "AF-2"}

    def test_excludes_crumbs_with_closed_blockers(self, crumbs_env: Path) -> None:
        """Crumbs whose all blockers are closed are not in the blocked list."""
        _seed_task(crumbs_env, "AF-1", "Closed blocker", status="closed")
        _seed_task(
            crumbs_env, "AF-2", "Unblocked task",
            links={"blocked_by": ["AF-1"]}
        )

        result = asyncio.run(crumb_blocked())
        ids = {r["id"] for r in result}
        assert "AF-2" not in ids

    def test_excludes_trails(self, crumbs_env: Path) -> None:
        """Trail records are never included even if theoretically blocked."""
        _seed_trail(crumbs_env, "AF-T1", "A trail")
        _seed_task(crumbs_env, "AF-1", "A regular blocker task")

        result = asyncio.run(crumb_blocked())
        ids = {r["id"] for r in result}
        assert "AF-T1" not in ids

    def test_empty_when_no_blocked_crumbs(self, crumbs_env: Path) -> None:
        """Returns empty list when no crumbs are blocked."""
        _seed_task(crumbs_env, "AF-1", "Free task")

        result = asyncio.run(crumb_blocked())
        assert result == []

    def test_result_has_schema_fields(self, crumbs_env: Path) -> None:
        """Each result object has required schema fields plus 'blockers'."""
        _seed_task(crumbs_env, "AF-1", "A blocker")
        _seed_task(
            crumbs_env, "AF-2", "Blocked task",
            links={"blocked_by": ["AF-1"]}
        )

        result = asyncio.run(crumb_blocked())
        blocked_task = next(r for r in result if r["id"] == "AF-2")
        for field in ("id", "title", "type", "status", "priority", "blockers"):
            assert field in blocked_task, f"Missing '{field}' in crumb_blocked result"


# ---------------------------------------------------------------------------
# TestCrumbLink
# ---------------------------------------------------------------------------


class TestCrumbLink:
    """Tests for the crumb_link MCP tool."""

    def test_sets_parent_link(self, crumbs_env: Path) -> None:
        """Sets a parent trail link on the crumb."""
        _seed_trail(crumbs_env, "AF-T1", "Parent trail")
        _seed_task(crumbs_env, "AF-1", "Child task")

        result = asyncio.run(crumb_link("AF-1", parent="AF-T1"))
        assert result["success"] is True
        assert result["links"]["parent"] == "AF-T1"

    def test_adds_blocked_by_link(self, crumbs_env: Path) -> None:
        """Adds a blocked_by link to the crumb."""
        _seed_task(crumbs_env, "AF-1", "Blocker")
        _seed_task(crumbs_env, "AF-2", "Task to block")

        result = asyncio.run(crumb_link("AF-2", blocked_by="AF-1"))
        assert result["success"] is True
        assert "AF-1" in result["links"]["blocked_by"]

    def test_removes_blocked_by_link(self, crumbs_env: Path) -> None:
        """Removes a blocked_by reference from the crumb."""
        _seed_task(
            crumbs_env, "AF-1", "Currently blocked",
            links={"blocked_by": ["AF-99"]}
        )

        result = asyncio.run(crumb_link("AF-1", remove_blocked_by="AF-99"))
        assert result["success"] is True
        blocked_by = result["links"].get("blocked_by", [])
        assert "AF-99" not in blocked_by

    def test_sets_discovered_from_link(self, crumbs_env: Path) -> None:
        """Sets a discovered_from provenance link."""
        _seed_task(crumbs_env, "AF-1", "Discovered task")

        result = asyncio.run(crumb_link("AF-1", discovered_from="some-source"))
        assert result["success"] is True
        assert result["links"]["discovered_from"] == "some-source"

    def test_no_change_returns_success_false(self, crumbs_env: Path) -> None:
        """Returns success=False and message when no link changes were made."""
        _seed_task(crumbs_env, "AF-1", "Unchanged task")

        result = asyncio.run(crumb_link("AF-1"))
        assert result["success"] is False
        assert "no link changes" in result.get("message", "")

    def test_raises_for_unknown_crumb_id(self, crumbs_env: Path) -> None:
        """Raises RuntimeError when crumb ID does not exist."""
        with pytest.raises(RuntimeError, match="not found"):
            asyncio.run(crumb_link("AF-9999", parent="AF-T1"))

    def test_persists_link_to_disk(self, crumbs_env: Path) -> None:
        """Link changes are persisted to tasks.jsonl."""
        _seed_trail(crumbs_env, "AF-T1", "Trail")
        _seed_task(crumbs_env, "AF-1", "Task")

        asyncio.run(crumb_link("AF-1", parent="AF-T1"))

        tasks_path = crumbs_env / "tasks.jsonl"
        disk_tasks = _crumb.read_tasks(tasks_path)
        task = next(t for t in disk_tasks if t["id"] == "AF-1")
        assert task.get("links", {}).get("parent") == "AF-T1"

    def test_duplicate_blocked_by_not_added_twice(self, crumbs_env: Path) -> None:
        """Adding the same blocked_by reference twice does not duplicate it."""
        _seed_task(crumbs_env, "AF-1", "Blocker")
        _seed_task(
            crumbs_env, "AF-2", "Already blocked",
            links={"blocked_by": ["AF-1"]}
        )

        result = asyncio.run(crumb_link("AF-2", blocked_by="AF-1"))
        # No-op: AF-1 already in blocked_by
        assert result["success"] is False
        blocked = result["links"].get("blocked_by", [])
        assert blocked.count("AF-1") == 1

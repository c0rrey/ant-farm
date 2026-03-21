"""Tests for the five core CRUD commands in crumb.py.

Tests are grouped into one class per command:
  TestCreate  — cmd_create (crumb create)
  TestShow    — cmd_show   (crumb show)
  TestUpdate  — cmd_update (crumb update)
  TestClose   — cmd_close  (crumb close)
  TestReopen  — cmd_reopen (crumb reopen)

All tests use the ``crumbs_env`` fixture (from conftest.py) which provides
an isolated ``.crumbs/`` directory and monkeypatches ``crumb.find_crumbs_dir``.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict

import pytest

from crumb import (
    cmd_close,
    cmd_create,
    cmd_reopen,
    cmd_show,
    cmd_update,
    read_config,
    read_tasks,
    write_tasks,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_create_args(**kwargs: Any) -> argparse.Namespace:
    """Build an argparse.Namespace for cmd_create with sane defaults.

    Args:
        **kwargs: Field overrides for the Namespace.

    Returns:
        Namespace with all fields cmd_create expects.
    """
    defaults: Dict[str, Any] = {
        "title": None,
        "from_json": None,
        "from_file": None,
        "priority": None,
        "crumb_type": None,
        "description": None,
        "json_output": False,
    }
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


def _make_show_args(crumb_id: str, json_output: bool = False) -> argparse.Namespace:
    """Build an argparse.Namespace for cmd_show.

    Args:
        crumb_id: The ID to look up.
        json_output: Whether to request JSON output mode.

    Returns:
        Namespace with ``id`` and ``json_output`` set.
    """
    return argparse.Namespace(id=crumb_id, json_output=json_output)


def _make_update_args(**kwargs: Any) -> argparse.Namespace:
    """Build an argparse.Namespace for cmd_update with sane defaults.

    Args:
        **kwargs: Field overrides (``id`` is required by callers).

    Returns:
        Namespace with all fields cmd_update expects.
    """
    defaults: Dict[str, Any] = {
        "id": None,
        "status": None,
        "note": None,
        "title": None,
        "priority": None,
        "description": None,
        "from_json": None,
        "json_output": False,
    }
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


def _make_close_args(*ids: str) -> argparse.Namespace:
    """Build an argparse.Namespace for cmd_close.

    Args:
        *ids: One or more crumb IDs to close.

    Returns:
        Namespace with ``ids`` set to the provided list.
    """
    return argparse.Namespace(ids=list(ids))


def _make_reopen_args(crumb_id: str) -> argparse.Namespace:
    """Build an argparse.Namespace for cmd_reopen.

    Args:
        crumb_id: The ID to reopen.

    Returns:
        Namespace with ``id`` set.
    """
    return argparse.Namespace(id=crumb_id)


def _seed_task(crumbs_env: Path, **fields: Any) -> Dict[str, Any]:
    """Write a single task to tasks.jsonl for test setup.

    Merges the provided fields over a minimal valid task record.

    Args:
        crumbs_env: Path to the isolated .crumbs/ directory.
        **fields: Fields to include/override on the record.

    Returns:
        The task dict that was written.
    """
    defaults: Dict[str, Any] = {
        "id": "AF-1",
        "type": "task",
        "title": "Test task",
        "status": "open",
        "priority": "P2",
        "created_at": "2026-01-01T00:00:00Z",
        "updated_at": "2026-01-01T00:00:00Z",
    }
    defaults.update(fields)
    tasks_file = crumbs_env / "tasks.jsonl"
    tasks_file.write_text(json.dumps(defaults) + "\n", encoding="utf-8")
    return defaults


# ---------------------------------------------------------------------------
# TestCreate
# ---------------------------------------------------------------------------


class TestCreate:
    """Tests for cmd_create."""

    def test_create_with_title_produces_correct_prefix_id(
        self, crumbs_env: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """cmd_create --title produces a crumb whose ID uses the config prefix."""
        args = _make_create_args(title="First task")
        cmd_create(args)

        tasks_file = crumbs_env / "tasks.jsonl"
        tasks = read_tasks(tasks_file)
        assert len(tasks) == 1
        assert tasks[0]["id"] == "AF-1"

    def test_create_with_title_sets_default_priority(
        self, crumbs_env: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """cmd_create --title uses default_priority from config (P2) when not specified."""
        args = _make_create_args(title="Priority test")
        cmd_create(args)

        tasks_file = crumbs_env / "tasks.jsonl"
        tasks = read_tasks(tasks_file)
        assert tasks[0]["priority"] == "P2"

    def test_create_with_title_sets_default_status_open(
        self, crumbs_env: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """cmd_create --title sets status to 'open' by default."""
        args = _make_create_args(title="Status test")
        cmd_create(args)

        tasks_file = crumbs_env / "tasks.jsonl"
        tasks = read_tasks(tasks_file)
        assert tasks[0]["status"] == "open"

    def test_create_increments_next_crumb_id(
        self, crumbs_env: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """cmd_create increments next_crumb_id in config.json after creating a crumb."""
        config_before = read_config()
        assert config_before["next_crumb_id"] == 1

        args = _make_create_args(title="Counter test")
        cmd_create(args)

        config_after = read_config()
        assert config_after["next_crumb_id"] == 2

    def test_create_two_tasks_get_sequential_ids(
        self, crumbs_env: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Creating two tasks produces IDs AF-1 and AF-2 in order."""
        cmd_create(_make_create_args(title="First"))
        cmd_create(_make_create_args(title="Second"))

        tasks_file = crumbs_env / "tasks.jsonl"
        tasks = read_tasks(tasks_file)
        assert len(tasks) == 2
        assert tasks[0]["id"] == "AF-1"
        assert tasks[1]["id"] == "AF-2"

    def test_create_prints_created_message(
        self, crumbs_env: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """cmd_create prints 'created AF-1' to stdout."""
        args = _make_create_args(title="Output test")
        cmd_create(args)

        captured = capsys.readouterr()
        assert "created AF-1" in captured.out

    def test_create_from_json_all_fields(
        self, crumbs_env: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """cmd_create --from-json accepts a JSON payload with all supported fields."""
        payload: Dict[str, Any] = {
            "title": "JSON task",
            "type": "bug",
            "description": "A bug description",
            "priority": "P1",
            "status": "open",
            "acceptance_criteria": ["Fix the bug", "Add a test"],
            "scope": {"agent_type": "python-pro"},
            "links": {"blocked_by": []},
            "notes": ["Initial note"],
        }
        args = _make_create_args(from_json=json.dumps(payload))
        cmd_create(args)

        tasks_file = crumbs_env / "tasks.jsonl"
        tasks = read_tasks(tasks_file)
        assert len(tasks) == 1
        task = tasks[0]
        assert task["title"] == "JSON task"
        assert task["type"] == "bug"
        assert task["description"] == "A bug description"
        assert task["priority"] == "P1"
        assert task["acceptance_criteria"] == ["Fix the bug", "Add a test"]
        assert task["scope"] == {"agent_type": "python-pro"}
        assert task["notes"] == ["Initial note"]

    def test_create_from_json_assigns_auto_id(
        self, crumbs_env: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """cmd_create --from-json without an 'id' field auto-assigns AF-1."""
        payload = {"title": "Auto-ID task"}
        args = _make_create_args(from_json=json.dumps(payload))
        cmd_create(args)

        tasks_file = crumbs_env / "tasks.jsonl"
        tasks = read_tasks(tasks_file)
        assert tasks[0]["id"] == "AF-1"

    def test_create_from_json_explicit_id_preserved(
        self, crumbs_env: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """cmd_create --from-json with an explicit 'id' uses that ID."""
        payload = {"id": "AF-99", "title": "Explicit ID task"}
        args = _make_create_args(from_json=json.dumps(payload))
        cmd_create(args)

        tasks_file = crumbs_env / "tasks.jsonl"
        tasks = read_tasks(tasks_file)
        assert tasks[0]["id"] == "AF-99"

    def test_create_from_json_cli_title_overrides_json_title(
        self, crumbs_env: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """When both --title and --from-json specify title, CLI --title wins."""
        payload = {"title": "JSON title"}
        args = _make_create_args(
            title="CLI title", from_json=json.dumps(payload)
        )
        cmd_create(args)

        tasks_file = crumbs_env / "tasks.jsonl"
        tasks = read_tasks(tasks_file)
        assert tasks[0]["title"] == "CLI title"

    def test_create_without_title_and_without_from_json_exits(
        self, crumbs_env: Path
    ) -> None:
        """cmd_create with neither --title nor --from-json raises SystemExit."""
        args = _make_create_args()
        with pytest.raises(SystemExit):
            cmd_create(args)

    def test_create_trail_type_via_from_json_exits(
        self, crumbs_env: Path
    ) -> None:
        """cmd_create with type='trail' in --from-json raises SystemExit."""
        payload = {"title": "A trail", "type": "trail"}
        args = _make_create_args(from_json=json.dumps(payload))
        with pytest.raises(SystemExit):
            cmd_create(args)

    def test_create_from_file_creates_crumb(
        self, crumbs_env: Path, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """cmd_create --from-file reads a JSON file and creates the crumb."""
        payload: Dict[str, Any] = {
            "title": "File task",
            "type": "bug",
            "priority": "P1",
            "description": "A bug from a file",
        }
        json_file = tmp_path / "crumb.json"
        json_file.write_text(json.dumps(payload), encoding="utf-8")

        args = _make_create_args(from_file=str(json_file))
        cmd_create(args)

        tasks_file = crumbs_env / "tasks.jsonl"
        tasks = read_tasks(tasks_file)
        assert len(tasks) == 1
        task = tasks[0]
        assert task["title"] == "File task"
        assert task["type"] == "bug"
        assert task["priority"] == "P1"
        assert task["description"] == "A bug from a file"

    def test_create_from_file_nonexistent_path_exits(
        self, crumbs_env: Path, tmp_path: Path
    ) -> None:
        """cmd_create --from-file with a missing path raises SystemExit."""
        missing = str(tmp_path / "does_not_exist.json")
        args = _make_create_args(from_file=missing)
        with pytest.raises(SystemExit):
            cmd_create(args)

    def test_create_from_file_invalid_json_exits(
        self, crumbs_env: Path, tmp_path: Path
    ) -> None:
        """cmd_create --from-file with invalid JSON content raises SystemExit."""
        bad_file = tmp_path / "bad.json"
        bad_file.write_text("{not valid json", encoding="utf-8")

        args = _make_create_args(from_file=str(bad_file))
        with pytest.raises(SystemExit):
            cmd_create(args)

    def test_create_from_file_and_from_json_mutual_exclusion_exits(
        self, crumbs_env: Path, tmp_path: Path
    ) -> None:
        """cmd_create with both --from-file and --from-json raises SystemExit."""
        json_file = tmp_path / "crumb.json"
        json_file.write_text(json.dumps({"title": "File task"}), encoding="utf-8")

        args = _make_create_args(
            from_file=str(json_file),
            from_json=json.dumps({"title": "JSON task"}),
        )
        with pytest.raises(SystemExit):
            cmd_create(args)

    def test_create_json_output_returns_valid_json_object(
        self, crumbs_env: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """cmd_create --json prints a JSON object with the created crumb."""
        args = _make_create_args(title="JSON create test", json_output=True)
        cmd_create(args)

        captured = capsys.readouterr()
        parsed = json.loads(captured.out)
        assert isinstance(parsed, dict), "Expected a JSON object"

    def test_create_json_output_contains_required_fields(
        self, crumbs_env: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """cmd_create --json output includes all required schema fields."""
        args = _make_create_args(title="Field check", json_output=True)
        cmd_create(args)

        captured = capsys.readouterr()
        parsed = json.loads(captured.out)
        for field in ("id", "title", "type", "status", "priority",
                      "description", "acceptance_criteria", "scope", "links", "notes"):
            assert field in parsed, f"Required field '{field}' missing from create --json output"

    def test_create_json_output_id_matches_created_record(
        self, crumbs_env: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """cmd_create --json output 'id' field matches the record written to tasks.jsonl."""
        args = _make_create_args(title="ID match", json_output=True)
        cmd_create(args)

        captured = capsys.readouterr()
        parsed = json.loads(captured.out)

        tasks_file = crumbs_env / "tasks.jsonl"
        tasks = read_tasks(tasks_file)
        assert parsed["id"] == tasks[0]["id"]

    def test_create_json_output_no_human_text(
        self, crumbs_env: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """cmd_create --json does not print human-readable 'created <ID>' text."""
        args = _make_create_args(title="Silent create", json_output=True)
        cmd_create(args)

        captured = capsys.readouterr()
        # The human-readable confirmation is "created AF-1"; the JSON output also
        # contains "created_at" as a field name, so check for the specific phrase.
        assert "created AF-" not in captured.out

    def test_create_without_json_still_human_readable(
        self, crumbs_env: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """cmd_create without --json still prints human-readable output unchanged."""
        args = _make_create_args(title="Human output", json_output=False)
        cmd_create(args)

        captured = capsys.readouterr()
        assert "created AF-1" in captured.out
        assert not captured.out.startswith("{"), "Output must not be JSON when --json absent"


# ---------------------------------------------------------------------------
# TestShow
# ---------------------------------------------------------------------------


class TestShow:
    """Tests for cmd_show."""

    def test_show_displays_title(
        self, crumbs_env: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """cmd_show prints the crumb title to stdout."""
        _seed_task(crumbs_env, id="AF-1", title="My visible task")
        cmd_show(_make_show_args("AF-1"))

        captured = capsys.readouterr()
        assert "My visible task" in captured.out

    def test_show_displays_status(
        self, crumbs_env: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """cmd_show prints the crumb status to stdout."""
        _seed_task(crumbs_env, id="AF-1", status="in_progress")
        cmd_show(_make_show_args("AF-1"))

        captured = capsys.readouterr()
        assert "in_progress" in captured.out

    def test_show_displays_priority(
        self, crumbs_env: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """cmd_show prints the crumb priority to stdout."""
        _seed_task(crumbs_env, id="AF-1", priority="P0")
        cmd_show(_make_show_args("AF-1"))

        captured = capsys.readouterr()
        assert "P0" in captured.out

    def test_show_displays_description(
        self, crumbs_env: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """cmd_show prints the crumb description when present."""
        _seed_task(crumbs_env, id="AF-1", description="Detailed description text")
        cmd_show(_make_show_args("AF-1"))

        captured = capsys.readouterr()
        assert "Detailed description text" in captured.out

    def test_show_displays_id(
        self, crumbs_env: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """cmd_show prints the crumb ID to stdout."""
        _seed_task(crumbs_env, id="AF-42", title="ID display test")
        cmd_show(_make_show_args("AF-42"))

        captured = capsys.readouterr()
        assert "AF-42" in captured.out

    def test_show_nonexistent_id_raises_system_exit(
        self, crumbs_env: Path
    ) -> None:
        """cmd_show raises SystemExit when the requested ID does not exist."""
        _seed_task(crumbs_env, id="AF-1", title="Existing task")
        with pytest.raises(SystemExit):
            cmd_show(_make_show_args("AF-999"))

    def test_show_prints_error_to_stderr_for_missing_id(
        self, crumbs_env: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """cmd_show writes an error message to stderr for a nonexistent ID."""
        _seed_task(crumbs_env, id="AF-1", title="Exists")
        with pytest.raises(SystemExit):
            cmd_show(_make_show_args("AF-NOPE"))
        captured = capsys.readouterr()
        assert "AF-NOPE" in captured.err

    def test_show_omits_empty_fields(
        self, crumbs_env: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """cmd_show does not print labels for fields with empty/None values."""
        _seed_task(crumbs_env, id="AF-1", title="Minimal task")
        # The record has no description, notes, etc.
        cmd_show(_make_show_args("AF-1"))

        captured = capsys.readouterr()
        # Empty-value fields are suppressed by the implementation
        assert "Description:" not in captured.out
        assert "Notes:" not in captured.out


# ---------------------------------------------------------------------------
# TestUpdate
# ---------------------------------------------------------------------------


class TestUpdate:
    """Tests for cmd_update."""

    def test_update_changes_status(
        self, crumbs_env: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """cmd_update --status changes the crumb's status field."""
        _seed_task(crumbs_env, id="AF-1", status="open")
        cmd_update(_make_update_args(id="AF-1", status="in_progress"))

        tasks_file = crumbs_env / "tasks.jsonl"
        tasks = read_tasks(tasks_file)
        assert tasks[0]["status"] == "in_progress"

    def test_update_status_prints_updated_message(
        self, crumbs_env: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """cmd_update prints 'updated AF-1' to stdout on success."""
        _seed_task(crumbs_env, id="AF-1", status="open")
        cmd_update(_make_update_args(id="AF-1", status="in_progress"))

        captured = capsys.readouterr()
        assert "updated AF-1" in captured.out

    def test_update_adds_note(
        self, crumbs_env: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """cmd_update --note appends a timestamped note to the crumb's notes list."""
        _seed_task(crumbs_env, id="AF-1")
        cmd_update(_make_update_args(id="AF-1", note="Important observation"))

        tasks_file = crumbs_env / "tasks.jsonl"
        tasks = read_tasks(tasks_file)
        notes = tasks[0].get("notes", [])
        assert isinstance(notes, list)
        assert len(notes) == 1
        assert "Important observation" in notes[0]

    def test_update_note_appended_to_existing_notes(
        self, crumbs_env: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """cmd_update --note appends without removing existing notes."""
        existing_notes = ["2026-01-01T00:00:00Z: First note"]
        _seed_task(crumbs_env, id="AF-1", notes=existing_notes)
        cmd_update(_make_update_args(id="AF-1", note="Second note"))

        tasks_file = crumbs_env / "tasks.jsonl"
        tasks = read_tasks(tasks_file)
        notes = tasks[0].get("notes", [])
        assert len(notes) == 2
        assert "First note" in notes[0]
        assert "Second note" in notes[1]

    def test_update_from_json_merges_fields(
        self, crumbs_env: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """cmd_update --from-json merges arbitrary FIELD=VALUE pairs into the record."""
        _seed_task(crumbs_env, id="AF-1", title="Original title")
        extra = {"title": "Updated via JSON", "description": "Added description"}
        cmd_update(_make_update_args(id="AF-1", from_json=json.dumps(extra)))

        tasks_file = crumbs_env / "tasks.jsonl"
        tasks = read_tasks(tasks_file)
        assert tasks[0]["title"] == "Updated via JSON"
        assert tasks[0]["description"] == "Added description"

    def test_update_from_json_cannot_change_id(
        self, crumbs_env: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """cmd_update --from-json ignores attempts to change the protected 'id' field."""
        _seed_task(crumbs_env, id="AF-1", title="Task")
        extra = {"id": "AF-HACKED", "title": "New title"}
        cmd_update(_make_update_args(id="AF-1", from_json=json.dumps(extra)))

        tasks_file = crumbs_env / "tasks.jsonl"
        tasks = read_tasks(tasks_file)
        assert tasks[0]["id"] == "AF-1"

    def test_update_title_field(
        self, crumbs_env: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """cmd_update --title changes the crumb's title."""
        _seed_task(crumbs_env, id="AF-1", title="Old title")
        cmd_update(_make_update_args(id="AF-1", title="New title"))

        tasks_file = crumbs_env / "tasks.jsonl"
        tasks = read_tasks(tasks_file)
        assert tasks[0]["title"] == "New title"

    def test_update_priority_field(
        self, crumbs_env: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """cmd_update --priority changes the crumb's priority."""
        _seed_task(crumbs_env, id="AF-1", priority="P3")
        cmd_update(_make_update_args(id="AF-1", priority="P0"))

        tasks_file = crumbs_env / "tasks.jsonl"
        tasks = read_tasks(tasks_file)
        assert tasks[0]["priority"] == "P0"

    def test_update_closed_crumb_status_raises_system_exit(
        self, crumbs_env: Path
    ) -> None:
        """cmd_update raises SystemExit when given an unrecognised status value.

        Note: argparse enforces choices=VALID_STATUSES so an invalid value would
        normally be rejected by the parser. We test the validation path by
        bypassing argparse and passing an invalid status directly.
        """
        _seed_task(crumbs_env, id="AF-1", status="open")
        # Directly mutate the tasks.jsonl to have an unexpected status so the
        # cmd_update validator hits the invalid-status code path via --status.
        # However, because cmd_update only reads args.status (no re-validation),
        # the real guard is the closed→open transition check. We test that path:
        # set a crumb to 'closed' then try to update its status directly.
        tasks_file = crumbs_env / "tasks.jsonl"
        task = json.loads(tasks_file.read_text(encoding="utf-8").strip())
        task["status"] = "closed"
        tasks_file.write_text(json.dumps(task) + "\n", encoding="utf-8")

        # Attempting to update a closed crumb's status should exit 1
        with pytest.raises(SystemExit):
            cmd_update(_make_update_args(id="AF-1", status="in_progress"))

    def test_update_nonexistent_id_raises_system_exit(
        self, crumbs_env: Path
    ) -> None:
        """cmd_update raises SystemExit when the target crumb does not exist."""
        _seed_task(crumbs_env, id="AF-1")
        with pytest.raises(SystemExit):
            cmd_update(_make_update_args(id="AF-MISSING", status="in_progress"))

    def test_update_no_changes_prints_no_changes(
        self, crumbs_env: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """cmd_update with no actual changes prints 'no changes to' message."""
        _seed_task(crumbs_env, id="AF-1", status="open")
        # Passing the same status that's already set — no change
        cmd_update(_make_update_args(id="AF-1", status="open"))

        captured = capsys.readouterr()
        assert "no changes" in captured.out

    def test_update_json_output_returns_valid_json_object(
        self, crumbs_env: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """cmd_update --json prints a JSON object with the updated crumb."""
        _seed_task(crumbs_env, id="AF-1", status="open")
        cmd_update(_make_update_args(id="AF-1", status="in_progress", json_output=True))

        captured = capsys.readouterr()
        parsed = json.loads(captured.out)
        assert isinstance(parsed, dict), "Expected a JSON object"

    def test_update_json_output_success_field_true(
        self, crumbs_env: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """cmd_update --json output includes 'success: true' on a successful update."""
        _seed_task(crumbs_env, id="AF-1", status="open")
        cmd_update(_make_update_args(id="AF-1", status="in_progress", json_output=True))

        captured = capsys.readouterr()
        parsed = json.loads(captured.out)
        assert parsed.get("success") is True

    def test_update_json_output_contains_updated_status(
        self, crumbs_env: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """cmd_update --json output reflects the updated field value."""
        _seed_task(crumbs_env, id="AF-1", status="open")
        cmd_update(_make_update_args(id="AF-1", status="in_progress", json_output=True))

        captured = capsys.readouterr()
        parsed = json.loads(captured.out)
        assert parsed.get("status") == "in_progress"

    def test_update_json_output_no_changes_success_false(
        self, crumbs_env: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """cmd_update --json with no changes returns success=false and a message."""
        _seed_task(crumbs_env, id="AF-1", status="open")
        cmd_update(_make_update_args(id="AF-1", status="open", json_output=True))

        captured = capsys.readouterr()
        parsed = json.loads(captured.out)
        assert parsed.get("success") is False
        assert "message" in parsed

    def test_update_without_json_still_human_readable(
        self, crumbs_env: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """cmd_update without --json still prints human-readable output unchanged."""
        _seed_task(crumbs_env, id="AF-1", status="open")
        cmd_update(_make_update_args(id="AF-1", status="in_progress", json_output=False))

        captured = capsys.readouterr()
        assert "updated AF-1" in captured.out
        assert not captured.out.startswith("{"), "Output must not be JSON when --json absent"

    def test_update_json_output_contains_required_fields(
        self, crumbs_env: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """cmd_update --json output includes all required crumb schema fields plus 'success'."""
        _seed_task(crumbs_env, id="AF-1", status="open")
        cmd_update(_make_update_args(id="AF-1", status="in_progress", json_output=True))

        captured = capsys.readouterr()
        parsed = json.loads(captured.out)
        for field in ("success", "id", "title", "type", "status", "priority",
                      "description", "acceptance_criteria", "scope", "links", "notes"):
            assert field in parsed, f"Required field '{field}' missing from update --json output"


# ---------------------------------------------------------------------------
# TestClose
# ---------------------------------------------------------------------------


class TestClose:
    """Tests for cmd_close."""

    def test_close_sets_status_to_closed(
        self, crumbs_env: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """cmd_close sets the crumb's status to 'closed'."""
        _seed_task(crumbs_env, id="AF-1", status="open")
        cmd_close(_make_close_args("AF-1"))

        tasks_file = crumbs_env / "tasks.jsonl"
        tasks = read_tasks(tasks_file)
        assert tasks[0]["status"] == "closed"

    def test_close_sets_closed_at(
        self, crumbs_env: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """cmd_close stamps a closed_at timestamp on the record."""
        _seed_task(crumbs_env, id="AF-1", status="open")
        cmd_close(_make_close_args("AF-1"))

        tasks_file = crumbs_env / "tasks.jsonl"
        tasks = read_tasks(tasks_file)
        assert "closed_at" in tasks[0]
        assert tasks[0]["closed_at"]  # non-empty

    def test_close_prints_closed_message(
        self, crumbs_env: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """cmd_close prints 'closed AF-1' to stdout."""
        _seed_task(crumbs_env, id="AF-1", status="open")
        cmd_close(_make_close_args("AF-1"))

        captured = capsys.readouterr()
        assert "closed AF-1" in captured.out

    def test_close_nonexistent_id_raises_system_exit(
        self, crumbs_env: Path
    ) -> None:
        """cmd_close raises SystemExit for a nonexistent crumb ID."""
        _seed_task(crumbs_env, id="AF-1", status="open")
        with pytest.raises(SystemExit):
            cmd_close(_make_close_args("AF-999"))

    def test_close_multiple_ids(
        self, crumbs_env: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """cmd_close with multiple IDs closes all of them."""
        tasks_file = crumbs_env / "tasks.jsonl"
        records = [
            {
                "id": "AF-1",
                "type": "task",
                "title": "Task one",
                "status": "open",
                "priority": "P2",
                "created_at": "2026-01-01T00:00:00Z",
                "updated_at": "2026-01-01T00:00:00Z",
            },
            {
                "id": "AF-2",
                "type": "task",
                "title": "Task two",
                "status": "open",
                "priority": "P2",
                "created_at": "2026-01-01T00:00:00Z",
                "updated_at": "2026-01-01T00:00:00Z",
            },
            {
                "id": "AF-3",
                "type": "task",
                "title": "Task three",
                "status": "open",
                "priority": "P2",
                "created_at": "2026-01-01T00:00:00Z",
                "updated_at": "2026-01-01T00:00:00Z",
            },
        ]
        tasks_file.write_text(
            "\n".join(json.dumps(r) for r in records) + "\n", encoding="utf-8"
        )

        cmd_close(_make_close_args("AF-1", "AF-2", "AF-3"))

        tasks = read_tasks(tasks_file)
        assert all(t["status"] == "closed" for t in tasks)
        assert all("closed_at" in t for t in tasks)

    def test_close_already_closed_is_idempotent(
        self, crumbs_env: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """cmd_close on an already-closed crumb prints 'already closed', not an error."""
        _seed_task(
            crumbs_env,
            id="AF-1",
            status="closed",
            closed_at="2026-01-01T00:00:00Z",
        )
        cmd_close(_make_close_args("AF-1"))

        captured = capsys.readouterr()
        assert "already closed" in captured.out

    def test_close_partial_multi_id_fails_on_unknown(
        self, crumbs_env: Path
    ) -> None:
        """cmd_close with a mix of valid and invalid IDs raises SystemExit."""
        _seed_task(crumbs_env, id="AF-1", status="open")
        with pytest.raises(SystemExit):
            cmd_close(_make_close_args("AF-1", "AF-UNKNOWN"))


# ---------------------------------------------------------------------------
# TestReopen
# ---------------------------------------------------------------------------


class TestReopen:
    """Tests for cmd_reopen."""

    def test_reopen_sets_status_to_open(
        self, crumbs_env: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """cmd_reopen restores the crumb's status to 'open'."""
        _seed_task(
            crumbs_env,
            id="AF-1",
            status="closed",
            closed_at="2026-01-01T00:00:00Z",
        )
        cmd_reopen(_make_reopen_args("AF-1"))

        tasks_file = crumbs_env / "tasks.jsonl"
        tasks = read_tasks(tasks_file)
        assert tasks[0]["status"] == "open"

    def test_reopen_clears_closed_at(
        self, crumbs_env: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """cmd_reopen removes the closed_at field from the record."""
        _seed_task(
            crumbs_env,
            id="AF-1",
            status="closed",
            closed_at="2026-01-01T00:00:00Z",
        )
        cmd_reopen(_make_reopen_args("AF-1"))

        tasks_file = crumbs_env / "tasks.jsonl"
        tasks = read_tasks(tasks_file)
        assert "closed_at" not in tasks[0]

    def test_reopen_prints_reopened_message(
        self, crumbs_env: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """cmd_reopen prints 'reopened AF-1' to stdout."""
        _seed_task(
            crumbs_env,
            id="AF-1",
            status="closed",
            closed_at="2026-01-01T00:00:00Z",
        )
        cmd_reopen(_make_reopen_args("AF-1"))

        captured = capsys.readouterr()
        assert "reopened AF-1" in captured.out

    def test_reopen_non_closed_crumb_raises_system_exit(
        self, crumbs_env: Path
    ) -> None:
        """cmd_reopen raises SystemExit for a crumb that is not closed."""
        _seed_task(crumbs_env, id="AF-1", status="open")
        with pytest.raises(SystemExit):
            cmd_reopen(_make_reopen_args("AF-1"))

    def test_reopen_in_progress_crumb_raises_system_exit(
        self, crumbs_env: Path
    ) -> None:
        """cmd_reopen raises SystemExit for a crumb in 'in_progress' status."""
        _seed_task(crumbs_env, id="AF-1", status="in_progress")
        with pytest.raises(SystemExit):
            cmd_reopen(_make_reopen_args("AF-1"))

    def test_reopen_nonexistent_id_raises_system_exit(
        self, crumbs_env: Path
    ) -> None:
        """cmd_reopen raises SystemExit when the requested ID does not exist."""
        _seed_task(crumbs_env, id="AF-1", status="closed", closed_at="2026-01-01T00:00:00Z")
        with pytest.raises(SystemExit):
            cmd_reopen(_make_reopen_args("AF-MISSING"))

    def test_reopen_updates_updated_at(
        self, crumbs_env: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """cmd_reopen updates the updated_at timestamp on the record."""
        original_updated_at = "2026-01-01T00:00:00Z"
        _seed_task(
            crumbs_env,
            id="AF-1",
            status="closed",
            closed_at="2026-01-01T00:00:00Z",
            updated_at=original_updated_at,
        )
        cmd_reopen(_make_reopen_args("AF-1"))

        tasks_file = crumbs_env / "tasks.jsonl"
        tasks = read_tasks(tasks_file)
        # updated_at should be set to a new timestamp (not the original)
        assert tasks[0]["updated_at"] != original_updated_at


# ---------------------------------------------------------------------------
# TestWriteTasksCleanup
# ---------------------------------------------------------------------------


class TestWriteTasksCleanup:
    """Tests for write_tasks temp-file cleanup on failure."""

    def test_write_tasks_cleans_up_tmp_on_json_serialization_error(
        self, tmp_path: Path
    ) -> None:
        """write_tasks removes .jsonl.tmp when json.dumps raises a TypeError.

        A record containing a non-serialisable value (e.g. a set) causes
        json.dumps to raise TypeError mid-write.  The temp file must not
        remain on disk after the exception propagates.
        """
        tasks_path = tmp_path / "tasks.jsonl"
        tasks_path.write_text("", encoding="utf-8")
        tmp_path_file = tasks_path.with_suffix(".jsonl.tmp")

        # set is not JSON-serialisable — json.dumps will raise TypeError.
        bad_records = [{"id": "AF-1", "bad_field": {1, 2, 3}}]

        with pytest.raises((TypeError, SystemExit)):
            write_tasks(tasks_path, bad_records)

        assert not tmp_path_file.exists(), (
            ".jsonl.tmp must be removed after a json.dumps failure"
        )

    def test_write_tasks_tmp_absent_after_successful_write(
        self, tmp_path: Path
    ) -> None:
        """After a successful write_tasks call, no .jsonl.tmp file is left behind."""
        tasks_path = tmp_path / "tasks.jsonl"
        tasks_path.write_text("", encoding="utf-8")
        tmp_path_file = tasks_path.with_suffix(".jsonl.tmp")

        write_tasks(tasks_path, [{"id": "AF-1", "title": "OK"}])

        assert not tmp_path_file.exists(), (
            ".jsonl.tmp must not remain after a successful write"
        )

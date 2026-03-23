"""Tests for trail subcommands and tree command in crumb.py.

Covers:
  _cmd_trail_create, _cmd_trail_show, _cmd_trail_list, _cmd_trail_close,
  _auto_close_trail_if_complete, _auto_reopen_trail_if_needed, cmd_tree,
  cmd_validate_trail, _validate_single_trail, _count_crumb_files.

All tests use the ``crumbs_env`` fixture so no real .crumbs/ directory is
touched.  Commands are called directly (not through subprocess) using
``argparse.Namespace`` objects to construct the ``args`` parameter.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List, Optional

import pytest

import crumb
from crumb import (
    _auto_close_trail_if_complete,
    _auto_reopen_trail_if_needed,
    _cmd_trail_close,
    _cmd_trail_create,
    _cmd_trail_list,
    _cmd_trail_show,
    _count_crumb_files,
    _validate_single_trail,
    cmd_tree,
    cmd_validate_trail,
    read_config,
    read_tasks,
    write_tasks,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_args(**kwargs: Any) -> argparse.Namespace:
    """Return an argparse.Namespace populated from kwargs."""
    return argparse.Namespace(**kwargs)


def _trail_args(title: str, **kwargs: Any) -> argparse.Namespace:
    """Return Namespace suitable for _cmd_trail_create."""
    return _make_args(
        title=title,
        description=kwargs.get("description", None),
        priority=kwargs.get("priority", None),
        acceptance_criteria=kwargs.get("acceptance_criteria", None),
    )


def _write_records(crumbs_env: Path, records: List[Dict[str, Any]]) -> None:
    """Write records directly to tasks.jsonl under crumbs_env."""
    tasks_file = crumbs_env / "tasks.jsonl"
    tasks_file.write_text(
        "\n".join(json.dumps(r) for r in records) + ("\n" if records else ""),
        encoding="utf-8",
    )


# ---------------------------------------------------------------------------
# TestTrail
# ---------------------------------------------------------------------------


class TestTrail:
    """Tests for the trail subcommands."""

    # ------------------------------------------------------------------
    # _cmd_trail_create
    # ------------------------------------------------------------------

    def test_create_produces_trail_record(
        self, crumbs_env: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """_cmd_trail_create appends a record with type='trail' to tasks.jsonl."""
        _cmd_trail_create(_trail_args("My First Trail"))
        tasks = read_tasks(crumbs_env / "tasks.jsonl")
        assert len(tasks) == 1
        assert tasks[0]["type"] == "trail"

    def test_create_assigns_t_prefixed_id(
        self, crumbs_env: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """_cmd_trail_create assigns an AF-T{n} ID using the config prefix."""
        _cmd_trail_create(_trail_args("Trail Alpha"))
        tasks = read_tasks(crumbs_env / "tasks.jsonl")
        assert tasks[0]["id"] == "AF-T1"

    def test_create_second_trail_gets_t2_id(
        self, crumbs_env: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """A second trail create call receives AF-T2."""
        _cmd_trail_create(_trail_args("Trail Alpha"))
        _cmd_trail_create(_trail_args("Trail Beta"))
        tasks = read_tasks(crumbs_env / "tasks.jsonl")
        ids = [t["id"] for t in tasks]
        assert "AF-T1" in ids
        assert "AF-T2" in ids

    def test_create_increments_next_trail_id(
        self, crumbs_env: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """_cmd_trail_create increments next_trail_id in config.json."""
        config_before = read_config()
        assert config_before["next_trail_id"] == 1
        _cmd_trail_create(_trail_args("Trail One"))
        config_after = read_config()
        assert config_after["next_trail_id"] == 2

    def test_create_sets_status_open(
        self, crumbs_env: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Newly created trail has status='open'."""
        _cmd_trail_create(_trail_args("Open Trail"))
        tasks = read_tasks(crumbs_env / "tasks.jsonl")
        assert tasks[0]["status"] == "open"

    def test_create_stores_title(
        self, crumbs_env: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """_cmd_trail_create stores the provided title."""
        _cmd_trail_create(_trail_args("Specific Title"))
        tasks = read_tasks(crumbs_env / "tasks.jsonl")
        assert tasks[0]["title"] == "Specific Title"

    def test_create_stores_optional_description(
        self, crumbs_env: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """_cmd_trail_create stores description when provided."""
        _cmd_trail_create(_trail_args("With Desc", description="A description"))
        tasks = read_tasks(crumbs_env / "tasks.jsonl")
        assert tasks[0].get("description") == "A description"

    def test_create_omits_description_when_none(
        self, crumbs_env: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """_cmd_trail_create omits description key when not provided."""
        _cmd_trail_create(_trail_args("No Desc"))
        tasks = read_tasks(crumbs_env / "tasks.jsonl")
        assert "description" not in tasks[0]

    def test_create_uses_default_priority(
        self, crumbs_env: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """_cmd_trail_create falls back to config default_priority when none given."""
        _cmd_trail_create(_trail_args("Default Prio"))
        tasks = read_tasks(crumbs_env / "tasks.jsonl")
        assert tasks[0]["priority"] == "P2"

    def test_create_respects_explicit_priority(
        self, crumbs_env: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """_cmd_trail_create uses explicit priority when provided."""
        _cmd_trail_create(_trail_args("High Prio", priority="P0"))
        tasks = read_tasks(crumbs_env / "tasks.jsonl")
        assert tasks[0]["priority"] == "P0"

    def test_create_prints_created_id(
        self, crumbs_env: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """_cmd_trail_create prints 'created AF-T1' to stdout."""
        _cmd_trail_create(_trail_args("Echo Trail"))
        captured = capsys.readouterr()
        assert "created AF-T1" in captured.out

    # ------------------------------------------------------------------
    # _cmd_trail_show
    # ------------------------------------------------------------------

    def test_show_displays_trail_title(
        self, crumbs_env: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """_cmd_trail_show prints the trail title."""
        _write_records(
            crumbs_env,
            [{"id": "AF-T1", "type": "trail", "title": "Big Trail", "status": "open", "priority": "P1"}],
        )
        _cmd_trail_show(_make_args(id="AF-T1"))
        captured = capsys.readouterr()
        assert "Big Trail" in captured.out

    def test_show_displays_trail_status(
        self, crumbs_env: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """_cmd_trail_show prints the trail status."""
        _write_records(
            crumbs_env,
            [{"id": "AF-T1", "type": "trail", "title": "T", "status": "open", "priority": "P2"}],
        )
        _cmd_trail_show(_make_args(id="AF-T1"))
        captured = capsys.readouterr()
        assert "open" in captured.out

    def test_show_lists_child_crumbs(
        self, crumbs_env: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """_cmd_trail_show lists child crumbs under the Children section."""
        _write_records(
            crumbs_env,
            [
                {"id": "AF-T1", "type": "trail", "title": "Trail", "status": "open", "priority": "P2"},
                {"id": "AF-1", "type": "task", "title": "Child One", "status": "open", "priority": "P2",
                 "links": {"parent": "AF-T1"}},
            ],
        )
        _cmd_trail_show(_make_args(id="AF-T1"))
        captured = capsys.readouterr()
        assert "Child One" in captured.out
        assert "Children" in captured.out

    def test_show_children_section_shows_closed_count(
        self, crumbs_env: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """_cmd_trail_show shows X/Y closed count in Children header."""
        _write_records(
            crumbs_env,
            [
                {"id": "AF-T1", "type": "trail", "title": "Trail", "status": "open", "priority": "P2"},
                {"id": "AF-1", "type": "task", "title": "Done", "status": "closed", "priority": "P2",
                 "links": {"parent": "AF-T1"}},
                {"id": "AF-2", "type": "task", "title": "Open", "status": "open", "priority": "P2",
                 "links": {"parent": "AF-T1"}},
            ],
        )
        _cmd_trail_show(_make_args(id="AF-T1"))
        captured = capsys.readouterr()
        assert "1/2 closed" in captured.out

    def test_show_no_children_prints_none(
        self, crumbs_env: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """_cmd_trail_show prints '(none)' when the trail has no children."""
        _write_records(
            crumbs_env,
            [{"id": "AF-T1", "type": "trail", "title": "Empty Trail", "status": "open", "priority": "P2"}],
        )
        _cmd_trail_show(_make_args(id="AF-T1"))
        captured = capsys.readouterr()
        assert "(none)" in captured.out

    def test_show_unknown_trail_id_exits(
        self, crumbs_env: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """_cmd_trail_show calls die() when the ID is not found."""
        _write_records(crumbs_env, [])
        with pytest.raises(SystemExit):
            _cmd_trail_show(_make_args(id="AF-T99"))

    def test_show_non_trail_id_exits(
        self, crumbs_env: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """_cmd_trail_show calls die() when the ID belongs to a non-trail record."""
        _write_records(
            crumbs_env,
            [{"id": "AF-1", "type": "task", "title": "A task", "status": "open", "priority": "P2"}],
        )
        with pytest.raises(SystemExit):
            _cmd_trail_show(_make_args(id="AF-1"))

    # ------------------------------------------------------------------
    # _cmd_trail_list
    # ------------------------------------------------------------------

    def test_list_displays_all_trails(
        self, crumbs_env: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """_cmd_trail_list prints one line per trail."""
        _write_records(
            crumbs_env,
            [
                {"id": "AF-T1", "type": "trail", "title": "Alpha Trail", "status": "open", "priority": "P2"},
                {"id": "AF-T2", "type": "trail", "title": "Beta Trail", "status": "closed", "priority": "P1"},
            ],
        )
        _cmd_trail_list(_make_args())
        captured = capsys.readouterr()
        assert "Alpha Trail" in captured.out
        assert "Beta Trail" in captured.out

    def test_list_includes_open_closed_counts(
        self, crumbs_env: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """_cmd_trail_list shows child completion counts (X/Y closed)."""
        _write_records(
            crumbs_env,
            [
                {"id": "AF-T1", "type": "trail", "title": "Trail", "status": "open", "priority": "P2"},
                {"id": "AF-1", "type": "task", "title": "Done", "status": "closed", "priority": "P2",
                 "links": {"parent": "AF-T1"}},
                {"id": "AF-2", "type": "task", "title": "Open", "status": "open", "priority": "P2",
                 "links": {"parent": "AF-T1"}},
            ],
        )
        _cmd_trail_list(_make_args())
        captured = capsys.readouterr()
        assert "1/2 closed" in captured.out

    def test_list_zero_children_shows_zero_count(
        self, crumbs_env: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """_cmd_trail_list shows 0/0 closed when a trail has no children."""
        _write_records(
            crumbs_env,
            [{"id": "AF-T1", "type": "trail", "title": "Empty", "status": "open", "priority": "P2"}],
        )
        _cmd_trail_list(_make_args())
        captured = capsys.readouterr()
        assert "0/0 closed" in captured.out

    def test_list_no_trails_prints_message(
        self, crumbs_env: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """_cmd_trail_list prints 'no trails found' when there are no trail records."""
        _write_records(crumbs_env, [])
        _cmd_trail_list(_make_args())
        captured = capsys.readouterr()
        assert "no trails found" in captured.out

    def test_list_excludes_non_trail_records_from_output(
        self, crumbs_env: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """_cmd_trail_list does not print non-trail records as trail rows."""
        _write_records(
            crumbs_env,
            [
                {"id": "AF-T1", "type": "trail", "title": "A Trail", "status": "open", "priority": "P2"},
                {"id": "AF-1", "type": "task", "title": "A Task", "status": "open", "priority": "P2"},
            ],
        )
        _cmd_trail_list(_make_args())
        captured = capsys.readouterr()
        # The task line should not appear as a trail-level row, but it is a
        # child counted in the completion number, not printed as a top-level
        # row. The count line for AF-T1 will contain "A Trail".
        assert "A Trail" in captured.out
        # "A Task" is a child and is NOT printed as a top-level trail row
        lines = [ln for ln in captured.out.splitlines() if "AF-1" in ln and "A Task" in ln]
        assert lines == []

    # ------------------------------------------------------------------
    # _cmd_trail_close
    # ------------------------------------------------------------------

    def test_close_sets_status_to_closed(
        self, crumbs_env: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """_cmd_trail_close sets trail status to 'closed'."""
        _write_records(
            crumbs_env,
            [{"id": "AF-T1", "type": "trail", "title": "Done Trail", "status": "open", "priority": "P2"}],
        )
        _cmd_trail_close(_make_args(id="AF-T1"))
        tasks = read_tasks(crumbs_env / "tasks.jsonl")
        trail = next(t for t in tasks if t["id"] == "AF-T1")
        assert trail["status"] == "closed"

    def test_close_sets_closed_at_timestamp(
        self, crumbs_env: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """_cmd_trail_close sets closed_at on the trail record."""
        _write_records(
            crumbs_env,
            [{"id": "AF-T1", "type": "trail", "title": "T", "status": "open", "priority": "P2"}],
        )
        _cmd_trail_close(_make_args(id="AF-T1"))
        tasks = read_tasks(crumbs_env / "tasks.jsonl")
        trail = next(t for t in tasks if t["id"] == "AF-T1")
        assert "closed_at" in trail
        assert trail["closed_at"]

    def test_close_rejects_trail_with_open_children(
        self, crumbs_env: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """_cmd_trail_close calls die() when the trail has open children."""
        _write_records(
            crumbs_env,
            [
                {"id": "AF-T1", "type": "trail", "title": "Blocked Trail", "status": "open", "priority": "P2"},
                {"id": "AF-1", "type": "task", "title": "Open Child", "status": "open", "priority": "P2",
                 "links": {"parent": "AF-T1"}},
            ],
        )
        with pytest.raises(SystemExit):
            _cmd_trail_close(_make_args(id="AF-T1"))

    def test_close_allows_trail_with_all_children_closed(
        self, crumbs_env: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """_cmd_trail_close succeeds when all children are closed."""
        _write_records(
            crumbs_env,
            [
                {"id": "AF-T1", "type": "trail", "title": "Completable", "status": "open", "priority": "P2"},
                {"id": "AF-1", "type": "task", "title": "Done", "status": "closed", "priority": "P2",
                 "links": {"parent": "AF-T1"}},
            ],
        )
        _cmd_trail_close(_make_args(id="AF-T1"))
        tasks = read_tasks(crumbs_env / "tasks.jsonl")
        trail = next(t for t in tasks if t["id"] == "AF-T1")
        assert trail["status"] == "closed"

    def test_close_already_closed_is_idempotent(
        self, crumbs_env: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """_cmd_trail_close prints 'already closed' and does not error."""
        _write_records(
            crumbs_env,
            [{"id": "AF-T1", "type": "trail", "title": "Already Done", "status": "closed", "priority": "P2"}],
        )
        _cmd_trail_close(_make_args(id="AF-T1"))
        captured = capsys.readouterr()
        assert "already closed" in captured.out

    def test_close_prints_closed_id(
        self, crumbs_env: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """_cmd_trail_close prints 'closed AF-T1' on success."""
        _write_records(
            crumbs_env,
            [{"id": "AF-T1", "type": "trail", "title": "T", "status": "open", "priority": "P2"}],
        )
        _cmd_trail_close(_make_args(id="AF-T1"))
        captured = capsys.readouterr()
        assert "closed AF-T1" in captured.out

    def test_close_unknown_trail_id_exits(
        self, crumbs_env: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """_cmd_trail_close calls die() when the trail ID does not exist."""
        _write_records(crumbs_env, [])
        with pytest.raises(SystemExit):
            _cmd_trail_close(_make_args(id="AF-T99"))

    # ------------------------------------------------------------------
    # _auto_close_trail_if_complete
    # ------------------------------------------------------------------

    def test_auto_close_closes_trail_when_last_child_closed(
        self, crumbs_env: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """_auto_close_trail_if_complete closes the trail when all children closed."""
        tasks: List[Dict[str, Any]] = [
            {"id": "AF-T1", "type": "trail", "title": "T", "status": "open", "priority": "P2"},
            {"id": "AF-1", "type": "task", "title": "Done", "status": "closed", "priority": "P2",
             "links": {"parent": "AF-T1"}},
        ]
        path = crumbs_env / "tasks.jsonl"
        write_tasks(path, tasks)
        _auto_close_trail_if_complete(tasks, path, "AF-1")
        updated = read_tasks(path)
        trail = next(t for t in updated if t["id"] == "AF-T1")
        assert trail["status"] == "closed"

    def test_auto_close_prints_message(
        self, crumbs_env: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """_auto_close_trail_if_complete prints auto-closed message."""
        tasks: List[Dict[str, Any]] = [
            {"id": "AF-T1", "type": "trail", "title": "T", "status": "open", "priority": "P2"},
            {"id": "AF-1", "type": "task", "title": "Done", "status": "closed", "priority": "P2",
             "links": {"parent": "AF-T1"}},
        ]
        path = crumbs_env / "tasks.jsonl"
        write_tasks(path, tasks)
        _auto_close_trail_if_complete(tasks, path, "AF-1")
        captured = capsys.readouterr()
        assert "auto-closed trail AF-T1" in captured.out

    def test_auto_close_does_not_close_when_open_children_remain(
        self, crumbs_env: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """_auto_close_trail_if_complete leaves trail open when siblings remain open."""
        tasks: List[Dict[str, Any]] = [
            {"id": "AF-T1", "type": "trail", "title": "T", "status": "open", "priority": "P2"},
            {"id": "AF-1", "type": "task", "title": "Done", "status": "closed", "priority": "P2",
             "links": {"parent": "AF-T1"}},
            {"id": "AF-2", "type": "task", "title": "Pending", "status": "open", "priority": "P2",
             "links": {"parent": "AF-T1"}},
        ]
        path = crumbs_env / "tasks.jsonl"
        write_tasks(path, tasks)
        _auto_close_trail_if_complete(tasks, path, "AF-1")
        updated = read_tasks(path)
        trail = next(t for t in updated if t["id"] == "AF-T1")
        assert trail["status"] == "open"

    def test_auto_close_skips_already_closed_trail(
        self, crumbs_env: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """_auto_close_trail_if_complete is a no-op when the trail is already closed."""
        tasks: List[Dict[str, Any]] = [
            {"id": "AF-T1", "type": "trail", "title": "T", "status": "closed", "priority": "P2",
             "closed_at": "2026-01-01T00:00:00Z"},
            {"id": "AF-1", "type": "task", "title": "Done", "status": "closed", "priority": "P2",
             "links": {"parent": "AF-T1"}},
        ]
        path = crumbs_env / "tasks.jsonl"
        write_tasks(path, tasks)
        _auto_close_trail_if_complete(tasks, path, "AF-1")
        captured = capsys.readouterr()
        assert "auto-closed" not in captured.out

    def test_auto_close_no_op_when_crumb_has_no_parent(
        self, crumbs_env: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """_auto_close_trail_if_complete does nothing when closed crumb has no parent."""
        tasks: List[Dict[str, Any]] = [
            {"id": "AF-1", "type": "task", "title": "Orphan", "status": "closed", "priority": "P2"},
        ]
        path = crumbs_env / "tasks.jsonl"
        write_tasks(path, tasks)
        _auto_close_trail_if_complete(tasks, path, "AF-1")
        captured = capsys.readouterr()
        assert "auto-closed" not in captured.out

    # ------------------------------------------------------------------
    # _auto_reopen_trail_if_needed
    # ------------------------------------------------------------------

    def test_auto_reopen_reopens_trail_when_open_child_linked(
        self, crumbs_env: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """_auto_reopen_trail_if_needed reopens a closed trail for an open child."""
        tasks: List[Dict[str, Any]] = [
            {"id": "AF-T1", "type": "trail", "title": "T", "status": "closed", "priority": "P2",
             "closed_at": "2026-01-01T00:00:00Z"},
        ]
        path = crumbs_env / "tasks.jsonl"
        write_tasks(path, tasks)
        _auto_reopen_trail_if_needed(tasks, path, "AF-T1", "open")
        updated = read_tasks(path)
        trail = next(t for t in updated if t["id"] == "AF-T1")
        assert trail["status"] == "open"

    def test_auto_reopen_removes_closed_at(
        self, crumbs_env: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """_auto_reopen_trail_if_needed removes closed_at when reopening the trail."""
        tasks: List[Dict[str, Any]] = [
            {"id": "AF-T1", "type": "trail", "title": "T", "status": "closed", "priority": "P2",
             "closed_at": "2026-01-01T00:00:00Z"},
        ]
        path = crumbs_env / "tasks.jsonl"
        write_tasks(path, tasks)
        _auto_reopen_trail_if_needed(tasks, path, "AF-T1", "open")
        updated = read_tasks(path)
        trail = next(t for t in updated if t["id"] == "AF-T1")
        assert "closed_at" not in trail

    def test_auto_reopen_prints_message(
        self, crumbs_env: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """_auto_reopen_trail_if_needed prints auto-reopened message."""
        tasks: List[Dict[str, Any]] = [
            {"id": "AF-T1", "type": "trail", "title": "T", "status": "closed", "priority": "P2",
             "closed_at": "2026-01-01T00:00:00Z"},
        ]
        path = crumbs_env / "tasks.jsonl"
        write_tasks(path, tasks)
        _auto_reopen_trail_if_needed(tasks, path, "AF-T1", "open")
        captured = capsys.readouterr()
        assert "auto-reopened trail AF-T1" in captured.out

    def test_auto_reopen_no_op_when_child_is_closed(
        self, crumbs_env: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """_auto_reopen_trail_if_needed does nothing when the linked child is closed."""
        tasks: List[Dict[str, Any]] = [
            {"id": "AF-T1", "type": "trail", "title": "T", "status": "closed", "priority": "P2",
             "closed_at": "2026-01-01T00:00:00Z"},
        ]
        path = crumbs_env / "tasks.jsonl"
        write_tasks(path, tasks)
        _auto_reopen_trail_if_needed(tasks, path, "AF-T1", "closed")
        updated = read_tasks(path)
        trail = next(t for t in updated if t["id"] == "AF-T1")
        assert trail["status"] == "closed"

    def test_auto_reopen_no_op_when_trail_already_open(
        self, crumbs_env: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """_auto_reopen_trail_if_needed does nothing when the trail is already open."""
        tasks: List[Dict[str, Any]] = [
            {"id": "AF-T1", "type": "trail", "title": "T", "status": "open", "priority": "P2"},
        ]
        path = crumbs_env / "tasks.jsonl"
        write_tasks(path, tasks)
        _auto_reopen_trail_if_needed(tasks, path, "AF-T1", "open")
        captured = capsys.readouterr()
        assert "auto-reopened" not in captured.out

    def test_auto_reopen_no_op_for_unknown_trail_id(
        self, crumbs_env: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """_auto_reopen_trail_if_needed does nothing when trail ID not found."""
        tasks: List[Dict[str, Any]] = []
        path = crumbs_env / "tasks.jsonl"
        write_tasks(path, tasks)
        # Should not raise
        _auto_reopen_trail_if_needed(tasks, path, "AF-T99", "open")
        captured = capsys.readouterr()
        assert "auto-reopened" not in captured.out


# ---------------------------------------------------------------------------
# TestTree
# ---------------------------------------------------------------------------


class TestTree:
    """Tests for the cmd_tree command."""

    def test_tree_no_args_shows_full_hierarchy(
        self, crumbs_env: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """cmd_tree with no id shows all trails and their children."""
        _write_records(
            crumbs_env,
            [
                {"id": "AF-T1", "type": "trail", "title": "Trail One", "status": "open", "priority": "P2"},
                {"id": "AF-1", "type": "task", "title": "Child Task", "status": "open", "priority": "P2",
                 "links": {"parent": "AF-T1"}},
                {"id": "AF-T2", "type": "trail", "title": "Trail Two", "status": "open", "priority": "P1"},
            ],
        )
        cmd_tree(_make_args(id=None))
        captured = capsys.readouterr()
        assert "Trail One" in captured.out
        assert "Trail Two" in captured.out
        assert "Child Task" in captured.out

    def test_tree_with_trail_id_shows_subtree(
        self, crumbs_env: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """cmd_tree with a trail ID shows only that trail and its children."""
        _write_records(
            crumbs_env,
            [
                {"id": "AF-T1", "type": "trail", "title": "Trail One", "status": "open", "priority": "P2"},
                {"id": "AF-T2", "type": "trail", "title": "Trail Two", "status": "open", "priority": "P1"},
                {"id": "AF-1", "type": "task", "title": "Child of T1", "status": "open", "priority": "P2",
                 "links": {"parent": "AF-T1"}},
                {"id": "AF-2", "type": "task", "title": "Child of T2", "status": "open", "priority": "P2",
                 "links": {"parent": "AF-T2"}},
            ],
        )
        cmd_tree(_make_args(id="AF-T1"))
        captured = capsys.readouterr()
        assert "Trail One" in captured.out
        assert "Child of T1" in captured.out
        assert "Trail Two" not in captured.out
        assert "Child of T2" not in captured.out

    def test_tree_children_are_indented(
        self, crumbs_env: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """cmd_tree indents child crumbs with leading spaces."""
        _write_records(
            crumbs_env,
            [
                {"id": "AF-T1", "type": "trail", "title": "Trail", "status": "open", "priority": "P2"},
                {"id": "AF-1", "type": "task", "title": "Child", "status": "open", "priority": "P2",
                 "links": {"parent": "AF-T1"}},
            ],
        )
        cmd_tree(_make_args(id=None))
        captured = capsys.readouterr()
        child_line = next(
            (ln for ln in captured.out.splitlines() if "Child" in ln), None
        )
        assert child_line is not None
        assert child_line.startswith("  "), (
            f"child line should start with at least 2 spaces; got: {child_line!r}"
        )

    def test_tree_subtree_children_are_indented(
        self, crumbs_env: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """cmd_tree with trail ID indents its children with leading spaces."""
        _write_records(
            crumbs_env,
            [
                {"id": "AF-T1", "type": "trail", "title": "Trail", "status": "open", "priority": "P2"},
                {"id": "AF-1", "type": "task", "title": "SubChild", "status": "open", "priority": "P2",
                 "links": {"parent": "AF-T1"}},
            ],
        )
        cmd_tree(_make_args(id="AF-T1"))
        captured = capsys.readouterr()
        child_line = next(
            (ln for ln in captured.out.splitlines() if "SubChild" in ln), None
        )
        assert child_line is not None
        assert child_line.startswith("  "), (
            f"child line should start with at least 2 spaces; got: {child_line!r}"
        )

    def test_tree_orphan_crumbs_listed_at_end(
        self, crumbs_env: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """cmd_tree shows orphan crumbs (no parent trail) under an orphans section."""
        _write_records(
            crumbs_env,
            [
                {"id": "AF-T1", "type": "trail", "title": "Trail", "status": "open", "priority": "P2"},
                {"id": "AF-1", "type": "task", "title": "Orphan Task", "status": "open", "priority": "P2"},
            ],
        )
        cmd_tree(_make_args(id=None))
        captured = capsys.readouterr()
        assert "Orphan Task" in captured.out
        assert "orphan" in captured.out.lower()

    def test_tree_unknown_trail_id_exits(
        self, crumbs_env: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """cmd_tree calls die() when the given trail ID does not exist."""
        _write_records(crumbs_env, [])
        with pytest.raises(SystemExit):
            cmd_tree(_make_args(id="AF-T99"))

    def test_tree_non_trail_id_exits(
        self, crumbs_env: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """cmd_tree calls die() when the given ID belongs to a non-trail record."""
        _write_records(
            crumbs_env,
            [{"id": "AF-1", "type": "task", "title": "Not a Trail", "status": "open", "priority": "P2"}],
        )
        with pytest.raises(SystemExit):
            cmd_tree(_make_args(id="AF-1"))

    def test_tree_full_hierarchy_trail_line_not_indented(
        self, crumbs_env: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """cmd_tree full hierarchy: trail lines are not indented (start at column 0)."""
        _write_records(
            crumbs_env,
            [{"id": "AF-T1", "type": "trail", "title": "Root Trail", "status": "open", "priority": "P2"}],
        )
        cmd_tree(_make_args(id=None))
        captured = capsys.readouterr()
        trail_line = next(
            (ln for ln in captured.out.splitlines() if "Root Trail" in ln), None
        )
        assert trail_line is not None
        assert not trail_line.startswith(" "), (
            f"trail line should not be indented; got: {trail_line!r}"
        )

    def test_tree_no_records_produces_no_output(
        self, crumbs_env: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """cmd_tree with empty tasks.jsonl produces no output (no crash)."""
        _write_records(crumbs_env, [])
        cmd_tree(_make_args(id=None))
        captured = capsys.readouterr()
        # No output expected; no exception raised
        assert captured.out == "" or captured.out.strip() == ""


# ---------------------------------------------------------------------------
# TestCountCrumbFiles
# ---------------------------------------------------------------------------


class TestCountCrumbFiles:
    """Tests for the _count_crumb_files helper."""

    def test_returns_zero_for_empty_scope(self) -> None:
        """_count_crumb_files returns 0 when scope is missing."""
        assert _count_crumb_files({}) == 0

    def test_returns_zero_for_none_scope(self) -> None:
        """_count_crumb_files returns 0 when scope is None."""
        assert _count_crumb_files({"scope": None}) == 0

    def test_returns_zero_for_scope_without_files(self) -> None:
        """_count_crumb_files returns 0 when scope.files key is absent."""
        assert _count_crumb_files({"scope": {"agent_type": "python-pro"}}) == 0

    def test_returns_zero_for_empty_files_list(self) -> None:
        """_count_crumb_files returns 0 for an empty files array."""
        assert _count_crumb_files({"scope": {"files": []}}) == 0

    def test_returns_correct_count(self) -> None:
        """_count_crumb_files returns the length of the files array."""
        crumb_rec = {"scope": {"files": ["a.py", "b.py", "c.py"]}}
        assert _count_crumb_files(crumb_rec) == 3

    def test_returns_zero_for_non_list_files(self) -> None:
        """_count_crumb_files returns 0 when files is not a list."""
        assert _count_crumb_files({"scope": {"files": "not-a-list"}}) == 0

    def test_returns_zero_for_non_dict_scope(self) -> None:
        """_count_crumb_files returns 0 when scope is not a dict."""
        assert _count_crumb_files({"scope": "bad-value"}) == 0


# ---------------------------------------------------------------------------
# TestValidateSingleTrail
# ---------------------------------------------------------------------------


class TestValidateSingleTrail:
    """Unit tests for the _validate_single_trail pure helper."""

    def _make_trail(self, trail_id: str = "AF-T1") -> Dict[str, Any]:
        return {"id": trail_id, "type": "trail", "title": "T", "status": "open", "priority": "P2"}

    def _make_task(
        self,
        task_id: str,
        trail_id: str,
        status: str = "open",
        files: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        rec: Dict[str, Any] = {
            "id": task_id,
            "type": "task",
            "title": task_id,
            "status": status,
            "priority": "P2",
            "links": {"parent": trail_id},
        }
        if files is not None:
            rec["scope"] = {"files": files}
        return rec

    def test_pass_when_crumb_count_in_range(self) -> None:
        """Returns PASS when open crumb count is within [min, max]."""
        tasks = [self._make_trail()]
        tasks += [self._make_task(f"AF-{i}", "AF-T1") for i in range(1, 5)]
        result = _validate_single_trail(tasks, "AF-T1", 3, 8, 8)
        assert result["status"] == "PASS"
        assert result["violations"] == []
        assert result["crumb_count"] == 4

    def test_fail_when_crumb_count_below_minimum(self) -> None:
        """Returns FAIL when open crumb count is below min_crumbs."""
        tasks = [self._make_trail()]
        tasks += [self._make_task(f"AF-{i}", "AF-T1") for i in range(1, 3)]
        result = _validate_single_trail(tasks, "AF-T1", 3, 8, 8)
        assert result["status"] == "FAIL"
        assert any(v["type"] == "FAIL" for v in result["violations"])

    def test_fail_when_crumb_count_exactly_minimum_minus_one(self) -> None:
        """Returns FAIL for exactly min-1 crumbs (boundary: 2 < 3)."""
        tasks = [self._make_trail()]
        tasks += [self._make_task(f"AF-{i}", "AF-T1") for i in range(1, 3)]
        result = _validate_single_trail(tasks, "AF-T1", 3, 8, 8)
        assert result["status"] == "FAIL"

    def test_pass_when_crumb_count_exactly_minimum(self) -> None:
        """Returns PASS for exactly min_crumbs crumbs (boundary: 3 == 3)."""
        tasks = [self._make_trail()]
        tasks += [self._make_task(f"AF-{i}", "AF-T1") for i in range(1, 4)]
        result = _validate_single_trail(tasks, "AF-T1", 3, 8, 8)
        assert result["status"] == "PASS"

    def test_pass_when_crumb_count_exactly_maximum(self) -> None:
        """Returns PASS for exactly max_crumbs crumbs (boundary: 8 == 8)."""
        tasks = [self._make_trail()]
        tasks += [self._make_task(f"AF-{i}", "AF-T1") for i in range(1, 9)]
        result = _validate_single_trail(tasks, "AF-T1", 3, 8, 8)
        assert result["status"] == "PASS"

    def test_fail_when_crumb_count_exceeds_maximum(self) -> None:
        """Returns FAIL when open crumb count exceeds max_crumbs."""
        tasks = [self._make_trail()]
        tasks += [self._make_task(f"AF-{i}", "AF-T1") for i in range(1, 10)]
        result = _validate_single_trail(tasks, "AF-T1", 3, 8, 8)
        assert result["status"] == "FAIL"
        assert any(v["type"] == "FAIL" for v in result["violations"])

    def test_closed_crumbs_not_counted(self) -> None:
        """Closed crumbs are excluded from the active count."""
        tasks = [self._make_trail()]
        # 3 open + 5 closed = 3 active; should PASS
        tasks += [self._make_task(f"AF-{i}", "AF-T1") for i in range(1, 4)]
        tasks += [self._make_task(f"AF-{i}", "AF-T1", status="closed") for i in range(4, 9)]
        result = _validate_single_trail(tasks, "AF-T1", 3, 8, 8)
        assert result["status"] == "PASS"
        assert result["crumb_count"] == 3

    def test_in_progress_crumbs_counted(self) -> None:
        """in_progress crumbs count toward the active total."""
        tasks = [self._make_trail()]
        tasks.append(self._make_task("AF-1", "AF-T1", status="in_progress"))
        tasks.append(self._make_task("AF-2", "AF-T1", status="in_progress"))
        tasks.append(self._make_task("AF-3", "AF-T1", status="open"))
        result = _validate_single_trail(tasks, "AF-T1", 3, 8, 8)
        assert result["crumb_count"] == 3
        assert result["status"] == "PASS"

    def test_warn_when_crumb_exceeds_file_limit(self) -> None:
        """Returns WARN when any crumb has more files than max_files_per_crumb."""
        tasks = [self._make_trail()]
        tasks += [self._make_task(f"AF-{i}", "AF-T1") for i in range(1, 4)]
        tasks.append(
            self._make_task("AF-99", "AF-T1", files=[f"f{j}.py" for j in range(9)])
        )
        result = _validate_single_trail(tasks, "AF-T1", 3, 8, 8)
        assert result["status"] == "WARN"
        warn_violations = [v for v in result["violations"] if v["type"] == "WARN"]
        assert len(warn_violations) == 1
        assert warn_violations[0]["crumb_id"] == "AF-99"

    def test_warn_does_not_downgrade_fail(self) -> None:
        """FAIL status is not downgraded to WARN when both conditions apply."""
        tasks = [self._make_trail()]
        # 1 crumb < min 3 → FAIL; plus too many files → WARN
        tasks.append(self._make_task("AF-1", "AF-T1", files=[f"f{j}.py" for j in range(9)]))
        result = _validate_single_trail(tasks, "AF-T1", 3, 8, 8)
        assert result["status"] == "FAIL"
        types = {v["type"] for v in result["violations"]}
        assert "FAIL" in types
        assert "WARN" in types

    def test_violation_message_contains_count_and_threshold(self) -> None:
        """FAIL violation message includes the actual count and the threshold."""
        tasks = [self._make_trail()]
        tasks += [self._make_task(f"AF-{i}", "AF-T1") for i in range(1, 3)]
        result = _validate_single_trail(tasks, "AF-T1", 3, 8, 8)
        fail_msg = next(v["message"] for v in result["violations"] if v["type"] == "FAIL")
        assert "2" in fail_msg
        assert "3" in fail_msg

    def test_result_includes_trail_id_and_crumb_count(self) -> None:
        """Result dict always includes trail_id and crumb_count keys."""
        tasks = [self._make_trail("AF-T5")]
        tasks += [self._make_task(f"AF-{i}", "AF-T5") for i in range(1, 4)]
        result = _validate_single_trail(tasks, "AF-T5", 3, 8, 8)
        assert result["trail_id"] == "AF-T5"
        assert result["crumb_count"] == 3

    def test_no_children_fails_below_minimum(self) -> None:
        """A trail with zero active children fails the minimum check."""
        tasks = [self._make_trail()]
        result = _validate_single_trail(tasks, "AF-T1", 3, 8, 8)
        assert result["status"] == "FAIL"
        assert result["crumb_count"] == 0

    def test_exactly_max_files_is_pass(self) -> None:
        """A crumb with exactly max_files files does not trigger WARN."""
        tasks = [self._make_trail()]
        tasks += [self._make_task(f"AF-{i}", "AF-T1") for i in range(1, 4)]
        tasks.append(
            self._make_task("AF-99", "AF-T1", files=[f"f{j}.py" for j in range(8)])
        )
        result = _validate_single_trail(tasks, "AF-T1", 3, 8, 8)
        assert result["status"] == "PASS"


# ---------------------------------------------------------------------------
# TestCmdValidateTrail
# ---------------------------------------------------------------------------

class TestCmdValidateTrail:
    """Integration tests for cmd_validate_trail via argparse.Namespace."""

    _TRAIL = {"id": "AF-T1", "type": "trail", "title": "T", "status": "open", "priority": "P2"}

    def _task(
        self,
        task_id: str,
        trail_id: str = "AF-T1",
        status: str = "open",
        files: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        rec: Dict[str, Any] = {
            "id": task_id,
            "type": "task",
            "title": task_id,
            "status": status,
            "priority": "P2",
            "links": {"parent": trail_id},
        }
        if files is not None:
            rec["scope"] = {"files": files}
        return rec

    def _args(self, **kwargs: Any) -> argparse.Namespace:
        defaults = {"id": None, "all_trails": False, "json_output": False, "strict": False}
        defaults.update(kwargs)
        return _make_args(**defaults)

    # ------------------------------------------------------------------
    # Single trail — text output
    # ------------------------------------------------------------------

    def test_single_trail_pass_output(
        self, crumbs_env: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """cmd_validate_trail reports PASS for a trail within thresholds."""
        _write_records(
            crumbs_env,
            [self._TRAIL] + [self._task(f"AF-{i}") for i in range(1, 5)],
        )
        cmd_validate_trail(self._args(id="AF-T1"))
        captured = capsys.readouterr()
        assert "PASS" in captured.out
        assert "no violations" in captured.out

    def test_single_trail_fail_below_minimum(
        self, crumbs_env: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """cmd_validate_trail reports FAIL when crumb count is below minimum."""
        _write_records(
            crumbs_env,
            [self._TRAIL] + [self._task(f"AF-{i}") for i in range(1, 3)],
        )
        cmd_validate_trail(self._args(id="AF-T1"))
        captured = capsys.readouterr()
        assert "FAIL" in captured.out

    def test_single_trail_fail_above_maximum(
        self, crumbs_env: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """cmd_validate_trail reports FAIL when crumb count exceeds maximum."""
        _write_records(
            crumbs_env,
            [self._TRAIL] + [self._task(f"AF-{i}") for i in range(1, 10)],
        )
        cmd_validate_trail(self._args(id="AF-T1"))
        captured = capsys.readouterr()
        assert "FAIL" in captured.out

    def test_single_trail_warn_on_excess_files(
        self, crumbs_env: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """cmd_validate_trail reports WARN when a crumb has too many files."""
        _write_records(
            crumbs_env,
            [self._TRAIL]
            + [self._task(f"AF-{i}") for i in range(1, 4)]
            + [self._task("AF-99", files=[f"f{j}.py" for j in range(9)])],
        )
        cmd_validate_trail(self._args(id="AF-T1"))
        captured = capsys.readouterr()
        assert "WARN" in captured.out

    def test_single_trail_shows_trail_id_in_output(
        self, crumbs_env: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """cmd_validate_trail always prints the trail ID in human output."""
        _write_records(
            crumbs_env,
            [self._TRAIL] + [self._task(f"AF-{i}") for i in range(1, 5)],
        )
        cmd_validate_trail(self._args(id="AF-T1"))
        captured = capsys.readouterr()
        assert "AF-T1" in captured.out

    def test_unknown_trail_id_exits(
        self, crumbs_env: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """cmd_validate_trail calls die() for an unknown trail ID."""
        _write_records(crumbs_env, [])
        with pytest.raises(SystemExit):
            cmd_validate_trail(self._args(id="AF-T99"))

    def test_non_trail_id_exits(
        self, crumbs_env: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """cmd_validate_trail calls die() when ID belongs to a non-trail record."""
        _write_records(
            crumbs_env,
            [{"id": "AF-1", "type": "task", "title": "Task", "status": "open", "priority": "P2"}],
        )
        with pytest.raises(SystemExit):
            cmd_validate_trail(self._args(id="AF-1"))

    def test_no_id_and_no_all_flag_exits(
        self, crumbs_env: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """cmd_validate_trail calls die() when neither id nor --all is given."""
        _write_records(crumbs_env, [self._TRAIL])
        with pytest.raises(SystemExit):
            cmd_validate_trail(self._args(id=None, all_trails=False))

    # ------------------------------------------------------------------
    # --all flag
    # ------------------------------------------------------------------

    def test_all_flag_validates_every_trail(
        self, crumbs_env: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """cmd_validate_trail --all prints summary rows for every trail."""
        trail2 = {"id": "AF-T2", "type": "trail", "title": "T2", "status": "open", "priority": "P2"}
        _write_records(
            crumbs_env,
            [self._TRAIL, trail2]
            + [self._task(f"AF-{i}") for i in range(1, 5)]
            + [self._task(f"AF-{i}", trail_id="AF-T2") for i in range(10, 14)],
        )
        cmd_validate_trail(self._args(all_trails=True))
        captured = capsys.readouterr()
        assert "AF-T1" in captured.out
        assert "AF-T2" in captured.out

    def test_all_flag_no_trails_prints_message(
        self, crumbs_env: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """cmd_validate_trail --all prints 'no trails found' when none exist."""
        _write_records(crumbs_env, [])
        cmd_validate_trail(self._args(all_trails=True))
        captured = capsys.readouterr()
        assert "no trails found" in captured.out

    def test_all_flag_shows_summary_counts(
        self, crumbs_env: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """cmd_validate_trail --all shows total trail count and PASS/WARN/FAIL breakdown."""
        _write_records(
            crumbs_env,
            [self._TRAIL] + [self._task(f"AF-{i}") for i in range(1, 5)],
        )
        cmd_validate_trail(self._args(all_trails=True))
        captured = capsys.readouterr()
        # Should show "1 trail(s): 1 PASS, 0 WARN, 0 FAIL" or similar
        assert "trail(s)" in captured.out

    # ------------------------------------------------------------------
    # --json flag
    # ------------------------------------------------------------------

    def test_json_output_single_trail_is_object(
        self, crumbs_env: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """--json returns a JSON object (not array) for a single trail."""
        _write_records(
            crumbs_env,
            [self._TRAIL] + [self._task(f"AF-{i}") for i in range(1, 5)],
        )
        cmd_validate_trail(self._args(id="AF-T1", json_output=True))
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert isinstance(data, dict)

    def test_json_output_single_trail_has_required_keys(
        self, crumbs_env: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """--json single trail result has trail_id, crumb_count, status, violations keys."""
        _write_records(
            crumbs_env,
            [self._TRAIL] + [self._task(f"AF-{i}") for i in range(1, 5)],
        )
        cmd_validate_trail(self._args(id="AF-T1", json_output=True))
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert "trail_id" in data
        assert "crumb_count" in data
        assert "status" in data
        assert "violations" in data

    def test_json_output_single_trail_fail_status(
        self, crumbs_env: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """--json reflects FAIL status when crumb count is out of range."""
        _write_records(
            crumbs_env,
            [self._TRAIL] + [self._task(f"AF-{i}") for i in range(1, 3)],
        )
        cmd_validate_trail(self._args(id="AF-T1", json_output=True))
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert data["status"] == "FAIL"
        assert len(data["violations"]) > 0

    def test_json_output_all_is_array(
        self, crumbs_env: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """--json --all returns a JSON array."""
        trail2 = {"id": "AF-T2", "type": "trail", "title": "T2", "status": "open", "priority": "P2"}
        _write_records(
            crumbs_env,
            [self._TRAIL, trail2]
            + [self._task(f"AF-{i}") for i in range(1, 5)]
            + [self._task(f"AF-{i}", trail_id="AF-T2") for i in range(10, 14)],
        )
        cmd_validate_trail(self._args(all_trails=True, json_output=True))
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert isinstance(data, list)
        assert len(data) == 2

    def test_json_output_all_no_trails_is_empty_array(
        self, crumbs_env: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """--json --all returns [] when there are no trails."""
        _write_records(crumbs_env, [])
        cmd_validate_trail(self._args(all_trails=True, json_output=True))
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert data == []

    # ------------------------------------------------------------------
    # --strict flag
    # ------------------------------------------------------------------

    def test_strict_exits_1_on_fail(
        self, crumbs_env: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """--strict causes sys.exit(1) when any trail has FAIL status."""
        _write_records(
            crumbs_env,
            [self._TRAIL] + [self._task(f"AF-{i}") for i in range(1, 3)],
        )
        with pytest.raises(SystemExit) as exc_info:
            cmd_validate_trail(self._args(id="AF-T1", strict=True))
        assert exc_info.value.code == 1

    def test_strict_exits_0_on_pass(
        self, crumbs_env: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """--strict does not exit non-zero when trail is PASS."""
        _write_records(
            crumbs_env,
            [self._TRAIL] + [self._task(f"AF-{i}") for i in range(1, 5)],
        )
        # Should not raise SystemExit
        cmd_validate_trail(self._args(id="AF-T1", strict=True))

    def test_strict_exits_0_on_warn(
        self, crumbs_env: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """--strict exits 0 when trail is WARN (not FAIL)."""
        _write_records(
            crumbs_env,
            [self._TRAIL]
            + [self._task(f"AF-{i}") for i in range(1, 4)]
            + [self._task("AF-99", files=[f"f{j}.py" for j in range(9)])],
        )
        # Should not raise SystemExit
        cmd_validate_trail(self._args(id="AF-T1", strict=True))

    def test_strict_all_exits_1_if_any_fail(
        self, crumbs_env: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """--strict --all exits 1 if at least one trail has FAIL status."""
        trail2 = {"id": "AF-T2", "type": "trail", "title": "T2", "status": "open", "priority": "P2"}
        _write_records(
            crumbs_env,
            # AF-T1 has 4 crumbs (PASS), AF-T2 has 1 crumb (FAIL)
            [self._TRAIL, trail2]
            + [self._task(f"AF-{i}") for i in range(1, 5)]
            + [self._task("AF-50", trail_id="AF-T2")],
        )
        with pytest.raises(SystemExit) as exc_info:
            cmd_validate_trail(self._args(all_trails=True, strict=True))
        assert exc_info.value.code == 1

    # ------------------------------------------------------------------
    # Configurable thresholds
    # ------------------------------------------------------------------

    def test_custom_thresholds_from_config(
        self, crumbs_env: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Thresholds are read from config.json when present."""
        import json as _json

        config_path = crumbs_env / "config.json"
        config = _json.loads(config_path.read_text(encoding="utf-8"))
        config["min_crumbs_per_trail"] = 1
        config["max_crumbs_per_trail"] = 2
        config["max_files_per_crumb"] = 5
        config_path.write_text(_json.dumps(config, indent=2) + "\n", encoding="utf-8")

        # 2 crumbs: within the custom [1, 2] range → PASS
        _write_records(
            crumbs_env,
            [self._TRAIL] + [self._task(f"AF-{i}") for i in range(1, 3)],
        )
        cmd_validate_trail(self._args(id="AF-T1"))
        captured = capsys.readouterr()
        assert "PASS" in captured.out

    def test_custom_threshold_triggers_fail_at_new_max(
        self, crumbs_env: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """A reduced max_crumbs_per_trail causes FAIL at the new lower threshold."""
        import json as _json

        config_path = crumbs_env / "config.json"
        config = _json.loads(config_path.read_text(encoding="utf-8"))
        config["min_crumbs_per_trail"] = 1
        config["max_crumbs_per_trail"] = 2
        config_path.write_text(_json.dumps(config, indent=2) + "\n", encoding="utf-8")

        # 3 crumbs: exceeds custom max of 2 → FAIL
        _write_records(
            crumbs_env,
            [self._TRAIL] + [self._task(f"AF-{i}") for i in range(1, 4)],
        )
        cmd_validate_trail(self._args(id="AF-T1"))
        captured = capsys.readouterr()
        assert "FAIL" in captured.out

    def test_default_thresholds_are_3_8_8(self) -> None:
        """DEFAULT_CONFIG has min_crumbs_per_trail=3, max_crumbs_per_trail=8, max_files_per_crumb=8."""
        assert crumb.DEFAULT_CONFIG["min_crumbs_per_trail"] == 3
        assert crumb.DEFAULT_CONFIG["max_crumbs_per_trail"] == 8
        assert crumb.DEFAULT_CONFIG["max_files_per_crumb"] == 8

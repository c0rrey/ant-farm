"""Tests for trail subcommands and tree command in crumb.py.

Covers:
  _cmd_trail_create, _cmd_trail_show, _cmd_trail_list, _cmd_trail_close,
  _auto_close_trail_if_complete, _auto_reopen_trail_if_needed, cmd_tree.

All tests use the ``crumbs_env`` fixture so no real .crumbs/ directory is
touched.  Commands are called directly (not through subprocess) using
``argparse.Namespace`` objects to construct the ``args`` parameter.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List

import pytest

import crumb
from crumb import (
    _auto_close_trail_if_complete,
    _auto_reopen_trail_if_needed,
    _cmd_trail_close,
    _cmd_trail_create,
    _cmd_trail_list,
    _cmd_trail_show,
    cmd_tree,
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

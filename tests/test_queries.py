"""Tests for query commands: list, ready, blocked, and search.

Covers cmd_list, cmd_ready, cmd_blocked, and cmd_search from crumb.py.
All tests use the crumbs_env fixture for an isolated .crumbs/ directory
and call command functions directly with argparse.Namespace mocks,
capturing stdout with capsys.
"""

from __future__ import annotations

from argparse import Namespace
from pathlib import Path
from typing import Any, Dict, List, Optional

import pytest

import json

from crumb import cmd_blocked, cmd_list, cmd_ready, cmd_search, cmd_show, write_tasks


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _task(
    task_id: str,
    title: str = "Untitled",
    status: str = "open",
    priority: str = "P2",
    task_type: str = "task",
    description: str = "",
    parent: Optional[str] = None,
    blocked_by: Optional[List[str]] = None,
    created_at: str = "2026-01-01T00:00:00Z",
) -> Dict[str, Any]:
    """Build a minimal task dict for test fixtures."""
    record: Dict[str, Any] = {
        "id": task_id,
        "type": task_type,
        "title": title,
        "status": status,
        "priority": priority,
        "created_at": created_at,
    }
    if description:
        record["description"] = description
    links: Dict[str, Any] = {}
    if parent:
        links["parent"] = parent
    if blocked_by:
        links["blocked_by"] = blocked_by
    if links:
        record["links"] = links
    return record


def _write(crumbs_env: Path, tasks: List[Dict[str, Any]]) -> None:
    """Write tasks to the tasks.jsonl file in crumbs_env."""
    tasks_file = crumbs_env / "tasks.jsonl"
    write_tasks(tasks_file, tasks)


def _list_args(**kwargs: Any) -> Namespace:
    """Build a Namespace matching cmd_list's expected attributes."""
    defaults = {
        "filter_open": False,
        "filter_closed": False,
        "filter_in_progress": False,
        "priority": None,
        "filter_type": None,
        "agent_type": None,
        "parent": None,
        "discovered": False,
        "after": None,
        "sort": "created_at",
        "limit": None,
        "short": False,
        "json_output": False,
    }
    defaults.update(kwargs)
    return Namespace(**defaults)


def _ready_args(**kwargs: Any) -> Namespace:
    """Build a Namespace matching cmd_ready's expected attributes."""
    defaults = {
        "sort": "created_at",
        "limit": None,
    }
    defaults.update(kwargs)
    return Namespace(**defaults)


def _search_args(query: str) -> Namespace:
    """Build a Namespace matching cmd_search's expected attributes."""
    return Namespace(query=query)


# ---------------------------------------------------------------------------
# TestList
# ---------------------------------------------------------------------------


class TestList:
    """Tests for cmd_list filter, sort, limit, and output modes."""

    def test_no_filters_shows_all_tasks_including_closed(
        self, crumbs_env: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """cmd_list with no filters returns all tasks, including closed ones.

        cmd_list has no implicit hide-closed behaviour; closed tasks are only
        excluded when an explicit status flag (--open, --in-progress) is passed.
        """
        _write(crumbs_env, [
            _task("AF-1", "Alpha", "open"),
            _task("AF-2", "Beta", "in_progress"),
            _task("AF-3", "Gamma", "closed"),
        ])
        cmd_list(_list_args())
        out = capsys.readouterr().out
        assert "AF-1" in out
        assert "AF-2" in out
        assert "AF-3" in out

    def test_filter_open_excludes_others(
        self, crumbs_env: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """--open shows only open crumbs."""
        _write(crumbs_env, [
            _task("AF-1", "Open task", "open"),
            _task("AF-2", "In progress", "in_progress"),
            _task("AF-3", "Closed", "closed"),
        ])
        cmd_list(_list_args(filter_open=True))
        out = capsys.readouterr().out
        assert "AF-1" in out
        assert "AF-2" not in out
        assert "AF-3" not in out

    def test_filter_closed_shows_only_closed(
        self, crumbs_env: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """--closed shows only closed crumbs."""
        _write(crumbs_env, [
            _task("AF-1", "Open", "open"),
            _task("AF-2", "Closed", "closed"),
        ])
        cmd_list(_list_args(filter_closed=True))
        out = capsys.readouterr().out
        assert "AF-1" not in out
        assert "AF-2" in out

    def test_filter_in_progress_shows_only_in_progress(
        self, crumbs_env: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """--in-progress shows only in_progress crumbs."""
        _write(crumbs_env, [
            _task("AF-1", "Open", "open"),
            _task("AF-2", "In progress", "in_progress"),
            _task("AF-3", "Closed", "closed"),
        ])
        cmd_list(_list_args(filter_in_progress=True))
        out = capsys.readouterr().out
        assert "AF-1" not in out
        assert "AF-2" in out
        assert "AF-3" not in out

    def test_filter_open_and_in_progress_compose(
        self, crumbs_env: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """--open --in-progress shows union of open and in_progress crumbs."""
        _write(crumbs_env, [
            _task("AF-1", "Open", "open"),
            _task("AF-2", "In progress", "in_progress"),
            _task("AF-3", "Closed", "closed"),
        ])
        cmd_list(_list_args(filter_open=True, filter_in_progress=True))
        out = capsys.readouterr().out
        assert "AF-1" in out
        assert "AF-2" in out
        assert "AF-3" not in out

    def test_filter_priority(
        self, crumbs_env: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """--priority filters to only crumbs matching that priority."""
        _write(crumbs_env, [
            _task("AF-1", "P0 task", priority="P0"),
            _task("AF-2", "P1 task", priority="P1"),
            _task("AF-3", "P2 task", priority="P2"),
        ])
        cmd_list(_list_args(priority="P1"))
        out = capsys.readouterr().out
        assert "AF-1" not in out
        assert "AF-2" in out
        assert "AF-3" not in out

    def test_filter_parent(
        self, crumbs_env: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """--parent filters to crumbs with matching links.parent."""
        _write(crumbs_env, [
            _task("AF-1", "Child of T1", parent="AF-T1"),
            _task("AF-2", "Child of T2", parent="AF-T2"),
            _task("AF-3", "No parent"),
        ])
        cmd_list(_list_args(parent="AF-T1"))
        out = capsys.readouterr().out
        assert "AF-1" in out
        assert "AF-2" not in out
        assert "AF-3" not in out

    def test_sort_by_priority(
        self, crumbs_env: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """--sort priority outputs lower priority number first."""
        _write(crumbs_env, [
            _task("AF-1", "P2 task", priority="P2", created_at="2026-01-03T00:00:00Z"),
            _task("AF-2", "P0 task", priority="P0", created_at="2026-01-02T00:00:00Z"),
            _task("AF-3", "P1 task", priority="P1", created_at="2026-01-01T00:00:00Z"),
        ])
        cmd_list(_list_args(sort="priority"))
        out = capsys.readouterr().out
        lines = [ln for ln in out.splitlines() if ln.strip()]
        ids_in_order = [ln.split()[0] for ln in lines]
        assert ids_in_order == ["AF-2", "AF-3", "AF-1"]

    def test_sort_by_status(
        self, crumbs_env: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """--sort status outputs open < in_progress < closed."""
        _write(crumbs_env, [
            _task("AF-1", "Closed", "closed", created_at="2026-01-01T00:00:00Z"),
            _task("AF-2", "In progress", "in_progress", created_at="2026-01-02T00:00:00Z"),
            _task("AF-3", "Open", "open", created_at="2026-01-03T00:00:00Z"),
        ])
        cmd_list(_list_args(sort="status"))
        out = capsys.readouterr().out
        lines = [ln for ln in out.splitlines() if ln.strip()]
        ids_in_order = [ln.split()[0] for ln in lines]
        assert ids_in_order == ["AF-3", "AF-2", "AF-1"]

    def test_sort_default_by_created_at(
        self, crumbs_env: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Default sort (created_at) returns earliest first."""
        _write(crumbs_env, [
            _task("AF-1", "Later", created_at="2026-01-03T00:00:00Z"),
            _task("AF-2", "Earlier", created_at="2026-01-01T00:00:00Z"),
            _task("AF-3", "Middle", created_at="2026-01-02T00:00:00Z"),
        ])
        cmd_list(_list_args())
        out = capsys.readouterr().out
        lines = [ln for ln in out.splitlines() if ln.strip()]
        ids_in_order = [ln.split()[0] for ln in lines]
        assert ids_in_order == ["AF-2", "AF-3", "AF-1"]

    def test_limit_caps_output(
        self, crumbs_env: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """--limit N returns at most N crumbs."""
        _write(crumbs_env, [
            _task(f"AF-{i}", f"Task {i}", created_at=f"2026-01-{i:02d}T00:00:00Z")
            for i in range(1, 6)
        ])
        cmd_list(_list_args(limit=2))
        out = capsys.readouterr().out
        lines = [ln for ln in out.splitlines() if ln.strip()]
        assert len(lines) == 2

    def test_limit_zero_shows_all(
        self, crumbs_env: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """--limit 0 is ignored; all crumbs are shown."""
        _write(crumbs_env, [_task(f"AF-{i}", f"Task {i}") for i in range(1, 4)])
        cmd_list(_list_args(limit=0))
        out = capsys.readouterr().out
        lines = [ln for ln in out.splitlines() if ln.strip()]
        assert len(lines) == 3

    def test_short_mode_output(
        self, crumbs_env: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """--short produces abbreviated one-line output per crumb."""
        _write(crumbs_env, [_task("AF-1", "Short output test", "open", "P1")])
        cmd_list(_list_args(short=True))
        out = capsys.readouterr().out.strip()
        # Short mode: {id:<12} {priority:<4} {status:<12} {title}
        # No date column is included in short mode
        assert "AF-1" in out
        assert "P1" in out
        assert "open" in out
        assert "Short output test" in out

    def test_long_mode_includes_type_and_date(
        self, crumbs_env: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Default (long) mode includes crumb type and created_at date."""
        _write(crumbs_env, [_task("AF-1", "Long mode", created_at="2026-03-01T10:00:00Z")])
        cmd_list(_list_args(short=False))
        out = capsys.readouterr().out
        assert "task" in out
        assert "2026-03-01" in out

    def test_empty_results_prints_message(
        self, crumbs_env: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """cmd_list prints 'no crumbs found' when no results match the filter."""
        _write(crumbs_env, [_task("AF-1", "Open only", "open")])
        cmd_list(_list_args(filter_closed=True))
        out = capsys.readouterr().out
        assert "no crumbs found" in out

    def test_trails_excluded_from_list(
        self, crumbs_env: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """cmd_list excludes records with type='trail'."""
        _write(crumbs_env, [
            _task("AF-1", "Real task", "open"),
            {
                "id": "AF-T1",
                "type": "trail",
                "title": "Trail record",
                "status": "open",
                "created_at": "2026-01-01T00:00:00Z",
            },
        ])
        cmd_list(_list_args())
        out = capsys.readouterr().out
        assert "AF-1" in out
        assert "AF-T1" not in out

    def test_priority_and_status_filter_compose(
        self, crumbs_env: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """--priority and --open together narrow to open crumbs with that priority."""
        _write(crumbs_env, [
            _task("AF-1", "P1 open", "open", "P1"),
            _task("AF-2", "P1 closed", "closed", "P1"),
            _task("AF-3", "P2 open", "open", "P2"),
        ])
        cmd_list(_list_args(filter_open=True, priority="P1"))
        out = capsys.readouterr().out
        assert "AF-1" in out
        assert "AF-2" not in out
        assert "AF-3" not in out

    def test_after_filter_rejects_non_iso_date(
        self, crumbs_env: Path
    ) -> None:
        """--after with non-zero-padded date (2026-3-1) exits non-zero."""
        _write(crumbs_env, [_task("AF-1", "Task")])
        with pytest.raises(SystemExit):
            cmd_list(_list_args(after="2026-3-1"))

    def test_after_filter_rejects_garbage_string(
        self, crumbs_env: Path
    ) -> None:
        """--after with non-date string exits non-zero."""
        _write(crumbs_env, [_task("AF-1", "Task")])
        with pytest.raises(SystemExit):
            cmd_list(_list_args(after="not-a-date"))

    def test_after_filter_accepts_valid_iso_date(
        self, crumbs_env: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """--after with valid YYYY-MM-DD continues to work correctly."""
        _write(crumbs_env, [
            _task("AF-1", "Old task", created_at="2025-12-01T00:00:00Z"),
            _task("AF-2", "New task", created_at="2026-06-01T00:00:00Z"),
        ])
        cmd_list(_list_args(after="2026-01-01"))
        out = capsys.readouterr().out
        assert "AF-1" not in out
        assert "AF-2" in out


# ---------------------------------------------------------------------------
# TestReady
# ---------------------------------------------------------------------------


class TestReady:
    """Tests for cmd_ready: returns open crumbs with all blockers closed."""

    def test_no_blockers_is_ready(
        self, crumbs_env: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """An open crumb with no blocked_by is ready."""
        _write(crumbs_env, [_task("AF-1", "No blockers", "open")])
        cmd_ready(_ready_args())
        out = capsys.readouterr().out
        assert "AF-1" in out

    def test_open_blocker_is_not_ready(
        self, crumbs_env: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """An open crumb blocked by an open crumb is not ready."""
        _write(crumbs_env, [
            _task("AF-1", "Blocker", "open"),
            _task("AF-2", "Blocked", "open", blocked_by=["AF-1"]),
        ])
        cmd_ready(_ready_args())
        out = capsys.readouterr().out
        assert "AF-1" in out
        assert "AF-2" not in out

    def test_in_progress_blocker_is_not_ready(
        self, crumbs_env: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """An open crumb blocked by an in_progress crumb is not ready."""
        _write(crumbs_env, [
            _task("AF-1", "Blocker", "in_progress"),
            _task("AF-2", "Blocked", "open", blocked_by=["AF-1"]),
        ])
        cmd_ready(_ready_args())
        out = capsys.readouterr().out
        # AF-1 is in_progress so not included (cmd_ready filters status==open only)
        assert "AF-1" not in out
        assert "AF-2" not in out

    def test_closed_blocker_makes_crumb_ready(
        self, crumbs_env: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """An open crumb whose blocker is closed is ready."""
        _write(crumbs_env, [
            _task("AF-1", "Closed blocker", "closed"),
            _task("AF-2", "Now ready", "open", blocked_by=["AF-1"]),
        ])
        cmd_ready(_ready_args())
        out = capsys.readouterr().out
        assert "AF-2" in out

    def test_partial_blocked_not_ready(
        self, crumbs_env: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """A crumb with one closed and one open blocker is not ready."""
        _write(crumbs_env, [
            _task("AF-1", "Closed", "closed"),
            _task("AF-2", "Open blocker", "open"),
            _task("AF-3", "Partially blocked", "open", blocked_by=["AF-1", "AF-2"]),
        ])
        cmd_ready(_ready_args())
        out = capsys.readouterr().out
        assert "AF-3" not in out

    def test_excludes_closed_tasks(
        self, crumbs_env: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """cmd_ready never includes closed crumbs."""
        _write(crumbs_env, [_task("AF-1", "Closed task", "closed")])
        cmd_ready(_ready_args())
        out = capsys.readouterr().out
        assert "AF-1" not in out

    def test_excludes_in_progress_tasks(
        self, crumbs_env: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """cmd_ready never includes in_progress crumbs."""
        _write(crumbs_env, [_task("AF-1", "In progress", "in_progress")])
        cmd_ready(_ready_args())
        out = capsys.readouterr().out
        assert "AF-1" not in out

    def test_limit_caps_output(
        self, crumbs_env: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """--limit N returns at most N ready crumbs."""
        _write(crumbs_env, [
            _task(f"AF-{i}", f"Task {i}", "open", created_at=f"2026-01-{i:02d}T00:00:00Z")
            for i in range(1, 5)
        ])
        cmd_ready(_ready_args(limit=2))
        out = capsys.readouterr().out
        lines = [ln for ln in out.splitlines() if ln.strip()]
        assert len(lines) == 2

    def test_missing_blocker_id_treated_as_resolved(
        self, crumbs_env: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """A blocked_by entry referencing a non-existent ID is ignored (treated resolved)."""
        _write(crumbs_env, [
            _task("AF-2", "Dangling blocker ref", "open", blocked_by=["AF-99"]),
        ])
        cmd_ready(_ready_args())
        out = capsys.readouterr().out
        # AF-99 doesn't exist, so AF-2 is considered unblocked -> ready
        assert "AF-2" in out

    def test_excludes_trails(
        self, crumbs_env: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """cmd_ready excludes trail records even when open."""
        _write(crumbs_env, [
            {
                "id": "AF-T1",
                "type": "trail",
                "title": "Open trail",
                "status": "open",
                "created_at": "2026-01-01T00:00:00Z",
            }
        ])
        cmd_ready(_ready_args())
        out = capsys.readouterr().out
        assert "AF-T1" not in out

    def test_sort_by_priority(
        self, crumbs_env: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """--sort priority returns lower priority numbers first."""
        _write(crumbs_env, [
            _task("AF-1", "P3 task", "open", "P3", created_at="2026-01-01T00:00:00Z"),
            _task("AF-2", "P1 task", "open", "P1", created_at="2026-01-02T00:00:00Z"),
            _task("AF-3", "P2 task", "open", "P2", created_at="2026-01-03T00:00:00Z"),
        ])
        cmd_ready(_ready_args(sort="priority"))
        out = capsys.readouterr().out
        lines = [ln for ln in out.splitlines() if ln.strip()]
        ids_in_order = [ln.split()[0] for ln in lines]
        assert ids_in_order == ["AF-2", "AF-3", "AF-1"]

    def test_empty_task_list_produces_no_output(
        self, crumbs_env: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """cmd_ready produces no output when tasks.jsonl is empty."""
        # crumbs_env already has an empty tasks.jsonl
        cmd_ready(_ready_args())
        out = capsys.readouterr().out
        assert out.strip() == ""


# ---------------------------------------------------------------------------
# TestBlocked
# ---------------------------------------------------------------------------


class TestBlocked:
    """Tests for cmd_blocked: returns open crumbs with at least one live blocker."""

    def test_open_blocker_appears_in_blocked(
        self, crumbs_env: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """An open crumb blocked by an open crumb appears in blocked output."""
        _write(crumbs_env, [
            _task("AF-1", "Blocker", "open"),
            _task("AF-2", "Blocked task", "open", blocked_by=["AF-1"]),
        ])
        cmd_blocked(Namespace())
        out = capsys.readouterr().out
        assert "AF-2" in out

    def test_in_progress_blocker_shows_as_blocked(
        self, crumbs_env: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """An open crumb blocked by an in_progress crumb appears in blocked output."""
        _write(crumbs_env, [
            _task("AF-1", "In-progress blocker", "in_progress"),
            _task("AF-2", "Blocked task", "open", blocked_by=["AF-1"]),
        ])
        cmd_blocked(Namespace())
        out = capsys.readouterr().out
        assert "AF-2" in out

    def test_closed_blocker_not_shown(
        self, crumbs_env: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """A crumb whose only blocker is closed does NOT appear in blocked output."""
        _write(crumbs_env, [
            _task("AF-1", "Closed blocker", "closed"),
            _task("AF-2", "No longer blocked", "open", blocked_by=["AF-1"]),
        ])
        cmd_blocked(Namespace())
        out = capsys.readouterr().out
        assert "AF-2" not in out

    def test_no_blocked_by_not_in_output(
        self, crumbs_env: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """An open crumb with no blocked_by does not appear in blocked output."""
        _write(crumbs_env, [_task("AF-1", "Free task", "open")])
        cmd_blocked(Namespace())
        out = capsys.readouterr().out
        assert "AF-1" not in out

    def test_excludes_closed_crumbs(
        self, crumbs_env: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """cmd_blocked never includes closed crumbs even if they have blockers."""
        _write(crumbs_env, [
            _task("AF-1", "Open blocker", "open"),
            _task("AF-2", "Closed blocked", "closed", blocked_by=["AF-1"]),
        ])
        cmd_blocked(Namespace())
        out = capsys.readouterr().out
        assert "AF-2" not in out

    def test_blocking_task_id_visible_in_output(
        self, crumbs_env: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """The blocked task's own ID appears in the output line."""
        _write(crumbs_env, [
            _task("AF-1", "Blocker", "open"),
            _task("AF-2", "I am blocked", "open", blocked_by=["AF-1"]),
        ])
        cmd_blocked(Namespace())
        out = capsys.readouterr().out
        # The blocked crumb ID itself must appear in the output
        assert "AF-2" in out

    def test_dangling_blocked_by_not_shown(
        self, crumbs_env: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """A blocked_by referencing a non-existent ID is treated as resolved (not blocked)."""
        _write(crumbs_env, [
            _task("AF-2", "Dangling blocker", "open", blocked_by=["AF-99"]),
        ])
        cmd_blocked(Namespace())
        out = capsys.readouterr().out
        # Non-existent blocker -> treated as resolved -> AF-2 is not blocked
        assert "AF-2" not in out

    def test_multiple_blocked_tasks(
        self, crumbs_env: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """cmd_blocked shows all blocked tasks, not just the first."""
        _write(crumbs_env, [
            _task("AF-1", "Shared blocker", "open"),
            _task("AF-2", "Blocked A", "open", blocked_by=["AF-1"]),
            _task("AF-3", "Blocked B", "open", blocked_by=["AF-1"]),
        ])
        cmd_blocked(Namespace())
        out = capsys.readouterr().out
        assert "AF-2" in out
        assert "AF-3" in out

    def test_excludes_trails(
        self, crumbs_env: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """cmd_blocked excludes trail records."""
        _write(crumbs_env, [
            _task("AF-1", "Open blocker", "open"),
            {
                "id": "AF-T1",
                "type": "trail",
                "title": "Blocked trail",
                "status": "open",
                "created_at": "2026-01-01T00:00:00Z",
                "links": {"blocked_by": ["AF-1"]},
            },
        ])
        cmd_blocked(Namespace())
        out = capsys.readouterr().out
        assert "AF-T1" not in out

    def test_empty_results_no_output(
        self, crumbs_env: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """cmd_blocked produces no output when no crumbs are blocked."""
        _write(crumbs_env, [_task("AF-1", "Free", "open")])
        cmd_blocked(Namespace())
        out = capsys.readouterr().out
        assert out.strip() == ""

    def test_partial_resolution_still_blocked(
        self, crumbs_env: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """A crumb with one closed and one open blocker is still blocked."""
        _write(crumbs_env, [
            _task("AF-1", "Closed blocker", "closed"),
            _task("AF-2", "Open blocker", "open"),
            _task("AF-3", "Partially resolved", "open", blocked_by=["AF-1", "AF-2"]),
        ])
        cmd_blocked(Namespace())
        out = capsys.readouterr().out
        assert "AF-3" in out


# ---------------------------------------------------------------------------
# TestSearch
# ---------------------------------------------------------------------------


class TestSearch:
    """Tests for cmd_search: case-insensitive match on title and description."""

    def test_matches_title(
        self, crumbs_env: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """cmd_search returns crumbs whose title contains the query."""
        _write(crumbs_env, [
            _task("AF-1", "Fix authentication bug"),
            _task("AF-2", "Refactor database layer"),
        ])
        cmd_search(_search_args("authentication"))
        out = capsys.readouterr().out
        assert "AF-1" in out
        assert "AF-2" not in out

    def test_matches_description(
        self, crumbs_env: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """cmd_search returns crumbs whose description contains the query."""
        _write(crumbs_env, [
            _task("AF-1", "Task one", description="Fix the login endpoint"),
            _task("AF-2", "Task two", description="Unrelated work"),
        ])
        cmd_search(_search_args("login"))
        out = capsys.readouterr().out
        assert "AF-1" in out
        assert "AF-2" not in out

    def test_case_insensitive_title(
        self, crumbs_env: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """cmd_search is case-insensitive when matching titles."""
        _write(crumbs_env, [_task("AF-1", "Fix Authentication Bug")])
        cmd_search(_search_args("authentication"))
        out = capsys.readouterr().out
        assert "AF-1" in out

    def test_case_insensitive_uppercase_query(
        self, crumbs_env: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """cmd_search is case-insensitive even when query is uppercase."""
        _write(crumbs_env, [_task("AF-1", "fix login issue")])
        cmd_search(_search_args("LOGIN"))
        out = capsys.readouterr().out
        assert "AF-1" in out

    def test_case_insensitive_description(
        self, crumbs_env: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """cmd_search is case-insensitive when matching descriptions."""
        _write(crumbs_env, [
            _task("AF-1", "Task", description="Database MIGRATION steps"),
        ])
        cmd_search(_search_args("migration"))
        out = capsys.readouterr().out
        assert "AF-1" in out

    def test_no_match_returns_no_output(
        self, crumbs_env: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """cmd_search produces no output when nothing matches."""
        _write(crumbs_env, [
            _task("AF-1", "Unrelated task"),
            _task("AF-2", "Another unrelated"),
        ])
        cmd_search(_search_args("xyzzy"))
        out = capsys.readouterr().out
        assert out.strip() == ""

    def test_matches_title_and_description(
        self, crumbs_env: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """cmd_search returns all crumbs matching query in either title or description."""
        _write(crumbs_env, [
            _task("AF-1", "Migration task"),
            _task("AF-2", "Unrelated", description="Database migration needed"),
            _task("AF-3", "Another unrelated"),
        ])
        cmd_search(_search_args("migration"))
        out = capsys.readouterr().out
        assert "AF-1" in out
        assert "AF-2" in out
        assert "AF-3" not in out

    def test_partial_word_match(
        self, crumbs_env: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """cmd_search performs substring matching (not whole-word only)."""
        _write(crumbs_env, [_task("AF-1", "Refactoring needed")])
        cmd_search(_search_args("factor"))
        out = capsys.readouterr().out
        assert "AF-1" in out

    def test_empty_tasks_produces_no_output(
        self, crumbs_env: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """cmd_search on empty tasks.jsonl produces no output."""
        cmd_search(_search_args("anything"))
        out = capsys.readouterr().out
        assert out.strip() == ""

    def test_trail_records_included_in_search(
        self, crumbs_env: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """cmd_search includes trail records (search does not filter by type)."""
        _write(crumbs_env, [
            {
                "id": "AF-T1",
                "type": "trail",
                "title": "Auth trail",
                "status": "open",
                "created_at": "2026-01-01T00:00:00Z",
            }
        ])
        cmd_search(_search_args("auth"))
        out = capsys.readouterr().out
        assert "AF-T1" in out

    def test_multiple_matches_all_shown(
        self, crumbs_env: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """cmd_search returns all matching crumbs, not just the first."""
        _write(crumbs_env, [
            _task("AF-1", "Fix auth service"),
            _task("AF-2", "Auth token refresh"),
            _task("AF-3", "Logging setup"),
        ])
        cmd_search(_search_args("auth"))
        out = capsys.readouterr().out
        assert "AF-1" in out
        assert "AF-2" in out
        assert "AF-3" not in out

    def test_output_includes_id_priority_status_title(
        self, crumbs_env: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """cmd_search output contains id, priority, status, and title."""
        _write(crumbs_env, [_task("AF-1", "Find me", "open", "P0")])
        cmd_search(_search_args("find me"))
        out = capsys.readouterr().out.strip()
        assert "AF-1" in out
        assert "P0" in out
        assert "open" in out
        assert "Find me" in out


# ---------------------------------------------------------------------------
# TestListJSON
# ---------------------------------------------------------------------------


class TestListJSON:
    """Tests for cmd_list --json output mode (direct-call via Namespace)."""

    def test_json_output_is_valid_json_array(
        self, crumbs_env: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """cmd_list with json_output=True prints a JSON array parseable by json.loads."""
        _write(crumbs_env, [_task("AF-1", "Alpha"), _task("AF-2", "Beta")])
        cmd_list(_list_args(json_output=True))
        out = capsys.readouterr().out
        parsed = json.loads(out)
        assert isinstance(parsed, list)
        assert len(parsed) == 2

    def test_json_output_contains_required_fields(
        self, crumbs_env: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Each JSON object in the array contains all required schema fields."""
        _write(crumbs_env, [_task("AF-1", "Schema check", "open", "P1")])
        cmd_list(_list_args(json_output=True))
        out = capsys.readouterr().out
        parsed = json.loads(out)
        obj = parsed[0]
        for field in ("id", "title", "type", "status", "priority",
                      "description", "acceptance_criteria", "scope", "links", "notes"):
            assert field in obj, f"Required field '{field}' missing from JSON output"

    def test_json_output_field_values_correct(
        self, crumbs_env: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """JSON object field values match the stored task data."""
        _write(crumbs_env, [_task("AF-1", "Value check", "in_progress", "P0")])
        cmd_list(_list_args(json_output=True))
        out = capsys.readouterr().out
        parsed = json.loads(out)
        obj = parsed[0]
        assert obj["id"] == "AF-1"
        assert obj["title"] == "Value check"
        assert obj["status"] == "in_progress"
        assert obj["priority"] == "P0"
        assert obj["type"] == "task"

    def test_json_output_with_filter_open(
        self, crumbs_env: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """--json and --open compose: only open crumbs appear in the JSON array."""
        _write(crumbs_env, [
            _task("AF-1", "Open task", "open"),
            _task("AF-2", "Closed task", "closed"),
            _task("AF-3", "In progress", "in_progress"),
        ])
        cmd_list(_list_args(json_output=True, filter_open=True))
        out = capsys.readouterr().out
        parsed = json.loads(out)
        ids = [obj["id"] for obj in parsed]
        assert "AF-1" in ids
        assert "AF-2" not in ids
        assert "AF-3" not in ids

    def test_json_output_empty_results_returns_empty_array(
        self, crumbs_env: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """cmd_list --json with no matching results returns '[]', not 'no crumbs found'."""
        _write(crumbs_env, [_task("AF-1", "Open only", "open")])
        cmd_list(_list_args(json_output=True, filter_closed=True))
        out = capsys.readouterr().out
        parsed = json.loads(out)
        assert parsed == []

    def test_json_output_absent_fields_are_null(
        self, crumbs_env: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Optional fields not stored on a crumb appear as null in JSON output."""
        _write(crumbs_env, [_task("AF-1", "Minimal task")])
        cmd_list(_list_args(json_output=True))
        out = capsys.readouterr().out
        parsed = json.loads(out)
        obj = parsed[0]
        # description and notes are not set by _task() — must be null
        assert obj["description"] is None
        assert obj["notes"] is None

    def test_human_readable_unchanged_without_json_flag(
        self, crumbs_env: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """cmd_list without json_output produces human-readable text, not JSON."""
        _write(crumbs_env, [_task("AF-1", "Human readable", "open", "P2")])
        cmd_list(_list_args(json_output=False))
        out = capsys.readouterr().out
        # Human-readable output: id in first column, not a JSON array
        assert out.strip().startswith("AF-1")
        # Must not be a JSON array
        assert not out.strip().startswith("[")


# ---------------------------------------------------------------------------
# Helper for cmd_show direct-call tests
# ---------------------------------------------------------------------------


def _show_args(task_id: str, json_output: bool = False) -> Namespace:
    """Build a Namespace matching cmd_show's expected attributes.

    Args:
        task_id: The crumb ID to look up.
        json_output: Whether to request JSON output mode.

    Returns:
        Namespace with ``id`` and ``json_output`` set.
    """
    return Namespace(id=task_id, json_output=json_output)


# ---------------------------------------------------------------------------
# TestShowJSON
# ---------------------------------------------------------------------------


class TestShowJSON:
    """Tests for cmd_show --json output mode (direct-call via Namespace)."""

    def test_show_json_returns_single_object(
        self, crumbs_env: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """cmd_show --json emits a single JSON object (dict), not a list."""
        _write(crumbs_env, [_task("AF-1", "Show me")])
        cmd_show(_show_args("AF-1", json_output=True))
        out = capsys.readouterr().out
        parsed = json.loads(out)
        assert isinstance(parsed, dict)

    def test_show_json_contains_required_fields(
        self, crumbs_env: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """cmd_show --json object includes all required schema fields."""
        _write(crumbs_env, [_task("AF-1", "Schema check", "open", "P1")])
        cmd_show(_show_args("AF-1", json_output=True))
        out = capsys.readouterr().out
        parsed = json.loads(out)
        for field in ("id", "title", "type", "status", "priority",
                      "description", "acceptance_criteria", "scope", "links", "notes"):
            assert field in parsed, f"Required field '{field}' missing from JSON output"

    def test_show_json_field_values_correct(
        self, crumbs_env: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """cmd_show --json values match the stored task data."""
        _write(crumbs_env, [_task("AF-5", "Verify values", "closed", "P0")])
        cmd_show(_show_args("AF-5", json_output=True))
        out = capsys.readouterr().out
        parsed = json.loads(out)
        assert parsed["id"] == "AF-5"
        assert parsed["title"] == "Verify values"
        assert parsed["status"] == "closed"
        assert parsed["priority"] == "P0"

    def test_show_json_human_readable_unchanged(
        self, crumbs_env: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """cmd_show without --json produces human-readable text, not JSON."""
        _write(crumbs_env, [_task("AF-1", "Human readable output")])
        cmd_show(_show_args("AF-1", json_output=False))
        out = capsys.readouterr().out
        # Human-readable: starts with "ID: AF-1" or similar, not a JSON brace
        assert "AF-1" in out
        assert not out.strip().startswith("{")

"""Tests for cmd_link: --parent, --blocked-by, --remove-blocked-by, --discovered-from.

All tests use the ``crumbs_env`` fixture so no real ``.crumbs/`` directory is
touched. Each test writes seed crumbs into tasks.jsonl, calls ``cmd_link``
directly with an ``argparse.Namespace``, then re-reads tasks.jsonl to verify
the persisted state.

Note on criterion 7 (nonexistent blocker/parent ID):
    ``cmd_link`` explicitly permits dangling references — the docstring states
    "Dangling references are allowed — the doctor command validates referential
    integrity."  Consequently, passing a nonexistent blocker or parent ID does
    NOT raise SystemExit; the link is stored as-is.  The test
    ``test_link_blocked_by_nonexistent_blocker_is_allowed`` documents this
    actual behaviour.  Acceptance criterion 7 as written ("raises SystemExit
    for nonexistent blocker/parent ID") does not match the implementation.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict

import pytest

from crumb import cmd_link, read_tasks


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_namespace(
    crumb_id: str,
    *,
    link_parent: str | None = None,
    blocked_by: str | None = None,
    remove_blocked_by: str | None = None,
    discovered_from: str | None = None,
) -> argparse.Namespace:
    """Build a minimal Namespace matching what argparse hands to cmd_link.

    Args:
        crumb_id: The ID of the crumb to modify (maps to ``args.id``).
        link_parent: Value for ``--parent`` flag (None = flag absent).
        blocked_by: Value for ``--blocked-by`` flag (None = flag absent).
        remove_blocked_by: Value for ``--remove-blocked-by`` flag.
        discovered_from: Value for ``--discovered-from`` flag.

    Returns:
        Populated ``argparse.Namespace`` ready for ``cmd_link``.
    """
    return argparse.Namespace(
        id=crumb_id,
        link_parent=link_parent,
        blocked_by=blocked_by,
        remove_blocked_by=remove_blocked_by,
        discovered_from=discovered_from,
    )


def _seed_task(crumbs_dir: Path, record: Dict[str, Any]) -> None:
    """Append a single task record to tasks.jsonl.

    Args:
        crumbs_dir: Path to the isolated ``.crumbs/`` directory.
        record: Task dict to serialise and append.
    """
    tasks_file = crumbs_dir / "tasks.jsonl"
    existing = tasks_file.read_text(encoding="utf-8")
    tasks_file.write_text(
        existing + json.dumps(record) + "\n",
        encoding="utf-8",
    )


def _read_crumb(crumbs_dir: Path, crumb_id: str) -> Dict[str, Any]:
    """Read tasks.jsonl and return the record with the given ID.

    Args:
        crumbs_dir: Path to the isolated ``.crumbs/`` directory.
        crumb_id: ID to look up.

    Returns:
        Matching task dict.

    Raises:
        KeyError: If no record with that ID is found.
    """
    tasks_file = crumbs_dir / "tasks.jsonl"
    for record in read_tasks(tasks_file):
        if record.get("id") == crumb_id:
            return record
    raise KeyError(f"crumb {crumb_id!r} not found in tasks.jsonl")


# ---------------------------------------------------------------------------
# TestLink
# ---------------------------------------------------------------------------


class TestLink:
    """Tests for cmd_link covering all four link modes and error paths."""

    # ------------------------------------------------------------------
    # --parent
    # ------------------------------------------------------------------

    def test_parent_sets_parent_field(self, crumbs_env: Path) -> None:
        """cmd_link --parent sets links.parent on the crumb record."""
        _seed_task(crumbs_env, {"id": "AF-1", "title": "Child task", "status": "open"})
        _seed_task(crumbs_env, {"id": "AF-T1", "title": "Parent trail", "status": "open", "type": "trail"})

        args = _make_namespace("AF-1", link_parent="AF-T1")
        cmd_link(args)

        record = _read_crumb(crumbs_env, "AF-1")
        assert record.get("links", {}).get("parent") == "AF-T1"

    def test_parent_replaces_existing_parent(self, crumbs_env: Path) -> None:
        """cmd_link --parent replaces an already-set parent link."""
        _seed_task(crumbs_env, {
            "id": "AF-1",
            "title": "Child task",
            "status": "open",
            "links": {"parent": "AF-T1"},
        })
        _seed_task(crumbs_env, {"id": "AF-T2", "title": "New trail", "status": "open", "type": "trail"})

        args = _make_namespace("AF-1", link_parent="AF-T2")
        cmd_link(args)

        record = _read_crumb(crumbs_env, "AF-1")
        assert record["links"]["parent"] == "AF-T2"

    def test_parent_no_change_when_already_set(self, crumbs_env: Path, capsys: pytest.CaptureFixture[str]) -> None:
        """cmd_link --parent prints 'no link changes' when parent is already set to same value."""
        _seed_task(crumbs_env, {
            "id": "AF-1",
            "title": "Child",
            "status": "open",
            "links": {"parent": "AF-T1"},
        })

        args = _make_namespace("AF-1", link_parent="AF-T1")
        cmd_link(args)

        captured = capsys.readouterr()
        assert "no link changes" in captured.out

    # ------------------------------------------------------------------
    # --blocked-by
    # ------------------------------------------------------------------

    def test_blocked_by_adds_blocker_to_list(self, crumbs_env: Path) -> None:
        """cmd_link --blocked-by appends the blocker ID to links.blocked_by."""
        _seed_task(crumbs_env, {"id": "AF-1", "title": "Task", "status": "open"})
        _seed_task(crumbs_env, {"id": "AF-2", "title": "Blocker", "status": "open"})

        args = _make_namespace("AF-1", blocked_by="AF-2")
        cmd_link(args)

        record = _read_crumb(crumbs_env, "AF-1")
        assert "AF-2" in record.get("links", {}).get("blocked_by", [])

    def test_blocked_by_appends_second_blocker(self, crumbs_env: Path) -> None:
        """cmd_link --blocked-by appends without removing an existing blocker."""
        _seed_task(crumbs_env, {
            "id": "AF-1",
            "title": "Task",
            "status": "open",
            "links": {"blocked_by": ["AF-2"]},
        })
        _seed_task(crumbs_env, {"id": "AF-3", "title": "Second blocker", "status": "open"})

        args = _make_namespace("AF-1", blocked_by="AF-3")
        cmd_link(args)

        record = _read_crumb(crumbs_env, "AF-1")
        blocked = record.get("links", {}).get("blocked_by", [])
        assert "AF-2" in blocked
        assert "AF-3" in blocked

    def test_blocked_by_no_duplicates(self, crumbs_env: Path) -> None:
        """cmd_link --blocked-by does not add a duplicate entry."""
        _seed_task(crumbs_env, {
            "id": "AF-1",
            "title": "Task",
            "status": "open",
            "links": {"blocked_by": ["AF-2"]},
        })

        args = _make_namespace("AF-1", blocked_by="AF-2")
        cmd_link(args)

        record = _read_crumb(crumbs_env, "AF-1")
        blocked = record.get("links", {}).get("blocked_by", [])
        assert blocked.count("AF-2") == 1

    # ------------------------------------------------------------------
    # --remove-blocked-by
    # ------------------------------------------------------------------

    def test_remove_blocked_by_removes_blocker(self, crumbs_env: Path) -> None:
        """cmd_link --remove-blocked-by removes the specified ID from blocked_by."""
        _seed_task(crumbs_env, {
            "id": "AF-1",
            "title": "Task",
            "status": "open",
            "links": {"blocked_by": ["AF-2", "AF-3"]},
        })

        args = _make_namespace("AF-1", remove_blocked_by="AF-2")
        cmd_link(args)

        record = _read_crumb(crumbs_env, "AF-1")
        blocked = record.get("links", {}).get("blocked_by", [])
        assert "AF-2" not in blocked
        assert "AF-3" in blocked

    def test_remove_blocked_by_last_entry_leaves_empty_list(self, crumbs_env: Path) -> None:
        """cmd_link --remove-blocked-by with the only entry produces an empty list."""
        _seed_task(crumbs_env, {
            "id": "AF-1",
            "title": "Task",
            "status": "open",
            "links": {"blocked_by": ["AF-2"]},
        })

        args = _make_namespace("AF-1", remove_blocked_by="AF-2")
        cmd_link(args)

        record = _read_crumb(crumbs_env, "AF-1")
        blocked = record.get("links", {}).get("blocked_by", [])
        assert "AF-2" not in blocked

    def test_remove_blocked_by_absent_id_no_change(self, crumbs_env: Path, capsys: pytest.CaptureFixture[str]) -> None:
        """cmd_link --remove-blocked-by prints 'no link changes' when ID is not present."""
        _seed_task(crumbs_env, {
            "id": "AF-1",
            "title": "Task",
            "status": "open",
            "links": {"blocked_by": ["AF-3"]},
        })

        args = _make_namespace("AF-1", remove_blocked_by="AF-99")
        cmd_link(args)

        captured = capsys.readouterr()
        assert "no link changes" in captured.out

    # ------------------------------------------------------------------
    # --discovered-from
    # ------------------------------------------------------------------

    def test_discovered_from_sets_field(self, crumbs_env: Path) -> None:
        """cmd_link --discovered-from sets links.discovered_from on the crumb."""
        _seed_task(crumbs_env, {"id": "AF-1", "title": "Task", "status": "open"})

        args = _make_namespace("AF-1", discovered_from="retro-2026-03")
        cmd_link(args)

        record = _read_crumb(crumbs_env, "AF-1")
        assert record.get("links", {}).get("discovered_from") == "retro-2026-03"

    def test_discovered_from_replaces_existing_value(self, crumbs_env: Path) -> None:
        """cmd_link --discovered-from replaces an already-set discovered_from value."""
        _seed_task(crumbs_env, {
            "id": "AF-1",
            "title": "Task",
            "status": "open",
            "links": {"discovered_from": "old-source"},
        })

        args = _make_namespace("AF-1", discovered_from="new-source")
        cmd_link(args)

        record = _read_crumb(crumbs_env, "AF-1")
        assert record["links"]["discovered_from"] == "new-source"

    def test_discovered_from_no_change_when_same_value(self, crumbs_env: Path, capsys: pytest.CaptureFixture[str]) -> None:
        """cmd_link --discovered-from prints 'no link changes' when value is already set."""
        _seed_task(crumbs_env, {
            "id": "AF-1",
            "title": "Task",
            "status": "open",
            "links": {"discovered_from": "retro-2026-03"},
        })

        args = _make_namespace("AF-1", discovered_from="retro-2026-03")
        cmd_link(args)

        captured = capsys.readouterr()
        assert "no link changes" in captured.out

    # ------------------------------------------------------------------
    # Error paths
    # ------------------------------------------------------------------

    def test_raises_system_exit_for_nonexistent_crumb_id(self, crumbs_env: Path) -> None:
        """cmd_link raises SystemExit when the target crumb ID does not exist."""
        # tasks.jsonl is empty — no crumbs seeded
        args = _make_namespace("AF-DOES-NOT-EXIST", link_parent="AF-T1")
        with pytest.raises(SystemExit):
            cmd_link(args)

    def test_raises_system_exit_for_nonexistent_crumb_id_with_blocked_by(self, crumbs_env: Path) -> None:
        """cmd_link raises SystemExit for nonexistent crumb ID even with --blocked-by."""
        args = _make_namespace("AF-GHOST", blocked_by="AF-2")
        with pytest.raises(SystemExit):
            cmd_link(args)


# ---------------------------------------------------------------------------
# TestLinkJSON
# ---------------------------------------------------------------------------


class TestLinkJSON:
    """Tests for cmd_link --json output mode."""

    def test_json_output_parent_returns_updated_crumb(
        self, crumbs_env: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """cmd_link --parent --json returns the updated crumb object with new links state."""
        _seed_task(crumbs_env, {"id": "AF-1", "title": "Child", "status": "open"})
        _seed_task(crumbs_env, {"id": "AF-T1", "title": "Trail", "status": "open", "type": "trail"})

        args = argparse.Namespace(
            id="AF-1",
            link_parent="AF-T1",
            blocked_by=None,
            remove_blocked_by=None,
            discovered_from=None,
            json_output=True,
        )
        cmd_link(args)

        out = capsys.readouterr().out
        obj = json.loads(out)
        assert obj["id"] == "AF-1"
        assert isinstance(obj["links"], dict)
        assert obj["links"].get("parent") == "AF-T1"

    def test_json_output_blocked_by_returns_updated_crumb(
        self, crumbs_env: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """cmd_link --blocked-by --json returns the updated crumb with its new links state."""
        _seed_task(crumbs_env, {"id": "AF-1", "title": "Blocked", "status": "open"})
        _seed_task(crumbs_env, {"id": "AF-2", "title": "Blocker", "status": "open"})

        args = argparse.Namespace(
            id="AF-1",
            link_parent=None,
            blocked_by="AF-2",
            remove_blocked_by=None,
            discovered_from=None,
            json_output=True,
        )
        cmd_link(args)

        out = capsys.readouterr().out
        obj = json.loads(out)
        assert obj["id"] == "AF-1"
        assert isinstance(obj["links"], dict)
        assert "AF-2" in obj["links"].get("blocked_by", [])

    def test_json_output_contains_required_fields(
        self, crumbs_env: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """JSON object from cmd_link contains all required schema fields."""
        _seed_task(crumbs_env, {"id": "AF-1", "title": "Task", "status": "open", "priority": "P1"})

        args = argparse.Namespace(
            id="AF-1",
            link_parent=None,
            blocked_by="AF-999",
            remove_blocked_by=None,
            discovered_from=None,
            json_output=True,
        )
        cmd_link(args)

        out = capsys.readouterr().out
        obj = json.loads(out)
        for field in ("id", "title", "type", "status", "priority", "links"):
            assert field in obj, f"Required field '{field}' missing from JSON output"

    def test_json_to_stdout_no_human_text(
        self, crumbs_env: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """With --json, no human-readable 'updated links for' text is printed."""
        _seed_task(crumbs_env, {"id": "AF-1", "title": "Task", "status": "open"})

        args = argparse.Namespace(
            id="AF-1",
            link_parent=None,
            blocked_by="AF-2",
            remove_blocked_by=None,
            discovered_from=None,
            json_output=True,
        )
        cmd_link(args)

        out = capsys.readouterr().out
        assert "updated links" not in out
        # Ensure it's valid JSON
        json.loads(out)

    def test_link_blocked_by_nonexistent_blocker_is_allowed(self, crumbs_env: Path) -> None:
        """cmd_link allows a nonexistent blocker ID — dangling references are permitted.

        The implementation docstring states: "Dangling references are allowed —
        the doctor command validates referential integrity."  As a result,
        passing a blocker ID that does not exist in tasks.jsonl succeeds and
        stores the dangling reference.

        This test documents the actual behaviour.  Acceptance criterion 7
        ("raises SystemExit for nonexistent blocker/parent ID") does NOT match
        the implementation; this is a known spec-vs-code discrepancy that is
        out of scope for this task.
        """
        _seed_task(crumbs_env, {"id": "AF-1", "title": "Task", "status": "open"})

        args = _make_namespace("AF-1", blocked_by="AF-NONEXISTENT")
        # Should NOT raise — dangling references are intentionally allowed
        cmd_link(args)

        record = _read_crumb(crumbs_env, "AF-1")
        assert "AF-NONEXISTENT" in record.get("links", {}).get("blocked_by", [])

    def test_link_parent_nonexistent_trail_is_allowed(self, crumbs_env: Path) -> None:
        """cmd_link allows a nonexistent parent trail ID — dangling references are permitted.

        Same rationale as ``test_link_blocked_by_nonexistent_blocker_is_allowed``:
        the implementation does not validate that the parent trail exists.
        """
        _seed_task(crumbs_env, {"id": "AF-1", "title": "Task", "status": "open"})

        args = _make_namespace("AF-1", link_parent="AF-T-NONEXISTENT")
        # Should NOT raise — dangling references are intentionally allowed
        cmd_link(args)

        record = _read_crumb(crumbs_env, "AF-1")
        assert record.get("links", {}).get("parent") == "AF-T-NONEXISTENT"

    # ------------------------------------------------------------------
    # Multiple flags in one invocation
    # ------------------------------------------------------------------

    def test_multiple_flags_combined(self, crumbs_env: Path) -> None:
        """cmd_link applies multiple flags in a single call."""
        _seed_task(crumbs_env, {"id": "AF-1", "title": "Task", "status": "open"})
        _seed_task(crumbs_env, {"id": "AF-T1", "title": "Trail", "status": "open", "type": "trail"})

        args = _make_namespace(
            "AF-1",
            link_parent="AF-T1",
            blocked_by="AF-2",
            discovered_from="kickoff-notes",
        )
        cmd_link(args)

        record = _read_crumb(crumbs_env, "AF-1")
        links = record.get("links", {})
        assert links.get("parent") == "AF-T1"
        assert "AF-2" in links.get("blocked_by", [])
        assert links.get("discovered_from") == "kickoff-notes"

    # ------------------------------------------------------------------
    # updated_at is stamped on change
    # ------------------------------------------------------------------

    def test_link_update_stamps_updated_at(self, crumbs_env: Path) -> None:
        """cmd_link updates the updated_at field when a link change is made."""
        _seed_task(crumbs_env, {
            "id": "AF-1",
            "title": "Task",
            "status": "open",
            "updated_at": "2020-01-01T00:00:00Z",
        })

        args = _make_namespace("AF-1", discovered_from="sprint-1")
        cmd_link(args)

        record = _read_crumb(crumbs_env, "AF-1")
        assert record.get("updated_at") != "2020-01-01T00:00:00Z"
        assert record.get("updated_at") is not None

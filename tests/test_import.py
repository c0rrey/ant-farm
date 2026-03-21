"""Tests for the import command and related Beads migration helpers.

Covers:
  - TestImportPlain: plain JSONL import via cmd_import
  - TestImportBeads: Beads-format migration via cmd_import --from-beads,
    _convert_beads_record, _resolve_beads_epic_refs, _apply_blocks_deps
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List

import pytest

import crumb
from crumb import (
    _apply_blocks_deps,
    _convert_beads_record,
    _resolve_beads_epic_refs,
    cmd_import,
    cmd_update,
    read_tasks,
    read_config,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_import_args(file: str, from_beads: bool = False) -> argparse.Namespace:
    """Return a minimal Namespace that mimics what argparse produces for 'import'."""
    return argparse.Namespace(file=file, from_beads=from_beads)


def _write_jsonl(path: Path, records: List[Dict[str, Any]]) -> None:
    """Write a list of dicts to a JSONL file."""
    with open(path, "w", encoding="utf-8") as fh:
        for rec in records:
            fh.write(json.dumps(rec) + "\n")


# ---------------------------------------------------------------------------
# TestImportPlain
# ---------------------------------------------------------------------------


class TestImportPlain:
    """Tests for plain JSONL import mode."""

    def test_import_adds_records_to_tasks_jsonl(
        self, crumbs_env: Path, tmp_path: Path
    ) -> None:
        """cmd_import reads a JSONL file and appends records to tasks.jsonl."""
        import_file = tmp_path / "import.jsonl"
        _write_jsonl(
            import_file,
            [
                {"id": "AF-1", "type": "task", "title": "Alpha", "status": "open"},
                {"id": "AF-2", "type": "task", "title": "Beta", "status": "open"},
            ],
        )

        args = _make_import_args(str(import_file))
        cmd_import(args)

        tasks = read_tasks(crumbs_env / "tasks.jsonl")
        ids = [t["id"] for t in tasks]
        assert "AF-1" in ids
        assert "AF-2" in ids
        assert len(tasks) == 2

    def test_import_preserves_existing_tasks(
        self, crumbs_env: Path, tmp_path: Path
    ) -> None:
        """cmd_import appends without overwriting pre-existing records."""
        # Seed an existing record
        tasks_path = crumbs_env / "tasks.jsonl"
        tasks_path.write_text(
            json.dumps({"id": "AF-99", "type": "task", "title": "Existing", "status": "open"})
            + "\n",
            encoding="utf-8",
        )

        import_file = tmp_path / "more.jsonl"
        _write_jsonl(import_file, [{"id": "AF-1", "type": "task", "title": "New", "status": "open"}])

        cmd_import(_make_import_args(str(import_file)))

        tasks = read_tasks(tasks_path)
        ids = [t["id"] for t in tasks]
        assert "AF-99" in ids
        assert "AF-1" in ids

    def test_import_assigns_correct_prefix_ids(
        self, crumbs_env: Path, tmp_path: Path
    ) -> None:
        """Imported records use their own IDs (plain mode keeps source IDs)."""
        import_file = tmp_path / "data.jsonl"
        _write_jsonl(import_file, [{"id": "AF-5", "type": "task", "title": "Five", "status": "open"}])

        cmd_import(_make_import_args(str(import_file)))

        tasks = read_tasks(crumbs_env / "tasks.jsonl")
        assert tasks[0]["id"] == "AF-5"

    def test_import_updates_config_counter(
        self, crumbs_env: Path, tmp_path: Path
    ) -> None:
        """After import, next_crumb_id is set above the highest imported ID."""
        import_file = tmp_path / "data.jsonl"
        _write_jsonl(
            import_file,
            [
                {"id": "AF-10", "type": "task", "title": "Ten", "status": "open"},
                {"id": "AF-7", "type": "task", "title": "Seven", "status": "open"},
            ],
        )

        cmd_import(_make_import_args(str(import_file)))

        config = read_config()
        assert config["next_crumb_id"] == 11

    def test_import_raises_system_exit_for_missing_file(
        self, crumbs_env: Path
    ) -> None:
        """cmd_import raises SystemExit when the input file does not exist."""
        args = _make_import_args("/nonexistent/path/missing.jsonl")
        with pytest.raises(SystemExit):
            cmd_import(args)

    def test_import_skips_malformed_json_lines(
        self, crumbs_env: Path, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Malformed JSON lines are skipped with a warning; valid lines are imported."""
        import_file = tmp_path / "mixed.jsonl"
        import_file.write_text(
            '{"id": "AF-1", "type": "task", "title": "Good", "status": "open"}\n'
            "NOT VALID JSON <<<\n"
            '{"id": "AF-2", "type": "task", "title": "Also Good", "status": "open"}\n',
            encoding="utf-8",
        )

        cmd_import(_make_import_args(str(import_file)))

        tasks = read_tasks(crumbs_env / "tasks.jsonl")
        ids = [t["id"] for t in tasks]
        assert "AF-1" in ids
        assert "AF-2" in ids
        assert len(tasks) == 2

        captured = capsys.readouterr()
        assert "malformed" in captured.err.lower()

    def test_import_skips_duplicate_ids(
        self, crumbs_env: Path, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Records with duplicate IDs are skipped with a warning."""
        import_file = tmp_path / "dups.jsonl"
        _write_jsonl(
            import_file,
            [
                {"id": "AF-1", "type": "task", "title": "First", "status": "open"},
                {"id": "AF-1", "type": "task", "title": "Duplicate", "status": "open"},
            ],
        )

        cmd_import(_make_import_args(str(import_file)))

        tasks = read_tasks(crumbs_env / "tasks.jsonl")
        assert len(tasks) == 1
        assert tasks[0]["title"] == "First"

        captured = capsys.readouterr()
        assert "duplicate" in captured.err.lower()

    def test_import_skips_record_without_id(
        self, crumbs_env: Path, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Records missing the 'id' field are skipped with a warning."""
        import_file = tmp_path / "noid.jsonl"
        _write_jsonl(
            import_file,
            [
                {"type": "task", "title": "No ID here", "status": "open"},
                {"id": "AF-3", "type": "task", "title": "Has ID", "status": "open"},
            ],
        )

        cmd_import(_make_import_args(str(import_file)))

        tasks = read_tasks(crumbs_env / "tasks.jsonl")
        assert len(tasks) == 1
        assert tasks[0]["id"] == "AF-3"


# ---------------------------------------------------------------------------
# TestImportBeads
# ---------------------------------------------------------------------------


class TestImportBeads:
    """Tests for Beads-format migration mode."""

    # --- _convert_beads_record unit tests ---

    def test_convert_beads_task_record(self) -> None:
        """_convert_beads_record converts a plain task record to crumb format."""
        beads_rec = {
            "id": "BD-5",
            "issue_type": "task",
            "title": "Do something",
            "status": "open",
            "priority": 2,
            "created_at": "2026-01-01T00:00:00Z",
            "updated_at": "2026-01-01T00:00:00Z",
        }
        config: Dict[str, Any] = {
            "prefix": "AF",
            "next_crumb_id": 1,
            "next_trail_id": 1,
            "default_priority": "P2",
        }
        result = _convert_beads_record(beads_rec, {}, config)

        assert result["id"] == "BD-5"
        assert result["type"] == "task"
        assert result["title"] == "Do something"
        assert result["status"] == "open"
        assert result["priority"] == "P2"

    def test_convert_beads_epic_becomes_trail(self) -> None:
        """An epic record is converted to a trail with a T-prefixed ID."""
        beads_rec = {
            "id": "BD-10",
            "issue_type": "epic",
            "title": "Big Epic",
            "status": "open",
            "priority": 1,
        }
        config: Dict[str, Any] = {
            "prefix": "AF",
            "next_crumb_id": 1,
            "next_trail_id": 3,
            "default_priority": "P2",
        }
        epic_id_map: Dict[str, str] = {}
        result = _convert_beads_record(beads_rec, epic_id_map, config)

        assert result["type"] == "trail"
        assert result["id"] == "AF-T3"
        assert epic_id_map["BD-10"] == "AF-T3"
        assert config["next_trail_id"] == 4

    def test_convert_beads_integer_priority_mapping(self) -> None:
        """Integer priorities 0-4 map to P0-P4 strings."""
        config: Dict[str, Any] = {
            "prefix": "AF",
            "next_crumb_id": 1,
            "next_trail_id": 1,
            "default_priority": "P2",
        }
        for int_val, expected in [(0, "P0"), (1, "P1"), (2, "P2"), (3, "P3"), (4, "P4")]:
            rec = {"id": f"BD-{int_val}", "issue_type": "task", "priority": int_val, "title": "T"}
            result = _convert_beads_record(rec, {}, config)
            assert result["priority"] == expected, f"expected {expected} for priority {int_val}"

    def test_convert_beads_unknown_priority_uses_default(self) -> None:
        """Unknown priority values fall back to config default_priority."""
        config: Dict[str, Any] = {
            "prefix": "AF",
            "next_crumb_id": 1,
            "next_trail_id": 1,
            "default_priority": "P3",
        }
        rec = {"id": "BD-9", "issue_type": "task", "priority": 99, "title": "T"}
        result = _convert_beads_record(rec, {}, config)
        assert result["priority"] == "P3"

    def test_convert_beads_string_priority_passthrough(self) -> None:
        """P-string priorities are passed through unchanged."""
        config: Dict[str, Any] = {
            "prefix": "AF",
            "next_crumb_id": 1,
            "next_trail_id": 1,
            "default_priority": "P2",
        }
        rec = {"id": "BD-9", "issue_type": "task", "priority": "P1", "title": "T"}
        result = _convert_beads_record(rec, {}, config)
        assert result["priority"] == "P1"

    def test_convert_beads_parent_child_dep_sets_links_parent(self) -> None:
        """parent-child dependency sets raw links.parent on the child record."""
        config: Dict[str, Any] = {
            "prefix": "AF",
            "next_crumb_id": 1,
            "next_trail_id": 1,
            "default_priority": "P2",
        }
        rec = {
            "id": "BD-3",
            "issue_type": "task",
            "title": "Child",
            "priority": 2,
            "dependencies": [
                {"type": "parent-child", "depends_on_id": "BD-10"}
            ],
        }
        result = _convert_beads_record(rec, {}, config)
        assert result.get("links", {}).get("parent") == "BD-10"

    def test_convert_beads_unknown_issue_type_falls_back_to_task(self) -> None:
        """Unrecognised issue_type values fall back to 'task'."""
        config: Dict[str, Any] = {
            "prefix": "AF",
            "next_crumb_id": 1,
            "next_trail_id": 1,
            "default_priority": "P2",
        }
        rec = {"id": "BD-7", "issue_type": "weird_type", "title": "W", "priority": 2}
        result = _convert_beads_record(rec, {}, config)
        assert result["type"] == "task"

    # --- _resolve_beads_epic_refs unit tests ---

    def test_resolve_beads_epic_refs_rewrites_parent(self) -> None:
        """_resolve_beads_epic_refs replaces the old Beads epic ID with the trail ID."""
        records = [
            {"id": "BD-3", "type": "task", "links": {"parent": "BD-10"}},
            {"id": "AF-T1", "type": "trail"},
        ]
        epic_id_map = {"BD-10": "AF-T1"}
        _resolve_beads_epic_refs(records, epic_id_map)
        assert records[0]["links"]["parent"] == "AF-T1"

    def test_resolve_beads_epic_refs_non_epic_parent_unchanged(self) -> None:
        """Parent IDs not in epic_id_map are left unchanged."""
        records = [{"id": "BD-3", "type": "task", "links": {"parent": "BD-5"}}]
        epic_id_map = {"BD-10": "AF-T1"}
        _resolve_beads_epic_refs(records, epic_id_map)
        assert records[0]["links"]["parent"] == "BD-5"

    def test_resolve_beads_epic_refs_rewrites_blocked_by(self) -> None:
        """_resolve_beads_epic_refs also rewrites epic IDs in blocked_by lists."""
        records = [
            {"id": "BD-4", "type": "task", "links": {"blocked_by": ["BD-10", "BD-20"]}}
        ]
        epic_id_map = {"BD-10": "AF-T1"}
        _resolve_beads_epic_refs(records, epic_id_map)
        blocked = records[0]["links"]["blocked_by"]
        assert "AF-T1" in blocked
        assert "BD-20" in blocked
        assert "BD-10" not in blocked

    def test_resolve_beads_epic_refs_skips_records_without_links(self) -> None:
        """Records without links are untouched and do not raise."""
        records = [{"id": "BD-3", "type": "task"}]
        _resolve_beads_epic_refs(records, {"BD-10": "AF-T1"})
        assert "links" not in records[0]

    # --- _apply_blocks_deps unit tests ---

    def test_apply_blocks_deps_adds_blocked_by_to_target(self) -> None:
        """A blocks-type dep adds the source's crumb ID to the target's blocked_by."""
        raw_beads = [
            {
                "id": "BD-1",
                "issue_type": "task",
                "dependencies": [{"type": "blocks", "depends_on_id": "BD-2"}],
            }
        ]
        records = [
            {"id": "BD-1", "type": "task"},
            {"id": "BD-2", "type": "task"},
        ]
        _apply_blocks_deps(raw_beads, records, {})
        target = next(r for r in records if r["id"] == "BD-2")
        assert "BD-1" in target["links"]["blocked_by"]

    def test_apply_blocks_deps_no_duplicates(self) -> None:
        """Duplicate block entries are not added twice to blocked_by."""
        raw_beads = [
            {
                "id": "BD-1",
                "issue_type": "task",
                "dependencies": [
                    {"type": "blocks", "depends_on_id": "BD-2"},
                    {"type": "blocks", "depends_on_id": "BD-2"},
                ],
            }
        ]
        records = [
            {"id": "BD-1", "type": "task"},
            {"id": "BD-2", "type": "task"},
        ]
        _apply_blocks_deps(raw_beads, records, {})
        target = next(r for r in records if r["id"] == "BD-2")
        assert target["links"]["blocked_by"].count("BD-1") == 1

    def test_apply_blocks_deps_translates_epic_ids(self) -> None:
        """Epic source IDs are translated via epic_id_map before being added."""
        raw_beads = [
            {
                "id": "BD-10",
                "issue_type": "epic",
                "dependencies": [{"type": "blocks", "depends_on_id": "BD-2"}],
            }
        ]
        records = [
            {"id": "AF-T1", "type": "trail"},
            {"id": "BD-2", "type": "task"},
        ]
        epic_id_map = {"BD-10": "AF-T1"}
        _apply_blocks_deps(raw_beads, records, epic_id_map)
        target = next(r for r in records if r["id"] == "BD-2")
        assert "AF-T1" in target["links"]["blocked_by"]

    def test_apply_blocks_deps_warns_missing_targets(self, capsys: pytest.CaptureFixture) -> None:
        """Block dependencies pointing to missing records emit a stderr warning."""
        raw_beads = [
            {
                "id": "BD-1",
                "issue_type": "task",
                "dependencies": [{"type": "blocks", "depends_on_id": "BD-GHOST"}],
            }
        ]
        records = [{"id": "BD-1", "type": "task"}]
        # Should not raise; missing target is skipped after warning
        _apply_blocks_deps(raw_beads, records, {})
        assert "links" not in records[0]
        captured = capsys.readouterr()
        assert "warning" in captured.err
        assert "BD-GHOST" in captured.err

    # --- cmd_import integration tests (--from-beads mode) ---

    def test_import_from_beads_converts_records(
        self, crumbs_env: Path, tmp_path: Path
    ) -> None:
        """cmd_import with --from-beads converts a Beads record to crumb format."""
        beads_file = tmp_path / "issues.jsonl"
        _write_jsonl(
            beads_file,
            [
                {
                    "id": "BD-1",
                    "issue_type": "task",
                    "title": "A task",
                    "status": "open",
                    "priority": 2,
                }
            ],
        )

        cmd_import(_make_import_args(str(beads_file), from_beads=True))

        tasks = read_tasks(crumbs_env / "tasks.jsonl")
        assert len(tasks) == 1
        assert tasks[0]["id"] == "BD-1"
        assert tasks[0]["priority"] == "P2"
        assert tasks[0]["type"] == "task"

    def test_import_from_beads_epic_becomes_trail_with_t_id(
        self, crumbs_env: Path, tmp_path: Path
    ) -> None:
        """Beads epics become trails with T-prefixed IDs in the crumb system."""
        beads_file = tmp_path / "issues.jsonl"
        _write_jsonl(
            beads_file,
            [
                {
                    "id": "BD-10",
                    "issue_type": "epic",
                    "title": "Epic One",
                    "status": "open",
                    "priority": 0,
                }
            ],
        )

        cmd_import(_make_import_args(str(beads_file), from_beads=True))

        tasks = read_tasks(crumbs_env / "tasks.jsonl")
        assert len(tasks) == 1
        trail = tasks[0]
        assert trail["type"] == "trail"
        assert trail["id"].startswith("AF-T")

    def test_import_from_beads_resolves_epic_refs_in_parent(
        self, crumbs_env: Path, tmp_path: Path
    ) -> None:
        """_resolve_beads_epic_refs is applied: child's links.parent becomes the trail ID."""
        beads_file = tmp_path / "issues.jsonl"
        _write_jsonl(
            beads_file,
            [
                {
                    "id": "BD-10",
                    "issue_type": "epic",
                    "title": "Epic",
                    "status": "open",
                    "priority": 1,
                },
                {
                    "id": "BD-3",
                    "issue_type": "task",
                    "title": "Child task",
                    "status": "open",
                    "priority": 2,
                    "dependencies": [{"type": "parent-child", "depends_on_id": "BD-10"}],
                },
            ],
        )

        cmd_import(_make_import_args(str(beads_file), from_beads=True))

        tasks = read_tasks(crumbs_env / "tasks.jsonl")
        child = next(t for t in tasks if t["id"] == "BD-3")
        trail = next(t for t in tasks if t["type"] == "trail")
        assert child["links"]["parent"] == trail["id"]

    def test_import_from_beads_applies_blocks_deps(
        self, crumbs_env: Path, tmp_path: Path
    ) -> None:
        """_apply_blocks_deps is applied: blocking record appears in blocked_by."""
        beads_file = tmp_path / "issues.jsonl"
        _write_jsonl(
            beads_file,
            [
                {
                    "id": "BD-1",
                    "issue_type": "task",
                    "title": "Blocker",
                    "status": "open",
                    "priority": 1,
                    "dependencies": [{"type": "blocks", "depends_on_id": "BD-2"}],
                },
                {
                    "id": "BD-2",
                    "issue_type": "task",
                    "title": "Blocked",
                    "status": "open",
                    "priority": 2,
                },
            ],
        )

        cmd_import(_make_import_args(str(beads_file), from_beads=True))

        tasks = read_tasks(crumbs_env / "tasks.jsonl")
        blocked = next(t for t in tasks if t["id"] == "BD-2")
        assert "BD-1" in blocked.get("links", {}).get("blocked_by", [])

    def test_import_from_beads_raises_system_exit_for_missing_file(
        self, crumbs_env: Path
    ) -> None:
        """cmd_import --from-beads raises SystemExit for a nonexistent file."""
        args = _make_import_args("/no/such/file.jsonl", from_beads=True)
        with pytest.raises(SystemExit):
            cmd_import(args)

    def test_import_from_beads_updates_trail_counter(
        self, crumbs_env: Path, tmp_path: Path
    ) -> None:
        """After importing a Beads epic, next_trail_id is advanced past the generated ID."""
        beads_file = tmp_path / "issues.jsonl"
        _write_jsonl(
            beads_file,
            [
                {
                    "id": "BD-10",
                    "issue_type": "epic",
                    "title": "Epic",
                    "status": "open",
                    "priority": 1,
                }
            ],
        )

        cmd_import(_make_import_args(str(beads_file), from_beads=True))

        config = read_config()
        # AF-T1 was generated; next_trail_id must be at least 2
        assert config["next_trail_id"] >= 2


# ---------------------------------------------------------------------------
# TestFromJsonNoop
# ---------------------------------------------------------------------------


def _make_update_args_import(**kwargs: Any) -> argparse.Namespace:
    """Return a minimal Namespace for cmd_update with sane defaults."""
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


class TestFromJsonNoop:
    """Tests verifying --from-json no-op behaviour when values are identical."""

    def test_from_json_identical_scalar_produces_no_changes(
        self, crumbs_env: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """--from-json with the same scalar value must not print 'updated'.

        When every field supplied via --from-json already matches the current
        value in the crumb record, cmd_update must report 'no changes' rather
        than 'updated <id>'.
        """
        # Seed a task with a known title and description.
        tasks_path = crumbs_env / "tasks.jsonl"
        record: Dict[str, Any] = {
            "id": "AF-1",
            "type": "task",
            "title": "Existing title",
            "description": "Existing description",
            "status": "open",
            "priority": "P2",
            "created_at": "2026-01-01T00:00:00Z",
            "updated_at": "2026-01-01T00:00:00Z",
        }
        tasks_path.write_text(json.dumps(record) + "\n", encoding="utf-8")

        # Pass identical values via --from-json.
        same_payload = json.dumps(
            {"title": "Existing title", "description": "Existing description"}
        )
        cmd_update(_make_update_args_import(id="AF-1", from_json=same_payload))

        captured = capsys.readouterr()
        assert "updated" not in captured.out, (
            "No-op --from-json must not produce 'updated' output"
        )
        assert "no changes" in captured.out

    def test_from_json_changed_scalar_produces_updated(
        self, crumbs_env: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """--from-json with an actually different value must print 'updated <id>'.

        This is the positive control: ensures that the changed-flag logic still
        fires when a field value genuinely differs from the stored record.
        """
        tasks_path = crumbs_env / "tasks.jsonl"
        record: Dict[str, Any] = {
            "id": "AF-1",
            "type": "task",
            "title": "Old title",
            "status": "open",
            "priority": "P2",
            "created_at": "2026-01-01T00:00:00Z",
            "updated_at": "2026-01-01T00:00:00Z",
        }
        tasks_path.write_text(json.dumps(record) + "\n", encoding="utf-8")

        new_payload = json.dumps({"title": "New title"})
        cmd_update(_make_update_args_import(id="AF-1", from_json=new_payload))

        captured = capsys.readouterr()
        assert "updated AF-1" in captured.out

    def test_from_json_identical_dict_subfield_produces_no_changes(
        self, crumbs_env: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """--from-json with an identical nested dict value must not print 'updated'.

        The dict-merge path in cmd_update must also guard against no-op writes
        when all incoming sub-keys already match the existing sub-values.
        """
        tasks_path = crumbs_env / "tasks.jsonl"
        record: Dict[str, Any] = {
            "id": "AF-1",
            "type": "task",
            "title": "Task",
            "status": "open",
            "priority": "P2",
            "scope": {"agent_type": "python-pro", "files": ["crumb.py"]},
            "created_at": "2026-01-01T00:00:00Z",
            "updated_at": "2026-01-01T00:00:00Z",
        }
        tasks_path.write_text(json.dumps(record) + "\n", encoding="utf-8")

        # Pass the same nested dict value — no real change.
        same_payload = json.dumps({"scope": {"agent_type": "python-pro"}})
        cmd_update(_make_update_args_import(id="AF-1", from_json=same_payload))

        captured = capsys.readouterr()
        assert "updated" not in captured.out, (
            "Identical nested-dict --from-json must not produce 'updated' output"
        )
        assert "no changes" in captured.out

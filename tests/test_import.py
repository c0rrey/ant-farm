"""Tests for the import command (plain JSONL import via cmd_import)."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List

import pytest

import crumb
from crumb import (
    cmd_import,
    cmd_update,
    read_tasks,
    read_config,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_import_args(file: str) -> argparse.Namespace:
    """Return a minimal Namespace that mimics what argparse produces for 'import'."""
    return argparse.Namespace(file=file)


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
# TestFromJsonNoop
# ---------------------------------------------------------------------------


def _make_update_args(**kwargs: Any) -> argparse.Namespace:
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
        cmd_update(_make_update_args(id="AF-1", from_json=same_payload))

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
        cmd_update(_make_update_args(id="AF-1", from_json=new_payload))

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
        cmd_update(_make_update_args(id="AF-1", from_json=same_payload))

        captured = capsys.readouterr()
        assert "updated" not in captured.out, (
            "Identical nested-dict --from-json must not produce 'updated' output"
        )
        assert "no changes" in captured.out

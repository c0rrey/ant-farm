"""Tests for the doctor command.

Covers:
  - TestDoctor: cmd_doctor — clean state, malformed JSONL, duplicate IDs,
    dangling blocked_by refs, dangling parent refs, and --fix repair mode.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List

import pytest

import crumb
from crumb import (
    cmd_doctor,
    read_tasks,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_doctor_args(fix: bool = False, json_output: bool = False) -> argparse.Namespace:
    """Return a minimal Namespace that mimics what argparse produces for 'doctor'.

    Args:
        fix: Whether to enable auto-repair mode.
        json_output: Whether to request JSON output mode.

    Returns:
        Namespace with ``fix`` and ``json_output`` set.
    """
    return argparse.Namespace(fix=fix, json_output=json_output)


def _write_tasks(crumbs_dir: Path, records: List[Dict[str, Any]]) -> None:
    """Write a list of dicts to the tasks.jsonl file in crumbs_dir."""
    tasks_file = crumbs_dir / "tasks.jsonl"
    with open(tasks_file, "w", encoding="utf-8") as fh:
        for rec in records:
            fh.write(json.dumps(rec) + "\n")


def _append_raw_line(crumbs_dir: Path, line: str) -> None:
    """Append a raw (possibly malformed) line to tasks.jsonl."""
    tasks_file = crumbs_dir / "tasks.jsonl"
    with open(tasks_file, "a", encoding="utf-8") as fh:
        fh.write(line + "\n")


# ---------------------------------------------------------------------------
# TestDoctor
# ---------------------------------------------------------------------------


class TestDoctor:
    """Tests for cmd_doctor validation and repair logic."""

    # --- Clean state ---

    def test_doctor_clean_state_prints_no_issues(
        self,
        crumbs_env: Path,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """cmd_doctor reports 'No issues found' when tasks.jsonl is valid."""
        trail_rec = {
            "id": "AF-T1",
            "type": "trail",
            "title": "My Trail",
            "status": "open",
            "priority": "P2",
        }
        child_rec = {
            "id": "AF-1",
            "type": "task",
            "title": "A task",
            "status": "open",
            "priority": "P2",
            "links": {"parent": "AF-T1"},
        }
        _write_tasks(crumbs_env, [trail_rec, child_rec])

        cmd_doctor(_make_doctor_args())

        captured = capsys.readouterr()
        assert "No issues found" in captured.out

    def test_doctor_clean_state_exits_zero(
        self,
        crumbs_env: Path,
    ) -> None:
        """cmd_doctor does not raise SystemExit when there are no errors."""
        _write_tasks(crumbs_env, [
            {"id": "AF-T1", "type": "trail", "title": "T", "status": "open", "priority": "P2"},
        ])
        # Should not raise
        cmd_doctor(_make_doctor_args())

    # --- Malformed JSONL ---

    def test_doctor_detects_malformed_json(
        self,
        crumbs_env: Path,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """cmd_doctor reports an error for malformed JSON lines."""
        _write_tasks(crumbs_env, [
            {"id": "AF-T1", "type": "trail", "title": "T", "status": "open", "priority": "P2"},
        ])
        _append_raw_line(crumbs_env, "NOT VALID JSON <<<")

        with pytest.raises(SystemExit) as exc_info:
            cmd_doctor(_make_doctor_args())

        assert exc_info.value.code == 1
        captured = capsys.readouterr()
        assert "malformed" in captured.err.lower()

    def test_doctor_malformed_json_includes_line_number(
        self,
        crumbs_env: Path,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """The malformed JSON error message includes the offending line number."""
        # Write a fresh tasks.jsonl: valid on line 1, malformed on line 2
        tasks_file = crumbs_env / "tasks.jsonl"
        tasks_file.write_text(
            json.dumps({"id": "AF-T1", "type": "trail", "title": "T", "status": "open", "priority": "P2"})
            + "\n"
            + "{{BROKEN}}\n",
            encoding="utf-8",
        )

        with pytest.raises(SystemExit):
            cmd_doctor(_make_doctor_args())

        captured = capsys.readouterr()
        assert "line 2" in captured.err

    # --- Duplicate IDs ---

    def test_doctor_detects_duplicate_ids(
        self,
        crumbs_env: Path,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """cmd_doctor reports an error when two records share the same ID."""
        _write_tasks(crumbs_env, [
            {"id": "AF-1", "type": "task", "title": "One", "status": "open", "priority": "P2"},
            {"id": "AF-1", "type": "task", "title": "Duplicate", "status": "open", "priority": "P2"},
        ])

        with pytest.raises(SystemExit) as exc_info:
            cmd_doctor(_make_doctor_args())

        assert exc_info.value.code == 1
        captured = capsys.readouterr()
        assert "duplicate" in captured.err.lower()
        assert "AF-1" in captured.err

    # --- Dangling blocked_by references ---

    def test_doctor_detects_dangling_blocked_by(
        self,
        crumbs_env: Path,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """cmd_doctor warns about blocked_by entries pointing to non-existent IDs."""
        _write_tasks(crumbs_env, [
            {
                "id": "AF-1",
                "type": "task",
                "title": "Blocked",
                "status": "open",
                "priority": "P2",
                "links": {"blocked_by": ["AF-GHOST"]},
            },
        ])

        # Dangling blocked_by is a warning, not an error — should not raise SystemExit
        cmd_doctor(_make_doctor_args())

        captured = capsys.readouterr()
        assert "dangling" in captured.err.lower()
        assert "AF-GHOST" in captured.err

    def test_doctor_dangling_blocked_by_does_not_exit_1(
        self,
        crumbs_env: Path,
    ) -> None:
        """Dangling blocked_by references are warnings only — exit code remains 0."""
        _write_tasks(crumbs_env, [
            {
                "id": "AF-1",
                "type": "task",
                "title": "T",
                "status": "open",
                "priority": "P2",
                "links": {"blocked_by": ["AF-GONE"]},
            },
        ])
        # Should not raise
        cmd_doctor(_make_doctor_args())

    # --- Dangling parent references ---

    def test_doctor_detects_dangling_parent_ref(
        self,
        crumbs_env: Path,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """cmd_doctor reports an error for a links.parent pointing to a non-existent ID."""
        _write_tasks(crumbs_env, [
            {
                "id": "AF-1",
                "type": "task",
                "title": "Orphaned",
                "status": "open",
                "priority": "P2",
                "links": {"parent": "AF-T999"},
            },
        ])

        with pytest.raises(SystemExit) as exc_info:
            cmd_doctor(_make_doctor_args())

        assert exc_info.value.code == 1
        captured = capsys.readouterr()
        assert "dangling" in captured.err.lower()
        assert "AF-T999" in captured.err

    def test_doctor_detects_parent_pointing_to_non_trail(
        self,
        crumbs_env: Path,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """cmd_doctor errors when links.parent points to an ID that exists but is not a trail."""
        _write_tasks(crumbs_env, [
            {"id": "AF-1", "type": "task", "title": "Parent", "status": "open", "priority": "P2"},
            {
                "id": "AF-2",
                "type": "task",
                "title": "Bad Child",
                "status": "open",
                "priority": "P2",
                "links": {"parent": "AF-1"},
            },
        ])

        with pytest.raises(SystemExit) as exc_info:
            cmd_doctor(_make_doctor_args())

        assert exc_info.value.code == 1
        captured = capsys.readouterr()
        assert "is not a trail" in captured.err.lower()

    # --- --fix repair mode ---

    def test_doctor_fix_removes_dangling_blocked_by(
        self,
        crumbs_env: Path,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """cmd_doctor --fix removes dangling blocked_by entries and rewrites tasks.jsonl."""
        _write_tasks(crumbs_env, [
            {
                "id": "AF-1",
                "type": "task",
                "title": "Has dangling blocker",
                "status": "open",
                "priority": "P2",
                "links": {"blocked_by": ["AF-GHOST", "AF-ALSO-GONE"]},
            },
        ])

        cmd_doctor(_make_doctor_args(fix=True))

        # Verify tasks.jsonl was rewritten without the dangling entries
        tasks = read_tasks(crumbs_env / "tasks.jsonl")
        task = tasks[0]
        blocked_by = task.get("links", {}).get("blocked_by", [])
        assert "AF-GHOST" not in blocked_by
        assert "AF-ALSO-GONE" not in blocked_by

    def test_doctor_fix_keeps_valid_blocked_by(
        self,
        crumbs_env: Path,
    ) -> None:
        """cmd_doctor --fix does not remove blocked_by entries that point to real records."""
        _write_tasks(crumbs_env, [
            {"id": "AF-2", "type": "task", "title": "Real Blocker", "status": "open", "priority": "P2"},
            {
                "id": "AF-1",
                "type": "task",
                "title": "Blocked",
                "status": "open",
                "priority": "P2",
                "links": {"blocked_by": ["AF-2", "AF-GHOST"]},
            },
        ])

        cmd_doctor(_make_doctor_args(fix=True))

        tasks = read_tasks(crumbs_env / "tasks.jsonl")
        task = next(t for t in tasks if t["id"] == "AF-1")
        blocked_by = task.get("links", {}).get("blocked_by", [])
        assert "AF-2" in blocked_by
        assert "AF-GHOST" not in blocked_by

    def test_doctor_fix_prints_fix_confirmation(
        self,
        crumbs_env: Path,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """cmd_doctor --fix prints a 'fixed:' message for each repair applied."""
        _write_tasks(crumbs_env, [
            {
                "id": "AF-1",
                "type": "task",
                "title": "T",
                "status": "open",
                "priority": "P2",
                "links": {"blocked_by": ["AF-PHANTOM"]},
            },
        ])

        cmd_doctor(_make_doctor_args(fix=True))

        captured = capsys.readouterr()
        assert "fixed" in captured.out.lower()

    def test_doctor_fix_no_changes_when_clean(
        self,
        crumbs_env: Path,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """cmd_doctor --fix on a clean file does not modify tasks.jsonl."""
        trail_rec = {
            "id": "AF-T1",
            "type": "trail",
            "title": "Trail",
            "status": "open",
            "priority": "P2",
        }
        _write_tasks(crumbs_env, [trail_rec])
        tasks_file = crumbs_env / "tasks.jsonl"
        original_content = tasks_file.read_text(encoding="utf-8")

        cmd_doctor(_make_doctor_args(fix=True))

        assert tasks_file.read_text(encoding="utf-8") == original_content

    def test_doctor_orphan_crumb_produces_warning(
        self,
        crumbs_env: Path,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """A non-trail crumb with no parent emits a warning (not an error)."""
        _write_tasks(crumbs_env, [
            {"id": "AF-1", "type": "task", "title": "Orphan", "status": "open", "priority": "P2"},
        ])

        # Orphan warning does not cause SystemExit
        cmd_doctor(_make_doctor_args())

        captured = capsys.readouterr()
        assert "orphan" in captured.err.lower()

    def test_doctor_fix_warns_about_malformed_lines_removed(
        self,
        crumbs_env: Path,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """--fix with co-occurring malformed lines AND dangling refs prints a stderr warning."""
        _write_tasks(crumbs_env, [
            {
                "id": "AF-1",
                "type": "task",
                "title": "Has dangling blocker",
                "status": "open",
                "priority": "P2",
                "links": {"blocked_by": ["AF-GHOST"]},
            },
        ])
        # Append a malformed line so both conditions co-occur
        _append_raw_line(crumbs_env, "this is not valid json{{{")

        # Malformed lines produce an error, so cmd_doctor exits 1 — that's expected
        with pytest.raises(SystemExit):
            cmd_doctor(_make_doctor_args(fix=True))

        captured = capsys.readouterr()
        # Fix confirmation goes to stdout
        assert "fixed" in captured.out.lower()
        # Malformed-line warning goes to stderr
        assert "malformed" in captured.err.lower()
        assert "removed" in captured.err.lower()

    # --- --json output mode ---

    def test_doctor_json_clean_state_returns_ok_true(
        self,
        crumbs_env: Path,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """cmd_doctor --json on a clean file prints a JSON object with ok=true."""
        _write_tasks(crumbs_env, [
            {"id": "AF-T1", "type": "trail", "title": "T", "status": "open", "priority": "P2"},
        ])

        cmd_doctor(_make_doctor_args(json_output=True))

        captured = capsys.readouterr()
        parsed = json.loads(captured.out)
        assert isinstance(parsed, dict), "Expected a JSON object"
        assert parsed["ok"] is True

    def test_doctor_json_output_contains_required_fields(
        self,
        crumbs_env: Path,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """cmd_doctor --json output contains all required schema fields."""
        _write_tasks(crumbs_env, [
            {"id": "AF-T1", "type": "trail", "title": "T", "status": "open", "priority": "P2"},
        ])

        cmd_doctor(_make_doctor_args(json_output=True))

        captured = capsys.readouterr()
        parsed = json.loads(captured.out)
        for field in ("ok", "error_count", "warning_count", "errors", "warnings", "fixes_applied"):
            assert field in parsed, f"Required field '{field}' missing from doctor --json output"

    def test_doctor_json_with_errors_ok_false_and_exits_1(
        self,
        crumbs_env: Path,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """cmd_doctor --json with errors sets ok=false and exits 1."""
        _write_tasks(crumbs_env, [
            {"id": "AF-1", "type": "task", "title": "One", "status": "open", "priority": "P2"},
            {"id": "AF-1", "type": "task", "title": "Duplicate", "status": "open", "priority": "P2"},
        ])

        with pytest.raises(SystemExit) as exc_info:
            cmd_doctor(_make_doctor_args(json_output=True))

        assert exc_info.value.code == 1
        captured = capsys.readouterr()
        parsed = json.loads(captured.out)
        assert parsed["ok"] is False
        assert parsed["error_count"] > 0
        assert len(parsed["errors"]) > 0

    def test_doctor_json_with_warnings_ok_true(
        self,
        crumbs_env: Path,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """cmd_doctor --json with warnings-only sets ok=true (warnings don't set exit 1)."""
        _write_tasks(crumbs_env, [
            {"id": "AF-1", "type": "task", "title": "Orphan", "status": "open", "priority": "P2"},
        ])

        # Orphan crumb produces a warning, not an error — should not raise SystemExit
        cmd_doctor(_make_doctor_args(json_output=True))

        captured = capsys.readouterr()
        parsed = json.loads(captured.out)
        assert parsed["ok"] is True
        assert parsed["warning_count"] > 0
        assert len(parsed["warnings"]) > 0

    def test_doctor_json_no_stderr_output(
        self,
        crumbs_env: Path,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """cmd_doctor --json does not write error/warning messages to stderr."""
        _write_tasks(crumbs_env, [
            {"id": "AF-1", "type": "task", "title": "Orphan", "status": "open", "priority": "P2"},
        ])

        cmd_doctor(_make_doctor_args(json_output=True))

        captured = capsys.readouterr()
        assert captured.err == "", "Expected no stderr output when --json is given"

    def test_doctor_without_json_still_human_readable(
        self,
        crumbs_env: Path,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """cmd_doctor without --json still prints human-readable output unchanged."""
        _write_tasks(crumbs_env, [
            {"id": "AF-T1", "type": "trail", "title": "T", "status": "open", "priority": "P2"},
        ])

        cmd_doctor(_make_doctor_args(json_output=False))

        captured = capsys.readouterr()
        assert "No issues found" in captured.out
        assert not captured.out.startswith("{"), "Output must not be JSON when --json absent"

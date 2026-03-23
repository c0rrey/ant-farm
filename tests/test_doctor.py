"""Tests for the doctor command.

Covers:
  - TestDoctor: cmd_doctor — clean state, malformed JSONL, duplicate IDs,
    dangling blocked_by refs, dangling parent refs, and --fix repair mode.
  - TestDoctorCycles: cycle detection — A->B->C->A chains, self-referential
    cycles, disconnected subgraphs, cycle-free regression, and --json output.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List

import time

import pytest

import crumb
from crumb import (
    cmd_doctor,
    read_tasks,
    _detect_cycles,
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


# ---------------------------------------------------------------------------
# TestDoctorCycles
# ---------------------------------------------------------------------------


def _make_task(task_id: str, blocked_by: List[str] | None = None) -> Dict[str, Any]:
    """Build a minimal task record, optionally with blocked_by set in links.

    Args:
        task_id: The crumb ID string.
        blocked_by: Optional list of crumb IDs this task is blocked by.

    Returns:
        A task record dict suitable for use in tasks.jsonl.
    """
    rec: Dict[str, Any] = {
        "id": task_id,
        "type": "task",
        "title": f"Task {task_id}",
        "status": "open",
        "priority": "P2",
    }
    if blocked_by is not None:
        rec["links"] = {"blocked_by": blocked_by}
    return rec


class TestDoctorCycles:
    """Tests for cycle detection in cmd_doctor and _detect_cycles."""

    # --- Unit tests on _detect_cycles directly ---

    def test_detect_cycles_empty_graph(self) -> None:
        """_detect_cycles returns an empty list for an empty graph."""
        assert _detect_cycles({}) == []

    def test_detect_cycles_no_cycle_linear_chain(self) -> None:
        """_detect_cycles returns [] when A->B->C has no cycle."""
        records = {
            "AF-1": _make_task("AF-1", blocked_by=["AF-2"]),
            "AF-2": _make_task("AF-2", blocked_by=["AF-3"]),
            "AF-3": _make_task("AF-3"),
        }
        assert _detect_cycles(records) == []

    def test_detect_cycles_self_referential(self) -> None:
        """_detect_cycles detects A blocked_by A as a self-referential cycle."""
        records = {"AF-1": _make_task("AF-1", blocked_by=["AF-1"])}
        cycles = _detect_cycles(records)
        assert len(cycles) == 1
        assert cycles[0] == ["AF-1", "AF-1"]

    def test_detect_cycles_two_node_cycle(self) -> None:
        """_detect_cycles detects A <-> B mutual dependency."""
        records = {
            "AF-1": _make_task("AF-1", blocked_by=["AF-2"]),
            "AF-2": _make_task("AF-2", blocked_by=["AF-1"]),
        }
        cycles = _detect_cycles(records)
        assert len(cycles) >= 1
        # Verify the cycle contains both nodes
        all_ids = {node for cycle in cycles for node in cycle}
        assert "AF-1" in all_ids
        assert "AF-2" in all_ids

    def test_detect_cycles_three_node_cycle(self) -> None:
        """_detect_cycles detects A->B->C->A circular chain."""
        records = {
            "AF-1": _make_task("AF-1", blocked_by=["AF-3"]),
            "AF-2": _make_task("AF-2", blocked_by=["AF-1"]),
            "AF-3": _make_task("AF-3", blocked_by=["AF-2"]),
        }
        cycles = _detect_cycles(records)
        assert len(cycles) >= 1
        all_ids = {node for cycle in cycles for node in cycle}
        assert "AF-1" in all_ids
        assert "AF-2" in all_ids
        assert "AF-3" in all_ids

    def test_detect_cycles_closed_path_format(self) -> None:
        """Each cycle path closes the loop: last element equals first element."""
        records = {
            "AF-1": _make_task("AF-1", blocked_by=["AF-2"]),
            "AF-2": _make_task("AF-2", blocked_by=["AF-1"]),
        }
        cycles = _detect_cycles(records)
        assert len(cycles) >= 1
        for cycle in cycles:
            assert len(cycle) >= 2, "Cycle path must have at least 2 elements"
            assert cycle[0] == cycle[-1], "Cycle path must close: first == last"

    def test_detect_cycles_disconnected_subgraphs(self) -> None:
        """_detect_cycles finds cycles in disconnected components independently."""
        # Component 1: A->B->A (cycle)
        # Component 2: C->D->C (cycle)
        # Component 3: E->F (no cycle)
        records = {
            "AF-1": _make_task("AF-1", blocked_by=["AF-2"]),
            "AF-2": _make_task("AF-2", blocked_by=["AF-1"]),
            "AF-3": _make_task("AF-3", blocked_by=["AF-4"]),
            "AF-4": _make_task("AF-4", blocked_by=["AF-3"]),
            "AF-5": _make_task("AF-5", blocked_by=["AF-6"]),
            "AF-6": _make_task("AF-6"),
        }
        cycles = _detect_cycles(records)
        assert len(cycles) >= 2
        all_ids = {node for cycle in cycles for node in cycle}
        assert "AF-1" in all_ids or "AF-2" in all_ids
        assert "AF-3" in all_ids or "AF-4" in all_ids
        # No cycle in E/F components
        cycle_ids_flat = [node for cycle in cycles for node in cycle]
        assert "AF-5" not in cycle_ids_flat
        assert "AF-6" not in cycle_ids_flat

    def test_detect_cycles_ignores_dangling_refs(self) -> None:
        """_detect_cycles only considers blockers that exist in id_to_record."""
        # AF-1 is blocked by AF-GHOST which doesn't exist — not a cycle
        records = {"AF-1": _make_task("AF-1", blocked_by=["AF-GHOST"])}
        cycles = _detect_cycles(records)
        assert cycles == []

    # --- Integration tests through cmd_doctor ---

    def test_doctor_detects_three_node_cycle(
        self,
        crumbs_env: Path,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """cmd_doctor reports FAIL with cycle path for A->B->C->A chain."""
        _write_tasks(crumbs_env, [
            _make_task("AF-1", blocked_by=["AF-3"]),
            _make_task("AF-2", blocked_by=["AF-1"]),
            _make_task("AF-3", blocked_by=["AF-2"]),
        ])

        with pytest.raises(SystemExit) as exc_info:
            cmd_doctor(_make_doctor_args())

        assert exc_info.value.code == 1
        captured = capsys.readouterr()
        assert "cycle" in captured.err.lower()

    def test_doctor_cycle_error_message_contains_arrow_path(
        self,
        crumbs_env: Path,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """The cycle error message contains ' -> ' separating node IDs."""
        _write_tasks(crumbs_env, [
            _make_task("AF-1", blocked_by=["AF-2"]),
            _make_task("AF-2", blocked_by=["AF-1"]),
        ])

        with pytest.raises(SystemExit):
            cmd_doctor(_make_doctor_args())

        captured = capsys.readouterr()
        assert " -> " in captured.err

    def test_doctor_self_referential_cycle_detected(
        self,
        crumbs_env: Path,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """cmd_doctor reports FAIL when a crumb is blocked_by itself."""
        _write_tasks(crumbs_env, [
            _make_task("AF-1", blocked_by=["AF-1"]),
        ])

        with pytest.raises(SystemExit) as exc_info:
            cmd_doctor(_make_doctor_args())

        assert exc_info.value.code == 1
        captured = capsys.readouterr()
        assert "cycle" in captured.err.lower()
        assert "AF-1" in captured.err

    def test_doctor_cycle_free_file_reports_no_cycle_errors(
        self,
        crumbs_env: Path,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """cmd_doctor on a cycle-free JSONL does not produce cycle errors (regression)."""
        _write_tasks(crumbs_env, [
            {"id": "AF-T1", "type": "trail", "title": "Trail", "status": "open", "priority": "P2"},
            {
                "id": "AF-1",
                "type": "task",
                "title": "A",
                "status": "open",
                "priority": "P2",
                "links": {"parent": "AF-T1", "blocked_by": ["AF-2"]},
            },
            {
                "id": "AF-2",
                "type": "task",
                "title": "B",
                "status": "open",
                "priority": "P2",
                "links": {"parent": "AF-T1"},
            },
        ])

        cmd_doctor(_make_doctor_args())

        captured = capsys.readouterr()
        assert "cycle" not in captured.err.lower()
        assert "No issues found" in captured.out

    def test_doctor_json_output_includes_cycles_field(
        self,
        crumbs_env: Path,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """cmd_doctor --json output includes a 'cycles' array field."""
        _write_tasks(crumbs_env, [
            {"id": "AF-T1", "type": "trail", "title": "T", "status": "open", "priority": "P2"},
        ])

        cmd_doctor(_make_doctor_args(json_output=True))

        captured = capsys.readouterr()
        parsed = json.loads(captured.out)
        assert "cycles" in parsed, "JSON output must include 'cycles' field"
        assert isinstance(parsed["cycles"], list)

    def test_doctor_json_cycles_empty_when_no_cycles(
        self,
        crumbs_env: Path,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """cmd_doctor --json 'cycles' is empty list when no cycles exist."""
        _write_tasks(crumbs_env, [
            {"id": "AF-T1", "type": "trail", "title": "T", "status": "open", "priority": "P2"},
        ])

        cmd_doctor(_make_doctor_args(json_output=True))

        captured = capsys.readouterr()
        parsed = json.loads(captured.out)
        assert parsed["cycles"] == []

    def test_doctor_json_cycles_populated_when_cycle_exists(
        self,
        crumbs_env: Path,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """cmd_doctor --json 'cycles' contains ordered ID paths when cycles exist."""
        _write_tasks(crumbs_env, [
            _make_task("AF-1", blocked_by=["AF-2"]),
            _make_task("AF-2", blocked_by=["AF-1"]),
        ])

        with pytest.raises(SystemExit):
            cmd_doctor(_make_doctor_args(json_output=True))

        captured = capsys.readouterr()
        parsed = json.loads(captured.out)
        assert "cycles" in parsed
        assert len(parsed["cycles"]) >= 1
        cycle = parsed["cycles"][0]
        assert isinstance(cycle, list)
        assert len(cycle) >= 2
        # The cycle must close: first == last
        assert cycle[0] == cycle[-1]

    def test_doctor_json_cycle_ids_are_ordered(
        self,
        crumbs_env: Path,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """cmd_doctor --json cycle entries are ordered lists of IDs (strings)."""
        _write_tasks(crumbs_env, [
            _make_task("AF-1", blocked_by=["AF-2"]),
            _make_task("AF-2", blocked_by=["AF-1"]),
        ])

        with pytest.raises(SystemExit):
            cmd_doctor(_make_doctor_args(json_output=True))

        captured = capsys.readouterr()
        parsed = json.loads(captured.out)
        for cycle in parsed["cycles"]:
            assert all(isinstance(node, str) for node in cycle), \
                "All cycle node IDs must be strings"

    def test_doctor_cycle_with_disconnected_subgraphs(
        self,
        crumbs_env: Path,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """cmd_doctor detects a cycle in one component while another is cycle-free."""
        _write_tasks(crumbs_env, [
            # Cycle component
            _make_task("AF-1", blocked_by=["AF-2"]),
            _make_task("AF-2", blocked_by=["AF-1"]),
            # Acyclic component
            _make_task("AF-3", blocked_by=["AF-4"]),
            _make_task("AF-4"),
        ])

        with pytest.raises(SystemExit) as exc_info:
            cmd_doctor(_make_doctor_args())

        assert exc_info.value.code == 1
        captured = capsys.readouterr()
        assert "cycle" in captured.err.lower()

    def test_doctor_performance_500_crumbs(
        self,
        crumbs_env: Path,
    ) -> None:
        """cmd_doctor completes in <1s for 500 crumbs with 3+ distinct cycles.

        Graph topology (500 tasks total):
          - 300 tasks in a long acyclic chain (AF-1 -> AF-2 -> ... -> AF-300)
          - Cycle 1 (3-node):  AF-301 -> AF-302 -> AF-303 -> AF-301
          - Cycle 2 (5-node):  AF-304 -> AF-305 -> AF-306 -> AF-307 -> AF-308 -> AF-304
          - Cycle 3 (10-node): AF-309 -> AF-310 -> ... -> AF-318 -> AF-309
          - Self-referential cycle: AF-319 blocked_by itself
          - AF-320 through AF-500: isolated tasks with no dependencies
        """
        records: List[Dict[str, Any]] = []

        # 300-node acyclic chain
        for i in range(1, 301):
            blocked: List[str] = [f"AF-{i + 1}"] if i < 300 else []
            records.append(_make_task(f"AF-{i}", blocked_by=blocked))

        # Cycle 1: 3-node ring
        for node, nxt in [(301, 302), (302, 303), (303, 301)]:
            records.append(_make_task(f"AF-{node}", blocked_by=[f"AF-{nxt}"]))

        # Cycle 2: 5-node ring
        cycle2 = [304, 305, 306, 307, 308]
        for idx, node in enumerate(cycle2):
            nxt = cycle2[(idx + 1) % len(cycle2)]
            records.append(_make_task(f"AF-{node}", blocked_by=[f"AF-{nxt}"]))

        # Cycle 3: 10-node ring
        cycle3 = list(range(309, 319))
        for idx, node in enumerate(cycle3):
            nxt = cycle3[(idx + 1) % len(cycle3)]
            records.append(_make_task(f"AF-{node}", blocked_by=[f"AF-{nxt}"]))

        # Self-referential cycle
        records.append(_make_task("AF-319", blocked_by=["AF-319"]))

        # Isolated tasks to reach 500 total
        for i in range(320, 501):
            records.append(_make_task(f"AF-{i}"))

        _write_tasks(crumbs_env, records)

        start = time.perf_counter()
        with pytest.raises(SystemExit):
            cmd_doctor(_make_doctor_args())
        elapsed = time.perf_counter() - start

        assert elapsed < 1.0, f"cmd_doctor took {elapsed:.3f}s on 500 crumbs — must be <1s"

    def test_detect_cycles_empty_jsonl_no_cycle_errors(
        self,
        crumbs_env: Path,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """cmd_doctor on an empty JSONL file reports no cycle errors.

        An empty tasks.jsonl contains no records, so _detect_cycles receives an
        empty id_to_record mapping and must return an empty list.
        """
        # crumbs_env starts with an empty tasks.jsonl — no writes needed
        cmd_doctor(_make_doctor_args())

        captured = capsys.readouterr()
        assert "cycle" not in captured.err.lower(), (
            "Empty JSONL must not produce any cycle errors"
        )
        assert "cycle" not in captured.out.lower()

    def test_detect_cycles_diamond_not_falsely_reported(
        self,
        crumbs_env: Path,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """Diamond dependency (A->B, A->C, B->D, C->D) is NOT reported as a cycle.

        A diamond is a valid DAG pattern: D is a common dependency of B and C,
        both of which are dependencies of A. There is no directed cycle here.
        """
        records = [
            _make_task("AF-A", blocked_by=["AF-B", "AF-C"]),
            _make_task("AF-B", blocked_by=["AF-D"]),
            _make_task("AF-C", blocked_by=["AF-D"]),
            _make_task("AF-D"),
        ]
        _write_tasks(crumbs_env, records)

        # Diamond is cycle-free — must not raise SystemExit from a cycle error.
        # (It may still exit 1 for orphan warnings, so we just verify no cycle output.)
        try:
            cmd_doctor(_make_doctor_args())
        except SystemExit:
            pass

        captured = capsys.readouterr()
        assert "cycle" not in captured.err.lower(), (
            "Diamond dependency pattern must not be falsely reported as a cycle"
        )

    def test_detect_cycles_200_crumb_chain_is_cycle_free(
        self,
        crumbs_env: Path,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """A 200-crumb linear chain without any back-edges is correctly cycle-free.

        Builds: AF-1 -> AF-2 -> ... -> AF-200 (each blocked by the next,
        no wrap-around). _detect_cycles must return an empty list.
        """
        records: List[Dict[str, Any]] = [
            _make_task(f"AF-{i}", blocked_by=[f"AF-{i + 1}"] if i < 200 else [])
            for i in range(1, 201)
        ]
        _write_tasks(crumbs_env, records)

        # May exit 1 due to orphan warnings (no parent trail), but must not
        # report any cycles.
        try:
            cmd_doctor(_make_doctor_args())
        except SystemExit:
            pass

        captured = capsys.readouterr()
        assert "cycle" not in captured.err.lower(), (
            "200-crumb linear chain must not be reported as cyclic"
        )

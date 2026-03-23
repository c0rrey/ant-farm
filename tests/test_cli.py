"""Integration tests for the crumb.py CLI via subprocess execution.

Each test in ``TestCLIIntegration`` invokes ``crumb.py`` as a real subprocess,
capturing stdout, stderr, and the process exit code.  A temporary directory
containing an isolated ``.crumbs/`` environment is used for every test so that
no test ever touches the real ``.crumbs/`` on disk.

Isolation strategy:
    ``crumb.py`` discovers its data directory by walking up from ``cwd`` (like
    git finds ``.git/``).  Setting ``cwd`` to a ``tmp_path`` that contains its
    own ``.crumbs/`` directory is therefore sufficient — no environment
    variable patching or monkeypatching of ``crumb`` internals is required.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import List

import pytest

from crumb import DEFAULT_CONFIG, SESSION_TS_FORMAT


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

CRUMB_PY: Path = Path(__file__).resolve().parent.parent / "crumb.py"


def _make_crumbs_env(base: Path) -> Path:
    """Create an isolated .crumbs/ directory under *base* and return its path.

    Sets up:
    - ``base/.crumbs/`` directory
    - ``config.json`` with default values
    - ``tasks.jsonl`` as an empty file

    Args:
        base: Directory that will serve as the working directory for
              subprocess calls.  ``crumb.py`` will find ``.crumbs/``
              here because it walks up from cwd.

    Returns:
        Path to the newly created ``.crumbs/`` directory.
    """
    crumbs_dir: Path = base / ".crumbs"
    crumbs_dir.mkdir(parents=True, exist_ok=True)

    config_file = crumbs_dir / "config.json"
    config_file.write_text(
        json.dumps(DEFAULT_CONFIG, indent=2) + "\n", encoding="utf-8"
    )

    tasks_file = crumbs_dir / "tasks.jsonl"
    tasks_file.write_text("", encoding="utf-8")

    return crumbs_dir


def _run(args: List[str], cwd: Path) -> subprocess.CompletedProcess:
    """Run ``crumb.py`` as a subprocess and return the completed process.

    Args:
        args: Arguments passed to ``crumb.py`` (not including the script path).
        cwd: Working directory for the subprocess.  Must contain a
             ``.crumbs/`` directory so that ``crumb.py`` can find it.

    Returns:
        ``subprocess.CompletedProcess`` with ``stdout`` and ``stderr``
        captured as strings and ``returncode`` set.
    """
    return subprocess.run(
        [sys.executable, str(CRUMB_PY), *args],
        capture_output=True,
        text=True,
        cwd=str(cwd),
    )


# ---------------------------------------------------------------------------
# Test class
# ---------------------------------------------------------------------------


class TestCLIIntegration:
    """End-to-end integration tests for the crumb.py CLI.

    Each test method:
    1. Receives a fresh ``tmp_path`` from pytest (function-scoped).
    2. Sets up an isolated ``.crumbs/`` environment via ``_make_crumbs_env``.
    3. Invokes ``crumb.py`` via ``subprocess.run`` with ``cwd=tmp_path``.
    4. Asserts on exit code, stdout, and/or stderr.
    """

    def test_create_exits_zero_and_prints_id(self, tmp_path: Path) -> None:
        """``crumb create --title Test`` exits 0 and prints a crumb ID to stdout.

        Acceptance criterion 2: subprocess produces exit code 0 and prints
        the new crumb ID.
        """
        _make_crumbs_env(tmp_path)

        result = _run(["create", "--title", "Test"], cwd=tmp_path)

        assert result.returncode == 0, (
            f"Expected exit code 0, got {result.returncode}.\n"
            f"stdout: {result.stdout!r}\nstderr: {result.stderr!r}"
        )
        # crumb.py prints the assigned ID (e.g. "AF-1") to stdout
        assert result.stdout.strip(), (
            "Expected non-empty stdout containing the new crumb ID, got nothing."
        )

    def test_list_exits_zero(self, tmp_path: Path) -> None:
        """``crumb list`` exits 0 on an empty task store.

        Acceptance criterion 3: subprocess produces exit code 0.
        """
        _make_crumbs_env(tmp_path)

        result = _run(["list"], cwd=tmp_path)

        assert result.returncode == 0, (
            f"Expected exit code 0, got {result.returncode}.\n"
            f"stdout: {result.stdout!r}\nstderr: {result.stderr!r}"
        )

    def test_show_nonexistent_exits_nonzero_with_stderr(
        self, tmp_path: Path
    ) -> None:
        """``crumb show NONEXISTENT`` exits nonzero and writes an error to stderr.

        Acceptance criterion 4: nonzero exit code and an error message on stderr.
        """
        _make_crumbs_env(tmp_path)

        result = _run(["show", "NONEXISTENT"], cwd=tmp_path)

        assert result.returncode != 0, (
            f"Expected nonzero exit code for missing crumb, got {result.returncode}.\n"
            f"stdout: {result.stdout!r}\nstderr: {result.stderr!r}"
        )
        assert result.stderr.strip(), (
            "Expected an error message on stderr, got nothing."
        )

    def test_help_exits_zero_and_contains_usage(self, tmp_path: Path) -> None:
        """``crumb --help`` exits 0 and output contains 'usage:'.

        Acceptance criterion 5: exit code 0 and 'usage:' in output.

        Note: argparse writes --help output to stdout and exits 0.  The
        check is case-insensitive to accommodate both ``Usage:`` and
        ``usage:`` variants that different Python/argparse versions emit.
        """
        _make_crumbs_env(tmp_path)

        result = _run(["--help"], cwd=tmp_path)

        assert result.returncode == 0, (
            f"Expected exit code 0 for --help, got {result.returncode}.\n"
            f"stdout: {result.stdout!r}\nstderr: {result.stderr!r}"
        )
        combined_output = (result.stdout + result.stderr).lower()
        assert "usage:" in combined_output, (
            f"Expected 'usage:' in help output.\n"
            f"stdout: {result.stdout!r}\nstderr: {result.stderr!r}"
        )

    def test_isolation_does_not_affect_real_crumbs(self, tmp_path: Path) -> None:
        """Verify that create/list operations only touch the temp directory.

        Acceptance criterion 6: tests use a temporary .crumbs/ directory
        to avoid touching real data.  This test confirms it explicitly by
        asserting the real project's .crumbs/ has NOT grown.
        """
        _make_crumbs_env(tmp_path)

        # Create a task in the isolated environment
        result = _run(["create", "--title", "IsolationCheck"], cwd=tmp_path)
        assert result.returncode == 0

        # The tasks.jsonl inside tmp_path/.crumbs/ must now have content
        tasks_file = tmp_path / ".crumbs" / "tasks.jsonl"
        assert tasks_file.read_text(encoding="utf-8").strip(), (
            "Expected tasks.jsonl in isolated env to contain the new task."
        )

    def test_create_then_show_roundtrip(self, tmp_path: Path) -> None:
        """Create a task, then show it by ID — full roundtrip via subprocess.

        Validates that a task created in the isolated environment is
        immediately visible via ``crumb show <ID>``.
        """
        _make_crumbs_env(tmp_path)

        create_result = _run(["create", "--title", "RoundtripTask"], cwd=tmp_path)
        assert create_result.returncode == 0, (
            f"create failed: {create_result.stderr!r}"
        )

        # crumb.py prints "created AF-1" on the first line; the ID is the
        # last whitespace-delimited token on that line.
        first_line = create_result.stdout.strip().splitlines()[0].strip()
        assert first_line, "Expected non-empty first line of stdout."
        task_id = first_line.split()[-1]

        show_result = _run(["show", task_id], cwd=tmp_path)
        assert show_result.returncode == 0, (
            f"show {task_id!r} failed: {show_result.stderr!r}"
        )
        assert task_id in show_result.stdout, (
            f"Expected ID {task_id!r} to appear in show output."
        )

    def test_list_json_returns_valid_json_array(self, tmp_path: Path) -> None:
        """``crumb list --json`` exits 0 and outputs a JSON array parseable by json.loads().

        Acceptance criterion 1: well-formed JSON array on stdout.
        """
        _make_crumbs_env(tmp_path)
        _run(["create", "--title", "Task Alpha"], cwd=tmp_path)
        _run(["create", "--title", "Task Beta"], cwd=tmp_path)

        result = _run(["list", "--json"], cwd=tmp_path)

        assert result.returncode == 0, (
            f"Expected exit code 0.\nstdout: {result.stdout!r}\nstderr: {result.stderr!r}"
        )
        parsed = json.loads(result.stdout)
        assert isinstance(parsed, list), (
            f"Expected a JSON array, got {type(parsed).__name__}."
        )
        assert len(parsed) == 2, (
            f"Expected 2 items in JSON array, got {len(parsed)}."
        )

    def test_list_json_with_open_filter_returns_only_open(self, tmp_path: Path) -> None:
        """``crumb list --json --open`` returns only open crumbs as a JSON array.

        Acceptance criterion 2: filter flags compose correctly with --json.
        """
        _make_crumbs_env(tmp_path)
        create_result = _run(["create", "--title", "Open task"], cwd=tmp_path)
        task_id = create_result.stdout.strip().splitlines()[0].split()[-1]
        _run(["close", task_id], cwd=tmp_path)
        _run(["create", "--title", "Still open"], cwd=tmp_path)

        result = _run(["list", "--json", "--open"], cwd=tmp_path)

        assert result.returncode == 0, (
            f"Expected exit code 0.\nstdout: {result.stdout!r}\nstderr: {result.stderr!r}"
        )
        parsed = json.loads(result.stdout)
        assert isinstance(parsed, list)
        assert len(parsed) == 1, (
            f"Expected 1 open crumb, got {len(parsed)}."
        )
        assert parsed[0]["status"] == "open"

    def test_show_json_returns_valid_json_object(self, tmp_path: Path) -> None:
        """``crumb show <id> --json`` exits 0 and outputs a JSON object.

        Acceptance criterion 3: single well-formed JSON object on stdout.
        """
        _make_crumbs_env(tmp_path)
        create_result = _run(["create", "--title", "Show JSON task"], cwd=tmp_path)
        task_id = create_result.stdout.strip().splitlines()[0].split()[-1]

        result = _run(["show", task_id, "--json"], cwd=tmp_path)

        assert result.returncode == 0, (
            f"Expected exit code 0.\nstdout: {result.stdout!r}\nstderr: {result.stderr!r}"
        )
        parsed = json.loads(result.stdout)
        assert isinstance(parsed, dict), (
            f"Expected a JSON object (dict), got {type(parsed).__name__}."
        )
        assert parsed["id"] == task_id, (
            f"Expected JSON 'id' field to be {task_id!r}, got {parsed.get('id')!r}."
        )

    def test_list_without_json_is_human_readable(self, tmp_path: Path) -> None:
        """``crumb list`` without --json produces identical human-readable output.

        Acceptance criterion 4: human-readable format is unchanged when --json is absent.
        """
        _make_crumbs_env(tmp_path)
        _run(["create", "--title", "Readable task"], cwd=tmp_path)

        result = _run(["list"], cwd=tmp_path)

        assert result.returncode == 0
        output = result.stdout.strip()
        # Human-readable output: first token on first line should be the ID (e.g. "AF-1")
        first_token = output.splitlines()[0].split()[0]
        assert first_token.startswith("AF-"), (
            f"Expected human-readable ID in first column, got {first_token!r}."
        )
        # Definitely not a JSON array
        assert not output.startswith("["), (
            "Human-readable output must not start with '[' (JSON array)."
        )

    def test_show_json_contains_required_fields(self, tmp_path: Path) -> None:
        """``crumb show <id> --json`` object contains all required schema fields.

        Acceptance criterion 5: id, title, type, status, priority, description,
        acceptance_criteria, scope, links, notes are all present.
        """
        _make_crumbs_env(tmp_path)
        create_result = _run(["create", "--title", "Field check"], cwd=tmp_path)
        task_id = create_result.stdout.strip().splitlines()[0].split()[-1]

        result = _run(["show", task_id, "--json"], cwd=tmp_path)

        assert result.returncode == 0
        parsed = json.loads(result.stdout)
        for field in ("id", "title", "type", "status", "priority",
                      "description", "acceptance_criteria", "scope", "links", "notes"):
            assert field in parsed, (
                f"Required field '{field}' missing from 'crumb show --json' output."
            )

    def test_create_json_returns_valid_json_object(self, tmp_path: Path) -> None:
        """``crumb create --title T --json`` exits 0 and outputs a JSON object.

        Acceptance criterion 3: newly created crumb returned as JSON object.
        """
        _make_crumbs_env(tmp_path)

        result = _run(["create", "--title", "JSON create", "--json"], cwd=tmp_path)

        assert result.returncode == 0, (
            f"Expected exit code 0.\nstdout: {result.stdout!r}\nstderr: {result.stderr!r}"
        )
        parsed = json.loads(result.stdout)
        assert isinstance(parsed, dict), (
            f"Expected a JSON object (dict), got {type(parsed).__name__}."
        )

    def test_create_json_contains_required_fields(self, tmp_path: Path) -> None:
        """``crumb create --json`` output contains all required schema fields."""
        _make_crumbs_env(tmp_path)

        result = _run(["create", "--title", "Field check", "--json"], cwd=tmp_path)

        assert result.returncode == 0
        parsed = json.loads(result.stdout)
        for field in ("id", "title", "type", "status", "priority",
                      "description", "acceptance_criteria", "scope", "links", "notes"):
            assert field in parsed, (
                f"Required field '{field}' missing from 'crumb create --json' output."
            )

    def test_create_without_json_unchanged_human_output(self, tmp_path: Path) -> None:
        """``crumb create`` without --json still prints human-readable 'created <ID>'."""
        _make_crumbs_env(tmp_path)

        result = _run(["create", "--title", "Human create"], cwd=tmp_path)

        assert result.returncode == 0
        assert "created" in result.stdout.lower(), (
            "Expected human-readable 'created ...' output when --json absent."
        )
        assert not result.stdout.strip().startswith("{"), (
            "Output must not be JSON when --json flag is absent."
        )

    def test_update_json_returns_success_true_and_updated_record(
        self, tmp_path: Path
    ) -> None:
        """``crumb update <id> --status=in_progress --json`` returns success=true and record.

        Acceptance criterion 1: JSON object with updated crumb record and success field.
        """
        _make_crumbs_env(tmp_path)
        create_result = _run(["create", "--title", "Update me"], cwd=tmp_path)
        task_id = create_result.stdout.strip().splitlines()[0].split()[-1]

        result = _run(["update", task_id, "--status=in_progress", "--json"], cwd=tmp_path)

        assert result.returncode == 0, (
            f"Expected exit code 0.\nstdout: {result.stdout!r}\nstderr: {result.stderr!r}"
        )
        parsed = json.loads(result.stdout)
        assert isinstance(parsed, dict), "Expected a JSON object"
        assert parsed.get("success") is True
        assert parsed.get("status") == "in_progress"
        assert parsed.get("id") == task_id

    def test_update_json_contains_required_fields(self, tmp_path: Path) -> None:
        """``crumb update --json`` output contains success + all required crumb fields."""
        _make_crumbs_env(tmp_path)
        create_result = _run(["create", "--title", "Field check update"], cwd=tmp_path)
        task_id = create_result.stdout.strip().splitlines()[0].split()[-1]

        result = _run(["update", task_id, "--status=in_progress", "--json"], cwd=tmp_path)

        assert result.returncode == 0
        parsed = json.loads(result.stdout)
        for field in ("success", "id", "title", "type", "status", "priority",
                      "description", "acceptance_criteria", "scope", "links", "notes"):
            assert field in parsed, (
                f"Required field '{field}' missing from 'crumb update --json' output."
            )

    def test_update_without_json_unchanged_human_output(self, tmp_path: Path) -> None:
        """``crumb update`` without --json still prints human-readable 'updated <ID>'."""
        _make_crumbs_env(tmp_path)
        create_result = _run(["create", "--title", "Human update"], cwd=tmp_path)
        task_id = create_result.stdout.strip().splitlines()[0].split()[-1]

        result = _run(["update", task_id, "--status=in_progress"], cwd=tmp_path)

        assert result.returncode == 0
        assert "updated" in result.stdout.lower(), (
            "Expected human-readable 'updated ...' output when --json absent."
        )
        assert not result.stdout.strip().startswith("{"), (
            "Output must not be JSON when --json flag is absent."
        )

    def test_doctor_json_returns_diagnostic_report(self, tmp_path: Path) -> None:
        """``crumb doctor --json`` exits 0 and outputs a JSON diagnostic report.

        Acceptance criterion 4: JSON object with diagnostic results.
        """
        _make_crumbs_env(tmp_path)
        _run(["create", "--title", "Healthy task"], cwd=tmp_path)

        result = _run(["doctor", "--json"], cwd=tmp_path)

        assert result.returncode == 0, (
            f"Expected exit code 0.\nstdout: {result.stdout!r}\nstderr: {result.stderr!r}"
        )
        parsed = json.loads(result.stdout)
        assert isinstance(parsed, dict), "Expected a JSON object"

    def test_doctor_json_contains_required_fields(self, tmp_path: Path) -> None:
        """``crumb doctor --json`` output contains all required diagnostic schema fields."""
        _make_crumbs_env(tmp_path)
        _run(["create", "--title", "Clean task"], cwd=tmp_path)

        result = _run(["doctor", "--json"], cwd=tmp_path)

        assert result.returncode == 0
        parsed = json.loads(result.stdout)
        for field in ("ok", "error_count", "warning_count", "errors", "warnings", "fixes_applied"):
            assert field in parsed, (
                f"Required field '{field}' missing from 'crumb doctor --json' output."
            )

    def test_doctor_without_json_unchanged_human_output(self, tmp_path: Path) -> None:
        """``crumb doctor`` without --json still prints human-readable output."""
        _make_crumbs_env(tmp_path)
        # Create a trail so doctor finds no issues (orphan warning is still OK to have)
        _run(["create", "--title", "Healthy"], cwd=tmp_path)

        result = _run(["doctor"], cwd=tmp_path)

        # Should be human-readable — not a JSON object
        assert not result.stdout.strip().startswith("{"), (
            "Output must not be JSON when --json flag is absent."
        )

    def test_search_json_returns_valid_json_array(self, tmp_path: Path) -> None:
        """``crumb search QUERY --json`` exits 0 and outputs a JSON array.

        Acceptance criterion: well-formed JSON array on stdout containing only
        crumbs whose title or description matches the query.
        """
        _make_crumbs_env(tmp_path)
        _run(["create", "--title", "Alpha task"], cwd=tmp_path)
        _run(["create", "--title", "Beta task"], cwd=tmp_path)
        _run(["create", "--title", "Unrelated"], cwd=tmp_path)

        result = _run(["search", "task", "--json"], cwd=tmp_path)

        assert result.returncode == 0, (
            f"Expected exit code 0.\nstdout: {result.stdout!r}\nstderr: {result.stderr!r}"
        )
        parsed = json.loads(result.stdout)
        assert isinstance(parsed, list), (
            f"Expected a JSON array, got {type(parsed).__name__}."
        )
        assert len(parsed) == 2, (
            f"Expected 2 matching crumbs, got {len(parsed)}."
        )

    def test_search_json_empty_results_returns_empty_array(self, tmp_path: Path) -> None:
        """``crumb search NOMATCHES --json`` exits 0 and outputs an empty JSON array.

        Acceptance criterion: no matches returns ``[]`` rather than no output.
        """
        _make_crumbs_env(tmp_path)
        _run(["create", "--title", "Something"], cwd=tmp_path)

        result = _run(["search", "xyzzy_no_match", "--json"], cwd=tmp_path)

        assert result.returncode == 0, (
            f"Expected exit code 0.\nstdout: {result.stdout!r}\nstderr: {result.stderr!r}"
        )
        parsed = json.loads(result.stdout)
        assert isinstance(parsed, list), (
            f"Expected a JSON array, got {type(parsed).__name__}."
        )
        assert len(parsed) == 0, (
            f"Expected empty array for no matches, got {len(parsed)} items."
        )

    def test_search_json_contains_required_fields(self, tmp_path: Path) -> None:
        """``crumb search QUERY --json`` objects contain all required schema fields."""
        _make_crumbs_env(tmp_path)
        _run(["create", "--title", "Fieldcheck crumb"], cwd=tmp_path)

        result = _run(["search", "fieldcheck", "--json"], cwd=tmp_path)

        assert result.returncode == 0
        parsed = json.loads(result.stdout)
        assert len(parsed) == 1, f"Expected 1 result, got {len(parsed)}."
        for field in ("id", "title", "type", "status", "priority",
                      "description", "acceptance_criteria", "scope", "links", "notes"):
            assert field in parsed[0], (
                f"Required field '{field}' missing from 'crumb search --json' output."
            )

    def test_search_without_json_is_human_readable(self, tmp_path: Path) -> None:
        """``crumb search QUERY`` without --json produces human-readable output.

        Acceptance criterion: human-readable format is unchanged when --json is absent.
        """
        _make_crumbs_env(tmp_path)
        _run(["create", "--title", "Human search task"], cwd=tmp_path)

        result = _run(["search", "human"], cwd=tmp_path)

        assert result.returncode == 0
        output = result.stdout.strip()
        assert output, "Expected non-empty output for a matching search."
        # Human-readable output: first token should be the ID (e.g. "AF-1")
        first_token = output.splitlines()[0].split()[0]
        assert first_token.startswith("AF-"), (
            f"Expected human-readable ID in first column, got {first_token!r}."
        )
        # Definitely not a JSON array
        assert not output.startswith("["), (
            "Human-readable output must not start with '[' (JSON array)."
        )


# ---------------------------------------------------------------------------
# Prune integration helpers
# ---------------------------------------------------------------------------

#: Seconds per day — used with os.utime to backdate directory mtimes.
_SECS_PER_DAY: int = 86_400

#: A mtime age (in seconds) guaranteed to be older than the 60-minute active
#: guard window.  Two hours is enough headroom.
_STALE_SESSION_AGE_SECS: int = 7_200


def _make_sessions_dir(crumbs_dir: Path) -> Path:
    """Create and return ``crumbs_dir/sessions/``.

    Args:
        crumbs_dir: The isolated ``.crumbs/`` directory.

    Returns:
        Path to the newly created ``sessions/`` sub-directory.
    """
    sessions_dir = crumbs_dir / "sessions"
    sessions_dir.mkdir(parents=True, exist_ok=True)
    return sessions_dir


def _make_session_dir(
    sessions_dir: Path,
    name: str,
    *,
    backdate_secs: int = _STALE_SESSION_AGE_SECS,
) -> Path:
    """Create a named session directory and optionally backdate its mtime.

    Args:
        sessions_dir: Parent ``sessions/`` directory.
        name: Directory name (e.g. ``_session-20260101-120000``).
        backdate_secs: How many seconds in the past to set the mtime.
            Pass ``0`` to leave the mtime as-is (i.e. current time).

    Returns:
        Path to the created directory.
    """
    session_dir = sessions_dir / name
    session_dir.mkdir(parents=True, exist_ok=True)
    if backdate_secs > 0:
        past = time.time() - backdate_secs
        os.utime(session_dir, (past, past))
    return session_dir


def _session_name(prefix: str, days_old: int, hour: int = 12) -> str:
    """Build a valid session directory name whose embedded timestamp is *days_old* days ago.

    Args:
        prefix: One of ``_session-``, ``_decompose-``, ``_review-``.
        days_old: How many days ago the timestamp should be.
        hour: Hour component of the timestamp (default 12 for noon).

    Returns:
        Directory name string, e.g. ``_session-20260215-120000``.
    """
    ts: datetime = datetime.now() - timedelta(days=days_old)
    ts = ts.replace(hour=hour, minute=0, second=0, microsecond=0)
    return f"{prefix}{ts.strftime(SESSION_TS_FORMAT)}"


# ---------------------------------------------------------------------------
# TestCLIPrune
# ---------------------------------------------------------------------------


class TestCLIPrune:
    """Subprocess-based integration tests for the ``crumb prune`` subcommand.

    Each test:
    1. Creates an isolated ``.crumbs/`` environment in a fresh ``tmp_path``.
    2. Populates ``sessions/`` with synthetic directories whose name-embedded
       timestamps and filesystem mtimes are controlled to exercise specific
       code paths.
    3. Invokes ``crumb prune`` (with optional flags) via ``_run()``.
    4. Asserts on exit code, stdout, stderr, and directory presence.
    """

    def test_default_prune_deletes_old_and_prints_count(
        self, tmp_path: Path
    ) -> None:
        """Default ``crumb prune`` deletes dirs older than 14 days and prints count.

        Acceptance criterion 2: default prune deletes dirs older than 14 days
        and prints the deleted count to stdout.
        """
        crumbs_dir = _make_crumbs_env(tmp_path)
        sessions_dir = _make_sessions_dir(crumbs_dir)

        # 20-day-old directory — should be pruned
        old_name = _session_name("_session-", days_old=20)
        old_dir = _make_session_dir(sessions_dir, old_name, backdate_secs=_STALE_SESSION_AGE_SECS)

        # 5-day-old directory — should be retained (below 14-day threshold)
        recent_name = _session_name("_session-", days_old=5, hour=10)
        recent_dir = _make_session_dir(sessions_dir, recent_name, backdate_secs=_STALE_SESSION_AGE_SECS)

        result = _run(["prune"], cwd=tmp_path)

        assert result.returncode == 0, (
            f"Expected exit 0.\nstdout: {result.stdout!r}\nstderr: {result.stderr!r}"
        )
        # stdout should mention "pruned" and the count
        assert "pruned" in result.stdout.lower(), (
            f"Expected 'pruned' in stdout.\nstdout: {result.stdout!r}"
        )
        assert "1" in result.stdout, (
            f"Expected count '1' in stdout.\nstdout: {result.stdout!r}"
        )
        # Old dir must be gone; recent dir must survive
        assert not old_dir.exists(), "Old session directory should have been deleted."
        assert recent_dir.exists(), "Recent session directory should NOT have been deleted."

    def test_days_7_deletes_only_dirs_older_than_7_days(
        self, tmp_path: Path
    ) -> None:
        """``crumb prune --days 7`` deletes dirs >7 days old, retains newer ones.

        Acceptance criterion 3: ``--days 7`` threshold is respected.
        """
        crumbs_dir = _make_crumbs_env(tmp_path)
        sessions_dir = _make_sessions_dir(crumbs_dir)

        # 10-day-old directory — should be pruned under --days 7
        old_name = _session_name("_session-", days_old=10)
        old_dir = _make_session_dir(sessions_dir, old_name, backdate_secs=_STALE_SESSION_AGE_SECS)

        # 3-day-old directory — should be retained (age < 7 days)
        new_name = _session_name("_session-", days_old=3, hour=10)
        new_dir = _make_session_dir(sessions_dir, new_name, backdate_secs=_STALE_SESSION_AGE_SECS)

        result = _run(["prune", "--days", "7"], cwd=tmp_path)

        assert result.returncode == 0, (
            f"Expected exit 0.\nstdout: {result.stdout!r}\nstderr: {result.stderr!r}"
        )
        assert not old_dir.exists(), (
            "10-day-old directory should have been deleted with --days 7."
        )
        assert new_dir.exists(), (
            "3-day-old directory should NOT have been deleted with --days 7."
        )

    def test_days_0_skips_active_dirs_with_stderr_warning(
        self, tmp_path: Path
    ) -> None:
        """``crumb prune --days 0`` skips active dirs (recent mtime) with warning.

        Acceptance criterion 4: active sessions are skipped and a warning is
        emitted to stderr when ``--days 0`` would otherwise qualify every dir.
        """
        crumbs_dir = _make_crumbs_env(tmp_path)
        sessions_dir = _make_sessions_dir(crumbs_dir)

        # A directory with an old name-timestamp but a *very recent* mtime
        # (within 60 minutes) — crumb.py must skip it as an active session.
        active_name = _session_name("_session-", days_old=20)
        active_dir = _make_session_dir(
            sessions_dir, active_name, backdate_secs=0  # mtime = now
        )

        result = _run(["prune", "--days", "0"], cwd=tmp_path)

        assert result.returncode == 0, (
            f"Expected exit 0.\nstdout: {result.stdout!r}\nstderr: {result.stderr!r}"
        )
        # The active session must not have been deleted
        assert active_dir.exists(), (
            "Active session directory should NOT have been deleted by --days 0."
        )
        # A warning about the active session must appear on stderr
        assert "warning" in result.stderr.lower(), (
            f"Expected 'warning' in stderr for active session.\nstderr: {result.stderr!r}"
        )
        assert "active" in result.stderr.lower(), (
            f"Expected 'active' in stderr warning.\nstderr: {result.stderr!r}"
        )

    def test_negative_days_exits_nonzero_no_deletion(
        self, tmp_path: Path
    ) -> None:
        """``crumb prune --days -1`` exits non-zero without deleting anything.

        Acceptance criterion 5: negative days argument causes non-zero exit
        and no directories are removed.
        """
        crumbs_dir = _make_crumbs_env(tmp_path)
        sessions_dir = _make_sessions_dir(crumbs_dir)

        old_name = _session_name("_session-", days_old=30)
        old_dir = _make_session_dir(sessions_dir, old_name, backdate_secs=_STALE_SESSION_AGE_SECS)

        result = _run(["prune", "--days", "-1"], cwd=tmp_path)

        assert result.returncode != 0, (
            f"Expected non-zero exit for --days -1, got {result.returncode}."
        )
        # Nothing should have been deleted
        assert old_dir.exists(), (
            "Session directory must not be deleted when --days is negative."
        )

    def test_dry_run_does_not_delete_and_prints_counts(
        self, tmp_path: Path
    ) -> None:
        """``crumb prune --dry-run`` prints would-prune/retain counts without deleting.

        Acceptance criterion 6: ``--dry-run`` leaves all directories intact
        and prints both would-prune and would-retain counts to stdout.
        """
        crumbs_dir = _make_crumbs_env(tmp_path)
        sessions_dir = _make_sessions_dir(crumbs_dir)

        # Old dir — would be pruned
        old_name = _session_name("_session-", days_old=20)
        old_dir = _make_session_dir(sessions_dir, old_name, backdate_secs=_STALE_SESSION_AGE_SECS)

        # Recent dir — would be retained
        recent_name = _session_name("_decompose-", days_old=3, hour=10)
        recent_dir = _make_session_dir(sessions_dir, recent_name, backdate_secs=_STALE_SESSION_AGE_SECS)

        result = _run(["prune", "--dry-run"], cwd=tmp_path)

        assert result.returncode == 0, (
            f"Expected exit 0 for --dry-run.\nstdout: {result.stdout!r}\nstderr: {result.stderr!r}"
        )
        # Neither directory should have been deleted
        assert old_dir.exists(), "Old dir must NOT be deleted by --dry-run."
        assert recent_dir.exists(), "Recent dir must NOT be deleted by --dry-run."
        # stdout must mention "would prune" and "would retain"
        stdout_lower = result.stdout.lower()
        assert "would prune" in stdout_lower, (
            f"Expected 'would prune' in stdout.\nstdout: {result.stdout!r}"
        )
        assert "would retain" in stdout_lower, (
            f"Expected 'would retain' in stdout.\nstdout: {result.stdout!r}"
        )

    def test_unknown_prefix_dirs_never_deleted(self, tmp_path: Path) -> None:
        """Directories without known prefixes are silently skipped by prune.

        Acceptance criterion 7: non-matching prefixes (e.g. ``mydata-``) are
        never deleted regardless of age.
        """
        crumbs_dir = _make_crumbs_env(tmp_path)
        sessions_dir = _make_sessions_dir(crumbs_dir)

        # Unknown-prefix directory with an old-looking name
        unknown_name = "mydata-20260101-120000"
        unknown_dir = _make_session_dir(
            sessions_dir, unknown_name, backdate_secs=_SECS_PER_DAY * 30
        )

        result = _run(["prune", "--days", "0"], cwd=tmp_path)

        assert result.returncode == 0, (
            f"Expected exit 0.\nstdout: {result.stdout!r}\nstderr: {result.stderr!r}"
        )
        assert unknown_dir.exists(), (
            "Directory with unknown prefix must NOT be deleted by prune."
        )

    def test_unparseable_timestamp_skipped_with_stderr_warning(
        self, tmp_path: Path
    ) -> None:
        """A known-prefix dir with an unparseable timestamp is skipped with a warning.

        Acceptance criterion 8: ``_session-baddate`` emits a stderr warning
        and is not deleted.
        """
        crumbs_dir = _make_crumbs_env(tmp_path)
        sessions_dir = _make_sessions_dir(crumbs_dir)

        # Known prefix but unparseable timestamp portion
        bad_name = "_session-baddate"
        bad_dir = _make_session_dir(
            sessions_dir, bad_name, backdate_secs=_SECS_PER_DAY * 30
        )

        result = _run(["prune", "--days", "0"], cwd=tmp_path)

        assert result.returncode == 0, (
            f"Expected exit 0.\nstdout: {result.stdout!r}\nstderr: {result.stderr!r}"
        )
        assert bad_dir.exists(), (
            "Directory with unparseable timestamp must NOT be deleted."
        )
        assert "warning" in result.stderr.lower(), (
            f"Expected 'warning' in stderr.\nstderr: {result.stderr!r}"
        )
        assert "timestamp not parseable" in result.stderr.lower(), (
            f"Expected 'timestamp not parseable' message.\nstderr: {result.stderr!r}"
        )


# ---------------------------------------------------------------------------
# validate-spec tests
# ---------------------------------------------------------------------------


class TestValidateSpec:
    """Integration tests for ``crumb validate-spec``."""

    # ------------------------------------------------------------------
    # Spec file helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _write_spec(tmp_path: Path, content: str) -> Path:
        """Write *content* to ``tmp_path/spec.md`` and return the path.

        Args:
            tmp_path: Pytest temporary directory.
            content: Markdown content for the spec file.

        Returns:
            Absolute path to the written spec file.
        """
        spec_file = tmp_path / "spec.md"
        spec_file.write_text(content, encoding="utf-8")
        return spec_file

    # ------------------------------------------------------------------
    # AC-3.1 — scans AC lines, reports line/phrase/text
    # ------------------------------------------------------------------

    def test_reports_match_with_line_phrase_and_text(self, tmp_path: Path) -> None:
        """A banned phrase in an AC line is reported with line number, phrase, and text.

        Acceptance criterion AC-3.1: ``crumb validate-spec`` scans lines
        matching ``AC-\\d+\\.\\d+:`` and reports each match with the line
        number, the matched phrase, and the full AC text.
        """
        _make_crumbs_env(tmp_path)
        spec = self._write_spec(
            tmp_path,
            "# Spec\n\n- AC-1.1: System works correctly under load.\n",
        )

        result = _run(["validate-spec", str(spec)], cwd=tmp_path)

        assert result.returncode == 1, (
            f"Expected exit code 1 for banned phrase.\nstdout: {result.stdout!r}"
        )
        output = result.stdout
        assert "works correctly" in output, (
            f"Expected matched phrase 'works correctly' in output.\nstdout: {output!r}"
        )
        # Line number 3 (header, blank, AC line)
        assert "3" in output, (
            f"Expected line number 3 in output.\nstdout: {output!r}"
        )
        assert "AC-1.1" in output, (
            f"Expected AC text fragment in output.\nstdout: {output!r}"
        )

    def test_non_ac_lines_not_scanned(self, tmp_path: Path) -> None:
        """Lines that do not match ``AC-\\d+\\.\\d+:`` are not scanned.

        Acceptance criterion AC-3.1: only AC-tagged lines are checked.
        """
        _make_crumbs_env(tmp_path)
        spec = self._write_spec(
            tmp_path,
            "# Title\n\nThis section works correctly but is not an AC line.\n",
        )

        result = _run(["validate-spec", str(spec)], cwd=tmp_path)

        assert result.returncode == 0, (
            "Banned phrase in a non-AC line must not trigger a failure.\n"
            f"stdout: {result.stdout!r}"
        )

    # ------------------------------------------------------------------
    # AC-3.2 — banned phrases read from config.json
    # ------------------------------------------------------------------

    def test_custom_phrase_in_config_triggers_failure(self, tmp_path: Path) -> None:
        """A phrase added to ``banned_phrases`` in config.json is enforced.

        Acceptance criterion AC-3.2 / AC-3.6: phrases are read from
        config.json; custom additions require no code changes.
        """
        crumbs_dir = _make_crumbs_env(tmp_path)
        # Inject a custom phrase into config.json
        config_file = crumbs_dir / "config.json"
        cfg = json.loads(config_file.read_text(encoding="utf-8"))
        cfg["banned_phrases"] = ["totally custom phrase"]
        config_file.write_text(json.dumps(cfg, indent=2) + "\n", encoding="utf-8")

        spec = self._write_spec(
            tmp_path,
            "- AC-2.1: The system does a totally custom phrase validation.\n",
        )

        result = _run(["validate-spec", str(spec)], cwd=tmp_path)

        assert result.returncode == 1, (
            "Custom config phrase must trigger exit 1.\n"
            f"stdout: {result.stdout!r}"
        )
        assert "totally custom phrase" in result.stdout, (
            f"Expected custom phrase in output.\nstdout: {result.stdout!r}"
        )

    def test_empty_banned_phrases_list_always_passes(self, tmp_path: Path) -> None:
        """``banned_phrases: []`` in config.json means every spec is clean.

        Acceptance criterion AC-3.2: list is fully configurable.
        """
        crumbs_dir = _make_crumbs_env(tmp_path)
        config_file = crumbs_dir / "config.json"
        cfg = json.loads(config_file.read_text(encoding="utf-8"))
        cfg["banned_phrases"] = []
        config_file.write_text(json.dumps(cfg, indent=2) + "\n", encoding="utf-8")

        spec = self._write_spec(
            tmp_path,
            "- AC-1.1: works correctly, as expected, robust, seamless.\n",
        )

        result = _run(["validate-spec", str(spec)], cwd=tmp_path)

        assert result.returncode == 0, (
            "Empty banned_phrases list must produce exit 0.\n"
            f"stdout: {result.stdout!r}"
        )

    # ------------------------------------------------------------------
    # AC-3.3 — case-insensitive + word boundary
    # ------------------------------------------------------------------

    def test_case_insensitive_match(self, tmp_path: Path) -> None:
        """Matching is case-insensitive: mixed-case variants are caught.

        Acceptance criterion AC-3.3.
        """
        _make_crumbs_env(tmp_path)
        spec = self._write_spec(
            tmp_path,
            "- AC-1.1: System Works Correctly under load.\n"
            "- AC-1.2: SYSTEM WORKS CORRECTLY ALWAYS.\n",
        )

        result = _run(["validate-spec", str(spec)], cwd=tmp_path)

        assert result.returncode == 1, (
            "Mixed-case banned phrase must trigger exit 1.\n"
            f"stdout: {result.stdout!r}"
        )
        # Both lines should produce a match
        assert result.stdout.count("works correctly") >= 2, (
            f"Expected 2 matches for two case variants.\nstdout: {result.stdout!r}"
        )

    def test_word_boundary_no_false_positive(self, tmp_path: Path) -> None:
        """'inappropriate' must NOT match the banned phrase 'appropriate'.

        Acceptance criterion AC-3.3: word-boundary matching prevents false
        positives on substrings.
        """
        _make_crumbs_env(tmp_path)
        spec = self._write_spec(
            tmp_path,
            "- AC-1.1: System behaves in an inappropriate manner.\n",
        )

        result = _run(["validate-spec", str(spec)], cwd=tmp_path)

        assert result.returncode == 0, (
            "'inappropriate' must not match banned phrase 'appropriate'.\n"
            f"stdout: {result.stdout!r}"
        )

    # ------------------------------------------------------------------
    # AC-3.4 — exit codes
    # ------------------------------------------------------------------

    def test_clean_spec_exits_zero(self, tmp_path: Path) -> None:
        """A spec with no banned phrases exits with code 0.

        Acceptance criterion AC-3.4.
        """
        _make_crumbs_env(tmp_path)
        spec = self._write_spec(
            tmp_path,
            "# Spec\n\n- AC-1.1: The service returns HTTP 200 within 200 ms.\n",
        )

        result = _run(["validate-spec", str(spec)], cwd=tmp_path)

        assert result.returncode == 0, (
            f"Clean spec must exit 0.\nstdout: {result.stdout!r}"
        )

    def test_dirty_spec_exits_one(self, tmp_path: Path) -> None:
        """A spec with a banned phrase exits with code 1.

        Acceptance criterion AC-3.4.
        """
        _make_crumbs_env(tmp_path)
        spec = self._write_spec(
            tmp_path,
            "- AC-1.1: System is robust and seamless.\n",
        )

        result = _run(["validate-spec", str(spec)], cwd=tmp_path)

        assert result.returncode == 1, (
            f"Dirty spec must exit 1.\nstdout: {result.stdout!r}"
        )

    # ------------------------------------------------------------------
    # AC-3.5 — --json output
    # ------------------------------------------------------------------

    def test_json_output_clean_spec(self, tmp_path: Path) -> None:
        """``--json`` on a clean spec outputs ``{"clean": true, "matches": []}``.

        Acceptance criterion AC-3.5.
        """
        _make_crumbs_env(tmp_path)
        spec = self._write_spec(
            tmp_path,
            "- AC-1.1: The widget returns the correct value.\n",
        )

        result = _run(["validate-spec", "--json", str(spec)], cwd=tmp_path)

        assert result.returncode == 0, (
            f"Clean spec with --json must exit 0.\nstdout: {result.stdout!r}"
        )
        parsed = json.loads(result.stdout)
        assert parsed["clean"] is True, (
            f"Expected 'clean: true'.\nresult: {parsed}"
        )
        assert parsed["matches"] == [], (
            f"Expected empty matches array.\nresult: {parsed}"
        )

    def test_json_output_dirty_spec(self, tmp_path: Path) -> None:
        """``--json`` on a dirty spec outputs ``clean: false`` and non-empty matches.

        Acceptance criterion AC-3.5.
        """
        _make_crumbs_env(tmp_path)
        spec = self._write_spec(
            tmp_path,
            "- AC-1.1: System handles errors as expected.\n",
        )

        result = _run(["validate-spec", "--json", str(spec)], cwd=tmp_path)

        assert result.returncode == 1, (
            f"Dirty spec with --json must exit 1.\nstdout: {result.stdout!r}"
        )
        parsed = json.loads(result.stdout)
        assert parsed["clean"] is False, (
            f"Expected 'clean: false'.\nresult: {parsed}"
        )
        assert len(parsed["matches"]) > 0, (
            f"Expected non-empty matches array.\nresult: {parsed}"
        )
        match = parsed["matches"][0]
        assert "line" in match, f"Match must have 'line' field.\nresult: {parsed}"
        assert "phrase" in match, f"Match must have 'phrase' field.\nresult: {parsed}"
        assert "text" in match, f"Match must have 'text' field.\nresult: {parsed}"

    def test_json_output_schema(self, tmp_path: Path) -> None:
        """``--json`` match objects contain ``line`` (int), ``phrase``, and ``text``.

        Acceptance criterion AC-3.5.
        """
        _make_crumbs_env(tmp_path)
        spec = self._write_spec(
            tmp_path,
            "- AC-1.1: The UI is intuitive and user-friendly.\n",
        )

        result = _run(["validate-spec", "--json", str(spec)], cwd=tmp_path)

        parsed = json.loads(result.stdout)
        for m in parsed["matches"]:
            assert isinstance(m["line"], int), (
                f"'line' must be an integer.\nresult: {parsed}"
            )
            assert isinstance(m["phrase"], str), (
                f"'phrase' must be a string.\nresult: {parsed}"
            )
            assert isinstance(m["text"], str), (
                f"'text' must be a string.\nresult: {parsed}"
            )

    # ------------------------------------------------------------------
    # Edge cases
    # ------------------------------------------------------------------

    def test_missing_spec_file_exits_nonzero(self, tmp_path: Path) -> None:
        """Passing a non-existent spec file path exits non-zero with an error.

        Guards against silent failures when a bad path is supplied.
        """
        _make_crumbs_env(tmp_path)

        result = _run(["validate-spec", str(tmp_path / "no_such_file.md")], cwd=tmp_path)

        assert result.returncode != 0, (
            "Missing spec file must produce a non-zero exit code.\n"
            f"stdout: {result.stdout!r}\nstderr: {result.stderr!r}"
        )

    def test_multiple_phrases_on_same_line_all_reported(self, tmp_path: Path) -> None:
        """Multiple banned phrases on one AC line each produce a separate match entry."""
        _make_crumbs_env(tmp_path)
        spec = self._write_spec(
            tmp_path,
            "- AC-1.1: System is robust, seamless, and intuitive.\n",
        )

        result = _run(["validate-spec", "--json", str(spec)], cwd=tmp_path)

        parsed = json.loads(result.stdout)
        phrases_found = {m["phrase"] for m in parsed["matches"]}
        assert "robust" in phrases_found, (
            f"Expected 'robust' in matches.\nresult: {parsed}"
        )
        assert "seamless" in phrases_found, (
            f"Expected 'seamless' in matches.\nresult: {parsed}"
        )
        assert "intuitive" in phrases_found, (
            f"Expected 'intuitive' in matches.\nresult: {parsed}"
        )

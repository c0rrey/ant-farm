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
# session-retries / session-reset-retries tests
# ---------------------------------------------------------------------------

#: Filename used by retry-tracker.js inside a session directory.
_RETRIES_FILE = "retries.json"


def _write_retries(session_dir: Path, events: list) -> None:
    """Write *events* to ``session_dir/retries.json``.

    Args:
        session_dir: Directory that acts as the session directory.
        events: List of retry event dicts to serialise.
    """
    retries_path = session_dir / _RETRIES_FILE
    retries_path.write_text(json.dumps(events, indent=2) + "\n", encoding="utf-8")


class TestSessionRetries:
    """Integration tests for ``crumb session-retries`` and
    ``crumb session-reset-retries`` subcommands."""

    # ------------------------------------------------------------------
    # session-retries — no retries.json
    # ------------------------------------------------------------------

    def test_session_retries_no_file_exits_zero(self, tmp_path: Path) -> None:
        """``crumb session-retries`` exits 0 when retries.json is absent."""
        _make_crumbs_env(tmp_path)
        session_dir = tmp_path / "session-001"
        session_dir.mkdir()

        result = _run(["session-retries", str(session_dir)], cwd=tmp_path)

        assert result.returncode == 0, (
            f"Expected exit code 0 for missing retries.json.\n"
            f"stdout: {result.stdout!r}\nstderr: {result.stderr!r}"
        )

    def test_session_retries_no_file_prints_total_zero(self, tmp_path: Path) -> None:
        """``crumb session-retries`` reports total 0 when retries.json is absent."""
        _make_crumbs_env(tmp_path)
        session_dir = tmp_path / "session-001"
        session_dir.mkdir()

        result = _run(["session-retries", str(session_dir)], cwd=tmp_path)

        assert "0" in result.stdout, (
            f"Expected '0' in stdout for missing retries.json.\n"
            f"stdout: {result.stdout!r}"
        )

    # ------------------------------------------------------------------
    # session-retries — with events
    # ------------------------------------------------------------------

    def test_session_retries_shows_total_count(self, tmp_path: Path) -> None:
        """``crumb session-retries`` shows the total number of retry events."""
        _make_crumbs_env(tmp_path)
        session_dir = tmp_path / "session-001"
        session_dir.mkdir()

        events = [
            {"timestamp": "2026-01-01T00:00:00.000Z", "failure_type": "checkpoint",
             "task_id": "AF-1", "retry_number": 1, "max_allowed": 2},
            {"timestamp": "2026-01-01T00:01:00.000Z", "failure_type": "agent_error",
             "task_id": "AF-2", "retry_number": 1, "max_allowed": 1},
        ]
        _write_retries(session_dir, events)

        result = _run(["session-retries", str(session_dir)], cwd=tmp_path)

        assert result.returncode == 0, (
            f"Expected exit code 0.\nstdout: {result.stdout!r}\nstderr: {result.stderr!r}"
        )
        assert "2" in result.stdout, (
            f"Expected total count '2' in stdout.\nstdout: {result.stdout!r}"
        )

    def test_session_retries_shows_failure_types(self, tmp_path: Path) -> None:
        """``crumb session-retries`` lists each failure type in output."""
        _make_crumbs_env(tmp_path)
        session_dir = tmp_path / "session-001"
        session_dir.mkdir()

        events = [
            {"timestamp": "2026-01-01T00:00:00.000Z", "failure_type": "checkpoint",
             "task_id": "AF-1", "retry_number": 1, "max_allowed": 2},
        ]
        _write_retries(session_dir, events)

        result = _run(["session-retries", str(session_dir)], cwd=tmp_path)

        assert "checkpoint" in result.stdout, (
            f"Expected 'checkpoint' in stdout.\nstdout: {result.stdout!r}"
        )

    # ------------------------------------------------------------------
    # session-retries --json
    # ------------------------------------------------------------------

    def test_session_retries_json_output_is_valid_json(self, tmp_path: Path) -> None:
        """``crumb session-retries --json`` emits valid JSON."""
        _make_crumbs_env(tmp_path)
        session_dir = tmp_path / "session-001"
        session_dir.mkdir()

        events = [
            {"timestamp": "2026-01-01T00:00:00.000Z", "failure_type": "checkpoint",
             "task_id": "AF-1", "retry_number": 1, "max_allowed": 2},
        ]
        _write_retries(session_dir, events)

        result = _run(["session-retries", "--json", str(session_dir)], cwd=tmp_path)

        assert result.returncode == 0, (
            f"Expected exit code 0.\nstdout: {result.stdout!r}\nstderr: {result.stderr!r}"
        )
        try:
            data = json.loads(result.stdout)
        except json.JSONDecodeError as exc:
            raise AssertionError(
                f"stdout is not valid JSON: {exc}\nstdout: {result.stdout!r}"
            ) from exc

        assert data["total"] == 1, f"Expected total=1, got {data!r}"
        assert "by_type" in data, f"Expected 'by_type' key in JSON output: {data!r}"
        assert "events" in data, f"Expected 'events' key in JSON output: {data!r}"

    def test_session_retries_json_no_file(self, tmp_path: Path) -> None:
        """``crumb session-retries --json`` emits ``total: 0`` when no file."""
        _make_crumbs_env(tmp_path)
        session_dir = tmp_path / "session-001"
        session_dir.mkdir()

        result = _run(["session-retries", "--json", str(session_dir)], cwd=tmp_path)

        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert data["total"] == 0

    # ------------------------------------------------------------------
    # session-reset-retries
    # ------------------------------------------------------------------

    def test_session_reset_retries_exits_zero(self, tmp_path: Path) -> None:
        """``crumb session-reset-retries`` exits 0 when retries.json exists."""
        _make_crumbs_env(tmp_path)
        session_dir = tmp_path / "session-001"
        session_dir.mkdir()
        _write_retries(session_dir, [
            {"timestamp": "2026-01-01T00:00:00.000Z", "failure_type": "checkpoint",
             "task_id": "AF-1", "retry_number": 1, "max_allowed": 2},
        ])

        result = _run(["session-reset-retries", str(session_dir)], cwd=tmp_path)

        assert result.returncode == 0, (
            f"Expected exit code 0.\nstdout: {result.stdout!r}\nstderr: {result.stderr!r}"
        )

    def test_session_reset_retries_clears_file(self, tmp_path: Path) -> None:
        """``crumb session-reset-retries`` overwrites retries.json with []."""
        _make_crumbs_env(tmp_path)
        session_dir = tmp_path / "session-001"
        session_dir.mkdir()
        _write_retries(session_dir, [
            {"timestamp": "2026-01-01T00:00:00.000Z", "failure_type": "checkpoint",
             "task_id": "AF-1", "retry_number": 1, "max_allowed": 2},
        ])

        _run(["session-reset-retries", str(session_dir)], cwd=tmp_path)

        retries_path = session_dir / _RETRIES_FILE
        stored = json.loads(retries_path.read_text(encoding="utf-8"))
        assert stored == [], f"Expected empty array after reset, got {stored!r}"

    def test_session_reset_retries_creates_file_when_absent(self, tmp_path: Path) -> None:
        """``crumb session-reset-retries`` creates retries.json when it does not exist."""
        _make_crumbs_env(tmp_path)
        session_dir = tmp_path / "session-001"
        session_dir.mkdir()

        result = _run(["session-reset-retries", str(session_dir)], cwd=tmp_path)

        assert result.returncode == 0, (
            f"Expected exit code 0.\nstdout: {result.stdout!r}\nstderr: {result.stderr!r}"
        )
        retries_path = session_dir / _RETRIES_FILE
        assert retries_path.exists(), "retries.json should be created by reset"
        stored = json.loads(retries_path.read_text(encoding="utf-8"))
        assert stored == []

    def test_session_reset_retries_atomic_no_tmp_left(self, tmp_path: Path) -> None:
        """``crumb session-reset-retries`` does not leave a .json.tmp file behind."""
        _make_crumbs_env(tmp_path)
        session_dir = tmp_path / "session-001"
        session_dir.mkdir()

        _run(["session-reset-retries", str(session_dir)], cwd=tmp_path)

        tmp_path_check = session_dir / "retries.json.tmp"
        assert not tmp_path_check.exists(), ".json.tmp should not exist after reset"

    def test_session_reset_retries_prints_confirmation(self, tmp_path: Path) -> None:
        """``crumb session-reset-retries`` prints a confirmation message."""
        _make_crumbs_env(tmp_path)
        session_dir = tmp_path / "session-001"
        session_dir.mkdir()

        result = _run(["session-reset-retries", str(session_dir)], cwd=tmp_path)

        assert result.stdout.strip(), (
            f"Expected non-empty stdout from reset command.\nstdout: {result.stdout!r}"
        )

    def test_session_retries_then_reset_then_retries(self, tmp_path: Path) -> None:
        """Round-trip: write events, reset, query shows 0."""
        _make_crumbs_env(tmp_path)
        session_dir = tmp_path / "session-001"
        session_dir.mkdir()
        _write_retries(session_dir, [
            {"timestamp": "2026-01-01T00:00:00.000Z", "failure_type": "checkpoint",
             "task_id": "AF-1", "retry_number": 1, "max_allowed": 2},
            {"timestamp": "2026-01-01T00:01:00.000Z", "failure_type": "agent_error",
             "task_id": "AF-2", "retry_number": 1, "max_allowed": 1},
        ])

        _run(["session-reset-retries", str(session_dir)], cwd=tmp_path)

        result = _run(["session-retries", "--json", str(session_dir)], cwd=tmp_path)
        data = json.loads(result.stdout)
        assert data["total"] == 0, f"Expected total=0 after reset, got {data!r}"


# ---------------------------------------------------------------------------
# session-status tests
# ---------------------------------------------------------------------------

#: Filename read by session-status inside a session directory.
_PROGRESS_LOG_FILE = "progress.log"


def _write_progress_log(session_dir: Path, lines: list) -> None:
    """Write *lines* as newline-joined content to ``session_dir/progress.log``.

    Args:
        session_dir: Directory that acts as the session directory.
        lines: List of raw progress log line strings.
    """
    progress_path = session_dir / _PROGRESS_LOG_FILE
    progress_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


class TestSessionStatus:
    """Integration tests for ``crumb session-status`` subcommand."""

    # ------------------------------------------------------------------
    # session-status — no progress.log
    # ------------------------------------------------------------------

    def test_session_status_no_file_exits_zero(self, tmp_path: Path) -> None:
        """``crumb session-status`` exits 0 when progress.log is absent."""
        _make_crumbs_env(tmp_path)
        session_dir = tmp_path / "session-001"
        session_dir.mkdir()

        result = _run(["session-status", str(session_dir)], cwd=tmp_path)

        assert result.returncode == 0, (
            f"Expected exit code 0 for missing progress.log.\n"
            f"stdout: {result.stdout!r}\nstderr: {result.stderr!r}"
        )

    def test_session_status_no_file_prints_unknown(self, tmp_path: Path) -> None:
        """``crumb session-status`` reports unknown when progress.log is absent."""
        _make_crumbs_env(tmp_path)
        session_dir = tmp_path / "session-001"
        session_dir.mkdir()

        result = _run(["session-status", str(session_dir)], cwd=tmp_path)

        assert "unknown" in result.stdout, (
            f"Expected 'unknown' in stdout for missing progress.log.\n"
            f"stdout: {result.stdout!r}"
        )

    # ------------------------------------------------------------------
    # session-status — with progress.log
    # ------------------------------------------------------------------

    def test_session_status_shows_last_step(self, tmp_path: Path) -> None:
        """``crumb session-status`` shows the last event type from progress.log."""
        _make_crumbs_env(tmp_path)
        session_dir = tmp_path / "session-001"
        session_dir.mkdir()

        _write_progress_log(session_dir, [
            "2026-01-01T00:00:00.000Z|SESSION_INIT|wave=0",
            "2026-01-01T00:01:00.000Z|SCOUT_COMPLETE|wave=0",
        ])

        result = _run(["session-status", str(session_dir)], cwd=tmp_path)

        assert result.returncode == 0, (
            f"Expected exit code 0.\nstdout: {result.stdout!r}\nstderr: {result.stderr!r}"
        )
        assert "SCOUT_COMPLETE" in result.stdout, (
            f"Expected last event type 'SCOUT_COMPLETE' in stdout.\nstdout: {result.stdout!r}"
        )

    def test_session_status_shows_next_step(self, tmp_path: Path) -> None:
        """``crumb session-status`` shows the expected next step from progress.log."""
        _make_crumbs_env(tmp_path)
        session_dir = tmp_path / "session-001"
        session_dir.mkdir()

        _write_progress_log(session_dir, [
            "2026-01-01T00:00:00.000Z|SESSION_INIT|wave=0|next_step=pre-spawn-check",
        ])

        result = _run(["session-status", str(session_dir)], cwd=tmp_path)

        assert result.returncode == 0, (
            f"Expected exit code 0.\nstdout: {result.stdout!r}\nstderr: {result.stderr!r}"
        )
        assert "pre-spawn-check" in result.stdout, (
            f"Expected 'pre-spawn-check' in stdout.\nstdout: {result.stdout!r}"
        )

    def test_session_status_shows_none_when_no_next_step(self, tmp_path: Path) -> None:
        """``crumb session-status`` shows none for next step when no next_step= field."""
        _make_crumbs_env(tmp_path)
        session_dir = tmp_path / "session-001"
        session_dir.mkdir()

        _write_progress_log(session_dir, [
            "2026-01-01T00:00:00.000Z|SESSION_INIT|wave=0",
        ])

        result = _run(["session-status", str(session_dir)], cwd=tmp_path)

        assert result.returncode == 0
        # When next_step is absent, the output should say "none"
        assert "none" in result.stdout.lower(), (
            f"Expected 'none' in stdout for missing next_step.\nstdout: {result.stdout!r}"
        )

    def test_session_status_last_next_step_wins(self, tmp_path: Path) -> None:
        """``crumb session-status`` uses the last next_step= value when multiple exist."""
        _make_crumbs_env(tmp_path)
        session_dir = tmp_path / "session-001"
        session_dir.mkdir()

        _write_progress_log(session_dir, [
            "2026-01-01T00:00:00.000Z|SESSION_INIT|wave=0|next_step=pre-spawn-check",
            "2026-01-01T00:01:00.000Z|SCOUT_COMPLETE|wave=0|next_step=scope-verify",
        ])

        result = _run(["session-status", str(session_dir)], cwd=tmp_path)

        assert result.returncode == 0
        assert "scope-verify" in result.stdout, (
            f"Expected last next_step 'scope-verify' in stdout.\nstdout: {result.stdout!r}"
        )
        # The earlier value should NOT be the dominant one shown
        assert "pre-spawn-check" not in result.stdout.split("next step:")[-1], (
            f"Expected 'pre-spawn-check' NOT to be shown as next step.\nstdout: {result.stdout!r}"
        )

    def test_session_status_shows_position(self, tmp_path: Path) -> None:
        """``crumb session-status`` shows a position label for known event types."""
        _make_crumbs_env(tmp_path)
        session_dir = tmp_path / "session-001"
        session_dir.mkdir()

        _write_progress_log(session_dir, [
            "2026-01-01T00:00:00.000Z|WAVE_SPAWNED|wave=1",
        ])

        result = _run(["session-status", str(session_dir)], cwd=tmp_path)

        assert result.returncode == 0
        # Position label should include step number
        assert "3" in result.stdout, (
            f"Expected step '3' in position output for WAVE_SPAWNED.\nstdout: {result.stdout!r}"
        )

    # ------------------------------------------------------------------
    # session-status --json
    # ------------------------------------------------------------------

    def test_session_status_json_output_is_valid_json(self, tmp_path: Path) -> None:
        """``crumb session-status --json`` emits valid JSON."""
        _make_crumbs_env(tmp_path)
        session_dir = tmp_path / "session-001"
        session_dir.mkdir()

        _write_progress_log(session_dir, [
            "2026-01-01T00:00:00.000Z|SCOUT_COMPLETE|wave=0|next_step=pre-spawn-check",
        ])

        result = _run(["session-status", "--json", str(session_dir)], cwd=tmp_path)

        assert result.returncode == 0, (
            f"Expected exit code 0.\nstdout: {result.stdout!r}\nstderr: {result.stderr!r}"
        )
        try:
            data = json.loads(result.stdout)
        except json.JSONDecodeError as exc:
            raise AssertionError(
                f"stdout is not valid JSON: {exc}\nstdout: {result.stdout!r}"
            ) from exc

        assert "position" in data, f"Expected 'position' key in JSON output: {data!r}"
        assert "last_step" in data, f"Expected 'last_step' key in JSON output: {data!r}"
        assert "next_step" in data, f"Expected 'next_step' key in JSON output: {data!r}"

    def test_session_status_json_last_step_correct(self, tmp_path: Path) -> None:
        """``crumb session-status --json`` returns correct last_step value."""
        _make_crumbs_env(tmp_path)
        session_dir = tmp_path / "session-001"
        session_dir.mkdir()

        _write_progress_log(session_dir, [
            "2026-01-01T00:00:00.000Z|SESSION_INIT|wave=0",
            "2026-01-01T00:01:00.000Z|SCOUT_COMPLETE|wave=0",
        ])

        result = _run(["session-status", "--json", str(session_dir)], cwd=tmp_path)

        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert data["last_step"] == "SCOUT_COMPLETE", (
            f"Expected last_step='SCOUT_COMPLETE', got {data['last_step']!r}"
        )

    def test_session_status_json_next_step_correct(self, tmp_path: Path) -> None:
        """``crumb session-status --json`` returns correct next_step value."""
        _make_crumbs_env(tmp_path)
        session_dir = tmp_path / "session-001"
        session_dir.mkdir()

        _write_progress_log(session_dir, [
            "2026-01-01T00:00:00.000Z|SESSION_INIT|wave=0|next_step=scope-verify",
        ])

        result = _run(["session-status", "--json", str(session_dir)], cwd=tmp_path)

        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert data["next_step"] == "scope-verify", (
            f"Expected next_step='scope-verify', got {data['next_step']!r}"
        )

    def test_session_status_json_no_file(self, tmp_path: Path) -> None:
        """``crumb session-status --json`` emits null fields when no progress.log."""
        _make_crumbs_env(tmp_path)
        session_dir = tmp_path / "session-001"
        session_dir.mkdir()

        result = _run(["session-status", "--json", str(session_dir)], cwd=tmp_path)

        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert data["position"] is None, f"Expected position=null, got {data['position']!r}"
        assert data["last_step"] is None, f"Expected last_step=null, got {data['last_step']!r}"
        assert data["next_step"] is None, f"Expected next_step=null, got {data['next_step']!r}"

    def test_session_status_json_next_step_null_when_absent(self, tmp_path: Path) -> None:
        """``crumb session-status --json`` returns next_step=null when no next_step= field."""
        _make_crumbs_env(tmp_path)
        session_dir = tmp_path / "session-001"
        session_dir.mkdir()

        _write_progress_log(session_dir, [
            "2026-01-01T00:00:00.000Z|SESSION_INIT|wave=0",
        ])

        result = _run(["session-status", "--json", str(session_dir)], cwd=tmp_path)

        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert data["next_step"] is None, (
            f"Expected next_step=null when no next_step= field, got {data['next_step']!r}"
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

    # ------------------------------------------------------------------
    # AC-3.3 — case-insensitive: 'As Expected' matches 'as expected'
    # ------------------------------------------------------------------

    def test_case_insensitive_as_expected(self, tmp_path: Path) -> None:
        """'As Expected' (mixed case) is caught by the banned phrase 'as expected'.

        Acceptance criterion AC-3.3: case-insensitive matching applies to the
        specific phrase 'as expected', so a capitalised variant in an AC line
        triggers exit 1 just as the lower-case form does.
        """
        _make_crumbs_env(tmp_path)
        spec = self._write_spec(
            tmp_path,
            "- AC-1.1: The module behaves As Expected in all scenarios.\n",
        )

        result = _run(["validate-spec", str(spec)], cwd=tmp_path)

        assert result.returncode == 1, (
            "'As Expected' (mixed case) must match banned phrase 'as expected'.\n"
            f"stdout: {result.stdout!r}"
        )
        assert "as expected" in result.stdout.lower(), (
            f"Expected matched phrase 'as expected' in output.\nstdout: {result.stdout!r}"
        )

    # ------------------------------------------------------------------
    # Edge cases — empty spec file
    # ------------------------------------------------------------------

    def test_empty_spec_file_exits_zero(self, tmp_path: Path) -> None:
        """An empty spec file contains no AC lines and exits 0 with 0 matches.

        Acceptance criterion 8: an empty file is valid (no banned phrases can
        appear in zero lines) and must not cause an error or non-zero exit.
        """
        _make_crumbs_env(tmp_path)
        spec = self._write_spec(tmp_path, "")

        result = _run(["validate-spec", str(spec)], cwd=tmp_path)

        assert result.returncode == 0, (
            "Empty spec file must exit 0.\n"
            f"stdout: {result.stdout!r}\nstderr: {result.stderr!r}"
        )

    def test_empty_spec_file_json_clean_true(self, tmp_path: Path) -> None:
        """``--json`` on an empty spec outputs ``{"clean": true, "matches": []}``.

        Supplements acceptance criterion 8: the JSON path also handles empty
        files gracefully, reporting clean=true and an empty matches array.
        """
        _make_crumbs_env(tmp_path)
        spec = self._write_spec(tmp_path, "")

        result = _run(["validate-spec", "--json", str(spec)], cwd=tmp_path)

        assert result.returncode == 0, (
            "Empty spec file with --json must exit 0.\n"
            f"stdout: {result.stdout!r}\nstderr: {result.stderr!r}"
        )
        parsed = json.loads(result.stdout)
        assert parsed["clean"] is True, (
            f"Expected 'clean: true' for empty spec.\nresult: {parsed}"
        )
        assert parsed["matches"] == [], (
            f"Expected empty matches array for empty spec.\nresult: {parsed}"
        )


class TestTreeJSON:
    """Integration tests for 'crumb tree --json' output."""

    def test_json_full_tree_has_trails_and_orphans_keys(self, tmp_path: Path) -> None:
        """crumb tree --json returns object with 'trails' and 'orphans' keys."""
        _make_crumbs_env(tmp_path)
        # Create a trail and a task
        _run(["trail", "create", "--title", "My Trail"], cwd=tmp_path)
        _run(["create", "--title", "Orphan task"], cwd=tmp_path)

        result = _run(["tree", "--json"], cwd=tmp_path)

        assert result.returncode == 0, f"tree --json failed: {result.stderr!r}"
        parsed = json.loads(result.stdout)
        assert "trails" in parsed
        assert "orphans" in parsed

    def test_json_full_tree_trails_contain_children(self, tmp_path: Path) -> None:
        """crumb tree --json: each trail object includes a 'children' array."""
        _make_crumbs_env(tmp_path)
        _run(["trail", "create", "--title", "Sprint 1"], cwd=tmp_path)
        # Create a task and link it to the trail
        _run(["create", "--title", "Child task"], cwd=tmp_path)
        _run(["link", "AF-1", "--parent", "AF-T1"], cwd=tmp_path)

        result = _run(["tree", "--json"], cwd=tmp_path)

        assert result.returncode == 0
        parsed = json.loads(result.stdout)
        assert len(parsed["trails"]) == 1
        trail = parsed["trails"][0]
        assert "children" in trail
        assert len(trail["children"]) == 1
        assert trail["children"][0]["id"] == "AF-1"

    def test_json_full_tree_orphan_not_in_trail_children(self, tmp_path: Path) -> None:
        """crumb tree --json: tasks with no parent trail appear in 'orphans'."""
        _make_crumbs_env(tmp_path)
        _run(["create", "--title", "Orphan"], cwd=tmp_path)

        result = _run(["tree", "--json"], cwd=tmp_path)

        assert result.returncode == 0
        parsed = json.loads(result.stdout)
        assert len(parsed["orphans"]) == 1
        assert parsed["orphans"][0]["id"] == "AF-1"

    def test_json_single_trail_returns_trail_with_children(self, tmp_path: Path) -> None:
        """crumb tree <trail-id> --json returns the trail object with children array."""
        _make_crumbs_env(tmp_path)
        _run(["trail", "create", "--title", "Trail"], cwd=tmp_path)
        _run(["create", "--title", "Child"], cwd=tmp_path)
        _run(["link", "AF-1", "--parent", "AF-T1"], cwd=tmp_path)

        result = _run(["tree", "AF-T1", "--json"], cwd=tmp_path)

        assert result.returncode == 0
        obj = json.loads(result.stdout)
        assert obj["id"] == "AF-T1"
        assert "children" in obj
        assert len(obj["children"]) == 1

    def test_human_readable_unchanged_without_json_flag(self, tmp_path: Path) -> None:
        """crumb tree without --json outputs human-readable indented tree."""
        _make_crumbs_env(tmp_path)
        _run(["trail", "create", "--title", "Trail"], cwd=tmp_path)

        result = _run(["tree"], cwd=tmp_path)

        assert result.returncode == 0
        assert "AF-T1" in result.stdout
        assert not result.stdout.strip().startswith("{")


class TestImportJSON:
    """Integration tests for 'crumb import --json' output."""

    def _write_jsonl(self, tmp_path: Path, records: list) -> Path:
        """Write records to a JSONL file and return its path."""
        import_file = tmp_path / "import.jsonl"
        lines = "\n".join(json.dumps(r) for r in records) + "\n"
        import_file.write_text(lines, encoding="utf-8")
        return import_file

    def test_json_import_returns_imported_count(self, tmp_path: Path) -> None:
        """crumb import <file> --json returns object with 'imported_count' field."""
        _make_crumbs_env(tmp_path)
        import_file = self._write_jsonl(tmp_path, [
            {"id": "AF-1", "title": "Task 1", "status": "open", "type": "task"},
            {"id": "AF-2", "title": "Task 2", "status": "open", "type": "task"},
        ])

        result = _run(["import", "--json", str(import_file)], cwd=tmp_path)

        assert result.returncode == 0, f"import --json failed: {result.stderr!r}"
        parsed = json.loads(result.stdout)
        assert "imported_count" in parsed
        assert parsed["imported_count"] == 2

    def test_json_import_has_skip_counts(self, tmp_path: Path) -> None:
        """crumb import --json includes skipped_malformed and skipped_duplicate fields."""
        _make_crumbs_env(tmp_path)
        import_file = self._write_jsonl(tmp_path, [
            {"id": "AF-1", "title": "Good", "status": "open", "type": "task"},
        ])

        result = _run(["import", "--json", str(import_file)], cwd=tmp_path)

        assert result.returncode == 0
        parsed = json.loads(result.stdout)
        assert "skipped_malformed" in parsed
        assert "skipped_duplicate" in parsed
        assert parsed["skipped_malformed"] == 0
        assert parsed["skipped_duplicate"] == 0

    def test_json_import_empty_file_returns_zero_count(self, tmp_path: Path) -> None:
        """crumb import --json on empty file returns imported_count of 0."""
        _make_crumbs_env(tmp_path)
        import_file = tmp_path / "empty.jsonl"
        import_file.write_text("", encoding="utf-8")

        result = _run(["import", "--json", str(import_file)], cwd=tmp_path)

        assert result.returncode == 0
        parsed = json.loads(result.stdout)
        assert parsed["imported_count"] == 0

    def test_human_readable_unchanged_without_json_flag(self, tmp_path: Path) -> None:
        """crumb import without --json outputs human-readable 'imported N record(s)'."""
        _make_crumbs_env(tmp_path)
        import_file = self._write_jsonl(tmp_path, [
            {"id": "AF-1", "title": "Task", "status": "open", "type": "task"},
        ])

        result = _run(["import", str(import_file)], cwd=tmp_path)

        assert result.returncode == 0
        assert "imported" in result.stdout
        assert not result.stdout.strip().startswith("{")


class TestInitJSON:
    """Integration tests for 'crumb init --json' output."""

    def test_json_init_returns_path_and_status_initialized(self, tmp_path: Path) -> None:
        """crumb init --json returns object with 'path' and 'status': 'initialized'."""
        result = _run(["init", "--json"], cwd=tmp_path)

        assert result.returncode == 0, f"init --json failed: {result.stderr!r}"
        parsed = json.loads(result.stdout)
        assert "path" in parsed
        assert parsed["status"] == "initialized"
        assert parsed["path"].endswith(".crumbs")

    def test_json_init_already_exists_returns_already_exists_status(self, tmp_path: Path) -> None:
        """crumb init --json when .crumbs/ already exists returns 'already_exists' status."""
        _make_crumbs_env(tmp_path)  # create .crumbs/ first

        result = _run(["init", "--json"], cwd=tmp_path)

        assert result.returncode == 0
        parsed = json.loads(result.stdout)
        assert parsed["status"] == "already_exists"
        assert "path" in parsed

    def test_human_readable_unchanged_without_json_flag(self, tmp_path: Path) -> None:
        """crumb init without --json outputs human-readable init message."""
        result = _run(["init"], cwd=tmp_path)

        assert result.returncode == 0
        assert "Initialised" in result.stdout or "nothing to do" in result.stdout
        assert not result.stdout.strip().startswith("{")


class TestRenderTemplateJSON:
    """Integration tests for 'crumb render-template --json' output."""

    def _write_template(self, tmp_path: Path, content: str) -> Path:
        """Write a template file and return its path."""
        tmpl = tmp_path / "template.md"
        tmpl.write_text(content, encoding="utf-8")
        return tmpl

    def test_json_render_returns_content_field(self, tmp_path: Path) -> None:
        """crumb render-template --json returns object with 'content' field."""
        _make_crumbs_env(tmp_path)
        tmpl = self._write_template(tmp_path, "Hello {{NAME}}!")

        result = _run(
            ["render-template", "--json", "--slot", "NAME=World", str(tmpl)],
            cwd=tmp_path,
        )

        assert result.returncode == 0, f"render-template --json failed: {result.stderr!r}"
        parsed = json.loads(result.stdout)
        assert "content" in parsed
        assert parsed["content"] == "Hello World!"

    def test_json_render_no_slots(self, tmp_path: Path) -> None:
        """crumb render-template --json on template with no slots returns full content."""
        _make_crumbs_env(tmp_path)
        tmpl = self._write_template(tmp_path, "Static content\n")

        result = _run(["render-template", "--json", str(tmpl)], cwd=tmp_path)

        assert result.returncode == 0
        parsed = json.loads(result.stdout)
        assert parsed["content"] == "Static content\n"

    def test_human_readable_unchanged_without_json_flag(self, tmp_path: Path) -> None:
        """crumb render-template without --json writes rendered content directly to stdout."""
        _make_crumbs_env(tmp_path)
        tmpl = self._write_template(tmp_path, "Hello {{NAME}}!")

        result = _run(
            ["render-template", "--slot", "NAME=World", str(tmpl)],
            cwd=tmp_path,
        )

        assert result.returncode == 0
        assert result.stdout == "Hello World!"
        assert not result.stdout.strip().startswith("{")


class TestPruneJSON:
    """Integration tests for 'crumb prune --json' output."""

    def test_json_prune_returns_pruned_and_retained(self, tmp_path: Path) -> None:
        """crumb prune --json returns object with 'pruned' and 'retained' arrays."""
        _make_crumbs_env(tmp_path)

        result = _run(["prune", "--json", "--days", "0"], cwd=tmp_path)

        assert result.returncode == 0, f"prune --json failed: {result.stderr!r}"
        parsed = json.loads(result.stdout)
        assert "pruned" in parsed
        assert "retained" in parsed

    def test_json_prune_dry_run_has_dry_run_true(self, tmp_path: Path) -> None:
        """crumb prune --dry-run --json returns object with 'dry_run': true."""
        _make_crumbs_env(tmp_path)

        result = _run(["prune", "--json", "--dry-run"], cwd=tmp_path)

        assert result.returncode == 0
        parsed = json.loads(result.stdout)
        assert parsed.get("dry_run") is True

    def test_json_prune_nothing_to_prune_returns_empty_pruned(self, tmp_path: Path) -> None:
        """crumb prune --json with nothing to prune returns pruned=[]."""
        _make_crumbs_env(tmp_path)

        # Use --days 999 so nothing exceeds the threshold
        result = _run(["prune", "--json", "--days", "999"], cwd=tmp_path)

        assert result.returncode == 0
        parsed = json.loads(result.stdout)
        assert parsed["pruned"] == []

    def test_human_readable_unchanged_without_json_flag(self, tmp_path: Path) -> None:
        """crumb prune without --json outputs human-readable text."""
        _make_crumbs_env(tmp_path)

        result = _run(["prune", "--days", "0"], cwd=tmp_path)

        assert result.returncode == 0
        assert not result.stdout.strip().startswith("{")


# ---------------------------------------------------------------------------
# Helpers for validate-tdd tests
# ---------------------------------------------------------------------------


def _make_git_repo(base: Path) -> str:
    """Initialise a minimal git repo under *base* and return the root commit hash.

    Sets a local user.name and user.email so commits work in CI environments
    that have no global git config.  Creates a dummy initial commit so that
    subsequent commits always have a reachable parent for ``A..B`` ranges.

    Returns:
        The hash of the initial (root) commit.
    """
    subprocess.run(["git", "init", str(base)], check=True, capture_output=True)
    subprocess.run(
        ["git", "config", "user.email", "test@example.com"],
        cwd=str(base), check=True, capture_output=True,
    )
    subprocess.run(
        ["git", "config", "user.name", "Test User"],
        cwd=str(base), check=True, capture_output=True,
    )
    # Add a sentinel initial commit so every subsequent commit has a parent.
    return _git_add_commit(base, {".gitkeep": ""}, "initial commit")


def _git_add_commit(base: Path, files: dict, message: str) -> str:
    """Write *files* (name -> content), ``git add`` them, commit, and return the hash.

    Args:
        base: Working directory (must already be a git repo).
        files: Dict mapping relative filename to text content.
        message: Commit message.

    Returns:
        The full 40-char commit hash.
    """
    for name, content in files.items():
        fpath = base / name
        fpath.parent.mkdir(parents=True, exist_ok=True)
        fpath.write_text(content, encoding="utf-8")
        subprocess.run(
            ["git", "add", name], cwd=str(base), check=True, capture_output=True
        )
    subprocess.run(
        ["git", "commit", "-m", message],
        cwd=str(base), check=True, capture_output=True,
    )
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=str(base), check=True, capture_output=True, text=True,
    )
    return result.stdout.strip()


# ---------------------------------------------------------------------------
# TestValidateTDD
# ---------------------------------------------------------------------------


class TestValidateTDD:
    """Integration tests for ``crumb validate-tdd``."""

    # ------------------------------------------------------------------
    # AC-1 / AC-2 — basic PASS when tests appear before or with impl files
    # ------------------------------------------------------------------

    def test_pass_when_test_added_before_impl(self, tmp_path: Path) -> None:
        """validate-tdd exits 0 when test file is committed before implementation.

        Acceptance criterion: test files (test_*.* pattern) must appear before
        or in the same commit as implementation files; no violation when they do.
        """
        _make_crumbs_env(tmp_path)
        root = _make_git_repo(tmp_path)

        # Commit: test file only
        _git_add_commit(tmp_path, {"test_foo.py": "# test"}, "add test")
        # Commit: implementation file
        commit_impl = _git_add_commit(tmp_path, {"foo.py": "# impl"}, "add impl")

        result = _run(["validate-tdd", f"{root}..{commit_impl}"], cwd=tmp_path)

        assert result.returncode == 0, (
            f"Expected PASS when test precedes impl.\nstdout: {result.stdout!r}\nstderr: {result.stderr!r}"
        )
        assert "PASS" in result.stdout, f"Expected 'PASS' in output.\nstdout: {result.stdout!r}"

    def test_fail_when_impl_added_before_test(self, tmp_path: Path) -> None:
        """validate-tdd exits 1 when implementation file is committed before test.

        Acceptance criterion: ordering_violations is non-empty when impl precedes tests.
        """
        _make_crumbs_env(tmp_path)
        root = _make_git_repo(tmp_path)

        # Commit: implementation file (no test yet — violation)
        _git_add_commit(tmp_path, {"foo.py": "# impl"}, "add impl")
        # Commit: test file added later
        commit_test = _git_add_commit(tmp_path, {"test_foo.py": "# test"}, "add test")

        result = _run(["validate-tdd", f"{root}..{commit_test}"], cwd=tmp_path)

        assert result.returncode == 1, (
            f"Expected FAIL when impl precedes test.\nstdout: {result.stdout!r}\nstderr: {result.stderr!r}"
        )
        assert "FAIL" in result.stdout, f"Expected 'FAIL' in output.\nstdout: {result.stdout!r}"

    # ------------------------------------------------------------------
    # AC-2 — test file patterns recognised
    # ------------------------------------------------------------------

    def test_recognises_all_test_file_patterns(self, tmp_path: Path) -> None:
        """All four test-file patterns are recognised as test files.

        Acceptance criterion: *_test.*, test_*.*, *.spec.*, *.test.* are test files.
        """
        _make_crumbs_env(tmp_path)
        root = _make_git_repo(tmp_path)

        # Add all test-pattern files in the first commit, impl in second.
        _git_add_commit(
            tmp_path,
            {
                "foo_test.py": "# test",
                "test_bar.js": "// test",
                "baz.spec.ts": "// spec",
                "qux.test.ts": "// test",
            },
            "add tests",
        )
        commit_impl = _git_add_commit(
            tmp_path, {"impl.py": "# impl"}, "add impl"
        )

        result = _run(["validate-tdd", "--json", f"{root}..{commit_impl}"], cwd=tmp_path)

        assert result.returncode == 0, (
            f"Expected PASS.\nstdout: {result.stdout!r}\nstderr: {result.stderr!r}"
        )
        parsed = json.loads(result.stdout)
        test_file_paths = [e["file"] for e in parsed["test_files"]]
        assert "foo_test.py" in test_file_paths
        assert "test_bar.js" in test_file_paths
        assert "baz.spec.ts" in test_file_paths
        assert "qux.test.ts" in test_file_paths

    # ------------------------------------------------------------------
    # AC-3 — PASS when test and implementation added in the same commit
    # ------------------------------------------------------------------

    def test_pass_when_test_and_impl_in_same_commit(self, tmp_path: Path) -> None:
        """validate-tdd exits 0 when test and implementation files are in the same commit.

        Acceptance criterion: files added together in a single commit have no
        ordering violation because the test commit index equals the impl
        commit index.
        """
        _make_crumbs_env(tmp_path)
        root = _make_git_repo(tmp_path)

        # Add both test and implementation file in one commit.
        commit_both = _git_add_commit(
            tmp_path,
            {"test_widget.py": "# test", "widget.py": "# impl"},
            "add test and impl together",
        )

        result = _run(["validate-tdd", f"{root}..{commit_both}"], cwd=tmp_path)

        assert result.returncode == 0, (
            f"Expected PASS when test and impl are in the same commit.\n"
            f"stdout: {result.stdout!r}\nstderr: {result.stderr!r}"
        )
        assert "PASS" in result.stdout, (
            f"Expected 'PASS' in output.\nstdout: {result.stdout!r}"
        )

    # ------------------------------------------------------------------
    # AC-4 — tdd: false skips Check 5
    # ------------------------------------------------------------------

    def test_skips_when_tdd_false(self, tmp_path: Path) -> None:
        """validate-tdd exits 0 and prints SKIP when crumb has tdd: false.

        Acceptance criterion: when --crumb-id points to a crumb with tdd: false,
        the check is skipped (exit 0, no violation reported).
        """
        _make_crumbs_env(tmp_path)
        _make_git_repo(tmp_path)

        # Create a crumb with tdd: false.
        # crumb create prints "created AF-N"; extract just the ID.
        create_result = _run(
            ["create", "--title", "No TDD task", "--no-tdd"], cwd=tmp_path
        )
        assert create_result.returncode == 0
        crumb_id = create_result.stdout.strip().split()[-1]

        # The git range is irrelevant because tdd: false causes an early exit
        # before any git commands are run.
        result = _run(
            ["validate-tdd", "HEAD~1..HEAD", "--crumb-id", crumb_id],
            cwd=tmp_path,
        )

        assert result.returncode == 0, (
            f"Expected exit 0 (SKIP) for tdd: false.\nstdout: {result.stdout!r}\nstderr: {result.stderr!r}"
        )
        assert "SKIP" in result.stdout.upper(), (
            f"Expected SKIP in output.\nstdout: {result.stdout!r}"
        )

    # ------------------------------------------------------------------
    # AC-5 — --json returns structured result
    # ------------------------------------------------------------------

    def test_json_returns_structured_result(self, tmp_path: Path) -> None:
        """validate-tdd --json returns test_files, impl_files, ordering_violations.

        Acceptance criterion: structured JSON output contains all three arrays.
        """
        _make_crumbs_env(tmp_path)
        root = _make_git_repo(tmp_path)

        _git_add_commit(tmp_path, {"test_foo.py": "# test"}, "add test")
        commit_impl = _git_add_commit(tmp_path, {"foo.py": "# impl"}, "add impl")

        result = _run(
            ["validate-tdd", "--json", f"{root}..{commit_impl}"], cwd=tmp_path
        )

        assert result.returncode == 0, (
            f"Expected PASS.\nstdout: {result.stdout!r}\nstderr: {result.stderr!r}"
        )
        parsed = json.loads(result.stdout)
        assert "test_files" in parsed, "JSON must contain 'test_files'"
        assert "impl_files" in parsed, "JSON must contain 'impl_files'"
        assert "ordering_violations" in parsed, "JSON must contain 'ordering_violations'"
        assert isinstance(parsed["test_files"], list)
        assert isinstance(parsed["impl_files"], list)
        assert isinstance(parsed["ordering_violations"], list)

    def test_json_skipped_when_tdd_false(self, tmp_path: Path) -> None:
        """validate-tdd --json returns skipped:true when tdd: false.

        Acceptance criterion: JSON output includes 'skipped: true' and 'crumb_id'.
        """
        _make_crumbs_env(tmp_path)
        _make_git_repo(tmp_path)

        create_result = _run(
            ["create", "--title", "No TDD", "--no-tdd"], cwd=tmp_path
        )
        # crumb create prints "created AF-N"; extract just the ID.
        crumb_id = create_result.stdout.strip().split()[-1]

        # tdd: false causes early return before git is invoked — range irrelevant.
        result = _run(
            ["validate-tdd", "--json", "HEAD~1..HEAD", "--crumb-id", crumb_id],
            cwd=tmp_path,
        )

        assert result.returncode == 0
        parsed = json.loads(result.stdout)
        assert parsed.get("skipped") is True
        assert parsed.get("crumb_id") == crumb_id

    # ------------------------------------------------------------------
    # AC-6 — warns on merge commits
    # ------------------------------------------------------------------

    def test_warns_on_merge_commit(self, tmp_path: Path) -> None:
        """validate-tdd warns to stderr when a merge commit is in the range.

        Acceptance criterion: merge commits trigger a warning message.
        """
        _make_crumbs_env(tmp_path)
        root = _make_git_repo(tmp_path)

        # Commit on the default branch.
        main_commit = _git_add_commit(tmp_path, {"base.py": "# base"}, "base commit")

        # Create a feature branch from root and add a test file there.
        subprocess.run(
            ["git", "checkout", "-b", "feature", root],
            cwd=str(tmp_path), check=True, capture_output=True,
        )
        _git_add_commit(tmp_path, {"test_feature.py": "# test"}, "feature test")

        # Switch back to the default branch (use rev-parse to find its name).
        default_branch = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            cwd=str(tmp_path), capture_output=True, text=True,
        ).stdout.strip()
        # We're on feature; HEAD of default branch is main_commit
        subprocess.run(
            ["git", "checkout", main_commit],  # detached HEAD ok for test
            cwd=str(tmp_path), check=True, capture_output=True,
        )
        # Re-create default branch pointer and check it out
        r = subprocess.run(
            ["git", "branch", "--list"],
            cwd=str(tmp_path), capture_output=True, text=True,
        )
        branch_names = [b.strip().lstrip("* ") for b in r.stdout.splitlines()]
        # Determine original default branch name (master or main).
        orig_branch = next(
            (b for b in branch_names if b in ("master", "main")),
            branch_names[0] if branch_names else "master",
        )
        subprocess.run(
            ["git", "checkout", orig_branch],
            cwd=str(tmp_path), check=True, capture_output=True,
        )

        # Merge feature --no-ff to force a merge commit.
        subprocess.run(
            ["git", "merge", "--no-ff", "feature", "-m", "merge feature"],
            cwd=str(tmp_path), check=True, capture_output=True,
        )

        merge_commit = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=str(tmp_path), check=True, capture_output=True, text=True,
        ).stdout.strip()

        # Range from root to merge commit; merge commit is within the range.
        result = _run(
            ["validate-tdd", f"{root}..{merge_commit}"],
            cwd=tmp_path,
        )

        # The merge warning goes to stderr.
        assert "merge" in result.stderr.lower() or "merge" in result.stdout.lower(), (
            f"Expected merge warning.\nstdout: {result.stdout!r}\nstderr: {result.stderr!r}"
        )

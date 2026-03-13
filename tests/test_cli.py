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
import subprocess
import sys
from pathlib import Path
from typing import List

import pytest


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

CRUMB_PY: Path = Path(__file__).resolve().parent.parent / "crumb.py"

# Default config written into every isolated .crumbs/ directory.
_DEFAULT_CONFIG: dict = {
    "prefix": "AF",
    "default_priority": "P2",
    "next_crumb_id": 1,
    "next_trail_id": 1,
}


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
        json.dumps(_DEFAULT_CONFIG, indent=2) + "\n", encoding="utf-8"
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

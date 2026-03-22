"""Tests for all pure helper functions and infrastructure in crumb.py.

Tests are ordered to mirror the helper sections in crumb.py:
  die, find_crumbs_dir, read_config, write_config,
  read_tasks, write_tasks, FileLock, cleanup_stale_tmp_files,
  now_iso, _priority_sort_key, _status_sort_key.
"""

from __future__ import annotations

import json
import os
import re
import time
from pathlib import Path

import pytest

import crumb
from crumb import (
    FileLock,
    _priority_sort_key,
    _status_sort_key,
    cleanup_stale_tmp_files,
    die,
    find_crumbs_dir,
    now_iso,
    read_config,
    read_tasks,
    write_config,
    write_tasks,
)


# ---------------------------------------------------------------------------
# die
# ---------------------------------------------------------------------------


def test_die_raises_system_exit(capsys: pytest.CaptureFixture[str]) -> None:
    """die() must raise SystemExit with the given code."""
    with pytest.raises(SystemExit) as exc_info:
        die("something went wrong")
    assert exc_info.value.code == 1


def test_die_default_exit_code(capsys: pytest.CaptureFixture[str]) -> None:
    """die() default exit code is 1."""
    with pytest.raises(SystemExit) as exc_info:
        die("msg")
    assert exc_info.value.code == 1


def test_die_custom_exit_code(capsys: pytest.CaptureFixture[str]) -> None:
    """die() respects a custom exit code."""
    with pytest.raises(SystemExit) as exc_info:
        die("msg", code=42)
    assert exc_info.value.code == 42


def test_die_stderr_message(capsys: pytest.CaptureFixture[str]) -> None:
    """die() prints 'error: <message>' to stderr."""
    with pytest.raises(SystemExit):
        die("something went wrong")
    captured = capsys.readouterr()
    assert captured.err.strip() == "error: something went wrong"


def test_die_no_stdout(capsys: pytest.CaptureFixture[str]) -> None:
    """die() does not print to stdout."""
    with pytest.raises(SystemExit):
        die("quiet")
    captured = capsys.readouterr()
    assert captured.out == ""


# ---------------------------------------------------------------------------
# find_crumbs_dir
# ---------------------------------------------------------------------------


def test_find_crumbs_dir_discovers_directory(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """find_crumbs_dir returns the .crumbs/ directory when found by walking up."""
    crumbs_dir = tmp_path / ".crumbs"
    crumbs_dir.mkdir()
    # Change cwd to tmp_path so the walk-up starts there
    monkeypatch.chdir(tmp_path)
    result = find_crumbs_dir()
    assert result == crumbs_dir


def test_find_crumbs_dir_walks_up(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """find_crumbs_dir walks up parent directories to find .crumbs/."""
    crumbs_dir = tmp_path / ".crumbs"
    crumbs_dir.mkdir()
    subdir = tmp_path / "a" / "b" / "c"
    subdir.mkdir(parents=True)
    monkeypatch.chdir(subdir)
    result = find_crumbs_dir()
    assert result == crumbs_dir


def test_find_crumbs_dir_exits_when_missing(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """find_crumbs_dir raises SystemExit when no .crumbs/ exists in any ancestor."""
    # Use a directory with no .crumbs/ present
    monkeypatch.chdir(tmp_path)
    with pytest.raises(SystemExit):
        find_crumbs_dir()


# ---------------------------------------------------------------------------
# read_config
# ---------------------------------------------------------------------------


def test_read_config_returns_expected_dict(crumbs_env: Path) -> None:
    """read_config returns a dict with all expected keys and values."""
    config = read_config()
    assert config["prefix"] == "AF"
    assert config["default_priority"] == "P2"
    assert config["next_crumb_id"] == 1
    assert config["next_trail_id"] == 1


def test_read_config_returns_dict_type(crumbs_env: Path) -> None:
    """read_config returns a plain dict."""
    config = read_config()
    assert isinstance(config, dict)


def test_read_config_missing_file_returns_defaults(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """read_config returns DEFAULT_CONFIG when config.json does not exist."""
    crumbs_dir = tmp_path / ".crumbs"
    crumbs_dir.mkdir()
    monkeypatch.setattr(crumb, "find_crumbs_dir", lambda: crumbs_dir)
    config = read_config()
    assert config["prefix"] == crumb.DEFAULT_CONFIG["prefix"]
    assert config["next_crumb_id"] == crumb.DEFAULT_CONFIG["next_crumb_id"]


def test_read_config_coerces_ids_to_int(crumbs_env: Path) -> None:
    """read_config coerces next_crumb_id and next_trail_id to int."""
    config_file = crumbs_env / "config.json"
    data = {"prefix": "X", "default_priority": "P1", "next_crumb_id": "5", "next_trail_id": "3"}
    config_file.write_text(json.dumps(data), encoding="utf-8")
    config = read_config()
    assert config["next_crumb_id"] == 5
    assert isinstance(config["next_crumb_id"], int)
    assert config["next_trail_id"] == 3
    assert isinstance(config["next_trail_id"], int)


# ---------------------------------------------------------------------------
# write_config
# ---------------------------------------------------------------------------


def test_write_config_persists_data(crumbs_env: Path) -> None:
    """write_config writes data that read_config can subsequently re-read."""
    original = read_config()
    original["next_crumb_id"] = 99
    original["prefix"] = "TEST"
    write_config(original)
    result = read_config()
    assert result["next_crumb_id"] == 99
    assert result["prefix"] == "TEST"


def test_write_config_creates_valid_json(crumbs_env: Path) -> None:
    """write_config produces a valid JSON file."""
    config = read_config()
    config["next_crumb_id"] = 7
    write_config(config)
    raw = (crumbs_env / "config.json").read_text(encoding="utf-8")
    parsed = json.loads(raw)
    assert parsed["next_crumb_id"] == 7


def test_write_config_atomic_no_leftover_tmp(crumbs_env: Path) -> None:
    """write_config removes the .tmp file after a successful write."""
    config = read_config()
    write_config(config)
    tmp_files = list(crumbs_env.glob("*.tmp"))
    assert tmp_files == []


# ---------------------------------------------------------------------------
# read_tasks
# ---------------------------------------------------------------------------


def test_read_tasks_empty_file_returns_empty_list(crumbs_env: Path) -> None:
    """read_tasks returns an empty list for an empty JSONL file."""
    tasks_file = crumbs_env / "tasks.jsonl"
    result = read_tasks(tasks_file)
    assert result == []


def test_read_tasks_returns_list(crumbs_env: Path) -> None:
    """read_tasks always returns a list."""
    tasks_file = crumbs_env / "tasks.jsonl"
    result = read_tasks(tasks_file)
    assert isinstance(result, list)


def test_read_tasks_parses_records(crumbs_env: Path) -> None:
    """read_tasks returns a list of dicts parsed from JSONL."""
    tasks_file = crumbs_env / "tasks.jsonl"
    records = [
        {"id": "AF-1", "title": "First task", "status": "open"},
        {"id": "AF-2", "title": "Second task", "status": "closed"},
    ]
    tasks_file.write_text(
        "\n".join(json.dumps(r) for r in records) + "\n",
        encoding="utf-8",
    )
    result = read_tasks(tasks_file)
    assert len(result) == 2
    assert result[0]["id"] == "AF-1"
    assert result[1]["id"] == "AF-2"


def test_read_tasks_skips_blank_lines(crumbs_env: Path) -> None:
    """read_tasks skips blank lines without raising an error."""
    tasks_file = crumbs_env / "tasks.jsonl"
    tasks_file.write_text(
        '{"id": "AF-1"}\n\n{"id": "AF-2"}\n',
        encoding="utf-8",
    )
    result = read_tasks(tasks_file)
    assert len(result) == 2


# ---------------------------------------------------------------------------
# write_tasks
# ---------------------------------------------------------------------------


def test_write_tasks_atomic_no_leftover_tmp(crumbs_env: Path) -> None:
    """write_tasks removes the .tmp file after a successful write."""
    tasks_file = crumbs_env / "tasks.jsonl"
    write_tasks(tasks_file, [])
    tmp_files = list(crumbs_env.glob("*.tmp"))
    assert tmp_files == []


def test_write_tasks_readable_by_read_tasks(crumbs_env: Path) -> None:
    """write_tasks writes records that read_tasks can re-read correctly."""
    tasks_file = crumbs_env / "tasks.jsonl"
    records = [
        {"id": "AF-1", "title": "Alpha", "status": "open"},
        {"id": "AF-2", "title": "Beta", "status": "in_progress"},
    ]
    write_tasks(tasks_file, records)
    result = read_tasks(tasks_file)
    assert result == records


def test_write_tasks_overwrites_existing(crumbs_env: Path) -> None:
    """write_tasks replaces all existing records in the file."""
    tasks_file = crumbs_env / "tasks.jsonl"
    write_tasks(tasks_file, [{"id": "AF-1"}])
    write_tasks(tasks_file, [{"id": "AF-2"}])
    result = read_tasks(tasks_file)
    assert len(result) == 1
    assert result[0]["id"] == "AF-2"


def test_write_tasks_empty_list(crumbs_env: Path) -> None:
    """write_tasks with an empty list produces an empty (or blank) file."""
    tasks_file = crumbs_env / "tasks.jsonl"
    tasks_file.write_text('{"id": "AF-1"}\n', encoding="utf-8")
    write_tasks(tasks_file, [])
    result = read_tasks(tasks_file)
    assert result == []


# ---------------------------------------------------------------------------
# FileLock
# ---------------------------------------------------------------------------


def test_file_lock_handle_is_set_while_held(crumbs_env: Path) -> None:
    """FileLock sets _lock_file to a non-None handle while the lock is held."""
    with FileLock() as lock:
        assert lock._lock_file is not None


def test_file_lock_handle_is_cleared_after_release(crumbs_env: Path) -> None:
    """FileLock sets _lock_file to None after __exit__ is called."""
    with FileLock() as lock:
        pass
    assert lock._lock_file is None


def test_file_lock_creates_lock_file(crumbs_env: Path) -> None:
    """FileLock creates the tasks.lock file if it does not exist."""
    lock_file = crumbs_env / "tasks.lock"
    assert not lock_file.exists()
    with FileLock():
        assert lock_file.exists()


def test_file_lock_releases_on_exit(crumbs_env: Path) -> None:
    """FileLock releases so a second acquisition succeeds after the first."""
    with FileLock():
        pass
    # If the lock were not released, this second context manager would deadlock
    with FileLock():
        pass


# ---------------------------------------------------------------------------
# cleanup_stale_tmp_files
# ---------------------------------------------------------------------------


def test_cleanup_stale_removes_tmp_files(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """cleanup_stale_tmp_files removes .tmp files from the .crumbs directory."""
    crumbs_dir = tmp_path / ".crumbs"
    crumbs_dir.mkdir()
    tmp_file = crumbs_dir / "tasks.jsonl.tmp"
    tmp_file.write_text("leftover", encoding="utf-8")
    # Backdate mtime so the file is considered stale (older than threshold)
    old_time = time.time() - 10
    os.utime(tmp_file, (old_time, old_time))
    monkeypatch.chdir(tmp_path)
    cleanup_stale_tmp_files()
    assert not tmp_file.exists()


def test_cleanup_stale_leaves_non_tmp_files(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """cleanup_stale_tmp_files does not remove non-.tmp files."""
    crumbs_dir = tmp_path / ".crumbs"
    crumbs_dir.mkdir()
    normal_file = crumbs_dir / "tasks.jsonl"
    normal_file.write_text("data", encoding="utf-8")
    monkeypatch.chdir(tmp_path)
    cleanup_stale_tmp_files()
    assert normal_file.exists()


def test_cleanup_stale_no_crumbs_dir_is_silent(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """cleanup_stale_tmp_files does nothing (no error) when no .crumbs/ exists."""
    # tmp_path has no .crumbs/ subdirectory
    monkeypatch.chdir(tmp_path)
    # Should not raise
    cleanup_stale_tmp_files()


def test_cleanup_stale_removes_multiple_tmp_files(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """cleanup_stale_tmp_files removes all .tmp files."""
    crumbs_dir = tmp_path / ".crumbs"
    crumbs_dir.mkdir()
    files = [crumbs_dir / f"file{i}.tmp" for i in range(3)]
    # Backdate mtime so files are considered stale (older than threshold)
    old_time = time.time() - 10
    for f in files:
        f.write_text("stale", encoding="utf-8")
        os.utime(f, (old_time, old_time))
    monkeypatch.chdir(tmp_path)
    cleanup_stale_tmp_files()
    for f in files:
        assert not f.exists()


# ---------------------------------------------------------------------------
# now_iso
# ---------------------------------------------------------------------------


def test_now_iso_returns_string() -> None:
    """now_iso returns a string."""
    result = now_iso()
    assert isinstance(result, str)


def test_now_iso_format() -> None:
    """now_iso returns a string in YYYY-MM-DDTHH:MM:SSZ format."""
    result = now_iso()
    # Pattern: 2026-03-13T15:30:00Z
    pattern = r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$"
    assert re.match(pattern, result), f"now_iso() returned unexpected format: {result!r}"


def test_now_iso_ends_with_z() -> None:
    """now_iso returns a string ending with 'Z' (UTC indicator)."""
    result = now_iso()
    assert result.endswith("Z")


# ---------------------------------------------------------------------------
# _priority_sort_key
# ---------------------------------------------------------------------------


def test_priority_sort_key_p0() -> None:
    """_priority_sort_key returns 0 for P0."""
    assert _priority_sort_key("P0") == 0


def test_priority_sort_key_p1() -> None:
    """_priority_sort_key returns 1 for P1."""
    assert _priority_sort_key("P1") == 1


def test_priority_sort_key_p2() -> None:
    """_priority_sort_key returns 2 for P2."""
    assert _priority_sort_key("P2") == 2


def test_priority_sort_key_p3() -> None:
    """_priority_sort_key returns 3 for P3."""
    assert _priority_sort_key("P3") == 3


def test_priority_sort_key_p4() -> None:
    """_priority_sort_key returns 4 for P4."""
    assert _priority_sort_key("P4") == 4


def test_priority_sort_key_unknown_sorts_last() -> None:
    """_priority_sort_key returns 5 for strings that don't match the PX pattern.

    Note: the implementation returns int(priority[1]) for any two-char string
    starting with 'P' followed by a digit, so 'P9' returns 9. Only strings
    that do not match len==2, priority[0]=='P', digit at [1] return 5.
    """
    assert _priority_sort_key("unknown") == 5
    assert _priority_sort_key("") == 5
    assert _priority_sort_key("INVALID") == 5


def test_priority_sort_key_ordering() -> None:
    """_priority_sort_key produces ascending order P0 < P1 < ... < P4 < unknown."""
    priorities = ["P4", "P1", "unknown", "P0", "P3", "P2"]
    sorted_priorities = sorted(priorities, key=_priority_sort_key)
    assert sorted_priorities[:5] == ["P0", "P1", "P2", "P3", "P4"]
    assert sorted_priorities[5] == "unknown"


# ---------------------------------------------------------------------------
# _status_sort_key
# ---------------------------------------------------------------------------


def test_status_sort_key_open() -> None:
    """_status_sort_key returns 0 for open."""
    assert _status_sort_key("open") == 0


def test_status_sort_key_in_progress() -> None:
    """_status_sort_key returns 1 for in_progress."""
    assert _status_sort_key("in_progress") == 1


def test_status_sort_key_closed() -> None:
    """_status_sort_key returns 2 for closed."""
    assert _status_sort_key("closed") == 2


def test_status_sort_key_unknown_sorts_last() -> None:
    """_status_sort_key returns 3 for unknown strings (sorts last)."""
    assert _status_sort_key("unknown") == 3
    assert _status_sort_key("") == 3
    assert _status_sort_key("PENDING") == 3


def test_status_sort_key_ordering() -> None:
    """_status_sort_key produces ascending order open < in_progress < closed < unknown."""
    statuses = ["closed", "unknown", "in_progress", "open"]
    sorted_statuses = sorted(statuses, key=_status_sort_key)
    assert sorted_statuses == ["open", "in_progress", "closed", "unknown"]

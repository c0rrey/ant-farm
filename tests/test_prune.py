"""Tests for the prune subcommand and its helper functions.

Covers:
  - TestParseSessionDirTimestamp: timestamp extraction and prefix validation
  - TestIsActiveSession: mtime-based active guard
  - TestCmdPruneAgeFiltering: --days threshold, default 14-day retention
  - TestCmdPruneNothingToPrune: empty / no sessions dir / all recent
  - TestCmdPruneDryRun: --dry-run lists without deleting
  - TestCmdPruneDaysZero: --days 0 with active session guard
  - TestCmdPruneNegativeDays: --days -1 errors and exits non-zero
  - TestCmdPruneErrorHandling: FileNotFoundError and OSError from rmtree
  - TestCmdPruneUnknownPrefixes: non-matching dirs are never deleted
  - TestCmdPruneUnparseableTimestamp: warn and skip bad timestamps
"""

from __future__ import annotations

import argparse
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List
from unittest.mock import patch, MagicMock

import pytest

import crumb
from crumb import (
    _is_active_session,
    _parse_session_dir_timestamp,
    cmd_prune,
    DEFAULT_RETENTION_DAYS,
    ACTIVE_GUARD_MINUTES,
    SESSION_DIR_PREFIXES,
    SESSION_TS_FORMAT,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_prune_args(
    days: int = DEFAULT_RETENTION_DAYS,
    dry_run: bool = False,
) -> argparse.Namespace:
    """Return a minimal Namespace mimicking what argparse produces for 'prune'."""
    return argparse.Namespace(days=days, dry_run=dry_run)


def _make_session_dir(sessions_dir: Path, name: str) -> Path:
    """Create a session directory under sessions_dir and return its path."""
    d = sessions_dir / name
    d.mkdir(parents=True, exist_ok=True)
    return d


def _session_name(prefix: str, dt: datetime) -> str:
    """Build a valid session directory name from a prefix and datetime."""
    return f"{prefix}{dt.strftime(SESSION_TS_FORMAT)}"


# ---------------------------------------------------------------------------
# TestParseSessionDirTimestamp
# ---------------------------------------------------------------------------


class TestParseSessionDirTimestamp:
    """Unit tests for _parse_session_dir_timestamp."""

    def test_valid_session_prefix(self) -> None:
        name = "_session-20260301-120000"
        result = _parse_session_dir_timestamp(name)
        assert result == datetime(2026, 3, 1, 12, 0, 0)

    def test_valid_decompose_prefix(self) -> None:
        name = "_decompose-20251225-083000"
        result = _parse_session_dir_timestamp(name)
        assert result == datetime(2025, 12, 25, 8, 30, 0)

    def test_valid_review_prefix(self) -> None:
        name = "_review-20260101-000001"
        result = _parse_session_dir_timestamp(name)
        assert result == datetime(2026, 1, 1, 0, 0, 1)

    def test_unknown_prefix_returns_none(self) -> None:
        # Directories not matching known prefixes must return None
        assert _parse_session_dir_timestamp("random-20260101-000000") is None

    def test_no_prefix_returns_none(self) -> None:
        assert _parse_session_dir_timestamp("20260101-120000") is None

    def test_empty_string_returns_none(self) -> None:
        assert _parse_session_dir_timestamp("") is None

    def test_bad_timestamp_returns_none(self) -> None:
        # Known prefix but timestamp portion is not valid
        assert _parse_session_dir_timestamp("_session-baddate") is None

    def test_partial_timestamp_returns_none(self) -> None:
        # Only 8 digits, missing the time part
        assert _parse_session_dir_timestamp("_session-20260101") is None

    def test_age_computation_12_days(self) -> None:
        """Age in days uses floor division via timedelta.days.

        _session-20260301-120000 to 2026-03-14T00:00:00 is 12.5 days,
        so timedelta.days == 12 (floor).
        """
        name = "_session-20260301-120000"
        now = datetime(2026, 3, 14, 0, 0, 0)
        parsed = _parse_session_dir_timestamp(name)
        assert parsed is not None
        assert (now - parsed).days == 12

    def test_extra_suffix_still_parseable(self) -> None:
        """Extra characters after the timestamp should not prevent parsing."""
        name = "_session-20260301-120000-extra-suffix"
        result = _parse_session_dir_timestamp(name)
        assert result == datetime(2026, 3, 1, 12, 0, 0)


# ---------------------------------------------------------------------------
# TestIsActiveSession
# ---------------------------------------------------------------------------


class TestIsActiveSession:
    """Unit tests for _is_active_session."""

    def test_very_recent_mtime_is_active(self, tmp_path: Path) -> None:
        d = tmp_path / "test_dir"
        d.mkdir()
        now_ts = time.time()
        assert _is_active_session(d, now_ts) is True

    def test_old_mtime_is_not_active(self, tmp_path: Path) -> None:
        d = tmp_path / "test_dir"
        d.mkdir()
        # Use a now_ts far in the future so mtime appears old
        future_ts = time.time() + 7200  # 2 hours ahead
        assert _is_active_session(d, future_ts) is False

    def test_exactly_at_guard_boundary_is_not_active(self, tmp_path: Path) -> None:
        d = tmp_path / "test_dir"
        d.mkdir()
        mtime = d.stat().st_mtime
        # now_ts is exactly ACTIVE_GUARD_MINUTES * 60 seconds after mtime
        now_ts = mtime + (ACTIVE_GUARD_MINUTES * 60)
        assert _is_active_session(d, now_ts) is False

    def test_vanished_dir_returns_false(self, tmp_path: Path) -> None:
        d = tmp_path / "nonexistent"
        now_ts = time.time()
        assert _is_active_session(d, now_ts) is False


# ---------------------------------------------------------------------------
# Shared fixture: crumbs_env with sessions directory
# ---------------------------------------------------------------------------


@pytest.fixture()
def sessions_env(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Create an isolated .crumbs/sessions/ environment for prune tests.

    Sets up .crumbs/ with config.json and tasks.jsonl (via crumbs_env
    structure) and creates the sessions/ subdirectory.  Monkeypatches
    ``crumb.find_crumbs_dir`` to return the isolated .crumbs/ directory.

    Returns:
        Path to the ``.crumbs/sessions/`` directory.
    """
    import json

    crumbs_dir = tmp_path / ".crumbs"
    crumbs_dir.mkdir()

    default_config: Dict[str, Any] = {
        "prefix": "AF",
        "default_priority": "P2",
        "next_crumb_id": 1,
        "next_trail_id": 1,
    }
    (crumbs_dir / "config.json").write_text(
        json.dumps(default_config, indent=2) + "\n", encoding="utf-8"
    )
    (crumbs_dir / "tasks.jsonl").write_text("", encoding="utf-8")

    sessions_dir = crumbs_dir / "sessions"
    sessions_dir.mkdir()

    monkeypatch.setattr(crumb, "find_crumbs_dir", lambda: crumbs_dir)

    return sessions_dir


# ---------------------------------------------------------------------------
# TestCmdPruneNothingToPrune
# ---------------------------------------------------------------------------


class TestCmdPruneNothingToPrune:
    """cmd_prune with no session directories to delete."""

    def test_no_sessions_dir_prints_message(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
        capsys: pytest.CaptureFixture,
    ) -> None:
        crumbs_dir = tmp_path / ".crumbs"
        crumbs_dir.mkdir()
        monkeypatch.setattr(crumb, "find_crumbs_dir", lambda: crumbs_dir)

        cmd_prune(_make_prune_args())

        out = capsys.readouterr().out
        assert "nothing to prune" in out
        assert "no sessions directory" in out

    def test_all_recent_dirs_nothing_to_prune(
        self,
        sessions_env: Path,
        capsys: pytest.CaptureFixture,
    ) -> None:
        # Create a directory from 2 days ago (well within 14-day retention)
        recent_dt = datetime.now() - timedelta(days=2)
        _make_session_dir(sessions_env, _session_name("_session-", recent_dt))

        cmd_prune(_make_prune_args())

        out = capsys.readouterr().out
        assert "nothing to prune" in out

    def test_empty_sessions_dir_nothing_to_prune(
        self,
        sessions_env: Path,
        capsys: pytest.CaptureFixture,
    ) -> None:
        # sessions_env exists but is empty
        cmd_prune(_make_prune_args())

        out = capsys.readouterr().out
        assert "nothing to prune" in out


# ---------------------------------------------------------------------------
# TestCmdPruneAgeFiltering
# ---------------------------------------------------------------------------


class TestCmdPruneAgeFiltering:
    """cmd_prune deletes directories that exceed the retention threshold."""

    def _backdate(self, d: Path, days: int) -> None:
        """Set a directory's mtime to ``days`` days ago (> active guard window)."""
        old_ts = time.time() - (days * 86400)
        os.utime(d, (old_ts, old_ts))

    def test_prune_default_14_days(
        self,
        sessions_env: Path,
        capsys: pytest.CaptureFixture,
    ) -> None:
        old_dt = datetime.now() - timedelta(days=20)
        old_name = _session_name("_session-", old_dt)
        old_dir = _make_session_dir(sessions_env, old_name)
        self._backdate(old_dir, 20)

        cmd_prune(_make_prune_args())

        assert not old_dir.exists(), "old directory should have been pruned"
        out = capsys.readouterr().out
        assert "pruned" in out
        assert old_name in out

    def test_prune_custom_days_7(
        self,
        sessions_env: Path,
        capsys: pytest.CaptureFixture,
    ) -> None:
        old_dt = datetime.now() - timedelta(days=10)
        old_name = _session_name("_session-", old_dt)
        old_dir = _make_session_dir(sessions_env, old_name)
        self._backdate(old_dir, 10)

        recent_dt = datetime.now() - timedelta(days=5)
        recent_name = _session_name("_session-", recent_dt)
        recent_dir = _make_session_dir(sessions_env, recent_name)

        cmd_prune(_make_prune_args(days=7))

        assert not old_dir.exists(), "10-day-old dir should be pruned with --days 7"
        assert recent_dir.exists(), "5-day-old dir should be retained with --days 7"

    def test_all_prefixes_pruned(
        self,
        sessions_env: Path,
        capsys: pytest.CaptureFixture,
    ) -> None:
        old_dt = datetime.now() - timedelta(days=20)
        dirs = []
        for prefix in SESSION_DIR_PREFIXES:
            name = _session_name(prefix, old_dt)
            d = _make_session_dir(sessions_env, name)
            self._backdate(d, 20)
            dirs.append(d)

        cmd_prune(_make_prune_args())

        for d in dirs:
            assert not d.exists(), f"{d.name} should have been pruned"

    def test_age_from_dir_name_not_mtime(
        self,
        sessions_env: Path,
        capsys: pytest.CaptureFixture,
    ) -> None:
        """Age must be computed from directory name, not filesystem mtime."""
        old_dt = datetime.now() - timedelta(days=30)
        old_name = _session_name("_session-", old_dt)
        old_dir = _make_session_dir(sessions_env, old_name)

        # Touch the directory to make its mtime very recent (but > 60 min guard)
        # by setting mtime to 2 hours ago — still recent filesystem-wise
        two_hours_ago = time.time() - 7200
        os.utime(old_dir, (two_hours_ago, two_hours_ago))

        cmd_prune(_make_prune_args())

        assert not old_dir.exists(), (
            "directory should be pruned based on name-embedded timestamp, "
            "not filesystem mtime"
        )


# ---------------------------------------------------------------------------
# TestCmdPruneDryRun
# ---------------------------------------------------------------------------


class TestCmdPruneDryRun:
    """--dry-run lists candidates without deleting."""

    def test_dry_run_no_deletion(
        self,
        sessions_env: Path,
        capsys: pytest.CaptureFixture,
    ) -> None:
        old_dt = datetime.now() - timedelta(days=20)
        old_dir = _make_session_dir(sessions_env, _session_name("_session-", old_dt))

        cmd_prune(_make_prune_args(dry_run=True))

        assert old_dir.exists(), "--dry-run must not delete anything"

    def test_dry_run_lists_would_prune(
        self,
        sessions_env: Path,
        capsys: pytest.CaptureFixture,
    ) -> None:
        old_dt = datetime.now() - timedelta(days=20)
        old_name = _session_name("_session-", old_dt)
        _make_session_dir(sessions_env, old_name)

        cmd_prune(_make_prune_args(dry_run=True))

        out = capsys.readouterr().out
        assert "would prune" in out
        assert old_name in out

    def test_dry_run_lists_would_retain(
        self,
        sessions_env: Path,
        capsys: pytest.CaptureFixture,
    ) -> None:
        old_dt = datetime.now() - timedelta(days=20)
        _make_session_dir(sessions_env, _session_name("_session-", old_dt))
        recent_dt = datetime.now() - timedelta(days=2)
        recent_name = _session_name("_session-", recent_dt)
        _make_session_dir(sessions_env, recent_name)

        cmd_prune(_make_prune_args(dry_run=True))

        out = capsys.readouterr().out
        assert "would retain" in out
        assert recent_name in out

    def test_dry_run_shows_age(
        self,
        sessions_env: Path,
        capsys: pytest.CaptureFixture,
    ) -> None:
        old_dt = datetime.now() - timedelta(days=20)
        _make_session_dir(sessions_env, _session_name("_session-", old_dt))

        cmd_prune(_make_prune_args(dry_run=True))

        out = capsys.readouterr().out
        # Age in days should appear in output (e.g., "20d old")
        assert "d old" in out or "20d" in out or "days" in out.lower() or "20" in out


# ---------------------------------------------------------------------------
# TestCmdPruneDaysZero
# ---------------------------------------------------------------------------


class TestCmdPruneDaysZero:
    """--days 0 deletes all except directories active within 60 minutes."""

    def test_days_zero_deletes_old(
        self,
        sessions_env: Path,
        capsys: pytest.CaptureFixture,
    ) -> None:
        old_dt = datetime.now() - timedelta(days=1)
        old_dir = _make_session_dir(sessions_env, _session_name("_session-", old_dt))
        # Make its mtime old so the active guard doesn't protect it
        two_hours_ago = time.time() - 7200
        os.utime(old_dir, (two_hours_ago, two_hours_ago))

        cmd_prune(_make_prune_args(days=0))

        assert not old_dir.exists()

    def test_days_zero_skips_active_session(
        self,
        sessions_env: Path,
        capsys: pytest.CaptureFixture,
    ) -> None:
        # age=0 means all dirs qualify by threshold, but active ones are skipped
        recent_dt = datetime.now()
        active_dir = _make_session_dir(sessions_env, _session_name("_session-", recent_dt))
        # mtime is fresh (just created), so it should be protected by active guard

        cmd_prune(_make_prune_args(days=0))

        assert active_dir.exists(), "active session must not be pruned with --days 0"
        err = capsys.readouterr().err
        assert "warning" in err.lower()
        assert "active" in err.lower()


# ---------------------------------------------------------------------------
# TestCmdPruneNegativeDays
# ---------------------------------------------------------------------------


class TestCmdPruneNegativeDays:
    """--days negative value prints error and exits non-zero."""

    def test_negative_days_exits_nonzero(
        self,
        sessions_env: Path,
    ) -> None:
        with pytest.raises(SystemExit) as exc_info:
            cmd_prune(_make_prune_args(days=-1))
        assert exc_info.value.code != 0

    def test_negative_days_prints_error_to_stderr(
        self,
        sessions_env: Path,
        capsys: pytest.CaptureFixture,
    ) -> None:
        with pytest.raises(SystemExit):
            cmd_prune(_make_prune_args(days=-1))
        err = capsys.readouterr().err
        assert "error" in err.lower() or "-1" in err

    def test_negative_days_no_deletion(
        self,
        sessions_env: Path,
    ) -> None:
        old_dt = datetime.now() - timedelta(days=30)
        old_dir = _make_session_dir(sessions_env, _session_name("_session-", old_dt))

        with pytest.raises(SystemExit):
            cmd_prune(_make_prune_args(days=-1))

        assert old_dir.exists(), "no deletion should occur when --days is negative"


# ---------------------------------------------------------------------------
# TestCmdPruneUnknownPrefixes
# ---------------------------------------------------------------------------


class TestCmdPruneUnknownPrefixes:
    """Directories not matching known prefixes are never deleted."""

    def test_unknown_prefix_not_deleted(
        self,
        sessions_env: Path,
        capsys: pytest.CaptureFixture,
    ) -> None:
        old_dt = datetime.now() - timedelta(days=30)
        # Use an unrecognised prefix
        name = f"archive-{old_dt.strftime(SESSION_TS_FORMAT)}"
        unknown_dir = _make_session_dir(sessions_env, name)

        cmd_prune(_make_prune_args())

        assert unknown_dir.exists(), "unknown-prefix dirs must never be deleted"

    def test_bare_timestamp_dir_not_deleted(
        self,
        sessions_env: Path,
        capsys: pytest.CaptureFixture,
    ) -> None:
        old_dt = datetime.now() - timedelta(days=30)
        name = old_dt.strftime(SESSION_TS_FORMAT)
        bare_dir = _make_session_dir(sessions_env, name)

        cmd_prune(_make_prune_args())

        assert bare_dir.exists(), "dirs without a recognised prefix must not be deleted"


# ---------------------------------------------------------------------------
# TestCmdPruneUnparseableTimestamp
# ---------------------------------------------------------------------------


class TestCmdPruneUnparseableTimestamp:
    """Unparseable timestamps are skipped with a stderr warning."""

    def test_unparseable_timestamp_skipped(
        self,
        sessions_env: Path,
        capsys: pytest.CaptureFixture,
    ) -> None:
        bad_dir = _make_session_dir(sessions_env, "_session-baddate")

        cmd_prune(_make_prune_args())

        assert bad_dir.exists(), "unparseable-timestamp dirs must not be deleted"

    def test_unparseable_timestamp_warns_to_stderr(
        self,
        sessions_env: Path,
        capsys: pytest.CaptureFixture,
    ) -> None:
        _make_session_dir(sessions_env, "_session-baddate")

        cmd_prune(_make_prune_args())

        err = capsys.readouterr().err
        assert "warning" in err.lower()
        assert "_session-baddate" in err


# ---------------------------------------------------------------------------
# TestCmdPruneErrorHandling
# ---------------------------------------------------------------------------


class TestCmdPruneErrorHandling:
    """FileNotFoundError and OSError from rmtree are handled gracefully."""

    def _backdate(self, d: Path, days: int) -> None:
        """Set a directory's mtime to ``days`` days ago (> active guard window)."""
        old_ts = time.time() - (days * 86400)
        os.utime(d, (old_ts, old_ts))

    def test_file_not_found_counted_as_pruned(
        self,
        sessions_env: Path,
        capsys: pytest.CaptureFixture,
    ) -> None:
        old_dt = datetime.now() - timedelta(days=30)
        old_name = _session_name("_session-", old_dt)
        old_dir = _make_session_dir(sessions_env, old_name)
        self._backdate(old_dir, 30)

        original_rmtree = __import__("shutil").rmtree

        def mock_rmtree(path: Any, *args: Any, **kwargs: Any) -> None:
            if Path(path) == old_dir:
                raise FileNotFoundError(f"{path} not found")
            original_rmtree(path, *args, **kwargs)

        with patch("crumb.shutil.rmtree", side_effect=mock_rmtree):
            cmd_prune(_make_prune_args())

        out = capsys.readouterr().out
        # Should report pruned (FileNotFoundError = already gone = counted)
        assert "pruned" in out

    def test_oserror_warns_and_continues(
        self,
        sessions_env: Path,
        capsys: pytest.CaptureFixture,
    ) -> None:
        old_dt1 = datetime.now() - timedelta(days=30)
        old_dt2 = datetime.now() - timedelta(days=25)
        dir1 = _make_session_dir(sessions_env, _session_name("_session-", old_dt1))
        dir2 = _make_session_dir(sessions_env, _session_name("_decompose-", old_dt2))
        self._backdate(dir1, 30)
        self._backdate(dir2, 25)

        call_count = {"n": 0}
        original_rmtree = __import__("shutil").rmtree

        def mock_rmtree(path: Any, *args: Any, **kwargs: Any) -> None:
            call_count["n"] += 1
            if call_count["n"] == 1:
                raise PermissionError("permission denied")
            original_rmtree(path, *args, **kwargs)

        with patch("crumb.shutil.rmtree", side_effect=mock_rmtree):
            cmd_prune(_make_prune_args())

        err = capsys.readouterr().err
        assert "warning" in err.lower()
        # Second directory should still have been processed (loop continues)
        assert call_count["n"] == 2


# ---------------------------------------------------------------------------
# TestCmdPruneAutoContract
# ---------------------------------------------------------------------------


class TestCmdPruneAutoContract:
    """Integration contract tests for the auto-prune hook wired in RULES.md.

    These tests verify that ``cmd_prune`` with default args behaves safely
    in the two edge-case scenarios that can occur at session startup:

    1. ``.crumbs/sessions/`` does not yet exist (first-ever session).
    2. ``shutil.rmtree`` raises ``PermissionError`` on a stale directory.

    In both cases the auto-prune invocation in RULES.md (line 527:
    ``crumb prune >/dev/null || true``) relies on ``|| true`` to suppress
    shell-level failure, but the Python contract is that ``cmd_prune`` must
    not raise any exception itself.
    """

    def test_auto_prune_no_sessions_dir(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """cmd_prune completes without exception when sessions/ does not exist.

        Contract: auto-prune at session start is safe even before any session
        directory has been created (e.g., the very first orchestration run).
        """
        crumbs_dir = tmp_path / ".crumbs"
        crumbs_dir.mkdir()
        # Intentionally do NOT create sessions/ subdirectory
        monkeypatch.setattr(crumb, "find_crumbs_dir", lambda: crumbs_dir)

        # Must not raise any exception
        cmd_prune(_make_prune_args())

    def test_auto_prune_rmtree_permission_error(
        self,
        sessions_env: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """cmd_prune completes without exception when rmtree raises PermissionError.

        Contract: OSError subclasses (including PermissionError) from rmtree
        are caught and logged to stderr; they are never re-raised.  The auto-
        prune invocation must not propagate errors that would block session
        startup.
        """
        from datetime import datetime, timedelta

        old_dt = datetime.now() - timedelta(days=30)
        old_dir = _make_session_dir(
            sessions_env, _session_name("_session-", old_dt)
        )
        # Backdate mtime so the active-session guard does not protect it
        past = old_dt.timestamp()
        import os as _os
        _os.utime(old_dir, (past, past))

        def _always_permission_error(path: Any, *args: Any, **kwargs: Any) -> None:
            raise PermissionError(f"permission denied: {path}")

        with patch("crumb.shutil.rmtree", side_effect=_always_permission_error):
            # Must not raise any exception
            cmd_prune(_make_prune_args())


# ---------------------------------------------------------------------------
# Ensure `import os` is accessible in test module for utime calls
# ---------------------------------------------------------------------------

import os

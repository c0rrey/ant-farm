"""Shared pytest fixtures for crumb.py test suite.

All tests that interact with crumb's filesystem layer should use the
``crumbs_env`` fixture, which monkeypatches ``crumb.find_crumbs_dir`` so
no test ever touches a real ``.crumbs/`` directory on disk.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

import pytest

import crumb


@pytest.fixture()
def crumbs_env(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Create an isolated .crumbs/ environment under tmp_path.

    Sets up:
    - ``tmp_path/.crumbs/`` directory
    - ``config.json`` with default config values
    - ``tasks.jsonl`` as an empty file

    Monkeypatches ``crumb.find_crumbs_dir`` so all crumb functions that
    call it will use the isolated directory instead of walking the real cwd.

    Args:
        tmp_path: pytest-provided temporary directory (function-scoped).
        monkeypatch: pytest monkeypatch fixture.

    Returns:
        Path to the isolated ``.crumbs/`` directory.
    """
    crumbs_dir: Path = tmp_path / ".crumbs"
    crumbs_dir.mkdir()

    # Write default config.json
    default_config: Dict[str, Any] = {
        "prefix": "AF",
        "default_priority": "P2",
        "next_crumb_id": 1,
        "next_trail_id": 1,
    }
    config_file = crumbs_dir / "config.json"
    config_file.write_text(json.dumps(default_config, indent=2) + "\n", encoding="utf-8")

    # Write empty tasks.jsonl
    tasks_file = crumbs_dir / "tasks.jsonl"
    tasks_file.write_text("", encoding="utf-8")

    # Monkeypatch find_crumbs_dir to return our isolated directory
    monkeypatch.setattr(crumb, "find_crumbs_dir", lambda: crumbs_dir)

    return crumbs_dir

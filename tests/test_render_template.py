"""Tests for the render-template subcommand and render_template() core function.

Tests are split into two classes:

- ``TestRenderTemplateFunction`` — unit tests for the ``render_template()``
  function, exercising validation and expansion logic in isolation (no
  subprocess, no filesystem I/O, no .crumbs/ required).

- ``TestRenderTemplateCLI`` — integration tests that invoke ``crumb.py`` as a
  real subprocess, covering the end-to-end CLI path including file I/O, exit
  codes, and stderr messages.

Acceptance criteria verified:
  1. Basic substitution with one or more slots.
  2. Missing slot exits 1 with ``error: missing slot: <NAME>`` to stderr.
  3. Extra slot exits 1 with ``error: extra slot: <NAME>`` to stderr.
  4. Single-pass expansion (slot values containing ``{{...}}`` are not re-expanded).
  5. Slots inside fenced code blocks are expanded identically to slots elsewhere.
  6. Nonexistent template file exits 1 with ``error: template not found: ...`` to stderr.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from typing import Dict

import pytest

import crumb
from crumb import render_template


# ---------------------------------------------------------------------------
# Helpers shared by both test classes
# ---------------------------------------------------------------------------

CRUMB_PY: Path = Path(__file__).resolve().parent.parent / "crumb.py"


def _run_cli(*args: str, cwd: Path) -> subprocess.CompletedProcess[str]:
    """Invoke ``crumb.py`` as a subprocess and return the result.

    Args:
        *args: Arguments passed to ``crumb.py`` (excluding the script path).
        cwd: Working directory.  For ``render-template`` this can be any
             directory; the command does not require a ``.crumbs/`` dir.

    Returns:
        ``subprocess.CompletedProcess`` with ``stdout`` and ``stderr`` as
        decoded strings and ``returncode`` set.
    """
    return subprocess.run(
        [sys.executable, str(CRUMB_PY), *args],
        capture_output=True,
        text=True,
        cwd=str(cwd),
    )


# ---------------------------------------------------------------------------
# Unit tests — render_template() function
# ---------------------------------------------------------------------------


class TestRenderTemplateFunction:
    """Unit tests for ``crumb.render_template()``."""

    # --- happy path ---

    def test_single_slot_replaced(self) -> None:
        """A single ``{{FOO}}`` placeholder is replaced with the provided value."""
        result = render_template("Hello {{FOO}}!", {"FOO": "world"})
        assert result == "Hello world!"

    def test_multiple_slots_replaced(self) -> None:
        """Multiple distinct ``{{SLOT}}`` placeholders are all replaced."""
        result = render_template("{{A}} and {{B}}", {"A": "alpha", "B": "beta"})
        assert result == "alpha and beta"

    def test_slot_replaced_multiple_times(self) -> None:
        """The same slot appearing more than once is replaced at every occurrence."""
        result = render_template("{{X}} {{X}} {{X}}", {"X": "go"})
        assert result == "go go go"

    def test_no_slots_empty_dict(self) -> None:
        """A template with no placeholders and an empty slot dict is returned as-is."""
        result = render_template("no placeholders here", {})
        assert result == "no placeholders here"

    def test_multiline_template(self) -> None:
        """Slots are expanded correctly in multi-line templates."""
        template = "line1\n{{SLOT}}\nline3"
        result = render_template(template, {"SLOT": "replaced"})
        assert result == "line1\nreplaced\nline3"

    def test_slot_value_with_newlines(self) -> None:
        """Slot values containing newlines are inserted verbatim."""
        template = "before\n{{BODY}}\nafter"
        result = render_template(template, {"BODY": "line a\nline b"})
        assert result == "before\nline a\nline b\nafter"

    def test_slot_inside_fenced_code_block(self) -> None:
        """Slots inside fenced code blocks are expanded (criterion 5)."""
        template = "```\n{{CMD}}\n```"
        result = render_template(template, {"CMD": "git status"})
        assert result == "```\ngit status\n```"

    # --- single-pass guarantee ---

    def test_single_pass_no_recursive_expansion(self) -> None:
        """A slot value containing ``{{OTHER}}`` is NOT further expanded (criterion 4)."""
        # {{A}} is provided; {{B}} is intentionally absent from slots.
        # If expansion were multi-pass, {{B}} would need to be present.
        # Single-pass means {{B}} inside the value of A is emitted literally.
        result = render_template("{{A}}", {"A": "{{B}}"})
        assert result == "{{B}}"

    def test_single_pass_self_referential_slot_value(self) -> None:
        """A slot value containing the same slot name is not re-expanded."""
        result = render_template("{{X}}", {"X": "{{X}}"})
        assert result == "{{X}}"

    # --- validation errors: missing slots ---

    def test_missing_slot_raises_systemexit(self) -> None:
        """Template containing ``{{MISSING}}`` with no matching key calls die() (criterion 2)."""
        with pytest.raises(SystemExit) as exc_info:
            render_template("{{MISSING}}", {})
        assert exc_info.value.code == 1

    def test_missing_slot_error_message(self, capsys: pytest.CaptureFixture[str]) -> None:
        """Missing slot prints ``error: missing slot: NAME`` to stderr (criterion 2)."""
        with pytest.raises(SystemExit):
            render_template("{{GONE}}", {})
        captured = capsys.readouterr()
        assert "missing slot: GONE" in captured.err

    def test_first_missing_slot_reported(self, capsys: pytest.CaptureFixture[str]) -> None:
        """When multiple slots are missing, the first one found in template order is reported."""
        # Template has {{A}} first, then {{B}}; neither is supplied.
        with pytest.raises(SystemExit):
            render_template("{{A}} and {{B}}", {})
        captured = capsys.readouterr()
        # The first missing slot (A) should appear in the error message.
        assert "missing slot: A" in captured.err

    # --- validation errors: extra slots ---

    def test_extra_slot_raises_systemexit(self) -> None:
        """Providing a slot that does not appear in the template calls die() (criterion 3)."""
        with pytest.raises(SystemExit) as exc_info:
            render_template("no slots here", {"EXTRA": "unused"})
        assert exc_info.value.code == 1

    def test_extra_slot_error_message(self, capsys: pytest.CaptureFixture[str]) -> None:
        """Extra slot prints ``error: extra slot: NAME`` to stderr (criterion 3)."""
        with pytest.raises(SystemExit):
            render_template("no slots here", {"EXTRA": "unused"})
        captured = capsys.readouterr()
        assert "extra slot: EXTRA" in captured.err

    def test_extra_slot_when_template_has_other_slots(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Extra slot is detected even when the template uses other slots correctly."""
        with pytest.raises(SystemExit):
            render_template("{{A}}", {"A": "ok", "EXTRA": "bad"})
        captured = capsys.readouterr()
        assert "extra slot: EXTRA" in captured.err

    # --- edge cases ---

    def test_slot_name_with_digits_and_underscores(self) -> None:
        """Slot names with digits and underscores are recognised and expanded."""
        result = render_template("{{FOO_BAR_2}}", {"FOO_BAR_2": "baz"})
        assert result == "baz"

    def test_lowercase_placeholder_not_treated_as_slot(self) -> None:
        """``{{lowercase}}`` is NOT a valid slot and is left unexpanded."""
        # No slots provided, no slots detected — should succeed.
        result = render_template("{{lowercase}} text", {})
        assert result == "{{lowercase}} text"

    def test_empty_template(self) -> None:
        """Empty template with empty slots returns empty string."""
        result = render_template("", {})
        assert result == ""


# ---------------------------------------------------------------------------
# Integration tests — render-template CLI subcommand
# ---------------------------------------------------------------------------


class TestRenderTemplateCLI:
    """End-to-end tests for ``crumb render-template`` invoked via subprocess."""

    def test_basic_substitution_exits_zero(self, tmp_path: Path) -> None:
        """``crumb render-template`` with matching slots exits 0 (criterion 1)."""
        tmpl = tmp_path / "t.md"
        tmpl.write_text("Hello {{FOO}}!", encoding="utf-8")

        result = _run_cli("render-template", str(tmpl), "--slot", "FOO=bar", cwd=tmp_path)

        assert result.returncode == 0, (
            f"Expected exit 0, got {result.returncode}.\n"
            f"stdout: {result.stdout!r}\nstderr: {result.stderr!r}"
        )

    def test_basic_substitution_output(self, tmp_path: Path) -> None:
        """Rendered output is written to stdout with placeholders replaced (criterion 1)."""
        tmpl = tmp_path / "t.md"
        tmpl.write_text("{{FOO}} and {{BAZ}}", encoding="utf-8")

        result = _run_cli(
            "render-template", str(tmpl), "--slot", "FOO=bar", "--slot", "BAZ=qux",
            cwd=tmp_path,
        )

        assert result.returncode == 0
        assert result.stdout == "bar and qux"

    def test_missing_slot_exits_one(self, tmp_path: Path) -> None:
        """Missing slot exits 1 (criterion 2)."""
        tmpl = tmp_path / "t.md"
        tmpl.write_text("{{MISSING}}", encoding="utf-8")

        result = _run_cli("render-template", str(tmpl), cwd=tmp_path)

        assert result.returncode == 1

    def test_missing_slot_stderr_message(self, tmp_path: Path) -> None:
        """Missing slot prints ``error: missing slot: MISSING`` to stderr (criterion 2)."""
        tmpl = tmp_path / "t.md"
        tmpl.write_text("{{MISSING}}", encoding="utf-8")

        result = _run_cli("render-template", str(tmpl), cwd=tmp_path)

        assert "error: missing slot: MISSING" in result.stderr

    def test_extra_slot_exits_one(self, tmp_path: Path) -> None:
        """Extra slot (not in template) exits 1 (criterion 3)."""
        tmpl = tmp_path / "t.md"
        tmpl.write_text("no placeholders", encoding="utf-8")

        result = _run_cli("render-template", str(tmpl), "--slot", "EXTRA=val", cwd=tmp_path)

        assert result.returncode == 1

    def test_extra_slot_stderr_message(self, tmp_path: Path) -> None:
        """Extra slot prints ``error: extra slot: EXTRA`` to stderr (criterion 3)."""
        tmpl = tmp_path / "t.md"
        tmpl.write_text("no placeholders", encoding="utf-8")

        result = _run_cli("render-template", str(tmpl), "--slot", "EXTRA=val", cwd=tmp_path)

        assert "error: extra slot: EXTRA" in result.stderr

    def test_single_pass_no_recursive_expansion(self, tmp_path: Path) -> None:
        """Slot value containing ``{{OTHER}}`` is not further expanded (criterion 4)."""
        tmpl = tmp_path / "t.md"
        tmpl.write_text("{{A}}", encoding="utf-8")

        result = _run_cli("render-template", str(tmpl), "--slot", "A={{B}}", cwd=tmp_path)

        assert result.returncode == 0
        assert result.stdout == "{{B}}"

    def test_slots_in_fenced_code_blocks_expanded(self, tmp_path: Path) -> None:
        """Slots inside fenced code blocks are expanded (criterion 5)."""
        tmpl = tmp_path / "t.md"
        tmpl.write_text("```\n{{CMD}}\n```", encoding="utf-8")

        result = _run_cli("render-template", str(tmpl), "--slot", "CMD=git status", cwd=tmp_path)

        assert result.returncode == 0
        assert result.stdout == "```\ngit status\n```"

    def test_nonexistent_template_exits_one(self, tmp_path: Path) -> None:
        """Nonexistent template file exits 1 (criterion 6)."""
        result = _run_cli(
            "render-template", "no-such-file.md", "--slot", "A=B", cwd=tmp_path
        )
        assert result.returncode == 1

    def test_nonexistent_template_stderr_message(self, tmp_path: Path) -> None:
        """Nonexistent template prints ``error: template not found: ...`` to stderr (criterion 6)."""
        result = _run_cli(
            "render-template", "no-such-file.md", "--slot", "A=B", cwd=tmp_path
        )
        assert "error: template not found: no-such-file.md" in result.stderr

    def test_no_slots_no_placeholders_exits_zero(self, tmp_path: Path) -> None:
        """Template with no placeholders and no ``--slot`` args exits 0."""
        tmpl = tmp_path / "t.md"
        tmpl.write_text("plain text\nno slots", encoding="utf-8")

        result = _run_cli("render-template", str(tmpl), cwd=tmp_path)

        assert result.returncode == 0
        assert result.stdout == "plain text\nno slots"

    def test_multiline_slot_value_via_equals(self, tmp_path: Path) -> None:
        """A slot value containing an ``=`` sign (after the first ``=``) is handled correctly."""
        tmpl = tmp_path / "t.md"
        tmpl.write_text("{{EQ}}", encoding="utf-8")

        # --slot EQ=a=b — value is "a=b" (partition on first '=')
        result = _run_cli("render-template", str(tmpl), "--slot", "EQ=a=b", cwd=tmp_path)

        assert result.returncode == 0
        assert result.stdout == "a=b"

    def test_does_not_require_crumbs_dir(self, tmp_path: Path) -> None:
        """``render-template`` works without a ``.crumbs/`` directory present."""
        # tmp_path has no .crumbs/ — confirm render-template still succeeds.
        assert not (tmp_path / ".crumbs").exists()
        tmpl = tmp_path / "t.md"
        tmpl.write_text("{{X}}", encoding="utf-8")

        result = _run_cli("render-template", str(tmpl), "--slot", "X=ok", cwd=tmp_path)

        assert result.returncode == 0
        assert result.stdout == "ok"

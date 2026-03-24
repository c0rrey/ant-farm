"""Structural integrity tests for the ant-farm orchestration system.

Covers nine categories:
1. Cross-reference integrity — every subagent_type string in RULES.md,
   RULES-decompose.md, RULES-review.md, and RULES-lite.md resolves to an
   agent file.
2. Frontmatter validity — every agents/*.md file has ``name``,
   ``description``, and ``tools`` YAML fields, and ``name`` matches the
   filename stem.
3. Checkpoint completeness — every orchestration/templates/checkpoints/*.md
   file (except common.md) contains at least one PASS, WARN, or FAIL verdict
   keyword.
4. Glossary coverage — every agent filename stem appears in
   orchestration/GLOSSARY.md.
5. Template slot coverage — every {UPPERCASE} slot in the skeleton templates
   processed by build-review-prompts.sh has a corresponding --slot KEY= call
   in that script.
6. Skill file mapping — every skill file path referenced in orchestration
   templates exists on disk.
7. Hook file existence — required hook scripts under hooks/ exist on disk.
8. TDD enforcement integration — claims-vs-code.md contains the
   ``crumb validate-tdd`` command reference, the ``tdd: false`` opt-out
   field, and the required JSON output keys.
9. PRD import template placeholders — orchestration/templates/prd-import.md
   contains the expected {UPPERCASE} placeholder patterns.

All tests are self-contained: stdlib only, no external dependencies, no LLM
calls.  The full suite should complete in well under 2 seconds.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

# ---------------------------------------------------------------------------
# Repo-root resolution
# ---------------------------------------------------------------------------

# This file lives at tests/test_orchestration.py.  One level up is the repo
# root.
REPO_ROOT: Path = Path(__file__).parent.parent

AGENTS_DIR: Path = REPO_ROOT / "agents"
CHECKPOINTS_DIR: Path = REPO_ROOT / "orchestration" / "templates" / "checkpoints"
GLOSSARY_FILE: Path = REPO_ROOT / "orchestration" / "GLOSSARY.md"

RULES_FILES: list[Path] = [
    REPO_ROOT / "orchestration" / "RULES.md",
    REPO_ROOT / "orchestration" / "RULES-decompose.md",
    REPO_ROOT / "orchestration" / "RULES-review.md",
    REPO_ROOT / "orchestration" / "RULES-lite.md",
]

# Regex that matches the Python-style agent spawn syntax used in RULES files:
#   subagent_type="ant-farm-something"
#   subagent_type='ant-farm-something'
_SUBAGENT_TYPE_RE: re.Pattern[str] = re.compile(
    r'subagent_type\s*=\s*["\']([^"\']+)["\']'
)

# Regex for a YAML frontmatter block at the very start of a file.
# Group 1 captures everything between the opening and closing ``---`` fences.
_FRONTMATTER_RE: re.Pattern[str] = re.compile(
    r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL
)

# YAML key-value: ``key: value`` (value may be empty).
_YAML_FIELD_RE: re.Pattern[str] = re.compile(r"^(\w[\w-]*)\s*:", re.MULTILINE)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _extract_frontmatter_fields(content: str) -> set[str]:
    """Return the set of top-level YAML field names from a frontmatter block.

    Args:
        content: Full text of a markdown file.

    Returns:
        Set of field name strings found in the frontmatter, or an empty set
        if no valid frontmatter block exists.
    """
    match = _FRONTMATTER_RE.match(content)
    if not match:
        return set()
    return set(_YAML_FIELD_RE.findall(match.group(1)))


def _extract_frontmatter_value(content: str, field: str) -> str | None:
    """Return the value of a specific YAML field from frontmatter.

    Args:
        content: Full text of a markdown file.
        field: The field name to look up (e.g. ``"name"``).

    Returns:
        The stripped value string, or ``None`` if the field is absent or the
        frontmatter block does not exist.
    """
    match = _FRONTMATTER_RE.match(content)
    if not match:
        return None
    block = match.group(1)
    field_match = re.search(
        rf"^{re.escape(field)}\s*:\s*(.+)$", block, re.MULTILINE
    )
    if not field_match:
        return None
    return field_match.group(1).strip()


# ---------------------------------------------------------------------------
# Test 1: Cross-reference integrity
# ---------------------------------------------------------------------------

# Agent names that appear in RULES files as code-block examples rather than
# real agent references.  These are excluded from the cross-reference check.
# Example: RULES-lite.md uses ``subagent_type="ant-farm-general-purpose"``
# with the comment ``# or the agent type matching the task`` — it is a
# placeholder, not a concrete agent file that must exist on disk.
_EXAMPLE_AGENT_NAMES: frozenset[str] = frozenset({"ant-farm-general-purpose"})


def test_cross_reference_integrity() -> None:
    """Every subagent_type string in RULES files must match an agent file.

    Parses ``subagent_type="..."`` patterns from RULES.md,
    RULES-decompose.md, RULES-review.md, and RULES-lite.md.  For each
    unique agent name found, asserts that ``agents/<name>.md`` exists in the
    repository.

    Agent names listed in ``_EXAMPLE_AGENT_NAMES`` are excluded — these
    appear in code-block examples (e.g. RULES-lite.md's ``# or the agent
    type matching the task`` comment) and are not real agent references.
    """
    referenced: set[str] = set()
    for rules_file in RULES_FILES:
        text = rules_file.read_text(encoding="utf-8")
        referenced.update(_SUBAGENT_TYPE_RE.findall(text))

    assert referenced, (
        "No subagent_type references found in RULES files — "
        "the extraction regex may be broken."
    )

    missing: list[str] = []
    for agent_name in sorted(referenced):
        if agent_name in _EXAMPLE_AGENT_NAMES:
            continue
        agent_path = AGENTS_DIR / f"{agent_name}.md"
        if not agent_path.exists():
            missing.append(agent_name)

    assert not missing, (
        "The following subagent_type values in RULES files have no matching "
        f"agent file under agents/:\n"
        + "\n".join(f"  - {name}  (expected agents/{name}.md)" for name in missing)
    )


# ---------------------------------------------------------------------------
# Test 2: Frontmatter validity
# ---------------------------------------------------------------------------

_REQUIRED_FRONTMATTER_FIELDS: frozenset[str] = frozenset(
    {"name", "description", "tools"}
)


def _collect_agent_files() -> list[Path]:
    return sorted(AGENTS_DIR.glob("*.md"))


@pytest.mark.parametrize("agent_file", _collect_agent_files(), ids=lambda p: p.name)
def test_frontmatter_validity(agent_file: Path) -> None:
    """Every agents/*.md file must have valid frontmatter with required fields.

    Checks:
    - A YAML frontmatter block (``--- ... ---``) exists at the top of the file.
    - The fields ``name``, ``description``, and ``tools`` are all present.
    - The ``name`` field value equals the file's stem (filename without ``.md``).

    Args:
        agent_file: Path to the agent markdown file under test.
    """
    content = agent_file.read_text(encoding="utf-8")

    # Must have frontmatter
    assert _FRONTMATTER_RE.match(content), (
        f"{agent_file.name}: no YAML frontmatter block found "
        "(expected ``--- ... ---`` at top of file)"
    )

    fields = _extract_frontmatter_fields(content)
    missing_fields = _REQUIRED_FRONTMATTER_FIELDS - fields
    assert not missing_fields, (
        f"{agent_file.name}: missing required frontmatter field(s): "
        f"{sorted(missing_fields)}"
    )

    # name field must match filename stem
    name_value = _extract_frontmatter_value(content, "name")
    expected_name = agent_file.stem
    assert name_value == expected_name, (
        f"{agent_file.name}: frontmatter ``name`` field is {name_value!r} "
        f"but expected {expected_name!r} (must match filename without .md)"
    )


# ---------------------------------------------------------------------------
# Test 3: Checkpoint completeness
# ---------------------------------------------------------------------------

_VERDICT_RE: re.Pattern[str] = re.compile(r"\b(PASS|WARN|FAIL)\b")


def _collect_non_common_checkpoints() -> list[Path]:
    return sorted(
        p for p in CHECKPOINTS_DIR.glob("*.md") if p.name != "common.md"
    )


@pytest.mark.parametrize(
    "checkpoint_file",
    _collect_non_common_checkpoints(),
    ids=lambda p: p.name,
)
def test_checkpoint_completeness(checkpoint_file: Path) -> None:
    """Every checkpoint file (except common.md) must contain verdict keywords.

    Asserts that at least one occurrence of ``PASS``, ``WARN``, or ``FAIL``
    appears as a whole word in the checkpoint file.

    Args:
        checkpoint_file: Path to the checkpoint markdown file under test.
    """
    content = checkpoint_file.read_text(encoding="utf-8")
    assert _VERDICT_RE.search(content), (
        f"{checkpoint_file.name}: no PASS, WARN, or FAIL verdict keyword found. "
        "Checkpoint files (except common.md) must define verdict criteria."
    )


# ---------------------------------------------------------------------------
# Test 4: Glossary coverage
# ---------------------------------------------------------------------------

# Regex that matches brace expansion patterns used in the glossary, e.g.:
#   ant-farm-reviewer-{clarity,edge-cases,correctness,drift}
# Group 1: prefix before the brace, group 2: comma-separated alternatives.
_BRACE_EXPAND_RE: re.Pattern[str] = re.compile(r"([\w-]+)\{([^}]+)\}")


def _expand_brace_notation(text: str) -> str:
    """Expand shell-style brace notation into individual tokens.

    Transforms patterns like ``ant-farm-reviewer-{clarity,edge-cases}`` into
    the space-separated tokens ``ant-farm-reviewer-clarity ant-farm-reviewer-edge-cases``
    so that a simple ``in`` membership check on the resulting string works.

    Args:
        text: Raw text that may contain brace-expansion patterns.

    Returns:
        The text with brace patterns replaced by their expanded alternatives.
    """

    def _replace(match: re.Match[str]) -> str:
        prefix = match.group(1)
        alternatives = match.group(2).split(",")
        return " ".join(f"{prefix}{alt.strip()}" for alt in alternatives)

    return _BRACE_EXPAND_RE.sub(_replace, text)


def test_glossary_coverage() -> None:
    """Every agent filename stem must appear in orchestration/GLOSSARY.md.

    Reads GLOSSARY.md and checks that each ``agents/*.md`` stem (the agent's
    logical name, e.g. ``ant-farm-recon-planner``) is mentioned at least
    once.  Brace expansion patterns (e.g.
    ``ant-farm-reviewer-{clarity,edge-cases,correctness,drift}``) are expanded
    before the membership check so that compact glossary entries covering
    multiple agent variants are handled correctly.

    Adding an agent without updating the glossary (either as a direct name
    reference or within an appropriate brace pattern) causes this test to fail.
    """
    raw_glossary = GLOSSARY_FILE.read_text(encoding="utf-8")
    # Expand brace notation so "ant-farm-reviewer-{clarity,...}" is treated
    # as individual name occurrences.
    glossary_text = _expand_brace_notation(raw_glossary)

    agent_files = sorted(AGENTS_DIR.glob("*.md"))

    assert agent_files, f"No agent files found under {AGENTS_DIR}"

    uncovered: list[str] = []
    for agent_file in agent_files:
        stem = agent_file.stem
        if stem not in glossary_text:
            uncovered.append(stem)

    assert not uncovered, (
        "The following agent filenames are not mentioned in "
        f"{GLOSSARY_FILE.relative_to(REPO_ROOT)}:\n"
        + "\n".join(f"  - {name}" for name in uncovered)
    )


# ---------------------------------------------------------------------------
# Test 5: Template slot coverage
# ---------------------------------------------------------------------------

TEMPLATES_DIR: Path = REPO_ROOT / "orchestration" / "templates"
BUILD_SCRIPT: Path = REPO_ROOT / "scripts" / "build-review-prompts.sh"

# Skeleton templates whose slots are filled by build-review-prompts.sh.
# Only these two are processed by that script; the other *-skeleton.md files
# are used directly by the Orchestrator/Planner without going through this script.
_BUILD_SCRIPT_SKELETONS: tuple[str, ...] = (
    "reviewer-skeleton.md",
    "review-consolidator-skeleton.md",
)

# Matches single-brace UPPERCASE placeholders used in skeleton templates,
# e.g. {REVIEW_TYPE}, {DATA_FILE_PATH}.  Excludes lowercase and mixed-case
# tokens which are prose or code examples, not template slots.
_SINGLE_BRACE_SLOT_RE: re.Pattern[str] = re.compile(r"\{([A-Z][A-Z_0-9]*)\}")

# Matches --slot "KEY= or --slot 'KEY= patterns in shell scripts.
_SHELL_SLOT_KEY_RE: re.Pattern[str] = re.compile(
    r'--slot\s+["\']([A-Z][A-Z_0-9]*)='
)


def _extract_agent_section(content: str) -> str:
    """Return the agent-facing section of a skeleton template.

    Skeleton templates contain an instruction block for the operator followed
    by the agent-facing template body, separated by a ``---`` line.  Only the
    agent-facing section contains real slot placeholders; the instruction block
    may contain example ``{PLACEHOLDER}`` tokens that are not actual slots.

    Args:
        content: Full text of a skeleton markdown file.

    Returns:
        Everything after the first bare ``---`` separator line, or the full
        content if no such separator is found (conservative fallback).
    """
    # Split on the first occurrence of a line that is exactly "---" (with
    # optional surrounding whitespace).  The separator may appear anywhere in
    # the first ~40 lines; we only want what follows it.
    separator = re.compile(r"^---\s*$", re.MULTILINE)
    match = separator.search(content)
    if match:
        return content[match.end():]
    # No separator found — return the full content as a safe fallback so the
    # test still catches real slots even in malformed templates.
    return content


def _collect_skeleton_slots(skeleton_path: Path) -> set[str]:
    """Extract all {UPPERCASE} slot names from a skeleton's agent-facing section.

    Args:
        skeleton_path: Absolute path to a ``*-skeleton.md`` file.

    Returns:
        Set of uppercase slot name strings (without braces).
    """
    content = skeleton_path.read_text(encoding="utf-8")
    agent_section = _extract_agent_section(content)
    return set(_SINGLE_BRACE_SLOT_RE.findall(agent_section))


def _collect_script_slot_keys(script_path: Path) -> set[str]:
    """Extract all --slot KEY= keys defined in a shell script.

    Args:
        script_path: Absolute path to the shell script.

    Returns:
        Set of slot key name strings found in ``--slot "KEY=..."`` calls.
    """
    content = script_path.read_text(encoding="utf-8")
    return set(_SHELL_SLOT_KEY_RE.findall(content))


def test_template_slot_coverage() -> None:
    """Every {UPPERCASE} slot in build-review-prompts.sh skeletons must be filled.

    Scans ``reviewer-skeleton.md`` and ``big-head-skeleton.md`` — the two
    skeleton templates processed by ``scripts/build-review-prompts.sh`` — for
    ``{UPPERCASE}`` placeholder tokens in their agent-facing sections.  Each
    such slot must have a corresponding ``--slot "KEY=`` call somewhere in the
    script.

    This test will fail if a new ``{ORPHAN_SLOT}`` is added to a skeleton
    without a matching ``--slot "ORPHAN_SLOT=`` in the script, which is the
    intended contract.

    AC-1: passes when every slot has a fill.
    AC-4: fails when an orphan slot is introduced.
    """
    assert BUILD_SCRIPT.exists(), (
        f"build-review-prompts.sh not found at {BUILD_SCRIPT}. "
        "Has the script been moved or renamed?"
    )

    script_keys: set[str] = _collect_script_slot_keys(BUILD_SCRIPT)

    assert script_keys, (
        f"No --slot KEY= patterns found in {BUILD_SCRIPT.name}. "
        "The slot-extraction regex may be broken, or the script no longer "
        "uses crumb render-template."
    )

    orphan_slots: list[str] = []
    for skeleton_name in _BUILD_SCRIPT_SKELETONS:
        skeleton_path = TEMPLATES_DIR / skeleton_name
        assert skeleton_path.exists(), (
            f"Expected skeleton template not found: {skeleton_path}. "
            "Update _BUILD_SCRIPT_SKELETONS if the filename changed."
        )
        slots = _collect_skeleton_slots(skeleton_path)
        for slot in sorted(slots):
            if slot not in script_keys:
                orphan_slots.append(f"{skeleton_name}: {{{slot}}}")

    assert not orphan_slots, (
        "The following template slots have no corresponding --slot KEY= call "
        f"in {BUILD_SCRIPT.name}:\n"
        + "\n".join(f"  - {entry}" for entry in sorted(orphan_slots))
        + "\n\nFor each orphan slot, add a --slot \"KEY=...\" argument to "
        "the relevant crumb render-template call in build-review-prompts.sh."
    )


# ---------------------------------------------------------------------------
# Test 6: Skill file mapping
# ---------------------------------------------------------------------------

# Matches file paths that reference skill files relative to the repo root,
# e.g. ``skills/init.md``, ``skills/plan.md``.  The pattern captures the
# path component starting with "skills/".
_SKILL_FILE_RE: re.Pattern[str] = re.compile(
    r"\bskills/[\w./-]+\.md\b"
)


def _collect_template_files() -> list[Path]:
    """Return all markdown files under orchestration/templates/.

    Returns:
        Sorted list of Path objects for every .md file in the templates dir.
    """
    return sorted(TEMPLATES_DIR.rglob("*.md"))


def test_skill_file_mapping() -> None:
    """Every skill file path referenced in orchestration templates must exist.

    Scans all Markdown files under ``orchestration/templates/`` for references
    to ``skills/*.md`` paths.  Each referenced path is resolved relative to
    the repository root and asserted to exist on disk.

    Currently there are no skill file references in templates, so this test
    passes vacuously.  It is designed to catch broken references if skill file
    paths are added to templates in the future.

    AC-2: passes (vacuously) when no skill references are present.
    AC-3: completes in well under 1 second regardless of reference count.
    """
    template_files = _collect_template_files()

    broken: list[str] = []
    for template_file in template_files:
        content = template_file.read_text(encoding="utf-8")
        for skill_path_str in _SKILL_FILE_RE.findall(content):
            skill_path = REPO_ROOT / skill_path_str
            if not skill_path.exists():
                rel_template = template_file.relative_to(REPO_ROOT)
                broken.append(f"{rel_template}: references missing {skill_path_str}")

    assert not broken, (
        "The following skill file references in orchestration templates point "
        "to files that do not exist on disk:\n"
        + "\n".join(f"  - {entry}" for entry in sorted(broken))
        + "\n\nEither create the missing skill files or update the template "
        "references to use the correct paths."
    )


# ---------------------------------------------------------------------------
# Test 7: Hook file existence
# ---------------------------------------------------------------------------

# Required hook scripts that must exist under hooks/.
_REQUIRED_HOOK_FILES: tuple[str, ...] = (
    "ant-farm-statusline.js",
    "ant-farm-scope-advisor.js",
)

HOOKS_DIR: Path = REPO_ROOT / "hooks"


def test_hook_file_existence() -> None:
    """Required hook scripts must exist on disk under hooks/.

    Validates that each file listed in ``_REQUIRED_HOOK_FILES`` is present
    in the ``hooks/`` directory.  These hooks are installed by the setup
    pipeline and referenced by the orchestration system — missing hooks
    would cause runtime failures in Claude Code.
    """
    missing: list[str] = []
    for hook_name in _REQUIRED_HOOK_FILES:
        hook_path = HOOKS_DIR / hook_name
        if not hook_path.exists():
            missing.append(hook_name)

    assert not missing, (
        "The following required hook files are missing from hooks/:\n"
        + "\n".join(f"  - {name}  (expected at hooks/{name})" for name in missing)
    )


# ---------------------------------------------------------------------------
# Test 8: TDD enforcement integration
# ---------------------------------------------------------------------------

CLAIMS_VS_CODE_FILE: Path = (
    REPO_ROOT / "orchestration" / "templates" / "checkpoints" / "claims-vs-code.md"
)

# Required strings that confirm ``crumb validate-tdd`` is wired into the
# Checkpoint Auditor's claims-vs-code verification step.
_REQUIRED_TDD_STRINGS: frozenset[str] = frozenset(
    {
        "crumb validate-tdd",    # the command invocation
        "tdd: false",             # the opt-out field name
        "ordering_violations",    # the JSON key the auditor must inspect
        "test_files",             # the JSON key listing test files found
    }
)


def test_tdd_enforcement_wired_in_checkpoint() -> None:
    """claims-vs-code.md must reference the validate-tdd command and key fields.

    The Checkpoint Auditor runs Check 5 using ``crumb validate-tdd``.
    This test asserts that the checkpoint template hard-codes the required
    command, opt-out field, and output key names so the auditor has
    unambiguous instructions for TDD verification.

    If any of these strings go missing the Check 5 instructions become
    incomplete and the auditor may not run TDD enforcement correctly.
    """
    assert CLAIMS_VS_CODE_FILE.exists(), (
        f"claims-vs-code.md not found at "
        f"{CLAIMS_VS_CODE_FILE.relative_to(REPO_ROOT)}. "
        "Has the file been moved or renamed?"
    )

    content = CLAIMS_VS_CODE_FILE.read_text(encoding="utf-8")
    missing: list[str] = [s for s in sorted(_REQUIRED_TDD_STRINGS) if s not in content]

    assert not missing, (
        "The following required TDD-enforcement strings are absent from "
        f"{CLAIMS_VS_CODE_FILE.relative_to(REPO_ROOT)}:\n"
        + "\n".join(f"  - {s!r}" for s in missing)
        + "\n\nCheck 5 of the Checkpoint Auditor relies on these strings to "
        "instruct the auditor how to run and interpret validate-tdd."
    )


def test_tdd_skip_logic_documented_in_checkpoint() -> None:
    """claims-vs-code.md must document the tdd: false early-exit path.

    When a crumb carries ``tdd: false``, the Checkpoint Auditor must skip
    Check 5 entirely.  This test verifies the checkpoint template contains
    the SKIP verdict keyword alongside the tdd: false opt-out condition so
    the auditor is not left guessing how to handle it.
    """
    assert CLAIMS_VS_CODE_FILE.exists(), (
        f"claims-vs-code.md not found at "
        f"{CLAIMS_VS_CODE_FILE.relative_to(REPO_ROOT)}. "
        "Has the file been moved or renamed?"
    )

    content = CLAIMS_VS_CODE_FILE.read_text(encoding="utf-8")

    assert "SKIP" in content, (
        f"{CLAIMS_VS_CODE_FILE.relative_to(REPO_ROOT)}: "
        "no SKIP verdict keyword found for the tdd: false early-exit path. "
        "The Checkpoint Auditor needs an explicit SKIP outcome in Check 5."
    )

    # The SKIP verdict must appear near the tdd: false condition, not in an
    # unrelated part of the file.  We check that both appear in the same
    # 20-line window by scanning a sliding block of lines.
    lines = content.splitlines()
    window = 20
    skip_near_tdd = any(
        ("SKIP" in lines[i] and any("tdd" in lines[j] for j in range(i, min(i + window, len(lines)))))
        or ("tdd" in lines[i] and any("SKIP" in lines[j] for j in range(i, min(i + window, len(lines)))))
        for i in range(len(lines))
    )
    assert skip_near_tdd, (
        f"{CLAIMS_VS_CODE_FILE.relative_to(REPO_ROOT)}: "
        "'SKIP' and 'tdd' do not appear within 20 lines of each other. "
        "Check 5 must co-locate the SKIP verdict with the tdd: false condition."
    )


# ---------------------------------------------------------------------------
# Test 9: PRD import template placeholders
# ---------------------------------------------------------------------------

PRD_IMPORT_FILE: Path = REPO_ROOT / "orchestration" / "templates" / "prd-import.md"

# Expected {UPPERCASE} placeholders that must appear in prd-import.md.
# These are the three user-supplied slot variables that the Planner fills
# before spawning the PRD Importer agent.
_REQUIRED_PRD_PLACEHOLDERS: frozenset[str] = frozenset(
    {"DECOMPOSE_DIR", "CODEBASE_ROOT", "PRD_PATH"}
)


def test_prd_import_placeholders() -> None:
    """PRD import template must contain expected placeholder patterns.

    Validates that ``orchestration/templates/prd-import.md`` exists and
    contains each of the required ``{UPPERCASE}`` placeholder tokens.
    These placeholders are filled by the Planner at runtime; their absence
    would break the PRD import pipeline.
    """
    assert PRD_IMPORT_FILE.exists(), (
        f"PRD import template not found at {PRD_IMPORT_FILE.relative_to(REPO_ROOT)}. "
        "Has the file been moved or renamed?"
    )

    content = PRD_IMPORT_FILE.read_text(encoding="utf-8")
    found_placeholders: set[str] = set(_SINGLE_BRACE_SLOT_RE.findall(content))

    missing_placeholders = _REQUIRED_PRD_PLACEHOLDERS - found_placeholders
    assert not missing_placeholders, (
        f"The following required placeholders are missing from "
        f"{PRD_IMPORT_FILE.relative_to(REPO_ROOT)}:\n"
        + "\n".join(
            f"  - {{{name}}}" for name in sorted(missing_placeholders)
        )
        + "\n\nThese placeholders are required for the Planner to fill "
        "before spawning the PRD Importer agent."
    )


# ---------------------------------------------------------------------------
# Test 10: validate-coverage subcommand registration
# ---------------------------------------------------------------------------

import subprocess  # noqa: E402  (placed near usage for clarity)
import sys  # noqa: E402

CRUMB_PY: Path = REPO_ROOT / "crumb.py"


def test_validate_coverage_registered_in_parser() -> None:
    """``crumb validate-coverage`` is registered as a subcommand in build_parser.

    Runs ``crumb --help`` as a subprocess and asserts that ``validate-coverage``
    appears in the output.  This verifies the subcommand is wired up correctly
    in ``build_parser`` and would be discovered by users via the help text.
    """
    import tempfile
    import json as _json

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        # Bootstrap a minimal .crumbs/ so crumb.py can start without error
        crumbs_dir = tmp_path / ".crumbs"
        crumbs_dir.mkdir()
        (crumbs_dir / "config.json").write_text(
            _json.dumps({
                "prefix": "AF",
                "next_crumb_id": 1,
                "default_priority": "P2",
                "banned_phrases": [],
            }) + "\n",
            encoding="utf-8",
        )
        (crumbs_dir / "tasks.jsonl").write_text("", encoding="utf-8")

        result = subprocess.run(
            [sys.executable, str(CRUMB_PY), "--help"],
            capture_output=True, text=True, cwd=str(tmp_path),
        )
    assert "validate-coverage" in result.stdout, (
        "crumb --help output does not mention 'validate-coverage'. "
        "Is the subcommand registered in build_parser()?\n"
        f"stdout: {result.stdout!r}"
    )


def test_validate_coverage_empty_spec_exits_0() -> None:
    """``crumb validate-coverage`` on a spec with no REQ headings exits 0.

    A spec file with no REQ-N: headings has no requirements to cover, so the
    command must exit 0 (100% coverage of an empty requirement set).
    """
    import tempfile
    import json as _json

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        crumbs_dir = tmp_path / ".crumbs"
        crumbs_dir.mkdir()
        (crumbs_dir / "config.json").write_text(
            _json.dumps({
                "prefix": "AF",
                "next_crumb_id": 1,
                "default_priority": "P2",
                "banned_phrases": [],
            }) + "\n",
            encoding="utf-8",
        )
        (crumbs_dir / "tasks.jsonl").write_text("", encoding="utf-8")

        spec_file = tmp_path / "spec.md"
        spec_file.write_text("# Overview\n\nNo requirements here.\n", encoding="utf-8")

        result = subprocess.run(
            [sys.executable, str(CRUMB_PY), "validate-coverage", str(spec_file)],
            capture_output=True, text=True, cwd=str(tmp_path),
        )
    assert result.returncode == 0, (
        "validate-coverage on an empty spec must exit 0.\n"
        f"stdout: {result.stdout!r}\nstderr: {result.stderr!r}"
    )


def test_validate_coverage_json_output_has_required_keys() -> None:
    """``crumb validate-coverage --json`` output has 'covered', 'uncovered', 'unmapped'.

    Structural contract: the JSON schema for validate-coverage must always
    include these three top-level keys so downstream orchestration consumers
    (e.g., Checkpoint Auditor) can rely on them without version checks.
    """
    import tempfile
    import json as _json

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        crumbs_dir = tmp_path / ".crumbs"
        crumbs_dir.mkdir()
        (crumbs_dir / "config.json").write_text(
            _json.dumps({
                "prefix": "AF",
                "next_crumb_id": 1,
                "default_priority": "P2",
                "banned_phrases": [],
            }) + "\n",
            encoding="utf-8",
        )
        (crumbs_dir / "tasks.jsonl").write_text("", encoding="utf-8")

        spec_file = tmp_path / "spec.md"
        spec_file.write_text("# Spec\n\n## REQ-1: Do something.\n", encoding="utf-8")

        result = subprocess.run(
            [sys.executable, str(CRUMB_PY), "validate-coverage", "--json", str(spec_file)],
            capture_output=True, text=True, cwd=str(tmp_path),
        )
    # Exit code 1 because REQ-1 is uncovered, but output is still JSON
    assert result.returncode == 1
    parsed = _json.loads(result.stdout)
    for key in ("covered", "uncovered", "unmapped"):
        assert key in parsed, (
            f"validate-coverage --json output missing required key '{key}'.\n"
            f"stdout: {result.stdout!r}"
        )


# ---------------------------------------------------------------------------
# TestValidateCoverageOrchestration — contract tests for orchestration consumers
# ---------------------------------------------------------------------------


class TestValidateCoverageOrchestration:
    """Orchestration integration tests for ``crumb validate-coverage``.

    Verifies structural contracts that downstream orchestration consumers
    (Checkpoint Auditor, review templates) depend on.  Uses stdlib only —
    no pytest fixtures that require crumb.py internals.
    """

    import sys as _sys
    import json as _json

    @staticmethod
    def _make_env(tmp_path: Path, tasks_content: str = "") -> None:
        """Write minimal .crumbs/ environment to *tmp_path*."""
        import json as _json
        crumbs_dir = tmp_path / ".crumbs"
        crumbs_dir.mkdir(parents=True, exist_ok=True)
        (crumbs_dir / "config.json").write_text(
            _json.dumps({
                "prefix": "AF",
                "next_crumb_id": 1,
                "default_priority": "P2",
                "banned_phrases": [],
            }) + "\n",
            encoding="utf-8",
        )
        (crumbs_dir / "tasks.jsonl").write_text(tasks_content, encoding="utf-8")

    def test_json_schema_always_has_three_keys_when_all_covered(
        self, tmp_path: Path
    ) -> None:
        """JSON output always includes covered/uncovered/unmapped even when fully covered."""
        import json as _json
        import sys
        self._make_env(tmp_path, tasks_content=(
            '{"id":"AF-1","title":"Task","status":"open","requirements":["REQ-1"]}\n'
        ))
        spec = tmp_path / "spec.md"
        spec.write_text("## REQ-1: Fully covered.\n", encoding="utf-8")

        result = subprocess.run(
            [sys.executable, str(CRUMB_PY), "validate-coverage", "--json", str(spec)],
            capture_output=True, text=True, cwd=str(tmp_path),
        )

        assert result.returncode == 0, (
            f"Expected exit 0.\nstdout: {result.stdout!r}\nstderr: {result.stderr!r}"
        )
        parsed = _json.loads(result.stdout)
        for key in ("covered", "uncovered", "unmapped"):
            assert key in parsed, (
                f"JSON output missing key '{key}' even when fully covered.\n"
                f"stdout: {result.stdout!r}"
            )
        assert parsed["covered"] != [], "covered must be non-empty when REQ-1 is covered"
        assert parsed["uncovered"] == [], "uncovered must be empty when all REQs covered"

    def test_json_schema_always_has_three_keys_when_no_reqs(
        self, tmp_path: Path
    ) -> None:
        """JSON output always includes covered/uncovered/unmapped for a no-REQ spec."""
        import json as _json
        import sys
        self._make_env(tmp_path)
        spec = tmp_path / "spec.md"
        spec.write_text("# Intro\n\nNo requirements.\n", encoding="utf-8")

        result = subprocess.run(
            [sys.executable, str(CRUMB_PY), "validate-coverage", "--json", str(spec)],
            capture_output=True, text=True, cwd=str(tmp_path),
        )

        assert result.returncode == 0
        parsed = _json.loads(result.stdout)
        for key in ("covered", "uncovered", "unmapped"):
            assert key in parsed, f"Missing key '{key}' for empty spec.\n{result.stdout!r}"
        assert parsed["covered"] == []
        assert parsed["uncovered"] == []

    def test_unmapped_key_present_when_crumb_has_no_requirements_field(
        self, tmp_path: Path
    ) -> None:
        """'unmapped' is non-empty when active crumbs have no requirements field."""
        import json as _json
        import sys
        self._make_env(tmp_path, tasks_content=(
            '{"id":"AF-1","title":"Old task","status":"open"}\n'
        ))
        spec = tmp_path / "spec.md"
        spec.write_text("## REQ-1: Uncovered.\n", encoding="utf-8")

        result = subprocess.run(
            [sys.executable, str(CRUMB_PY), "validate-coverage", "--json", str(spec)],
            capture_output=True, text=True, cwd=str(tmp_path),
        )

        assert result.returncode == 1  # REQ-1 uncovered
        parsed = _json.loads(result.stdout)
        assert "AF-1" in parsed["unmapped"], (
            f"Crumb with no requirements field must appear in unmapped.\n"
            f"unmapped: {parsed['unmapped']!r}"
        )

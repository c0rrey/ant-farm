"""Structural integrity tests for the ant-farm orchestration system.

Covers six categories:
1. Cross-reference integrity — every subagent_type string in RULES.md,
   RULES-decompose.md, and RULES-review.md resolves to an agent file.
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


def test_cross_reference_integrity() -> None:
    """Every subagent_type string in RULES files must match an agent file.

    Parses ``subagent_type="..."`` patterns from RULES.md,
    RULES-decompose.md, and RULES-review.md.  For each unique agent name
    found, asserts that ``agents/<name>.md`` exists in the repository.
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
# are used directly by the Queen/Planner without going through this script.
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

    Scans ``nitpicker-skeleton.md`` and ``big-head-skeleton.md`` — the two
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

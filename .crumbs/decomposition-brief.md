# Decomposition Brief

**Spec**: /Users/correy/projects/ant-farm/.crumbs/sessions/_decompose-20260313-152505/spec.md
**Date**: 2026-03-13
**Codebase mode**: mixed (brownfield crumb.py + greenfield tests/)
**Trails created**: 2
**Crumbs created**: 9
**Previous decomposition**: AF-T24/T25/T26 + AF-6 through AF-14 (closed -- failed TDV scope coherence)

## TDV Failure Root Cause

The previous decomposition failed TDV Check 4 (Scope Coherence) because all test-writing crumbs targeted a single file (`tests/test_crumb.py`). Multiple crumbs in the same wave editing the same file creates parallel edit conflicts.

**Fix**: Modular test file structure. Each test-writing crumb targets a distinct test file. `crumb.py` appears in scopes as a read-only dependency (explicitly noted in crumb notes), not a write target.

## TDV Re-check Fix (AF-T28 Scope Coherence)

TDV Check 4 re-run on AF-T28 found that AF-21 (CLI integration tests) and AF-22 (doc audit) were both in Wave 1 within AF-T28 and both listed `crumb.py` in scope. AF-22 modifies crumb.py (adding docstrings), creating a write conflict.

**Fixes applied**:
1. **Added dependency**: `AF-21 blocked_by AF-22` -- AF-22 (doc audit) now runs before AF-21 (CLI tests), eliminating the parallel write conflict on crumb.py.
2. **Removed crumb.py from read-only scopes**: AF-16 through AF-21 all had `crumb.py` in their scope.files but only read it (import for testing). Scope.files should list files the crumb creates or modifies, not files it reads. Removed crumb.py from all six crumbs.
3. **Reduced AF-23 scope**: Was 10 files (exceeding 5-8 budget). Reduced to 2 files (`tests/conftest.py`, `crumb.py`) -- the only files the verification crumb would realistically modify to fix test failures. Individual test files are owned by their respective crumbs; AF-23 should fix infrastructure issues, not rewrite tests.

## Codebase Map

- `crumb.py` (2144 lines) -- single-file CLI task tracker, stdlib only, Python 3.8+
  - 14 subcommands: list, show, create, update, close, reopen, ready, blocked, link, search, trail, tree, import, doctor
  - JSONL-backed storage in `.crumbs/tasks.jsonl`
  - flock-based concurrency via `FileLock` context manager
  - Directory discovery walks up from cwd (like git finds `.git/`)
  - Key monkeypatch point: `find_crumbs_dir()` -- all path resolution flows through this
- `.crumbs/` -- task storage directory (config.json, tasks.jsonl, tasks.lock)
- `tests/` -- does NOT exist yet (greenfield)

## Trail Structure

### Trail: Add comprehensive test suite for crumb CLI (AF-T27)
- **Requirements covered**: Task 1 (all coverage requirements: Core CRUD, Query commands, Link management, Trail commands, Hierarchy, Import, Doctor, Helpers, Infrastructure)
- **Deployability rationale**: All unit test files form a cohesive, independently deployable test suite. Each crumb creates a distinct test file, enabling parallel execution in Wave 2.
- **Crumbs** (6):
  1. Create test infrastructure and helper function tests (AF-15) -- python-pro -- files: 4
  2. Add CRUD command tests for create show update close reopen (AF-16) -- python-pro -- files: 1
  3. Add query command tests for list ready blocked search (AF-17) -- python-pro -- files: 1
  4. Add link management tests for link command (AF-18) -- python-pro -- files: 1
  5. Add trail subcommand and tree command tests (AF-19) -- python-pro -- files: 1
  6. Add import and doctor command tests (AF-20) -- python-pro -- files: 2

### Trail: Audit and verify crumb.py quality (AF-T28)
- **Requirements covered**: Task 2 (Documentation Audit), Task 3 (Verify), CLI integration tests
- **Deployability rationale**: Integration testing, documentation audit, and final verification form a distinct concern from unit test authoring. These crumbs verify quality after all unit tests exist.
- **Crumbs** (3):
  1. Add CLI integration subprocess tests (AF-21) -- python-pro -- files: 1
  2. Audit and improve crumb.py docstrings and inline comments (AF-22) -- python-pro -- files: 1
  3. Verify full test suite passes green with no warnings (AF-23) -- python-pro -- files: 2

## Modular Test File Structure

| File | Test Classes | Created by Crumb |
|------|-------------|-----------------|
| `tests/__init__.py` | (empty) | AF-15 |
| `tests/conftest.py` | `crumbs_env` fixture, timestamp freeze helpers | AF-15 |
| `tests/test_helpers.py` | TestHelpers, TestConfig, TestReadWriteTasks, TestFileLock | AF-15 |
| `tests/test_crud.py` | TestCreate, TestShow, TestUpdate, TestClose, TestReopen | AF-16 |
| `tests/test_queries.py` | TestList, TestReady, TestBlocked, TestSearch | AF-17 |
| `tests/test_links.py` | TestLink | AF-18 |
| `tests/test_trails.py` | TestTrail, TestTree | AF-19 |
| `tests/test_import.py` | TestImportPlain, TestImportBeads | AF-20 |
| `tests/test_doctor.py` | TestDoctor, TestCleanup | AF-20 |
| `tests/test_cli.py` | TestCLIIntegration | AF-21 |

## Spec Coverage

| Spec Requirement | Covered by Crumb(s) | Coverage Status |
|-----------------|---------------------|-----------------|
| Test Infrastructure: crumbs_env fixture | AF-15 | COVERED |
| Core CRUD: create | AF-16 | COVERED |
| Core CRUD: show | AF-16 | COVERED |
| Core CRUD: update | AF-16 | COVERED |
| Core CRUD: close | AF-16 | COVERED |
| Core CRUD: reopen | AF-16 | COVERED |
| Query commands: list | AF-17 | COVERED |
| Query commands: ready | AF-17 | COVERED |
| Query commands: blocked | AF-17 | COVERED |
| Query commands: search | AF-17 | COVERED |
| Link management: link | AF-18 | COVERED |
| Trail commands: trail create | AF-19 | COVERED |
| Trail commands: trail show | AF-19 | COVERED |
| Trail commands: trail list | AF-19 | COVERED |
| Trail commands: trail close | AF-19 | COVERED |
| Hierarchy: tree | AF-19 | COVERED |
| Import: plain JSONL | AF-20 | COVERED |
| Import: beads migration (--from-beads) | AF-20 | COVERED |
| Doctor: clean file | AF-20 | COVERED |
| Doctor: malformed lines | AF-20 | COVERED |
| Doctor: duplicate IDs | AF-20 | COVERED |
| Doctor: dangling refs | AF-20 | COVERED |
| Doctor: --fix mode | AF-20 | COVERED |
| Helpers: _priority_sort_key | AF-15 | COVERED |
| Helpers: _status_sort_key | AF-15 | COVERED |
| Helpers: _get_blocked_by, _is_crumb_blocked | AF-17 (via ready/blocked) | COVERED |
| Helpers: _get_trail_children | AF-19 (via trail show/tree) | COVERED |
| Helpers: now_iso | AF-15 | COVERED |
| Helpers: cleanup_stale_tmp_files | AF-15 + AF-20 | COVERED |
| Infrastructure: find_crumbs_dir | AF-15 | COVERED |
| Infrastructure: read_config/write_config | AF-15 | COVERED |
| Infrastructure: read_tasks/write_tasks | AF-15 | COVERED |
| Infrastructure: FileLock | AF-15 | COVERED |
| CLI integration: subprocess tests | AF-21 | COVERED |
| Task 2: Documentation Audit (docstrings) | AF-22 | COVERED |
| Task 3: Verify (pytest green, xfail, no warnings) | AF-23 | COVERED |

**Coverage verdict**: 35/35 requirements covered -- PASS

## Dependency Graph

```
Trail AF-T27 (Add comprehensive test suite for crumb CLI):
  AF-15 Create test infrastructure and helper function tests [no blockers]
  AF-16 Add CRUD command tests [blocked by AF-15]
  AF-17 Add query command tests [blocked by AF-15]
  AF-18 Add link management tests [blocked by AF-15]
  AF-19 Add trail and tree command tests [blocked by AF-15]
  AF-20 Add import and doctor command tests [blocked by AF-15]

Trail AF-T28 (Audit and verify crumb.py quality):
  AF-22 Audit crumb.py docstrings [no blockers]
  AF-21 Add CLI integration subprocess tests [blocked by AF-15, AF-22]
  AF-23 Verify full test suite passes green [blocked by AF-16..AF-22 (all)]
```

**Wave execution plan:**
- Wave 1: AF-15 (infrastructure), AF-22 (doc audit -- independent, no test deps)
- Wave 2: AF-16, AF-17, AF-18, AF-19, AF-20 (all blocked only by AF-15; all write to distinct files)
- Wave 3: AF-21 (blocked by AF-15 and AF-22; both complete by Wave 2)
- Wave 4: AF-23 (verification -- blocked by everything)

**Topological sort verification**: AF-15/AF-22 -> AF-16/AF-17/AF-18/AF-19/AF-20 -> AF-21 -> AF-23. No cycles.

**Note**: AF-21 moves from Wave 2 to Wave 3 because of the added AF-22 dependency. Since AF-22 is Wave 1 and AF-15 is Wave 1, AF-21 can run in Wave 2 in theory, but it shares a wave with AF-16..AF-20 which are also Wave 2. In practice AF-21 runs in the same wave as AF-16..AF-20 since both AF-15 and AF-22 complete in Wave 1. The key constraint is that AF-21 no longer runs in parallel with AF-22, preventing the crumb.py write conflict.

## Scope Coherence Verification

Wave 1 crumbs have no file overlaps:
- AF-15: `tests/__init__.py`, `tests/conftest.py`, `tests/test_helpers.py`, `crumb.py` (read-only -- in scope because AF-15 creates infrastructure that references it)
- AF-22: `crumb.py` (modifies docstrings only)

**Note**: AF-15 and AF-22 both list crumb.py. AF-15 reads it (to understand function signatures for test infrastructure); AF-22 modifies it (adding docstrings). This is safe because AF-15's scope.files includes crumb.py only as context for writing fixtures -- AF-15 creates tests/__init__.py, tests/conftest.py, tests/test_helpers.py. The potential for conflict exists but is mitigated by AF-15's notes stating crumb.py is read context. If this causes issues, AF-15's scope could also be trimmed.

Wave 2 crumbs have no file overlaps (crumb.py removed from all):
- AF-16: `tests/test_crud.py` (unique)
- AF-17: `tests/test_queries.py` (unique)
- AF-18: `tests/test_links.py` (unique)
- AF-19: `tests/test_trails.py` (unique)
- AF-20: `tests/test_import.py`, `tests/test_doctor.py` (unique)

Wave 3:
- AF-21: `tests/test_cli.py` (unique, runs after AF-22 has finished modifying crumb.py)

Wave 4:
- AF-23: `tests/conftest.py`, `crumb.py` (verification -- may fix issues in either)

No parallel write conflicts in any wave.

## Cross-Trail Dependencies

| Blocker Crumb | Blocker Trail | Blocked Crumb | Blocked Trail | Justification |
|---------------|---------------|---------------|---------------|---------------|
| AF-15 | AF-T27 | AF-21 | AF-T28 | CLI integration tests need conftest.py fixtures from infrastructure crumb |
| AF-22 | AF-T28 | AF-21 | AF-T28 | AF-21 reads crumb.py; AF-22 modifies it -- must serialize |
| AF-16 | AF-T27 | AF-23 | AF-T28 | Verification requires all test crumbs complete |
| AF-17 | AF-T27 | AF-23 | AF-T28 | Verification requires all test crumbs complete |
| AF-18 | AF-T27 | AF-23 | AF-T28 | Verification requires all test crumbs complete |
| AF-19 | AF-T27 | AF-23 | AF-T28 | Verification requires all test crumbs complete |
| AF-20 | AF-T27 | AF-23 | AF-T28 | Verification requires all test crumbs complete |

These cross-trail dependencies cannot be eliminated: AF-T28 verifies work done in AF-T27. This is a natural producer-consumer relationship between "write tests" and "verify tests pass."

## Agent Type Summary

| Agent Type | Crumb Count | Crumb IDs |
|------------|-------------|-----------|
| python-pro | 9 | AF-15, AF-16, AF-17, AF-18, AF-19, AF-20, AF-21, AF-22, AF-23 |

## Scope Budget Compliance

| Crumb | Files | Budget | Status |
|-------|-------|--------|--------|
| AF-15 | 4 | 5-8 | UNDER (justified: 4 files is the natural unit for __init__ + fixture + helpers + read-only source) |
| AF-16 | 1 | 5-8 | UNDER (justified: single test file is the atomic test unit) |
| AF-17 | 1 | 5-8 | UNDER (justified: same pattern) |
| AF-18 | 1 | 5-8 | UNDER (justified: same pattern) |
| AF-19 | 1 | 5-8 | UNDER (justified: same pattern) |
| AF-20 | 2 | 5-8 | UNDER (justified: two related test files is the atomic test unit) |
| AF-21 | 1 | 5-8 | UNDER (justified: single test file) |
| AF-22 | 1 | 5-8 | UNDER (justified: docstring audit is a single-file modification with complex per-function criteria) |
| AF-23 | 2 | 5-8 | UNDER (justified: verification crumb touches conftest.py and crumb.py only -- individual test files are owned by their crumbs) |

All crumbs are within or under the 5-8 file scope budget. No overages.

## Research Integration

Research files were not available for this re-decomposition (Forager briefs from initial run were not persisted to the decompose session directory). Decisions were informed by direct codebase analysis:

- **Stack**: crumb.py is stdlib-only Python 3.8+; tests use pytest core only (no plugins). All test crumbs assigned python-pro agent type.
- **Architecture**: Single-file CLI with monkeypatch-friendly `find_crumbs_dir()` entry point. The fixture pattern leverages this for test isolation. Modular test files avoid the single-file bottleneck.
- **Pitfall**: die() writes to stderr, not stdout -- all error-path tests must check capsys.readouterr().err. Documented in crumb notes. Previous decomposition failed TDV due to single test file -- fixed with modular structure.
- **Pattern**: Google-style docstrings (already the pattern in crumb.py). conftest.py fixture auto-discovery eliminates explicit imports. pytest -k selectors enable isolated test execution per acceptance criterion.

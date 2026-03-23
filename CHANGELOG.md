# Changelog

## 2026-03-23 — Session 2ad19b6d (Gate Enforcement Infrastructure and crumb CLI Expansion)

### Summary

Shipped 18 tasks (15 implementation + 3 review fixes) across 4 implementation waves in ~2 hours. The session delivered the complete gate enforcement stack — scope advisor enforcing mode, gate-manager library, retry tracker, gate enforcer PreToolUse hook, position check, and full npm registration wiring — alongside two new `crumb` CLI subcommands (`validate-trail`, `validate-spec`) and cycle detection with `--fix` mode in `crumb doctor`. Two review rounds were run; round 1 identified 3 P2 findings (documentation staleness and import organization) which were auto-fixed and verified clean in round 2. All 77 implementation acceptance criteria passed per the correctness reviewer. 19 commits, 21 files changed.

### Implementation (Waves 1–4)

- **AF-452**: feat: cycle detection in crumb doctor — `_detect_cycles()` with graphlib + iterative peeling, 18 tests, JSON `cycles` field (`crumb.py`, `tests/test_doctor.py`) (`13f9a53`)
- **AF-455**: feat: add `validate-trail` subcommand with configurable thresholds — PASS/FAIL/WARN logic, `--all`/`--strict`/`--json`, 49 tests (`crumb.py`, `tests/test_trails.py`) (`b436d4d`)
- **AF-459**: feat: add enforcing mode to scope advisor hook — `mode` + `permitted_exceptions` in sidecar schema, `isPermittedException()`, blocking path with debug log, 31 tests (`hooks/ant-farm-scope-advisor.js`, `hooks/lib/scope-reader.js`, `hooks/test/scope-advisor.test.js`, `hooks/lib/test/scope-reader.test.js`) (`de614a2`, `526ea7d`)
- **AF-462**: feat: implement gate-manager.js library module — `readGateStatus`, `writeGateVerdict` (atomic tmp+rename), `isGatePassed`, `GATE_CHAIN`, 26 tests (`hooks/lib/gate-manager.js`, `hooks/lib/test/gate-manager.test.js`) (`ee519c5`)
- **AF-456**: feat: add `validate-spec` banned-phrase filter subcommand — word-boundary regex AC-line scanner, 11 default banned phrases, `--json`, 13 tests (`crumb.py`, `tests/test_cli.py`) (`bad0ce2`)
- **AF-464**: feat: implement retry tracker library and CLI — `recordRetry`, `canRetry`, `getTotalRetries`, `resetRetries`, `crumb session-retries`/`session-reset-retries`, 22 JS + 12 Python tests (`hooks/lib/retry-tracker.js`, `hooks/lib/test/retry-tracker.test.js`, `crumb.py`, `tests/test_cli.py`) (`d8c3b52`)
- **AF-453**: feat: add `--fix` mode to `crumb doctor` for cycle breaking — `_break_cycle_edges()` batch closing-edge removal, JSON `cycle_fixes_applied` field, 13 tests (`crumb.py`, `tests/test_doctor.py`) (`777fa87`)
- **AF-454**: feat: add cycle detection performance test and edge cases — 500-crumb topology fixture, diamond + chain + empty tests (`tests/test_doctor.py`, `tests/fixtures/500_crumbs_with_cycles.jsonl`) (`f8aacf0`)
- **AF-457**: test: add AC1-AC4 validate-trail coverage — 8 tests for minimum/maximum violation messages and `--all` per-trail statuses (`tests/test_trails.py`) (`b133b3c`)
- **AF-458**: test: add missing validate-spec tests for empty file and 'As Expected' phrase — 3 tests for AC-3 and AC-8 (`tests/test_cli.py`) (`a062d15`)
- **AF-460**: feat: set scope mode per agent type in prompt composer — `mode`/`permitted_exceptions` sidecar doc, enforcing/advisory rule, BLOCKED event check in scope-verify step 4 (`orchestration/templates/prompt-composer.md`, `orchestration/templates/checkpoints/scope-verify.md`) (`117c97a`)
- **AF-461**: feat: add debug log integration test for scope advisor enforcing mode — byte-offset snapshot + truncate-in-finally pattern (`hooks/test/scope-advisor.test.js`) (`a2ca04b`)
- **AF-463**: feat: implement gate enforcement PreToolUse hook — startup-check gating, env/prompt-scan session detection, `bypass_gates` escape hatch, BYPASS_TOOLS pass-through, 27 tests (`hooks/ant-farm-gate-enforcer.js`, `hooks/test/gate-enforcer.test.js`) (`5fe16da`)
- **AF-465**: feat: add `getExpectedNextStep`, position check enforcer, and `session-status` CLI — `readAllLines`/`getExpectedNextStep` in progress-reader, position check in gate enforcer, `crumb session-status`, 19 JS + 12 Python tests (`hooks/lib/progress-reader.js`, `hooks/lib/test/progress-reader.test.js`, `hooks/ant-farm-gate-enforcer.js`, `crumb.py`, `tests/test_cli.py`) (`aaa32a6`)
- **AF-466**: feat: wire retry tracking and position check into gate enforcer — `canRetry` check, `extractTaskIdFromPrompt`, `AGENT_SPAWN_GATE` timestamp, npm manifest + hooks-registration wired, 9 new tests (`hooks/ant-farm-gate-enforcer.js`, `hooks/test/gate-enforcer.test.js`, `npm/install-manifest.json`, `npm/lib/hooks-registration.js`) (`d9c90ea`)

### Review Fixes (Round 1 P2s)

- **AF-554**: fix: update hooks-registration.js JSDoc to include gate enforcer — module JSDoc and `unregisterScopeAdvisorHook` doc updated (`npm/lib/hooks-registration.js`) (`07f3c36`)
- **AF-555**: fix: correct debug log path in scope-verify.md checkpoint template — stale project-root path replaced with `~/.claude/.ant-farm-hook-debug.log` (`orchestration/templates/checkpoints/scope-verify.md`) (`ece658a`)
- **AF-556**: fix: hoist scattered require declarations in gate-enforcer.test.js — mid-file requires hoisted to top, duplicate gate-manager require deduplicated (`hooks/test/gate-enforcer.test.js`) (`7e435e3`)

### Review Statistics

| Round | Scope | P1 | P2 | P3 | Verdict |
|-------|-------|----|----|-----|---------|
| 1 | 21 files, 15 tasks | 0 | 3 | 15 | PASS WITH ISSUES |
| 2 | 3 fix commits | 0 | 0 | 0 | PASS |

18 root causes consolidated (7 findings merged). 3 P2s auto-fixed; 15 P3s deferred.

## 2026-03-23 — Session 6355db7e (Orchestration Template Polish and Documentation Consistency)

### Summary

Completed 19 tasks across 3 implementation waves (7/5/3) plus a 4-task review fix cycle, all focused on documentation clarity and consistency improvements across orchestration templates, RULES files, and skills. Work included adding rationale to magic constants, fixing stale terminology and naming conventions, standardizing pre-flight check patterns, capping fix-cycle agent batch sizes, and cleaning up import style in tests. Two review rounds ran: round 1 produced 0 P1 and 4 P2 findings (all auto-fixed), plus 22 P3 crumbs filed; round 2 cleared with 0 findings. Session produced 19 commits across 18 files (including 2 external commits outside task scope).

### Implementation (Waves 1–3)

- **AF-505**: docs: add inline rationale for magic constants in RULES-review.md and reviews.md (`d57a426`)
- **AF-507**: fix: update stale heading and wrong monitoring tool name in SESSION_PLAN_TEMPLATE.md (`cb88e2f`)
- **AF-512**: fix: remove redundant parenthetical and move FAIL-FAST annotations to after conditions list in prompt-composer.md (`25bba4f`)
- **AF-515**: fix: replace emoji MANDATORY marker with bold convention in implementation.md (`a2ef8db`)
- **AF-518**: fix: correct Step 7 heading — CLI fallbacks are inline parentheticals, not comments in task-decomposer-skeleton.md (`aa1eea8`)
- **AF-519**: fix: standardize pre-flight check to two-outcome form in quick.md and work.md (`fd2cdc2`)
- **AF-520**: fix: lowercase bash sentinel output in status.md hook check (`a872ff2`)
- **AF-506**: docs: fix internal agent terminology leaks in RULES docs — bridge FORAGER/Researcher, fix CG prose, correct FIX_CMVCC_COMPLETE typo (`8ab3231`)
- **AF-511**: docs: explain {{REVIEW_ROUND}} double-brace convention in reviews.md (`661ef85`)
- **AF-510**: fix: clarify step 10a as async reply handler in review-consolidator-skeleton.md (`69e1235`)
- **AF-508**: fix: split Check 1 format string into per-round conditionals in review-integrity.md (`f6852a2`)
- **AF-522**: fix: remove unused List import and normalize Dict to dict in test_mcp_server.py (`45fa5e4`)
- **AF-527**: fix: cap fix-cycle agent batch size to 3 crumbs per agent in recon-planner.md and RULES-review.md (`395ab51`)
- **AF-525**: fix: align error message wording in review-consolidator-skeleton.md with reviews.md (`9d3244b`)
- **AF-509**: chore: remove historical Check 3b HTML comment from review-integrity.md (`191570e`)

### Review Fixes (Round 1)

- **AF-528, AF-529, AF-534**: fix: update check counts, MCP tool list, and remove duplicate paragraph in startup-check.md, RULES.md, work.md, implementation.md (`95f7fea`)
- **AF-541**: fix: reformat orchestration-agent exclusion list as bullet list in recon-planner.md (`05183be`)

### Review Statistics

| Round | Scope | P1 | P2 | P3 | Verdict |
|-------|-------|----|----|-----|---------|
| 1 | 15 tasks | 0 | 4 | 22 | PASS WITH ISSUES |
| 2 | 4 fix tasks | 0 | 0 | 0 | PASS |

26 root causes consolidated. 4 P2 auto-fixed in fix cycle; 22 P3 filed as future crumbs (AF-530 through AF-553, excluding fix IDs).


## 2026-03-23 — Session 20260323-124227 (MCP Tool Expansion and Full Framework Migration)

### Summary

Completed 23 tasks across 3 primary implementation waves and a review-driven fix cycle. The session delivered the 7 missing MCP tools for the crumb task tracker (crumb_trail_list, crumb_trail_show, crumb_trail_close, crumb_close, crumb_ready, crumb_blocked, crumb_link) and migrated the entire orchestration framework — 4 RULES files, 21 template files, 12 skill and agent files — to prefer MCP tool calls over CLI. Two review rounds ran: round 1 produced 1 P1 and 4 P2 findings (all fixed), plus 14 deferred P3 crumbs; round 2 cleared with 0 P1/P2 and 1 P3 residual that was fixed within the session. Session produced 13 commits across 39 files.

### Implementation (Waves 1–3)

- **AF-492**: feat: add 7 missing MCP tools (crumb_trail_list, crumb_trail_show, crumb_trail_close, crumb_close, crumb_ready, crumb_blocked, crumb_link) with 44 new tests (`mcp_server.py`, `tests/test_mcp_server.py`) (`7f55373`)
- **AF-493**: feat: migrate RULES files to prefer MCP tools over CLI — fallback notes added to 4 RULES files; prose CLI invocations replaced with MCP forms (`b126d65`)
- **AF-494**: feat: migrate 21 orchestration template files to prefer MCP tools over CLI — prose converted, bash code blocks preserved as CLI, trail creation stays CLI (`1786e20`)
- **AF-495**: feat: migrate 12 skills and agent definition files to prefer MCP tools over CLI — top-level blockquote note blocks added to all 5 skills and 7 agent files (`7d6e75e`)

### Review Fixes (Round 1)

- **AF-496, AF-498, AF-499, AF-500, AF-501**: fix: improve error messages and consistency across MCP tools — corrected crumb_update docstring, preserved exit code in SystemExit conversions, added missing handlers to crumb_list/crumb_query, added early return for empty ids, corrected crumb_close output-order docstring (`mcp_server.py`) (`9048bac`)
- **AF-504**: fix: add 7 missing MCP tools to agent/skill banners — extended all 9 file banners from 6-tool list to full 13-tool list (`dc1e6b8`)
- **AF-517, AF-516, AF-514**: fix: remove duplicate placeholders, clarify suffix example, fix nested fence in template skeleton files (`1b138ce`)
- **AF-521, AF-523, AF-524**: fix: consolidate crumb doctor call in work.md, update MCP tool names in RULES.md Hard Gates table and recon-planner.md Step 4 (`8c6abf5`)
- **AF-503**: fix: align language-detection script with early-exit comment in skills/init.md (`8a2fad9`)
- **AF-502**: fix: rename "Crumbs filed" to "Open crumbs" in session-complete.md Check 6 (`9c62040`)
- **AF-513**: fix: clarify scribe-skeleton.md path base directory in claude-block.md (`b3f0df8`)

### Review Fixes (Post-Round-2)

- **AF-526**: fix: remove 3 remaining bare `except RuntimeError: raise` no-op clauses in mcp_server.py and update affected test (`ba191b0`, `76a79af`)

### Review Statistics

| Round | Scope | P1 | P2 | P3 | Verdict |
|-------|-------|----|----|-----|---------|
| 1 | 39 files, 4 tasks | 1 | 4 | 25 | PASS WITH ISSUES |
| 2 | 7 fix commits, 16 crumbs | 0 | 0 | 1 | PASS |

31 root causes consolidated in round 1 (43 raw findings, 12 merges). 5 P1/P2 findings fixed; 14 P3 findings deferred to backlog.

## 2026-03-22 — Session 20260322-185904 (Test Cleanup, Null Guards, Hook Tests & JSON Schema Docs)

### Summary

Completed 14 tasks across 2 primary waves and a review-driven fix cycle. Work spanned Python test-quality improvements (constant deduplication, naming fixes, test renames), JavaScript install-tooling polish (step banners, null guard, hook registration tests), and a new `docs/json-schema.md` reference document. Two review rounds ran: round 1 produced 1 P2 finding (silent dict-to-scalar replacement in `from_json`) which was auto-fixed; round 2 cleared with 0 findings. 6 P3 polish crumbs (AF-444–AF-449) filed and deferred. Session produced 11 commits.

### Implementation (Waves 1–2)

- **AF-156 + AF-159 + AF-160**: fix/refactor: replace hardcoded constants with imports, extract `_SECS_PER_DAY`, move local import to module level (`tests/conftest.py`, `tests/test_cli.py`, `tests/test_prune.py`) (`05440b1`)
- **AF-158**: fix: rename misleading test method and rewrite docstring for closed-crumb guard (`tests/test_crud.py`) (`66d8e2c`)
- **AF-256**: fix: remove unused `from typing import Dict` import (`tests/test_render_template.py`) (`3812ba2`)
- **AF-331**: refactor: rename `_make_update_args_import` → `_make_update_args` at definition and all call sites (`tests/test_import.py`) (`77268d3`)
- **AF-333**: fix: align event-type comment table arrows to column 23 (`hooks/lib/progress-reader.js`) (`90bb714`)
- **AF-335 + AF-346**: fix: add `// Step U1/U2/U3:` banners to `runUninstallMode` and guard top-level catch with `err?.message ?? String(err)` (`npm/bin/install.js`) (`33d7c29`)
- **AF-344**: fix: add null guard before `trimEnd()` in `syncClaudeMdBlock` to replace silent TypeError with descriptive Error (`npm/lib/claude-md.js`) (`f05f281`)
- **AF-343**: refactor: move `_show_args` helper adjacent to `TestShowJSON` (`tests/test_queries.py`) (`45e1862`)
- **AF-436**: test: add 8 unit tests for `registerHooks`/`unregisterHooks` following `registerMcp`/`unregisterMcp` pattern (`npm/test/install.test.js`, `npm/test/uninstall.test.js`) (`8ab3232`)
- **AF-437**: docs: add `docs/json-schema.md` JSON schema reference for crumb CLI `--json` output; add cross-reference in `crumb.py` docstring (`aaf2367`)

### Review Fixes (Round 1)

- **AF-443**: fix: emit `sys.stderr` warning on dict-to-scalar replacement in `from_json` deep-merge (`crumb.py`) (`fda07ff`)

### Review Statistics

| Round | Scope | P1 | P2 | P3 | Verdict |
|-------|-------|----|----|-----|---------|
| 1 | 11 files, 13 tasks | 0 | 1 | 6 | PASS WITH ISSUES |
| 2 | 1 file, 1 task (fix) | 0 | 0 | 0 | PASS |

7 root causes consolidated. P2 auto-fixed; 6 P3 crumbs (AF-444–AF-449) filed and deferred.

## 2026-03-22 — Session 20260322-151004 (Metaphor Rename: Colony → Descriptive Names)

### Summary

Completed a full rename of all ant-colony metaphor display names (Queen, Scout, Pantry, Crumb Gatherer, Nitpicker, Big Head, Pest Control, Surveyor, Forager, Architect, Scribe) to descriptive equivalents (Orchestrator, Recon Planner, Prompt Composer, Implementer, Reviewer, Review Consolidator, Checkpoint Auditor, Spec Writer, Researcher, Task Decomposer, Session Scribe) across 66+ files in 3 parallel waves covering 13 crumbs across epics AF-T65, AF-T66, and AF-T67. One review round produced 22 raw findings consolidated to 10 root causes; 4 P1/P2s were auto-fixed, 5 P3s deferred to crumbs, and 1 skipped as a pre-existing duplicate. 15 commits total.

### Implementation (Wave 1 — RULES, templates, agents)

- **AF-421**: refactor: rename old metaphor display names in RULES core files — RULES.md, RULES-review.md, RULES-decompose.md, RULES-lite.md; parenthetical acronyms removed (`65137dc`)
- **AF-422**: refactor: rename old metaphor display names in reviews, pantry, scout templates — reviews.md, pantry.md, scout.md; ~126 replacements (`d1cccef`)
- **AF-423**: refactor: rename old metaphor names in planning/design templates — forager.md, forager-skeleton.md, decomposition.md, architect-skeleton.md, surveyor.md, surveyor-skeleton.md, prd-import.md (`3a62fc7`)
- **AF-424**: refactor: rename old metaphor names in execution and skeleton templates — 8 skeleton/implementation templates; NITPICKER ABORTED and SCRIBE_COMPLETE identifiers preserved (`10b0d90`)
- **AF-425**: refactor: rename old metaphor names in checkpoint templates — 8 files under orchestration/templates/checkpoints/ (`8452e51`)
- **AF-426**: refactor: rename old metaphor names in orchestration support files — queen-state.md, claude-block.md, PLACEHOLDER_CONVENTIONS.md, SETUP.md, agent-catalog.md (`df2fd69`)
- **AF-427**: refactor: rename old metaphor names to descriptive names in agent files — 7 agents/*.md; YAML frontmatter preserved (`5b3bd7f`)

### Implementation (Wave 2 — docs, reference, scripts, skills, tests)

- **AF-428**: docs: rename metaphor names to descriptive names in top-level docs — README.md, CONTRIBUTING.md, CLAUDE.md, GLOSSARY.md; agent table restructured; historical names blockquote added (`3b782bc`)
- **AF-429**: refactor: rename old metaphor names in orchestration reference docs — 8 files under orchestration/reference/ (`37cdab1`)
- **AF-430**: refactor: rename old metaphor display names in scripts and skills — build-review-prompts.sh, parse-progress-log.sh, skills/work.md, skills/plan.md (`bdb2e92`)
- **AF-432**: test: add RULES-lite, hook, and PRD import structural tests — RULES-lite.md added to cross-reference coverage; hook existence and PRD placeholder tests added; test count 23 → 25 (`0081dae`)
- **AF-433**: feat/fix: add hook-status reporting and JSON output to status skill — hook detection step added; Steps 1–2 use crumb list --json; CMVCC fix applied (`dd50bbe`, `e127c0c`)

### Implementation (Wave 3 — verification sweep)

- **AF-431**: refactor: fix straggler old metaphor names across 10 files — agents/, README.md, scripts/, tests/, docs/installation-guide.md (`0b96d23`)

### Review Fixes (Round 1 auto-fix)

- **RC-1/RC-2/RC-9/RC-10**: fix: address P1/P2 review findings — fixed stale BIG_HEAD_SKELETON test path variables, reverted crumb list --json to direct jq, updated WAVE_WWD_PASS key to WAVE_SCOPE_VERIFY_PASS, corrected CLAUDE.md step number (`3f1b898`)

### Review Statistics

| Round | Scope | P1 | P2 | P3 | Verdict |
|-------|-------|----|----|-----|---------|
| 1 | 66 files, 13 tasks | 3 | 1 | 5 | PASS WITH ISSUES |

10 root causes consolidated (1 skipped as duplicate of AF-388). P1/P2s auto-fixed; P3s deferred to 5 new crumbs.


## Decision Record: Use `mcp` Python Package for MCP Server

**Date**: 2026-03-22
**Status**: Accepted

### Decision

Use the third-party `mcp` Python package (`pip install mcp`) to implement the MCP server (`mcp_server.py`) rather than building a stdlib-only JSON-RPC transport layer.

### Why

- The `mcp` package provides `FastMCP`, a production-ready server framework with built-in stdio transport, tool registration decorators, and JSON-RPC message framing — eliminating hundreds of lines of boilerplate that would otherwise need to be written and maintained in-house.
- The MCP protocol specification is actively evolving; the `mcp` package tracks spec changes upstream, reducing the risk of protocol drift that a hand-rolled implementation would require manual patching to address.
- The `mcp` package handles async lifecycle management (event loop, signal handling, graceful shutdown) correctly out of the box, which is non-trivial to implement reliably with raw `asyncio` + `json` stdlib modules.
- All other ant-farm Python code (crumb.py, tests) remains stdlib-only. The `mcp` dependency is isolated to a single file (`mcp_server.py`) and is only required when the MCP server feature is used.

### Alternatives Considered

- **Stdlib-only JSON-RPC**: Implement the JSON-RPC 2.0 transport using only `json`, `asyncio`, and `sys.stdin`/`sys.stdout`. This would eliminate the external dependency but require writing and maintaining ~200-300 lines of protocol framing, error handling, and tool dispatch code. The maintenance burden was deemed disproportionate to the dependency-avoidance benefit, especially given the evolving MCP spec.

## 2026-03-22 — Simplify crumb.py (32% reduction)

### Summary

Simplified crumb.py from 3033 to 2055 lines (32% reduction, 978 lines removed) with no functionality loss and no external interface changes. All 455 tests pass.

### Changes

- **Remove Beads import subsystem** (-293 lines): Deleted dead one-time migration code (`_convert_beads_record`, `_resolve_beads_epic_refs`, `_apply_blocks_deps`, `_BEADS_*` maps, `--from-beads` flag) and corresponding `TestImportBeads` test class. Plain JSONL import retained.
- **Trim docstrings** (-578 lines): Reduced 691 lines of docstrings (22.8% of file) — trimmed functions with docstring-to-code ratio > 2x, removed embedded JSON examples from command handlers, condensed module docstring and `cmd_prune` timezone essay.
- **Extract shared helpers** (-107 lines net): Added `_require_crumb()` (replaces 9 find+die patterns), `_format_row()` (replaces 12 display format blocks), `_sort_crumbs()` (replaces 3 sort blocks), `_print_fields()` (replaces 2 label-value loops), `_add_json_flag()` (replaces 6 argparse blocks).
- **Clean up unused imports**: Removed `tempfile` and `Iterator`.

## 2026-03-22 — Session 20260322-131616 (crumb.py Bug Fix Sweep — Epic AF-T63)

### Summary

Session completed epic AF-T63, resolving all 19 crumb.py P3 bugs in a single Wave 1 using 3 parallel agents batched by non-overlapping file regions. Changes covered the full file: Windows-safe `fcntl` import, `FileLock` retry error handling, `cleanup_stale_tmp_files` locking and error visibility, `cmd_create`/`cmd_prune`/`cmd_close`/`cmd_tree` correctness, type annotation consistency, and minor docstring/comment accuracy fixes. Round 1 review (4 reviewers) found 1 P1 (stale `FileLock` docstring) and 3 P3 issues; all 4 were auto-fixed in a single fix agent pass. Round 2 confirmed clean convergence with 0 findings. All 476 tests pass. 2 commits total.

### Implementation (Wave 1 — 19 tasks)

- **AF-178**: fix: add `--from-file` to usage synopsis (`crumb.py:14`) (`162e3e3`)
- **AF-259**: fix: wrap unconditional `fcntl` import in `try/except ImportError` with `None` fallback (`crumb.py:38`) (`162e3e3`)
- **AF-253**: fix: add `Set` to typing import and replace bare `set` annotations with `Set[str]` at three sites (`crumb.py:53,1771,2062,2285`) (`162e3e3`)
- **AF-33**: fix: remove redundant `crumbs_dir()` wrapper function (`crumb.py:113`) (`162e3e3`)
- **AF-345**: fix: narrow bare `except` in `write_tasks` to `except Exception` (`crumb.py:289`) (`162e3e3`)
- **AF-332**: fix: normalize blank lines before section separator (`crumb.py:294–296`) (`162e3e3`)
- **AF-46 + AF-257**: fix: add `except OSError` fallback after `except BlockingIOError` in `FileLock.__enter__` retry loop — unified fix (`crumb.py:357–370`) (`162e3e3`)
- **AF-215**: fix: log `OSError` in `cleanup_stale_tmp_files` instead of swallowing silently (`crumb.py:401–404`) (`162e3e3`)
- **AF-347**: fix: wrap `cleanup_stale_tmp_files` call under `FileLock` (`crumb.py:379–406`) (`162e3e3`)
- **AF-177**: fix: add ISO-8601 validation for `--after` DATE argument (`crumb.py:700–706`) (`162e3e3`)
- **AF-174**: fix: remove duplicate CLI-override merge block in `cmd_create` (`crumb.py:832–862`) (`162e3e3`)
- **AF-155**: fix: reject empty-string title in `--from-json` path (`crumb.py:884`) (`162e3e3`)
- **AF-35**: fix: expand incomplete protected-field comment in `cmd_update` (`crumb.py:888–891`) (`162e3e3`)
- **AF-76**: fix: add invariant comment to second `_find_crumb` call in `cmd_close` (`crumb.py:976`) (`162e3e3`)
- **AF-213**: fix: remove dead variable `all_trail_ids` in `cmd_tree` (`crumb.py:1602`) (`162e3e3`)
- **AF-212**: fix: remove hardcoded `(currently 60)` parenthetical from `cmd_prune` docstring (`crumb.py:2295`) (`162e3e3`)
- **AF-93**: fix: add TOCTOU re-check of `_is_active_session` before each `rmtree` in `cmd_prune` (`crumb.py:2313–2356`) (`162e3e3`)
- **AF-254**: fix: rename local `crumbs_dir` to `prune_dir` to eliminate module-level shadowing (`crumb.py:2414`) (`162e3e3`)

### Review Fixes (Round 1)

- **AF-417**: fix: update `FileLock` docstring — use-time `SystemExit`, not import-time `AttributeError` (`crumb.py:301–304`) (`dcfddf0`)
- **AF-418**: fix: replace magic backdate `10` with `_STALE_TMP_AGE_SECS + 5` (`tests/test_helpers.py:326,358`) (`dcfddf0`)
- **AF-419**: fix: remove `(currently 60)` parenthetical from `cmd_prune` docstring (`crumb.py:2592`) (`dcfddf0`)
- **AF-420**: fix: replace `assert crumb is not None` with explicit `if crumb is None: die(...)` guard (`crumb.py:1217–1218`) (`dcfddf0`)

### Review Statistics

| Round | Scope | P1 | P2 | P3 | Verdict |
|-------|-------|----|----|-----|---------|
| 1 | 4 files, 19 tasks | 1 | 0 | 3 | PASS WITH ISSUES — auto-fix |
| 2 | 4 fix tasks | 0 | 0 | 0 | PASS — CONVERGED |

4 root causes consolidated (0 merges needed). All P1 and P3 findings fixed this session.


## 2026-03-22 — Session 20260322-115432 (Defensive Bash Hardening & Clarity — 25-Task Sweep)

### Summary

Session executed 25 tasks across two phases: a 20-task Wave 1 targeting defensive correctness, naming clarity, and comment quality across four scripts (`build-review-prompts.sh`, `setup.sh`, `parse-progress-log.sh`, `generate-agent-catalog.sh`) and their test files, followed by a 5-task fix cycle addressing all issues raised by the Round 1 Nitpicker team. Key behavioral fixes include bash 3.2–safe array expansion, atomic temp-file rename, cleanup trap race-window closure, unrecognized-step-key warnings, and loud-exit on invariant violation. Round 1 review found 0 P1 / 1 P2 / 4 P3 issues (all auto-fixed); Round 2 confirmed full convergence with 0 findings. 23 commits total.

### Implementation (Wave 1 — 20 tasks)

- **ant-farm-8kds**: no-op — fill_slot function already removed; temp file leak impossible in current codebase (N/A)
- **AF-110**: fix: update sync_claude_block header comment to mention create/append/replace (`ad965be`)
- **AF-154**: fix: add RETURN trap for temp file cleanup in sync_claude_block (`f22b8cb`)
- **AF-181**: refactor: rename resolve_arg to expand_at_file_arg for clarity (`7cc1789`)
- **AF-182**: fix: add readability check to expand_at_file_arg for @file arguments (`c33acf0`)
- **AF-183**: fix: add explanatory comments on non-obvious bash constructs (`8206bb2`)
- **AF-184**: fix: add EXIT trap for test temp directory cleanup on assertion failure (`eccd362`)
- **AF-185**: fix: clean up scratch-pad comment in Test 13 and add source comment for magic string in Test 7 (`3e011dc`)
- **AF-187**: fix: filter blank lines before sort in CHANGED_FILES pipeline (`c1029fc`)
- **AF-188**: fix: replace printf '%b' with literal newlines for expected_paths construction (`34f263c`)
- **AF-203**: fix: move cleanup trap inside map_init before mkdir calls (`0300937`)
- **AF-211**: fix: create temp files in destination directory for atomic rename (`c97f46b`)
- **AF-214**: fix: rename PROMPTDIR_COMPONENT to REPO_ROOT_ESCAPED with transformation-example comment (`8b74a5c`)
- **AF-258**: fix: add script-level EXIT trap as safety net for temp file cleanup (`bcc5ac9`)
- **AF-302**: fix: document classification regex and normalize keyword casing (`6286155`)
- **AF-303**: fix: add linking comment at AGENTS_CHANGED setter in setup.sh (`ffb9431`)
- **AF-305**: fix: strip surrounding quotes from YAML frontmatter name field (`c61bf77`)
- **AF-306**: fix: improve first-sentence truncation to handle abbreviations (`e4301cd`)
- **ant-farm-5nhs**: fix: add stderr warning for unrecognized step keys in parse-progress-log.sh (`4ea96ae`)
- **ant-farm-by3g**: fix: replace silent fallback with loud error exit in unreachable branch (`79970f6`)

### Review Fixes (Round 1)

- **AF-411**: fix: bash 3.2-safe empty array expansion in cleanup_temp_files (`bb192c0`)
- **AF-412**: fix: rename REPO_ROOT_ESCAPED to REPO_ROOT_SLUG in setup.sh (`495d03c`)
- **AF-413**: fix: use part1_clarity consistently in both test partition assertions (`adcda8b`)
- **AF-414**: fix: add output directory existence check in generate-agent-catalog.sh (`4b2bdea`)
- **AF-415**: fix: update stale setup.sh:L509 line reference to L515 — combined with AF-411 (`bb192c0`)

### Review Statistics

| Round | Scope | P1 | P2 | P3 | Verdict |
|-------|-------|----|----|-----|---------|
| 1 | 6 files, 20 tasks | 0 | 1 | 4 | PASS WITH ISSUES — auto-fix |
| 2 | 5 fix commits | 0 | 0 | 0 | PASS — CONVERGED |

5 root causes consolidated (1 merge: CL-1 + CL-2 → RC-2). All P2 and P3 findings fixed this session.

## 2026-03-22 — Session 20260321-213359 (Documentation & Tooling Hygiene — 40-Task Sweep)

### Summary

Session executed 40 implementation tasks across epics AF-T60 and AF-T61, covering documentation accuracy, stale comment removal, shell script hardening, and cross-reference correctness in orchestration templates, scripts, and skills. Seven parallel Crumb Gatherer agents (Opus for 6, Sonnet for 1) completed all 40 tasks in a single wave. Two Nitpicker review rounds ran post-implementation: Round 1 (4 reviewers) found 0 P1s / 4 P2s / 7 P3s and issued an auto-fix directive; Round 2 (2 reviewers) found 1 P1 in the AF-400 fix (wrong merge-conflict side kept), fixed directly by the Queen as AF-410. All 5 P1/P2 findings fixed. 7 P3 findings deferred as open crumbs. 41 commits total.

### Implementation (Wave 1 — 36 commits; 4 no-commit tasks)

- **ant-farm-sf3v**: fix: remove stale "user approval" from SCOUT_COMPLETE step label in parse-progress-log.sh (`9d7bc98`)
- **ant-farm-dxia**: fix: SETUP.md intro and code-reviewer path self-contradictions resolved (`66c2288`)
- **ant-farm-ix7m**: fix: remove stale CHANGELOG references from DOCS_COMMITTED and XREF_VERIFIED labels in parse-progress-log.sh (`66f40d7`)
- **ant-farm-d1rx**: fix: polling loop off-by-one in reviews.md — `-lt` changed to `-le` for full timeout boundary coverage (`66dd239`)
- **ant-farm-nuc1**: fix: consistent formatting for prohibition bullets, reviewer names, and sub-step labels across CLAUDE.md, RULES.md, scout.md (`ffc3df0`)
- **ant-farm-t3k0**: fix: standalone documentation polish — SSV acronym expansion, ANSI-C shell quoting, GLOSSARY severity wording, rsync stale-file warning (`2325579`)
- **ant-farm-kzz6**: docs: terminology, wording, and cross-reference polish across reviews.md, pantry.md, RULES.md (`9d1c472`)
- **ant-farm-6t89**: no-op — deprecated artifact references already resolved in prior session; no files modified
- **ant-farm-wk1a**: fix: align nitpicker-skeleton.md Round 2+ scope instructions with reviews.md (`9ab0b65`)
- **ant-farm-z8lq**: fix: add commit-range filtering section to review task ID scoping in reviews.md (`279ae7e`)
- **AF-30**: crumb metadata only — corrected AF-15 AC text for priority sort key (99→5) and now_iso format (+00:00→Z); no commit
- **AF-63**: fix: update stale code-reviewer agent description in SETUP.md (`5ad55a8`)
- **AF-64**: fix: update status skill to read exec-summaries from .crumbs/sessions/ (`ea9fcdb`)
- **AF-65**: fix: update reader comment to reference build-review-prompts.sh in parse-progress-log.sh (`a3e3d56`)
- **AF-66**: docs: add rationale comments for extract_focus_block and double-bracing in build-review-prompts.sh (`b8109dd`)
- **AF-73**: fix: remove --type=task filter from work skill pre-flight check (`c13261d`)
- **AF-74**: fix: add review-focus-areas.md row to PLACEHOLDER_CONVENTIONS audit table (`1f02be7`)
- **AF-92**: fix: document naive datetime assumption in crumb.py cmd_prune docstring and call site (stash anomaly: landed in `66dd239`)
- **AF-95**: fix: add prune to build_parser epilog in crumb --help output (`2c3d3bd`)
- **AF-108**: fix: remove stale manual-approval instructions from troubleshooting kickoff in RULES.md (`7261f62`)
- **AF-109**: fix: update installation-guide.md intro sentence to reflect CLAUDE.md orchestration-block write (`f1f40bb`)
- **AF-111**: fix: rename Step 8 to Step 8a in RULES.md to pair with existing Step 8b (`340d80b`)
- **AF-114**: fix: add minimum length check to prefix validation rules in crumb.py (`12b0a12`)
- **AF-124**: fix: add preflight warning text to code-reviewer note in SETUP.md (`f60af14`)
- **AF-146**: fix: correct stale comments in parse-progress-log.sh, build-review-prompts.sh, RULES.md (`a0daa45`)
- **AF-150**: crumb metadata only — corrected AF-141 AC#2 "trail status" → "trail show"; no commit
- **AF-153**: fix: align Big Head sed regex in build-review-prompts.sh with nitpicker pattern to include digits (`b7366c2`)
- **AF-175**: fix: add crumb ready and crumb blocked entries to crumb-cheatsheet.md Commands section (`a05edf7`)
- **AF-186**: fix: update polling code to iterate EXPECTED_REPORT_PATHS for split-instance review support (`ff5dd28`)
- **AF-204**: fix: update stale RULES.md table references and Pantry read target in CONTRIBUTING.md (`74d7839`)
- **AF-205**: fix: update stale checkpoints.md reference to checkpoints/common.md in audit table (`c2e2ad0`)
- **AF-210**: fix: document --force flag in SETUP.md setup.sh usage line (`e07b45c`)
- **AF-216**: fix: add code-reviewer.md new-machine workaround to SETUP.md (`08bfe95`)
- **AF-218**: fix: add rationale for Partial+PASS status in reviewer-skeleton.md audit row (`fc64ae6`)
- **AF-255**: fix: add missing trailing period on Why sentence in backup section (`95842ae`)
- **AF-260**: fix: strip blank lines from CHANGED_FILES_SORTED pipeline in build-review-prompts.sh (`ba0e32f`)
- **AF-297**: fix: replace imprecise Queen template read claim with explicit file enumeration in RULES.md (`84ec572`)
- **AF-299**: docs: add cross-reference comments to inline reviewer prompt blocks in reviews.md (`0a149f6`)
- **AF-300**: fix: assign explicit step numbers to cross-reference table rows in reviews.md (`3e55dfd`)
- **AF-307**: fix: add crumb CLI installation check before stderr-suppressed invocation in build-review-prompts.sh (`67668b0`)

### Review Fixes (Round 1 — P2 auto-fix)

- **AF-399**: fix: replace stale fill-review-slots.sh references in reviews.md (4 occurrences) (`65994c8`)
- **AF-400**: fix: resolve merge conflict markers in docs/installation-guide.md (`2a90f2a`)
- **AF-401**: fix: add history fallback to status.md exec-summary lookup (`20aed8e`)
- **AF-402**: fix: use array for CRUMB and strip whitespace-only lines in build-review-prompts.sh file filter (`3fdb5de`)

### Review Fixes (Round 2 — P1 Queen direct fix)

- **AF-410**: fix: correct installation-guide.md to describe repo CLAUDE.md model — re-resolved 5 conflict blocks to "Updated upstream" side; fixed /ant-farm:init → /ant-farm-init at 2 occurrences (`622c5fe`)

### Review Statistics

| Round | Scope | P1 | P2 | P3 | Verdict |
|-------|-------|----|----|-----|---------|
| 1 | 36 commits, 40 tasks, 4 reviewers (Clarity/Edge Cases/Correctness/Drift) | 0 | 4 | 7 | PASS WITH ISSUES |
| 2 | 4 fix commits (AF-399–402), 2 reviewers (Correctness/Edge Cases) | 1 | 0 | 0 | FAIL → PASS after AF-410 |

11 root causes consolidated in Round 1 (2 skipped as cross-session duplicates: AF-379, AF-345; 4 excluded as no-fix-needed). Round 2 single P1 fixed directly by Queen. 7 P3 root causes deferred as open crumbs (AF-403–AF-409).

# Changelog

## 2026-03-21 — Session 195300 (AF-T59 P3 Template Polish Sweep)

### Summary

Completed all 20 tasks in AF-T59, a P3 bug sweep targeting documentation correctness across orchestration template files (pantry.md, RULES.md, SESSION_PLAN_TEMPLATE.md, scout.md, and checkpoint files). All tasks ran in a single wave (5 agents). Round 1 review found 0 P1s and 3 P2s (error suppression, missing input guard, missing `signals` directory); all were auto-fixed and verified clean in Round 2. The 13 P3 root causes from Round 1 were repaired inline via 4 lightweight agents and verified clean in Round 3. 26 commits across 11 files.

### Implementation (Wave 1 — AF-T59, 20 tasks)

- **ant-farm-gf80**: fix: add file existence verification note to Pantry fail-fast checks (`orchestration/templates/pantry.md`) (`697b56d`)
- **ant-farm-m47x**: fix: add skeleton file existence check to Pantry Step 3 (`orchestration/templates/pantry.md`) (`f90befc`)
- **ant-farm-5d9x**: fix: use consistent shell variable syntax in crash recovery dir-check (`orchestration/RULES.md`) (`db2b8cf`)
- **ant-farm-5vs8**: fix: remove emoji risk labels and time estimate fields from SESSION_PLAN_TEMPLATE (`orchestration/templates/SESSION_PLAN_TEMPLATE.md`) (`5d0fdb0`)
- **ant-farm-8qgy**: fix: label pseudocode as conceptual in SESSION_PLAN_TEMPLATE (`orchestration/templates/SESSION_PLAN_TEMPLATE.md`) (`91e09ed`)
- **ant-farm-oluh**: fix: clarify partial verdict table runs once after all tasks, not per-failure (`orchestration/templates/pantry.md`) (`d5955fa`)
- **ant-farm-sycy**: fix: document sequential-check invariant for failure artifact path collision (`orchestration/templates/pantry.md`) (`be63d21`)
- **ant-farm-xdw3**: fix: replace misleading 'Halt' wording with skip-to-next-task semantics (`orchestration/templates/pantry.md`) (`1efefba`)
- **ant-farm-yufy**: fix: add STOP banner and forward-references to deprecated Pantry Section 2 (`orchestration/templates/pantry.md`) (`5b74678`)
- **AF-202**: fix: document local-FS synchronous-flush assumption at Pantry read sites (`orchestration/templates/pantry.md`) (`c54a5bd`)
- **AF-207**: fix: renumber sections for sequential numbering, move deprecated content to appendix (`orchestration/templates/pantry.md`) (`aff9aba`)
- **ant-farm-pxsk**: fix: replace stale hardcoded values in SESSION_PLAN_TEMPLATE (`orchestration/templates/SESSION_PLAN_TEMPLATE.md`) (`4435216`)
- **ant-farm-t8cg**: fix: replace bracket-pipe syntax with plain English OR connectors in scout.md (`orchestration/templates/scout.md`) (`468de47`)
- **AF-121**: fix: handle zero-task boundary in SSV Check 2 and add scout truncation warning (`orchestration/templates/checkpoints/startup-check.md`, `orchestration/templates/scout.md`) (`1b3fcd2`)
- **AF-201**: fix: add scout truncation count and replace wc -l with grep -c in work.md (`orchestration/templates/scout.md`, `skills/work.md`) (`37a2362`)
- **ant-farm-roqb**: fix: update stale check count from 8 to 9 after Check 3b addition (`orchestration/templates/checkpoints/review-integrity.md`, `orchestration/templates/checkpoints/common.md`) (`08e34cd`)
- **ant-farm-omwi**: fix: extract policy text from placeholder list into separate subsection (`orchestration/templates/crumb-gatherer-skeleton.md`) (`a43513a`)
- **AF-67**: fix: remove emoji from scope boundary template heading (`orchestration/templates/implementation.md`) (`ec5ccc3`)
- **AF-312**: fix: common.md Quantitative Threshold column label → Threshold / Condition (`orchestration/templates/checkpoints/common.md`) (`57027c1`)
- **ant-farm-w1dn**: fix: remove development artifacts from production checkpoint templates (`orchestration/templates/checkpoints/pre-spawn-check.md`, `orchestration/templates/checkpoints/review-integrity.md`) (`563a691`)

### Review Fixes (Round 1 P2 Auto-fixes)

- **AF-396**: fix: resolve error suppression and add signals dir to session mkdir — exit-code-checked crumb CLI calls; `2>/dev/null` patterns removed (`skills/work.md`) (`39a46a5`)
- **AF-398**: fix: add signals subdirectory to session mkdir — aligned with RULES.md canonical mkdir (`skills/work.md`) (`39a46a5`)
- **AF-397**: fix: add SESSION_START_DATE input guard to review-integrity checkpoint (`orchestration/templates/checkpoints/review-integrity.md`) (`b121acb`)

### P3 Polish (Round 1 inline, 4 agents)

- fix: P3 polish — position check promotion, term expansion, xxd portability, mkdir guard (RULES.md) (`340d12e`)
- fix: P3 polish — wc-l consistency, opaque epic ref, approval checkpoint caveat (scout, impl, template) (`148a17b`)
- fix: P3 polish — clarify curly-brace semantics, tighten placeholder regex (pantry.md) (`1f9aed4`)
- fix: P3 polish — term clarity, threshold wording, check renumbering, typo fix, heading accuracy (checkpoints) (`d56d8e5`)

### Review Statistics

| Round | Scope | P1 | P2 | P3 | Verdict |
|-------|-------|----|----|-----|---------|
| 1 | 11 files, 20 tasks | 0 | 3 | 13 | PASS WITH ISSUES |
| 2 | 2 files, 3 fix tasks | 0 | 0 | 0 | PASS — CLEAN |
| 3 | 8 files, 13 P3 root causes | 0 | 0 | 0 | PASS — CLEAN |

16 root causes consolidated (3 merges). All P2s auto-fixed same session; all P3s repaired inline. No deferred issues.

# Changelog

## 2026-03-21 — Session 20260321-180235 (Safety-Fix Propagation and RULES.md Clarity Sweep)

### Summary

Completed 24 tasks across two implementation waves and one fix cycle. Wave 1 (13 tasks) and Wave 2 (7 tasks) targeted RULES.md operator-instruction clarity and safety-feature propagation: shutdown-authorization/dispatch timing disambiguation, crash-recovery labeling, Position Check global-scope signaling, batch-mode boundary conditions, wave failure threshold counting, round-2 reviewer composition alignment, SESSION_ID collision guard, signals/ sentinel directory, sentinel-file completion protocol, post-push sync documentation, mktemp migration, and crumb prune visible-warning forms. Two tasks were pre-resolved by prior sessions; one by a concurrent fix. Round 1 review (4 reviewers, 18 raw findings → 15 root causes) found Correctness clean and four P2 propagation gaps; all P2s were auto-fixed in-session. Round 2 (2 reviewers) found 0 issues. Eleven P3 documentation-polish items deferred as AF-385–AF-395. Session produced 21 commits across 11 files.

### Implementation (Wave 1 — 13 tasks)

- **ant-farm-dnlu**: fix: distinguish shutdown authorization from dispatch timing in RULES.md with sub-bullets (`bb3d8bb`)
- **ant-farm-8evt**: fix: promote crash recovery to labeled Step 0a with conditional callout in RULES.md (`9da762d`)
- **AF-217**: fix: make Position Check global scope visually prominent in RULES.md (`a622954`)
- **ant-farm-hf9a**: fix: add batch mode boundary conditions for N=1 and partial commits in RULES.md (`f30a8e0`)
- **ant-farm-jzc3**: docs: team roster dense bullet pre-resolved (content in RULES-review.md); no change (no commit)
- **ant-farm-bb01**: docs: Information Diet section pre-resolved (removed in prior session); no change (no commit)
- **AF-120**: fix: replace silent error suppression with visible warning for crumb prune in RULES.md (`50156df`)
- **ant-farm-mtfh**: fix: clarify wave failure threshold retry counting timing in RULES.md (`16d70ea`)
- **ant-farm-s7vu**: docs: replace 'directly' with 'then' in Termination Rule to remove P3-skipping ambiguity (`efed6fb`)
- **AF-200**: fix: replace PID-based temp file naming with mktemp in review-consolidator-skeleton.md and decomposition.md (`b92e645`)
- **AF-309**: fix: file existence guard in RULES-decompose.md wc -l loop pre-resolved by AF-362 (no new commit)
- **AF-341**: fix: replace vague "notes you recorded" with progress.log reference in RULES-decompose.md (`0c8a6c3`)
- **AF-339**: fix: move AFFECTED_FILES_LIST explanation before bash snippet in RULES-lite.md (`6eb272d`)

### Implementation (Wave 2 — 7 tasks)

- **ant-farm-xyas**: docs: align RULES.md round 2+ reviewer composition with reviews.md (`7c93db5`)
- **ant-farm-jegj**: docs: add Pantry review-mode precondition guards and RULES.md validation reference (`ddb4f5a`)
- **AF-147**: docs: document review-focus-areas.md in Template Lookup table and RULES-review.md (`87977cb`)
- **AF-199**: fix: add random suffix to SESSION_ID for concurrent Queen collision guard in RULES.md and session-directory.md (`25a259f`)
- **AF-94**: docs: document all session directory prefixes in RULES.md (`2f847c9`)
- **ant-farm-e26s**: docs: document post-push sync and pre-push hook defense-in-depth in RULES.md Step 7 (`9a1b55d`)
- **ant-farm-f0x**: feat: add sentinel-file completion protocol for background subagents in RULES.md, crumb-gatherer-skeleton.md, and checkpoints/common.md (`902fd9e`)

### Review Fixes (Round 1)

- **AF-381**: fix: pass dynamic values via sys.argv in python3 crumb-filing blocks in reviews.md, review-consolidator-skeleton.md, and RULES-lite.md (`bf40c70`)
- **AF-382**: fix: replace PID-based temp files with mktemp in reviews.md (12 locations) (`a4717ff`)
- **AF-383**: fix: add random suffix to SESSION_ID in RULES-lite.md (`d99d5a6`)
- **AF-384**: fix: propagate signals/ directory to session-directory.md and RULES-lite.md (`7dec448`)

### Review Statistics

| Round | P1 | P2 | P3 | Decision |
|-------|----|----|----|----------|
| 1 | 0 | 4 | 11 | auto-fix P2s / defer P3s to crumbs |
| 2 | 0 | 0 | 0 | terminated (clean) |

18 raw findings consolidated to 15 root causes in Round 1 (3 merges). Correctness reviewer: 0 findings. All 4 P2s resolved before push. 11 P3s deferred as AF-385–AF-395.

## 2026-03-21 — Session 20260321-161341 (AF-T57: Documentation and Template Consistency Sweep)

### Summary

Completed 25 tasks targeting documentation and template consistency across the ant-farm orchestration layer (epic AF-T57). Work covered placeholder notation standardization, terminology alignment, path normalization, and missing field fixes across 21 files. All tasks were non-code documentation fixes. Round 1 review found 1 P1, 2 P2, and 4 P3 consolidated root causes; all were auto-fixed in-session. Round 2 found 1 residual P2 (concurrent-fix interaction between AF-375 and AF-370) and terminated clean after an inline fix. Session produced 24 commits.

### Implementation (Wave 1 — 14 tasks)

- **ant-farm-9aj1 / AF-301**: fix: add substitution clarification comments to prose `{CONSOLIDATED_OUTPUT_PATH}` instructions and rename `{OPEN_BEAD_IDS}` to `{OPEN_CRUMB_IDS}` in scribe-skeleton.md (`1ded8c0`)
- **ant-farm-9d4e**: fix: replace bare numeric step-7 cross-file references with descriptive names in review-consolidator-skeleton.md (`438f5bd`)
- **ant-farm-mv6b**: fix: add missing `summary` field to SendMessage pseudo-API examples in reviews.md (`287b672`)
- **AF-149**: docs: add next_step value reference table to Position Check section in RULES.md (`cd71f57`)
- **ant-farm-8awb**: fix: replace `{timestamp}` with `<timestamp>` in Hard Gates table and add checkpoint name prefix in CONTRIBUTING.md (`421fd56`)
- **AF-296**: fix: replace "priority" with "severity" for P1/P2/P3 scale in ant-farm-review-consolidator agent (`49c1767`)
- **ant-farm-bql5 / AF-311**: fix: disambiguate overloaded `{TASK_SUFFIX}` in Reviewer section of claims-vs-code.md to `{REVIEW_TYPE}` (`d1446de`)
- **AF-145**: fix: standardize progress log placeholder notation to angle-bracket format in RULES-review.md (`49e01d5`)
- **AF-176**: fix: replace cryptic `P<P>` placeholder with `P<severity>` in review-consolidator-skeleton.md crumb-filing template (`6737888`)
- **AF-338**: fix: normalize bare path references in scout.md to `~/.claude/orchestration/` prefix (`23a65cd`)
- **ant-farm-k476**: docs: define INFRASTRUCTURE/SUBSTANCE FAILURE taxonomy in terms.md and add cross-references to pantry.md and four checkpoint files (`0e127e2`)
- **AF-337**: fix: replace `{session-dir}` with `{SESSION_DIR}` in pantry.md task brief write instruction (`9ec0f5c`)

### Implementation (Wave 2 — 1 task)

- **ant-farm-im8**: refactor: standardize task ID placeholder naming to `{TASK_ID}` / `{TASK_SUFFIX}` across 9 active and archive template files; update PLACEHOLDER_CONVENTIONS.md audit table (`3b088c0`)

### Review Fixes (Round 1)

- **AF-370**: fix: convert remaining REVIEW_TRIAGED entries in RULES-review.md L220/L222 to angle-bracket notation (`53f2429`)
- **AF-371**: fix: replace "priority" with "severity" in OUT-OF-SCOPE rule in review-consolidator-skeleton.md (`5e72ccd`)
- **AF-372**: fix: append `next_step=STEP_6_ESV` to SCRIBE_COMPLETE progress log entry in scribe-skeleton.md (`04eec6a`)
- **AF-373**: fix: revert `{SESSION_DIR}` to `{session-dir}` in pantry.md path references for internal consistency (`baa5911`)
- **AF-374**: fix: replace "Big Head" with "Review Consolidator" in PLACEHOLDER_CONVENTIONS.md reviews.md audit row (`fa0b794`, `a92bd6b`, `519b756`)
- **AF-375**: fix: remove stale `{crumb-ids}`, `{names}`, `{hashes}`, `{range}` from RULES-review.md Tier 2 column in PLACEHOLDER_CONVENTIONS.md (`a92bd6b`)
- **AF-376**: fix: normalize bare GLOSSARY.md path reference in scout.md:L54 to `~/.claude/orchestration/` prefix (`19fe698`)
- **AF-377**: fix: update implementation-summary.md to use "Review Consolidator" agent name (`0ab66e7`)
- **AF-378**: fix: update reviewer-skeleton.md to use "Review Consolidator" agent name (`540888e`)

### Review Fixes (Round 2 — inline)

- **AF-380**: fix: remove stale `{count}` from RULES-review.md Tier 2 column in PLACEHOLDER_CONVENTIONS.md after concurrent AF-370/AF-375 interaction (`e5d3b37`)

### Review Statistics

| Round | Scope | P1 | P2 | P3 | Verdict |
|-------|-------|----|----|-----|---------|
| 1 | 21 files, 15 tasks | 1 | 2 | 4 | NEEDS WORK |
| 2 | fix commits only | 0 | 1 | 0 | PASS WITH ISSUES (inline fix) |

10 raw findings consolidated to 7 root causes in Round 1 (3 merges). Round 2 found 1 residual P2 from a concurrent-fix interaction; fixed inline by Queen. All P1/P2 findings resolved before push.

### Open Issues

- **AF-379** (P3): Remaining "Big Head" → "Review Consolidator" terminology in `orchestration/templates/checkpoints/common.md`, `orchestration/reference/session-directory.md`, and `orchestration/reference/dependency-analysis.md`. Deferred — was out of scope for all fix agents this session.


## 2026-03-21 — Session 135712 (AF-T56: Stale Agent Name Rename Campaign)

### Summary

Completed epic AF-T56, a mechanical find-and-replace campaign propagating the AF-225 agent renames (Pest Control → Checkpoint Auditor, Big Head → Review Consolidator, Nitpicker → Reviewer, Surveyor → Spec Writer, Forager → Researcher, Architect → Task Decomposer, CCO → pre-spawn-check, fix-dp → fix-cg) across all orchestration files. 20 implementation tasks ran across 2 waves, followed by 2 review rounds that caught and fixed 6 P1/P2 gaps. Session produced 23 commits touching 31 files and closed all 26 tasks.

### Implementation (Waves 1–2)

- **AF-285**: fix: update agent body text to canonical new names — 9 agent files (checkpoint-auditor, prompt-composer, review-consolidator, 4 reviewers, spec-writer, task-decomposer) (`5db7dbc`)
- **AF-286**: fix: replace stale Pest Control/Nitpicker names in checkpoint templates and skeleton — checkpoint templates and review-consolidator-skeleton.md (`4e5f4c8`)
- **AF-287**: fix: replace stale Pest Control/Big Head/Nitpicker names in RULES.md annotations (`0cbc88a`)
- **AF-288**: fix: replace stale Nitpicker/Architect names in RULES-decompose.md table cells (`5381bc2`)
- **AF-289**: fix: replace stale agent names in README.md and CONTRIBUTING.md (`fb30a44`)
- **AF-290**: fix: replace stale Nitpicker/Architect names in GLOSSARY.md checkpoint table (`64793a6`)
- **AF-291**: fix: replace stale agent names in SESSION_PLAN_TEMPLATE.md Quality Review section (`b921d88`)
- **AF-292**: fix: global find-and-replace of stale display names in reviews.md (`9d79ce3`)
- **AF-293**: fix: regenerate agent-catalog.md to replace Nitpicker with Reviewer team (`aefdeb6`)
- **AF-294**: fix: replace stale Nitpicker terminology in setup.sh preflight warning (`cd484ac`)
- **AF-198**: fix: rename fix-dp/fix DPs to fix-cg/fix CGs after Crumb Gatherer rename (`a7b2b1a`)
- **AF-308**: fix: redirect stderr to /dev/null for crumb list in cross-session dedup (`62f9c93`)
- **AF-310**: fix: split Step 10 into send-and-end-turn and reply-handling phases (`9f14d6e`)
- **AF-314**: verify: big-head-skeleton.md rename AC already satisfied — no commit needed
- **AF-298**: verify: RULES-review.md DP abbreviation expansion satisfied by AF-198 — no commit needed
- **ant-farm-2sjc**: fix: add [OUT-OF-SCOPE] severity enforcement to Review Consolidator logic (`1035613`)
- **ant-farm-fvui**: fix: rename 'Fix handoff' label to 'Review complete' in review-consolidator-skeleton.md (`9dea576`)
- **ant-farm-uul5**: fix: clarify 'subsequent turns' in Review Consolidator retry protocol (`c8794d0`)
- **ant-farm-ldha**: fix: replace nonexistent P4 severity with P1 vs P3 example in review-consolidator (`5813d72`)
- **ant-farm-retj**: verify: Cross-Review Messaging already in correct position — no commit needed

### Review Fixes (Round 1)

- **AF-351**: fix: rename fix-dp to fix-cg in reviews.md:L1094–L1157 (`0398d39`)
- **AF-352**: fix: rename Pest Control → Checkpoint Auditor in tdv.md (all 5 occurrences) (`3b03dd5`)
- **AF-353**: fix: update stale Nitpicker/Big Head names in GLOSSARY.md L27 and L46 (`aa4d9d1`)
- **AF-354**: fix: rename old role names to canonical names in RULES-decompose.md body text (`7647d0c`)
- **AF-355**: fix: update stale skeleton template filenames in CONTRIBUTING.md, README.md, PLACEHOLDER_CONVENTIONS.md (`46971a6`)
- **AF-356**: fix: add source provenance to code-reviewer.md missing warning in setup.sh (`4a5b49b`)

### Review Statistics

| Round | Scope | P1 | P2 | P3 | Verdict |
|-------|-------|----|----|-----|---------|
| 1 | 29 files, 20 tasks | 2 | 4 | 12 | PASS WITH ISSUES |
| 2 | 6 fix tasks | 0 | 0 | 1 | PASS |

19 root causes consolidated in Round 1 (24 raw → 19 after dedup; 1 skipped as cross-session duplicate). Round 2 confirmed all P1/P2 fixes landed cleanly. 13 P3 items deferred to Future Work trail (12 from Round 1 + AF-369 from Round 2).


## 2026-03-21 — Session 20260321-102858 (Installer, crumb.py, and orchestration docs quality sweep)

### Summary

Eighteen tasks completed across 5 implementation waves and a review fix wave, targeting three active epics: AF-T53 (installer plumbing), AF-T54 (crumb.py quality), and AF-T55 (orchestration docs). Work wired MCP registration into the install/uninstall flow, hardened MCP server error handling, cleaned up crumb.py temp-file safety and --from-json semantics, and resolved a broad set of documentation drift and naming issues across orchestration templates and test files. Round 1 review found 0 P1 and 4 P2 consolidated issues; all 4 auto-fixed. Round 2 terminated clean. 469 tests pass. 18 commits total.

### Implementation (Waves 1–5)

- **AF-317**: fix: wire registerMcp/unregisterMcp into installer flow — sequential MCP registration in `npm/bin/install.js`; 8 new tests (`16352ce`)
- **AF-320**: fix: guard empty stdout and filter SystemExit in MCP server — empty-output guard in `_run_cmd_json`, tightened `_run_doctor` exit-code filter, 5 new tests (`9a64172`)
- **AF-321**: fix: clean up .jsonl.tmp on any write_tasks failure and guard --from-json changed flag — bare-except cleanup and per-field comparison in `crumb.py`; 5 new tests (`65e7856`)
- **AF-248**: fix: add context-aware CRUMB fallback and startup validation in build-review-prompts.sh — three-tier resolution + `render-template --help` gate + smoke-test script (`4a23405`)
- **AF-324**: fix: correct checkpoint count to 7, add TDV row, fix step refs and CONTRIBUTING line range — GLOSSARY.md and CONTRIBUTING.md (`246e696`)
- **AF-318**: fix: add RULES-lite.md to install manifest and fix JSDoc step numbering — `npm/install-manifest.json` entry; 10-step JSDoc in `install.js` (`08a2d92`)
- **AF-323**: fix: correct test naming, remove dead import, rename vague constant — `test_queries.py`, `test_crud.py`, `test_cli.py` (`01824c4`)
- **AF-250**: fix: align cmd_render_template OSError message with acceptance criteria — `crumb.py` L2550 message format (`8533f0a`)
- **AF-325**: fix: correct progress log labels and role names in RULES-lite and RULES-decompose — `STEP_1_SELECT`, `STEP_3_IMPLEMENT`, canonical role names (`3dcc053`)
- **AF-319**: fix: progress event map, JSDoc, test helper rename, hook warnings, trimEnd symmetry — `progress-reader.js`, `manifest.js`, `install.test.js`, `install.js`, `claude-md.js` (`8e109a1`)
- **AF-249**: docs: replace stale fill_slot reference with crumb render-template — `review-consolidator-wiring.md` L111 (`ef0aa71`)
- **AF-326**: docs: fix path convention in pantry.md and add Crumb Gatherer cross-ref in scout.md (`841d552`)
- **AF-251**: no-op — stale comment at `crumb.py:702` already cleaned by earlier wave; closed without commit
- **AF-322**: refactor: fix PEP 8 naming and add config counter validation note — `crumb.py` (`d9ad5f1`)

### Review Fixes (Round 1)

- **AF-327**: fix: renumber RULES.md Steps 5b/5c/6 to 5/6/7, matching GLOSSARY.md — RULES.md + 8 propagation files (`bfd34ec`)
- **AF-328**: fix: guard _run_doctor against empty cmd_doctor output — `mcp_server.py` + new test (`080c5b4`)
- **AF-329**: fix: rename skippedAbsPaths to skippedRelPaths in uninstall test — `npm/test/uninstall.test.js` (`5a6ba87`)
- **AF-330**: refactor: rename d to session_dir in _make_session_dir — `tests/test_cli.py` (`71ddd06`)

### Review Statistics

| Round | Scope | P1 | P2 | P3 | Verdict |
|-------|-------|----|----|-----|---------|
| 1 | 32 files, 14 tasks | 0 | 4 | 17 | PASS WITH ISSUES |
| 2 | 4 fix commits | 0 | 0 | 0 | PASS |

21 root causes consolidated (5 skipped via cross-session dedup). 4 P2s auto-fixed; 17 P3s filed as AF-331 through AF-347. 1 drift observation filed as AF-348 (TOTAL_STEPS constant).


## 2026-03-20 — Session 20260320-193617 (Complete rename: metaphor names and checkpoint acronyms to canonical descriptive names)

### Summary

Eighteen tasks completed across six implementation waves, a full review cycle (2 rounds), and a review fix wave. Work delivered the complete rename of all ant-farm orchestration identifiers — 12 agent files, 6 checkpoint files, and references across 46 files — from metaphor names (Big Head, Pest Control, Nitpicker, Surveyor, Architect) and checkpoint acronyms (SSV, CCO, WWD, CMVCC, CCB, ESV) to descriptive canonical names. Round 1 review found 3 P1 and 7 P2 consolidated issues; all 10 auto-fixed. Round 2 found 1 P1 and 1 P2; both fixed; round 3 terminated clean. All 23 structural tests pass. 16 commits total.

### Implementation (Waves 1–5)

- **AF-225**: refactor: rename 12 agent `.md` files from metaphor names to descriptive names; update `name:` frontmatter in all 12 (`45acb96`)
- **AF-226**: refactor: rename 6 checkpoint files from acronyms to descriptive names; follow-up `git rm` for stash-conflict residuals (`73690d7`, `0916d9c`)
- **AF-227**: refactor: update agent names, checkpoint names, and progress-log key strings in RULES.md, RULES-decompose.md, RULES-review.md; retry for display-form references (`5284960`, `2010b1a`)
- **AF-228**: refactor: update 17 template and checkpoint files with new agent names, `reviewer-team` team name, and new checkpoint filenames (`55e9353`)
- **AF-229**: docs: update CLAUDE.md, GLOSSARY.md, README.md, CONTRIBUTING.md, generate-agent-catalog.sh, setup.sh migration table; regenerate agent-catalog.md; resolve 3 merge conflicts in README (`4220870`, `743445b`)
- **AF-230**: fix: update RULES-decompose.md (3 stale `subagent_type` calls), agent-types.md, model-assignments.md, big-head-wiring.md, and test docstrings; all 23 pytest tests pass (`b742a49`)

### Review Fixes (Rounds 1–2)

- **AF-274, AF-277**: fix: rename `nitpicker-skeleton.md` → `reviewer-skeleton.md`, `big-head-skeleton.md` → `review-consolidator-skeleton.md`, `big-head-wiring.md` → `review-consolidator-wiring.md`; update wiring L3 pointer (`ee075e7`)
- **AF-283**: fix: remove self-contradictory "judgment-heavy" label from sonnet model comment in reviews.md (`1252b09`)
- **AF-281**: fix: update `ant-farm-pest-control` → `ant-farm-checkpoint-auditor` in RULES-decompose.md Step 5 TDV spawn (`5ac1931`, `47e8254`)
- **AF-284**: fix: separate `find` stderr from null-delimited stdout in setup.sh (`82c6e38`)
- **AF-275, AF-276, AF-278, AF-280, AF-282**: fix: update `reviewer-team` team name, `fix-pc-scope-verify`/`fix-pc-claims-vs-code` agent names, and reviewer section labels in model-assignments.md, review-consolidator-wiring.md, reviews.md (`dc1735c`)
- **AF-315, AF-316** (RC-A2 + RC-B2): fix: update `_BUILD_SCRIPT_SKELETONS` in tests/test_orchestration.py to new skeleton names; replace `big-head-skeleton.md` references in reviews.md (7) and model-assignments.md (3) (`0e20449`)

### Review Statistics

| Round | Scope | P1 | P2 | P3 | Verdict |
|-------|-------|----|----|-----|---------|
| 1 | 46 files, 6 agents | 3 | 7 | 29 | NEEDS WORK → auto-fix |
| 2 | fix commits ee075e7..dc1735c | 1 | 1 | 0 | NEEDS WORK → fix-now |

10 root causes consolidated in round 1; 2 in round 2. All P1/P2 findings fixed before session close.


## 2026-03-20 — Session 171420 (crumb render-template: new subcommand, pipeline wiring, test coverage)

### Summary

Nine tasks completed across three implementation waves and a review fix pass. Work delivered the `crumb render-template` subcommand (AF-223), replaced the `fill_slot` shell function with a single `crumb render-template` call per prompt (AF-224), added structural test coverage for cross-references, frontmatter, checkpoints, GLOSSARY, and template slot coverage (AF-221, AF-222), and removed the stale `orchestration/_archive/` directory references (AF-220). Round 1 review found 1 P1 (CRUMB path resolution breaks in installed context) and 3 P2s (stale docs, missing OSError handling, misleading comment), all auto-fixed as AF-248–AF-251; Round 2 verified all fixes clean with 0 new findings. 8 commits total.

### Implementation (Waves 1–3)

- **AF-220**: chore: remove `orchestration/_archive/` gitignore entry and all references across RULES.md, scout.md, SETUP.md, PLACEHOLDER_CONVENTIONS.md, setup.sh, CONTRIBUTING.md, docs/installation-guide.md (`4ff5335`)
- **AF-223**: feat: add `render_template()` pure function and `cmd_render_template()` CLI handler to `crumb.py`; add `tests/test_render_template.py` (31 tests, all 6 ACs) (`e230860`)
- **AF-221**: feat: add `tests/test_orchestration.py` with 21 structural tests for subagent cross-references, frontmatter validity, checkpoint completeness, and GLOSSARY coverage (`b3dee1b`)
- **AF-224**: refactor: replace `fill_slot()` in `build-review-prompts.sh` with single `crumb render-template` call per prompt; all 18 shell tests pass unchanged (`c551975`)
- **AF-222**: feat: extend `tests/test_orchestration.py` with `test_template_slot_coverage` and `test_skill_file_mapping`; 23 tests total (`c9da5ab`)

### Review Fixes (Round 1)

- **AF-248**: fix: add context-aware CRUMB path fallback (repo-local → installed) in `scripts/build-review-prompts.sh:46`; add path-resolution tests (`297857b`, `d6dc2bc`)
- **AF-249, AF-250, AF-251**: fix: update stale fill_slot refs in `PLACEHOLDER_CONVENTIONS.md` and `crumb.py:2289`; add OSError handling in `cmd_render_template`; fix misleading comment at `crumb.py:702` (`bebabff`)

### Review Statistics

| Round | Scope | P1 | P2 | P3 | Verdict |
|-------|-------|----|----|-----|---------|
| 1 | 13 files, 5 tasks | 1 | 3 | 9 | PASS WITH ISSUES |
| 2 | fix commits, 4 tasks | 0 | 0 | 0 | PASS CLEAN |

13 root causes consolidated (5 findings merged into 3 groups). All P1/P2 auto-fixed; 9 P3 findings filed as crumbs for future sessions.

## 2026-03-20 — Session 20260320-141218 (setup.sh Hardening: Identity Check, Manifest Cleanup, Portability)

### Summary

Eight planned tasks and two review-driven fix tasks completed across three waves and two review rounds. Work focused on hardening `scripts/setup.sh`: a crumb identity sentinel and `--force` bypass (AF-51), `.local` override detection with RULES.md documentation (AF-52/AF-118), manifest-based orphan cleanup and `.af-bak.` backup pruning (AF-53), plus documentation accuracy fixes in `orchestration/PLACEHOLDER_CONVENTIONS.md` and `orchestration/templates/big-head-skeleton.md`. Round 1 review found 2 P2 issues (misleading "stubs" header, `mapfile` bash 3.2 incompatibility) that were auto-fixed; Round 2 verified both fixes clean with 0 findings. 7 commits total.

### Implementation (Waves 1–3)

- **AF-51**: feat: add crumb identity sentinel and `--force` flag — `crumb.py:2` sentinel, FORCE flag parsing, identity-check `elif` in Step 5 of `setup.sh` (`b7e3541`)
- **AF-115 + AF-122**: fix: audit table corrections and line number removal — corrected placeholder name, added missing entry, removed stale line-number citations, deduplicated Compliance Status in `orchestration/PLACEHOLDER_CONVENTIONS.md` (`1bc50fe`)
- **AF-116 + AF-123**: fix: quote shell paths and add mkdir prose handlers — mkdir-failure prose handlers for both bash blocks in `orchestration/templates/big-head-skeleton.md` (`8d54eea`)
- **AF-52 + AF-118**: feat: add .local override detection and code-reviewer verification — inline `.local` detection in orchestration install loop, HTML comment + Queen Prohibition in `orchestration/RULES.md`, reference sentence in `orchestration/SETUP.md` (`fb14fa5`)
- **AF-53**: feat: add manifest-based orphan cleanup and backup pruning — `INSTALLED_FILES` accumulator, manifest write, orphan cleanup, `.af-bak.` suffix migration, `BACKUP_KEEP=5` pruning in `scripts/setup.sh` (`e81d09d`)

### Review Fixes (Round 1 auto-fix)

- **AF-208**: fix: replace misleading 'stubs' section header with accurate description — `crumb.py:443` comment-only fix (`6b39315`)
- **AF-209**: fix: replace mapfile with portable while-read loop — `scripts/setup.sh:629` bash 3.2 compatibility fix (`b0e8659`)

### Review Statistics

| Round | Scope | P1 | P2 | P3 | Verdict |
|-------|-------|----|----|-----|---------|
| 1 | 6 files, 8 tasks | 0 | 2 | 9 | PASS WITH ISSUES |
| 2 | 2 fix commits | 0 | 0 | 0 | PASS — CLEAN |

15 root causes consolidated. 4 cross-session deduplication skips applied (RC-1/AF-117, RC-8/AF-33, RC-9/AF-92, RC-11/AF-76). 9 P3 crumbs filed (AF-210–AF-218); 1 P2 drift crumb filed (AF-219: `docs/installation-guide.md` backup suffix mismatch).



## 2026-03-18 — Session 20260318-000524 (Dirt Pusher to Crumb Gatherer Rename)

### Summary

Completed a full framework-wide rename of "Dirt Pusher" → "Crumb Gatherer" and "DMVDC" → "CMVCC" across 5 implementation tasks (AF-191–195) touching 27 files in 8 commits (~1h 20m). Round 1 review across 4 reviewers produced 2 P2s and 10 deferred P3s; both P2s were auto-fixed as AF-196 and AF-197. Round 2 found 0 issues. 10 P3 findings were filed to the backlog (AF-198–AF-207).

### Implementation (Waves 1–2)

- **AF-191**: refactor: rename checkpoint and skeleton files — `git mv` of `dirt-pusher-skeleton.md` → `crumb-gatherer-skeleton.md` and `checkpoints/dmvdc.md` → `checkpoints/cmvcc.md`; updated content in those files and in `common.md`, `wwd.md`, `cco.md` (`d0ce918`, `332d1ea`)
- **AF-192**: refactor: update orchestration rules, glossary, and state templates — replaced DMVDC/Dirt Pusher across `RULES.md`, `RULES-review.md`, `queen-state.md`, `GLOSSARY.md`, `PLACEHOLDER_CONVENTIONS.md`; updated event keys, agent names, artifact globs (`d368792`)
- **AF-193**: refactor: update orchestration template prose — replaced legacy terminology across 8 template files including `pantry.md`, `reviews.md`, `implementation.md`, and fix-team naming tables (`2361664`)
- **AF-194**: refactor: update reference docs and agent definition files — replaced all occurrences across 4 reference files and 4 agent definition files (`4e00b3d`)
- **AF-195**: refactor: update top-level docs, scripts, skills, and remove ghost files — updated `README.md`, `CONTRIBUTING.md`, `parse-progress-log.sh`, `skills/work.md`; removed 3 stale ghost files from `~/.claude/orchestration/` (`6edb529`)

### Review Fixes (Round 1 P2)

- **AF-196**: fix: strip whitespace from REVIEW_ROUND before regex validation — `tr -d '[:space:]'` added at `RULES-review.md:L33` (`c15cbdc`)
- **AF-197**: fix: correct CCB model in README Hard Gates table from haiku to sonnet — `README.md:L81` updated to match `model-assignments.md:L14` (`44dc8ad`)

### Review Statistics

| Round | Scope | P1 | P2 | P3 | Verdict |
|-------|-------|----|----|-----|---------|
| 1 | 27 files, 5 tasks | 0 | 2 | 10 | PASS WITH ISSUES |
| 2 | 2 fix tasks | 0 | 0 | 0 | PASS |

12 root causes consolidated (21 raw findings). 2 P2s auto-fixed; 10 P3s deferred to backlog (AF-198–AF-207); 2 skipped as cross-session duplicates (→ AF-120, AF-146).


## 2026-03-18 — Session 20260317-203111 (Split-Instance Reviewer Support)

### Summary

Completed the split-instance reviewer feature across 10 tasks in 5 execution waves (~2h 5m). The primary work (AF-163–AF-170) added file-partitioning logic to `build-review-prompts.sh` so that Clarity and Drift reviewer prompts are split across multiple instances when the changed-file count exceeds `REVIEW_SPLIT_THRESHOLD`, while Correctness and Edge Cases always receive the full file list. Supporting changes updated model-assignment docs to reflect the mixed-model Nitpicker team (opus for Correctness/Edge Cases, sonnet for Clarity/Drift), revised Big Head templates for variable report counts and split-instance dedup, updated wiring docs and `RULES-review.md` for dynamic member lists, and added 18 integration tests. Review round 1 found 2 P2 issues (unvalidated env var, stale GLOSSARY entries) that were fixed and verified clean in round 2. 10 P3 deferred items were filed to the backlog. 11 commits total.

### Implementation (Waves 1–5)

- **AF-163**: docs: update Nitpicker model assignments — Correctness and Edge Cases now opus (`orchestration/reference/model-assignments.md`, `reviews.md`, `GLOSSARY.md`, `big-head-wiring.md`) (`3ca2c1d`)
- **AF-164**: docs: specify opus model for Correctness and Edge Cases reviewers in RULES-review and reviews.md TeamCreate blocks (`orchestration/RULES-review.md`, `orchestration/templates/reviews.md`) (`fe54c05`)
- **AF-165**: fix: audit and remove stale all-Sonnet Nitpicker references; revert out-of-scope Step 5.5 addition (`dependency-analysis.md`, `_archive/ORCHESTRATOR_DISCIPLINE.md`, `_archive/QUALITY_REVIEW_TEMPLATES.md`, `RULES-decompose.md`) (`7eceb15`, `fea5527`)
- **AF-166**: feat: add file partitioning logic to build-review-prompts.sh with REVIEW_SPLIT_THRESHOLD env var and 9 unit tests (`scripts/build-review-prompts.sh`, `tests/test_build_review_prompts.sh`) (`3352948`)
- **AF-167**: feat: add preflight team-size check and 4 tests for split instance return table and Big Head expected paths (`scripts/build-review-prompts.sh`, `tests/test_build_review_prompts.sh`) (`ed0579c`)
- **AF-168**: feat: update Big Head skeleton for variable report count and split-instance dedup guidance (`orchestration/templates/big-head-skeleton.md`, `orchestration/reference/big-head-wiring.md`, `orchestration/templates/reviews.md`) (`c994be9`)
- **AF-169**: docs: update wiring docs and RULES-review for split instance team setup — dynamic member lists, naming convention, idle semantics, named-member SendMessage (`orchestration/reference/big-head-wiring.md`, `orchestration/RULES-review.md`, `orchestration/templates/reviews.md`) (`21732e7`)
- **AF-170**: test: add integration tests for split-instance file partitioning — 5 tests covering threshold boundaries, file-list coverage, and Big Head expected_paths (`tests/test_build_review_prompts_split.sh`) (`4b1820e`)

### Review Fixes (Round 1 P2)

- **AF-179**: fix: validate REVIEW_SPLIT_THRESHOLD is a positive integer — regex guard `^[1-9][0-9]*$` added after default assignment (`scripts/build-review-prompts.sh`) (`ee01178`)
- **AF-180**: fix: update GLOSSARY.md stale Scribe and Nitpicker agent entries — `general-purpose` → `ant-farm-technical-writer` and unified file → four-file brace expansion (`orchestration/GLOSSARY.md`) (`1db08a0`)

### Review Statistics

| Round | Scope | P1 | P2 | P3 | Verdict |
|-------|-------|----|----|-----|---------|
| 1 | 13 files, 8 tasks | 0 | 2 | 10 | PASS WITH ISSUES |
| 2 | 2 fix tasks | 0 | 0 | 0 | PASS |

15 root causes consolidated (20 raw findings). 2 P2s auto-fixed; 10 P3s deferred to backlog (AF-181–AF-190); 3 skipped as cross-session duplicates.

## 2026-03-17 — Session 20260317-193045 (--from-file Feature, Heredoc Migration, Review Fixes)

### Summary

Session completed 5 tasks across 2 execution waves and 2 review rounds in approximately 55 minutes. Wave 1 shipped the `crumb create --from-file` feature (AF-161) and migrated the Big Head template away from fragile `--from-json $(cat ...)` heredoc concatenation (AF-162). Round 1 review across four reviewers produced 3 P2 and 5 P3 findings; the 3 P2s were auto-fixed in a second wave as AF-171, AF-172, and AF-173. Round 2 found zero new findings and all 10 acceptance criteria passed. The 5 P3 findings were deferred as open crumbs. 5 commits total.

### Implementation (Wave 1–2 + Review Fixes)

- **AF-161**: feat: add `--from-file` flag to `crumb create` for JSON file input (`crumb.py`, `tests/test_crud.py`) (`2ae72fd`)
- **AF-162**: docs: switch Big Head crumb filing to `--from-file` to fix heredoc escaping (`orchestration/templates/big-head-skeleton.md`, `orchestration/reference/crumb-cheatsheet.md`) (`ee09a31`)
- **AF-171**: fix: add `is_dir()` guard and widen `except` to `OSError` in `cmd_create --from-file` (`crumb.py:846-851`) (`93ad832`)
- **AF-172**: fix: warn on stderr when `--fix` silently removes malformed lines (`crumb.py:2175-2180`, `tests/test_doctor.py`) (`b02e4df`)
- **AF-173**: fix: replace `--from-json` heredoc patterns with `--from-file` across templates (`orchestration/templates/reviews.md`, `orchestration/templates/decomposition.md`, `orchestration/templates/architect-skeleton.md`, `agents/ant-farm-architect.md`) (`1aab383`)

### Review Statistics

| Round | Scope | P1 | P2 | P3 | Verdict |
|-------|-------|----|----|-----|---------|
| 1 | 9 files, 2 tasks (AF-161, AF-162) | 0 | 3 | 5 | PASS WITH ISSUES |
| 2 | fix commits only, 3 tasks (AF-171, AF-172, AF-173) | 0 | 0 | 0 | PASS |

8 root causes consolidated (2 cross-session duplicates skipped: C1 → AF-158, E4 → AF-92). All 3 P2 findings resolved; 5 P3 findings filed as AF-174 through AF-178 and deferred.


## 2026-03-17 — Session 20260317-162123 (Large-Scale Maintenance Sweep — crumb.py, Scripts, Tests)

### Summary

25 tasks completed across crumb.py, shell scripts, and test files in a single-wave batch. Work covered dead-code removal, behavioral correctness fixes (counter arithmetic, status transition warnings, path validation, import path warnings), shell script security and robustness fixes (anchored grep, temp-file leak, mktemp diagnostic, sed regex), and test hygiene (dedup, rename, restructure, import cleanup). Round 1 review found 0 P1, 1 P2, 8 P3 across 10 root causes; the P2 (outer `set -e` aborting the test harness) was auto-fixed as AF-152 and verified clean in Round 2. 25 commits total.

### Implementation (Wave 1 — 24 tasks + 1 review fix)

**crumb.py — dead code and correctness**
- **AF-88**: fix: remove unused `import re` from crumb.py import block (`ba37f6e`)
- **AF-42**: fix: remove unused `iter_jsonl` to eliminate SystemExit-in-generator (`c195bb4`)
- **AF-34**: fix: rename `seen` → `merged` in `_get_blocked_by` for type/name accuracy (`baf3730`)
- **AF-36**: fix: add comment to document last-wins behavior in `_convert_beads_record` (`aac6d5c`)
- **AF-89**: fix: remove unnecessary f-string prefix from plain literal in `cmd_prune` (`25ede64`)

**crumb.py — behavioral fixes**
- **AF-70**: fix: warn on `in_progress → open` transition in `cmd_update` (`f284228`)
- **AF-71**: fix: advance `next_crumb_id` past explicit numeric IDs in `cmd_create` (`5af3e6a`)
- **AF-32**: fix: clamp counter and unconditionally write config in `cmd_import` (`84925fa`)
- **AF-72**: fix: add `is_dir()` check to `cmd_import` path validation (`f5306a4`)
- **AF-43**: fix: emit stderr warning for blocks dep to missing target in `_apply_blocks_deps` (`8c0d13d`)
- **AF-45**: fix: use only `links.get("parent")` in `cmd_doctor` parent lookup (`47363af`)

**scripts**
- **AF-81, AF-113**: fix: anchor identity grep with `-x` and fix `$blockfile` leak on awk failure (`71f2913`)
- **AF-148**: fix: add `mktemp -d` error diagnostic in `map_init` (`fe871ac`)
- **AF-151**: fix: include digits in sed slot-conversion regex (`f9bcab1`)

**tests — clarity and deduplication**
- **AF-31**: fix: rename misleading test to reflect closed→in_progress guard (`073ac52`)
- **AF-37**: refactor: remove `_blocked_args()` passthrough helper, inline `Namespace()` directly (`ecd7d7b`)
- **AF-38**: fix: split conflated FileLock umbrella test into two focused tests (`9c20870`)
- **AF-39**: fix: replace dual-or assertion with precise "is not a trail" check (`f879dc3`)
- **AF-44**: fix: remove duplicate `cleanup_stale_tmp_files` tests from `test_doctor.py` (`0441ffa`)
- **AF-85**: fix: move `import os` to top-level import block, remove inline alias (`fd009ad`)
- **AF-90**: refactor: extract duplicated `_backdate` into module-level helper (`46feb6c`)
- **AF-91**: fix: rename `_OLD_MTIME_SECS` → `_OUTSIDE_ACTIVE_GUARD_SECS` to clarify purpose (`f9f0995`)

**test harness**
- **AF-112**: fix: add `-e` to set options in test harness with explanatory comment (`140d0df`)

### Review Fixes (Round 1 → Round 2)

- **RC-1 / AF-152**: fix: replace `|| true; local rc=$?` with `local rc=0; ( ... ) || rc=$?` in `run_test()` to correctly capture subshell exit code under outer `set -e` (`475f791`, `16c1fe4`)

### Review Statistics

| Round | Scope | P1 | P2 | P3 | Verdict |
|-------|-------|----|----|-----|---------|
| 1 | 12 files, 24 tasks | 0 | 1 | 8 | PASS WITH ISSUES |
| 2 | 1 file, 1 fix task | 0 | 0 | 0 | CLEAN |

10 root causes consolidated (16 raw findings). 1 cross-session dedup skip (RC-3 → AF-146 already open). 9 new crumbs filed (AF-152–AF-160); AF-152 fixed this session, AF-153–AF-160 deferred as P3.


## 2026-03-16 — Session 144528 (next_step Breadcrumbs, Crumb Cheat Sheet, Review Fix Cycle)

### Summary

Five tasks completed in two feature waves followed by a two-round Nitpicker review cycle. AF-140 added crash-recovery `next_step=` breadcrumbs to all progress log echo statements across RULES.md and RULES-review.md and extended parse-progress-log.sh to display them. AF-141 added a crumb CLI cheat sheet. Round 1 found 3 P2 and 7 P3 issues across 10 root causes; the three P2s were auto-fixed as AF-142, AF-143, and AF-144. Round 2 returned PASS with zero findings. 5 commits total.

### Implementation (Waves 1–2 + fix cycle)

- **AF-140**: feat: add next_step breadcrumbs to progress log entries — appended `|next_step=<VALUE>` to all 22 echo statements across `orchestration/RULES.md` and `orchestration/RULES-review.md`; added mandatory Position Check block; extended `scripts/parse-progress-log.sh` to extract and surface the breadcrumb value
- **AF-141**: docs: add crumb CLI cheat sheet and register in RULES.md permitted list — created `orchestration/reference/crumb-cheatsheet.md` (78 lines) with syntax templates, examples, and gotchas for all 9 crumb subcommands
- **AF-142**: fix: make REVIEW_TRIAGED next_step conditional on decision value — split unconditional `next_step=STEP_4_DOCS` into fix-path (`next_step=FIX_SCOUT`) and non-fix-path branches in `orchestration/RULES.md` and `orchestration/RULES-review.md`
- **AF-143**: fix: macOS grep -P compat in build-review-prompts.sh — replaced `grep -qP` with `grep -qE` at both scan call sites in `scripts/build-review-prompts.sh`
- **AF-144**: fix: input validation for SESSION_DIR and TASK_IDS in build-review-prompts.sh — added empty/existence guards mirroring the existing CHANGED_FILES pattern
- **Queen fix** (`bd8b362`): fix: remove stray apostrophe in awk comment that broke single-quote block in `scripts/build-review-prompts.sh`

### Review Fixes (Round 1)

- **RC-1** (AF-142): fix: REVIEW_TRIAGED logs wrong next_step for fix-path decisions (`orchestration/RULES.md`, `orchestration/RULES-review.md`)
- **RC-2** (AF-143): fix: grep -P silently no-ops on macOS, disabling placeholder scan (`scripts/build-review-prompts.sh:458,460`)
- **RC-3** (AF-144): fix: SESSION_DIR and TASK_IDS not validated in build-review-prompts.sh (`scripts/build-review-prompts.sh:59-66,99-102`)

### Review Statistics

| Round | Scope | P1 | P2 | P3 | Verdict |
|-------|-------|----|----|-----|---------|
| 1 | 5 files, 2 tasks (AF-140, AF-141) | 0 | 3 | 7 | PASS WITH ISSUES |
| 2 | 2 files, 3 tasks (AF-142, AF-143, AF-144) | 0 | 0 | 0 | PASS |

10 root causes consolidated from 13 raw findings (Round 1). 3 P2s auto-fixed; 7 P3s filed as new crumbs.

## 2026-03-16 — Session 20260315-191629 (Move orchestration block to per-project prompt-dir)

### Summary

6 tasks completed across 3 waves, plus a review fix wave that resolved all P2 findings. The session migrated the ant-farm orchestration trigger block out of the global `~/.claude/CLAUDE.md` and into per-project Claude Code prompt-dir files. Wave 1 extracted the canonical block to `orchestration/templates/claude-block.md` and replaced `CLAUDE.md` with project-specific content. Wave 2 rewrote `scripts/setup.sh` Step 6 to remove any existing block from the global file (migration cleanup) and write the block to `~/.claude/projects/-<escaped-path>/CLAUDE.md`. Wave 3 ran 4 agents in parallel: shell tests for the migration logic, a new Step 8b in `skills/init.md` for the `/ant-farm:init` path, and documentation updates across `README.md`, `orchestration/SETUP.md`, and `docs/installation-guide.md`. Review Round 1 (4 reviewers, 21 raw findings, 13 root causes) found no P1s and 5 P2s — all fixed in-session. Round 2 (2 reviewers) returned 0 findings. 13 commits total; 7 P3 crumbs filed for future work.

### Implementation

- **AF-97** (`139722b`): refactor: extract orchestration block to canonical template file — created `orchestration/templates/claude-block.md` with the full 50-line orchestration block; rewrote `CLAUDE.md` as an ant-farm project-specific file with no orchestration block content (grep count for "Parallel Work Mode" in `CLAUDE.md` → 0)
- **AF-98** (`24181c4`): refactor: replace global CLAUDE.md sync with migration removal + prompt-dir write — added `remove_claude_block` to `scripts/setup.sh` (awk sentinel-strip, dry-run, backup, atomic replace); Step 6a calls it on `~/.claude/CLAUDE.md`; Step 6b calls existing `sync_claude_block` with `claude-block.md` as source to write to per-project prompt-dir; 309 existing Python tests passed
- **AF-99** (`9630398`): test: add shell tests for setup.sh migration removal and prompt-dir write — created `tests/test_setup_migration.sh` (295 lines, executable); 5 tests using subshell-per-test pattern with isolated fake `HOME` dirs; all 5 pass
- **AF-100** (`fb5d248`): feat: add prompt-dir CLAUDE.md install step to init skill — inserted Step 8b ("Install Orchestration Triggers to Prompt-Dir CLAUDE.md") into `skills/init.md` between Step 8 and Step 9; 5 sub-steps handle path computation, `mkdir -p`, block sourcing, state detection (create/append/update/error_partial), and atomic write; Step 9 summary updated
- **AF-101 + AF-102** (`ff74127`): docs: update installation guide for per-project CLAUDE.md flow — `README.md` Wire Up section leads with `/ant-farm:init`; File Reference table updated to "per-project prompt-dir"; `orchestration/SETUP.md` Quick Setup removes stale CLAUDE.md bullet; Step 2 documents `/ant-farm:init`; `docs/installation-guide.md` rewrote Step 6 description, added Per-Project Prompt-Dir Installation subsection, updated Uninstalling and Troubleshooting sections for the new model

### Review Fixes

- **AF-106** (`28617f9`): fix: correct `/ant-farm:init` target path parenthetical in `CLAUDE.md:7` from `~/.claude/CLAUDE.md` to `~/.claude/projects/-<escaped-project-path>/CLAUDE.md` (RC-D)
- **AF-107** (`a0e4fe7`): fix: add error guard to install `cp` in `backup_and_copy` — bare `cp "$src" "$dst"` at `scripts/setup.sh:82` now has `|| { echo ... >&2; return 1; }` so a failed install is not silently swallowed (RC-K)
- **AF-103/104/105** (`d1930ac`): fix: correct three `docs/installation-guide.md` documentation errors — wrong source path (`CLAUDE.md` → `orchestration/templates/claude-block.md`) in Per-Project section (RC-A); stale "every setup run backs up before overwriting" backup section rewritten for removal-only behavior (RC-B); spurious `Source` field removed from Global Migration Cleanup section (RC-C)
- **AF-116** (`d2efac7`): fix: add `mkdir -p` error guards to both failure-artifact write blocks in `orchestration/templates/big-head-skeleton.md` (surfaced during review, not in original task plan)

### Review Statistics

| Round | Reviewers | Scope | P1 | P2 | P3 | Verdict |
|-------|-----------|-------|----|----|-----|---------|
| 1 | 4 (Clarity, Edge Cases, Correctness, Drift) | 9 files, 6 planned tasks | 0 | 5 | 7 | PASS WITH ISSUES |
| 2 | 2 (Correctness, Edge Cases) | 4 fix commits | 0 | 0 | 0 | PASS — CLEAN |

21 raw findings consolidated to 13 root cause groups in Round 1. 1 group (RC-F: SETUP.md duplicate content) deduplicated against existing open crumb ant-farm-y719 and skipped. 5 P2 root causes auto-fixed in the review fix wave. 7 P3 root causes filed as new crumbs (AF-108 through AF-114) to Future Work. Round 2 verified all fixes and terminated with 0 findings.

## 2026-03-14 — Session 20260314-104356 (Agent Name Prefix Sweep + Setup Migration)

### Summary

7 tasks completed across 1 planned wave plus a review fix wave. The planned wave (AF-48, AF-49, AF-50) swept all agent name references across orchestration files, templates, config files, and setup.sh to use the `ant-farm-` prefix convention established by AF-47. Review Round 1 (4 reviewers, 13 root causes) surfaced 2 P1s and 2 P2s, all auto-fixed in a parallel fix wave (AF-77 through AF-80). Round 2 verified all fixes clean with 0 P1/P2 and terminated the loop; one minor P3 regression (AF-81) filed to Future Work. 6 commits total.

### Implementation (Wave 1: 3 planned tasks)

- **AF-48** (`ee991ae`): fix: update agent name references to ant-farm- prefix in RULES and config files — `orchestration/RULES.md`, `RULES-decompose.md`, `RULES-review.md`, `GLOSSARY.md`, `README.md`
- **AF-49** (`d609da6`): feat: update agent name references to ant-farm- prefix in orchestration templates — `templates/scout.md`, `big-head-skeleton.md`, `reviews.md`, `pantry.md`, `review-focus-areas.md`
- **AF-50** (`5714122`): feat: add agent migration logic to setup.sh before install — `scripts/setup.sh`; `migrate_old_agents()` uses YAML `name:` sentinel to identity-verify and remove old unprefixed agent files before installing prefixed copies

### Review Fixes (Round 1 — 4 P1/P2 root causes)

- **AF-77** (`10f8e47`): fix: create `agents/ant-farm-technical-writer.md` and update all three RULES.md references — satisfies AF-48 AC-1 blocked by missing agent file
- **AF-78** (`83f39f7`): fix: add `mkdir -p` guard before failure artifact writes in `big-head-skeleton.md` — both timeout and crumb-list failure blocks now ensure parent directory exists before `cat >` redirect
- **AF-79** (`4c50b5b`): fix: add `rm` error handling in `migrate_old_agents` — bare `rm` replaced with `rm ... || { warn ... ; continue; }` to match existing error-recovery pattern
- **AF-80** (`4c50b5b`): fix: portability fixes in `setup.sh` and `RULES-review.md` — `grep -qE` regex interpolation replaced with `grep -qF`; bash parameter expansion replaced with POSIX `tr -d '[:space:]'`

### Review Statistics

| Round | Scope | P1 | P2 | P3 | Verdict |
|-------|-------|----|----|-----|---------|
| 1 | 13 files, 3 planned tasks | 2 | 2 | 9 | PASS WITH ISSUES |
| 2 | 3 fix commits | 0 | 0 | 1 | PASS WITH ISSUES |

13 root causes consolidated in Round 1. 4 auto-fixed (2 P1 + 2 P2); 6 P3 root causes deferred per protocol; 3 P3 root causes matched existing open crumbs (AF-63, ant-farm-mk03, AF-65). Round 2 verified all fixes and terminated with 0 P1/P2; 1 P3 regression (AF-81) auto-filed to Future Work.


## 2026-03-14 — Session 20260313-200323 (Documentation Maintenance + Agent Renames + crumb.py Features)

### Summary

20 planned tasks delivered across 4 waves — Wave 1 handled independent file fixes (7 agents), Wave 2 batched overlapping orchestration file fixes (5 agents), Wave 3 isolated the 8 agent file renames, and Wave 4 ran the cross-cutting placeholder standardization pass last to avoid conflicts. Task scope spanned documentation fixes, two crumb.py features (`crumb init` subcommand; marketplace plugin format for skills), and a large-scale orchestration consistency sweep. A review fix wave then resolved 4 P1/P2 findings surfaced by the Nitpicker team in Round 1. Round 2 verified all 4 fixes and returned 0 P1/P2, terminating the loop. 18 commits total.

### Implementation (Waves 1–4: 20 planned tasks)

- **AF-2** (`d613c96`): feat: add `crumb init` subcommand — `crumb.py` `cmd_init` creates `.crumbs/`, writes `config.json` with `--prefix` flag, touches `tasks.jsonl`, idempotently updates `.gitignore`; `build_parser` epilog updated; all 264 tests pass
- **AF-1** (`5f18dc5`): feat: convert skills to marketplace plugin format — `skills/*.md` frontmatter stripped; `scripts/setup.sh` Step 4 rewired to install to `~/.claude/plugins/ant-farm/commands/<name>.md`
- **ant-farm-0jn7** (`b247c71`): docs: expand README.md Architecture item 4 to capture Pest Control dual role — standalone checkpoint runner (CCO, WWD, DMVDC, ESV) and Nitpicker team member (DMVDC, CCB)
- **ant-farm-0xr1** (`fcb2595`): fix: add ESV PASS (Step 5c) gate to SESSION_PLAN_TEMPLATE.md Pre-Push Verification checklist
- **ant-farm-1r2o** (`1022301`): docs: replace 26-line duplicated "Landing the Plane" block in AGENTS.md with 3-line cross-reference to CLAUDE.md as single source of truth
- **ant-farm-1yl** (`41dc76f`): fix: quote `SESSION_DIR` in PLACEHOLDER_CONVENTIONS.md shell example — `"${SESSION_DIR}/"{...}` is now idiomatic bash
- **ant-farm-21q7** (`f943bb4`): docs: add P1–P3 severity scale explanation to GLOSSARY.md Nitpicker cell with cross-reference to `reviews.md`
- **ant-farm-0di** (`506a651`): docs: clarify RULES.md Step 3b-iii — `mkdir -p` for `review-reports/` now has explicit **before** ordering language relative to Nitpicker spawn
- **ant-farm-39w + ant-farm-0c28** (`4b294e8`): docs: rewrite checkpoints.md `{TASK_ID}`/`{TASK_SUFFIX}` term definitions with labeled categories and examples; add WWD mode selection rule paragraph with RULES.md Step 3 cross-reference
- **ant-farm-07ai + ant-farm-164n + ant-farm-0xqf + ant-farm-10ff** (`55e83d2`): docs: add Step Numbering Cross-Reference table to `reviews.md`; add Pantry conditional marker validation (item 6); update all three skeleton format hints to match Pantry output; add Big Head re-spawn coexistence blockquote to `big-head-skeleton.md`
- **ant-farm-0t31 + ant-farm-2585** (`df9cdbe`): docs: fix `build-review-prompts.sh` block comment format; document NUL-byte, tab-in-paths, and `printf %b` escape assumptions inline
- **ant-farm-0kwo + ant-farm-1s5k** (`ec98bfc`): docs: shorten `agents/nitpicker.md` frontmatter to single sentence; establish canonical scope shorthand labels per reviewer and apply consistently across all 12 NOT YOUR RESPONSIBILITY entries
- **AF-47** (`21ee6f5`): refactor: rename all 8 agent files with `ant-farm-` prefix via `git mv`; update `name:` frontmatter and functional `subagent_type` references in RULES.md and RULES-decompose.md
- **ant-farm-gkk** (`5d3bd91`, `98a43b6`): docs: standardize placeholder syntax across 7 orchestration files — grep-first audit per file; template placeholders converted to `{lowercase-kebab}` Tier 2; CLI examples preserved; PLACEHOLDER_CONVENTIONS.md audit table updated

### Review Fixes (Round 1 — 4 P1/P2 root causes)

- **AF-54** (`3921895`): fix: correct invalid `crumb list` flags in `agents/ant-farm-big-head.md:L22` and `orchestration/templates/scout.md:L40` — `--status=open -n 0` replaced with `--open`
- **AF-55** (`6b9325e`): fix: narrow `crumb init` gitignore entry from `.crumbs/` to `.crumbs/sessions/` at `crumb.py:L2149` — `tasks.jsonl` and `config.json` now remain trackable
- **AF-56** (`e492d76`): fix: correct GLOSSARY.md Pest Control model column — CCB moved from haiku to sonnet (team member); standalone/team-member context labels added
- **AF-57** (`6b9325e`): fix: add pre-validation loop to `cmd_close` before mutation loop — multi-ID close is now atomic; no partial mutations reach disk when a later ID is missing

### Review Statistics

| Round | Scope | P1 | P2 | P3 | Verdict |
|-------|-------|----|----|-----|---------|
| 1 | 33 files, 20 planned tasks | 1 | 5 | 22 | PASS WITH ISSUES |
| 2 | 4 fix commits | 0 | 0 | 1 | PASS |

28 root causes consolidated in Round 1. 4 auto-fixed (P1 + 3 new-P2); 2 P2 skipped (matched existing crumbs AF-48/AF-49 and ant-farm-dxia); 16 new P3 crumbs filed to Future Work; 5 P3 groups skipped (matched existing crumbs); 1 group informational. Round 2 verified all fixes and terminated with 0 P1/P2.


## 2026-03-13 — Session 20260313-155355 (crumb.py Test Suite + Docstring Audit + Review Fix Loop)

### Summary

15 tasks built the full pytest test suite for crumb.py (264 tests across 8 files) and audited its docstrings, then a review fix loop resolved all P1/P2 findings in round 1 with no regressions surfacing in round 2. The implementation tasks ran across 4 waves: Wave 1 established test infrastructure and docstrings (AF-15, AF-22); Wave 2 added CRUD, query, link, trail, and import/doctor tests in parallel (AF-16 through AF-20); Wave 3 added subprocess integration tests (AF-21); Wave 4 verified the full suite green (AF-23). Review round 1 found 2 P1 AC text errors and 4 P2 robustness gaps; all 6 were fixed in a parallel fix wave. Round 2 returned 0 P1/P2 — loop terminated. 17 P3 findings filed to Future Work. 15 commits total.

### Implementation (Waves 1–4: 9 feature/verification tasks)

- **AF-15** (`0fce1ae`): feat: create test infrastructure and helper function tests — `tests/__init__.py`, `tests/conftest.py` (function-scoped `crumbs_env` fixture), `tests/test_helpers.py` (45 tests for all 11 helper functions)
- **AF-16** (`14320e4`): feat: add comprehensive CRUD command tests — `tests/test_crud.py` (45 tests across TestCreate, TestShow, TestUpdate, TestClose, TestReopen)
- **AF-17** (`14320e4`): feat: add query command tests — `tests/test_queries.py` (53 tests across TestList, TestReady, TestBlocked, TestSearch)
- **AF-18** (`ab9a618`): feat: add link management tests — `tests/test_links.py` (18 tests in TestLink; documented spec-vs-code discrepancy on dangling reference behavior)
- **AF-19** (`9055dd9`): feat: add trail subcommand and tree command tests — `tests/test_trails.py` (50 tests across TestTrail and TestTree)
- **AF-20** (`ba45d70`): feat: add import and doctor command tests — `tests/test_import.py` (29 tests), `tests/test_doctor.py` (18 tests)
- **AF-21** (`30e6ed1`): feat: add CLI integration subprocess tests — `tests/test_cli.py` (6 tests in TestCLIIntegration using real subprocess invocations with isolated `.crumbs/` environments)
- **AF-22** (`ec5beff`): docs: audit and improve crumb.py docstrings and inline comments — minimal gap-fill: Args/Returns/Raises added to all public functions, FileLock method docstrings added, step-by-step inline comments added to three beads import pipeline functions; 140 insertions, 19 deletions, zero logic changes
- **AF-23** (`3ff54eb`): chore: verify full test suite passes green — 264 passed, 0 failed, exit code 0, no warnings (Python 3.14.2 / pytest 9.0.2)

### Review Fixes (Round 1 — 6 P1/P2 root causes)

- **AF-24** (`ee34a0e`): fix: correct AF-15 AC 4 status sort key values to match implementation — AC text inverted `open`/`in_progress` ordering; corrected to `open=0, in_progress=1, closed=2, unknown=3`
- **AF-25** (`f44f6ef`): fix: update AF-18 AC 6 to reflect dangling reference behavior in cmd_link — AC text claimed `cmd_link` rejects nonexistent IDs; corrected to document that dangling refs are permitted and validated by `crumb doctor`
- **AF-26** (`2730160`): fix: remove dead dual-field parent/discovered access pattern — eliminated top-level `crumb.get("parent")` / `t.get("parent")` / `t.get("discovered_from")` checks from `_auto_close_trail_if_complete` and `cmd_list` filters in `crumb.py`; aligned to `links.get(...)` resolution only
- **AF-27** (`2730160`): fix: add LOCK_NB retry loop with 10-second timeout to FileLock — replaced indefinitely-blocking `LOCK_EX` with `LOCK_EX | LOCK_NB` plus retry/sleep loop and human-readable "waiting for lock..." message in `crumb.py`
- **AF-28** (`2730160`): fix: clean up .tmp file on os.rename failure in write_config and write_tasks — added try/finally unlink guard to both atomic-write functions in `crumb.py`
- **AF-29** (`d074b82`): fix: tighten weak assertion in test_import_updates_config_counter — changed `>= 11` to `== 11` in `tests/test_import.py`

### Review Statistics

| Round | Scope | P1 | P2 | P3 | Verdict |
|-------|-------|----|----|-----|---------|
| 1 | 15 files, 9 tasks | 2 | 4 | 15 | PASS WITH ISSUES |
| 2 | 5 fix commits | 0 | 0 | 2 | PASS |

29 raw findings (round 1) → 21 root causes consolidated (4 merges, 1 retraction); 6 P1/P2 root causes fixed across 4 parallel fix agents. Round 2: 3 raw findings → 2 root causes, both P3; loop terminated. 17 P3 findings filed to Future Work (AF-30 through AF-46).

## 2026-03-13 — Session 20260313-111851 (Infrastructure Cutover: Beads/Dolt to Crumbs)

### Summary

7 tasks completed the AF-T1 Infrastructure Cutover epic, fully migrating the ant-farm repo from the Beads/Dolt stack to Crumbs. The 4-task planned sequence (import, validate, delete, verify) executed cleanly in ~57 minutes; when the verification gate failed with 28 active files still referencing `bd` commands, 3 parallel fix agents (AF-3, AF-4, AF-5) were spawned to clear the remaining stale references. All operational files — agents, orchestration templates, root orchestration files, scripts, and AGENTS.md — are now fully migrated. Only intentional retention remains: the migration comparison table in `skills/work.md` and historical content in `docs/` and `reviews/`. No review rounds were run (operational/migration tasks). 5 commits total.

### Implementation (Wave 1-4: 4 cutover tasks, sequential)

- **ant-farm-2sar** (`dc410a8`): feat: migrate 531 beads issues to crumbs format — executed `crumb import --from-beads`, importing 531 records (21 epics → trails, 510 non-epics) into `.crumbs/tasks.jsonl` with zero collisions; `config.json` counters advanced correctly
- **ant-farm-5jw0**: chore: validate migrated data with crumb doctor — confirmed 0 errors, 270 acceptable orphan-crumb warnings; `crumb ready` returned 195 open tasks (no files modified)
- **ant-farm-t2xd** (`415c7c1`): chore: remove legacy Beads/Dolt artifacts — deleted `.beads/` directory, `scripts/scrub-pii.sh`, `scripts/sync-to-claude.sh`, `scripts/install-hooks.sh`, `config.yaml`, and all stale `.git/hooks/` variants; `.beads.bak/` safety backup retained
- **ant-farm-l1lf**: chore: run verification gate — gate FAILED; produced per-file breakdown of 28 files with stale `bd` commands, 25 with `.beads/` paths, 14 with Beads/Dolt terminology (no files modified)

### Implementation (Fix wave: 3 parallel reference-cleanup tasks)

- **AF-3** (`761c048`): fix: replace bd/beads references with crumb equivalents in agents/ — updated `agents/architect.md`, `agents/big-head.md`, `agents/scout-organizer.md`, `agents/forager.md`, `agents/surveyor.md`
- **AF-4** (`49e3c04`): fix: replace bd/beads references with crumb equivalents in orchestration/templates/ — updated 11 template files; removed Dolt mode warning block from `decomposition.md`; replaced all `bd` commands, `.beads/` paths, and terminology
- **AF-5** (`4b63fb6`): fix: replace bd/beads references with crumb equivalents in orchestration root and scripts — updated `orchestration/GLOSSARY.md`, `orchestration/PLACEHOLDER_CONVENTIONS.md`, `orchestration/RULES-decompose.md`, `scripts/parse-progress-log.sh`, `AGENTS.md`; removed `bd sync` (no crumbs equivalent)

## 2026-03-13 — Session 20260313-021748 (Decomposition Workflow Infrastructure + Fix Loop)

### Summary

11 original tasks built out the decomposition workflow infrastructure: the Surveyor, Forager, and Architect agent triplets (each a 3-file layered design), all four user-facing slash skills (`/ant-farm:init`, `/ant-farm:work`, `/ant-farm:plan`, `/ant-farm:status`), the `setup.sh` installer, `RULES-decompose.md` (457-line self-contained Planner orchestration rules), and the Planner Orchestrator Profile. Review round 1 covered the 11 original task commits, finding 4 P1 and 8 P2 root causes from 51 raw findings (17 consolidated); the primary P1s were an incomplete bd-to-crumb CLI migration in the Architect's executable templates and a DECOMPOSE_DIR path mismatch in RULES-decompose.md. All 12 root causes were filed as fix beads; 7 were fixed in a parallel fix wave. Round 2 found 1 P2 regression in the ant-farm-3iye fix (single-quote injection via `printf` literal substitution) and 2 P3s; the P2 was fixed in 1 commit. Round 3 returned 0 findings — PASS. 18 commits total.

### Implementation (Wave 1 — 7 tasks, parallel)

- **ant-farm-399a** (`0ec9ed2`): feat: add Surveyor agent definition, workflow template, and skeleton — `agents/surveyor.md`, `orchestration/templates/surveyor.md` (6-step workflow with brownfield handling, question prohibitions, good/bad examples), `orchestration/templates/surveyor-skeleton.md`
- **ant-farm-y4hl** (`8312b12`): feat: add Forager agent definition, workflow template, and skeleton — `agents/forager.md`, `orchestration/templates/forager.md` (4 focus areas with scope boundaries, source hierarchy, 100-line cap), `orchestration/templates/forager-skeleton.md`
- **ant-farm-2hx8** (`7fdcc1e`): feat: add /ant-farm:work skill definition — `skills/work.md` (pre-flight checks, coherence check via crumb doctor, SESSION_DIR creation, RULES.md delegation with crumbs-specific overrides)
- **ant-farm-3bz5** (`7dde9ce`): feat: add setup.sh install script replacing sync-to-claude.sh — `scripts/setup.sh` (agents, orchestration, build-review-prompts.sh, crumb.py to `~/.local/bin/crumb`; timestamped backups; `--dry-run`; idempotent; PATH validation)
- **ant-farm-3imu** (`4429953`): feat: add /ant-farm:init skill definition — `skills/init.md` (language detection, .crumbs/ creation, interactive prefix, config.json, .gitignore, crumb.py install, idempotent repair mode)
- **ant-farm-a5lq** (`467aa6e`): feat: add /ant-farm:plan skill definition — `skills/plan.md` (pre-flight, input type detection, 6-signal structured/freeform classifier, DECOMPOSE_DIR creation, RULES-decompose.md delegation)
- **ant-farm-n3qr** (`f54578b`): feat: add /ant-farm:status skill definition — `skills/status.md` (trail completion counts, per-status crumb counts, last session summary, fixed-width dashboard with graceful degradation)

### Implementation (Wave 2 — 1 task, serial)

- **ant-farm-xtu9** (`eb1fae4`): feat: add Architect agent definition, decomposition workflow, and skeleton — `agents/architect.md`, `orchestration/templates/decomposition.md` (9-step workflow: brownfield scan, trail identification, crumb decomposition with 5-8 file scope budget, 100% coverage gate, CLI commands, decomposition-brief.md output), `orchestration/templates/architect-skeleton.md`

### Implementation (Wave 3 — 2 tasks, parallel)

- **ant-farm-hlv6** (`ebcffeb`): feat: add full JSON payload example to decomposition orchestration template — realistic Python auth service crumb example with 5 acceptance criteria and file paths added to Step 7 of `orchestration/templates/decomposition.md`
- **ant-farm-rwsk** (`8ab12f5`): feat: add RULES-decompose.md with 7-step decomposition workflow — `orchestration/RULES-decompose.md` (457 lines: Planner workflow Steps 0–6, hard gates, retry limits, concurrency rules, read permissions, brownfield heuristic, 15-20% context budget)

### Implementation (Wave 4 — 1 task, serial)

- **ant-farm-3mdg** (`6f3485e`): docs: define Planner orchestrator profile in RULES-decompose.md — added 8-row Queen comparison table, State Tracking subsection, Context Budget subsection with multi-agent round-trip reasoning

### Review Fixes (Round 1 — 7 P2 fix beads)

- **ant-farm-v45n** (`57d7a66`): fix: resolve config schema mismatch in init skill — replaced nested `"counters"` with flat `"next_crumb_id"/"next_trail_id"` in `skills/init.md` to match crumb.py reads
- **ant-farm-prjj** + **ant-farm-jc98** (`8ebb3ba`): fix: resolve work.md review bugs — restructured "follow exactly / except" prose; added `config.json` to initialization guard (`skills/work.md`)
- **ant-farm-li6e** (`344a18d`): fix: resolve shell robustness gaps in setup.sh — added `shopt -s nullglob`, replaced process substitution with tmpfile, changed `exit 1` to `return 1`, added loop call-site guards (`scripts/setup.sh`)
- **ant-farm-3iye** (`a5ce388`): fix: resolve heredoc/JSON injection in plan skill — replaced manifest.json heredoc with `jq -n --arg/--argjson`; replaced input.txt heredoc with `printf '%s\n'` (`skills/plan.md`)
- **ant-farm-bcv4** (`6766723`): fix: add placeholder guard and line cap enforcement in RULES-decompose — added `[ -d "${CODEBASE_ROOT}" ]` guard; added post-research truncation loop (`orchestration/RULES-decompose.md`)
- **ant-farm-k1z2** (`588b82c`): fix: add empty feature request validation in surveyor — explicit whitespace-stripped emptiness check added to Surveyor error handling (`orchestration/templates/surveyor.md`)

### Review Fixes (Round 2 — 1 P2 fix bead)

- **ant-farm-qiqh** (`b782dc4`): fix: use shell variable for printf in plan skill input write — replaced `printf '%s\n' '<INPUT_TEXT>'` (single-quote injection risk) with `printf '%s\n' "${INPUT_TEXT}"`; changed `--argjson class_score` to `--arg class_score` (`skills/plan.md`)

### Review Statistics

| Round | Scope | P1 | P2 | P3 | Verdict |
|-------|-------|----|----|-----|---------|
| 1 | 38 files, 11 tasks | 4 | 8 | 5 groups | NEEDS WORK |
| 2 | 7 fix commits | 0 | 1 | 2 | PASS WITH ISSUES |
| 3 | 1 fix commit | 0 | 0 | 0 | PASS |

51 raw findings (round 1) → 17 root causes consolidated; 1 cross-session dedup skip; 12 P1/P2 root causes filed as beads; 7 of 12 were in-session fix scope (ant-farm-v45n, ant-farm-prjj, ant-farm-jc98, ant-farm-li6e, ant-farm-3iye, ant-farm-bcv4, ant-farm-k1z2). Round 2: 4 raw findings → 3 root causes; 1 P2 fixed (ant-farm-qiqh); 2 P3s auto-filed to Future Work (ant-farm-6zr5, ant-farm-k65u).

## 2026-03-13 — Session 20260313-021827 (Beads Migration + New Agent Infrastructure + Fix Loop)

### Summary

Two migration epics (ant-farm-irgq: 6 mechanical tasks; ant-farm-f4h5: 9 semantic tasks) replaced all `bd`/`.beads/` references with `crumb`/`.crumbs/` equivalents across 15 template, script, and documentation files in 3 waves. The same session also introduced the Architect and Forager agent definitions, a 7-step decomposition workflow (RULES-decompose.md), four slash-skill definitions (init, work, plan, status), and the setup.sh installer. Review round 1 covered 36 changed files, finding 3 P1 and 10 P2 root causes from 51 raw findings (23 consolidated); all 13 were fixed across 3 sub-waves. Round 2 found 1 residual P2 (ant-farm-tbis fix incomplete on pantry.md and big-head-skeleton.md); fixed in 1 commit. Round 3 found 1 P3 only — terminated. 46 commits total.

### Implementation (Wave 1: bd-to-crumb Mechanical Migration — 6 tasks)

- **ant-farm-6gg6** (`5708d88`): docs: migrate Scout and implementation templates to crumb CLI — all `bd` references replaced in `orchestration/templates/scout.md` and `orchestration/templates/implementation.md`
- **ant-farm-eifm** (`06c0011`): docs: migrate queen-state and session plan templates to crumb CLI — `orchestration/templates/queen-state.md` and `orchestration/templates/SESSION_PLAN_TEMPLATE.md`
- **ant-farm-gvd4** (`b0dab79`): chore: migrate dirt-pusher, nitpicker, scribe skeletons bd to crumb — `dirt-pusher-skeleton.md`, `nitpicker-skeleton.md`, `scribe-skeleton.md`
- **ant-farm-k03k** (`2ac0e86`): docs: replace bd references with crumb equivalents in reference and setup docs — `orchestration/reference/dependency-analysis.md`, `orchestration/SETUP.md`
- **ant-farm-mmo3** (`76d02ad`): docs: replace bd command references with crumb equivalents in agent definitions — `agents/scout-organizer.md`, `agents/nitpicker.md`
- **ant-farm-vjhe** (`37cce08`): docs: migrate project docs from bd/beads to crumb/crumbs — `README.md`, `AGENTS.md`, `CONTRIBUTING.md`, `docs/installation-guide.md`

### Implementation (Waves 1–3: bd-to-crumb Semantic Migration — 9 tasks)

- **ant-farm-6d3f** (`8aa01a7`): chore: replace `bd show` with `crumb show` in `scripts/build-review-prompts.sh`
- **ant-farm-a50b** (`cb2204b`): fix: migrate big-head-skeleton.md bd commands to crumb CLI — `orchestration/templates/big-head-skeleton.md`
- **ant-farm-ax38** (`5260783`): docs: migrate CLAUDE.md bd references to crumb CLI — `CLAUDE.md` and `~/.claude/CLAUDE.md`
- **ant-farm-epmv** (`3fe4b6e`): docs: migrate pantry.md bd CLI references to crumb equivalents — `orchestration/templates/pantry.md`
- **ant-farm-h2gu** (`15fe938`): docs: migrate bd CLI references to crumb equivalents in checkpoints.md
- **ant-farm-n56q** (`b9892fe`): docs: migrate reviews.md bd CLI references to crumb CLI
- **ant-farm-o0wu** (`710ec47`): docs: migrate RULES-review.md bd commands and .beads/ paths to crumb/.crumbs/ — new file added (214 lines)
- **ant-farm-rue4** (`4147daf`): docs: migrate RULES.md bd commands and paths to crumb/.crumbs/ equivalents
- **ant-farm-veht** (`b8bbdb4`): docs: add TDV checkpoint definition to checkpoints.md

### Implementation (New Agent Infrastructure and Skills)

- **ant-farm-xtu9** (`eb1fae4`): feat: add Architect agent definition, decomposition workflow, and skeleton — `agents/architect.md`, `orchestration/templates/decomposition.md`, `orchestration/templates/architect-skeleton.md`
- **ant-farm-y4hl** (`8312b12`): feat: add Forager agent definition, workflow template, and skeleton — `agents/forager.md`, `orchestration/templates/forager.md`, `orchestration/templates/forager-skeleton.md`
- **ant-farm-rwsk** (`8ab12f5`): feat: add RULES-decompose.md with 7-step decomposition workflow (457 lines)
- **ant-farm-hlv6** (`ebcffeb`): feat: add full JSON payload example to decomposition orchestration template
- **ant-farm-3mdg** (`6f3485e`): docs: define Planner orchestrator profile in RULES-decompose.md
- **ant-farm-3imu** (`57d7a66`): feat: add /ant-farm:init skill definition — `skills/init.md` (239 lines)
- **ant-farm-2hx8** (`7fdcc1e`): feat: add /ant-farm:work skill definition — `skills/work.md` (142 lines)
- **ant-farm-a5lq** (`467aa6e`): feat: add /ant-farm:plan skill definition — `skills/plan.md` (169 lines)
- **ant-farm-n3qr** (`f54578b`): feat: add /ant-farm:status skill definition — `skills/status.md` (183 lines)
- **ant-farm-3bz5** (`7dde9ce`): feat: add setup.sh install script replacing sync-to-claude.sh — `scripts/setup.sh` (245 lines)

### Review Fixes (Round 1, Wave 1 — 7 P1/P2 root causes)

- **ant-farm-5ujg** (`e668d8e`, `68006ac`): fix: remove non-existent `crumb sync` from AGENTS.md quick-reference and push block
- **ant-farm-rlne** (`6e6357c`): fix: clarify Condition 3 contamination detection with precise regex and example (`orchestration/templates/pantry.md`)
- **ant-farm-rgg3** (`d2d3f1f`): fix: add `-r` check to FOCUS_AREAS_FILE validation (`scripts/build-review-prompts.sh`)
- **ant-farm-9ahp** (`28baea2`): fix: add CLAUDE.md sync step to setup.sh (`scripts/setup.sh`)
- **ant-farm-52ka** (`b8bbdb4`): fix: add substitution instruction before brownfield detection block (`orchestration/RULES-decompose.md`)
- **ant-farm-5fq0** (`55381ec`): fix: add rollback error handling to Dolt mode switch (`orchestration/templates/decomposition.md`)
- **ant-farm-nmpw** (`34712c8`): fix: exclude error-status tasks from conflict analysis and wave 1 (`orchestration/templates/scout.md`)

### Review Fixes (Round 1, Wave 2 — 4 P2 root causes)

- **ant-farm-tbis** (`cef1915`): fix: update stale SESSION_DIR path in 6 files — `AGENTS.md`, `CLAUDE.md`, `scout.md`, `dependency-analysis.md`, `dirt-pusher-skeleton.md`, `scribe-skeleton.md`
- **ant-farm-5ohl** (`75aaea0`): fix: propagate resolve_arg failures from command substitutions (`scripts/build-review-prompts.sh`)
- **ant-farm-7fc3** (`2ef18a7`): fix: remove hardcoded polling timeout from big-head-skeleton (`orchestration/templates/big-head-skeleton.md`)
- **ant-farm-z305** (`e6a0a27`): fix: filter pre-flight task count to tasks only (`skills/work.md`)

### Review Fixes (Round 1, Wave 3 — 2 P2 root causes)

- **ant-farm-c47w** (`1749415`): fix: clarify crumb vs bd CLI relationship in AGENTS.md — added explanatory note; aligned prohibition language
- **ant-farm-qv4a** (`344a18d`): fix: clean up temp files on error paths in fill_slot and big-head dedup (`scripts/build-review-prompts.sh`, `orchestration/templates/big-head-skeleton.md`)

### Review Fixes (Round 2, 1 P2 root cause)

- **ant-farm-tack** (`ca13ddf`): fix: update stale SESSION_DIR examples in pantry.md and big-head-skeleton.md — two files missed by ant-farm-tbis in Round 1

### Review Statistics

| Round | Scope | P1 | P2 | P3 | Verdict |
|-------|-------|----|----|-----|---------|
| 1 | 36 files, 15 migration + infra tasks | 3 | 10 | 11+ | NEEDS WORK |
| 2 | 13 fix commits | 0 | 1 | 0 | PASS WITH ISSUES |
| 3 | 1 fix commit | 0 | 0 | 1 | PASS WITH ISSUES |

51 raw findings (round 1) → 23 root causes consolidated; 3 skipped (cross-session dedup); 13 P1/P2 root causes fixed across 3 sub-waves. Round 2: 2 raw findings → 1 root cause fixed. Round 3: 1 raw finding → 1 P3 auto-filed to Future Work (ant-farm-sj3f).

## 2026-03-13 — Session 20260313-001327 (Crumb CLI Build + Review Fix Loop)

### Summary

Epic ant-farm-e7em (Crumb CLI) completed in full: 9 feature tasks built crumb.py from scaffold to a production-ready single-file Python CLI across 4 waves (~47 minutes). Review round 1 found 0 P1 and 5 P2 root causes across 17 consolidated root causes (26 raw findings); all 5 P2s were auto-fixed in a serial fix cycle (5 commits, 1 agent, same file). Round 2 reviewed the 5 fix commits, found 1 new P2 regression (ant-farm-k040), deferred by user. 14 commits total.

### Implementation (Waves 1–4: 9 feature tasks)

- **ant-farm-mg0r** (`03708ef`): feat: scaffold crumb.py with CLI framework and core infrastructure — argparse subparser dispatch, FileLock, atomic write via temp-then-rename, walk-up directory discovery, JSONL utilities (crumb.py, 599 lines)
- **ant-farm-l7pk** (`41004c4`): feat: implement crumb create, show, list commands — `_find_crumb`, sort key helpers; dual-mode create (--title / --from-json); filtering, sorting, limit, --short output (crumb.py)
- **ant-farm-cmcd** (`86770aa`): feat: implement crumb update, close, reopen commands — status transition guard, note appending, multi-ID close (idempotent), reopen clears closed_at (crumb.py)
- **ant-farm-h7af** (`a67cf4a`): feat: implement crumb link command — nested links dict; --parent, --blocked-by (dedup), --remove-blocked-by, --discovered-from flags (crumb.py)
- **ant-farm-jmvi** (`58c61b3`): feat: implement trail commands — trail create/show/list/close; auto-close and auto-reopen hooks in cmd_close and cmd_link (crumb.py)
- **ant-farm-vxpr** (`1ff6edc`): feat: implement crumb ready and blocked commands — `_get_blocked_by` + `_is_crumb_blocked` helpers; partition of open crumbs by readiness (crumb.py)
- **ant-farm-izng** (`bdcf2ed`): feat: implement crumb doctor command — two-pass syntax + semantic validation; malformed JSON, duplicate IDs, dangling parents (errors), orphan/dangling blocked_by (warnings); --fix flag (crumb.py)
- **ant-farm-fdz2** (`36dffe2`): feat: implement crumb import and --from-beads migration — plain JSONL import with line-level error recovery; beads-to-crumb format conversion; counter advancement (crumb.py)
- **ant-farm-dhh8** (`0627e70`): feat: implement crumb search and tree commands — case-insensitive keyword search; hierarchical tree view with orphan section (crumb.py)

### Review Fixes (Round 1, 5 P2 root causes)

- **ant-farm-35a5** (`500d88e`): fix: wrap open/touch calls in try/except OSError in read_tasks(), iter_jsonl(), FileLock.__enter__ (crumb.py)
- **ant-farm-ru51** (`d33fde5`): fix: dual-lookup parent/discovered_from in cmd_list filters and _auto_close_trail_if_complete (crumb.py)
- **ant-farm-l1en** (`87cdd8f`): fix: validate --from-json type (isinstance dict) and config counter fields in read_config() (crumb.py)
- **ant-farm-bzhs** (`74c5cf6`): fix: fix inverted blocks dependency direction in _convert_beads_record; add _apply_blocks_deps post-processing pass (crumb.py)
- **ant-farm-ch0z** (`96347af`): fix: expand FileLock scope in cmd_doctor to cover full read-validate-write sequence (crumb.py)

### Review Statistics

| Round | Scope | P1 | P2 | P3 | Verdict |
|-------|-------|----|----|-----|---------|
| 1 | 1 file, 9 tasks | 0 | 5 | 12 | PASS WITH ISSUES |
| 2 | 1 file, 5 fix tasks | 0 | 1 | 0 | PASS WITH ISSUES |

26 raw findings (round 1) → 17 root causes consolidated; 1 raw finding (round 2) → 1 root cause. 5 P2 root causes fixed in round 1. 12 P3 findings not filed as beads. Round 2 P2 (ant-farm-k040) deferred by user.

## 2026-02-23 — Session 20260222-225628 (Persistent-Team Fix Loop + CCB Spot-Check)

### Summary

4 original tasks (ant-farm-ygmj.1–.4) upgraded the review-fix loop infrastructure: CCB model from haiku to sonnet with a new root cause spot-check, Big Head bead-list handoff step, full rewrite of the reviews.md fix workflow for the in-team persistent model, and RULES.md documentation of team persistence, fix inner loop, and 4 new progress log milestones. Review round 1 found 2 P1 and 6 P2 root causes across 23 raw findings (17 consolidated); all fixed in a batched fix cycle across 3 delivery agents. Round 2 found 2 P2 defects in the fix itself (pseudocode in shell, criteria drift); both fixed in 1 commit. Round 3 confirmed all fixes and found 1 P3, terminating the loop. 10 commits total.

### Implementation (Waves 1–3: 4 tasks)

- **ant-farm-ygmj.1** (`05ebb82`): feat: upgrade CCB to sonnet and add root cause spot-check — new Check 3b section in checkpoints.md with minor/material severity distinction, 6-step escalation path; CCB row updated in RULES.md Model Assignments table
- **ant-farm-ygmj.2** (`9f4c6da`): feat: add bead-list handoff step to Big Head skeleton — new Step 12 in big-head-skeleton.md with SendMessage format, round-conditional trigger, P1/P2/P3 separation
- **ant-farm-ygmj.3** (`f686f88`): refactor: rewrite fix workflow for in-team agents — replaced outdated standalone-agent Fix Workflow in reviews.md with 8 subsections covering Scout auto-approval, Pantry/CCO skip, naming, prompt structure, inner loop, wave composition, round transition, re-run reviews
- **ant-farm-ygmj.4** (`9fcfc87`): refactor: update RULES.md for persistent team and fix inner loop — Steps 3b/3c rewritten for persistent team; Model Assignments and Retry Limits tables expanded; 4 new progress log milestones added

### Review Fixes (Round 1, 8 P1/P2 root causes)

- **ant-farm-ql6s** (`06cf404`): fix: wrong team name "nitpickers" → "nitpicker-team" in reviews.md Fix Workflow (reviews.md)
- **ant-farm-1pa0** (`06cf404`): fix: add single-invocation constraint comment and increase POLL_TIMEOUT_SECS from 30 to 60 (reviews.md, big-head-skeleton.md)
- **ant-farm-f7lg** (`06cf404`, `0463fa5`): fix: remove phantom briefs/ path; add explicit edge-cases output path to round-transition spec (reviews.md, RULES.md)
- **ant-farm-5zs0** (`06cf404`): fix: rewrite Round 2+ spawn instructions to use SendMessage re-tasking, not TeamCreate (reviews.md)
- **ant-farm-fp74** (`06cf404`): fix: add failure artifact write and Queen notification before exit 1 on bd list failure (reviews.md, big-head-skeleton.md)
- **ant-farm-01a8** (`365a0d9`): fix: restore conditional clarity/drift path check with REVIEW_ROUND pre-validation invariant comment (reviews.md)
- **ant-farm-1rof** + **ant-farm-evk2** (`a58c56f`, `0463fa5`): fix: add session dir existence check to crash recovery; add shutdown prohibition to Queen Prohibitions and Step 3c (RULES.md)
- **ant-farm-ccg8** (`4021909`): fix: add repo root commit guard to ESV Check 2 git log range (checkpoints.md)

### Review Fixes (Round 2, 2 P2 root causes)

- **ant-farm-fz32** (`50844a7`): fix: remove SendMessage pseudocode from shell error handler; add prose halt-and-notify instruction outside bash block (reviews.md, big-head-skeleton.md)
- **ant-farm-pj9t** (`50844a7`): fix: update ant-farm-01a8 acceptance criteria to document conditional-check approach and REVIEW_ROUND pre-validation invariant (bead metadata only)

### Review Statistics

| Round | Scope | P1 | P2 | P3 | Verdict |
|-------|-------|----|----|-----|---------|
| 1 | 4 files, 4 tasks | 2 | 6 | 9 | PASS WITH ISSUES |
| 2 | 4 files, 9 fix tasks | 0 | 2 | 3 | PASS WITH ISSUES |
| 3 | 2 files, 2 fix tasks | 0 | 0 | 1 | PASS |

23 raw findings (round 1) → 17 root causes consolidated; 6 raw findings (round 2) → 5 root causes; 3 raw findings (round 3) → 1 root cause. 10 P1/P2 root causes fixed across rounds 1 and 2. 13 P3 beads filed (10 round 1 + 3 round 2+ auto-filed to Future Work epic ant-farm-66gl).

## 2026-02-22 — Session 86c76859 (CCB Timeout + Pantry Preview + Review Focus Areas)

### Summary

3 original tasks (ant-farm-q59z, ant-farm-vxcn, ant-farm-m4si) fixing CCB timeout, Pantry preview enforcement, and progress log key naming. Review round 1 found 0 P1, 4 P2, 9 P3 (13 root causes). 4 P2 fixes applied in-session across 3 waves. 12 review beads filed by Big Head. Mid-session fix: `build-review-prompts.sh` patched to inject per-type focus areas from `review-focus-areas.md` (CCO caught missing focus blocks).

### Implementation (Wave 1: 3 tasks, parallel)

- **ant-farm-q59z** (`a59d61e`): fix: replace sleep-based CCB wait with turn-based end-turn protocol in reviews.md and big-head-skeleton.md
- **ant-farm-vxcn** (`1b8f898`): fix: enforce preview file as mandatory output in Pantry Step 3 with read-back verification
- **ant-farm-m4si** (`55514c1`): fix: rename tasks_approved to tasks_accepted, document N derivation in RULES.md

### Review Fixes (Round 1, 4 P2 root causes)

- **RC-5** (ant-farm-m2cb, `ba0d70d`): fix: rename Priority Calibration to Bead Priority Calibration, consolidate Information Diet, move Review Quality Metrics
- **RC-10** (ant-farm-bzl6, `ed0a651`): fix: enforce REVIEW_ROUND >= 1 and non-empty CHANGED_FILES in build-review-prompts.sh
- **RC-6** (ant-farm-60em, `214ad51`): docs: expand incomplete mechanism descriptions in RULES.md and big-head-skeleton.md
- **RC-2** (ant-farm-zzdk, `f81bd86`): fix: resolve template-vs-runtime placeholder confusion, add post-write placeholder scan

### Infrastructure Fix (Mid-Session)

- `build-review-prompts.sh`: Added `extract_focus_block()` helper and `## Focus` section injection per review type, sourced from `review-focus-areas.md`. CCO caught identical generic prompts across all 4 review types.

### Review Statistics

| Round | Scope | P1 | P2 | P3 | Verdict |
|-------|-------|----|----|-----|---------|
| 1 | 4 files, 3 tasks | 0 | 4 | 9 | PASS WITH ISSUES |

13 root causes consolidated from 35 raw findings. 4 P2 root causes fixed in-session. 8 P3 beads filed. 1 P3 skipped (matched existing ant-farm-2sjc).

### Open beads filed this session

- ant-farm-sf3v (P3): Stale "user approval" label in parse-progress-log.sh
- ant-farm-yufy (P3): Deprecated pantry.md Section 2 stale and misleading
- ant-farm-8evt (P3): Lifecycle metadata mixed into operational steps
- ant-farm-az7u (P3): Pantry step numbering namespace collision
- ant-farm-e26s (P3): Post-push sync check documentation gaps
- ant-farm-8kds (P3): fill_slot temp file leak on awk failure
- ant-farm-d1rx (P3): Polling loop off-by-one (28s vs 30s)
- ant-farm-kf0y (P3): RULES.md bash blocks missing edge-case handling

## 2026-02-22 — Session 2bb21f22 (Auto-Approve Scout Strategy)

### Summary

1 feature task (ant-farm-fomy) to auto-approve Scout strategy after SSV PASS, removing the user approval gate from Step 1b. Review round 1 found 1 P1 + 2 P2 + 1 P3 (4 root causes). P1 and P2 fixes applied in-session. Review round 2 found 0 P1/P2 (3 P3s auto-filed to Future Work). 3 implementation commits + 2 fix commits.

### Implementation (Wave 1: 1 task)

- **ant-farm-fomy**: docs: auto-approve Scout strategy after SSV PASS in Step 1b — removed user approval gate, added risk analysis block documenting safety nets, rejected complexity threshold

### Review Fixes (Round 1, 3 root causes)

- **RC-2** (ant-farm-i7wl): fix: add zero-task guard and SSV FAIL retry cap to RULES.md Step 1b
- **RC-3** (ant-farm-sfe0): fix: update stale briefing.md descriptions in RULES.md (lines 28, 474)
- **RC-4** (ant-farm-or8q, partial): fix: remove user-approval references from checkpoints.md and dependency-analysis.md; CLAUDE.md and README.md updated by Queen in Step 4

### Review Statistics

| Round | Scope | P1 | P2 | P3 | Verdict |
|-------|-------|----|----|-----|---------|
| 1 | 1 file, 1 task | 1 | 2 | 1 | PASS WITH ISSUES |
| 2 | 3 files, 3 fix tasks | 0 | 0 | 3 | PASS |

4 root causes consolidated from 11 raw findings (round 1). 3 P1/P2 root causes fixed in-session. 1 P3 (RC-1, ant-farm-m4si) filed. Round 2: 3 P3s auto-filed to Future Work epic.

### Open beads filed this session

- ant-farm-m4si (P3): Progress log key tasks_approved misleading after auto-approve change
- ant-farm-vxcn (P2): Pantry skips writing preview file to previews/ directory
- ant-farm-q59z (P2): Big Head cannot receive Pest Control messages — timeout on every CCB exchange
- Plus 3 P3s auto-filed by Big Head to Future Work epic (round 2)

## 2026-02-22 — Session d81536bb (Exec Summary Scribe Infrastructure)

### Summary

Epic ant-farm-68di: Created the Scribe agent infrastructure for automated session exec summaries and CHANGELOG entries. Added ESV (Exec Summary Verification) as the 6th Pest Control checkpoint. 5 implementation tasks across 3 waves, plus 7 P2 review fixes. 11 commits total (5 implementation + 6 fixes).

### Implementation (3 waves, 5 tasks)

- **ant-farm-68di.1**: feat: add Scribe skeleton template — new orchestration/templates/scribe-skeleton.md with 7-source input table, embedded exec-summary format, CHANGELOG derivation rules, and duration calculation instructions
- **ant-farm-68di.2**: feat: add ESV checkpoint to checkpoints.md — 6 mechanical checks (task coverage, commit coverage, open bead accuracy, CHANGELOG fidelity, section completeness, metric consistency) with bd show guard and retry-then-escalate flow
- **ant-farm-68di.3**: docs: integrate Scribe and ESV workflow into RULES.md — new Steps 5b/5c, Hard Gates table, Agent Types/Model Assignments tables, Session Directory artifacts, Template Lookup, Retry Limits
- **ant-farm-68di.4**: feat: add SCRIBE_COMPLETE and ESV_PASS milestones to crash recovery script (parse-progress-log.sh)
- **ant-farm-68di.5**: docs: update cross-references from Step 4 CHANGELOG to Step 5b/Scribe across reviews.md, SESSION_PLAN_TEMPLATE.md, README.md, GLOSSARY.md, queen-state.md

### Review Fixes (Round 1, 7 P2 root causes)

- **RC-1** (ant-farm-nra7): fix: propagate ESV to GLOSSARY checkpoint counts ("five" -> "six"), acronyms table, Pest Control role
- **RC-2** (ant-farm-lbr9): fix: add ESV row to README Hard Gates table
- **RC-3** (ant-farm-ru2v): fix: update RULES.md Step 3c defer path from "document in CHANGELOG" to Scribe/Step 5b
- **RC-8** (ant-farm-tx0z): fix: complete ESV input specification — empty bead list handling, ^.. commit range, spawn fields
- **RC-9** (ant-farm-ye5r): fix: add empty-data fallback instructions to Scribe skeleton (missing CHANGELOG, zero summaries)
- **RC-16** (ant-farm-hodh): fix: move scribe-skeleton.md from FORBIDDEN to PERMITTED in Queen Read Permissions
- **RC-22** (ant-farm-7026): fix: add empty-string guard to Big Head polling placeholder check

### Review Statistics

| Round | Scope | P1 | P2 | P3 | Verdict |
|-------|-------|----|----|-----|---------|
| 1 | 9 files, 5 tasks | 0 | 7 | 16 | PASS WITH ISSUES |

23 root causes consolidated from 36 raw findings. 7 P2s fixed in-session. 15 P3s filed as beads (backlog). 1 no-action (RC-23).

### Open P3 beads filed this session

ant-farm-ix7m, ant-farm-3vye, ant-farm-7l1z, ant-farm-6t89, ant-farm-5vs8, ant-farm-hefc, ant-farm-qm8d, ant-farm-by3g, ant-farm-21q7, ant-farm-l70g, ant-farm-cqzj, ant-farm-hiyh, ant-farm-9p9q, ant-farm-0xr1, ant-farm-5nhs

## 2026-02-22 — Session 5da05acb (Documentation Bug Fixes + Review Fix Cycle)

### Summary

6 P2 documentation bugs fixed across orchestration docs, README, CONTRIBUTING, GLOSSARY, sync script, and SESSION_PLAN_TEMPLATE. Review round 1 found 0 P1, 2 P2, 8 P3 (13 root causes, 3 deduplicated against existing beads). 5 root causes fixed in-session (RC-3, RC-4, RC-5, RC-6, RC-11). 5 P3s dropped by user decision. 6 implementation commits + 3 fix commits.

### Implementation (Wave 1: 4 agents, 6 tasks)

- **ant-farm-2yww + ant-farm-80l0**: fix: update reader attributions from Pantry (review mode) to build-review-prompts.sh across RULES.md, README.md, GLOSSARY.md, CONTRIBUTING.md; add missing SSV row to README Hard Gates table
- **ant-farm-q84z + ant-farm-zg7t**: fix: unify TIMESTAMP naming (remove dual REVIEW_TIMESTAMP), replace macOS-incompatible shell commands with bash-native equivalents in RULES.md
- **ant-farm-tour**: fix: update SESSION_PLAN_TEMPLATE review sections to match parallel TeamCreate workflow and root-cause-based triage
- **ant-farm-sje5**: fix: add preflight check for missing code-reviewer.md agent in sync-to-claude.sh

### Review Fixes (Round 1 auto-fix, 5 root causes)

- **RC-3**: fix: update skeleton template attributions from Pantry to build-review-prompts.sh (nitpicker-skeleton.md, big-head-skeleton.md)
- **RC-4**: fix: add warning when agents/ directory exists but contains no .md files (sync-to-claude.sh)
- **RC-5**: fix: replace fixed sleep 5 with 15s readiness poll in dummy reviewer tmux launch (RULES.md)
- **RC-6**: fix: replace single-item for-loop with direct cp (sync-to-claude.sh)
- **RC-11**: fix: add explicit error guard on backup cp (sync-to-claude.sh)

### Review Statistics

| Round | Scope | P1 | P2 | P3 | Verdict |
|-------|-------|----|----|-----|---------|
| 1 | 6 files, 6 tasks | 0 | 2 | 8 | PASS WITH ISSUES |

13 root causes consolidated. 3 skipped (existing beads: ant-farm-2yww, ant-farm-q84z, ant-farm-4lcv). 5 fixed in-session. 5 P3s dropped per user decision.

## 2026-02-22 — Session db790c8d + e7ff7c0d (P1 Bug Fixes + Deferred Reviews)

### Summary

4 P1 bug fixes completed in session db790c8d, with reviews deferred and completed in continuation session e7ff7c0d. 1 P2 review finding fixed (WAVE_WWD_PASS missing from crash recovery). Reviews terminated at round 2 (0 P1, 1 dismissed P2 false positive). 6 P3 findings filed. 5 implementation commits.

### Implementation (Session db790c8d — 2 waves, 4 tasks)

- **x8iw**: fix: update Scout and Pantry model references from sonnet to opus (GLOSSARY.md, README.md, scout-organizer.md)
- **h94m**: docs: correct checkpoints.md Pest Control architecture to direct execution
- **wg2i**: fix: regenerate pre-push hook with non-fatal sync, fix CONTRIBUTING.md sync docs
- **zuae**: fix: document WWD batch vs serial execution modes in RULES.md + checkpoints.md

### Review Fix (Session e7ff7c0d)

- **951b**: fix: add WAVE_WWD_PASS to parse-progress-log.sh STEP_KEYS (P2 — unmet crash recovery criterion)

### Review Statistics

| Round | Scope | P1 | P2 | P3 | Verdict |
|-------|-------|----|----|-----|---------|
| 1 | 6 files, 4 tasks | 0 | 1 | 6 | PASS WITH ISSUES |
| 2 | 1 file, 1 fix task | 0 | 1 (dismissed) | 0 | Terminated |

7 review beads filed in round 1 (1 P2 + 6 P3). Round 2 P2 dismissed as false positive (reviewer misread acceptance criteria). P3s remain open for future work.

## 2026-02-21 — Session 068ecc83 (Documentation Cleanup + Pantry-Review Deprecation)

### Summary

6 tasks completed (3 original P3 doc bugs + 3 P2 review fixes) across 8 files. Reviews converged at round 2 (0 P1/P2). 16 P3 findings filed to Future Work epic. 6 commits, +30/-19 lines.

### Implementation (Wave 1: 3 tasks)

- **6jxn**: fix: update stale pantry-review references across 4 documentation surfaces (reviews.md, README.md, pantry.md, _archive/pantry-review.md)
- **oc9v**: docs: remove stale pantry-review from Scout exclusion list (scout.md)
- **n0or**: docs: clarify comments and fix code fence nesting (SETUP.md, parse-progress-log.sh, compose-review-skeletons.sh)

### Review Fixes (Round 2)

- **xybg**: fix: re-add pantry-review to Scout exclusion list (P2 — stale agent on disk unguarded)
- **aqlp**: fix: tighten sed regex from * to + and document canonical slot names (P2 — blanket uppercase conversion)
- **wzno**: fix: correct POSIX-compatible comment to Bash 3+-compatible (P2 — misleading portability claim)

### Review Statistics

| Round | Scope | P1 | P2 | P3 | Verdict |
|-------|-------|----|----|-----|---------|
| 1 | 8 files, 3 tasks | 0 | 3 | 16 | PASS WITH ISSUES |
| 2 | 3 files, 3 fix tasks | 0 | 0 | 0 | PASS |

19 review beads filed (round 1: 3 P2 + 16 P3; round 2: 0). P3s filed to Future Work epic (ant-farm-bkco).

### Epics

- **ant-farm-bkco** (Future Work): 16 new P3 children added from review findings

## 2026-02-21 — Session 7edaafbb (Shell Script Hardening + P2 Bugs)

### Summary

30 tasks completed (4 P2 bugs + 26 P3 shell script hardening) across 14 files. 7 review findings fixed in round 2 (1 P1, 6 P2). Reviews converged at round 2 (0 P1/P2). 37 commits, +310/-127 lines.

### Implementation (Wave 1: 26 tasks, Wave 2: 4 tasks)

**fill-review-slots.sh** (4 tasks):
- **39zq**: perf: batch fill_slot awk calls into single pass per file
- **i2zd**: fix: add EXIT trap to clean up temp files on abnormal exit
- **lc97**: fix: reject empty @file arguments in resolve_arg with error
- **ti6g**: fix: reject review round 0

**scrub-pii.sh** (5 tasks):
- **9wk8**: fix: replace magic 'ctc' token with self-documenting '[REDACTED]'
- **ns95**: docs: document intentional email regex coverage scope
- **9vq**: fix: use PII_FIELD_PATTERN variable in post-scrub verification grep calls
- **50m**: fix: check perl availability at startup with clear error message
- **wtp**: fix: print re-staging reminder when run standalone outside a git hook

**sync-to-claude.sh** (5 tasks):
- **40z**: fix: remove rsync --delete to preserve custom user files
- **g29r**: fix: warn to stderr when expected sync scripts are missing
- **szcy**: docs: add comment explaining why only two scripts are synced
- **3r9**: fix: append PID to backup timestamp to eliminate collision risk
- **rja**: fix: warn to stderr when agents/ directory is missing

**install-hooks.sh** (4 tasks):
- **3mg**: fix: ensure sync-to-claude.sh is executable after clone
- **4fx**: fix: use timestamped backup filenames to preserve backup history
- **4g7**: fix: add descriptive error message with remediation on sync failure
- **dv9g**: docs: add rationale comment for non-fatal sync failure design

**compose-review-skeletons.sh + parse-progress-log.sh** (3 tasks):
- **o058**: fix: count both frontmatter delimiters in extract_agent_section
- **yn1r**: fix: document sed regex 2+ char minimum and blanket-conversion assumption
- **npfx**: fix: harden parse-progress-log.sh (overwrite warning, dead branch, timestamp validation)

**RULES.md** (2 tasks):
- **e1u6**: fix: add $TMUX guard around dummy reviewer tmux commands
- **qoig**: fix: add tmux binary availability check to dummy reviewer guard

**SETUP.md + scout.md** (3 tasks):
- **a66**: fix: replace hardcoded hs_website example paths with generic my-project
- **kwp**: fix: clarify test checklist — Queen delegates bd show to Scout
- **lhq**: fix: enrich Scout error metadata template with context fields

**Cross-cutting Wave 2** (4 tasks):
- **352c.1**: fix: replace LLM-interpreted IF ROUND 1 markers with shell conditionals
- **w2i1**: fix: add unfilled slot marker validation to fill-review-slots.sh
- **j6jq**: refactor: replace magic numbers, fix inverted sentinel in reviews.md polling loop
- **a1rf**: fix: harden grep -c set-e interaction, simplify whitespace check, wrap backup cp

### Review Fixes (Round 2)

- **ul02**: fix: revert extract_agent_section awk to count>=1 for single-delimiter skeletons (P1)
- **viyd**: fix: replace grep \s with POSIX [[:space:]] for BSD compatibility
- **ub8a**: fix: exclude _archive/ from rsync to prevent stale deprecated files
- **shkt**: fix: add placeholder guard for REVIEW_ROUND assignment
- **sjyg**: fix: reword troubleshooting to delegate bd show to Scout
- **2qmt**: fix: update stale TIMED_OUT reference to REPORTS_FOUND
- **bhgt**: fix: make pre-commit hook warn instead of fail when scrub-pii.sh missing

### Review Statistics

| Round | Scope | P1 | P2 | P3 | Verdict |
|-------|-------|----|----|-----|---------|
| 1 | 13 files, 30 tasks | 1 | 6 | 8 | NEEDS WORK |
| 2 | 7 files, 7 fix tasks | 0 | 0 | 3 | PASS |

18 review beads filed (round 1: 1 P1 + 6 P2 + 8 P3; round 2: 3 P3 auto-filed to Future Work).

### Epics

- **ant-farm-352c** (Future Work): 11 new P3 children added from review findings

## 2026-02-20 — Session cd9866 (Bug Sweep)

### Summary

17 P2 bugs fixed across 14 files (orchestration templates, scripts, docs). 5 P2 review findings fixed in round 2, 1 P2 fix regression fixed in round 3. Reviews converged at round 3 (0 P1/P2).

### Implementation (Wave 1 + Wave 2)

- **bi3**: add directory pre-check and fix ambiguous file reference in pantry.md
- **yfnj**: inline Big Head Step 0a error return format in pantry.md Section 2
- **yb95**: remove deprecated pantry-review agent, stub Section 2, clean RULES.md rows
- **txw**: add failure artifact convention to Big Head skeleton
- **auas**: add input validation guards for REVIEW_ROUND, CHANGED_FILES, TASK_IDS
- **0gs**: replace glob patterns with exact timestamp placeholders in reviews.md error template
- **32gz**: add $RANDOM to SESSION_ID entropy to prevent same-second collision
- **033**: add pre-commit PII scrub hook documentation to installation guide
- **1b8**: fix uninstall path (~/.git/ -> .git/) and add pre-commit hook uninstall
- **7yv**: block commits when scrub-pii.sh missing/non-executable, chmod +x on install
- **z69**: make pre-push hook resilient to sync-to-claude.sh failures
- **cl8**: remove quote anchors from PII regexes to match unquoted occurrences
- **1e1**: complete "data file" -> "task brief" rename in skeleton and README
- **1y4**: verified already fixed (no changes needed)
- **27x**: remove Edit tool from big-head.md tools list (least-privilege)
- **9j6z**: verified already fixed (review-clarify -> review-clarity rename)
- **z3j**: define small-file threshold, guard DMVDC sampling formula, scope CCB bead list

### Review Fixes (Round 2)

- **4bna**: move scrub-pii.sh check inside staged-file guard (was blocking all commits)
- **yjrj**: scope PII scrub regex to owner/created_by fields only
- **l3d5**: add placeholder substitution validation guards at consumption points
- **88zh**: register {REVIEW_TIMESTAMP} in placeholder conventions
- **2gde**: replace dead GLOSSARY.md links with inline wave definition

### Review Fix (Round 3)

- **12u9**: add IF ROUND 1 markers to placeholder guard path list in reviews.md

### Review Statistics

| Round | Scope | P1 | P2 | P3 | Verdict |
|-------|-------|----|----|-----|---------|
| 1 | 14 files, 17 tasks | 0 | 5 | 16 | PASS WITH ISSUES |
| 2 | 7 files, 5 fix tasks | 0 | 1 | 0 | PASS WITH ISSUES |
| 3 | 1 file, 1 fix task | 0 | 0 | 1 | PASS |

21 review beads filed (round 1: 5 P2 + 15 P3; round 2: 1 P2; round 3: 1 P3 auto-filed to Future Work).

### Epics

- **ant-farm-753** (Verification & Checkpoints): closed (17/17 children)

## 2026-02-17 — Session 6ecb64 (Review Cycle)

### Review Summary

Code review of 6 tasks across 4 epics (d6k, 21d, 753, amk) from session 795d29.

- 72 raw findings from 4 Nitpicker reviewers (clarity, edge-cases, correctness, excellence)
- 40 root causes after Big Head deduplication (44% dedup rate)
- 1 P1, 6 P2, 33 P3

### Deferred P1

- **ant-farm-0mx**: PII scrub regression — `bd sync` (commit f455361) reverted the email scrub from task i0c (commit 047f1be). All records in `.beads/issues.jsonl` still contain owner email at HEAD. User decision: defer fix, document here.

### Epic Verdicts

| Epic | Verdict | Score |
|------|---------|-------|
| d6k (Setup & Forkability) | NEEDS WORK | 6.5/10 |
| 21d (Orchestration Reliability) | PASS WITH ISSUES | 9/10 |
| 753 (Review Pipeline Improvements) | PASS WITH ISSUES | 8/10 |
| amk (Documentation & Standards) | PASS | 7.5/10 |

### Tasks Completed (Session 795d29)

- **pq7**: fix: add mkdir -p guards and CLAUDE.md backup to sync script
- **4gi**: feat: add install-hooks.sh and document hook installation step
- **i0c**: fix: scrub owner email PII from issues.jsonl and document fork/init step
- **nr2**: fix: prevent silent task dropping with structured error metadata
- **z6r**: docs: clarify Big Head verification pipeline boundaries and add read confirmation
- **p33**: docs: add placeholder conventions canonical reference

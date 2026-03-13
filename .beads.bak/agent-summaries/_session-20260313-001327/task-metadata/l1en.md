# Task: ant-farm-l1en
**Status**: success
**Title**: Missing type validation on --from-json payload and config counter int() conversions
**Type**: bug
**Priority**: P2
**Epic**: none
**Agent Type**: python-pro
**Dependencies**: {blocks: [], blockedBy: []}

## Affected Files
- crumb.py:645-649 — `cmd_create --from-json`: `json.loads` result not checked with `isinstance(payload, dict)` before `.get()`
- crumb.py:679 — `int(config.get("next_crumb_id", 1))` unguarded `ValueError`
- crumb.py:1148 — `int(config.get("next_trail_id", 1))` same unguarded pattern
- crumb.py:1433 — import path same `int()` pattern
- crumb.py:1646-1647 — post-import counter update same `int()` pattern

## Root Cause
External inputs parsed via `json.loads` or `int()` are used directly without type validation. A non-dict JSON payload from `--from-json` causes `AttributeError` on `.get()`, and a non-integer config counter causes `ValueError` on `int()`. Both produce raw Python tracebacks.

## Expected Behavior
Clean error messages for invalid inputs: non-dict --from-json payloads and corrupted config counter fields.

## Acceptance Criteria
1. `crumb create --from-json '["a"]'` produces a clean error message, not a Python traceback
2. `crumb create --from-json '"just a string"'` produces a clean error message
3. Corrupted `next_crumb_id` (e.g., `"corrupted"`) in config.json produces a clean error pointing to the config field

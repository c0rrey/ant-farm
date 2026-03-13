---
bead: ant-farm-l1en
title: Missing type validation on --from-json payload and config counter int() conversions
commit: 87cdd8f
---

## Files Changed

- `crumb.py` — added `isinstance(payload, dict)` check in `cmd_create` and int-validation loop in `read_config()`

## Implementation

Two distinct problems were fixed:

1. **`cmd_create --from-json` type check (L673-674)**: After `json.loads()` succeeds, added `if not isinstance(payload, dict): die("--from-json must be a JSON object, not a list or scalar")`. Previously, passing a JSON array or scalar (e.g., `'["a"]'` or `'"string"'`) would parse successfully but then crash with `AttributeError` on the first `payload.get(...)` call, since lists and strings don't have `.get()`.

2. **Config counter validation in `read_config()` (L146-150)**: Added a loop after `config.update(stored)` that iterates over `("next_crumb_id", "next_trail_id")`, attempts `int()` conversion, and calls `die()` on `ValueError` or `TypeError`. This covers all five `int(config.get(...))` call sites (`cmd_create` L697, `_cmd_trail_create` L1166, import path L1451, post-import update L1664-1665) from a single fix point. The validated integer is written back into `config[field]`, so downstream callers get an `int` directly.

## Approaches Considered

1. **Wrap each `int()` call site individually in `try/except ValueError`**: Would fix the five affected lines independently. Rejected in favour of the `read_config()` validator because it requires five parallel changes that could drift out of sync as new call sites are added. The single fix point in `read_config()` is more robust and matches the bug description's preferred approach ("preferred — single fix point").

2. **Add a `validate_config(config)` helper called from `read_config()`**: Functionally identical to the chosen approach but split into a separate named function. Rejected as over-engineering — there are only two fields to validate and the logic is three lines. A named helper adds indirection with no readability benefit.

3. **Use `int(config.get("next_crumb_id", 1) or 1)` to silently fall back to 1 on corruption**: Would suppress the error rather than surface it. Rejected because silent fallback resets the counter, potentially creating duplicate IDs if the config is partially corrupted. A clean `die()` message is the correct user experience.

4. **Validate the JSON payload shape earlier — at `argparse` level with a custom `type=` function**: `argparse` supports `type=json.loads` to parse at argument-parse time. A custom type that also validates `isinstance(result, dict)` would catch the error before `cmd_create` is called. Rejected because other JSON-taking arguments in the codebase don't use this pattern, and the existing `try/except json.JSONDecodeError` in `cmd_create` is already the established location for `--from-json` validation.

5. **Validate all config fields (including `prefix`, `default_priority`) in `read_config()`**: A more comprehensive validator. Rejected as out of scope — the bug only covers counter fields that feed `int()` calls, and the other fields are used as strings where type errors produce comprehensible output.

## Per-File Correctness Notes

### crumb.py

- **`isinstance` check (L673-674)**: Placed immediately after the `try/except json.JSONDecodeError` block and before the CLI flag merge (`if args.title: payload["title"] = ...`). This is the earliest safe point — `json.loads` must succeed first. The `die()` call exits before any `.get()` on the non-dict payload, so no `AttributeError` is possible.
- **`read_config()` validator (L146-150)**: The loop runs after `config.update(stored)`, so it validates the merged config (defaults + stored values). `DEFAULT_CONFIG` sets `next_crumb_id` and `next_trail_id` to `1` (integers), so if neither key is present in `stored`, the loop validates `1` against `int()` trivially — no false positives for fresh installs. `config[field] = int(config[field])` normalises the value so callers like `int(config.get("next_crumb_id", 1))` become redundant but harmless double-conversions. `TypeError` is caught alongside `ValueError` to handle the case where the field is `None` or another non-string type that `int()` rejects with `TypeError` rather than `ValueError`.

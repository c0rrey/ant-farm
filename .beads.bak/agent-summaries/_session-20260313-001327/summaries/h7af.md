# Task Summary: ant-farm-h7af

## Approaches Considered

1. **Nested `links` dict (selected)** — Store all link data under `crumb["links"] = {"parent": ..., "blocked_by": [...], "discovered_from": ...}`. Matches the task spec's data model exactly. `cmd_show` already displays the `links` key as a fallback, so show output will reflect updates.

2. **Top-level fields** — Store `crumb["parent"]`, `crumb["blocked_by"]`, `crumb["discovered_from"]` at the top level. Matches how `cmd_show` and `cmd_list` check for these fields in some places. Conflicts with the task spec's stated data model.

3. **Dual-write (nested + top-level)** — Write both nested `links` dict and top-level fields for backward compatibility. Redundant data, complicates future maintenance, no clear benefit for this codebase.

4. **Lazy links initialization with property** — Only create the `links` dict when the first link is set. Effectively what Approach 1 does (using `crumb.get("links") or {}`), just framed differently. No implementation distinction at this scale.

## Selected Approach

Approach 1: nested `links` dict per task spec. The `cmd_show` function already has a `("links", "Links")` entry in its fields list that will display the dict, satisfying AC5. The top-level `blocked_by` and `discovered_from` entries in `cmd_show` are for legacy/imported records that store those at the top level.

## Implementation Description

`cmd_link` replaces the stub at crumb.py L768. It acquires `FileLock`, reads tasks, finds the target crumb, then conditionally applies each flag:

- `--parent` (`args.link_parent`): Sets `links["parent"]`; skips write if already equal.
- `--blocked-by` (`args.blocked_by`): Appends to `links["blocked_by"]` list only if not already present (no-duplicate guard).
- `--remove-blocked-by` (`args.remove_blocked_by`): Filters out the given ID from `links["blocked_by"]`; no-op if not present.
- `--discovered-from` (`args.discovered_from`): Sets `links["discovered_from"]`; skips write if already equal.

Multiple flags can be combined in one invocation. After all changes, if `changed=True`, writes `crumb["links"] = links`, stamps `updated_at`, and calls `write_tasks`.

## Correctness Review

**crumb.py** (changed section L768-839):

- AC1 (--parent sets links.parent): `links["parent"] = args.link_parent` under the `args.link_parent is not None` guard. Confirmed by smoke test showing `Links: {'parent': 'AF-T1'}`.
- AC2 (--blocked-by appends without duplicates): `if args.blocked_by not in blocked: blocked.append(...)`. Confirmed: adding AF-1 twice only appears once in the array.
- AC3 (--remove-blocked-by removes from array): List comprehension filters the ID. Confirmed: after removing AF-1, only AF-2 remains.
- AC4 (--discovered-from sets field): `links["discovered_from"] = args.discovered_from`. Confirmed by smoke test.
- AC5 (show reflects updated links): `cmd_show` displays the `links` key via its `("links", "Links")` field entry. Confirmed: show output showed the full nested dict.
- AC6 (flock + atomic write): `with FileLock():` wraps the entire operation; `write_tasks` uses temp-file-then-rename. Code inspection confirms both.

No regressions: only the cmd_link stub was replaced. All other functions unchanged.

## Build/Test Validation

Smoke tested all acceptance criteria manually against the temp `.crumbs/` directory from task 1 testing. All passed. No test suite exists for crumb.py (adjacent issue, not fixed).

## Acceptance Criteria Checklist

- [x] `crumb link <id> --parent <trail-id>` sets links.parent field in the crumb's JSONL entry — PASS
- [x] `crumb link <id> --blocked-by <other-id>` appends to links.blocked_by array (no duplicates) — PASS
- [x] `crumb link <id> --remove-blocked-by <other-id>` removes the specified ID from links.blocked_by — PASS
- [x] `crumb link <id> --discovered-from <other-id>` sets links.discovered_from field — PASS
- [x] Running `crumb show <id>` after link operations reflects the updated link fields — PASS
- [x] All link operations acquire flock and use atomic write — PASS

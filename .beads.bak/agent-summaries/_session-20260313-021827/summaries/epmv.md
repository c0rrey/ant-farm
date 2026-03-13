# Summary: ant-farm-epmv — Migrate pantry.md (semantic)

## 1. Approaches Considered

**Approach A — Literal token substitution only**
Replace every `bd` token with `crumb` and adjust only the subcommand names mechanically. No prose changes. Tradeoff: the flag for `bd dep add --type parent-child` has no direct mapping and requires more than a word swap; this approach would leave incorrect flag syntax.

**Approach B — Semantic replacement plus prose context rewrite**
Replace commands and rewrite surrounding explanatory prose to remove all conceptual references to the old CLI. Tradeoff: risks changing instructional meaning and violates scope boundaries by touching content outside the 6 targeted lines.

**Approach C — Remove deprecated section entirely**
L276-L334 live inside Section 2, which is already marked DEPRECATED. Delete the entire Big Head bead-filing subsection instead of migrating it. Tradeoff: loses specification detail that big-head-skeleton.md still references; creates a gap in the deprecated-but-retained documentation.

**Approach D — In-place command migration, remove label line, preserve all prose**
Replace each `bd` command string in-place with the correct `crumb` equivalent, remove only the `bd label add` line (no crumb equivalent), and leave all surrounding prose and workflow logic untouched. This is the minimal surgical edit satisfying all acceptance criteria without structural risk.

## 2. Selected Approach

**Approach D** was selected because:
- It achieves the exact acceptance criteria (grep returns 0, label removed, dep add correctly mapped)
- It respects scope boundaries — only command strings change, not structure or prose logic
- `crumb link --parent` is the verified correct flag for the former `bd dep add --type parent-child` pattern
- `crumb create --from-json` is the correct structured-creation equivalent for `bd create --body-file`
- `crumb list --open --short` correctly maps `bd list --status=open -n 0 --short`
- Removing only the `bd label add` line (no crumb label subcommand exists) is cleaner than leaving a broken command

## 3. Implementation Description

Six `bd` references in `orchestration/templates/pantry.md` were migrated across three distinct areas:

**L91** (Section 1, Step 2): `bd show` → `crumb show` in a "do not run" guard note.

**L165** (Section 1, Step 4): `bd show` and `bd` → `crumb show` and `crumb` in a session summary composition guard.

**L276** (Section 2, Step 3): `bd show <task-id>` → `crumb show <task-id>` in correctness review brief instruction.

**L329** (Section 2, Step 4, Big Head bead filing): `bd dep add --type parent-child` → `crumb link --parent`. The semantic intent is preserved: "do not assign standalone review beads to a specific epic by linking them as a child."

**L331** (Section 2, Step 4): `bd create --body-file` → `crumb create --from-json`. The `--body-file` flag does not exist in crumb; `--from-json` is the correct flag for structured bead creation.

**L333** (Section 2, Step 4): `bd list --status=open -n 0 --short` → `crumb list --open --short`. The `-n 0` flag does not exist in crumb; `--open` filters open items and `--short` provides brief output.

**L334** (Section 2, Step 4): `bd label add <id> <primary-review-type>` — line removed entirely. Crumb has no label subcommand; this functionality has no equivalent and the line would be a dangling broken command.

Net diff: 1 file changed, 6 insertions(+), 7 deletions(-).

## 4. Correctness Review

**File: orchestration/templates/pantry.md**

Reviewed each of the 6 original `bd` locations post-edit:

- L91: `crumb show` — correct CLI subcommand, instruction intent preserved
- L165: `crumb show`/`crumb` — correct, guard note semantics unchanged
- L276: `crumb show <task-id>` — correct, correctness reviewer instruction preserved
- L329: `crumb link --parent` — verified against `crumb link --help`: `--parent ID` is a valid flag
- L331: `crumb create --from-json` — verified against `crumb create --help`: `--from-json JSON` is a valid flag
- L333: `crumb list --open --short` — verified against `crumb list --help`: `--open` and `--short` are valid flags
- L334: removed — no crumb label subcommand; removal is correct

The workflow logic in Section 1 (Implementation Mode) and Section 2 (Review Mode, DEPRECATED) is structurally unchanged. Step sequences, conditional guards, failure artifact paths, and return table formats are all intact.

No adjacent issues were modified. One adjacent issue observed (Section 2 DEPRECATED header references `big-head-skeleton.md step 10` which may need updating for crumb command syntax) — documented here, not fixed per scope boundary rules.

## 5. Build/Test Validation

```
$ grep -c '\bbd\b' orchestration/templates/pantry.md
0
```

Grep returns 0. All 6 `bd` references confirmed removed.

Crumb flag verification:
- `crumb link --help` confirms `--parent ID` flag exists
- `crumb create --help` confirms `--from-json JSON` flag exists
- `crumb list --help` confirms `--open` and `--short` flags exist

## 6. Acceptance Criteria Checklist

| Criterion | Status |
|-----------|--------|
| All 6 bd references in pantry.md converted to crumb equivalents | PASS |
| bd dep add patterns converted to crumb link with correct flag (--parent or --blocked-by) | PASS — `crumb link --parent` at L329 |
| bd label references removed | PASS — line deleted, no crumb equivalent |
| `grep -c '\bbd\b' orchestration/templates/pantry.md` returns 0 | PASS — verified output: 0 |
| Pantry prompt composition workflow logic preserved | PASS — structure, steps, and prose logic unchanged |

**Commit**: `3fe4b6e` — docs: migrate bd CLI references to crumb equivalents in pantry.md (ant-farm-epmv)

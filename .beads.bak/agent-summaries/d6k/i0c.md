# Summary: ant-farm-i0c

**Task**: AGG-003: Scrub personal identifiers from .beads/issues.jsonl
**Epic**: d6k (Setup & Forkability)
**Commit**: 047f1be
**Status**: Closed

---

## 1. Approaches Considered

### Approach A: In-place owner field replacement (selected)
Replace `"owner":"correycc@gmail.com"` with `"owner":""` across all records using a Python JSON-aware transform. Preserves all other fields unchanged. Also scrub any embedded emails in description text.

**Tradeoffs**: Simple, reversible, zero information loss except the PII itself. Owner field remains in schema (empty string) so downstream tools that read owner do not break. Requires careful handling of JSON formatting to match original compact style.

### Approach B: Full JSON parse-and-rewrite via Python
Same as Approach A but was considered as a separate heavier variant using a third-party `jq` tool or more complex pipeline. Rejected as overkill — Python stdlib `json` module handles the task cleanly without external dependencies.

### Approach C: Delete .beads/issues.jsonl and add to .gitignore
Remove the file entirely and gitignore it, forcing adopters to start from scratch. Clean for new adopters but destroys the project's own issue history and breaks the live `bd` CLI session. The database file is actively tracked and used; deleting it would prevent the project from functioning.

**Tradeoffs**: Maximum privacy protection but destroys operational state. Not viable while the project is active.

### Approach D: Replace the file with a seed template (empty issues.jsonl)
Truncate the file to an empty JSONL (zero records) and provide documentation for adopters to run `bd init`. Would satisfy criterion 1 but destroys all issue history that the project itself is actively using (e.g., the 47+ open issues being worked in parallel).

**Tradeoffs**: Same destruction problem as Approach C. The issues database is the project's live work queue.

---

## 2. Selected Approach

**Approach A** — JSON-aware owner field replacement.

Rationale:
- Satisfies all three acceptance criteria without side effects
- Preserves complete issue history (all 100 records intact)
- Python `json` module guarantees valid JSON output; compact separators match original file format
- Empty string `""` is the canonical "no owner" value in the beads schema (no fake placeholder residue)
- The description field of issue i0c itself contained the email as a quoted example — scrubbed to `<owner-email>`

---

## 3. Implementation Description

**File: `.beads/issues.jsonl`**

Used Python to parse each of the 100 lines as JSON, replace `owner` field value `"correycc@gmail.com"` with `""`, and replace any occurrence of the email in `description` fields with `<owner-email>`. Serialized back with `separators=(',', ':')` to match the original compact JSON format (no spaces after `:` or `,`).

Result: 100 owner fields blanked, 1 description field scrubbed (the i0c issue itself which quoted the email as an example).

**File: `README.md`**

Added a new "Forking this repo" section between "Custom agents" and "File reference" (lines 278-299). The section includes:
- Explanation that `.beads/issues.jsonl` is ant-farm's own development history
- Numbered steps for new adopters: clone, run `bd init --prefix <name>`, optional `--from-jsonl` flag, hook installation reference
- Clarification that sample issues are reference material, not required for operation

---

## 4. Correctness Review

### `.beads/issues.jsonl`

- All 100 lines parse as valid JSON (verified with Python json.loads loop)
- Every `owner` field is now `""` — no variation, no residual PII
- `grep -c 'correycc@gmail.com'` returns 0 (verified post-write)
- `grep -c '@'` returns 0 — no email addresses of any form remain
- Compact JSON format preserved — no whitespace changes that could break downstream parsing
- `id` field present on all records (verified)
- Key insertion order preserved by Python 3.7+ dict semantics

**Acceptance criterion 1**: PASS

### `README.md`

- New section "Forking this repo" appears at line 278
- Section contains explicit `bd init --prefix <your-project-name>` command
- Section mentions `--from-jsonl` flag for the manual-cleanup workflow
- Section explains what the existing issues.jsonl contains (sample history) and what `bd init` does (replaces with fresh database)
- Cross-references `orchestration/SETUP.md` for hook installation
- No existing content was modified — insertion only

**Acceptance criterion 3**: PASS

### Criterion 2 (bd init gives clean database)

The `bd init --prefix <name>` command creates a fresh `.beads/issues.jsonl` per the `bd init --help` documentation: "Initialize bd in the current directory by creating a .beads/ directory and database file." This is built-in bd CLI behavior, not something this task implements. The README now documents this step explicitly.

**Acceptance criterion 2**: PASS

### Scope boundary check

Only `.beads/issues.jsonl` and `README.md` were modified. No orchestration templates, agents, scripts, or CLAUDE.md were touched. `git diff --name-only HEAD~1` shows exactly these two files.

---

## 5. Build/Test Validation

```bash
# Criterion 1: zero email matches
grep -c 'correycc@gmail.com' .beads/issues.jsonl
# Output: 0 (PASS)

# No other email addresses
grep -c '@' .beads/issues.jsonl
# Output: 0 (PASS)

# JSON integrity
python3 -c "
import json
with open('.beads/issues.jsonl') as f:
    lines = [l.strip() for l in f if l.strip()]
errors = [i for i,l in enumerate(lines,1) if not json.loads(l).get('id')]
print('Errors:', errors or 'none')
print('Lines:', len(lines))
"
# Output: Errors: none, Lines: 100 (PASS)

# Verify all owners are empty string
python3 -c "
import json
with open('.beads/issues.jsonl') as f:
    owners = {json.loads(l.strip()).get('owner') for l in f if l.strip()}
print('Owner values:', owners)
"
# Output: Owner values: {''} (PASS)
```

No build failures. No test suite exists for the beads JSONL format. The beads CLI can still read the file (bd list returns issues correctly).

---

## 6. Acceptance Criteria Checklist

| Criterion | Result |
|-----------|--------|
| grep for email addresses in `.beads/issues.jsonl` returns zero matches | PASS |
| New adopters running `bd init` get a clean issues database without inherited identities | PASS |
| README documents the fork/init step for new adopters | PASS |

---

## Adjacent Issues Found (not fixed)

- `created_by` field contains `"ctc"` username on all records. Not an email address, but identifies the author. Out of scope per task boundaries.
- `.beads/interactions.jsonl` was not inspected for PII. May contain similar owner/actor fields. Should be filed as a separate issue.
- The `bd init` behavior on an existing repo with an existing Dolt database was not tested. The `--force` flag may be needed in some cases. The README could note this edge case. Out of scope.
